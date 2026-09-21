"""A258 [M]: the LEAST SIDE of a pinwheel of rows, per sense pattern and row-length vector, over ALL per-wall tilts.

s_min(senses, lengths) := inf over tilt vectors phi in (0, 45 deg)^4 of dom258.min_side (an exact LP in the offsets
and the side).  Grid over the tilts (GRID^4), then Nelder-Mead polish of the tilts from the five best grid points and
from the near-flat corner.  A pattern with s_min >= 4 has NO pinwheel of rows anywhere on (3, 4).
Rows of results/side258.jsonl keyed by (senses, lengths); resumable; logs/STOP stops between rows.
After the s_min rows: the extent of D (sense ++++, rows of two) at the four test sides (scan258.one).
"""
import itertools
import json
import os
import time

from scipy.optimize import minimize

import dom258 as Dm
import geo258 as G
import scan258 as S

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
OUT = os.path.join(ATT, 'results', 'side258.jsonl')
STOP = os.path.join(ATT, 'logs', 'STOP')
GRID = [0.75, 3, 6, 10, 14, 18, 22, 27, 32, 38, 44]
JOBS = [((1, 1, 1, 1), (2, 2, 2, 2)), ((1, 1, 1, -1), (2, 2, 2, 2)), ((1, 1, -1, -1), (2, 2, 2, 2)),
        ((1, -1, 1, -1), (2, 2, 2, 2)), ((1, 1, 1, 1), (3, 2, 2, 2)), ((1, 1, 1, 1), (3, 3, 2, 2)),
        ((1, 1, 1, 1), (3, 2, 3, 2)), ((1, 1, 1, 1), (3, 3, 3, 2)), ((1, 1, 1, 1), (3, 3, 3, 3)),
        ((1, 1, 1, -1), (3, 2, 2, 2)), ((1, 1, 1, -1), (2, 2, 2, 3)), ((1, 1, -1, -1), (3, 2, 2, 2)),
        ((1, -1, 1, -1), (3, 2, 2, 2))]


def one(sg, l):
    vals = []
    for deg in itertools.product(GRID, repeat=4):
        v, a = Dm.min_side([d * G.DEG for d in deg], sg, l)
        vals.append((v, deg))
    vals.sort()
    below4 = sum(1 for v, _ in vals if v < 4)
    best = (vals[0][0], list(vals[0][1]))
    clamp = lambda x: [min(max(float(v), 0.05), 44.95) for v in x]
    f = lambda x: Dm.min_side([v * G.DEG for v in clamp(x)], sg, l)[0]
    for v0, deg in vals[:5] + [(0, (0.3, 0.3, 0.3, 0.3))]:
        r = minimize(f, list(deg), method='Nelder-Mead', options=dict(xatol=1e-5, fatol=1e-9, maxiter=500))
        if r.fun < best[0]:
            best = (float(r.fun), clamp(r.x))
    a = Dm.min_side([v * G.DEG for v in best[1]], sg, l)[1]
    row = dict(senses=list(sg), lengths=list(l), grid=GRID, n_grid=len(vals), n_grid_below_4=below4,
               grid_min=vals[0][0], grid_argmin=list(vals[0][1]), s_min=best[0], tilts_deg=best[1], offsets=a)
    # the least side at tilts bounded away from flat (every tilt >= 3 deg): where the bound is not the flat limit
    away = [(v, d) for v, d in vals if min(d) >= 3]
    row['grid_min_tilts_ge_3deg'] = away[0][0]
    row['grid_argmin_tilts_ge_3deg'] = list(away[0][1])
    if best[0] < 4 and a is not None:
        s = best[0] + 1e-9
        row['verify_at_s_min'] = Dm.verify(s, a, [v * G.DEG for v in best[1]], sg, l)
    return row


def main():
    S.belownormal()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    done = set()
    if os.path.exists(OUT):
        for ln in open(OUT, encoding='utf-8'):
            r = json.loads(ln)
            done.add((tuple(r['senses']), tuple(r['lengths'])))
    for sg, l in JOBS:
        if (sg, l) in done:
            continue
        if os.path.exists(STOP):
            print('STOP', flush=True)
            return
        t0 = time.time()
        row = one(sg, l)
        row['seconds'] = round(time.time() - t0, 1)
        with open(OUT, 'a', encoding='utf-8') as f:
            f.write(json.dumps(row) + '\n')
        print('%s %s  s_min=%.6f at %s  (grid below 4: %d; tilts >= 3 deg: %.5f)  %.0fs' % (
            sg, l, row['s_min'], [round(v, 2) for v in row['tilts_deg']], row['n_grid_below_4'],
            row['grid_min_tilts_ge_3deg'], row['seconds']), flush=True)
    # the extent of D at the test sides (sense ++++, rows of two; with and without the slot cut)
    done = set()
    if os.path.exists(S.OUT):
        for ln in open(S.OUT, encoding='utf-8'):
            r = json.loads(ln)
            done.add((round(r['s'], 6), tuple(r['senses']), tuple(r['lengths']), r['slots']))
    for s in S.SIDES:
        for slots in (False, True):
            key = (round(s, 6), (1, 1, 1, 1), (2, 2, 2, 2), slots)
            if key in done:
                continue
            if os.path.exists(STOP):
                print('STOP', flush=True)
                return
            t0 = time.time()
            row = S.one(s, (1, 1, 1, 1), (2, 2, 2, 2), slots)
            row['seconds'] = round(time.time() - t0, 1)
            with open(S.OUT, 'a', encoding='utf-8') as f:
                f.write(json.dumps(row) + '\n')
            print('D extent s=%.4f slots=%s n+=%d sup=%+.5f' % (s, slots, row['n_positive'], row['sup_margin']),
                  flush=True)
    print('DONE', flush=True)


if __name__ == '__main__':
    main()
