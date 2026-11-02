---
scope: meta
status: active
last-verified: 2026-11-02
keywords: [升级, 分发, manifest, 回滚, 幂等]
type: decision
created: 2026-11-02
superseded-by:
---

# 0020 就地升级：manifest 驱动的 `keel-upgrade.sh`

## 背景

v3.4.11 的采用方（lytjs）升 v3.5.0 时，`install.sh` 的"已有 keel/"分支只按
**手写白名单**逐个补工具链，并且对已存在的文件一律「保留不覆盖」。结果是：

- 白名单漏了 `test-lint.py`，该文件永远装不进去；
- 漏装的 locale 修复（`LC_ALL` 泄漏）**没有任何检查会报**；
- 最后只能逐文件手工 `cp` 并肉眼比对哈希。

分发渠道的失效是静默的：lint 绿、CI 绿、文档全，只有升级这件事本身错了。

## 决定

新增 `checks/keel-upgrade.sh`，并用模板内的 `checks/manifest.tsv` 作为**唯一分类真源**：

| 分类 | 含义 | 动作 |
|---|---|---|
| `kernel` | 内核工具链（lint / 自测 / 钩子 / install / retrieval…） | 按版本覆盖，带 sha256 校验 |
| `merge` | `INDEX.md` | 只改 `keel-version` 行；路由表与协议正文不覆盖 |
| `preserve` | 采用方自定义（rules / CONSTITUTION / decisions / pitfalls / NOW…） | 一律不动 |
| `additive` | 新增结构文件 | 缺失且**父目录已存在**时补 |

脚本**不含任何文件名字面量**：加文件只需改 manifest（发布方跑
`--regen-manifest` 重算校验和）。`install.sh` 的已有分支改为**委派**给本引擎，
两份 install.sh 仍由 CI 逐字比对。

- **install 用于新建**（全量复制），**upgrade 用于升级**（分类增量合并）；
- 引导路径：≤3.5.0 的仓库没有本脚本，**重跑 install.sh 就是它的升级入口**
  （新模板自带引擎），解决"升级工具本身还没装"的先有鸡问题；
- **幂等**：`keel-version` 已等于目标时直接 `exit 0` 并明说"无需升级"；
  `--force` 才重放一次；
- **门禁对比**：升级前后各跑 lint + test-lint + 预算固定成本，任一失败即
  `rm -rf` 还原并 `exit 3`，文件、manifest 一起回到升级前。

## 被否掉的选项

| 选项 | 为什么没选 |
|---|---|
| 继续手写白名单 | 漏一个文件的代价是静默的（本轮实测踩中）；清单散落脚本里无法 diff、无法校验 |
| 用 JSON manifest | 内核必须零外部依赖；TSV 纯 bash/awk 可读、diff 友好 |
| 用 git 工作区还原来回滚 | 采用方常有未提交自定义，`git checkout` 会连自己一起吞掉 |
| 按目标版本号在线拉文件 | 无法在离线/内网运行；`--from <模板目录>` 保留离线路径 |

## 备份策略

整目录 `cp -R keel/` 到 `<项目根>/.keel-backup/<from>-to-<to>-<ts>/`，保留最近 3 份，
并生成可执行的 `restore.sh`。**不用 git 还原**：备份在有无 VCS、工作区是否脏的
情况下都成立，且回滚是"把目录换回去"，不需要理解提交历史。

## 失效场景（已知限制）

1. **升级引擎自身有缺陷**：旧版没有新引擎，只能重跑 install.sh；
   install.sh 报"该模板没有 keel-upgrade.sh"时按提示手工同步一次。
2. **无旧 manifest 的仓库无法检测本地改过内核文件**：v3.4.11 及更早没有 manifest，
   首次升级一律覆盖内核；被改过的原文件仍留在备份里。
3. **`additive` 不复活被裁剪的层**（keel-lite 删掉的目录不会被补回）——这是特性不是缺陷。
4. **不处理降级**：目标版本低于当前直接拒绝，回滚走 `--rollback`。
5. **`merge` 只认 `keel-version` 行**；检索协议正文不一致时只告警，留给人工（§12.3）。

## 后果

- 好处：升级从"逐文件手工同步 + 肉眼比对"变成一条命令；失败自动回滚；
  重复执行不产生额外改动；自测覆盖正常/跨版本/保留/回滚/幂等五类场景。
- 代价：manifest 需要与模板同步维护（`--regen-manifest` + 自测第 9 条双向兜底）；
  备份目录会占用磁盘（限制 3 份）；首次升级（旧版无 manifest）检测不到本地改动。
