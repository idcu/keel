---
scope: meta
status: active
severity: P3
last-verified: 2026-10-04
keywords: [stderr噪声, safe-delete, shim, 临时目录泄漏]
triggers: 2
---

## 症状
`keel-lint.sh` 每次 stderr 多一行 `[SAFE_DELETE_INVALID_PATH]…`，`%TEMP%` 堆积
301 个 `tmp.XXXXXXXX`（内含 lint 自己的 `*.ln`/`*.z`）。

## 根因
**不是 Keel 的缺陷，是环境的 shim 拦截**：lint 用
`tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT`（`keel-lint.sh:63`）清理，而 PATH
前段 `…/shim/safe-bin/rm` 是安全删除垫片**拒绝带盘符的路径** → 删除被拒、trap
失效。**判据本身正确，退出码仍是 0。**

## 正解
**不要为此改 Keel**——判据没错，改了就是迎合环境（违 §2 原则 4）。
识别法：`grep -rn "SAFE_DELETE" keel/checks/keel-lint.sh` 为空即非 Keel 发。

## 补充
判据生效后**当场抓到第二个变体**（此前判据根本不检查 stderr）→ 白名单改为按
**前缀**豁免整个垫片，见 ADR 0014。

## 为什么值得登记
§9.3 声称「零 stderr 噪声」而本机不成立——**不是断言错了，是它隐含假设
"环境不注入噪声"**，与宪法第 7 条同源。ADR 0014 已补上。
