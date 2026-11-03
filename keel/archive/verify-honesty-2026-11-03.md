# v3.11.0 验证诚实性实测（2026-11-03）

> 结论先说：**三环境的 test-faults 语义已可区分，且不会静默 PASS；3.6.1 矩阵格
> 跑通并顺带修掉一个恢复缺口（旧引擎中断后重跑 install.sh 无法续跑）；
> verify-report.json 已进入发布链路，含 SKIP 的清单配「无条件通过」文案会被判死。**
> 未跑项列在 §8，不用「全部通过」掩盖。

## 1. 环境

| 项 | 值 |
|---|---|
| 机器 | macOS 15.8.2（Darwin 24H232），Apple Silicon |
| Python | 3.13.5（`python3`） |
| Docker | 29.7.2（Docker Desktop，linux 容器可用，`docker info` OSType=linux） |
| locale | `LANG=zh_CN.UTF-8`，`LC_ALL` 未设置 |
| 起点仓 | `keel-starter` HEAD `0c3f5df`（v3.10.0） |
| 矩阵快照缓存 | `${TMPDIR}/keel-matrix-cache`（按 tag 缓存，命中复用） |

## 2. test-faults 三环境实测

命令统一为 `python3 keel/checks/test-faults.py`，只改环境：

| 环境 | 构造方式 | 输出（关键行） | exit |
|---|---|---|---|
| ① Docker 可用 | 原样 | 7 例 `PASS`；`✅ 真实故障自测通过：7 通过 / 0 失败 / 0 跳过（未验证）` | 0 |
| ② 无 docker 二进制 | `PATH=/usr/bin:/bin:/usr/sbin:/sbin`（不卸载） | `SKIP：PATH 上找不到 docker 二进制`；`环境分类：no-binary`；`⚠️ … 0 通过 / 0 失败 / 7 跳过（未验证）` | 0 |
| ③ daemon 不可用 | `DOCKER_HOST=unix:///tmp/keel-no-such-docker.sock` | `SKIP：docker 二进制在，但 daemon 不可用（docker info rc=1）`；`环境分类：no-daemon`；同样 `0/0/7 跳过（未验证）` | 0 |
| ③ + 严格模式 | 同上 + `KEEL_FAULTS_REQUIRE_DOCKER=1` | 同上，另打印「严格模式 … → exit 1」 | 1 |

要点：

- 环境探测分五态（`ok / disabled / no-binary / no-daemon / non-linux`），
  ②③ 的**原因不同**，修复方式也不同，不再合并成一句「没有 Docker」。
- 无 Docker 时汇总永远写成「0 通过 / 0 失败 / N 跳过（未验证）」，不出现「通过」
  这个无条件词；7 例故障注入被明确标为未验证。
- 默认策略是「跳过并计入未验证、exit 0」，理由与 ADR 0005 一致：CI 缺 Docker 时
  变红只说明环境没装好，不指向任何代码缺陷，红得没有信息量会被习惯性忽略；
  门禁要求真跑时用 `KEEL_FAULTS_REQUIRE_DOCKER=1` 主动收紧。
- 6 条判死自检（不需要 Docker）随套件先跑：无断言输出、有 `FAIL` 行、`LINT≠0`
  都不得算 PASS；跳过策略不得退化成无条件通过表述。②③ 环境下自检仍 6/6 通过，
  即「汇总器本身没被骗」已被验证，只是故障注入未验证。

## 3. 矩阵：3.6.1 新格与恢复缺口

默认格改为 `3.6.1,3.7.4,3.8.0,3.9.0,current`，另保留 `3.4.11(install)` 与 `REG-1`。

命令：

```bash
python3 keel/checks/matrix/test-upgrade-matrix.py            # 串行
KEEL_MATRIX_JOBS=4 python3 keel/checks/matrix/test-upgrade-matrix.py   # 并行
```

实测结果（7 格 / 0 失败 / 0 跳过）：

| 格 | 结果 | 说明 |
|---|---|---|
| 3.6.1 → current | PASS | 老引擎执行升级：无假失败、内核逐字节一致、自定义文件哈希不变、门禁绿、终态五项 |
| 3.7.4 → current | PASS | 同上 + backup 中断续跑 + rollback |
| 3.8.0 → current | PASS | 同上 |
| 3.9.0 → current | PASS | 同上 |
| current → current | PASS | 幂等：no-op、零改动 |
| 3.4.11(install) | PASS | ≤3.5.0 无升级引擎，走 install.sh 引导 |
| REG-1 | PASS | 旧引擎备份布局（无 restore.sh）不再触发终态误判 |

3.6.1 暴露的两个问题与处理：

1. **矩阵误用新判据**：3.6.1 引擎早于 v3.7.1，没有 `--resume` / `KEEL_UPGRADE_*`
   故障钩子，直接套 ⑥⑦ 会红在「历史版本没这个能力」，不是升级被误判。
   处理：`engine_caps()` 探测起点能力；不足时改走 `install.sh` 引导路径，由
   **目标版本新引擎**完成并验证续跑/回滚。该格因此同时覆盖「老引擎执行」与
   「引导到新引擎」两条真实路径，耗时 53.9s（其余格约 10–15s）。
2. **恢复缺口（产品 bug）**：引导在 backup 阶段中断后，目标盘上的引擎仍是旧的；
   重跑 `install.sh` 原本会以「存在未完成升级」exit 5，并把 `--resume` 命令指向
   这个不支持它的旧引擎（实测报「未知参数: --resume」）。修复：`install.sh`
   检测 `.keel-upgrade.pending` 后，把断点交给目标版本引擎并带 `--resume`。
   矩阵 3.6.1 格已作为回归用例覆盖这条路径。

耗时变化：串行总耗时 113s → 170s（+57s，主要是 3.6.1 的双路径）；快照缓存命中
不联网。新增 `KEEL_MATRIX_JOBS`（默认 1，保持日志顺序）；`KEEL_MATRIX_JOBS=4`
实测 68s，断言一条未减（只改调度）。未默认开并行，避免单核 CI 抖动与日志交错。

## 4. verify-report：清单与判据

生成：

```bash
bash keel/checks/verify/verify.sh --out verify-report.json
python3 keel/checks/verify/check-verify-report.py --report verify-report.json --summary
```

清单每条记录：套件名、`PASS/FAIL/SKIP`、跳过原因、用例数、通过/失败/跳过数、
耗时、环境（平台 / locale / 容器镜像 / 引擎版本 / 矩阵并行度）、矩阵格。

判据（`check-verify-report.py`，`--selftest` 8 个构造样例）：

- 套件标 `PASS` 却 `skipped>0` → 伪装 PASS，判死；
- 清单含 SKIP/FAIL 时，发行说明出现「全部通过 / 全绿 / all green」等 → 判死；
- 含 SKIP 时说明必须写「X 通过 / Y 跳过（未验证）」，且 **X/Y 要与清单数字一致**；
  只写「跳过（未验证）」但 Y 写成 0，同样判死；
- `--selftest` 自带负例（含 SKIP + 无条件通过）证明判据会红，不是永远绿的装饰。

真文案负控（用本轮 CHANGELOG 作为说明）：

| 清单 | 说明 | 结果 |
|---|---|---|
| 98 通过 / 1 跳过 | CHANGELOG 3.11.0 小节（写「98 通过 / 0 失败 / 1 跳过（未验证）」） | ✅ 一致 |
| 96 通过 / 1 跳过（构造） | 同一份 CHANGELOG | ❌ `称 98 通过，清单是 96 通过` |

这证明「清单里有 SKIP 而说明写无条件通过/数字不符」会在 release.sh 推送前被拦住。

## 5. 全量复跑数字

命令（starter 仓内，完整清单 + 并行矩阵）：

```bash
KEEL_MATRIX_JOBS=4 bash keel/checks/verify/verify.sh \
  --out /tmp/vr-final4.json --label "v3.11.0 全量"
```

| 套件 | 用例数 | 结果 | 耗时 |
|---|---|---|---|
| claims-selftest | 8 | 8/8 | 0.0s |
| lint（starter） | 1 门 | 0 fail | 1.6s |
| manifest（starter） | 1 门 | 75 行一致 | 1.7s |
| test-lint | 51 | 50 通过 / 0 失败 / 1 跳过 | 16.0s |
| test-upgrade | 24 | 24/24 | 393.1s |
| test-faults | 7（+6 判死自检） | 7/0/0 | 32.5s |
| matrix | 7 格 | 7/0/0 | 72.3s |
| **合计** | **98 通过** | **98 通过 / 0 失败 / 1 跳过（未验证）** | **约 8 分 37 秒** |

1 项跳过是 test-lint 用例 44（「文件名仅大小写不同」）：macOS 默认卷大小写不敏感，
无法构造两个只差大小写的文件，该例主动 SKIP 并打印原因。**它没有被记成 PASS**——
清单里 `skipped=1`、套件状态 `SKIP`、附原因；Windows / Git Bash 的同名覆盖行为
因此仍未验证。这正是「清单也是验谎对象」的用例：解析器若把打印出来的 SKIP 吞掉，
清单就会变成 `0 跳过` 的伪装通过（本轮改的就是这个 bug）。

DOC / PROSE 两项元检查在本机 macOS 上因为能向上找到 `DESIGN.md`，实测通过；
`test-lint` 总 50/50 含这两项。项目仓单独复核：`keel-lint` 0 fail（2s，预算 300s）；
`--check-manifest` 75 行一致；`test-lint` 50/50（含 DOC / PROSE）。
glibc Debian 12 双 locale 见 §7。

**本轮排查记录（必须保留）**：首次全量复跑得到 `68 通过 / 30 失败`，根因不是代码，
而是改完 `checks/verify/check-verify-report.py` 后 starter 的 `manifest.tsv` 哈希未重算
（`--check-manifest` 已直接指出）。重算后同一套命令 98 通过 / 0 失败 / 1 跳过。教训并入
`pitfalls/meta/distribution-list-drift.md` 的 v3.11.0 修订，避免下次再从四个套件逐个查。

## 6. 最终 verify-report（本机）

`/tmp/vr-final4.json` 已原样归档到 `keel/archive/verify-report-3.11.0.json`：

```json
{
  "schema": 1,
  "generated_at": "2026-11-04T01:27:03+08:00",
  "label": "v3.11.0 全量",
  "environment": {
    "platform": "darwin",
    "platform_release": "24.6.0",
    "python": "3.13.5",
    "locale": {"LANG": "zh_CN.UTF-8", "LC_ALL": null, "LC_CTYPE": null},
    "container_image": "python:3.11",
    "engine_version": "3.11.0",
    "matrix_jobs": "4"
  },
  "summary": {"passed": 98, "failed": 0, "skipped": 1, "verified": false}
}
```

`verified: false` 是如实的：test-lint 用例 44 在 macOS 上跳过。发行说明必须写
「98 通过 / 1 跳过（未验证）」——`check-verify-report.py` 已实测放行该文案，
并在构造「清单 96 通过 / 1 跳过 + 说明 98 通过」时判死。

## 7. glibc 双 locale（容器内）

复用长期容器 `keel-gnu-12`（Debian 12 / bash 5.2.15 / glibc 2.36 / python 3.11.2 /
已生成 `zh_CN.utf8`）；`/src` 只读挂载宿主仓，容器内 `cp -a` 到 `/w-C`、`/w-Z`
后并行跑，宿主零写入。

```bash
docker exec keel-gnu-12 bash -lc '
  rm -rf /w-C /w-Z; cp -a /src/keel-starter /w-C; cp -a /src/keel-starter /w-Z
  ( cd /w-C && export LANG=C LC_ALL=C && \
      bash keel/checks/keel-lint.sh keel && \
      bash keel/checks/keel-upgrade.sh --check-manifest keel && \
      bash keel/checks/test-lint.sh && bash keel/checks/test-upgrade.sh ) &
  ( cd /w-Z && export LANG=zh_CN.UTF-8 LC_ALL=zh_CN.UTF-8 && …同上… ) &
  wait'
```

| 项 | Debian 12 · C | Debian 12 · zh_CN.UTF-8 |
|---|---|---|
| keel-lint | 0 fail · 0.223s | 0 fail · 0.388s |
| manifest | 75 行一致 | 75 行一致 |
| test-lint | 50/50（DOC / PROSE 因无 DESIGN.md 打印 SKIP） | 50/50（同上） |
| test-upgrade | 24/24 | 24/24 |

两 locale 并行执行，未逐套件单独计时；`test-lint` 的 DOC/PROSE 跳过与 macOS
starter 一致（发布模板不含 `DESIGN.md`），不是 locale 引起的差异。

## 8. 未覆盖 / 未验证项

- 无 Docker 与 daemon 不可用环境下的**真实故障注入**未跑：只实测了 `SKIP(原因)`
  语义与退出码，故障本身未验证。需在有 Docker 的机器复跑 `test-faults.py`。
- 矩阵未覆盖 3.5.x、3.10.x 起点；3.6.1 只取该系列一个代表格，不能外推整个 3.6.x。
- EROFS 在无 `SYS_ADMIN` 的 CI 环境未验证；本机 Docker Desktop 下 7 例全过。
- 并行矩阵在单核/低内存 CI 的耗时未实测；`KEEL_MATRIX_JOBS=4` 只在本机验证。

## 9. 发布与跨版本冒烟

- 版本：3.11.0（minor：旧引擎续跑修复、矩阵 3.6.1、机器可读清单）。
- 发布：`bash scripts/release.sh --apply` 在推送前重跑完整验证，结果为
  **98 通过 / 0 失败 / 1 跳过（未验证）**，判据放行 CHANGELOG 后按顺序推送：
  - starter `main`：`0c3f5df..4016ed4`；annotated tag `v3.11.0`（tag 对象
    `771d1ef`，peeled `4016ed4`）
  - 项目仓 `main`：`48bb60e..6e6b0a6`（子模块指针 = `4016ed4`）；
    本文件与 NOW 的收尾记录在 `6e6b0a6` 之后单独提交并推送（发布仓不再变动）
  - `ls-remote` 双向核对：两仓 `refs/heads/main` 与本地 HEAD 一致；
    `refs/tags/v3.11.0^{}` = `4016ed4`，不存在「声明了版本但取不到 tag」。

- 冒烟（真实 clone tag，不用工作区）：
  1. `git clone --depth 1 --branch v3.8.0 … /tmp/keel-smoke-old` →
     `bash …/install.sh /tmp/keel-smoke-proj --ref v3.8.0 --with-anchor`，rc 0，
     `keel-version: 3.8.0`，lint 通过。
     （首次误用不带 `--ref` 的旧 install.sh：它默认取 `main`，装成 3.11.0；
     故本次冒烟显式钉 `--ref`，避免把「装到最新」误当成「装到旧版」。）
  2. `bash /tmp/keel-smoke-new/install.sh /tmp/keel-smoke-proj --ref v3.11.0
     --with-anchor`（模板来自 v3.11.0 tag），rc 0：
     `✅ 升级完成：3.8.0 → 3.11.0（内核覆盖 27 · 新增 0 · 保留 47）`，
     终态校验 5 项通过，升级后 lint 0 fail。
  3. 验收：`keel-version: 3.11.0`，`keel-lint` 通过（1s），锚点已写入。
     备份 `3.8.0-to-3.11.0-20261104-014437` 保留可回滚。
