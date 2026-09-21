"""A255 tests: SENSE-INVARIANT, NORMAL-CELL (a), the orbit count, and an INDEPENDENT re-check of every local /
blocked witness row (containment in the quadrant, pairwise SAT gaps, the required / avoided cells, the senses,
the blocker of T).  python test255.py"""
import json
import math
import os
import sys

import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.abspath(os.path.join(HERE, '..', 'results'))
sys.path.insert(0, HERE)
import geo255 as G                                                    # noqa: E402
from local255 import sat_gap, PAIRS, C00, C01, C10                    # noqa: E402


def test_sense_invariant():
    rng = np.random.default_rng(1)
    for th in rng.uniform(0, 2 * math.pi, 2000):
        assert G.sense(th) == G.sense(th + math.pi / 2) == G.sense(th + math.pi)
        if G.sense(th) in (1, -1):
            assert G.sense(-th) == -G.sense(th)                        # a reflection flips the sense
    return 'sense: quarter turns fix it, reflections flip it (2000 tilts)'


def test_normal_cell():
    rng = np.random.default_rng(2)
    for _ in range(2000):
        phi = math.radians(rng.uniform(-44.5, 44.5))
        hw = 0.5 * (abs(math.cos(phi)) + abs(math.sin(phi)))
        s1 = (rng.uniform(1, 3), hw, phi)                              # a floor toucher
        T = (s1[0] + 1.0 / math.cos(phi), hw, phi)
        g = sat_gap(G.corners_of(*s1), G.corners_of(*T))
        assert abs(g) < 1e-12, g                                       # edge to edge: gap exactly 0
        assert abs(G.corners_of(*T)[:, 1].min()) < 1e-12               # T touches the floor
    return 'NORMAL-CELL (a): T = s1 + sec(phi) e is edge-to-edge with s1 and touches the wall (2000 tilts)'


def test_orbits():
    import ringsense255 as R
    reps = R.orbits()
    assert len(reps) == 43 and sum(len(R.orbit(p)) for p in reps) == 256
    return '43 sense-pattern orbits, sizes summing to 256'


def check_row(r, blocked):
    names = ['B', 'A', 'C', 'D'] + (['E'] if blocked else [])
    ps = [tuple(r['poses'][n]) for n in names]
    V = [G.corners_of(*p) for p in ps]
    assert min(v.min() for v in V) >= -1e-9, 'containment'
    assert min(sat_gap(V[i], V[j]) for i in range(len(V)) for j in range(i)) >= -1e-9, 'overlap'
    assert G.depth(*ps[0], C00) > 0 and G.depth(*ps[1], C00) > 0 and G.depth(*ps[2], C01) > 0 and G.depth(*ps[3], C10) > 0
    assert all(G.depth(*p, C00) <= 1e-12 for p in ps[2:]), 'a third root meeter'
    if blocked:
        kind, sg = r['type'].split(':')
        des = [('B', 'V', sg[0]), ('C', 'V', sg[1])] if kind == 'W' else [('A', 'H', sg[0]), ('B', 'V', sg[1])]
        VT = G.corners_of(*r['T'])
        others = [n for n in names if n not in ((des[0][0], 'C') if kind == 'W' else (des[0][0], 'D'))]
        assert any(-sat_gap(V[names.index(n)], VT) > 0 for n in others), 'T not blocked'
    else:
        p, sg = r['type'].split(':')
        des = [(n, role, c) for (n, role), c in zip(PAIRS[p], sg)]
    for n, role, c in des:
        q = ps[names.index(n)]
        v = G.corners_of(*q)
        assert abs(v[:, 0].min() if role == 'V' else v[:, 1].min()) < 1e-9, 'not touching'
        assert {'+': 1, '-': -1, '0': 0}[c] == G.sense(q[2]), 'sense'


def test_witnesses():
    out = []
    for name, blocked in (('local255.jsonl', False), ('blocked255.jsonl', True)):
        p = os.path.join(RES, name)
        rows = [json.loads(l) for l in open(p)] if os.path.exists(p) else []
        ok = 0
        for r in rows:
            if r['verdict'] == 'FEASIBLE-WITNESS':
                check_row(r, blocked)
                ok += 1
        out.append('%s: %d of %d rows are witnesses, all re-verified' % (name, ok, len(rows)))
    return '; '.join(out)


if __name__ == '__main__':
    for t in (test_sense_invariant, test_normal_cell, test_orbits, test_witnesses):
        print('PASS', t())
