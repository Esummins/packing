"""A258 scan [M]: the pinwheel of ROWS over a grid of per-wall tilts, for every sense pattern and row-length
vector, at s in {3.82, s-hat, 3.95, 3.99}.  For each tilt vector the sup over the offsets is an exact LP
(dom258.sup_margin, HARD containment by parametrisation); the grid optimum is polished over the tilts by
Nelder-Mead; every positive optimum is re-verified with the full geometry (dom258.verify).

Rows of results/scan258.jsonl are keyed by (s, senses, lengths, slots); resumable; logs/STOP stops between rows.
    python scan258.py            # everything
"""
import itertools
import json
import math
import os
import time

import numpy as np
from scipy.optimize import minimize

import dom258 as Dm
import geo258 as G

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
OUT = os.path.join(ATT, 'results', 'scan258.jsonl')
STOP = os.path.join(ATT, 'logs', 'STOP')
GRID = [1.5, 5, 9, 13, 17, 21, 25, 29, 33, 38, 43]
SIDES = [3.82, G.SHAT, 3.95, 3.99]
# sense patterns up to the rotations of the square and the global reflection (which flips every sense AND the
# walking direction: it maps a pattern to the reversed negated pattern)
SENSES = [(1, 1, 1, 1), (1, 1, 1, -1), (1, 1, -1, -1), (1, -1, 1, -1)]
# a row of ONE never meets both boxes: a + b = s - w(phi) > 2 (dom258.sup_margin returns < 0 at once) -- not scanned
LENGTHS = [(2, 2, 2, 2), (3, 2, 2, 2), (3, 3, 2, 2), (3, 2, 3, 2), (3, 3, 3, 2), (3, 3, 3, 3)]


def belownormal():
    try:
        import psutil
        p = psutil.Process()
        p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        p.cpu_affinity(list(range(16)))
    except Exception:
        pass


def one(s, sg, l, slots):
    best, top = (-9.0, None, None), []
    n_pos, n_all = 0, 0
    pos_lo, pos_hi, spread = [99] * 4, [-1] * 4, 0.0
    for deg in itertools.product(GRID, repeat=4):
        phi = [d * G.DEG for d in deg]
        t, a = Dm.sup_margin(s, phi, sg, l, slots)
        n_all += 1
        if t > 0:
            n_pos += 1
            spread = max(spread, max(deg) - min(deg))
            for w in range(4):
                pos_lo[w], pos_hi[w] = min(pos_lo[w], deg[w]), max(pos_hi[w], deg[w])
        top.append((t, deg))
        if t > best[0]:
            best = (t, deg, a)
    top.sort(reverse=True)
    pol = best
    for t0, deg in top[:3]:                                   # polish the tilts
        f = lambda x: -Dm.sup_margin(s, [min(max(v, 0.2), 44.8) * G.DEG for v in x], sg, l, slots)[0]
        r = minimize(f, list(deg), method='Nelder-Mead', options=dict(xatol=1e-4, fatol=1e-7, maxiter=400))
        if -r.fun > pol[0]:
            x = [min(max(float(v), 0.2), 44.8) for v in r.x]
            pol = (float(-r.fun), x, Dm.sup_margin(s, [v * G.DEG for v in x], sg, l, slots)[1])
    row = dict(s=s, senses=list(sg), lengths=list(l), slots=slots, grid=GRID, n_grid=n_all, n_positive=n_pos,
               grid_best=best[0], sup_margin=pol[0], tilts_deg=list(pol[1]) if pol[1] is not None else None,
               offsets=pol[2], pos_tilt_lo=pos_lo, pos_tilt_hi=pos_hi, max_tilt_spread_deg=spread)
    if pol[0] > 0 and pol[2] is not None:
        row['verify'] = Dm.verify(s, pol[2], [v * G.DEG for v in pol[1]], sg, l)
    return row


def main():
    belownormal()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    done = set()
    if os.path.exists(OUT):
        for ln in open(OUT, encoding='utf-8'):
            r = json.loads(ln)
            done.add((round(r['s'], 6), tuple(r['senses']), tuple(r['lengths']), r['slots']))
    jobs = []
    for s in SIDES:
        for sg in SENSES:
            jobs.append((s, sg, (2, 2, 2, 2), False))
    for s in SIDES:
        jobs.append((s, (1, 1, 1, 1), (2, 2, 2, 2), True))
        for l in LENGTHS[1:]:
            jobs.append((s, (1, 1, 1, 1), l, False))
    for s, sg, l, slots in jobs:
        if (round(s, 6), sg, l, slots) in done:
            continue
        if os.path.exists(STOP):
            print('STOP', flush=True)
            return
        t0 = time.time()
        row = one(s, sg, l, slots)
        row['seconds'] = round(time.time() - t0, 1)
        with open(OUT, 'a', encoding='utf-8') as f:
            f.write(json.dumps(row) + '\n')
        print('%.4f %s %s slots=%s  n+=%d  sup=%+.5f  %.0fs' % (s, sg, l, slots, row['n_positive'],
                                                               row['sup_margin'], row['seconds']), flush=True)
    print('DONE', flush=True)


if __name__ == '__main__':
    main()
