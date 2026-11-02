---
scope: meta
status: active
last-verified: 2026-11-02
keywords: [坑库, 索引, shell, 性能, 批量化]
---

| 症状（一行，供 grep 命中） | scope | 严重度 | → 文件 |
|---|---|---|---|
| 批量化误报 frontmatter 缺字段 | meta | P1 | [meta/xargs-arg-becomes-filename.md](meta/xargs-arg-becomes-filename.md) |
| 纯 shell 查表循环挂死 | meta | P2 | [meta/command-substitution-eats-newline.md](meta/command-substitution-eats-newline.md) |
| wc total 行被当文件假 fail | meta | P2 | [meta/wc-total-line-treated-as-file.md](meta/wc-total-line-treated-as-file.md) |
| install/doctor 验错对象 | meta | P0 | [meta/install-verifies-wrong-dir.md](meta/install-verifies-wrong-dir.md) |
| awk 数字按字典序比，峰值偏小 | meta | P2 | [meta/awk-string-vs-number-compare.md](meta/awk-string-vs-number-compare.md) |
| install.sh $@ 遍历中 shift 吃版本号 | meta | P0 | [meta/arg-parse-shift-while-iterating.md](meta/arg-parse-shift-while-iterating.md) |
| JSON 空值写 n/a 解析失败 | meta | P2 | [meta/handwritten-json-nan-placeholder.md](meta/handwritten-json-nan-placeholder.md) |
| 两仓全绿但 submodule 有 + | meta | P1 | [meta/submodule-pointer-drift-not-machine-checked.md](meta/submodule-pointer-drift-not-machine-checked.md) |
| 归档 NOW-history 后报死链 | meta | P3 | [meta/cold-zone-link-prefix.md](meta/cold-zone-link-prefix.md) |
| 举例写链接语法被判死链 | meta | P3 | [meta/link-syntax-example-becomes-real-link.md](archive/link-syntax-example-becomes-real-link.md) |
| Windows 新 clone 装完即红 1211>1200 | meta | P0 | [meta/byte-budget-assumes-lf.md](meta/byte-budget-assumes-lf.md) |
| worktree 误报 27 孤儿 | meta | P1 | [meta/worktree-eol-differs-from-main.md](meta/worktree-eol-differs-from-main.md) |
| test-lint 全例 FAIL 无输出 | meta | P0 | [meta/harness-invokes-bare-bash.md](meta/harness-invokes-bare-bash.md) |
| check-mcp-config 可达但 rc=7 假绿 | meta | P3 | [meta/check-mcp-config-only-proves-path.md](meta/check-mcp-config-only-proves-path.md) |
| stderr 多行 SAFE_DELETE、TEMP 堆积 | meta | P3 | [meta/safe-delete-shim-blocks-cleanup.md](archive/safe-delete-shim-blocks-cleanup.md) |
| load-estimate 报超限但改不动 | meta | P2 | [meta/broad-keyword-false-overrun.md](meta/broad-keyword-false-overrun.md) |
| 批量化误报 39 非坑、漏真坑 | meta | P1 | [meta/awk-enfile-ignores-skip-state.md](meta/awk-enfile-ignores-skip-state.md) |
| release.sh 推分支漏 tag | meta | P1 | [meta/release-pushes-branch-not-tag.md](meta/release-pushes-branch-not-tag.md) |
| keel-lite --apply 后 6 孤儿 exit 1 | meta | P1 | [meta/lite-strips-index-before-delete.md](meta/lite-strips-index-before-delete.md) |
| macOS awk 误报孤儿/丢末件字段 | meta | P0 | [meta/awk-gawk-gaps.md](meta/awk-gawk-gaps.md) |
| bash3 UTF-8 下 $VAR吞字节/glob误判 | meta | P1 | [meta/bash3-utf8-varname-eats-byte.md](meta/bash3-utf8-varname-eats-byte.md) |
