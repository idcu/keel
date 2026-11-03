---
scope: meta
status: active
severity: P1
last-verified: 2026-11-04
triggers: 2
keywords: [清单, SKIP, 解析器, 伪装PASS, 验证, 诚实]
---

## 症状

`verify-report.json` 写「98 通过 / 0 跳过」，而套件原始输出里有 `[SKIP] 44`。
人类读到的跳过没进机器字段，发行说明因此拿到「0 跳过」的假前提。

## 根因

汇总器只解析「X/Y 通过」总结行，把打印的 `[SKIP]` 当装饰：
`skipped=0` 且套件标 `PASS`——正是判据要抓的伪装 PASS，只是发生在**生成清单**这一步。

## 正解

- 必须把 `[SKIP]` 计入 `skipped` 并保留原因；`status_of()` 见 `skipped>0` 即标 SKIP。
- 算 `passed` 必须减掉 skips：套件的口径是「跳过也算进 ok」（保住跨平台 50/50 承诺），
  照抄就重复计数——实测 `98+0+1 ≠ 100`。锚是 `passed+failed+skipped == cases`。
- 这类账目错误**不会让任何判据变红**，只能靠真实套件输出回归发现。
