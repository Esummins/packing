#!/usr/bin/env python3
"""
tiltmax.py -- how many unit squares with tilt <= eps fit in [0,3.84]^2 ?

This measures the WEAK LINK of the A26 ledger.  band.py proves rigorously (an
elementary pigeonhole on the centre lattice) only

        at most 9 squares have tilt within  eps* = 3.326 deg  of axis-parallel

and the bound jumps uselessly to 16 above eps*.  The composition experiment
(compose.py) needs the much stronger "at most 9 (or 10) squares have tilt within
eps of axis-parallel" for eps of order 10-30 deg.  Before anyone tries to PROVE
such a statement it is worth knowing whether it is TRUE.

This is a NUMERICAL (non-rigorous) search: for each eps and n, minimise a smooth
overlap+containment penalty over n placements with theta in [-eps, eps], from many
random starts.  A start that reaches penalty 0 and passes the exact float SAT
check `code/squares.is_valid(X, s, tol=1e-9)` is a WITNESS that n squares of tilt
<= eps DO fit -- which REFUTES the corresponding forcing conjecture.
Failure to find one is evidence, not proof.

    python tiltmax.py --n 10 --eps 0 3 5 8 10 15 20 28.5 45 --restarts 400 --workers 8
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import os
import sys
import time
from multiprocessing import Pool

import numpy as np
from scipy.optimize import minimize

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'code'))
import squares as SQ                                    # noqa: E402

S = 3.84


def penalty(v, n, s, eps):
    X = v.reshape(n, 3)
    sep = SQ.pair_separations(X)
    cm = SQ.containment_margin(X, s)
    p = np.sum(np.minimum(sep, 0.0) ** 2) + np.sum(np.minimum(cm, 0.0) ** 2)
    return p


def one_start(args):
    n, eps_deg, seed, s = args
    rng = np.random.default_rng(seed)
    e = math.radians(eps_deg)
    best = None
    for _ in range(3):
        X = np.empty((n, 3))
        X[:, 0] = rng.uniform(0.6, s - 0.6, n)
        X[:, 1] = rng.uniform(0.6, s - 0.6, n)
        X[:, 2] = rng.uniform(-e, e, n) if e > 0 else 0.0
        lo = np.tile([0.5, 0.5, -e], n)
        hi = np.tile([s - 0.5, s - 0.5, e], n)
        r = minimize(penalty, X.ravel(), args=(n, s, e),
                     method='L-BFGS-B', bounds=list(zip(lo, hi)),
                     options=dict(maxiter=4000, ftol=1e-18, gtol=1e-14))
        val = r.fun
        Xr = r.x.reshape(n, 3)
        # polish: push apart slightly then re-minimise
        for _k in range(2):
            r = minimize(penalty, Xr.ravel(), args=(n, s, e), method='L-BFGS-B',
                         bounds=list(zip(lo, hi)),
                         options=dict(maxiter=4000, ftol=1e-20, gtol=1e-16))
            Xr = r.x.reshape(n, 3)
            val = min(val, r.fun)
        m = min(SQ.pair_separations(Xr).min(), SQ.containment_margin(Xr, s).min())
        if best is None or m > best[0]:
            best = (float(m), Xr.copy())
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=10)
    ap.add_argument('--eps', type=float, nargs='+',
                    default=[0, 3, 5, 8, 10, 15, 20, 28.5, 45])
    ap.add_argument('--restarts', type=int, default=300)
    ap.add_argument('--workers', type=int, default=8)
    ap.add_argument('--s', type=float, default=S)
    ap.add_argument('--out', default='results/tiltmax.json')
    a = ap.parse_args()
    os.chdir(HERE)
    res = {}
    t0 = time.time()
    for eps in a.eps:
        jobs = [(a.n, eps, 10_000 * int(eps * 10) + k, a.s) for k in range(a.restarts)]
        with Pool(a.workers) as pool:
            outs = pool.map(one_start, jobs, chunksize=4)
        outs.sort(key=lambda o: -o[0])
        m, X = outs[0]
        ok = bool(SQ.is_valid(X, a.s, tol=1e-9))
        res[f'{eps}'] = dict(n=a.n, eps=eps, best_margin=m, valid=ok,
                             X=X.tolist() if ok or m > -1e-3 else None)
        print(f'  eps={eps:6.2f} deg  n={a.n}: best min-margin = {m:+.6f}  '
              f'{"FITS (witness found)" if ok else "no packing found"}',
              flush=True)
        json.dump(res, open(a.out, 'w'), indent=1)
    print(f'DONE in {time.time()-t0:.0f}s -> {a.out}', flush=True)


if __name__ == '__main__':
    main()
