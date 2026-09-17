"""A251 tests: the SOUNDNESS of the box-valid certificate (the cores really are inside every
square of the box, so the pocket is over-approximated), the two elementary lemmas of the analytic
route, and MID-NOTCH against a direct disc search.

    python test251.py
"""
import math
import os
import sys

import numpy as np
from shapely.geometry import Point, Polygon

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom251 as C                                                   # noqa: E402
import family251 as F                                                 # noqa: E402
import analytic251 as A                                               # noqa: E402
import twotilted249 as W                                              # noqa: E402
import geom248 as G                                                   # noqa: E402

SEED_X = [0.254, 0.891, 0.254, 0.695, 1.317, 0.695, 1.317, 0.891]
XW = list(SEED_X[:4]) + list(SEED_X[4:8]) + list(SEED_X[:4]) + list(SEED_X[4:8])
SW = 3.877084


def test_core_sound(trials=400, rad=0.03, seed=1):
    """the CORE of a box lies inside EVERY square of the box -- the only direction that makes the
    pocket over-approximation sound."""
    rng = np.random.default_rng(seed)
    bad = 0.0
    for _ in range(trials):
        xc = np.array(XW) + rng.normal(0, 0.05, 16)
        sc = SW + rng.normal(0, 0.01)
        r = [rad] * 17
        poses, names, _ = F.poses_of(list(xc), sc)
        rhos, dths = F.deviations(r)
        cores = [C.member_poly(m) for m in C.core_members(poses, rhos, dths)]
        for _ in range(6):
            d = rng.uniform(-1, 1, 17) * rad
            p2, _, _ = F.poses_of(list(xc + d[:16]), sc + d[16])
            sq = [Polygon(C.G237.sq_verts(p[0], p[1], p[2], 0.5)) for p in p2]
            for k in range(8):
                bad = max(bad, cores[k].difference(sq[k]).area)
    print('  core_sound: max core-outside-square area %.3e over %d boxes' % (bad, trials))
    assert bad < 1e-9, bad


def test_pierce_monotone():
    """shrinking the cores can only enlarge the over-pocket, so the PIERCE residual is monotone."""
    poses, _, _ = F.poses_of(XW, SW)
    prev = -1.0
    for eps in (0.0, 0.05, 0.10, 0.20, 0.30):
        mem = [(p[0], p[1], p[2], 0.5 - eps) for p in poses]
        v = C.pierce(mem, SW, [(SW / 2, SW / 2)], step_deg=3.0)
        assert v >= prev - 1e-12, (eps, v, prev)
        prev = v
    print('  pierce_monotone: residual non-decreasing in the core shrink  OK')


def test_inradius(trials=3000, seed=2):
    """Lemma INRADIUS: interior-disjoint unit squares have centres at distance >= 1."""
    rng = np.random.default_rng(seed)
    worst = 9.0
    for _ in range(trials):
        a = [rng.uniform(0, 4), rng.uniform(0, 4), rng.uniform(0, math.pi / 2)]
        b = [rng.uniform(0, 4), rng.uniform(0, 4), rng.uniform(0, math.pi / 2)]
        if G.poly_gap(G.verts(a), G.verts(b)) >= 0:
            worst = min(worst, math.hypot(a[0] - b[0], a[1] - b[1]))
    print('  inradius: least centre distance of disjoint unit squares %.4f (>= 1)' % worst)
    assert worst >= 1.0 - 1e-9


def test_three_disc(trials=20000, seed=3):
    """Lemma THREE-DISC: three points pairwise >= 1 apart need an enclosing disc of radius
    >= 1/sqrt3; sampled triples that fit in a smaller disc must fail the distance test."""
    rng = np.random.default_rng(seed)
    R = 1.0 / math.sqrt(3.0)
    worst = 0.0
    for _ in range(trials):
        pts = rng.normal(0, 0.45, (3, 2))
        rad = max(np.linalg.norm(p) for p in pts)
        d = min(np.linalg.norm(pts[i] - pts[j]) for i in range(3) for j in range(i))
        if d >= 1.0:
            worst = max(worst, R - rad)
    print('  three_disc: no triple with pairwise >= 1 inside radius %.5f (worst slack %.3e)' % (R, worst))
    assert worst <= 1e-9


def test_mid_notch(trials=20000, seed=4):
    """MID-NOTCH numerically: for random admissible (theta, delta) wall pairs on the window no
    disc of radius 1/2 fits in the wall's middle triangle."""
    rng = np.random.default_rng(seed)
    worst, n = 0.0, 0
    for _ in range(trials):
        s = rng.uniform(3.82, 4.0)
        t, tp = rng.uniform(0.01, math.pi / 2 - 0.01, 2)
        d = rng.uniform(max(0.0, s - 2 - G.w(t)), 1.0)
        dp = rng.uniform(max(0.0, s - 2 - G.w(tp)), 1.0)
        r = A.notch_inradius(t, tp, d, dp, s)
        worst = max(worst, r)
        n += 1
    print('  mid_notch: max middle-notch inradius %.4f over %d admissible wall pairs (bound 0.5)'
          % (worst, n))
    assert worst < 0.5


def test_g_min():
    gm, td = A.g_min_exact()
    assert abs(gm - A.g_min()[0]) < 1e-5
    assert 2.0 * gm > 2.0 * (4.0 - 3.82) + 1e-6
    print('  g_min: %.5f at %.3f deg; 2 g_min = %.5f > 2 (4 - 3.82) = %.5f' % (gm, td, 2 * gm, 0.36))


def test_gap_lemma():
    g = F.gap_lemma(XW, SW)
    assert all(w['ok'] for w in g['walls'])
    print('  gap_lemma: the witness ring\'s four wall gaps %s (bound %.4f)'
          % ([round(w['gap'], 4) for w in g['walls']], 4.0 - SW))


def test_witness_pierce():
    poses, _, _ = F.poses_of(XW, SW)
    mem = [(p[0], p[1], p[2], 0.5) for p in poses]
    v = C.pierce(mem, SW, [(SW / 2, SW / 2)], step_deg=1.0)
    print('  witness: PIERCE(1) residual %.3e at the centre (A249: 0)' % v)
    assert v <= 1e-9
    D = Point(SW / 2, SW / 2).buffer(0.5, 64)
    assert all(Polygon(C.G237.sq_verts(p[0], p[1], p[2], 0.5)).intersection(D).area < 1e-9
               for p in poses)


if __name__ == '__main__':
    print('A251 tests')
    test_g_min()
    test_gap_lemma()
    test_inradius()
    test_three_disc()
    test_mid_notch()
    test_witness_pierce()
    test_pierce_monotone()
    test_core_sound()
    print('all A251 tests passed')
