---
scope: meta
status: active
last-verified: 2026-10-04
keywords: [校验, 规则, 扩展检查, CI]
---

# 扩展检查（项目自定）

> Keel 内核只做**通用**检查（`keel-lint.sh`，见《Keel 设计稿》§9.1 / §9.3）。
> 契约漂移、术语混用这类检查依赖具体技术栈，内核**不假装能通用实现**——
> 在本文件里声明项目自己的命令，由 CI 串联执行，级别（fail / warn）由项目自定。
> 规格见《Keel 设计稿》§9.2。
>
> **内核自带脚本清单**（install-hooks / verify-hooks / load-estimate / compliance 等）
> 已按 §7.3「沉」移入冷区：[../archive/script-inventory.md](../archive/script-inventory.md)——
> 那是"查得到就行"的信息，不该占单轮加载预算。

## 声明格式

每条规则必须写得出**一个可执行命令**。写不出命令的，不是检查项，是愿望——
按 §2 原则 4，它不该出现在这里。

| # | 检查 | 命令 | 级别 | 触发时机 |
|---|---|---|---|---|
| 1 | <检查什么> | `<可直接粘贴执行的命令>` | ❌ fail / ⚠️ warn | pre-commit / CI |

<!-- 不打算启用的规则整行删掉——留着一条跑不通的命令，比没有更糟。 -->
