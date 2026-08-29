#!/usr/bin/env python3
"""A43-H2 canaries: type a REALIZED wall-to-wall chain and run every constraint
of the census against the realized numbers (realized-point check) plus the
type-survival check.

A FAIL on a realized configuration means the corresponding filter is UNSOUND: it
kills something that exists.  The driver stops the census in that case.
"""
from __future__ import annotations

import math
from fractions import Fraction as F

import spine as S
import geomx as GX
from ivl import I, h_deg, SQRT2


# --------------------------------------------------------------- typing
def type_of_path(cfg, path, wall_a='L', wall_b='R'):
    """(eL, eR, links, info) for a realized wall-to-wall chain."""
    adj, pc, wc = cfg.graph()
    q0, qk = path[0], path[-1]
    eL = S.END_F if len(wc[q0][wall_a]) >= 2 else S.END_C
    eR = S.END_F if len(wc[qk][wall_b]) >= 2 else S.END_C
    links = []
    for a, b in zip(path, path[1:]):
        key = (a, b) if a < b else (b, a)
        r = pc[key]
        if r['kind'] == 'FL':
            links.append(S.FL)
        elif r['kind'] == 'CC':
            links.append(S.CC)
        else:
            # CE: corner of r['other'] lies on the edge of r['owner']
            links.append(S.CEAB if r['other'] == a else S.CEBA)
    return eL, eR, tuple(links), dict(pc=pc, wc=wc)


def states_of_path(eL, eR, links, phi):
    """Class-state (ZS / ZE / bin) per square of a realized path.
    Runs = maximal blocks of consecutive FL links; the first run is ZS when
    e_L = F, the last is ZE when e_R = F (ZS wins if they are the same run)."""
    k = len(phi)
    run = [0] * k
    for i in range(1, k):
        run[i] = run[i - 1] if links[i - 1] == S.FL else run[i - 1] + 1
    nrun = run[-1] + 1
    rst = [min(S.NBIN - 1, max(0, int(phi[i] / S.BW))) for i in range(k)]
    val = {}
    for i in range(k):
        val.setdefault(run[i], rst[i])
    if eR == S.END_F:
        val[nrun - 1] = S.ZE
    if eL == S.END_F:
        val[0] = S.ZS
    return [val[run[i]] for i in range(k)]


# ------------------------------------------------- realized-point checks
def realized_check(cfg, path, eL, eR, links, geo, atlas=None, field_ok=False,
                   tol=None):
    """Run C0-C4 against the realized numbers.  Returns a dict of named checks."""
    s = cfg.s
    if tol is None:
        tol = cfg.eps_pos
    ep = cfg.eps_phi
    k = len(path)
    phi = [cfg.phi(i) for i in path]
    x = [cfg.sq[i][0] for i in path]
    y = [cfg.sq[i][1] for i in path]
    out = {}
    det = {}

    # ---- C0 end identities, span, containment, per-link dx membership
    h1 = h_deg(phi[0], phi[0])
    hk = h_deg(phi[-1], phi[-1])
    out['C0.x1=h(phi1)'] = abs(x[0] - 0.5 * (h1.lo + h1.hi)) < tol
    out['C0.xk=s-h(phik)'] = abs((s - x[-1]) - 0.5 * (hk.lo + hk.hi)) < tol
    span = x[-1] - x[0]
    span_iv = I(s, s) - h1 - hk
    out['C0.span identity'] = span_iv.lo - tol <= span <= span_iv.hi + tol
    det['span'] = span
    det['span_iv'] = span_iv.as_list()
    ok_cont = True
    for i in range(k):
        hi_ = h_deg(phi[i], phi[i])
        if not (hi_.lo - tol <= x[i] <= s - hi_.lo + tol):
            ok_cont = False
    out['C0.containment'] = ok_cont
    # per-link dx must lie in the certified branch union at the realized tilts
    ok_dx = True
    dxdet = []
    for i in range(k - 1):
        dx = x[i + 1] - x[i]
        br = S.branches_p(links[i], (phi[i] - ep, phi[i] + ep),
                          (phi[i + 1] - ep, phi[i + 1] + ep))
        hit = [bk for bk, iv in br if iv.lo - tol <= dx <= iv.hi + tol]
        dxdet.append(dict(link=S.LINK_NAME[links[i]], dx=dx,
                          nbranch=len(br), hits=[list(map(str, b)) for b in hit]))
        if not hit:
            ok_dx = False
    out['C0.dx in branch union'] = ok_dx
    det['links'] = dxdet
    # |delta| in [1, sqrt2]  (L5a)
    ok_d = True
    for i in range(k - 1):
        d = math.hypot(x[i + 1] - x[i], y[i + 1] - y[i])
        if not (1.0 - tol <= d <= SQRT2.hi + tol):
            ok_d = False
    out['C0.|delta| in [1,sqrt2]'] = ok_d

    # ---- C1 tilt coupling on the realized tilts
    ok_c1 = True
    for i in range(k - 1):
        if links[i] == S.FL and abs(phi[i] - phi[i + 1]) > 2 * ep:
            ok_c1 = False
        if links[i] in (S.CEAB, S.CEBA) and abs(phi[i] - phi[i + 1]) <= 2 * ep:
            ok_c1 = False
    if eL == S.END_F and abs(phi[0]) > 2 * ep:
        ok_c1 = False
    if eR == S.END_F and abs(phi[-1]) > 2 * ep:
        ok_c1 = False
    if eL == S.END_C and abs(phi[0]) <= 2 * ep:
        ok_c1 = False
    if eR == S.END_C and abs(phi[-1]) <= 2 * ep:
        ok_c1 = False
    out['C1.tilt coupling'] = ok_c1

    # ---- C2a the realized anchor must be admitted by the layered DP
    st = states_of_path(eL, eR, links, phi)
    cells = [min(geo.ncell - 1, int(v / geo.cw)) for v in x]
    ok_dp = True
    pins = geo.pins(k)
    for i in range(k - 1):
        T = geo.trans(links[i], pins[i][0], pins[i][1])
        ra = st[i] * geo.ncell + cells[i]
        rb = st[i + 1] * geo.ncell + cells[i + 1]
        if not T[ra, rb]:
            ok_dp = False
    v0 = geo.start_vec(eL)
    if not v0[st[0] * geo.ncell + cells[0]]:
        ok_dp = False
    em = geo.end_mask(eR)
    if not em[st[-1] * geo.ncell + cells[-1]]:
        ok_dp = False
    out['C2a.realized anchor in DP'] = ok_dp
    det['states'] = st
    det['cells'] = cells
    det['phi'] = phi
    det['x'] = x

    # ---- C2b y-column capacity lemma on the realized x
    out['C2b.capacity lemma'] = capacity_ok([(xi, xi) for xi in x], s)

    # ---- C3 tight-variety at the realized placements
    if field_ok:
        import fieldx
        _, meta = fieldx.get()
        thr = float(F(meta['thr']))
        worst = 0.0
        for i in path:
            cx, cy, th = cfg.sq[i]
            t = math.tan((math.degrees(th) % 90.0) / 2.0 * math.pi / 180.0)
            worst = max(worst, fieldx.coverage_at(t, cx, cy))
        det['C3_max_mu'] = worst
        det['C3_thr'] = thr
        out['C3.mu <= 1+eta'] = worst <= thr + 1e-9
    else:
        out['C3.mu <= 1+eta'] = None

    # ---- C4 interface wastage at the realized placements
    if atlas is not None:
        tot, used = atlas_sum(atlas, [(cfg.phi(i), cfg.sq[i][0], cfg.sq[i][1])
                                      for i in path], point=True)
        budget = s * s - 11.0
        det['C4_sum'] = float(tot)
        det['C4_budget'] = budget
        det['C4_used'] = used
        out['C4.wastage <= s^2-11'] = float(tot) <= budget
    else:
        out['C4.wastage <= s^2-11'] = None
    return out, det


def capacity_ok(xwin, s, tol=1e-9):
    """y-column capacity lemma (C2b).  xwin = list of (lo, hi) certified windows.
    For any subset whose windows all lie in a common window of width Delta < 1,
    |S| <= 1 + floor((s-1)/sqrt(1-Delta^2)).  Returns True if NOT violated."""
    n = len(xwin)
    for i in range(n):
        for j in range(n):
            lo = min(xwin[i][0], xwin[j][0])
            hi = max(xwin[i][1], xwin[j][1])
            D = hi - lo
            if D >= 1.0 - tol:
                continue
            cnt = sum(1 for a, b in xwin if a >= lo - tol and b <= hi + tol)
            cap = 1 + math.floor((s - 1.0) / math.sqrt(1.0 - D * D))
            if cnt > cap:
                return False
    return True


def atlas_sum(atlas, placements, point=False):
    """A25 budget-lemma sum over the spine squares.  placements = list of
    (phi_deg or (lo,hi), cx or (lo,hi), cy or (lo,hi)).  Greedily drops squares
    whose region lists collide, which is conservative (a smaller certified sum).
    Returns (Fraction sum, list of indices actually used)."""
    from query import disjoint_regions
    vals, regs = [], []
    for p in placements:
        th, cx, cy = p
        if point:
            th = (float(th), float(th))
            cx = (F(cx), F(cx))
            cy = (F(cy), F(cy))
        v, r = atlas.lookup(cx, cy, th)
        vals.append(v)
        regs.append(r)
    order = sorted(range(len(vals)), key=lambda i: -float(vals[i]))
    used, groups = [], []
    for i in order:
        if vals[i] == 0:
            continue
        if disjoint_regions(groups + [regs[i]]):
            used.append(i)
            groups.append(regs[i])
    return sum((vals[i] for i in used), F(0)), sorted(used)
