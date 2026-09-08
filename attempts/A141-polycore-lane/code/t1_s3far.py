"""A141 T1 -- `s3_far_BL389484_TR018470`, exactly.

(a) the PI's three distances (and the two K'(h2) wall gaps) from the CERTIFIED polygon cores;
(b) the lane statement at TR by a finite cover of the corner-meeting poses;
(c) the kill certificates + the sample line;
(d) see notes/lean_shape.md.

    python t1_s3far.py
"""
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
sys.path.insert(0, HERE)

import blas1  # noqa: F401,E402
import numpy as np  # noqa: E402

import polylane as P              # noqa: E402
import polycore as PC             # noqa: E402
import emit141 as EM              # noqa: E402
from caselp import Box            # noqa: E402

CELL = "s3_far_BL389484_TR018470"
A140 = os.path.join(ROOT, "attempts", "A140-k0-residue-gallery", "results", "t1_polycore.json")


def poly_dist(A, B):
    """min Euclidean distance between two convex polygons (0 if they meet)."""
    def seg(p, q, r):
        vx, vy = q[0] - p[0], q[1] - p[1]
        wx, wy = r[0] - p[0], r[1] - p[1]
        LL = vx * vx + vy * vy
        t = 0.0 if LL == 0 else max(0.0, min(1.0, (wx * vx + wy * vy) / LL))
        return math.hypot(p[0] + t * vx - r[0], p[1] + t * vy - r[1])
    best = 1e9
    for i in range(len(A)):
        for j in range(len(B)):
            best = min(best, seg(A[i], A[(i + 1) % len(A)], B[j]),
                       seg(B[j], B[(j + 1) % len(B)], A[i]))
    return best


def band(poly, x):
    ys = []
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        if (a[0] - x) * (b[0] - x) <= 0 and a[0] != b[0]:
            t = (x - a[0]) / (b[0] - a[0])
            ys.append(a[1] + t * (b[1] - a[1]))
    return (min(ys), max(ys)) if ys else None


def distances(raw, tight):
    """The five numbers the PI quoted, on BOTH the raw A140 boxes and the container-tightened
    ones.  `raw` reproduces A140's stored `margin_poly` / `pairs.depth_poly` exactly."""
    out = {}
    for tag, pcs in (("A140_raw", raw), ("container_tightened", tight)):
        h2, h3 = pcs[2].P, pcs[3].P
        lo = max(h2[:, 0].min(), h3[:, 0].min())
        hi = min(h2[:, 0].max(), h3[:, 0].max())
        pocket = None
        if hi > lo:
            g = []
            for x in np.linspace(lo, hi, 4001):
                u3, u2 = band(h3, x), band(h2, x)
                if u3 and u2:
                    g.append(u2[0] - u3[1])
            pocket = dict(strip=[float(lo), float(hi)], min=float(min(g)), max=float(max(g)))
        out[tag] = dict(
            K3_right_to_right_wall=float(P.S0 - h3[:, 0].max()),
            K3_top_to_top_wall=float(P.S0 - h3[:, 1].max()),
            K2_right_to_right_wall=float(P.S0 - h2[:, 0].max()),
            K2_top_to_top_wall=float(P.S0 - h2[:, 1].max()),
            bbox_vertical_gap_K3top_to_K2bottom=float(h2[:, 1].min() - h3[:, 1].max()),
            pocket_over_the_x_strip=pocket,
            pinch_K2_K3=float(poly_dist(h2, h3)),
            K2_bbox=[float(h2[:, 0].min()), float(h2[:, 0].max()),
                     float(h2[:, 1].min()), float(h2[:, 1].max())],
            K3_bbox=[float(h3[:, 0].min()), float(h3[:, 0].max()),
                     float(h3[:, 1].min()), float(h3[:, 1].max())],
            areas=[float(p.area()) for p in pcs])
    return out


def main():
    t00 = time.time()
    rec = [x for x in json.load(open(A140, encoding="utf-8"))["twelve"]
           if x["cell"] == CELL][0]
    raw_boxes = [Box(*b["box"]) for b in rec["boxes"]]
    raw = [PC.build(b) for b in raw_boxes]
    conds = P.build_cond(raw_boxes, verbose=True)
    tight = [c.pc for c in conds]
    for p in raw + tight:
        assert p.certified

    out = dict(cell=CELL, s=P.S0, widen_w=P.W0, lam_max=P.LAM_MAX,
               boxes_raw=[P.box_json(b) for b in raw_boxes],
               boxes_tightened=[P.box_json(c.box) for c in conds],
               n_verts=[len(p.verts) for p in tight],
               distances=distances(raw, tight))
    print(json.dumps(out["distances"]["A140_raw"], indent=1), flush=True)

    # ---------------------------------------------------------------- (b)/(c) the four corners
    rng = np.random.default_rng(141)
    out["corners"] = {}
    certs = {}
    for corner in ("TR", "BL", "BR", "TL"):
        t0 = time.time()
        r = P.lane_corner(corner, conds, rng=rng, keep_cert=True, max_open=4000, sample=40000)
        r["secs"] = round(time.time() - t0, 2)
        out["corners"][corner] = {k: v for k, v in r.items()
                                  if k not in ("cover_cert", "cover_open_cert", "M_cert")}
        print(f"  {corner}: LANE<={r['lane_ub']} (>= {r['lane_lb']}) M={r['M']} "
              f"{r['verdict']} meeters={r['meeters']} {r['secs']}s", flush=True)
        if r["lane_ub"] is not None:
            d = EM.cert_dict("polycore_lane", CELL, corner, conds, raw_boxes, r)
            p = os.path.join(BASE, "certs", f"{CELL}_{corner}.json")
            certs[corner] = dict(path=os.path.relpath(p, ROOT), sha256=EM.write_cert(p, d))

    # ---------------------------------------------------------------- the pair contradiction
    out["pairs"] = []
    for i in range(len(conds)):
        for j in range(len(conds)):
            if i == j:
                continue
            r = P.pair_incompatible(conds[i].box, conds[j].box)
            row = dict(i=i, j=j, incompatible=bool(r["ok"]), leaves=r["n_leaves"])
            if r["ok"]:
                d = EM.pair_cert_dict(CELL, i, j, conds[i].box, conds[j].box, r)
                p = os.path.join(BASE, "certs", f"{CELL}_pair_{i}{j}.json")
                row.update(cert=os.path.relpath(p, ROOT), sha256=EM.write_cert(p, d),
                           witness=r["leaves"][0].get("w") if len(r["leaves"]) == 1 else None)
            out["pairs"].append(row)
    out["pair_kill"] = [r for r in out["pairs"] if r["incompatible"]]
    print("  pair kills:", [(r["i"], r["j"], r["leaves"]) for r in out["pair_kill"]], flush=True)
    out["polypoly_depth_tightened"] = [
        [i, j, float(PC.poly_poly_depth(tight[i].P, tight[j].P))]
        for i in range(len(tight)) for j in range(i + 1, len(tight))]

    # ---------------------------------------------------------------- the sample line
    Cs, Ts = P.sample_meeting(P.corner_cell("TR"), P.S0, 400000, rng)
    per = {}
    hit = np.zeros(len(Cs), bool)
    for cs in conds:
        h = PC.poly_square_depth(cs.pc.P, Cs, Ts) > 0.0
        per[cs.idx] = int(h.sum())
        hit |= h
    out["sample_line_TR"] = dict(drawn=400000, corner_meeting=int(len(Cs)),
                                 overlapping_some_core=int(hit.sum()), per_core=per,
                                 free=int((~hit).sum()))
    print("  sample line TR:", out["sample_line_TR"], flush=True)

    out["certs"] = certs
    out["secs"] = round(time.time() - t00, 1)
    p = os.path.join(BASE, "results", "t1_s3far.json")
    json.dump(out, open(p, "w", encoding="utf-8"), indent=1)
    print("wrote", p, "in %.1fs" % out["secs"])


if __name__ == "__main__":
    main()
