---
scope: meta
status: active
severity: P0
last-verified: 2026-11-06
triggers: 1
keywords: [变异, 清单, 算子, 哈希, 复算]
---

## 症状
`mutants.tsv` 里的替换文本是手写的（old→new 各一份），改一次判据脚本后，
清单仍指向旧锚点；变异注入找不到目标，报告却可能显示“无效/跳过”，不显示“清单过期”。

## 根因
替换文本与判据逻辑是两份真源：手写清单不知道 anchor 是否仍唯一命中，
也不知道算子改动后 new 是否还成立。没有 target 哈希绑定时，旧清单看起来仍然有效。

## 正解
- `sites.tsv` 只写 `anchor + operator + cases`；`new` 必须由 `operators.py` 纯函数生成。
- `mutants.tsv` 头部绑定 `target_sha256` 与 `manifest_sha256`；`--enumerate` 逐字节比对。
- anchor 命中次数 ≠ 1、算子不适用（返回 None）、`new == old` 一律 ENUMERATE 失败并 rc=1。
- 判据脚本一改，先 `--regen-mutants` 再 `--recompute`；结果与旧清单不一致即红。
