"""A231 tests: the n-general geometry against A217's (n = 11) routines on the ring witness, the fixed-tilt LP against
A223's click at t = 0 (the four-crowd's own side), the corner meeters against the witness's list, the A226 retraction
swap (a packing at the same side with a settled corner), the schedule and the grain sets.
    python test231.py
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geomn231 as GN         # noqa: E402
import inputs231 as IN        # noqa: E402
import realign231 as RA       # noqa: E402
sys.path.insert(0, os.path.join(HERE, '..', '..', 'A217-torque-probe', 'code'))
import geom217 as G           # noqa: E402
import grains223 as GR        # noqa: E402


def test_geometry_matches_geom217():
    w = [x for x in GR.four_crowds() if x['rid'] == IN.RING][0]
    z = np.array(w['z'], float)
    p, s = IN.poses_of_z(z)
    g_new = GN.pair_gaps(p)
    g_old = G.pair_gaps(z)
    assert max(abs(g_new[k] - g_old[k]) for k in g_old) < 1e-12
    assert abs(GN.wall_min(p, s) - float(G.wall_rows(z)[0].min())) < 1e-12
    for c in GN.CORNERS:
        assert GN.corner_meeters(p, s, c) == sorted(int(i) for i in w['meeters'][c]), c
        assert GN.corner_meeters(p, s, c) == G.corner_meeters(z, c), c
    print('geometry: gaps, walls, corner meeters agree with geom217 on the ring')


def test_lp_reproduces_click_start():
    w = [x for x in GR.four_crowds() if x['rid'] == IN.RING][0]
    p, s = IN.poses_of_z(w['z'])
    th = np.array([q[2] for q in p])
    p1, s1, _, _ = GN.fixed_tilt_min(p, th, GN.contacts(p), {})
    assert abs(s1 - 4.1099276) < 2e-6, s1          # A223 click223.md s.3, t = 0
    ok, gap, wall = GN.check(p1, s1)
    assert ok, (gap, wall)
    print('LP: the ring at its own tilts minimises to %.7f (A223: 4.1099276)' % s1)


def test_pin_and_schedule():
    p = [(0.5, 0.5, 0.0), (1.5, 0.5, 0.0), (2.6, 0.7, 0.3)]
    th = np.array([q[2] for q in p])
    p1, s1, _, _ = GN.fixed_tilt_min(p, th, {}, {0: 'BL'})
    assert abs(p1[0][0] - 0.5) < 1e-9 and abs(p1[0][1] - 0.5) < 1e-9
    p2, s2, _, _ = GN.fixed_tilt_min([(2.5, 2.5, 0.0), (1.5, 0.5, 0.0), (0.6, 0.7, 0.3)], th, {}, {0: 'TR'})
    assert abs(p2[0][0] - (s2 - 0.5)) < 1e-9 and abs(p2[0][1] - (s2 - 0.5)) < 1e-9
    th1 = RA.schedule([0.3, math.radians(70), math.pi / 4, 0.0], 1.0, [0, 1, 2, 3])
    assert abs(th1[0]) < 1e-12 and abs(th1[1] - math.pi / 2) < 1e-12 and abs(th1[2]) < 1e-12 and th1[3] == 0.0
    th2 = RA.schedule([0.3, math.radians(70)], 0.5, [0])
    assert abs(th2[0] - 0.15) < 1e-12 and abs(th2[1] - math.radians(70)) < 1e-12
    print('pins and schedule ok')


def test_a226_retraction():
    cs = IN.cases_a226()
    assert len(cs) == 32, len(cs)
    for k in cs:
        assert k['poses'] is not None, (k['wid'], k['corner'], k['swap'])
        assert GN.settled_at(k['poses'], k['corner'], k['s0']) == k['S']
        assert len(GN.corner_meeters(k['poses'], k['s0'], k['corner'])) == 1
        assert len(GN.corner_meeters(k['poses0'], k['s0'], k['corner'])) == 2
    print('a226: 32 retraction swaps are packings at the same side with the corner settled (was doubly met)')


def test_grain_sets_and_run():
    k = [c for c in IN.cases_193() if c['rid'] == IN.RING and c['corner'] == 'BR'][0]
    assert k['S'] is not None and k['poses'] is not None
    rec = RA.run_case(k, 4)
    assert rec['status'] == 'ok' and rec['s_lp0'] <= rec['s0'] + 1e-9
    for name, r in rec['paths'].items():
        if 'horn' in r:
            assert r['s'][0] == rec['s_lp0'] or abs(r['s'][0] - rec['s_lp0']) < 1e-6, (name, r['s'][0], rec['s_lp0'])
    print('ring BR: s0 %.5f -> shrink %.5f; grains %s; comp A: %s %s s_min %s' % (
        rec['s0'], rec['s_lp0'], rec['grains'], rec['paths']['compA'].get('horn'),
        rec['paths']['compA'].get('endpoint'), rec['paths']['compA'].get('s_min')))


if __name__ == '__main__':
    test_geometry_matches_geom217()
    test_lp_reproduces_click_start()
    test_pin_and_schedule()
    test_a226_retraction()
    test_grain_sets_and_run()
    print('ALL PASS')
