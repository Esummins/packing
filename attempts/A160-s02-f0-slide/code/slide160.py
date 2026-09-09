"""A160 T1 -- f0's SLIDING SLOT in the S02 (k7 + pinwheel-4) shadow.

The clearance of a pose of one square, the other ten FROZEN at the shadow's poses, is

    g(x, y, theta) = min( wall gaps, min_j max_{8 selections} sat_gap(pose, square_j) ),

so the admissible set is {g >= 0}.  At the shadow tilt this set has EMPTY INTERIOR for the
pinwheel's free squares (checked exactly with shapely in `pocket_area`): f0 is wedged, and its
freedom is a one-parameter FAMILY -- a curve in (x, y, theta) -- not a pocket.  A curve is invisible
to an area computation, so the slide is traced here on a grid of the clearance field:

  * `g` is AFFINE in (x, y) at fixed tilt for every one of the 8 selections of every pair, so the
    whole field is evaluated by numpy array algebra (no Python inner loop, exact float rows);
  * the slide at level eps is the connected component of {g >= -eps} that contains the square's own
    shadow pose (scipy.ndimage.label, 3-D connectivity over the (x, y, theta) grid);
  * its extent in x, y and theta is reported for a ladder of eps down to the grid's own resolution,
    so the eps -> 0 limit is visible and the reported extent is never an artefact of one tolerance;
  * the contact set (pairs and walls at |gap| <= tol) is reported at the component's two extreme
    ends and at its centre, which is the contact-graph sequence the slide passes through.

    python slide160.py [--tag S02] [--squares f0,f1,f2,f3,...] [--anchor shat|s0]
                       [--dtheta 0.1] [--h 0.0025] [--half 0.6]

READ-ONLY on every campaign and prior attempt; writes only under attempts/A160-s02-f0-slide/.
"""
from __future__ import annotations

import argparse, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "attempts", "A116-local-selection-tree", "code"))
import a116lib as A            # noqa: E402  (imports blas1 -> BLAS pinned to one thread)

import numpy as np             # noqa: E402
from scipy import ndimage      # noqa: E402
from shapely.geometry import Polygon, box as sbox   # noqa: E402

RES = os.path.join(BASE, "results")
os.makedirs(RES, exist_ok=True)
S0 = A.S0
CONTACT_TOL = 1e-6


# ------------------------------------------------------------------ the frozen configuration
def config(tag, anchor):
    """(side, {name: (x, y, theta_rad)}) of the eleven squares.
      `shat`     the gallery shadow (a111lib, six printed decimals);
      `polished` the same configuration refined to ~1e-16 by code/polish160.py (the object every
                 slide length in this attempt is measured against);
      `s0`       A116's s0-anchored frame (free squares dilated by s0/s*, slots at s0) -- the frame
                 the local certificate's boxes are centred in, where the eleven do NOT fit."""
    s_sh, P, slots, free = A.shadow_poses(tag)
    if anchor == "shat":
        return s_sh, P, list(slots), list(free)
    if anchor == "polished":
        d = json.load(open(os.path.join(RES, "polish160.json"), encoding="utf-8"))["eleven"]
        Pp = {n: (v[0], v[1], math.radians(v[2])) for n, v in d["poses"].items()}
        return d["s"], Pp, list(slots), list(free)
    if anchor == "s0_polished":
        d = json.load(open(os.path.join(RES, "polish160.json"), encoding="utf-8"))["eleven"]
        lam = S0 / d["s"]
        Pp = {}
        for n, v in d["poses"].items():
            if n in slots:
                Pp[n] = (A.slot_xy(n, S0)[0], A.slot_xy(n, S0)[1], 0.0)
            else:
                Pp[n] = (v[0] * lam, v[1] * lam, math.radians(v[2]))
        return S0, Pp, list(slots), list(free)
    _, Pa, slots, free = A.anchored(tag, S0)
    return S0, Pa, list(slots), list(free)


# ------------------------------------------------------------------ the clearance field
def field(name, poses, side, X, Y, th):
    """g(X, Y, th) on a meshgrid: min over walls and over the ten frozen squares of the pair's
    best (max over the 8 selections) separating gap.  Affine in (X, Y) per selection."""
    h = 0.5 * A.wfun(th)
    g = np.minimum.reduce([X - h, side - h - X, Y - h, side - h - Y])
    a0 = [A.axis(th, 0), A.axis(th, 1)]
    for n, (px, py, pt) in poses.items():
        if n == name:
            continue
        wt = 0.5 * A.wfun(th - pt)
        best = None
        for k in (0, 1):
            ax, ay = a0[k]                       # owner = the MOVING square
            proj = (px - X) * ax + (py - Y) * ay
            for eps in (1, -1):
                v = eps * proj - 0.5 - wt
                best = v if best is None else np.maximum(best, v)
            ax, ay = A.axis(pt, k)               # owner = the FROZEN square
            proj = (X - px) * ax + (Y - py) * ay
            for eps in (1, -1):
                v = eps * proj - 0.5 - wt
                best = np.maximum(best, v)
        g = np.minimum(g, best)
    return g


def clearance(name, poses, side, pose):
    x, y, th = pose
    return float(field(name, poses, side, np.array([[x]]), np.array([[y]]), th)[0, 0])


def contacts(name, poses, side, pose, tol=CONTACT_TOL):
    x, y, th = pose
    out = []
    h = 0.5 * A.wfun(th)
    for lbl, g in (("wall-xlo", x - h), ("wall-xhi", side - h - x),
                   ("wall-ylo", y - h), ("wall-yhi", side - h - y)):
        if g <= tol:
            out.append(lbl)
    for n, (px, py, pt) in poses.items():
        if n == name:
            continue
        if A.sat_gap((x, y), th, (px, py), pt) <= tol:
            out.append(n)
    return sorted(out)


# ------------------------------------------------------------------ the exact pocket test
def pocket_area(name, poses, side, th):
    """The EXACT area of the admissible centre set at tilt `th` (shapely boolean ops on the
    Minkowski octagons).  0.0 means the slot has empty interior at this tilt."""
    w = A.wfun(th)
    lo, hi = 0.5 * w, side - 0.5 * w
    if hi <= lo:
        return 0.0
    reg = sbox(lo, lo, hi, hi)
    for n, (x, y, t) in poses.items():
        if n == name:
            continue
        ci, cj = A.corners((0.0, 0.0), t), A.corners((0.0, 0.0), th)
        M = Polygon([(a[0] + b[0], a[1] + b[1]) for a in ci for b in cj]).convex_hull
        reg = reg.difference(Polygon([(x + a, y + b) for a, b in M.exterior.coords[:-1]]))
        if reg.is_empty:
            return 0.0
    return float(reg.area)


# ------------------------------------------------------------------ the slide
def scan(name, poses, side, th_lo, th_hi, dth, half, hstep, eps_ladder):
    ax0, ay0, at0 = poses[name]
    nth = int(round((th_hi - th_lo) / dth)) + 1
    ths = np.array([math.radians(th_lo + i * dth) for i in range(nth)])
    nx = int(round(2 * half / hstep)) + 1
    xs = ax0 - half + hstep * np.arange(nx)
    ys = ay0 - half + hstep * np.arange(nx)
    Xg, Yg = np.meshgrid(xs, ys, indexing="ij")
    G = np.empty((nth, nx, nx), dtype=np.float32)
    for i, th in enumerate(ths):
        G[i] = field(name, poses, side, Xg, Yg, float(th)).astype(np.float32)

    i0 = int(np.argmin(np.abs(np.degrees(ths) - math.degrees(at0))))
    jx = int(np.argmin(np.abs(xs - ax0)))
    jy = int(np.argmin(np.abs(ys - ay0)))
    g_shadow = clearance(name, poses, side, poses[name])

    out = dict(square=name,
               anchor_pose=[round(ax0, 6), round(ay0, 6), round(math.degrees(at0), 5)],
               side=round(side, 9), clearance_at_anchor=round(g_shadow, 10),
               exact_pocket_area_at_anchor_tilt=round(pocket_area(name, poses, side, at0), 10),
               grid=dict(theta_deg=[th_lo, th_hi, dth], xy_half=half, xy_step=hstep,
                         shape=list(G.shape)),
               max_clearance_over_grid=round(float(G.max()), 8),
               best_pose_over_grid=None, levels=[])
    k = np.unravel_index(int(np.argmax(G)), G.shape)
    out["best_pose_over_grid"] = [round(float(xs[k[1]]), 6), round(float(ys[k[2]]), 6),
                                  round(math.degrees(float(ths[k[0]])), 4),
                                  round(float(G[k]), 8)]
    # max clearance per tilt: the "is there a pocket at this tilt" curve
    out["clearance_by_tilt"] = [[round(math.degrees(float(ths[i])), 4),
                                 round(float(G[i].max()), 8)] for i in range(nth)]

    for eps in eps_ladder:
        M = G >= -eps
        lab, n = ndimage.label(M)
        cid = lab[i0, jx, jy]
        if cid == 0:                    # the anchor cell missed the component: take the nearest
            idx = np.argwhere(M)
            if len(idx) == 0:
                out["levels"].append(dict(eps=eps, cells=0))
                continue
            d = np.abs(idx[:, 0] - i0) + np.abs(idx[:, 1] - jx) + np.abs(idx[:, 2] - jy)
            cid = lab[tuple(idx[int(np.argmin(d))])]
        sel = np.argwhere(lab == cid)
        ti, xi, yi = sel[:, 0], sel[:, 1], sel[:, 2]
        tdeg = np.degrees(ths[ti])
        xv, yv = xs[xi], ys[yi]
        # the principal direction of the component's (x, y) footprint
        pts = np.stack([xv, yv], axis=1)
        c = pts.mean(axis=0)
        _, sv, vt = np.linalg.svd(pts - c, full_matrices=False)
        if len(sv) < 2:
            sv = np.array([sv[0] if len(sv) else 0.0, 0.0])
        axv = vt[0] if vt.shape[0] else np.array([1.0, 0.0])
        pr = (pts - c) @ axv
        lo_i, hi_i = int(np.argmin(pr)), int(np.argmax(pr))
        gv = G[ti, xi, yi]
        rec = dict(eps=eps, n_components=int(n), cells=int(len(sel)),
                   x=[round(float(xv.min()), 6), round(float(xv.max()), 6)],
                   y=[round(float(yv.min()), 6), round(float(yv.max()), 6)],
                   theta_deg=[round(float(tdeg.min()), 4), round(float(tdeg.max()), 4)],
                   extent=[round(float(xv.max() - xv.min()), 6),
                           round(float(yv.max() - yv.min()), 6),
                           round(float(tdeg.max() - tdeg.min()), 4)],
                   slide_axis_xy=[round(float(axv[0]), 5), round(float(axv[1]), 5)],
                   slide_length=round(float(pr.max() - pr.min()), 6),
                   slide_width=round(float(2 * sv[1] / max(1.0, math.sqrt(len(pts)))), 6),
                   max_clearance=round(float(gv.max()), 8),
                   end_lo=[round(float(xv[lo_i]), 6), round(float(yv[lo_i]), 6),
                           round(float(tdeg[lo_i]), 4)],
                   end_hi=[round(float(xv[hi_i]), 6), round(float(yv[hi_i]), 6),
                           round(float(tdeg[hi_i]), 4)])
        for lbl, p in (("lo", rec["end_lo"]), ("hi", rec["end_hi"])):
            rec["contacts_" + lbl] = contacts(name, poses, side,
                                              (p[0], p[1], math.radians(p[2])))
        rec["contacts_anchor"] = contacts(name, poses, side, poses[name])
        out["levels"].append(rec)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="S02")
    ap.add_argument("--squares", default="f0")
    ap.add_argument("--anchor", default="shat", choices=("shat", "polished", "s0", "s0_polished"))
    ap.add_argument("--dtheta", type=float, default=0.1)
    ap.add_argument("--th-lo", type=float, default=20.0)
    ap.add_argument("--th-hi", type=float, default=80.0)
    ap.add_argument("--h", type=float, default=0.0025)
    ap.add_argument("--half", type=float, default=0.6)
    ap.add_argument("--eps", default="0,1e-6,1e-4,1e-3,1e-2")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    side, poses, slots, free = config(a.tag, a.anchor)
    names = list(poses) if a.squares == "ALL" else a.squares.split(",")
    eps_ladder = [float(v) for v in a.eps.split(",")]
    cfg = list(poses.values())
    wp = min(A.sat_gap(cfg[i][:2], cfg[i][2], cfg[j][:2], cfg[j][2])
             for i in range(len(cfg)) for j in range(i + 1, len(cfg)))
    out = dict(tag=a.tag, anchor=a.anchor, side=round(side, 9),
               worst_pair_sat_gap=round(wp, 10), squares={})
    for nm in names:
        r = scan(nm, poses, side, a.th_lo, a.th_hi, a.dtheta, a.half, a.h, eps_ladder)
        out["squares"][nm] = r
        top = r["levels"][0] if r["levels"] else {}
        print("%-9s g(anchor)=%+.2e  pocket area(anchor tilt)=%.3g  max g on grid=%+.4f"
              % (nm, r["clearance_at_anchor"], r["exact_pocket_area_at_anchor_tilt"],
                 r["max_clearance_over_grid"]))
        for L in r["levels"]:
            if L.get("cells"):
                print("    eps=%-7g cells=%-8d x=%s y=%s th=%s  len=%.4f axis=%s"
                      % (L["eps"], L["cells"], L["x"], L["y"], L["theta_deg"],
                         L["slide_length"], L["slide_axis_xy"]))
    p = a.out or os.path.join(RES, "slide_%s_%s.json" % (a.tag, a.anchor))
    json.dump(out, open(p, "w", encoding="utf-8"), indent=1)
    print("wrote", p)


if __name__ == "__main__":
    main()
