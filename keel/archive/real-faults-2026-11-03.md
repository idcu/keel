# 真实故障下的 --resume（2026-11-03）

> 结论：**3/3 判死用例通过**。磁盘满（备份阶段 / apply 阶段）与断网两类真实故障
> 各有机器断言，不再依赖 `KEEL_UPGRADE_FAULT` 模拟中断。本轮因此暴露 **3 处真实缺陷**
> （见 §4），均已修复并进入 v3.8.0。

## 1. 环境与命令

| 项 | 值 |
|---|---|
| Docker | 29.7.2，`linux/x86_64` |
| 镜像 | 默认 `python:3.11`（实测 10.4s）；本地亦可 `KEEL_FAULT_IMAGE=idcu-go-devbox:latest`（6.8s） |
| 宿主 | macOS 15.8.2 / python3 3.13.5 |
| 模板 | 规格仓的 `keel/`（`TEMPLATE_REL=keel`），升级目标 3.7.0 → 当前版本 |

```bash
python3 keel/checks/test-faults.py                 # 3/3，约 10s
KEEL_FAULT_IMAGE=idcu-go-devbox:latest python3 keel/checks/test-faults.py
```

容器参数：宿主仓库 `:ro` 挂载 + 容器内 `cp -a` 副本；`--tmpfs /small:size=4m,exec`
（默认 `noexec` 会让 lint 判「钩子不可执行」）；断网用例 `--network none`；必须 `-i`
（否则 `bash -s` 读不到脚本、零输出）。

## 2. 三条用例与判死断言

### A. 磁盘满 · 备份阶段（`t_disk_backup`）

填充 tmpfs 至只剩 32K → 备份必然 ENOSPC。断言：

- rc=2 且输出含「备份失败」（不是静默成功）；
- `.keel-upgrade.pending` 仍完整，`stage=preflight`（不被写坏）；
- `keel-version` 仍是 3.7.0（失败路径没动树）；
- 删除填充球后 `--resume` 续完到目标版本、pending 消失、lint 0 fail。

### B. 磁盘满 · apply 阶段（`t_disk_apply`）

留「备份 + 24K」，并在 prelude 删掉 `checks/retrieval/`、`test-upgrade.py`、
`test-lint.py` 制造"旧版本缺文件"（否则覆盖同尺寸文件净耗零，永远写不满）。断言：

- rc=2 且输出含「写入失败」；
- pending 可读，`stage ∈ {backup, applying}`；
- **pending 记录的每个文件哈希与磁盘一致**（记错哈希 = 续跑会跳过没写完的文件）；
- **树里无 0 字节脚本**（截断检测）；
- pending 含 `to=` / `backup=` 元信息（可按备份回滚）；
- 清空填充球后 `--resume` 续完，且 `diff -r` 与全新安装**逐字节一致**、lint 0 fail。

### C. 断网（`t_offline`）

`--network none` 下默认在线升级（从远端取模板）。断言：

- rc=2 且输出含「拉取模板失败」（错误可读）；
- 无 `.keel-upgrade.pending`、无 `.keel-backup/`、整树 sha256 不变（零残留）；
- **同环境** `--from <本地模板>` 离线升级成功。

## 3. 计入与耗时

| 套件 | 结果 | 耗时 |
|---|---|---|
| `test-faults.py`（3 例） | 3/3 PASS | 10.4s（`python:3.11`）/ 6.8s（devbox 镜像） |
| `test-upgrade.py`（19 例，含断点注入） | 19/19 PASS | 148s |
| `test-lint.py`（44 例 + 2 元检查） | 46/46 | 14.8s（macOS） |

## 4. 本轮暴露的 3 处真实缺陷（均已修复）

| # | 缺陷 | 严重度 | 修法 |
|---|---|---|---|
| 1 | `pending_write` 的 `printf >` 与 `mv` 失败都被忽略：磁盘满时 pending 停在上一版，调用方以为已记下，**零输出** | 中 | 两步都判退出码，失败 `die 2`；失败时**保留上一版 pending**（清 temp、不 rename） |
| 2 | kernel / additive 分支 `cp` 与 merge 分支 `sed -i` 的退出码没人看：ENOSPC 留下截断文件、把**残片哈希**记进 pending；直接覆盖 `keel-upgrade.sh` 自身时，正在执行的脚本被截成 0 字节，进程仍打印「✅ 升级完成」 | **高** | 一律 temp + `mv` 原子替换（执行中的旧 inode 不被截断）；每个写动作失败即 `die 2` 并提示 `--resume` / `--rollback`；manifest 落盘同样 temp+mv |
| 3 | temp+mv 的中间文件 `*.keel-new.*` 被 SIGKILL 留在树里（不在清单、会被 lint 看见） | 低 | apply 前统一清理 `find ... -name '*.keel-new.*' -delete` |

新增坑条目 [upgrade-silent-write-failure](../pitfalls/archive/upgrade-silent-write-failure.md)
（P0，含判死方式）。因坑目录 20 文件已满，按 §7.3 把 `awk-string-vs-number-compare`
沉到 `pitfalls/archive/`，未放宽 `budget.env`。

## 5. Docker 缺失时怎么办（CI 跳过条件）

`test-faults.py` 头部与 `docker_ok()` 规定：以下任一成立即打印 `SKIP` 并 **exit 0**，
本地与 CI 都不会因缺 Docker 变红：

- `KEEL_SKIP_DOCKER=1`；
- 本机无 `docker`；
- `docker info` 不可用（daemon 未启动）；
- `docker info` 的 `OSType ≠ linux`。

要真跑就必须装 Docker（linux 容器）；本轮两仓的门禁在无 Docker 环境下按同一规则跳过。

## 6. 未覆盖

- 4MB tmpfs 是按仓库实际体积选的，未测更大的仓库（备份所需空间随之增长，阈值需按 `du -sk keel` 调）；
- 未测"磁盘满发生在 gate 阶段"（门禁运行期间写日志/临时文件）；
- 未测文件系统只读（EROFS）与配额超限（不同 errno，错误文案同为「磁盘满或只读？」）；
- 断网用例只覆盖 `--to`（在线）与 `--from`（离线）两条，未覆盖"拉取到一半断网"。
