# AGENTS.md

> Keel 项目（`keel` 规格仓）的 AI 上下文入口。

## 点火锚点（规范原文，禁止改写）

任何任务开始前，先读 keel/INDEX.md 与其中指向的 NOW.md，并遵守 INDEX.md 里的检索协议。

> 这一句是《Keel 设计稿》§4.1 的原文。`keel-lint.sh` 第 10 项按**逐字比对**校验它，
> 改写即 fail——因为锚点写错等于整套检索协议从未被读到，而这种失效不会报任何错。

## 本仓怎么工作

| 做什么 | 去哪 |
|---|---|
| 改规格 | `DESIGN.md`（唯一真源，§ 编号引用都指向它） |
| 改模板 | `keel-starter/keel/`（对外分发的纯骨架） |
| 记进度 | `keel/NOW.md`（每轮必改，见下） |
| 发布 | `scripts/release.sh --apply`（推送顺序写死在脚本里） |

**先读 `keel/INDEX.md`，再动手。** 它的路由表告诉你去哪个文件；不要全局 grep。

## 三个最容易踩的坑

1. **改了 `keel-lint.sh` 必须同步 `DESIGN.md` §9.3 的代码块**——`test-lint.sh`
   的 DOC 检查逐字比对，不一致直接 FAIL。改脚本与改文档是同一个动作。
2. **推送顺序恒为「先发布仓、后项目仓」**——反了别人 clone 会取不到子模块。
   用 `scripts/release.sh --apply`，别手动敲两条 push。
3. **`keel/`（本仓根）与 `keel-starter/keel/`（模板）是两个东西**——
   结构相同、内容独立演进。改模板改子模块那一份，改本项目进度改根目录那一份。

## 收尾（不做这步，本轮不算完成）

- 写回 `keel/NOW.md`：本轮做了什么、没做什么、下一步、阻塞
- 新坑登记进 `keel/pitfalls/INDEX.md`（并在 commit message 写 `pitfall: <文件名>`，
  钩子会自动给该条 `triggers` +1）
- 跑一次 `bash keel/checks/keel-lint.sh keel`，必须 0 fail

```bash
bash keel/checks/keel-lint.sh keel      # 一致性校验：0 fail 才放行
bash keel/checks/test-lint.sh           # lint 自测：41 用例 + 1 元检查
```

> 前置：每个新 clone 跑一次 `bash keel/checks/install-hooks.sh`（`core.hooksPath`
> 是仓库级本地设置，不进版本历史）。
