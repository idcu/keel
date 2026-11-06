#!/usr/bin/env python3
"""mutation.py —— 判据变异引擎（DESIGN §12.3「判据变异引擎」）

用法：
    python3 keel/checks/mutation/mutation.py --enumerate        # 枚举并逐字节比对 mutants.tsv
    python3 keel/checks/mutation/mutation.py --regen-mutants    # 重新生成 mutants.tsv（有意改位点/算子时）
    python3 keel/checks/mutation/mutation.py --run [--jobs N] [--out results.json]
    python3 keel/checks/mutation/mutation.py --verify            # 门禁：秒级自洽校验，不重跑
    python3 keel/checks/mutation/mutation.py --recompute [--jobs N]  # 全量重跑并比对已提交结果
    python3 keel/checks/mutation/mutation.py --negctl           # 三条负控实跑

口径（正文在 DESIGN §12.3，本文件只实现）：
    * 靶子是判据本身；sites.tsv 是人工位点清单，operators.py 是算子注册表。
    * mutants.tsv 是生成物：同一仓库版本 + 同一算子集合 → 逐字节相同，带 manifest sha256。
    * results.json 是实测结果；exemptions.tsv 是等价/暂不可杀的显式豁免（理由 + 到期）。
    * 等价变异体单独计数，不进得分分母；存活未豁免 → rc=1；已杀却声明等价 → rc=1。

退出码：0 = 全绿；1 = 有存活/无效/清单漂移/负控未判死；2 = 环境或基线错误。
"""

import argparse
import concurrent.futures as futures
import datetime
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
sys.dont_write_bytecode = True   # 变异引擎不该在仓里留下 __pycache__
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
KEEL = os.path.dirname(os.path.dirname(HERE))
PY = sys.executable

SITES = os.path.join(HERE, "sites.tsv")
MUTANTS = os.path.join(HERE, "mutants.tsv")
EXEMPTIONS = os.path.join(HERE, "exemptions.tsv")
RESULTS = os.path.join(HERE, "results.json")
REPORT = os.path.join(HERE, "mutation-report.json")

FAIL_RE = re.compile(r"^\[FAIL\] (\S+)", re.M)

# 未纳入本轮变异的判据与理由（逐条写清，不允许只挑好做的）。
EXCLUDED = [
    ("§9.1-5", "三段式缺失：多段 grep 聚合，删任一条与 §9.1-2 的「字段存在性」同型；按检查类型抽样"),
    ("§9.1-7", "索引登记：两段式（grep 索引 + awk 表格），断单行只能测到登记分支；与 §9.1-4 同型"),
    ("§9.1-8", "命名规则：含文件系统大小写敏感性交互（用例 44 在 macOS 默认盘上跳过），跨平台非确定"),
    ("§9.1-9", "引用环：依赖可选工具 tsort，缺 tsort 时判据本身 SKIP；变异存活会变成环境噪声"),
    ("§9.1-11", "状态机例外：ADR 例外字段多分支，断单条与 §9.1-6 的值域检查同型"),
    ("§9.1-12", "陈旧告警：warn_msg 且退出码仍为 0；本轮只做 fail 级判据"),
    ("§9.1-13", "待蒸馏：阈值告警，同 §9.1-12，非 fail 级"),
    ("§9.1-14", "superseded 指向：目标文件存在性，与 §9.1-4 同型"),
    ("§9.1-15", "项目扩展位：内核不实现，没有可变异的代码"),
    ("§9.1-16", "钩子本体：文件存在性，与 §9.1-10 同型"),
    ("§9.3 meta", "DOC/LOCALE/PROSE/SPEC 元检查：注入变异需要另一套 fixture 工厂；留给下一轮"),
]


def sha256_text(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def load_operators():
    spec = importlib.util.spec_from_file_location("keel_ops", os.path.join(HERE, "operators.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def parse_sites(path=SITES):
    rows = []
    with open(path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.rstrip("\n")
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) != 6:
                raise ValueError("%s:%d 列数=%d，应为 6" % (path, lineno, len(parts)))
            site, ref, target, anchor, op, cases = parts
            rows.append({"site": site, "ref": ref, "target": target,
                         "anchor": anchor, "operator": op, "cases": cases})
    return rows


def target_shas(sites):
    shas = {}
    for s in sites:
        p = os.path.join(KEEL, s["target"])
        shas[s["target"]] = sha256_text(read(p))
    return shas


def enumerate_mutants(sites, ops=None):
    """确定性枚举：sites 行序 + 纯函数算子。任何位点/算子问题都返回错误，不静默跳过。"""
    ops = ops or load_operators()
    errors = []
    shas = target_shas(sites)
    line_index = {}
    for s in sites:
        if s["target"] not in line_index:
            text = read(os.path.join(KEEL, s["target"]))
            idx = {}
            for i, l in enumerate(text.splitlines(), 1):
                idx.setdefault(l, []).append(i)
            line_index[s["target"]] = idx
    rows = []
    for s in sites:
        if s["operator"] not in ops.OPERATORS:
            errors.append("%s 引用了未注册算子 %s" % (s["site"], s["operator"]))
            continue
        occ = line_index[s["target"]].get(s["anchor"], [])
        if len(occ) != 1:
            errors.append("%s 的 anchor 在 %s 命中 %d 次（应为 1）"
                          % (s["site"], s["target"], len(occ)))
            continue
        try:
            new = ops.apply(s["operator"], s["anchor"])
        except KeyError as e:
            errors.append("%s: %s" % (s["site"], e))
            continue
        if not new or new == s["anchor"]:
            errors.append("%s 的算子 %s 不适用于该位点" % (s["site"], s["operator"]))
            continue
        mid = sha256_text("%s|%s|%s|%s|%s" % (s["ref"], s["site"], s["operator"],
                                              s["anchor"], new))[:12]
        rows.append({"id": mid, "site": s["site"], "ref": s["ref"],
                     "operator": s["operator"], "line": occ[0],
                     "old": s["anchor"], "new": new, "cases": s["cases"],
                     "target": s["target"]})
    body = "\n".join(serialize_row(r) for r in rows) + ("\n" if rows else "")
    manifest = sha256_text(body)
    target_spec = ",".join("%s@%s" % (t, shas[t]) for t in sorted(shas))
    header = "# keel-mutants v1 target=%s manifest_sha256=%s\n" % (target_spec, manifest)
    return {"rows": rows, "body": body, "manifest_sha256": manifest,
            "targets": shas, "text": header + body, "errors": errors}


def serialize_row(r):
    return "\t".join(str(r[k]) for k in
                     ("id", "site", "ref", "operator", "line", "old", "new", "cases", "target"))


def load_mutants(path=MUTANTS):
    if not os.path.isfile(path):
        return None, ["清单缺失：%s（先跑 --regen-mutants）" % path]
    text = read(path)
    header = text.split("\n", 1)[0]
    m = re.match(r"# keel-mutants v1 target=(\S+) manifest_sha256=([0-9a-f]{64})$", header)
    if not m:
        return None, ["清单头部格式非法：%s" % header]
    rows = []
    errors = []
    for lineno, line in enumerate(text.splitlines()[1:], 2):
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) != 9:
            errors.append("%s:%d 列数=%d，应为 9" % (path, lineno, len(parts)))
            continue
        rows.append(dict(zip(("id", "site", "ref", "operator", "line", "old",
                              "new", "cases", "target"), parts)))
    body = "\n".join(serialize_row(r) for r in rows) + ("\n" if rows else "")
    if sha256_text(body) != m.group(2):
        errors.append("清单 body sha256 与头部 manifest_sha256 不一致")
    return {"target_spec": m.group(1), "manifest_sha256": m.group(2),
            "rows": rows, "text": text}, errors


def load_exemptions(path=EXEMPTIONS, today=None):
    today = today or datetime.date.today().isoformat()
    if not os.path.isfile(path):
        return None, ["豁免清单缺失：%s" % path]
    rows = []
    errors = []
    seen = set()
    with open(path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.rstrip("\n")
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) != 5:
                errors.append("%s:%d 列数=%d，应为 5" % (path, lineno, len(parts)))
                continue
            mid, kind, reason, expires, condition = parts
            if kind not in ("equivalent", "deferred"):
                errors.append("%s:%d kind=%s 非法（应为 equivalent/deferred）"
                              % (path, lineno, kind))
            if not reason.strip():
                errors.append("%s:%d 缺理由" % (path, lineno))
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", expires):
                errors.append("%s:%d expires=%s 非 YYYY-MM-DD" % (path, lineno, expires))
            elif expires < today:
                errors.append("%s:%d 豁免已到期（%s）" % (path, lineno, expires))
            if mid in seen:
                errors.append("%s:%d 豁免重复：%s" % (path, lineno, mid))
            seen.add(mid)
            rows.append({"mutant": mid, "kind": kind, "reason": reason,
                         "expires": expires, "condition": condition})
    return {"rows": rows}, errors


def run(cmd, cwd, timeout=180):
    p = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, timeout=timeout)
    return p.returncode, p.stdout.decode("utf-8", "replace")


def copy_tree(root, name):
    d = os.path.join(root, name)
    shutil.copytree(KEEL, os.path.join(d, "keel"))
    return d


def case_ids(cases):
    return ",".join(sorted(cases.split(","), key=lambda x: int(x)))


def run_case_subset(d, cases):
    return run([PY, os.path.join(d, "keel/checks/test-lint.py"),
                "--only", case_ids(cases)], cwd=d)


def baseline(root, sites):
    union = sorted({c for s in sites for c in s["cases"].split(",")}, key=lambda x: int(x))
    d = copy_tree(root, "baseline")
    rc, out = run_case_subset(d, ",".join(union))
    fails = FAIL_RE.findall(out)
    if rc != 0 or fails:
        return False, "未变异基线不绿：rc=%d fails=%s\n%s" % (rc, fails, out[-600:])
    return True, "基线 %d 例全绿" % len(union)


def one_mutant(root, m):
    d = copy_tree(root, m["id"])
    path = os.path.join(d, "keel", m["target"])
    text = read(path)
    if text.count(m["old"]) != 1:
        return {"id": m["id"], "site": m["site"], "ref": m["ref"],
                "operator": m["operator"], "cases": m["cases"],
                "status": "invalid", "by": [], "rc": None,
                "detail": "变异锚点命中 %d 次（应为 1）" % text.count(m["old"])}
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text.replace(m["old"], m["new"], 1))
    rc, out = run_case_subset(d, m["cases"])
    fails = FAIL_RE.findall(out)
    want = set(m["cases"].split(","))
    hit = [c for c in fails if c in want]
    killed = rc != 0 and bool(hit)
    return {"id": m["id"], "site": m["site"], "ref": m["ref"],
            "operator": m["operator"], "cases": m["cases"],
            "status": "killed" if killed else "survived",
            "by": hit, "rc": rc,
            "detail": "" if killed else
                      ("用例仍绿（变异体存活）" if rc == 0 else
                       "变红但不是目标用例：%s" % fails)}


def summarize(results, mutants, exemptions):
    """从逐条结果推导每条判据与总数；任何不一致都进 errors。"""
    errors = []
    ex = {e["mutant"]: e for e in exemptions["rows"]}
    ids = {m["id"] for m in mutants["rows"]}
    for mid, e in ex.items():
        if mid not in ids:
            errors.append("豁免引用了不存在的变异体：%s" % mid)
    per = {}
    for m in mutants["rows"]:
        per.setdefault(m["ref"], {"total": 0, "killed": 0, "survived": 0,
                                  "equivalent": 0, "exempt": 0, "invalid": 0,
                                  "evidence": []})
        c = per[m["ref"]]
        c["total"] += 1
    for r in results:
        c = per[r["ref"]]
        if r["status"] == "invalid":
            c["invalid"] += 1
            if r["id"] in ex:
                errors.append("无效变异体不得豁免：%s" % r["id"])
        elif r["status"] == "killed":
            c["killed"] += 1
            if r["id"] in ex and ex[r["id"]]["kind"] == "equivalent":
                errors.append("已杀变异体 %s 被声明为等价（矛盾）" % r["id"])
        else:
            c["survived"] += 1
            if r["id"] not in ex:
                errors.append("存活变异体未豁免：%s %s" % (r["id"], r["detail"]))
        if r["id"] in ex:
            if ex[r["id"]]["kind"] == "equivalent":
                c["equivalent"] += 1
            else:
                c["exempt"] += 1
    for ref, c in per.items():
        if c["invalid"]:
            status = "INVALID"
        elif c["survived"] > c["equivalent"] + c["exempt"]:
            status = "SURVIVED"
        elif c["equivalent"] + c["exempt"]:
            status = "EXEMPT"
        elif c["total"] and c["killed"] == c["total"]:
            status = "PASS"
        else:
            status = "NONE"
        c["status"] = status
        c["evidence"] = ",".join("%s:%s" % (r["id"], r["status"])
                                 for r in results if r["ref"] == ref)
    totals = {
        "mutants": len(mutants["rows"]),
        "killed": sum(c["killed"] for c in per.values()),
        "survived": sum(c["survived"] for c in per.values()),
        "equivalent": sum(c["equivalent"] for c in per.values()),
        "exempt": sum(c["exempt"] for c in per.values()),
        "invalid": sum(c["invalid"] for c in per.values()),
    }
    totals["score_denominator"] = totals["mutants"] - totals["equivalent"]
    totals["score_pct"] = (round(totals["killed"] * 100.0 / totals["score_denominator"], 1)
                           if totals["score_denominator"] else 0.0)
    return per, totals, errors


def run_all(sites, jobs, out_path=None, committed=None, report_path=None):
    ops = load_operators()
    enum = enumerate_mutants(sites, ops)
    if enum["errors"]:
        for e in enum["errors"]:
            print("❌ " + e)
        return None, enum["errors"]
    ex, ex_errors = load_exemptions()
    if ex_errors:
        for e in ex_errors:
            print("❌ " + e)
        return None, ex_errors
    root = tempfile.mkdtemp(prefix="keel-mut-")
    t0 = time.time()
    print("判据变异引擎 · 变异体 %d · 判据 %d · 算子 %s · 并行 %d"
          % (len(enum["rows"]), len({m["ref"] for m in enum["rows"]}),
             "、".join(sorted({m["operator"] for m in enum["rows"]})), jobs))
    print("=" * 78)
    try:
        ok, msg = baseline(root, enum["rows"])
        print("· " + msg)
        if not ok:
            return None, ["基线自检失败：" + msg]
        results = []
        with futures.ThreadPoolExecutor(max_workers=jobs) as pool:
            for r in pool.map(lambda m: one_mutant(root, m), enum["rows"]):
                results.append(r)
                mark = {"killed": "KILLED", "survived": "SURVIVED", "invalid": "INVALID"}[r["status"]]
                extra = ("by %s" % ",".join(r["by"])) if r["by"] else r["detail"]
                print("[%-8s] %s %-8s %-15s %s"
                      % (mark, r["id"], r["ref"], r["operator"], extra))
    finally:
        shutil.rmtree(root, ignore_errors=True)
    duration = round(time.time() - t0, 1)
    per, totals, errors = summarize(results, enum, ex)
    print("=" * 78)
    print("变异得分：%d/%d 被杀（%.1f%%）· 存活 %d · 等价 %d · 豁免 %d · 无效 %d · %.1fs @ %d 并行"
          % (totals["killed"], totals["score_denominator"], totals["score_pct"],
             totals["survived"], totals["equivalent"], totals["exempt"],
             totals["invalid"], duration, jobs))
    for e in errors:
        print("❌ " + e)
    payload = {
        "schema": 2,
        "generated_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "engine": "operators.py v1",
        "operators": sorted(ops.OPERATORS),
        "jobs": jobs,
        "duration_s": duration,
        "targets": enum["targets"],
        "manifest_sha256": enum["manifest_sha256"],
        "totals": totals,
        "criteria": [{"id": k, "mutants": v["total"], "killed": v["killed"],
                      "survived": v["survived"], "equivalent": v["equivalent"],
                      "exempt": v["exempt"], "invalid": v["invalid"],
                      "status": v["status"], "evidence": v["evidence"]}
                     for k, v in sorted(per.items())],
        "mutants": results,
        "exemptions": ex["rows"],
        "selected": sorted({m["ref"] for m in enum["rows"]}),
        "excluded": [{"ref": r, "reason": why} for r, why in EXCLUDED],
        "boundary": "抓不到接线错、跨文件/跨版本行为；低分是结论，但不许为抬分删除位点",
    }
    bad = bool(errors)
    if committed is not None:
        drift = compare_results(payload, committed)
        for d in drift:
            print("❌ " + d)
        errors += drift
        bad = bad or bool(drift)
    if out_path:
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        print("   结果已写入：%s" % out_path)
    if report_path:
        write_report(payload, report_path, jobs)
    return payload, (errors if bad else [])


def canonical(results):
    """可复算投影：剔除时间/耗时/并行度，保留结论与证据。"""
    return {
        "manifest_sha256": results.get("manifest_sha256"),
        "targets": results.get("targets"),
        "totals": results.get("totals"),
        "criteria": results.get("criteria"),
        "mutants": sorted(
            [{k: r.get(k) for k in ("id", "ref", "operator", "cases", "status", "by", "rc")}
             for r in results.get("mutants", [])], key=lambda x: x["id"]),
        "exemptions": results.get("exemptions"),
    }


def compare_results(actual, claimed):
    a = canonical(actual)
    c = canonical(claimed)
    out = []
    for key in ("manifest_sha256", "targets", "totals", "criteria", "mutants", "exemptions"):
        if a[key] != c[key]:
            if key == "mutants":
                ids = sorted({m["id"] for m in a[key]} | {m["id"] for m in c[key]})
                diff = [i for i in ids
                        if next((m for m in a[key] if m["id"] == i), None)
                        != next((m for m in c[key] if m["id"] == i), None)]
                out.append("逐变异体结果与已提交不一致：%s" % ",".join(diff[:6]))
            elif key == "criteria":
                out.append("每条判据的变异计数与已提交不一致")
            elif key == "totals":
                out.append("总数与逐条结果推导不一致：实际 %s / 声明 %s"
                           % (json.dumps(a[key], ensure_ascii=False, sort_keys=True),
                              json.dumps(c[key], ensure_ascii=False, sort_keys=True)))
            else:
                out.append("%s 与已提交不一致" % key)
    return out


def verify_data(enum, mutants, exemptions, results):
    """门禁用的秒级自洽校验（不重跑）。"""
    errors = []
    if enum["errors"]:
        errors.extend(enum["errors"])
    if enum["text"] != mutants["text"]:
        errors.append("mutants.tsv 与重新枚举不一致（清单漂移；先跑 --regen-mutants）")
    if results is None:
        return ["结果缺失：%s（先跑 --run）" % RESULTS]
    if results.get("manifest_sha256") != enum["manifest_sha256"]:
        errors.append("结果绑定的 manifest_sha256 与当前清单不一致")
    for target, sha in enum["targets"].items():
        if (results.get("targets") or {}).get(target) != sha:
            errors.append("结果绑定的 %s sha256 与当前脚本不一致" % target)
    rid = {r["id"] for r in results.get("mutants", [])}
    mid = {m["id"] for m in mutants["rows"]}
    if rid != mid:
        errors.append("结果覆盖的变异体集合与清单不一致（缺 %d / 多 %d）"
                      % (len(mid - rid), len(rid - mid)))
    per, totals, sum_errors = summarize(results.get("mutants", []), mutants, exemptions)
    errors.extend(sum_errors)
    if results.get("totals") != totals:
        errors.append("results.totals 与逐条结果推导不一致（不许写死总数）")
    claimed = {c["id"]: c for c in results.get("criteria", [])}
    for ref, c in per.items():
        got = claimed.get(ref)
        want = {"mutants": c["total"], "killed": c["killed"],
                "survived": c["survived"], "equivalent": c["equivalent"],
                "exempt": c["exempt"], "invalid": c["invalid"],
                "status": c["status"]}
        got2 = None if got is None else {k: got.get(k) for k in want}
        if got2 != want:
            errors.append("%s 的变异计数与逐条结果不一致（清单/结果被写死或漂移）" % ref)
    for ref in claimed:
        if ref not in per:
            errors.append("结果声明了清单里没有的判据：%s" % ref)
    return errors


def write_report(payload, path, jobs):
    """对外复核包：结果 + 复算入口 + 期望哈希/数字。脚本可逐项比对，不是散文。"""
    rep = json.loads(json.dumps(payload))
    rep["report_schema"] = "keel-mutation-report v1"
    rep["reproduce"] = {
        "enumerate": "python3 keel/checks/mutation/mutation.py --enumerate",
        "verify": "python3 keel/checks/mutation/mutation.py --verify",
        "recompute": "python3 keel/checks/mutation/mutation.py --recompute --jobs %d" % jobs,
        "expected_manifest_sha256": payload["manifest_sha256"],
        "expected_targets": payload["targets"],
        "expected_totals": payload["totals"],
        "note": "清单逐字节比对 mutants.tsv；结果按 id/status/by/rc 逐条比对，忽略耗时与并行度",
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(rep, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("   对外报告已写入：%s" % path)


def check_report(enum, results, path=REPORT):
    if not os.path.isfile(path):
        return ["对外报告缺失：%s（跑 --run --report %s）" % (path, path)]
    try:
        with open(path, encoding="utf-8") as fh:
            rep = json.load(fh)
    except (OSError, ValueError) as e:
        return ["对外报告无法解析：%s" % e]
    errors = []
    if rep.get("report_schema") != "keel-mutation-report v1":
        errors.append("对外报告 schema 非法")
    if rep.get("manifest_sha256") != enum["manifest_sha256"]:
        errors.append("对外报告的 manifest_sha256 与当前清单不一致")
    if rep.get("totals") != results.get("totals"):
        errors.append("对外报告的总数与 results.json 不一致")
    a = {m["id"]: m["status"] for m in rep.get("mutants", [])}
    b = {m["id"]: m["status"] for m in results.get("mutants", [])}
    if a != b:
        errors.append("对外报告的逐变异体状态与 results.json 不一致")
    return errors


def load_results(path=RESULTS):
    if not os.path.isfile(path):
        return None, ["结果缺失：%s（先跑 --run）" % path]
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh), []
    except (OSError, ValueError) as e:
        return None, ["结果无法解析：%s" % e]


def print_recompute(payload, committed, duration, jobs):
    print("复算清单 sha256 = %s" % payload["manifest_sha256"])
    for t, sha in payload["targets"].items():
        print("  %s sha256 = %s" % (t, sha))
    print("实测：%d 变异体 / %d 杀 / %d 存活 / %d 等价 / %d 豁免 / %d 无效 · %.1fs @ %d 并行"
          % (payload["totals"]["mutants"], payload["totals"]["killed"],
             payload["totals"]["survived"], payload["totals"]["equivalent"],
             payload["totals"]["exempt"], payload["totals"]["invalid"],
             payload["duration_s"], jobs))
    drift = compare_results(payload, committed) if committed else []
    for d in drift:
        print("❌ " + d)
    if not drift:
        print("结论：复算与已提交 results.json 一致（rc=0）")


def negctl():
    """三条负控必须真判死。返回 (killed, total)。"""
    results = []

    def run_case(name, cond, detail=""):
        ok = bool(cond)
        results.append((name, ok, detail))
        print("[%s] %s%s" % ("KILLED" if ok else "SURVIVED", name,
                            ("：" + detail) if detail else ""))

    # 1) 把已杀变异体声明为等价。
    enum = enumerate_mutants(parse_sites())
    muts, _ = load_mutants()
    res, _ = load_results()
    ex, _ = load_exemptions()
    if res and muts and ex:
        killed = next(r for r in res["mutants"] if r["status"] == "killed")
        bad = {"rows": list(ex["rows"]) + [{
            "mutant": killed["id"], "kind": "equivalent",
            "reason": "负控：人为声明已杀体为等价",
            "expires": datetime.date.today().isoformat(), "condition": "-"}]}
        errs = verify_data(enum, muts, bad, res)
        run_case("负控1 已杀变异体被改判等价", any("被声明为等价" in e for e in errs),
                 errs[0] if errs else "未被抓住")
    else:
        run_case("负控1 已杀变异体被改判等价", False, "缺清单/结果/豁免")

    # 2) 某条判据的变异体数量写死：篡改 results 的 totals 与 criteria 计数。
    if res:
        fake = json.loads(json.dumps(res))
        fake["totals"]["mutants"] += 1
        fake["criteria"][0]["mutants"] += 1
        errs = verify_data(enum, muts, ex, fake) if muts and ex else []
        run_case("负控2 判据变异数量被写成常量", any("写死" in e or "推导不一致" in e
                                                   or "不一致" in e for e in errs),
                 errs[0] if errs else "未被抓住")
    else:
        run_case("负控2 判据变异数量被写成常量", False, "缺结果")

    # 3) 把存活报告成已杀：用一个真实会存活的合成位点重跑，再伪造状态。
    sites = parse_sites()
    probe = dict(sites[5])            # S06 死链检查
    probe["cases"] = "00"             # 只跑合法基线 → 删除检查必然存活
    root = tempfile.mkdtemp(prefix="keel-neg-")
    t0 = time.time()
    try:
        ok, msg = baseline(root, [probe])
        if ok:
            enum1 = {"rows": [], "errors": []}
            ops = load_operators()
            occ = read(os.path.join(KEEL, probe["target"]))
            new = ops.apply(probe["operator"], probe["anchor"])
            mid = sha256_text("%s|%s|%s|%s|%s" % (probe["ref"], probe["site"],
                                                  probe["operator"], probe["anchor"], new))[:12]
            row = {"id": mid, "site": probe["site"], "ref": probe["ref"],
                   "operator": probe["operator"], "line": occ[:occ.find(probe["anchor"])].count("\n") + 1,
                   "old": probe["anchor"], "new": new, "cases": "00",
                   "target": probe["target"]}
            got = one_mutant(root, row)
            fake = {"manifest_sha256": "x", "targets": {}, "totals": {},
                    "criteria": [], "mutants": [], "exemptions": []}
            actual = {"manifest_sha256": "x", "targets": {},
                      "totals": {"mutants": 1, "killed": 0, "survived": 1,
                                 "equivalent": 0, "exempt": 0, "invalid": 0,
                                 "score_denominator": 1, "score_pct": 0.0},
                      "criteria": [], "exemptions": [],
                      "mutants": [got]}
            forged = json.loads(json.dumps(actual))
            forged["totals"].update({"killed": 1, "survived": 0, "score_pct": 100.0})
            forged["mutants"][0]["status"] = "killed"
            forged["mutants"][0]["by"] = ["00"]
            drift = compare_results(actual, forged)
            run_case("负控3 存活被报告成已杀", got["status"] == "survived" and bool(drift),
                     (drift[0] if drift else "伪造结果未被复算抓住"))
        else:
            run_case("负控3 存活被报告成已杀", False, msg)
    finally:
        shutil.rmtree(root, ignore_errors=True)
    print("=" * 60)
    killed = sum(1 for _, ok, _ in results if ok)
    print("%s：负控 %d/%d 判死 · %.1fs"
          % ("✅" if killed == len(results) else "❌", killed, len(results),
             time.time() - t0))
    return killed, len(results)


def main():
    ap = argparse.ArgumentParser(description="判据变异引擎")
    ap.add_argument("--enumerate", action="store_true")
    ap.add_argument("--regen-mutants", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--recompute", action="store_true")
    ap.add_argument("--negctl", action="store_true")
    ap.add_argument("--out", default="")
    ap.add_argument("--report", default="")
    ap.add_argument("--jobs", type=int, default=min(8, os.cpu_count() or 1))
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args()

    if a.negctl:
        killed, total = negctl()
        return 0 if killed == total else 1

    sites = parse_sites()

    if a.regen_mutants:
        enum = enumerate_mutants(sites)
        if enum["errors"]:
            for e in enum["errors"]:
                print("❌ " + e, file=sys.stderr)
            return 1
        with open(MUTANTS, "w", encoding="utf-8") as fh:
            fh.write(enum["text"])
        print("已生成 %s（manifest sha256=%s，%d 个变异体）"
              % (MUTANTS, enum["manifest_sha256"], len(enum["rows"])))
        return 0

    if a.enumerate:
        enum = enumerate_mutants(sites)
        if enum["errors"]:
            for e in enum["errors"]:
                print("❌ " + e)
            return 1
        committed, errs = load_mutants()
        if errs:
            for e in errs:
                print("❌ " + e)
            return 1
        print("枚举：%d 个变异体 · 判据 %d · 算子 %s"
              % (len(enum["rows"]), len({m["ref"] for m in enum["rows"]}),
                 "、".join(sorted({m["operator"] for m in enum["rows"]}))))
        print("清单 manifest sha256 = %s" % enum["manifest_sha256"])
        if committed["text"] != enum["text"]:
            print("❌ mutants.tsv 与重新枚举不一致（清单漂移；先跑 --regen-mutants）")
            return 1
        print("✅ 清单与重新枚举逐字节一致")
        return 0

    if a.verify:
        enum = enumerate_mutants(sites)
        muts, merrs = load_mutants()
        ex, exerrs = load_exemptions()
        res, rerrs = load_results()
        errors = enum["errors"] + merrs + exerrs + rerrs
        if muts and ex and res and not errors:
            errors += verify_data(enum, muts, ex, res)
            errors += check_report(enum, res)
        for e in errors:
            print("❌ " + e)
        if not errors:
            print("✅ 变异清单/结果/豁免自洽（manifest %s）" % enum["manifest_sha256"])
        return 1 if errors else 0

    if a.recompute:
        enum = enumerate_mutants(sites)
        if enum["errors"]:
            for e in enum["errors"]:
                print("❌ " + e)
            return 1
        committed, errs = load_mutants()
        if errs:
            for e in errs:
                print("❌ " + e)
            return 1
        if committed["text"] != enum["text"]:
            print("❌ mutants.tsv 与重新枚举不一致（先跑 --regen-mutants）")
            return 1
        res, rerrs = load_results()
        payload, errors = run_all(sites, a.jobs, out_path=a.out or None,
                                  committed=res if res else None,
                                  report_path=a.report or None)
        if payload is None:
            return 2
        print_recompute(payload, res, payload["duration_s"], a.jobs)
        return 0 if not errors else 1

    # 默认 = --run（verify.py 的历史调用方式）
    payload, errors = run_all(sites, a.jobs, out_path=a.out or None,
                              report_path=a.report or None)
    return 0 if payload is not None and not errors else (2 if payload is None else 1)


if __name__ == "__main__":
    sys.exit(main())
