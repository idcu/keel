# keel · 规格仓

[![keel CI](https://github.com/idcu/keel/actions/workflows/keel.yml/badge.svg)](https://github.com/idcu/keel/actions/workflows/keel.yml)
[![keel-version](https://img.shields.io/badge/keel--version-3.3.4-4B3FE3)](keel/INDEX.md)

> **Keel / 龙骨** —— AI 开发项目的上下文基座 + 轻量合规关卡。
> 一句话：**让 AI 在任何一次会话里，都能以恒定成本拿到正确的上下文。**
> 存储量可以无限增长，单次会话的加载量恒定在 ≤5k token。

## 先分清两个仓

| 仓 | 是什么 | 你要不要 |
|---|---|---|
| **`keel`**（本仓） | 规格唯一真源 `DESIGN.md` + Keel 项目自己的实例 | 读规格 / 看落地样例时来 |
| **`keel-starter`** | 对外分发的**纯模板**（不含设计稿） | **装这个** |

装到你的项目只要一条命令：

```bash
bash <(curl -fsSL https://gitee.com/idcu/keel-starter/raw/main/install.sh) <你的项目根>
```

装完还差三步（**缺任一步，这套系统等于不存在**）：贴锚点、填自己的内容、小项目先裁剪。
脚本会把三步打给你。**要固定版本**加 `--ref v3.3.4`。

## 目录

| 路径 | 是什么 |
|---|---|
| `DESIGN.md` | 规格唯一真源（13 章；所有 `§` 编号引用都指向它） |
| `keel/` | Keel 项目自己的上下文基座（**实例**，非模板副本） |
| `keel-starter/` | 发布仓（子模块），纯模板 |
| `docs/research/` | 竞品源码级核实报告（逐个读源码，非读 README） |
| `scripts/release.sh` | 两仓发布编排：「先发布仓、后项目仓」顺序写死在脚本里 |
| `AGENTS.md` | 点火锚点——AI 每次任务的入口 |

## 状态

- `keel-version` **3.3.4** · `project-state` **building**（唯一存储位置：`keel/INDEX.md` frontmatter）
- 内核校验：`bash keel/checks/keel-lint.sh keel` → 0 fail
- lint 自测：`bash keel/checks/test-lint.sh` → 38/38
- 遵守率：`bash keel/checks/compliance.sh report`（无基线时不作数，见 §11.2）

## 改之前先看这三条

1. **`keel/`（本仓根，实例）与 `keel-starter/keel/`（模板）结构相同、内容独立演进**——改模板改子模块那一份，改本项目进度改根目录那一份（详见 `keel/ARCHITECTURE.md`）。
2. **改了 `keel-lint.sh` 必须同步 `DESIGN.md` §9.3 的代码块**——`test-lint.sh` 的 DOC 检查逐字比对，不一致直接 FAIL。改脚本与改文档是同一个动作。
3. **推送顺序恒为「先发布仓、后项目仓」**——用 `bash scripts/release.sh --apply`，别手动敲两条 push。

## License

MIT（见 [LICENSE](LICENSE)）。模板 `keel-starter` 同。
