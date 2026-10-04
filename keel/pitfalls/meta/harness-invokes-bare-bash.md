---
scope: meta
status: distilled
severity: P0
last-verified: 2026-10-04
keywords: [裸bash, WSL垫片, test-lint]
triggers: 1
superseded-by: ../../CONSTITUTION.md
---

> **已蒸馏**为宪法第 7 条（2026-10-04）。日常只读那一行。

## 症状

`test-lint.sh` 38 例全 FAIL，每条都报「（无任何 ❌/⚠️ 输出）」，真实输出仅 95 字节
（乱码的 WSL 安装提示）；手动跑 `keel-lint.sh` 却完全正常，两仓均 0 fail。

## 根因

`test-lint.py` 用**裸 `"bash"`** 调子进程。Windows 上 `subprocess` 命中
`C:\Windows\system32\bash.exe`（**WSL 垫片**，打印提示后 exit 1），`shutil.which`
才命中 Git Bash。于是 38 次调用**一次 lint 都没跑**，断言全落空——判据没坏，坏的
是"跑判据"那一层。与 `byte-budget-assumes-lf` 同源：**把关键变量交给了用户机器**
（那次是 git 行尾，这次是 PATH）。

## 正解

解释器一律用绝对路径：`subprocess.run([shutil.which("bash") or "bash", …])`
→ 修复后 **38/38 PASS，19m24s**（修复前"秒级返回"就是没跑的证据）。
**验套件不能只看返回值**：亚秒级的 38/38 与 19 分钟的不是一回事
