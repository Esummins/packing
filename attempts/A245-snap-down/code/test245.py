"""A245 self-tests (about 60 s): STACK's order / clearance / chord bound on random mutual pairs, the
contact-type table, the contact-keeps-cells grid, the wall-frame round trips, the LP at t = 0, REDUCE on
the 4 x 4 grid.   python test245.py"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom245 as G      # noqa: E402
import lp245 as L        # noqa: E402
import reduce245 as R    # noqa: E402
import stack245 as S     # noqa: E402
import testbeds245 as T  # noqa: E402


def test_frames():
    rng = random.Random(3)
    for wall in G.WALLS:
        for _ in range(50):
            s = rng.uniform(3.5, 4.5)
            p = (rng.uniform(0.8, s - 0.8), rng.uniform(0.8, s - 0.8), rng.uniform(0, math.pi / 2))
            q = G.from_frame(G.to_frame(p, wall, s), wall, s)
            V, W = G.verts(p), G.verts(q)
            assert max(abs(float(v)) for v in (V - W).ravel()) < 1e-9 or \
                sorted(map(tuple, V.round(9))) == sorted(map(tuple, W.round(9))), (wall, p, q)
    for _ in range(200):
        th, ell = rng.uniform(0.01, math.pi / 2 - 0.01), rng.uniform(1, 2)
        t2, e2 = G.wall_params(G.wall_pose(th, ell))
        assert abs(t2 - th) < 1e-9 and abs(e2 - ell) < 1e-9
    print('frames OK')


def test_stack(n=3000):
    rng = random.Random(11)
    got = 0
    for s in (3.5, 3.82, 3.877084, 3.95, 3.99):
        while got < n:
            smp = S.sample(rng, s)
            if smp is None:
                continue
            r = S.analyse(*smp, s)
            if not (r['mutual'] and r['contained'] and r['disjoint']):
                continue
            got += 1
            assert r['order_ok'], r
            assert r['clear_lt_4ms'], r
            assert r['B_meets_c01'] and r['Bp_meets_cp01'], r
            if r['contact_type'] not in ('none', 'n/a'):
                assert r['H_contact'] >= r['chord_sum'] - 1e-9, r
                ts = r['contact_type'].replace('flush:', '').split('+')
                near90 = abs(r['th'] + r['thp'] - 90) < 0.05
                assert near90 or r['contact_type'] == "T=V'" or any(t in r['predicted'] for t in ts), r
        got = 0
    print('STACK order / clearance / chords / table OK')


def test_contact_keeps_cells():
    """coarse grid: lowering B' onto B keeps the mutual cells (the note's Cor. STACK (d), [M])."""
    bad = 0
    tot = 0
    for s in (3.82, 3.877084, 3.95, 3.99):
        for i in range(2, 90, 4):
            th = math.radians(i)
            for j in range(2, 90, 4):
                thp = math.radians(j)
                lo, hi = max(math.cos(th), s - 2 - math.sin(th)), 1 + math.cos(th)
                for k in range(1, 6):
                    ell = lo + (hi - lo) * k / 6
                    ec = S.contact_ell(th, ell, thp, s)
                    if ec is None:
                        continue
                    Bc = G.wall_pose(thp, ec)
                    B = G.wall_pose(th, ell)
                    if not (S.contained(Bc, s) and S.mutual(B, Bc, s)[3]):
                        continue           # B' at contact leaves the container or c01: no mutual pair in this slice
                    tot += 1
                    if not S.mutual(B, Bc, s)[2]:
                        bad += 1
    print('contact keeps c\'00 on %d / %d admissible slices (violations = floating-only slices)' % (tot - bad, tot))
    return tot, bad


def test_lp():
    cfg = T.four_crowds()[0]
    poses, s0 = cfg['poses'], cfg['s']
    p2, s, sel, k = L.fixed_tilt_min(poses, list(range(len(poses))))
    assert p2 is not None and s <= s0 + 1e-6, (s, s0)
    ok, gw, gp = G.check_packing(p2, s, tol=1e-7)
    assert ok, (gw, gp)
    p3, s3, _, _ = L.fixed_tilt_min(poses, [0, 1])
    assert p3 is not None and abs(s3 - s0) < 1e-6, (s3, s0)
    print('LP OK: global %.6f <= s0 %.6f, local = s0' % (s, s0))


def test_reduce_grid():
    poses = [(i + 0.5, j + 0.5, 0.0) for i in range(4) for j in range(4)][:11]
    for wall in G.WALLS:
        rec = R.reduce_wall(poses, 4.0, wall)
        assert rec['k1']['size'] <= 1 and rec['any_ok'], rec
    print('REDUCE on the grid OK')


if __name__ == '__main__':
    test_frames()
    test_stack()
    test_contact_keeps_cells()
    test_lp()
    test_reduce_grid()
    print('all tests passed')
