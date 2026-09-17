"""A252: the ADVERSARIAL ladder -- over the ring family at a side s, maximise a capacity metric of
the centre set C (disc252.metrics) subject to ring feasibility (margin >= need):

    far_O     max |q - O| over C            (A251's Lemma CENTRE-DISC about the container centre;
                                             the bound is FALSE on the window: far_O > 1/sqrt3)
    sec_r     smallest enclosing circle     (the corrected lemma: SOME centre within 1/sqrt3)
    halves    max diameter of C n {y <= s/2}, {y >= s/2}, {x <= s/2}, {x >= s/2}  (two pieces < 1)
    disp3     max over triples of the least pairwise distance  (< 1: no three admissible centres)

Nelder-Mead on metric - pen * max(0, need - margin), structured restarts (A249's s-hat ring, the
C2 rings of neighbouring sides, near-FLAT corner starts, random).  One row per (side, metric,
start) in results/adv252.jsonl; the best feasible per (side, metric) in results/adv252.json.
Resumable (done starts skipped); logs/STOP honoured between starts.

    python adv252.py [--sides 3.82,...] [--metrics far_O,sec_r,halves,disp3] [--starts N]
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np
from scipy.optimize import minimize

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import disc252 as D                                                   # noqa: E402
import twotilted249 as W                                              # noqa: E402

ROWS = os.path.join(ATT, 'results', 'adv252.jsonl')
BEST = os.path.join(ATT, 'results', 'adv252.json')
STOP = os.path.join(ATT, 'logs', 'STOP')


def metric_value(x, s, metric):
    polys, _ = D.ring(x, s)
    C = D.centre_set(polys, s, res=32)
    pts = D.boundary_pts(C, step=0.02)
    if len(pts) == 0:
        return 0.0
    if metric == 'far_O':
        return D.far_from(pts, (s / 2, s / 2))[0]
    if metric == 'sec_r':
        return D.sec(pts)[0]
    if metric == 'halves':
        m = []
        for ax, sg in ((1, -1), (1, 1), (0, -1), (0, 1)):
            sel = pts[sg * (pts[:, ax] - s / 2) >= -1e-9]
            m.append(D.diam(sel))
        return max(m)
    if metric == 'disp3':
        return D.disp3(pts[::2])
    raise ValueError(metric)


def starts(s, n, seed):
    """structured restarts: s-hat C2 ring, C2 rings of other sides, near-flat corners, random."""
    rng = np.random.default_rng(seed)
    out = []
    fn = os.path.join(D.ROOT, 'attempts', 'A249-type-t-chase', 'results', 'twotilted249_ring2.json')
    j = json.load(open(fn, encoding='utf-8'))
    for key in ('3.877084', '3.850000', '3.900000', '4.000000'):
        y = j[key]['result']['x']
        out.append(('c2_' + key, list(y[:4]) + list(y[4:8]) + list(y[:4]) + list(y[4:8])))
    base = out[0][1]
    for c in range(4):
        x = list(base)
        x[4 * c:4 * c + 4] = [math.radians(87), 0.94, math.radians(88.5), 0.97]
        out.append(('flat_%d' % c, x))
    k = 0
    while len(out) < n:
        out.append(('rand_%d' % k, list(W.random_start(rng, 4, k % 3))))
        k += 1
    return out[:n]


def optimise(x0, s, metric, need=0.002, pen=30.0, maxiter=3000):
    def J(z):
        m = D.margin(z, s)
        f = metric_value(z, s, metric) if m > -0.25 else 0.0
        return -(f - pen * max(0.0, need - m))
    r = minimize(J, x0, method='Nelder-Mead',
                 options={'xatol': 1e-8, 'fatol': 1e-10, 'maxiter': maxiter, 'adaptive': True})
    x = [float(v) for v in r.x]
    return x, D.margin(x, s), metric_value(x, s, metric)


def load_rows():
    rows = []
    if os.path.exists(ROWS):
        for line in open(ROWS, encoding='utf-8'):
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def refresh_best(rows):
    best = {}
    for r in rows:
        if r['margin'] < 0:
            continue
        key = '%s|%s' % (r['side'], r['metric'])
        if key not in best or r['value'] > best[key]['value']:
            best[key] = r
    out = {}
    for key, r in best.items():
        m = D.metrics(r['x'], float(r['side']))
        out[key] = dict(r, metrics=m)
    json.dump(out, open(BEST, 'w', encoding='utf-8'), indent=1)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sides', default='3.82,3.85,3.877084,3.90,3.95,3.99')
    ap.add_argument('--metrics', default='far_O,sec_r,halves,disp3')
    ap.add_argument('--starts', type=int, default=12)
    ap.add_argument('--maxiter', type=int, default=3000)
    ap.add_argument('--seed', type=int, default=252)
    a = ap.parse_args()
    D.belownormal()
    rows = load_rows()
    done = {(r['side'], r['metric'], r['start']) for r in rows}
    sides = [float(v) for v in a.sides.split(',')]
    for metric in a.metrics.split(','):
        for s in sides:
            key_s = '%.6f' % s
            for name, x0 in starts(s, a.starts, a.seed):
                if os.path.exists(STOP):
                    print('STOP present', flush=True)
                    refresh_best(rows)
                    return
                if (key_s, metric, name) in done:
                    continue
                t0 = time.time()
                x, m, v = optimise(x0, s, metric, maxiter=a.maxiter)
                row = {'side': key_s, 'metric': metric, 'start': name, 'margin': m, 'value': v,
                       'x': x, 'seconds': time.time() - t0}
                rows.append(row)
                with open(ROWS, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(row) + '\n')
                print('s=%s %s start %-12s margin %+.5f value %.4f (%.0fs)' % (key_s, metric, name, m, v, row['seconds']), flush=True)
            refresh_best(rows)
    print('ADV DONE', flush=True)


if __name__ == '__main__':
    main()
