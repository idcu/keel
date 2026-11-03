---
scope: archive
status: done
last-verified: 2026-11-03
keywords: [两阶段引导, 跨版本矩阵, 升级引擎, 回归, EROFS, SKIP]
---

# 两阶段引导 + 跨版本矩阵 · 2026-11-03（v3.10.0）

## 结论

- **两阶段引导成立**：起点 ≤3.9.x 的仓库，实际判据由**目标版本引擎**以子进程执行；
  旧引擎只取模板 + 校验，校验不过 `exit 2`，目标零改动。
- **矩阵 6/6 通过**（macOS 与 Debian 12 各一遍）。v3.9.0 的 `restore.sh` 误判已成为
  永久回归用例 REG-1，并实测通过。
- 矩阵顺带照出两处**旧实现缺陷**（裸 `cp` 自替换截断、git 快照权限漂移），已隔离/修正，
  REG 不把旧实现缺陷记到新判据头上。
- EROFS 用例改为能力探测：无 `SYS_ADMIN` 输出明确 SKIP 原因并单列「未验证」，CI 不红。

## 环境

| 基线 | 版本 | 说明 |
|---|---|---|
| macOS 主机 | bash 3.2.57 · BSD 工具链 | 开发机，跑全量 |
| `keel-gnu-12` 容器 | Debian 12 · bash 5.2.15 · glibc 2.36 · python 3.11.2 | 双 locale：`C` 与 `zh_CN.UTF-8` |
| 容器挂载 | `/Volumes/Data/keel → /src`（只读） | 容器内 `cp -a` 到 `/work` 再跑，宿主零写入 |

## 命令

```bash
# macOS 全量
bash keel/checks/test-lint.sh
bash keel/checks/test-upgrade.sh
python3 keel/checks/test-faults.py            # 需要 Docker
bash keel/checks/matrix/test-upgrade-matrix.sh
bash keel/checks/keel-lint.sh keel
bash keel/checks/keel-upgrade.sh --check-manifest keel

# glibc 双 locale（容器内 /work）
for L in C zh_CN.UTF-8; do
  LC_ALL=$L bash keel/checks/test-lint.sh
  LC_ALL=$L bash keel/checks/test-upgrade.sh
  LC_ALL=$L bash keel/checks/keel-lint.sh keel
done
KEEL_MATRIX_CACHE=/tmp/kc-gnu bash keel/checks/matrix/test-upgrade-matrix.sh

# SKIP 路径（不联网 + 从未发布过的 tag）
KEEL_MATRIX_CACHE=/tmp/kc-empty KEEL_MATRIX_OFFLINE=1 \
KEEL_MATRIX_VERSIONS=3.99.0,current KEEL_MATRIX_NO_INSTALL_CELL=1 \
  bash keel/checks/matrix/test-upgrade-matrix.sh; echo "exit=$?"
```

## 实测（v3.10.0 最终代码）

| 项 | macOS | Debian 12 · C | Debian 12 · zh_CN.UTF-8 |
|---|---|---|---|
| test-lint | 50/50 · 13.7s | 50/50 | 50/50 |
| test-upgrade | 24/24 · 5:51 | 24/24 | 24/24 |
| test-faults | 7 通过 / 0 失败 / 0 跳过 · 32.8s | ——（依赖 Docker，未在容器内跑） | —— |
| test-faults（`KEEL_EROFS_CAP=off`） | 6 通过 / 0 失败 / 1 跳过（未验证） | —— | —— |
| keel-lint | 0 fail | 0 fail | 0 fail |
| manifest | 72 行一致 | 72 行一致 | 72 行一致 |
| 矩阵（6 格） | 6 通过 / 0 失败 / 0 跳过 · 1:53 | 6 通过 / 0 失败 / 0 跳过 · 约 30s | —— |

矩阵各格耗时（macOS / Debian 12）：3.7.4 13.1s / 3.8s；3.8.0 13.2s / 3.6s；
3.9.0 36.5s / 6.5s；current 1.9s / 0.3s；3.4.11-install 46.6s / 14.4s；REG-1 1.8s / 0.9s。

## SKIP 行为（实测输出）

```
[SKIP] 3.99.0 → 3.10.0
       拿不到 v3.99.0 快照：本地无此 tag，且 KEEL_MATRIX_OFFLINE=1 禁止联网
[PASS] current → 3.10.0
[PASS] REG-1 旧引擎备份布局（无 restore.sh）
✅ 矩阵通过：2 通过 / 0 失败 / 1 跳过（未验证）
   ⚠️ 未验证：3.99.0 —— 拿不到 v3.99.0 快照：本地无此 tag，且 KEEL_MATRIX_OFFLINE=1 禁止联网
exit=0
```

要点：取不到的格计「跳过（未验证）」，汇总单列，退出码 0（CI 不红），
且**不会**计入通过数——SKIP 与 PASS 在输出上不可混淆。

快照缓存：默认 `$TMPDIR/keel-matrix-cache/vX.Y.Z`，命中即复用；
缺失 tag 才 `git fetch --depth 1 origin <tag>`；`KEEL_MATRIX_OFFLINE=1` 禁网。
本地已有 tag 时离线也能跑（git archive 不走网络）。

## 矩阵照出的两处旧实现缺陷（均已处置）

1. **旧引擎裸 `cp` 自替换**：`cp` 是 truncate 不是 rename，正在执行的脚本被截断后
   bash 从同 inode 新内容中间继续读，3.7.4 实测崩 `_rel: unbound variable`。
   矩阵把旧引擎复制到临时位置执行以隔离该实现缺陷；新引擎的 rename 路径由
   test-upgrade「自身替换安全」用例单独验证。
2. **git archive 快照权限漂移**：git 默认 `tar.umask=0002`，解出的文件是 664/775，
   与 manifest 的 644/755 不符；矩阵取快照时加 `-c tar.umask=0022`。

## 发布后跨版本冒烟（v3.8.0 → v3.10.0）

空目录真装 v3.8.0，加自建文件（`NOW.md` 段落 + `decisions/0099-smoke.txt`），
再用 v3.10.0 的 `install.sh` 升级：

```bash
bash <(curl -fsSL .../raw/v3.8.0/install.sh) . --ref v3.8.0 --with-anchor
bash <(curl -fsSL .../raw/v3.10.0/install.sh) . --ref v3.10.0 --with-anchor
```

| 项 | 结果 |
|---|---|
| 升级 | rc=0 · 86s · `keel-upgrade · 目标=… 3.8.0 → 3.10.0 模式=apply` |
| 终态 | 版本 / 断点终态 / 备份可回滚 / manifest / 临时文件 5 项全过 |
| 输出 | `✅ 升级完成：3.8.0 → 3.10.0（内核覆盖 24 · 新增 0 · 保留 47）` |
| 自定义 | `NOW.md`、`decisions/0099-smoke.txt` 哈希逐字节不变 |
| 残留 | 无 `.keel-upgrade.pending` / `.keel-bootstrap.pending` |
| 备份 | `3.8.0-to-3.10.0-…/keel/INDEX.md` = 3.8.0，含 `restore.sh` |
| 升级后 | manifest 72 行一致 · lint 0 fail |

说明：旧版仓库里没有新引擎，因此实际执行者是新 `install.sh` 拿到的**模板引擎**
（输出首行即目标版本引擎的标识）。旧引擎原地直跑（不推荐）仍可用，但判据由旧引擎做，
这正是 QUICKSTART 要求「升级请走 install.sh / 新引擎」的原因。

另外记一条环境噪声：冒烟目录不是 git 仓库，install.sh 第 4 步会打印
`❌ 不是 git 仓库` 并提示钩子未装——预期行为，不影响升级结果。

## 未覆盖

- Windows / Git Bash 本轮未跑（历史归档已记，仍未验证）。
- test-faults 在**无 Docker**环境下如何降级未实测（当前实现是 Docker 不可用即失败）。
- bash 3.2 仅在 macOS 上覆盖（Linux 发行版不提供）。
- 矩阵默认格未包含 3.6.x（该区间由 v3.4.11 install 格 + 3.7.4 格夹住，
  需要时用 `KEEL_MATRIX_VERSIONS` 加格）。
