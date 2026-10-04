---
scope: meta
status: active
last-verified: 2026-10-03
keywords: [坑库, 索引, shell, 性能, 批量化]
---

| 症状（一行，供 grep 命中） | scope | 严重度 | → 文件 |
|---|---|---|---|
| 批量化后报大量"frontmatter 缺字段"，字段其实齐全 | meta | P1 | [meta/xargs-arg-becomes-filename.md](meta/xargs-arg-becomes-filename.md) |
| 纯 shell 查表循环挂死不退出，停在字符串拆分处 | meta | P2 | [meta/command-substitution-eats-newline.md](meta/command-substitution-eats-newline.md) |
| 批量 wc 后报"超行数 N>M: total"这类假 fail | meta | P2 | [meta/wc-total-line-treated-as-file.md](meta/wc-total-line-treated-as-file.md) |
| install.sh 报"lint 通过"但没验到新装项目（cwd 相对路径） | meta | **P0** | [meta/install-verifies-wrong-dir.md](meta/install-verifies-wrong-dir.md) |
| awk 取出的数字比较时按字典序，峰值/最大值偏小 | meta | P2 | [meta/awk-string-vs-number-compare.md](meta/awk-string-vs-number-compare.md) |
| install.sh 遍历 "$@" 时 shift，版本号被当项目根 | meta | **P0** | [meta/arg-parse-shift-while-iterating.md](meta/arg-parse-shift-while-iterating.md) |
| 手写 JSON 把空值写成 "n/a"，jq / json.load 解析失败 | meta | P2 | [meta/handwritten-json-nan-placeholder.md](meta/handwritten-json-nan-placeholder.md) |
| 两仓 lint 与 CI 全绿，但 `submodule status` 行首有 `+` | meta | P1 | [meta/submodule-pointer-drift-not-machine-checked.md](meta/submodule-pointer-drift-not-machine-checked.md) |
| 归档到 NOW-history/ 后报死链，文件其实都存在 | meta | P3 | [meta/cold-zone-link-prefix.md](meta/cold-zone-link-prefix.md) |
| 文档里举例写链接语法，被判成死链 | meta | P3 | [meta/link-syntax-example-becomes-real-link.md](meta/link-syntax-example-becomes-real-link.md) |
| 全新 clone 到 Windows 装完即红：超字节 1211>1200（CI 上同文件 1181） | meta | **P0** | [meta/byte-budget-assumes-lf.md](meta/byte-budget-assumes-lf.md) |
| 临时 worktree 里报一大片孤儿/超字节（27 条），主工作树 0 fail | meta | P1 | [meta/worktree-eol-differs-from-main.md](meta/worktree-eol-differs-from-main.md) |
| test-lint 38 例全 FAIL、每条报"（无任何 ❌/⚠️ 输出）"，手跑 lint 正常 | meta | **P0** | [meta/harness-invokes-bare-bash.md](meta/harness-invokes-bare-bash.md) |
| lint 每次 stderr 多一行 `[SAFE_DELETE_INVALID_PATH]`，%TEMP% 积 301 个 tmp 目录 | meta | P3 | [meta/safe-delete-shim-blocks-cleanup.md](meta/safe-delete-shim-blocks-cleanup.md) |
| 批量化后报 39 个非坑文件缺三段、真坑一条不报 | meta | P1 | [meta/awk-enfile-ignores-skip-state.md](meta/awk-enfile-ignores-skip-state.md) |
| release.sh 报"推送完成"但 tag 没上远端，`--ref` 装不到 | meta | P1 | [meta/release-pushes-branch-not-tag.md](meta/release-pushes-branch-not-tag.md) | [meta/awk-enfile-ignores-skip-state.md](meta/awk-enfile-ignores-skip-state.md) |
