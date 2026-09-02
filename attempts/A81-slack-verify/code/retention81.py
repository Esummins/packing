#!/usr/bin/env python
# -*- coding: ascii -*-
"""retention81.py -- A81 T1 analysis: per-level frontier retention r(d) = split(d) /
(2 split(d-1)) of hintbatch81 hole/summary files, against the A77 corners4 reference
(Lemma W'''), and the implied complete-tree size law.

    python code\retention81.py results/hb_md1_full.json [more.json ...] [--ref]
"""
import argparse
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
A77 = os.path.join(HERE, "..", "..", "A77-corners4-close", "results")


def curve(fp):
    d = json.load(open(fp))
    s = d["summary"]
    cd = {int(k): v for k, v in s["census_by_depth"].items()}
    r, sp = {}, {}
    for dd in sorted(cd):
        sp[dd] = cd[dd].get("split", 0)
        if dd - 1 in cd and cd[dd - 1].get("split", 0) > 0:
            r[dd] = cd[dd].get("split", 0) / (2.0 * cd[dd - 1]["split"])
    return s, cd, sp, r


def geo_mean(vals):
    vals = [v for v in vals if v > 0]
    return math.exp(sum(math.log(v) for v in vals) / len(vals)) if vals else float("nan")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--lo", type=int, default=8)
    ap.add_argument("--hi", type=int, default=25)
    ap.add_argument("--extra_levels", type=int, default=20,
                    help="levels beyond the measured frontier to the W'' atom-depth scale")
    args = ap.parse_args()
    refs = [("A77 corners4 md8 root 2,11 (rule certain, 1.59M)", os.path.join(A77, "deep_40_2M.json")),
            ("A77 corners4 md8 all roots cap 60k", os.path.join(A77, "hb_md8.json"))]
    rows = []
    for name, fp in refs + [(os.path.basename(f), f) for f in args.files]:
        if not os.path.exists(fp):
            continue
        s, cd, sp, r = curve(fp)
        win = [r[d] for d in range(args.lo, args.hi + 1) if d in r and sp.get(d, 0) >= 32]
        # budget-truncated levels (budget_hit) show as r -> 0; keep only levels whose
        # parent frontier was fully expanded: sp[d] > 0 and the level is before the
        # first level where opens dominate (heuristic: r > 0.05)
        win = [v for v in win if v > 0.05]
        gm = geo_mean(win)
        last = max((d for d in sp if sp[d] > 0), default=0)
        front = cd.get(last, {})
        opens = sum(v.get("open", 0) + v.get("amb", 0) for v in cd.values())
        # frontier growth per level = 2 r (each open box splits into two children of which
        # a fraction r stay undecided): nodes to e more levels ~ opens * sum_{i<=e} (2r)^i
        est = (opens * sum((2 * gm) ** i for i in range(1, args.extra_levels + 1))) if gm == gm else float("nan")
        rows.append((name, s["nodes"], s["roots"], s["census"], last, gm, win, opens, est))
        print("== %s" % name)
        print("   nodes=%d roots=%d census=%s" % (s["nodes"], s["roots"], json.dumps(s["census"])))
        print("   split(d): %s" % {d: sp[d] for d in sorted(sp) if sp[d] > 0})
        print("   r(d):     %s" % {d: round(r[d], 3) for d in sorted(r)})
        print("   r geo-mean over d in [%d,%d] (expanded levels): %.3f over %d levels; opens=%d; "
              "nodes for %d more levels at growth 2r = %.3g" % (args.lo, args.hi, gm, len(win), opens, args.extra_levels, est))
    print("\n| tree | nodes | roots | last split depth | r(d) geo-mean [%d,%d] | opens | nodes for %d more levels (x(2r)^e) |"
          % (args.lo, args.hi, args.extra_levels))
    print("|---|---|---|---|---|---|---|")
    for (name, nodes, roots, cen, last, gm, win, opens, est) in rows:
        print("| %s | %d | %d | %d | %.3f (%d levels) | %d | %.2g |"
              % (name, nodes, roots, last, gm, len(win), opens, est))


if __name__ == "__main__":
    main()
