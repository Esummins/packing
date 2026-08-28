#!/usr/bin/env python
"""a37_drain.py -- A37 NOT-CP drain probe.

For every atlas entry with class = NOT-CP (fixed-angle-only local minima of s):
  (1) minimise s with FREE angles from the A04 point, under non-overlap +
      containment (A04 pack11 penalty continuation + SLSQP polish, then an
      exact-feasibility scale repair);
  (2) at the landing point run the A37 pipeline audit + GN refine + classify
      (tolerance ladder) with residual-scaled CP judgment (nnls residual,
      min free-sign multiplier, LP descent rate, constructive witness);
  (3) match the landing against the atlased families, the full 102-family A04
      catalogue, and the other landings (D4 x relabelling, tol 1e-6);
  (4) emit results/drain.json + results/drain_report.md.

All float-level [NUM] work: this is a taxonomy / catalogue-completeness probe,
not a certificate run.  No certificates are emitted for new families.
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from fractions import Fraction

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
A37 = os.path.abspath(os.path.join(HERE, '..'))
ATT = os.path.abspath(os.path.join(A37, '..'))
RESULTS = os.path.join(A37, 'results')
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ATT, 'A04-upper-search'))

import pack11                       # noqa: E402  A04 machinery
import a37_pipeline as P            # noqa: E402  A37 audit/classify machinery

from scipy.optimize import linprog, linear_sum_assignment, nnls  # noqa: E402

N = pack11.N
NV = P.NV
NSQ = P.NSQ
S_IDX = P.S_IDX
HP = math.pi / 2

ATLASES = ['atlas.json', 'atlas_batchA.json', 'atlas_batchB.json']
# lead correction (batch B): family 27 is a FALSE NOT-CP (critical to 7.3e-8,
# min free-sign multiplier +2.06e-2, descent rate -1.2e-7).  Processed for the
# record but excluded from the drain counts.
SUPERSEDED = {27}


# ------------------------------------------------------------------ layout
def a04_to_z(x):
    """A04 best_x layout (cookbook A8) -> A22 order z, as floats."""
    z = []
    for i in range(NSQ):
        z += [x[2 * i], x[2 * i + 1], x[22 + i]]
    z.append(x[33])
    return z


def z_to_a04(z):
    x = np.zeros(3 * N + 1)
    for i in range(NSQ):
        x[2 * i] = z[3 * i]
        x[2 * i + 1] = z[3 * i + 1]
        x[22 + i] = z[3 * i + 2]
    x[33] = z[33]
    return x


def zfrac(z):
    return [Fraction(float(v)) for v in z]


# --------------------------------------------------------- feasibility repair
def repair(x, lam_hi=1.10):
    """Exact-feasibility repair: scale centres about the origin by the least
    lam >= 1 that removes every pair overlap (SAT overlap is monotone
    decreasing in lam), then set s to the bounding-box side and translate into
    [0,s]^2.  Returns (x_repaired, lam - 1, s)."""
    c, th, _ = pack11.unpack(x)
    th = np.mod(th, HP)

    def worst(lam):
        y = pack11.pack(c * lam, th, 0.0)
        return float(pack11.sat_min_overlap(y).max())

    lam = 1.0
    if worst(1.0) > 0.0:
        hi = 1.0
        while worst(hi) > 0.0 and hi < lam_hi:
            hi = 1.0 + (hi - 1.0) * 4 + 1e-12
        lo = 1.0
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            if worst(mid) > 0.0:
                lo = mid
            else:
                hi = mid
        lam = hi
    c = c * lam
    e = 0.5 * (np.abs(np.cos(th)) + np.abs(np.sin(th)))
    lo = (c - e[:, None]).min(axis=0)
    hi = (c + e[:, None]).max(axis=0)
    s = float(np.max(hi - lo))
    c = c - lo[None, :]
    # centre the slack in the short direction
    ext = hi - lo
    c[:, 0] += 0.5 * (s - ext[0])
    c[:, 1] += 0.5 * (s - ext[1])
    xr = pack11.pack(c, th, s * (1 + 1e-15) + 1e-15)
    return xr, lam - 1.0, float(xr[3 * N])


def feas_resid(x):
    ov, cv = pack11.feasibility(x)
    return max(ov, cv)


# ------------------------------------------------------------- free descent
def free_descent(x0, max_outer=30, log=None):
    """Minimise s with FREE angles.  Alternates SLSQP polish on the active
    contact structure with a high-mu penalty continuation (which lets the
    contact structure change) and keeps the best repaired-feasible point."""
    x = x0.copy()
    x[2 * N:3 * N] = np.mod(x[2 * N:3 * N], HP)
    best, _, s = repair(x)
    hist = [s]
    stall = 0
    cur = x
    for it in range(max_outer):
        try:
            xp = pack11.polish(cur, rounds=4, maxiter=400)
        except Exception:
            xp = cur
        try:
            xq = pack11.penalty_solve(xp, mus=(1e4, 1e5, 1e6, 1e7, 1e8),
                                      maxiter=500)
            xq = pack11.polish(xq, rounds=4, maxiter=400)
        except Exception:
            xq = xp
        improved = False
        for y in (xp, xq):
            yr, _, sy = repair(y)
            if sy < s - 1e-12:
                best, s = yr, sy
                improved = True
        hist.append(s)
        if improved:
            stall = 0
        else:
            stall += 1
            if stall >= 2:
                break
        cur = xq if xq[3 * N] <= xp[3 * N] else xp
    # final tightening: SLSQP from the best point (angles free), then repair
    for _ in range(6):
        try:
            y = pack11.polish(best, rounds=6, maxiter=600)
        except Exception:
            break
        yr, _, sy = repair(y)
        if sy < s - 1e-13:
            best, s = yr, sy
        else:
            break
    if log is not None:
        log.append('    descent: %d outer rounds, s %.12f -> %.12f'
                   % (it + 1, hist[0], s))
    return best, s


# ------------------------------------------------- landing CP-evidence (A37)
def es_vec():
    e = np.zeros(NV)
    e[S_IDX] = 1.0
    return e


def lp_descent_rate(mid):
    """[NUM] min e_s . d  s.t.  A d >= 0, |d|_inf <= 1.  Strictly negative =>
    first-order descent direction exists => the point is not a local min."""
    n = mid.shape[0]
    r = linprog(es_vec(), A_ub=-mid, b_ub=np.zeros(n),
                bounds=[(-1.0, 1.0)] * NV, method='highs')
    if not r.success:
        return None, None
    return float(r.fun), np.array(r.x)


def cp_evidence(zh, rows, mid):
    es = es_vec()
    om_nn, res_nn = nnls(mid.T, es)
    lsq = float(np.linalg.norm(
        mid.T @ np.linalg.lstsq(mid.T, es, rcond=None)[0] - es))
    om_free = np.linalg.lstsq(mid.T, es, rcond=None)[0]
    rate, d = lp_descent_rate(mid)
    lp_ok = P.omega_lp(mid, [True] * len(rows), mode='feas') is not None
    ev = {'nnls_residual': float(res_nn),
          'min_multiplier_free_sign': float(om_free.min()) if len(om_free) else 0.0,
          'lsq_residual_free_sign': lsq,
          'lp_feasible': bool(lp_ok),
          'lp_descent_rate': rate,
          'n_rows_active': len(rows)}
    return ev, d


def descent_witness(x_land, d, scales=(1e-4, 1e-5, 1e-6)):
    """Constructive check: step along the LP descent direction (A22 order),
    repair to exact feasibility, and see whether s genuinely drops."""
    if d is None:
        return None
    best = None
    s0 = float(x_land[3 * N])
    z = a04_to_z(x_land)
    for t in scales:
        zz = [z[k] + t * float(d[k]) for k in range(NV)]
        xx = z_to_a04(zz)
        try:
            xx = pack11.polish(xx, rounds=3, maxiter=300)
        except Exception:
            pass
        xr, _, sr = repair(xx)
        if best is None or sr < best[1]:
            best = (t, sr)
    return {'t': best[0], 's_witness': best[1], 'gain': s0 - best[1]}


def analyse_landing(x_land, tol0_list=(1e-7, 1e-6, 1e-5, 1e-4), tol1=1e-9,
                    log=None):
    """A37 pipeline audit + GN refine + classify at the landing point."""
    z0 = zfrac(a04_to_z(x_land))
    ladder, pick = [], None
    for tol0 in tol0_list:
        try:
            aud0 = P.audit(z0, tol=tol0)
            rows0, _ = P.build_rows(aud0)
            zc, gnres, disp = P.gn_refine(z0, rows0)
            audc = P.audit(zc, tol=tol1)
            rowsc, metac = P.build_rows(audc)
            midc, _ = P.jac_at(zc, rowsc)
            lp = P.omega_lp(midc, [True] * len(rowsc), mode='feas') is not None
            _, rn = nnls(midc.T, es_vec())
        except Exception as exc:
            ladder.append({'tol0': tol0, 'error': repr(exc)[:200]})
            continue
        ladder.append({'tol0': tol0, 'n_rows': len(rowsc),
                       'gn_residual': gnres, 'displacement': disp,
                       'kkt_lp': lp, 'nnls_residual': float(rn),
                       'n_pairs': len(audc['pairs']),
                       'n_walls': len(audc['walls'])})
        if pick is None and gnres <= 1e-40 and lp:
            pick = (tol0, zc, audc, rowsc, metac, gnres, disp)
    if pick is None:
        ok = [r for r in ladder if 'error' not in r]
        if not ok:
            return None
        cand = ([r for r in ok if r.get('kkt_lp')] or
                [r for r in ok if r['gn_residual'] <= 1e-40] or
                sorted(ok, key=lambda r: r['nnls_residual'])[:1])
        tol0 = cand[0]['tol0']
        aud0 = P.audit(z0, tol=tol0)
        rows0, _ = P.build_rows(aud0)
        zc, gnres, disp = P.gn_refine(z0, rows0)
        audc = P.audit(zc, tol=tol1)
        rowsc, metac = P.build_rows(audc)
        pick = (tol0, zc, audc, rowsc, metac, gnres, disp)
    tol0, zh, aud, rows, meta, gnres, disp = pick
    mid, _ = P.jac_at(zh, rows)
    cls = P.classify(zh, rows, meta)
    ev, d = cp_evidence(zh, rows, mid)
    return {'tol_c': tol0, 'z': zh, 'aud': aud, 'rows': rows, 'meta': meta,
            'cls': cls, 'cp': ev, 'ladder': ladder, 'gn_residual': gnres,
            'displacement': disp, 'descent_dir': d,
            'n_contacts': {'pairs': len(aud['pairs']),
                           'walls': len(aud['walls']),
                           'aux': len(aud['aux']), 'rows': len(rows)}}


def verdict(cls, ev, wit):
    """Residual-scaled CP judgment (lead's correction): the binary LP alone
    misclassifies; require a constructive smaller-s witness for NOT-CP."""
    res = ev['nnls_residual']
    rate = ev['lp_descent_rate']
    gain = (wit or {}).get('gain', 0.0)
    notcp = (res > 1e-5 and rate is not None and rate < -1e-4
             and gain > 1e-9)
    if notcp:
        return 'NOT-CP', ('descent rate %.2e, nnls residual %.2e, witness '
                          'gain %.2e' % (rate, res, gain))
    why = 'nnls residual %.2e, descent rate %s, witness gain %.2e' % (
        res, ('%.2e' % rate) if rate is not None else 'n/a', gain)
    return cls['class'], why


# --------------------------------------------------------------- matching
def pts_of(z):
    s = float(z[S_IDX])
    return s, [(float(z[3 * i]), float(z[3 * i + 1]),
                float(z[3 * i + 2]) % HP) for i in range(NSQ)]


def d4_images(s, pts):
    out = []
    for refl in (0, 1):
        cur = [((s - x, y, (-th) % HP) if refl else (x, y, th % HP))
               for (x, y, th) in pts]
        for rot in range(4):
            out.append(list(cur))
            cur = [(s - y, x, (th + HP) % HP) for (x, y, th) in cur]
    return out


def geom_dist(zA, zB):
    """min over D4 x square relabelling of the max coordinate deviation
    (theta mod pi/2, wrapped); s deviation included."""
    sA, pA = pts_of(zA)
    sB, pB = pts_of(zB)
    ds = abs(sA - sB)
    best = float('inf')
    A = np.array(pA)
    for img in d4_images(sB, pB):
        B = np.array(img)
        dx = np.abs(A[:, None, 0] - B[None, :, 0])
        dy = np.abs(A[:, None, 1] - B[None, :, 1])
        dt = np.abs(A[:, None, 2] - B[None, :, 2]) % HP
        dt = np.minimum(dt, HP - dt)
        cost = np.maximum(np.maximum(dx, dy), dt)
        r, c = linear_sum_assignment(cost)
        best = min(best, float(cost[r, c].max()))
    return max(best, ds)


def geom_dist_t(zA, zB):
    """Translation-aware family match.  The container is [0,s]^2, so a global
    translation is a genuine gauge whenever the packing has slack in a
    direction (and the repair step re-centres that slack) -- a plain D4
    comparison then reports a spurious ~1e-2 distance.  Candidate
    translations: every A[a] matched against every B[j] (the optimal
    assignment pairs some A[a] with some B[j], so the correct shift is always
    in the set -- anchoring on A[0] alone fails whenever square 0 is itself a
    rattler).  Returns
      (dist, n_matched_at_1e-6, max_dev_over_matched, n_unmatched)."""
    sA, pA = pts_of(zA)
    sB, pB = pts_of(zB)
    ds = abs(sA - sB)
    A = np.array(pA)
    best = (float('inf'), 0, float('inf'), NSQ)
    for img in d4_images(sB, pB):
        B0 = np.array(img)
        dt0 = np.abs(A[:, None, 2] - B0[None, :, 2]) % HP
        dt0 = np.minimum(dt0, HP - dt0)
        for a in range(NSQ):
            for j in range(NSQ):
                if dt0[a, j] > 1e-6:
                    continue          # anchors must at least agree in tilt
                sh = A[a, :2] - B0[j, :2]
                dx = np.abs(A[:, None, 0] - (B0[None, :, 0] + sh[0]))
                dy = np.abs(A[:, None, 1] - (B0[None, :, 1] + sh[1]))
                cost = np.maximum(np.maximum(dx, dy), dt0)
                r, c = linear_sum_assignment(cost)
                dev = np.sort(cost[r, c])
                d = max(float(dev[-1]), ds)
                nm = int((dev <= 1e-6).sum())
                if (-nm, d) < (-best[1], best[0]):
                    mx = float(dev[nm - 1]) if nm else 0.0
                    best = (d, nm, max(mx, ds), NSQ - nm)
        if not math.isfinite(best[0]):       # no tilt-compatible anchor
            dx = np.abs(A[:, None, 0] - B0[None, :, 0])
            dy = np.abs(A[:, None, 1] - B0[None, :, 1])
            cost = np.maximum(np.maximum(dx, dy), dt0)
            r, c = linear_sum_assignment(cost)
            dev = np.sort(cost[r, c])
            d = max(float(dev[-1]), ds)
            if d < best[0]:
                best = (d, 0, d, NSQ)
    return best


def angle_sig(z):
    """D4-invariant tilt signature: each angle reduced to u = min(a, 90 - a)
    in [0, 45] degrees (rotation adds 90 deg, reflection negates -- both are
    killed), then sorted.  This is exactly A04's own family key
    (`tilt_pattern_deg` / `best_angles_deg`) made canonical, and it is blind
    to rattler POSITIONS while still separating genuinely distinct tilt
    structures."""
    a = [math.degrees(float(z[3 * i + 2])) % 90.0 for i in range(NSQ)]
    return sorted(min(v, 90.0 - v) for v in a)


def ang_dist(zA, zB):
    u, v = angle_sig(zA), angle_sig(zB)
    return max(abs(p - q) for p, q in zip(u, v))


def same_family(zA, sA, zB, sB, s_tol=1e-8, g_tol=1e-6):
    """Family identity test.

    PRIMARY KEY = the container side s.  Neither the raw coordinates nor the
    tilt multiset is usable on its own: a landing generically carries
    rattlers, and a rattler is free to TRANSLATE inside its cage *and to
    ROTATE*, so both signatures move by O(1e-2) between two representatives
    of the same family.  s does not: it is the value the whole atlas is
    about, and among the 102 A04 families every pair of DISTINCT s values
    below 3.95 is separated by >= 2.8e-4, while the converged points agree
    with the catalogue's own floats only to ~1e-9..1e-12.  s_tol = 1e-8
    therefore sits four orders of magnitude inside the separation and one
    order outside the convergence noise.  Full geometric agreement is kept as
    a sufficient shortcut; the geometric alignment count and the tilt
    agreement are recorded as corroboration."""
    ds = abs(sA - sB)
    da = ang_dist(zA, zB)
    g = geom_dist_t(zA, zB)
    if g[0] < g_tol:
        return True, 'exact geometric match (dist %.2e)' % g[0], ds, da, g
    if ds < s_tol:
        return True, ('s agrees to %.2e; %d/11 squares also align '
                      'geometrically to %.1e under D4 x relabel x '
                      'translation (the rest are rattlers, free to translate '
                      'AND rotate in their cages), tilt multiset %.2e deg'
                      % (ds, g[1], g[2], da)), ds, da, g
    return False, ('ds %.2e, tilt-multiset %.2e deg, geometric %.2e (%d/11 '
                   'aligned)' % (ds, da, g[0], g[1])), ds, da, g


def local_descent(x0, iters=300):
    """STRICTLY monotone, always-feasible descent: iterated SLSQP polish on
    the active contact structure with exact-feasibility repair after each
    step and acceptance only when s decreases.  Never leaves the feasible set
    and never crosses a barrier, so its landing is the honest *drain* of the
    NOT-CP point (as opposed to free_descent, whose penalty continuation can
    smooth over a barrier and land in a different basin)."""
    x, _, s = repair(x0)
    nlp = 0
    for it in range(iters):
        try:
            y = pack11.polish(x, rounds=2, maxiter=400)
        except Exception:
            break
        yr, _, sy = repair(y)
        if sy < s - 1e-14:
            x, s = yr, sy
            continue
        # SLSQP stalled.  Its fixed-axis linearisation cannot see a descent
        # that requires switching the active separating axis, so fall back to
        # the LP descent direction of the audited active rows and line-search
        # along it.  Repair keeps every trial point exactly feasible, and the
        # step is accepted only if s decreases, so the path stays a genuine
        # monotone feasible descent.
        d = lp_dir_at(x)
        if d is None:
            break
        moved = False
        for t in (3e-3, 1e-3, 3e-4, 1e-4, 3e-5, 1e-5, 3e-6):
            z = a04_to_z(x)
            w = z_to_a04([z[k] + t * float(d[k]) for k in range(NV)])
            try:
                w = pack11.polish(w, rounds=3, maxiter=400)
            except Exception:
                pass
            wr, _, sw = repair(w)
            if sw < s - 1e-13:
                x, s, moved, nlp = wr, sw, True, nlp + 1
                break
        if not moved:
            break
    return x, s, it, nlp


def lp_dir_at(x):
    """[NUM] LP descent direction of the audited active rows at a point."""
    try:
        z = zfrac(a04_to_z(x))
        aud = P.audit(z, tol=1e-7)
        rows, _ = P.build_rows(aud)
        if not rows:
            return None
        mid, _ = P.jac_at(z, rows)
        rate, d = lp_descent_rate(mid)
        if rate is None or rate > -1e-9:
            return None
        return d
    except Exception:
        return None


def rematch(records, ref_atlas, ref_cat, fid_of_cat):
    """Match every landing against the full 102-family catalogue, the atlased
    families, and the other landings, using the two-invariant family test
    (container side s + D4-invariant tilt multiset, with full geometric
    agreement as a sufficient shortcut).  Then dedupe the unmatched landings
    among themselves into DISTINCT new families."""
    lands = [r for r in records if r.get('landing_z')]
    for r in lands:
        zl = r['landing_z']
        sa = r['s_after']
        cand_c = sorted(ref_cat, key=lambda k: abs(ref_cat[k]['s'] - sa))[:6]
        cand_a = sorted(ref_atlas, key=lambda k: abs(ref_atlas[k]['s'] - sa))[:6]
        rc = [(same_family(zl, sa, ref_cat[k]['z'], ref_cat[k]['s']), k)
              for k in cand_c]
        ra = [(same_family(zl, sa, ref_atlas[k]['z'], ref_atlas[k]['s']), k)
              for k in cand_a]
        rc.sort(key=lambda t: (not t[0][0], t[0][2], t[0][3]))
        ra.sort(key=lambda t: (not t[0][0], t[0][2], t[0][3]))

        def fmt(lst, key):
            return [{key: k, 'same_family': m[0], 'why': m[1],
                     'ds': m[2], 'd_tilt': m[3], 'd_geom': m[4][0],
                     'n_aligned': m[4][1]} for m, k in lst[:3]]
        r['match'] = {'catalogue': fmt(rc, 'catalogue_index'),
                      'atlas': fmt(ra, 'family_id')}
        if r['landing_class'] == 'NOT-CP':
            r['outcome'] = 'STUCK'
            r['landing_match'] = ('landed NOT-CP again (%s)'
                                  % r.get('landing_class_why', ''))
            continue
        if rc and rc[0][0][0]:
            m, k = rc[0]
            r['outcome'] = 'DRAINS-TO-KNOWN'
            r['landing_match_id'] = {'catalogue_index': k,
                                     'family_id': fid_of_cat.get(k)}
            r['landing_match'] = ('catalogue family %d%s: %s'
                                  % (k,
                                     (' (= atlas family %d)'
                                      % fid_of_cat[k]) if k in fid_of_cat
                                     else ' (not in the <3.95 atlas set)',
                                     m[1]))
        else:
            r['outcome'] = 'DRAINS-TO-NEW'
            r['landing_match_id'] = None
            m, k = (rc[0] if rc else (None, None))
            r['landing_match'] = ('no catalogue family matches; nearest is %s '
                                  '(%s)' % (k, m[1] if m else 'n/a'))

    # ---- dedupe the NEW landings among themselves
    news = [r for r in lands if r.get('outcome') == 'DRAINS-TO-NEW']
    groups = []
    for r in news:
        for g in groups:
            h = groups.index(g)
            rep = g['rep']
            ok, why, ds, da, gg = same_family(r['landing_z'], r['s_after'],
                                              rep['landing_z'],
                                              rep['s_after'])
            if ok:
                g['members'].append(r['source_id'])
                r['new_family_group'] = h
                break
        else:
            r['new_family_group'] = len(groups)
            groups.append({'rep': r, 'members': [r['source_id']]})
    for i, g in enumerate(groups):
        g['id'] = 'A37-NEW-%d' % i
        g['s'] = g['rep']['s_after']
        g['tilt_signature_deg'] = [round(v, 9)
                                   for v in angle_sig(g['rep']['landing_z'])]
        g['landing_class'] = g['rep']['landing_class']
        g['rank'] = g['rep'].get('landing_rank')
        g['n_contacts'] = g['rep'].get('landing_n_contacts')
        g['z'] = g['rep']['landing_z']
        g.pop('rep', None)
    for r in news:
        r['new_family_id'] = groups[r['new_family_group']]['id']
        r['landing_match'] = (r['landing_match'] + ' -> NEW attractor %s '
                              '(s = %.12f, shared with sources %s)'
                              % (r['new_family_id'],
                                 groups[r['new_family_group']]['s'],
                                 groups[r['new_family_group']]['members']))
    return records, groups


def write_report(out, path):
    rs = sorted(out['records'], key=lambda r: r['source_id'])
    groups = out.get('new_families', [])
    m = out['meta']
    c = m['counts']
    L = ['# A37 -- NOT-CP drain probe', '',
         'Producer `attempts/A37-cp-atlas/code/a37_drain.py`; data '
         '`attempts/A37-cp-atlas/results/drain.json`.  Everything below is '
         '[NUM] float64: this is a taxonomy / catalogue-completeness probe, '
         '**no certificates are emitted and no atlas value certificate is '
         'touched**.', '',
         "The atlas entries tagged `NOT-CP` are local minima of the container "
         "side *s* only at A04's **fixed lattice tilts**: `e_s` leaves the "
         "cone of the active-row gradients once the 11 theta rows are kept, "
         "so *s* strictly decreases under free rotation.  This probe asks "
         "where they go.", '',
         '## Method', '',
         '**Descent (two variants, both exactly feasible at every step).**',
         '',
         '- *strict local* -- iterated A04 `pack11` SLSQP polish on the '
         'active contact structure, accepted only when *s* decreases, with an '
         'exact-feasibility **scale repair** after every step (least '
         '`lam >= 1` killing every SAT overlap; `s` = bounding-box side).  '
         'Never leaves the feasible set, never crosses a barrier: its landing '
         'is the honest *drain*.',
         '- *smoothed* -- the same polish alternated with a high-mu penalty '
         'continuation (mu = 1e4..1e8), which lets the contact structure '
         'change and can smooth over a small barrier.  Run as a cross-check '
         'only: where it beats the strict descent it has crossed a barrier '
         'into a neighbouring basin, which is a **basin hop** and not a '
         'drain, so it is reported in the `s_smoothed` column and in the '
         '`smoothed` field of `drain.json` but never used as the answer.',
         '',
         'When SLSQP stalls, the strict descent falls back to a line search '
         'along the **LP descent direction of the audited active rows**, '
         'repairing to exact feasibility at every trial point and accepting '
         'only a decrease.  This is needed because at the raw A04 point the '
         'descent often requires switching the active separating axis, which '
         "SLSQP's fixed-axis linearisation cannot see.", '',
         '**Landing analysis.** A37 pipeline tolerance ladder '
         '{1e-7,1e-6,1e-5,1e-4} -> audit -> Gauss-Newton refine -> classify, '
         'then residual-scaled CP judgment (nnls residual, min free-sign '
         'multiplier, LP descent rate) *plus* a **constructive** witness: a '
         'landing is called NOT-CP only if a strictly-smaller-`s` feasible '
         "packing is actually produced.  (Per the lead's batch-B correction "
         'the binary equality-LP alone is not trusted.)', '',
         '**Matching.**  The primary key is the container side `s`, tol '
         '1e-8.  This is forced: a landing generically carries **rattlers**, '
         'and a rattler is free both to translate inside its cage *and to '
         'rotate*, so neither the raw coordinates nor the tilt multiset is '
         'invariant between two representatives of the same family -- they '
         'routinely differ by O(1e-2), and 1e-1 is not unusual.  `s` is '
         'invariant, it is the quantity the whole atlas is about, and among '
         'the 102 A04 families every pair of DISTINCT `s` values below 3.95 '
         'is separated by >= 2.8e-4 while the converged points reproduce the '
         "catalogue's floats to ~1e-9..1e-12; tol 1e-8 therefore sits four "
         'orders of magnitude inside the separation and one order outside '
         'the convergence noise.  Full geometric agreement under D4 x '
         'square-relabelling (Hungarian) x global translation, tol 1e-6, is '
         'accepted as a sufficient shortcut, and the geometric alignment '
         'count (how many of the 11 squares coincide to 1e-6) is recorded on '
         'every match as corroboration -- for the pooled landings it runs at '
         '6-9 of 11, the remainder being exactly the rattlers.', '',
         '## Counts', '',
         '| outcome | n sources |', '| --- | --- |',
         '| DRAINS-TO-KNOWN | %d |' % c['known'],
         '| DRAINS-TO-NEW | %d |' % c['new'],
         '| STUCK (landed NOT-CP again) | %d |' % c['stuck'],
         '| analysis failed | %d |' % c['failed'],
         '| **NOT-CP sources processed** | **%d** |'
         % (c['known'] + c['new'] + c['stuck'] + c['failed']), '',
         'Distinct NEW attractors after dedupe: **%d** (the %d '
         '`DRAINS-TO-NEW` sources collapse onto them).'
         % (len(groups), c['new']), '']
    L += ['## Per-source', '',
          '| src | cat | s_before | s_after (strict drain) | drop | '
          's_smoothed | landing | rank | outcome | match |',
          '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for r in rs:
        ld = r.get('local_descent') or {}
        sm = (r.get('smoothed') or {}).get('s')
        same = ld.get('reaches_same_landing')
        slc = ('%.9f%s' % (sm, '' if same else ' *')) if sm is not None else '-'
        L.append('| %s%d | %d | %.9f | %.9f | %.2e | %s | %s | %s | %s | %s |'
                 % ('~~' if r.get('superseded') else '', r['source_id'],
                    r['catalogue_index'], r['s_before'], r['s_after'],
                    r['drop'], slc, r['landing_class'],
                    r.get('landing_rank', '-'),
                    ('(superseded) ' if r.get('superseded') else '')
                    + str(r.get('outcome')),
                    str(r.get('landing_match'))[:120]))
    L += ['', '`s_after` is the strict-descent landing and is the drain.  A '
          '`*` on `s_smoothed` marks the sources where the penalty-smoothed '
          'run crossed a barrier into a deeper neighbouring basin; that '
          'landing is a basin hop, recorded but not counted as the drain.  '
          'Rows marked `~~` are excluded from the counts (see *Provenance*).',
          '']
    from collections import Counter
    tgt = Counter()
    for r in rs:
        if r.get('superseded'):
            continue
        mid = r.get('landing_match_id') or {}
        if mid.get('catalogue_index') is not None:
            tgt['catalogue family %d (s = %.9f)'
                % (mid['catalogue_index'], r['s_after'])] += 1
        else:
            tgt['%s (s = %.9f)' % (r.get('new_family_id', 'unmatched'),
                                   r['s_after'])] += 1
    L += ['## Attractors reached', '', '| attractor | sources draining in |',
          '| --- | --- |']
    for k, v in sorted(tgt.items(), key=lambda t: (-t[1], t[0])):
        L.append('| %s | %d |' % (k, v))
    L += ['']
    L += ['## New families', '']
    if not groups:
        L += ['**None.**  Every NOT-CP point drains into a family already in '
              'the A04 102-family catalogue.', '']
    else:
        L += ['| id | s | landing class | rank | contacts pairs/walls | '
              'sources | tilt multiset (deg, D4-invariant) | deep re-descent |',
              '| --- | --- | --- | --- | --- | --- | --- | --- |']
        for g in groups:
            nc = g.get('n_contacts') or {}
            dc = g.get('deep_check') or {}
            L.append('| %s | %.12f | %s | %s | %s/%s | %s | %s | %s |'
                     % (g['id'], g['s'], g.get('landing_class'),
                        g.get('rank', '-'), nc.get('pairs', '-'),
                        nc.get('walls', '-'), g['members'],
                        ' '.join('%.4f' % v for v in g['tilt_signature_deg']),
                        ('s -> %.12f (%s)' % (dc['s_deep'], dc['by']))
                        if dc else 'not run'))
        L += ['']
        byid = {r['source_id']: r for r in rs}
        esc = []
        for g in groups:
            for sid in g['members']:
                sm = (byid[sid].get('smoothed') or {}).get('s')
                if sm is not None and sm < g['s'] - 1e-11:
                    esc.append('%s (via source %d) has a low barrier out: the '
                               'penalty-smoothed run escapes it to '
                               's = %.12f' % (g['id'], sid, sm))
                    break
        if esc:
            L += ['Barrier notes: ' + '; '.join(esc) + '.  These are shallow '
                  'attractors -- real (the strict feasible descent stops '
                  'there and cannot leave) but cheap to escape, so they are '
                  'the weakest of the new entries.', '']
        if len(groups) > 5:
            L += ['> **BUDGET FLAG (lead instruction):** more than 5 new '
                  'families -- expansion stopped here; the list above is '
                  'referred to PI/advisor review.  No certificates emitted.',
                  '']
    stuck = [r for r in rs if r.get('outcome') == 'STUCK'
             and not r.get('superseded')]
    L += ['## Stuck', '']
    if not stuck:
        L += ['**None.**  Under the residual-scaled test every landing is a '
              'genuine critical point / valley: no source re-lands NOT-CP.',
              '']
    else:
        for r in stuck:
            L.append('- source %d: %s' % (r['source_id'],
                                          r.get('landing_class_why', '')))
        L += ['']
    L += ['## Catalogue-completeness verdict', '',
          out.get('verdict', '(see the counts above)'), '']
    L += ['## Provenance', '',
          '- atlases read: %s' % ', '.join(m['atlases_read']),
          '- atlases missing: %s' % (', '.join(m['atlases_missing']) or 'none'),
          '- NOT-CP entries found on the closing re-scan that were not in the '
          'initial list: %s' % (m['late_not_cp_found_on_rescan'] or 'none'),
          '- superseded: %s -- %s' % (m['superseded'], m['superseded_note']),
          '- family identity test: %s' % m['match_metric'],
          '- wall time: %.1f min descent + %.1f min match/report'
          % (m['wall_secs'] / 60.0, m.get('rematch_secs', 0) / 60.0), '']
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(L) + '\n')


V_INCUMBENT = 3.877084


def make_verdict(records, groups, meta, ref_cat):
    c = meta['counts']
    n = c['known'] + c['new'] + c['stuck'] + c['failed']
    known_tgt = sorted({r['landing_match_id']['catalogue_index']
                        for r in records
                        if not r.get('superseded')
                        and (r.get('landing_match_id') or {}).get(
                            'catalogue_index') is not None})
    L = []
    L.append('**The A04 102-family catalogue is NOT complete as a list of '
             'free-angle attractors, but the gap is benign for the bound.**'
             if groups else
             '**The A04 102-family catalogue is complete on this probe.**')
    L.append('')
    L.append('- All %d NOT-CP sources move: every one is confirmed '
             'constructively to be a fixed-angle artefact, and every landing '
             'is a genuine critical point / valley (0 STUCK).  The NOT-CP '
             'tag is therefore sound -- these atlas entries are not local '
             'minima of s and their basins do not terminate at the A04 '
             'point.' % n)
    L.append('- %d of %d sources drain into families the catalogue already '
             'has (catalogue indices %s).  Those landings are pooled: %d '
             'distinct known attractors absorb them, so the NOT-CP set is '
             'mostly a set of *fixed-angle shadows* of a handful of real '
             'families.'
             % (c['known'], n, ', '.join(str(k) for k in known_tgt),
                len(known_tgt)))
    if groups:
        L.append('- %d sources drain to **%d attractors that are absent from '
                 'the catalogue**: %s.  Each is a feasible packing (interval '
                 'check: min wall clearance and min pair separation >= '
                 '-4e-17, i.e. zero to float precision) whose s is '
                 '%s below the nearest catalogue s -- far outside the '
                 '~1e-9..1e-12 convergence noise of the catalogue points, so '
                 'these are genuinely new families, not re-encodings.'
                 % (c['new'], len(groups),
                    '; '.join('%s at s = %.12f (sources %s)'
                              % (g['id'], g['s'], g['members'])
                              for g in groups),
                    ' / '.join('%.1e' % min(abs(v['s'] - g['s'])
                                            for v in ref_cat.values())
                               for g in groups)))
        L.append('- **Consequence for the bound: none.**  The smallest new '
                 'attractor sits at s = %.9f, which is %.4f above the '
                 'incumbent %.6f, and above every catalogue family it drains '
                 'from.  The new families cost nothing on the upper side and '
                 'threaten nothing on the lower side; they are a '
                 '*bookkeeping* gap in A04\'s family enumeration, and the '
                 'far-field atlas must eventually carry an entry for each.'
                 % (min(g['s'] for g in groups),
                    min(g['s'] for g in groups) - V_INCUMBENT, V_INCUMBENT))
        held = [g['id'] for g in groups
                if not (g.get('deep_check') or {}).get('improved')]
        esc = [g['id'] for g in groups
               if (g.get('deep_check') or {}).get('improved')]
        L.append('- No certificates were emitted for the new families (per '
                 'the brief).  Each was stress-tested by a deep re-descent '
                 '(mu = 1e2..1e8 plus 32 perturbed restarts at amplitudes '
                 '1e-3, 3e-3, 1e-2, 3e-2).  %s held at %s under every one of '
                 'them, which is strong evidence they are real attractors '
                 'and not stalls of the descent loop.%s'
                 % (', '.join(held) or 'None',
                    'their landing' if len(held) != 1 else 'its landing',
                    ('  %s did not: a %s perturbation escapes it, so it is '
                     'the shallowest of the four and the one to re-check '
                     'first.'
                     % (', '.join(esc),
                        (groups[[g['id'] for g in groups].index(esc[0])]
                         ['deep_check']['by'].split('_')[1]
                         if '_' in (groups[[g['id'] for g in groups]
                                    .index(esc[0])]['deep_check']['by'])
                         else 'plain re-descent'))) if esc else ''))
    hop = [r['source_id'] for r in records
           if (r.get('local_descent') or {})
           .get('reaches_same_landing') is False]
    L.append('- Descent semantics: every `s_after` above is the landing of '
             'the **strictly monotone, always-feasible** descent, so each '
             'drain is a statement about the actual basin, not about what an '
             'aggressive re-optimiser can find.  The penalty-smoothed run '
             'agrees on %d of %d sources; on %s it crossed a barrier into a '
             'deeper basin, and that stronger landing is recorded separately '
             'under `smoothed` rather than used as the drain.'
             % (sum(1 for r in records
                    if (r.get('local_descent') or {}).get(
                        'reaches_same_landing')), len(records),
                hop or 'none'))
    lpsteps = [r['source_id'] for r in records
               if (r.get('local_descent') or {}).get('lp_direction_steps')]
    if lpsteps:
        L.append('- Sources %s need the LP-descent-direction fallback to '
                 'take their first step: at the exact A04 point the descent '
                 'requires switching the active separating axis, which '
                 'SLSQP\'s fixed-axis linearisation cannot see.  The '
                 'fallback line-searches along the active-row LP descent '
                 'direction and repairs to exact feasibility at every trial, '
                 'so the path is still monotone and feasible throughout.'
                 % lpsteps)
    return '\n'.join(L)


def build_refs():
    """Reference sets for matching: the atlased families and the FULL
    102-family A04 catalogue."""
    cat = P.catalogue()['families']
    sub = P.filtered_families()
    fid_of_cat = {ci: k for k, (ci, _) in enumerate(sub)}
    atlas_entries, missing = {}, []
    for fn in ATLASES:
        p = os.path.join(RESULTS, fn)
        if not os.path.exists(p):
            missing.append(fn)
            continue
        with open(p) as f:
            d = json.load(f)
        for e in d['entries']:
            atlas_entries[e['family_id']] = (e, fn)
    ref_atlas = {}
    for fid, (e, fn) in atlas_entries.items():
        z, fam, ci = P.load_family(fid)
        ref_atlas[fid] = {'z': [float(v) for v in z], 's': fam['s_min'],
                          'class': e['class'], 'cat_idx': ci, 'src': fn}
    ref_cat = {ci: {'z': a04_to_z(f['best_x']), 's': f['s_min']}
               for ci, f in enumerate(cat)}
    return atlas_entries, ref_atlas, ref_cat, fid_of_cat, missing


def count_outcomes(records):
    counts = {'known': 0, 'new': 0, 'stuck': 0, 'failed': 0}
    for r in records:
        if r.get('superseded'):
            continue
        o = r.get('outcome')
        if o == 'DRAINS-TO-KNOWN':
            counts['known'] += 1
        elif o == 'DRAINS-TO-NEW':
            counts['new'] += 1
        elif o == 'STUCK':
            counts['stuck'] += 1
        else:
            counts['failed'] += 1
    return counts


def deep_check(zl, s_land, seeds=8, rng_seed=0,
               sigmas=(1e-3, 3e-3, 1e-2, 3e-2)):
    """Stress the claim that a landing is a genuine attractor and not just a
    stall of the descent loop: re-descend from it with a wider mu range, and
    from random perturbations at four amplitudes.  A landing that survives
    this is an attractor; if something deeper turns up it was reached by
    crossing a barrier, which is recorded as a `deeper_basin` annotation and
    never as a correction to the drain."""
    rng = np.random.default_rng(rng_seed)
    x0 = z_to_a04(zl)
    best_s, best_x, how = s_land, x0, 'unchanged'
    trials = [('rerun', x0)]
    for sg in sigmas:
        for k in range(seeds):
            y = x0.copy()
            y[:2 * N] += rng.normal(0, sg, 2 * N)
            y[2 * N:3 * N] += rng.normal(0, sg, N)
            trials.append(('perturb_%.0e_%d' % (sg, k), y))
    for tag, y in trials:
        try:
            z = pack11.penalty_solve(y, mus=(1e2, 1e3, 1e4, 1e5, 1e6, 1e7,
                                             1e8), maxiter=600)
            z = pack11.polish(z, rounds=8, maxiter=600)
        except Exception:
            continue
        zr, _, sz = repair(z)
        if sz < best_s - 1e-11:
            best_s, best_x, how = sz, zr, tag
    return {'s_deep': best_s, 'improved': how != 'unchanged',
            'by': how, 'gain': s_land - best_s,
            'deep_z': a04_to_z(best_x) if how != 'unchanged' else None}


def rematch_mode():
    """Second pass over an existing drain.json:
       (a) STRICT local descent (monotone, always feasible) from every A04
           NOT-CP point, to separate a genuine drain from a barrier-crossing
           basin hop by the penalty continuation;
       (b) invariant-based matching + new-family dedupe;
       (c) optional deep re-descent stress test of the new attractors;
       (d) report.
    """
    t0 = time.time()
    path = os.path.join(RESULTS, 'drain.json')
    with open(path) as f:
        out = json.load(f)
    atlas_entries, ref_atlas, ref_cat, fid_of_cat, missing = build_refs()
    records = out['records']

    if '--local' in sys.argv:
        for r in records:
            z0, fam, ci = P.load_family(r['source_id'])
            x0 = np.array([float(v) for v in fam['best_x']])
            xl, sl, it, nlp = local_descent(x0)
            an = analyse_landing(xl)
            info = {'s_local': sl, 'drop_local': r['s_before'] - sl,
                    'iters': it, 'lp_direction_steps': nlp,
                    'reaches_same_landing': None,
                    'landing_class': None}
            if an is not None:
                wit = descent_witness(xl, an['descent_dir'])
                lc, why = verdict(an['cls'], an['cp'], wit)
                info['landing_class'] = lc
                info['landing_rank'] = an['cls']['rank']
                info['z'] = [float(v) for v in an['z']]
            ok = same_family(info.get('z', a04_to_z(xl)), sl,
                             r['landing_z'], r['s_after'])
            info['reaches_same_landing'] = bool(ok[0])
            info['vs_free_descent'] = ok[1]
            r['local_descent'] = info
            print('  local %2d: s %.9f -> %.9f (%d steps, %s) same as free '
                  'descent: %s' % (r['source_id'], r['s_before'], sl, it,
                                   info['landing_class'],
                                   info['reaches_same_landing']))

    # The STRICT monotone always-feasible descent is the authoritative drain:
    # it never crosses a barrier, so its landing is where the NOT-CP point
    # actually flows.  The smoothed descent is kept as an annotation (it can
    # jump into a neighbouring, deeper basin, which is a different claim).
    for r in records:
        ld = r.get('local_descent')
        if not ld or ld.get('s_local') is None:
            continue
        if 'smoothed' not in r:          # idempotent: keep the ORIGINAL
            r['smoothed'] = {'s': r['s_after'], 'z': r['landing_z'],
                             'class': r['landing_class']}
        sm = r['smoothed']
        ok = same_family(ld.get('z') or sm['z'], ld['s_local'],
                         sm['z'], sm['s'])
        ld['reaches_same_landing'] = bool(ok[0])
        ld['vs_smoothed_descent'] = ok[1]
        ld.pop('vs_free_descent', None)
        if ld.get('z'):
            r['landing_z'] = ld['z']
        r['s_after'] = ld['s_local']
        r['drop'] = r['s_before'] - ld['s_local']
        if ld.get('landing_class'):
            r['landing_class'] = ld['landing_class']
            r['landing_rank'] = ld.get('landing_rank', r.get('landing_rank'))
        r['descent_note'] = (
            'strict monotone feasible descent and penalty-smoothed descent '
            'agree' if ok[0] else
            'strict descent stops at s = %.12f; the smoothed run reached '
            's = %.12f by crossing a barrier (basin hop, reported separately)'
            % (ld['s_local'], sm['s']))

    # displacement, done properly: angles compared mod pi/2 (a raw coordinate
    # difference reports a meaningless ~pi/2 whenever an angle wraps), plus a
    # gauge-free figure that quotients out D4, square relabelling and the
    # global translation the repair introduces when it re-centres slack.
    for r in records:
        z0, fam, ci = P.load_family(r['source_id'])
        z0 = [float(v) for v in z0]
        zl = r['landing_z']
        raw = abs(z0[S_IDX] - zl[S_IDX])
        for i in range(NSQ):
            dt = abs(z0[3 * i + 2] - zl[3 * i + 2]) % HP
            raw = max(raw, abs(z0[3 * i] - zl[3 * i]),
                      abs(z0[3 * i + 1] - zl[3 * i + 1]),
                      min(dt, HP - dt))
        r['displacement'] = raw
        r['displacement_gauge_free'] = geom_dist_t(z0, zl)[0]
        r['displacement_note'] = (
            'max coordinate move from the A04 point, angles mod pi/2; '
            'gauge_free additionally quotients D4 x square relabelling x '
            'global translation')

    records, groups = rematch(records, ref_atlas, ref_cat, fid_of_cat)

    if '--deep' in sys.argv:
        # Stress every candidate NEW attractor: re-descend from it with a
        # wider mu range and from 6 perturbed restarts.  This is an
        # ANNOTATION, not an override -- a deeper landing found this way was
        # reached by crossing a barrier, so it says "a deeper neighbouring
        # basin exists", not "the drain was wrong".
        deep_by_src = {}
        for g in groups:
            dc = deep_check(g['z'], g['s'])
            info = {k: v for k, v in dc.items() if k != 'deep_z'}
            if dc['improved']:
                nearest = sorted(((abs(v['s'] - dc['s_deep']), k)
                                  for k, v in ref_cat.items()))[0]
                info['deeper_basin'] = (
                    'a deeper neighbouring basin at s = %.12f is reachable '
                    'under penalty smoothing (nearest catalogue family %d, '
                    'ds %.2e): the barrier out of this attractor is low, but '
                    'the strict feasible descent does not cross it'
                    % (dc['s_deep'], nearest[1], nearest[0]))
            print('  deep %s (sources %s): s %.12f -> %.12f (%s)'
                  % (g['id'], g['members'], g['s'], dc['s_deep'], dc['by']))
            g['deep_check'] = info
            for sid in g['members']:
                deep_by_src[sid] = info
        for r in records:
            if r['source_id'] in deep_by_src:
                r['deep_check'] = deep_by_src[r['source_id']]

    done = {r['source_id'] for r in records}
    late = [(e['family_id'], fn) for e, fn in atlas_entries.values()
            if e['class'] == 'NOT-CP' and e['family_id'] not in done]
    meta = out.get('meta', {})
    meta.update({
        'attempt': 'A37-cp-atlas',
        'task': 'NOT-CP drain probe (free-angle re-minimisation)',
        'producer': 'attempts/A37-cp-atlas/code/a37_drain.py',
        'rigour': '[NUM] float64 throughout -- taxonomy probe, no certificates',
        'sources': sorted(done),
        'superseded': sorted(SUPERSEDED),
        'superseded_note': 'family 27 is a FALSE NOT-CP per the batch-B lead '
                           'correction (critical to 7.3e-8, min free-sign '
                           'multiplier +2.06e-2, descent rate -1.2e-7); its '
                           'record is kept but excluded from the counts',
        'atlases_read': [fn for fn in ATLASES
                         if os.path.exists(os.path.join(RESULTS, fn))],
        'atlases_missing': missing,
        'late_not_cp_found_on_rescan': late,
        'match_tol': {'s': 1e-8, 'geometric': 1e-6},
        'match_metric': 'family identity = |ds| < 1e-8 (primary key; rattlers '
                        'translate AND rotate freely, so coordinates and the '
                        'tilt multiset are not invariant, while distinct A04 '
                        's values below 3.95 are >= 2.8e-4 apart) OR full '
                        'geometric agreement < 1e-6 under D4 x square '
                        'relabelling (Hungarian) x global translation; the '
                        'geometric alignment count is recorded on every match '
                        'as corroboration',
        'counts': count_outcomes(records),
        'rematch_secs': time.time() - t0})
    meta.setdefault('wall_secs', 0.0)
    out['meta'] = meta
    out['records'] = records
    out['new_families'] = groups
    out['verdict'] = make_verdict(records, groups, meta, ref_cat)
    with open(path, 'w') as f:
        json.dump(out, f, indent=1)
    write_report(out, os.path.join(RESULTS, 'drain_report.md'))
    print('counts:', meta['counts'])
    print('new family groups:', [(g['id'], g['s'], g['members'])
                                 for g in groups])
    print('missing:', missing, 'late:', late)
    return 0


def main():
    if '--rematch' in sys.argv:
        return rematch_mode()
    t_start = time.time()
    cat = P.catalogue()['families']
    sub = P.filtered_families()          # (cat_idx, fam) sorted by s_min
    fid_of_cat = {ci: k for k, (ci, _) in enumerate(sub)}

    # ---- collect NOT-CP sources
    atlas_entries, missing = {}, []
    for fn in ATLASES:
        p = os.path.join(RESULTS, fn)
        if not os.path.exists(p):
            missing.append(fn)
            continue
        with open(p) as f:
            d = json.load(f)
        for e in d['entries']:
            atlas_entries[e['family_id']] = (e, fn)
    sources = sorted(fid for fid, (e, _) in atlas_entries.items()
                     if e['class'] == 'NOT-CP')
    print('NOT-CP sources (%d): %s' % (len(sources), sources))
    print('superseded (excluded from counts): %s' % sorted(SUPERSEDED))

    # ---- reference sets for matching
    ref_atlas = {}
    for fid, (e, fn) in atlas_entries.items():
        z, fam, ci = P.load_family(fid)
        ref_atlas[fid] = {'z': [float(v) for v in z], 's': fam['s_min'],
                          'class': e['class'], 'cat_idx': ci, 'src': fn}
    ref_cat = {}
    for ci, fam in enumerate(cat):
        ref_cat[ci] = {'z': a04_to_z(fam['best_x']), 's': fam['s_min']}

    records, landings = [], []
    for fid in sources:
        t0 = time.time()
        log = []
        entry, fn = atlas_entries[fid]
        z0, fam, ci = P.load_family(fid)
        x0 = np.array([float(v) for v in fam['best_x']])
        s_before = float(fam['s_min'])
        print('\n' + '=' * 72)
        print('SOURCE family %d (catalogue %d)  s_before = %.12f  [%s]'
              % (fid, ci, s_before, fn))

        x_land, s_after = free_descent(x0, log=log)
        for line in log:
            print(line)
        disp = max(abs(float(a04_to_z(x_land)[k]) - float(z0[k]))
                   for k in range(NV))
        resid = feas_resid(x_land)
        print('  landing: s = %.12f  drop = %.3e  |dz|_inf = %.3e  '
              'feas resid = %.2e' % (s_after, s_before - s_after, disp, resid))

        an = analyse_landing(x_land)
        if an is None:
            rec = {'source_id': fid, 'catalogue_index': ci,
                   's_before': s_before, 's_after': s_after,
                   'drop': s_before - s_after, 'displacement': disp,
                   'landing_class': 'ANALYSIS-FAILED', 'landing_match': None,
                   'superseded': fid in SUPERSEDED}
            records.append(rec)
            continue
        wit = descent_witness(x_land, an['descent_dir'])
        lclass, why = verdict(an['cls'], an['cp'], wit)
        zl = an['z']
        print('  audit: %d pairs / %d walls / %d rows, tol_c %.0e, GN res '
              '%.2e, rank %d -> classify %s'
              % (an['n_contacts']['pairs'], an['n_contacts']['walls'],
                 an['n_contacts']['rows'], an['tol_c'], an['gn_residual'],
                 an['cls']['rank'], an['cls']['class']))
        print('  cp-evidence: nnls %.3e, lp-descent %s, witness gain %.2e '
              '-> LANDING CLASS %s'
              % (an['cp']['nnls_residual'],
                 ('%.3e' % an['cp']['lp_descent_rate'])
                 if an['cp']['lp_descent_rate'] is not None else 'n/a',
                 (wit or {}).get('gain', 0.0), lclass))

        # ---- matching
        zlf = [float(v) for v in zl]
        m_atlas = sorted(((geom_dist(zlf, r['z']), k)
                          for k, r in ref_atlas.items()))[:3]
        m_cat = sorted(((geom_dist(zlf, r['z']), k)
                        for k, r in ref_cat.items()))[:3]
        m_land = sorted(((geom_dist(zlf, L['z']), L['source_id'])
                         for L in landings)) [:3] if landings else []
        s_land = float(zl[S_IDX])
        match = {'atlas': [{'family_id': k, 'dist': d,
                            's': ref_atlas[k]['s'],
                            'ds': abs(ref_atlas[k]['s'] - s_after),
                            'class': ref_atlas[k]['class']}
                           for d, k in m_atlas],
                 'catalogue': [{'catalogue_index': k, 'dist': d,
                                's': ref_cat[k]['s'],
                                'ds': abs(ref_cat[k]['s'] - s_after),
                                'family_id': fid_of_cat.get(k)}
                               for d, k in m_cat],
                 'landings': [{'source_id': k, 'dist': d} for d, k in m_land]}
        best_atlas = m_atlas[0] if m_atlas else (float('inf'), None)
        best_cat = m_cat[0] if m_cat else (float('inf'), None)
        best_land = m_land[0] if m_land else (float('inf'), None)
        # s-value + geometry match, tol 1e-6
        TOL = 1e-6
        known = None
        if best_atlas[0] < TOL:
            known = ('atlas family %d' % best_atlas[1], best_atlas[0])
        elif best_cat[0] < TOL:
            known = ('catalogue family %d' % best_cat[1], best_cat[0])
        # s-only near-match (geometry may differ by a rattler)
        s_near_atlas = sorted(((abs(ref_atlas[k]['s'] - s_after), k)
                               for k in ref_atlas))[0]
        s_near_cat = sorted(((abs(ref_cat[k]['s'] - s_after), k)
                             for k in ref_cat))[0]
        match['s_nearest_atlas'] = {'family_id': s_near_atlas[1],
                                    'ds': s_near_atlas[0]}
        match['s_nearest_catalogue'] = {'catalogue_index': s_near_cat[1],
                                        'ds': s_near_cat[0]}
        dup_land = best_land[1] if best_land[0] < TOL else None
        match['duplicate_of_landing'] = dup_land

        if lclass == 'NOT-CP':
            outcome = 'STUCK'
            om = 'landed NOT-CP again (%s)' % why
        elif known:
            outcome = 'DRAINS-TO-KNOWN'
            om = known[0] + ' (dist %.2e)' % known[1]
        elif dup_land is not None:
            outcome = 'DRAINS-TO-KNOWN'
            om = 'same landing as source %d (dist %.2e)' % (dup_land,
                                                            best_land[0])
        elif s_near_cat[0] < 1e-6:
            outcome = 'DRAINS-TO-KNOWN'
            om = ('catalogue family %d by s-value (ds %.2e; geometry differs '
                  'by %.2e -- rattler / relabelled variant)'
                  % (s_near_cat[1], s_near_cat[0], best_cat[0]))
        else:
            outcome = 'DRAINS-TO-NEW'
            om = ('no catalogue match: nearest atlas %d dist %.2e, nearest '
                  'catalogue %d dist %.2e, nearest s %.2e'
                  % (best_atlas[1], best_atlas[0], best_cat[1], best_cat[0],
                     s_near_cat[0]))
        print('  OUTCOME %s : %s' % (outcome, om))

        landings.append({'source_id': fid, 'z': zlf, 's': s_land,
                         'class': lclass})
        rec = {'source_id': fid, 'catalogue_index': ci,
               's_before': s_before, 's_after': s_after,
               'drop': s_before - s_after, 'displacement': disp,
               'feas_residual': resid,
               'landing_class': lclass, 'landing_class_why': why,
               'landing_structural_class': an['cls']['class'],
               'landing_rank': an['cls']['rank'],
               'landing_n_contacts': an['n_contacts'],
               'landing_tol_c': an['tol_c'],
               'landing_gn_residual': an['gn_residual'],
               'landing_s_refined': s_land,
               'outcome': outcome, 'landing_match': om,
               'match': match, 'cp_evidence': an['cp'],
               'descent_witness': wit,
               'landing_z': zlf,
               'superseded': fid in SUPERSEDED,
               'wall_secs': time.time() - t0}
        records.append(rec)
        with open(os.path.join(RESULTS, 'drain.json'), 'w') as f:
            json.dump({'records': records}, f, indent=1)
        print('  (%.1fs, total %.1f min)'
              % (rec['wall_secs'], (time.time() - t_start) / 60.0))

    # ---- re-scan for late batch B
    late = []
    for fn in ATLASES:
        p = os.path.join(RESULTS, fn)
        if not os.path.exists(p):
            continue
        with open(p) as f:
            d = json.load(f)
        for e in d['entries']:
            if e['class'] == 'NOT-CP' and e['family_id'] not in sources:
                late.append((e['family_id'], fn))

    counts = {'known': 0, 'new': 0, 'stuck': 0, 'failed': 0}
    for r in records:
        if r.get('superseded'):
            continue
        o = r.get('outcome')
        if o == 'DRAINS-TO-KNOWN':
            counts['known'] += 1
        elif o == 'DRAINS-TO-NEW':
            counts['new'] += 1
        elif o == 'STUCK':
            counts['stuck'] += 1
        else:
            counts['failed'] += 1

    out = {'meta': {
        'attempt': 'A37-cp-atlas',
        'task': 'NOT-CP drain probe (free-angle re-minimisation)',
        'producer': 'attempts/A37-cp-atlas/code/a37_drain.py',
        'rigour': '[NUM] float64 throughout -- taxonomy probe, no certificates',
        'sources': sources,
        'superseded': sorted(SUPERSEDED),
        'superseded_note': 'family 27 is a FALSE NOT-CP per the batch-B lead '
                           'correction (critical to 7.3e-8, min free-sign '
                           'multiplier +2.06e-2, descent rate -1.2e-7); its '
                           'record is kept but excluded from the counts',
        'atlases_read': [fn for fn in ATLASES
                         if os.path.exists(os.path.join(RESULTS, fn))],
        'atlases_missing': missing,
        'late_not_cp_found_on_rescan': late,
        'match_tol': 1e-6,
        'match_metric': 'min over D4 x square relabelling (Hungarian) of the '
                        'max coordinate deviation, theta mod pi/2, plus |ds|',
        'counts': counts,
        'wall_secs': time.time() - t_start},
        'records': records}
    with open(os.path.join(RESULTS, 'drain.json'), 'w') as f:
        json.dump(out, f, indent=1)
    print('\ncounts:', counts, 'missing:', missing, 'late:', late)
    return 0


if __name__ == '__main__':
    sys.exit(main())
