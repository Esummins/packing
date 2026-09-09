"""A164 -- the INDEPENDENT checker for a stored U mask.

It shares NO code with geo164's rotated-grid / dilation machinery and NO code with A132's
`poly_square_depth`: the separating-axis test below is written out here, and the search over poses
is a direct one over the region a MEETING square's centre can occupy, not a morphological
dilation.  Two passes, both refutation hunts:

  (A) TARGETED RANDOM.  For a certified-uncoverable cell C, sampling a pose that MEETS C is easy:
      draw a tilt, draw a point p uniformly in C, draw an offset d uniformly in [-lam/2, lam/2]^2
      and set c = p - R_th d; then p in Q_lam(c, th) ∩ C, so the pose meets C.  Every such pose
      must be INADMISSIBLE.  `--nrand` poses are spread over the whole certified set.
  (B) DENSE LOCAL SWEEP.  For `--ncell` sampled cells, a complete grid of centres at pitch `--dc`
      over the cell dilated by lam*sqrt2/2 (the only place a meeting square's centre can be)
      crossed with `--ndth` tilts; every pose that meets the cell must be inadmissible.

  (C) CONVERSE SPOT CHECK on cells the mask left UNSHADED: (A)'s sampler must find an admissible
      meeting pose for most of them.  A miss is NOT a refutation -- the mask is only an inner
      approximation of U -- so misses are reported as `unwitnessed`, not as failures.

A single admissible meeting pose on a certified cell refutes the mask.

    set PYTHONDONTWRITEBYTECODE=1 && python verify164.py --id l1_104
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
for _p in (os.path.join(ATT, "A148-gallery-v4", "code"),
           os.path.join(ATT, "A132-polygon-core", "code"),
           os.path.join(ATT, "A135-polycore-verifier", "code"),
           os.path.join(ATT, "A57-shadow-trees", "code"), HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import geo164 as G                                                    # noqa: E402

ROOT2H = math.sqrt(2.0) / 2.0


# --------------------------------------------------------------- this file's own SAT, vectorised
def own_gap_poly_square(P, CX, CY, CT, ST, half):
    """separating-axis GAP between the convex polygon P (nv, 2) and the squares of half-side
    `half` at centres (CX, CY) with cos/sin (CT, ST).  > 0 disjoint, < 0 interiors overlap.
    Written out here; polycore is not imported."""
    P = np.asarray(P, float)
    best = np.full(np.shape(CX), -np.inf)
    E = np.roll(P, -1, axis=0) - P
    for k in range(len(P)):
        ex, ey = E[k]
        ln = math.hypot(ex, ey)
        if ln < 1e-14:
            continue
        ax, ay = ey / ln, -ex / ln                     # a normal of edge k
        pp = P[:, 0] * ax + P[:, 1] * ay
        plo, phi = pp.min(), pp.max()
        hw = half * (np.abs(ax * CT + ay * ST) + np.abs(-ax * ST + ay * CT))
        qc = CX * ax + CY * ay
        best = np.maximum(best, np.maximum(plo - (qc + hw), (qc - hw) - phi))
    for (ax, ay) in ((CT, ST), (-ST, CT)):
        pp = np.multiply.outer(P[:, 0], ax) + np.multiply.outer(P[:, 1], ay)
        plo, phi = pp.min(0), pp.max(0)
        qc = CX * ax + CY * ay
        best = np.maximum(best, np.maximum(plo - (qc + half), (qc - half) - phi))
    return best


def own_meets_cell(cx, cy, x0, x1, y0, y1, CX, CY, CT, ST, half):
    """True where the square of half-side `half` at (CX, CY) MEETS the closed axis-aligned cell."""
    P = np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1]], float)
    return own_gap_poly_square(P, CX, CY, CT, ST, half) <= 0.0


def own_admissible(s, obstacles, CX, CY, CT, ST):
    """the UNIT square at (CX, CY, th) is inside [0, s]^2 and interior-disjoint from every core."""
    w = 0.5 * (np.abs(CT) + np.abs(ST))
    ok = (CX >= w) & (CX <= s - w) & (CY >= w) & (CY <= s - w)
    for P in obstacles:
        if not ok.any():
            break
        ok &= own_gap_poly_square(P, CX, CY, CT, ST, 0.5) >= 0.0
    return ok


# --------------------------------------------------------------- pass (A): targeted random
def targeted(rng, s, obstacles, xs, ys, ii, jj, h, lam, n):
    k = rng.integers(0, len(ii), n)
    px = xs[ii[k]] + rng.uniform(-h, h, n)
    py = ys[jj[k]] + rng.uniform(-h, h, n)
    th = rng.uniform(0.0, math.pi / 2.0, n)
    ct, st = np.cos(th), np.sin(th)
    du = rng.uniform(-0.5 * lam, 0.5 * lam, n)
    dv = rng.uniform(-0.5 * lam, 0.5 * lam, n)
    cx = px - (du * ct - dv * st)
    cy = py - (du * st + dv * ct)
    ok = own_admissible(s, obstacles, cx, cy, ct, st)
    return int(n), int(ok.sum()), [float(cx[ok][0]), float(cy[ok][0]),
                                   float(math.degrees(th[ok][0]))] if ok.any() else None


# --------------------------------------------------------------- pass (B): dense local sweep
def dense_cell(s, obstacles, px, py, h, lam, dc, ndth):
    reach = 0.5 * lam * math.sqrt(2.0) + h
    n = int(math.ceil(2.0 * reach / dc)) + 1
    us = np.linspace(px - reach, px + reach, n)
    vs = np.linspace(py - reach, py + reach, n)
    UU, VV = np.meshgrid(us, vs)
    UU, VV = UU.ravel(), VV.ravel()
    nmeet, nadm = 0, 0
    for th in (np.arange(ndth) + 0.5) * (math.pi / 2.0) / ndth:
        ct, st = math.cos(th), math.sin(th)
        CT = np.full(UU.shape, ct)
        ST = np.full(UU.shape, st)
        mt = own_meets_cell(px, py, px - h, px + h, py - h, py + h, UU, VV, CT, ST, 0.5 * lam)
        if not mt.any():
            continue
        nmeet += int(mt.sum())
        ad = own_admissible(s, obstacles, UU[mt], VV[mt], CT[mt], ST[mt])
        nadm += int(ad.sum())
        if nadm:
            return nmeet, nadm
    return nmeet, nadm


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True)
    ap.add_argument("--nrand", type=int, default=200000)
    ap.add_argument("--ncell", type=int, default=60)
    ap.add_argument("--dc", type=float, default=0.02)
    ap.add_argument("--ndth", type=int, default=45)
    ap.add_argument("--seed", type=int, default=1164)
    a = ap.parse_args()

    z = np.load(os.path.join(BASE, "results", f"mask_{a.id}.npz"), allow_pickle=True)
    spec = json.loads(str(z["spec"][0]))
    U, xs, ys = z["U"], z["xs"], z["ys"]
    s, lam = spec["s"], spec["lam"]
    p = float(xs[1] - xs[0])
    h = 0.5 * p
    obstacles, names, kinds, boxes = G.obstacles_of(spec["boxes"])
    rng = np.random.default_rng(a.seed)

    out = dict(id=a.id, spec=spec, obstacles=names,
               checker=dict(nrand=a.nrand, ncell=a.ncell, dc=a.dc, ndth=a.ndth,
                            cell_half=h, seed=a.seed,
                            note="own SAT, own search; shares no code with geo164's dilation "
                                 "or with A132 poly_square_depth"))
    jj, ii = np.nonzero(U)
    out["n_cells_U"] = int(len(ii))
    out["area_U_from_mask"] = float(len(ii)) * p * p
    if len(ii) == 0:
        out["verdict"] = "EMPTY MASK (nothing to refute)"
        print(json.dumps(out, indent=1))
        json.dump(out, open(os.path.join(BASE, "results", f"verify164_{a.id}.json"), "w",
                            encoding="utf-8"), indent=1)
        return

    n, nad, wit = targeted(rng, s, obstacles, xs, ys, ii, jj, h, lam, a.nrand)
    out["A_targeted"] = dict(drawn=n, admissible_meeters=nad, witness=wit,
                             claim="every pose that meets a certified-uncoverable cell must be "
                                   "inadmissible")
    pick = rng.integers(0, len(ii), min(a.ncell, len(ii)))
    tm, ta, bad = 0, 0, 0
    for k in pick:
        nm, na = dense_cell(s, obstacles, float(xs[ii[k]]), float(ys[jj[k]]), h, lam, a.dc,
                            a.ndth)
        tm += nm
        ta += na
        bad += int(na > 0)
    out["B_dense"] = dict(cells=int(len(pick)), poses_meeting=int(tm),
                          admissible_meeters=int(ta), cells_refuted=int(bad))
    jj2, ii2 = np.nonzero(~U)
    n2, nad2, w2 = targeted(rng, s, obstacles, xs, ys, ii2, jj2, h, lam, max(20000, a.nrand // 5))
    out["C_converse"] = dict(drawn=n2, admissible_meeters=nad2,
                             note="unshaded cells: an admissible meeter SHOULD normally exist; a "
                                  "shortfall is not a refutation, the mask is only an inner "
                                  "approximation of U")
    refuted = nad + ta
    out["verdict"] = ("MASK CONFIRMED — no admissible pose meets any certified-uncoverable cell "
                      f"({n} targeted + {tm} dense meeting poses tested)"
                      if refuted == 0 else f"MASK REFUTED — {refuted} admissible meeting poses")
    print(json.dumps(out, indent=1))
    q = os.path.join(BASE, "results", f"verify164_{a.id}.json")
    json.dump(out, open(q, "w", encoding="utf-8"), indent=1)
    print("wrote", q)


if __name__ == "__main__":
    main()
