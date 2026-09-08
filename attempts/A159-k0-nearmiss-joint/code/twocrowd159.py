"""A159 T1c -- a DIRECT search for a realised two-crowd, at both widths, on every near-miss.

The PI's reading of `docs/shadows/k0v4/l1_124.svg` is not the statement `LANE + M <= 1`; it is the
JOINT statement *"two squares can each touch the corner cell but they are mutually exclusive"*.
The lane leaf counts the two sides separately, so it cannot see that; and A159's `unwiden159.py`
shows the separate counts do not close at `w = 0` either (`LANE <= 1`, `M = 1` there too).  The
statement is decided instead by asking directly whether the pair EXISTS:

    maximise   J(H, F) = min( depth(Q_H, cell), depth(Q_F, cell), gap(Q_F, Q_H),
                              slack(Q_H, container), slack(Q_F, container) )
    over       H = (x, y, th) in B   (the cell's conditioned box)
               F = (x, y, th) free,  th in [0, 90)

`J > 0` is exactly a realised two-crowd: both squares meet the OPEN corner box, they are
interior-disjoint, and both are inside the container.  A maximiser with `J > 0` REFUTES the PI's
reading (and every lane leaf at that corner); a search that never gets `J` above 0 is evidence
FOR the reading, not a proof -- it is reported as `best_J` with the number of restarts, never as a
kill.

Run at `w = W0 = 0.0255100742` (Lemma K0-WIDEN's widened box, the box every lane leaf and every
kill in this campaign is stated over) and at `w = 0` (the plain unit corner cell `TR(0,0)`, which
is what the PI is looking at on the page).

Geometry here is written from scratch (support functions along the 4 + 4 edge normals); nothing is
imported from A141.  Every positive hit is re-verified EXACTLY by `xwitness159.check_one`.

    python twocrowd159.py --restarts 400
"""
import argparse
import glob
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
A141 = os.path.join(ROOT, "attempts", "A141-polycore-lane")
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402
from scipy.optimize import minimize  # noqa: E402

import xwitness159 as X  # noqa: E402  (A159's own exact checker, for the final verification)

S0 = 969271.0 / 250000.0
W0 = (S0 / 3.82 - 1.0) * (1.0 + 1.0 / math.sqrt(2.0))


def corner_cell(corner, w):
    lo, hi = 0.0, 1.0 + w
    return {"BL": (lo, hi, lo, hi), "BR": (S0 - hi, S0 - lo, lo, hi),
            "TR": (S0 - hi, S0 - lo, S0 - hi, S0 - lo),
            "TL": (lo, hi, S0 - hi, S0 - lo)}[corner]


def _sup(p, ux, uy):
    """max over the unit square Q(p) of <q, u>."""
    x, y, t = p
    c, s = math.cos(t), math.sin(t)
    return x * ux + y * uy + 0.5 * (abs(c * ux + s * uy) + abs(-s * ux + c * uy))


def _axes(t):
    c, s = math.cos(t), math.sin(t)
    return ((c, s), (-s, c), (-c, -s), (s, -c))


def depth_in_cell(p, cell):
    """-(SAT gap between Q(p) and the cell).  > 0 iff the interiors meet.  SAT is complete for
    convex polygons, so this is the exact predicate."""
    X0, X1, Y0, Y1 = cell
    lo_x = -_sup(p, -1.0, 0.0)          # min x over Q
    hi_x = _sup(p, 1.0, 0.0)            # max x over Q
    lo_y = -_sup(p, 0.0, -1.0)
    hi_y = _sup(p, 0.0, 1.0)
    sep = max(X0 - hi_x, lo_x - X1, Y0 - hi_y, lo_y - Y1)
    V = ((X0, Y0), (X1, Y0), (X1, Y1), (X0, Y1))
    for (ux, uy) in _axes(p[2])[:2]:
        pr = [vx * ux + vy * uy for (vx, vy) in V]
        q = p[0] * ux + p[1] * uy
        sep = max(sep, min(pr) - (q + 0.5), (q - 0.5) - max(pr))
    return -sep


def gap_sq_sq(a, b):
    """SAT gap between Q(a) and Q(b).  > 0 iff interior-disjoint."""
    best = -1e9
    for t in (a[2], b[2]):
        for (ux, uy) in _axes(t)[:2]:
            g1 = -(_sup(a, ux, uy) + _sup(b, -ux, -uy))
            g2 = -(_sup(a, -ux, -uy) + _sup(b, ux, uy))
            best = max(best, g1, g2)
    return best


def container_slack(p):
    return min(-_sup(p, -1.0, 0.0), -_sup(p, 0.0, -1.0),
               S0 - _sup(p, 1.0, 0.0), S0 - _sup(p, 0.0, 1.0))


def J(v, cell):
    H = (v[0], v[1], v[2])
    F = (v[3], v[4], v[5])
    return min(depth_in_cell(H, cell), depth_in_cell(F, cell), gap_sq_sq(F, H),
               container_slack(H), container_slack(F))


def _nm(f, v, lo, hi, iters=1500):
    r = minimize(lambda u: -f(np.clip(u, lo, hi)), v, method="Nelder-Mead",
                 options=dict(maxiter=iters, xatol=1e-12, fatol=1e-14))
    u = np.clip(r.x, lo, hi)
    return f(u), u


def deepest_H(box, cell, restarts, rng):
    """max over H in B of depth(Q_H, C).  <= 0 says NO pose of the conditioned square reaches the
    cell at all -- which is `M = 0`, and with `LANE <= 1` an outright kill."""
    x0, x1, y0, y1, t0d, t1d = box
    lo = np.array([x0, y0, math.radians(t0d)])
    hi = np.array([x1, y1, math.radians(t1d)])
    f = lambda u: depth_in_cell((u[0], u[1], u[2]), cell)                     # noqa: E731
    best, bv = None, -1e9
    for _ in range(restarts):
        v0 = lo + (hi - lo) * rng.random(3)
        val, u = _nm(f, v0, lo, hi)
        if val > bv:
            bv, best = val, u
    return bv, best


def best_free_against(H, cell, restarts, rng):
    """max over F of min(depth(Q_F, C), gap(Q_F, Q_H), slack(Q_F))."""
    lo = np.array([0.5, 0.5, 0.0])
    hi = np.array([S0 - 0.5, S0 - 0.5, math.pi / 2])
    f = lambda u: min(depth_in_cell((u[0], u[1], u[2]), cell),                # noqa: E731
                      gap_sq_sq((u[0], u[1], u[2]), H),
                      container_slack((u[0], u[1], u[2])))
    best, bv = None, -1e9
    for _ in range(restarts):
        v0 = lo + (hi - lo) * rng.random(3)
        val, u = _nm(f, v0, lo, hi)
        if val > bv:
            bv, best = val, u
        if bv > 1e-7:
            break
    return bv, best


def search(box, cell, restarts, rng, seed_pose=None, seed_free=None):
    """Staged search.  The feasible set is a sliver (`J` tops out at 1e-5 on the PI's own cell),
    so a flat 6-D multistart finds nothing; the stages are:

      1. the DEEPEST H in B (3 vars), plus sampled poses of B that reach the cell, plus A141's own
         recorded witness when there is one -- this is the seed pool for H;
      2. for each seed H, the best free square against it (3 vars);
      3. a joint polish in 6 vars from the best (H, F) found.
    """
    x0, x1, y0, y1, t0d, t1d = box
    lo6 = np.array([x0, y0, math.radians(t0d), 0.5, 0.5, 0.0])
    hi6 = np.array([x1, y1, math.radians(t1d), S0 - 0.5, S0 - 0.5, math.pi / 2])
    dH, Hstar = deepest_H(box, cell, max(30, restarts // 8), rng)
    seeds = []
    if Hstar is not None and dH > 0.0:
        seeds.append(tuple(Hstar))
    if seed_pose is not None:
        seeds.append((seed_pose[0], seed_pose[1], math.radians(seed_pose[2])))
    m = max(2000, restarts * 20)
    S = np.column_stack([rng.uniform(x0, x1, m), rng.uniform(y0, y1, m),
                         np.radians(rng.uniform(t0d, t1d, m))])
    dep = np.array([depth_in_cell(tuple(s), cell) for s in S])
    for k in np.argsort(-dep)[:max(8, restarts // 25)]:
        if dep[k] > 0.0:
            seeds.append(tuple(S[k]))
    best, bv = None, -1e9
    if seed_pose is not None and seed_free is not None:
        # A141's own recorded PAIR, evaluated as-is: the incumbent the search must beat
        w = np.array([seed_pose[0], seed_pose[1], math.radians(seed_pose[2]),
                      seed_free[0], seed_free[1], math.radians(seed_free[2])])
        bv, best = J(w, cell), w
    for H in seeds:
        if container_slack(H) < 0.0:
            continue
        val, F = best_free_against(H, cell, max(20, restarts // 10), rng)
        v = min(val, depth_in_cell(H, cell))
        if v > bv:
            bv, best = v, np.array([H[0], H[1], H[2], F[0], F[1], F[2]])
        if bv > 1e-7:
            break
    if best is not None:
        val, u = _nm(lambda w: J(w, cell), best, lo6, hi6, iters=4000)
        if val > bv:
            bv, best = val, u
    if best is None:
        best = 0.5 * (lo6 + hi6)
    return bv, best, dH


def t2_rows():
    rows = {}
    for f in sorted(glob.glob(os.path.join(A141, "results", "t2_cells_s*.jsonl"))):
        for ln in open(f, encoding="utf-8"):
            r = json.loads(ln)
            rows.setdefault(r["cell"], r)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--restarts", type=int, default=400)
    ap.add_argument("--out", default=os.path.join(BASE, "results", "twocrowd159.jsonl"))
    a = ap.parse_args()
    rows = t2_rows()
    seed = {}
    for r in json.load(open(os.path.join(A141, "results", "t5_twocrowd.json"), encoding="utf-8")):
        seed[(r["cell"], r["corner"])] = (r["H"], r["free"])   # A141's own recorded pair
    jobs = []
    for cid, r in sorted(rows.items()):
        for c in ("BL", "BR", "TR", "TL"):
            if r["corners"][c]["verdict"].startswith("NEAR-MISS"):
                jobs.append((cid, c))
    print("%d near-miss corners x 2 widths" % len(jobs), flush=True)
    done = set()
    if os.path.exists(a.out):
        for ln in open(a.out, encoding="utf-8"):
            try:
                z = json.loads(ln)
                done.add((z["cell"], z["corner"]))
            except Exception:                                    # noqa: BLE001
                pass
    fh = open(a.out, "a", encoding="utf-8")
    n_w, n_0 = 0, 0
    for (cid, corner) in jobs:
        if (cid, corner) in done:
            continue
        box = rows[cid]["boxes"][0]
        rec = dict(cell=cid, corner=corner, box=box)
        t0 = time.time()
        for tag, w in (("widened", W0), ("unwidened", 0.0)):
            rng = np.random.default_rng(1592)
            sd = seed.get((cid, corner)) or (None, None)
            bv, best, dH = search(box, corner_cell(corner, w), a.restarts, rng,
                                  seed_pose=sd[0], seed_free=sd[1])
            rec[tag] = dict(best_J=float(bv), restarts=a.restarts, deepest_H=float(dH),
                            found=bool(bv > 0.0),
                            H=[float(best[0]), float(best[1]), math.degrees(float(best[2]))],
                            free=[float(best[3]), float(best[4]),
                                  math.degrees(float(best[5]))])
            if bv > 0.0:
                # EXACT re-verification of the float witness, at 60 dps
                v = X.check_one(dict(cell=cid, corner=corner, j=0,
                                     free=rec[tag]["free"], H=rec[tag]["H"], gap=bv),
                                rows[cid], 60)
                rec[tag]["exact"] = {k: v[k] for k in
                                     ("SURVIVES", "pose_H_in_B", "H_meets_widened",
                                      "free_meets_widened", "disjoint", "H_vs_widened",
                                      "free_vs_widened", "free_vs_H", "H_vs_unwidened",
                                      "free_vs_unwidened")}
        rec["secs"] = round(time.time() - t0, 1)
        n_w += int(rec["widened"]["found"])
        n_0 += int(rec["unwidened"]["found"])
        fh.write(json.dumps(rec) + "\n")
        fh.flush()
        print("%-26s %s  widened J=%+.3e dH=%+.3e %s | unwidened J=%+.3e dH=%+.3e %s  %.0fs"
              % (cid, corner, rec["widened"]["best_J"], rec["widened"]["deepest_H"],
                 "FOUND" if rec["widened"]["found"] else "none",
                 rec["unwidened"]["best_J"], rec["unwidened"]["deepest_H"],
                 "FOUND" if rec["unwidened"]["found"] else "none", rec["secs"]), flush=True)
    fh.close()
    print("two-crowd realised: %d at the widened box, %d at the unwidened cell" % (n_w, n_0))


if __name__ == "__main__":
    main()
