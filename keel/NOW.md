---
scope: now
status: active
last-verified: 2026-11-04
updated: 2026-11-04
keywords: [判据, 覆盖率, 账本, 3.13.0]
---

# NOW · main

## 当前焦点

**第十五轮：判据覆盖率账本（快赢 2）落地；发 v3.13.0。**
第十四轮（矩阵补两格 + 复评）见 git 历史。

## 本轮进度

- [x] 新增 `checks/verify/checks-ledger.py`：§9.1 的 19 条判据单一登记；
      覆盖状态从 `test-lint.py` 的 `CASES` 自动推导，不维护第二份手写表
- [x] `verify-report.json` 增 `checks_ledger`；`check-verify-report.py` 增 3 个判死样例（8 → 11）
- [x] 账本自检 7 例，含「删掉 §9.1-19 的 4 条用例 → coverage 变 none」反向验证
- [x] 两仓内核同步 + manifest 新增 kernel 行；DESIGN §12.3、ADR 0002 修订

## 实测

- 判据覆盖：**18/19 有负例（94.7%）**；`coverage=0` 仅 §9.1-15（项目扩展位）
- 单列：§9.3 预算检查 1 条有负例；5 个元检查只有 2 个进 test-lint 自测分母
- 账本暴露两处散文不一致：DESIGN「39 例 fail」实测 38（已改）；
  test-lint 自报「2 元检查」实为 5（DOC / LOCALE / PROSE 未进分母）
- 全量：**109 通过 / 0 失败 / 1 跳过（未验证）**（macOS；跳过 = 用例 44）
- 首次复跑 `lint` 曾失败但清单只有状态没有原因 → `verify.py` 失败时保留
  `output_tail`（最后 12 行）；失败必须留证据
- 发布：v3.13.0（starter 先推 → 项目仓；tag 双向核对；发布后冒烟）

## 下一步

1. 快赢 1：`verify-report.json` 最小 provenance（commit / dirty / checks_sha256）
2. 主攻：判据变异测试（19 项 × ≥1 变异体，抓取率 ≥90%）
3. 外部采用仍为 0：所有「带分母」指标的分母都只是单仓数据

## 阻塞

| 卡在 | 解锁条件 | 绕行 |
|---|---|---|
| Windows 运行时未验证 | 可跑 bash 的 Windows | 静态判据 + 三档结论 |
| 无 Docker 真故障未跑 | 有 Docker 的机器 | 清单显式记 SKIP（未验证） |
| 外部采用为零 | 真实用户安装并使用 3 轮 | 无（不靠改代码解决） |
