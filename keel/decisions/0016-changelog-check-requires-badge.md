---
scope: meta
status: active
last-verified: 2026-10-05
keywords: [判据, 版本副本, CHANGELOG, 误报, 发行仓, 徽章]
type: decision
created: 2026-10-05
superseded-by:
---

# 0016 版本副本检查收窄触发：从「CHANGELOG 存在」改为「写了 keel 徽章」

## 背景

第 17 项（v3.4.5）本意只查 keel 发行仓的门面一致性，边界的实现却是"副本存在才查"。
首个真实采用方 lytjs（自带自己的 `CHANGELOG.md`、无 keel 徽章）安装当日即被误判
「CHANGELOG.md 缺 3.4.6 小节」——**判据把"用户有 CHANGELOG"当成了"自认 keel 发行仓"**。

## 决定

副本检查的触发条件改为：**根或 `keel/` 的 README 写了 `keel--version-` 徽章**。
徽章 = 该仓自认 keel 发行仓（keel 与 keel-starter 都写了）；无徽章 → 两个副本都不查。
徽章一致性检查本身不变，只是改为先执行、并记录 `_badge_seen` 供 CHANGELOG 检查判据。

## 被否掉的选项

| 选项 | 为什么没选 |
|---|---|
| INDEX frontmatter 加 `keel-role: publisher` 标记 | 模板与实例是同一份 INDEX，标记会被所有用户项目继承，误报原样复发 |
| 只在有 DESIGN.md 的仓检查 | keel-starter 无 DESIGN.md 但需要这项检查（其 CHANGELOG 是发布物） |
| 环境变量 / CLI 开关 | 门禁存在性交给"记得传参"：pre-commit 钩子与 CI 会静默失效 |

## 影响

- 自测：新增用例 42（自带 CHANGELOG、无徽章 → 必须跳过）；用例 40 补徽章前置条件
- 规格：DESIGN §9.1-17 行、§9.3 代码块（逐字同步）、自测计数段
- keel-starter 的 `keel-lint.sh` 同步；lytjs 首日反馈闭环
