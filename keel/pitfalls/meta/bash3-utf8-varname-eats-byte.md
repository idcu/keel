---
scope: meta
status: distilled
severity: P1
last-verified: 2026-11-02
keywords: [bash3.2, UTF-8, locale, 变量定界, glob范围]
triggers: 4
---

> **已蒸馏**：上提至 `CONSTITUTION.md` 硬约束第 7 条第四例。

## 症状

① release.sh 崩 `BR_STARTER: unbound`：UTF-8 下 bash 3.2 把全角括号首字节
吞进 `$VAR` 名。② commit-msg 钩子对所有合法文件名误判「非 kebab-case」——
本机历次 triggers +1 从未生效（glob `*[A-Z]*` 按 collation 匹配小写）。

## 根因

macOS bash 3.2.57 UTF-8 locale：`$VAR` 后吞非 ASCII 首字节；glob `[A-Z]`
按 collation 展开（≈[a-zA-Z]）。C/POSIX 正常。连带：lint 段 4 同款 glob
"碰巧正确"——靠段 3 `LC_ALL=C XLIST=…;` 泄漏变 C（本轮已修：命令前缀+字母表）。

## 正解

写法 locale 无关：`${VAR}` 定界；大小写用字母表（钩子两仓已修）。
排查：`grep -nP '\$[A-Za-z_]+[\x80-\xff]|\[A-Z\]' <脚本>`。
