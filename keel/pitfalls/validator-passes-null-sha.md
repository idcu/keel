---
scope: meta
status: active
severity: P0
last-verified: 2026-11-06
triggers: 1
keywords: [证据链, sha256, null, provenance, 校验器]
---

## 症状

`verify-report.json` 的 `provenance.checks_sha256` 四个值全是 `null`，
摘要却打印「4 个判据文件 sha256 已记录」，`check-verify-report.py --repo .` 也 PASS。

## 根因

两处叠加：① `verify.py` 的 `CHECK_FILES` 是 `checks/…`，却用 `REPO`（keel 的父目录）
拼路径；② 校验器写 `elif want and _sha(path) != want`——`want=None` 直接放行。
「记录失败」与「校验放行」各自都静默，所以两年没人发现。

## 正解

- 键相对 `keel/`，路径用 `KEEL` 拼；任一项缺失则摘要显示 `n/4` 而不是「已记录」。
- 校验器先判 sha 形态（`^[0-9a-f]{64}$`），null / 空串 / 长度不符一律判死。
- 负控：`--selftest` 增加「全 null 必须被拒」样例；真实报告改成 null 后 rc=1。
