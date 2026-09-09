"""A167 -- why a piece has NO viable guard offset: the full screened-out table for one piece.

    python whydead.py --nid c0_Y0169 --slot "TL(0,0)" --pieces 01000,01001,0100
"""
import argparse
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import condlane2 as C2  # noqa: E402
import chordlane as CL  # noqa: E402
import numpy as np      # noqa: E402
import polylane as P    # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nid", default="c0_Y0169")
    ap.add_argument("--slot", default="TL(0,0)")
    ap.add_argument("--pieces", default="")
    ap.add_argument("--sample", type=int, default=20000)
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
    rng = np.random.default_rng(1670)
    res = []
    for path in [p for p in a.pieces.split(",") if p != ""] or [""]:
        b = conds[jH].box
        for ch in path:
            b = P.split_box(b)[0 if ch == "0" else 1]
        pc = P.build_cond([b], tighten=False)[0]
        pc.idx = jH
        misses, _ = CL.box_misses_cell_exact(b, cell)
        ranked, pool, contra, dead = C2.rank_lines(cell, others, pc, orients, CL.S0, rng,
                                                   a.sample, 48, 0 if misses else 1)
        cnt = collections.Counter((d["orient"], d["why"]) for d in dead)
        print("piece %-8s m=%d  box=%s" % (path or "(root)", 0 if misses else 1, P.box_json(b)))
        print("   viable %d, screened %d" % (len(ranked), len(dead)))
        for k, v in sorted(cnt.items()):
            print("      %-2s %-46s %4d" % (k[0], k[1], v))
        for d in dead:
            if d["orient"] == "v" and 0.70 <= float(__import__("fractions").Fraction(d["off"])) \
                    <= 0.75:
                print("      near-0.729 v-line: %s" % json.dumps(d))
        res.append(dict(path=path, m=0 if misses else 1, box=P.box_json(b),
                        n_viable=len(ranked), n_dead=len(dead),
                        by_reason={"%s|%s" % k: v for k, v in cnt.items()},
                        witness=C2.free_pose_witness(pool)))
    if a.out:
        json.dump(res, open(a.out, "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
