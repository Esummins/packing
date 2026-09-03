"""fj88.py -- A88 TIER 2: FJ exclusion over the CORE box of one structure.

Branch and bound over the core box B of a structure H with leaf tests

  (iii) HC4 / interval Gauss-Seidel PROPAGATION.  With the tilt CLASS bins
        fixed on a box, every row of H is interval-linear in the centres and s
        (rows88.lin_row), so each row can be solved for one variable and the
        result intersected back:  v_j <- -(K + sum_{i!=j} a_i v_i) / a_j .
        The interval-linear form depends ONLY on the tilt bins, so it is built
        once per box and reused across sweeps.
  (i)   a-STRUCTURE: 0 not in [g_r](B) for some row r  ->  discard.
  (ii)  a-SIGMA: sigma_min(B) > s-hat_hi  ->  discard.  sigma >= every corner
        coordinate of every LOADED square, so the max over loaded corners of
        the interval lower bound is a sound lower bound for sigma.
  (iv)  F (Gordan/Farkas, FIXED row set): an LP for y in R^D with
        grad s . y <= -eps and inf_B grad g_r . y >= eps for EVERY row of H.
        Dotting FJ stationarity with y forces lam0 = 0 and all lam_k = 0,
        contradicting the normalisation -> no FJ point in B.  There is NO
        selection menu here (the rows are fixed by H), so A87's menu explosion
        does not arise.  This is the BOX version of the point-wise NNLS/Gordan
        descent test in A87's fjpolish87.
  (v)   K (Krawczyk, rigid-possible only): pick D independent rows of H by rank
        at the box midpoint and run one interval Krawczyk step on that square
        D x D system.  K disjoint from B -> no root; K inside int B -> exactly
        one root, isolated.
  (vi)  otherwise bisect the widest coordinate relative to its initial range.

Arithmetic: fastiv float intervals with outward padding (NOT a certificate;
this is a COST measurement).  Row-activity zero tests carry an absolute slack
ZTOL.
"""
from __future__ import annotations

import math
import time

import numpy as np
from scipy.optimize import linprog

import p88_iv as F
import p88_rows as R
import p88_struct as S

ZTOL = 1e-12
BIG = 1e12


# ------------------------------------------------------------- linear cache

def lin_cache(st, box):
    """[(coef, K)] for every row -- depends only on the TILT bins of `box`."""
    return [R.lin_row(st, box, r) for r in st.rows]


def ineq_cache(st, box):
    return [R.lin_row(st, box, r) for r in getattr(st, 'ineq', ())]


def a_structure_ineq(st, box, icache):
    """Discard when a g >= 0 side row is provably negative on the box."""
    for coef, K in icache:
        v = lin_value(coef, K, box)
        if v[1] < -ZTOL:
            return True
    return False


def lin_value(coef, K, box):
    v = K
    for j, a in coef.items():
        v = F.add(v, F.mul(a, box[j]))
    return v


def _div(a, b):
    """a / b with 0 not in b."""
    p = (a[0] / b[0], a[0] / b[1], a[1] / b[0], a[1] / b[1])
    lo, hi = min(p), max(p)
    r = F.PAD_REL * max(abs(lo), abs(hi))
    return (lo - r, hi + r)


def propagate(st, box, cache, sweeps=3, ztol=ZTOL):
    """Interval Gauss-Seidel on the equality rows.  Returns (box, ok)."""
    box = list(box)
    for _ in range(sweeps):
        changed = 0.0
        for coef, K in cache:
            if not coef:
                if not F.contains0(K, ztol):
                    return None, False
                continue
            for j, a in coef.items():
                if a[0] <= 0.0 <= a[1]:
                    continue
                rest = K
                for i, ai in coef.items():
                    if i != j:
                        rest = F.add(rest, F.mul(ai, box[i]))
                rest = (rest[0] - ztol, rest[1] + ztol)
                nv = _div(F.neg(rest), a)
                new = F.isect(box[j], nv)
                if new is None:
                    return None, False
                w0 = box[j][1] - box[j][0]
                if w0 > 0:
                    changed = max(changed, (w0 - (new[1] - new[0])) / w0)
                box[j] = new
        if changed < 1e-3:
            break
    return box, True


# --------------------------------------------------------------- leaf tests

def a_structure(st, box, cache, ztol=ZTOL):
    for coef, K in cache:
        v = lin_value(coef, K, box)
        if not F.contains0(v, ztol):
            return True
    return False


def sigma_lo(st, box):
    """Sound lower bound for sigma over the box (max loaded corner coord)."""
    best = 0.0
    for i in st.loaded:
        for c in range(4):
            for axis in ('x', 'y'):
                j, A = R.corner_lin(st, box, i, c, axis)
                lo = box[j][0] + A[0]
                if lo > best:
                    best = lo
    return best


def a_sigma(st, box, s_hat_hi):
    lo = sigma_lo(st, box)
    if lo > s_hat_hi:
        return True, None
    js = st.ix[('s',)]
    ns = F.isect(box[js], (lo, s_hat_hi))
    if ns is None:
        return True, None
    if ns != box[js]:
        box = list(box); box[js] = ns
    return False, box


def farkas(st, box, eps_min=1e-9):
    """LP for y in R^D: grad_s . y <= -t, inf_B grad g_r . y >= t, max t."""
    D = st.D
    js = st.ix[('s',)]
    G = []
    for r in st.rows:
        _, g = R.eval_row_core(st, box, r, grad=True)
        lo = np.zeros(D); hi = np.zeros(D)
        for j, v in g.items():
            lo[j] = v[0]; hi[j] = v[1]
        G.append((lo, hi))
    # y = yp - ym, yp, ym in [0, 1];  n = 2D + 1 (last var = t)
    n = 2 * D + 1
    A = np.zeros((len(G) + 1, n)); b = np.zeros(len(G) + 1)
    for i, (lo, hi) in enumerate(G):
        A[i, :D] = -lo
        A[i, D:2 * D] = hi
        A[i, -1] = 1.0
    A[-1, js] = 1.0; A[-1, D + js] = -1.0; A[-1, -1] = 1.0
    c = np.zeros(n); c[-1] = -1.0
    bounds = [(0.0, 1.0)] * (2 * D) + [(0.0, 1.0)]
    r = linprog(c, A_ub=A, b_ub=b, bounds=bounds, method='highs')
    if not r.success:
        return False, 0.0
    t = -r.fun
    return bool(t > eps_min), float(t)


def _midbox(box):
    return [(0.5 * (a + b), 0.5 * (a + b)) for a, b in box]


def pick_rows(st, box, D):
    """D rows of H that are independent at the box midpoint.

    Column-pivoted QR on M^T (M = midpoint Jacobian, one row per row of H)
    orders the rows of M by how much new direction each adds; a greedy rank
    pass then takes the first D that stay independent.
    """
    mb = _midbox(box)
    M = np.zeros((len(st.rows), D))
    for i, r in enumerate(st.rows):
        _, g = R.eval_row_core(st, mb, r, grad=True)
        for j, v in g.items():
            M[i, j] = 0.5 * (v[0] + v[1])
    try:
        import scipy.linalg as sla
        _, _, piv = sla.qr(M.T, pivoting=True, mode='economic')
    except Exception:                                        # pragma: no cover
        piv = np.argsort(-np.abs(M).max(axis=1))
    sel = []
    B = np.zeros((0, D))
    for i in piv:
        C = np.vstack([B, M[i]])
        if np.linalg.matrix_rank(C, tol=1e-9) > B.shape[0]:
            B = C
            sel.append(int(i))
        if len(sel) == D:
            break
    return sel, M


def krawczyk(st, box, sel):
    """One interval Krawczyk step on the square system {g_r = 0 : r in sel}.

    n = len(sel) must equal D (the core dimension).  Returns
      excluded : K disjoint from B  -> B holds no root of the row system
      isolated : K contained in int B -> exactly one root, and it is in K
    """
    D = st.D
    n = len(sel)
    if n != D:
        return {'status': 'nonsquare'}
    mid = [0.5 * (a + b) for a, b in box]
    mb = [(x, x) for x in mid]
    Fm = np.zeros(n)
    Jm = np.zeros((n, n))
    for a, i in enumerate(sel):
        v, g = R.eval_row_core(st, mb, st.rows[i], grad=True)
        Fm[a] = 0.5 * (v[0] + v[1])
        for j, gv in g.items():
            Jm[a, j] = 0.5 * (gv[0] + gv[1])
    try:
        Y = np.linalg.inv(Jm)
        cond = float(np.linalg.cond(Jm))
    except np.linalg.LinAlgError:
        return {'status': 'singular', 'cond': float('inf')}
    if not np.isfinite(cond) or cond > 1e13:
        return {'status': 'ill', 'cond': cond}
    JLO = np.zeros((n, n))
    JHI = np.zeros((n, n))
    for a, i in enumerate(sel):
        _, g = R.eval_row_core(st, box, st.rows[i], grad=True)
        for j, gv in g.items():
            JLO[a, j] = gv[0]
            JHI[a, j] = gv[1]
    YF = Y.dot(Fm)
    # M = I - Y J  over the box (interval matrix product, endpoint form)
    P1 = Y[:, :, None] * JLO[None, :, :]
    P2 = Y[:, :, None] * JHI[None, :, :]
    lo = np.minimum(P1, P2).sum(axis=1)
    hi = np.maximum(P1, P2).sum(axis=1)
    I = np.eye(n)
    MLO = I - hi
    MHI = I - lo
    radlo = np.array([box[j][0] - mid[j] for j in range(n)])
    radhi = np.array([box[j][1] - mid[j] for j in range(n)])
    Q = np.stack([MLO * radlo, MLO * radhi, MHI * radlo, MHI * radhi])
    Klo = np.array(mid) - YF + Q.min(axis=0).sum(axis=1)
    Khi = np.array(mid) - YF + Q.max(axis=0).sum(axis=1)
    excluded = False
    isolated = True
    ratio = 0.0
    for i in range(n):
        if Khi[i] < box[i][0] or Klo[i] > box[i][1]:
            excluded = True
        if not (Klo[i] > box[i][0] and Khi[i] < box[i][1]):
            isolated = False
        hw = 0.5 * (box[i][1] - box[i][0])
        if hw > 0:
            ratio = max(ratio, max(abs(Klo[i] - mid[i]),
                                   abs(Khi[i] - mid[i])) / hw)
    return {'status': 'ok', 'excluded': bool(excluded),
            'isolated': bool(isolated), 'cond': cond, 'ratio': float(ratio),
            'mid': mid, 'K': [(float(Klo[i]), float(Khi[i])) for i in range(n)]}


def _kstep(st, sel, box, mid):
    """Krawczyk operator K(box, mid) for the square system indexed by `sel`."""
    n = len(sel)
    mb = [(x, x) for x in mid]
    Fm = np.zeros(n)
    Jm = np.zeros((n, n))
    for a, i in enumerate(sel):
        v, g = R.eval_row_core(st, mb, st.rows[i], grad=True)
        Fm[a] = 0.5 * (v[0] + v[1])
        for j, gv in g.items():
            Jm[a, j] = 0.5 * (gv[0] + gv[1])
    try:
        Y = np.linalg.inv(Jm)
        cond = float(np.linalg.cond(Jm))
    except np.linalg.LinAlgError:
        return None, None, None, float('inf')
    if not np.isfinite(cond) or cond > 1e13:
        return None, None, None, cond
    JLO = np.zeros((n, n)); JHI = np.zeros((n, n))
    for a, i in enumerate(sel):
        _, g = R.eval_row_core(st, box, st.rows[i], grad=True)
        for j, gv in g.items():
            JLO[a, j] = gv[0]; JHI[a, j] = gv[1]
    P1 = Y[:, :, None] * JLO[None, :, :]
    P2 = Y[:, :, None] * JHI[None, :, :]
    lo = np.minimum(P1, P2).sum(axis=1)
    hi = np.maximum(P1, P2).sum(axis=1)
    I = np.eye(n)
    MLO = I - hi; MHI = I - lo
    m = np.asarray(mid)
    radlo = np.array([box[j][0] for j in range(n)]) - m
    radhi = np.array([box[j][1] for j in range(n)]) - m
    Q = np.stack([MLO * radlo, MLO * radhi, MHI * radlo, MHI * radhi])
    YF = Y.dot(Fm)
    Klo = m - YF + Q.min(axis=0).sum(axis=1)
    Khi = m - YF + Q.max(axis=0).sum(axis=1)
    return Klo, Khi, YF, cond


def krawczyk_isolate(st, box, sel, inflate=16.0, floor=1e-13):
    """EPSILON-INFLATED Krawczyk existence/uniqueness test (A76 Lemma K form).

    A plain Krawczyk step on a box that has been bisected around a root can
    never certify isolation, because the root sits on the box boundary and K
    straddles it (the observed ratio pins at 1.0).  The standard remedy: take
    one Newton step from the midpoint to a candidate x1, build a small box
    around x1 inflated to cover the step, and run Krawczyk there.  K inside
    int B' certifies EXACTLY ONE root of the row system in B'.
    """
    n = len(sel)
    if n != st.D:
        return {'status': 'nonsquare'}
    mid = [0.5 * (a + b) for a, b in box]
    Klo, Khi, YF, cond = _kstep(st, sel, box, mid)
    if Klo is None:
        return {'status': 'ill', 'cond': cond}
    x1 = np.asarray(mid) - YF
    rad = inflate * np.abs(YF) + floor
    B2 = [(float(x1[i] - rad[i]), float(x1[i] + rad[i])) for i in range(n)]
    m2 = [0.5 * (a + b) for a, b in B2]
    K2lo, K2hi, _, cond2 = _kstep(st, sel, B2, m2)
    if K2lo is None:
        return {'status': 'ill', 'cond': cond2}
    isolated = bool(all(K2lo[i] > B2[i][0] and K2hi[i] < B2[i][1]
                        for i in range(n)))
    excluded = bool(any(K2hi[i] < B2[i][0] or K2lo[i] > B2[i][1]
                        for i in range(n)))
    ratio = 0.0
    for i in range(n):
        hw = 0.5 * (B2[i][1] - B2[i][0])
        if hw > 0:
            ratio = max(ratio, max(abs(K2lo[i] - m2[i]),
                                   abs(K2hi[i] - m2[i])) / hw)
    return {'status': 'ok', 'isolated': isolated, 'excluded': excluded,
            'cond': cond2, 'ratio': float(ratio),
            'root_box': B2, 'K': [(float(K2lo[i]), float(K2hi[i]))
                                  for i in range(n)],
            'newton_step_linf': float(np.max(np.abs(YF)))}


# ------------------------------------------------------------------ driver

def relvol(box, w0):
    lv = 0.0
    for (a, b), w in zip(box, w0):
        if w > 0:
            u = b - a
            if u <= 0:
                return -math.inf
            lv += math.log10(u / w)
    return lv


def solve(st, s_lo=S.S_LO, s_hi=S.S_HAT_HI, max_boxes=20000, max_secs=600.0,
          use_hc4=True, use_farkas=True, use_krawczyk=True,
          krawczyk_relwidth=0.05, krawczyk_abswidth=0.05, ztol=ZTOL,
          verbose=False):
    t0 = time.time()
    root = st.core_box(s_lo, s_hi)
    w0 = [b - a for a, b in root]
    hist = {'a_struct': 0, 'a_ineq': 0, 'a_sigma': 0, 'hc4': 0, 'F': 0,
            'K_norot': 0, 'K_isolated': 0, 'bisect': 0, 'depth_cap': 0}
    depth_disch = {}
    depth_visits = {}
    disch = 0.0                      # discharged volume as a fraction of |B|
    narrow_disch = [0.0]             # of which: removed by CONTRACTION
    roots = []
    stack = [(root, 0)]
    # how many core coordinates does HC4 leave wider than the Krawczyk basin?
    _rc = lin_cache(st, root)
    _rn, _rok = propagate(st, root, _rc, ztol=ztol)
    root_wide = None
    if _rok and _rn is not None:
        ws = sorted((b - a for a, b in _rn), reverse=True)
        root_wide = {
            'n_gt_krawczyk_abswidth': sum(1 for w in ws
                                          if w > krawczyk_abswidth),
            'max_width': ws[0] if ws else 0.0,
            'widths_sorted_top10': ws[:10],
            'halvings_needed_per_wide_coord':
                (math.log2(ws[0] / krawczyk_abswidth) if ws and ws[0] > 0
                 else 0.0)}
    nbox = 0
    maxdepth = 0
    survivors = []
    stopped = None
    rigid_possible = st.chi >= 0
    # bisecting a TILT class is worth more than bisecting a centre: every trig
    # enclosure in every row of H tightens with it, so give it a preference
    tiltw = [1.0] * st.D
    for c in st.free_cls:
        tiltw[st.ix[('th', c)]] = 1.5
    trace = []
    fstat = [0, -1e30, 0.0]           # (n LPs, best t, sum t)
    kstat = {'attempts': 0, 'ok': 0, 'ill': 0, 'singular': 0,
             'best_ratio': None, 'min_cond': None}
    min_maw = [float('inf')]
    while stack:
        if nbox >= max_boxes:
            stopped = 'box_cap'; break
        if time.time() - t0 > max_secs:
            stopped = 'time_cap'; break
        if nbox % 100 == 0:
            trace.append((nbox, len(stack)))
        box, dep = stack.pop()
        nbox += 1
        depth_visits[dep] = depth_visits.get(dep, 0) + 1
        maxdepth = max(maxdepth, dep)
        vol = [10.0 ** relvol(box, w0)]

        def discharge(kind, amount=None):
            a = vol[0] if amount is None else amount
            hist[kind] = hist.get(kind, 0) + (1 if amount is None else 0)
            depth_disch[dep] = depth_disch.get(dep, 0.0) + a
            return a

        def narrowed(nb):
            """Volume removed by a sound CONTRACTION (HC4 / sigma clip) is
            discharged too: the removed part provably holds no realisation of
            H, so it must be counted or the completion estimate is nonsense."""
            v1 = 10.0 ** relvol(nb, w0)
            if v1 < vol[0]:
                d = vol[0] - v1
                depth_disch[dep] = depth_disch.get(dep, 0.0) + d
                narrow_disch[0] += d
                vol[0] = v1
                return d
            return 0.0

        if not st.order_consistent(box):
            discharge('a_struct'); disch += vol[0]; continue
        cache = lin_cache(st, box)
        if use_hc4:
            nb, ok = propagate(st, box, cache, ztol=ztol)
            if not ok:
                discharge('hc4'); disch += vol[0]; continue
            if nb is not box:
                disch += narrowed(nb)
                hist['hc4_narrow'] = hist.get('hc4_narrow', 0) + 1
                box = nb
        if a_structure(st, box, cache, ztol):
            discharge('a_struct'); disch += vol[0]; continue
        if getattr(st, 'ineq', None) and a_structure_ineq(
                st, box, ineq_cache(st, box)):
            discharge('a_ineq'); disch += vol[0]; continue
        kill, nb = a_sigma(st, box, s_hi)
        if kill:
            discharge('a_sigma'); disch += vol[0]; continue
        if nb is not box:
            disch += narrowed(nb)
        box = nb
        if use_farkas:
            ok, t = farkas(st, box)
            fstat[0] += 1
            if t > fstat[1]:
                fstat[1] = t
            fstat[2] += t
            if ok:
                discharge('F'); disch += vol[0]; continue
        relw = [(b - a) / w if w > 0 else 0.0 for (a, b), w in zip(box, w0)]
        mrw = max(relw) if relw else 0.0
        maw = max((b - a) for a, b in box)
        if maw < min_maw[0]:
            min_maw[0] = maw
        if use_krawczyk and rigid_possible and maw < krawczyk_abswidth \
                and st.m >= st.D:
            sel, _ = pick_rows(st, box, st.D)
            kstat['attempts'] += 1
            if len(sel) == st.D:
                kr = krawczyk(st, box, sel)
                k_status = kr.get('status', 'other')
                kstat[k_status] = kstat.get(k_status, 0) + 1
                if kr.get('cond') is not None and (
                        kstat['min_cond'] is None
                        or kr['cond'] < kstat['min_cond']):
                    kstat['min_cond'] = kr['cond']
                if kr.get('status') == 'ok':
                    if (kstat['best_ratio'] is None
                            or kr['ratio'] < kstat['best_ratio']):
                        kstat['best_ratio'] = kr['ratio']
                    if not kr['excluded'] and not kr['isolated']:
                        ki = krawczyk_isolate(st, box, sel)
                        if ki.get('status') == 'ok' and ki['isolated']:
                            kr = dict(kr)
                            kr['isolated'] = True
                            kr['ratio'] = ki['ratio']
                            kr['K'] = ki['K']
                            kstat['isolated_by_inflation'] = \
                                kstat.get('isolated_by_inflation', 0) + 1
                    if kr['excluded']:
                        discharge('K_norot'); disch += vol[0]; continue
                    if kr['isolated']:
                        hist['K_isolated'] += 1
                        roots.append({'depth': dep, 'ratio': kr['ratio'],
                                      'cond': kr['cond'],
                                      's': box[st.ix[('s',)]],
                                      'K_box': kr['K'],
                                      'relwidth_max': mrw})
                        discharge('K_isolated_vol', vol[0])
                        disch += vol[0]
                        continue
        if dep >= 200:
            hist['depth_cap'] += 1
            survivors.append((box, dep)); continue
        j = max(range(st.D), key=lambda k: relw[k] * tiltw[k])
        if relw[j] <= 1e-12:
            survivors.append((box, dep)); continue
        lo, hi = box[j]; mid = 0.5 * (lo + hi)
        a = list(box); a[j] = (lo, mid)
        b = list(box); b[j] = (mid, hi)
        hist['bisect'] += 1
        stack.append((a, dep + 1)); stack.append((b, dep + 1))
    secs = time.time() - t0
    for box, dep in stack:
        survivors.append((box, dep))
    # effective dimension of what survived
    eff = None
    if survivors:
        acc = [0.0] * st.D
        for box, _ in survivors[:2000]:
            for k in range(st.D):
                if w0[k] > 0:
                    acc[k] = max(acc[k], (box[k][1] - box[k][0]) / w0[k])
        eff = {'n_coord_relwidth_gt_0.5': sum(1 for x in acc if x > 0.5),
               'n_coord_relwidth_gt_0.1': sum(1 for x in acc if x > 0.1),
               'max_relwidth': max(acc) if acc else 0.0,
               'median_relwidth': float(np.median(acc)) if acc else 0.0}
    disch = min(disch, 1.0)
    rate = disch / nbox if nbox else 0.0
    # log-space REMAINING volume: the fraction metric saturates at 1.0 the
    # moment HC4 contracts (the FJ set has positive codimension, so the
    # surviving region has volume ~1e-90 of the core box after one sweep).
    lv = [relvol(b, w0) for b, _ in survivors]
    if lv:
        mx = max(lv)
        log10_remaining = mx + math.log10(sum(10.0 ** (x - mx) for x in lv))             if mx > -math.inf else None
    else:
        log10_remaining = None            # stack empty => search COMPLETE
    # tree shape: does the open stack shrink?
    slope = None
    to_completion = None
    if len(trace) >= 4:
        half = trace[len(trace) // 2:]
        x0, y0 = half[0]; x1, y1 = half[-1]
        if x1 > x0:
            slope = (y1 - y0) / float(x1 - x0)
            if slope < -1e-9:
                to_completion = int(nbox + len(stack) / (-slope))
    return {
        'tag': st.tag, 'boxes': nbox, 'secs': secs,
        'ms_per_box': 1000.0 * secs / nbox if nbox else None,
        'stopped': stopped or 'complete',
        'hist': hist, 'max_depth': maxdepth,
        'discharged_frac': disch,
        'discharged_by_contraction_frac': min(narrow_disch[0], 1.0),
        'undischarged_frac': max(0.0, 1.0 - disch),
        'log10_undischarged_frac': (math.log10(1.0 - disch)
                                    if 0.0 < 1.0 - disch else None),
        'log10_discharged_frac': (math.log10(disch) if disch > 0 else None),
        'depth_profile': {str(k): v for k, v in sorted(depth_disch.items())},
        'depth_visits': {str(k): v for k, v in sorted(depth_visits.items())},
        'root_wide_coords': root_wide,
        'n_survivor_boxes': len(survivors),
        'eff_dim': eff, 'roots': roots,
        'log10_remaining_volume_frac': log10_remaining,
        'open_stack_final': len(stack),
        'd_open_per_box': slope,
        'open_stack_trace': trace[-40:],
        'boxes_to_completion_EXTRAPOLATED': to_completion,
        'boxes_to_completion_note': ('open stack SHRINKING' if to_completion
                                     else 'open stack not shrinking at the cap'),
        'discharge_rate_per_box': rate,
        'farkas': {'n_lp': fstat[0], 'best_t': (fstat[1] if fstat[0] else None),
                   'mean_t': (fstat[2] / fstat[0] if fstat[0] else None)},
        'krawczyk': kstat,
        'min_max_abs_width_reached': (min_maw[0] if min_maw[0] < 1e30
                                      else None),
        'krawczyk_abswidth_threshold': krawczyk_abswidth,
        'rigid_possible': rigid_possible,
        'D': st.D, 'm': st.m, 'k_H': st.k_H, 'chi': st.chi,
    }


# ------------------------------------------------------- canary: follow a point

def follow_point(st, zpt, s_lo=S.S_LO, s_hi=S.S_HAT_HI, max_depth=400,
                 krawczyk_abswidth=0.05, ztol=ZTOL):
    """Descend the B&B always into the child that CONTAINS the given point.

    This is the A76 Lemma K canary in its sharpest form: if any leaf test ever
    discharges the box holding a genuine FJ point, the test is UNSOUND.  The
    expected outcome for Trump's support is that no test ever discharges it and
    Krawczyk eventually CONTRACTS onto it (isolated), reporting s = s-hat.
    """
    core = [0.0] * st.D
    for i in st.loaded:
        core[st.ix[('cx', i)]] = zpt[3 * i]
        core[st.ix[('cy', i)]] = zpt[3 * i + 1]
    for c in st.free_cls:
        core[st.ix[('th', c)]] = st.reps[c]
    core[st.ix[('s',)]] = zpt[33]
    box = st.core_box(s_lo, s_hi)
    for j in range(st.D):
        if not (box[j][0] - 1e-9 <= core[j] <= box[j][1] + 1e-9):
            return {'status': 'point_outside_core_box', 'coord': j,
                    'box': box[j], 'point': core[j]}
    log = []
    for dep in range(max_depth):
        cache = lin_cache(st, box)
        nb, ok = propagate(st, box, cache, ztol=ztol)
        if not ok:
            return {'status': 'CANARY_FAIL', 'test': 'hc4', 'depth': dep,
                    'final_box': box, 'log': log[-3:]}
        for j in range(st.D):
            if not (nb[j][0] - 1e-7 <= core[j] <= nb[j][1] + 1e-7):
                return {'status': 'CANARY_FAIL', 'test': 'hc4_lost_point',
                        'depth': dep, 'coord': j, 'box': nb[j],
                        'point': core[j], 'log': log}
        box = nb
        if a_structure(st, box, cache, ztol):
            return {'status': 'CANARY_FAIL', 'test': 'a_structure',
                    'depth': dep, 'log': log}
        kill, nb = a_sigma(st, box, s_hi)
        if kill:
            return {'status': 'CANARY_FAIL', 'test': 'a_sigma', 'depth': dep,
                    'log': log}
        box = nb
        ok, t = farkas(st, box)
        if ok:
            return {'status': 'CANARY_FAIL', 'test': 'farkas', 'depth': dep,
                    'farkas_t': t, 'log': log}
        maw = max(b - a for a, b in box)
        if maw < krawczyk_abswidth and st.m >= st.D:
            sel, _ = pick_rows(st, box, st.D)
            if len(sel) == st.D:
                kr = krawczyk(st, box, sel)
                ki = krawczyk_isolate(st, box, sel)
                log.append({'depth': dep, 'maw': maw,
                            'plain': {k: v for k, v in kr.items()
                                      if k in ('status', 'excluded',
                                               'isolated', 'cond', 'ratio')},
                            'inflated': {k: v for k, v in ki.items()
                                         if k in ('status', 'excluded',
                                                  'isolated', 'cond', 'ratio',
                                                  'newton_step_linf')}})
                if kr.get('status') == 'ok' and kr['excluded']:
                    return {'status': 'CANARY_FAIL',
                            'test': 'krawczyk_excluded',
                            'depth': dep, 'krawczyk': kr, 'log': log[-4:]}
                if ki.get('status') == 'ok' and ki['excluded']:
                    return {'status': 'CANARY_FAIL',
                            'test': 'krawczyk_inflated_excluded',
                            'depth': dep, 'krawczyk': ki, 'log': log[-4:]}
                if ki.get('status') == 'ok' and ki['isolated']:
                    js = st.ix[('s',)]
                    return {'status': 'ISOLATED', 'depth': dep,
                            'maw': maw, 'cond': ki['cond'],
                            'ratio': ki['ratio'],
                            'newton_step_linf': ki['newton_step_linf'],
                            's_box': box[js],
                            'root_s_box': ki['root_box'][js],
                            'root_box_maxwidth': max(b - a for a, b
                                                     in ki['root_box']),
                            'final_box': box, 'sel': sel,
                            'log': log[-3:]}
        # bisect the widest coordinate and keep the half holding the point
        w = [(b - a) for a, b in box]
        j = max(range(st.D), key=lambda k: w[k])
        if w[j] <= 1e-14:
            return {'status': 'box_degenerate', 'depth': dep,
                    'maw': maw, 'final_box': box, 'log': log[-3:]}
        lo, hi = box[j]
        mid = 0.5 * (lo + hi)
        box = list(box)
        box[j] = (lo, mid) if core[j] <= mid else (mid, hi)
    return {'status': 'depth_cap', 'depth': max_depth,
            'maw': max(b - a for a, b in box), 'final_box': box,
            'log': log[-3:]}


def refine_root(st, box, sel, rounds=8, inflate=4.0, floor=1e-15):
    """Iterate the inflated Krawczyk test to shrink a certified root box."""
    cur = None
    out = []
    b = list(box)
    for _ in range(rounds):
        ki = krawczyk_isolate(st, b, sel, inflate=inflate, floor=floor)
        if ki.get('status') != 'ok' or not ki['isolated']:
            break
        cur = ki
        out.append({'maxwidth': max(y - x for x, y in ki['root_box']),
                    'ratio': ki['ratio'],
                    'newton_step_linf': ki['newton_step_linf']})
        nb = [(0.5 * (a1 + b1) - 0.5 * (b1 - a1),
               0.5 * (a1 + b1) + 0.5 * (b1 - a1))
              for a1, b1 in ki['K']]
        if max(y - x for x, y in nb) >= max(y - x for x, y in ki['root_box']):
            b = ki['root_box']
        else:
            b = nb
    return cur, out
