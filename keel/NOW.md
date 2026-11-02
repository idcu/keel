---
scope: now
status: active
last-verified: 2026-11-02
updated: 2026-11-02
keywords: [焦点, 分发断层, keel upgrade, manifest, v3.6.0]
---

# NOW · main

## 当前焦点

**第六轮：根治分发断层。** 上轮发现 v3.4.11 采用方拿不到 v3.5.0 的 locale 修复
（install.sh 白名单漏 test-lint.py + 已存在文件一律保留），只能手工同步。
本轮做 `keel upgrade`：manifest 驱动、门禁对比、失败回滚、幂等，并用 lytjs 真跑回归。

## 本轮完成

- [x] **主线一** `keel-upgrade.sh` + `checks/manifest.tsv`（四分类真源：
  kernel 覆盖 / merge 只改版本行 / preserve 不动 / additive 父目录在才补）
- [x] 升级前后各跑 lint + test-lint + 预算固定成本；失败整目录还原（exit 3）；
  备份 `.keel-backup/`（保留 3 份 + restore.sh），不用 git 还原（怕吞未提交自定义）
- [x] 幂等：已是目标版本明说「无需升级」；`--force` 才重放
- [x] install.sh 已有分支**委派**给升级引擎（≤3.5.0 的引导路径 = 重跑 install）
- [x] 自测 `test-upgrade.py` 10 例（正常/跨版本/保留自定义/失败回滚/幂等/…），10/10、51s
- [x] ADR 0020 + DESIGN §12.3 四分类 + CHANGELOG 3.6.0；CI 与 release.sh 接入自测
- [x] 两仓门禁：lint 0 fail；test-lint 43/43（starter 10.1s / 项目 9.7s）
- [x] **主线二** lytjs 真跑回归（临时副本，未碰作者在研提交）：3.4.11→3.6.0
  一条命令 exit 0；内核 21/21 与模板逐字节一致、46 个自定义文件全保留；
  与上轮手工同步相比只多 v3.6.0 新增件；引擎 20.5s（两次 test-lint 约 18s）；
  幂等复跑「✅ 已是 v3.6.0，无需升级」。详见 [回归报告](archive/keel-upgrade-regression-2026-11-02.md)

## 未完成

- [ ] 主线三 五分钟接入 quickstart
- [ ] 外部采用度仍为零（推广动作，非代码）

## 下一步

1. 写 `QUICKSTART.md`（安装/首跑/最小自定义/升级回滚/排错），命令实跑通过
2. lytjs 主仓择机用 `keel upgrade` 跟进到 v3.6.0（等作者推送在研提交后）

## 阻塞

| 卡在 | 解锁条件 | 绕行 |
|---|---|---|
| 无 | —— | —— |
