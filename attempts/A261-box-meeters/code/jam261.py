"""A261 O1 [M]: the JAMMED FLOATER -- is there a floating box meeter C that NO wall-touching cell can receive?

P1 of normal_ring.md in its any-pose form: a Phi1-maximiser has no wall-touching unit cell T (ANY tilt) with
M(T) within {C} for a non-toucher C.  Local model in the BL quadrant (s-free): X touches x = 0 (the wall's next
square, above), A touches y = 0 and meets the open box, C floats (both wall distances >= t) and meets the box.
    J := max over wall-touching cells T (on x = 0 and on y = 0, every tilt, grid + the pose C itself dropped) of
         min( gap(T, A), gap(T, X), depth(T, C) )          -- J >= 0 <=> some cell meeting C is free of A and X
and the search maximises  t = min(pair gaps, meet depths, float distances, -J).   t > 0  <=>  a JAMMED floater.
Variants: X may / may not meet the box ('third meeter' when it does).  HARD containment by parametrisation.
    python jam261.py [--restarts 30]    -> results/jam261.jsonl
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
import local261 as L                                                   # noqa: E402
G8 = L.G8
OUT = os.path.join(ATT, 'results', 'jam261.jsonl')
BOX = L.BOX
TSTEP, PSTEP = (3.0, 0.04) if os.environ.get('JAM_COARSE') else (1.0, 0.01)   # search coarse, re-check FINE
TH = np.radians(np.arange(0.0, 90.0, TSTEP))
POS = np.arange(0.0, 2.6, PSTEP)


def cells():
    """all grid cells touching x = 0 (first half) and y = 0 (second half): vertex arrays (N, 4, 2)."""
    th, p = np.meshgrid(TH, POS, indexing='ij')
    th, p = th.ravel(), p.ravel()
    wv = np.abs(np.cos(th)) + np.abs(np.sin(th))
    out = []
    for cx, cy in ((0.5 * wv, 0.5 * wv + p), (0.5 * wv + p, 0.5 * wv)):
        c, s = np.cos(th), np.sin(th)
        V = np.stack([np.stack([cx + 0.5 * (a * c - b * s), cy + 0.5 * (a * s + b * c)], 1)
                      for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))], 1)
        out.append(V)
    return np.concatenate(out), np.concatenate([th, th])


CELLS, CTH = cells()
CN = np.stack([np.stack([np.cos(CTH), np.sin(CTH)], 1), np.stack([-np.sin(CTH), np.cos(CTH)], 1)], 1)   # (N, 2, 2)


def gaps(P):
    """SAT gap of every grid cell against the polygon P: (N,)."""
    e = np.roll(P, -1, 0) - P
    n = np.stack([e[:2, 1], -e[:2, 0]], 1)
    n = n / np.linalg.norm(n, axis=1, keepdims=True)
    best = np.full(len(CELLS), -1e9)
    for ax in n:                                                        # the polygon's two axes
        pc, pp = CELLS @ ax, P @ ax
        best = np.maximum(best, np.maximum(pc.min(1) - pp.max(), pp.min() - pc.max(1)))
    for k in (0, 1):                                                    # each cell's own two axes
        pc = np.einsum('nvj,nj->nv', CELLS, CN[:, k])
        pp = P @ CN[:, k].T                                             # (4, N)
        best = np.maximum(best, np.maximum(pc.min(1) - pp.max(0), pp.min(0) - pc.max(1)))
    return best


def J_of(P):
    """P = [C, A, X] vertex arrays."""
    j = np.minimum(np.minimum(gaps(P[1]), gaps(P[2])), -gaps(P[0]))
    i = int(np.argmax(j))
    return float(j[i]), i


def terms(x, sq, meet, notmeet):
    ps = L.poses(x, sq)
    P = [L.verts(*p) for p in ps]
    t = [G8.sat_gap(P[i], P[j]) for i in range(3) for j in range(i)]
    t += [3.2 - float(p.max()) for p in P]
    t += [G8.depth(P[i], BOX) for i, s in enumerate(sq) if s[0] in meet]
    t += [-G8.depth(P[i], BOX) for i, s in enumerate(sq) if s[0] in notmeet]
    t += [float(P[0][:, 0].min()), float(P[0][:, 1].min())]
    j, i = J_of(P)
    return t + [-j], ps, i


def seeds(rng, n):
    out = []
    for _ in range(n):
        tx, ta, tc = math.radians(rng.uniform(15, 44)), math.radians(rng.uniform(0.5, 20)), math.radians(rng.uniform(0, 44))
        a, yx = rng.uniform(0.6, 1.0), rng.uniform(1.2, 2.0)
        cx, cy = rng.uniform(0.9, 1.5), rng.uniform(1.2, 1.8)
        out.append([math.sqrt(max(cx - L.w(tc) / 2, 1e-3)), math.sqrt(max(cy - L.w(tc) / 2, 1e-3)), tc,
                    math.sqrt(a), ta, math.sqrt(yx), tx])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--restarts', type=int, default=30)
    a = ap.parse_args()
    rng = np.random.default_rng(261)
    for key, notmeet in (('JAM', ['X']), ('JAM3', [])):
        sq, dim = L.layout('C:F A:H X:V')
        meet = ['C', 'A'] if key == 'JAM' else ['C', 'A', 'X']
        f = lambda x: -min(terms(x, sq, meet, notmeet)[0])
        best, bx, t0 = -1e9, None, time.time()
        for x0 in seeds(rng, a.restarts):
            r = minimize(f, x0, method='Nelder-Mead', options=dict(maxiter=2500, xatol=1e-7, fatol=1e-9, adaptive=True))
            r = minimize(f, r.x, method='Nelder-Mead', options=dict(maxiter=2500, xatol=1e-8, fatol=1e-10, adaptive=True))
            if -r.fun > best:
                best, bx = -r.fun, r.x
        t, ps, i = terms(bx, sq, meet, notmeet)
        row = dict(scenario=key, squares='C:F A:H X:V', meet=meet, notmeet=notmeet, sup_margin=best,
                   restarts=a.restarts, seconds=round(time.time() - t0, 1), terms=[float(v) for v in t],
                   poses={s[0]: list(map(float, p)) for s, p in zip(sq, ps)},
                   freest_cell=dict(wall='x0' if i < len(CELLS) // 2 else 'y0', verts=CELLS[i].tolist(), J=-float(t[-1])),
                   grid=dict(tilt_step_deg=TSTEP, pos_step=PSTEP),
                   verdict='JAMMED-WITNESS (grid)' if best > 1e-6 else 'NO-WITNESS')
        with open(OUT, 'a') as fh:
            fh.write(json.dumps(row) + '\n')
        print(key, row['verdict'], '%.5f' % best, row['seconds'], 's', flush=True)


if __name__ == '__main__':
    main()
