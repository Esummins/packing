"""A249 tests: the closed-form cell predicates T-CELLS (T1) against exact SAT depths on random
wall / floor squares, Lemma T-TIP (the chord of A at height 1 avoids B's chord: A's tip enters
c01 only right of B's cap or under B's bottom edge) on random disjoint pairs, the mirror map, the
exact rational verification of the type-T ring witness (twotilted249 ring2 at s-hat) when present,
and the corpus invariants of chase249.jsonl.

    python test249.py
"""
import json
import math
import os
import random
import sys
from fractions import Fraction

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import geom249 as T                                                   # noqa: E402
import geom248 as G                                                   # noqa: E402


def test_cells(n=30000, seed=249):
    rng = random.Random(seed)
    checked = 0
    for _ in range(n):
        th, d = rng.uniform(0.001, math.pi / 2 - 0.001), rng.uniform(0.0, 1.3)
        for kind, sq, preds in (('B', T.wall_square(th, d), (T.B_meets_c00, T.B_meets_c01, T.B_meets_c10)),
                                ('A', T.floor_square(th, d), (T.A_meets_c00, T.A_meets_c01, T.A_meets_c10))):
            dep = [G.depth_rect(sq, T.CELLS_C[c]) for c in ('c00', 'c01', 'c10')]
            if min(abs(v) for v in dep) < 1e-7:
                continue
            checked += 1
            assert [v > 0 for v in dep] == [p(th, d) for p in preds], (kind, th, d, dep)
            t2, d2, g2 = T.frame_params(sq, kind)
            assert abs(t2 - th) < 1e-9 and abs(d2 - d) < 1e-9 and abs(g2) < 1e-9
    assert checked > 20000


def chord_A_at_1(th, dA):
    lam = (G.w(th) - 1) / (math.sin(th) * math.cos(th))
    return T.u_A_at_1(th, dA), T.u_A_at_1(th, dA) + lam


def chord_B_at_1(th, dB):
    ell = dB + math.cos(th)
    b1 = (ell - 1) * math.tan(th) if ell >= 1 else (1 - ell) / math.tan(th)
    return b1, T.u_B_at_1(th, dB)


def test_tip(n=40000, seed=7):
    """random disjoint (A floor, B wall) pairs both meeting c00: if A meets c01 then A's open
    chord at height 1 is disjoint from B's open chord at height 1 (right of B's cap, or under
    B's bottom edge when B's wall vertex is above 1)."""
    rng = random.Random(seed)
    seen = {'right': 0, 'under': 0}
    for _ in range(n):
        tB, dB = rng.uniform(0.01, math.pi / 2 - 0.01), rng.uniform(0.0, 0.999)
        tA, dA = rng.uniform(0.01, math.pi / 2 - 0.01), rng.uniform(0.0, 0.999)
        B, A = T.wall_square(tB, dB), T.floor_square(tA, dA)
        if G.poly_gap(A, B) < 1e-9 or not T.A_meets_c01(tA, dA):
            continue
        a1, a2 = chord_A_at_1(tA, dA)
        b1, b2 = chord_B_at_1(tB, dB)
        assert a1 >= b2 - 1e-9 or a2 <= b1 + 1e-9, (tA, dA, tB, dB, (a1, a2), (b1, b2))
        seen['right' if a1 >= b2 - 1e-9 else 'under'] += 1
        assert not T.B_meets_c10(tB, dB) or a2 <= b1 + 1e-9        # NSS: A on all three => B misses c10
    assert seen['right'] > 100, seen
    return seen


def test_mirror(n=2000, seed=3):
    rng = random.Random(seed)
    for _ in range(n):
        th, d = rng.uniform(0.01, math.pi / 2 - 0.01), rng.uniform(0.0, 1.0)
        B = T.wall_square(th, d)
        M = np.stack([B[:, 1], B[:, 0]], axis=1)                       # u <-> v
        A = T.floor_square(math.pi / 2 - th, d)
        assert np.allclose(np.sort(M, axis=0), np.sort(A, axis=0))


def rational_square(th, d, kind, den=10 ** 6):
    """the square with the tilt rationalised onto the unit circle (t = tan(th/2) rounded), exact."""
    t = Fraction(round(math.tan(th / 2) * den), den)
    co, si = (1 - t * t) / (1 + t * t), 2 * t / (1 + t * t)
    d = Fraction(round(d * den), den)
    if kind == 'B':
        L = (Fraction(0), d + co)
        V = (L[0] + si, L[1] - co)
    else:
        V = (d + si, Fraction(0))
    return [V, (V[0] + co, V[1] + si), (V[0] + co - si, V[1] + si + co), (V[0] - si, V[1] + co)]


def exact_gap(P, Q):
    """exact SAT: max over the 8 edge normals of the projection gap (Fractions; normals unnormalised)."""
    best = None
    for poly in (P, Q):
        for k in range(4):
            e = (poly[(k + 1) % 4][0] - poly[k][0], poly[(k + 1) % 4][1] - poly[k][1])
            nrm = (e[1], -e[0])
            a = [p[0] * nrm[0] + p[1] * nrm[1] for p in P]
            b = [q[0] * nrm[0] + q[1] * nrm[1] for q in Q]
            g = max(min(b) - max(a), min(a) - max(b))
            best = g if best is None or g > best else best
    return best


def test_ring_exact():
    fn = os.path.join(ATT, 'results', 'twotilted249_ring2.json')
    if not os.path.exists(fn):
        return 'no ring file'
    res = json.load(open(fn, encoding='utf-8'))
    key = '3.877084'
    if key not in res or res[key]['result']['sup_margin'] <= 0:
        return 'no positive ring at s-hat'
    x = res[key]['result']['x']
    s = Fraction(3877084, 10 ** 6)
    sq = []
    for k, corner in enumerate(('BL', 'BR')):
        tB, dB, tA, dA = x[:4] if k == 0 else x[4:8]
        for kind, th, d in (('B', tB, dB), ('A', tA, dA)):
            P = rational_square(th, d, kind)
            if corner == 'BR':
                P = [(s - p[0], p[1]) for p in P]
            sq.append(P)
            sq.append([(s - p[0], s - p[1]) for p in P])               # the C2 image
    # container, pairwise disjoint, every cell doubly met (exact)
    for P in sq:
        assert all(0 <= p[0] <= s and 0 <= p[1] <= s for p in P)
    for i in range(8):
        for j in range(i):
            assert exact_gap(sq[i], sq[j]) >= 0, (i, j)
    cells = {}
    for c, (X, Y) in (('BL', ((0, 1), (0, 1))), ('BR', ((s - 1, s), (0, 1))), ('TR', ((s - 1, s), (s - 1, s))), ('TL', ((0, 1), (s - 1, s)))):
        cells[c + '00'] = (X, Y)
        cells[c + '01'] = (X, (1, 2) if Y[0] == 0 else (s - 2, s - 1))
        cells[c + '10'] = ((1, 2) if X[0] == 0 else (s - 2, s - 1), Y)
    for name, (X, Y) in cells.items():
        R = [(X[0], Y[0]), (X[1], Y[0]), (X[1], Y[1]), (X[0], Y[1])]
        assert sum(exact_gap(P, R) < 0 for P in sq) >= 2, name
    return 'exact ring at s-hat verified (8 squares, 12 cells doubly met)'


def test_corpus_file():
    p = os.path.join(ATT, 'results', 'chase249.jsonl')
    if not os.path.exists(p):
        return
    rows = [json.loads(l) for l in open(p, encoding='utf-8')]
    assert len([r for r in rows if not r['kind'].startswith('fj')]) == 764
    for r in rows:
        for v in r['views']:
            if 'tt' not in v:
                continue
            t = v['tt']
            for k in ('A', 'B'):
                if 'pred_' + k in t and min(abs(t['cells_' + k][c]) for c in t['cells_' + k]) > 1e-6:
                    assert {c: t['cells_' + k][c] > 1e-9 for c in t['cells_' + k]} == t['pred_' + k], (r['rid'], v['corner'])


if __name__ == '__main__':
    for name, fn in sorted(globals().items()):
        if name.startswith('test_'):
            print('ok', name, fn() or '')
