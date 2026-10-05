---
scope: now
status: active
last-verified: 2026-10-05
updated: 2026-10-05
keywords: [焦点, 采用日, macOS, 链式挂载, v3.4.7]
---

# NOW · main

## 当前焦点

**第十八轮：采用日（首个外部采用方 lytjs）+ 发 v3.4.7。** 上轮见 `NOW-history/`。

## 本轮完成

- [x] **macOS 兼容修复 ×2**：BWK awk 正则字面量 → 段 9 全量孤儿误报；gawk 专有
      ENDFILE → 末件字段丢、自测 13/42 假失败（坑 `awk-gawk-gaps`）；三副本 + DESIGN 同步
- [x] **doctor 传参修复**：曾把 keel 目录当项目根 → 挂载检查整体跳过（假"闭环成立"）；
      第 5 项占位正则同步收窄（不再误报 HTML 注释）
- [x] **ADR 0016**：版本副本检查只在写了 keel 徽章的发行仓生效；新增用例 42 作护栏
- [x] **ADR 0017 链式挂载**：verify-hooks 认可框架钩子调用 keel 本体；lytjs（husky）实测通过
- [x] **模板身份泄漏修复**：starter 的 CONSTITUTION/NOW 改为占位骨架
- [x] **发布面收口 + 发 v3.4.7**：根/内部 `install.sh` 漂移、`test-lint.py` 未随 ADR 0016
      同步——已修；v3.4.6 tag 之后的修复此前取不到（`--ref`），随本版收口
- [x] 全量自测 43/43 · 两仓 lint 0 fail

## 未完成

- [ ] 遵守率无基线 —— lytjs 已接入，等提交累积
- [ ] 段 2/3 真正优化（方案已写好，需独立验判死能力后再落地）
- [ ] 模板里的 decisions/pitfalls 示例库是否随采用方清理，待观察

## 下一步

1. 观察 lytjs 第二周：遵守率 / 检索预算 / 蒸馏触发是否真跑起来
2. 坑库再登记撞线时按子目录分层（属规格变更，走人审）
3. "同版本 patch vs tag" 政策：本次以发版收口；后续是否默认"patch 后必发版"待观察

## 阻塞

| 卡在 | 解锁条件 |
|---|---|
| 遵守率无真实基线 | 提交累积数周 |
