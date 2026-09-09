"""A167 -- diagnostic: one (node, slot), pre-split to a fixed depth, per piece x per offset.

Prints the piece table (m, beta, sampled outside_free / band_free under K'(piece), both covers with
their leaf counts, reasons and wall times) so the levers can be tuned before the population pass.

    python diag167.py --nid c0_Y0169 --slot "TL(0,0)" --predepth 3 --per 40 --noff 3
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import condlane2 as C2  # noqa: E402
import chordlane as CL  # noqa: E402
import numpy as np      # noqa: E402
import polylane as P    # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nid", default="c0_Y0169")
    ap.add_argument("--slot", default="TL(0,0)")
    ap.add_argument("--predepth", type=int, default=3)
    ap.add_argument("--per", type=float, default=40.0, help="seconds per piece")
    ap.add_argument("--noff", type=int, default=3)
    ap.add_argument("--nlines", type=int, default=48)
    ap.add_argument("--maxopen", type=int, default=2500)
    ap.add_argument("--bandopen", type=int, default=0)
    ap.add_argument("--sample", type=int, default=8000)
    ap.add_argument("--offs", type=float, default=2.0)
    ap.add_argument("--longs", type=float, default=12.0)
    ap.add_argument("--pieces", default="", help="comma-separated paths to run (default all)")
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    recs = {r["nid"]: r for r in CL.CP.load_nodes()}
    boxes, _ = CL.CP.load_open_boxes(set(recs))
    for b in boxes:
        if not b.get("covered_by_node"):
            recs.setdefault(b["nid"], b)
    rec = recs[a.nid]
    conds, meet, cell, corner, i, j = CL.frame_boxes(rec, a.slot)
    jH = meet[0]
    others = [c for c in conds if c.idx != jH]
    orients = CL.WALL_ORIENT[(i, j)]
    stack = [("", conds[jH].box)]
    for _ in range(a.predepth):
        nxt = []
        for (p, b) in stack:
            c0, c1 = P.split_box(b)
            nxt.append((p + "0", c0))
            nxt.append((p + "1", c1))
        stack = nxt
    want = set(a.pieces.split(",")) if a.pieces else None
    print("%s %s cell=%s corner=%s orients=%s  B_H=%s" % (a.nid, a.slot, cell, corner, orients,
                                                          P.box_json(conds[jH].box)))
    rng = np.random.default_rng(1670)
    rows = []
    for (p, b) in stack:
        if want is not None and p not in want:
            continue
        pc = P.build_cond([b], tighten=False)[0]
        pc.idx = jH
        t0 = time.time()
        r = C2.piece_bound(cell, others, pc, orients, CL.S0, rng, sample=a.sample,
                           n_lines=a.nlines, n_off=a.noff, max_open=a.maxopen,
                           band_open=(a.bandopen or None), deadline=time.time() + a.per,
                           keep_cert=False, off_s=a.offs, long_s=a.longs)
        print("piece %-6s m=%d ok=%s total=%s  %.0f s   %s  %s"
              % (p or "(root)", r["m"], r["ok"], r.get("total"), time.time() - t0,
                 r.get("why", ""), json.dumps(r.get("dead_sample") or [])[:150]))
        for t in r["tries"]:
            print("    off %-12s beta=%d  s_out_free=%-4s s_band_free=%-5s | LANE_out=%-4s "
                  "(%4d lv, %4d op, %4.1fs) %s | LANE_band=%-4s (%s lv, %s op, %ss) %s"
                  % (t["off"], t["beta"], t["sample_outside_free"], t["sample_band_free"],
                     t["lane_out"], t["out_leaves"], t["out_open"], t.get("t_out", 0),
                     (t.get("out_reason") or "")[:34], t.get("lane_band"),
                     t.get("band_leaves"), t.get("band_open"), t.get("t_band"),
                     (t.get("band_reason") or "")[:34]))
        rows.append(dict(path=p, m=r["m"], ok=r["ok"], total=r.get("total"),
                         box=P.box_json(b), tries=r["tries"], why=r.get("why")))
    print("\n%d/%d pieces closed" % (sum(1 for r in rows if r["ok"]), len(rows)))
    if a.out:
        json.dump(rows, open(a.out, "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
