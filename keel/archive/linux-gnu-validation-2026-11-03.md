---
scope: archive
status: done
last-verified: 2026-11-03
keywords: [linux, gnu, 验证, coreutils, busybox, 断点续跑, 权限]
---

# Linux / GNU 验证记录 · 2026-11-03

## 结论

Linux 全量跑通，`--resume` 在 GNU 下成立。三条基线全绿，并暴露出 **4 处真实缺陷**
（2 处跨平台、1 处仅缺工具时静默降级、1 处发布后才由冒烟照出的文档漂移），
前 3 处在 v3.7.3 修复，第 4 处在 v3.7.4 修复；没有发现 GNU 特有的
`stat` / `sed` / `mktemp` 参数不兼容。

## 环境

| 基线 | 镜像 | shell | coreutils / userland | libc | awk |
|---|---|---|---|---|---|
| A | `debian:bookworm-slim`（Debian 12） | bash 5.2.15 | GNU coreutils 9.1 | glibc 2.36 | mawk 1.3.4 |
| B | `debian:stable-slim`（Debian 13） | bash 5.2.37 | GNU coreutils 9.7 | glibc 2.41 | mawk 1.3.4 |
| C | `alpine:3.20` | bash 5.2.26 | busybox 1.36.1（stat/sed/find/awk 全是 busybox） | musl | busybox awk |
| 对照 | macOS 主机 | bash 3.2.57 | BSD stat / shasum | libSystem | BWK awk |

容器里装 `python3`（跑 test-upgrade / test-lint）与 `locales`（生成 zh_CN.UTF-8）。
C 基线是本轮唯一能拿到的第三套 userland；bash 3.2 在 Linux 上无法复现（发行版不再提供），
所以「更老 bash」这一项**未验证**。

## 方法

- `docker run -v /Volumes/Data/keel:/src:ro`：宿主仓库**只读挂载**，容器内 `cp` 到 `/work`
  再跑，宿主工作区全程未被写入。
- 容器间同步用 `COPYFILE_DISABLE=1 tar`，否则 macOS bsdtar 会带出 `._*` AppleDouble
  文件（实测污染 `checks/`，会让「未登记文件」提示失真，但**不是 Keel 缺陷**）。

## 实测（修复后，最终代码）

| 项 | Debian 12 | Debian 13 | Alpine/musl | macOS 对照 |
|---|---|---|---|---|
| lint（相对 / 绝对 / `.`） | 0.20s · 0/0/0 | 0.21s · 0/0/0 | 约 1s · 0/0/0 | 0 fail · 0/0/0 |
| test-lint `LC_ALL=C` | 4.32s · 44/44 | 4.43s · 44/44 | 4.00s · 44/44 | 9s · 44/44 |
| test-lint `zh_CN.UTF-8` | 4.57s · 44/44 | 4.65s · 44/44 | 4.00s · 44/44 | 11s · 44/44 |
| test-upgrade（19 例） | 42.03s · 19/19 | 41.68s · 19/19 | 32.00s · 19/19 | 119.6s · 19/19 |
| manifest 校验 | 69 行一致 | 69 行一致 | 69 行一致 | 69 行一致 |
| 权限比对（755→600） | 判死 | —— | —— | 判死 |

Alpine 的 lint 耗时只能秒级测：busybox 的 `date` 不支持 `%N`，亚秒数字是假的。

## 真实采用方链路（Debian 12）

| 步骤 | 结果 | 耗时 |
|---|---|---|
| `install.sh --ref v3.6.1` | rc=0 · 3.6.1 | 1.13s |
| 模板升级到 3.7.3 | rc=0 · 内核覆盖 21 / 保留 47 | 8.94s（含前后门禁） |
| 故障注入 `after:file:7` | rc=137 · stage=applying · 已完成 7 个 | 4.23s |
| `--resume` 续跑 | rc=0 · pending 清除 · 3.7.3 | 4.76s（不重新备份） |

升级后 lint 在相对与绝对两种入参下都 0 fail。

## 发布后冒烟（`install.sh --ref <tag>`）

发完 tag 在空目录真装一次，检查「分发链路」而不只是「仓库里的代码」：

| tag | 结果 | 耗时 | 结尾提示 |
|---|---|---|---|
| v3.7.3 | rc=0 · `keel-version: 3.7.3` · lint 0 fail · 自测 44/44 | 2.03s | ❌ 仍写「42 用例 + 1 元检查」→ 缺陷 4 |
| v3.7.4 | rc=0 · `keel-version: 3.7.4` · lint 0 fail · 自测 44/44 | 2.29s | ✅「必须全绿（数字以实际输出为准）」 |

## 发现与处置

### 缺陷 1（跨平台，高）：lint 入参形式改变判据

- 症状：`bash keel/checks/keel-lint.sh "$(pwd)/keel"` 与 `cd keel && bash checks/keel-lint.sh`
  （用法里写着的默认 `.`）会把**全部热区文档误报成孤儿**；starter 实测 28 条。
  只有 `keel-lint.sh keel` 这一种相对入参能过。
- 根因：段 9 把链接规范化后与 `find` 输出逐字比对，而 `norm()` 丢掉前导 `/` 与开头的 `.`
  （`/k/x` → `k/x`，`./x` → `x`）。
- 性质：**不是 GNU 专属**——macOS 上同样复现；Linux 只是以绝对路径调用才把它照出来。
- 修法：入参先 `pwd -P` 归一化为绝对路径；`norm()` 保留前导 `/`。
- 判死测试：test-lint 新增 INVOKE 元检查（相对 / 绝对 / `.` 三种入参各跑一次）；
  自测口径 43/43 → 44/44（42 用例 + 2 元检查）。
- 坑库：`worktree-eol-differs-from-main` 原写「传绝对路径全判孤儿」并建议用相对入参绕过，
  已改为「v3.7.3 已修」。

### 缺陷 2（跨平台，中）：环检测依赖 `tsort`，缺工具时判据消失

- 症状：Alpine/busybox 无 `tsort`，lint 只打一行 warn 就跳过循环引用检查；
  test-lint 的「引用成环」用例因此失去判据，升级门禁里连带失败。
- 性质：不是崩溃，是**判据静默失效**——比 fail 更危险。
- 修法：改用 awk 的 Kahn 拓扑排序（能消解全部节点即无环），彻底去掉外部依赖；
  顺带消掉 BSD/GNU `tsort` 的退出码差异。
- 判死测试：原有「引用成环」用例现在在三条基线上都要求 0 fail。

### 缺陷 3（跨平台，中低）：`cp -R` 受 umask 过滤，「回滚恢复权限」不无条件成立

- 症状：`umask 077` 下 `cp -R` 把 755 复制成 700（macOS 与 GNU 实测一致）。
  备份与回滚都用 `cp -R`，于是「恢复到升级前字节（含权限）」在严格 umask 下失效。
- 修法：备份 / 回滚 / 自动回滚 / `restore.sh` / `install.sh` / `compliance.sh` 的
  目录复制改用 `cp -pR`。
- 判死测试：test-upgrade 新增第 19 例，把备份 → 覆盖 → 回滚整条链路放在 umask 077 下跑。

### 缺陷 4（发布链路，低）：`install.sh` 结尾提示写死旧的自测口径（v3.7.4）

- 症状：发完 v3.7.3 在空目录跑 `install.sh --ref v3.7.3` 冒烟（2.03s，rc=0，
  目标仓 `keel-version: 3.7.3`、`test-lint` 实测 44/44），但结尾提示仍打印
  `# lint 自测：42 用例 + 1 元检查`（三份脚本共 6 处）。
- 性质：不是 lint 判据错，是**发布输出与真源不一致**；PROSE 元检查只守
  README/DESIGN，管不到脚本输出，所以三处缺陷修完自测全绿也照不出来——
  只有"发布后真装一次"能照出来。
- 修法：提示改为 `# lint 自测：必须全绿（数字以实际输出为准）`——无判据处不写死数字。
- 判死方式：把「发布后跑一次 `install.sh --ref <新 tag>` 冒烟」列为例行动作；
  结果（版本行 / 自测比分 / 结尾提示）记入本归档，不再依赖人记。

## BSD 专用写法逐项实测

| 写法 | 结果 | 依据 |
|---|---|---|
| `stat -f %Lp` / `stat -c %a` | 兼容：GNU 走 `-c %a`，BSD 走 `-f %Lp`；权限比对真实生效 | 755→600 在 GNU 被判死 |
| `sed -i.bak` | 兼容：GNU 与 BSD 都生成 `.bak` 再删 | 3.6.1→3.7.3 的版本行合并成功 |
| `mktemp -d` / `mktemp`（无模板） | 兼容（GNU / busybox / BSD 均通过） | lint 每次运行、升级临时目录 |
| `readlink -f` | 未使用（全仓 grep 0 命中） | —— |
| `date -v` | 未使用；`to_epoch` 已改成纯 shell 算术 | —— |
| `find -perm +` | 未使用 | —— |
| `tar --no-same-owner` | 未使用（Keel 不分发 tar） | —— |
| `cp -R` 保留权限 | **命中**：受 umask 过滤，已改 `cp -pR` | 见缺陷 3 |

## 与 macOS 的差异清单

1. **测试耗时**：GNU 下 lint 0.2s（macOS 约 1s）；test-lint 4–5s（macOS 9–11s）；
   test-upgrade 40s 级（macOS 约 2 分钟）。差异来自 fork 成本与文件系统，不是判据。
2. **awk 实现**：macOS 用 BWK awk，Debian 用 mawk，Alpine 用 busybox awk；
   三套下 lint / 自测结果一致（含新的 Kahn 环检测）。
3. **时间戳精度**：busybox `date` 无 `%N`，只影响测量，不影响脚本行为。
4. **locale**：容器需显式 `locale-gen zh_CN.UTF-8`；未生成时 glibc 会静默回退，
   所以本轮先生成再跑，避免"假双 locale"。

## 仍未验证

- Windows / Git Bash（原计划的第三平台，本轮未做）。
- bash 3.2 在 Linux（发行版不提供，无法复现；macOS 上持续在跑）。
- 真实断网 / 磁盘满场景下的 `--resume` 提示（本轮用故障注入模拟强杀）。
