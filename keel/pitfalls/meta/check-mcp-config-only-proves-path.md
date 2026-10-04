---
scope: meta
status: active
severity: P3
last-verified: 2026-10-04
keywords: [check-mcp-config, PATH, 接入位]
triggers: 1
---

## 症状
`check-mcp-config.sh` 对 `command=bash, args=["-c","exit 7"]` 报 **✅ 全部可达**，
实际 **rc=7**——它根本起不来。

## 根因
判据是「**command 在 PATH 上**」（§9.5 / ADR 0007 写死）。它只证明**可执行文件存在**，
证不了**server 能不能跑**——参数错、依赖缺、协议不兼容全在判据外。

**不是实现 bug，是规格的能力上限**：MCP server 多是 stdio 子进程，真要验"能起来"得**真的
拉起来发 initialize**，超出 lint 范围（要超时保护、防挂）。

## 正解
**保持现状**（它防"声明落空"不防"不能启动"），边界写进 §9.5：
**"在 PATH"= 不落空；"能启动"要自己跑一次 initialize**。

## 为什么值得登记
宪法第 4 条的形状：**判据只覆盖它声称覆盖的一半，文案听起来覆盖全部。**
判别法：看到检查报 ✅ 时**问一句"它没覆盖什么"**——"没装 Serena 不算缺陷"是刻意设计
（ADR 0007），但"装了能启动"同样不在范围内，两者不能混谈。
