"""A233 tests: the two inequalities behind Lemma RADIAL and the LOCALITY constants, on random configurations;
the census formula; the RADIAL identity on every witness corner already in results/arm233.jsonl.
    python test233.py
"""
import json
import math
import os
import random
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'A222-ring-swap', 'code'))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'A217-torque-probe', 'code'))
import draw222 as D            # noqa: E402
import census233 as C          # noqa: E402

SQ2 = math.sqrt(2)


def support(pose, n):
    """support function h_Q(n) = n.c + g_Q(n)."""
    cx, cy, th = pose
    e = (math.cos(th), math.sin(th))
    ep = (-math.sin(th), math.cos(th))
    return n[0] * cx + n[1] * cy + (abs(n[0] * e[0] + n[1] * e[1]) + abs(n[0] * ep[0] + n[1] * ep[1])) / 2


def test_pair_row_term(trials=3000):
    """for an interior-disjoint pair with separating axis n (an edge normal of the owner), n.(c_j - c_i) >= 1."""
    rng = random.Random(233)
    worst = 9.0
    for _ in range(trials):
        p = (rng.uniform(1, 3), rng.uniform(1, 3), rng.uniform(0, math.pi / 2))
        q = (rng.uniform(0, 4), rng.uniform(0, 4), rng.uniform(0, math.pi / 2))
        if D.sep(p, q) < 0:
            continue
        for th in (p[2], q[2]):
            own, oth = (p, q) if th == p[2] else (q, p)
            for ax in ((math.cos(th), math.sin(th)), (-math.sin(th), math.cos(th)), (-math.cos(th), -math.sin(th)), (math.sin(th), -math.cos(th))):
                gap = -support(oth, (-ax[0], -ax[1])) - support(own, ax)   # min_oth n.q - max_own n.q
                if gap >= -1e-12:                                          # a separating axis
                    worst = min(worst, ax[0] * (oth[0] - own[0]) + ax[1] * (oth[1] - own[1]))
    assert worst >= 1 - 1e-9, worst
    return worst


def test_locality(trials=20000):
    """a meeter's centre is < 1 + 1/sqrt2 in each frame coordinate; two touching squares have |dc|_inf <= sqrt2."""
    rng = random.Random(7)
    cmax, dmax = 0.0, 0.0
    for _ in range(trials):
        p = (rng.uniform(0.5, 2.0), rng.uniform(0.5, 2.0), rng.uniform(0, math.pi / 2))
        v = np.array(D.sq_verts(*p))
        if v.min() < 0:
            continue
        if v[:, 0].min() < 1 - 1e-9 and v[:, 1].min() < 1 - 1e-9:   # meets the open box (a vertex inside)
            cmax = max(cmax, p[0], p[1])
        q = (p[0] + rng.uniform(-1.5, 1.5), p[1] + rng.uniform(-1.5, 1.5), rng.uniform(0, math.pi / 2))
        g = D.sep(p, q)
        if abs(g) < 2e-3:
            dmax = max(dmax, abs(p[0] - q[0]), abs(p[1] - q[1]))
    assert cmax < 1 + 1 / SQ2 + 1e-9, cmax
    assert dmax <= SQ2 + 5e-3, dmax
    return cmax, dmax


def test_census():
    assert C.holder_lists(0) == 1 and C.holder_lists(1) == 3 and C.holder_lists(2) == 6
    assert C.count(0) == sum(3 * C.WALL_OPTIONS[a] * 5 * C.WALL_OPTIONS[b] * 5 for i, a in enumerate(C.CELLS) for b in C.CELLS[i + 1:])
    return C.count(3)


def test_radial_identity():
    rs = [json.loads(l) for l in open(os.path.join(HERE, '..', 'results', 'arm233.jsonl'), encoding='utf-8')]
    rad = [r['radial'] for r in rs if r['radial']]
    res = max(abs(d['identity_residual']) for d in rad)
    neg = sum(d['internal'] < -1e-7 for d in rad)
    assert res < 1e-5 and neg == 0, (res, neg)
    return len(rad), res


if __name__ == '__main__':
    print('pair-row term min n.(cj-ci) =', test_pair_row_term())
    print('locality: max meeter centre coord, max |dc|_inf of touching pairs =', test_locality())
    print('census count(3) =', test_census())
    print('radial identity on witness corners (n, max residual) =', test_radial_identity())
    print('OK')
