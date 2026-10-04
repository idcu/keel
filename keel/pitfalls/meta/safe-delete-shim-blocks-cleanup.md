---
scope: meta
status: distilled
severity: P3
last-verified: 2026-10-04
keywords: [stderr噪声, safe-delete, shim, 临时目录]
triggers: 3
---

## 症状
`keel-lint.sh` 每次 stderr 多一行 `[SAFE_DELETE_INVALID_PATH]…`；`%TEMP%` 堆积
301 个 `tmp.XXXXXXXX`。

## 根因
**不是判据缺陷，是路径畸形 + 环境 shim 拦截**：`mktemp -d` 在 Windows 返回
`C:\Users\…\Temp/tmp.X`——**含盘符且混用两种分隔符**，而 PATH 前段的删除垫片
**按规则拒绝内嵌盘符** → `trap 'rm -rf "$tmp"'` 被拒 → 清理静默失效。
**判据本身正确，退出码仍是 0。**

## 正解
**归一化路径，不让判据闭嘴**（后者是迎合环境，违 §2 原则 4）。
`keel-lint.sh` 现在 `tmp=$(mktemp -d)` 后立刻 `pwd -P` 取规范路径覆盖 `tmp`
再交给 `trap`。实测归一后为纯 POSIX 路径，垫片放行、目录确实被删。

用 `pwd -P` 而非 `pwd -W`：后者 MSYS 专有，macOS 没有。

**踩坑与实测记录**见 [archive/safe-delete-full.md](../../archive/safe-delete-full.md)。
一句话教训：**判死能力 ≠ 自身正确性**，改完必须跑全量自测。