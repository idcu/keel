---
scope: meta
status: active
severity: P1
last-verified: 2026-11-03
triggers: 1
keywords: [清单, SKIP, 解析器, 伪装PASS, 验证, 诚实]
---

## 症状

`verify-report.json` 汇总写「98 通过 / 0 失败 / 0 跳过（未验证）」，
但被调用套件的原始输出里明明有 `[SKIP] 44 文件名仅大小写不同`。
人类读的 SKIP 没有进入机器可读字段，发行说明因此拿到了「0 跳过」的假前提。

## 根因

汇总器只解析各套件的「X/Y 通过」总结行，把打印出来的 `[SKIP]` 当成装饰。
JSON 里 `skipped=0`、套件状态 `PASS`——正是判据要抓的「伪装 PASS」，
只是伪装发生在**生成清单**这一步，而不是发行说明。

## 正解

- 解析器必须把套件输出里的 `[SKIP]` 计入 `skipped`，并保留原因；
  `status_of()` 见 `skipped>0` 即标 `SKIP`，不再给 PASS。
- `check-verify-report.py` 的「PASS 且 skipped>0」判死保留：它是第二道闸。
- 自检要用真实套件输出回归（本轮就是靠全量复跑才发现），
  不能只用手工构造的 JSON 样例。
