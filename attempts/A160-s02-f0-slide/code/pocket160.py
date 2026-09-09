"""A160 T1 -- the EXACT eps-relaxed admissible set of one square, the other ten frozen.

The eight signed separating-axis selections of a pair are AFFINE in the moving square's centre at a
fixed tilt, so the pair's forbidden set of centres is the intersection of eight half-planes -- a
convex octagon (a square when the two tilts agree mod 90 deg).  Relaxing the disjointness to
`gap >= -eps` pushes each of the eight half-planes inward by exactly eps, so

    FREE_eps(theta) = [h - eps, side - h + eps]^2  \  union_j OCT_j(theta, eps),
    OCT_j = { c : eps_s * ((c_j - c) . a_k(theta)) <= 1/2 + w/2 - eps  and  the four owner=j rows },

is an EXACT polygon (shapely boolean ops on half-plane clips, no buffering, no grid).  Letting
eps -> 0 shows what the admissible set is: a pocket if its area tends to a positive number, a SLIDE
(a one-parameter family) if its area tends to 0 while its LENGTH tends to a positive number, and a
rigid point if both tend to 0 like sqrt(eps) and eps.

    python pocket160.py [--tag S02] [--squares f0] [--anchor shat|s0] [--dtheta 0.25]
                        [--eps 1e-2,3e-3,1e-3,3e-4,1e-4,1e-5]

READ-ONLY on every campaign and prior attempt.
"""
from __future__ import annotations

import argparse, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "attempts", "A116-local-selection-tree", "code"))
sys.path.insert(0, HERE)
import a116lib as A                       # noqa: E402
import numpy as np                        # noqa: E402
from shapely.geometry import Polygon, box as sbox, Point   # noqa: E402
from slide160 import config, contacts     # noqa: E402

RES = os.path.join(BASE, "results")
os.makedirs(RES, exist_ok=True)
BIG = 40.0


def halfplane(nrm, rhs):
    """{c : nrm . c <= rhs} clipped to the big box, as a polygon."""
    nx, ny = nrm
    nn = math.hypot(nx, ny)
    ux, uy = nx / nn, ny / nn
    d = rhs / nn
    px, py = ux * d, uy * d                # a point on the line
    tx, ty = -uy, ux                       # along the line
    return Polygon([(px + BIG * tx, py + BIG * ty), (px - BIG * tx, py - BIG * ty),
                    (px - BIG * tx - BIG * ux, py - BIG * ty - BIG * uy),
                    (px + BIG * tx - BIG * ux, py + BIG * ty - BIG * uy)])


def oct_forbidden(cj, tj, th, eps):
    """The pair's eps-relaxed forbidden centre set of the moving square (tilt th) against a frozen
    square at (cj, tj): the intersection of the eight relaxed half-planes."""
    b = 0.5 + 0.5 * A.wfun(th - tj) - eps
    reg = None
    for k in (0, 1):
        axm = A.axis(th, k)                # owner = moving square: L(c) = e * ((cj - c) . a_k(th))
        for e in (1, -1):
            nrm = (e * -axm[0], e * -axm[1])
            rhs = b - e * (cj[0] * axm[0] + cj[1] * axm[1])
            hp = halfplane(nrm, rhs)
            reg = hp if reg is None else reg.intersection(hp)
        axf = A.axis(tj, k)                # owner = frozen square: L(c) = e * ((c - cj) . a_k(tj))
        for e in (1, -1):
            nrm = (e * axf[0], e * axf[1])
            rhs = b + e * (cj[0] * axf[0] + cj[1] * axf[1])
            hp = halfplane(nrm, rhs)
            reg = reg.intersection(hp)
    return reg


def free_poly(name, poses, side, th, eps):
    h = 0.5 * A.wfun(th)
    lo, hi = h - eps, side - h + eps
    if hi <= lo:
        return Polygon()
    reg = sbox(lo, lo, hi, hi)
    for n, (x, y, t) in poses.items():
        if n == name:
            continue
        reg = reg.difference(oct_forbidden((x, y), t, th, eps))
        if reg.is_empty:
            return reg
    return reg


def comps(reg):
    if reg is None or reg.is_empty:
        return []
    if reg.geom_type == "Polygon":
        return [reg]
    return [g for g in getattr(reg, "geoms", []) if g.geom_type == "Polygon" and g.area >= 0]


def descr(poly):
    pts = np.array(poly.exterior.coords[:-1])
    c = pts.mean(axis=0)
    if len(pts) < 3:
        return dict(area=0.0, length=0.0, width=0.0, axis=[1.0, 0.0])
    _, sv, vt = np.linalg.svd(pts - c, full_matrices=False)
    axv = vt[0]
    pr = (pts - c) @ axv
    qr = (pts - c) @ vt[1]
    return dict(area=float(poly.area), length=float(pr.max() - pr.min()),
                width=float(qr.max() - qr.min()), axis=[float(axv[0]), float(axv[1])],
                end_lo=[float(pts[int(np.argmin(pr))][0]), float(pts[int(np.argmin(pr))][1])],
                end_hi=[float(pts[int(np.argmax(pr))][0]), float(pts[int(np.argmax(pr))][1])],
                centroid=[float(poly.centroid.x), float(poly.centroid.y)])


def scan(name, poses, side, ths, eps_list):
    ax0, ay0, at0 = poses[name]
    ap = Point(ax0, ay0)
    out = dict(square=name, anchor_pose=[round(ax0, 6), round(ay0, 6), round(math.degrees(at0), 5)],
               side=round(side, 9), by_eps=[])
    for eps in eps_list:
        rows, live = [], []
        for th in ths:
            cs = comps(free_poly(name, poses, side, th, eps))
            if not cs:
                rows.append(dict(theta_deg=round(math.degrees(th), 4), n=0))
                continue
            pick = min(cs, key=lambda g: g.distance(ap))
            d = descr(pick)
            r = dict(theta_deg=round(math.degrees(th), 4), n=len(cs),
                     area=round(d["area"], 9), length=round(d["length"], 6),
                     width=round(d["width"], 6),
                     axis=[round(v, 4) for v in d["axis"]],
                     bbox=[round(v, 6) for v in pick.bounds],
                     centroid=[round(v, 6) for v in d["centroid"]],
                     end_lo=[round(v, 6) for v in d["end_lo"]],
                     end_hi=[round(v, 6) for v in d["end_hi"]],
                     dist_anchor=round(pick.distance(ap), 8),
                     area_all=round(sum(g.area for g in cs), 9))
            rows.append(r)
            live.append(r)
        rec = dict(eps=eps, n_theta=len(rows), n_theta_live=len(live), rows=rows)
        if live:
            rec["theta_range_deg"] = [live[0]["theta_deg"], live[-1]["theta_deg"]]
            rec["union_bbox"] = [round(min(r["bbox"][0] for r in live), 6),
                                 round(min(r["bbox"][1] for r in live), 6),
                                 round(max(r["bbox"][2] for r in live), 6),
                                 round(max(r["bbox"][3] for r in live), 6)]
            rec["max_area"] = round(max(r["area"] for r in live), 9)
            rec["max_length"] = round(max(r["length"] for r in live), 6)
            rec["max_width"] = round(max(r["width"] for r in live), 6)
            best = max(live, key=lambda r: r["length"])
            rec["longest_at_tilt"] = best["theta_deg"]
            rec["longest_axis"] = best["axis"]
            rec["contacts_end_lo"] = contacts(name, poses, side,
                                              (best["end_lo"][0], best["end_lo"][1],
                                               math.radians(best["theta_deg"])), tol=2 * eps)
            rec["contacts_end_hi"] = contacts(name, poses, side,
                                              (best["end_hi"][0], best["end_hi"][1],
                                               math.radians(best["theta_deg"])), tol=2 * eps)
            rec["contacts_mid"] = contacts(name, poses, side,
                                           (best["centroid"][0], best["centroid"][1],
                                            math.radians(best["theta_deg"])), tol=2 * eps)
        out["by_eps"].append(rec)
        print("  eps=%-8g live tilts %3d/%d  %s  max area %.3g  max len %.5f  max wid %.5f  bbox %s"
              % (eps, rec["n_theta_live"], rec["n_theta"],
                 ("th [%g, %g]" % tuple(rec["theta_range_deg"])) if live else "-",
                 rec.get("max_area", 0), rec.get("max_length", 0), rec.get("max_width", 0),
                 rec.get("union_bbox")))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="S02")
    ap.add_argument("--squares", default="f0")
    ap.add_argument("--anchor", default="shat", choices=("shat", "polished", "s0", "s0_polished"))
    ap.add_argument("--dtheta", type=float, default=0.25)
    ap.add_argument("--th-lo", type=float, default=0.0)
    ap.add_argument("--th-hi", type=float, default=90.0)
    ap.add_argument("--eps", default="1e-2,3e-3,1e-3,3e-4,1e-4,1e-5")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    side, poses, slots, free = config(a.tag, a.anchor)
    names = list(poses) if a.squares == "ALL" else a.squares.split(",")
    n = int(round((a.th_hi - a.th_lo) / a.dtheta)) + 1
    ths = [math.radians(a.th_lo + i * a.dtheta) for i in range(n)]
    eps_list = [float(v) for v in a.eps.split(",")]
    out = dict(tag=a.tag, anchor=a.anchor, side=round(side, 9), dtheta=a.dtheta,
               th_window=[a.th_lo, a.th_hi], squares={})
    for nm in names:
        print(nm, "anchor", [round(v, 6) for v in poses[nm][:2]],
              round(math.degrees(poses[nm][2]), 4))
        out["squares"][nm] = scan(nm, poses, side, ths, eps_list)
    p = a.out or os.path.join(RES, "pocket_%s_%s.json" % (a.tag, a.anchor))
    json.dump(out, open(p, "w", encoding="utf-8"), indent=1)
    print("wrote", p)


if __name__ == "__main__":
    main()
