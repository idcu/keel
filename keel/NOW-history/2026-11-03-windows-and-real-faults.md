# NOW-history · 2026-11-03 · Windows 第三平台 + 真实故障（第十轮）

> 由 `keel/NOW.md` 轮转而来（§7.3「沉」）。当前焦点见 [NOW](../NOW.md)。

## 焦点

Windows / Git Bash 第三平台能不能支持；以及不用故障注入、在**真实**磁盘满 / 断网下
`--resume` 是否仍成立。

## 完成

- **Windows 途径探测**：UTM/Parallels/VMware/VBox 无 VM、无云凭据、GitHub 镜像只读
  （push 无凭据）、无 wine/msys2、Docker 是 linux → **运行时不可用**
- **静态守卫**：lint §15（CRLF + 大小写冲突）；用例 43/44；INVOKE 第 4 形式（空格+中文）
- **真实故障 3/3**：`test-faults.py`（磁盘满备份 / 磁盘满 apply 后续跑逐字节一致 / 断网
  在线失败 + `--from` 离线成功）
- **修 3 处真缺陷**：pending 写入双失败静默、写文件失败被忽略且会截断执行中脚本
  （temp+mv）、`.keel-new.*` 残留清理
- **记录**：`keel/archive/windows-gitbash-audit-2026-11-03.md`、
  `keel/archive/real-faults-2026-11-03.md`；坑库按 §7.3 沉降后新增 P0 条目
- **发布**：v3.8.0（先 starter 后项目仓，annotated tag + `ls-remote` 双向验证）

## 未完成 / 下一步

1. Windows 运行时仍缺：只能停在「静态守卫已加但未运行」，不宣称支持
2. 第二个采用方样本未找到，「单样本」边界未拆
3. gate 阶段磁盘满、EROFS、配额部分写入、拉到一半断网 —— 本轮未覆盖
