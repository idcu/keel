---
scope: meta
status: active
severity: P1
last-verified: 2026-10-04
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
推分支时一并带 tag（已修）：
```bash
git -C "$SUB" push --follow-tags origin "$BR_STARTER"
```
`--follow-tags` 带上所有可达 tag，不用手写列表。失败只告警不中止
（分支已推成功，中止反而留下更糟状态）。

## 为什么值得登记
**这是 ADR 0010 的第一个真实违约**——那条 ADR 写于两轮前，
理由正是"tag 缺失让 `--ref` 失效"。**规则写对了，编排脚本却漏了。**
与 `submodule-pointer-drift-not-machine-checked` 同族：
机器没验的那一环，规则就等于不存在。判别法：发布后**必查 `ls-remote --tags`**。
