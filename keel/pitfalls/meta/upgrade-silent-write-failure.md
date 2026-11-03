---
scope: meta
status: active
severity: P0
last-verified: 2026-11-03
triggers: 3
keywords: [升级, 磁盘满, ENOSPC, 静默成功, 原子写, 截断]
---

## 症状

- tmpfs 写满后升级仍打印「✅ 升级完成」、退出码 0，pending 停在上一阶段
- 覆盖 `keel-upgrade.sh` 自身时文件被截成 0 字节（正在执行的 bash 读到残片）
- 记进 pending 的 sha256 是截断残片的哈希 → `--resume` 校验必失败

## 根因

写文件分支的退出码没人看：`cp` / `sed -i` / `printf` 直接覆盖目标，
ENOSPC 时留下半文件并继续；状态文件与实际磁盘不一致（假成功）。

## 正解

- 每个写动作都判退出码，失败即 `die 2` 并提示 `--resume` / `--rollback`
- 一律 temp + `mv` 原子替换：执行中的旧 inode 不被截断，失败只留可清理临时文件
- pending 写入失败必须显式失败，且**保留上一版状态**（清 temp、不 rename）
- 判死：`test-faults.py` 用真 tmpfs ENOSPC 断言 rc=2、无 0 字节脚本、续跑逐字节一致
- 门禁阶段盘满同样不得判为通过（日志写不下是 fail，不是 pass）
