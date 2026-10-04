---
scope: now
status: active
last-verified: 2026-10-04
updated: 2026-10-04
keywords: [焦点, 交接, 工具实测, keel-lite, MCP版本, to_epoch]
---

# NOW · main

## 当前焦点

**第十二轮：把"没人测过的工具"逐个实测。**
本轮清掉三件不依赖外部用户的事：`to_epoch` 纯 shell 化（65s）、
**`keel-lite --apply` 顺序 bug**、**MCP 版本号不再硬编码**（原 3.1.0）。
上一轮见 [NOW-history/](NOW-history/)（10-04 评估与竞品对比）。

## 本轮完成

- [x] **`to_epoch` 纯 shell 化**：`date` 每次跑两次（BSD 失败再试 GNU，~250ms）
      → 改 Howard Hinnant days_from_civil，**对 23 个日期与 `date -u -d` 逐字对照**
      （含 1900/2100 非闰年世纪）。新旧版对同一 fixture 输出**逐字相同**
      （`stale(2468d)`）。**65s，余量 4.62×**
- [x] **修 `keel-lite.sh` 一个真 bug**：它**先删目录后剥 INDEX 路由行**，导致
      §9.1-4 把 6 个文档判成孤儿、脚本 `exit 1`——**裁剪反而把项目弄红**，而用户
      只照 README 跑了一条命令。改为「先算新 INDEX → 再删 → 最后替换」；
      实测 39 → 19 个 md，裁剪后 lint ✅（5s）
- [x] **MCP 实测**：内置自测 8/8 PASS；**发现 `SERVER_VERSION` 硬编码 "3.1.0"**
      → 改读 `INDEX.md` 的 `keel-version`，读不到报 `0.0.0-unknown`
- [x] `check-mcp-config.sh` 实测：未声明检索增强时恒 exit 0（合规）
- [x] 两仓 lint 0 fail + 38/38 自测 + §9.3 逐字一致；新坑 2 条已登记

## 未完成 / 半途

- [ ] 段 11 三段式仍逐文件 3 次 grep（约 3.6s）—— 批量化须走"先滤清单再 xargs"
- [ ] 未提交、未发版（本轮改了模板 = 改了发布仓）
- [ ] 遵守率无真实基线；零外部采用证据；stderr 判据项需 owner + 双签

## 下一步（按优先级）

1. 走 `scripts/release.sh --apply` 发 v3.4.1
2. 找 1–2 个真实用户跑 `install.sh --with-anchor`（解锁采用 + 基线）
3. 段 11 批量化（量小，可搭车下一版）

## 阻塞

| 卡在 | 解锁条件 | 绕行 |
|---|---|---|
| 遵守率无真实基线 | 提交累积数周 | 假项目只验机制 |
| 外部采用证据 | 时间 + 真实用户 | 公网 `clone --branch v3.4.0` 已验可装 |
| 改判据（stderr 项等） | **owner + 双签** | 不改，写进本表 |
