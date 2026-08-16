"""
Independent exact verifier (fractions.Fraction) for an 11-unit-square packing.
Input: centres (cx,cy), angles theta (radians) and container side s (floats).
Rounding: t_i = tan(theta_i/2) rounded to a rational with denominator DEN, giving exact
cos = (1-t^2)/(1+t^2), sin = 2t/(1+t^2); centres rounded to denominator DEN.
Checks (all with strictly positive margin, exact arithmetic):
  * containment: every corner strictly inside [0, s_rat]^2  (s_rat = rational >= s given)
  * pairwise disjointness: separating axis theorem for convex polygons - there exists an axis among the
    4 edge normals along which the projections are separated by a strictly positive gap.
Returns (ok, min_margin, details).  Completely independent of pack11.py.
"""
from fractions import Fraction as Fr
import math, json, sys

DEN = 10 ** 12


def rat(x, den=DEN):
    return Fr(round(x * den), den)


def square_corners(cx, cy, t):
    """exact corners of unit square centred (cx,cy) with tan(theta/2)=t (all Fractions)."""
    c = (1 - t * t) / (1 + t * t)
    s = 2 * t / (1 + t * t)
    h = Fr(1, 2)
    u = (c * h, s * h)      # half edge vector 1
    v = (-s * h, c * h)     # half edge vector 2
    return [(cx + u[0] + v[0], cy + u[1] + v[1]),
            (cx + u[0] - v[0], cy + u[1] - v[1]),
            (cx - u[0] - v[0], cy - u[1] - v[1]),
            (cx - u[0] + v[0], cy - u[1] + v[1])], (c, s)


def sat_gap(P, Q, axes):
    """max over axes of the projection gap (positive => separated)."""
    best = None
    for (ax, ay) in axes:
        pP = [ax * x + ay * y for x, y in P]
        pQ = [ax * x + ay * y for x, y in Q]
        gap = max(min(pQ) - max(pP), min(pP) - max(pQ))
        # normalise by axis length (axes here have length 1 exactly since c^2+s^2=1)
        if best is None or gap > best:
            best = gap
    return best


def verify(centres, thetas, s, den=DEN, s_rat=None):
    n = len(centres)
    if s_rat is None:
        s_rat = Fr(math.ceil(s * den), den)
    sq = []
    for (cx, cy), th in zip(centres, thetas):
        t = rat(math.tan(th / 2), den)
        cxr, cyr = rat(cx, den), rat(cy, den)
        corners, (c, sn) = square_corners(cxr, cyr, t)
        sq.append((corners, [(c, sn), (-sn, c)]))
    min_margin = None
    # containment
    for corners, _ in sq:
        for x, y in corners:
            m = min(x, y, s_rat - x, s_rat - y)
            if min_margin is None or m < min_margin:
                min_margin = m
    if min_margin <= 0:
        return False, float(min_margin), 'containment failed'
    # pairwise
    for i in range(n):
        for j in range(i + 1, n):
            g = sat_gap(sq[i][0], sq[j][0], sq[i][1] + sq[j][1])
            if g <= 0:
                return False, float(g), 'overlap pair %d %d' % (i, j)
            if g < min_margin:
                min_margin = g
    return True, float(min_margin), 'ok: s_rat=%s (%.12f)' % (s_rat, float(s_rat))


def verify_x(x, den=DEN, s_rat=None):
    N = (len(x) - 1) // 3
    centres = [(x[2 * i], x[2 * i + 1]) for i in range(N)]
    thetas = list(x[2 * N:3 * N])
    return verify(centres, thetas, x[3 * N], den, s_rat)


if __name__ == '__main__':
    # usage: python verify_exact.py results.jsonl  -> verifies the best record in the file
    import numpy as np
    best = None
    for line in open(sys.argv[1]):
        r = json.loads(line)
        if best is None or r['s'] < best['s']:
            best = r
    print('best s =', best['s'], best['angles'])
    ok, m, msg = verify_x(best['x'])
    print(ok, m, msg)


def verify_claim(x, s_claim, den=DEN):
    """Scale the configuration (centres only) by s_claim/s about the container centre and verify
    exactly inside [0, s_claim]^2 with strictly positive margins.  s_claim is rounded UP to den."""
    N = (len(x) - 1) // 3
    s = x[3 * N]
    lam = s_claim / s
    centres = [(s_claim / 2 + lam * (x[2 * i] - s / 2), s_claim / 2 + lam * (x[2 * i + 1] - s / 2))
               for i in range(N)]
    thetas = list(x[2 * N:3 * N])
    s_rat = Fr(math.ceil(s_claim * den), den)
    return verify(centres, thetas, s_claim, den, s_rat)
