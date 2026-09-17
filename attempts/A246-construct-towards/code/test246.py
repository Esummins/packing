"""A246 self-tests: the new lemmas on grids / random samples, the interval enclosures' soundness.
    python test246.py
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom246 as G                                   # noqa: E402
import interval246 as IV                              # noqa: E402
import cells244 as C                                  # noqa: E402


def test_square_in_triangle():
    """Lemma C: h(phi) >= (al + be)(1 - w(phi)/2) for al, be > 0, phi in [0, 90 deg] -- the inequality
    behind SQUARE-IN-TRIANGLE -- and no unit square fits in a right triangle with 1/a + 1/b > 1."""
    worst = 1e9
    for phi in np.linspace(0, math.pi / 2, 721):
        c, s = math.cos(phi), math.sin(phi)
        for al in np.linspace(0.05, 5, 60):
            for be in np.linspace(0.05, 5, 60):
                h = (abs(al * c + be * s) + abs(-al * s + be * c)) / 2
                worst = min(worst, h - (al + be) * (1 - (c + s) / 2))
    assert worst >= -1e-12, worst
    rng = np.random.default_rng(1)
    for _ in range(20000):
        a, b = rng.uniform(1.0, 2.5, 2)
        if 1 / a + 1 / b <= 1:
            continue
        cx, cy, th = rng.uniform(0.5, 1.5), rng.uniform(0.5, 1.5), rng.uniform(0, math.pi / 2)
        q = C.square_corners(cx, cy, th)
        inside = (q[:, 0] >= 0).all() and (q[:, 1] >= 0).all() and (q[:, 0] / a + q[:, 1] / b <= 1).all()
        assert not inside, (a, b, cx, cy, th)
    print('square-in-triangle: ok, worst slack %.2e' % worst)


def test_not_self_sufficient():
    """Lemma D: two disjoint squares in the quadrant never BOTH meet all three cells of a corner
    to depth >= 1e-3 (random search over 200k pairs)."""
    rng = np.random.default_rng(2)
    cells = [(0, 1, 0, 1), (0, 1, 1, 2), (1, 2, 0, 1)]
    hits = 0
    for _ in range(200000):
        a = (rng.uniform(0.5, 1.8), rng.uniform(0.5, 1.8), rng.uniform(0, math.pi / 2))
        b = (rng.uniform(0.5, 1.8), rng.uniform(0.5, 1.8), rng.uniform(0, math.pi / 2))
        if min(C.overlap_depth(*a, r) for r in cells) < 1e-3 or min(C.overlap_depth(*b, r) for r in cells) < 1e-3:
            continue
        if C.square_corners(*a).min() < 0 or C.square_corners(*b).min() < 0:
            continue                                   # not in the closed quadrant
        if pair_depth_ref(a, b) <= 0:
            hits += 1
            print('  counterexample?', a, b)
    assert hits == 0, hits
    print('not-self-sufficient: ok (no disjoint pair among the random both-triple meeters)')


def test_max_five():
    """Lemma B at s-hat: one square meets <= 5 cells, and a square meeting no box <= 4 (grid)."""
    s = G.SHAT
    rects = {n: C.cell_rect(n, s) for n in C.CELLS}
    best, best_free = 0, 0
    for cx in np.linspace(0.5, s - 0.5, 61):
        for cy in np.linspace(0.5, s - 0.5, 61):
            for th in np.linspace(0, math.pi / 2, 31):
                met = [n for n, r in rects.items() if C.overlap_depth(cx, cy, th, r) > 1e-9]
                best = max(best, len(met))
                if not any(n.endswith('00') for n in met):
                    best_free = max(best_free, len(met))
    assert best <= 5 and best_free <= 4, (best, best_free)
    print('max-five: ok (max %d cells, free max %d)' % (best, best_free))


def test_rprime():
    """R'(th, delta) = w(th) - (delta - sin th) tan th >= 1 for sin th <= delta <= 1."""
    worst = 1e9
    for th in np.linspace(1e-4, math.pi / 2 - 1e-4, 4000):
        for d in np.linspace(math.sin(th), 1.0, 50):
            worst = min(worst, G.w(th) - (d - math.sin(th)) * math.tan(th) - 1.0)
    assert worst >= -1e-9, worst
    print("R' >= 1: ok, worst slack %.2e" % worst)


def test_interval_soundness():
    """random boxes, random points inside: the point depth lies within the enclosure."""
    rng = np.random.default_rng(3)
    rect = (0.0, 1.0, 0.0, 1.0)
    worst = 0.0
    for _ in range(3000):
        lo = np.array([rng.uniform(0, 1.5), rng.uniform(0, 1.5), rng.uniform(0, 1.4),
                       rng.uniform(0, 1.5), rng.uniform(0, 1.5), rng.uniform(0, 1.4)])
        wd = rng.uniform(0, 0.2, 6)
        hi = np.minimum(lo + wd, [3, 3, math.pi / 2, 3, 3, math.pi / 2])
        box = np.stack([lo, hi])[None]
        pa, pb = IV.pose_of(box, 0), IV.pose_of(box, 3)
        dr = IV.depth_rect(pa, rect)
        dp = IV.depth_pair(pa, pb)
        for _ in range(5):
            p = lo + rng.uniform(0, 1, 6) * (hi - lo)
            v = C.overlap_depth(p[0], p[1], p[2], rect)
            worst = max(worst, dr[0][0] - v, v - dr[1][0])
            vp = IV.depth_pair_pt(p[:3], p[3:])
            v2 = pair_depth_ref(p[:3], p[3:])
            worst = max(worst, dp[0][0] - v2, v2 - dp[1][0], abs(vp - v2))
    assert worst <= 1e-12, worst
    print('interval enclosures: sound on 15000 samples (worst excess %.1e)' % worst)


def pair_depth_ref(a, b):
    """reference SAT depth of two unit squares (vertex projections)."""
    qa, qb = C.square_corners(*a), C.square_corners(*b)
    best = 1e9
    for th in (a[2], b[2]):
        for n in C.square_normals(th):
            pa, pb = qa @ n, qb @ n
            best = min(best, min(pa.max(), pb.max()) - max(pa.min(), pb.min()))
    return float(best)


def test_slotmet_alive():
    """the B&B keeps the initial box, discards a narrow box of two (overlapping) copies of one
    admissible square, and discards one whose cap violates v >= cos th."""
    import slotmet246 as S
    ok, _ = S.alive(S.INIT.T[None].copy(), 1e-3)
    assert bool(ok[0])
    b = np.array([[0.30, 0.1, 0.96, 0.30, 0.1, 0.96], [0.301, 0.101, 0.961, 0.301, 0.101, 0.961]])[None]
    ok1, dp = S.alive(b, 1e-3)
    assert not bool(ok1[0]) and dp[0][0] > 0.5
    b2 = b.copy()
    b2[0, :, 2] = [0.10, 0.11]                   # v_A = 0.1 < cos(0.3) = 0.955
    b2[0, :, 5] = [0.90, 0.91]
    ok2, _ = S.alive(b2, 1e-3)
    assert not bool(ok2[0])
    print('slotmet alive/discard: ok')


if __name__ == '__main__':
    test_square_in_triangle()
    test_not_self_sufficient()
    test_max_five()
    test_rprime()
    test_interval_soundness()
    test_slotmet_alive()
    print('all tests passed')
