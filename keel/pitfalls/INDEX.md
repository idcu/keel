---
scope: meta
status: active
last-verified: 2026-11-02
keywords: [坑库, 索引, shell, 性能, 批量化]
---

| 症状 | scope | 严重度 | → |
|---|---|---|---|
| 批量化误报缺fm | meta | P1 | [xargs-arg-becomes-filename](meta/xargs-arg-becomes-filename.md) |
| shell查表挂死 | meta | P2 | [command-substitution-eats-newline](meta/command-substitution-eats-newline.md) |
| wc total假fail | meta | P2 | [wc-total-line-treated-as-file](meta/wc-total-line-treated-as-file.md) |
| install验错对象 | meta | P0 | [install-verifies-wrong-dir](meta/install-verifies-wrong-dir.md) |
| awk字典序峰值偏小 | meta | P2 | [awk-string-vs-number-compare](meta/awk-string-vs-number-compare.md) |
| install遍历shift吃版本 | meta | P0 | [arg-parse-shift-while-iterating](meta/arg-parse-shift-while-iterating.md) |
| JSON空值n/a解析失败 | meta | P2 | [handwritten-json-nan-placeholder](meta/handwritten-json-nan-placeholder.md) |
| 两仓全绿submodule有+ | meta | P1 | [submodule-pointer-drift-not-machine-checked](meta/submodule-pointer-drift-not-machine-checked.md) |
| 归档NOW-history报死链 | meta | P3 | [cold-zone-link-prefix](meta/cold-zone-link-prefix.md) |
| 举例链接语法判死链(蒸馏) | meta | P3 | [link-syntax-example-becomes-real-link](archive/link-syntax-example-becomes-real-link.md) |
| 新clone即红1211>1200 | meta | P0 | [byte-budget-assumes-lf](meta/byte-budget-assumes-lf.md) |
| worktree误报27孤儿 | meta | P1 | [worktree-eol-differs-from-main](meta/worktree-eol-differs-from-main.md) |
| test-lint全FAIL无输出 | meta | P0 | [harness-invokes-bare-bash](meta/harness-invokes-bare-bash.md) |
| check-mcp rc=7假绿 | meta | P3 | [check-mcp-config-only-proves-path](meta/check-mcp-config-only-proves-path.md) |
| stderr SAFE_DELETE堆积(蒸馏) | meta | P3 | [safe-delete-shim-blocks-cleanup](archive/safe-delete-shim-blocks-cleanup.md) |
| load-estimate超限改不动 | meta | P2 | [broad-keyword-false-overrun](meta/broad-keyword-false-overrun.md) |
| 批量化误报39漏真坑 | meta | P1 | [awk-enfile-ignores-skip-state](meta/awk-enfile-ignores-skip-state.md) |
| release推分支漏tag | meta | P1 | [release-pushes-branch-not-tag](meta/release-pushes-branch-not-tag.md) |
| keel-lite 6孤儿exit1 | meta | P1 | [lite-strips-index-before-delete](meta/lite-strips-index-before-delete.md) |
| macOS awk误报孤儿丢末件 | meta | P0 | [awk-gawk-gaps](meta/awk-gawk-gaps.md) |
| bash3 UTF-8吞字节/glob误判(蒸馏) | meta | P1 | [bash3-utf8-varname-eats-byte](meta/bash3-utf8-varname-eats-byte.md) |
| 升级漏文件且无检查会报 | meta | P1 | [distribution-list-drift](meta/distribution-list-drift.md) |
