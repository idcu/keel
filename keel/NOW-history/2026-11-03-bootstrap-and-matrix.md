---
scope: history
status: archived
last-verified: 2026-11-03
updated: 2026-11-03
keywords: [两阶段引导, 跨版本矩阵, 升级引擎, 回归, EROFS]
---

# 第十二轮：两阶段引导 + 跨版本矩阵（v3.10.0，2026-11-03）

## 焦点

`final_verify` 要求备份含 `restore.sh`，而 3.8.x 引擎不写它——所有从旧版升上来的
采用方都会被判失败。50 例自测 + 19 例升级自测 + 7 例故障自测全绿也没照出，因为
套件里「新引擎升新版」永远自洽；真实路径是旧引擎执行升级。

## 进度

- [x] `keel-upgrade.sh` 两阶段引导：模板取到并校验（版本 / manifest / sha256 / 权限）后，
      自身与模板引擎字节不同即以子进程交给**目标版本引擎**执行；`KEEL_UPGRADE_BOOTSTRAPPED=1`
      防递归；交接标记 `.keel-bootstrap.pending`；校验失败 `exit 2`、目标零改动
- [x] `install.sh` 升级分支走同一条交接（含 ≤3.5.0 无引擎者），退出码 3–5 原样透传
- [x] `test-upgrade` 24 例：引导搬运 / 自身替换 / 模板语法坏拒绝交接 / rc 透传 / dry-run 零改动
- [x] 新增 `checks/matrix/`：3.7.4 / 3.8.0 / 3.9.0 / current + 3.4.11(install) + REG-1 六格；
      判据含无假失败、内核逐字节、自定义哈希、门禁、终态五项、续跑、回滚
- [x] 快照按 git tag + 缓存，`KEEL_MATRIX_VERSIONS` 可配置；离线/缺 tag 整格 SKIP 并单列「未验证」
- [x] test-faults EROFS 能力探测：无 `SYS_ADMIN` → SKIP 原因 + 未验证计数（实测 6/0/1）
- [x] 记录：`keel/archive/upgrade-handoff-and-matrix-2026-11-03.md`

## 实测

- macOS：test-lint 50/50（13.7s）· test-upgrade 24/24（5:51）· test-faults 7/0/0（32.8s）
  · 矩阵 6/0/0（1:53）· lint 两仓 0 fail · manifest 72 行
- Debian 12 双 locale（C / zh_CN.UTF-8）：test-lint 50/50 · test-upgrade 24/24 · lint 0 fail
  · manifest 72 行；容器内矩阵 6/0/0（约 30s）
- 冒烟：v3.8.0 真装 → 新 install.sh 升 3.10.0，rc=0、五项终态过（86s），不误判

## 未覆盖

- Windows / Git Bash 运行时
- 第二个采用方样本
