"""A158 probe -- price the YES child on one (node, slot) over a ladder of S radii.

For each radius r and each tilt piece of S it reports the sampled LOWER bounds that can REFUTE
the YES kill outright (a realised free meeter clear of K'(S), or a conditioned square that can
still meet the cell clear of K'(S)), and the geometry of K'(S) itself.

    python probe158.py --nid c0_Y0076 --slot "TL(0,0)" --radii 0.05,0.1,0.15 --n 400000
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


def load_rec(nid):
    for cand in (os.path.join(BASE, "results", "recs158.json"),
                 os.path.join(BASE, "..", "A157-undecided-slots", "results", "recs157.json")):
        if os.path.exists(cand):
            d = json.load(open(cand, encoding="utf-8"))
            if nid in d:
                return d[nid]
    recs = {r["nid"]: r for r in SL.CP.load_nodes()}
    return recs[nid]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nid", default="c0_Y0076")
    ap.add_argument("--slot", default="TL(0,0)")
    ap.add_argument("--radii", default="0.05,0.10,0.15")
    ap.add_argument("--tilts", default="10,15")
    ap.add_argument("--n", type=int, default=400000)
    ap.add_argument("--nm", type=int, default=200000)
    ap.add_argument("--out", default=os.path.join(BASE, "results", "probe158.json"))
    a = ap.parse_args()

    rec = load_rec(a.nid)
    conds, meet, cell, (c, i, j) = SL.build_node(rec, a.slot)
    rng = np.random.default_rng(158)
    out = dict(nid=a.nid, slot=a.slot, cls=rec["cls"], src=rec["src"], level=rec.get("level"),
               cell=list(cell), corner=c, ij=[i, j], n_pins=len(conds) - len(meet),
               meeters=meet, cond_boxes=[SL.P.box_json(x.box) for x in conds], rows=[])
    base = SL.screen_conditional(conds, cell, rng, a.n)
    base_m = SL.screen_cond_meet(conds, meet, cell, rng, a.nm)
    out["baseline"] = dict(screen=base, M=base_m)
    print("BASELINE (A141/A157, no S): free %d/%d meeting, lane_lb %d, M_lb %d"
          % (base.get("free", 0), base.get("meeting", 0), base["lane_lb"], base_m["M_lb"]),
          flush=True)
    if base.get("free_pose"):
        print("  best free pose %s clearance %.6e" % (base["free_pose"], base["clearance"]),
              flush=True)

    for r in [float(v) for v in a.radii.split(",")]:
        for tt in [float(v) for v in a.tilts.split(",")]:
            for piece in (0, 1):
                t0 = time.time()
                cs, sq = SL.add_s(conds, i, j, r, tt, piece)
                sc = SL.screen_conditional(cs, cell, rng, a.n)
                sm = SL.screen_cond_meet(cs, meet, cell, rng, a.nm)
                row = dict(r=r, tt=tt, piece=piece,
                           S_box=SL.P.box_json(sq.box), S_core_verts=len(sq.pc.verts),
                           S_core_area=float(sq.pc.area()),
                           screen=sc, M=sm,
                           yes_refuted=bool(sc["lane_lb"] >= 1 or sm["M_lb"] >= 1),
                           secs=round(time.time() - t0, 1))
                out["rows"].append(row)
                print("r=%.3f tt=%.0f piece=%d  K'(S) area %.5f verts %d | free %d (lane_lb %d) "
                      "M_lb %d -> %s  [%.1fs]"
                      % (r, tt, piece, row["S_core_area"], row["S_core_verts"],
                         sc.get("free", 0), sc["lane_lb"], sm["M_lb"],
                         "YES-REFUTED" if row["yes_refuted"] else "yes-still-possible",
                         row["secs"]), flush=True)
                if sc.get("free_pose"):
                    print("    free pose %s clearance %.6e"
                          % ([round(v, 6) for v in sc["free_pose"]], sc["clearance"]), flush=True)
    json.dump(out, open(a.out, "w", encoding="utf-8"), indent=1)
    print("wrote", a.out, flush=True)


if __name__ == "__main__":
    main()
