"""A255 addendum, local search WITH the slide-block clause (five squares).

On top of local255's model (B, A root meeters; C meets c01 not c00; D meets c10 not c00) a fifth square E
(unconstrained) and the clause "the second meeter is BLOCKED from the normalising slide":
    W-types (the wall chain):  s1 = B (wall toucher, tilted), slider C (the second meeter of c01, a wall
        toucher of ANOTHER sense or flat), normal cell T = B + (0, sec phi_B): some square other than B, C
        meets T  (else C teleports onto T: Lemma CELLS on the tilted cell {T}, and the pair becomes common);
    K-types (the corner):  s1 = A (floor toucher, tilted), slider D (the second meeter of c10, unconstrained),
        T = A + (sec phi_A, 0) blocked by a square other than A, D; B is a wall toucher of another sense
        (the corner's mixed pair survives the normalisation of its floor row).
sup-margin > 0  <=>  the blocked counter-hypothesis is realised locally (witness, to be drawn).
    python blocked255.py [--restarts 80]   -> results/blocked255.jsonl (resumable; logs/STOP)
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
import local255 as L                                                  # noqa: E402

OUT = os.path.join(ATT, 'results', 'blocked255.jsonl')
TYPES = [('W', sg) for sg in ('+-', '-+', '+0', '-0')] + [('K', sg) for sg in ('+-', '-+', '+0', '-0')]
# sg = (sense of s1, sense of the other designated toucher); s1 is always tilted (it defines T)


def layout(kind, sg):
    ptype = 'P2' if kind == 'W' else 'P1'
    senses = sg if kind == 'W' else sg[::-1]           # P1's order is (B, A); s1 = A carries sg[0]
    spec, dim = L.layout(ptype, senses)
    return spec, dim, dim + 3                          # E = three more parameters


def terms(x, spec, dim, kind):
    t, ps = L.terms(x[:dim], spec)
    E = (x[dim], x[dim + 1], x[dim + 2])
    VE = G.corners_of(*E)
    V = [G.corners_of(*p) for p in ps]
    t += [L.sat_gap(VE, v) for v in V]
    t += [min(1.0, 1.0 + 10.0 * min(VE[:, 0].min(), VE[:, 1].min())),
          min(1.0, 1.0 + 10.0 * (3.42 - max(VE[:, 0].max(), VE[:, 1].max()))),
          -G.depth(*E, L.C00)]                         # E is not a third root meeter (|M(c00)| = 2)
    s1 = ps[0] if kind == 'W' else ps[1]
    sec = 1.0 / math.cos(math.radians(G.phi_deg(s1[2])))
    T = (s1[0], s1[1] + sec, s1[2]) if kind == 'W' else (s1[0] + sec, s1[1], s1[2])
    VT = G.corners_of(*T)
    others = ([V[1], V[3]] if kind == 'W' else [V[0], V[2]]) + [VE]     # not s1, not the slider
    t.append(max(-L.sat_gap(v, VT) for v in others))   # a BLOCKER meets T
    slider = V[2] if kind == 'W' else V[3]
    t.append(-L.sat_gap(slider, VT) + 1.0)             # informational (never binding)
    return t, ps + [E], T


def solve(kind, sg, restarts, seed):
    spec, dim, full = layout(kind, sg)
    rng = np.random.default_rng(seed)
    best, bx = -1e9, None
    t0 = time.time()
    for r in range(restarts):
        if os.path.exists(L.STOP):
            break
        x0 = np.concatenate([L.random_start(rng, spec, dim),
                             [rng.uniform(0.6, 2.6), rng.uniform(0.6, 2.6), rng.uniform(0, math.pi / 2)]])
        res = minimize(lambda x: -min(terms(x, spec, dim, kind)[0]), x0, method='Nelder-Mead',
                       options={'maxiter': 4000, 'xatol': 1e-7, 'fatol': 1e-9, 'adaptive': True})
        if -res.fun > best:
            best, bx = -res.fun, res.x
        if best > 0.02:
            break
    tt, ps, T = terms(bx, spec, dim, kind)
    return {'type': '%s:%s' % (kind, sg), 'sup_margin': best, 'restarts_used': r + 1, 'seconds': time.time() - t0,
            'poses': {n: list(map(float, p)) for n, p in zip(L.NAMES + ('E',), ps)}, 'T': list(map(float, T)),
            'phi_deg': {n: G.phi_deg(p[2]) for n, p in zip(L.NAMES + ('E',), ps)},
            'verdict': 'FEASIBLE-WITNESS' if best > 1e-6 else 'NO-WITNESS'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--restarts', type=int, default=80)
    ap.add_argument('--seed', type=int, default=2255)
    a = ap.parse_args()
    done = {json.loads(l)['type'] for l in open(OUT)} if os.path.exists(OUT) else set()
    for kind, sg in TYPES:
        if '%s:%s' % (kind, sg) in done or os.path.exists(L.STOP):
            continue
        row = solve(kind, sg, a.restarts, a.seed)
        with open(OUT, 'a') as f:
            f.write(json.dumps(row) + '\n')
        print(row['type'], row['verdict'], round(row['sup_margin'], 5), round(row['seconds'], 1), flush=True)


if __name__ == '__main__':
    main()
