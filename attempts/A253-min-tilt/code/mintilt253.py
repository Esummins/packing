"""A253 task 1: THETA_MIN(s) -- the smallest tilt of the all-ADJ ring that still admits the POKER.

(i) COMMON tilt: every member has tau_i = tau; the ring is then (sigma, deltas) with sigma in
    {0,1}^8 saying, per member, whether theta = tau or 90 deg - tau (`geom253.x_of`).  For a fixed
    (tau, sigma) the sup over the eight deltas and the poker pose of  min(feas, poke_margin)  is a
    continuous M(tau, sigma, s); theta_min^(i)(s) = inf{tau : max_sigma M > 0}, bracketed by
    bisection (the upper end is CERTIFIED EXACTLY by cert253, the lower end is measured: the search
    found nothing).
(ii) non-uniform: minimise max_i tau_i over feasible ring + poker -- A252's protected form,
    J = max_i tau_i + pen * max(0, need - min(feas, poke)) over 19 coordinates (8 tau, 8 delta,
    3 poker), many restarts.  theta_min^(ii) <= theta_min^(i) by construction.

    python mintilt253.py --mode screen|curve|bisect|minimax [--sides ...] [--starts N]
Rows append to results/mintilt253_<mode>.jsonl (resumable, logs/STOP honoured).
"""
import argparse
import itertools
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
import poker252 as PK                                                 # noqa: E402

STOP = os.path.join(ATT, 'logs', 'STOP')
RES = os.path.join(ATT, 'results')
DEG = Z.DEG
SIDES = (3.82, 3.85, Z.SW, 3.92, 3.95, 3.99)
WALLS = (0, 1, 2, 3)


def stop():
    return os.path.exists(STOP)


def rows(fn):
    p = os.path.join(RES, fn)
    return [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()] if os.path.exists(p) else []


def emit(fn, row):
    with open(os.path.join(RES, fn), 'a', encoding='utf-8') as f:
        f.write(json.dumps(row) + '\n')


def ring_only(tau, sigma, s, d0=None, maxiter=2500, tries=2, seed=0):
    """sup over the eight deltas of feas at a fixed common tilt."""
    rng = np.random.default_rng(seed)
    best = (-9.0, [0.8] * 8)
    xs = Z.shat_ring()
    starts = ([list(d0)] if d0 is not None else []) + \
        [[xs[1], xs[3], xs[5], xs[7], xs[9], xs[11], xs[13], xs[15]]]
    for t in range(len(starts) + tries):
        d = starts[t] if t < len(starts) else list(rng.uniform(0.55, 0.99, 8))
        r = minimize(lambda z: -Z.feas(Z.x_of(tau, sigma, z), s), d, method='Nelder-Mead',
                     options={'xatol': 1e-10, 'fatol': 1e-12, 'maxiter': maxiter, 'adaptive': True})
        if -r.fun > best[0]:
            best = (float(-r.fun), [float(v) for v in r.x])
    return best


def joint_best(tau, sigma, s, d0=None, walls=WALLS, maxiter=1000, tries=1, seed=0, pk_restarts=3,
               pk_maxiter=1200):
    """sup over deltas + poker pose of min(feas, poke_margin), over the walls."""
    fv, d = ring_only(tau, sigma, s, d0, maxiter=maxiter, tries=tries, seed=seed)
    if fv <= 0:
        return {'M': fv, 'stage': 'ring', 'deltas': d, 'wall': None, 'pose': None, 'feas': fv}
    x = Z.x_of(tau, sigma, d)
    P = Z.polys(x, s)
    out = {'M': -9.0, 'stage': 'joint', 'deltas': d, 'pose': None, 'wall': None, 'feas': fv}
    for w in walls:
        pm, pose, _ = Z.find_poker(P, s, restarts=pk_restarts, seed=7 + w, walls=(w,),
                                   maxiter=pk_maxiter)
        z0 = list(d) + list(pose)
        r = minimize(lambda z: -Z.joint(Z.x_of(tau, sigma, z[:8]), z[8:11], s, w), z0,
                     method='Nelder-Mead',
                     options={'xatol': 1e-9, 'fatol': 1e-11, 'maxiter': maxiter, 'adaptive': True})
        M = float(-r.fun)
        if M > out['M']:
            zz = [float(v) for v in r.x]
            out = {'M': M, 'stage': 'joint', 'deltas': zz[:8], 'pose': zz[8:11], 'wall': w,
                   'feas': Z.feas(Z.x_of(tau, sigma, zz[:8]), s)}
    return out


def sigmas():
    return [''.join(map(str, t)) for t in itertools.product((0, 1), repeat=8)]


def mode_screen(a):
    """which sign patterns carry a ring at a reference tilt (ring only)."""
    done = {(r['side'], r['tau_deg'], r['sigma']) for r in rows('mintilt253_screen.jsonl')}
    for s in a.sides:
        for tau_deg in a.taus:
            for sg in sigmas():
                if stop():
                    return print('STOP present', flush=True)
                if ('%.6f' % s, tau_deg, sg) in done:
                    continue
                sig = [int(c) for c in sg]
                fv, d = ring_only(tau_deg * DEG, sig, s, maxiter=a.maxiter, tries=1)
                emit('mintilt253_screen.jsonl', {'side': '%.6f' % s, 'tau_deg': tau_deg,
                                                 'sigma': sg, 'feas': fv, 'deltas': d})
            print('screen s=%.6f tau=%.2f done' % (s, tau_deg), flush=True)


PINWHEEL = '00110011'
FORCE = []


def best_sigmas(s, tau_deg, top=6):
    if FORCE:
        x = Z.shat_ring()
        d = [x[1], x[3], x[5], x[7], x[9], x[11], x[13], x[15]]
        return [(sg, d) for sg in FORCE]
    R = [r for r in rows('mintilt253_screen.jsonl')
         if r['side'] == '%.6f' % s and abs(r['tau_deg'] - tau_deg) < 1e-9 and r['feas'] > 0]
    R.sort(key=lambda r: -r['feas'])
    return [(r['sigma'], r['deltas']) for r in R[:top]]


def mode_curve(a):
    """M(tau) on a grid for the leading sign patterns: the shape of the ring / poker margins."""
    done = {(r['side'], r['sigma'], round(r['tau_deg'], 6)) for r in rows('mintilt253_curve.jsonl')}
    for s in a.sides:
        cand = best_sigmas(s, a.ref_deg, a.top)
        if not cand:
            print('no screened sigma at s=%.6f' % s, flush=True)
            continue
        for sg, d0 in cand:
            sig = [int(c) for c in sg]
            d = list(d0)
            for tau_deg in a.taus:
                if stop():
                    return print('STOP present', flush=True)
                if ('%.6f' % s, sg, round(tau_deg, 6)) in done:
                    continue
                t0 = time.time()
                r = joint_best(tau_deg * DEG, sig, s, d0=d, maxiter=a.maxiter, tries=a.tries)
                if r['deltas']:
                    d = r['deltas']
                row = {'side': '%.6f' % s, 'sigma': sg, 'tau_deg': tau_deg, 'M': r['M'],
                       'feas': r['feas'], 'stage': r['stage'], 'wall': r['wall'],
                       'deltas': r['deltas'], 'pose': r['pose'], 'seconds': time.time() - t0}
                if r['pose'] is not None:
                    x = Z.x_of(tau_deg * DEG, sig, r['deltas'])
                    row['binding'] = Z.feas_named(x, s, 3) + Z.poke_gaps(r['pose'], x, s, r['wall'])[:3]
                emit('mintilt253_curve.jsonl', row)
                print('curve s=%.6f %s tau %5.2f  M %+.5f feas %+.5f (%.0fs)'
                      % (s, sg, tau_deg, r['M'], r['feas'], row['seconds']), flush=True)


def bisect(s, sg, lo, hi, d0, iters=16, maxiter=3000, tries=2, kind='joint'):
    """bracket the least tau with a positive margin; hi must be feasible."""
    sig = [int(c) for c in sg]
    best, hist, d = None, [], list(d0)
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if kind == 'joint':
            r = joint_best(mid * DEG, sig, s, d0=d, maxiter=maxiter, tries=tries)
        else:
            fv, dd = ring_only(mid * DEG, sig, s, d, maxiter=maxiter, tries=tries)
            r = {'M': fv, 'feas': fv, 'deltas': dd, 'pose': None, 'wall': None, 'stage': 'ring'}
        hist.append((mid, r['M']))
        if r['M'] > 0:
            hi, best = mid, dict(r, tau_deg=mid)
            d = r['deltas']
        else:
            lo = mid
        if stop():
            break
    return lo, hi, best, hist


def mode_bisect(a):
    done = {(r['side'], r['sigma'], r['kind']) for r in rows('mintilt253_bisect.jsonl')}
    for s in a.sides:
        for sg, d0 in best_sigmas(s, a.ref_deg, a.top):
            for kind in ('ring', 'joint'):
                if stop():
                    return print('STOP present', flush=True)
                if ('%.6f' % s, sg, kind) in done:
                    continue
                t0 = time.time()
                lo, hi, best, hist = bisect(s, sg, a.lo, a.hi, d0, iters=a.iters,
                                            maxiter=a.maxiter, tries=a.tries, kind=kind)
                row = {'side': '%.6f' % s, 'sigma': sg, 'kind': kind, 'lo_deg': lo, 'hi_deg': hi,
                       'best': best, 'history': hist, 'seconds': time.time() - t0}
                if best is not None and best.get('pose'):
                    x = Z.x_of(best['tau_deg'] * DEG, [int(c) for c in sg], best['deltas'])
                    row['binding_at_hi'] = Z.feas_named(x, s, 3) + \
                        Z.poke_gaps(best['pose'], x, s, best['wall'])[:3]
                lowr = joint_best(lo * DEG, [int(c) for c in sg], s, d0=d0, maxiter=a.maxiter, tries=3)
                xl = Z.x_of(lo * DEG, [int(c) for c in sg], lowr['deltas'])
                row['blocker_at_lo'] = {
                    'M': lowr['M'], 'feas': lowr['feas'], 'stage': lowr['stage'], 'wall': lowr['wall'],
                    'deltas': lowr['deltas'], 'pose': lowr['pose'],
                    'binding': Z.feas_named(xl, s, 4) + (
                        Z.poke_gaps(lowr['pose'], xl, s, lowr['wall'])[:3] if lowr['pose'] else [])}
                emit('mintilt253_bisect.jsonl', row)
                print('bisect s=%.6f %s %s -> [%.4f, %.4f] deg (%.0fs)'
                      % (s, sg, kind, lo, hi, row['seconds']), flush=True)


def minimax_obj(z, s, sig, wall, need, pen):
    us = [abs(v) for v in z[:8]]
    x = Z.x_free(us, sig, z[8:16])
    m = Z.joint(x, z[16:19], s, wall)
    return max(us) / DEG + pen * max(0.0, need - m)


def mode_minimax(a):
    """(ii) minimise the MAXIMUM tilt over the eight (non-uniform), A252's protected form."""
    done = {(r['side'], r['start']) for r in rows('mintilt253_minimax.jsonl')}
    base = rows('mintilt253_bisect.jsonl')
    for s in a.sides:
        for si, (sg, d0) in enumerate(best_sigmas(s, a.ref_deg, a.top)):
            name = '%s_%d' % (sg, si)
            if stop():
                return print('STOP present', flush=True)
            if ('%.6f' % s, name) in done:
                continue
            sig = [int(c) for c in sg]
            bs = [r['best'] for r in base if r['side'] == '%.6f' % s and r['sigma'] == sg
                  and r['kind'] == 'joint' and r['best']]
            if not bs:
                continue
            b, t0, best = bs[0], time.time(), None
            for k in range(a.starts):
                rng = np.random.default_rng(1000 + k)
                tau0 = b['tau_deg'] * DEG
                z0 = [tau0] * 8 + list(b['deltas']) + list(b['pose'])
                if k:
                    z0[:8] = [max(1e-3, tau0 * (1 + 0.12 * v)) for v in rng.normal(size=8)]
                r = minimize(minimax_obj, z0, args=(s, sig, b['wall'], a.need, a.pen),
                             method='Nelder-Mead',
                             options={'xatol': 1e-9, 'fatol': 1e-11, 'maxiter': a.maxiter,
                                      'adaptive': True})
                z = [float(v) for v in r.x]
                us = [abs(v) for v in z[:8]]
                m = Z.joint(Z.x_free(us, sig, z[8:16]), z[16:19], s, b['wall'])
                if m > 0 and (best is None or max(us) < best['maxtilt']):
                    best = {'maxtilt': max(us), 'maxtilt_deg': max(us) / DEG, 'margin': m,
                            'tilts_deg': [u / DEG for u in us], 'z': z, 'wall': b['wall']}
            row = {'side': '%.6f' % s, 'start': name, 'sigma': sg, 'best': best,
                   'starts': a.starts, 'need': a.need, 'seconds': time.time() - t0}
            emit('mintilt253_minimax.jsonl', row)
            print('minimax s=%.6f %s -> %s deg (%.0fs)' % (
                s, name, None if best is None else round(best['maxtilt_deg'], 4),
                row['seconds']), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', default='screen')
    ap.add_argument('--sides', default=','.join('%.6f' % v for v in SIDES))
    ap.add_argument('--taus', default='14.545')
    ap.add_argument('--ref-deg', type=float, default=14.545, dest='ref_deg')
    ap.add_argument('--top', type=int, default=4)
    ap.add_argument('--tries', type=int, default=2)
    ap.add_argument('--starts', type=int, default=8)
    ap.add_argument('--iters', type=int, default=16)
    ap.add_argument('--lo', type=float, default=0.05)
    ap.add_argument('--hi', type=float, default=30.0)
    ap.add_argument('--need', type=float, default=0.0015)
    ap.add_argument('--pen', type=float, default=400.0)
    ap.add_argument('--maxiter', type=int, default=3000)
    ap.add_argument('--force-sigmas', default='', dest='force_sigmas')
    a = ap.parse_args()
    a.sides = [float(v) for v in a.sides.split(',')]
    a.taus = [float(v) for v in a.taus.split(',')]
    if a.force_sigmas:
        FORCE.extend(a.force_sigmas.split(','))
    Z.belownormal()
    {'screen': mode_screen, 'curve': mode_curve, 'bisect': mode_bisect,
     'minimax': mode_minimax}[a.mode](a)
    print('%s DONE' % a.mode.upper(), flush=True)


if __name__ == '__main__':
    main()
