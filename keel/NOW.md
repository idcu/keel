---
scope: now
status: active
last-verified: 2026-11-02
updated: 2026-11-02
keywords: [焦点, 升级, manifest, 守卫, lytjs, 案例]
---

# NOW · main

## 当前焦点

**第七轮：把「能升级」变成「敢升级」——四条主线已全部收口。**
发布侧有了 manifest 守卫，真实采用方 lytjs 第一次用 `upgrade` 跟到 v3.7.0，
过程写成了公开案例。下一轮转向「采用方可自证」：业务侧回归与中断恢复。
第六轮详情见 [history](NOW-history/2026-11-02-分发断层根治.md)。

## 本轮进度

- [x] 主线一 NOW 轮转：完成项沉入 history（余量 32B → 1284B）
- [x] 主线二 manifest 发布侧守卫：`--check-manifest` + CI/release 必过 + 自测第 11 例
- [x] 主线三 lytjs 首次外部 `upgrade`：3.5.0 → 3.7.0，49.5s（无引擎 → install 引导），
      详情见 [实测报告](archive/keel-upgrade-lytjs-first-external-2026-11-02.md)
- [x] 主线四 公开案例 `keel-starter/CASE.md`（数字全部本机实测，README 已链）

## 下一步

1. 在 lytjs 上重跑业务套件确认 3.7.0 零回归（本轮只验了 keel 门禁，未跑 8436 用例）
2. 升级中途强杀（Ctrl-C）的断点恢复未覆盖，`--rollback` 目前只处理门禁失败路径

## 阻塞

| 卡在 | 解锁条件 | 绕行 |
|---|---|---|
| 无 | —— | —— |
