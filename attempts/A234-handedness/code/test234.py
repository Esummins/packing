"""A234 self-tests (~20 s): Lemma W on random poses (all four walls), the pairwise cancellation of pair-row moments
about any point, TORQUE-ID (global and per corner) on Trump, S07 and a HELD four-crowd, the n-general row model
against A217/A219's on Trump, and the handedness bookkeeping.
    python test234.py
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stress234 as S          # noqa: E402
import hand234 as H            # noqa: E402

rng = np.random.default_rng(234)
fails = 0


def check(name, ok, detail=''):
    global fails
    print('%-52s %s %s' % (name, 'ok' if ok else 'FAIL', detail))
    fails += 0 if ok else 1


def lemma_w():
    """theta-gradient of a vertex-on-wall row = (sin th - cos th)/2 for the extreme vertex, every wall."""
    worst = 0.0
    for _ in range(200):
        th = rng.uniform(0, math.pi / 2)
        s = 5.0
        for wall in S.WALLS:
            c = {'x=0': (0.5 * (math.cos(th) + math.sin(th)), 2.5), 'y=0': (2.5, 0.5 * (math.cos(th) + math.sin(th))),
                 'x=s': (s - 0.5 * (math.cos(th) + math.sin(th)), 2.5), 'y=s': (2.5, s - 0.5 * (math.cos(th) + math.sin(th)))}[wall]
            z = np.array([c[0], c[1], th, s])
            q = S.verts(z)[0]
            k = int(np.argmin({'x=0': q[:, 0], 'y=0': q[:, 1], 'x=s': -q[:, 0], 'y=s': -q[:, 1]}[wall]))
            g = S.row_grad(z, {'kind': 'wall', 'i': 0, 'corner': k, 'wall': wall})
            worst = max(worst, abs(g[2] - (math.sin(th) - math.cos(th)) / 2))
    check('Lemma W: tau = W (sin th - cos th)/2 on all four walls', worst < 1e-12, '%.1e' % worst)


def pair_cancel(w):
    """for every pair row the two squares' moments about O sum to zero (Newton's third law at the common point)."""
    z = w['z']
    cx, cy, th, s, n = S.unpack(z)
    c = np.stack([cx, cy], -1)
    O = rng.uniform(0, s, 2)
    worst = 0.0
    for r, g in zip(w['rows'], w['A']):
        if r['kind'] != 'edge':
            continue
        tot = 0.0
        for i in (r['i'], r['j']):
            tot += g[3 * i + 2] + H.cross(c[i] - O, g[3 * i:3 * i + 2])
        worst = max(worst, abs(tot))
    check('pair rows: moments about a random point cancel (%s)' % w['name'], worst < 1e-12, '%.1e' % worst)


def torque_id(w):
    rec = H.analyse(w)
    check('TORQUE-ID global residual (%s)' % w['name'], abs(rec['torque_id']['residual']) < 1e-5, '%.1e' % rec['torque_id']['residual'])
    check('  sum tau^wall + C = 0 (%s)' % w['name'], abs(rec['torque_id']['sum_tau_wall'] + rec['torque_id']['C'] + rec['torque_id']['ext_moment']) < 1e-5)
    for cn, a in rec['corners'].items():
        check('  corner %s arm moment residual, floor >= 0 >= wall' % cn, abs(a['residual']) < 1e-5 and a['floor'] >= -1e-9 and a['wall'] <= 1e-9,
              'floor %.3f wall %.3f' % (a['floor'], a['wall']))
    tilted = [x for x in rec['squares'] if x['tilted'] and x['W'] > 1e-7]
    check('  tau^wall has sign -chi on every loaded tilted toucher', all(-x['chi'] * x['tau_wall'] >= -1e-9 for x in tilted), '%d squares' % len(tilted))
    check('  S_tilted = -sum tau^wall(tilted)', abs(rec['S_tilted'] + sum(x['tau_wall'] for x in tilted)) < 1e-9)
    check('  S_tilted inside its polytope range', rec['ranges']['S_tilted'][0] - 1e-6 <= rec['S_tilted'] <= rec['ranges']['S_tilted'][1] + 1e-6)
    return rec


def row_models():
    """the n-general row finder against rows219 on Trump: same wall rows and the same touching pairs."""
    w = S.trump()
    z = w['z']
    mine = S.active_rows_general(z, 1e-6)
    walls = lambda rows: {(r['i'], r['corner'], r['wall']) for r in rows if r['kind'] == 'wall'}
    pairs = lambda rows: {frozenset((r['i'], r['j'])) for r in rows if r['kind'] == 'edge'}
    check('n-general rows: wall rows agree with A217 on Trump', walls(mine) == walls(w['rows']))
    check('n-general rows: touching pairs agree with A217 on Trump', pairs(mine) == pairs(w['rows']),
          '%d vs %d' % (len(pairs(mine)), len(pairs(w['rows']))))
    A = np.array([S.row_grad(z, r) for r in mine])
    check('n-general model: Trump has a stress', S.feasible(A) is not None)
    g = S.meeters_general(z)
    check('n-general meeters agree on Trump', {k: list(v) for k, v in g.items()} == {k: list(v) for k, v in w['meeters'].items()}, str(g))


def flips():
    check('handedness: rotation by 90 deg keeps chi', H.handed(0.3)[0] == H.handed(0.3 + math.pi / 2)[0])
    check('handedness: reflection swaps chi', H.handed(0.3)[0] == -H.handed(-0.3)[0])
    check('handedness: 45 deg is D with d = 0', H.handed(math.pi / 4) == (0, 'D', 0.0))


def main():
    lemma_w()
    flips()
    row_models()
    for w in (S.trump(), S.s07()):
        pair_cancel(w)
        torque_id(w)
    ring = None
    for l in open(S.WIT, encoding='utf-8'):
        r = json.loads(l)
        if r['wid'] == 'w364_held':
            ring = S.from_w217(r)
    pair_cancel(ring)
    rec = torque_id(ring)
    check('ring: four doubly-met corners, external load > 0', rec['four_crowd'] and rec['ext_load'] > 1e-6, '%.3f' % rec['ext_load'])
    print('FAILURES', fails)
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
