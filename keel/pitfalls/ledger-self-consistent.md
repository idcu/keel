---
scope: meta
status: active
severity: P0
last-verified: 2026-11-06
triggers: 1
keywords: [账本, 分母, 判据, 复算, 静默删除]
---

## 症状
`criteria.tsv`、`test-lint.py`、`ledger.tsv` 三处同步删掉一条 §9.1 判据后，
`--check` 仍逐字节通过，百分比仍显示"全绿"；只有 DESIGN §9.1 表还多着那一行。

## 根因
账本只与「清单 + 用例」自洽，不知道规格里声明了多少条判据。
删判据时若只改机器可读的三处，规格与账本会安静地分叉；
`--regen` 会把这种分叉固化成新的"正确"基线。

## 正解
- `criteria.tsv` 的 §9.1 行**禁止 `counted=no`**：移出分母就是改口径，必须 ADR + 新旧两套数字。
- `--check` 每次把清单的 §9.1 编号集与 DESIGN §9.1 表比对，缺行 / 多行 / 缺号即 rc=1。
- 删判据必须同时删 DESIGN 行并留痕；`--negctl` 负控 2 专测「三处对齐但 DESIGN 仍 19 行」。
- 采用方没有 DESIGN 时，对齐状态打 SKIP，不伪装 PASS。
