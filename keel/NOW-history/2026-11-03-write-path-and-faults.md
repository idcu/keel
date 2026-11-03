---
scope: history
status: archived
last-verified: 2026-11-03
keywords: [写失败, atomic_write, 终态校验, EROFS, 配额, 断网, v3.9.0, v3.9.1]
---

# NOW 归档 · 2026-11-03 · 写路径与故障覆盖（第十一轮）

## 当前焦点

「写失败却报成功」机制化 + 四类故障收官；发 v3.9.0 → 冒烟后发 v3.9.1。
第十轮的 Windows / 真实故障见
[2026-11-03-windows-and-real-faults.md](2026-11-03-windows-and-real-faults.md)。

## 本轮进度

- [x] 升级引擎收敛为单一写路径：`atomic_write`（temp → sync → 读回哈希 → rename → die）
      + `record_file` 写后复核；kernel / additive / merge / manifest / pending / restore.sh 全走它
- [x] `final_verify`：版本 / pending 清除 / 备份可回滚 / manifest 一致 / 无临时残留，5 项全过
      才允许打印「✅ 升级完成」
- [x] lint 第 16 段（§9.1-19）静态判据：裸 `cp`/`mv`/`install`、`sed -i`、重定向写 `$TARGET`；
      核心区间 + `# keel-write:ok` + heredoc 三类豁免
- [x] test-lint 用例 45–48（各配判死断言）：口径 46/46 → **50/50**
- [x] test-faults 新增 gate 满 / EROFS（preflight + apply 中途）/ 配额部分写入 / 半断网：
      3 → **7 例**
- [x] 记录：`keel/archive/real-faults-round2-2026-11-03.md`
- [x] 发布 v3.9.0 后做真实冒烟（`install.sh --ref` + v3.8.0 升级中断 + `--resume`），
      照出 4 条缺陷（备份须含 restore.sh 的误判 / 先清 pending 后校验 / 续跑 `from` 被改写 /
      备份目录同秒撞名）→ v3.9.1 全修，正好也是 test-faults 偶发 6/7 的根因

## 下一步（当时）

1. 有 Windows 运行时后：跑 test-lint / test-upgrade / install + 升级 + `--resume` 端到端
2. 找第二个采用方样本，拆掉「单样本」边界
3. test-faults 的 EROFS 依赖 `--cap-add SYS_ADMIN`：无该能力的 CI 上会失败而非 SKIP，
   需要时再补能力探测（v3.10.0 已补）

## 阻塞

| 卡在 | 解锁条件 | 绕行 |
|---|---|---|
| Windows 运行时未验证 | 一台可跑 bash 的 Windows（VM / 云 / Actions 写权限） | 静态守卫 + 文档三档结论，不宣称支持 |
