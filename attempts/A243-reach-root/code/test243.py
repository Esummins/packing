"""A243 -- unit tests: the closed forms against geom239 (wrapped read-only), the summary map on the window crowd,
TILT-MIN on the type-F builder, the holder witness, the fibre sampler's invariants, the corner maps.  ~20 s."""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import leaves243 as L                                                   # noqa: E402
import price243 as P                                                    # noqa: E402

sys.path.insert(0, os.path.join(HERE, "..", "..", "A239-rings-below-4", "code"))
import geom239 as G                                                     # noqa: E402  (read-only)


def test_reach_matches_geom239():
    for th in (1.0, 10.0, 20.0, 33.79, 45.0, 60.0, 80.0):
        for d in (math.sin(th * L.DEG) + 0.02, 0.7, 0.98):
            assert abs(L.reach_F(th, d) - G.reach(th, d)) < 1e-12
    assert abs(L.theta_star(3.95) - G.theta_star(3.95)) < 1e-9


def test_pair_F_geometry():
    for th in (5.0, 20.0, 30.0, 57.0):
        d = math.sin(th * L.DEG) + 0.02
        A, B = L.pair_F(th, d)
        gA, gB = G.window_pair(th, d)
        assert max(abs(a - b) for a, b in zip(A, gA)) < 1e-12 and max(abs(a - b) for a, b in zip(B, gB)) < 1e-12
        assert L.in_quadrant(A) and L.in_quadrant(B) and L.meets_box(A) and L.meets_box(B)
        assert L.disjoint(A, B, tol=1e-9)
        assert L.tiltmin_ok(th, d)
        ru, rv, d1, d2 = L.summary(A, B)
        assert abs(ru - (1 + d)) < 1e-12                                 # A's far edge: the crowd's floor reach
        assert abs(rv - (1 - (d - math.sin(th * L.DEG)) * math.tan(th * L.DEG) + L.w_of(th * L.DEG))) < 1e-12
        assert abs(d1 - (1 - d)) < 1e-12 or abs(d2 - (1 - d)) < 1e-12   # the flat meeter's depth 1 - delta
        assert d1 + d2 <= 1 + 1e-12                                      # DEPTH-BUDGET


def test_depth_exact():
    # a flat square [a, a+1] x [b, b+1]: mu = max(a, b)
    for a, b in ((0.3, 0.6), (0.7, 0.2), (0.0, 0.9)):
        assert abs(L.mu((a + .5, b + .5, 0.0)) - max(a, b)) < 1e-12
    # a 45-degree diamond centred (c, c): mu = c - 1/sqrt 2 (the lower vertex on the diagonal)
    for c in (0.9, 1.2):
        assert abs(L.mu((c, c, math.pi / 4)) - (c - 1 / (2 * L.SQ2))) < 1e-12
    # brute force against a fine boundary sample
    rng = random.Random(1)
    for _ in range(200):
        p = (rng.uniform(0.5, 1.7), rng.uniform(0.5, 1.7), rng.uniform(0, math.pi / 2))
        V = L.verts(p)
        m = min(max(V[i][0] + t * (V[(i + 1) % 4][0] - V[i][0]), V[i][1] + t * (V[(i + 1) % 4][1] - V[i][1]))
                for i in range(4) for t in (k / 400.0 for k in range(401)))
        assert L.mu(p) <= m + 1e-12 and m - L.mu(p) < 5e-3


def test_holder_witness():
    A, C, f, ov, ylow = L.holder_witness()
    assert ov < 1e-12 and ylow > 0.5 and f[0] < 0 and f[1] < 0
    assert L.in_quadrant(C) and not L.meets_box(C)
    # the contact: A's corner lies on C's edge (distance 0), and C's edge normal is the force direction
    p = (1.36, 1.0)
    assert L.poly(C).exterior.distance(__import__("shapely.geometry", fromlist=["Point"]).Point(p)) < 1e-12
    # the page's witness (phi = 95): also disjoint from the window crowd's partner B
    d = math.sin(20 * L.DEG) + 0.02
    A2, B2 = L.pair_F(20.0, d)
    _, C2, f2, ov2, yl2 = L.holder_witness(delta=d, phi_deg=95.0)
    assert ov2 < 1e-12 and yl2 > 0.7 and f2[0] < -0.99 and L.disjoint(B2, C2) and L.disjoint(A2, C2) and not L.meets_box(C2)


def test_fibre_sampler():
    A, B = L.pair_F(20.0, math.sin(20 * L.DEG) + 0.02)
    cell = L.cell_around(A, B, 0.1)
    pairs, acc = L.sample_fibre(cell, 40, seed=3, tries=400000)
    assert len(pairs) == 40 and acc > 0
    for X, Y in pairs:
        ru, rv, d1, d2 = L.summary(X, Y)
        assert cell[0][0] - 1e-9 <= ru <= cell[0][1] + 1e-9 and cell[1][0] - 1e-9 <= rv <= cell[1][1] + 1e-9
        assert cell[2][0] - 1e-9 <= d1 <= cell[2][1] + 1e-9 and cell[3][0] - 1e-9 <= d2 <= cell[3][1] + 1e-9
        assert L.disjoint(X, Y) and L.in_quadrant(X) and L.in_quadrant(Y) and L.meets_box(X) and L.meets_box(Y)
    core = L.core_outer(pairs, 'deep')
    assert core.area <= min(L.poly(X).area for X, _ in pairs) + 1e-9


def test_corner_maps():
    S = 3.9
    Q = L.poly((0.8, 0.7, 0.3))
    for c in ('BL', 'BR', 'TL', 'TR'):
        R = P.to_corner(Q, c, S, alternate=False)
        assert abs(R.area - 1.0) < 1e-12
        b = R.bounds
        assert -1e-9 <= b[0] and b[2] <= S + 1e-9 and -1e-9 <= b[1] and b[3] <= S + 1e-9
    assert abs(P.to_corner(Q, 'TR', S).centroid.x - (S - 0.8)) < 1e-9
    assert abs(P.to_corner(Q, 'BR', S).centroid.x - (S - 0.7)) < 1e-9 and abs(P.to_corner(Q, 'BR', S).centroid.y - 0.8) < 1e-9


def test_wall_slot():
    import wallslot243 as W
    from shapely.ops import unary_union
    for S in (3.82, L.SHAT, 3.99):
        cells = W.cells12(S)
        assert len(cells) == 12 and all(abs(b.area - 1) < 1e-12 for _, b in cells)
        cont = __import__("shapely.geometry", fromlist=["box"]).box(0, 0, S, S)
        assert all(b.difference(cont).area < 1e-12 for _, b in cells)
        border = cont.difference(__import__("shapely.geometry", fromlist=["box"]).box(1, 1, S - 1, S - 1))
        assert border.difference(unary_union([b for _, b in cells])).area < 1e-9      # the 12 cells cover the border strip
    tested, found, best = W.slot_met_search(n=20000, seed=5)
    assert tested > 1000 and found == 0 and best[0] > 0.05
    assert W.wall_slot_leaf((2.2, 2.3), (2.2, 2.3), 3.9) == 'MUTUAL-POSSIBLE'
    assert W.wall_slot_leaf((1.5, 1.8), (2.2, 2.3), 3.9).startswith('MUTUAL-IMPOSSIBLE')


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
    print("all tests passed")
