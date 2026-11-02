---
scope: now
status: active
last-verified: 2026-11-03
updated: 2026-11-03
keywords: [焦点, 断点恢复, 升级, lytjs, 覆盖率]
---

# NOW · main

## 当前焦点

**第九轮：Linux/GNU 全量验证（3 条基线）暴露 4 处真实缺陷，已修并发 v3.7.4。**
断点恢复在 GNU 下成立；lint 入参形式与环检测的 tsort 依赖已消除；
升级自测 18 → 19 例。第八轮见 [history](NOW-history/2026-11-02-分发断层根治.md)。

## 本轮进度

- [x] 三条 Linux 基线（Debian 12 / Debian 13 / Alpine+musl）全量跑通：
      lint 0 fail、test-lint 双 locale 44/44、test-upgrade 19/19、manifest 69 行
- [x] 修 3 处：lint 路径归一化（相对/绝对/`.` 等价）、环检测去 tsort（awk Kahn）、
      备份/回滚 `cp -pR`（umask 077 下权限不再丢）
- [x] 真实采用方链路：3.6.1 → 3.7.3 升级 9.14s；故障注入中断后 `--resume` 4.80s 续完
- [x] 记录：`keel/archive/linux-gnu-validation-2026-11-03.md`；CASE 边界按实测更新
- [x] 发布后冒烟又暴露第 4 处：`install.sh` 结尾提示写死「42 用例 + 1 元检查」
      （PROSE 只守 README/DESIGN，管不到脚本输出）→ 改为不写死数字，发 v3.7.4

## 下一步

1. Windows（Git Bash）跑一遍长套件，补齐三平台矩阵
2. 找第二个采用方样本，拆掉「单样本」边界

## 阻塞

| 卡在 | 解锁条件 | 绕行 |
|---|---|---|
| 无 | —— | —— |
