---
scope: meta
status: active
severity: P3
last-verified: 2026-10-04
keywords: [stderr噪声, safe-delete, shim]
triggers: 1
---

## 症状

`keel-lint.sh` 每次运行 stderr 都多一行 `[safe-delete][SAFE_DELETE_INVALID_PATH]…`，
且 `%TEMP%` 下堆积 301 个 `tmp.XXXXXXXX`（内含 lint 自己的 `*.ln` / `*.z`）。

## 根因

**不是 Keel 的缺陷，是环境的 shim 拦截**：lint 用
`tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT`（`keel-lint.sh:63`）清理，
而 PATH 前段的 `…/shim/safe-bin/rm` 是安全删除垫片，**拒绝带盘符的路径** →
删除被拒、trap 失效。**判据本身正确，退出码仍是 0。**

## 正解

**不要为此改 Keel**——判据没错，改了就是迎合环境（违 §2 原则 4）。识别：
`grep -rn "SAFE_DELETE" keel/checks/` 为空即非 Keel 所发；真要消除得把临时目录建在
无盘符前缀的路径——**但那是为环境改判据，须 owner 决定。**
## 为什么值得登记

§9.3 声称自测「零 stderr 噪声」，本机不成立——**不是断言错了，是它隐含假设"环境不
注入噪声"**，与宪法第 7 条同源。自测无"stderr 为空"项，是**真实缺口**。
