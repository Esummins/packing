"""A253 task 2: the ROOM in the pocket of a given ring (+ poker), exactly as the lab measures it.

Three independent readings of the capacity of P = [0, s]^2 minus the eight ring squares:

  FIT(k)     A222's region search (`region222.cspace` / `greedy`: per tilt the exact configuration
             space of one more square, the pole of inaccessibility, a beam over tilts) followed by
             a sup-margin polish on the 3k free coordinates and the lab's SAT check
             (`geom248.poly_gap` >= 0 and containment) -- a LOWER bound on the capacity.
  PIERCE(k)  A237's box-valid piercing certificate (`geom237.pierce`: over 1-degree tilt bins,
             P (-) K_bin covered by k translates of K_bin) -- residual 0 proves capacity <= k.
             The k points are optimised (Nelder-Mead on the 2k coordinates, seeded by the FIT
             centres and the poles).
  ANCHORED   A252's poker-anchored residual: with the poker pinned, the centre set of the residual
             pocket, its diameter (< 1 => capacity <= 1 beside the poker, so <= 2 in all).

    python room253.py --mode rings|tiltsweep [--src ...]
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
import geom253 as Z                                                   # noqa: E402
import geom237 as G237                                                # noqa: E402
import region222 as RG                                                # noqa: E402
import disc252 as D                                                   # noqa: E402
import geom248 as G                                                   # noqa: E402

STOP = os.path.join(ATT, 'logs', 'STOP')
RES = os.path.join(ATT, 'results')
TOL = 1e-9


def poses_of(x, s):
    return [tuple(map(float, G.pose_of(V))) for V in Z.polys(x, s)]


def fit_margin(free, fixed, s):
    """the lab's sup-margin of k free squares in the pocket: min SAT gap and containment."""
    Vs = [G.verts(p) for p in free]
    Fs = [G.verts(p) for p in fixed]
    m = 9.0
    for V in Vs:
        m = min(m, V[:, 0].min(), V[:, 1].min(), s - V[:, 0].max(), s - V[:, 1].max())
    for i, V in enumerate(Vs):
        for F in Fs:
            m = min(m, G.poly_gap(V, F))
        for j in range(i):
            m = min(m, G.poly_gap(V, Vs[j]))
    return float(m)


def fit(fixed, s, k, restarts=8, seed=0, maxiter=4000):
    """A222 region search + sup-margin polish; returns (margin, poses)."""
    if k == 0:
        return 0.0, []
    rng = np.random.default_rng(seed)
    seeds = []
    got = RG.greedy(list(fixed), s, k, [math.radians(t) for t in range(0, 90, 5)], beam=3)
    if got is not None:
        seeds.append(list(got))
    got = RG.greedy(list(fixed), s, k, [math.radians(t) for t in np.arange(0, 90, 2.0)], beam=2)
    if got is not None:
        seeds.append(list(got))
    for _ in range(restarts):
        seeds.append([(rng.uniform(0.5, s - 0.5), rng.uniform(0.5, s - 0.5),
                       rng.uniform(0, math.pi / 2)) for _ in range(k)])
    best = (-9.0, None)
    for z0 in seeds:
        flat = [v for p in z0 for v in p]
        r = minimize(lambda z: -fit_margin([z[3 * i:3 * i + 3] for i in range(k)], fixed, s), flat,
                     method='Nelder-Mead',
                     options={'xatol': 1e-10, 'fatol': 1e-12, 'maxiter': maxiter, 'adaptive': True})
        if -r.fun > best[0]:
            best = (float(-r.fun), [tuple(float(v) for v in r.x[3 * i:3 * i + 3]) for i in range(k)])
        if best[0] > 1e-6:
            break
    return best


def pierce_opt(members, s, k, step_deg=1.0, seeds=(), restarts=4, seed=0, maxiter=1500):
    """minimise A237's piercing residual over k points; residual ~ 0 certifies capacity <= k."""
    free = G237.coverable(members, s, step_deg)[1]
    P = G237.pocket(members, s)
    pts0 = []
    for sd in seeds:
        if len(sd) == k:
            pts0.append([(p[0], p[1]) for p in sd])
    rng = np.random.default_rng(seed)
    b = P.bounds
    for _ in range(restarts):
        pts0.append([(rng.uniform(b[0], b[2]), rng.uniform(b[1], b[3])) for _ in range(k)])
    best = (9.0, None)
    for p0 in pts0:
        flat = [v for p in p0 for v in p]
        r = minimize(lambda z: G237.pierce(members, s, [(z[2 * i], z[2 * i + 1]) for i in range(k)],
                                           step_deg, free), flat, method='Nelder-Mead',
                     options={'xatol': 1e-8, 'fatol': 1e-12, 'maxiter': maxiter, 'adaptive': True})
        if r.fun < best[0]:
            best = (float(r.fun), [(float(r.x[2 * i]), float(r.x[2 * i + 1])) for i in range(k)])
        if best[0] <= 1e-12:
            break
    return best


def room(x, s, pose=None, wall=None, kmax=3, step_deg=1.0, restarts=6, pierce_restarts=3):
    """every reading of the room of the ring's pocket (and, if a poker is given, beside it)."""
    t0 = time.time()
    ring = poses_of(x, s)
    P = G237.pocket(ring, s)
    out = {'side': s, 'feas': Z.feas(x, s), 'tilts_deg': [t / Z.DEG for t in Z.tilts_of(x)],
           'pocket_area': float(P.area), 'fit': {}, 'pierce': {}}
    fits = {}
    for k in range(1, kmax + 1):
        m, ps = fit(ring, s, k, restarts=restarts, seed=k)
        fits[k] = ps
        out['fit'][k] = {'margin': m, 'fits': bool(m >= -TOL), 'poses': ps}
        if m < -TOL:
            break
    for k in range(1, kmax + 1):
        sd = [fits[k]] if k in fits and fits[k] else []
        res, pts = pierce_opt(ring, s, k, step_deg, seeds=sd, restarts=pierce_restarts, seed=k)
        out['pierce'][k] = {'residual': res, 'certifies': bool(res <= 1e-12), 'points': pts}
        if res <= 1e-12:
            break
    lo = max([k for k in out['fit'] if out['fit'][k]['fits']] or [0])
    hi = min([k for k in out['pierce'] if out['pierce'][k]['certifies']] or [kmax + 1])
    out['capacity_lo'], out['capacity_hi'] = lo, hi
    if pose is not None:
        out['poker'] = {'pose': list(pose), 'wall': wall,
                        'margin': Z.poke(pose, Z.polys(x, s), s, wall)}
        out['anchored'] = D.anchored(x, s, list(pose)) if hasattr(D, 'anchored') else None
        m2, ps2 = fit(ring + [tuple(pose)], s, 2, restarts=restarts, seed=11)
        m1, ps1 = fit(ring + [tuple(pose)], s, 1, restarts=restarts, seed=12)
        out['beside_poker'] = {'one': {'margin': m1, 'fits': bool(m1 >= -TOL), 'poses': ps1},
                               'two': {'margin': m2, 'fits': bool(m2 >= -TOL), 'poses': ps2}}
    out['seconds'] = time.time() - t0
    return out


def emit(fn, row):
    with open(os.path.join(RES, fn), 'a', encoding='utf-8') as f:
        f.write(json.dumps(row) + '\n')


def loaded(fn):
    p = os.path.join(RES, fn)
    return [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()] if os.path.exists(p) else []


def jobs_from_bisect():
    """the theta_min rings (task 1) plus the tilt ladder theta_min + 5, + 10 deg and A249's 14.6 deg."""
    out = []
    for r in loaded('mintilt253_bisect.jsonl'):
        if r['kind'] != 'joint' or not r.get('best'):
            continue
        b, s, sg = r['best'], float(r['side']), r['sigma']
        for tag, tau in (('theta_min', b['tau_deg']), ('plus5', b['tau_deg'] + 5.0),
                         ('plus10', b['tau_deg'] + 10.0), ('a249', 14.545)):
            out.append({'side': s, 'sigma': sg, 'tag': tag, 'tau_deg': tau,
                        'deltas': b['deltas'], 'pose': b['pose'], 'wall': b['wall']})
    return out


def jobs_from_sweep(sides, taus, sg):
    x = Z.shat_ring()
    d = [x[1], x[3], x[5], x[7], x[9], x[11], x[13], x[15]]
    return [{'side': s, 'sigma': sg, 'tag': 't%.3f' % t, 'tau_deg': t, 'deltas': d,
             'pose': None, 'wall': None} for s in sides for t in taus]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', default='rings')
    ap.add_argument('--kmax', type=int, default=3)
    ap.add_argument('--step-deg', type=float, default=1.0, dest='step_deg')
    ap.add_argument('--restarts', type=int, default=6)
    ap.add_argument('--sides', default='3.877084')
    ap.add_argument('--taus', default='14.545,6,2')
    ap.add_argument('--sigma', default='00110011')
    a = ap.parse_args()
    Z.belownormal()
    import mintilt253 as M
    done = {(r['side_key'], r['sigma'], r['tag']) for r in loaded('room253.jsonl')}
    jobs = jobs_from_bisect() if a.mode == 'rings' else jobs_from_sweep(
        [float(v) for v in a.sides.split(',')], [float(v) for v in a.taus.split(',')], a.sigma)
    carry = {}
    for j in jobs:
        if j['side'] in carry:
            j['deltas'] = carry[j['side']]
        key = ('%.6f' % j['side'], j['sigma'], j['tag'])
        if key in done or os.path.exists(STOP):
            if os.path.exists(STOP):
                return print('STOP present', flush=True)
            continue
        sig = [int(c) for c in j['sigma']]
        rr = M.joint_best(j['tau_deg'] * Z.DEG, sig, j['side'], d0=j['deltas'], maxiter=1000,
                          walls=(j['wall'],) if j['wall'] is not None else (0, 1, 2, 3))
        if rr['M'] <= 0:
            emit('room253.jsonl', {'side_key': key[0], 'sigma': j['sigma'], 'tag': j['tag'],
                                   'tau_deg': j['tau_deg'], 'infeasible': True, 'M': rr['M']})
            print('room %s %s infeasible (M %+.5f)' % (key[0], j['tag'], rr['M']), flush=True)
            continue
        carry[j['side']] = rr['deltas']
        x = Z.x_of(j['tau_deg'] * Z.DEG, sig, rr['deltas'])
        row = room(x, j['side'], rr['pose'], rr['wall'], kmax=a.kmax, step_deg=a.step_deg,
                   restarts=a.restarts)
        row.update({'side_key': key[0], 'sigma': j['sigma'], 'tag': j['tag'],
                    'tau_deg': j['tau_deg'], 'x': x, 'M': rr['M']})
        emit('room253.jsonl', row)
        print('room %s %-9s tau %6.3f  capacity in [%d, %d]  pocket %.4f  beside poker: 1 %s 2 %s (%.0fs)'
              % (key[0], j['tag'], j['tau_deg'], row['capacity_lo'], row['capacity_hi'],
                 row['pocket_area'], row['beside_poker']['one']['fits'],
                 row['beside_poker']['two']['fits'], row['seconds']), flush=True)
    print('ROOM DONE', flush=True)


if __name__ == '__main__':
    main()
