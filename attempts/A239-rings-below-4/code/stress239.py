"""A239 gear-lemma LP on a ring with its contact structure fixed (n-general): the active rows (walls + pair rows on
every tied axis, A234's stress234), the FREE Fritz-John multiplier LP {A^T lam = e_s, lam >= 0} (no tilt floor, no
crowd rows), the minimal EXTERNAL load closing the balance (A219's ring219: torque-only / force + torque), the
force table (arrows), Lemma W's wall torque per tilted wall square, Lemma PUSH's separating axis at every doubly-met
corner, the loaded component and the walls it reaches (Corollary CHAIN).
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
LP_CAP, EPS, LOAD_TOL, RHO = 1e4, 1e-7, 1e-6, 0.1
CORNERS = ('BL', 'BR', 'TR', 'TL')


def zvec(poses, S):
    return np.array([v for p in poses for v in p] + [S], float)


def rows_and_A(poses, S, tol=1e-6):
    z = zvec(poses, S)
    rows = ST.active_rows_general(z, tol)
    n = len(poses)
    A = np.array([ST.row_grad(z, r) for r in rows]) if rows else np.zeros((0, 3 * n + 1))
    return z, rows, A


def free_lp(A):
    """('lam0=1', lam) | ('self-stress', lam) | ('INFEASIBLE', None)."""
    if A.shape[0] == 0:
        return 'INFEASIBLE', None
    lam = ST.feasible(A)
    if lam is not None:
        return 'lam0=1', lam
    m, nv = A.shape
    Aeq = np.vstack([np.hstack([A.T, np.eye(nv)]), np.concatenate([np.ones(m), np.zeros(nv)])[None, :]])
    beq = np.concatenate([np.zeros(nv), [1.0]])
    r = linprog(np.zeros(m + nv), A_eq=Aeq, b_eq=beq, bounds=[(0, LP_CAP)] * m + [(-EPS, EPS)] * nv, method='highs')
    return ('self-stress', np.asarray(r.x)[:m]) if r.success else ('INFEASIBLE', None)


def min_external(A, coords):
    """min sum |mu| over external unit loads on the listed coordinates with A^T lam + E mu = e_s (EPS slack),
    lam >= 0.  Returns (lam, mu, objective) or None."""
    m, nv = A.shape
    k = len(coords)
    E = np.zeros((k, nv))
    for a, c in enumerate(coords):
        E[a, c] = 1.0
    Aeq = np.hstack([A.T, E.T, -E.T, np.eye(nv)]) if m else np.hstack([E.T, -E.T, np.eye(nv)])
    cost = np.concatenate([np.zeros(m), np.ones(2 * k), np.zeros(nv)])
    bounds = [(0, LP_CAP)] * (m + 2 * k) + [(-EPS, EPS)] * nv
    r = linprog(cost, A_eq=Aeq, b_eq=ST.e_s(nv), bounds=bounds, method='highs')
    if not r.success:
        return None
    x = np.asarray(r.x)
    return x[:m], x[m:m + k] - x[m + k:m + 2 * k], float(r.fun)


def cross2(a, b):
    return float(a[0] * b[1] - a[1] * b[0])


def force_table(z, rows, lam):
    """arrows (kind, i, j, p, f, lam) and per-square sums: W (total wall force), tau_wall, tau_contact, tilt."""
    cx, cy, th, s, n = ST.unpack(z)
    q, nrm = ST.verts(z), ST.normals(z)
    c = np.stack([cx, cy], -1)
    sq = [{'W': 0.0, 'walls': {}, 'tau_wall': 0.0, 'tau_contact': 0.0, 'F': np.zeros(2), 'contacts': []} for _ in range(n)]
    arrows = []
    for r, l in zip(rows, lam):
        if l <= LOAD_TOL:
            continue
        if r['kind'] == 'wall':
            i = r['i']
            p = q[i, r['corner']]
            f = l * np.array(WALL_IN[r['wall']])
            sq[i]['W'] += l
            sq[i]['walls'][r['wall']] = sq[i]['walls'].get(r['wall'], 0.0) + l
            sq[i]['tau_wall'] += cross2(p - c[i], f)
            sq[i]['F'] += f
            arrows.append({'kind': 'wall', 'i': i, 'wall': r['wall'], 'p': p.tolist(), 'f': f.tolist(), 'lam': float(l)})
        else:
            p_, o = r['i'], r['j']
            pt = q[p_, r['corner']]
            f = l * nrm[o, r['edge']]
            sq[p_]['F'] += f
            sq[o]['F'] -= f
            sq[p_]['tau_contact'] += cross2(pt - c[p_], f)
            sq[o]['tau_contact'] += cross2(pt - c[o], -f)
            sq[p_]['contacts'].append(o)
            sq[o]['contacts'].append(p_)
            arrows.append({'kind': 'edge', 'i': p_, 'j': o, 'p': pt.tolist(), 'f': f.tolist(), 'lam': float(l)})
    per = []
    for i in range(n):
        t = th[i] % (math.pi / 2)
        tilted = min(t, math.pi / 2 - t) > 1e-6
        per.append({'i': i, 'tilt_deg': math.degrees(t), 'tilted': bool(tilted), 'W': float(sq[i]['W']),
                    'walls': {k: float(v) for k, v in sq[i]['walls'].items()},
                    'tau_wall': float(sq[i]['tau_wall']), 'tau_contact': float(sq[i]['tau_contact']),
                    'tau_wall_lemmaW': float(0.5 * sq[i]['W'] * (math.sin(t) - math.cos(t))) if tilted else 0.0,
                    'aligning_sense': (-1 if t < math.pi / 4 else 1) if tilted else 0,
                    'F_resid': float(np.abs(sq[i]['F']).max()), 'contacts': sorted(set(sq[i]['contacts']))})
    return arrows, per


def push_axes(poses, S, meeters):
    """per doubly-met corner: the two meeters, their best separating axis (owner, edge), gap, and the axis normal
    pointing INTO the non-owner in the corner frame (n_u, n_v) plus the contact point (the non-owner's extreme
    vertex against the axis).  Lemma PUSH: a loaded push has a positive component, and a positive component along
    the wall the pushed square touches."""
    out = {}
    z = zvec(poses, S)
    q, nrm = ST.verts(z), ST.normals(z)
    c = np.array([[p[0], p[1]] for p in poses])
    for cn in CORNERS:
        ms = meeters.get(cn, [])
        if len(ms) < 2:
            continue
        i, j = ms[0], ms[1]
        best = None
        for o, p in ((i, j), (j, i)):
            for e in range(4):
                pr = (q[p] - c[o]) @ nrm[o, e] - 0.5
                k = int(np.argmin(pr))
                if best is None or pr[k] > best[0]:
                    best = (float(pr[k]), o, e, p, k)
        gap, o, e, p, k = best
        M, t, det = G.corner_frame(cn, S)
        nf = M @ nrm[o, e]
        out[cn] = {'meeters': [i, j], 'owner': o, 'pushed': p, 'edge': e, 'gap': gap, 'contact': q[p, k].tolist(),
                   'n_frame': [float(nf[0]), float(nf[1])], 'n': nrm[o, e].tolist(),
                   'touching': bool(gap <= LOAD_TOL),
                   'pushed_walls': BD.touches(poses[p], S), 'owner_walls': BD.touches(poses[o], S)}
    return out


def loaded_component(rows, lam, n, start):
    """closure of `start` under loaded pair rows; the loaded wall rows of its members."""
    adj = {i: set() for i in range(n)}
    walls = {}
    for r, l in zip(rows, lam if lam is not None else []):
        if l <= LOAD_TOL:
            continue
        if r['kind'] == 'edge':
            adj[r['i']].add(r['j'])
            adj[r['j']].add(r['i'])
        else:
            walls.setdefault(r['i'], set()).add(r['wall'])
    comp, stack = set(start), list(start)
    while stack:
        i = stack.pop()
        for j in adj[i]:
            if j not in comp:
                comp.add(j)
                stack.append(j)
    return sorted(comp), {i: sorted(walls.get(i, [])) for i in comp}


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


def analyse(poses, S, tol=1e-6):
    """the whole gear-lemma reading of one ring."""
    z, rows, A = rows_and_A(poses, S, tol)
    n = len(poses)
    meeters = {cn: BD.meeters(poses, S, cn) for cn in CORNERS}
    status, lam = free_lp(A)
    res = {'n': n, 'S': S, 'n_rows': len(rows), 'rows': [{k: v for k, v in r.items()} for r in rows],
           'free_lp': status, 'meeters': meeters, 'pattern': ' '.join(str(len(meeters[c])) for c in CORNERS)}
    if lam is not None:
        res['lam'] = lam.tolist()
        res['arrows'], res['squares'] = force_table(z, rows, lam)
    tc = [3 * i + 2 for i in range(n)]
    fc = [3 * i + a for i in range(n) for a in range(3)]
    r_t = min_external(A, tc)
    res['torque_only'] = None if r_t is None else {'objective': r_t[2], 'tau': {i: float(r_t[1][i]) for i in range(n) if abs(r_t[1][i]) > 1e-7}}
    r_f = min_external(A, fc)
    pr = partner_rows(rows, meeters)
    res['partner_rows'] = pr
    for key, r_ in (('deficit', r_f), ('loaded_deficit', loaded_deficit(A, n, pr, RHO) if pr else None)):
        if r_ is None:
            res[key] = None
            continue
        lamF, muF, obj = r_
        res[key] = {'objective': obj, 'per_square': classify_external(muF, z, meeters, S), 'lam': lamF.tolist(),
                    'rho': RHO if key == 'loaded_deficit' else 0.0}
        res[key]['arrows'], res[key]['squares'] = force_table(z, rows, lamF)
        start = [i for cn in CORNERS for i in meeters[cn]]
        comp, cw = loaded_component(rows, lamF, n, start)
        res[key]['component'] = comp
        res[key]['component_walls'] = cw
    res['push'] = push_axes(poses, S, meeters)
    return res
