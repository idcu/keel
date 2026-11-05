---
scope: now
status: active
last-verified: 2026-11-06
updated: 2026-11-06
keywords: [P0-4, 判据账本, 分母, 复算, 负控]
---

# NOW · main

## 当前焦点

**第二十轮：P0-4 判据账本可复算（D1/D2/D3），守住「带分母的遵守率」。**

## 本轮进度

- [x] **口径入规格** DESIGN §12.3：枚举真源 `checks/verify/criteria.tsv`；
      分母 = `counted=yes` 行数（不写常量）；PASS=有负例；SKIP（正例/无用例）
      **进分母不进分子**；EXCLUDED 必须有理由；§9.1 判据禁止 `counted=no`。
- [x] **账本落盘** `checks/verify/ledger.tsv`（每判据一行，含状态/证据/原因），
      生成物入库；`--check` 逐字节比对，手改/写死分母/删行都判死。
- [x] **复算入口** `checks-ledger.py --recompute`：打印完整分母 ID 清单、百分比、
      SKIP/EXCLUDED 原因与两份 sha256。
- [x] **23/24 缺项 = §9.1-15**（extension，内核不实现）：**尚未落地**，
      SKIP 但保留在分母，未按「合理排除」移出。
- [x] **未做**：不改判据口径、不动预算数字；模板同步 starter `71fa54a`。

## 实测

- 迁移前后数字不变：D1 **18/19=94.7%**、D2 **22/23=95.7%**、D3 **23/24=95.8%**
- `--recompute` rc=0：criteria sha `6b7cef7b…`、ledger sha `436932e0…`，与期望一致
- `--negctl` **3/3 判死**：①18 行却写死 D1=19；②三处删 §9.1-9 但 DESIGN 仍 19 行；
      ③DESIGN 20 行 vs 账本 19 行。三条均 rc=1
- 账本自检 **15/15**；批1全量 verify **166 通过 / 0 失败 / 8 跳过**
      （跳过 = test-faults 7 + macOS 大小写 1）
- test-lint **61 通过 / 1 跳过 / 0 失败**（62 项）；lint 0 fail；
      接线 **27/27·25/25**；变异 **16/16**
- 提交：项目 `17bb288`、模板 `71fa54a`；坑 `ledger-self-consistent.md`

## 下一步

1. 补 §9.1-2 其余分支（缺 frontmatter / 未闭合 / 缺 scope·status·last-verified）
2. §9.1-16 钩子不可执行、§9.1-12 frozen 新增契约、§9.1-19 缺「升级完成」行
3. L4：fixture 工厂 + 对 DOC/LOCALE/PROSE/INVOKE 各造 1 个实现级变异体

## 阻塞

| 卡在 | 解锁条件 | 绕行 |
|---|---|---|
| Windows 运行时未验证 | 可跑 bash 的 Windows | 静态判据 + 三档结论 |
| 外部采用为零 | 真实用户安装并使用 3 轮 | 无（不靠改代码解决） |
