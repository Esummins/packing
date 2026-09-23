"""A272 UPPER-case probe: on each adv271 violator (and the rings / random H1-H3 points) find the best unit square Q
of the quadrant with its CENTRE ABOVE L_h (the UPPER case of strip_enclosure.md s.2-3: WEDGE-FLOAT already puts
every free strip square there), interior-disjoint from C and X, with an interior point in S = T_u \\ C:
    t_up(q, Q) = min(gap(Q, C), gap(Q, X), Q_xmin, Q_ymin, depth(Q, T_u), q_y - L_h).
probe271's sup t sits at the corner-box entry (the vacuous h_v -> 1 boundary); this probe isolates the wedge entry
that A267's (U3)-(U6), (U8) steps guard, and reports WHICH terms are active at the optimum (what stops Q).
Mode 'fixed': Q only, per configuration.  Mode 'joint': also over q with H1-H3 HARD (adv271.EPS, exact SAT).
    python upper272.py fixed            -> results/upper272_fixed.json   (< 2 min)
    python upper272.py joint [seconds]  -> results/upper272_joint.json"""
import json
import math
import os
import sys
import time

import numpy as np
from scipy.optimize import minimize

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
A271 = os.path.join(HERE, '..', '..', 'A271-ring-domain', 'code')
sys.path.insert(0, A271)
import ringdom271 as R                                                # noqa: E402
import adv271 as ADV                                                  # noqa: E402
import probe271 as PR                                                 # noqa: E402

Z = R.Z
RES = os.path.join(HERE, '..', 'results')
TERMS = ['gap_C', 'gap_X', 'wall', 'floor', 'depth_Tu', 'centre_above_Lh']


def terms_of(q, Qp):
    C, X, A, Tu = R.squares(q)
    Q = PR.q_square(Qp)
    Lh = q[1] + math.cos(q[2])
    return [Z.poly_gap(Q, C), Z.poly_gap(Q, X), float(Q[:, 0].min()), float(Q[:, 1].min()),
            -Z.poly_gap(Q, Tu), float(Qp[1] - Lh)]


def t_up(q, Qp):
    return float(min(terms_of(q, Qp)))


def frame(q, Qp):
    """Q in C's frame (a along C's upper-left edge from L, b outward) and in the corner frame."""
    hu, hv, th = q[0], q[1], q[2]
    c, s = math.cos(th), math.sin(th)
    L = np.array([hu, hv + c])
    e, n = np.array([c, s]), np.array([-s, c])
    Q = PR.q_square(Qp)
    a, b = (Q - L) @ e, (Q - L) @ n
    cd = R.conditions(q)
    return dict(a_min=float(a.min()), a_max=float(a.max()), b_min=float(b.min()), b_max=float(b.max()),
                a_star=cd['a_star'], a_B=cd['a_B'], b_B=cd['b_B'], a_R=cd['a_R'], b_R=cd['b_R'], beta_deg=cd['beta_deg'],
                q_y=float(Qp[1]), L_h=float(hv + c), C_top=float(hv + c + s), X_low=float(q[3]),
                X_top=float(q[3] + math.cos(q[4]) + math.sin(q[4])), Q_ymin=float(Q[:, 1].min()),
                Q_xmin=float(Q[:, 0].min()), psi_deg=float((Qp[2] % (math.pi / 2)) / R.DEG))


def best_Q(q, n_polish=12):
    hu, hv, th = q[0], q[1], q[2]
    Lh = hv + math.cos(th)
    cands = []
    for cx in np.linspace(0.3, 2.8, 11):
        for cy in np.linspace(Lh, Lh + 1.6, 9):
            for psi in np.linspace(0, math.pi / 2, 8, endpoint=False):
                cands.append(((cx, cy, psi), t_up(q, (cx, cy, psi))))
    cands.sort(key=lambda z: -z[1])
    best = cands[0]
    for Qp, _ in cands[:n_polish]:
        r = minimize(lambda p: -t_up(q, p), np.array(Qp), method='Nelder-Mead',
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
    return dict(start=str(kind), t_upper=t, Q=[float(v) for v in Qp], q=[float(v) for v in q], active=act,
                terms=dict(zip(TERMS, tv)), frame=frame(q, Qp), cond={k: R.conditions(q)[k] for k in R.COND},
                exact_H1H3=bool(R.constraints(q).min() >= -1e-9))


def run_fixed():
    adv = json.load(open(os.path.join(A271, '..', 'results', 'adv271.json')))['results']
    rng = np.random.default_rng(2)
    starts = [(k, np.array(v['q'])) for k, v in adv.items() if k in ('U3', 'U4', 'U5', 'U6', 'U8', 'D1', 'D2', 'U2')]
    starts += ADV.starts(rng, 12)
    t0, rows = time.time(), []
    for kind, q in starts:
        Qp, t = best_Q(q)
        rows.append(row_for(kind, q, Qp, t))
        print('%-8s t_upper %+.4f  active %s  %.0fs' % (str(kind)[:8], t, rows[-1]['active'], time.time() - t0), flush=True)
    out = dict(mode='fixed', seconds=time.time() - t0, n=len(rows), best_t=max(r['t_upper'] for r in rows), rows=rows)
    json.dump(out, open(os.path.join(RES, 'upper272_fixed.json'), 'w'), indent=1)


def run_joint(budget):
    fixed = json.load(open(os.path.join(RES, 'upper272_fixed.json')))['rows']
    t0, rows, best = time.time(), [], -9.0

    def f(z):
        q, Qp = z[:8], z[8:]
        v = R.constraints(q) - ADV.EPS
        pen = float(np.sum(np.minimum(v, 0.0) ** 2)) * 1e4 + float(np.sum(v < 0)) * 1e-2
        return -t_up(q, Qp) + pen
    for r0 in fixed:
        if time.time() - t0 > budget:
            break
        z0 = np.concatenate([r0['q'], r0['Q']])
        r = minimize(f, z0, method='Nelder-Mead', options=dict(maxfev=8000, xatol=1e-9, fatol=1e-12))
        q, Qp = np.clip(r.x[:8], ADV.LO, ADV.HI), r.x[8:]
        if not ADV.feasible(q):
            Qp2, t2 = r0['Q'], -9.0
            rows.append(dict(start=r0['start'], t_upper=t2, note='joint end infeasible', q=[float(v) for v in q]))
            continue
        Qp, t = best_Q(q, n_polish=6)
        rows.append(row_for(r0['start'] + '+joint', q, Qp, t))
        best = max(best, t)
        print('%-8s joint t_upper %+.4f  active %s  %.0fs' % (r0['start'][:8], t, rows[-1]['active'], time.time() - t0), flush=True)
    out = dict(mode='joint', seconds=time.time() - t0, n=len(rows), best_t=best, rows=rows)
    json.dump(out, open(os.path.join(RES, 'upper272_joint.json'), 'w'), indent=1)
    print('JOINT sup t_upper = %+.5f' % best)


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'fixed'
    if mode == 'fixed':
        run_fixed()
    else:
        run_joint(float(sys.argv[2]) if len(sys.argv) > 2 else 600.0)
