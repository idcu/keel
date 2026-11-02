# keel upgrade 首次外部采用方实测（lytjs 3.5.0 → v3.7.0）

> 目的：以**真实采用方**的视角跑第一次 `upgrade`，记录所有介入点，回答
> 「不知道内部实现的人，只靠 QUICKSTART 能不能升级」。
> 全部数字为本机 2026-11-02 实测；环境 macOS / bash 3.2.57 / zh_CN.UTF-8。

## 0. 前置：为什么不直接在主仓跑

`/Volumes/Data/lytjs` 的 `v7.0.0-dev` 比 `origin/v7.0.0-dev` 多 4 个提交
（`37f1cf15`、`17ba44da`、`986b7b14`、`e3c355f7`，均未推送），工作区另有 3 处
作者自己的未提交改动（`scripts/check-integration.mjs`、`scripts/gate.mjs`、
`?? scripts/check-render-cost.mjs`）。

→ 按「未推送即在临时副本上跑，不覆盖作者工作」：`git clone -q --no-hardlinks`
（跨设备，硬链接失败）取 `origin/v7.0.0-dev`，副本 `/tmp/lytjs-ext`；
主仓只读、未被触碰；跑完即 `rm -rf`。

副本接入形态与主仓一致：vendored `keel/`（非 submodule），版本 **3.5.0**。

## 1. 第一次尝试：直接跑 upgrade（失败）

照直觉执行 QUICKSTART 里那条命令：

```bash
bash keel/checks/keel-upgrade.sh --target . --to v3.7.0
```

```
bash: keel/checks/keel-upgrade.sh: No such file or directory
exit 127
```

**这是本次唯一一次被拦住的地方，也是最重要的采用方介入点。**

判定是否合理：合理——文件确实不存在，不是误报。但站在采用方角度，这条报错
**只说了"没有这个文件"，没说"你该做什么"**：用户看到的是自己的命令打错了吗？
版本太低吗？要手工拷脚本吗？这三种解释在 3.5.0 的仓库里无法自证。

根因：升级引擎是 v3.6.0 才引入的；≤3.5.0 的仓库没有任何 `upgrade` 能力，
`--ref v3.5.0` 的 QUICKSTART 里也没有这一段（那时还不存在）。

## 2. 真实路径：install.sh 委派（成功）

QUICKSTART 的定位是"五分钟接入"，其路径是重跑 `install.sh`——新版
`checks/install.sh` 检测到目标已有 `keel/` 时会**委派升级引擎**：

```bash
bash <(curl -fsSL https://gitee.com/idcu/keel-starter/raw/v3.7.0/install.sh) . --ref v3.7.0
```

- 退出码 **0**
- 全流程耗时 **49.5s**（含在线 clone 发布仓 + 升级 + 前后门禁）
- 没有第二次报错，没有要求人工改任何自定义文件

### 改动清单（采用方视角）

| 类型 | 文件 | 说明 |
|---|---|---|
| 改 | `keel/INDEX.md` | 只改 `keel-version:` 一行（3.5.0 → 3.7.0） |
| 改 | `keel/checks/install.sh` | 新版改为委派升级引擎 |
| 改 | `keel/checks/test-lint.py` | 权限 755 → 644（清单登记值，非内容变化） |
| 新增 | `keel/checks/keel-upgrade.sh` | 升级引擎本体 |
| 新增 | `keel/checks/manifest.tsv` | 四分类清单（内核/合并/保留/新增）+ sha256 + 权限 |
| 新增 | `keel/checks/test-upgrade.py` / `test-upgrade.sh` | 升级引擎自测 |
| 新增 | `keel/archive/safe-delete-full.md` | 冷区归档 |
| 新增 | `.keel-backup/` | 整目录备份（可 `--rollback` 一键回退） |

**采用方自定义的 `rules.md` / `CONSTITUTION.md` / `decisions/` / `pitfalls/` /
`NOW.md` 一个字节都没动**——47 个 preserve/merge 文件哈希不变。

### 门禁前后（副本内实跑）

| 门禁 | 升级前（3.5.0 自带工具） | 升级后（3.7.0 工具） |
|---|---|---|
| `keel-lint.sh keel` | 0 fail（2.77s） | 0 fail（3.02s） |
| `test-lint.sh` | 43/43（19.5s） | 43/43（20.3s） |
| 预算固定成本 | 4861B ≤ 15000B | 4861B ≤ 15000B |

门禁没有拦下升级，也没有在升级后报出新问题——3.5.0 → 3.7.0 跨 6 个小版本，
采用方侧零返工。

### 装好后的自证

| 检查 | 结果 |
|---|---|
| `--check-manifest keel` | ✅ 一致（69 行）；发布侧守卫在**采用方仓库**上同样成立 |
| 幂等复跑 | `✅ 已是 v3.7.0，无需升级`，exit 0，未新增备份 |
| `--force` 复跑 | 47.0s，内核覆盖 21 / 新增 0 / 保留 47，预算 4861B |

## 3. 结论：QUICKSTART 够不够？

**按本次实测：不够，但缺的是文档的一段，不是脚本的行为。**

- 脚本侧：`install.sh` 的委派路径完全可用，一条命令、exit 0、零人工介入；
- 文档侧：QUICKSTART 直到 v3.7.0 才补上「先确认有没有升级引擎」这一步。
  3.5.0 的采用方翻开 QUICKSTART §4 只会看到 `keel-upgrade.sh ...` 三行，
  照抄必 127——这正是本次的介入点。

已在本轮补两处（不改脚本）：

1. QUICKSTART §4 开头：`ls keel/checks/keel-upgrade.sh` → 没有就重跑
   `install.sh --ref v3.7.0`（会拉起引擎并直接升级）；
2. §5 排错表新增一行：`No such file or directory` → 停在 ≤3.5.0 → 重跑 `install.sh`。

补上后，一个不知道内部实现的新采用方**只靠 QUICKSTART 就能完成升级**。

### 退出码与提示评估

| 场景 | 提示 | 够用？ |
|---|---|---|
| 没有引擎（127） | `No such file or directory` | ❌ 只说事实不说出路（已在文档补） |
| 版本已最新 | `✅ 已是 v3.7.0，无需升级` | ✅ 明确、exit 0 |
| 升级成功 | 分类动作 + 前后门禁对比 + 备份路径 | ✅ 可核对 |
| 门禁失败 | 自动整目录回滚，exit 3 | ✅ 不会留下半升级状态 |
| 清单漂移（发布方） | 文件名 + 期望/实际哈希，exit 1 | ✅ v3.7.0 新增，前移到发布侧 |

## 4. 本轮未覆盖（v3.7.0 时点）

- 3.7.0 升级后**未重跑 lytjs 自身业务套件**（只改了 `keel/`，属工具面变更）——
  已在 §5 补齐（2026-11-03 实测）。
- 未验证「升级中途 Ctrl-C」的断点恢复（`--rollback` 只覆盖门禁失败路径）——
  已在 v3.7.1 补齐（pending + `--resume`，见 §5 末注）。

## 5. 3.7.0 业务侧补测（2026-11-03）

在 `origin/v7.0.0-dev`（`dab27d73`）临时副本上，先把 Keel 升到 **v3.7.0**，再跑
`npm run test:coverage`（= `vitest run --coverage`）。结果：

| 项 | 3.5.0 记录 | 3.7.0 实测 |
|---|---|---|
| 文件 / 用例 | 385 / 8436 | **384 / 8432** |
| vitest 耗时 | 323.6s | **54.94s** |
| statements / branches | 87.66% / 87.73% | **87.65% / 87.71%** |
| functions / lines | 88.00% / 87.69% | **88.02% / 87.65%** |

差异原因：`origin` 比本地 HEAD 少 5 个测试文件（本地未推送），因此少 1 文件 / 4 用例，
**不是升级影响**；耗时旧值未保留运行条件（冷/热缓存、机器负载），本次只报可复现的
54.94s，不做归因；覆盖率四项差 ≤0.04pp，视为持平。运行 `rc=0`，无 skip / fail。
详见 starter `CASE.md` §6。

> 中断恢复已在 v3.7.1 补齐：pending 原子写 + `--resume`（sha256 校验 / 拒跨版本 /
> 只处理剩余文件）+ `--rollback`（字节与权限还原）；自测 18 例覆盖 6 类中断场景。
