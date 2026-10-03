---
scope: meta
status: active
severity: P1
last-verified: 2026-10-03
triggers: 1
keywords: [子模块, 指针, 漂移, 硬约束, 两仓, 无人值守]
---

## 症状

两仓 lint 与 CI 全绿，但 `git submodule status` 行首有 `+`：索引 `77aa58f`，工作树已 `a668a71`。
**发布仓的最新修复进不了任何人的克隆，没有任何一个检查会报错。**

## 根因

`CONSTITUTION.md` 硬约束 2 要求"行首不得出现 `+`"，但**判它的是人不是脚本**：
lint 的检查面是 `keel/` 里的 md；CI 检出子模块用的是索引里的旧指针，所以也绿。
按 §2 原则 4，不能被脚本判死的规则等于建议——这条红线是**无人值守**的。
与 §12.3 的 tag 缺失同类：**声明与可获取脱节时，一切都看起来正常。**

## 正解

发布仓每次提交后跑 `bash scripts/release.sh --apply`——第 ④ 步推项目仓前会再查一次指针。
要机器替你盯，在项目仓 CI 加一步：
`git submodule status | grep -q '^+' && { echo "指针漂移（硬约束 2）"; exit 1; }`
