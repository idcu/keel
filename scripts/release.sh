#!/usr/bin/env bash
# release.sh —— 两仓推送编排（《Keel 设计稿》§12.3）
# 用法: bash scripts/release.sh [--apply] [--allow-dirty]
# 退出码: 0 = 完成（含 dry-run）；1 = 前置检查或自检未通过；2 = 用法 / 环境错误
#
# 为什么需要它：
#   §12.3 有一条硬约束——**推送顺序恒为：先发布仓（keel-starter）、后项目仓（keel）**，
#   否则别人 clone 后 `git submodule update` 会取不到指针指向的那个提交。
#   这条约束靠人记，迟早会错一次；所以把它变成脚本：顺序写死在代码里，不靠自觉。
#
# 默认 dry-run：只打印将要执行的动作，加 --apply 才真的 push。
set -uo pipefail

HERE=$(cd "$(dirname "$0")" && pwd)
PROJ=$(cd "$HERE/.." && pwd)
SUB="$PROJ/keel-starter"

APPLY=0; ALLOW_DIRTY=0
for a in "$@"; do
  case "$a" in
    --apply|-y) APPLY=1 ;;
    --dry-run) APPLY=0 ;;
    --allow-dirty) ALLOW_DIRTY=1 ;;
    -*) echo "❌ 未知参数: $a"; exit 2 ;;
  esac
done

die() { echo "❌ $1"; exit 1; }

[ -e "$SUB/.git" ] || die "找不到子模块工作区: $SUB（先 git submodule update --init）"
[ -f "$PROJ/.gitmodules" ] || die "项目仓缺 .gitmodules"

echo "release · 项目仓=$PROJ · 发布仓=$SUB · 模式=$([ "$APPLY" -eq 1 ] && echo apply || echo dry-run)"

echo "── 1. 前置检查"
if [ "$ALLOW_DIRTY" -eq 0 ]; then
  for r in "$PROJ" "$SUB"; do
    [ -z "$(git -C "$r" status --porcelain)" ] || die "工作区不干净: $r（先提交 / stash，或用 --allow-dirty 跳过本检查）"
  done
  echo "   ✅ 两侧工作区干净"
else
  echo "   ⚠️  已跳过「工作区干净」检查（--allow-dirty）"
fi

# 子模块指针一致性：git submodule status 行首 '+' = 指针与检出不一致
st=$(git -C "$PROJ" submodule status -- keel-starter 2>/dev/null) || die "读不到子模块状态"
case "$st" in
  "") die "子模块未注册（.gitmodules 与索引不一致？）" ;;
  +*) die "子模块指针与发布仓 HEAD 不一致（status 行首为 +）——先在项目仓 git add keel-starter 并提交" ;;
  *)  echo "   ✅ 子模块指针一致：$(printf '%s' "$st" | sed -E 's/^[ +-]//' | cut -c1-12)…" ;;
esac

echo "── 2. 发布仓自检（不通过就不许推）"
if [ "$APPLY" -eq 1 ]; then
  ( cd "$SUB" && bash keel/checks/test-lint.sh ) || die "发布仓自测未通过"
  ( cd "$SUB" && bash keel/checks/keel-lint.sh keel ) || die "发布仓 keel-lint 未通过"
else
  echo "   [dry-run] (cd keel-starter && bash keel/checks/test-lint.sh)"
  echo "   [dry-run] (cd keel-starter && bash keel/checks/keel-lint.sh keel)"
fi

echo "── 3. 推送（§12.3 硬约束：① 发布仓 → ② 项目仓）"
BR_STARTER=$(git -C "$SUB" rev-parse --abbrev-ref HEAD)
BR_PROJ=$(git -C "$PROJ" rev-parse --abbrev-ref HEAD)
# detached HEAD 只在**真要推送**时才是问题：CI 的新 clone 里子模块本来就是分离头
# （checkout 出来的），dry-run 必须能在那种环境下跑通，否则它就成了"只能在本地跑的自检"。
if [ "$APPLY" -eq 1 ]; then
  [ "$BR_STARTER" = "HEAD" ] && die "发布仓处于 detached HEAD，无法推送"
  [ "$BR_PROJ" = "HEAD" ] && die "项目仓处于 detached HEAD，无法推送"
fi

echo "   ① 发布仓（$BR_STARTER）—— 必须先推，否则②的指针没人能取到"
if [ "$APPLY" -eq 1 ]; then
  git -C "$SUB" push -u origin "$BR_STARTER" || die "发布仓推送失败，已中止（项目仓未推送）"
else
  echo "   [dry-run] git -C keel-starter push -u origin $BR_STARTER"
fi

# 推送前再确认一次指针：发布仓若刚有新提交，指针会再次失配
st2=$(git -C "$PROJ" submodule status -- keel-starter 2>/dev/null)
case "$st2" in
  +*) die "推送前指针又失配（发布仓刚有新提交？）——在项目仓 git add keel-starter 后重跑" ;;
esac

echo "   ② 项目仓（$BR_PROJ）"
if [ "$APPLY" -eq 1 ]; then
  git -C "$PROJ" push -u origin "$BR_PROJ" || die "项目仓推送失败（发布仓已推送成功，重跑会跳过它）"
else
  echo "   [dry-run] git -C $PROJ push -u origin $BR_PROJ"
fi

echo "──"
if [ "$APPLY" -eq 1 ]; then echo "✅ 两仓推送完成（顺序正确：发布仓 → 项目仓）"; else echo "（dry-run 未推送）确认无误后重跑：bash scripts/release.sh --apply"; fi
exit 0
