---
scope: now
status: active
last-verified: 2026-11-03
updated: 2026-11-03
keywords: [焦点, 两阶段引导, 跨版本矩阵, 升级引擎, 回归, EROFS]
---

# NOW · main

## 当前焦点

**第十二轮：两阶段引导（判据交给目标版本引擎）+ 跨版本升级矩阵；发 v3.10.0。**
第十一轮的写路径 / 故障覆盖见
[history](NOW-history/2026-11-03-write-path-and-faults.md)。

## 本轮进度

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

## 下一步

1. Windows / Git Bash 运行时（仍未验证）
2. 找第二个采用方样本，拆掉「单样本」边界
3. test-faults 在无 Docker 环境下的降级行为（当前是不可用即失败）

## 阻塞

| 卡在 | 解锁条件 | 绕行 |
|---|---|---|
| Windows 运行时未验证 | 一台可跑 bash 的 Windows（VM / 云 / Actions 写权限） | 静态守卫 + 文档三档结论，不宣称支持 |
