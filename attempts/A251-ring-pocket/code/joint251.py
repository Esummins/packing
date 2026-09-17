"""A251 task 4 / the family-wide obligation: RING + k FREE SQUARES as ONE SAT search.

RING-POCKET(11) asks that the pocket of every all-ADJ ring of the family holds at most TWO unit
squares.  The direct form is a feasibility question in 16 + 3k coordinates at each side:

    maximise  min( ring feasibility terms (family251),
                   the k free squares inside [0, s]^2,
                   free-vs-ring and free-vs-free polygon gaps )

sup < 0 at k = 3 over the window = no ring of the family holds three squares [T-computed];
sup > 0 at k = 1 is A249's poke.  Mode `far` maximises |q - O| over (ring, one free square) --
the radius R of Lemma CENTRE-DISC, which with THREE-DISC (three points pairwise >= 1 apart need a
disc of radius >= 1/sqrt3 = 0.5774) certifies capacity <= 2 when R < 0.5774.

    python joint251.py --mode fit|far [--sides ..] [--ks 1,2,3] [--rings N] [--restarts N]
        -> results/joint251.json    (resumable per side+mode+k; logs/STOP honoured)
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
import family251 as F                                                 # noqa: E402
import twotilted249 as W                                              # noqa: E402
import geom248 as G                                                   # noqa: E402

RES = os.path.join(ATT, 'results', 'joint251.json')
STOP = os.path.join(ATT, 'logs', 'STOP')
SEED_X = [0.254, 0.891, 0.254, 0.695, 1.317, 0.695, 1.317, 0.891]


def free_polys(y, k):
    return [G.verts(y[3 * i:3 * i + 3]) for i in range(k)]


def joint_terms(y, s, k):
    """the full term list: the ring's own terms, then the free squares' containment and gaps."""
    t = list(W.ring_margin(list(y[:16]), s, False, True))
    polys, _, _ = W.ring_polys(list(y[:16]), s, False)
    new = free_polys(y[16:], k)
    for i, V in enumerate(new):
        t.append(float(min(V[:, 0].min(), V[:, 1].min(), s - V[:, 0].max(), s - V[:, 1].max())))
        for P in polys:
            t.append(float(G.poly_gap(V, P)))
        for j in range(i):
            t.append(float(G.poly_gap(V, new[j])))
    return t


def joint_margin(y, s, k, terms=False):
    t = joint_terms(y, s, k)
    return t if terms else float(min(t))


def far_margin(y, s, terms=False):
    """feasibility of (ring, one free square) with the free square's centre at distance >= r
    from O; we maximise r subject to feasibility by penalising infeasibility hard."""
    t = joint_terms(y, s, 1)
    return t if terms else float(min(t))


def fit_k(x, s, k, restarts, rng):
    """place k free squares in the pocket of the fixed ring x (Nelder-Mead on the least gap)."""
    polys, _, _ = W.ring_polys(list(x), s, False)
    best = None
    for _ in range(restarts):
        y0 = np.concatenate([[rng.uniform(0.7, s - 0.7), rng.uniform(0.7, s - 0.7),
                              rng.uniform(0, math.pi / 2)] for _ in range(k)])

        def f(z):
            new = free_polys(z, k)
            m = math.inf
            for i, V in enumerate(new):
                m = min(m, V[:, 0].min(), V[:, 1].min(), s - V[:, 0].max(), s - V[:, 1].max())
                for P in polys:
                    m = min(m, G.poly_gap(V, P))
                for j in range(i):
                    m = min(m, G.poly_gap(V, new[j]))
            return -m
        r = minimize(f, y0, method='Nelder-Mead',
                     options={'xatol': 1e-10, 'fatol': 1e-12, 'maxiter': 4000 * k})
        if best is None or r.fun < best.fun:
            best = r
    return list(map(float, best.x)), float(-best.fun)


def polish_joint(y, s, k, iters=400):
    def terms(z):
        return joint_margin(z, s, k, True)
    y0 = np.concatenate([y, [joint_margin(y, s, k)]])
    cons = {'type': 'ineq', 'fun': lambda z: np.asarray(terms(z[:-1])) - z[-1]}
    try:
        r = minimize(lambda z: -z[-1], y0, method='SLSQP', constraints=[cons],
                     options={'maxiter': iters, 'ftol': 1e-12})
        if joint_margin(r.x[:-1], s, k) > joint_margin(y, s, k):
            return list(map(float, r.x[:-1]))
    except Exception:
        pass
    return list(y)


def run_fit(s, k, rings, restarts, seed):
    rng = np.random.default_rng(seed + k)
    best = None
    for r0 in rings:
        if os.path.exists(STOP):
            break
        yf, gap = fit_k(r0['x'], s, k, restarts, rng)
        y = list(r0['x']) + list(yf)
        y = polish_joint(y, s, k)
        m = joint_margin(y, s, k)
        # a Nelder-Mead pass on the JOINT vector from that start
        rr = minimize(lambda z: -joint_margin(z, s, k), y, method='Nelder-Mead',
                      options={'xatol': 1e-9, 'fatol': 1e-11, 'maxiter': 4000 + 2000 * k,
                               'adaptive': True})
        y2 = polish_joint(list(map(float, rr.x)), s, k)
        if joint_margin(y2, s, k) > m:
            y, m = y2, joint_margin(y2, s, k)
        if best is None or m > best[0]:
            best = (m, y, float(gap))
    return {'sup_margin': best[0], 'y': best[1], 'ring_fixed_gap': best[2]} if best else None


def run_far(s, rings, restarts, seed):
    """max |q - O| over feasible (ring, one free square): the CENTRE-DISC radius at side s."""
    rng = np.random.default_rng(seed)
    O = np.array([s / 2.0, s / 2.0])
    best = None
    for r0 in rings:
        if os.path.exists(STOP):
            break
        yf, gap = fit_k(r0['x'], s, 1, max(8, restarts // 4), rng)
        y = list(r0['x']) + list(yf)
        for pen in (1e2, 1e3, 1e4):
            rr = minimize(lambda z: -(np.linalg.norm(np.array(z[16:18]) - O)
                                      + pen * min(0.0, joint_margin(z, s, 1))),
                          y, method='Nelder-Mead',
                          options={'xatol': 1e-9, 'fatol': 1e-11, 'maxiter': 12000, 'adaptive': True})
            z = polish_joint(list(map(float, rr.x)), s, 1)
            for cand in (list(map(float, rr.x)), z):
                if joint_margin(cand, s, 1) >= -1e-9:
                    d = float(np.linalg.norm(np.array(cand[16:18]) - O))
                    if best is None or d > best[0]:
                        best = (d, cand, float(joint_margin(cand, s, 1)))
    return {'max_dist': best[0], 'y': best[1], 'margin': best[2]} if best else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', default='fit')
    ap.add_argument('--sides', default='3.85,3.877084,3.90,3.95,3.99')
    ap.add_argument('--ks', default='1,2,3')
    ap.add_argument('--rings', type=int, default=6)
    ap.add_argument('--restarts', type=int, default=40)
    ap.add_argument('--seed', type=int, default=251)
    a = ap.parse_args()
    try:
        import cert251
        cert251.belownormal()
    except Exception:
        pass
    out = json.load(open(RES, encoding='utf-8')) if os.path.exists(RES) else {}
    for s in [float(v) for v in a.sides.split(',')]:
        if os.path.exists(STOP):
            print('STOP present')
            break
        key = '%.6f' % s
        out.setdefault(key, {})
        if 'rings' not in out[key]:
            t0 = time.time()
            rs = F.sample_rings(s, a.restarts, sym_seed=SEED_X)
            out[key]['rings'] = {'n': len(rs), 'best_margin': rs[0]['margin'] if rs else None,
                                 'x': [r['x'] for r in rs[:a.rings]], 'seconds': time.time() - t0}
            json.dump(out, open(RES, 'w', encoding='utf-8'), indent=1)
            print('s %.6f: %d feasible rings, best margin %s (%.0f s)'
                  % (s, len(rs), rs[0]['margin'] if rs else None, time.time() - t0), flush=True)
        rings = [{'x': x} for x in out[key]['rings']['x']]
        if not rings:
            continue
        if a.mode == 'far':
            if 'far' not in out[key]:
                t0 = time.time()
                out[key]['far'] = run_far(s, rings, a.restarts, a.seed)
                out[key]['far']['seconds'] = time.time() - t0
                print('s %.6f far: max |q - O| = %.4f (1/sqrt3 = %.4f)'
                      % (s, out[key]['far']['max_dist'], 1 / math.sqrt(3)), flush=True)
                json.dump(out, open(RES, 'w', encoding='utf-8'), indent=1)
            continue
        for k in [int(v) for v in a.ks.split(',')]:
            if os.path.exists(STOP):
                break
            kk = 'fit%d' % k
            if kk in out[key]:
                continue
            t0 = time.time()
            r = run_fit(s, k, rings, a.restarts, a.seed)
            if r is None:
                continue
            r['seconds'] = time.time() - t0
            out[key][kk] = r
            print('s %.6f k = %d: sup joint margin %+.5f (ring-fixed best gap %+.5f) [%.0f s]'
                  % (s, k, r['sup_margin'], r['ring_fixed_gap'], r['seconds']), flush=True)
            json.dump(out, open(RES, 'w', encoding='utf-8'), indent=1)
    json.dump(out, open(RES, 'w', encoding='utf-8'), indent=1)


if __name__ == '__main__':
    main()
