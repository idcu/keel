---
scope: meta
status: active
severity: P1
last-verified: 2026-11-02
keywords: [bash3.2, UTF-8, locale, 变量定界, glob范围, release]
triggers: 3
---

## 症状

① release.sh 推送段崩 `BR_STARTER�: unbound`（set -u）：UTF-8 locale 下
bash 3.2 词法把全角括号首字节吞进 `$VAR` 变量名。② commit-msg 钩子对所有
合法坑文件名一律「跳过非 kebab-case」——本机历次 triggers +1 从未生效
（glob `*[A-Z]*` 按 collation 匹配小写）。

## 根因

macOS 自带 bash 3.2.57 在 UTF-8 locale 下：`$VAR` 后吞非 ASCII 首字节；
glob `[A-Z]` 按 collation 展开（≈[a-zA-Z]）。C/POSIX 皆正常。连带发现：
lint 段 4 同款 glob"碰巧正确"——靠段 3 `LC_ALL=C XLIST=…;` 独立赋值的
泄漏把进程 locale 变 C；泄漏消除前不得动段 3（修复同步 §9.3，人审）。

## 正解

写法不依赖 locale：`${VAR}` 显式定界；大小写判断把 `[A-Z]` 展开成字母表
（commit-msg 钩子两仓已修）。排查：`grep -nP '(?-u)\$[A-Za-z_]+[\x80-\xff]|\[A-Z\]' <脚本>`。
历史 triggers 计数路径未审计。
