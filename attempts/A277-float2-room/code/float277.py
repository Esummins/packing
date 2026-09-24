"""A277 [M]: FLOAT2 corners in the P1 sense: every drop of every floater blocked (local261.terms) AND no wall-touching
unit cell of any pose (jam261 grid, JAM_COARSE) that meets a floater is free of the other squares (A261's J < 0), with
local261 / jam261 imported (never edited).  Objective t = min(all terms, -J_F for every floater F); sup t > 0 <=> a
FLOAT2 corner that P1 cannot land (in this local model).  Scenarios (name: squares, meet, notmeet):
  F4  C:F D:F X:V Y:H   C D | X Y     the 4-square FLOAT2 (A261's E, 10 restarts -> NO-WITNESS; witness277b says a witness exists)
  F4b C:F D:F X:V Y:H   C D | -       X, Y free to meet the box
  F5  C:F D:F K:F X:V Y:H  C D | X Y  a fifth square K floating (an indirect blocker allowed)
  F3  C:F D:F X:V       C D | X       no floor toucher at all
Seeds: random (local261 style) + the exact witness of witness277b perturbed.  Resumable: one jsonl row per (scenario, seed).
    python float277.py --restarts 12   -> results/float277.jsonl"""
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
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A261-box-meeters', 'code'))
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A259-normal-room', 'code'))
os.environ.setdefault('JAM_COARSE', '1')
import local261 as L                                                   # noqa: E402
import jam261 as J                                                     # noqa: E402  (any-pose P1 test J on the coarse grid)
import geom259 as Z                                                    # noqa: E402

OUT = os.path.join(HERE, '..', 'results', 'float277.jsonl')
SCEN = {'F4': ('C:F D:F X:V Y:H', 'C D', 'X Y'), 'F4b': ('C:F D:F X:V Y:H', 'C D', ''),
        'F5': ('C:F D:F K:F X:V Y:H', 'C D', 'X Y'), 'F3': ('C:F D:F X:V', 'C D', 'X')}
WIT = json.load(open(os.path.join(HERE, '..', 'results', 'float277_witness.json')))


def x_seed(sq, rng, jitter):
    """local261's parametrisation: F -> (sqrt(h_u), sqrt(h_v), th); V -> (sqrt(y_low), phi); H -> (sqrt(x_low), al)."""
    w = lambda th: abs(math.cos(th)) + abs(math.sin(th))
    x = []
    for name, role, k in sq:
        if name in ('C', 'D', 'X'):
            cx, cy, thd = WIT['poses'][name]
            th = math.radians(thd)
            if role == 'F':
                x += [math.sqrt(max(cx - w(th) / 2, 1e-6)), math.sqrt(max(cy - w(th) / 2, 1e-6)), th]
            else:
                x += [math.sqrt(max(cy - w(th) / 2, 1e-6)), th]
        elif name == 'Y':
            Yv = np.array(WIT['Y_vertices'])
            x += [math.sqrt(float(Yv[:, 0].min())), math.radians(77.21)]
        else:
            x += list(np.append(rng.uniform(0.0, 1.1, 2), rng.uniform(0, math.pi / 2)))
    return np.array(x) + jitter * rng.standard_normal(len(x))


def run(key, restarts, seed):
    spec, meet, notmeet = SCEN[key]
    sq, dim = L.layout(spec)
    meet, notmeet = meet.split(), notmeet.split()
    rng = np.random.default_rng(seed)
    def f(x):
        t, ps, nm = L.terms(x, sq, meet, notmeet)
        m = min(t)
        if m > -0.05:                                                  # P1 any-pose: no wall cell meeting a floater is free of the rest
            P = [L.verts(*p) for p in ps]
            G = [J.gaps(V) for V in P]
            for i, (name, role, k) in enumerate(sq):
                if role == 'F':
                    m = min(m, -float(np.minimum.reduce([G[j] for j in range(len(P)) if j != i] + [-G[i]]).max()))
        return -m
    best, bx, t0 = -1e9, None, time.time()
    for r in range(restarts):
        if r % 2 == 0:
            x0 = x_seed(sq, rng, 0.02 * (r // 2))
        else:
            x0 = np.concatenate([np.append(rng.uniform(0.0, 1.1, 2 if s[1] == 'F' else 1), rng.uniform(0, math.pi / 2)) for s in sq])
        opt = dict(maxiter=4000, xatol=1e-9, fatol=1e-11, adaptive=True)
        res = minimize(f, x0, method='Nelder-Mead', options=opt)
        res = minimize(f, res.x, method='Nelder-Mead', options=opt)
        if -res.fun > best:
            best, bx = -res.fun, res.x
    tt, ps, names = L.terms(bx, sq, meet, notmeet)
    P = [L.verts(*p) for p in ps]
    G = [J.gaps(V) for V in P]
    Jv = {s_[0]: float(np.minimum.reduce([G[j] for j in range(len(P)) if j != i] + [-G[i]]).max()) for i, s_ in enumerate(sq) if s_[1] == 'F'}
    row = dict(scenario=key, squares=spec, meet=meet, notmeet=notmeet, sup_margin=float(best), restarts=restarts, seed=seed,
               seconds=round(time.time() - t0, 1), poses={n: list(map(float, p)) for n, p in zip(names, ps)},
               J_coarse=Jv, verdict='FEASIBLE-WITNESS' if best > 1e-6 else 'NO-WITNESS')
    row['check'] = L.check_witness(ps, sq, meet, notmeet)
    if row['verdict'] == 'FEASIBLE-WITNESS' and not row['check']['ok']:
        row['verdict'] = 'CHECK-FAILED'
    return row


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--restarts', type=int, default=12)
    ap.add_argument('--seeds', default='1,2')
    ap.add_argument('--only', default='F4,F4b,F5,F3')
    a = ap.parse_args()
    Z.belownormal()
    done = {(json.loads(l)['scenario'], json.loads(l)['seed']) for l in open(OUT)} if os.path.exists(OUT) else set()
    for key in a.only.split(','):
        for sd in map(int, a.seeds.split(',')):
            if (key, sd) in done:
                continue
            row = run(key, a.restarts, sd)
            with open(OUT, 'a') as fh:
                fh.write(json.dumps(row) + '\n')
            print(key, sd, row['verdict'], '%.6f' % row['sup_margin'], row['seconds'], 's', flush=True)
