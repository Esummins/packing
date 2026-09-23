"""A271 probe: is STRIP_2 TRUE under H1-H3 alone?  Search (C, X, A, side) with H1-H3 HARD and a unit square Q of the
quadrant, interior-disjoint from C and X, with an interior point in the strip S = T_u \\ C:
    t(q, Q) = min(gap(Q, C), gap(Q, X), Q_xmin, Q_ymin, depth(Q, T_u))  > 0  <=>  a free square of the strip.
Mode 'two': obstacles {C, X} (STRIP_2 as stated); mode 'three': also gap(Q, A) >= 0.  Starts: the adv271 violators
(fixed q, Q from a centre grid), then joint Nelder-Mead over (q, Q).  Every reported witness passes the exact check.
    python probe271.py [seconds=200] [mode=two] -> results/probe271_<mode>.json"""
import json
import math
import os
import sys
import time

import numpy as np
from scipy.optimize import minimize

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ringdom271 as R                                                # noqa: E402
import adv271 as ADV                                                  # noqa: E402

Z = R.Z


def q_square(Qp):
    cx, cy, psi = Qp
    return Z.sq_verts(cx, cy, psi)


def t_of(q, Qp, mode):
    C, X, A, Tu = R.squares(q)
    Q = q_square(Qp)
    terms = [Z.poly_gap(Q, C), Z.poly_gap(Q, X), float(Q[:, 0].min()), float(Q[:, 1].min()), -Z.poly_gap(Q, Tu)]
    if mode == 'three':
        terms.append(Z.poly_gap(Q, A))
    return float(min(terms))


def best_Q_for(q, mode, rng, n=60):
    """max_t over Q for a fixed configuration: grid of centres in [0.5, 2.5]^2 x 6 tilts, polish the 8 best."""
    cands = []
    for cx in np.linspace(0.5, 2.5, 9):
        for cy in np.linspace(0.5, 2.6, 9):
            for psi in np.linspace(0, math.pi / 2, 6, endpoint=False):
                cands.append(((cx, cy, psi), t_of(q, (cx, cy, psi), mode)))
    cands.sort(key=lambda z: -z[1])
    best = cands[0]
    for Qp, _ in cands[:8]:
        r = minimize(lambda p: -t_of(q, p, mode), np.array(Qp), method='Nelder-Mead', options=dict(maxfev=1500, xatol=1e-8))
        if -r.fun > best[1]:
            best = (tuple(float(v) for v in r.x), float(-r.fun))
    return best


def joint(q0, Qp0, mode, budget):
    def f(z):
        q, Qp = z[:8], z[8:]
        v = R.constraints(q) - ADV.EPS
        pen = float(np.sum(np.minimum(v, 0.0) ** 2)) * 1e4 + float(np.sum(v < 0)) * 1e-2
        return -t_of(q, Qp, mode) + pen
    z0 = np.concatenate([q0, Qp0])
    r = minimize(f, z0, method='Nelder-Mead', options=dict(maxfev=6000, xatol=1e-8, fatol=1e-10))
    q, Qp = np.clip(r.x[:8], ADV.LO, ADV.HI), r.x[8:]
    return q, Qp, (t_of(q, Qp, mode) if ADV.feasible(q) else -9.0)


def main():
    budget = float(sys.argv[1]) if len(sys.argv) > 1 else 200.0
    mode = sys.argv[2] if len(sys.argv) > 2 else 'two'
    rng = np.random.default_rng(1)
    adv = json.load(open(os.path.join(HERE, '..', 'results', 'adv271.json')))['results']
    starts = [(k, np.array(v['q'])) for k, v in adv.items()] + ADV.starts(rng, 40)
    t0, rows, best = time.time(), [], None
    for i, (kind, q) in enumerate(starts):
        if time.time() - t0 > budget:
            break
        Qp, t = best_Q_for(q, mode, rng)
        qj, Qj, tj = joint(q, np.array(Qp), mode, budget)
        row = dict(start=str(kind), t_fixed=t, t_joint=tj, q=[float(v) for v in qj], Q=[float(v) for v in Qj],
                   cond={k: R.conditions(qj)[k] for k in R.COND})
        rows.append(row)
        if best is None or max(t, tj) > best['t']:
            best = dict(t=max(t, tj), row=row if tj >= t else dict(start=str(kind), t_fixed=t, q=[float(v) for v in q], Q=list(Qp)))
        print('%-8s fixed %+.4f joint %+.4f  %.0fs' % (str(kind)[:8], t, tj, time.time() - t0), flush=True)
    out = dict(mode=mode, seconds=time.time() - t0, n=len(rows), best_t=best['t'], best=best['row'], rows=rows)
    json.dump(out, open(os.path.join(HERE, '..', 'results', 'probe271_%s.json' % mode), 'w'), indent=1)
    print('BEST t = %+.5f (%s): a free square of the strip exists under H1-H3' % (best['t'], mode) if best['t'] > 0
          else 'BEST t = %+.5f (%s): none found' % (best['t'], mode))


if __name__ == '__main__':
    main()
