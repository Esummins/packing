"""A281: witnesses for the wall pair types and the f-classes.  Roles per corner: 'T' (both meeters tilted), 'Ff' (flat
on the corner's OUTGOING wall = its frame floor; poker on the incoming wall), 'Fw' (flat on the incoming wall; poker
on the outgoing).  Nelder-Mead sup-margin over the frame parameters, then EXACT rational verification.
    python wall281.py pairs|rings|all [--sides 3.82,3.877083590022814] [--restarts 6]
Results: ../results/wall281_pairs.json, ../results/wall281_rings.json."""
import argparse
import itertools
import json
import math
import os
import sys
import time
from fractions import Fraction

import numpy as np
from scipy.optimize import minimize

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom281 as G  # noqa: E402

RES = os.path.join(HERE, '..', 'results')
DEG = math.pi / 180
TMIN, TMAX = 0.3 * DEG, 89.7 * DEG


def unpack(x, roles, active):
    """x -> per active corner (thA, dA, thB, dB); flats have th = 0 and consume no tilt variable."""
    out, k = {}, 0
    for c in active:
        r = roles[c]
        if r == 'T':
            thA, dA, thB, dB = x[k:k + 4]
            k += 4
        elif r == 'Ff':                      # A flat
            dA, thB, dB = x[k:k + 3]
            thA = 0.0
            k += 3
        else:                                # 'Fw': B flat
            thA, dA, dB = x[k:k + 3]
            thB = 0.0
            k += 3
        out[c] = (thA, dA, thB, dB)
    return out


def nvars(roles, active):
    return sum(4 if roles[c] == 'T' else 3 for c in active)


def squares(params, s, exact=False, sf=None):
    sq = {}
    for c, (thA, dA, thB, dB) in params.items():
        if exact:
            sq[(c, 'A')] = G.exact_square('A', thA, dA, c, sf)
            sq[(c, 'B')] = G.exact_square('B', thB, dB, c, sf)
        else:
            sq[(c, 'A')] = G.float_square('A', thA, dA, c, s)
            sq[(c, 'B')] = G.float_square('B', thB, dB, c, s)
    return sq


def margin(x, roles, active, s, extra, want_terms=False):
    p = unpack(x, roles, active)
    terms = []
    for c, (thA, dA, thB, dB) in p.items():
        for th, r_is_tilted in ((thA, roles[c] != 'Ff'), (thB, roles[c] != 'Fw')):
            if r_is_tilted:
                terms.append(min(th - TMIN, TMAX - th))
        terms += [dA, 1 - dA, dB, 1 - dB]
        if roles[c] == 'Ff':                 # poker beside the floor flat: sin thB <= dA (TILT-MIN)
            terms.append(dA - math.sin(thB))
        if roles[c] == 'Fw':                 # poker beside the wall flat: cos thA <= dB (TILT-MIN mirrored)
            terms.append(dB - math.cos(thA))
    sq = squares(p, s)
    keys = list(sq)
    for i in range(len(keys)):
        P = sq[keys[i]]
        c, kind = keys[i]
        Pf = G.frame_square(kind, p[c][0] if kind == 'A' else p[c][2], p[c][1] if kind == 'A' else p[c][3])
        terms.append(min(s - max(q[0] for q in Pf), s - max(q[1] for q in Pf)))   # container (touched wall excluded)
        terms.append(-G.gap(P, G.cells(s, keys[i][0])['c00']))          # meets its own box
        for j in range(i):
            terms.append(G.gap(P, sq[keys[j]]))
    for e in extra:
        if e[0] == 'tilt':                                             # ('tilt', c, kind, lo, hi): a tilt window
            th = p[e[1]][0 if e[2] == 'A' else 2]
            terms.append(min(th - e[3], e[4] - th))
        else:                                                          # (c, kind, c2, cell): must meet that cell
            terms.append(-G.gap(sq[(e[0], e[1])], G.cells(s, e[2])[e[3]]))
    m = min(terms)
    return (m, terms) if want_terms else m


def random_start(roles, active, rng):
    x = []
    for c in active:
        r = roles[c]
        th = lambda: rng.uniform(5, 80) * DEG  # noqa: E731
        if r == 'T':
            if rng.uniform() < 0.6:          # structured: one shallow near-flush meeter, one steep partner (A249)
                sh, st = rng.uniform(5, 25) * DEG, rng.uniform(55, 85) * DEG
                a, b = (sh, st) if rng.uniform() < 0.5 else (st, sh)
                x += [a, rng.uniform(0.5, 0.95), b, rng.uniform(0.5, 0.95)]
            else:
                x += [th(), rng.uniform(0.2, 0.95), th(), rng.uniform(0.2, 0.95)]
        elif r == 'Ff':
            x += [rng.uniform(0.3, 0.95), rng.uniform(5, 40) * DEG, rng.uniform(0.3, 0.95)]
        else:
            x += [rng.uniform(50, 85) * DEG, rng.uniform(0.3, 0.95), rng.uniform(0.3, 0.95)]
    return np.array(x)


def optimise(roles, active, s, extra=(), restarts=6, seed=0, maxiter=2500):
    rng = np.random.default_rng(seed)
    best = (-9, None)
    f = lambda x: -margin(x, roles, active, s, extra)  # noqa: E731
    for r in range(restarts):
        x0 = random_start(roles, active, rng)
        res = minimize(f, x0, method='Nelder-Mead', options={'maxiter': maxiter, 'xatol': 1e-9, 'fatol': 1e-10})
        res = minimize(f, res.x, method='Nelder-Mead', options={'maxiter': maxiter, 'xatol': 1e-10, 'fatol': 1e-12})
        x, m = res.x, -res.fun
        try:                                  # SLSQP polish of the slack form: max t s.t. every term >= t
            n = len(x)
            cons = {'type': 'ineq', 'fun': lambda z: np.array(margin(z[:n], roles, active, s, extra, True)[1]) - z[n]}
            r2 = minimize(lambda z: -z[n], np.append(x, m), method='SLSQP', constraints=[cons],
                          options={'maxiter': 200, 'ftol': 1e-12})
            m2 = margin(r2.x[:n], roles, active, s, extra)
            if m2 > m:
                x, m = r2.x[:n], m2
        except Exception:
            pass
        if m > best[0]:
            best = (m, x)
    return best


def exact_verify(x, roles, active, s, extra):
    """rationalise and check EVERY constraint exactly; returns (ok, details)."""
    sf = G.rational(s)
    p = unpack(x, roles, active)
    sq = squares(p, s, exact=True, sf=sf)
    det = {'container': True, 'disjoint': True, 'boxes': True, 'extra': True, 'flats_ok': True}
    for k, P in sq.items():
        if not G.in_container(P, sf):
            det['container'] = False
        if not G.meets(P, G.cells(sf, k[0])['c00']):
            det['boxes'] = False
    keys = list(sq)
    for i in range(len(keys)):
        for j in range(i):
            if G.gap(sq[keys[i]], sq[keys[j]]) < 0:
                det['disjoint'] = False
    for e in extra:
        if e[0] == 'tilt':
            th = p[e[1]][0 if e[2] == 'A' else 2]
            det['extra'] = bool(det['extra'] and (e[3] <= th <= e[4]))
        elif not G.meets(sq[(e[0], e[1])], G.cells(sf, e[2])[e[3]]):
            det['extra'] = False
    return all(det.values()), det


PAIR_ROLES = {   # wall 3 (x = 0) is BL's INCOMING and TL's OUTGOING wall: BL 'Fw' -> Phi, 'Ff' -> Pi; TL 'Ff' -> Phi, 'Fw' -> Pi.
    'PhiPhi': {0: 'Fw', 3: 'Ff'}, 'PhiPi': {0: 'Fw', 3: 'Fw'}, 'PiPi': {0: 'Ff', 3: 'Fw'},
    'Phi-tau': {0: 'Fw', 3: 'T'}, 'Pi-tau': {0: 'Ff', 3: 'T'}, 'tau-tau': {0: 'T', 3: 'T'},
}
PAIR_EXTRA = {   # ADJ-supply variants: TL's wall-3 meeter (its A, on its outgoing wall) meets BL's slot on wall 3 (BL c01)
    'Pi-tau+ADJ': ('Pi-tau', [(3, 'A', 0, 'c01')]),
    'Pi-tau+ADJ<45': ('Pi-tau', [(3, 'A', 0, 'c01'), ('tilt', 3, 'A', TMIN, 44.5 * DEG)]),
    'Pi-tau+ADJ>45': ('Pi-tau', [(3, 'A', 0, 'c01'), ('tilt', 3, 'A', 45.5 * DEG, TMAX)]),
    'Pi-tau+ROW': ('Pi-tau', [(3, 'A', 0, 'c01'), ('tilt', 3, 'A', TMIN, 44.5 * DEG), (3, 'A', 3, 'c10')]),
    'Phi-tau+ADJ': ('Phi-tau', [(3, 'A', 0, 'c01'), (0, 'B', 3, 'c10')]),
    'PhiPi+ADJ?': ('PhiPi', [(0, 'B', 3, 'c10')]),          # the flat supplying the poker's slot: must FAIL (FLAT-ABOVE)
    'tau-tau+ADJ': ('tau-tau', [(3, 'A', 0, 'c01'), (0, 'B', 3, 'c10')]),
}


def run_pairs(sides, restarts):
    out = {}
    for name, roles in PAIR_ROLES.items():
        for s in sides:
            t0 = time.time()
            m, x = optimise(roles, [0, 3], s, restarts=restarts)
            ok, det = exact_verify(x, roles, [0, 3], s, []) if m > 0 else (False, {})
            out['%s@%.6f' % (name, s)] = {'sup_margin': m, 'x': list(map(float, x)), 'roles': roles, 'exact_ok': ok,
                                          'exact': det, 'secs': time.time() - t0}
            print(name, '%.6f' % s, 'margin %.5f' % m, 'exact', ok, flush=True)
    for name, (base, extra) in PAIR_EXTRA.items():
        roles = PAIR_ROLES[base]
        for s in sides:
            m, x = optimise(roles, [0, 3], s, extra=extra, restarts=restarts)
            ok, det = exact_verify(x, roles, [0, 3], s, extra) if m > 0 else (False, {})
            p = unpack(x, roles, [0, 3])
            out['%s@%.6f' % (name, s)] = {'sup_margin': m, 'x': list(map(float, x)), 'roles': roles, 'extra': extra,
                                          'exact_ok': ok, 'exact': det, 'thA_TL_deg': p[3][0] / DEG}
            print(name, '%.6f' % s, 'margin %.5f' % m, 'exact', ok, 'thA(TL)=%.2f' % (p[3][0] / DEG), flush=True)
    json.dump(out, open(os.path.join(RES, 'wall281_pairs.json'), 'w'), indent=1)


def wall_types(roles):
    """wall w joins corner w (outgoing) and corner w+1 (incoming).  role on outgoing: Ff->Phi, Fw->Pi, T->tau;
    role on incoming: Ff->Pi, Fw->Phi, T->tau."""
    out_role = {'Ff': 'Phi', 'Fw': 'Pi', 'T': 'tau'}
    in_role = {'Ff': 'Pi', 'Fw': 'Phi', 'T': 'tau'}
    return [tuple(sorted((out_role[roles[w]], in_role[roles[(w + 1) % 4]]))) for w in range(4)]


def canonical(roles):
    """orbit representative under rotation and reflection (reflection reverses the cycle and swaps Ff <-> Fw)."""
    swap = {'Ff': 'Fw', 'Fw': 'Ff', 'T': 'T'}
    cands = []
    for k in range(4):
        r = roles[k:] + roles[:k]
        cands.append(tuple(r))
        rr = tuple(swap[t] for t in reversed(r))
        cands.append(rr)
    return min(cands)


def run_rings(sides, restarts):
    classes = sorted({canonical(list(r)) for r in itertools.product(['T', 'Ff', 'Fw'], repeat=4)})
    out = {}
    for roles in classes:
        wt = wall_types(list(roles))
        dead = ('Pi', 'Pi') in wt
        f = sum(r != 'T' for r in roles)
        rec = {'roles': roles, 'walls': wt, 'f': f, 'side_dead_PiPi': dead, 'runs': {}}
        for s in sides:
            t0 = time.time()
            m, x = optimise({c: roles[c] for c in range(4)}, [0, 1, 2, 3], s, restarts=restarts)
            ok, det = exact_verify(x, {c: roles[c] for c in range(4)}, [0, 1, 2, 3], s, []) if m > 0 else (False, {})
            rec['runs']['%.6f' % s] = {'sup_margin': m, 'x': list(map(float, x)), 'exact_ok': ok, 'exact': det,
                                      'secs': time.time() - t0}
            print(roles, wt, 'f=%d' % f, '%.6f' % s, 'margin %.5f' % m, 'exact', ok, '%.0fs' % (time.time() - t0), flush=True)
        out['/'.join(roles)] = rec
        json.dump(out, open(os.path.join(RES, 'wall281_rings.json'), 'w'), indent=1)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=['pairs', 'rings', 'all'])
    ap.add_argument('--sides', default='3.82,%r' % G.SHAT)
    ap.add_argument('--restarts', type=int, default=10)
    a = ap.parse_args()
    os.makedirs(RES, exist_ok=True)
    sides = [float(v) for v in a.sides.split(',')]
    if a.mode in ('pairs', 'all'):
        run_pairs(sides, a.restarts)
    if a.mode in ('rings', 'all'):
        run_rings(sides, a.restarts)
