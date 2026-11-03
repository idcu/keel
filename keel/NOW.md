---
scope: now
status: active
last-verified: 2026-11-03
updated: 2026-11-03
keywords: [验证清单, SKIP, 矩阵, 3.6.1]
---

# NOW · main

## 当前焦点

**第十三轮：验证诚实性机制化（test-faults 三环境、矩阵补 3.6.1、verify-report 进发布链路）；发 v3.11.0。**
第十二轮见 [history](NOW-history/2026-11-03-bootstrap-and-matrix.md)。

## 本轮进度

- [x] test-faults 五态环境探测（ok/disabled/no-binary/no-daemon/non-linux），SKIP 带原因，
      汇总单列「N 跳过（未验证）」；默认跳过 `exit 0`，`KEEL_FAULTS_REQUIRE_DOCKER=1` 才红；
      6 条判死自检（伪 PASS / FAIL 行 / LINT≠0 / 跳过策略）
- [x] 矩阵默认格补 3.6.1；旧引擎无 pending/钩子时按能力探测改走 `install.sh` 引导验续跑/回滚
- [x] 修复恢复缺口：`install.sh` 检测 `.keel-upgrade.pending` 后交给新引擎 `--resume`
- [x] 新增 `checks/verify/`：`verify-report.json`（套件/结果/跳过原因/用例数/耗时/环境/矩阵格）
      + `check-verify-report.py` 判据（8 样例自检）
- [x] `release.sh` 推送前跑清单、打印发行说明一节、校验 CHANGELOG 当前小节
- [x] 记录：`keel/archive/verify-honesty-2026-11-03.md`

## 实测

- 全量 verify：98/0/1（未验证），8 分 37 秒；跳过 = test-lint 用例 44（Windows 未验证）
- test-faults：① 7/0/0；② no-binary 0/0/7 跳过；③ no-daemon 0/0/7 跳过（严格模式 rc 1）
- 矩阵：串行 170s（3.6.1 +57s）；`KEEL_MATRIX_JOBS=4` 68s，7/0/0
- 文案负控：伪造 1 例 SKIP 清单 + 说明写 0 跳过 → 判死
- 排障：首次全量 68/30 是 manifest 哈希未重算；`--check-manifest` 定位，重算后 98/0/1
- 解析器曾把 test-lint 打印的 SKIP 吞成 0 跳过，已修并重跑
- 发布：v3.11.0 已推（tag peeled 4016ed4）；冒烟 v3.8.0→3.11.0，覆盖 27 / 保留 47

## 下一步

1. 无 Docker 环境复跑真实故障注入（当前只验证 SKIP 语义）
2. 矩阵补 3.5.x / 3.10.x；第二个采用方样本
3. Windows / Git Bash 运行时

## 阻塞

| 卡在 | 解锁条件 | 绕行 |
|---|---|---|
| Windows 运行时未验证 | 可跑 bash 的 Windows | 静态守卫 + 文档三档结论 |
| 无 Docker 真故障未跑 | 可装 Docker 的 Linux / CI | 清单与发行说明显式记 SKIP（未验证） |
