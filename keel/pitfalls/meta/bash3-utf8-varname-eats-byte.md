---
scope: meta
status: active
severity: P1
last-verified: 2026-11-02
keywords: [bash3.2, UTF-8, 变量名定界, 全角字符, release]
triggers: 1
---

## 症状

`release.sh --apply` 自检全绿后，推送段第一行 echo 即崩
（`BR_STARTER�: unbound variable`，`set -u`），发布一步未执行。
dry-run 同炸；C/POSIX locale 正常，UTF-8 locale（zh_CN/en_US）必现。

## 根因

macOS 自带 bash 3.2.57 在 **UTF-8 locale** 下解析 `"（$VAR）"` 时，
把全角 `）`（EF BC 89）的**首字节**吞进变量名 → `VAR\xef` 未定义。
C locale 按单字节处理反而正常——bash 3.2 多字节词法有 bug，
`$VAR` 后紧跟任何非 ASCII 字符都不安全。与 harness-invokes-bare-bash
同族：脚本行为再次被交给用户机器的环境（这次是 locale）。

## 正解

变量展开一律写 **`${VAR}`** 显式定界，不依赖 locale 词法。release.sh
4 处（`$SUB（` / `$r（` / `$BR_STARTER）` / `$BR_PROJ）`）加花括号后，
四种 locale 的 dry-run 全过。排查同类：
`grep -nP '(?-u)\$[A-Za-z_][A-Za-z0-9_]*[\x80-\xff]' <脚本>`。
