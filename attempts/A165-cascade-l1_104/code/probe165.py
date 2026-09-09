"""A165 T0 -- the measurement probe: is the PI's cascade premise (a NARROW forced corner crowd)
true on `l1_104`?  Reports the widened-corner meeter cover size at each corner, the pair count
after the two sound pair prunes, and the top-wall row facts.  Writes results/probe165.json.

    python code/probe165.py --cell l1_104 --depth 9
"""
import argparse
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cas165 as K                                               # noqa: E402
import numpy as np                                               # noqa: E402
import polylane as PL                                            # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", default="l1_104")
    ap.add_argument("--depth", type=int, default=9)
    ap.add_argument("--max_open", type=int, default=6000)
    ap.add_argument("--corners", default="TR,TL,BL,BR")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    meta, rec, boxes = K.load_node(a.cell)
    conds = PL.build_cond(boxes, verbose=True)
    out = dict(cell=a.cell, meta=meta, boxes=[K.bx_json(b) for b in boxes],
               budget=rec["budget"], tau=rec["tau"], converged=rec["converged"],
               s0=K.S0, w=K.W0, a_w=K.AW, r6_gap=K.r6_gap(), depth0=a.depth, corners={})

    # the top-wall row facts
    yL1 = K.S0 - 1.0 - K.W0
    yL2 = K.S0 - 1.0 + 1e-6
    out["top_row"] = dict(at_widened_bottom=K.top_row_facts(yL1),
                          just_above_s0_minus_1=K.top_row_facts(yL2))

    for corner in a.corners.split(","):
        t0 = time.time()
        cov = K.meeter_cover(corner, conds, depth0=a.depth, max_open=a.max_open)
        obs = K.open_boxes(cov)
        n = len(obs)
        rowd = dict(cell=K.corner_cell(corner), n_leaves=len(cov.get("leaves", [])),
                    n_open=n, lane=cov.get("lane"), complete=cov.get("complete"),
                    reason=cov.get("reason"), wall_s=round(time.time() - t0, 1))
        if 0 < n <= 4000:
            OV = K.pair_matrix(obs)
            # unordered pairs (i <= j) that are NOT always-overlapping
            iu = np.triu_indices(n, 0)
            alive = int((~OV[iu]).sum())
            rowd.update(n_pairs_raw=int(n * (n + 1) // 2), n_pairs_after_ovl=alive)
            # how much of the pose window survives, in centre-area terms
            rowd["open_volume"] = float(sum((b.x1 - b.x0) * (b.y1 - b.y0) * (b.th1 - b.th0)
                                            for b in obs))
        out["corners"][corner] = rowd
        print(f"{a.cell} {corner}: leaves={rowd['n_leaves']} open={n} "
              f"pairs={rowd.get('n_pairs_after_ovl')} {rowd['wall_s']}s", flush=True)

    p = a.out or os.path.join(K.BASE, "results", "probe165_%s_d%d.json" % (a.cell, a.depth))
    K.jdump(out, p)
    print("wrote", p, flush=True)
    print(json.dumps(out["top_row"], indent=1))


if __name__ == "__main__":
    main()
