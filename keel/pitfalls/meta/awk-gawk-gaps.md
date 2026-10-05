---
scope: meta
status: active
severity: P0
last-verified: 2026-10-05
triggers: 1
keywords: [awk, gawk, ENDFILE, macOS, 正则字面量, 孤儿误报]
---

## 症状

- macOS 装完当天 lint 报几十条「孤儿」（非 INDEX 文档全中）
- 自测 13/42 假失败：末个文件的 frontmatter 字段被报"整体缺失"

## 根因

两处都在 keel-lint.sh 的 awk 里，报错被 `2>/dev/null` 吞掉：
① 正则字面量 `/\/[^/]*$/`——BWK awk（macOS 自带，`awk --version`=20200816）把
字符类里的裸 `/` 当分隔符 → `nonterminated character class` → 段 9 引用图整体
不执行 → 全量误报孤儿；
② 批量化 flush 用 gawk 专有 `ENDFILE`——BWK awk 视为未定义变量、末件字段不落表；
"产物为空才回落"兜底挡不住"只缺末件"。
gawk/mawk 都可解析，故两仓此前未暴露——同「判据隐含假设运行环境」（宪法硬约束 7）。

## 正解

- 字符类里的斜杠一律转义：`sub(/\/[^\/]*$/, "", out)`
- 批量化收尾 flush 用 `END` 兜底（不用 `ENDFILE`）：末件在 END 补打印
- 改完同步 DESIGN §9.3 与发布仓副本；含 awk 的判据在 macOS 复核一次即可暴露
