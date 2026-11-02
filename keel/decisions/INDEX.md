---
scope: meta
status: active
last-verified: 2026-11-02
keywords: [决策, ADR, 索引, 性能, 批量化]
---

| # | 决策（一句话） | 状态 | → 文件 |
|---|---|---|---|
| 0001 | 预算=行×字节×单行三约束，budget.env 真源 | active | [0001-budget-three-constraints.md](0001-budget-three-constraints.md) |
| 0002 | 入口机器验：版本/状态必填+锚点原文 | active | [0002-machine-verified-entry.md](0002-machine-verified-entry.md) |
| 0003 | triggers 由 commit-msg 钩子计数，废手工+1 | active | [0003-hook-counted-triggers.md](0003-hook-counted-triggers.md) |
| 0004 | 孤儿判定用真实链接图，非文件名子串 | active | [0004-orphan-link-graph.md](0004-orphan-link-graph.md) |
| 0005 | 钩子验谎：lint 16项+verify-hooks | active | [0005-verify-hooks.md](0005-verify-hooks.md) |
| 0006 | 单轮加载进预算+load-estimate | active | [0006-session-load-budget.md](0006-session-load-budget.md) |
| 0007 | MCP 只读落点+语义检索接入位 | active | [0007-mcp-readonly-and-retrieval-slot.md](0007-mcp-readonly-and-retrieval-slot.md) |
| 0008 | lint fork 批量化+时限预算 | active | [0008-batch-fork-and-time-budget.md](0008-batch-fork-and-time-budget.md) |
| 0009 | 遵守率口径与数据源（并0011/0012） | active | [0009-compliance-rate-objective-only.md](0009-compliance-rate-objective-only.md) |
| 0010 | 版本声明与可获取同时成立 | active | [0010-version-declared-and-fetchable.md](0010-version-declared-and-fetchable.md) |
| 0013 | 性能抖动根因=fork成本，只订正基线 | active | [0013-perf-variance-root-cause-is-fork-cost.md](0013-perf-variance-root-cause-is-fork-cost.md) |
| 0014 | 零 stderr 噪声入判据 | active | [0014-zero-stderr-as-criterion-proposal.md](0014-zero-stderr-as-criterion-proposal.md) |
| 0015 | 性能先查再动：采纳--only子集 | active | [0015-perf-measure-before-optimize.md](0015-perf-measure-before-optimize.md) |
| 0016 | 版本副本检查收窄：徽章=发行仓声明 | active | [0016-changelog-check-requires-badge.md](0016-changelog-check-requires-badge.md) |
| 0017 | 链式挂载：框架并入调用keel本体 | active | [0017-chained-mount.md](0017-chained-mount.md) |
| 0018 | 散文数字机器校验(PROSE)，历史须带版本号 | active | [0018-prose-numbers-machine-checked.md](0018-prose-numbers-machine-checked.md) |
| ~~0011/0012~~ | 已并入 0009（回填不进分母/写回过门禁），原文沉 archive/ | archived | [archive/](archive/) |
