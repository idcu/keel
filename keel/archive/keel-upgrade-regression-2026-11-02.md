# keel upgrade 真跑回归（lytjs v3.4.11 → v3.6.0）

> 目的：验证「一条命令升级」能否替代 2026-11-02 那次**手工逐文件同步**。
> 全程在 `/tmp/lytjs-keel-regress/` 临时副本中进行；未触碰 lytjs 主工作树
> （HEAD `986b7b14`，含作者未推送的 `37f1cf15`、`17ba44da`）。

## 方法

1. `git archive 522eddfa keel AGENTS.md README.md scripts` 取出**升级前快照**
   （keel v3.4.11，含作者自定义的 rules / CONSTITUTION / decisions / pitfalls）；
2. 让新的 `install.sh` 对它执行就地升级（模拟真实用户：≤3.5.0 的仓库没有
   upgrade 脚本，重跑 install 就是引导路径）；
3. 另用模板自带的 `keel-upgrade.sh --target <fixture> --from <模板>` 单独计时；
4. 与 `dab27d73`（上轮手工同步到 v3.5.0 的提交）比对文件集与内容哈希。

## 结果

| 项 | 结果 |
|---|---|
| 版本 | 3.4.11 → 3.6.0，exit 0 |
| 分类动作 | 内核覆盖 21 · 新增 1 · 保留 46 |
| 内核文件与 v3.6.0 模板 | **21/21 逐字节一致**（sha256 全等） |
| 采用方自定义 | 46 个 preserve/merge 文件哈希**全部未变**（INDEX 仅 `keel-version` 行变化） |
| 新增文件 | `checks/keel-upgrade.sh`、`checks/test-upgrade.sh/py`、`checks/manifest.tsv`、`checks/retrieval/keel-search.py`、`archive/safe-delete-full.md` |
| 幂等 | 再跑一次：`✅ 已是 v3.6.0，无需升级`，exit 0，未新增备份 |

### 与上轮手工同步（`dab27d73`）对比

| 差异 | 文件 | 说明 |
|---|---|---|
| 内容不同 | `checks/install.sh` | 预期：v3.6.0 改为委派升级引擎 |
| 工具升级多出 | `keel-upgrade.sh`、`test-upgrade.sh/py`、`manifest.tsv` | v3.6.0 新增能力 |
| 手工有而工具缺 | 无 | —— |
| 其余内核文件 | 全部字节一致 | lint / test-lint / 钩子 / BM25 检索 / MCP |

**结论：工具升级 = 手工同步结果 + v3.6.0 新增件 − 无需人工重写 install.sh。**

## 门禁前后对比（fixture 内实跑）

| 门禁 | 升级前（v3.4.11 自带工具） | 升级后（v3.6.0 工具） |
|---|---|---|
| keel-lint | 0 fail（1.40s） | 0 fail（1.4s） |
| test-lint | 43/43（9.27s） | 43/43 |
| 预算固定成本 | 4862B ≤ 15000B | 4861B ≤ 15000B（INDEX 版本名短 1 字节） |

## 耗时

| 路径 | 耗时 |
|---|---|
| 全流程（新 install.sh 引导：clone + 升级 + 装钩子 + 复核） | **22.96s** |
| 仅升级引擎（含前后两轮门禁） | **20.54s** |

耗时构成：两次 test-lint 约 18s 是主体；分类 / 校验 / 复制 / 备份本身约 1–2s。
`--skip-test-lint` 可把非发布场景的耗时压到秒级（代价是不做升级后验证）。

## 人工介入

- **无**。exit 0、前后门禁全绿、自定义文件全部保留。
- 唯一限制：≤3.5.0 的仓库**没有升级引擎**，必须先拿到新版 `install.sh`
  （curl 或手工下载）；这正是「install 负责新建/引导、upgrade 负责升级」的分工。
- 备份在 `<项目根>/.keel-backup/`（本次 1 份，约 1.2MB），回滚一条命令：
  `bash keel/checks/keel-upgrade.sh --rollback`。
