"""A166 -- the Trump side of the per-cell table (the coordinator's two additions).

(1) WHICH INTERIOR SQUARE.  Trump's packing (A22 / `attempts/A03-upper-reconstruct/trump11_float.json`,
    the same data A65 `crowdfam.trump_scaled` and A99 `class84.trump_scaled` read) has six upright and
    five tilted squares, all five tilted at 40.181937 deg.  Two of the five touch a wall
    (`sq6` the top wall, `sq10` the right wall), so the INTERIOR tilted squares are `sq7`, `sq8`,
    `sq9`.  For each of the eight D4 images and each of the eleven cells we report the tilted square
    whose pose is nearest `H`'s box in the pose metric

        dist(pose, B) = max( |dx|_box, |dy|_box, |dth|_box / 45 )     (0 iff the pose is IN B)

    where `|dx|_box` is the distance from the coordinate to the box's interval and `dth` uses the
    90-periodic tilt.  The scale 1/45 makes a 45 deg tilt error worth one container-unit of position
    error; the ranking is reported with the raw components so it can be re-read under any other
    scale.

(2) SIMPLE / NON-SIMPLE CORNERS.  At the EXACT unit corner box (`w = 0`) each Trump image has three
    corners met by exactly one square and one met by two (A143 sec 4): the three are the SIMPLE
    corners, the fourth the NON-SIMPLE one.  Its two meeters are one upright NON-slot square and one
    tilted square.  A separate label, `n_simple`, records how many of a corner's meeters are
    axis-aligned; the corner with THREE axis-aligned meeters at the widened box is the
    "three-simple corner" `BL[2,1]` of trump5's frame.

(3) QUADRANT CENSUS.  The container is split at `s0/2` into BL / BR / TR / TL quadrants (a centre
    exactly on a split line is assigned to the LOW side, and the file records how many are within
    1e-6 of a line).  We print Trump's census per image and each cell's dual-support census.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, ".."))
for _p in (HERE,):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import cells166 as C                                                # noqa: E402

S0 = C.S0
TRUMP = os.path.join(ROOT, "attempts", "A03-upper-reconstruct", "trump11_float.json")
CORNERS = C.CORNERS


# ------------------------------------------------------------------ Trump at s0, and its 8 images
def trump_scaled():
    """A99 `class84.trump_scaled` re-derived (read-only on the data file): centres blown up by
    lambda = s0/s_T so the family lives at s0; squares stay unit, tilts unchanged."""
    T = json.load(open(TRUMP, encoding="utf-8"))
    st = float(T["s"])
    lam = S0 / st
    return [[x * lam, y * lam, th] for (x, y, th) in T["X"]], st, lam


def symmetry(Y, k):
    """A65 `crowdfam.symmetry`: bit0 x-flip, bit1 y-flip, bit2 transpose; theta mod pi/2."""
    out = []
    for (x, y, th) in Y:
        if k & 1:
            x, th = S0 - x, -th
        if k & 2:
            y, th = S0 - y, -th
        if k & 4:
            x, y, th = y, x, math.pi / 2 - th
        out.append([x, y, th % (math.pi / 2)])
    return out


def half_extent(th_rad):
    return 0.5 * (abs(math.cos(th_rad)) + abs(math.sin(th_rad)))


def is_interior(x, y, th_rad, s=S0, tol=1e-9):
    h = half_extent(th_rad)
    return (x > h + tol) and (x < s - h - tol) and (y > h + tol) and (y < s - h - tol)


def _verts(cx, cy, th):
    co, si = math.cos(th), math.sin(th)
    e1 = (0.5 * co, 0.5 * si)
    e2 = (-0.5 * si, 0.5 * co)
    return [(cx + a * e1[0] + b * e2[0], cy + a * e1[1] + b * e2[1])
            for a, b in ((1, 1), (1, -1), (-1, -1), (-1, 1))]


def meets_rect(cx, cy, th, rect, tol=0.0):
    """SAT: does int Q(cx,cy,th) meet int(rect)?  rect = (X0, X1, Y0, Y1).  Complete for convex
    polygons -- returns the overlap depth; > tol means the interiors meet."""
    X0, X1, Y0, Y1 = rect
    V = _verts(cx, cy, th)
    R = [(X0, Y0), (X1, Y0), (X1, Y1), (X0, Y1)]
    best = None
    axes = [(1.0, 0.0), (0.0, 1.0), (math.cos(th), math.sin(th)), (-math.sin(th), math.cos(th))]
    for (nx, ny) in axes:
        a = [p[0] * nx + p[1] * ny for p in V]
        b = [p[0] * nx + p[1] * ny for p in R]
        d = min(max(a), max(b)) - max(min(a), min(b))
        best = d if best is None else min(best, d)
    return best


def corner_census(Z, a_w, s=S0):
    """per corner: the meeters of the (possibly widened) corner box, with the axis-aligned flag."""
    out = {}
    for c in CORNERS:
        rect = C.corner_rect(c, a_w, s)
        met = []
        for i, (x, y, th) in enumerate(Z):
            d = meets_rect(x, y, th, rect)
            if d > 0.0:
                tn = math.degrees(th) % 90.0
                met.append(dict(sq=i, depth=round(d, 9), th_deg=round(tn, 6),
                                simple=bool(min(tn, 90.0 - tn) < 1e-6),
                                interior=bool(is_interior(x, y, th))))
        out[c] = dict(n=len(met), n_simple=sum(1 for m in met if m["simple"]), meeters=met)
    return out


def quadrant_of(x, y, s=S0):
    mid = 0.5 * s
    if x <= mid and y <= mid:
        return "BL"
    if x > mid and y <= mid:
        return "BR"
    if x > mid and y > mid:
        return "TR"
    return "TL"


def quad_census(pts, s=S0):
    cnt = {c: 0 for c in CORNERS}
    near = 0
    mid = 0.5 * s
    for (x, y) in pts:
        cnt[quadrant_of(x, y, s)] += 1
        if abs(x - mid) < 1e-6 or abs(y - mid) < 1e-6:
            near += 1
    return cnt, near


# ------------------------------------------------------------------ pose distance to a box
def box_pose_dist(b, x, y, th_deg):
    def gap(v, lo, hi):
        return max(lo - v, v - hi, 0.0)
    dx = gap(x, b.x0, b.x1)
    dy = gap(y, b.y0, b.y1)
    t = th_deg % 90.0
    dt = min(gap(t, b.th0, b.th1), gap(t + 90.0, b.th0, b.th1), gap(t - 90.0, b.th0, b.th1))
    return max(dx, dy, dt / 45.0), dict(dx=dx, dy=dy, dth=dt)


def main():
    Y0, st, lam = trump_scaled()
    images = {("g%d" % k): symmetry(Y0, k) for k in range(8)}
    out = dict(s_trump=st, lam=lam, s0=S0,
               tilted=[i for i, (_x, _y, th) in enumerate(Y0) if abs(math.degrees(th) % 90) > 1e-6],
               interior_tilted=[i for i, (x, y, th) in enumerate(Y0)
                                if abs(math.degrees(th) % 90) > 1e-6 and is_interior(x, y, th)],
               images={})
    for g, Z in images.items():
        ex = corner_census(Z, 1.0)
        wd = corner_census(Z, 1.0 + C.W_MAX)
        nonsimple = [c for c in CORNERS if ex[c]["n"] >= 2]
        three = [c for c in CORNERS if wd[c]["n_simple"] >= 3]
        qc, near = quad_census([(x, y) for (x, y, _t) in Z])
        out["images"][g] = dict(exact=ex, widened=wd, nonsimple=nonsimple, three_simple=three,
                                quad=qc, quad_on_line=near,
                                poses=[[round(x, 9), round(y, 9), round(math.degrees(t) % 90, 9)]
                                       for (x, y, t) in Z])
        print("%s  exact n=%s  nonsimple=%s  three_simple=%s  quad=%s"
              % (g, {c: ex[c]["n"] for c in CORNERS}, nonsimple, three, qc), flush=True)

    # ---- per cell: nearest Trump interior tilted square over all eight images
    rows = []
    for (meta, b, rec) in C.load_eleven():
        nc, dist = C.nearest_corner(b)
        best = None
        allm = []
        for g, Z in images.items():
            for i in out["interior_tilted"]:
                x, y, th = Z[i]
                d, comp = box_pose_dist(b, x, y, math.degrees(th))
                allm.append(dict(image=g, sq=i, d=d, **comp))
                if best is None or d < best["d"]:
                    best = dict(image=g, sq=i, d=d, **comp)
        # also the nearest tilted square of any kind, and the nearest square of any kind
        best_any = None
        for g, Z in images.items():
            for i, (x, y, th) in enumerate(Z):
                d, comp = box_pose_dist(b, x, y, math.degrees(th))
                if best_any is None or d < best_any["d"]:
                    best_any = dict(image=g, sq=i, d=d, tilted=bool(i in out["tilted"]),
                                    interior=bool(i in out["interior_tilted"]), **comp)
        img = out["images"][best["image"]]
        sup = [(float(p["cx"]), float(p["cy"])) for p in (rec.get("packing") or [])]
        qc, near = quad_census(sup)
        rows.append(dict(cell=meta["cell"], level=meta["level"], family=meta["family"],
                         box=b.to_json(), nearest_corner=nc,
                         dist_to_corners={k: round(v, 6) for k, v in dist.items()},
                         trump_interior=best, trump_any=best_any,
                         image_nonsimple=img["nonsimple"], image_three_simple=img["three_simple"],
                         nearest_is_nonsimple=bool(nc in img["nonsimple"]),
                         nearest_is_three_simple=bool(nc in img["three_simple"]),
                         n_support=len(sup), support_quad=qc, support_quad_on_line=near,
                         trump_quad=img["quad"]))
        print("%-12s nearest %s | trump sq%d of %s (d=%.4f dx=%.4f dy=%.4f dth=%.2f) | "
              "nonsimple %s | support quad %s"
              % (meta["cell"], nc, best["sq"], best["image"], best["d"], best["dx"], best["dy"],
                 best["dth"], img["nonsimple"], qc), flush=True)
    out["cells"] = rows
    p = os.path.join(BASE, "results", "trump166.json")
    json.dump(out, open(p, "w"), indent=1)
    print("wrote", p, flush=True)


if __name__ == "__main__":
    main()
