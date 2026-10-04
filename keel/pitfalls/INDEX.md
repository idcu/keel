---
scope: meta
status: active
last-verified: 2026-10-03
keywords: [坑库, 索引, shell, 性能, 批量化]
---

| 症状（一行，供 grep 命中） | scope | 严重度 | → 文件 |
|---|---|---|---|
| 批量化后报大量 frontmatter 缺字段 | meta | P1 | [meta/xargs-arg-becomes-filename.md](meta/xargs-arg-becomes-filename.md) |
| 纯 shell 查表循环挂死 | meta | P2 | [meta/command-substitution-eats-newline.md](meta/command-substitution-eats-newline.md) |
| 批量 wc 报"超行数 N>M: total"假 fail | meta | P2 | [meta/wc-total-line-treated-as-file.md](meta/wc-total-line-treated-as-file.md) |
| install.sh 报 lint 通过但没验到新装 | meta | P0 | [meta/install-verifies-wrong-dir.md](meta/install-verifies-wrong-dir.md) |
| awk 数字按字典序比，峰值偏小 | meta | P2 | [meta/awk-string-vs-number-compare.md](meta/awk-string-vs-number-compare.md) |
| install.sh 遍历 "$@" 时 shift，版本号当项目根 | meta | **P0** | [meta/arg-parse-shift-while-iterating.md](meta/arg-parse-shift-while-iterating.md) |
| 手写 JSON 空值写 "n/a" 解析失败 | meta | P2 | [meta/handwritten-json-nan-placeholder.md](meta/handwritten-json-nan-placeholder.md) |
| 两仓全绿但 submodule status 有 + | meta | P1 | [meta/submodule-pointer-drift-not-machine-checked.md](meta/submodule-pointer-drift-not-machine-checked.md) |
| 归档到 NOW-history 后报死链 | meta | P3 | [meta/cold-zone-link-prefix.md](meta/cold-zone-link-prefix.md) |
| 文档举例写链接语法被判死链 | meta | P3 | [meta/link-syntax-example-becomes-real-link.md](meta/link-syntax-example-becomes-real-link.md) |
| Windows 全新 clone 装完即红 1211>1200 | meta | P0 | [meta/byte-budget-assumes-lf.md](meta/byte-budget-assumes-lf.md) |
| worktree 报 27 条孤儿，主树 0 fail | meta | P1 | [meta/worktree-eol-differs-from-main.md](meta/worktree-eol-differs-from-main.md) |
| test-lint 38 例全 FAIL 且无任何输出 | meta | P0 | [meta/harness-invokes-bare-bash.md](meta/harness-invokes-bare-bash.md) |
| check-mcp-config 报"全部可达"但实际 rc=7 | meta | P3 | [meta/check-mcp-config-only-proves-path.md](meta/check-mcp-config-only-proves-path.md) |
| lint stderr 多一行 SAFE_DELETE、TEMP 堆积 | meta | P3 | [meta/safe-delete-shim-blocks-cleanup.md](meta/safe-delete-shim-blocks-cleanup.md) |
| load-estimate 报超限但拆/提/沉都改不动 | meta | P2 | [meta/broad-keyword-false-overrun.md](meta/broad-keyword-false-overrun.md) |
| 批量化后 39 非坑缺三段、真坑不报 | meta | P1 | [meta/awk-enfile-ignores-skip-state.md](meta/awk-enfile-ignores-skip-state.md) |
| release.sh 报推送完成但 tag 未上远端 | meta | P1 | [meta/release-pushes-branch-not-tag.md](meta/release-pushes-branch-not-tag.md) |
| keel-lite --apply 后 6 个孤儿、exit 1 | meta | P1 | [meta/lite-strips-index-before-delete.md](meta/lite-strips-index-before-delete.md) |
