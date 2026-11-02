---
scope: meta
status: archived
last-verified: 2026-11-02
keywords: [冒烟, lytjs, 外部采用, 实测]
---

# lytjs 外部冒烟测试报告（2026-11-02）

> 冷区归档。热区口径见 `keel/NOW.md`。本报告记录 keel 在首个真实采用方
> lytjs（/Volumes/Data/lytjs）上的实测表现，核实用户记忆中的三组数字是否成立。

## 一、keel 在 lytjs 上的表现

| 项 | 实测 | 预算/判据 | 结论 |
|---|---|---|---|
| keel-lint | 2s，0 fail（55 篇热区） | 300s | ✅ 余量 150× |
| test-lint | 43/43（42 用例 + 1 元检查） | — | ✅ DOC 因无 DESIGN.md 跳过（starter 正常） |
| 接入方式 | lytjs 内置 `lytjs/lytjs/keel/`，CI 有 `check-keel-wiring` 守 | — | ✅ 接线完整 |

**第一小时结论：能用。** keel 在 lytjs 上零误报、秒级返回、门禁齐全。
唯一问题是 lytjs 的 keel 版本为 **v3.4.11**，含 v3.4.13 已修的两个 locale 缺陷
（段3 `LC_ALL=C` 泄漏赋值、段4 `*[A-Z]*` glob、commit-msg 钩子同病）。
当前能过是因为泄漏"歪打正着"让段4 处于 C locale——属脆弱正确，应升级至 v3.5.0。

## 二、三组数字核实

| 用户记忆 | 实测 | 是否成立 | 证据 |
|---|---|---|---|
| 6341 用例 | **8436 用例全绿**（385 文件，323.6s，exit=0） | ❌ 已过时 | `npx vitest run --maxWorkers=2` 实跑；6341 出自 `lytjs/vitest.config.ts:166` 的 2026-10-15 注释 |
| 63.93% 覆盖率 | **66.50%** statements（36993/55631，427 文件） | ❌ 已过时 | `coverage/clover.xml` 解析；两者均为 2026-10-15 数据，同日多次测量；距今 18 天，不能代表当前 444+ 文件 |
| 15/15 权威基线 | **11/11**（fast 档门禁） | ❌ 已过时 | `node scripts/gate.mjs --tier fast` 实跑 11.6s 全过；15/15 出自 `.workbuddy-ai/memory/2026-10-15.md`，门禁配置此后调整 |

### 核实方法

- **用例数**：`cd /Volumes/Data/lytjs/lytjs && npx vitest run --maxWorkers=2`，
  读取输出 `Test Files` / `Tests` 行与退出码。
- **覆盖率**：`python3` 解析 `coverage/clover.xml` 的 `<metrics>` 属性
  （statements / coveredstatements 等）。
- **基线**：`node scripts/gate.mjs --list` 看门禁分档，`--tier fast` 实跑 fast 档。

## 三、lytjs 当前 keel 版本缺陷（v3.4.11）

```
段3: LC_ALL=C XLIST="$HOTLIST"; xrun awk ...   ← 泄漏赋值
段4: *[A-Z]*                                   ← locale 依赖 glob
钩子: *[A-Z]*                                  ← 同病
```

修复见 keel v3.4.13/v3.5.0：段3 改 `XLIST="$HOTLIST"; LC_ALL=C xrun awk`
（LC_ALL 作命令前缀），段4 与钩子改字母表展开
`*[ABCDEFGHIJKLMNOPQRSTUVWXYZ]*`。

## 四、耗时与预算

| 操作 | 耗时 |
|---|---|
| keel-lint（lytjs，55 篇） | 2s |
| test-lint（lytjs） | ~10s |
| lytjs 全量测试（8436 用例） | 323.6s（5.4 min） |
| lytjs fast 门禁（11 项） | 11.6s |

keel 300s lint 预算在 lytjs 规模下余量极充足（2s vs 300s）。
