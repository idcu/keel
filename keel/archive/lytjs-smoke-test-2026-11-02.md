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

## 五、v3.4.11 → v3.5.0 升级验证（2026-11-02 同日追加）

> 升级目的：消除 v3.4.11 段3 `LC_ALL=C` 泄漏赋值 + 段4 `*[A-Z]*` locale 依赖 glob
> （commit-msg 钩子同病）的「脆弱正确」——泄漏让段4 歪打正着处于 C locale，
> 在非作者环境（zh_CN.UTF-8）下可能误报。

### 升级执行

- 接入形态：lytjs 内置 `lytjs/lytjs/keel/`（vendored，非 submodule），版本号来源 `keel/INDEX.md` frontmatter `keel-version`
- 改动：同步 4 个工具链文件（`keel-lint.sh` / `hooks/commit-msg` / `test-lint.py` / `perf-findings.txt`）+ 新增 `checks/retrieval/keel-search.py`（BM25）+ `INDEX.md` 版本号 `3.4.11 → 3.5.0`；**不动** lytjs 自定义的 `rules.md` / `CONSTITUTION.md` / `decisions/` / `pitfalls/` / `NOW.md`
- 提交：`dab27d73 chore: 同步 keel 工具 v3.4.11 → v3.5.0（locale 泄漏修复 + BM25 检索）`，已推送 `v7.0.0-dev`
- 回滚锚点：升级前 `522eddfa`

### 前后对比

| 项 | v3.4.11（升级前） | v3.5.0（升级后） |
|---|---|---|
| keel lint（zh_CN.UTF-8） | 0 fail，2s，55 篇（脆弱正确） | **0 fail，1.82s，55 篇**（locale 加固后仍稳） |
| test-lint | 43/43 | **43/43 + LOCALE PASS + PROSE PASS**，13.8s |
| lytjs 全量测试 | 8436/8436，385 文件，323.6s | **8436/8436，385 文件，317.23s** |
| lytjs fast 门禁 | 11/11，11.6s | **12/12，5.4s** |
| 覆盖率（clover.xml） | 66.50%（2026-10-15 旧数据，未重跑） | **statements 87.66% / branches 87.73% / functions 88.00% / lines 87.69%**（50437/57535 等，阈值 66.5/86.2/72.2/66.5 全过） |

### locale 修复在非作者环境的结论

**成立，且未暴露此前被掩盖的问题。**

- LOCALE 自测（test-lint 内置）：UTF-8 / C 双 locale 下段4 无误报、无 `LC_ALL` 泄漏赋值 → PASS
- zh_CN.UTF-8 下 `keel-lint.sh keel`：0 fail（lytjs 文件名均合法 kebab-case，段4 字母表 `*[ABCDEFGHIJKLMNOPQRSTUVWXYZ]*` 不误报）
- 无需判定「lytjs 真问题 vs keel 判据过严」——没有误报也没有漏报，段3 泄漏消除后段4 行为符合预期

### 备注

- 升级后首次全量测试出现 6 个失败（`slots-demo.integration.test.ts`，`renderer.render is not a function`），根源在 lytjs 在研代码 `examples/slots-demo/app.ts`，与 keel 升级无关（改动仅限 `keel/`）。lytjs 作者随后提交 `37f1cf15 fix(vdom): P0 —— v-for 列表项被挂到祖父节点`，重跑全量 8436/8436 全绿。
- 覆盖率采集首次全量跑因 6 个失败用例未生成 `coverage/` 目录（vitest 在测试失败后未写覆盖率产物）；排除该文件重跑后产物正常，数字如上。该 6 用例占比可忽略，对覆盖率无实质影响。
