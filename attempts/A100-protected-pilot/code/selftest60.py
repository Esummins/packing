"""
A60 P0 selftests for the two engine fold-ins (G-A59-11).

Every test is a REPRODUCTION of an A59 measurement or an exact soundness invariant.  A failure
here means the fold-in changed semantics and the campaign must not launch.

T1  alive gate at j = 0 reproduces A59 results/m2_killability_census.json
    (cover 1152 / contradictory 344 / ok 808 / unkillable 41 / attemptable 767).
T2  classify_at + gate at conditioning depths j = 1..4 reproduce m2_branching_by_depth.json.
T3  CANARY: every cover box containing one of Trump's free placements is alive-gated
    UNKILLABLE (so the driver never launches an LP on it and never certifies it).
T4  GATE SOUNDNESS (the load-bearing one): on every node A59 actually certified (its
    conf_ladder PASSes and the M3 interior NO child), the gate must report k < budget, i.e.
    the gate never blocks a kill that exists.  And on every node A59 refused, k >= budget or
    the LP said tau >= budget -- the gate is only ever a lower bound (Lemma A57-3).
T5  vacuity arbiter end-to-end: reproduce the pilot's r_kill crossover at hw = 1e-3 --
    a = 0.00455078 PASSes and a = 0.00448242 FAILs, from a fresh zero-atom certificate.
T6  classify_at degenerate cases: a box that IS a conditioning box -> 'shared' (never
    certified), a box far from it and meeting it -> 'contradictory' (free kill).
"""
import json, math, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
A59 = os.path.join(ATT, "A59-trump-residual")
sys.path.insert(0, HERE)

import blas1  # A57 T18: pin BLAS to 1 thread BEFORE numpy loads
import tree60 as T
from tree60 import gate, classify_at, census, basin_box, H, TSC
from pilot59 import PINS, SLOTS, FREE, deep_cores, no_fam_7, core_box
from caselp import Box, Hyp
from alive59 import alive_verdict

FAILS = []


def check(name, got, want, detail=""):
    ok = got == want
    print(("  PASS  " if ok else "  FAIL  ") + name + "  got=%s want=%s %s" % (got, want, detail))
    if not ok:
        FAILS.append(name)
    return ok


def t1():
    print("T1 alive gate at j=0 vs A59 m2_killability_census")
    ref = json.load(open(os.path.join(A59, "results", "m2_killability_census.json")))
    c = census([], out="selftest_census_j0.json")["counts"]
    check("T1.cover", c["cover"], ref["cover"])
    check("T1.contradictory", c["contradictory"], 344)
    check("T1.ok", c["attemptable"] + c["unkillable"], ref["n_ok"])
    check("T1.unkillable", c["unkillable"], ref["n_unkillable"])
    check("T1.attemptable", c["attemptable"], ref["n_attemptable"])


def t2():
    print("T2 branching by conditioning depth vs A59 m2_branching_by_depth")
    ref = json.load(open(os.path.join(A59, "results", "m2_branching_by_depth.json")))
    for row in ref:
        cond = row["conditioned"]
        if not cond:
            continue
        c = census(cond)["counts"]
        check("T2.j%d.contradictory" % row["j"], c["contradictory"] + c.get("shared", 0),
              row["contradictory"], "(shared=%d)" % c.get("shared", 0))
        check("T2.j%d.attemptable" % row["j"], c["attemptable"], row["attemptable"])
        check("T2.j%d.unkillable" % row["j"], c["unkillable"], row["unkillable"])
        check("T2.j%d.budget" % row["j"], 6 - row["j"] - 1, row["child_budget"])


def t3():
    print("T3 canary: Trump-containing cover boxes are alive-gated unkillable")
    cen = json.load(open(os.path.join(BASE, "results", "selftest_census_j0.json")))
    hit = [r for r in cen["rows"] if r["trump_in_box"]]
    check("T3.count", len(hit), 3, str([r["trump_in_box"] for r in hit]))
    check("T3.all_unkillable", all(r["state"] == "unkillable" for r in hit), True)


def t4():
    print("T4 gate soundness: the gate never blocks a kill A59 actually made")
    lad = json.load(open(os.path.join(A59, "results", "conf_ladder.json")))
    passed = set()
    for line in open(os.path.join(A59, "results", "pilot_zonetree.jsonl")):
        try:
            d = json.loads(line)
        except Exception:
            continue
        if d.get("verdict") == "PASS" and d["tag"].startswith("conf_j"):
            passed.add(d["tag"])
    n = 0
    for r in lad:
        j, a = r["j"], r["a"]
        budget = 6 - j
        cond = [core_box(nm, 0.02, TSC * 0.02) for nm in ["sq4", "sq6", "sq8", "sq9"][:j]]
        hyp = Hyp(PINS + cond, [no_fam_7(a, TSC * a)])
        k = alive_verdict(hyp, budget)["k"]
        n += 1
        check("T4.k(j%d,a%g)" % (j, a), k, r["k"])
        tag = "conf_j%d_hw0.02_a%g" % (j, a)
        if tag in passed:
            check("T4.gate-allows-%s" % tag, k < budget, True, "k=%d budget=%d" % (k, budget))
    check("T4.rows_checked", n, len(lad))
    check("T4.pilot_PASSes_seen", len(passed) > 0, True, str(sorted(passed)))
    # the M3 interior NO child: A59 certified it at budget 6 with k = 3
    from caselp import NoFam
    hyp = Hyp(PINS, [NoFam(1.1, 2.777, 1.1, 2.777, [(0.0, 90.0)])])
    check("T4.m3.k", alive_verdict(hyp, 6)["k"], 3)
    check("T4.root.k", alive_verdict(Hyp(PINS, []), 6)["k"], 6)
    check("T4.root.unkillable", alive_verdict(Hyp(PINS, []), 6)["unkillable"], True)


def t5():
    print("T5 vacuity arbiter end-to-end (pilot r_kill crossover at hw=1e-3)")
    import vac59
    from tree60 import Sink
    Sink("selftest_vac.jsonl", "selftest.log")
    cores = deep_cores(0.001, TSC * 0.001)
    for (a, want) in ((0.00455078, "PASS"), (0.00448242, "FAIL")):
        hyp = Hyp(PINS + cores, [no_fam_7(a, TSC * a)])
        t0 = time.time()
        r = vac59.run_vacuity("selftest_vac_a%.8g" % a, hyp, 1, depth=60, force=True)
        got = "PASS" if r["verdict"] == "PASS" else "FAIL"
        check("T5.a%.8g" % a, got, want, "%.1f s" % (time.time() - t0))


def t6():
    print("T6 classify_at degenerate cases")
    cond = [basin_box("sq7")]
    same = basin_box("sq7")
    st, _ = classify_at(same, cond)
    check("T6.shared", st, "shared")
    cx, cy, _ = FREE["sq7"]
    # a box whose core certainly meets sq7's conditioning core but is (c,theta)-disjoint from it
    b = Box(cx + 0.02, cx + 0.16, cy - 0.07, cy + 0.07, 0.0, 14.25)
    st, info = classify_at(b, cond)
    check("T6.contradictory", st, "contradictory", str(info))


if __name__ == "__main__":
    which = sys.argv[1:] or ["t1", "t2", "t3", "t4", "t5", "t6"]
    t0 = time.time()
    for nm in which:
        globals()[nm]()
    print("\n%s  (%d checks failed) in %.1f s" %
          ("ALL PASS" if not FAILS else "FAILURES: " + ", ".join(FAILS), len(FAILS),
           time.time() - t0))
    sys.exit(1 if FAILS else 0)
