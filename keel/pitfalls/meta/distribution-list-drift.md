---
scope: meta
status: active
severity: P1
last-verified: 2026-11-02
triggers: 0
keywords: [分发, 升级, manifest, 权限, 引擎缺失, 静默]
---

## 症状

- v3.4.11 升 v3.5.0 后 `test-lint.py` 不存在、locale 修复没进来，而 lint/CI 全绿
- ≤3.5.0 的采用方照 QUICKSTART 抄 `keel-upgrade.sh` → `No such file`（exit 127）
- `--regen-manifest` 沿用旧清单里的权限（从不读磁盘）→ 首次 `--check-manifest` 逐条报
  「期望 644 / 实际 755」；旧实现还先落盘再判死，校验失败时清单已被写坏

## 根因

"要同步哪些文件"靠手写清单，与模板各自演化；清单一旦生成就被当权威——
权限不回流、写入顺序不校验。引擎只在 v3.6.0+ 存在，旧仓库没有任何提示。

## 正解

- 清单是机器真源（`manifest.tsv`）；`--regen-manifest` 的权限**以磁盘为准**、
  先判后写；`--check-manifest` 前移到 CI 与发布脚本，必过
- 覆盖类按版本覆盖，不"存在即保留"；判据：清单能从模板单向重建
- 旧版本采用方：先 `ls keel/checks/keel-upgrade.sh`，没有就重跑
  `install.sh --ref v3.7.0`（QUICKSTART §4 已前置）
