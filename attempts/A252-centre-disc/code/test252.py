"""A252 tests: the centre-set metrics against direct geometry, the closed forms of lemmas252
(MOUTH, NOTCH-SEP, TWO-VERTEX, the flat limit), the capacity criteria on sampled rings, and
the [F] witness (far_O > 1/sqrt3 on a feasible ring when adv252 rows exist).

    python test252.py
"""
import json
import math
import os
import sys

import numpy as np
from shapely.geometry import Point, Polygon

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import disc252 as D                                                   # noqa: E402
import lemmas252 as L                                                 # noqa: E402
import geom249 as T                                                   # noqa: E402

SEED = [0.254, 0.891, 0.254, 0.695, 1.317, 0.695, 1.317, 0.891]
XW = list(SEED[:4]) + list(SEED[4:8]) + list(SEED[:4]) + list(SEED[4:8])


def test_centre_set_direct(n=400, seed=3):
    """C = P (-) D_{1/2}: sampled points of C have disc-distance >= 1/2 to every square and wall;
    points of P at distance < 1/2 from a square are not in C."""
    rng = np.random.default_rng(seed)
    polys, _ = D.ring(XW, D.SW)
    C = D.centre_set(polys, D.SW)
    P = D.pocket(polys, D.SW)
    bad = 0
    for _ in range(n):
        q = (rng.uniform(0.5, D.SW - 0.5), rng.uniform(0.5, D.SW - 0.5))
        dmin = min(min(Polygon(V).distance(Point(q)) for V in polys), q[0], q[1], D.SW - q[0], D.SW - q[1])
        inC = C.contains(Point(q))
        if inC and dmin < 0.5 - 2e-3:
            bad += 1
        if (not inC) and dmin > 0.5 + 2e-3 and P.contains(Point(q)):
            bad += 1
    assert bad == 0, bad
    return 'centre set vs direct distances: 0 disagreements on %d samples' % n


def test_far_point_contacts():
    m = D.metrics(XW, D.SW)
    c = m['contacts']
    assert abs(c[0][1] - 0.5) < 1e-3 and abs(c[1][1] - 0.5) < 1e-3, c
    assert m['far_O'] < D.R3 and m['sec_r'] < D.R3 and m['halves_diam'] < 1 and m['disp3'] < 1
    return 'far point of the s-hat ring touches %s and %s at 1/2; far_O %.4f sec %.4f halves %.4f disp3 %.4f' % (
        c[0][0], c[1][0], m['far_O'], m['sec_r'], m['halves_diam'], m['disp3'])


def test_mouth_centre(n=300, seed=5):
    """the two-line contact point is at distance exactly 1/2 from both edge LINES."""
    rng = np.random.default_rng(seed)
    worst = 0.0
    for _ in range(n):
        tB, tA = rng.uniform(0.05, 1.5, 2)
        dB, dA = rng.uniform(0.41, 1.0, 2)
        q = L.mouth_centre(tB, dB, tA, dA)
        if q is None:
            continue
        V = (math.sin(tB), dB)
        TA = (dA + math.cos(tA), math.sin(tA) + math.cos(tA))
        d1 = (q[0] - V[0]) * math.sin(tB) - (q[1] - V[1]) * math.cos(tB)
        d2 = (q[0] - TA[0]) * math.cos(tA) + (q[1] - TA[1]) * math.sin(tA)
        worst = max(worst, abs(d1 - 0.5), abs(d2 - 0.5))
    assert worst < 1e-9, worst
    q = L.mouth_centre(math.radians(88), 0.98, math.radians(89), 0.99)
    assert abs(q[0] - 1.5) < 0.06 and abs(q[1] - 1.5) < 0.06, q
    return 'mouth centre exact on %d draws; near the flat limit -> %s ~ (1.5, 1.5)' % (n, tuple(round(v, 3) for v in q))


def test_flat_limit():
    assert abs(D.flat_limit_far(D.S_FLAT) - D.R3) < 1e-12
    assert D.flat_limit_far(3.82) > D.R3 and D.flat_limit_far(3.8) < D.R3
    return 'flat limit (s/2 - 3/2) sqrt2 crosses 1/sqrt3 at s = %.5f < 3.82' % D.S_FLAT


def test_notch_sep(n=2000, seed=7):
    """a disc of radius 1/2 in the corner notch behind B's edge L->V and A's edge V_A->W
    (direct check) implies theta_B > 45 deg and delta_B >= phi(theta_B), mirror for A."""
    rng = np.random.default_rng(seed)
    hits, viol = 0, 0
    for _ in range(n):
        tB, dB, tA, dA = rng.uniform(0.02, 1.55), rng.uniform(0.41, 1), rng.uniform(0.02, 1.55), rng.uniform(0.41, 1)
        B, A = T.wall_square(tB, dB), T.floor_square(tA, dA)
        q = (rng.uniform(0.5, 1.5), rng.uniform(0.5, 1.5))
        L_ = B[3]
        behindB = (q[0] - L_[0]) * math.cos(tB) + (q[1] - L_[1]) * math.sin(tB) <= -0.5
        VA = A[0]
        behindA = (q[0] - VA[0]) * math.cos(tA) + (q[1] - VA[1]) * math.sin(tA) <= -0.5
        if behindB and behindA:
            hits += 1
            if not (tB > math.pi / 4 and dB >= L.phi(tB) - 1e-9 and tA < math.pi / 4 and dA >= L.phi(math.pi / 2 - tA) - 1e-9):
                viol += 1
    assert viol == 0, viol
    return 'NOTCH-SEP: %d notch discs on %d draws, 0 violations of the phi bound' % (hits, n)


def test_two_vertex(n=200, seed=9):
    rng = np.random.default_rng(seed)
    for _ in range(n):
        P1, P2 = rng.uniform(0, 2, 2), rng.uniform(0, 2, 2)
        d = math.dist(P1, P2)
        if d > 1:
            continue
        M = (P1 + P2) / 2
        u = (P2 - P1) / d
        h = math.sqrt(0.25 - d * d / 4)
        q = M + h * np.array([-u[1], u[0]])
        assert abs(math.dist(q, P1) - 0.5) < 1e-12 and abs(math.dist(q, P2) - 0.5) < 1e-12
        O = rng.uniform(0, 2, 2)
        assert math.dist(q, O) <= L.two_vertex_bound(P1, P2, O) + 1e-12
    return 'TWO-VERTEX bound holds on random pairs'


def test_witness_rows():
    fn = os.path.join(ATT, 'results', 'adv252.jsonl')
    if not os.path.exists(fn):
        return 'no adversarial rows yet'
    best = None
    for line in open(fn, encoding='utf-8'):
        r = json.loads(line)
        if r['metric'] == 'far_O' and r['margin'] >= 0 and (best is None or r['value'] > best['value']):
            best = r
    if best is None:
        return 'no feasible far_O row yet'
    m = D.metrics(best['x'], float(best['side']))
    assert m['margin'] >= 0 and abs(m['far_O'] - best['value']) < 0.02
    return 'best feasible far_O row: side %s far_O %.4f (1/sqrt3 = %.5f) margin %+.4f -> CENTRE-DISC about O %s' % (
        best['side'], m['far_O'], D.R3, m['margin'], 'FALSE' if m['far_O'] > D.R3 else 'not refuted')


if __name__ == '__main__':
    D.belownormal()
    for f in (test_centre_set_direct, test_far_point_contacts, test_mouth_centre, test_flat_limit,
              test_notch_sep, test_two_vertex, test_witness_rows):
        print('  %s: %s' % (f.__name__, f()))
    print('all A252 tests passed')
