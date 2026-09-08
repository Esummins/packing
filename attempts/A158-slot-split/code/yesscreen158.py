"""A158 -- the FAST YES-child screen: is the YES kill refuted at the PI's box S(r, tt)?

One 400,000-pose draw per (cell, tilt piece).  A realised free meeter of int C that clears every
node core AND K'(S) is a sound `LANE_K'(C | S) >= 1`; a realised pose of a conditioned box that
meets int C and clears every other core AND K'(S) is a sound `M(C | S) >= 1`.  Either one refutes
`LANE_K'(C | S) = 0 AND M(C | S) = 0`, i.e. the YES kill, WITHOUT any cover.  Only if both come
back 0 is a certifying cover worth buying — and then this script says so.

    python yesscreen158.py --jobs ../results/top158.jsonl --r 0.10 --tt 10
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import slotlib158 as SL  # noqa: E402
import numpy as np  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", default=os.path.join(BASE, "results", "top158.jsonl"))
    ap.add_argument("--recs", default=os.path.join(BASE, "results", "recs158.json"))
    ap.add_argument("--r", type=float, default=0.10)
    ap.add_argument("--tt", type=float, default=10.0)
    ap.add_argument("--n", type=int, default=400000)
    ap.add_argument("--nm", type=int, default=120000)
    ap.add_argument("--out", default=os.path.join(BASE, "results", "yesscreen158.jsonl"))
    ap.add_argument("--budget", type=float, default=2400.0)
    a = ap.parse_args()

    recs = json.load(open(a.recs, encoding="utf-8"))
    jobs = [json.loads(l) for l in open(a.jobs, encoding="utf-8") if l.strip()]
    done = set()
    if os.path.exists(a.out):
        for ln in open(a.out, encoding="utf-8"):
            try:
                d = json.loads(ln)
                done.add((d["nid"], d["slot"], d.get("r"), d.get("tt")))
            except Exception:                                      # noqa: BLE001
                pass
    rng = np.random.default_rng(15801)
    fh = open(a.out, "a", encoding="utf-8")
    t0 = time.time()
    for j in jobs:
        if (j["nid"], j["slot"], a.r, a.tt) in done:
            continue
        if time.time() - t0 > a.budget:
            print("budget reached", flush=True)
            break
        try:
            conds, meet, cell, (c, i, j_) = SL.build_node(recs[j["nid"]], j["slot"])
            row = dict(nid=j["nid"], slot=j["slot"], src=j.get("src"), cls=j.get("cls"),
                       level=j.get("level"), w=j.get("w"), r=a.r, tt=a.tt,
                       n_pins=len(conds) - len(meet), pieces=[])
            for piece in (0, 1):
                cs, sq = SL.add_s(conds, i, j_, a.r, a.tt, piece)
                sc = SL.screen_conditional(cs, cell, rng, a.n)
                sm = SL.screen_cond_meet(cs, meet, cell, rng, a.nm)
                row["pieces"].append(dict(piece=piece, lane_lb=sc["lane_lb"], M_lb=sm["M_lb"],
                                          free=sc.get("free"), meeting=sc.get("meeting"),
                                          clearance=sc.get("clearance"),
                                          free_pose=sc.get("free_pose"),
                                          S_core_area=float(sq.pc.area())))
            row["yes_refuted"] = any(p["lane_lb"] >= 1 or p["M_lb"] >= 1 for p in row["pieces"])
            row["cover_worth_buying"] = not row["yes_refuted"]
        except Exception as e:                                     # noqa: BLE001
            row = dict(nid=j["nid"], slot=j["slot"], r=a.r, tt=a.tt, error=repr(e)[:200])
        fh.write(json.dumps(row) + "\n")
        fh.flush()
        print("%-32s %-9s %s  %s"
              % (j["nid"], j["slot"],
                 " | ".join("p%d lane>=%s M>=%s" % (p["piece"], p["lane_lb"], p["M_lb"])
                            for p in row.get("pieces", [])),
                 "YES-REFUTED" if row.get("yes_refuted") else
                 ("cover worth buying" if row.get("cover_worth_buying") else row.get("error"))),
              flush=True)
    fh.close()
    print("%.0f s" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
