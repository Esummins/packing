"""A196 step 3 -- the CERTIFIED uncoverable region U of the node (A164 geo164.uncoverable, A184 E3's contract):
obstacles = every role's K' polygon (inside every surviving pose, A172), covers = the union of every role's poses
over its surviving pieces (per tilt sub-bin bounding rects: a SUPERSET, so the complement is an inner approximation
of U [T]); a free square is admissible iff inside the container and interior-disjoint from every K'.  A cell is
claimed only when NO admissible pose meets the closed cell (Lipschitz margins).  Every square of a packing
consistent with the node lies inside its own coverable set, interiors disjoint, so 11 <= s0^2 - |U|:

    |U| > s0^2 - 11 = 4.03178  kills the node (Leaf WASTE);  else  Z = {c : dist(c, U) <= 1/2}  is a NO-family
    (a unit square with centre in Z contains a point of U, which no square of the packing contains) [T],
    as rects (inner: the U cells dilated by floor(h/p) - 1 cells, h = 1/(2 sqrt 2)), t-interval [0, 1].

All four corners of k5_16 are pins, so A184's corner rule (U_a) does not apply here: the corner pockets are
whatever U_b claims between the pins and the walls.  The 'strip the chord rows leave' is reported as U's share
inside the pin bands (y <= 1.01, y >= s0 - 1.01, x <= 1.01, x >= s0 - 1.01) -- a MEASUREMENT of where U sits,
not a further certified area (a chord row bounds a 1-D sum, it does not certify a 2-D region).
"""
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ATT = os.path.join(ROOT, "attempts")
RES = os.path.abspath(os.path.join(HERE, "..", "results"))
for _p in (os.path.join(ATT, "A164-wastage-area", "code"), HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import prio196                                                   # noqa: E402,F401
import geo164 as G                                               # noqa: E402  READ-ONLY (A164)
from caselp import Box                                           # noqa: E402  READ-ONLY (A57)

S0 = 969271 / 250000
B0 = S0 * S0 - 11                                                # 4.03178...


def role_geometry(kprime, pieces, max_groups=48):
    """(K' polygon floats or None, per-sub-bin bounding Boxes of the pieces: a superset cover)."""
    P = [(float(v[0]), float(v[1])) for v in kprime] if kprime else None
    groups = {}
    for p in pieces:
        b = Box(*p)
        groups.setdefault((round(b.th0, 9), round(b.th1, 9)), []).append(b)
    boxes = [Box(min(b.x0 for b in g), max(b.x1 for b in g), min(b.y0 for b in g), max(b.y1 for b in g), k[0], k[1])
             for k, g in groups.items()]
    if len(boxes) > max_groups:
        boxes.sort(key=lambda b: b.th0)
        step = int(math.ceil(len(boxes) / max_groups))
        boxes = [Box(min(b.x0 for b in g), max(b.x1 for b in g), min(b.y0 for b in g), max(b.y1 for b in g),
                     min(b.th0 for b in g), max(b.th1 for b in g))
                 for g in (boxes[i:i + step] for i in range(0, len(boxes), step))]
    return P, boxes


def zone_rects(U, xs, ys, p):
    """{c : dist(c, U) <= 1/2} inner-approximated (A184): dilate by k = floor(h/p) - 1 cells, h = 1/(2 sqrt2)."""
    k = int(math.floor((0.5 / math.sqrt(2.0)) / p)) - 1
    Z = G._dilate_box(np.pad(U, k, constant_values=False), k)[k:-k, k:-k] if k > 0 else U
    runs = G.runs_of(Z, xs, ys, p)
    merged = []
    for (x0, x1, y0, y1) in runs:
        if merged and abs(merged[-1][0] - x0) < 1e-12 and abs(merged[-1][1] - x1) < 1e-12 and abs(merged[-1][3] - y0) < 1e-9:
            merged[-1] = (x0, x1, merged[-1][2], y1)
        else:
            merged.append((x0, x1, y0, y1))
    return Z, [[round(v, 6) for v in r] for r in merged]


def band_areas(U, xs, ys, p):
    X, Y = np.meshgrid(xs, ys)
    cell = p * p
    return {"bottom band (y<=1.01)": float((U & (Y <= 1.01)).sum()) * cell,
            "top band (y>=s0-1.01)": float((U & (Y >= S0 - 1.01)).sum()) * cell,
            "left band (x<=1.01)": float((U & (X <= 1.01)).sum()) * cell,
            "right band (x>=s0-1.01)": float((U & (X >= S0 - 1.01)).sum()) * cell,
            "interior (1.01<x,y<s0-1.01)": float((U & (X > 1.01) & (X < S0 - 1.01) & (Y > 1.01) & (Y < S0 - 1.01)).sum()) * cell}


def uncoverable_node(key, node, pitch=0.01, ntilt=36, save_mask=True):
    """node = the step-1 snapshot (kprime, pieces per role).  -> record (+ results/masks/<key>.npz)."""
    t0 = time.time()
    obstacles, boxes, per_role = [], [], {}
    for nm in node["pieces"]:
        P, bx = role_geometry(node["kprime"].get(nm), node["pieces"][nm])
        if P is not None and len(P) >= 3:
            obstacles.append(P)
        boxes += bx
        per_role[nm] = bx
    Ub, xs, ys, res = G.uncoverable(S0, obstacles, boxes, lam=1.0, pitch=pitch, ntilt=ntilt, want_extra=False)
    p = float(res["pitch"])
    area = float(Ub.sum()) * p * p
    Z, zr = zone_rects(Ub, xs, ys, p)
    chk = G.sample_confirm(S0, obstacles, boxes, Ub, xs, ys, lam=1.0, n=30000, n_contain=8000)
    rec = dict(key=key, roles=list(node["pieces"]), n_obstacles=len(obstacles), n_boxes=len(boxes), pitch=p, ntilt=ntilt,
               area_U=area, B0=B0, ratio_B0=area / B0, kill=bool(area > B0), by_region=res.get("by_region"),
               bands=band_areas(Ub, xs, ys, p), zone_n_rects=len(zr), zone_area=float(Z.sum()) * p * p, zone_rects=zr,
               sample=chk, seconds=round(time.time() - t0, 1))
    if save_mask:
        os.makedirs(os.path.join(RES, "masks"), exist_ok=True)
        np.savez_compressed(os.path.join(RES, "masks", key + ".npz"), U=Ub, Z=Z, xs=xs, ys=ys)
    return rec


def nofam_rects(zr, shrink=1e-6):
    """the zone rects shrunk by `shrink` (the certificate rounds to 1e-9: inner stays inner)."""
    out = []
    for (x0, x1, y0, y1) in zr:
        if x1 - x0 > 2 * shrink and y1 - y0 > 2 * shrink:
            out.append((x0 + shrink, x1 - shrink, y0 + shrink, y1 - shrink))
    return out
