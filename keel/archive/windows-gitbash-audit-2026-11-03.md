# Windows / Git Bash 第三平台审计（2026-11-03）

> 结论先说：**没有走到"已实测"档**。本机与所有可触达的通道都拿不到一个能真实执行
> bash 的 Windows 运行时，因此本轮只做到「静态守卫已加但未运行」。**不得据此宣称支持 Windows。**

## 1. 环境

| 项 | 值 |
|---|---|
| 宿主 | macOS 15.8.2（24H232），x86_64 |
| bash | 3.2.57（Apple），与 Windows Git Bash 的 bash 4.4+ 不同代 |
| Docker | 29.7.2，`OSType=linux`，`linux/x86_64` |
| git | 2.39.5 (Apple Git-154) |
| python3 | 3.13.5 |

## 2. 探测的六条途径与阻断证据

| 途径 | 命令 / 证据 | 结论 |
|---|---|---|
| Windows VM（UTM） | `ls ~/Library/Containers/com.utmapp.UTM/Data/Documents/*.utm` → no matches | 无 VM |
| Windows VM（Parallels） | `ls ~/Parallels/*.pvm` → no matches | 无 VM |
| Windows VM（VMware / VirtualBox） | `/Applications` 无对应 `.app`；`~/Virtual Machines*`、`~/VirtualBox VMs` 均不存在 | 无 VM |
| 云 Windows 实例 | 无云厂商凭据；`gh` 未安装（`command -v gh` → none） | 不可达 |
| GitHub Actions `windows-latest` | 镜像 `git ls-remote https://github.com/idcu/keel.git` **可读**（HEAD 正常返回），但 `ssh -T git@github.com` → `Permission denied (publickey)`，无写入凭据；主仓在 gitee | 只能读、不能跑 |
| wine / msys2 | `command -v wine wine64` → none；`command -v pacman msys2` → none | 均未安装 |
| Docker Windows 容器 | `docker run --platform windows/amd64 mcr.microsoft.com/windows/nanoserver` → `unable to find user ContainerUser`；daemon 是 linux | 不能执行 Windows 二进制 |

**判定：Windows 运行时不可用。** 按用户要求转「静态危害审计 + 机器判据」，不做"语法检查冒充验证"。

## 3. 逐项静态审计（11 条）

| # | 危害 | 能否立机器判据 | 处置 |
|---|---|---|---|
| 1 | **CRLF / LF 混入**：Git Bash 默认 `core.autocrlf=true`，`.sh` 检出成 CRLF 后 `bash 脚本` 首行报 `$'\r': command not found`——lint 自己就是那个跑不起来的脚本 | ✅ 可判 | lint §15a：`grep -l $'\r'` 扫 `*.sh` / `*.py` / `*.md` / `checks/hooks/*`；用例 43 判死 |
| 2 | **文件名仅大小写不同**：Windows 不区分大小写，两个路径互相覆盖，检出后「缺一个、坏一个」 | ✅ 可判 | lint §15b：`find` 全量按 `tolower` 查重；用例 44 判死（Linux 上真跑，macOS 默认 APFS 不区分大小写→显式 SKIP） |
| 3 | `pwd -P` 在 Git Bash 返回 `/c/...` | ⚠️ 不能（两种写法都合法，无法区分"预期"与"实际"） | 只依赖 `pwd -P` 输出作绝对路径；不做前缀假设；已由 INVOKE 的「空格+中文」第四形式覆盖路径拼接 |
| 4 | `chmod` 语义不真实（Git Bash 权限位来自 MSYS 映射） | ⚠️ 不能（宿主 FS 无 POSIX 位） | 升级引擎不依赖权限位做安全判断；`--check-manifest` 的权限核对在 Windows 只会告警式漂移，文档注明 |
| 5 | 符号链接需开发者模式 / `core.symlinks=false` | ⚠️ 不能 | 仓库内**零符号链接**（`find -type l` = 0）；模板不引入 |
| 6 | `sha256sum` / `mktemp` / `stat` 实现差异 | ⚠️ 不能（脚本已有三级回退） | 引擎按 `sha256sum → shasum → openssl`、`stat -c → stat -f` 回退；lint 用 `pwd -P` 归一化 mktemp 返回值 |
| 7 | 路径含空格 / 中文 | ✅ 可判 | INVOKE 第四形式：把整条基线复制到 `... 路径 有空格` 再跑，四种入参 0 fail |
| 8 | `core.autocrlf` 配置 | ✅ 预防 | 两仓 `.gitattributes` 强制 `*.sh` / `*.md` LF；lint §15a 是检出后的判据（配置可被采用方改掉） |
| 9 | 子模块指针 | ⚠️ 部分 | 项目仓有 `pitfall: submodule-pointer-drift` 机制；Windows 检出本身不影响指针（指针是 git 对象，不是文件内容） |
| 10 | 长路径（260 字符限制） | ⚠️ 不能（仓库内最长路径远低于限制） | 记录为未验证；模板不引入深目录 |
| 11 | 盘符路径与 POSIX 路径混用 | ⚠️ 不能 | lint 用 `pwd -P` 归一化；注释里已记录 `mktemp -d` 返回 `C:\...\Temp/tmp.XXX` 的历史坑 |

## 4. 已加的守卫与实测

- `keel-lint.sh` §15（跨平台底线）：CRLF + 大小写冲突，两条都是 ❌ fail。
- `test-lint.py`：用例 **43**（钩子追加 CRLF → 期望含「含 CRLF」）、**44**（`demo.md` + `Demo.md` → 期望含「仅大小写不同」）；INVOKE 增加第 4 种入参形式（空格+中文）。
- 实测（macOS 15.8.2）：
  - 全量 `test-lint`：**46/46（44 用例 + 2 元检查）**，14.8s；用例 44 在本机 SKIP（APFS 不区分大小写）。
  - 同一条 44 在**大小写敏感卷**（`hdiutil create -fs "Case-sensitive APFS"` + `TMPDIR` 指向挂载点）上 **PASS**：lint 确实报「文件名仅大小写不同」。
  - 两仓 `keel-lint` 0 fail（项目仓 2s / 模板仓 1s）。

## 5. 三档结论（本轮唯一口径）

| 档 | 内容 |
|---|---|
| **已实测通过** | macOS（bash 3.2.57）；Linux/GNU 三条基线（Debian 12 / Debian 13 / Alpine，见 `linux-gnu-validation-2026-11-03.md`） |
| **静态守卫已加但未运行** | CRLF（§15a，用例 43 已在 macOS/Linux 真跑，但 Windows 检出行为未实测）；大小写冲突（§15b，用例 44 在 Linux/大小写敏感卷真跑，Windows 未实测）；空格+中文入参（真跑，但 Windows 盘符形式未实测） |
| **已知不适用并有文档处置** | `chmod` 语义、符号链接、长路径、盘符与 POSIX 混用——见 §3 第 3–6、9–11 条 |

## 6. 仍未验证（明确声明）

- 在真实 Windows / Git Bash 上跑 `test-lint`（含 LOCALE / PROSE / DOC / INVOKE）、`test-upgrade`、`install.sh` + 升级 + `--resume` 端到端；
- CRLF 检出后的真实报错形态与修复动作（本地只用人工追加 `\r` 模拟）；
- 大小写不敏感文件系统上的真实检出结果（本地用大小写敏感卷模拟"仓库侧正确"，未模拟"Windows 侧覆盖"）；
- `core.autocrlf=true` 下 `.gitattributes` 是否被尊重、`core.symlinks=false` 时的钩子可执行位。

## 7. 复现

```bash
bash keel/checks/keel-lint.sh keel                 # 0 fail
python3 keel/checks/test-lint.py                   # 46/46（macOS 上用例 44 SKIP）
# 在大小写敏感卷上真跑用例 44：
hdiutil create -size 40m -fs "Case-sensitive APFS" /tmp/keelcs.dmg
hdiutil attach /tmp/keelcs.dmg -mountpoint /tmp/keelcs-mnt
TMPDIR=/tmp/keelcs-mnt/ python3 keel/checks/test-lint.py --only 44
hdiutil detach /tmp/keelcs-mnt && rm -f /tmp/keelcs.dmg
```
