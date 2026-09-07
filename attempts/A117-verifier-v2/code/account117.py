"""A117 T3 -- accounting: the equivalence table, the NO-side re-verification table, the TC leaf
census, and which A112 region-tree kills can now be claimed window-valid.  Read-only; writes
results/accounting.json and notes/accounting.md."""
from __future__ import annotations

import json
import os
import sys
from collections import Counter, defaultdict

os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
RES = os.path.normpath(os.path.join(HERE, "..", "results"))
NOTES = os.path.normpath(os.path.join(HERE, "..", "notes"))


def jload(p, default=None):
    try:
        return json.load(open(p))
    except Exception:
        return default


def jl(p):
    out = []
    if os.path.exists(p):
        for ln in open(p):
            ln = ln.strip()
            if ln:
                out.append(json.loads(ln))
    return out


def region_of(name):
    """the A112/A111 region a NO certificate belongs to."""
    b = name
    for pre in ("canary_m2__a111__", "canary_m2__", "canary__"):
        if b.startswith(pre):
            b = b[len(pre):]
    for sep in ("__S02__", "__S07__", "_m2__", "_v2__", "_m1__"):
        if sep in b:
            return b.split(sep)[0]
    return b


def main():
    eq = jload(os.path.join(RES, "equivalence.json"), {})
    rv = jl(os.path.join(RES, "no_reverify.jsonl"))
    tc = jload(os.path.join(RES, "tc_replay.json"), {})
    sha = open(os.path.join(RES, "frozen.sha256")).read().strip().splitlines()

    # ---------------- T1 equivalence
    eq_rows = eq.get("rows", [])
    eq_tab = [dict(tag=r.get("tag"), cert=os.path.basename(r["cert"]),
                   result=r.get("v1", {}).get("result"),
                   boxes=r.get("v1", {}).get("boxes"),
                   identical=r["identical"], diffs=r["diffs"]) for r in eq_rows]

    # ---------------- T1 NO-side re-verification
    by_res = Counter(r.get("result") for r in rv)
    gained = [r for r in rv if r.get("result") == "PASS"]
    lost = [r for r in rv if r.get("result") == "FAIL" and r["fixed_result"] == "PASS"]
    capped = [r for r in rv if r.get("result") == "CAP"]
    wall_window = sum(r.get("seconds", 0) for r in rv)
    wall_four = sum(r.get("four_side_seconds", 0) for r in rv)
    wall_window_pass = sum(r.get("seconds", 0) for r in gained)
    wall_four_pass = sum(r.get("four_side_seconds", 0) for r in gained)

    # ---------------- which A112 regions become window-valid on the NO side
    per_region = defaultdict(lambda: dict(n=0, passed=0, failed=0, capped=0))
    for r in rv:
        d = per_region[region_of(r["name"])]
        d["n"] += 1
        d["passed" if r.get("result") == "PASS" else
          "failed" if r.get("result") == "FAIL" else "capped"] += 1
    regions_all_pass = sorted(k for k, v in per_region.items()
                              if v["n"] and v["passed"] == v["n"])

    doc = dict(
        frozen=sha,
        t1=dict(equivalence=dict(n=eq.get("n"), identical=eq.get("identical"),
                                 differing=eq.get("differing"),
                                 v1_sha256=eq.get("v1_sha256"), v2_sha256=eq.get("v2_sha256"),
                                 rows=eq_tab),
                reverify=dict(n=len(rv), by_result=dict(by_res),
                              window_valid_kills_gained=len(gained),
                              fixed_PASS_now_window_FAIL=len(lost),
                              capped=len(capped),
                              window_wall_s=round(wall_window, 1),
                              four_side_wall_s=round(wall_four, 1),
                              window_wall_s_on_PASS=round(wall_window_pass, 1),
                              four_side_wall_s_on_PASS=round(wall_four_pass, 1),
                              ratio_window_over_four_sides=(
                                  round(wall_window / wall_four, 3) if wall_four else None),
                              ratio_on_PASS=(round(wall_window_pass / wall_four_pass, 3)
                                             if wall_four_pass else None),
                              per_region={k: v for k, v in sorted(per_region.items())},
                              regions_all_NO_children_window_valid=regions_all_pass)),
        t2=dict(n_fires=tc.get("n_fires"), n_exact_fires=tc.get("n_exact_fires"),
                n_not_reproduced=tc.get("n_not_reproduced"),
                total_sampled_pairs=tc.get("total_sampled_pairs"),
                samples_per_fire=tc.get("samples_per_fire"),
                counterexamples=tc.get("n_sample_counterexamples"),
                worst_sat_gap=tc.get("worst_sat_gap"),
                min_exact_slack=tc.get("min_exact_slack"),
                by_kind=tc.get("by_kind"), a111_census=tc.get("a111_census"),
                side_check=jload(os.path.join(RES, "tc_sidecheck.json"), {}).get("n") and
                {k: jload(os.path.join(RES, "tc_sidecheck.json"), {})[k]
                 for k in ("n", "window_valid", "side_local")},
                lean="statements only ([C]); no new axioms"),
        probe=jl(os.path.join(RES, "no_reverify_probe.jsonl")))
    json.dump(doc, open(os.path.join(RES, "accounting.json"), "w"), indent=1)
    def trim(v):
        if isinstance(v, dict):
            return {k: trim(x) for k, x in v.items() if k not in ("rows", "per_region")}
        if isinstance(v, list):
            return "[%d entries]" % len(v) if len(v) > 4 else v
        return v
    print(json.dumps({k: trim(v) for k, v in doc.items()}, indent=1)[:6000])


if __name__ == "__main__":
    main()
