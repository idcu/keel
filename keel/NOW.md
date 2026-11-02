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
- [x] lytjs 升级 keel v3.4.11 → v3.5.0（提交 `dab27d73`，已推送 `v7.0.0-dev`）：同步 4 工具链文件 + BM25 检索 + 版本号；**不动** lytjs 自定义 rules/CONSTITUTION/decisions/pitfalls

## 未完成

- [ ] 外部采用度仍为零（代码层无解，属推广动作）

## 下一步

1. 观察 lytjs 真实采用下遵守率趋势 / 蒸馏是否触发
2. ADR 0019 升级条件：同义改写 top5 无命中占比 >10% 时启动 embedding

### lytjs v3.5.0 升级验证数字（2026-11-02）

- keel lint（zh_CN.UTF-8）：0 fail，1.82s，55 篇
- test-lint：43/43 + LOCALE PASS + PROSE PASS，13.8s
- lytjs 全量测试：8436/8436，385 文件，317.23s（exit=0）
- lytjs fast 门禁：12/12，5.4s
- 覆盖率（clover.xml）：statements 87.66% / branches 87.73% / functions 88.00% / lines 87.69%（阈值 66.5/86.2/72.2/66.5 全过；原 66.50% 为 2026-10-15 旧数据）
- locale 结论：修复在非作者环境成立，未暴露被掩盖的问题（无误报无漏报）
- 详见 `archive/lytjs-smoke-test-2026-11-02.md` §五

## 阻塞

| 卡在 | 解锁条件 | 绕行 |
|---|---|---|
| 无 | —— | —— |
