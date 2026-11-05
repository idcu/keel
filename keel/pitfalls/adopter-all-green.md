---
scope: meta
status: active
severity: P0
last-verified: 2026-11-06
triggers: 0
keywords: [采用方, SKIP, 全绿, manifest, 判据篡改, 三态]
---

## 症状

采用方仓库没有 `DESIGN.md`，DOC / PROSE 两项元检查只能 SKIP；`test-lint` 却打印
「✅ 自测通过：55/55」——本地全绿，看不出有两项判据没跑。若判据脚本被改成
`exit 0`，也没有任何本地信号。

## 根因

① 跳过被计入「通过」，汇总只有分子分母；② 采用方没有 DESIGN，DOC 一致性无从
比对，且没有第二份「判据脚本应该是什么」的哈希真源。

## 正解

- 汇总三态：`N 通过 / M 跳过 / K 失败`，跳过不计入通过；退出码仍是 0。
- 复用 `checks/manifest.tsv` 的 kernel sha256 做 SPEC-DIGEST（不新增第二份清单）。
- 负控：把采用方 `keel-lint.sh` 追加一行 → `SPEC-DIGEST` FAIL、rc=1。
