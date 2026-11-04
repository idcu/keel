---
scope: now
status: active
last-verified: 2026-11-04
updated: 2026-11-04
keywords: [接线, 变异, 入口矩阵, 3.15.0]
---

# NOW · main

## 当前焦点

**第十七轮：入口级接线审计（L1）+ 变异测试试点（L2）；发 v3.15.0。**
第十六轮（元检查进分母 + provenance）见 git 历史。

## 本轮进度

- [x] `checks/wiring/test-wiring.py`：26 个 CLI/发布入口 × 24 条判死用例，
      矩阵进 verify-report.json 的 `wiring`；`wiring=0` 与 `n/a` 分开
- [x] 三条 v3.14.0 缺陷回归：W16 无 `--claims` 的 commit 不符、W17 `<repo>/keel/`
      布局、W18 `--claims/--summary` 与含混文案；删任一修复对应用例即红
- [x] `checks/mutation/`：9 条 §9.1 判据 × 16 变异体 / 3 类算子
- [x] wiring 抓出 1 条新缺陷：`verify.py --suites <子集>` 在
      `mutation=None` 时走 `else` 分支 TypeError（W14 判死，已改 `elif`）
- [x] verify 套件 8 → 9；清单自检 20 → 27；两处进清单、变异不进发布门禁
- [x] CI：项目仓 workflow 增加 wiring（门禁）与 mutation（`continue-on-error`）

## 实测

- 接线：**26/26 入口有判死用例 · 24/24 用例通过 · wiring=0: 0 · n/a: 0**；
  全套件内 156.4s（`--jobs 4`），单跑 161–173s
- 变异：**15/16 被杀（93.8%）**，存活 M10（§9.1-10 的 INDEX/CONSTITUTION 分支，
  用例 17 只删 NOW.md）；实测 47.1s
- 门禁：lint 两仓 0 fail；test-lint **53/53**；账本 11/11；清单自检 **27/27**
- 全量 verify：**158 通过 / 0 失败 / 1 跳过（未验证）**，31:59
  （跳过 = test-lint 用例 44，macOS 大小写不敏感卷；Linux 下 53/53）
- 发布：v3.15.0；先 starter 后项目仓；tag 双向验证 + 真安装冒烟

## 下一步

1. 补 §9.1-10 的 INDEX/CONSTITUTION 分支用例，把 M10 杀掉（下一轮首件）
2. 变异扩到 §9.3 meta（DOC/LOCALE/PROSE）与边界值，不追分只找盲区
3. test-upgrade 1229s 占全量 64%，考虑安全并行（断言不减）
4. 外部核对 provenance / 外部采用仍为 0——带分母指标仍只是单仓数据

## 阻塞

| 卡在 | 解锁条件 | 绕行 |
|---|---|---|
| Windows 运行时未验证 | 可跑 bash 的 Windows | 静态判据 + 三档结论 |
| 外部采用为零 | 真实用户安装并使用 3 轮 | 无（不靠改代码解决） |
