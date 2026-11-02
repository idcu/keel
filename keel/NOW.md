---
scope: now
status: active
last-verified: 2026-11-03
updated: 2026-11-03
keywords: [焦点, 跨平台, Windows, 断点恢复, 真实故障, 磁盘满]
---

# NOW · main

## 当前焦点

**第十轮：Windows 第三平台 + 真实故障下的 `--resume`；发 v3.8.0。**
Windows **无可用运行时**，只到「静态守卫已加但未运行」档；真实故障 3/3 通过，
并暴露 3 处升级引擎缺陷（已修）。第九轮见 [history](NOW-history/2026-11-02-分发断层根治.md)。

## 本轮进度

- [x] Windows 途径探测：UTM/Parallels/VMware/VBox 无 VM、无云凭据、GitHub 镜像只读
      （push 无凭据）、无 wine/msys2、Docker 是 linux → **运行时不可用**
- [x] 静态守卫：lint §15（CRLF + 大小写冲突）；用例 43/44；INVOKE 第 4 形式（空格+中文）
- [x] 真实故障：`test-faults.py` 3/3（磁盘满备份/apply、断网在线失败 + 离线成功）
- [x] 修 3 处：pending 写入双失败静默、写文件失败被忽略且会截断执行中脚本（temp+mv）、
      `.keel-new.*` 残留清理
- [x] 记录：`keel/archive/windows-gitbash-audit-2026-11-03.md`、
      `keel/archive/real-faults-2026-11-03.md`；坑库按 §7.3 沉降后新增 P0 条目

## 下一步

1. 有 Windows 运行时后：跑 test-lint / test-upgrade / install + 升级 + `--resume` 端到端
2. 找第二个采用方样本，拆掉「单样本」边界
3. gate 阶段磁盘满、只读文件系统（EROFS）可补进 test-faults

## 阻塞

| 卡在 | 解锁条件 | 绕行 |
|---|---|---|
| Windows 运行时未验证 | 一台可跑 bash 的 Windows（VM / 云 / Actions 写权限） | 静态守卫 + 文档三档结论，不宣称支持 |
