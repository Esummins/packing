"""A248 tests: the POKE witness (exact), TOP-2 / FLAT-ABOVE / TILT-MIN on random pokers, the click
accounting against the depth functional, the wall frames, and the corpus invariants.

    python test248.py
"""
import json
import math
import os
import random
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import geom248 as G                                                   # noqa: E402


def test_witness():
    f = G.poke_witness_exact()
    assert f['disjoint_from_A'] and f['touches_wall'] and f['V_in_box'] and f['top_ge_2']
    assert not f['lowest_nearer_wall_than_highest'], 'the CW witness must refute POKE'
    B = G.poker(math.atan2(4, 3), 0.1)
    A = G.flat_floor(0.95)
    assert G.poly_gap(A, B) > 0 and G.depth_rect(B, (0, 1, 0, 1)) > 0
    assert G.poke_facts(B, 0.95)['sense'] == 'CW'


def test_top2_and_tiltmin(n=20000, seed=248):
    """random pokers beside a flat floor meeter: disjoint => depth <= TILT-MIN bound, top >= 2,
    and no flat wall square with 0 < y0 < 2 is disjoint from the poker."""
    rng = random.Random(seed)
    checked = 0
    for _ in range(n):
        delta = rng.uniform(0.05, 0.999)
        th = rng.uniform(0.001, math.pi / 2 - 0.001)
        xv = rng.uniform(math.sin(th), min(1.0, delta))
        d = rng.uniform(0.0, 1.2 * (delta - xv) * math.tan(th) + 1e-3)
        B = G.poker(th, d, x_v=xv)
        if G.poly_gap(G.flat_floor(delta), B) < 0 or G.depth_rect(B, (0, 1, 0, 1)) <= 0:
            continue
        checked += 1
        pf = G.poke_facts(B, delta)
        assert pf['d_v'] <= pf['tiltmin_bound'] + 1e-9, (delta, th, d, xv)
        assert pf['top'] >= 2 - 1e-9, (delta, th, d, xv, pf['top'])
        y0 = rng.uniform(0.0, 2.0)
        W = np.array([(0, y0), (1, y0), (1, y0 + 1), (0, y0 + 1)], float)
        assert G.poly_gap(W, B) < 0, ('FLAT-ABOVE', delta, th, d, xv, y0)
    assert checked > 1000
    # the identity behind TOP-2
    for _ in range(100000):
        t = rng.uniform(1e-6, math.pi / 2 - 1e-6)
        assert (1 - math.sin(t)) * math.tan(t) <= G.w(t) - 1 + 1e-9


def test_click_account(seed=3):
    """the flush stack's depths: [0,1]x[1,2] has depth 0 at every corner, [0,1]x[2,3] has depth
    4 - s at TL (s in [3, 4)) and 0 elsewhere."""
    rng = random.Random(seed)
    for _ in range(200):
        s = rng.uniform(3.0, 3.999)
        lo = np.array([(0, 1), (1, 1), (1, 2), (0, 2)], float)
        hi = np.array([(0, 2), (1, 2), (1, 3), (0, 3)], float)
        for wall in G.WALLS:
            pass
        assert G.depth_corner(lo) == 0 and G.depth_corner(G.flip_up(lo, s)) == 0
        assert abs(G.depth_corner(G.flip_up(hi, s)) - (4 - s)) < 1e-12 and G.depth_corner(hi) == 0
        assert abs(G.click_gain(0.1, 0.05, s) - ((4 - s) - 0.15)) < 1e-12


def test_frames(seed=5):
    rng = np.random.default_rng(seed)
    for _ in range(200):
        s = rng.uniform(3.8, 4.5)
        V = G.verts((rng.uniform(0.8, s - 0.8), rng.uniform(0.8, s - 0.8), rng.uniform(0, 1.5)))
        for wl in G.WALLS:
            W = G.to_wall(V, wl, s)
            assert np.allclose(G.from_wall(W, wl, s), V)
            e0, e1 = V[1] - V[0], W[1] - W[0]
            assert abs(np.linalg.det(np.array([e0, V[3] - V[0]])) - np.linalg.det(np.array([e1, W[3] - W[0]]))) < 1e-9


def test_mu():
    sq = np.array([(0.3, 0.7), (1.3, 0.7), (1.3, 1.7), (0.3, 1.7)], float)
    assert abs(G.mu_corner(sq) - 0.7) < 1e-12
    for _ in range(300):
        V = G.verts((random.uniform(0.6, 1.5), random.uniform(0.6, 1.5), random.uniform(0, 1.5)))
        pts = np.array([V[0] + a * (V[1] - V[0]) + b * (V[3] - V[0]) for a in np.linspace(0, 1, 41)
                        for b in np.linspace(0, 1, 41)])
        assert G.mu_corner(V) <= np.max(pts, axis=1).min() + 1e-12
        assert G.mu_corner(V) >= np.max(pts, axis=1).min() - 2e-2


def test_corpus_file():
    p = os.path.join(ATT, 'results', 'chase248.jsonl')
    if not os.path.exists(p):
        return
    rows = [json.loads(l) for l in open(p, encoding='utf-8')]
    cor = [r for r in rows if not r['kind'].startswith('fj')]
    assert len(cor) == 764
    for r in cor:
        for v in r['views']:
            if 'poke' in v:
                pf = v['poke']
                assert not pf['flat_above'] and pf['top_ge_2'] and pf['sin_le_delta']
                assert pf['d_v'] <= pf['tiltmin_bound'] + 1e-5


if __name__ == '__main__':
    for name, fn in sorted(globals().items()):
        if name.startswith('test_'):
            fn()
            print('ok', name)
