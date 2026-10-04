---
scope: meta
status: active
severity: P1
last-verified: 2026-10-04
keywords: [keel-lite, 孤儿, 裁剪, 顺序错]
triggers: 1
---

## 症状
`keel-lite.sh --apply` 跑完报「裁剪后 keel-lint 未通过」并 `exit 1`，6 个热区文档
被判孤儿（CONSTITUTION / NOW / rules.md / pitfalls/*）。

## 根因
**顺序错：先删目录、后剥 INDEX 路由行。**
剥离特征表是**文本**，目录删完后匹配结果与 dry-run 不同步（实测 dry-run 说
"剥离 6 行"、apply 说"无需剥离"）。更严重：INDEX 不再链接 CONSTITUTION / NOW /
pitfalls，而 §9.1-4 **只豁免 INDEX.md 与 _template\*** → 每个热区文档都成孤儿。
**裁剪反而把项目弄红**，而用户只照 README 跑了一条命令。

## 正解
**先算好新 INDEX → 再删目录 → 最后替换 INDEX**（已修）。
实测 39 → 19 个 md，裁剪后 lint ✅ 通过（5s）。

## 为什么值得登记
宪法第 7 条的变体：**脚本隐含假设了"用户的文件是我以为的样子"**。
判别法：凡"跑完变红"的工具，**先怀疑它的顺序与前提，别先怀疑环境**。
