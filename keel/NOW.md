---
scope: now
status: active
last-verified: 2026-10-04
updated: 2026-10-04
keywords: [焦点, 交接, 能力边界, check-mcp-config, ADR0014]
---

# NOW · main

## 当前焦点

**第十四轮：查"判据没覆盖什么"——查出一处能力边界。**
`check-mcp-config` 对 `{"command":"bash","args":["-c","exit 7"]}` 判 **✅ 全部可达**，
实际 rc=7。**不是 bug，是规格的能力上限**，已写进 §9.5。
上一轮见 [NOW-history/](NOW-history/)（10-04 评估与竞品对比）。

## 本轮完成

- [x] **实测 `check-mcp-config` 五个边界**：无声明 rc=0；command 不在 PATH 正确报；
      JSON 坏 / mcpServers 空 / 缺 command 均正确提示
- [x] **查出判据能力边界**：判据只证"可执行文件存在"，证不了"server 能启动"（MCP 是
      stdio 子进程，要真验得拉起来发 initialize，超出 lint 范围）。**未改判据**，
      边界写进 §9.5 + 登记 P3 坑
- [x] 索引按 §7.3 重整：15 条坑的症状列削到"最短可 grep 特征"（细节留在坑文件）
- [x] 38/38 自测 PASS · §9.3 逐字一致 · 两仓 lint 0 fail

## 未完成 / 半途

- [ ] **ADR 0014 待双签**：stderr 判据 + 豁免白名单
- [ ] 遵守率无真实基线；零外部采用——**只能等时间与第二个人**
- [ ] 语义检索接入：需先有真实用户

## 下一步（按优先级）

1. 走 `scripts/release.sh --apply` 发 v3.4.3
2. 找 1–2 个真实用户跑 `install.sh --with-anchor`
3. 拿到双签后执行 ADR 0014

## 阻塞

| 卡在 | 解锁条件 | 绕行 |
|---|---|---|
| 遵守率无真实基线 | 提交累积数周 | 假项目只验机制 |
| 外部采用证据 | 时间 + 真实用户 | 公网 v3.4.2 已验可装可裁剪 |
| ADR 0014 判据变更 | **owner + 双签** | 提案已写好 |
