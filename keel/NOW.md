---
scope: now
status: active
last-verified: 2026-11-04
updated: 2026-11-04
keywords: [矩阵, 3.5.0, 3.10.0, SKIP, 评估]
---

# NOW · main

## 当前焦点

**第十四轮：矩阵补 3.5.0 / 3.10.0 两格 + CI 跳过可见性；按同一标尺复评并出新报告；发 v3.12.0。**
第十三轮见 [history](NOW-history/2026-11-03-verify-honesty.md)。

## 本轮进度

- [x] 矩阵引擎格加 3.10.0（两阶段引导起点）；`install_cell` / `make_matrix_repo` 参数化，
      install 用例扩为 3.4.11 + 3.5.0（此前硬编码单一版本 = 只有一个旧世界样本）
- [x] CI：`checkout` 加 `fetch-depth: 0`；test-faults 与矩阵两步把 SKIP 行与原因写进
      `GITHUB_STEP_SUMMARY`，本地以 `KEEL_SKIP_DOCKER=1` / `KEEL_MATRIX_OFFLINE=1` 模拟验证
- [x] 全量清单 3.12.0，归档 `keel/archive/verify-report-3.12.0.json`
- [x] 新报告 `KEEL-全维度评估与竞品对比-20261104.md`（同 9 维同口径，74 → 75/90）

## 实测

- 矩阵串行 9/0/0，813.7s：3.5.0 145.4s、3.10.0 131.3s、3.6.1 163.2s；**无新增缺陷**
- lint 3.87/3.93/4.07s（load 12.68）；同机 24h 前 1.6s，2.4× 差系主机争用，非回归
- 全量：PENDING-VERIFY
- 评估：唯一涨分「分发与门面」8→9；采用度 0 star/0 fork/0 issue/0 PR 不涨

## 下一步

1. 第二个采用方样本 + 遵守率分母（唯一能推 7 分的方式）
2. Windows / Git Bash 运行时实测（当前只有两条静态判据）
3. 语义检索接入位实接一次并度量「grep 漏、语义中」

## 阻塞

| 卡在 | 解锁条件 | 绕行 |
|---|---|---|
| Windows 运行时未验证 | 可跑 bash 的 Windows | `docs` 三档结论 + 静态判据 |
| 无 Docker 真故障未跑 | 有 Docker 的机器 | 清单与发行说明显式记 SKIP（未验证） |
| 外部采用为零 | 真实用户安装并使用 3 轮 | 无（不靠改代码解决） |
