"""
A60 / G-A60-2, the CORRECT route for the outer three squares.

The zone-cover route fails for sq4 / sq6 / sq10 and fails STRUCTURALLY, not for want of compute:
with j squares conditioned, budget = 6 - j - 1 for a YES child and only 6 - j Trump witnesses
survive, so a cover box that knocks out exactly ONE survivor has k = budget and is ALIVE-CERTIFIED
unkillable (Lemma A57-3).  In the crowded interior almost every box reaches TWO of Trump's squares
and therefore dies; in a side zone almost nothing does.  Measured: side_R at j = 3 has 0
attemptable boxes out of 444, and its 19-box residue diverges under refinement (19 -> 1780 by
level 12, max containment stuck at 0.407).  No amount of bisection helps.

The route that works is the one A59's P4 already prescribes from j >= 2: **confinement**.  Add a
NO-family around Trump's placement instead of a YES core.  The NO-family swallows that witness,
so k drops by one while the budget does NOT (a NO child keeps the parent budget), which is exactly
the margin the cover route can never buy.  The pilot measured PASS at j = 2, 3, 4, 5.

    python code\confine60.py --sq sq10 --a 0.3,0.15,0.075 --lp_time 300
"""
import argparse, json, math, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import tree60 as T
from tree60 import Sink, kill, gate, TSC, RES, PROG, logline
from caselp import Box, NoFam, Hyp
from alive59 import alive_verdict
from pilot59 import PINS, SLOTS, FREE, init_warm
from sidezones60 import interior_triple


def no_fam(name, a):
    """NO-family: no square centred within sup-norm radius a of Trump's placement `name`."""
    from pilot59 import rq, tbox_deg
    cx, cy, th = FREE[name]
    t = math.tan(th / 2.0)
    at = TSC * a
    th0, th1 = tbox_deg(t - at, t + at)
    return NoFam(rq(cx - a), rq(cx + a), rq(cy - a), rq(cy + a), [(th0, th1)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sq", default="sq10")
    ap.add_argument("--a", default="0.3,0.15,0.075")
    ap.add_argument("--lp_time", type=float, default=300.0)
    ap.add_argument("--cert_time", type=float, default=240.0)
    ap.add_argument("--full_theta", action="store_true",
                    help="NO-family over all tilts (centre-only confinement)")
    a = ap.parse_args()
    cond, names = interior_triple()
    j = len(cond)
    budget = 6 - j                      # a NO child KEEPS the parent budget
    sink = Sink("a60_confine_j%d.jsonl" % j, "confine_j%d.log" % j)
    init_warm()
    prog = os.path.join(PROG, "confine_j%d_%s.json" % (j, a.sq))
    st = dict(phase="confine", j=j, cond=names, sq=a.sq, budget=budget, done=0, passed=0,
              failed=0, alive=0, started=time.strftime("%Y-%m-%d %H:%M:%S"), rows=[])
    t0 = time.time()
    logline("A60 confinement j=%d cond=%s sq=%s budget=%d" % (j, names, a.sq, budget))
    for av in [float(v) for v in a.a.split(",")]:
        if a.full_theta:
            from pilot59 import rq
            cx, cy, _ = FREE[a.sq]
            fam = NoFam(rq(cx - av), rq(cx + av), rq(cy - av), rq(cy + av), [(0.0, 90.0)])
            mark = "ft"
        else:
            fam = no_fam(a.sq, av)
            mark = "tw"
        hyp = Hyp(PINS + cond, [fam])
        k = alive_verdict(hyp, budget)
        tag = "conf60_%s_a%g_%s" % (a.sq, av, mark)
        logline("  %s: k=%d budget=%d -> %s" % (tag, k["k"], budget,
                "attemptable" if not k["unkillable"] else "ALIVE (skip)"))
        row = dict(tag=tag, sq=a.sq, a=av, k=k["k"], budget=budget,
                   witnesses=k["witness_family"], unkillable=k["unkillable"])
        if not k["unkillable"]:
            rec = kill(sink, tag, None, cond, [fam], budget,
                       dict(kind="NO-confine", depth_j=j, a=av, at=(None if a.full_theta else TSC * av),
                            pinguard="ok", cond=list(names), k=k["k"]),
                       lp_time=a.lp_time, cert_time=a.cert_time)
            v = (rec or {}).get("verdict", "")
            row.update(verdict=v, tau=(rec or {}).get("tau"), lp_s=(rec or {}).get("lp_s"),
                       cert_s=(rec or {}).get("cert_s"))
            st["passed"] += 1 if v == "PASS" else 0
            st["failed"] += 1 if v.startswith("FAIL") else 0
            st["alive"] += 1 if v.startswith("refused") else 0
        st["rows"].append(row)
        st["done"] += 1
        st["elapsed_s"] = round(time.time() - t0, 1)
        json.dump(st, open(prog, "w"), indent=1)
        logline("  " + json.dumps(row))
    st["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    json.dump(st, open(prog, "w"), indent=1)
    print(json.dumps(st, indent=1))


if __name__ == "__main__":
    main()
