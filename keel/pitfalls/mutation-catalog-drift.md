---
scope: meta
status: active
severity: P0
last-verified: 2026-11-06
triggers: 2
keywords: [变异, 清单, 算子, 哈希, 复算]
---

## 症状
`mutants.tsv` 的 old→new 是手写替换文本，判据脚本一改就指向旧锚点；注入找不到目标，
报告却不显示「清单过期」。

## 根因
替换文本与判据逻辑是两份真源：手写清单不知道 anchor 是否仍唯一命中，也不知道算子
改动后 new 是否成立；无 target 哈希绑定时旧清单看起来仍有效。

## 正解
- `sites.tsv` 只写 `anchor + operator + cases`；`new` 由 `operators.py` 纯函数生成。
- `mutants.tsv` 头部绑定 `target/manifest` sha256；`--enumerate` 逐字节比对。
- anchor 命中≠1、算子返回 None、`new==old` 一律 ENUMERATE 失败。
- 改判据脚本后先 `--regen-mutants` 再 `--recompute`；与旧结果不一致即红。

## 变体（2026-11-06）：元检查抢红
靶子就是判据脚本，SPEC-DIGEST/DOC 会比对其 sha。不隔离时任何变异都先打红它们，
「判据没反应」被误记成「被别的检查兜住」。正解：变异体在临时树回写自身 manifest sha，元检查仍守真实仓库。
