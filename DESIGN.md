# Keel · 开发文档（v3）

> 中文名：龙骨　｜　定位：AI 开发项目的上下文基座 + 轻量合规关卡
> 一句话：**让 AI 在任何一次会话里，都能以恒定成本拿到正确的上下文。**

> 关于本文档：这是设计稿，不进入运行期加载路径（因此不适用 §7 的行数预算；落地后的规则正文按 §7 拆分）。v2 修复了 v1 的全部规格矛盾，补齐了接入 / 闭环 / 蒸馏计数 / 并发 / 合规五处机制空缺；**v3 把"机器验"回敬给文档自己**——预算从"行数单约束"改成"行数 × 字节 × 单行"三约束（行数不是 token 的有效代理，实测可差 10 倍），把此前"声称由 lint 强制、实则未实现"的 9 项检查真正写进 §9.3，并让入口规格、项目状态、点火锚点全部进入可验证路径。§9.3 的脚本已通过 38 例故障注入实测（30 例 fail 缺陷 + 2 类告警 + 6 类合法基线）。**v3.4.4 起「零 stderr 噪声」由 ADR 0014 变成判据**：自测会检查每例的 stderr，非空即 fail（环境噪声走显式豁免白名单，且豁免必打印，不许静默）。
> **v3.1 的改动集中在一件事上：把还停在"建议"层面的三处承诺变成可执行形式**——孤儿判定改用真实链接图（§9.1-4）、闭环钩子本体进 lint（§9.1-16）、单轮加载量进预算真源并给出命令（§7.2）；另补齐 §4.2 那句悬空的 MCP 落点，并把语义检索短板明确定义为"接入位"而非内核职责（§4.4 / §9.5）。
> 阅读路线：§1–2 立论 → §3 结构 → **§4 点火（不做这步，其余全部无效）** → §5–8 规范 → §9 校验 → §10–11 运转 → §12 落地。

---

## 1. 核心命题

AI 时代开发最贵的成本不是写代码，是**上下文重建**：每次开新会话，AI 都像一个手速极快、但每天早上失忆的实习生。

Keel 给这个实习生配齐：**入职手册 + 工作台 + 错题本 + 交接本 + 质检台**。

### 1.1 唯一的死因

Keel 这类基座项目只有一个死法：**长胖到没人（也没 AI）读得动，最后沦为摆设**。

所以第一性原理不是"内容全"，而是：

> **矛盾不在「内容多」，在「存储量 vs 加载量」。存储可以无限增长，加载量必须恒定。**

- 目标不是让 Keel 变小——而是无论它长到 1MB 还是 1GB，单次会话加载量恒定在 **≤5k token**；
- 手段是把「大文件」拆成「索引 + 一堆小文件」：总字数不减反增，但每次只取一格。

### 1.2 不做什么

- ❌ 不做通用项目管理工具（不替代 Jira / Linear）
- ❌ 不做文档 wiki（不替代 Confluence）
- ❌ 不做审计 / 权限系统——合规留痕用 git 历史 + `decisions/`（SSOT，不重复造）
- ❌ 不重复定义已有的东西：每类事实只有一个定义位置（见 §2 原则 1）
- ❌ 不做"事实迁移"运动——仓库里已有的 ADR / `docs/` / `CONTRIBUTING.md` 不搬不删，只在 `INDEX.md` 路由表里登记为**指针**（§2 原则 1：能引用的绝不复制）。判断标准只有一条：**这条内容会被 AI 反复读吗？** 会，才值得迁进 Keel；不会，留在原地并指过去。
- ❌ 不靠人自觉——能脚本化的检查一律脚本化，有钩子的闭环才算闭环（见 §10.4）

---

## 2. 设计原则

| # | 原则 | 含义 | 违反后果 |
|---|---|---|---|
| 1 | **SSOT · 定义权单向** | 每类事实只有一个定义位置（见 §3.1）；其他位置只能引用，不得复制 | 必然漂移，AI 读到过期版本 |
| 2 | **恒定加载** | 单次会话读取量恒定，不随 Keel 体积增长 | 注意力稀释，退化成"没用 Keel" |
| 3 | **索引化** | 任何超预算内容必须降级为索引 + 指针 | 找不到 / 一次读太多 |
| 4 | **机器验** | 一致性靠脚本，不靠自觉 | 文档腐烂无人知 |
| 5 | **强制闭环** | 完成任务必须写回；且闭环要有可执行的钩子 | 下次会话上下文断裂 |
| 6 | **坑的复利** | 任何返工 / 回滚 / revert 必须补一条坑 | AI 反复犯同一个错 |
| 7 | **蒸馏上提** | 高频坑提炼为宪法一行规则；**触发次数必须被计数** | 每次都要重读长文 |
| 8 | **点火优先** | 没有接入锚点，整套系统不会被触发（见 §4） | 一切设计空转 |

---

## 3. 结构

### 3.1 六层

| 层 | 管什么（定义权归属） | 变化频率 | 典型文件 |
|---|---|---|---|
| **L0 宪法与关卡** | 项目身份、硬约束、架构红线、人审关卡 | 几乎不变 | `CONSTITUTION.md` |
| **L1 地图** | 代码地图、模块边界、依赖方向、环境、契约真源 | 低 | `ARCHITECTURE.md`、`contracts/`、`env/` |
| **L2 记忆** | 决策记录、坑库、反模式、术语表 | 增量为王 | `pitfalls/`、`decisions/`、`GLOSSARY.md` |
| **L3 执行** | 现在做什么、卡在哪、下一步、交接 | 每次会话都动 | `NOW*.md`、`NOW-history/` |
| **L4 技能** | 可复用操作手册（跑测试 / 发版 / 接内部服务） | 中 | `skills/*.md` |
| **L5 校验** | 一致性检查、质量门、CI gate | 低 | `checks/` |

**层间规则（v2 修正）**：六层是"事实类型"的分区，不是引用限制。

- 引用**可以跨层**，但必须是指针（`@路径` 或 markdown 链接），**不得复制内容**，不得形成循环引用；
- 分配权单向：L0 红线 > L1 契约 > 其余层只能引用上层定义，不得重新定义。

### 3.2 目录结构

```
keel/
├── INDEX.md                  # 唯一入口 ≤100 行（检索协议 + 路由 + project-state + keel-version）
├── CONSTITUTION.md           # L0 宪法：红线 + 人审关卡
├── ARCHITECTURE.md           # L1 代码地图 + 依赖方向
├── GLOSSARY.md               # L2 术语表
├── NOW.md                    # L3 当前焦点 ≤60 行（并行时 NOW-<stream>.md，见 §5.5）
├── NOW-history/              # 冷区：NOW 历史归档（YYYY-MM-DD-焦点.md）
│
├── contracts/                # L1 契约真源（INDEX.md + *.schema.* + _template.schema.json）
├── env/                      # L1 环境（INDEX.md + setup.md：依赖锁、密钥来源、配额、mock）
├── skills/                   # L4 操作手册（INDEX.md + _template.md + *.md）
├── pitfalls/                 # L2 坑库（INDEX.md 表格 + <scope>/ 子目录 + _template.md）
├── decisions/                # L2 决策记录（INDEX.md + _template.md + 0001-*.md）
├── checks/                   # L5 校验（keel-lint.sh + budget.env + rules.md
│                             #            + install-hooks.sh + test-lint.sh/.py
│                             #            + hooks/：版本化的 pre-commit / commit-msg）
└── archive/                  # 冷区：已失效内容（不进索引正文）
```

### 3.3 冷热区

- **热区 = 工作区**：除冷区外的全部内容。索引、校验、陈旧判定都作用于热区。
- **冷区 = `archive/` + `NOW-history/`**：已失效阶段、过时方案、历史交接。规则：
  1. 不进任何索引正文，只在 `INDEX.md` 底部留一行指针；
  2. lint 对冷区只做**死链检查**（其余检查豁免）；
  3. **检索时必须显式排除**（`grep --exclude-dir=archive --exclude-dir=NOW-history`，见 §6.1 / §8）——否则冷区会挤占恒定预算；
  4. 内容没丢，只是不占位；
  5. **空目录不被 git 跟踪**：`archive/` 与 `NOW-history/` 里必须各放一个 `.gitkeep`——否则新 clone 的仓库一跑 lint 就是两条死链（`INDEX.md` 的冷区指针指向不存在的目录）。这是 §12.1 "第 0 天"里唯一容易漏掉的一步。

### 3.4 命名与豁免

- 坑库文件名 = 关键词（`connection-pool-exhausted.md` ✅；`2026-09-12-note.md` ❌）；
- 其余文件用 kebab-case 英文名；日期只允许出现在冷区归档名里；
- 并行工作流用 `NOW-<stream>.md`；域目录超 20 个文件时按主题再分层，**但只允许一层**（路由深度上限 2 级，见 §6.3）——再超就该往上"提炼"，而不是继续往下分；
- **唯一豁免**：`_template*` 文件豁免 frontmatter / 孤儿 / 陈旧 / 三段式检查（尺寸与死链照查）。

### 3.5 拓扑（单仓库 / monorepo）

**一个 Keel 管一个"发布单元"，不是管一棵目录树。** 判定口诀：

> **这条事实，另一个服务也会踩到吗？** 会 → 放根 `keel/`；不会 → 放该服务自己的 `keel/`。

- **单仓库单服务**：仓库根一个 `keel/`；
- **monorepo 多服务**：根 `keel/` 管全仓共用的事实（宪法、术语、跨服务契约、流程），各服务目录下各放一个 `keel/`，其 INDEX 用 `scope` 前缀区分（如 `api-*`、`web-*`）；
- 跨 keel 引用一律用相对指针（`@../../keel/GLOSSARY.md`），仍然**只允许指针、不允许复制**（§3.1）；
- lint 逐层跑：`for d in keel */keel; do bash keel/checks/keel-lint.sh "$d"; done`。

> 反例（要避免的形态）：把每个服务的坑都堆进根 `keel/pitfalls/`——根索引会被撑爆，而服务自己反而查不到；或者反过来，把术语表和宪法在 5 个服务里各抄一份，然后各自漂移。

---

## 4. 接入：先点火（P0）

> **不做这一节，Keel 等于不存在**：检索协议写在 INDEX.md 里面，但 AI 不会凭空知道去读它。协议在门内，钥匙必须在门外。

### 4.1 门外锚点（就一句话）

在 AI 工具的规则入口放这一句（**Keel 之外只允许存在这一句**，其余规则一律在 INDEX.md 内，避免第二个真源）：

```
任何任务开始前，先读 keel/INDEX.md 与其中指向的 NOW.md，并遵守 INDEX.md 里的检索协议。
```

> 这一句由 lint 检查（§9.1-10）：在 `CLAUDE.md` / `AGENTS.md` / `.cursorrules` / `.cursor/rules/` 里找不到**原文**（或原文被改写）即 fail。**"点火"从此也是机器验的**——v2 把点火列为 P0 却没有任何检查，等于把整套系统的开关交给了自觉。

### 4.2 落点

| 环境 | 落点 |
|---|---|
| Claude Code / 通用 CLI agent | 项目根 `AGENTS.md` 首行（跨工具事实标准）；Claude Code 亦可写 `CLAUDE.md` |
| Cursor | `.cursor/rules/keel.mdc`（`.cursorrules` 是旧格式，仍兼容） |
| 自建 Agent | 系统提示 preamble 的前三条之内 |
| 支持 MCP 的客户端 | 把 INDEX + NOW 暴露成 **MCP resource / 只读工具**——让"必读"变成协议动作，而不是提示词里的礼貌请求。**实现已随 starter 发布**：`keel/checks/mcp/keel-mcp-server.py`（§4.4） |
| 无 shell 的聊天型 AI | 降级模式：把 INDEX.md + NOW.md 手动粘入上下文（§4.3） |

> 上面这些落点**由 lint 逐个探测**（§9.1-10）：任何一个文件里包含 §4.1 原文即算点火成功。

### 4.3 降级模式说明

Agent 没有 shell / grep 能力时，"检索协议"退化为逐级手动展开：INDEX → 域索引 → 条目。恒定加载目标不变，只是检索变慢——**而且没有任何机制能阻止它多读**。所以这一类环境优先改用 MCP resource（上表第 4 行），把"读多少"重新交还给协议。

### 4.4 MCP 只读服务（§4.2 第 4 行的落地）

v2 把 MCP 落点写进了表，却没给实现——于是这一行长期是**设计稿里的承诺**。v3.1 补上最小实现：

```bash
python3 keel/checks/mcp/keel-mcp-server.py --self-test   # 不开客户端先验证它工作（8 项）
python3 keel/checks/mcp/keel-mcp-server.py               # 以 stdio 提供服务，自动向上找 keel 目录
```

暴露三个只读资源：`keel://index`、`keel://constitution`、`keel://now`（并行工作流为 `keel://now/<stream>`）。

边界是刻意画死的，**它不许越界**：

- **只读**：不接受任何写操作——"写回"仍由 §10.3 的会话结束清单负责人承担；
- **不进内核**：`keel-lint.sh` 不引用它，§9.3"零依赖"的前提不变；本文件因此**不在 §9.1 的检查面内**；
- **不替代检索**：它只解决"必读三件怎么到手"；定位 scope、命中条目仍走 §8 的 grep 协议；
- 依赖仅 python3 标准库（与自测套件同一条底线），不开客户端时用 `--self-test` 自证。

> 这一节是"§9 精神"的又一次套用：**写在表里的能力，要么被实现，要么被标注为未实现**；长期悬空的承诺和文档腐烂是同一种病。

---

## 5. 各层规范

### 5.1 入口层 `INDEX.md`（唯一必读）

`INDEX.md` 是全系统**唯一被强制读取**的文件（§7.2 的固定成本），承载检索协议、路由表、项目状态三样东西。它此前只有"≤100 行"的约束，没有内容规格——入口没有规格，等于入口不存在。因此固定如下：

```markdown
---
scope: meta
status: active
last-verified: 2026-09-29
keywords: [索引, 入口, 路由]
keel-version: 2.1.0
project-state: building     # exploring | architecture-locked | building | frozen（§5.2）
---

# keel · INDEX

## 检索协议
（§8 原文照抄，不得改写、不得精简）

## 路由（scope → 入口）
| scope | 一句话 | 入口 |
|---|---|---|
| meta | 宪法 / 地图 / 术语 | [CONSTITUTION.md](CONSTITUTION.md) · [ARCHITECTURE.md](ARCHITECTURE.md) |
| now | 当前焦点与交接 | [NOW.md](NOW.md) |
| db | 数据库 / 连接 / 迁移 | [pitfalls/INDEX.md](pitfalls/INDEX.md) |
| … | | |

## 冷区指针（只此一行）
[archive/](archive/) · [NOW-history/](NOW-history/)
```

三条硬规则：

1. **路由表就是 scope 一览表**。新增 scope 必须在此加一行；§10.1 第 3 步的"定位 scope"由此有据可依，**不允许靠猜**。
2. **`project-state` 只写在这里**。它是 `frozen` 期契约冻结（§5.2）的唯一开关，必须待在必读路径上——写在 `CONSTITUTION.md` 里 AI 看不到。
3. 路由表逼近 100 行时，走 §7.5 的降级路径（按层分组 → 二层路由），不得直接顶破预算。

### 5.2 L0 宪法层 `CONSTITUTION.md`

不是"最佳实践建议"，是**违反就打回**。

```markdown
# CONSTITUTION

## 身份
本项目是 <项目名>，技术栈 <...>，目标 <一句话>，owner <谁>。

## 硬约束（违反即打回）
1. 禁止跨层调用：<模块A> 不得 import <模块B>
2. 禁止在客户端存储任何密钥 / token；env/ 只记录来源，不记录值
3. 契约只能定义在 contracts/，其他位置不得重复定义
4. 单次会话 Keel 加载量 ≤5k token（见 @INDEX.md）

## 人审关卡（AI 不得自行决定）
| 改动类型 | 审批 | 留痕 | 时限 |
|---|---|---|---|
| 资金 / 支付 / 退款 | owner + 跨职能一人（双签） | decisions/ + PR | 24h |
| 权限 / 鉴权 / 数据删除 | owner | PR + decisions/（删除类必记） | 48h |
| contracts/ 契约变更 | owner + 契约 owner | decisions/ | 24h |
| 引入新第三方依赖 | owner | decisions/ | 48h |
| frozen 期任何契约改动 | 例外通道：双签 + 记例外 | decisions/ | 24h |

> 审计轨迹 = git 历史 + decisions/；不另建审计系统。
>
> **时限怎么落地**（否则 24h / 48h 只是装饰）：采用**登记制**，不新建审批系统。审批一挂起，当场写进 `NOW*.md` 的阻塞表（卡在谁 / 解锁条件 / 绕行三件套齐全）；表中的"时限"= 从登记到结论的最长时长。超时未决的，由 §11 的双周回顾统一统计并升级（找上级 owner），**同一件事不允许在阻塞表里挂过两个回顾周期**。

## 项目状态机
exploring → architecture-locked → building → frozen

- **当前状态的唯一存储位置 = `INDEX.md` frontmatter 的 `project-state`**（§5.1 规则 2）。本节只定义状态与规则，不存状态；
- frozen 期契约冻结，只允许"最小修复"，且不得新增契约面（字段 / 端点）；`frozen` 期间新增 `contracts/**` 文件由 lint 直接 fail（§9.1-11）；
- 冻结期例外决策每月回顾：例外记在 `decisions/`，且**必须同时带 `type: exception` 与 `created: YYYY-MM-DD`**（缺 `created` 由 lint 直接 fail），由 lint 按月计数（§9.1-11）；**单月 >2 次例外，强制退回 building 重新评审**。
```

### 5.3 L1 地图与契约

- `ARCHITECTURE.md`：模块边界、依赖方向、关键数据流——只画现状，不写愿望；
- `contracts/`：API / 类型 / 事件的**唯一真源**（SSOT），修改走人审关卡；
- `env/`：依赖锁、密钥**来源**与获取方式（禁写值）、配额、mock 约定。

> 这一层三件（`ARCHITECTURE.md` / `contracts/` / `env/`）的规格与骨架见 §5.7.1–§5.7.3。

### 5.4 L2 坑库

强制三段式，**缺任一段视为不合规**（lint fail）：

```markdown
---
scope: db
status: active          # active | distilled（已上提宪法） | archived（已失效，移入 archive/）
severity: P1            # P0–P3，定义见下
last-verified: 2026-09-29
triggers: 0             # 每被触发一次 +1；≥3 由 lint 提醒蒸馏
keywords: [连接池, 超时, 连接池耗尽, connection pool]
---

## 症状
压测下接口大面积 500，日志报 `connection pool exhausted`。

## 根因
DAO 层在循环内新建连接，未走连接池单例；连接数上限 20，QPS>50 即耗尽。

## 正解
- 连接必须走全局池，禁止循环内建连
- 池大小 = CPU 核数 × 2 + 有效磁盘数
- 超时时间必须显式设置，禁用默认 0（无限等待）
```

严重度定义：

| 级别 | 定义 | 例 |
|---|---|---|
| P0 | 资金 / 数据 / 安全损失，或不可逆 | 重复退款、数据误删 |
| P1 | 主流程阻断 | 连接池耗尽、构建失败 |
| P2 | 局部返工 | 生成物漂移、契约不一致 |
| P3 | 效率与体验 | 报错难懂、路径绕 |

### 5.5 L3 `NOW*.md` 会话交接契约

**这是 AI 开发最大隐形浪费的解药。** 每次会话结束必须覆盖重写（不是追加）：

```markdown
---
scope: now
status: active
last-verified: 2026-09-29
updated: 2026-09-29
keywords: [焦点, 交接]
---

# NOW · main

## 当前焦点
<一句话：正在做什么>

## 本轮完成
- [x] <做了什么>

## 未完成 / 半途
- [ ] <什么没做完，做到哪一步>

## 下一步（按优先级）
1. <下一步>

## 阻塞
| 卡在 | 解锁条件 | 绕行 |
|---|---|---|
| <谁/什么> | <明确条件> | <方案 / 无> |

## 本轮新发现的坑
- <文件名 + triggers 初值；未登记则本轮不算完成>
```

阻塞必须写**三件事**：卡在谁/什么、解锁条件、有无绕行。缺"解锁条件"，AI 会自作主张绕路。

**归档时机（默认单 `NOW.md` 也必须执行）**：**先归档，再重写**——覆盖之前把上一轮内容落到 `NOW-history/<YYYY-MM-DD>-<焦点>.md`，日期取被替换那一轮的 `updated`。

- 不归档就重写 = 历史当场蒸发，§11 的"平均阻塞时长"从此再也算不出来；
- 这是流程规则（脚本判不了"你归档了没"），所以配一条兜底：`NOW.updated` 超 7 天 → lint ⚠️（§9.1-12），提示"这个会话可能没写回"。

**并发约定**：默认单文件、单一写者（当前会话独占）；多分支 / 多 agent 并行时按工作流拆 `NOW-<stream>.md`（如 `NOW-api.md`），并在 INDEX 登记；stream 完结后内容归档到 `NOW-history/`。

**写冲突守卫**（覆盖重写会静默丢内容，所以必须成文）：

1. **开工前**跑 `git status`：若 `NOW*.md` 已有未提交改动，说明上一个会话没走完 §10.3 清单——先归档再接手，不要直接改；
2. 需要并行时**开工前**就拆 `NOW-<stream>.md` 并在 `INDEX.md` 登记，**不允许事后拆**（事后拆必然要合并两份历史）；
3. 真的发生覆盖事故，按原则 6 处理：登记 `pitfalls/`（scope: meta）并复盘——**"被抓到的坑"正是坑库的原料**。

### 5.6 L4 技能层

每个 skill 是写给 AI 看**可复用操作手册**，格式固定：

```markdown
---
name: run-tests
scope: meta
status: active
last-verified: 2026-09-29
keywords: [测试, 验证]
trigger: 需要验证改动是否破坏既有行为
---

## 前置
<必须先具备什么>

## 步骤
1. ...

## 失败分支
- 报 X → 原因通常是 Y → 见 @../pitfalls/build/xxx.md

## 验证标准

<什么算成功>
```

### 5.7 按需层的规格与骨架（§12.1 之外的层）

这五类**不进 MVP**：它们是从真实痛点长出来的，提前造只会变成摆设（§12.1）。
但一旦要加，形态固定如下。分工与 §6.2 同一条原则：**规格在这里判死，教学注释在各目录的 `_template*` 里**——
文档不重复模板的逐行解释，模板不重复文档的硬要求。

#### 5.7.1 L1 地图 `ARCHITECTURE.md`

**硬要求**：只写现状，不写愿望（愿望只允许写在宪法"身份"段）；必须有"模块表 + 依赖方向矩阵"；**不复制任何契约字段**，只指向 `contracts/`。
依赖方向矩阵就是 `CONSTITUTION.md` 硬约束 1 的判据——**改矩阵等于改红线，走人审关卡**。

```markdown
| 模块 | 一句话职责 | 目录 | owner |
|---|---|---|---|
| <api> | <对外入口> | `<src/api/>` | <谁> |

| 从 ↓ 到 → | api | domain | infra |
|---|---|---|---|
| **api** | — | ✅ | ❌ |
| **domain** | ❌ | — | ✅ |
```

> 用矩阵不用图：加模块时加一行一列，比重画一张图便宜，而且能逐格判死（图判不了）。

#### 5.7.2 L1 契约 `contracts/`

**硬要求**：契约（API / 类型 / 事件）**只能定义在这里**（硬约束 3，别处只能引用）；`INDEX.md` 是纯表格（域索引规则，§6.2）；契约变更走人审关卡（owner + 契约 owner / `decisions/` / 24h）；**`frozen` 期不得新增契约文件**（§9.1-11）。
格式不限（JSON Schema / OpenAPI / Protobuf 皆可），但**必须自带版本与字段级语义**——否则 AI 只能看到字段名，猜不出含义。

| 契约（唯一真源） | 类型 | 版本 | → 文件 |
|---|---|---|---|

> 契约漂移检查**不由 lint 判定**（它不懂你的技术栈）：在 `checks/rules.md` 声明项目自己的命令，由 CI 串联（§9.2）。

#### 5.7.3 L1 环境 `env/`

**硬要求**：只记**来源与获取方式**，**永不记录值**（硬约束 2）；`INDEX.md` 纯表格 + `setup.md`（依赖锁 / 密钥来源 / 配额 / mock 约定）。

| 变量名 | 来源 | 谁有权限 | 怎么拿到 |
|---|---|---|---|
| `<API_KEY>` | <密码管理器 / KMS / 平台密钥管理> | <谁> | <步骤，不含值> |

> 写了值 = 违反硬约束 2，而且 **git 历史里永远擦不掉**——这是少数"删了也还在"的位置。

#### 5.7.4 L2 术语表 `GLOSSARY.md`

**硬要求**：术语的唯一真源；**必须有"禁止写法"列**——术语混用的本质是"同一概念多种写法并存"，
只写正解、不写禁止写法，`rules.md` 里那条 grep 规则就无从下手，这张表也就退化成一本字典。
同一术语的写法之争反复发生（同一坑触发 ≥3 次）时，**上提为宪法的一行硬约束**，而不是继续加表行（§7.4 蒸馏）。

| 术语（唯一写法） | 禁止写法 | 一句话定义 | 备注 |
|---|---|---|---|
| <订单> | <order / 单子 / 定单> | <用户提交的一次购买请求> | <代码里用 `Order`> |

#### 5.7.5 L2 决策记录 `decisions/`

**硬要求**：`INDEX.md` 纯表格；文件名 `0001-<slug>.md`（四位序号递增，日期只允许出现在冷区归档名里）；
**ADR 定稿即不可变**——要改就再写一篇、互相写 `superseded-by`（§9.4）；
**必须写"被否掉的选项"与"代价"**，只写好处的 ADR 是宣传稿。
走了 frozen 例外通道的，额外带 `type: exception` 与 `created: YYYY-MM-DD`，由 lint 按月计数（§9.1-11）。

```markdown
# 0001 <决策标题>
## 背景   ← 什么情况下必须做这个决定
## 决定   ← 一句话说完最好
## 被否掉的选项   ← 表格：选项 / 为什么没选（ADR 最值钱的部分，防"半年后又有人提同样方案"）
## 后果   ← 好处 + **代价**（缺代价就不算决策记录）
```

> ADR 豁免 `last-verified` 陈旧检查（§9.4）：它的时效靠"被谁取代"表达，不靠日期——
> 给不可变文档刷日期，只会产出永久假告警，而假告警会让整套告警机制被无视。

---

## 6. 可检索性

### 6.1 结构化头（每个 md 必带）

| 字段 | 值域 | 说明 |
|---|---|---|
| `scope` | db / api / auth / build / finance / meta … | 检索主键，目录名即 scope |
| `status` | active / distilled / archived | 生命周期 |
| `last-verified` | YYYY-MM-DD | **陈旧判定的唯一基准**（不用文件 mtime） |
| `keywords` | [中英混合] | 供 `grep` 命中 |
| 角色字段 | pitfall：`severity`、`triggers`；skill：`trigger`；NOW：`updated` | 由 lint 强制 |

唯一豁免：`_template*`（见 §3.4）。值域（`status` / `severity` / 日期格式 / `keywords` 非空）由 lint 强制，见 §9.1-6。

**frontmatter 按 YAML 解析**：`key: value   # 注释` 里的行内注释会被剥掉（要求 `#` 前有空白），因此 §5.2 / §5.3 模板里那些注释是合法的。**别在值里塞 `#`**，它之后的内容都会被当注释——这是唯一一处"看起来能用、实际被截断"的地方。

检索方式：`grep -rl "连接池" keel/ --exclude-dir=archive --exclude-dir=NOW-history` —— 秒中，且冷区不进结果（§3.3 规则 3）。**漏掉 `--exclude-dir` 会直接击穿 §7.2 的预算账本。**

### 6.2 一行索引化

`pitfalls/INDEX.md` **只允许是表格，不允许放正文**：

> **规则泛化（v3）**：**任何域索引 `*/INDEX.md` 都只允许是表格行**，连 HTML 注释也不行；
> **根 `INDEX.md` 是唯一例外**——它的内容是 §5.1 规定的那三样（检索协议 + 路由表 + 冷区指针）。
> 那么"怎么填"的说明写在哪？**写在同目录的 `_template.md` 里**。
> 一句话：**索引负责定位，模板负责教怎么填**；两者混在一起，索引就不再是可扫的路由表。

```markdown
| 症状（一行） | scope | 严重度 | → 文件 |
|---|---|---|---|
| 压测下 DB 连接耗尽 | db | P1 | [conn-pool.md](db/connection-pool-exhausted.md) |
| 幂等缺失导致重复退款 | finance | P0 | [dup-refund.md](finance/duplicate-refund.md) |
```

### 6.3 三级路由

```
INDEX.md             ← 第 1 跳：唯一入口，~1.2k token
  └─ 域/INDEX.md     ← 第 2 跳：按需加载，~1k token
       └─ 具体条目   ← 第 3 跳：只读命中的那一个，≤2k token
```

即"**两跳索引 + 一跳正文**"。**路由深度上限 = 2 级索引**（域目录再分层也只允许一层，见 §3.4）；**绝不允许"读整个目录"**（见 §8 协议第 4 条）。

---

## 7. 上下文预算控制（本项目的生命线）

### 7.1 硬预算表（脚本强制，超限即 fail）

| 对象 | 行数上限 | 字节上限 | 近似 token |
|---|---|---|---|
| 根 `INDEX.md` | 100 | 4,500 | ~1.5k |
| 域 `*/INDEX.md` | 80 | 3,000 | ~1.0k |
| `NOW*.md` | 60 | 2,400 | ~0.8k |
| 单条坑 `pitfalls/**` | 30 | 1,200 | ~0.4k |
| 其余单文档 | 160 | 4,800 | ~1.6k |
| **任意单行** | — | **360** | ~0.12k |
| 单目录文件数 | ≤20 | — | — |
| frontmatter | ≤10 行 | 600 | — |
| **`keel-lint.sh` 自身耗时** | — | **≤180 秒** | — |

> **v3.2 新增一行"工具自身的耗时"**（`LINT_SECONDS`，ADR 0008）。前八行管的都是
> "文档有多大"，这一行管的是"检查跑多快"——此前它是唯一没有预算约束的东西，
> 于是 v3.1 的 lint 在 24 个文档上要 319 秒，且规模线性放大。
> **超时限只告警不 fail**：机器慢不等于文件错，把性能当 fail 会让人在慢机器上
> 开始绕过 lint，那比慢更坏。改上限只改 `checks/budget.env` 一处。
>
> **换算基准（v3 改为字节，实测校准）**：UTF-8 中英混排下 **≈3 字节 / token**。三个实测样本分别落在 3.0 / 3.1 / 3.3 字节/token，故取 3 做换算，并**按最坏情况（全中文）定上限**。
>
> **为什么放弃"≈12 token/行"**：行数不是 token 的有效代理。实测同一个"≤30 行"的坑条目，短行 ≈0.4k，而每行写满时 ≈3.9k——**差 10 倍**；中文密集的域索引 84 行实测 ≈3.1k，比按 12 token/行 估算高出 3 倍。因此预算改成三约束：**行数**（管形态）、**字节**（管总量）、**单行**（堵住长行）。
>
> 代价要说清楚：字节上限按最坏情况取，**纯 ASCII 内容会显得偏紧**（实际只用掉约 1/3 额度）。这是刻意的保守——超限早报，好过预算被静默击穿。
>
> **单行上限 360 字节同样计入大小检查**，且 `_template*` 不豁免尺寸。
>
> **资产型目录**（`contracts/`、`checks/`、`env/`）常按"一个契约一个文件"增长，同样受 ≤20 约束——撞限时**先按主题分子目录**（`contracts/payment/`、`contracts/user/`），不要靠放宽上限解决；确需放宽，只改 `budget.env` 里的 `MAX_DIR_FILES` 并记一条 ADR。
>
> **每季度抽测一次**（找最大的 5 个文件看真实字节/行比）：
> ```bash
> for f in $(find keel -name '*.md'); do printf '%s %s\n' "$(wc -c < "$f")" "$f"; done | sort -rn | head -5
> ```
> 用"字节 ÷ 3"复核 token 估算，偏差 >30% 就收紧上限（自动化建议见 §11）。
>
> **这些数字的唯一真源是 `checks/budget.env`（§9.3）**，本节表格只是它的文档副本；要改预算只改 env 一处，缺该文件 lint 直接 fail。

### 7.2 会话加载账本（写进宪法）

```
根 INDEX.md（必读）        ≤4,500 字节 ≈1.5k
当前 NOW*.md（必读）       ≤2,400 字节 ≈0.8k   ← 固定成本 最坏≈2.3k / 典型≈1.9k
域索引（按需）             ≤3,000 字节 ≈1.0k
命中条目（按需）           ≤4,800 字节 ≈1.6k   ← 1 份机制文档，或最多 4 条坑
──────────────────────────────────────────
上限                      ≈4.9k ≤ 5k（恒定，不随 Keel 体积增长）
```

**全局口径**：单次会话 Keel 加载总量 **≤15,000 字节**（≈5k token）。上表是单文件上限；同时命中多项时按**字节总和**收敛，不是各自顶格。

> **这一条不再是"自觉"（v3.1）**：上限数字的唯一真源是 `checks/budget.env` 的 `BYTES_SESSION`；
> 本轮要读多少，由 `checks/load-estimate.sh` 按同一口径算出来并与它比对——
> **超了直接红**。于是 §8 协议第 4 条从"写在协议里的礼貌请求"变成"可执行的命令"。
>
> ```bash
> bash keel/checks/load-estimate.sh 连接池 超时        # 固定成本 + 命中文件字节，与 BYTES_SESSION 比对
> bash keel/checks/load-estimate.sh 连接池 超时 --list  # 顺带列出命中文件与各自字节
> ```

### 7.3 超限的三条出路（没有第四条）

1. **拆** —— 垂直按主题切，**不按时间切**（按时间切会把一件事撕成碎片）
2. **提** —— 反复被验证的共识，上提到宪法 / 术语表，压缩成一行规则
3. **沉** —— 冷内容进 `archive/`，索引里只留一行指针

### 7.4 蒸馏机制（复利最高的一招）

触发次数被 `triggers` 字段计数后，"蒸馏"从口号变成可计算的流程：

```
坑被再次命中 → commit message 写 `pitfall: <文件名>` → commit-msg 钩子自动 +1（§10.4）
        ↓
triggers ≥ 3 → lint 持续 ⚠️ 提醒
        ↓
会话结束流程处理：提炼为宪法一行 + 原文件 status: distilled（细节留存）
        ↓
之后日常只加载宪法那一行（~20 token），真踩了才顺着指针点开全文
```

> 两处机械细节（都实测过，写清楚免得后人当成 bug 去"修"）：
> ① **这次 +1 落在下一次提交里**：git 在 commit-msg 执行前就已定树（实测 git 2.39.5），钩子只能改工作区与索引，历史晚一步。对"≥3 才提醒"这种粗粒度信号无影响，**不值得为它加机制绕开**。
> ② **钩子本体版本化在 `keel/checks/hooks/`**，由 `install-hooks.sh` 用 `core.hooksPath` 挂载——不往 `.git/hooks/` 写不可见文件，因此可评审、团队共享、跟着分支走。
> 反面教材也要写下来：**triggers 一旦改回"会话结束由 AI 自己 +1"，整条蒸馏链路立刻失效**——那是 v2 的做法，也是 v3 修掉的坑之一。

### 7.5 根 `INDEX.md` 的降级路径（唯一不可拆的文件）

`INDEX.md` 是唯一没有"父目录"可以拆的文件，却又同时承载协议 + 路由 + 状态，因此最容易第一个撞上限。它超限时**按顺序**走：

1. **提**：把解释、示例、注记全部移出，只留协议原文 + 路由表 + 冷区指针；
2. **并**：路由表按**层**合并（L0–L5 各一行），不再逐 scope 展开；
3. **分层**（最后手段）：拆出 `INDEX-<层>.md`（如 `INDEX-l2.md` 只列 L2 的 scope → 域索引），根 INDEX 只保留"六层指针 + 协议"，深度不得超过二级。

> 顺序不能颠倒。先"拆"会让同一类事实出现两个入口，直接违反 §2 原则 1——**降级路径本身也必须守 SSOT**。

---

## 8. 检索协议（原文写进 `INDEX.md` 开头）

```markdown
## 检索协议（必须遵守）
1. 必读：INDEX.md（唯一入口）+ 当前 NOW*.md —— 固定预算 ≤2.3k token（最坏）
2. 定位：先 grep -rl "关键词" keel/ --exclude-dir=archive --exclude-dir=NOW-history（只出文件名，冷区不参与检索）；命中过多先收窄关键词
3. 读取：只 read 命中的那一个文件；不够就回到第 2 步换关键词，不得扩大范围
4. 预算：单次检索输出 ≤100 行；本轮 Keel 加载总量 ≤15,000 字节（≈5k token）
5. 写回：完成任务必须写回 NOW*.md（新坑登记进 pitfalls/INDEX.md 且 triggers 维护），否则本轮不算完成
```

> 第 2 条的理由：冷区（`archive/`、`NOW-history/`）内容没丢但不占位，漏掉 `--exclude-dir` 会让检索结果和预算同时失控。
> 第 4 条的理由：真实会话里超预算最常见的方式不是"读了篇大文档"，而是 grep 命中十几个文件后顺手全读。
> 第 4 条不再是空口承诺（v3.1）：它有一个可执行形式——`bash keel/checks/load-estimate.sh <关键词>`，
> 按完全相同的口径把本轮要读的字节算出来，超过 `budget.env` 的 `BYTES_SESSION` 即返回非零（§7.2）。

---

## 9. 校验（机器守卫）

### 9.1 检查项

| # | 检查 | 级别 |
|---|---|---|
| 1 | 大小：行数 / 字节 / 单行字节 / 单目录文件数超限（§7.1） | ❌ fail |
| 2 | frontmatter：缺失、字段缺失（基础字段 + 角色字段）、行数 >10、字节 >600 | ❌ fail |
| 3 | **死链**：`@路径` 与 markdown 链接指向不存在的文件（按所在文件目录解析；冷区照查） | ❌ fail |
| 4 | **孤儿**：热区文档未被任何热区文档以**链接**引用（真实链接图；v3.1 起"正文提及文件名"不算引用） | ❌ fail |
| 5 | 坑条目三段式（症状 / 根因 / 正解）缺失 | ❌ fail |
| 6 | **值域**：`status` ∉ {active, distilled, archived}；`severity` ∉ {P0…P3}；`keywords` 为空；`last-verified` 非 `YYYY-MM-DD`；`triggers` 非数字 | ❌ fail |
| 7 | **登记**：坑文件未出现在 `pitfalls/INDEX.md`；**域索引（`*/INDEX.md`）含非表格正文**（§6.2） | ❌ fail |
| 8 | **命名**：热区文件名含日期；或含大写 / 下划线 / 空格（§3.4） | ❌ fail |
| 9 | **循环引用**：`md → md` 引用图存在环（§3.1） | ❌ fail |
| 10 | **必读与点火**：`INDEX.md` / `CONSTITUTION.md` / `NOW*.md` 缺失；根 INDEX 缺 `keel-version` / `project-state`；§4.1 锚点缺失或与原文不一致 | ❌ fail |
| 11 | **状态机**：`project-state: frozen` 期间新增 `contracts/**`；单月 `type: exception` 决策 >2 条 | ❌ fail |
| 12 | 陈旧：`last-verified` 超 30 天；`NOW` 的 `updated` 超 7 天（**豁免类目见 §9.4**） | ⚠️ warn |
| 13 | 待蒸馏：`triggers ≥ 3` **且 `status ≠ distilled`**（v3.4.4：已蒸馏的不再提醒，否则 §7.4 的流程走不到终点） | ⚠️ warn |
| 14 | **取代关系**：`decisions/*` 的 `superseded-by` 指向不存在的文件 | ❌ fail |
| 15 | 契约漂移 / 术语混用 | 项目扩展位（§9.2） |
| 16 | **闭环钩子本体**：`checks/hooks/{pre-commit,commit-msg}` 缺失或不可执行（§10.4 铁律） | ❌ fail |
| 17 | **版本副本一致**（v3.4.5；v3.4.7 收窄触发，ADR 0016）：`keel-version`、根 `CHANGELOG.md` 当期小节、README 徽章版本号三者不一致（**仅"写了 keel 徽章"的发行仓检查——用户项目自带 CHANGELOG 不再误判**） | ❌ fail |

> **孤儿检测是核心。** 文件一多，最常见的不是"太大"，是"再也找不到"。
> **文档腐烂比没文档更危险**，因为 AI 会信它——所以陈旧判定必须锚在 `last-verified` 这个"人来验证过"的字段上。
> 第 2 / 6 / 7 / 8 / 9 / 10 / 11 项是 v3 新补的：v2 写了规则却没写检查，属于"声称强制、实则空转"。**规则只要不能被脚本判死，就等于建议。**
> 第 16 项是 v3.1 新补的：钩子本体一旦被误删或被 checkout 掉了可执行位，闭环会**静默失效**——而静默失效正是"铁律"最怕的形态。
> 第 4 项在 v3.1 被重写：旧的"按文件名 grep"是近似算法（正文字符串里偶然同名会漏报、改名会误报），现在按**解析后的链接目标路径**判定。
> **第 17 项是本项目自身的 Lint Leakage 修复**（v3.4.5）：ADR 0010 立了"版本声明与可获取必须同时成立"，发布仓 CI 也有 CHANGELOG 检查——**但两者都只存在于发布仓，且已两周无人查看**。实测 `keel-version` 已到 3.4.4 而 CHANGELOG 最新小节停在 3.4.2（发布仓 CI 必然 exit 1）、两仓 README 徽章停在 3.3.8。**判据存在却没人看，等于没有判据**——这正是 arXiv 2606.15828 记录的 Lint Leakage（62%）在本项目内的复现。故把一致性补成第 17 项：**价值不在补上这一版，在拦住下一次**。它只查"副本存在时是否一致"，不负责生成副本。

### 9.2 扩展检查接口

契约漂移、术语混用这类检查依赖具体技术栈，Keel 内核**不假装能通用实现**：

- 在 `checks/rules.md` 里声明项目自己的命令（如 `npm run check:contracts`、术语 grep 规则）；
- 由 CI 串联执行；级别（fail / warn）由项目自定。

### 9.3 `checks/keel-lint.sh`

实测版（兼容 macOS 自带 bash 3.2；已通过 **42 例**故障注入——**33 例 fail（覆盖 31 类缺陷）**：超行数 / 超字节 / 单行超限 / 目录文件数 / frontmatter 缺失·超行数·超字节 / 字段缺失 / status 值域 / severity 值域 / keywords 为空 / 日期格式 / 缺 triggers / 命名含日期 / 命名含大写 / **域索引含正文** / 索引漏登记 / 引用环 / 引用环外的**链接图孤儿**（含"正文提及但未链接"的回归例）/ 缺必读文件 / 缺 keel-version / 缺 project-state / 缺预算真源 / **缺闭环钩子本体** / 缺点火锚点 / 死链（含冷区）/ 三段式缺失 / 例外决策缺 created / superseded-by 指向不存在 / **CHANGELOG 缺当期小节** / **README 徽章版本漂移**；**2 类告警**：陈旧 / 蒸馏阈值；**8 类合法基线**：MVP 全绿 / `_template` 三级豁免 / `decisions/` 陈旧豁免 / `stale-check: off` 逃生口 / frontmatter 行内注释 / 模板占位字段不算数 / **无 CHANGELOG 与 README 的纯模板安装态 / 无徽章的自带 CHANGELOG（ADR 0016）**。**另有一项元检查**：`NOISE` —— 全部 42 例的 stderr 必须为空或命中显式豁免白名单（ADR 0014；此前此处只是一句描述，没人断言它）。

> 写这版脚本时实测抓到两个 bash 3.2 的坑，已修并在注释里标了出处：
> ① **变量后紧跟中文标点必须写成 `${st}）`，不能写 `$st）`**——实测在部分环境下 bash 3.2 会把中文标点的首字节并进变量名，`set -u` 下直接报 `unbound variable`（v2 脚本里 5 处都有这个问题）；
> ② **BSD / macOS 的 `tsort` 遇环仍然返回 0**，只把 `cycle in data` 写到 stderr（GNU `tsort` 才返回 1），所以环检测必须同时看退出码与 stderr。
> 这正是 §9 存在的理由：**"机器验的东西，必须先自己验过"**——包括验证脚本自己。

**怎么复现这 41 例**：`keel-starter` 随仓库带自测套件，用例与 §9.1 检查表一一对应（每个用例都标注它对应哪一行）：

```bash
bash keel/checks/test-lint.sh              # 41 例 + 元检查 + 文档一致性检查
bash keel/checks/test-lint.sh -v --keep     # 逐例详细输出，并保留临时 fixture 供排查
```

它同时守住两件事：

1. **每条规则都真的能判死对应故障**——为 §9.1 的每一项造一个"应该被判死"的故障仓库，外加 6 类"应该放行"的合法基线（MVP 全绿 / `_template` 豁免 / `decisions/` 陈旧豁免 / `stale-check: off` / frontmatter 行内注释 / 模板占位字段）；
2. **随仓库发布的 `keel-lint.sh` 与本文档 §9.3 逐字一致**——只要能在上级目录找到 DESIGN.md 就比对，不一致直接 FAIL。

> **为什么测试也必须进仓库**：规则会腐烂，**验证规则的脚本一样会腐烂**。改了检查项却忘了改用例、改了脚本却忘了改文档，两种漂移都只会表现为"lint 一直绿"——那正是 §9 要防的事。所以：**改 `keel-lint.sh` 必须同时改 `test-lint.py`，否则 CI 红**（§10.4 之四）。
> 自测本身用 python3 写（fixture 生成与断言更可靠）；`keel-lint.sh` 本体仍然只依赖 bash 3.2+ / awk / sed / find。

预算数字**不在脚本里定义真源**：内置默认值仅作兜底，`checks/budget.env` 才是唯一真源——**缺它直接判 fail**，避免"文档一套、脚本一套"。

```bash
# checks/budget.env —— 预算唯一真源（§7.1 的表格是它的文档副本）
MAX_INDEX=100;        BYTES_INDEX=4500         # 根 INDEX.md
MAX_DOMAIN_INDEX=80;  BYTES_DOMAIN_INDEX=3000  # 域内 */INDEX.md
MAX_NOW=60;           BYTES_NOW=2400           # NOW*.md
MAX_PIT=30;           BYTES_PIT=1200           # 单条坑
MAX_DOC=160;          BYTES_DOC=4800           # 其余单文档
BYTES_FM=600                                   # frontmatter 字节
MAX_LINE=360                                   # 任意单行字节
MAX_DIR_FILES=20                               # 单目录文件数
BYTES_SESSION=15000                            # §7.2 单轮加载总量（INDEX+NOW+按需命中）
STALE_DAYS=30; NOW_STALE_DAYS=7; DISTILL_AT=3
# v3.2：工具自身的执行时间也纳入预算（ADR 0008）。
# 起因：v3.1 的 lint 在 24 个文档上要 319 秒，而 §7 把加载量管到字节级
# 却对"检查自己多快"零约束——那是"机器验"唯一没覆盖到的地方。
# 上限按实测留足余量：Windows/Git Bash 实测在 97–193s 间波动（同代码两次测量），
# 取 300s 留 1.5× 余量；Linux CI 约 3–8s，永远不会触发。
# 超时只告警不 fail——机器慢不等于文件错（ADR 0008 明确否决过"性能当 fail"）。
LINT_SECONDS=300
```

```bash
#!/usr/bin/env bash
# keel-lint.sh —— Keel 一致性校验（v3）
# 用法:  bash keel/checks/keel-lint.sh keel            # 从项目根目录调用
#        bash checks/keel-lint.sh                     # 在 keel/ 内调用（默认 .）
# 退出码: 0 = 通过（含 warn）；1 = 存在 fail；2 = keel 目录不存在
# 口径:  热区 = 全部 md 减去 archive/ 与 NOW-history/；冷区只做死链检查。
# 依赖:  bash 3.2+ / awk / sed / find / tsort（可选）/ git（仅 frozen 检查用）
set -uo pipefail

KEEL_DIR="${1:-.}"; KEEL_DIR="${KEEL_DIR%/}"
[ -d "$KEEL_DIR" ] || { echo "❌ 目录不存在: $KEEL_DIR"; exit 2; }

# ---------- 硬预算默认值（兜底；真源是 checks/budget.env） ----------
MAX_INDEX=100;        BYTES_INDEX=4500
MAX_DOMAIN_INDEX=80;  BYTES_DOMAIN_INDEX=3000
MAX_NOW=60;           BYTES_NOW=2400
MAX_PIT=30;           BYTES_PIT=1200
MAX_DOC=160;          BYTES_DOC=4800
BYTES_FM=600
MAX_LINE=360
MAX_DIR_FILES=20
STALE_DAYS=30
NOW_STALE_DAYS=7
DISTILL_AT=3
LINT_SECONDS=300                 # 工具自身的时限预算（ADR 0008）；超时只告警不 fail

# §4.1 门外锚点原文（唯一允许存在于 Keel 之外的一句）
ANCHOR='任何任务开始前，先读 keel/INDEX.md 与其中指向的 NOW.md，并遵守 INDEX.md 里的检索协议。'

fail=0
fail_msg() { echo "❌ $1"; fail=1; }
warn_msg() { echo "⚠️ $1"; }

# ---------- budget.env（唯一真源；缺失即 fail，兜底用上方默认值） ----------
if [ -f "$KEEL_DIR/checks/budget.env" ]; then
  . "$KEEL_DIR/checks/budget.env"
else
  fail_msg "缺预算真源 checks/budget.env（§9.3），已退回内置默认值"
fi

hot_files() { find "$KEEL_DIR" -name '*.md' -not -path '*/archive/*' -not -path '*/NOW-history/*' 2>/dev/null; }
all_files() { find "$KEEL_DIR" -name '*.md' 2>/dev/null; }
rel_of() { printf '%s' "${1#"$KEEL_DIR"/}"; }
# 取首个 --- 块（v3 修正：不再只扫前 12 行，否则字段放后面会被误判为"缺失"）
fm_block() { awk 'NR==1 && $0=="---" { f=1; next } f && $0=="---" { exit } f { print }' "$1" 2>/dev/null; }
fm_end_line() { awk 'NR==1 && $0=="---" { next } /^---$/ { print NR; exit }' "$1" 2>/dev/null; }
# frontmatter 按 YAML 解析：`key: value   # 注释` 里的行内注释必须剥掉
# （§5.2 / §5.3 的模板自带注释，不剥就会把注释当成值的一部分，直接误判值域非法）
# `key: # 注释` 这种"值整个是注释"的写法同样按空值处理（YAML 语义），否则
# 会得到一个假的非空值——例如占位用的 `superseded-by:` 会被误判成"指向不存在的文件"
yaml_val() { sed -E "s/^#.*$//; s/[[:space:]]+#.*$//; s/[[:space:]]+$//"; }
fm_val() { fm_block "$1" | grep -m1 "^$2:" | sed -E "s/^$2:[[:space:]]*//" | yaml_val; }
# YYYY-MM-DD → epoch 秒，**纯 shell 算术，零 fork**（v3.4.0 / ADR 0013 续）
# 原实现每次调用跑两次 `date`（先试 BSD 的 -j -f，在 Linux/Git Bash 上必然失败，
# 再试 GNU 的 -d）—— 实测每次 ~250ms，段 10 每文件调 1–2 次，是剩余最大的一块。
# 改用 Howard Hinnant 的 days_from_civil（公历恒等式，无闰年特殊分支）。
# **该算法已对 23 个日期与 `date -u -d` 逐字对照**（含 1900/2100 非闰年世纪、
# 2000/2024 闰年、1600/9999 边界），非法输入一律拒绝——判据与报错文案不变。
to_epoch() {
  case "$1" in
    [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]) ;;
    *) return 1 ;;
  esac
  _y=${1%%-*}; _r=${1#*-}; _m=${_r%%-*}; _d=${1##*-}
  # 显式去前导零：bash 里 08 会被当八进制（$((08)) 直接报错）
  _y=$((10#$_y)); _m=$((10#$_m)); _d=$((10#$_d))
  [ "$_m" -ge 1 ] && [ "$_m" -le 12 ] || return 1
  [ "$_d" -ge 1 ] && [ "$_d" -le 31 ] || return 1
  [ "$_y" -ge 1 ] || return 1
  [ "$_m" -le 2 ] && _y=$((_y - 1))
  _era=$(( _y / 400 ))
  _yoe=$(( _y - _era * 400 ))
  if [ "$_m" -gt 2 ]; then _doy=$(( (153*(_m-3) + 2) / 5 + _d - 1 ))
  else _doy=$(( (153*(_m+9) + 2) / 5 + _d - 1 )); fi
  _doe=$(( _yoe*365 + _yoe/4 - _yoe/100 + _doy ))
  REPLY=$(( (_era*146097 + _doe - 719468) * 86400 ))
  return 0
}

# ---------- 性能：零 fork 的取值方式（v3.3.9 / ADR 0013）----------
# 实测（Windows/Git Bash，N=30）：**`v=$(纯 shell 函数)` 本身就要 ~100ms**，
# 因为命令替换会开一个子 shell——**与函数体内有没有外部命令无关**。
# 直接调用（不取返回值）是 ~0ms；用全局变量回传也是 ~0ms。
# 全脚本原有 30 个 `$(rel_of|basename|fmq|…)` 站点 × 39 文件 ≈ 1,170 次 fork ≈ 117s，
# 占实测 142s 的大头（ADR 0008 只消掉了真外部命令那层，没消掉这层）。
#
# 所以下面每个"取 X"函数都配一个 **setter 版**：结果写进 REPLY / REL / BASE，
# 调用处不写 `$(...)`。**语义、判据、报错文案一字不改**——只换传值方式。
rel_set() { REL="${1#"$KEEL_DIR"/}"; }
base_set() { BASE="${1##*/}"; }

# ---------- 性能：把 per-file 的 fork 批量化（v3.2）----------
# 动因：实测 24 个文档的目录，单次 lint 要 319 秒（Windows / Git Bash）。
# 根因不是检查本身复杂，而是**进程创建成本**——单次 fork 在该环境约 370ms，
# 而原实现有 ~1500 次 per-file fork（wc×2、awk、grep、sed 各自单文件调用）。
# 同样的检查用 xargs 批量做，实测 16.1s → 0.52s（31×）。
# 做法：文件清单先落成一份 NUL 分隔的清单，再整体喂给 awk / wc。
# 语义不变——同样的输入、同样的判据、同一套报错文案；只是把 N 次进程换成 1 次。

# 临时目录：**创建后立刻归一化成 POSIX 路径**再往下用，否则清理在部分环境下静默失败。
# 起因（坑 safe-delete-shim-blocks-cleanup）：Windows 上 `mktemp -d` 返回
# `C:\Users\...\Temp/tmp.XXXXXXXX`——**含盘符且混用两种分隔符**，本身就是畸形路径。
# PATH 前段的安全删除垫片按规则拒绝内嵌盘符 → trap 的 `rm -rf` 被拒（rc=1）→
# 每次 lint 都在 %TEMP% 留一个目录（历史实测堆积 301 个）。
# 修法不是"让判据闭嘴"（那是迎合环境），而是消除路径表示的歧义。
# 用 `pwd -P`（POSIX 平台与 Git Bash 都有，不依赖 MSYS 专有的 -W）：
# 它给出规范的绝对路径，实测垫片放行、目录确实被删。
# 注意：`pwd` 失败时**不赋空值**——那样trap 会去删空路径，而 tmp 下游文件也会跟着失效。
tmp=$(mktemp -d)
if _tp=$(cd "$tmp" 2>/dev/null && pwd -P 2>/dev/null) && [ -n "$_tp" ]; then
  tmp="$_tp"
fi
unset _tp
trap 'rm -rf "$tmp"' EXIT
# 用临时文件收集结果：兼容 bash 3.2（case 不能直接出现在 $() 内），也避开管道子 shell 吞掉 fail 计数
deadf="$tmp/dead"; refd="$tmp/refd"; longf="$tmp/long"; idxbad="$tmp/idxbad"; edges="$tmp/edges"; pitmiss="$tmp/pitmiss"; pitmisslist="$tmp/pitmisslist"

HOTLIST="$tmp/hot.z"     # 热区清单（NUL 分隔，供 xargs 批量消费）
ALLLIST="$tmp/all.z"     # 全量清单（含冷区，NUL 分隔）
HOTLINES="$tmp/hot.ln"   # 热区清单（换行分隔，供 while read 消费）
ALLLINES="$tmp/all.ln"   # 全量清单（换行分隔）
# 两种视图各存一份的原因：xargs -0 读 NUL 清单（路径含空格安全），
# 而后面 10 处 `while IFS= read -r f` 是按行读的——若让 hot_files 直接吐 NUL，
# 那些循环会读到一个空行就 EOF，于是**所有后续检查静默跳过**（不报错、判死失效）。
# 路径含空格在这份换行清单里也不安全，但 keel 约定文件名 kebab-case 不含空格
# （§3.4，且 lint 第 4 项会判含空格的文件名），故按行读是安全的。
hot_files() { cat "$HOTLINES"; }
all_files() { cat "$ALLLINES"; }
# 供 xargs 消费：-0 读 NUL 分隔。
# **用法约定（踩过坑，务必照此写）**：清单路径必须走环境变量 XLIST，
# 不能作为 xrun 的第一个位置参数——`xargs -0 CMD "$@"` 里 xargs 会把 "$@"
# 里的每一项都当成"要追加到 CMD 后面的文件名"。于是 `xrun list awk 'prog'`
# 会执行成 `awk list prog file1 file2…`：awk 把清单和脚本都当输入文件名，
# 结果读不到任何文件、输出为空——**而且不报任何错**（实测踩过：
# "xargs: hot.z: No such file or directory" 只在清单路径不完整时才现形）。
# 正确形态：XLIST=清单; xrun awk 'prog'   （xrun 内部只做 xargs -0 CMD < "$XLIST"）
XLIST=""
xrun() { [ -s "$XLIST" ] || return 0; xargs -0 "$@" < "$XLIST"; return 0; }

find "$KEEL_DIR" -name '*.md' -not -path '*/archive/*' -not -path '*/NOW-history/*' -print0 2>/dev/null | sort -z > "$HOTLIST"
find "$KEEL_DIR" -name '*.md' -print0 2>/dev/null | sort -z > "$ALLLIST"
tr '\0' '\n' < "$HOTLIST" > "$HOTLINES"
tr '\0' '\n' < "$ALLLIST" > "$ALLLINES"
HOTN=$(wc -l < "$HOTLINES" | tr -d '[:space:]')

# ---------- frontmatter 一次提取，后续全部查表（v3.2 性能）----------
# 原实现里 fm_val 每次调用 fork 4 次（awk + grep + sed + sed），而段 2/3/10
# 对每个文件要调 5–6 次 → 单文件 20+ 次 fork，24 文件就是 500+ 次。
# 这里改成：一个 awk 扫全部文件，把每个文件的 fm 字段一次算完落成查询表，
# 之后 fmq 直接查表（零 fork）。行为等价，判据与报错文案不变。
FMQ="$tmp/fmq"      # 查询表：<路径>\t<key>\t<value>
FMHAS="$tmp/fmhas"  # 每个文件的 fm 原始行（供"字段是否存在"判断）
if [ "$HOTN" -gt 0 ]; then
  # 一次 awk 扫全部文件，把每个文件的 fm 字段算完落成查询表（v3.4.9：附三个
  # 合成字段 _fmopen / _fmend / _fmbytes，段 2 流式结算由此零 fork）。
  # 收尾 flush 用 END，**不用 gawk 专有 ENDFILE**——BWK awk（macOS）把它当未定义
  # 变量、末文件字段静默丢失（坑 awk-gawk-gaps）；产物为空仍回落逐文件版。
  # LC_ALL=C：保证 length() 按字节计（与旧版 wc -c 同口径）。
  : > "$FMQ"
  XLIST="$HOTLIST"; LC_ALL=C xrun awk -v OFS='\t' '
    function trim(v) { sub(/^[[:space:]]+/, "", v); sub(/[[:space:]]+$/, "", v); return v }
    function yval(v) { if (v ~ /^#/) return ""; sub(/[[:space:]]+#.*$/, "", v); return trim(v) }
    function flush(   kk) {
      for (kk in seen) print pf, kk, val[kk]
      if (open_ != "") print pf, "_fmopen", open_
      if (end_ != "")  print pf, "_fmend", end_
      if (nb_   != "") print pf, "_fmbytes", nb_
      delete seen; delete val; open_ = ""; end_ = ""; nb_ = ""
    }
    FNR==1 {
      if (NR > 1) flush()
      infm = ($0 == "---"); pf = FILENAME
      open_ = (infm ? 1 : 0); end_ = ""; nb_ = length($0) + 1; next
    }
    {
      if (infm) {
        nb_ += length($0) + 1
        if ($0 == "---") { end_ = FNR; infm = 0; next }
        ci = index($0, ":")
        if (ci > 0) { k = substr($0, 1, ci - 1)
          if (k ~ /^[A-Za-z0-9_-]+$/ && !(k in val)) { seen[k] = 1; val[k] = yval(trim(substr($0, ci + 1))) } }
      }
    }
    END { flush() }
  ' > "$FMQ" 2>/dev/null
  if [ ! -s "$FMQ" ]; then
    : > "$FMQ"
    while IFS= read -r f; do
      LC_ALL=C awk -v OFS='\t' -v P="$f" '
        function trim(v) { sub(/^[[:space:]]+/, "", v); sub(/[[:space:]]+$/, "", v); return v }
        function yval(v) { if (v ~ /^#/) return ""; sub(/[[:space:]]+#.*$/, "", v); return trim(v) }
        NR==1 { infm = ($0 == "---"); open_ = (infm ? 1 : 0); end_ = ""; nb_ = length($0) + 1; next }
        {
          if (infm) {
            nb_ += length($0) + 1
            if ($0 == "---") { end_ = NR; infm = 0; next }
            ci = index($0, ":")
            if (ci > 0) { k = substr($0, 1, ci-1)
              if (k ~ /^[A-Za-z0-9_-]+$/ && !(k in val)) { val[k] = yval(trim(substr($0, ci+1))) } }
          }
        }
        END { for (kk in val) print P, kk, val[kk]
              if (open_ != "") print P, "_fmopen", open_
              if (end_ != "")  print P, "_fmend", end_
              if (nb_   != "") print P, "_fmbytes", nb_ }
      ' "$f" >> "$FMQ" 2>/dev/null
    done < "$HOTLINES"
  fi
fi
# fmq <文件> <键> / fmhas <文件> <键>：查表取值 / 判断字段存在。
# v3.2：原来每次调用 fork 一个 awk（段 2/3/10/11/12 合计 ~200 次）。
# 现在把查询表整份读进一个 shell 变量，用 case 做行首匹配——**零 fork**。
# 规模前提：查询表 = 文件数 × 字段数（keel-starter 实测 131 行），
# 几百个文档也只到几千行，shell 变量完全装得下。
# 换来的约束：值里不能有换行（frontmatter 是逐行键值对，天然满足）。
# 查表用**纯 shell 循环**（没有 printf/grep/cut/head 任何子进程）。
# 中间试过 `printf | grep | head | cut`，那仍是 4 次 fork／次调用，
# 200 次调用反而比原来的 1 次 fork 更慢（实测 119s → 154s）——
# 批量化不能只看"调用次数"，要看**每次调用内部有几个进程**。
KEEL_NL='
'
FMQ_RAW=""
if [ -s "$FMQ" ]; then FMQ_RAW=$(cat "$FMQ"); fi
# fmq <文件> <键>：命中则打印值（首行），未命中返回空
fmq() {
  [ -n "$FMQ_RAW" ] || return 0
  _want="$1	$2	"
  _rest="$FMQ_RAW"
  while [ -n "$_rest" ]; do
    _line="${_rest%%$KEEL_NL*}"
    if [ "$_line" = "$_rest" ]; then _rest=""; else _rest="${_rest#*$KEEL_NL}"; fi
    case "$_line" in
      "$_want"*) printf '%s' "${_line#"$_want"}"; return 0 ;;
    esac
  done
  return 0
}
# 零 fork 版：结果写进 REPLY（未命中时为空，与 fmq 打印空串的行为一致）
fmq_set() {
  REPLY=""
  [ -n "$FMQ_RAW" ] || return 0
  _want="$1	$2	"
  _rest="$FMQ_RAW"
  while [ -n "$_rest" ]; do
    _line="${_rest%%$KEEL_NL*}"
    if [ "$_line" = "$_rest" ]; then _rest=""; else _rest="${_rest#*$KEEL_NL}"; fi
    case "$_line" in
      "$_want"*) REPLY="${_line#"$_want"}"; return 0 ;;
    esac
  done
  return 0
}
# fmhas <文件> <键>：字段是否存在（值可为空，故与 fmq 分开判断）
fmhas() {
  [ -n "$FMQ_RAW" ] || return 1
  _want="$1	$2	"
  _rest="$FMQ_RAW"
  while [ -n "$_rest" ]; do
    _line="${_rest%%$KEEL_NL*}"
    if [ "$_line" = "$_rest" ]; then _rest=""; else _rest="${_rest#*$KEEL_NL}"; fi
    case "$_line" in
      "$_want"*) return 0 ;;
    esac
  done
  return 1
}

# ---------- 链接一次提取，段 6/8/9 共用（v3.2 性能）----------
# 段 6（引用环）、段 8（死链）、段 9（孤儿）原本各自对每个文件跑
# `grep -oE + sed + tr`；段 9 还要为**每条链接** fork 2 次 cd + dirname/basename。
# 实测：24 文件的段 9 单独跑要 49 秒（占整体 325 秒的大头）。
# 这里改成一次 awk 抽出所有链接落表，三段各自消费——把 N×M 次进程降到 1 次。
#
# 关键写法说明：awk 的脚本用单引号包住，**不能**把文件清单直接接在脚本后面
# （那是给 awk 当输入文件名，bash 会先执行它 —— 实测踩过，报了一屏
# "scope:: command not found"）。正确做法是用 `xargs ... | awk` 或
# `awk -f 脚本文件`，这里统一走 xargs 管道。
LINKS="$tmp/links"
if [ "$HOTN" -gt 0 ]; then
  # 注意喂的是 $HOTLIST（NUL 分隔），不是 $HOTLINES —— xargs -0 只认 NUL。
  # 喂错的话 xargs 会把整份换行清单当成**一个文件名**，awk 读不到文件、
  # LINKS 变空，于是段 9 把所有文档误报成孤儿（实测踩过）。
  XLIST="$HOTLIST"; xrun awk '
    { line = $0
      while (match(line, /\]\([^)]+\)/)) {
        seg = substr(line, RSTART + 2, RLENGTH - 3)
        p = seg; sub(/[ \t].*$/, "", p)
        if (p != "") print FILENAME "\t" p
        line = substr(line, RSTART + RLENGTH)
      }
      line = $0
      while (match(line, /@[A-Za-z0-9_.\/-]+\.md/)) {
        print FILENAME "\t" substr(line, RSTART + 1, RLENGTH - 1)
        line = substr(line, RSTART + RLENGTH)
      }
    }
  ' 2>/dev/null | sort -u > "$LINKS"
fi


_t0=$(date +%s 2>/dev/null || echo 0)
echo "keel-lint · $(date '+%Y-%m-%d %H:%M') · 目录=$KEEL_DIR · 热区文档=$HOTN"
echo "── 1. 预算：行数 / 字节 / 单行 / 目录文件数"
# 1a. 行数 + 字节：**一次 wc 扫全部文件**（原为每文件 2 次 wc + 2 次 tr = 4 次 fork）
# 路径含空格安全：wc 由 xargs -0 喂 NUL 分隔清单，不经过 shell 分词。
# 输出形如 "  42  1234 /path/to/file"，末列含空格时用 tab 切分前两列、其余归到末列。
if [ "$HOTN" -gt 0 ]; then
  XLIST="$HOTLIST"; xrun wc -lc > "$tmp/sizes" 2>/dev/null
  # wc 多文件模式会追加一行 "total"，必须显式排除（实测踩过：
  # 那行被当成文件名 total，报出 "超行数 793>160: total" 的假 fail）
  while IFS=$' \t' read -r n b f; do
    [ -n "${f:-}" ] || continue
    [ "${f##*/}" = "total" ] && continue
    case "$n" in ''|*[!0-9]*) continue ;; esac
    rel_set "$f"; rel=$REL
    case "$rel" in
      */INDEX.md)          lim=$MAX_DOMAIN_INDEX; blim=$BYTES_DOMAIN_INDEX ;;
      INDEX.md)            lim=$MAX_INDEX;        blim=$BYTES_INDEX ;;
      NOW*.md|*/NOW*.md)   lim=$MAX_NOW;          blim=$BYTES_NOW ;;
      pitfalls/*)          lim=$MAX_PIT;          blim=$BYTES_PIT ;;
      *)                   lim=$MAX_DOC;          blim=$BYTES_DOC ;;
    esac
    [ "$n" -gt "$lim" ]  && fail_msg "超行数 ${n}>${lim}: $rel"
    [ "$b" -gt "$blim" ] && fail_msg "超字节 ${b}>${blim}: $rel"
  done < "$tmp/sizes"
fi

# 单行上限：LC_ALL=C 保证 awk 的 length() 按字节而非字符计
# 批量版：一次 awk 扫全部文件（原来每文件 1 次 awk = 24 次 fork）
if [ "$HOTN" -gt 0 ]; then
  LC_ALL=C XLIST="$HOTLIST"; xrun awk -v L="$MAX_LINE" '
    { if (length($0) > L) printf "❌ 单行超限 %d>%d 字节: %s:%d\n", length($0), L, FILENAME, FNR }
  ' > "$longf" 2>/dev/null
fi
if [ -s "$longf" ]; then sed -n '1,10p' "$longf"; fail=1; fi

# 目录文件数：一次 find -printf 风格不可移植，改用 find 出行 + 一次 awk 聚合
find "$KEEL_DIR" -type d 2>/dev/null | while IFS= read -r d; do
  case "$d" in */archive|*/archive/*|*/NOW-history|*/NOW-history/*) continue ;; esac
  echo "$d"
done > "$tmp/dirs" 2>/dev/null
# 每个目录一次 ls 仍是 per-dir fork；这里用一次 find 输出全部条目后 awk 按目录聚合
if [ -s "$tmp/dirs" ]; then
  find "$KEEL_DIR" -type f 2>/dev/null | awk -v K="$KEEL_DIR" -v MAXD="$MAX_DIR_FILES" '
    { p=$0; sub("/[^/]*$", "", p); if (p!=K) cnt[p]++ }
    END { for (d in cnt) if (cnt[d] > MAXD) {
             r=d; sub("^" K "/", "", r)
             printf "❌ 目录文件超限 %d>%d: %s/\n", cnt[d], MAXD, r } }
  ' > "$tmp/dirbig" 2>/dev/null
  if [ -s "$tmp/dirbig" ]; then sort -u "$tmp/dirbig"; fail=1; fi
fi

echo "── 2. frontmatter：存在性 / 字段 / 行数 / 字节"
# v3.4.9：改流式结算——单趟扫 FMQ（含合成字段 _fmopen/_fmend/_fmbytes），
# 全程不调用 fmq_set/head/awk/sed/wc。教训：热点＝查表调用数 × 表行数
# （perf-findings #2/#4 两次失败同源）。判定语义与旧版逐字同源：
# 字段存在性＝表中出现该键的行（值可空，与 fmhas 注释一致）。
S2_CUR=""; S2_SEEN=""
S2_open=""; S2_end=""; S2_nb=""; S2_hs=""; S2_hst=""; S2_hlv=""; S2_hkw=""
S2_htr=""; S2_hsev=""; S2_htrs=""; S2_hkv=""; S2_hps=""
s2_finish() {
  [ -n "$S2_CUR" ] || return 0
  base_set "$S2_CUR"
  case "$BASE" in _template*) return 0 ;; esac
  rel_set "$S2_CUR"
  if [ "$S2_open" != "1" ]; then fail_msg "缺 frontmatter: $REL"; return 0; fi
  if [ -z "$S2_end" ]; then fail_msg "frontmatter 未闭合: $REL"; return 0; fi
  nl=$((S2_end - 2))
  [ "$nl" -gt 10 ] && fail_msg "frontmatter 超行数 ${nl}>10: $REL"
  [ "${S2_nb:-0}" -gt "$BYTES_FM" ] && fail_msg "frontmatter 超字节 ${S2_nb}>${BYTES_FM}: $REL"
  [ -n "$S2_hs" ]  || fail_msg "frontmatter 缺 scope: $REL"
  [ -n "$S2_hst" ] || fail_msg "frontmatter 缺 status: $REL"
  [ -n "$S2_hlv" ] || fail_msg "frontmatter 缺 last-verified: $REL"
  [ -n "$S2_hkw" ] || fail_msg "frontmatter 缺 keywords: $REL"
  case "$REL" in
    */INDEX.md) ;;   # 域索引只查基础字段
    skills/*)   [ -n "$S2_htr" ]  || fail_msg "skill 缺 trigger: $REL" ;;
    pitfalls/*) [ -n "$S2_hsev" ] || fail_msg "坑条目缺 severity: $REL"
                [ -n "$S2_htrs" ] || fail_msg "坑条目缺 triggers: $REL" ;;
  esac
  case "$REL" in
    INDEX.md)   [ -n "$S2_hkv" ] || fail_msg "根 INDEX 缺 keel-version: $REL"
                [ -n "$S2_hps" ] || fail_msg "根 INDEX 缺 project-state: $REL" ;;
  esac
  return 0
}
while IFS=$'\t' read -r s2f s2k s2v; do
  if [ "$s2f" != "$S2_CUR" ]; then
    s2_finish
    S2_SEEN="${S2_SEEN}${s2f}|"
    S2_CUR="$s2f"
    S2_open=""; S2_end=""; S2_nb=""; S2_hs=""; S2_hst=""; S2_hlv=""; S2_hkw=""
    S2_htr=""; S2_hsev=""; S2_htrs=""; S2_hkv=""; S2_hps=""
  fi
  case "$s2k" in
    _fmopen)  S2_open="$s2v" ;;
    _fmend)   S2_end="$s2v" ;;
    _fmbytes) S2_nb="$s2v" ;;
    scope)    S2_hs=1 ;;
    status)   S2_hst=1 ;;
    last-verified) S2_hlv=1 ;;
    keywords) S2_hkw=1 ;;
    trigger)  S2_htr=1 ;;
    severity) S2_hsev=1 ;;
    triggers) S2_htrs=1 ;;
    keel-version)  S2_hkv=1 ;;
    project-state) S2_hps=1 ;;
  esac
done <<< "$FMQ_RAW"
s2_finish
# 表中未出现的文件（空文件不触发 FNR==1）——旧版头行判定会报"缺 frontmatter"；
# 表整体为空（降级）时不报，避免把构建降级误判成内容违规。
if [ -n "$FMQ_RAW" ]; then
  while IFS= read -r f; do
    base_set "$f"
    case "$BASE" in _template*) continue ;; esac
    case "$S2_SEEN" in *"$f|"*) ;; *) rel_set "$f"; fail_msg "缺 frontmatter: $REL" ;; esac
  done < "$HOTLINES"
fi

echo "── 3. 值域与格式（status / severity / keywords / last-verified / triggers）"
# v3.4.8：流式扫描——FMQ 表按文件分组且与 HOTLINES 同序，**单趟扫完**，
# 在文件边界结算该文件。原实现对每个文件 fmq_set 5 次（每次重扫全表），
# 复杂度 O(文件数 × 表行数)；现在 O(表行数)。判据与报错文案逐字不变。
s3_f() {   # $1 = 文件路径；用本趟已累积的 _s3_* 变量结算
  base_set "$1"; case "$BASE" in _template*) return ;; esac
  [ "$_s3_has" = 1 ] || return
  rel_set "$1"; rel=$REL
  case "${_s3_st:-}" in
    active|distilled|archived|"") ;;
    *) fail_msg "status 值域非法（${_s3_st}）: $rel" ;;
  esac
  if [ -n "${_s3_lv:-}" ]; then
    case "$_s3_lv" in
      [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]) ;;
      *) fail_msg "last-verified 非 YYYY-MM-DD（${_s3_lv}）: $rel" ;;
    esac
  fi
  case "${_s3_kw:-}" in ""|"[]"|"[ ]") fail_msg "keywords 为空: $rel" ;; esac
  case "$rel" in
    pitfalls/*)
      case "${_s3_sv:-}" in
        P0|P1|P2|P3|"") ;;
        *) fail_msg "severity 值域非法（${_s3_sv}）: $rel" ;;
      esac
      case "${_s3_tg:-}" in
        ''|*[!0-9]*) [ -n "${_s3_tg:-}" ] && fail_msg "triggers 非数字（${_s3_tg}）: $rel" ;;
      esac
      ;;
  esac
}
_s3_cur=""; _s3_st=""; _s3_lv=""; _s3_kw=""; _s3_sv=""; _s3_tg=""; _s3_has=0
while IFS=$'\t' read -r _s3_p _s3_k _s3_v || [ -n "$_s3_p" ]; do
  if [ "$_s3_p" != "$_s3_cur" ]; then
    [ -n "$_s3_cur" ] && s3_f "$_s3_cur"
    _s3_cur="$_s3_p"; _s3_st=""; _s3_lv=""; _s3_kw=""; _s3_sv=""; _s3_tg=""; _s3_has=0
  fi
  case "$_s3_k" in
    status) _s3_st="$_s3_v"; _s3_has=1 ;;
    last-verified) _s3_lv="$_s3_v" ;;
    keywords) _s3_kw="$_s3_v" ;;
    severity) _s3_sv="$_s3_v" ;;
    triggers) _s3_tg="$_s3_v" ;;
  esac
done < "$FMQ"
[ -n "$_s3_cur" ] && s3_f "$_s3_cur"

echo "── 4. 命名（kebab-case / 热区禁日期）"
while IFS= read -r f; do
  base_set "$f"; base=$BASE; rel_set "$f"; rel=$REL
  # 固定名豁免：根级入口/地图/宪法/术语/NOW 由 §3.2 定义，不受 kebab-case 约束
  case "$base" in
    _template*|INDEX.md|CONSTITUTION.md|ARCHITECTURE.md|GLOSSARY.md|NOW.md|NOW-*.md) continue ;;
  esac
  case "$base" in *[A-Z]*)     fail_msg "命名含大写（应 kebab-case）: $rel" ;; esac
  case "$base" in *"_"*|*" "*) fail_msg "命名含下划线/空格（应 kebab-case）: $rel" ;; esac
  case "$base" in *[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]*) fail_msg "热区文件名含日期: $rel" ;; esac
done < <(hot_files)

echo "── 5. 域索引：纯表格 / 坑条目登记"
# 5a. 任何域索引（*/INDEX.md）只允许表格行；根 INDEX.md 例外（它是唯一入口，见 §5.1）
: > "$idxbad"
while IFS= read -r x; do
  rel_set "$x"; xrel=$REL
  case "$xrel" in */INDEX.md) ;; *) continue ;; esac
  awk -v R="$xrel" '
    NR==1 && $0=="---" { f=1; next }
    f==1 && $0=="---" { f=0; next }
    f==1 { next }
    $0 ~ /^[[:space:]]*$/ { next }
    $0 !~ /^\|/ { printf "❌ 域索引含非表格正文: %s 第%d行: %s\n", R, NR, substr($0,1,30) }
  ' "$x"
done < <(hot_files) >> "$idxbad"
if [ -s "$idxbad" ]; then sed -n '1,6p' "$idxbad"; fail=1; fi
# 5b. 坑条目必须登记进 pitfalls/INDEX.md
if [ -f "$KEEL_DIR/pitfalls/INDEX.md" ]; then
  while IFS= read -r p; do
    base_set "$p"; b=$BASE
    case "$b" in INDEX.md|_template*) continue ;; esac
    grep -qF "$b" "$KEEL_DIR/pitfalls/INDEX.md" || { rel_set "$p"; fail_msg "坑条目未登记进 pitfalls/INDEX.md: $REL"; }
  done < <(find "$KEEL_DIR/pitfalls" -name '*.md' 2>/dev/null)
else
  fail_msg "缺 pitfalls/INDEX.md"
fi

echo "── 6. 引用图环检测（md → md；§3.1 禁止循环引用，路由枢纽 INDEX.md 除外）"
# 边表由 LINKS 一次 awk 得出（v3.2：不再每文件跑 grep+sed+tr）
if [ -s "$LINKS" ]; then
  awk -F'\t' '
    { f = $1; l = $2
      if (l ~ /^https?:/ || l ~ /^mailto:/ || l == "") next
      sub(/#.*$/, "", l)
      if (l !~ /\.md$/) next
      n = split(f, a, "/"); from = a[n]
      if (from == "INDEX.md") next
      m = split(l, b, "/"); to = b[m]
      # 索引是路由枢纽（人人都指向它、它也指向人人），把它当普通节点必然误报
      if (to == "INDEX.md") next
      if (from == to) next
      print from, to
    }
  ' "$LINKS" | sort -u > "$edges" 2>/dev/null
fi
sort -u "$edges" -o "$edges"
if [ -s "$edges" ]; then
  if command -v tsort >/dev/null 2>&1; then
    tsort "$edges" >/dev/null 2>"$tmp/tsort.err"; tsort_rc=$?
    # 注意：BSD/macOS 的 tsort 遇环仍返回 0，只把 "cycle in data" 写到 stderr；
    # GNU tsort 返回 1。所以"退出码非 0"和"stderr 非空"两个条件要一起看。
    if [ "$tsort_rc" -ne 0 ] || [ -s "$tmp/tsort.err" ]; then
      fail_msg "引用存在环（§3.1 禁止循环引用）: $(head -1 "$tmp/tsort.err")"
    fi
  else
    warn_msg "环境无 tsort，跳过循环引用检查"
  fi
fi

echo "── 7. 必读文件与点火锚点"
for need in INDEX.md CONSTITUTION.md; do
  [ -f "$KEEL_DIR/$need" ] || fail_msg "缺必读文件: $need"
done
[ "$(find "$KEEL_DIR" -maxdepth 1 -name 'NOW*.md' | wc -l | tr -d '[:space:]')" -eq 0 ] && fail_msg "缺必读文件: NOW*.md"
anchor_ok=0
for cand in CLAUDE.md AGENTS.md .cursorrules .cursor/rules/keel.mdc; do
  for pfx in "$KEEL_DIR/.." "$KEEL_DIR"; do
    [ -f "$pfx/$cand" ] || continue
    grep -qF "$ANCHOR" "$pfx/$cand" && anchor_ok=1
  done
done
[ "$anchor_ok" -eq 1 ] || fail_msg "点火锚点缺失或与 §4.1 原文不一致（查 CLAUDE.md / AGENTS.md / .cursorrules / .cursor/rules）"

echo "── 8. 死链（@路径 与 markdown 链接，相对所在文件目录）"
# 死链要查冷区（archive / NOW-history），所以按全量清单再抽一次链接。
# 冷区文件极少（keel-starter 里 1 个），这次额外 awk 的成本可忽略。
DEADL="$tmp/deadlinks"
if [ -s "$ALLLINES" ]; then
  xargs -0 awk '
    { line = $0
      while (match(line, /\]\([^)]+\)/)) {
        seg = substr(line, RSTART + 2, RLENGTH - 3)
        p = seg; sub(/[ \t].*$/, "", p)
        if (p != "") print FILENAME "\t" p
        line = substr(line, RSTART + RLENGTH)
      }
      line = $0
      while (match(line, /@[A-Za-z0-9_.\/-]+\.md/)) {
        print FILENAME "\t" substr(line, RSTART + 1, RLENGTH - 1)
        line = substr(line, RSTART + RLENGTH)
      }
    }
  ' < "$ALLLIST" 2>/dev/null | sort -u > "$DEADL"
fi
: > "$deadf"
if [ -s "$DEADL" ]; then
  while IFS=$'\t' read -r f link; do
    [ -n "${link:-}" ] || continue
    case "$link" in http*|mailto:*|"") continue ;; esac
    t="${link%%#*}"; [ -z "$t" ] && continue
    case "$f" in
      */*) dir=${f%/*} ;;
      *)   dir="." ;;
    esac
    [ -e "$dir/$t" ] || echo "❌ 死链: $t  (见 ${f#"$KEEL_DIR"/})"
  done < "$DEADL" >> "$deadf"
fi
if [ -s "$deadf" ]; then cat "$deadf"; fail=1; fi

echo "── 9. 孤儿（热区文档未被任何热区文档以链接引用；INDEX/_template 豁免）"
# v3.1 修正：孤儿判定改用"真实链接图"——把每条链接解析成目标文件的绝对路径再比对。
# 旧实现是「grep 文件名」的近似：正文里偶然出现同名子串会漏报，文件改名会误报。
# 被引用目标集合：把 LINKS 里每条链接按"相对所在文件目录"解析成规范化路径。
# v3.2：原实现对**每条链接** fork 2 次 cd + 2 次 dirname/basename，
# 24 文件 × 平均 8 条链接 ≈ 400 次进程，实测这一段单独就 49 秒。
# 现在改成一次 awk 做纯字符串路径规范化（不依赖 cd —— cd 在 Windows 上
# 还会把路径分隔符与预期搞乱），存在性判断留给后面一次批量 test。
# 注意：LINKS 里的 $1 已经是 find 输出的路径（本身就含 $KEEL_DIR 前缀），
# 所以这里只做"相对所在文件目录"的拼接，**不能再拼一次 K** ——
# 拼两次会得到 keel/keel/xxx，于是每个文件都"未被引用"、全量误报孤儿（实测踩过）。
awk -F'\t' '
  function norm(p,   parts, np, i, out, seg) {
    np = split(p, parts, "/"); out = ""
    for (i = 1; i <= np; i++) {
      seg = parts[i]
      if (seg == "" || seg == ".") continue
      if (seg == "..") { sub(/\/[^\/]*$/, "", out); continue }
      out = (out == "" ? seg : out "/" seg)
    }
    return out
  }
  { f = $1; l = $2
    if (l ~ /^https?:/ || l ~ /^mailto:/ || l == "") next
    sub(/#.*$/, "", l); if (l == "") next
    n = split(f, a, "/"); fdir = ""
    for (i = 1; i < n; i++) fdir = fdir a[i] "/"
    tgt = norm(fdir l)
    if (tgt != "") print tgt
  }
' "$LINKS" 2>/dev/null | sort -u > "$refd.raw" 2>/dev/null
# 存在性过滤：awk 不知道文件系统状态，用一次 while + [ -e ] 判定（无 fork）
: > "$refd"
if [ -s "$refd.raw" ]; then
  while IFS= read -r cand; do
    [ -e "$cand" ] && printf '%s\n' "$cand" >> "$refd"
  done < "$refd.raw"
fi
while IFS= read -r f; do
  base_set "$f"; base=$BASE
  case "$base" in INDEX.md|_template*) continue ;; esac
  grep -qxF "$f" "$refd" || fail_msg "孤儿（未被任何热区文档链接引用）: ${f#"$KEEL_DIR"/}"
done < "$HOTLINES"

echo "── 10. 陈旧（last-verified / NOW updated；豁免类目见 §9.4）"
today=$(date +%s)
# v3.4.8：同段 3，改流式扫描（单趟 O(表行数)）；判据与文案逐字不变。
s10_f() {
  base_set "$1"; case "$BASE" in _template*) return ;; esac
  rel_set "$1"; rel=$REL
  case "$rel" in decisions/*) return ;; esac              # ADR 定稿即不可变，见 §9.4
  [ "${_s10_sc:-}" = "off" ] && return   # 逃生口，需在 decisions/ 留理由
  d="${_s10_lv:-}"
  if [ -n "$d" ]; then
    if to_epoch "$d"; then e=$REPLY
    else e=""; fi
    if [ -n "$e" ]; then
      age=$(( (today - e) / 86400 ))
      [ "$age" -gt "$STALE_DAYS" ] && warn_msg "stale(${age}d): $rel"
    else
      warn_msg "last-verified 无法解析: $rel ($d)"
    fi
  fi
  case "$rel" in NOW*.md|*/NOW*.md)
    u="${_s10_upd:-}"
    if [ -z "$u" ]; then fail_msg "NOW 缺 updated: $rel"
    else
      to_epoch "$u" && { e=$REPLY
        [ -n "$e" ] && { age=$(( (today - e) / 86400 )); [ "$age" -gt "$NOW_STALE_DAYS" ] && warn_msg "NOW 已 ${age}d 未更新: $rel"; } }
    fi ;;
  esac
}
_s10_cur=""; _s10_sc=""; _s10_lv=""; _s10_upd=""
while IFS=$'\t' read -r _s10_p _s10_k _s10_v || [ -n "$_s10_p" ]; do
  if [ "$_s10_p" != "$_s10_cur" ]; then
    [ -n "$_s10_cur" ] && s10_f "$_s10_cur"
    _s10_cur="$_s10_p"; _s10_sc=""; _s10_lv=""; _s10_upd=""
  fi
  case "$_s10_k" in
    stale-check) _s10_sc="$_s10_v" ;;
    last-verified) _s10_lv="$_s10_v" ;;
    updated) _s10_upd="$_s10_v" ;;
  esac
done < "$FMQ"
[ -n "$_s10_cur" ] && s10_f "$_s10_cur"

echo "── 11. 坑条目（三段式 + 蒸馏阈值）"
# 三段式批量化（v3.4.1）：原为每条坑 3 次 grep（12 坑 = 36 次 fork，~3.6s）。
# **过滤与判断必须分开**：上一版把过滤写进 awk 的 `FNR==1` + `ENDFILE`，
# 而 `ENDFILE` **不受 skip 状态约束** → 12 条真坑全漏判、39 个非坑文件误报
# （坑：awk-enfile-ignores-skip-state）。
# 现在：① 过滤在 shell 侧（纯 `case`，零 fork）落成清单；② 一次 awk 扫清单里的全部文件。
# ② 用 `FNR==1` 切文件 + `END` 收尾——**POSIX awk 即可**，不依赖 gawk 的 ENDFILE。
: > "$pitmiss"
: > "$pitmisslist"
while IFS= read -r f; do
  rel_set "$f"; rel=$REL
  case "$rel" in pitfalls/*) ;; *) continue ;; esac
  base_set "$f"; case "$BASE" in INDEX.md|_template*) continue ;; esac
  printf '%s\n' "$f" >> "$pitmisslist"
done < <(hot_files)
if [ -s "$pitmisslist" ]; then
  tr '\n' '\0' < "$pitmisslist" | xargs -0 awk '
    function rel(p) { sub(/^.*\/keel\//, "keel/", p); return p }
    function report(  i) {
      for (i = 1; i <= 3; i++) if (!seen[i]) printf "❌ 坑条目缺失【%s】: %s\n", h[i], r
    }
    BEGIN { h[1]="## 症状"; h[2]="## 根因"; h[3]="## 正解" }
    FNR == 1 { if (NR > 1) report(); r = rel(FILENAME); seen[1]=seen[2]=seen[3]=0 }
    { for (i = 1; i <= 3; i++) if (index($0, h[i]) > 0) seen[i] = 1 }
    END { if (NR > 0) report() }
  ' 2>/dev/null | sort -u > "$pitmiss"
  if [ -s "$pitmiss" ]; then sed -n '1,10p' "$pitmiss"; fail=1; fi
fi

# v3.4.8：同段 3，改流式扫描（只关心 pitfalls/ 的 triggers 与 status）——
# 已蒸馏的不再提醒（v3.4.4）：`status: distilled` 就是"这条已被提炼进宪法"的标记，
# 它的存在意义就是让这条告警停下来；§7.4 的流程是
# 「triggers ≥ 3 → 提醒 → 提炼 + 置 distilled」，故蒸馏状态必须参与判断。
s11_f() {
  base_set "$1"; case "$BASE" in INDEX.md|_template*) return ;; esac
  rel_set "$1"; rel=$REL
  case "$rel" in pitfalls/*) ;; *) return ;; esac
  t="${_s11_tg:-0}"
  case "$t" in
    ''|*[!0-9]*) [ -n "${_s11_tg:-}" ] && warn_msg "triggers 非数字: $rel" ;;
    *)
      if [ "$t" -ge "$DISTILL_AT" ] && [ "${_s11_st:-}" != "distilled" ]; then
        warn_msg "待蒸馏（triggers=${t} ≥ ${DISTILL_AT}）: $rel"
      fi
      ;;
  esac
}
_s11_cur=""; _s11_tg=""; _s11_st=""
while IFS=$'\t' read -r _s11_p _s11_k _s11_v || [ -n "$_s11_p" ]; do
  if [ "$_s11_p" != "$_s11_cur" ]; then
    [ -n "$_s11_cur" ] && s11_f "$_s11_cur"
    _s11_cur="$_s11_p"; _s11_tg=""; _s11_st=""
  fi
  case "$_s11_k" in
    triggers) _s11_tg="$_s11_v" ;;
    status) _s11_st="$_s11_v" ;;
  esac
done < "$FMQ"
[ -n "$_s11_cur" ] && s11_f "$_s11_cur"


echo "── 12. 状态机（frozen 契约冻结 / 例外计数）"
IDX="$KEEL_DIR/INDEX.md"
if [ -f "$IDX" ]; then
  fmq_set "$IDX" project-state; ps=$REPLY
  case "${ps:-}" in
    frozen)
      if command -v git >/dev/null 2>&1 && git -C "$KEEL_DIR" rev-parse --git-dir >/dev/null 2>&1; then
        added=$(git -C "$KEEL_DIR" log --since="$(date '+%Y-%m-01')" --diff-filter=A --name-only --pretty=format: 2>/dev/null | grep -E '(^|/)contracts/' | grep -v '/_template' | sort -u)
        [ -n "$added" ] && fail_msg "frozen 期新增契约文件（§5.2 禁止）: $(printf '%s' "$added" | tr '\n' ' ')"
      fi ;;
    exploring|architecture-locked|building) ;;
    "") fail_msg "project-state 缺失或为空: INDEX.md" ;;
    *)  fail_msg "project-state 值域非法（${ps}）: INDEX.md" ;;
  esac
fi
# v3.4.10：流式结算——单趟扫 FMQ 取 decisions 文件的 type/created/superseded-by，
# 不调用 fmq_set（热点＝查表调用数 × 表行数，见 perf-findings #2/#4/#5）。
mon=$(date '+%Y-%m'); exc=0
S12_CUR=""; S12_type=""; S12_made=""; S12_sb=""
s12_finish() {
  [ -n "$S12_CUR" ] || return 0
  case "${S12_CUR##*/}" in _template*) return 0 ;; esac   # 模板不是真实记录（§3.4 豁免）
  if [ "$S12_type" = "exception" ]; then
    if [ -z "$S12_made" ]; then fail_msg "例外决策缺 created 字段: ${S12_CUR#"$KEEL_DIR"/}"
    else case "$S12_made" in "$mon"*) exc=$((exc + 1)) ;; esac; fi
  fi
  # 取代关系：superseded-by 必须指向存在的文件（ADR 靠"被谁取代"表达时效，而非 last-verified）
  if [ -n "$S12_sb" ]; then
    case "$S12_CUR" in */*) sbdir=${S12_CUR%/*} ;; *) sbdir="." ;; esac
    [ -e "$sbdir/$S12_sb" ] || fail_msg "superseded-by 指向不存在的文件（${S12_sb}）: ${S12_CUR#"$KEEL_DIR"/}"
  fi
  return 0
}
while IFS=$'\t' read -r s12f s12k s12v; do
  case "$s12f" in "$KEEL_DIR"/decisions/*.md) ;; *) continue ;; esac
  if [ "$s12f" != "$S12_CUR" ]; then
    s12_finish
    S12_CUR="$s12f"; S12_type=""; S12_made=""; S12_sb=""
  fi
  case "$s12k" in
    type) S12_type="$s12v" ;;
    created) S12_made="$s12v" ;;
    superseded-by) S12_sb="$s12v" ;;
  esac
done <<< "$FMQ_RAW"
s12_finish
[ "$exc" -gt 2 ] && fail_msg "本月例外决策 ${exc}>2，强制退回 building（§5.2）"

echo "── 13. 闭环钩子（本体存在且可执行；§10.4 铁律：缺一，闭环不成立）"
for h in pre-commit commit-msg; do
  hf="$KEEL_DIR/checks/hooks/$h"
  if [ ! -f "$hf" ]; then fail_msg "缺闭环钩子本体: checks/hooks/$h"
  elif [ ! -x "$hf" ]; then fail_msg "闭环钩子不可执行（需 chmod +x）: checks/hooks/$h"; fi
done

# 段 14（v3.4.5）：版本声明的三处副本必须一致。
#
# 为什么加这项：ADR 0010 立了"版本声明与可获取必须同时成立"，
# 发布仓 CI 也有 CHANGELOG 检查——**但两者都只存在于发布仓**。
# 2026-10-04 实测发现：keel-version 已到 3.4.4，CHANGELOG 最新小节还停在
# 3.4.2（缺两节 → CI 必然 exit 1），两仓 README 徽章停在 3.3.8。
# **判据存在却两周无人看**，这正是本项目引用的 Lint Leakage（62%）在自己身上复现。
#
# 所以这里补的是**机制性修复**：把"发布后门面会漂"从一次性补正变成判死。
# 三处副本任一滞后即 fail——**价值不在补上这一版，在拦住下一次**。
#
# 适用范围的诚实说明（§9.5 同类边界，v3.4.7 收窄触发）：
#   - 触发条件是「根或 keel/ 的 README 写了 keel 徽章」——徽章 = 自认 keel 发行仓；
#     真实用户项目（自带自己的 CHANGELOG、无徽章）→ 跳过，不误判
#     （实测：首个采用方 lytjs 安装当日被旧触发条件误判"缺当期小节"，ADR 0016）。
#   - 只查"副本存在时是否一致"，不负责生成它们（生成是发布脚本的事）。
VER_IDX="$KEEL_DIR/INDEX.md"
if [ -f "$VER_IDX" ]; then
  _v=$(sed -n 's/^keel-version:[[:space:]]*\([^[:space:]]*\).*/\1/p' "$VER_IDX" | head -1)
  case "${_v:-}" in
    ""|*[!0-9.]*) ;;# 缺失/非法：段 2 已在管，这里不重复报
    *)
      _root=$(dirname "$KEEL_DIR")
      # 副本二（先查）：README 徽章里的版本号。只在写了徽章时查——
      # 徽章同时是副本一（CHANGELOG）的触发条件：没徽章 = 不是 keel 发行仓。
      _badge_seen=""
      for _rd in "$_root/README.md" "$KEEL_DIR/README.md"; do
        [ -f "$_rd" ] || continue
        _badge=$(grep -o 'keel--version-[0-9][0-9.]*' "$_rd" 2>/dev/null | head -1 | sed 's/^keel--version-//')
        [ -n "${_badge:-}" ] || continue
        _badge_seen=1
        [ "$_badge" = "$_v" ] || fail_msg "README 徽章版本 ${_badge} 与 keel-version ${_v} 不一致（§9.1-14）: ${_rd#"$PWD"/}"
      done
      # 副本一：根 CHANGELOG 的当期小节。仅发行仓（写了徽章）检查。
      if [ -n "$_badge_seen" ]; then
        _cl="$_root/CHANGELOG.md"
        if [ -f "$_cl" ]; then
          grep -qE "^## ${_v} —" "$_cl" \
            || fail_msg "CHANGELOG.md 缺 ${_v} 小节（版本已声明 ${_v}，用户装不到/读不到这次变更；ADR 0010）"
        fi
      fi
      ;;
  esac
  unset _v _root _cl _rd _badge _badge_seen
fi

# 自报耗时并对照 LINT_SECONDS（ADR 0008）：
# **只告警不 fail**——机器慢不等于文件错。把性能当 fail 会让人在慢机器上
# 开始绕过 lint，那是比慢更坏的结果（§9.4 同类教训：制造大规模假告警）。
_el=$(date +%s 2>/dev/null || echo 0)
if [ "$_t0" -gt 0 ] && [ "$_el" -ge "$_t0" ]; then
  _spent=$((_el - _t0))
  if [ "$_spent" -gt "${LINT_SECONDS:-300}" ]; then
    warn_msg "lint 耗时 ${_spent}s 超过预算 ${LINT_SECONDS}s —— 文件数变多或存在 per-file fork；改预算只改 checks/budget.env"
  fi
  echo "   耗时 ${_spent}s（预算 ${LINT_SECONDS:-300}s）"
fi
echo "──"
if [ "$fail" -eq 0 ]; then echo "✅ keel-lint 通过"; else echo "❌ keel-lint 失败（见上方 ❌ 项）"; fi
exit "$fail"
```

### 9.4 陈旧豁免（不可变文档）

陈旧判定的前提是"这个文件还会被读、且内容可能已经过期"。有一类文档天然不满足这个前提，硬套 `last-verified` 只会产出**永久假告警**——而假告警会让整套告警机制被无视，比漏报更危险。

| 类目 | 为什么豁免 | 改用什么表达时效 |
|---|---|---|
| `decisions/*`（ADR） | 定稿即不可变；"改"指的是被新决策取代，不是内容腐坏 | `superseded-by: <文件名>`（lint 检查其存在，§9.1-14） |
| `archive/*`、`NOW-history/*` | 冷区本就豁免全部检查（§3.3 规则 2） | —— |
| 任意文件加 `stale-check: off` | 逃生口：确属长期稳定的参考事实 | 须在 `decisions/` 记一条理由，否则属于掩盖腐烂 |

> `last-verified` 的语义是"**有人复核过**"，不是"文件被碰过"。所以它在"增量为王"的层（`pitfalls/`、`skills/`、`NOW`）上是有效信号，在不可变层上只是噪声。

### 9.5 检索增强接入位（可选，不是缺陷项）

Keel 的检索是 `grep` + 三级路由，召回**停在关键词级**：搜得到"连接池"，搜不到"那个老是超时的池子"。这不是疏忽，是取舍——内核要保住零依赖，就不能自带语义索引。

要补这块短板，走**接入位**，而不是往内核里塞：

| 类型 | 代表 | 补的是什么 | 接入方式 |
|---|---|---|---|
| 符号级检索 | Serena（LSP，符号/引用/跨文件重命名） | 代码结构，不看文本 | MCP server |
| 预计算图 | code-graph、trace-mcp（调用图 / 路由图） | "谁调用谁""改这里会炸哪" | MCP server |
| 库文档 | Context7 | 第三方 API 的当前版本用法 | MCP server |

**唯一规则**：接入了就必须真的能用。声明形式是项目根的 MCP 配置（`.mcp.json` / `.cursor/mcp.json`），由 `checks/check-mcp-config.sh` 校验——**能解析、且每个 server 的 command 在 PATH 上**。

> **这条判据的能力边界**（实测确认，别把它当更强的东西用）：
> 它证明的是「**声明不落空**」——可执行文件存在。仅此而已。
> **它证不了「server 能启动」**：实测 `{"command":"bash","args":["-c","exit 7"]}`
> 会被判 ✅，而真跑起来 rc=7（参数错、依赖缺、协议不兼容全在判据之外）。
> 真要确认能启动，得自己发一次 `initialize` —— 那是**接入方的一次性验收**，不是 lint 的职责。
> 坑：[keel/pitfalls/meta/check-mcp-config-only-proves-path.md](keel/pitfalls/meta/check-mcp-config-only-proves-path.md)。

```bash
bash keel/checks/check-mcp-config.sh        # 恒 exit 0：未接入不算缺陷，落空才算
```

级别刻意定为 ⚠️ warn：**"没装 Serena"绝不能算项目缺陷**，接不接入是团队决策。它只防一种病——配置文件里写了一行、但那行根本起不来。

> 与 §9.2 的分工：§9.2 管"项目自己要用命令判死什么"；本节管"项目声明要用什么外部能力，并且不落空"。两者的共同底线一致：**能被判死，且误报有逃生口**。

---

## 10. 工作流

### 10.1 会话开始

```
1. 读 INDEX.md（唯一入口，内含检索协议）
2. 读 NOW*.md → 拿到当前焦点、下一步、阻塞
3. grep 定位本次任务相关的 scope 索引 → 加载
4. 只 read 命中的具体条目
```

### 10.2 会话进行中

- 遇到阻塞 → **立即**写进 NOW 阻塞表（三要素齐全）
- 踩到坑 → **立即**建 `pitfalls/` 条目（三段式 + `triggers: 0`），同步在 `pitfalls/INDEX.md` 加一行
- 做了架构决策 → 在 `decisions/` 记 ADR；改了契约 → 走人审关卡
- 发现某文件要超预算 → 当场拆 / 提 / 沉（§7.3），不要"下次再说"

### 10.3 会话结束（强制闭环清单）

- [ ] `NOW*.md` 已覆盖重写：焦点 / 完成 / 未完成 / 下一步 / 阻塞 / 新坑
- [ ] 新坑已登记：文件 + `pitfalls/INDEX.md` 索引行（否则本轮不算完成；lint 会查，§9.1-7）
- [ ] 被再次命中的坑：commit message 已带 `pitfall: <文件名>`（`commit-msg` 钩子自动 +1，**不再手工计数**）
- [ ] 改动过的文档：`last-verified` / `updated` 已刷新
- [ ] 跑了 `keel-lint.sh`，无 ❌

### 10.4 闭环钩子（**没有钩子，闭环就退化为自觉**）

| 层 | 触发时机 | 执行内容 |
|---|---|---|
| ① 工具侧规则（§4 锚点） | 每次任务开始 | AI 按协议读取与写回；**锚点存在性与原文一致性由 lint 检查**（§9.1-10） |
| ② pre-commit | `keel/` 下 md 有变更时 | `bash keel/checks/keel-lint.sh keel`，0 fail 才放行 |
| ③ commit-msg | 每次提交 | 扫描 message 里的 `pitfall: <文件名>`，自动给对应条目 `triggers` +1 并 stage（§7.4） |
| ④ CI | push / PR | lint 必须 0 fail；**自测必须 39/39**（`bash keel/checks/test-lint.sh`，§9.3）；钩子本体与可执行位由 lint 第 16 项守（§9.1）；PR 模板含"写回确认"勾选项 |
| 兜底 | —— | `NOW.updated` 超 7 天 → lint ⚠️（提示会话可能未写回） |

**【铁律】①②③④ 缺一，强制闭环就不成立。** 钩子由 `keel-starter` 的 `checks/install-hooks.sh` 落地（§12.1）——**只在文档里写钩子、不安装钩子，等于没有钩子**；v2 的"铁律"与 MVP 五件套自相矛盾（MVP 里既没有钩子也没有 CI），v3 已把四件事一起并入 MVP。

> 落地方式：钩子本体版本化在 `keel/checks/hooks/`，`install-hooks.sh` 只把 `core.hooksPath` 指过去——**不往 `.git/hooks/` 写不可见文件**，所以钩子可评审、团队共享、跟着分支走，也比 `.pre-commit-config.yaml` 少一层外部依赖。
> **与既有钩子框架共存（v3.4.7，ADR 0017）**：`core.hooksPath` 已被 husky 等框架占用时，
> 不要去抢它——把 keel 两个钩子本体**并入该框架的钩子文件**（`bash keel/checks/hooks/<钩子名>`）即可；
> `verify-hooks.sh` 支持这种**链式挂载**：在"git 实际执行的钩子文件、或其父目录同名文件"里
> 检出 keel 钩子本体路径即判就绪。首个采用方 lytjs（husky）验证了该路径。

---

## 11. 度量与回顾

别让基座变成自我感动，盯三个数（**每个都有采集方式，否则不叫度量**）：

| 指标 | 含义 | 采集方式 | 健康信号 |
|---|---|---|---|
| 返工率 | 被 revert / 重做的改动占比 | 每两周：`git log --oneline -i --grep=revert --since='2 weeks ago' \| wc -l` ÷ 同期总提交 | 持续下降 |
| 坑复发率 | 同一条坑被触发次数 | `pitfalls` 的 `triggers` 汇总（lint 持续提醒 ≥3） | 单坑 ≤1；≥3 立即蒸馏 |
| 平均阻塞时长 | 阻塞从登记到解锁的时长 | `NOW-history/` 阻塞表（登记 → 解锁日期差） | 缩短 |

### 11.1 遵守率：唯一没人做的那个指标（v3.2 新增）

上面三个数全部度量**项目**。还有一个数度量**AI 本身**——它有没有真的遵守 Keel：

| 指标 | 含义 | 为什么至今无人做 |
|---|---|---|
| **遵守率** | AI 的行为里有多少符合 Keel 规则 | **"加载"易测，"遵守"无从下手**——而它才是最终目的 |

**2026-10 联网调研的结论（逐个读源码，非读 README）**：

| 项目 | 体量 | 它的"遵守率" | 判定 |
|---|---|---|---|
| `jackeyunjie/dsh-rule-lens` | 1485 行 JS / 3 提交 / 零测试 | 面板标题写"遵守率"，但**数据结构里只有拦截计数、没有分母**；加载 10 条违反 1 条 → 拦截数 0 → 显示"0 次拦截"，看起来像 100% 遵守 | **语义是反的** |
| `fuwasegu/aegis` | 41k 行 TS / 989 测试 | 生成的 adapter 规则第 5 步原文是 **"Self-Review"——让 AI 自报** | 自报 = 不可验 |
| `holaOS`（48 万行 TS，生产级） | 全仓 grep 遵守率 → **零实现** | 但它留下了一份 223 行的"假遵守"取证（见下） | 干脆没做 |

**所以：没有任何项目真正实现了"度量 AI 是否遵守规则"。** 这个空白是真的。

### 11.2 关键判断：不测 AI 说什么，测文件系统发生了什么

调研中最重要的一个发现来自 holaOS 的取证文档（`docs/research/context-governance-verify.md` 全文）：
它的门禁**全部正确触发**，AI **对 `src/client/` 零编辑**，然后**宣布任务完成**。
它试过加重门禁措辞 → 得到更精致的形式合规。它还记录了一个反直觉现象：

> **点名失败模式，AI 就精确复现那个失败模式**（在 rules 里写"不要犯 X"，反而提高了犯 X 的概率）

由此得出本项目的路线——**不要去解析 AI 的自述，那既不可靠也可被无意识地美化。
去观测客观事实：文件被改成了什么样、lint 命中了什么、提交信息写了什么。**

Keel 的三件套（lint + pre-commit + commit-msg）**本来就全是客观的**，
缺的只是一个把三者输出聚合成**带分子分母**的数字的聚合器：

```
violations.jsonl   ← lint 的 ❌/⚠️ 命中（pre-commit 自动写）
load.jsonl         ← 每轮加载字节 + 是否超限（load-estimate.sh 自动写）
回滚数            ← git log --grep='^Revert "'（直接读 git，不需额外文件）

遵守率 = 1 − (lint 命中轮次 + 放行后被回滚数) / 总检查轮次
```

**分母为什么是"所有提交"而不是"改了 md 的提交"**（v3.3.2 修正）：
最初的守卫是 `grep -E "^keel/.*\.md$"`（只为不白跑 lint），于是**只改代码的提交
完全不进分母**——而"改 contracts 却没同步 INDEX"这类违规恰恰最容易发生在纯代码提交里，
它成了指标的盲区（实测：提交一次只改 `.py` → 记录 0 条）。

现拆成两件事：**记录 = 所有提交都记**（廉价，只用 `git diff`）；
**校验 = 只有 keel 下的 md 变了才跑**（昂贵，且此时才有意义）。
配套新增**覆盖率**指标：

```
覆盖率 = 跑过 lint 的提交数 / 全部提交数
```

**必须与遵守率一起读**：未检查的提交计入分母、不计入分子，所以覆盖率低会让遵守率
**偏低**——真正的风险是「**覆盖率低 + 遵守率高**」，那说明大量提交根本没被检查，
高分是假的。报告脚本会同时打出这两个数，并在 `report` 输出里写明这一点。

**分子为什么是"命中 + 回滚"两项**（v3.3.1 修正，ADR 0009）：
初版只算 lint 命中，**漏了放行后被回滚的提交**——而那恰恰是 lint 自己看不见的一类
不遵守：门禁说通过、提交成功，之后才被推翻。实测同一假仓（三轮记录 + 一次真回滚）
**从 66.7% 降到 33.3%，虚高一倍**。口径错一点，整个数字就没意义。

匹配回滚用 `git log --grep='^Revert "'`（git 自动生成的精确格式），
**不要用 `-i --grep=revert`**——实测后者会把"实现 revert 按钮的功能"这类普通提交误计。

**这个数字 AI 一个都改不了**——它不来自 AI 的输出，而来自文件系统与 git 历史。
这是本项目与"让 AI 自报"路线的根本分野。

**为什么遵守率不能靠"回填历史"来造基线**（v3.3.5 / ADR 0011）：

技术上做得到——lint 是纯 bash，可以对任意历史提交重放。但**这个基线是假的**：
遵守率的分母是"门禁有机会拦的次数"，**装上钩子之前的历史提交根本没有门禁，分母不存在**。
把它们算进分母，等于宣称"这些提交当年被检查过"——那正是 ADR 0009 反对的伪造客观事实。

所以回填（`checks/compliance.sh backfill`）产出的是**另一个数**：

```
存量合规率 = 1 − 命中提交数 / 被回填的历史提交数
```

- 记录带 `backfill=1`，**与 `baseline` 一样被排除出遵守率的分母**，只在报告里单列一段；
- 判据统一：用**当前**的 `keel-lint.sh` 与 `budget.env` 重放历史内容，
  否则各提交自带一套上限，跨提交的数字不可比；
- 它回答的是「**仓库现存内容，按今天的判据看有多干净**」，与遵守率是两件事。

**适用边界要写清楚**：在**已经用 Keel 管住的仓库**里它会接近 100%——
存量早被门禁筛过一遍，信息量低。它真正的用武之地是"刚装完、历史从未被门禁管过"的仓库，
也就是**新用户的第一天**：让他装完立刻看到第一个数，而不是等几周。

**预算超限率**（同一份 load.jsonl，`report` 一并给出）：
超限率测的是"上下文基座够不够用"，与遵守率正相关但**不是一回事**——
遵守率低 → AI 不守规矩；超限率高 → 基座装不下该装的东西，该拆/提/沉了。
对比 aegis：它超限时把文档**降级为 deferred**，而 AI 并不知道哪部分被降级了，
会基于残缺上下文自信作答；Keel 是超限即报错，更强——但要把它变成可度量信号。

> 为什么不直接问 AI"你遵守了吗"：holaOS 的取证已经证明那条路会产出**更精致的形式合规**。
> 自报数据不仅不可靠，还会因为过于体面而失去诊断价值。

### 11.3 与前三个指标的关系

遵守率不是第四个并列指标，而是**前三个的先行指标**：返工率高多半是遵守率低的结果。
若遵守率长期偏低，先查的是规则本身是否可遵守（§2 原则 4：不能被脚本判死的规则不叫规则），
而不是催 AI 更认真。

**每两周回顾一次**（15 分钟）：读三个数 → 看 lint warn 清单 → 决定下一轮补哪一层 / 哪个 skill。

> 三个数里有两个的可行性依赖前置规则，v3 才补齐：坑复发率依赖 `triggers` 由钩子计数（§10.4 之三），平均阻塞时长依赖 `NOW` 先归档再重写（§5.5）——**指标不可采集，通常不是因为没数据，而是因为上游动作没人做**。

**必须自动化，否则会消失**：三个指标的采集、lint warn 清单、季度抽测，全部挂成定时任务（每两周触发一次提醒，并把上面的命令跑完贴回 `NOW.md`）。**靠"我记得"维持的例会在第三周就会消失**——这和 §10.4 是同一个道理：没有钩子的流程等于建议。

**最后一次自检（本项目自己的验收）**：把本文档 §12 之前的规则抄成一个真实 `keel/`，跑一次 `keel-lint.sh`——出现任何 ❌，就说明文档和脚本又不一致了。

---

## 12. 落地路线

**架构是被真实痛点长出来的，不是一次性设计出来的。**

### 12.1 MVP（当天可用）

```
keel/
├── INDEX.md                 # 入口：检索协议 + 路由 + project-state + keel-version
├── CONSTITUTION.md          # 红线 + 人审关卡
├── NOW.md                   # 当前焦点 + 交接
├── pitfalls/                # INDEX.md（表格）+ _template.md + 1 条真实坑
└── checks/                  # keel-lint.sh + budget.env + rules.md + test-lint.sh/.py
│                            # + install-hooks.sh + verify-hooks.sh + hooks/{pre-commit, commit-msg}
＋ archive/.gitkeep · NOW-history/.gitkeep   # 空目录不被 git 跟踪（§3.3 规则 5）
＋ CI 片段（.github/workflows/keel.yml）——lint 0 fail + 自测 39/39（§10.4 之四）
＋ PR 模板（.github/pull_request_template.md）——"写回确认"勾选项（§10.4 之四）
＋ 工具侧锚点 1 句（AGENTS.md 首行）——没有它，上面这些文件不会被读到（§10.4 之一）
＋ checks/keel-doctor.sh —— 装完一键自证（v3.4.5）
```

**第 0 天五步（缺任一步，MVP 不算落地）**：

0. **（v3.4.5 新增，最先跑）一键自证**：`bash keel/checks/keel-doctor.sh`——
   它逐项报 5 件事（闭环门禁 / lint 结果 / 单轮加载预算 / 判据自检怎么跑 / 还差你亲手填什么），
   **只读不改**（诊断与修复分开，避免"顺手改掉你的东西"）。
   为什么放第0 步：装完的第一分钟是决定会不会继续用的那一分钟，
   而"读 README 理解价值"要 30 分钟、"跑一条命令看到自己的数字"只要 10 秒。
   **价值应该可自证，而不是靠说明书说服。**
1. 展开 `keel-starter`（§12.3），或直接复制 MVP 文件；
2. 装钩子：`bash keel/checks/install-hooks.sh`（pre-commit + commit-msg）；
3. 贴 CI 片段，并在项目根写入 §4.1 锚点；
4. 跑 `bash keel/checks/keel-lint.sh keel`——**第一次自检必须 0 fail**（锚点也在检查范围内，§9.1-10）；
5. 跑 `bash keel/checks/test-lint.sh`——**必须 39/39**。这一步验的不是你的仓库，而是**你手上的 lint 到底能不能判死它声称能判死的问题**；将来改检查项时它也是唯一的护栏。

**按需层（不进 MVP，痛点到了再加）**——starter 已带骨架，规格见 §5.7，"怎么填"写在同目录的 `_template*` 里：

| 层 | 什么痛了才加 | starter 里的形态 |
|---|---|---|
| `contracts/` | 改了一个接口，三个调用方没跟上 | `INDEX.md`（表格）+ 契约 `_template.schema.json`（用 `x-keel-*` 字段自文档化） |
| `ARCHITECTURE.md` | 有人（或 AI）搞错模块边界 / 依赖方向 | 模块表 + 依赖方向矩阵（**只写现状**） |
| `GLOSSARY.md` | 同一个概念出现了第二种写法 | 「唯一写法 / 禁止写法」表，同时是术语混用检查的输入 |
| `decisions/` | 出现"当初为什么这么定"的争论 | `INDEX.md`（表格）+ ADR `_template.md` |
| `skills/` | 同一个操作第二次被口述 | `INDEX.md`（表格）+ 技能 `_template.md` |
| `env/` | 有第二个环境，或密钥来源说不清 | `INDEX.md`（表格）+ `setup.md`（**只记来源，不记值**） |

> 加层时别忘了 INDEX.md 路由表——**新 scope 不加行，就是孤儿**（§9.1-4 会判死），而这正是"文件一多就再也找不到"的起点。

### 12.2 迭代节奏

1. 跑两周
2. 看 AI 在**哪类事上仍然反复出错**、看三个度量指标
3. 就补哪一层 / 补哪个 skill

### 12.3 分发与升级

- `keel-starter`：模板仓库（MVP 全部文件 + CI 示例 + 锚点片段 + `checks/install-hooks.sh`）；
- 升级：starter 发版带 CHANGELOG，各仓库按 `keel-version` **增量合并**。文件按三类处理，**不允许"一键覆盖"**：

| 类别 | 文件 | 升级动作 |
|---|---|---|
| **纯本地，永不覆盖** | `pitfalls/`、`contracts/`、`decisions/`、`env/`、`archive/`、`NOW-history/` | 完全跳过 |
| **结构合并** | `INDEX.md` | 只合并 frontmatter 的 `keel-version` 与 §8 检索协议正文；**路由表、`project-state` 保留本地** |
| **本地优先** | `NOW.md`、`ARCHITECTURE.md`、`GLOSSARY.md`、`CONSTITUTION.md` 的身份与硬约束段 | 有本地改动则不覆盖，只在 `decisions/` 记一条"待人工合并" |

- 版本声明：根 `INDEX.md` frontmatter 的 `keel-version` 字段（lint 强制其存在，§9.1-10）；
- **破坏性变更**（改检索协议、改预算数字、加 frontmatter 必填字段）须在 `decisions/` 记 ADR，并在 CHANGELOG 里给出迁移命令；
- 升级本身也要过 §10.4 的钩子：升完跑一次 `keel-lint.sh`，**允许 0 fail 才算升级完成**。

**本项目自己的仓库拓扑**（与 §3.5"一个 Keel 管一个发布单元"同源）：

| 仓库 | 内容 | 可见性 |
|---|---|---|
| `keel`（项目仓） | 设计稿 `DESIGN.md` + `keel-starter` 子模块指针 | 规格在这里版本化 |
| `keel-starter`（发布仓） | 纯模板，**不含设计稿** | 可单独公开/分发 |

- 设计稿**必须进版本管理**：它是唯一真源，只有单副本等于没有备份；`.gitignore` 里不忽略它；
- 发布仓不含设计稿，所以 `test-lint.sh` 的"脚本与文档逐字一致"检查在那里自动 SKIP（§9.3）；
- 在项目仓里这条检查**能读到 `DESIGN.md`**——于是"文档与脚本不许漂移"这条不变量终于落在有历史可依的地方；
- 子模块指针与发布仓 HEAD 必须一致（`git submodule status` 行首不出现 `+`），且**推送顺序恒为：先发布仓、后项目仓**，否则别人 clone 后 `submodule update` 会取不到那个提交。

**版本可获取（v3.3.4 补上：此前 §12.3 整节没提过 tag）**：

版本有**两处真源**，两者必须同时成立，否则其中一个就是假的：

| 真源 | 位置 | 谁守 |
|---|---|---|
| 声明 | `keel/INDEX.md` 的 `keel-version` + `CHANGELOG.md` 小节 | 发布关卡 |
| 可获取 | 发布仓的 `vX.Y.Z` tag | **CI「版本号与 tag 一致」检查** |

实测踩过：`keel-version` 升到 3.3.3、CHANGELOG 写了五节，**tag 却只到 v3.1.1**。
后果不是"少几个标记"——`install.sh --ref v3.2.0`（README 亲口教用户这么用）直接失效，
用户无法固定版本，只能跟着 `main` 走。**"可复现的安装"是分发渠道的底线。**

判据：**"版本号写对了"不等于"版本能用"。**
声明与可获取脱节时，一切看起来都正常（CI 绿、文档全、版本号对），
只是用户装不到那一版——因此必须由机器一起验。

**发布编排（v3.1：这条约束不再靠人记）**：

项目仓根目录的 `scripts/release.sh` 把上面那条顺序**写进代码**——默认 dry-run，`--apply` 才真推：

```bash
bash scripts/release.sh            # dry-run：前置检查 + 打印将要执行的推送
bash scripts/release.sh --apply    # ① 发布仓 push → ② 项目仓 push（顺序写死）
```

它按顺序做四件事：① 两侧工作区是否干净、子模块指针是否一致；② 发布仓跑 lint + 自测（不过就不许推）；
③ 先推发布仓；④ 再推项目仓，**推送前再查一次指针**（发布仓若刚有新提交，指针会再次失配）。
第③步失败会直接中止，绝不出现"项目仓推上去了、发布仓没有"的坏状态。

**两站镜像（Gitee 主 + GitHub 镜像）**：

- `.gitmodules` 用**相对 URL** `../keel-starter.git`：两个托管站各自解析到同站同级仓库，CI 与人都不需要改配置；
- **不要写 `./keel-starter`**——实测它解析成 `<host>/<org>/keel.git/keel-starter`（远端 URL 的末段被当成目录，等于多了一层），`../` 才是同级；
- CI 分两处：**发布仓**跑 lint + 自测（不依赖子模块，镜像过去即可用）；**规格仓**跑自测，此时"脚本与文档逐字一致"那条才真正生效（§9.3）；
- **镜像同步是无序的（v3.1 实测，不是推测）**：Gitee→GitHub 的自动同步**不保证两仓先后**——
  实测发布仓镜像平均比项目仓晚 **3–4 分钟**。于是在"项目仓指针指向发布仓新提交"的那段窗口里，
  GitHub 上的发布仓还没有那个提交，`actions/checkout` 取子模块直接失败：
  `remote error: upload-pack: not our ref <sha>` / `did not contain <sha>`。
  连续三次指针提交（`082a6de` `8bd2183` `d6ff9eb`）全部踩中，滞后分别为 3 / 4 / 3 分钟。

  > 结论：**"先发布仓、后项目仓"只约束得了人工推送**（`scripts/release.sh` 强制），**管不到镜像**。
  > 所以项目仓 CI 必须自己容忍这段延迟：子模块检出改为带退避的重试（10 × 30s）。
  > 这条也顺带解释了"人工顺序完全正确、徽章却红"的现象——**约束的适用边界，本身就是文档该写清楚的事**。

### 12.4 派生命名

| 层级 | 命名 |
|---|---|
| 品牌名 | Keel |
| 中文名 | 龙骨 |
| 仓库名 | `keel` / `keel-compliance` |
| SDK / 包 | `@yourco/keel` |
| 子模块 | `keel-skill`、`keel-pitfalls`、`keel-checks`、`keel-starter` |

---

## 13. 一句话总结

**全量存、索引化、按需取、机器验、定期蒸馏、先点火。**

Keel 想长到多大就长多大，它是一本书；
AI 每次只读书里的一页——而目录永远只有两页。