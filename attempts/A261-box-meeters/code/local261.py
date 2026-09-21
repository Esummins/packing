"""A261 O1 / O2 [M]: the LOCAL search for a FLOATING box meeter that the normal form cannot land.

Corner frame of BL (quadrant x, y >= 0; every square lies in [0, 3.2]^2, so the problem is s-FREE, the same for every
m >= 4).  P1+ of box_meeters.md: in a Phi1-maximiser both DROP CELLS of a non-toucher C (C translated straight onto
x = 0 / onto y = 0) are met by another square, and the chain of blockers ends in wall touchers.  A scenario lists
squares with a role  V (touches x = 0), H (touches y = 0), F (floats: both wall distances >= t), which of them must
MEET the open box (0,1)^2, which must NOT, and demands for every floater and both walls a blocker among the listed
squares.  HARD containment by parametrisation (F: cx = w/2 + p^2, cy = w/2 + q^2); sup of the least margin by
Nelder-Mead restarts; every witness is re-checked by check_witness (independent SAT: A258's geo258, imported).

    python local261.py [--restarts 40] [--only A,B]      -> results/local261.jsonl   (resumable; logs/STOP_LOCAL)
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
sys.path.insert(0, os.path.abspath(os.path.join(ATT, '..', 'A258-normal-ring', 'code')))
import geo258 as G8                                                    # noqa: E402

OUT = os.path.join(ATT, 'results', 'local261.jsonl')
STOP = os.path.join(ATT, 'logs', 'STOP_LOCAL')
BOX = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], float)
# name: (squares 'name:role', meet, notmeet, what it IS)
SCEN = {
    'A': ('C:F B:V', 'C B', '', 'floater C + wall toucher B, both meet the box; B alone blocks both drops of C'),
    'B': ('C:F B:V Y:H', 'C B', 'Y', 'exactly two meeters: floater C and wall toucher B; floor toucher Y (not a meeter) under C'),
    'B2': ('C:F B:V Y:H', 'C B', '', 'as B, Y free to meet the box too'),
    'C': ('C:F B:V A:H', 'C B A', '', 'THIRD meeter: wall toucher B, floor toucher A and a floater C all meet the box'),
    'D': ('C:F B:V X:V Y:H', 'C B', 'X Y', 'two meeters C (floats), B; blockers X on the wall above, Y on the floor, not meeters'),
    'E': ('C:F D:F X:V Y:H', 'C D', 'X Y', 'FLOAT2: both meeters float; touchers X, Y (not meeters) block'),
    'E2': ('C:F D:F X:V Y:H', 'C D', '', 'FLOAT2 with X, Y free to meet the box'),
    'G': ('C:F B:V K:F Y:H', 'C B', 'K Y', 'floater C blocked by a second floater K (itself blocked) and toucher Y'),
}


def w(th):
    return abs(math.cos(th)) + abs(math.sin(th))


def verts(cx, cy, th):
    c, s = math.cos(th), math.sin(th)
    return np.array([[cx + 0.5 * (a * c - b * s), cy + 0.5 * (a * s + b * c)] for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))])


def layout(spec):
    sq, k = [], 0
    for tok in spec.split():
        name, role = tok.split(':')
        n = 3 if role == 'F' else 2
        sq.append((name, role, k))
        k += n
    return sq, k


def poses(x, sq):
    out = []
    for name, role, k in sq:
        if role == 'F':
            th = x[k + 2]
            out.append((0.5 * w(th) + x[k] ** 2, 0.5 * w(th) + x[k + 1] ** 2, th))
        elif role == 'V':
            out.append((0.5 * w(x[k + 1]), 0.5 * w(x[k + 1]) + x[k] ** 2, x[k + 1]))
        else:
            out.append((0.5 * w(x[k + 1]) + x[k] ** 2, 0.5 * w(x[k + 1]), x[k + 1]))
    return out


def terms(x, sq, meet, notmeet):
    ps = poses(x, sq)
    P = [verts(*p) for p in ps]
    names = [s[0] for s in sq]
    t = [G8.sat_gap(P[i], P[j]) for i in range(len(P)) for j in range(i)]
    t += [3.2 - float(p.max()) for p in P]
    for i, (name, role, k) in enumerate(sq):
        if name in meet:
            t.append(G8.depth(P[i], BOX))
        if name in notmeet:
            t.append(-G8.depth(P[i], BOX))
        if role == 'F':
            dx, dy = float(P[i][:, 0].min()), float(P[i][:, 1].min())
            t += [dx, dy]
            Tu, Tv = P[i] - [dx, 0.0], P[i] - [0.0, dy]
            t.append(max(G8.depth(P[j], Tu) for j in range(len(P)) if j != i))
            t.append(max(G8.depth(P[j], Tv) for j in range(len(P)) if j != i))
    return t, ps, names


def check_witness(ps, sq, meet, notmeet):
    """independent re-check from the POSES only: containment, pairwise SAT gaps, box meetings, floats, drops."""
    P = [verts(*p) for p in ps]
    r = dict(contain=min(float(p.min()) for p in P), pair_gap=min(G8.sat_gap(P[i], P[j]) for i in range(len(P)) for j in range(i)))
    names = [s[0] for s in sq]
    r['meet_depth'] = {n: G8.depth(P[names.index(n)], BOX) for n in meet}
    r['notmeet_depth'] = {n: G8.depth(P[names.index(n)], BOX) for n in notmeet}
    r['touch'] = {s[0]: [float(P[i][:, 0].min()), float(P[i][:, 1].min())] for i, s in enumerate(sq)}
    drops = {}
    for i, s in enumerate(sq):
        if s[1] == 'F':
            dx, dy = r['touch'][s[0]]
            for lab, T in (('u', P[i] - [dx, 0.0]), ('v', P[i] - [0.0, dy])):
                drops[s[0] + lab] = {names[j]: G8.depth(P[j], T) for j in range(len(P)) if j != i and G8.depth(P[j], T) > 0}
    r['drop_blockers'] = drops
    r['ok'] = bool(r['contain'] >= -1e-12 and r['pair_gap'] >= -1e-12 and all(v > 0 for v in r['meet_depth'].values())
                   and all(v <= 0 for v in r['notmeet_depth'].values()) and all(len(v) > 0 for v in drops.values())
                   and all(min(r['touch'][s[0]]) > 0 for s in sq if s[1] == 'F'))
    return r


def solve(key, restarts, seed):
    spec, meet, notmeet, what = SCEN[key]
    sq, dim = layout(spec)
    meet, notmeet = meet.split(), notmeet.split()
    rng = np.random.default_rng(seed)
    f = lambda x: -min(terms(x, sq, meet, notmeet)[0])
    best, bx, t0 = -1e9, None, time.time()
    for r in range(restarts):
        if os.path.exists(STOP):
            break
        x0 = np.concatenate([np.append(rng.uniform(0.0, 1.1, 2 if s[1] == 'F' else 1), rng.uniform(0, math.pi / 2)) for s in sq])
        res = minimize(f, x0, method='Nelder-Mead', options=dict(maxiter=4000, xatol=1e-8, fatol=1e-10, adaptive=True))
        res = minimize(f, res.x, method='Nelder-Mead', options=dict(maxiter=4000, xatol=1e-9, fatol=1e-11, adaptive=True))
        if -res.fun > best:
            best, bx = -res.fun, res.x
    tt, ps, names = terms(bx, sq, meet, notmeet)
    row = dict(scenario=key, what=what, squares=spec, meet=meet, notmeet=notmeet, sup_margin=best, restarts=r + 1,
               seconds=round(time.time() - t0, 1), poses={n: list(map(float, p)) for n, p in zip(names, ps)},
               verdict='FEASIBLE-WITNESS' if best > 1e-6 else 'NO-WITNESS')
    row['check'] = check_witness(ps, sq, meet, notmeet)
    if row['verdict'] == 'FEASIBLE-WITNESS' and not row['check']['ok']:
        row['verdict'] = 'CHECK-FAILED'
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--restarts', type=int, default=40)
    ap.add_argument('--only', default='')
    ap.add_argument('--seed', type=int, default=261)
    a = ap.parse_args()
    done = {json.loads(ln)['scenario'] for ln in open(OUT)} if os.path.exists(OUT) else set()
    for key in (a.only.split(',') if a.only else SCEN):
        if key in done or os.path.exists(STOP):
            continue
        row = solve(key, a.restarts, a.seed)
        with open(OUT, 'a') as fh:
            fh.write(json.dumps(row) + '\n')
        print(key, row['verdict'], '%.5f' % row['sup_margin'], row['seconds'], 's', flush=True)


if __name__ == '__main__':
    main()
