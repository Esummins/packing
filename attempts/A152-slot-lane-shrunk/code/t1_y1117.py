"""A152 T1 -- the focused study of the PI's example, `k5_16_interior_Y1117` slot BR(0,1).

Reproduces A141's exact-cell verdict, then runs the same leaf on
  * the SHRUNK cell (the PI's literal proposal -- diagnostic only), and
  * every ADMISSIBLE TRANSLATE of the cell (the sound form),
under both pin regimes (A141's exact-slot pin cores, and the slack-family fattened ones).

    python t1_y1117.py [--nid k5_16_interior_Y1117] [--slot "BR(0,1)"] [--sample 24000]
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import lane152 as L152                                   # noqa: E402
import numpy as np                                       # noqa: E402
import polylane as P                                     # noqa: E402


def one(rec, slot, pin_h, hs, sample, maxopen, rng, deep=True):
    conds, meet, (i, j), pin_b = L152.build(rec, slot, pin_h)
    ts = L152.admissible_translates(pin_b, i, j, hs, pin_h)
    variants = [("exact", L152.cell_exact(i, j)),
                ("shrunk", L152.cell_shrunk(i, j, hs))]
    for t in ts:
        variants.append(("trans(%+.5f,%+.5f)" % t, L152.cell_trans(i, j, t)))
    rows = []
    for name, cell in variants:
        t0 = time.time()
        sm = L152.screen(cell, conds, rng, sample)
        row = dict(variant=name, cell=list(cell), lane_lb=sm["lane_lb"], M_lb=sm["M_lb"],
                   free=sm.get("free"), meeting=sm.get("meeting"),
                   max_pair_gap=sm.get("max_pair_gap"),
                   witness_pair=sm.get("witness_pair"), free_pose=sm.get("free_pose"))
        if deep and sm["lane_lb"] + sm["M_lb"] <= 1:
            res = L152.full(cell, conds, meet, rng, sample, maxopen, keep_cert=False)
            row.update(lane_ub=res["lane_ub"], M=res["M"], verdict=res["verdict"],
                       cover_leaves=res.get("cover_leaves"), cover_open=res.get("cover_open"))
        else:
            row["verdict"] = ("LANE>=2" if sm["lane_lb"] >= 2 else "NEAR-MISS-OR-WORSE")
        row["seconds"] = round(time.time() - t0, 1)
        rows.append(row)
    return dict(nid=rec["nid"], src=rec["src"], cls=rec["cls"], level=rec["level"], slot=slot,
                pin_h=pin_h, snap_h=hs, i=i, j=j,
                pin_boxes=[[b.x0, b.x1, b.y0, b.y1] for b in pin_b],
                cond_boxes=[P.box_json(c.box) for c in conds if c.idx in meet],
                admissible_translates=[list(t) for t in ts], variants=rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nid", default="k5_16_interior_Y1117")
    ap.add_argument("--slot", default="BR(0,1)")
    ap.add_argument("--sample", type=int, default=24000)
    ap.add_argument("--maxopen", type=int, default=2500)
    ap.add_argument("--out", default=os.path.join(BASE, "results", "t1_y1117.json"))
    a = ap.parse_args()

    recs = {r["nid"]: r for r in L152.alive_records()}
    if a.nid not in recs:
        allr = {r["nid"]: r for r in L152.CP.load_nodes()}
        recs[a.nid] = allr[a.nid]
    rec = recs[a.nid]
    rng = np.random.default_rng(1520)
    slots = (list(L152.CP.CLASSES[rec["cls"]]["usable"].keys()) if a.slot == "all"
             else a.slot.split(";"))
    out = dict(nid=a.nid, slot=a.slot, node_path=rec.get("path"), alive=rec.get("alive"),
               regimes=[])
    for slot in slots:
        for tag, pin_h in (("exact_pins(A141)", 0.0), ("slack_pins(delta=1e-2)",
                                                       L152.node_pin_h(rec))):
            r = one(rec, slot, pin_h, L152.H_G1, a.sample, a.maxopen, rng)
            r["pin_regime"] = tag
            out["regimes"].append(r)
            print("== %s %s  translates=%s" % (slot, tag, r["admissible_translates"]), flush=True)
            for v in r["variants"]:
                print("   %-24s lane_lb=%s M_lb=%s lane_ub=%s M=%s %-18s free=%s gap=%s (%ss)"
                      % (v["variant"], v["lane_lb"], v["M_lb"], v.get("lane_ub"), v.get("M"),
                         v["verdict"], v.get("free"),
                         (None if v.get("max_pair_gap") is None
                          else round(v["max_pair_gap"], 5)), v["seconds"]), flush=True)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(out, open(a.out, "w", encoding="utf-8"), indent=1)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
