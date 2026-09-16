"""A236 tests (python test236.py; ~10 s): the lemmas of docs/proofs/ring_capacity.md on random configurations and
the invariants of results/capacity236.jsonl.
  TILT-BAND    a tilted square in [0,s]^2, s > 2 + sqrt2, meets the open centre (1, s-1)^2; the explicit point of
               the proof (on the edge from the max-x vertex to the max-y vertex) has x > 1 and y > 1.
  BAND-FLUSH   a flush square is a band square iff it touches a wall; a tilted square is never a band square.
  TWO          a unit square inside a square container of side < 2 contains the container's centre in its interior.
  OVERLAP      two flush squares meeting the same corner box from its two walls overlap (BAND-COUNT's claim rule).
  NO-CLOSURE   4(m-2) + ((m-2)^2 - 3) + 4 = m^2 - 3.
  DATA         B + K + X = n on every full packing; BAND-COUNT on the four-crowds; WALL-EXCESS chord sums <= s;
               K <= N_proved(s - 2); the packing-number staircases at the checkpoints.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import band236 as BD                                                   # noqa: E402

RES = os.path.join(HERE, '..', 'results', 'capacity236.jsonl')
rng = np.random.default_rng(236)
fails = []


def check(name, ok, info=''):
    if not ok:
        fails.append(name + ' ' + str(info))


def random_square_in(s, th):
    e = BD.extent(th)
    return (rng.uniform(e / 2, s - e / 2), rng.uniform(e / 2, s - e / 2), th)


def tilt_band():
    for _ in range(3000):
        s = rng.uniform(2 + math.sqrt(2) + 1e-3, 8.0)
        th = rng.uniform(1e-3, math.pi / 2 - 1e-3)
        p = random_square_in(s, th)
        check('TILT-BAND depth', BD.depth_into_centre(p, s) > 0, (s, p))
        check('TILT-BAND class', BD.centre_class(p, s) != 'band', (s, p))
    # the proof's explicit point: BL quadrant, a = min x, b = min y, edge v_R -> v_T, direction (-sin, cos)
    for _ in range(3000):
        th = rng.uniform(1e-4, math.pi / 2 - 1e-4)
        a, b = rng.uniform(0, 1.5), rng.uniform(0, 1.5)
        c, d = math.cos(th), math.sin(th)
        vR = (a + c + d, b + d)
        lower = (1 - b - d) / c
        upper = (a + c + d - 1) / d
        lo, hi = max(lower, 0.0), min(upper, 1.0)
        check('TILT-BAND interval', lo < hi, (th, a, b))
        ell = 0.5 * (lo + hi)
        x, y = vR[0] - ell * d, vR[1] + ell * c
        check('TILT-BAND point', x > 1 and y > 1, (th, a, b, x, y))


def band_flush():
    for _ in range(2000):
        s = rng.uniform(3.5, 8.0)
        a, b = rng.uniform(0, s - 1), rng.uniform(0, s - 1)
        if rng.uniform() < 0.5:
            a = 0.0 if rng.uniform() < 0.5 else s - 1
        p = (a + 0.5, b + 0.5, 0.0)
        touching = a < 1e-9 or a > s - 1 - 1e-9 or b < 1e-9 or b > s - 1 - 1e-9
        check('BAND-FLUSH', (BD.centre_class(p, s) == 'band') == touching, (s, a, b))


def lemma_two():
    for _ in range(3000):
        sig = rng.uniform(1.0, 2.0 - 1e-6)
        th = rng.uniform(0, math.pi / 2)
        e = BD.extent(th)
        if sig < e:
            continue
        p = random_square_in(sig, th)
        O = np.array([sig / 2, sig / 2]) - np.array(p[:2])
        R = np.array([[math.cos(th), math.sin(th)], [-math.sin(th), math.cos(th)]])
        check('TWO', np.abs(R @ O).max() < 0.5, (sig, p))


def overlap():
    for _ in range(2000):
        a, b = rng.uniform(1e-6, 1 - 1e-6), rng.uniform(1e-6, 1 - 1e-6)
        check('OVERLAP', BD.sep((a + 0.5, 0.5, 0.0), (0.5, b + 0.5, 0.0)) < -1e-9, (a, b))


def no_closure():
    for m in range(3, 13):
        check('NO-CLOSURE', 4 * (m - 2) + ((m - 2) ** 2 - 3) + 4 == m * m - 3, m)


def data():
    if not os.path.exists(RES):
        fails.append('DATA: results missing (run capacity236.py)')
        return
    rows = [json.loads(l) for l in open(RES, encoding='utf-8')]
    for r in rows:
        if len(r['poses']) == r['n']:
            check('DATA sum', r['B'] + r['K'] + r['X'] == r['n'], r['label'])
        check('DATA wall-excess', r['wall_excess_ok'], r['label'])
        check('DATA touchers', r['touchers_per_wall_le_floor'], r['label'])
        check('DATA core', r['K'] <= r['N_proved'], r['label'])
        check('DATA tilt-band', r['tilted_all_intrude'], r['label'])
        check('DATA band-flush', r['band_all_flush_touchers'], r['label'])
        if r['four_crowd']:
            check('DATA band-count', r['B'] <= 4 * (r['floor_s'] - 1), r['label'])
            check('DATA one-tilted', len(r['tilted_meeters']) >= 4, r['label'])
    for sig, np_, nr in ((1.99, 1, 1), (2.0, 4, 4), (2.70, 4, 4), (2.71, 5, 5), (2.99, 5, 5), (3.0, 9, 9),
                         (3.70, 9, 9), (3.71, 10, 10), (3.80, 12, 10), (3.99, 12, 11)):
        check('STAIRCASE proved', BD.N_proved(sig) == np_, (sig, BD.N_proved(sig)))
        check('STAIRCASE record', BD.N_record(sig) == nr, (sig, BD.N_record(sig)))


if __name__ == '__main__':
    tilt_band()
    band_flush()
    lemma_two()
    overlap()
    no_closure()
    data()
    print('A236 tests:', 'OK' if not fails else 'FAIL %d' % len(fails))
    for f in fails[:20]:
        print('  ', f)
    sys.exit(1 if fails else 0)
