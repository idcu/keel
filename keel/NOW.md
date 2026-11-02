---
scope: now
status: active
last-verified: 2026-11-02
updated: 2026-11-02
keywords: [焦点, 域索引沉降, locale泄漏, BM25检索, v3.5.0]
---

# NOW · main

## 当前焦点

**第五轮：四条主线全量落地 + 发 v3.5.0。** 上轮（PROSE + v3.4.12/13）已归档 `NOW-history/`。

## 本轮完成

- [x] L1 域索引沉降：decisions/INDEX 2965→2510B（余 490B）、pitfalls/INDEX 2980→2570B（余 430B），不动 budget.env
- [x] L2 lint 段3 `LC_ALL=C` 泄漏消除 + 段4 glob 字母表化 + LOCALE 自测（结构判死泄漏赋值）+ §9.3 同步；双 bash/双 locale 验证
- [x] L3 bash3 坑蒸馏：`bash3-utf8-varname-eats-byte` 置 distilled，CONSTITUTION rule7 扩为四例
- [x] L4 语义检索接入位参考实现：`checks/retrieval/keel-search.py`（纯 py3 BM25，k1=1.5/b=0.75）+ ADR 0019；49 篇索引 27.9ms、热路径中位 2.6–3.7ms、QPS≈322
- [x] L5 lytjs 外部冒烟：keel lint 2s/55篇 0 fail、test-lint 43/43；lytjs keel 为 v3.4.11（含段3/4 locale 缺陷，需升 3.4.13+）；fast 门禁 11/11
- [x] v3.5.0 双仓同步：INDEX 版本 / 徽章 / CHANGELOG / `--ref`；门禁 43/43 + DOC + LOCALE + PROSE 全绿

## 未完成

- [ ] lytjs 全量测试已实跑：**385 文件 / 8436 用例全绿，323.6s**（exit=0）；覆盖率 66.50% 仍为 2026-10-15 旧数据，未重跑 `vitest --coverage`
- [ ] 外部采用度仍为零（代码层无解，属推广动作）

## 下一步

1. lytjs 升级 keel 至 3.5.0（段3/4 locale 缺陷 + BM25 检索）
2. 观察 lytjs 真实采用下遵守率趋势 / 蒸馏是否触发
3. ADR 0019 升级条件：同义改写 top5 无命中占比 >10% 时启动 embedding

## 阻塞

| 卡在 | 解锁条件 | 绕行 |
|---|---|---|
| 无 | —— | —— |
