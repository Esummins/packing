"""A255: COMMON-SENSE at RING level -- does the all-ADJ ring (A249 s.2.3: eight wall-touching tilted meeters,
both boxes' meeters reaching the far slot of their wall, every border cell doubly met by the eight) exist with
a MIXED sense pattern?  A249/A251/A253 only ever found the two pinwheels (one sense).  Here the sense of each
of the eight members is PRESCRIBED (256 patterns, 43 orbits under D4 with reflections flipping every sense) and
the sup of A249's `ring_margin` (wrapped, read-only) plus the sense terms is searched per orbit and side.
sup > 0: the mixed ring EXISTS (a witness against ring-level COMMON-SENSE, exact poses kept);
sup <= 0 over the restarts: [M] no mixed ring of that pattern (not a certificate).

Member order (A249): B_BL, A_BL, B_BR, A_BR, B_TR, A_TR, B_TL, A_TL; frame tilt t in (0, 90) per member; the
GLOBAL sense is + iff (t < 45) XOR (corner in {BR, TL}) (their frames are reflected).
    python ringsense255.py [--sides 3.99,3.877084] [--restarts 6]  -> results/ringsense255.jsonl
Resumable (rows keyed by pattern orbit + side are skipped); stop: touch logs/STOP.  Patterns are ordered by the
number of members whose sense differs from the pinwheel (controls first).
"""
import argparse
import itertools
import json
import math
import os
import sys
import time

import numpy as np
from scipy.optimize import minimize

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
ROOT = os.path.abspath(os.path.join(ATT, '..', '..'))
for p in ('attempts/A249-type-t-chase/code', 'attempts/A248-corner-chase/code'):
    sys.path.insert(0, os.path.join(ROOT, p))
import twotilted249 as W                                              # noqa: E402

OUT = os.path.join(ATT, 'results', 'ringsense255.jsonl')
STOP = os.path.join(ATT, 'logs', 'STOP')
Q = math.pi / 4
REFL = (0, 0, 1, 1, 0, 0, 1, 1)                # members of BR, TL live in reflected frames
# D4 action on member indices (B_c, A_c): rotation by 90 deg maps corner BL->BR->TR->TL and swaps the roles
ROT = (3, 2, 5, 4, 7, 6, 1, 0)                 # image index of member i under the quarter turn (B<->A per corner)
MIR = (2, 3, 0, 1, 6, 7, 4, 5)                 # x-mirror: BL<->BR, TR<->TL, roles kept; senses flip


def orbit(p):
    out, q = set(), tuple(p)
    for _ in range(4):
        q = tuple(q[ROT.index(i)] for i in range(8))
        out.add(q)
        out.add(tuple(-q[MIR[i]] for i in range(8)))
    return out


def orbits():
    seen, reps = set(), []
    for p in itertools.product((1, -1), repeat=8):
        if p in seen:
            continue
        o = orbit(p)
        seen |= o
        rep = min(o, key=lambda q: (sum(1 for v in q if v < 0), q))
        reps.append(rep)
    reps.sort(key=lambda q: (min(sum(1 for v in q if v < 0), sum(1 for v in q if v > 0)), q))
    return reps


def halves(pattern):
    """per member the frame-tilt interval realising the prescribed global sense."""
    out = []
    for sg, rf in zip(pattern, REFL):
        low = (sg > 0) != bool(rf)
        out.append((0.0, Q) if low else (Q, 2 * Q))
    return out


def margin(x, s, hv):
    t = W.ring_margin(list(x), s, False, True)
    ts = [x[4 * k + j] for k in range(4) for j in (0, 2)]
    t = list(t) + [min(v - lo, hi - v) for v, (lo, hi) in zip(ts, hv)]
    return min(t)


def start(rng, hv):
    x = np.zeros(16)
    for i, (lo, hi) in enumerate(hv):
        k, j = divmod(i, 2)
        tau = rng.uniform(0.03, 0.5)
        x[4 * k + 2 * j] = lo + tau if lo == 0.0 else hi - tau
        x[4 * k + 2 * j + 1] = rng.uniform(0.55, 0.98)
    return x


def solve(pattern, s, restarts, seed):
    hv = halves(pattern)
    rng = np.random.default_rng(seed)
    best, bx, t0 = -1e9, None, time.time()
    for r in range(restarts):
        if os.path.exists(STOP):
            break
        res = minimize(lambda x: -margin(x, s, hv), start(rng, hv), method='Nelder-Mead',
                       options={'maxiter': 6000, 'xatol': 1e-7, 'fatol': 1e-9, 'adaptive': True})
        if -res.fun > best:
            best, bx = -res.fun, res.x
        if best > 5e-3:
            break
    return {'pattern': ''.join('+' if v > 0 else '-' for v in pattern), 's': s, 'sup_margin': best,
            'x': [float(v) for v in bx] if bx is not None else None, 'restarts_used': r + 1,
            'n_minority': min(sum(1 for v in pattern if v < 0), sum(1 for v in pattern if v > 0)),
            'seconds': time.time() - t0, 'verdict': 'RING-EXISTS' if best > 1e-6 else 'NO-RING-FOUND'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sides', default='3.99,3.877084')
    ap.add_argument('--restarts', type=int, default=6)
    ap.add_argument('--seed', type=int, default=255)
    ap.add_argument('--list', action='store_true')
    a = ap.parse_args()
    reps = orbits()
    if a.list:
        print(len(reps), [''.join('+' if v > 0 else '-' for v in p) for p in reps])
        return
    done = set()
    if os.path.exists(OUT):
        done = {(json.loads(l)['pattern'], round(json.loads(l)['s'], 6)) for l in open(OUT)}
    for s in [float(v) for v in a.sides.split(',')]:
        for p in reps:
            key = (''.join('+' if v > 0 else '-' for v in p), round(s, 6))
            if key in done or os.path.exists(STOP):
                continue
            row = solve(p, s, a.restarts, a.seed)
            with open(OUT, 'a') as f:
                f.write(json.dumps(row) + '\n')
            print(row['pattern'], s, row['verdict'], round(row['sup_margin'], 5), round(row['seconds']), flush=True)


if __name__ == '__main__':
    main()
