"""A143 -- descend the TRUMP pair lineage of the doubly-met corner-first root, geometry only.

The PI's prediction: "since Trump is NOT in k0, that lineage must die when the other three corners
are forced toward Trump's single simple meeters -- report at which depth the K' lane count on BR,
TR or the far corner reaches LANE + M <= 1 (K0-FREE kill)".

What this measures.  The lineage is followed by bisecting BOTH hypothesis boxes and keeping the
child that still contains Trump's own two BL meeters (D4-mapped into the canonical pair frame).  At
every depth the K' lane test is run on all four corners.

    python code/descend143.py --depth 3
"""
import argparse
import itertools
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
A118 = os.path.join(ROOT, "attempts", "A118-lane-count", "code")
A99 = os.path.join(ROOT, "attempts", "A99-k0-tree-v2", "code")
_A57 = os.path.join(ROOT, "attempts", "A57-shadow-trees", "code")
_A132 = os.path.join(ROOT, "attempts", "A132-polygon-core", "code")
for _p in (A118, A99, _A57, _A132, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import blas1                                                    # noqa: F401,E402
import numpy as np                                              # noqa: E402
import polycore                                                 # noqa: E402
import lane as LANE                                             # noqa: E402
from caselp import Box                                          # noqa: E402
import class84 as K84                                           # noqa: E402
import cells143 as C                                            # noqa: E402
import pairs143 as P                                            # noqa: E402

CORNERS = ["BL(0,0)", "BR(0,0)", "TR(0,0)", "TL(0,0)"]


def transpose_pose(p):
    return (p[1], p[0], (90.0 - p[2]) % 90.0)


def trump_bl_pair():
    """the two BL meeters of the image whose BL corner is Trump's genuine (unwidened) 2-crowd,
    in the canonical pair frame."""
    Y0, _st, _lam = K84.trump_scaled()
    best = None
    for k in range(8):
        Z = K84.symmetry(Y0, k)
        ms = []
        for i, (x, y, th) in enumerate(Z):
            tn = math.degrees(th) % 90.0
            if C.meets_bl(x, y, tn, a_w=1.0):
                ms.append((i, x, y, tn))
        if len(ms) >= 2:
            best = (k, ms)
            break
    k, ms = best
    p1 = (ms[0][1], ms[0][2], ms[0][3])
    p2 = (ms[1][1], ms[1][2], ms[1][3])

    def raw_cell(p):
        w = (C.ZHI - C.ZLO) / C.NPOS
        return (min(C.NPOS - 1, max(0, int((p[0] - C.ZLO) / w))),
                min(C.NPOS - 1, max(0, int((p[1] - C.ZLO) / w))),
                min(C.NTILT - 1, max(0, int((p[2] % 90.0) / C.TILT_W))))
    k1, k2 = raw_cell(p1), raw_cell(p2)
    a = tuple(sorted((k1, k2)))
    b = tuple(sorted((P.transpose_key(k1), P.transpose_key(k2))))
    if min(a, b) == b:                              # the canonical rep is the transposed pair
        p1, p2 = transpose_pose(p1), transpose_pose(p2)
        k1, k2 = P.transpose_key(k1), P.transpose_key(k2)
    if (k2, k1) == min((k1, k2), (k2, k1)):
        pass
    order = sorted([(k1, p1), (k2, p2)])
    return "g%d" % k, [order[0][1], order[1][1]], [order[0][0], order[1][0]]


def in_box(b, p, tol=1e-9):
    return (b.x0 - tol <= p[0] <= b.x1 + tol and b.y0 - tol <= p[1] <= b.y1 + tol
            and b.th0 - tol <= p[2] <= b.th1 + tol)


def split8(b):
    xm, ym = 0.5 * (b.x0 + b.x1), 0.5 * (b.y0 + b.y1)
    tm = 0.5 * (b.th0 + b.th1)
    out = []
    for (X0, X1) in ((b.x0, xm), (xm, b.x1)):
        for (Y0, Y1) in ((b.y0, ym), (ym, b.y1)):
            for (T0, T1) in ((b.th0, tm), (tm, b.th1)):
                out.append(Box(X0, X1, Y0, Y1, T0, T1))
    return out


def lane_all(b1, b2, seed):
    rec = dict(src="A143", nid="descend", cls="k0_00", level=1,
               cond=[dict(x0=b.x0, x1=b.x1, y0=b.y0, y1=b.y1, th0=b.th0, th1=b.th1)
                     for b in (b1, b2)])
    rng = np.random.default_rng(seed)
    out = {}
    for cn in CORNERS:
        try:
            v = LANE.run_cell(rec, cn, rng, rigorous=True)
        except Exception as e:                                  # noqa: BLE001
            v = dict(verdict="ERROR", error=repr(e)[:150])
        out[cn] = dict(verdict=v.get("verdict"), lane_ub=v.get("lane_ub"),
                       lane_lb=v.get("lane_lb"), M=v.get("ncond_pot"), kill=bool(v.get("kill")))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--depth", type=int, default=3)
    a = ap.parse_args()
    img, poses, keys = trump_bl_pair()
    print(f"Trump image {img}: BL meeters {poses} in cells {keys}", flush=True)
    byk = {P.cell_key(c): c for c in C.all_cells() if not c.empty}
    b1, b2 = byk[tuple(keys[0])].box, byk[tuple(keys[1])].box
    assert in_box(b1, poses[0]) and in_box(b2, poses[1]), "Trump pose outside its clipped cell"
    out = []
    for d in range(a.depth + 1):
        pd = polycore.poly_poly_depth(polycore.build(b1, max_v=16).P,
                                      polycore.build(b2, max_v=16).P)
        lanes = lane_all(b1, b2, 1430 + d)
        rec = dict(depth=d, box1=b1.to_json(), box2=b2.to_json(),
                   poly_poly_depth=pd, P1_fires=bool(pd > 0.0),
                   max_centre_dist=P.max_centre_dist(b1, b2),
                   P2_fires=bool(P.max_centre_dist(b1, b2) < 1.0),
                   lanes=lanes,
                   any_kill=any(v["kill"] for v in lanes.values()))
        out.append(rec)
        print(f"depth {d}: P1={rec['P1_fires']} P2={rec['P2_fires']}  " +
              "  ".join(f"{c[:2]}: {v['verdict']} M={v['M']} kill={v['kill']}"
                        for c, v in lanes.items()), flush=True)
        if d == a.depth:
            break
        c1 = [c for c in split8(b1) if in_box(c, poses[0])]
        c2 = [c for c in split8(b2) if in_box(c, poses[1])]
        assert c1 and c2, "lost the Trump pose while descending"
        b1, b2 = c1[0], c2[0]
    p = os.path.join(BASE, "results", "descend143.json")
    json.dump(dict(image=img, poses=poses, cells=[list(k) for k in keys], levels=out),
              open(p, "w"), indent=1)
    print("wrote", p, flush=True)


if __name__ == "__main__":
    main()
