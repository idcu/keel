---
scope: meta
status: active
severity: P1
last-verified: 2026-10-04
keywords: [keel-lite, 孤儿, 裁剪, 顺序错]
triggers: 1
---

## 症状
`keel-lite.sh --apply` 报「裁剪后 keel-lint 未通过」并 `exit 1`，6 个文档被判孤儿。

## 根因（**两处，都要改**）
1. **顺序错**：先删目录、后剥 INDEX 路由行。剥离特征是**文本**，目录删完后匹配结果与
   dry-run 不同步。更严重：INDEX 不再链接 CONSTITUTION / NOW / pitfalls，而 §9.1-4
   **只豁免 INDEX.md 与 `_template*`** → 每个热区文档都成孤儿。**裁剪反而把项目弄红**。
2. **复核传了绝对路径**：`keel-lint.sh "$KEEL"` 实测判 **16 条 ❌**、相对路径 0 条
   ——绝对路径下锚点与相对引用全部错位（同 `worktree-eol-differs-from-main`）。

## 正解
① 先算新 INDEX → 再删目录 → 最后替换；② 复核用相对路径调 lint。
实测干净 clone 39 → 18 个 md，自报「✅ 通过」。

## 为什么值得登记
宪法第 7 条的变体：**脚本隐含假设了"用户的文件是我以为的样子"**。
判别法：凡"跑完变红"的工具，**先怀疑它的顺序与前提**。
