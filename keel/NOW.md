---
scope: now
status: active
last-verified: 2026-11-06
updated: 2026-11-06
keywords: [P0 修复, sha256 绑定, 采用方全绿, 冷区, CHANGELOG 副本]
---

# NOW · main

## 当前焦点

**第十九轮：P0-1~P0-3 三条「假绿」修复，三批小步提交。**
第十八轮（M10 分支覆盖 + 发布两仓 tag）见 git 历史。

## 本轮进度

- [x] **P0-1**：`provenance.checks_sha256` 4 个值恒 null 且校验器放行。
      `verify.py` 改拼 `KEEL` 路径；`check-verify-report.py` 增 `_valid_sha`，
      null / 非法一律判死；selftest 27→28。负控：报告全 null 必须 FAIL。
- [x] **P0-2**：采用方无 DESIGN 时 DOC/PROSE 跳过，本地仍打印全绿。
      新增 SPEC-DIGEST（复用 `checks/manifest.tsv`，不新建真源）；汇总改三态
      （通过 / 跳过 / 失败分列）；负控 m04：改判据脚本必须红。
- [x] **P0-3**：冷区目录计数未豁免 + 有徽章缺根 CHANGELOG 静默放行。
      `find` 聚合处过滤 `archive/`、`NOW-history/`；缺副本改 `fail_msg`；
      用例 51（冷区 21 文件 rc=0）/ 52（有徽章无副本必须报错）；补根 CHANGELOG。
- [x] 改 `keel-lint.sh` 已同步 DESIGN §9.3 代码块（逐字一致）
- [x] **未做**：不改判据口径、不动预算数字；L4 元检查变异仍延后

## 实测

- 每批全量 verify 0 fail：批1 **155/0/8**（18:41）、批2 **160/0/8**（18:56）、
  批3 **162/0/8**（03:18；8 跳过 = test-faults 7 + macOS 大小写 1）
- test-lint：**62 项 = 52 用例 + 4 元检查用例 + 6 元检查**；
  61 通过 / 1 跳过 / 0 失败（两仓同）
- 接线 **27/27 · 25/25**；变异 **16/16**；账本 23/24（95.8%）
- lint 两侧 rc=0；provenance：4/4 判据 sha256 已记录
- 待决：复核 §9.1-19 与「缺引擎只 warn」无规格冲突，未改实现

## 下一步

1. 补 §9.1-2 其余分支（缺 frontmatter / 未闭合 / 缺 scope·status·last-verified）
2. §9.1-16 钩子不可执行、§9.1-12 frozen 新增契约、§9.1-19 缺「升级完成」行
3. L4：fixture 工厂 + 对 DOC/LOCALE/PROSE/INVOKE 各造 1 个实现级变异体

## 阻塞

| 卡在 | 解锁条件 | 绕行 |
|---|---|---|
| Windows 运行时未验证 | 可跑 bash 的 Windows | 静态判据 + 三档结论 |
| 外部采用为零 | 真实用户安装并使用 3 轮 | 无（不靠改代码解决） |
