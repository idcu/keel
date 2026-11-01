---
scope: now
status: active
last-verified: 2026-11-02
updated: 2026-11-02
keywords: [焦点, 评估整改, PROSE, v3.4.12]
---

# NOW · main

## 当前焦点

**11-02 全维度评估（第四轮）问题清单全量落地 + 发 v3.4.12。** 上轮（性能收口 + 采用方首测）已归档 `NOW-history/`。

## 本轮完成

- [x] 第四轮评估：三条上轮 P0 实测转绿（裸 bash 修复 / 遵守率回预算 / 性能散布归零）
- [x] P1-1/P1-2：test-lint 增 **PROSE 元检查**（ADR 0018）——散文数字从靠人记变机器判；14 处漂移全修
- [x] P2-1：starter 遗留 NOW（10-15 度量回顾）补提交（2e8c07b）
- [x] P2-2 更正：报告误判——两条坑 v3.4.4 起已 distilled 且宪法有行，关闭
- [x] decisions/INDEX 撞 3000B 预算（3146）→ §7.3「提」压缩至 2965B（不动 budget.env）
- [x] v3.4.12 双仓同步：INDEX / 徽章 / CHANGELOG / `--ref`；门禁 43/43 + DOC + PROSE 全绿
- [x] release.sh 修 bash3.2 UTF-8 变量定界坑（4 处 `${VAR}`；推送段曾崩 unbound）→ 登记 `meta/bash3-utf8-varname-eats-byte`
- [x] v3.4.12 tag 重打 annotated 推远端（lightweight 被 `--follow-tags` 静默漏推；同坑第二次命中）
- [x] 两条 distilled 坑沉 `pitfalls/archive/`（§7.3，meta/ 21→20）；pitfalls/INDEX 压至 2978B

## 未完成

- [ ] P2-3 语义检索接入位未实接（战略项，非代码缺陷）
- [ ] 外部采用度仍为零（代码层无解，属推广动作）

## 下一步

1. 域索引余量双薄（decisions 35B / pitfalls 22B）：下次新增前先做沉降（老条目指针化，§7.3「沉」，走人审）
2. 观察 lytjs 第二周：遵守率趋势 / 蒸馏是否真触发
3. PROSE 在双仓 CI 的首跑结果确认

## 阻塞

| 卡在 | 解锁条件 | 绕行 |
|---|---|---|
| 无 | —— | —— |
