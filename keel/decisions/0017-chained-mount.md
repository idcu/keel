---
scope: meta
status: active
last-verified: 2026-10-05
keywords: [钩子, 链式挂载, husky, core.hooksPath, 通用性]
type: decision
created: 2026-10-05
superseded-by:
---

# 0017 支持链式挂载：既有钩子框架（husky 等）不必让出 core.hooksPath

## 背景

首个真实采用方 lytjs 用 husky：`core.hooksPath=.husky/_`，且 husky 的 `prepare` 会在每次
`pnpm install` 时重置挂载点。而 `install-hooks.sh` 拒绝覆盖既有挂载、`verify-hooks.sh` 又要求
精确等于 `keel/checks/hooks`——采用者卡在"装不上闭环"，只能二选一：放弃 husky 或放弃 keel 钩子。
不能为单一框架特化，但"与既有钩子框架共存"是任何项目都会遇到的通用场景。

## 决定

"闭环成立"的判定从"挂载点必须相等"扩展为**两种形态**：
1. **直挂**：`core.hooksPath` == `<keel>/checks/hooks`（原判定，不变）；
2. **链式**：`core.hooksPath` 归别的框架，但 **git 实际执行的钩子文件、或其父目录的同名文件**里
   检出了 keel 钩子本体路径（`<keel>/checks/hooks/<钩子名>`）→ 视为已挂载。

父目录探测覆盖 husky 的委托形态（`.husky/_` → `.husky/<钩子>`）；判定用 `grep -qF`，
只看"有没有调用"，不解析框架语义。`install-hooks.sh` 的冲突提示同步指向"并入调用"的修法。

## 被否掉的选项

| 选项 | 为什么没选 |
|---|---|
| 让 keel 抢回 core.hooksPath，再回调 husky | husky 的 prepare 会在每次 install 重置挂载点，争夺同一配置位 |
| 只认框架容器里的文件（不含父目录） | husky 的委托链是 `_/` 执行 → 父目录用户钩子，不探测父目录就检不出 |
| 靠人改 verify-hooks 白名单 | 豁免靠口头约定 = 静默失效；违反"机器可判" |

## 影响

- `verify-hooks.sh`：新增链式判定与提示；直挂 / 未挂载行为不变
- `install-hooks.sh`：冲突提示补充链式修法（拒绝覆盖的行为不变）
- 规格：DESIGN §10.4 增"与既有钩子框架共存"段
- lytjs：keel 钩子本体并入 `.husky/{pre-commit,commit-msg}`，闭环在 husky 之下成立
