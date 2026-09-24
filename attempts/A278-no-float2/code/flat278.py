r"""A278: does a FLAT (axis-aligned) wall cell always land a floater of a FLOAT2 corner in the 4-square model?
Same model and parametrisation as A277's float277 (local261 imported: C, D floaters meeting the open box; X a wall
toucher, Y a floor toucher, both missing the box; every drop of every floater blocked; pair gaps; containment), but
the P1 term counts ONLY the flat cells F_x = [x, x+1] x [0,1] (floor) and G_y = [0,1] x [y, y+1] (wall), any x, y:
objective t = min(local terms, -J_flat(F) for F in {C, D}), J_flat(F) = sup over flat cells of
min(gap to the other three squares, depth into F).  sup t > 0  <=>  a 4-square FLOAT2 configuration with all drops
blocked and NO free flat cell (the residual of the flat-cell mechanism, to be re-tested with any-pose cells);
sup t <= 0  <=>  [M] the flat cells suffice on the model.  Runs ~5-10 min per seed (12 restarts), one python,
BelowNormal, affinity 0xFFFF; resumable (rows keyed by seed).
    python flat278.py --restarts 12 --seeds 1,2  -> results/flat278.jsonl"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np
from scipy.optimize import minimize

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
for a_ in ('A261-box-meeters', 'A259-normal-room', 'A277-float2-room'):
    sys.path.insert(0, os.path.join(ROOT, 'attempts', a_, 'code'))
import local261 as L                                                   # noqa: E402
import geo258 as G8                                                    # noqa: E402
import geom259 as Z                                                    # noqa: E402
import float277 as F7                                                  # noqa: E402  (x_seed from the exact witness)

OUT = os.path.join(HERE, '..', 'results', 'flat278.jsonl')
SPEC, MEET, NOTMEET = 'C:F D:F X:V Y:H', ['C', 'D'], ['X', 'Y']
XS = np.arange(0.0, 2.6, 0.01)


def rect(x0, y0):
    return np.array([[x0, y0], [x0 + 1, y0], [x0 + 1, y0 + 1], [x0, y0 + 1]], float)


def j_flat(P, i):
    """sup over flat floor / wall cells of min(gaps to the others, depth into P[i]); coarse grid then local refine."""
    def val(x0, y0):
        R = rect(x0, y0)
        return min([G8.sat_gap(R, P[j]) for j in range(len(P)) if j != i] + [G8.depth(P[i], R)])
    cands = [(val(x, 0.0), x, 0.0) for x in XS] + [(val(0.0, y), 0.0, y) for y in XS]
    best = max(cands)
    v, x0, y0 = best
    for step in (0.005, 0.001, 0.0002):
        for d in (-step, step):
            for (xx, yy) in ((x0 + d, y0), (x0, y0 + d)) if (x0 > 0 and y0 > 0) else (((x0 + d, 0.0),) if y0 == 0.0 else ((0.0, y0 + d),)):
                if xx >= 0 and yy >= 0:
                    vv = val(xx, yy)
                    if vv > v:
                        v, x0, y0 = vv, xx, yy
    return v, x0, y0


def run(restarts, seed):
    sq, dim = L.layout(SPEC)
    rng = np.random.default_rng(seed)

    def f(x):
        t, ps, nm = L.terms(x, sq, MEET, NOTMEET)
        m = min(t)
        if m > -0.05:
            P = [L.verts(*p) for p in ps]
            for i, (name, role, k) in enumerate(sq):
                if role == 'F':
                    m = min(m, -j_flat(P, i)[0])
        return -m
    best, bx, t0 = -1e9, None, time.time()
    for r in range(restarts):
        x0 = F7.x_seed(sq, rng, 0.02 * (r // 2)) if r % 2 == 0 else \
            np.concatenate([np.append(rng.uniform(0.0, 1.1, 2 if s[1] == 'F' else 1), rng.uniform(0, math.pi / 2)) for s in sq])
        opt = dict(maxiter=3000, xatol=1e-9, fatol=1e-11, adaptive=True)
        res = minimize(f, x0, method='Nelder-Mead', options=opt)
        res = minimize(f, res.x, method='Nelder-Mead', options=opt)
        if -res.fun > best:
            best, bx = -res.fun, res.x
    tt, ps, names = L.terms(bx, sq, MEET, NOTMEET)
    P = [L.verts(*p) for p in ps]
    Jf = {s_[0]: j_flat(P, i) for i, s_ in enumerate(sq) if s_[1] == 'F'}
    row = dict(scenario='FLAT4', squares=SPEC, sup_margin=float(best), restarts=restarts, seed=seed, seconds=round(time.time() - t0, 1),
               poses={n: list(map(float, p)) for n, p in zip(names, ps)}, J_flat={k: list(map(float, v)) for k, v in Jf.items()},
               verdict='RESIDUAL-POINT' if best > 1e-6 else 'NO-WITNESS')
    row['check'] = L.check_witness(ps, sq, MEET, NOTMEET)
    return row


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--restarts', type=int, default=12)
    ap.add_argument('--seeds', default='1,2')
    a = ap.parse_args()
    Z.belownormal()
    done = {json.loads(l)['seed'] for l in open(OUT)} if os.path.exists(OUT) else set()
    for sd in map(int, a.seeds.split(',')):
        if sd in done:
            continue
        row = run(a.restarts, sd)
        with open(OUT, 'a') as fh:
            fh.write(json.dumps(row) + '\n')
        print('FLAT4', sd, row['verdict'], '%.6f' % row['sup_margin'], row['seconds'], 's', flush=True)
