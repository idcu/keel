---
scope: meta
status: active
last-verified: 2026-10-04
keywords: [脚本清单, 内核脚本, 冷区, inventory]
---

# Keel 内核自带脚本清单（冷区）

> 本文是**清单**，不是判据——判据在《Keel 设计稿》§9.1 / §9.3，扩展位在 [../checks/rules.md](../checks/rules.md)。
> 沉到冷区的原因：§7.3「沉」——清单是"查得到就行"的信息，不该占单轮加载预算。
> 主会话需要某个脚本的准确用法时，点开对应脚本的 `--help` 或读设计稿对应节。

| 脚本 | 作用 | 何时跑 |
|---|---|---|
| `checks/install-hooks.sh` | 安装 pre-commit + commit-msg（写 `core.hooksPath`） | 每个 clone 一次 |
| `checks/verify-hooks.sh` | 钩子"验谎"：本体可执行 + 挂载点正确 | 装完复核；CI 加 `--allow-unset` |
| `checks/load-estimate.sh <关键词>` | 按 §7.2 口径算本轮加载量，超 `BYTES_SESSION` 即非零退出 | 每轮检索时（§8 协议第 4 条） |
| `checks/keel-lite.sh [目录] --apply` | 裁掉按需层成最小集，并剥离 INDEX 对应路由行 | 小项目第 0 天（§12.1） |
| `checks/mcp/keel-mcp-server.py` | MCP 只读服务：把 INDEX / CONSTITUTION / NOW 暴露成 resource | 支持 MCP 的客户端（§4.4） |
| `checks/compliance.sh report` | 遵守率 + 存量合规率（§11.2 / ADR 0009 / ADR 0011）；pre-commit 自动记录，report 只读 | 双周回顾（§11） |
| `checks/compliance.sh backfill [--max N] [--dry]` | 回填历史提交，出"存量合规率"（**不是遵守率**，ADR 0011） | 刚装完的第一天 |
| `checks/compliance.sh reset [--backfill]` | 清指标；`--backfill` 定向只清回填段（裸 reset 会删掉不可重建的遵守率记录） | 指标口径变更后 |
| `checks/check-mcp-config.sh` | 校验已声明的 MCP server 可达（未声明不算缺陷，恒 exit 0） | 接入语义检索后 · CI（§9.5） |

## 与内核的分工

- **内核负责**（全项目通用、开箱即用）：预算、frontmatter、值域、命名、登记、引用环、
  死链、孤儿、陈旧、状态机、闭环钩子本体（§9.1-16）。
- **扩展位负责**（项目专属、需技术栈知识）：契约与实现是否一致、术语是否统一、
  依赖许可证、生成物是否漂移。
- CI 串联顺序：**先跑内核 lint（0 fail 才继续）**，再逐条跑扩展位里级别为 ❌ 的命令；
  ⚠️ 规则只输出、不阻断。

## 一条扩展规则的准入标准

1. 能被脚本判死（§2 原则 4）——靠人记的不算；
2. 误报可接受，且误报有**显式豁免方式**（学 §9.4：给豁免留一个字段，而不是靠口头约定）；
3. 级别定了就别轻易改——**告警降级比告警漏报更容易让人无视全部告警**。
