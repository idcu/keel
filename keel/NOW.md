---
scope: now
status: active
last-verified: 2026-11-04
updated: 2026-11-04
keywords: [判据, 覆盖率, 元检查, provenance, 3.14.0]
---

# NOW · main

## 当前焦点

**第十六轮：分母扩到元检查（L1）+ 清单绑定 provenance（L2）；发 v3.14.0，补 3.14.1。**
第十五轮（判据覆盖率账本）见 git 历史。

## 本轮进度

- [x] `test-lint.py` 增 `META_CASES`：DOC / LOCALE / PROSE 各一条判死用例；
      自测分母 50 → 53（48 用例 + 3 元检查用例 + 2 元检查）
- [x] 账本分母 19 → 22（含元检查）→ 23（含 §9.3-BUDGET）；三口径同屏打印
- [x] `§9.3-BUDGET` 给正式编号（用例 20 已判死）；`§9.1-15` 仍不给——
      给不了判死用例就不登记
- [x] `verify-report.json` 增 `provenance`（commit / dirty / 4 文件 sha256 /
      平台 / locale / 时间）；`release.sh` 用 `--repo` 校验，三种不一致都拦
- [x] `check-verify-report` 自检 11 → 17，含 4 条真 git 仓库负控
- [x] 3.14.1 修两处「判据存在但没被调用」：provenance 校验只在 claims 路径生效
      （`--report --repo` 静默 exit 0）、`--repo` 拼路径少一层 `keel/`；
      拆 `structure_problems()` + 3 条 CLI 级用例，自检 17 → 20

## 实测

- 判据覆盖：**22/23（含元检查与预算检查，95.7%）**；含元检查 21/22（95.5%）；
  仅 §9.1 18/19（94.7%）；`coverage=0` 仍只有 §9.1-15
- 负控：commit 不符、自称干净、sha256 已变、旧清单、只给 `--repo`，全部判死
- 发布：v3.14.0 → 补 v3.14.1（先 starter 后项目仓；tag 双向）；冒烟 **125/0/1**，
  新 clone 账本 11/11 + 自检 20/20，`install --ref v3.14.1` 落 3.14.1 且 lint 通过

## 下一步

1. 变异测试：19 项 × ≥1 变异体，抓取率 ≥90%——账本证明「有用例」，变异证「用例有效」
2. 外部核对 provenance：CI 二次构建或独立签名，才谈得上「可信」
3. 外部采用仍为 0：所有带分母指标的分母都只是单仓数据

## 阻塞

| 卡在 | 解锁条件 | 绕行 |
|---|---|---|
| Windows 运行时未验证 | 可跑 bash 的 Windows | 静态判据 + 三档结论 |
| 无 Docker 真故障未跑 | 有 Docker 的机器 | 清单显式记 SKIP（未验证） |
| 外部采用为零 | 真实用户安装并使用 3 轮 | 无（不靠改代码解决） |
