"""A223 tests: handedness calculus, the ring's grains and chain formula, the click LP at t = 0 reproduces the witness,
the flush end, Lemma FLUSH numerically (the LP with 11 flat squares never goes below 4).
    python test223.py
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import grains223 as GR        # noqa: E402
import click223 as CK         # noqa: E402
import geom217 as G           # noqa: E402


def test_handedness():
    assert GR.handedness(math.radians(20)) == '+' and GR.handedness(math.radians(70)) == '-'
    assert GR.handedness(math.radians(110)) == '+' and GR.handedness(-math.radians(20)) == '-'      # rotation keeps, reflection swaps
    assert GR.handedness(0.0) == 'F' and GR.handedness(math.pi / 2) == 'F' and GR.handedness(math.pi / 4) == 'D'


def test_ring():
    w = [x for x in GR.four_crowds() if x['rid'] == GR.RING][0]
    g = GR.grains(w)
    gs = {tuple(x['members']): x['hand'] for x in g['grains']}
    assert gs[(2, 3, 4, 5)] == '-' and gs[(6, 7, 8, 10)] == '+' and gs[(9,)] == 'F', gs
    kinds = sorted((b['kind'], tuple(b['pair'])) for b in g['boundaries'])
    assert kinds == [('FLAT', (3, 9)), ('FLAT', (9, 10)), ('LEAN', (4, 6))], kinds
    assert g['rattlers'] == [0, 1] and g['walls_covered'] == ['x=0', 'x=s', 'y=0', 'y=s']
    # the left ladder's chain formula s = (c+s) + (2+sig0) s + (1+sig1+sig2) c with the measured offsets
    z = np.array(w['z'])
    cx, cy, th, s = G.unpack(z)
    t = th[4]
    u = lambda i: cx[i] * math.cos(t) + cy[i] * math.sin(t)          # noqa: E731
    v = lambda i: -cx[i] * math.sin(t) + cy[i] * math.cos(t)         # noqa: E731
    assert abs(v(5) - v(4) - 1) < 1e-6
    assert abs(u(2) - u(5) - 1) < 1e-6 and abs(u(3) - u(2) - 1) < 1e-6
    sig = (u(5) - u(4), v(2) - v(5), v(3) - v(2))
    formula = (math.cos(t) + math.sin(t)) + (2 + sig[0]) * math.sin(t) + (1 + sig[1] + sig[2]) * math.cos(t)
    assert abs(formula - s) < 1e-6, (formula, s, sig)


def test_click_ring():
    w = [x for x in GR.four_crowds() if x['rid'] == GR.RING][0]
    z0 = np.array(w['z'])
    A = CK.path(z0, list(range(G.N)), True, 4)
    assert abs(A['s'][0] - z0[G.S_IDX]) < 1e-6, A['s']            # t = 0 reproduces the witness's side
    assert A['blocked_at'] is None and abs(A['s_end'] - 4.0) < 1e-9 and A['monotone'], A
    z1 = np.array(A['z_end'])
    assert all(GR.handedness(v) == 'F' for v in z1[2:33:3])         # flush end
    ok, gap, wall = CK.RG.exact_check(z1)
    assert ok, (gap, wall)


def test_flush_floor():
    """Lemma FLUSH numerically: 11 flat squares, random selections, LP side never below 4."""
    rng = np.random.default_rng(1)
    idx = list(range(G.N))
    th = np.zeros(G.N)
    for _ in range(20):
        c = rng.uniform(0.5, 4.5, 2 * G.N)
        cc, s, sel, it = CK.fixed_tilt_min(c, th, idx, {})
        assert cc is None or s >= 4 - 1e-9, s


if __name__ == '__main__':
    for f in (test_handedness, test_ring, test_click_ring, test_flush_floor):
        f()
        print(f.__name__, 'ok')
