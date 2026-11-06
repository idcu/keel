---
scope: now
status: active
last-verified: 2026-11-06
updated: 2026-11-06
keywords: [P0-c, 变异引擎, 算子, 等价, 复算]
---

# NOW · main

## 当前焦点

**第二十一轮：P0-c 判据变异产品化（算子可插拔 / 清单可枚举 / 杀伤率进账本 / 结果可复算）。**

## 本轮进度

- [x] **批1 `146c783`**：DESIGN §12.3 写入口径；`operators.py` 四算子；
      `sites.tsv` 16 位点；`mutants.tsv` 绑定 target/manifest sha256。
- [x] **批2 `e036761`**：`mutation.py` 重写（--enumerate/--run/--verify/--recompute/--negctl/--report）；
      `exemptions.tsv`；ledger v2 增 7 个 mutation 字段；verify.py 把存活判 FAIL。
- [x] **全量实测**：16/16 被杀、0 存活、0 等价、0 豁免、0 无效；
      58s@1 → 25s@4 → 21s@8（8 并行 2.8×）。
- [x] **负控 3/3 判死**：已杀改等价 / 变异数写死 / 存活报成已杀（重跑比对）。
- [x] **对外报告** `mutation-report.json`（含复算命令与期望哈希）；`--verify` 秒级自校验。
- [x] **未做**：§9.3 meta 判据变异（需 fixture 工厂，下一轮）；不改判据口径/预算。

## 实测

- manifest sha `239400ce…`；keel-lint sha `61eacb5b…`
- ledger v2 sha `c66e77a5…`；D1 18/19、D2 22/23、D3 23/24（口径未变）
- lint 0 fail；test-lint 61/1/0；ledger 自检 15/15；接线 27/27·25/25
- 批2全量 verify：182 通过 / 0 失败 / 8 跳过；变异行 PASS（16/16）
- 干净 clone（`e036761`）：--enumerate/--verify 一致，--recompute 18.4s@8，
      16/16 杀、0 存活，清单 sha `239400ce…`、脚本 sha `61eacb5b…`
- 坑 `mutation-catalog-drift.md`（INDEX 2995B）

## 下一步

1. §9.3 meta 变异：DOC/LOCALE/PROSE/SPEC 各 1 个实现级变异体
2. 位点扩容：§9.1-2 其余分支、§9.1-16 钩子不可执行
3. 豁免到期巡检：把 expires 纳入 lint 告警

## 阻塞

| 卡在 | 解锁条件 | 绕行 |
|---|---|---|
| Windows 运行时未验证 | 可跑 bash 的 Windows | 静态判据 + 三档结论 |
| 外部采用为零 | 真实用户安装并使用 3 轮 | 无（不靠改代码解决） |
