#!/usr/bin/env python3
"""operators.py —— 判据变异算子注册表（DESIGN §12.3「判据变异引擎」）

一个算子 = 一个纯函数 `apply(anchor: str) -> str | None`：
    * 输入是 `sites.tsv` 里逐字命中的一行判据代码；
    * 输出是**同一行**的语义改动；返回 None 表示该算子不适用于这个位点（ENUMERATE 失败，不静默跳过）。
    * 无随机、无环境依赖、无文件系统访问——同一输入永远同一输出。

新增算子：实现函数 → 加进 OPERATORS → 在 `sites.tsv` 的 operator 列引用。
"""

import re


def remove_check(old):
    """删掉一次 fail/warn 发射（含 case 分支的 `;;` 与 `if ...; then` 内联形态）。"""
    indent = old[:len(old) - len(old.lstrip())]
    s = old.strip()
    m = re.match(r"^(\S+\))\s*(?:fail_msg|warn_msg)\s.*\s(;;)$", s)
    if m:
        return indent + m.group(1) + " " + m.group(2)
    m = re.match(r"^((?:if|elif)\s.*;\s*then)\s+(?:fail_msg|warn_msg)\s.*$", s)
    if m:
        return indent + m.group(1) + " :"
    if ("fail_msg" in s or "warn_msg" in s or 'echo "❌' in s
            or 'echo "⚠️' in s):
        return indent + ":"
    return None


def remove_emit(old):
    """删掉 awk 程序里的一行 `printf "❌ ..."` 发射（整行换成 awk/bash 注释）。"""
    indent = old[:len(old) - len(old.lstrip())]
    if 'printf "❌' in old or "printf '❌" in old:
        return indent + "# removed"
    return None


_TOKENS = {
    "-gt": "-le", "-le": "-gt",
    "-lt": "-ge", "-ge": "-lt",
    "-eq": "-ne", "-ne": "-eq",
    "-n": "-z", "-z": "-n",
}
_TOKEN_RE = re.compile(r'(?<![A-Za-z0-9_"$])'
                       r'(-gt|-le|-lt|-ge|-eq|-ne|-n|-z)'
                       r'(?![A-Za-z0-9_])')
_EQ_RE = re.compile(r'(?<![=!<>])\s=\s(?!=)')
_NE_RE = re.compile(r'(?<![=!<>])!=')
_EQ2_RE = re.compile(r'(?<![=!<>])==(?!=)')


def invert_guard(old):
    """把一次比较 / 测试条件取反；含 `-n↔-z`、`=↔!=`、`==↔!=`。"""
    m = _TOKEN_RE.search(old)
    if m:
        tok = m.group(1)
        return old[:m.start(1)] + _TOKENS[tok] + old[m.end(1):]
    m = _NE_RE.search(old)
    if m:
        return old[:m.start()] + "==" + old[m.end():]
    m = _EQ2_RE.search(old)
    if m:
        return old[:m.start()] + "!=" + old[m.end():]
    m = _EQ_RE.search(old)
    if m:
        return old[:m.start()] + " != " + old[m.end():]
    return None


_IF_RE = re.compile(r'^(\s*)if\s+(?!not\s)(.+):\s*$')


def invert_if(old):
    """把 Python 的 `if <条件>:` 取反成 `if not <条件>:`（用于元检查的判死分支）。"""
    m = _IF_RE.match(old)
    if not m:
        return None
    return "%sif not %s:" % (m.group(1), m.group(2))


_BOUND_RE = re.compile(r'(-gt|-ge)\s+("[^"]+"|[0-9]+)')


def shift_bound(old):
    """上界阈值放宽 ×2：`-gt 10` → `-gt 20`，`-gt "$lim"` → `-gt "$((lim * 2))"`。"""
    m = _BOUND_RE.search(old)
    if not m:
        return None
    operand = m.group(2)
    if operand.startswith('"'):
        inner = operand[1:-1]
        if not inner.startswith("$"):
            return None
        var = inner[2:] if inner.startswith("${") else inner[1:]
        if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", var):
            return None
        new = '"$((%s * 2))"' % var
    elif operand.isdigit():
        new = str(int(operand) * 2)
    else:
        return None
    return old[:m.start(2)] + new + old[m.end(2):]


_MATCH_RE = re.compile(r'(-qE?)\s+"([^"]+)"')


def relax_match(old):
    """放宽 grep 模式：删掉模式里的版本字面量（`^## ${_v} —` → `^## `）。"""
    m = _MATCH_RE.search(old)
    if not m:
        return None
    pat = m.group(2)
    if "${" not in pat:
        return None
    prefix = pat.split("${", 1)[0]
    newpat = prefix if prefix.strip() else "."
    return old[:m.start(2)] + newpat + old[m.end(2):]


# 算子 id → (实现, 一句话说明, 适用位点特征)
OPERATORS = {
    "remove_check": (remove_check, "删掉 fail/warn 发射或 case 分支", "fail_msg/warn_msg/echo ❌"),
    "remove_emit": (remove_emit, "删掉 awk 里的 printf 发射行", 'printf "❌'),
    "invert_guard": (invert_guard, "比较/测试条件取反", "-gt/-eq/-n/=/==/!="),
    "invert_if": (invert_if, "Python if 条件取反", "if <expr>:"),
    "shift_bound": (shift_bound, "上界阈值放宽 ×2", "-gt/-ge 的数值或变量"),
    "relax_match": (relax_match, "grep 模式删掉版本字面量", "-qE 含 ${...} 的模式"),
}


def apply(op, anchor):
    if op not in OPERATORS:
        raise KeyError("未注册的算子: %s" % op)
    return OPERATORS[op][0](anchor)
