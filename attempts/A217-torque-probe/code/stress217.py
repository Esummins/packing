"""A217 Fritz-John stress at a witness: forces on the active contacts, per-square wall / holder torques,
per-corner signed torques in the corner frame, global wall-torque checks, LP ranges over the multiplier
polytope {A^T lam = e_s, lam >= 0}.
"""
import math
import os
import sys

import numpy as np
from scipy.optimize import linprog, nnls

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geom217 as G
import opt217 as O

PI2 = math.pi / 2
WALL_N = {'x=0': (1.0, 0.0), 'y=0': (0.0, 1.0), 'x=s': (-1.0, 0.0), 'y=s': (0.0, -1.0)}
LP_CAP = 1e4


def cross(a, b):
    return a[0] * b[1] - a[1] * b[0]


def multipliers(A, lam0=1.0):
    """Feasible lam >= 0 with A^T lam = lam0 e_s (lam0 = 1) or A^T lam = 0, sum lam = 1 (lam0 = 0)."""
    m = A.shape[0]
    if m == 0:
        return None
    if lam0 > 0:
        r = linprog(np.ones(m), A_eq=A.T, b_eq=O.E_S, bounds=(0, LP_CAP), method='highs')
    else:
        Aeq = np.vstack([A.T, np.ones((1, m))])
        beq = np.concatenate([np.zeros(G.NV), [1.0]])
        r = linprog(np.zeros(m), A_eq=Aeq, b_eq=beq, bounds=(0, LP_CAP), method='highs')
    return np.asarray(r.x) if r.success else None


def lp_range(A, w, lam0=1.0):
    """min and max of w.lam over the multiplier polytope."""
    m = A.shape[0]
    out = []
    for sgn in (1.0, -1.0):
        if lam0 > 0:
            r = linprog(sgn * w, A_eq=A.T, b_eq=O.E_S, bounds=(0, LP_CAP), method='highs')
        else:
            Aeq = np.vstack([A.T, np.ones((1, m))])
            beq = np.concatenate([np.zeros(G.NV), [1.0]])
            r = linprog(sgn * w, A_eq=Aeq, b_eq=beq, bounds=(0, LP_CAP), method='highs')
        out.append(float(sgn * r.fun) if r.success else float('nan'))
    return out


def force_table(z, rows, lam):
    """Per row: (square, point, force) entries; per square: wall force, wall torque, contact torque,
    bound torque."""
    cx, cy, th, s = G.unpack(z)
    q = G.corners(z)
    n = G.normals(z)
    c = np.stack([cx, cy], -1)
    sq = [{'F_wall': np.zeros(2), 'tau_wall': 0.0, 'tau_contact': 0.0, 'tau_bound': 0.0,
           'F_contact': np.zeros(2), 'W': {w: 0.0 for w in G.WALLS}, 'contacts': []} for _ in range(G.N)]
    arrows = []
    for r, l in zip(rows, lam):
        if l <= 1e-12:
            continue
        if r['kind'] == 'wall':
            i = r['i']
            p = q[i, r['corner']]
            f = l * np.array(WALL_N[r['wall']])
            sq[i]['F_wall'] += f
            sq[i]['tau_wall'] += cross(p - c[i], f)
            sq[i]['W'][r['wall']] += l
            arrows.append({'kind': 'wall', 'i': i, 'wall': r['wall'], 'p': p.tolist(), 'f': f.tolist(), 'lam': float(l)})
        elif r['kind'] == 'edge':
            p_, j = r['i'], r['j']
            pt = q[p_, r['corner']]
            f = l * n[j, r['edge']]
            sq[p_]['F_contact'] += f
            sq[p_]['tau_contact'] += cross(pt - c[p_], f)
            sq[j]['F_contact'] -= f
            sq[j]['tau_contact'] += cross(pt - c[j], -f)
            sq[p_]['contacts'].append((j, float(cross(pt - c[p_], f))))
            sq[j]['contacts'].append((p_, float(cross(pt - c[j], -f))))
            arrows.append({'kind': 'edge', 'i': p_, 'j': j, 'p': pt.tolist(), 'f': f.tolist(), 'lam': float(l)})
        elif r['kind'] == 'tiltbound':
            sq[r['i']]['tau_bound'] += r['sign'] * l
        elif r['kind'] == 'crowd':                       # external force at the designated vertex, toward the corner
            i = r['i']
            M, t_, _ = G.corner_frame(r['corner'], s)
            a = 0 if r['coord'] == 'u' else 1
            f = -l * M[a]
            pt = q[i, r['vertex']]
            sq[i]['F_bound'] = sq[i].get('F_bound', np.zeros(2)) + f
            sq[i]['tau_bound'] += cross(pt - c[i], f)
            arrows.append({'kind': 'crowd', 'i': i, 'corner': r['corner'], 'p': pt.tolist(), 'f': f.tolist(), 'lam': float(l)})
    return sq, arrows


def analyse(z, tmin=None, tol=1e-7, extra_active=None):
    cx, cy, th, s = G.unpack(z)
    res, lam_nnls, rows = O.fj_residual(z, tol=tol, tmin=tmin, extra_active=extra_active)
    rows2, A = O.active_rows(z, tol)
    if extra_active is not None and len(extra_active[0]):
        A = np.vstack([A, np.asarray(extra_active[1])])
    nb = len(rows) - A.shape[0]                      # the tilt-bound rows fj_residual appended last
    if nb > 0:
        extra = []
        for r in rows[-nb:]:
            g = np.zeros(G.NV)
            g[3 * r['i'] + 2] = r['sign']
            extra.append(g)
        A = np.vstack([A, np.array(extra)])
    lam0 = 1.0
    lam = multipliers(A, 1.0) if A.shape[0] else None
    if lam is None:
        lam = multipliers(A, 0.0) if A.shape[0] else None
        lam0 = 0.0 if lam is not None else None
    out = {'s': float(s), 'fj_res': res, 'n_rows': len(rows), 'lam0': lam0, 'rows': rows}
    if lam is None:
        out['fj'] = 'INFEASIBLE'
        return out
    out['fj'] = 'lam0=1' if lam0 == 1.0 else 'lam0=0 (self-stress)'
    out['lam'] = lam.tolist()
    sq, arrows = force_table(z, rows, lam)
    out['arrows'] = arrows
    O_ = np.array([s / 2, s / 2])
    q = G.corners(z)
    tot_wall_torque = 0.0
    moments = {w: 0.0 for w in G.WALLS}
    pressure = {w: 0.0 for w in G.WALLS}
    for r, l in zip(rows, lam):
        if r['kind'] != 'wall' or l <= 1e-12:
            continue
        p = q[r['i'], r['corner']]
        f = l * np.array(WALL_N[r['wall']])
        tot_wall_torque += cross(p - O_, f)
        pressure[r['wall']] += l
        along = (p[1] - s / 2) if r['wall'] in ('x=0', 'x=s') else (p[0] - s / 2)
        moments[r['wall']] += l * along
    out['total_wall_torque_about_centre'] = float(tot_wall_torque)
    out['wall_pressure'] = pressure
    out['wall_moment'] = moments
    out['sum_farwall_lambda'] = pressure['x=s'] + pressure['y=s']
    # per square
    per = []
    for i in range(G.N):
        d = sq[i]
        eq_t = d['tau_wall'] + d['tau_contact'] + d['tau_bound']
        eq_f = d['F_wall'] + d['F_contact'] + d.get('F_bound', np.zeros(2))
        W = sum(d['W'].values())
        t = th[i] % PI2
        per.append({'i': i, 'tilt_deg': math.degrees(t), 'tilted': G.axis_dev(th[i]) > 1e-6,
                    'W': W, 'W_walls': {w: v for w, v in d['W'].items() if v > 1e-12},
                    'tau_wall': d['tau_wall'], 'tau_contact': d['tau_contact'], 'tau_bound': d['tau_bound'],
                    'tau_wall_pred': 0.5 * W * (math.sin(t) - math.cos(t)) if G.axis_dev(th[i]) > 1e-6 else None,
                    'eq_torque': float(eq_t), 'eq_force': float(np.abs(eq_f).max()),
                    'contacts': d['contacts']})
    out['squares'] = per
    # per corner, in the corner frame
    corners = {}
    for cn in G.CORNER_NAMES:
        M, t_, det = G.corner_frame(cn, s)
        sett = G.settled(z, cn)
        meet = G.corner_meeters(z, cn)
        ent = {'settled': sett, 'meeters': meet, 'det': det, 'members': []}
        T = 0.0
        for i in meet:
            tf = (th[i] if det == 1 else -th[i]) % PI2
            chi = 1 if tf < math.pi / 4 else -1
            wall_names = [w for w, v in sq[i]['W'].items() if v > 1e-12]
            m = {'i': i, 'tilt_frame_deg': math.degrees(tf), 'chi': chi if G.axis_dev(th[i]) > 1e-6 else 0,
                 'walls': wall_names, 'W': sum(sq[i]['W'].values()),
                 'tau_wall_frame': det * sq[i]['tau_wall'], 'tau_hold_frame': det * sq[i]['tau_contact'],
                 'tau_bound_frame': det * sq[i]['tau_bound']}
            T += m['tau_wall_frame']
            ent['members'].append(m)
        ent['T_corner'] = T
        # LP range of T_corner over the polytope
        w = np.zeros(len(rows))
        for k, r in enumerate(rows):
            if r['kind'] == 'wall' and r['i'] in meet:
                p = q[r['i'], r['corner']]
                w[k] = det * cross(p - np.array([cx[r['i']], cy[r['i']]]), np.array(WALL_N[r['wall']]))
        ent['T_corner_range'] = lp_range(A, w, lam0) if len(rows) else [0, 0]
        corners[cn] = ent
    out['corners'] = corners
    return out
