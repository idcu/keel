---
scope: meta
status: active
severity: P0
last-verified: 2026-11-02
triggers: 1
keywords: [假成功, 校验对象, cwd, install, doctor, 自测]
---

## 症状

- `install.sh` 报「✅ lint 通过」，单独跑 lint 却 ❌ 锚点缺失——结论相反
- `keel-doctor.sh` 报「闭环成立」，但 `core.hooksPath` 指向别处——挂载没验
- 同一自测发布仓 10/10、规格仓 8/10 假失败：fixture 缺仓外文件 → 前置 lint 死链

## 根因

验证脚本"验错了对象"，且都静默——**假成功比不验证更坏**：
① install 用相对路径调 lint，入参按 cwd 解析，从别处调用 ⇒ 检的是发布仓；
② doctor 把 keel 目录当项目根传给 `verify-hooks.sh` ⇒ 前缀失效、mount 跳过 ⇒ 恒 0；
③ 自测默认"脚下 `keel/` 可独立分发"，规格仓实例却引用 `../DESIGN.md` 等。

## 正解

- 调相对路径入参的脚本前先 `cd "$TARGET"`；传参前核对签名要的是哪个对象
- 判据：验证步骤必须验证到"被验证的那个对象"；验证器也要有反向用例
- 自测先判被测目录能否独立分发；不能就改用发布模板（修 fixture，别放宽门禁）
