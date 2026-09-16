"""A236 capacity test: the band / core / straddler trichotomy, the intrusion of the meeters, the loaded component
(the RING) and the count bounds on (a) the ring rand_0_0569|t20 and the 193 HELD / CROWD four-crowds of A217 (loaded
components from A233's arm233.jsonl), (b) A226's eight-square crowd rings at n = 11 (S = 3.90 / 3.95 / 3.99) with the
pocket capacity, (c) the 21 survey records (not rings: the lemma must not fire).
    python capacity236.py            -> results/capacity236.jsonl  (one row per packing), then summarise236.py
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
try:
    import psutil
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    psutil.Process().cpu_affinity(list(range(16)))
except Exception:
    pass
import band236 as BD                                                   # noqa: E402

ATT = os.path.abspath(os.path.join(HERE, '..'))
ATTS = os.path.abspath(os.path.join(ATT, '..'))
WIT = os.path.join(ATTS, 'A217-torque-probe', 'results', 'witnesses217.jsonl')
ARM = os.path.join(ATTS, 'A233-local-lock', 'results', 'arm233.jsonl')
RING11 = os.path.join(ATTS, 'A226-one-flush', 'results', 'ring11_226.jsonl')
OUT = os.path.join(ATT, 'results', 'capacity236.jsonl')
RING = 'rand_0_0569|t20'


def poses_of_z(z):
    n = (len(z) - 1) // 3
    return [(float(z[3 * i]), float(z[3 * i + 1]), float(z[3 * i + 2])) for i in range(n)], float(z[-1])


def four_crowds():
    out = []
    for l in open(WIT, encoding='utf-8'):
        w = json.loads(l)
        if w['n2'] == 4 and w['cls'] in ('HELD', 'CROWD'):
            out.append(w)
    out.sort(key=lambda w: (w['rid'] != RING, w['wid']))
    return out


def loaded_components():
    """wid -> union over the four corners of A233's loaded component of the meeters (the RING U)."""
    U = {}
    for l in open(ARM, encoding='utf-8'):
        r = json.loads(l)
        ch = r.get('chain') or {}
        U.setdefault(r['wid'], set()).update(ch.get('component') or [])
    return U


def row_of(src, label, poses, s, n, U=None, extra=None):
    rec = BD.records()
    m = math.ceil(math.sqrt(n))
    C = BD.classify(poses, s)
    fl = math.floor(s + 1e-9)
    row = {'src': src, 'label': label, 'n': n, 's': s, 'm': m, 'below_m': s < m - 1e-9, 'floor_s': fl,
           'B': C['B'], 'K': C['K'], 'X': C['X'], 'n_tilted': C['n_tilted'], 'doubly_met': C['doubly_met'],
           'four_crowd': C['four_crowd'], 'tilted_meeters': C['tilted_meeters'],
           'corners': {c: C['corners'][c] for c in BD.CORNERS},
           'walls': {w: {k: v for k, v in C['walls'][w].items() if k != 'touchers'} for w in BD.WALLS},
           'wall_excess_ok': all(C['walls'][w]['chord_sum'] <= s + 1e-6 for w in BD.WALLS),
           'touchers_per_wall_le_floor': all(len(C['walls'][w]['touchers']) <= fl for w in BD.WALLS),
           'band_all_flush_touchers': C['band_all_flush_touchers'], 'tilted_all_intrude': C['tilted_all_intrude'],
           'band_count_bound': 4 * (fl - 1), 'band_count_ok': C['B'] <= 4 * (fl - 1) or not C['four_crowd'],
           'sigma': s - 2.0, 'N_proved': BD.N_proved(s - 2.0), 'N_record': BD.N_record(s - 2.0, rec),
           'core_ok': C['K'] <= BD.N_proved(s - 2.0),
           'meeter_depth_min': C['min_meeter_depth'], 'meeter_depth_max': C['max_meeter_depth'],
           'meeter_iota': {str(i): C['squares'][i]['iota'] for i in C['tilted_meeters']},
           'meeter_depth': {str(i): C['squares'][i]['depth'] for c in BD.CORNERS for i in C['corners'][c]},
           'classes': [q['cls'] for q in C['squares']], 'depths': [q['depth'] for q in C['squares']],
           'poses': [list(p) for p in poses]}
    if U is not None:
        U = sorted(U)
        rest = [i for i in range(len(poses)) if i not in U]
        row.update({'U': U, 'p': len(U), 'rest': rest, 'n_minus_p': n - len(U),
                    'U_classes': {str(i): C['squares'][i]['cls'] for i in U},
                    'U_core_members': [i for i in U if C['squares'][i]['cls'] == 'core'],
                    'U_max_depth': max(C['squares'][i]['depth'] for i in U) if U else 0.0,
                    'rest_classes': {str(i): C['squares'][i]['cls'] for i in rest},
                    'rest_le_N_record': n - len(U) <= BD.N_record(s - 2.0, rec),
                    'rest_le_N_proved': n - len(U) <= BD.N_proved(s - 2.0)})
    if extra:
        row.update(extra)
    return row


def pocket_capacity(ring, S):
    """how many unit squares fit in the container minus the ring: A222's greedy placer over a 5-degree tilt grid
    (k = 1, 2, 3), plus the largest flush square inscribed in the pocket (grid + bisection)."""
    sys.path.insert(0, os.path.join(ATTS, 'A222-ring-swap', 'code'))
    sys.path.insert(0, os.path.join(ATTS, 'A217-torque-probe', 'code'))
    import region222 as RG
    thetas = [math.radians(t) for t in range(0, 90, 5)]
    k = 0
    for kk in (1, 2, 3):
        got = RG.greedy(ring, S, kk, thetas, beam=3)
        if got is None:
            break
        k = kk
    # inscribed flush square: bisection on the side over a grid of centres
    def fits(side):
        h = side / 2
        g = 40
        for a in range(g + 1):
            for b in range(g + 1):
                cx, cy = h + (S - side) * a / g, h + (S - side) * b / g
                if all(BD.sep_polys(BD.verts(q), np.array(
                        [(cx - h, cy - h), (cx + h, cy - h), (cx + h, cy + h), (cx - h, cy + h)]),
                        BD.axes_of(q[2]) + BD.axes_of(0.0)) >= -1e-9 for q in ring):
                    return True
        return False
    lo, hi = 0.0, S - 2.0
    for _ in range(30):
        mid = 0.5 * (lo + hi)
        if fits(mid):
            lo = mid
        else:
            hi = mid
    return k, lo


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    rows = []
    U = loaded_components()
    for w in four_crowds():
        poses, s = poses_of_z(w['z'])
        rows.append(row_of('193', w['wid'], poses, s, 11, U.get(w['wid']), {'rid': w['rid'], 'cls': w['cls']}))
    for l in open(RING11, encoding='utf-8'):
        r = json.loads(l)
        ring = [tuple(p) for p in r['ring']]
        k, side_in = pocket_capacity(ring, r['S'])
        rows.append(row_of('ring11', 'ring8_S%.2f_eps%.2f' % (r['S'], r['eps']), ring, r['S'], 11,
                           list(range(8)), {'pocket_k_greedy': k, 'pocket_inscribed_side': side_in,
                                            'a226_k_max_greedy': r['k_max_greedy'], 'eps': r['eps'],
                                            'note': '8 ring members; n - p = 3 to place; A226 found 1'}))
    for l in open(BD.SURVEY, encoding='utf-8'):
        r = json.loads(l)
        poses = [tuple(p) for p in r['squares']]
        rows.append(row_of('survey', r['label'], poses, r['side'], r['n'], None, {'source': r['source']}))
    with open(OUT, 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r) + '\n')
    print('rows', len(rows), '->', OUT)


if __name__ == '__main__':
    main()
