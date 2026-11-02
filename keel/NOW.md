---
scope: now
status: active
last-verified: 2026-11-03
updated: 2026-11-03
keywords: [焦点, 断点恢复, 升级, lytjs, 覆盖率]
---

# NOW · main

## 当前焦点

**第八轮收尾：断点恢复 v3.7.1 已发布；lytjs 3.7.0 业务数字已实测，v3.7.2 补文档。**
apply 期间原子写 `.keel-upgrade.pending`，中断后可 `--resume` 续跑或 `--rollback` 整目录还原；
自测 11 → 18 例。第七轮详情见 [history](NOW-history/2026-11-02-分发断层根治.md)。

## 本轮进度

- [x] 主线一 断点恢复：pending 原子写 + `--resume`（sha256 校验 / 拒跨版本 / 只处理剩余文件）
      + 回滚清 pending；6 类中断场景 + 开关防护，test-upgrade 18/18（实测 93s）
- [x] 主线二 lytjs 3.7.0：384 文件 / 8432 用例 / 54.94s；
      覆盖率 87.65 / 87.71 / 88.02 / 87.65（四项差 ≤0.04pp，原因已写 CASE §6）

## 下一步

1. 找第二个采用方样本，拆掉「单样本」边界；Windows/GNU 环境跑一遍长套件
2. 观察 `--resume` 在真实断网/磁盘满场景下的提示是否还需要补

## 阻塞

| 卡在 | 解锁条件 | 绕行 |
|---|---|---|
| 无 | —— | —— |
