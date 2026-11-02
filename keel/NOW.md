---
scope: now
status: active
last-verified: 2026-11-03
updated: 2026-11-03
keywords: [焦点, 断点恢复, 升级, lytjs, 覆盖率]
---

# NOW · main

## 当前焦点

**第八轮：把「敢升级」补成「断了也能接上」。**
v3.7.1 已发布：apply 期间原子写 `.keel-upgrade.pending`，中断后可 `--resume` 续跑或
`--rollback` 整目录还原；自测 11 → 18 例。第七轮详情见
[history](NOW-history/2026-11-02-分发断层根治.md)。

## 本轮进度

- [x] 主线一 断点恢复：pending 原子写 + `--resume`（sha256 校验 / 拒绝跨版本 / 只处理剩余文件）
      + 回滚清 pending；6 类中断场景 + 开关防护，test-upgrade 18/18
- [ ] 主线二 lytjs 3.7.0 业务侧数字（全量套件 + 覆盖率），补 CASE.md 与升级报告

## 下一步

1. lytjs 临时副本跑全量业务套件与覆盖率，按版本标注写入 CASE.md
2. QUICKSTART 补「中断后跑哪条命令」（`--resume` / `--rollback`）

## 阻塞

| 卡在 | 解锁条件 | 绕行 |
|---|---|---|
| 无 | —— | —— |
