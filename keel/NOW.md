---
scope: now
status: active
last-verified: 2026-11-02
updated: 2026-11-02
keywords: [焦点, 升级, manifest, 守卫, lytjs, 案例]
---

# NOW · main

## 当前焦点

**第七轮：把「能升级」变成「敢升级」。** 上轮交付了 manifest 驱动的
`keel upgrade`（ADR 0020），但发布侧没有守卫、真实采用方还没跑过一条命令。
本轮补 CI 守卫、让 lytjs 首次 `--to` 跟进、把过程写成可公开案例。
第六轮详情见 [history](NOW-history/2026-11-02-分发断层根治.md)。

## 本轮进度

- [x] 主线一 NOW 轮转：已完成项沉入 history，余量 ≥200B
- [ ] 主线二 manifest 发布侧守卫（`--check-manifest` + CI 必过）
- [ ] 主线三 lytjs 首次外部 `upgrade` 到 3.6.1
- [ ] 主线四 采用过程写成一页公开案例

## 下一步

1. 观察真实采用方首次升级的介入点（本轮 lytjs 就是第一次），缺口写回 QUICKSTART
2. 案例文档只在数字可复现时发布，样本单薄就写「不做 + 触发条件」

## 阻塞

| 卡在 | 解锁条件 | 绕行 |
|---|---|---|
| 无 | —— | —— |
