---
scope: meta
status: active
severity: P1
last-verified: 2026-10-04
keywords: [ENDFILE, awk, 批量化, 过滤失效]
triggers: 1
---

## 症状
段 11「坑三段式」批量化成一次 awk 后，39 个**非坑**文件全被报"缺三段式"，
12 条真坑一条没报——方向反了。过滤写的是 `if (p !~ /pitfalls\//) { skip=1; next }`。

## 根因

**`ENDFILE` 不受"跳过"状态约束**：`skip=1` 只挡主体规则，`ENDFILE` 仍每文件都跑
一次——非坑文件 `seen[]` 全空 → 报缺三段；真坑齐全 → 也不报。**看着合理，实际整体颠倒。**

## 正解
**过滤与 `ENDFILE` 不可靠共存**，择一：① `ENDFILE` 里自判 `if (skip) next`；
② 不用 `ENDFILE`，先滤清单再 `xargs` 喂给每文件一次 `END` 的 awk。

**本项目选"不批量化"**——段 11 只有 36 次 grep ≈ 3.6s，收益远小于误判风险
（语义优先，ADR 0013）。另：`ENDFILE` 是 gawk 扩展，POSIX awk 不支持。

## 为什么值得登记
宪法第 4 条的形状：**一个"看起来正常工作"的改动，产出的是颠倒的结论。**
错的是"以为它对"。判别法：批量化后**必须核对真样例**。
