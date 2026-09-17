"""A245 -- the fixed-tilt side-minimising LP with a FREE SUBSET of centres (n-general).

Rows (Lemma GRAIN-LP, `grain_flood.md`): walls  c >= w(theta), c <= s - w(theta) per coordinate; for every
pair with a free member the selected separating axis (owner o, outward edge normal n_e(theta_o)):
n . (c_p - c_o) >= (1 + wfun(n, theta_p)) / 2 -- affine in the free centres, constant in the fixed ones.
The selection is re-chosen at the LP's solution until stable (A223 `click223.lp` / `select`).
"""
import math

import numpy as np
from scipy.optimize import linprog

import geom245 as G

NHAT = np.array([(0.0, -1.0), (1.0, 0.0), (0.0, 1.0), (-1.0, 0.0)])
S_MAX = 9.0
TOL = 1e-7


def onormals(th):
    co, si = math.cos(th), math.sin(th)
    return np.array([(co * n[0] - si * n[1], si * n[0] + co * n[1]) for n in NHAT])


def wfun(n, th):
    return abs(n[0] * math.cos(th) + n[1] * math.sin(th)) + abs(-n[0] * math.sin(th) + n[1] * math.cos(th))


def select(poses, pairs, fixed_sel=None):
    """best separating axis (owner, edge) per pair at the current poses; `fixed_sel` pins some pairs."""
    fixed_sel = fixed_sel or {}
    V = [G.verts(p) for p in poses]
    C = [np.array(p[:2]) for p in poses]
    NM = [onormals(p[2]) for p in poses]
    sel, gaps = {}, {}
    for (i, j) in pairs:
        if (i, j) in fixed_sel:
            o, e = fixed_sel[(i, j)]
            p = j if o == i else i
            sel[(i, j)] = (o, e)
            gaps[(i, j)] = float((NM[o][e] @ (V[p] - C[o]).T).min() - 0.5)
            continue
        best = None
        for o, p in ((i, j), (j, i)):
            g = (NM[o] @ (V[p] - C[o]).T).min(axis=1) - 0.5          # (4 edges,)
            e = int(np.argmax(g))
            if best is None or g[e] > best[0]:
                best = (float(g[e]), o, e)
        gaps[(i, j)] = best[0]
        sel[(i, j)] = (best[1], best[2])
    return sel, gaps


def lp(poses, free, sel, s_max=S_MAX):
    """min s over the free centres at the poses' tilts; returns (new poses, s) or None if infeasible."""
    n = len(poses)
    idx = {i: k for k, i in enumerate(free)}
    nv = 2 * len(free) + 1
    A, b = [], []

    def row():
        return np.zeros(nv)
    for i, (cx, cy, th) in enumerate(poses):
        w = G.extent(th) / 2
        if i in idx:
            k = idx[i]
            for d in range(2):
                r = row(); r[2 * k + d] = -1.0; A.append(r); b.append(-w)
                r = row(); r[2 * k + d] = 1.0; r[-1] = -1.0; A.append(r); b.append(-w)
        else:
            for c in (cx, cy):
                r = row(); r[-1] = -1.0; A.append(r); b.append(-(c + w))
    for (i, j), (o, e) in sel.items():
        p = j if o == i else i
        if o not in idx and p not in idx:
            continue
        nrm = onormals(poses[o][2])[e]
        rhs = (1 + wfun(nrm, poses[p][2])) / 2
        r = row()
        const = 0.0
        if p in idx:
            r[2 * idx[p]:2 * idx[p] + 2] = -nrm
        else:
            const += -nrm @ np.array(poses[p][:2])
        if o in idx:
            r[2 * idx[o]:2 * idx[o] + 2] = nrm
        else:
            const += nrm @ np.array(poses[o][:2])
        A.append(r); b.append(-rhs - const)                # -n.c_p + n.c_o <= -rhs  (constants moved)
    cost = row(); cost[-1] = 1.0
    res = linprog(cost, A_ub=np.array(A), b_ub=np.array(b),
                  bounds=[(0, s_max)] * (nv - 1) + [(1, s_max)], method='highs')
    if not res.success:
        return None
    out = list(poses)
    for i, k in idx.items():
        out[i] = (float(res.x[2 * k]), float(res.x[2 * k + 1]), poses[i][2])
    return out, float(res.x[-1])


def fixed_tilt_min(poses, free, iters=8, fixed_sel=None):
    """alternating LP; returns (poses, s, sel, k) or (None, None, sel, k) when P(S, theta) is empty."""
    n = len(poses)
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n) if i in free or j in free]
    sel, _ = select(poses, pairs, fixed_sel)
    best, k = None, 0
    for k in range(iters):
        r = lp(poses, free, sel)
        if r is None:
            return (None, None, sel, k) if best is None else best + (k,)
        poses, s = r
        if best is None or s < best[1] - 1e-10:
            best = (poses, s, sel)
        sel2, _ = select(poses, pairs, fixed_sel)
        if sel2 == sel:
            break
        sel = sel2
    return best + (k + 1,)


def blockers(poses_prev, poses_new, members):
    """pairs (member, other) whose SAT gap is negative at the new tilts with the previous centres."""
    trial = [(poses_prev[i][0], poses_prev[i][1], poses_new[i][2]) for i in range(len(poses_prev))]
    out = []
    for i in members:
        for j in range(len(trial)):
            if j == i:
                continue
            g = G.pair_gap(trial[i], trial[j])
            if g < -1e-9:
                out.append((int(i), int(j), round(float(g), 5)))
    return sorted(out, key=lambda x: x[2])[:6]
