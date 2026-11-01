---
scope: meta
status: active
severity: P1
last-verified: 2026-11-02
keywords: [release.sh, tag未推送, follow-tags, ADR0010]
triggers: 1
---

## 症状
`release.sh --apply` 报「✅ 两仓推送完成」、两仓 HEAD 也对上了，
**但 `ls-remote --tags` 里没有新 tag**——tag 只在本地，`--ref` 装不到。

## 根因
第 74 行只推**分支**：`git push -u origin "$BR_STARTER"`——
**`git push` 默认不推 tag**。脚本把"推送完成"当成功报出，没人复核 tag 到没到。

## 正解
推分支带 tag（已修 `--follow-tags`）；失败只告警不中止。**但
`--follow-tags` 只带 annotated tag**——2026-11-02 第二次命中：
v3.4.12 打成 lightweight，输出 Everything up-to-date，tag 静默漏推。
两条硬约定：① 发版 tag 一律 `git tag -a`（annotated）；
② 发布后必查 `git ls-remote --tags`（第一版的判别法，仍成立）。

## 为什么值得登记
**ADR 0010 的两次真实违约**：规则写对、编排漏做；连上一版"正解"
自身的假设也是错的。与 submodule-pointer-drift 同族：
机器没验的那一环，规则就等于不存在。
