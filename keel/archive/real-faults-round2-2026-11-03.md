---
scope: meta
status: active
last-verified: 2026-11-03
keywords: [真实故障, EROFS, 配额, 断网, atomic_write]
---

# 真实故障（第二轮）· 2026-11-03

> 配套改动：`keel-upgrade.sh` 单一写路径 + `final_verify`；`keel-lint.sh` 第 16 段。
> 上一轮（备份满 / apply 满 / 断网）见 `real-faults-2026-11-03.md`。

## 环境

- 宿主：macOS arm64；Docker linux 容器，镜像 `python:3.11`（Debian 12, glibc）
- glibc 双 locale：复用容器 `keel-gnu-12`（`debian:bookworm-slim` + python3 + `zh_CN.utf8`）
- 无 Docker / `KEEL_SKIP_DOCKER=1` / `OSType≠linux` → `test-faults.py` 整套 **SKIP 并 exit 0**

## 命令

```bash
python3 keel/checks/test-faults.py       # 7 例
bash   keel/checks/test-lint.sh          # 50/50
bash   keel/checks/test-upgrade.sh       # 19/19
bash   keel/checks/keel-lint.sh keel     # 0 fail
bash   keel/checks/keel-upgrade.sh --check-manifest keel
docker exec -e LC_ALL=C|zh_CN.UTF-8 keel-gnu-12 bash -c 'cd /src && bash keel/checks/test-lint.sh'
```

## 实测（宿主 macOS，2026-11-03）

| 用例 | 注入方式 | 判死断言 | 结果 |
|---|---|---|---|
| 磁盘满·备份 | tmpfs 4M 压到 32K | rc=2 且「备份失败」；pending=preflight；树未改 | PASS |
| 磁盘满·apply | tmpfs 留 备份+24K | rc=2「写入失败」；pending 哈希与磁盘一致；0 字节脚本 0 个；续跑后 `diff -r` 相等 | PASS |
| **磁盘满·gate** | 轮询 pending 到 `stage=gate` 后 `dd` 填满 | **rc=4 且无「升级完成」**；pending=gate；腾空后 `--resume` rc=0、lint 0；`--rollback` 回 3.7.0 | PASS |
| **EROFS·preflight** | `mount -o remount,ro` 目标盘 | rc=2 且「写入失败」；无 pending、无备份、树哈希不变 | PASS |
| **EROFS·apply 中途** | apply 中 remount ro（真 EROFS） | rc=2；pending=applying 可读；0 字节脚本 0 个；无成功打印；恢复可写后 `--resume` + `diff -r` + lint 0 | PASS |
| **配额·部分写入** | tmpfs 留 备份+12K（45KB 文件写不完） | rc=2；**未入 pending 的文件哈希与升级前逐一相同**（目标文件未被截断）；无 `*.keel-new.*`；续跑后 `diff -r` 相等 | PASS |
| **拉到一半断网** | git daemon + 慢速 TCP 代理，2s 掐断 shallow clone | rc=2「拉取模板失败」；无 pending/备份/半成品目录；树未改；同环境 `--from` 成功 | PASS |

耗时（宿主）：`test-faults` **7/7，31.2s**；`test-lint` **50/50，31.6s**；`keel-lint` 4.1s；
`test-upgrade` **19/19，378.7s**（同机负载偏高，此前同套件 148s）。
glibc 容器：`test-lint` 50/50（C 9.2s / zh_CN 10.0s）；`test-upgrade` 19/19 两 locale 均通过；
`keel-lint` 与 `--check-manifest` 两 locale 均 0。

## 机制化判据（同轮，v3.9.0）

- `atomic_write`：tmp → `sync` → 读回 sha256 → `mv` → 失败 `die 2`；目标文件在
  ENOSPC / EROFS 下**从未被截断**（写坏的只是 tmp）。
- `final_verify`：版本 / pending 清除 / 备份含 restore.sh / manifest 一致 / 无临时残留，
  5 项全过才允许打印「✅ 升级完成」。
- lint §9.1-19（第 16 段）：裸 `cp`/`mv`/`install`、`sed -i`、重定向写 `$TARGET` → fail；
  豁免 `# >>> keel-write-core` 区间、`# keel-write:ok`、heredoc 数据体。

## 本轮暴露并修掉的真实缺陷

1. **merge 分支用 `sed | atomic_write`**：管道里的函数跑在子 shell，`AW_HASH` 回不到父 shell，
   `record_file` 拿到**上一个文件的哈希** → 「写入后校验失败: INDEX.md」。
   修法：sed 先落临时文件，再 `atomic_write < tmp`；每轮循环清空 `AW_HASH`。
2. **成功打印早于终态校验**（重构前）：gate 通过即打印成功，未复核版本/pending/manifest。
3. **restore.sh 在 apply 之后写**：盘满时写不进去却仍打印"已完成"→ 已提前到备份阶段生成。

## 未覆盖项

- **EROFS 用例需要 `--cap-add SYS_ADMIN`**：没有该能力的 CI 上会失败而非 SKIP（未加能力探测，
  以免把"跑不了"伪装成 PASS）。
- apply 中途转只读的**时间窗**靠慢速 `sha256sum` 垫片拉开（30ms/次）；故障本身是真 EROFS，
  但"恰好第 N 个文件后"的精确停点未做。
