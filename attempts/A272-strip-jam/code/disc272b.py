"""A272 disc test, the LOWER cases (centre in (L_h, C_top]).  Mode 'all': centre anywhere above L_h, Q RIGHT of X
(sets Xi, Gam as disc272; covers cases M, A2, A1-right).  Mode 'leftX': centre in (L_h, X_low), Q LEFT of X above
X_low (case A1-left): the forbidden set from X is Xi' = {X_low <= y <= X_top, x >= x_left(y)} (right of X's left
boundary), P = S \\ Xi'.  t as disc272 with q_y - C_top replaced by q_y - L_h (and X_low - q_y for 'leftX').
    python disc272b.py all|leftX [fixed|joint] [seconds] -> results/disc272b_<mode>_<phase>.json"""
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
import disc272 as DC                                                  # noqa: E402

R, ADV, RES, BIG = DC.R, DC.ADV, DC.RES, DC.BIG


def sets(q, mode):
    hu, hv, th, xlow, phi = q[0], q[1], q[2], q[3], q[4]
    C, X, A, Tu = R.squares(q)
    c = math.cos(th)
    Lh, Ctop = hv + c, hv + c + math.sin(th)
    if mode == 'all':
        Xi = Polygon([(0.0, xlow), tuple(X[0]), tuple(X[1]), tuple(X[2]), (0.0, float(X[2][1]))])
    else:
        Xi = Polygon([tuple(X[0]), (BIG, xlow), (BIG, float(X[2][1])), tuple(X[2]), tuple(X[3])])
    Gam = Polygon([tuple(C[0]), (BIG, hv), (BIG, Ctop), tuple(C[2]), tuple(C[3])])
    P = Polygon(Tu).difference(Polygon(C)).difference(Xi)
    return Xi, Gam, P, Lh, Ctop, xlow


def t_disc(q, pt, mode, S=None):
    Xi, Gam, P, Lh, Ctop, xlow = S if S is not None else sets(q, mode)
    z = Point(pt)
    terms = [z.distance(Xi) - 0.5, z.distance(Gam) - 0.5, pt[1] - Lh,
             0.5 ** 0.5 - (z.distance(P) if not P.is_empty else BIG), pt[0] - 0.5, pt[1] - 0.5]
    if mode == 'leftX':
        terms.append(xlow - pt[1])
    return float(min(terms))


def best_q(q, mode):
    S = sets(q, mode)
    Lh = S[3]
    cands = []
    for cx in np.linspace(0.5, 3.0, 26):
        for cy in np.linspace(Lh, Lh + 1.5, 31):
            cands.append(((cx, cy), t_disc(q, (cx, cy), mode, S)))
    cands.sort(key=lambda z: -z[1])
    best = cands[0]
    for pt, _ in cands[:6]:
        r = minimize(lambda p: -t_disc(q, p, mode, S), np.array(pt), method='Nelder-Mead',
                     options=dict(maxfev=600, xatol=1e-9, fatol=1e-12))
        if -r.fun > best[1]:
            best = (tuple(float(v) for v in r.x), float(-r.fun))
    return best


def run(mode, phase, budget):
    t0, rows, best = time.time(), [], -9.0
    if phase == 'fixed':
        adv = json.load(open(os.path.join(DC.U.A271, '..', 'results', 'adv271.json')))['results']
        rng = np.random.default_rng(5)
        starts = [(k, np.array(v['q'])) for k, v in adv.items()] + ADV.starts(rng, 30)
        for kind, q in starts:
            pt, t = best_q(q, mode)
            rows.append(dict(start=str(kind), t_disc=t, q=[float(v) for v in q], centre=list(pt)))
            best = max(best, t)
            print('%-8s %s t_disc %+.4f  centre (%.3f, %.3f)  %.0fs' % (str(kind)[:8], mode, t, pt[0], pt[1], time.time() - t0), flush=True)
    else:
        fixed = json.load(open(os.path.join(RES, 'disc272b_%s_fixed.json' % mode)))['rows']
        fixed.sort(key=lambda r: -r['t_disc'])

        def f(z):
            q, pt = z[:8], z[8:]
            v = R.constraints(q) - ADV.EPS
            pen = float(np.sum(np.minimum(v, 0.0) ** 2)) * 1e4 + float(np.sum(v < 0)) * 1e-2
            try:
                return -t_disc(q, pt, mode) + pen
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
            pt, t = best_q(q, mode)
            rows.append(dict(start=r0['start'] + '+joint', t_disc=t, q=[float(v) for v in q], centre=list(pt),
                             cond={k: R.conditions(q)[k] for k in R.COND}, exact_H1H3=True))
            best = max(best, t)
            print('%-8s %s joint t_disc %+.4f  %.0fs' % (r0['start'][:8], mode, t, time.time() - t0), flush=True)
    out = dict(mode=mode, phase=phase, seconds=time.time() - t0, n=len(rows), best_t=best, rows=rows)
    json.dump(out, open(os.path.join(RES, 'disc272b_%s_%s.json' % (mode, phase)), 'w'), indent=1)
    print('%s %s sup t_disc = %+.5f' % (mode, phase, best))


if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else 'fixed', float(sys.argv[3]) if len(sys.argv) > 3 else 500.0)
