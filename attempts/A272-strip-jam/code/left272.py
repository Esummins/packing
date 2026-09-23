"""A272 UPPER-case probe WITH the LEFT constraint (strip_enclosure.md s.1: a square that contains a strip point has
all its horizontal chords at heights in (h_v, C_top) LEFT of C).  upper272's near-misses violate it: they sit RIGHT of
C below C_top and touch T_u's right edge from outside (h_u -> 0), which says nothing about the wedge entry.  Here
    t_L(q, Q) = min(gap(Q, C), gap(Q, X), Q_xmin, Q_ymin, depth(Q, T_u), q_y - L_h, left(Q, C)),
left(Q, C) = -max over the vertices of Q clipped to the bands [h_v, L_h], [L_h, C_top] of (x - l_C(y)) (l_C affine
on each band, so the max is at a vertex).  Modes and outputs as upper272 (results/left272_{fixed,joint}.json)."""
import json
import math
import os
import sys
import time

import numpy as np
from scipy.optimize import minimize
from shapely.geometry import Polygon, box as sbox

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import upper272 as U                                                  # noqa: E402

R, Z, PR, ADV = U.R, U.Z, U.PR, U.ADV
RES = U.RES
TERMS = U.TERMS + ['left_of_C']


def l_C(q, y):
    hu, hv, th = q[0], q[1], q[2]
    c, s = math.cos(th), math.sin(th)
    Lh = hv + c
    if y <= Lh or th < 1e-12:
        return hu + s - (y - hv) * math.tan(th)
    return hu + (y - Lh) / math.tan(th)


def left_term(q, Q):
    hu, hv, th = q[0], q[1], q[2]
    Lh, Ctop = hv + math.cos(th), hv + math.cos(th) + math.sin(th)
    P = Polygon(Q)
    worst = -9.0
    for lo, hi in ((hv, Lh), (Lh, Ctop)):
        if hi - lo < 1e-12:
            continue
        clip = P.intersection(sbox(-5, lo, 9, hi))
        if clip.is_empty:
            continue
        for G in getattr(clip, 'geoms', [clip]):
            if G.geom_type != 'Polygon':
                continue
            for x, y in np.array(G.exterior.coords):
                worst = max(worst, x - l_C(q, y))
    return -worst if worst > -9.0 else 9.0


def terms_of(q, Qp):
    Q = PR.q_square(Qp)
    return U.terms_of(q, Qp) + [left_term(q, Q)]


def t_L(q, Qp):
    return float(min(terms_of(q, Qp)))


def best_Q(q, n_polish=12):
    hu, hv, th = q[0], q[1], q[2]
    Lh = hv + math.cos(th)
    cands = []
    for cx in np.linspace(0.3, 2.4, 10):
        for cy in np.linspace(Lh, Lh + 1.5, 9):
            for psi in np.linspace(0, math.pi / 2, 8, endpoint=False):
                cands.append(((cx, cy, psi), t_L(q, (cx, cy, psi))))
    cands.sort(key=lambda z: -z[1])
    best = cands[0]
    for Qp, _ in cands[:n_polish]:
        r = minimize(lambda p: -t_L(q, p), np.array(Qp), method='Nelder-Mead',
                     options=dict(maxfev=2500, xatol=1e-9, fatol=1e-12))
        if -r.fun > best[1]:
            best = (tuple(float(v) for v in r.x), float(-r.fun))
    return best


def active(q, Qp, tol=2e-3):
    tv = terms_of(q, Qp)
    m = min(tv)
    return [TERMS[i] for i, v in enumerate(tv) if v - m <= tol], [round(v, 5) for v in tv]


def row_for(kind, q, Qp, t):
    act, tv = active(q, Qp)
    return dict(start=str(kind), t_left=t, Q=[float(v) for v in Qp], q=[float(v) for v in q], active=act,
                terms=dict(zip(TERMS, tv)), frame=U.frame(q, Qp), cond={k: R.conditions(q)[k] for k in R.COND},
                exact_H1H3=bool(R.constraints(q).min() >= -1e-9))


def run_fixed():
    adv = json.load(open(os.path.join(U.A271, '..', 'results', 'adv271.json')))['results']
    rng = np.random.default_rng(3)
    starts = [(k, np.array(v['q'])) for k, v in adv.items() if k in ('U3', 'U4', 'U5', 'U6', 'U8', 'D1', 'U2')]
    starts += ADV.starts(rng, 10)
    t0, rows = time.time(), []
    for kind, q in starts:
        Qp, t = best_Q(q)
        rows.append(row_for(kind, q, Qp, t))
        print('%-8s t_left %+.4f  active %s  %.0fs' % (str(kind)[:8], t, rows[-1]['active'], time.time() - t0), flush=True)
    out = dict(mode='fixed', seconds=time.time() - t0, n=len(rows), best_t=max(r['t_left'] for r in rows), rows=rows)
    json.dump(out, open(os.path.join(RES, 'left272_fixed.json'), 'w'), indent=1)


def run_joint(budget):
    fixed = json.load(open(os.path.join(RES, 'left272_fixed.json')))['rows']
    t0, rows, best = time.time(), [], -9.0

    def f(z):
        q, Qp = z[:8], z[8:]
        v = R.constraints(q) - ADV.EPS
        pen = float(np.sum(np.minimum(v, 0.0) ** 2)) * 1e4 + float(np.sum(v < 0)) * 1e-2
        return -t_L(q, Qp) + pen
    for r0 in fixed:
        if time.time() - t0 > budget:
            break
        z0 = np.concatenate([r0['q'], r0['Q']])
        r = minimize(f, z0, method='Nelder-Mead', options=dict(maxfev=8000, xatol=1e-9, fatol=1e-12))
        q = np.clip(r.x[:8], ADV.LO, ADV.HI)
        if not ADV.feasible(q):
            rows.append(dict(start=r0['start'], t_left=-9.0, note='joint end infeasible', q=[float(v) for v in q]))
            continue
        Qp, t = best_Q(q, n_polish=6)
        rows.append(row_for(r0['start'] + '+joint', q, Qp, t))
        best = max(best, t)
        print('%-8s joint t_left %+.4f  active %s  %.0fs' % (r0['start'][:8], t, rows[-1]['active'], time.time() - t0), flush=True)
    out = dict(mode='joint', seconds=time.time() - t0, n=len(rows), best_t=best, rows=rows)
    json.dump(out, open(os.path.join(RES, 'left272_joint.json'), 'w'), indent=1)
    print('JOINT sup t_left = %+.5f' % best)


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'fixed'
    if mode == 'fixed':
        run_fixed()
    else:
        run_joint(float(sys.argv[2]) if len(sys.argv) > 2 else 900.0)
