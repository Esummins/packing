"""A239 deficit helpers (n-general), split from stress239: the LOADED minimal external load (every partner row
carries lam >= rho: hypothesis LOAD of k0_count.md), the partner rows of the doubly-met corners, and the reading of
an external load per square (into its wall / along its wall toward the corner / other; the torque's sense vs Lemma W).
"""
import math
import os
import sys

import numpy as np
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
for a in ('A234-handedness', 'A217-torque-probe', 'A236-ring-capacity'):
    sys.path.insert(0, os.path.join(HERE, '..', '..', a, 'code'))
import stress234 as ST                                                     # noqa: E402
import geom217 as G                                                        # noqa: E402
import band236 as BD                                                       # noqa: E402

WALL_IN = {'x=0': (1.0, 0.0), 'y=0': (0.0, 1.0), 'x=s': (-1.0, 0.0), 'y=s': (0.0, -1.0)}
LP_CAP, EPS = 1e4, 1e-7
CORNERS = ('BL', 'BR', 'TR', 'TL')


def loaded_deficit(A, n, rows, rho):
    """the minimal external load (force + torque on every square) closing the balance when every PARTNER row
    (the A-B pair of a doubly-met corner, listed by index in `rows`) carries lam >= rho: LOAD of k0_count.md.
    Returns (lam, mu, objective) or None."""
    m, nv = A.shape
    k = 3 * n
    E = np.zeros((k, nv))
    for a in range(k):
        E[a, a] = 1.0
    Aeq = np.hstack([A.T, E.T, -E.T, np.eye(nv)])
    cost = np.concatenate([np.zeros(m), np.ones(2 * k), np.zeros(nv)])
    bounds = [(rho if i in rows else 0.0, LP_CAP) for i in range(m)] + [(0, LP_CAP)] * (2 * k) + [(-EPS, EPS)] * nv
    r = linprog(cost, A_eq=Aeq, b_eq=ST.e_s(nv), bounds=bounds, method='highs')
    if not r.success:
        return None
    x = np.asarray(r.x)
    return x[:m], x[m:m + k] - x[m + k:m + 2 * k], float(r.fun)


def partner_rows(rows, meeters):
    """indices of the pair rows joining the two meeters of a doubly-met corner."""
    out = []
    for cn, ms in meeters.items():
        if len(ms) >= 2:
            for k, r in enumerate(rows):
                if r['kind'] == 'edge' and {r['i'], r['j']} == {ms[0], ms[1]}:
                    out.append(k)
    return out


def classify_external(mu, z, meeters, S):
    """per square the external force / torque of the minimal closing load, read in its corner frame when it is a
    meeter: into its wall / along its wall toward the corner / other; the torque's sense vs Lemma W."""
    cx, cy, th, s, n = ST.unpack(z)
    who = {i: cn for cn in CORNERS for i in meeters[cn]}
    poses = [(cx[i], cy[i], th[i]) for i in range(n)]
    out = {}
    for i in range(n):
        F, tau = mu[3 * i:3 * i + 2], float(mu[3 * i + 2])
        if np.linalg.norm(F) < 1e-7 and abs(tau) < 1e-7:
            continue
        d = {'F': [float(F[0]), float(F[1])], 'tau': tau, 'meeter': i in who}
        t = th[i] % (math.pi / 2)
        tilted = min(t, math.pi / 2 - t) > 1e-6
        if tilted and abs(tau) > 1e-7:
            d['torque'] = 'anti-aligning' if np.sign(tau) == np.sign(math.cos(t) - math.sin(t)) else 'aligning'
        if np.linalg.norm(F) > 1e-7:
            u = F / np.linalg.norm(F)
            walls = BD.touches(poses[i], S)
            cands = {}
            for wl in walls:
                cands['into ' + wl] = float(u @ -np.array(WALL_IN[{'floor': 'y=0', 'right': 'x=s', 'ceil': 'y=s', 'left': 'x=0'}[wl]]))
            if i in who:
                M, tr, det = G.corner_frame(who[i], S)
                uf = M @ u
                d['F_frame'] = [float(uf[0]), float(uf[1])]
                for wl in walls:
                    a = 0 if wl in ('left', 'right') else 1
                    cands['along %s toward corner' % wl] = float(-uf[1 - a])
            d['direction'] = max(cands, key=cands.get) if cands else 'interior'
            d['cos'] = cands.get(d.get('direction'))
        out[i] = d
    return out
