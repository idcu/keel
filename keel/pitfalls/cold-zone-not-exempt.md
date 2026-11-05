---
scope: meta
status: active
severity: P0
last-verified: 2026-11-06
triggers: 1
keywords: [冷区, archive, 目录计数, CHANGELOG, 静默跳过]
---

## 症状

两处该红却绿：冷区 `archive/` 堆 28 个文件，lint 报「目录文件超限」，
但 §3.3 规定冷区只查死链；README 已写版本徽章（= 发行仓）却缺根
`CHANGELOG.md` 副本，lint 不报错直接通过。

## 根因

目录计数时 `find` 扫全量、`dirs` 只列热区，文件没跟着过滤；§9.1-17
的第三副本写成 `[ -f "$_cl" ] && grep ...`，文件不存在时整条检查被
静默跳过——与「检查通过」不可区分。

## 正解

- `find` 输出处就排掉 `/archive/`、`/NOW-history/`，再聚合计数。
- 缺副本必须 `fail_msg`；「文件缺失」与「小节缺失」是两个独立失败条件。
- 负控：用例 51（冷区 21 文件 rc=0）、用例 52（有徽章无副本必须报错）。
