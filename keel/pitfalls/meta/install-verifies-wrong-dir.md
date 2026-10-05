---
scope: meta
status: active
severity: P0
last-verified: 2026-10-05
triggers: 0
keywords: [假成功, 校验对象, cwd, 相对路径, 传参, install, doctor, 静默]
---

## 症状

- `install.sh` 报「✅ lint 通过」，单独跑 lint 却是 ❌ 点火锚点缺失——**结论相反**
- `keel-doctor.sh` 报「闭环成立」，但 `core.hooksPath` 指向别处——挂载根本没验

## 根因

验证脚本"验错了对象"，且都静默：
① install 用相对路径调 lint（`... keel-lint.sh keel`），入参相对 **cwd** 解析；
从别处调用时 cwd 是发布仓自己 ⇒ 检的是发布仓（当然绿）；
② doctor 把 **keel 目录**当项目根传给 `verify-hooks.sh "$KEEL"` ⇒ 前缀匹配失效、
mount 检查整体跳过 ⇒ 恒 exit 0。

**比"不验证"更坏**：不验证至少诚实，假成功让人以为装好了。

## 正解

- 调接受相对路径入参的脚本前先 `cd "$TARGET"`；传参前核对**签名要的是哪个对象**
- 判据：**验证步骤必须验证到"被验证的那个对象"**；验证器自身也要有反向用例
