"""A272 disc test for the MAIN case (Q's centre above C_top): a free strip square Q has (i) all horizontal chords
at heights in [X_low, X_top] RIGHT of X, i.e. int Q misses the convex set Xi = {X_low <= y <= X_top, x <= r_X(y)};
(ii) its part below C_top LEFT of C (LEFT), i.e. int Q misses the convex set Gam = {h_v <= y <= C_top, x >= l_C(y)};
(iii) its inscribed disc D(q, 1/2) inside Q and its interior point p of the strip within 1/sqrt2 of the centre q.
So NECESSARILY  dist(q, Xi) >= 1/2, dist(q, Gam) >= 1/2, q_y > C_top, dist(q, P) < 1/sqrt2,  P = S \\ (Xi u Gam).
    t_disc(q) = min(dist(q,Xi) - 1/2, dist(q,Gam) - 1/2, q_y - C_top, 1/sqrt2 - dist(q, P)).
If sup t_disc < 0 on the H1-H3 set, the main case is a statement about THREE convex sets and a point (no tilt).
    python disc272.py [fixed|joint] [seconds]  -> results/disc272_<mode>.json"""
import json
import math
import os
import sys
import time

import numpy as np
from scipy.optimize import minimize
from shapely.geometry import Point, Polygon

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import upper272 as U                                                  # noqa: E402

R, ADV = U.R, U.ADV
RES = U.RES
BIG = 9.0


def sets(q):
    hu, hv, th, xlow, phi = q[0], q[1], q[2], q[3], q[4]
    C, X, A, Tu = R.squares(q)
    c, s = math.cos(th), math.sin(th)
    Ctop = hv + c + s
    Xi = Polygon([(0.0, xlow), tuple(X[0]), tuple(X[1]), tuple(X[2]), (0.0, float(X[2][1]))])
    Gam = Polygon([tuple(C[0]), (BIG, hv), (BIG, Ctop), tuple(C[2]), tuple(C[3])])
    P = Polygon(Tu).difference(Polygon(C)).difference(Xi)
    return Xi, Gam, P, Ctop


def t_disc(q, pt, S=None):
    Xi, Gam, P, Ctop = S if S is not None else sets(q)
    z = Point(pt)
    return float(min(z.distance(Xi) - 0.5, z.distance(Gam) - 0.5, pt[1] - Ctop,
                     0.5 ** 0.5 - (z.distance(P) if not P.is_empty else BIG)))


def best_q(q):
    S = sets(q)
    Ctop = S[3]
    cands = []
    for cx in np.linspace(0.2, 3.0, 29):
        for cy in np.linspace(Ctop, Ctop + 1.0, 21):
            cands.append(((cx, cy), t_disc(q, (cx, cy), S)))
    cands.sort(key=lambda z: -z[1])
    best = cands[0]
    for pt, _ in cands[:6]:
        r = minimize(lambda p: -t_disc(q, p, S), np.array(pt), method='Nelder-Mead',
                     options=dict(maxfev=600, xatol=1e-9, fatol=1e-12))
        if -r.fun > best[1]:
            best = (tuple(float(v) for v in r.x), float(-r.fun))
    return best


def run_fixed():
    adv = json.load(open(os.path.join(U.A271, '..', 'results', 'adv271.json')))['results']
    rng = np.random.default_rng(4)
    starts = [(k, np.array(v['q'])) for k, v in adv.items()] + ADV.starts(rng, 30)
    t0, rows = time.time(), []
    for kind, q in starts:
        pt, t = best_q(q)
        rows.append(dict(start=str(kind), t_disc=t, q=[float(v) for v in q], centre=list(pt),
                         cond={k: R.conditions(q)[k] for k in R.COND}))
        print('%-8s t_disc %+.4f  centre (%.3f, %.3f)  %.0fs' % (str(kind)[:8], t, pt[0], pt[1], time.time() - t0), flush=True)
    out = dict(mode='fixed', seconds=time.time() - t0, n=len(rows), best_t=max(r['t_disc'] for r in rows), rows=rows)
    json.dump(out, open(os.path.join(RES, 'disc272_fixed.json'), 'w'), indent=1)


def run_joint(budget):
    fixed = json.load(open(os.path.join(RES, 'disc272_fixed.json')))['rows']
    fixed.sort(key=lambda r: -r['t_disc'])
    t0, rows, best = time.time(), [], -9.0

    def f(z):
        q, pt = z[:8], z[8:]
        v = R.constraints(q) - ADV.EPS
        pen = float(np.sum(np.minimum(v, 0.0) ** 2)) * 1e4 + float(np.sum(v < 0)) * 1e-2
        try:
            return -t_disc(q, pt) + pen
        except Exception:
            return 1e3
    for r0 in fixed:
        if time.time() - t0 > budget:
            break
        r = minimize(f, np.concatenate([r0['q'], r0['centre']]), method='Nelder-Mead',
                     options=dict(maxfev=6000, xatol=1e-9, fatol=1e-12))
        q = np.clip(r.x[:8], ADV.LO, ADV.HI)
        if not ADV.feasible(q):
            continue
        pt, t = best_q(q)
        rows.append(dict(start=r0['start'] + '+joint', t_disc=t, q=[float(v) for v in q], centre=list(pt),
                         cond={k: R.conditions(q)[k] for k in R.COND}, exact_H1H3=True))
        best = max(best, t)
        print('%-8s joint t_disc %+.4f  %.0fs' % (r0['start'][:8], t, time.time() - t0), flush=True)
    out = dict(mode='joint', seconds=time.time() - t0, n=len(rows), best_t=best, rows=rows)
    json.dump(out, open(os.path.join(RES, 'disc272_joint.json'), 'w'), indent=1)
    print('JOINT sup t_disc = %+.5f' % best)


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'fixed'
    if mode == 'fixed':
        run_fixed()
    else:
        run_joint(float(sys.argv[2]) if len(sys.argv) > 2 else 600.0)
