"""A239 tests: WEDGED-SEAL numerics (Monte-Carlo second-meeter search, the wedge inequality f(alpha) >= 1, Lemma
B0*), the reach formula against the built contact ring, the free FJ LP on the 3 x 3 grid (feasible), the GEAR RATIO
on the uniform contact ring (force balance with free torques infeasible unless theta = 45 deg, feasible there).
    python test239.py
"""
import math
import os
import sys
import time

import numpy as np
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom239 as GM                                                       # noqa: E402
import stress239 as SS                                                     # noqa: E402
import stress234 as ST                                                     # noqa: E402
import band236 as BD                                                       # noqa: E402
from rings239 import theta_contact                                          # noqa: E402

GM.set_priority()
FAILS = []


def check(name, ok, detail=''):
    print('%-58s %s %s' % (name, 'PASS' if ok else 'FAIL', detail), flush=True)
    if not ok:
        FAILS.append(name)


def test_wedged_seal():
    for th in (5.0, 20.0, 45.0, 70.0, 85.0):
        Q = GM.wedged_square(th)
        v = BD.verts(Q)
        check('wedged square theta %.0f touches both walls, in quadrant' % th,
              abs(v[:, 0].min()) < 1e-12 and abs(v[:, 1].min()) < 1e-12 and v.min() > -1e-12)
        check('  far vertices at x, y = cos + sin >= 1',
              v[:, 0].max() >= 1 - 1e-12 and v[:, 1].max() >= 1 - 1e-12)
        check('  meets the open box', BD.meets_corner(Q, 10.0, 'BL', 1.0))
        found, worst = GM.second_meeter_search(th, 20000, seed=int(th))
        check('  Monte-Carlo: 20000 random meeters, second meeters found = 0', found == 0, 'largest gap %.3f' % worst)
        fmin = min(GM.f_alpha(th, a) for a in np.arange(th, 90.0, 0.01))
        check('  f(alpha) >= 1 on alpha in [theta, 90)', fmin >= 1 - 1e-12, 'min %.4f' % fmin)
    bmin = min(GM.b0star(p, z) for p in np.arange(0.0, 360.0, 0.25) for z in np.arange(0.0, 90.01, 0.25))
    check('Lemma B0* on a 0.25-deg grid', bmin >= -1e-12, 'min %.2e' % bmin)


def test_reach():
    for S in (3.877, 3.95):
        th = theta_contact(S)
        R, delta = GM.window_ring(S, th, None, 0.0)
        gap = BD.verts(R[3])[:, 0].min() - BD.verts(R[0])[:, 0].max()
        check('reach: contact ring S %.3f theta* %.2f has floor gap S - 2 - R = 0' % (S, th), abs(gap) < 1e-9 and abs(S - 2 - GM.reach(th, delta)) < 1e-9, 'gap %.1e' % gap)
        ok, g, w = BD.check_packing(R, S)
        check('  and is a packing', ok, 'gap %.1e wall %.1e' % (g, w))
    for th, d in ((10.0, 0.3), (30.0, 0.7), (60.0, 0.95)):
        A, B = GM.window_pair(th, d, 0.0)
        span = BD.verts(B)[:, 1].max() + BD.verts(A)[:, 0].max() - 1.0
        check('reach formula vs the built crowd (theta %.0f, delta %.2f)' % (th, d), abs(span - 1 - GM.reach(th, d)) < 1e-9)


def test_lp():
    grid = [(i + 0.5, j + 0.5, 0.0) for i in range(3) for j in range(3)]
    res = SS.analyse(grid, 3.0)
    check('free FJ LP on the 3 x 3 grid at side 3: feasible', res['free_lp'] == 'lam0=1', res['free_lp'])


def force_only(poses, S):
    z, rows, A = SS.rows_and_A(poses, S)
    n = len(poses)
    tc = [3 * i + 2 for i in range(n)]
    keep = [k for k in range(A.shape[1]) if k not in tc]
    r = linprog(np.ones(A.shape[0]), A_eq=A[:, keep].T, b_eq=ST.e_s(A.shape[1])[keep], bounds=[(0, 1e4)] * A.shape[0], method='highs')
    return r.success


def test_gear():
    th = theta_contact(3.95)
    R, delta = GM.window_ring(3.95, th, None, 0.0)
    check('gear ratio: uniform contact ring theta %.2f, force balance (torques free) infeasible' % th, not force_only(R, 3.95))
    d = min(math.sin(math.pi / 4) + math.cos(math.pi / 4) ** 3, 0.999)
    Sb = 2 + GM.reach(45.0, d)
    Rb, _ = GM.window_ring(Sb, 45.0, d, 0.0)
    check('gear ratio: uniform ring at 45 deg (S %.3f), force balance (torques free) feasible' % Sb, force_only(Rb, Sb))


if __name__ == '__main__':
    t0 = time.time()
    test_wedged_seal()
    test_reach()
    test_lp()
    test_gear()
    print('%d failures, %.1f s' % (len(FAILS), time.time() - t0))
    sys.exit(1 if FAILS else 0)
