#!/usr/bin/env python3
"""
A47 leg (a) TASK 2 -- INDEPENDENT spot-check of a passed obstacle certificate.

The exact verifier's PASS says: every closed unit square in [0,s']^2 whose interior misses C_shr
carries mass >= 1.  This script tests that statement directly on random placements, WITHOUT using
the branch-and-bound: it picks random rational placements, decides "free" (interior misses C_shr)
by an independent float polygon-clipping test with a safety margin, and then evaluates the mass
EXACTLY (fractions).  A single free placement with exact mass < 1 would refute the PASS.

usage:  python sstar_selfcheck.py cert.json [--n 20000] [--seed 1]
"""
import argparse
import json
import os
import random
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sstar_geom as G                      # noqa: E402
import verify_measure_obs as V              # noqa: E402
from verify_measure_obs import clip_float   # noqa: E402

VM = V.VM


def poly_area(poly):
    a = 0.0
    n = len(poly)
    for i in range(n):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % n]
        a += x0 * y1 - x1 * y0
    return abs(a) / 2


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cert")
    ap.add_argument("--n", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--area-tol", type=float, default=1e-9)
    a = ap.parse_args(argv)

    d, s, n, atoms, weights, total, box, obstacle = V.load(a.cert)
    pieces = []
    for name in G.PIECES:
        pieces.append(([(float(x), float(y)) for (x, y) in obstacle[name]["verts"]],
                       [(float(u), float(v), float(w)) for (u, v, w) in obstacle[name]["halfplanes"]]))
    rng = random.Random(a.seed)
    sf = float(s)
    nfree = 0
    worst = None
    for _ in range(a.n):
        t = F(rng.randint(0, 10 ** 6), 10 ** 6)
        co, si = VM.cos_sin_t(t)
        w = co + si
        lo, hi = w / 2, s - w / 2
        cx = lo + (hi - lo) * F(rng.randint(0, 10 ** 6), 10 ** 6)
        cy = lo + (hi - lo) * F(rng.randint(0, 10 ** 6), 10 ** 6)
        cf, sf_, cxf, cyf = float(co), float(si), float(cx), float(cy)
        q = [(cxf + cf * 0.5 - sf_ * 0.5, cyf + sf_ * 0.5 + cf * 0.5),
             (cxf - cf * 0.5 - sf_ * 0.5, cyf - sf_ * 0.5 + cf * 0.5),
             (cxf - cf * 0.5 + sf_ * 0.5, cyf - sf_ * 0.5 - cf * 0.5),
             (cxf + cf * 0.5 + sf_ * 0.5, cyf + sf_ * 0.5 - cf * 0.5)]
        free = True
        for (vt, hp) in pieces:
            inter = clip_float(list(q), hp)
            if len(inter) >= 3 and poly_area(inter) > a.area_tol:
                free = False
                break
        if not free:
            continue
        nfree += 1
        m = VM.mass_at_frac(atoms, weights, t, cx, cy)
        if worst is None or m < worst[0]:
            worst = (m, t, cx, cy)
        if m < 1:
            print(f"REFUTED: free placement t={t} c=({cx},{cy}) exact mass {m} (~{float(m):.9f})")
            return 1
    print(f"{a.n} random placements, {nfree} free; min exact mass on free placements = "
          f"{worst[0] if worst else 'n/a'} (~{float(worst[0]) if worst else float('nan'):.9f})")
    print(f"total = {total} (~{float(total):.6f}) < n = {n}: {total < n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
