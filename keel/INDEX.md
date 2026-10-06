---
scope: meta
status: active
last-verified: 2026-10-06
keywords: [索引, 入口, 路由, 规格, 两仓]
keel-version: 3.4.10
project-state: building     # exploring | architecture-locked | building | frozen
---

# keel · INDEX

> **唯一必读入口。** 检索协议、路由表、项目状态三样的唯一真源就在这里。
> 规格见《Keel 设计稿》§5.1；协议正文必须与 §8 逐字一致，不得改写、不得精简。
>
> **本文件属于 Keel 项目自己**（`keel` 规格仓的上下文基座）。
> 模板在 `keel-starter/keel/`，两者结构相同、内容各自独立演进——见
> [ARCHITECTURE.md](ARCHITECTURE.md) 的「`keel/` 目录的两个身份」。

## 检索协议（必须遵守）

1. 必读：INDEX.md（唯一入口）+ 当前 NOW*.md —— 固定预算 ≤2.3k token（最坏）
2. 定位：先 grep -rl "关键词" keel/ --exclude-dir=archive --exclude-dir=NOW-history（只出文件名，冷区不参与检索）；命中过多先收窄关键词
3. 读取：只 read 命中的那一个文件；不够就回到第 2 步换关键词，不得扩大范围
4. 预算：单次检索输出 ≤100 行；本轮 Keel 加载总量 ≤15,000 字节（≈5k token）
5. 写回：完成任务必须写回 NOW*.md（新坑登记进 pitfalls/INDEX.md 且 triggers 维护），否则本轮不算完成

## 路由（scope → 入口）

<!-- 规则 1：新增 scope 必须在此加一行。"定位 scope"不允许靠猜。 -->

| scope | 一句话 | 入口 |
|---|---|---|
| meta | 宪法：身份 / 硬约束 / 人审关卡 / 状态机 | [CONSTITUTION.md](CONSTITUTION.md) |
| meta | 代码地图：两仓拓扑 / 模块边界 / 依赖方向 | [ARCHITECTURE.md](ARCHITECTURE.md) |
| spec | **规格唯一真源**（设计稿，§ 编号引用都指向它） | [../DESIGN.md](../DESIGN.md) |
| meta | 对外分发的模板（纯骨架，不含设计稿） | [../keel-starter/keel/INDEX.md](../keel-starter/keel/INDEX.md) |
| meta | 两仓发布编排（推送顺序写死在脚本里） | [../scripts/release.sh](../scripts/release.sh) |
| api | 契约真源：API / 类型 / 事件 | [contracts/INDEX.md](contracts/INDEX.md) |
| meta | 术语表：唯一写法与禁止写法 | [GLOSSARY.md](GLOSSARY.md) |
| meta | 决策记录（ADR） | [decisions/INDEX.md](decisions/INDEX.md) |
| meta | 可复用操作手册 | [skills/INDEX.md](skills/INDEX.md) |
| meta | 校验规则与项目扩展检查位 | [rules.md](checks/rules.md) |
| now | 当前焦点、下一步与阻塞 | [NOW.md](NOW.md) |
| db | 数据库 / 连接 / 迁移 | [pitfalls/INDEX.md](pitfalls/INDEX.md) |

## 冷区指针（只此一行）

[archive/](archive/) · [NOW-history/](NOW-history/)
