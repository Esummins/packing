"""A247: witness verification -- float pre-test, then EXACT rational verification (Fractions):
the tilt is rationalised onto the unit circle (t = tan(th/2) -> cos = (1-t^2)/(1+t^2),
sin = 2t/(1+t^2)), centres and side are rationalised, and every SAT depth (square vs cell,
square vs square) is computed exactly; a witness passes iff every required depth is > 0 (or
>= eta), every avoided depth <= 0, every pair depth <= 0 and every square lies in [0, s]^2.
Also the soundness test of the interval enclosures on random boxes (run: python verify247.py).
"""
import math
import random
from fractions import Fraction as Fr

import numpy as np

import geo247 as G


# ---------------------------------------------------------------- float pre-test
def check_float(s, ps, problem, margin=1e-7, eta=0.0):
    for i, sq in enumerate(problem['squares']):
        q = G.C.square_corners(*ps[i])
        if q.min() < margin or q.max() > s - margin:
            return False
        for name in sq['req']:
            if G.depth_cell_pt(ps[i], name, s) <= eta + margin:
                return False
        for name in sq.get('avoid', ()):
            if G.depth_cell_pt(ps[i], name, s) >= -margin:
                return False
    for i in range(len(ps)):
        for j in range(i + 1, len(ps)):
            if G.depth_pair_pt(ps[i], ps[j]) >= -margin:
                return False
    return True


# ---------------------------------------------------------------- exact layer
def rat(x, den=10 ** 9):
    return Fr(round(x * den), den)


def rational_pose(pose):
    cx, cy, th = pose
    t = rat(math.tan(th / 2))
    co = (1 - t * t) / (1 + t * t)
    si = 2 * t / (1 + t * t)
    return (rat(cx), rat(cy), co, si)


def corners_exact(rp):
    cx, cy, co, si = rp
    h = Fr(1, 2)
    return [(cx + co * a - si * b, cy + si * a + co * b) for a, b in ((-h, -h), (h, -h), (h, h), (-h, h))]


def proj(pts, n):
    vals = [p[0] * n[0] + p[1] * n[1] for p in pts]
    return min(vals), max(vals)


def depth_exact(ptsA, normalsA, ptsB, normalsB):
    best = None
    for n in list(normalsA) + list(normalsB):
        a, b = proj(ptsA, n), proj(ptsB, n)
        d = min(a[1], b[1]) - max(a[0], b[0])
        best = d if best is None else min(best, d)
    return best


def rect_exact(name, s):
    a0, b0, a1, b1, c0, d0, c1, d1 = G.rect_coeffs(name)
    x0, x1, y0, y1 = a0 + b0 * s, a1 + b1 * s, c0 + d0 * s, c1 + d1 * s
    return [(Fr(x0), Fr(y0)), (Fr(x1), Fr(y0)), (Fr(x1), Fr(y1)), (Fr(x0), Fr(y1))]


AXES = ((Fr(1), Fr(0)), (Fr(0), Fr(1)))


def check_exact(s, ps, problem):
    """exact verdict on the rationalised witness; returns a dict with the rational data."""
    sr = rat(s)
    rps = [rational_pose(p) for p in ps]
    eta = Fr(problem.get('eta', 0.0)).limit_denominator(10 ** 12)
    out = {'ok': True, 's': str(sr), 'poses': [[str(v) for v in rp] for rp in rps], 'fail': None,
           'min_req': None, 'max_avoid': None, 'max_pair': None}
    pts = [corners_exact(rp) for rp in rps]
    nrm = [((rp[2], rp[3]), (-rp[3], rp[2])) for rp in rps]
    for i, sq in enumerate(problem['squares']):
        for p in pts[i]:
            if p[0] < 0 or p[1] < 0 or p[0] > sr or p[1] > sr:
                out.update(ok=False, fail='containment %d' % i)
                return out
        for name in sq['req']:
            d = depth_exact(pts[i], nrm[i], rect_exact(name, sr), AXES)
            out['min_req'] = d if out['min_req'] is None else min(out['min_req'], d)
            if d <= eta:
                out.update(ok=False, fail='req %d %s' % (i, name))
                return out
        for name in sq.get('avoid', ()):
            d = depth_exact(pts[i], nrm[i], rect_exact(name, sr), AXES)
            out['max_avoid'] = d if out['max_avoid'] is None else max(out['max_avoid'], d)
            if d > 0:
                out.update(ok=False, fail='avoid %d %s' % (i, name))
                return out
    for i in range(len(ps)):
        for j in range(i + 1, len(ps)):
            d = depth_exact(pts[i], nrm[i], pts[j], nrm[j])
            out['max_pair'] = d if out['max_pair'] is None else max(out['max_pair'], d)
            if d > 0:
                out.update(ok=False, fail='pair %d %d' % (i, j))
                return out
    for key in ('min_req', 'max_avoid', 'max_pair'):
        if out[key] is not None:
            out[key] = float(out[key])
    return out


# ---------------------------------------------------------------- soundness of the enclosures
def soundness(n=20000, seed=247):
    """random boxes (pose x side), random poses inside: the float depth must lie in the enclosure."""
    rng = random.Random(seed)
    worst = 0.0
    for _ in range(n):
        s0 = rng.uniform(3.82, 4.4)
        s1 = s0 + rng.uniform(0, 0.05)
        b = []
        for _ in range(2):
            c = [rng.uniform(0.5, 3.0), rng.uniform(0.5, 3.0), rng.uniform(0, math.pi / 2)]
            w = [rng.uniform(0, 0.3), rng.uniform(0, 0.3), rng.uniform(0, 0.3)]
            b.append([(c[k], min(c[k] + w[k], math.pi / 2 if k == 2 else 9)) for k in range(3)])
        box = np.array([[s0] + [b[i][k][0] for i in range(2) for k in range(3)],
                        [s1] + [b[i][k][1] for i in range(2) for k in range(3)]])[None]
        s = (box[:, 0, 0], box[:, 1, 0])
        pa, pb = G.IV.pose_of(box, 1), G.IV.pose_of(box, 4)
        sv = rng.uniform(s0, s1)
        a = tuple(rng.uniform(*b[0][k]) for k in range(3))
        bb = tuple(rng.uniform(*b[1][k]) for k in range(3))
        name = rng.choice(G.RING)
        d = G.depth_cell(pa, G.rect_i(name, s))
        v = G.depth_cell_pt(a, name, sv)
        worst = max(worst, d[0][0] - v, v - d[1][0])
        dl = G.depth_cell_loose(pa, G.rect_i(name, s))
        worst = max(worst, dl[0][0] - d[0][0], d[1][0] - dl[1][0])      # tight inside loose
        dp = G.depth_pair(pa, pb)
        vp = G.depth_pair_pt(a, bb)
        worst = max(worst, dp[0][0] - vp, vp - dp[1][0])
        dpl = G.depth_pair_loose(pa, pb)
        worst = max(worst, dpl[0][0] - dp[0][0], dp[1][0] - dpl[1][0])
        (xlo, xhi), (ylo, yhi) = G.extent(pa)
        q = G.C.square_corners(*a)
        worst = max(worst, xlo[0][0] - q[:, 0].min(), q[:, 0].max() - xhi[1][0])
    return worst


if __name__ == '__main__':
    w = soundness()
    print('enclosure soundness on 20000 random boxes: worst excess %.3e (must be <= 1e-12)' % w)
    assert w <= 1e-12
    # exact layer against the float layer on the A244 5-cell witness
    s = 3.877084
    p = (1.393, 1.393, 0.0)
    prob = {'squares': [{'req': list(G.NBR['BL']), 'avoid': []}], 's': (s, s), 'eta': 0.0}
    print('float:', check_float(s, [p], prob), 'exact:', check_exact(s, [p], prob))
