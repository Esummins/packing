"""A90 / T3 task 4 -- the BLIND obstruction hunt (the FJ form of NOCRIT).

Lemma BLIND (theory): moving squares that carry NO positive multiplier in an FJ
certificate, keeping the packing at the same side, preserves the FJ certificate.

So: at each certified k0 FJ point compute
  * the LOADABLE rows  (lambda_k > 0 in SOME FJ certificate: per-row LP
    max lambda_k  s.t.  A_n^T lambda = e_s, lambda >= 0),
  * the UNLOADABLE squares (no loadable row touches them) -- these are the
    squares Lemma BLIND lets us move,
  * the corner occupancy n_block (k0dir87 float test, depth > 1e-9),
and then try to REPOSITION only the unloadable squares, with every loaded square
and the tight bounding box frozen, so that all four corner slots get >= 2
intruders (i.e. the point becomes K0-BLOCKED while staying an FJ point).

A success would be a K0-BLOCKED FJ point = the explicit obstruction to NOCRIT.

Usage: python task4_90.py [n_points] [restarts]
"""
from __future__ import annotations

import os
import sys

for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
           'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ[_v] = '1'

import json
import math
import random
import time
from fractions import Fraction

import numpy as np
from scipy.optimize import linprog, minimize

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import t3_90 as G                                  # noqa: E402
from t3_90 import A87, RESULTS, LOGS, CORNERS, N   # noqa: E402
import fjpolish87 as F                             # noqa: E402
import k0dir87 as KD                               # noqa: E402
import t3lib as T                                  # noqa: E402

LAM_UB = 1e3
LOAD_TOL = 1e-9
DTARGET = 3e-3          # intrusion depth aimed for at a deficient corner
GAPMIN = 1e-7           # required pair separation of a repositioned square


# --------------------------------------------------------------- loadable set

def loadable_rows(A):
    """Rows that carry lambda_k > 0 in SOME FJ certificate (per-row LP)."""
    m = A.shape[0]
    nrm = np.linalg.norm(A, axis=1)
    nrm[nrm == 0] = 1.0
    An = A / nrm[:, None]
    b = np.zeros(T.NV)
    b[33] = 1.0
    out = np.zeros(m)
    feasible = True
    for k in range(m):
        c = np.zeros(m)
        c[k] = -1.0
        r = linprog(c, A_eq=An.T, b_eq=b, bounds=[(0, LAM_UB)] * m, method='highs')
        if not r.success:
            feasible = False
            break
        out[k] = -r.fun
    return out, feasible


def touched(rows, k):
    r = rows[k]
    return {r['i']} if r['kind'] == 'wall' else {r['o'], r['p']}


# ------------------------------------------------------------- repositioning

def build_pose(zfix, free, u):
    z = np.asarray(zfix, float).copy()
    for t, i in enumerate(free):
        z[3 * i:3 * i + 3] = u[3 * t:3 * t + 3]
    return z


_E = np.arange(4) * G.HALFPI


def all_gaps(C, TH):
    """Vectorised 11x11 matrix of SAT pair gaps (>= 0 <=> interior-disjoint)."""
    n = len(TH)
    ang = TH[:, None] + _E[None, :]                 # (n, 4) edge normal angles
    Nn = np.stack([np.cos(ang), np.sin(ang)], axis=2)       # (n, 4, 2)
    Q = np.empty((n, 4, 2))
    for i in range(n):
        Q[i] = G.verts(C[i], TH[i])
    # proj[o, e, p, k] = Q[p, k] . Nn[o, e]
    proj = np.einsum('oej,pkj->oepk', Nn, Q)
    cn = np.einsum('oej,oj->oe', Nn, C)             # (n, 4)
    M = proj.min(axis=3) - cn[:, :, None] - 0.5     # (n, 4, n)
    G1 = M.max(axis=1)                              # (o, p)
    return np.maximum(G1, G1.T)


def penalty(u, zfix, free, bbox, assign):
    z = build_pose(zfix, free, u)
    C, TH, _s = G.unpack_z(z)
    V = G.all_verts(C, TH)
    xlo, xhi, ylo, yhi = bbox
    p = 0.0
    fr_idx = np.array(free, int)
    qf = V[fr_idx]
    p += float(np.sum(np.maximum(0.0, xlo - qf[:, :, 0]) ** 2)
               + np.sum(np.maximum(0.0, qf[:, :, 0] - xhi) ** 2)
               + np.sum(np.maximum(0.0, ylo - qf[:, :, 1]) ** 2)
               + np.sum(np.maximum(0.0, qf[:, :, 1] - yhi) ** 2))
    Gm = all_gaps(C, TH)
    mask = np.zeros((N, N), bool)
    mask[fr_idx, :] = True
    mask[:, fr_idx] = True
    np.fill_diagonal(mask, False)
    viol = np.maximum(0.0, GAPMIN - Gm[mask])
    p += 20.0 * float(np.sum(viol ** 2))            # each pair counted twice
    for (cn, i) in assign:
        fr = G.frame(bbox, cn)
        d, _f, _A = G.depth_arg(V[i], fr)
        if d < DTARGET:
            p += 10.0 * (DTARGET - d) ** 2
    return p


def try_reposition(z, free, bbox, deficient, rng, restarts=40):
    """Random restarts + penalty minimisation over the free squares' poses.

    When there are fewer unloadable squares than deficient corners the best that
    can be attempted is to fill min(|U|, D) of them; the run then measures how
    close the point gets (which corner is left behind, and why)."""
    xlo, xhi, ylo, yhi = bbox
    best = None
    k = min(len(free), len(deficient))
    if k == 0:
        return None
    for _r in range(restarts):
        pick = rng.sample(list(free), k)
        cs = rng.sample(list(deficient), k)
        assign = list(zip(cs, pick))
        u = []
        for i in free:
            if i in pick:
                cn = [c for c, k in assign if k == i][0]
                fr = G.frame(bbox, cn)
                ox, oy, sx, sy = fr
                a = rng.uniform(0.15, 0.85)
                b = rng.uniform(0.15, 0.85)
                cx = ox + sx * a
                cy = oy + sy * b
                th = rng.uniform(0.0, G.HALFPI)
                u += [cx, cy, th]
            else:
                u += list(z[3 * i:3 * i + 3])
        u = np.array(u, float)
        r = minimize(penalty, u, args=(z, free, bbox, assign), method='Powell',
                     options=dict(maxiter=30, maxfev=2000, xtol=1e-8, ftol=1e-11))
        val = float(r.fun)
        ev = evaluate(z, z, free, r.x, bbox)
        clean = (ev['overlap'] <= 1e-9 and ev['container'] <= 1e-9
                 and not ev['bbox_grew'])
        key = (ev['min_n_block'] if clean else -1, sum(ev['n_block']), -val)
        if best is None or key > best[0]:
            best = (key, val, r.x.copy(), assign, ev)
        if clean and ev['min_n_block'] >= 2:
            break
    return best


def evaluate(z, zfix, free, u, bbox):
    """Float verdict on a repositioned configuration."""
    zz = build_pose(zfix, free, u) if u is not None else np.asarray(zfix, float)
    C, TH, s = G.unpack_z(zz)
    bb = G.tight_bbox_of(C, TH)
    cst = G.corner_state(C, TH, bb)
    nb = [cst[c]['n_block'] for c in CORNERS]
    x = KD.z_to_x(zz)
    ov, cv = KD.feas(x)
    return {'z': zz, 'n_block': nb, 'min_n_block': int(min(nb)),
            'overlap': float(ov), 'container': float(cv),
            'sigma': float(F.enclosing_side(zz)),
            'bbox_grew': bool(bb[1] - bb[0] > bbox[1] - bbox[0] + 1e-12
                              or bb[3] - bb[2] > bbox[3] - bbox[2] + 1e-12)}


# ------------------------------------------------------------------- driver

def main():
    npts = int(sys.argv[1]) if len(sys.argv) > 1 else 10 ** 9
    restarts = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    t0 = time.time()
    rows_in = [json.loads(l) for l in
               open(os.path.join(A87, 'results', 'cp87_fj_polished.jsonl'))
               if l.strip()]
    pts = [r for r in rows_in if r.get('survivor_tight') and r.get('z_polished')]
    print('certified k0 FJ points with a stored z: %d' % len(pts), flush=True)
    # the 17 FJ endpoints of k0dir87.polish.jsonl store z_polished only when the
    # point came out exactly K0-BLOCKED, so their configurations are NOT on disk
    pol = [json.loads(l) for l in
           open(os.path.join(A87, 'results', 'k0dir87.polish.jsonl')) if l.strip()]
    n_fj_pol = sum(1 for r in pol if r.get('fj_at_tight_tol'))
    n_fj_pol_z = sum(1 for r in pol if r.get('fj_at_tight_tol') and r.get('z_polished'))
    print('k0dir87.polish.jsonl FJ endpoints: %d, of which with a stored z: %d'
          % (n_fj_pol, n_fj_pol_z), flush=True)

    out = []
    rng = random.Random(90903)
    successes = []
    for idx, r in enumerate(pts[:npts]):
        z = np.array([float(Fraction(v)) for v in r['z_polished']])
        C, TH, s = G.unpack_z(z)
        bbox = G.tight_bbox_of(C, TH)
        cst = G.corner_state(C, TH, bbox)
        nb = [cst[c]['n_block'] for c in CORNERS]
        rows, info = F.classify(z, 1e-6)
        ent = {'tag': r['tag'], 'sigma': r['sigma_polished'], 'n_block': nb,
               'min_n_block': int(min(nb))}
        if not rows:
            ent['error'] = 'no active rows'
            out.append(ent)
            continue
        A = F.gradA(z, rows)
        lam_max, feas = loadable_rows(A)
        load = [k for k in range(len(rows)) if lam_max[k] > LOAD_TOL]
        loaded_sq = set()
        for k in load:
            loaded_sq |= touched(rows, k)
        free = sorted(set(range(N)) - loaded_sq)
        deficient = [CORNERS[k] for k in range(4) if nb[k] < 2]
        ent.update({'m_rows': len(rows), 'lp_feasible': feas,
                    'n_loadable_rows': len(load),
                    'loaded_squares': sorted(int(v) for v in loaded_sq),
                    'unloadable_squares': [int(v) for v in free],
                    'n_unloadable': len(free),
                    'deficient_corners': deficient,
                    'n_deficient': len(deficient),
                    'free_area': float(s * s - N),
                    'sigma_bbox': float(max(bbox[1] - bbox[0], bbox[3] - bbox[2])),
                    'countable': bool(len(free) >= len(deficient))})
        res = try_reposition(z, free, bbox, deficient, rng, restarts) \
            if (free and deficient) else None
        if res is not None:
            _key, val, u, assign, ev = res
            ent['penalty'] = float(val)
            ent['assignment'] = [[c, int(i)] for c, i in assign] if assign else None
            ent['best_n_block'] = ev['n_block']
            ent['best_min_n_block'] = ev['min_n_block']
            ent['best_overlap'] = ev['overlap']
            ent['best_container'] = ev['container']
            ent['best_sigma'] = ev['sigma']
            ent['bbox_grew'] = ev['bbox_grew']
            ok = (ev['min_n_block'] >= 2 and ev['overlap'] <= 1e-9
                  and ev['container'] <= 1e-9 and not ev['bbox_grew'])
            ent['float_success'] = bool(ok)
            ent['n_corners_ge2'] = int(sum(1 for v in ev['n_block'] if v >= 2))
            if ok:
                successes.append((r['tag'], ev['z'], rows, load, lam_max))
        else:
            ent['best_n_block'] = nb
            ent['best_min_n_block'] = int(min(nb))
            ent['float_success'] = False
            ent['n_corners_ge2'] = int(sum(1 for v in nb if v >= 2))
        out.append(ent)
        if (idx + 1) % 10 == 0:
            print('  %3d/%d  %.0fs  successes %d'
                  % (idx + 1, min(npts, len(pts)), time.time() - t0,
                     len(successes)), flush=True)
    json.dump(out, open(os.path.join(RESULTS, 't4_blind.json'), 'w'), indent=1)

    # ------------------------------------------------------------- summary
    done = [e for e in out if 'n_unloadable' in e]
    print()
    print('points analysed              : %d' % len(done))
    import collections
    print('n_unloadable histogram       : %s' % dict(sorted(
        collections.Counter(e['n_unloadable'] for e in done).items())))
    print('n_deficient histogram        : %s' % dict(sorted(
        collections.Counter(e['n_deficient'] for e in done).items())))
    print('n_block min histogram (orig) : %s' % dict(sorted(
        collections.Counter(e['min_n_block'] for e in done).items())))
    print('countable (|U| >= D)         : %d/%d' % (
        sum(1 for e in done if e['countable']), len(done)))
    print('best min_n_block histogram   : %s' % dict(sorted(
        collections.Counter(e.get('best_min_n_block', e['min_n_block'])
                            for e in done).items())))
    print('n corners reaching >= 2      : %s' % dict(sorted(
        collections.Counter(e.get('n_corners_ge2', 0) for e in done).items())))
    print('all four corners >= 2        : %d' % sum(
        1 for e in done if e.get('best_min_n_block', 0) >= 2))
    print('float successes              : %d' % sum(
        1 for e in done if e.get('float_success')))
    print('free area sigma^2 - 11       : min %.4f median %.4f max %.4f' % tuple(
        np.quantile([e['free_area'] for e in done], [0, .5, 1])))
    print('secs %.0f' % (time.time() - t0))

    # ---------------------------------------------------- exact verification
    for tag, zz, rows, load, lam_max in successes:
        zf = [Fraction(float(v)).limit_denominator(10 ** 15) for v in zz]
        tel = KD.exact_blocked_test(zf)
        ver = F.verify_exact(zf)
        v = F.verdict(zz, tag + ':blind')
        rec = {'tag': tag, 'z': [T.frac_str(q) for q in zf],
               'exact_n_block': tel['n_block_certified'],
               'exact_K0_BLOCKED': tel['K0_BLOCKED_certified'],
               'verify': ver, 'fj_at_tight_tol': v['fj_at_tight_tol'],
               'cone_residual': v['ladder'][0].get('cone_residual')}
        p = os.path.join(RESULTS, 'blind_obstruction_%s.json' % tag)
        json.dump(rec, open(p, 'w'), indent=1)
        print('SUCCESS %s -> %s  exact n_block %s  K0_BLOCKED %s  FJ %s'
              % (tag, p, tel['n_block_certified'],
                 tel['K0_BLOCKED_certified'], v['fj_at_tight_tol']), flush=True)
    if not successes:
        print('NO SUCCESS: no FJ point could be repositioned into K0-BLOCKED.')


if __name__ == '__main__':
    main()
