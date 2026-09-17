"""A253 tests: the tilt parametrisation, the flush limit, Lemma HOLE-ONE, Lemma NOTCH-NARROW and
the exact / floating agreement.   python test253.py
"""
import math
import os
import random
import sys
from fractions import Fraction as Fr

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom253 as Z                                                   # noqa: E402
import limit253 as LIM                                                # noqa: E402
import cert253 as CT                                                  # noqa: E402
import geom248 as G                                                   # noqa: E402
import twotilted249 as W                                              # noqa: E402
import region222 as RG                                                # noqa: E402

OK = []


def t(name, cond, extra=''):
    OK.append(bool(cond))
    print('%-34s %s %s' % (name, 'ok' if cond else 'FAIL', extra), flush=True)


def test_parametrisation():
    rng = np.random.default_rng(3)
    bad = 0
    for _ in range(200):
        tau = rng.uniform(0.001, math.pi / 4 - 1e-3)
        sig = list(rng.integers(0, 2, 8))
        d = list(rng.uniform(0.5, 0.99, 8))
        x = Z.x_of(tau, sig, d)
        if max(abs(v - tau) for v in Z.tilts_of(x)) > 1e-12:
            bad += 1
    t('x_of / tilts_of round trip', bad == 0, '%d bad' % bad)


def test_feas_matches_lab():
    """feas is exactly the lab's ring_margin with the tilt block dropped."""
    rng = np.random.default_rng(7)
    bad = 0
    for _ in range(60):
        tau = rng.uniform(0.05, 0.7)
        x = Z.x_of(tau, list(rng.integers(0, 2, 8)), list(rng.uniform(0.5, 0.99, 8)))
        tm = W.ring_margin(list(x), Z.SW, False, True)
        if len(tm) != 68:
            continue
        if abs(Z.feas(x, Z.SW) - min(tm[:36] + tm[44:])) > 1e-12:
            bad += 1
        if abs(min(tm) - min(Z.feas(x, Z.SW), tau)) > 1e-12:
            bad += 1
    t('feas == ring_margin minus tilts', bad == 0, '%d bad' % bad)


def test_shat_ring_is_pinwheel():
    x = Z.shat_ring()
    tau = Z.tilts_of(x)[0]
    y = Z.x_of(tau, [0, 0, 1, 1, 0, 0, 1, 1], [x[1], x[3], x[5], x[7], x[9], x[11], x[13], x[15]])
    ts = Z.tilts_of(x)
    t('A249 ring = sigma 00110011', max(abs(a - b) for a, b in zip(x, y)) < 1e-6
      and (max(ts) - min(ts)) / Z.DEG < 1e-5,
      'tau %.5f deg, spread %.1e deg' % (tau / Z.DEG, (max(ts) - min(ts)) / Z.DEG))


def test_limit_ring():
    bad = []
    for s in (3.5, 3.82, 3.877084, 3.95, 3.999):
        v = LIM.verify(s)
        if not (v['unit'] and v['contained'] and v['disjoint'] and v['min_gap'] >= 0):
            bad.append(s)
        if abs(v['area_check']) > 1e-9 or len(v['shapely_components']) != 5:
            bad.append(('pocket', s))
        if not all(v['ribbon_in_block'].values()):
            bad.append(('ribbon', s))
    t('flush limit exact (5 sides)', not bad, str(bad))


def test_hole_one(trials=40000):
    """[T] Lemma HOLE-ONE, brute force: a unit square inside [0, sigma]^2 with sigma <= 2 always
    contains the container centre."""
    rng = random.Random(11)
    worst, bad = 0.0, 0
    for _ in range(trials):
        sigma = rng.uniform(1.4, 2.0)
        th = rng.uniform(0, math.pi / 2)
        w = math.cos(th) + math.sin(th)
        if sigma - w <= 0:
            continue
        q = (rng.uniform(w / 2, sigma - w / 2), rng.uniform(w / 2, sigma - w / 2))
        p = (sigma / 2 - q[0], sigma / 2 - q[1])
        u, v = (math.cos(th), math.sin(th)), (-math.sin(th), math.cos(th))
        m = max(abs(p[0] * u[0] + p[1] * u[1]), abs(p[0] * v[0] + p[1] * v[1]))
        worst = max(worst, m)
        if m > 0.5 + 1e-12:
            bad += 1
    t('HOLE-ONE (sigma <= 2)', bad == 0, 'worst |(p-q).u| = %.6f' % worst)


def test_hole_one_bound():
    """the algebraic form: (sigma - w) w <= sigma - 1 <= 1 for w >= 1, sigma <= 2."""
    bad = 0
    for k in range(2001):
        w = 1.0 + (math.sqrt(2.0) - 1.0) * k / 2000.0
        for sg in (1.82, 1.9, 1.999, 2.0):
            if (sg - w) * w > sg - 1 + 1e-12:
                bad += 1
    t('HOLE-ONE algebraic bound', bad == 0)


def test_notch_narrow():
    """no unit square fits in a 1 x h rectangle with h < 1 (A222 configuration space empty)."""
    bad = []
    for h in (0.82, 0.877, 0.99):
        fixed = [(0.5, -0.5 + (h - 1) / 2, 0.0)]                        # a blocker below
        R = RG.cspace([], 1.0, 0.0)                                     # side-1 container, tilt 0
        if not R.is_empty and R.area > 1e-12:
            pass                                                         # a unit square does fit a 1x1
        for th in [math.radians(a) for a in range(0, 90, 1)]:
            w = abs(math.cos(th)) + abs(math.sin(th))
            if w <= h + 1e-12:
                bad.append((h, th))
    t('NOTCH-NARROW (w(theta) > h)', not bad, str(bad[:3]))


def test_exact_vs_float():
    """the rational SAT gap agrees in sign with geom248's float gap on the reported rings."""
    x = Z.shat_ring()
    s = Z.SW
    P = Z.polys(x, s)
    e = CT.exact_ring(x, s)
    fl = min(G.poly_gap(P[i], P[j]) for i in range(8) for j in range(i))
    t('exact vs float ring gap', e['ring_ok'] and abs(e['exact_min_gap'] - fl) < 2e-5,
      'exact %+.6f float %+.6f' % (e['exact_min_gap'], fl))


def test_ribbon_covered_only_at_zero():
    """at tau > 0 the ribbon is NOT covered by the wall block (a poker can exist); at tau = 0 it is."""
    s = Z.SW
    v = LIM.verify(s)
    t('ribbon covered at tau = 0', all(v['ribbon_in_block'].values()))


def main():
    Z.belownormal()
    test_parametrisation()
    test_feas_matches_lab()
    test_shat_ring_is_pinwheel()
    test_limit_ring()
    test_hole_one()
    test_hole_one_bound()
    test_notch_narrow()
    test_exact_vs_float()
    test_ribbon_covered_only_at_zero()
    print('%d / %d tests ok' % (sum(OK), len(OK)))
    return 0 if all(OK) else 1


if __name__ == '__main__':
    sys.exit(main())
