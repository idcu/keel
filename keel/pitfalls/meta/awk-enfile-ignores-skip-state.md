---
scope: meta
status: active
severity: P1
last-verified: 2026-10-04
keywords: [ENDFILE, awk, 批量化, 过滤]
triggers: 2
---

## 症状
段 11 批量化成"一次 awk + `ENDFILE`"后，**39 个非坑文件全被报"缺三段式"、
12 条真坑一条不报**——方向完全反了，输出却看着合理。

## 根因
**`ENDFILE` 不受"跳过"状态约束。** `FNR==1` 设了 `skip=1`、主体也有
`skip { next }`，但 `ENDFILE` **每文件都跑一次**：非坑 `seen[]` 全空 → 报缺三段。

## 正解（v3.4.1 已落地实测通过）
**过滤与批量化分成两步，且不要用 `ENDFILE`**：
① **过滤在 shell 侧**：纯 `case` 判 `pitfalls/*` 与 `INDEX.md`/`_template*` 豁免，
零 fork，落成清单；② **判断在 awk 侧**：一次 awk 扫全部，用
**`FNR==1` 切文件 + `END` 收尾**（POSIX awk 即可）——`ENDFILE` 的可移植替代品。
验证：造缺段的坑，**新旧两版输出逐字相同**；38/38 自测 PASS。

## 为什么值得登记
宪法第 4 条的形状：**"看起来正常工作"的改动，产出的是颠倒的结论。**
判别法：**批量化后必须核对一条真实样例**，光看"有输出"不算验证。
