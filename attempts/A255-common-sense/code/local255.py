"""A255 task 3a: the LOCAL counter-hypothesis as a sup-margin search, per PAIR TYPE.

Corner frame of BL (the quadrant x, y >= 0; the far walls never bind: every square below lies in
[0, 3.42]^2, so the problem is s-FREE and the same for every m >= 4).  Squares:
    B, A  the two ROOT meeters (both meet c00 = (0,1)^2),
    C     meets c01 = (0,1)x(1,2) and NOT c00   (the third square the domino {c00, c01} needs),
    D     meets c10 = (1,2)x(0,1) and NOT c00   (... {c00, c10}; C != D is the triple {c00,c01,c10}),
pairwise interior-disjoint.  This is exactly "every CELLS family inside {c00, c01, c10} is over-met" with
|M(c00)| = 2.  COUNTER-HYPOTHESIS of type (pair, sa, sb): the two designated squares are wall TOUCHERS
(role V: touches x = 0; role H: touches y = 0) with senses sa != sb (+: tilt in (0,45), -: (45,90),
0: flat); the other squares are unconstrained.  sup over poses of the least margin > 0  <=>  the
counter-hypothesis is realised (a drawn WITNESS against the local lemma); <= 0 after many restarts is
[M] evidence of infeasibility, to be certified by cert255 (interval branch-and-bound).

    python local255.py [--restarts 60] [--types P1:+-,...]   -> results/local255.jsonl (resumable; logs/STOP)
"""
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
ATT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import geo255 as G                                                    # noqa: E402

OUT = os.path.join(ATT, 'results', 'local255.jsonl')
STOP = os.path.join(ATT, 'logs', 'STOP')
Q = math.pi / 4
C00, C01, C10 = (0.0, 1.0, 0.0, 1.0), (0.0, 1.0, 1.0, 2.0), (1.0, 2.0, 0.0, 1.0)
NAMES = ('B', 'A', 'C', 'D')
# pair types: which two squares are the designated touchers, and their roles
PAIRS = {'P1': (('B', 'V'), ('A', 'H')), 'P2': (('B', 'V'), ('C', 'V')),
         'P3': (('B', 'V'), ('D', 'H')), 'P4': (('C', 'V'), ('D', 'H'))}
SENSES = {'P1': ('+-', '-+', '+0', '0+'), 'P2': ('+-', '-+', '+0', '0+', '-0', '0-'),
          'P3': ('+-', '-+', '+0', '0+', '-0', '0-'), 'P4': ('+-', '-+', '+0', '0+')}
# controls: the COMMON-sense versions (must be feasible if the model is right)
CONTROLS = {'P1': ('++', '--'), 'P2': ('++', '--'), 'P3': ('++',), 'P4': ('++',)}


def w(th):
    return abs(math.cos(th)) + abs(math.sin(th))


def layout(ptype, senses):
    """per square: (role, sense or None); the parameter slices."""
    des = {name: (role, sg) for (name, role), sg in zip(PAIRS[ptype], senses)}
    spec, k = [], 0
    for name in NAMES:
        role, sg = des.get(name, ('F', None))
        npar = 3 if role == 'F' else (1 if sg == '0' else 2)
        spec.append((name, role, sg, k, npar))
        k += npar
    return spec, k


def poses_of(x, spec):
    """x -> list of (cx, cy, th) and the list of sense margins."""
    out, sm = [], []
    for name, role, sg, k, npar in spec:
        if role == 'F':
            cx, cy, th = x[k], x[k + 1], x[k + 2]
        else:
            t = x[k]
            th = 0.0 if sg == '0' else x[k + 1]
            cx, cy = (0.5 * w(th), t) if role == 'V' else (t, 0.5 * w(th))
            if sg == '+':
                sm.append(min(th, Q - th))
            elif sg == '-':
                sm.append(min(th - Q, 2 * Q - th))
        out.append((cx, cy, th))
    return out, sm


def sat_gap(P, R):
    """separation of two convex polygons (> 0 disjoint, < 0 = -overlap depth) over their edge normals."""
    best = -1e9
    for poly in (P, R):
        for i in range(len(poly)):
            e = poly[(i + 1) % len(poly)] - poly[i]
            n = np.array([-e[1], e[0]]) / math.hypot(e[0], e[1])
            a, b = P @ n, R @ n
            best = max(best, max(a.min() - b.max(), b.min() - a.max()))
    return best


def terms(x, spec):
    ps, sm = poses_of(x, spec)
    V = [G.corners_of(*p) for p in ps]
    t = [sat_gap(V[i], V[j]) for i in range(4) for j in range(i)]
    t += [min(1.0, 1.0 + 10.0 * min(v[:, 0].min(), v[:, 1].min())) for v in V]      # containment: hard
    t += [min(1.0, 1.0 + 10.0 * (3.42 - max(v[:, 0].max(), v[:, 1].max()))) for v in V]
    t += [G.depth(*ps[0], C00), G.depth(*ps[1], C00), G.depth(*ps[2], C01), G.depth(*ps[3], C10)]
    t += [-G.depth(*ps[2], C00), -G.depth(*ps[3], C00)]
    t += [4.0 * v for v in sm]
    return t, ps


def margin(x, spec):
    return min(terms(x, spec)[0])


def random_start(rng, spec, dim):
    x = np.zeros(dim)
    for name, role, sg, k, npar in spec:
        base = {'B': (0.6, 1.2), 'A': (1.2, 0.6), 'C': (0.9, 2.4), 'D': (2.4, 0.9)}[name]
        if role == 'F':
            x[k:k + 3] = [base[0] + rng.normal(0, 0.3), base[1] + rng.normal(0, 0.3), rng.uniform(0, 2 * Q)]
        else:
            x[k] = (base[1] if role == 'V' else base[0]) + rng.normal(0, 0.3)
            if sg != '0':
                x[k + 1] = rng.uniform(0.02, Q - 0.02) + (Q if sg == '-' else 0.0)
    return x


def solve(ptype, senses, restarts, seed):
    spec, dim = layout(ptype, senses)
    rng = np.random.default_rng(seed)
    best, bx = -1e9, None
    t0 = time.time()
    for r in range(restarts):
        if os.path.exists(STOP):
            break
        x0 = random_start(rng, spec, dim)
        res = minimize(lambda x: -margin(x, spec), x0, method='Nelder-Mead',
                       options={'maxiter': 3000, 'xatol': 1e-7, 'fatol': 1e-9, 'adaptive': True})
        if -res.fun > best:
            best, bx = -res.fun, res.x
        if best > 0.02:
            break
    tt, ps = terms(bx, spec)
    return {'type': '%s:%s' % (ptype, senses), 'pair': [n for n, _ in PAIRS[ptype]], 'senses': senses,
            'sup_margin': best, 'restarts_used': r + 1, 'seconds': time.time() - t0,
            'poses': {n: list(map(float, p)) for n, p in zip(NAMES, ps)},
            'phi_deg': {n: G.phi_deg(p[2]) for n, p in zip(NAMES, ps)},
            'binding': int(np.argmin(tt)), 'verdict': 'FEASIBLE-WITNESS' if best > 1e-6 else 'NO-WITNESS'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--restarts', type=int, default=60)
    ap.add_argument('--types', default='')
    ap.add_argument('--seed', type=int, default=255)
    a = ap.parse_args()
    todo = [(p, sg) for p in PAIRS for sg in CONTROLS[p] + SENSES[p]]
    if a.types:
        todo = [tuple(t.split(':')) for t in a.types.split(',')]
    done = set()
    if os.path.exists(OUT):
        done = {json.loads(l)['type'] for l in open(OUT)}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    for p, sg in todo:
        if '%s:%s' % (p, sg) in done or os.path.exists(STOP):
            continue
        row = solve(p, sg, a.restarts, a.seed)
        with open(OUT, 'a') as f:
            f.write(json.dumps(row) + '\n')
        print(row['type'], row['verdict'], round(row['sup_margin'], 5), round(row['seconds'], 1), flush=True)


if __name__ == '__main__':
    main()
