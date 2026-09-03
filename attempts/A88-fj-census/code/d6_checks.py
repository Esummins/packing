"""A88 D6: certified-FJ checks against the A87 FJ-polished points.

Uses the 167 TIGHT survivors of attempts/A87-drain-flow/results/cp87_fj_polished.jsonl
(survivor_tight true; z_polished = exact rational strings).  A87's t3lib is
imported READ-ONLY; the three helpers (active_rows_at_point, grad_matrix,
cone_nnls) are COPIED here verbatim so nothing under A87 is touched.

(1) T1 floor check on the SUPPORT H = rows with lambda > 1e-9 of one NNLS
    certificate (multipliers are non-unique; this is ONE certificate).
(2) Census membership: contact types by code, ACTIVE graph G and SUPPORT graph
    H, the F0 filters, and the k0 filters K0-1/K0-3.  These points sit at sigma
    in [3.897, 4.9], OUTSIDE the census window, so L5(a)/N1 are ALSO run with
    the window widened to [3.82, sigma+1e-6].
"""
import os
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
           'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ[_v] = '1'
import json
import math
import sys
from collections import defaultdict
from fractions import Fraction

import numpy as np
from scipy.optimize import nnls

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
A87 = os.path.join(ROOT, 'attempts', 'A87-drain-flow', 'code')
sys.path.insert(0, A87)
import t3lib as T                                     # noqa: E402  (A87 copy)
sys.path.insert(0, HERE)
import a88lib as A                                    # noqa: E402

TOL = 1e-6
RES = os.path.join(HERE, '..', 'results')
NH = [(0, -1), (1, 0), (0, 1), (-1, 0)]
HALFOFF = [(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)]


# ---- COPIED VERBATIM from attempts/A87-drain-flow/code/jobs87.py -----------
def active_rows_at_point(z, tol=1e-6):
    pt = [T._to_iv(x) for x in z]
    ab = T.test_ab(pt)
    info = {'point_infeasible': ab['infeasible'], 'point_reason': ab['reason']}
    if ab['infeasible']:
        info['min_gap'] = ab.get('min_gap')
        return None, info
    info['min_gap'] = ab['min_gap']
    info['min_clear'] = ab['min_clear']
    rows = []
    for i in range(11):
        for c in range(4):
            for w in T.WALLS:
                r = T.wall_row(i, c, w)
                if abs(float(T.row_value(pt, r).a)) <= tol:
                    rows.append(r)
    info['n_wall_active'] = len(rows)
    contact_pairs = [p for p, v in ab['pairs'].items() if v[1] <= tol]
    info['n_contact_pairs'] = len(contact_pairs)
    nsel = 0
    n_nosel = 0
    for (i, j) in sorted(contact_pairs):
        got = False
        for o, p in ((i, j), (j, i)):
            if got:
                break
            for e in range(4):
                if got:
                    break
                for k in range(4):
                    rr = [T.sep_row(o, e, p, k)] + [T.dom_row(o, e, p, k, m)
                                                    for m in range(4) if m != k]
                    vals = [T.row_value(pt, r) for r in rr]
                    if all(float(v.a) >= -tol for v in vals):
                        add = [r for r, v in zip(rr, vals)
                               if abs(float(v.a)) <= tol]
                        rows += add
                        nsel += len(add)
                        got = True
                        break
        if not got:
            n_nosel += 1
    info['n_sel_active'] = nsel
    info['n_pairs_no_consistent_selection'] = n_nosel
    info['contact_pairs'] = sorted(contact_pairs)
    return rows, info


# ---- COPIED VERBATIM from attempts/A87-drain-flow/code/pilot87.py ----------
def grad_matrix(box, rows):
    A_ = np.zeros((len(rows), T.NV))
    for k, r in enumerate(rows):
        _, g = T.row_grad(box, r)
        for gi, val in g.items():
            A_[k, gi] = T._mid(val)
    return A_


# ---- COPIED VERBATIM from attempts/A87-drain-flow/code/fjpolish87.py -------
def cone_nnls(A_):
    m = A_.shape[0]
    if m == 0:
        d = np.zeros(T.NV)
        d[33] = -1.0
        return float('inf'), None, d
    nrm = np.linalg.norm(A_, axis=1)
    nrm[nrm == 0] = 1.0
    An = A_ / nrm[:, None]
    b = np.zeros(T.NV)
    b[33] = 1.0
    lam, res = nnls(An.T, b)
    r = An.T @ lam - b
    return float(res), (lam / nrm), r


# --------------------------------------------------------------- geometry
def corners(z, i):
    cx, cy, th = float(z[3 * i]), float(z[3 * i + 1]), float(z[3 * i + 2])
    c, s = math.cos(th), math.sin(th)
    return [(cx + a * c - b * s, cy + a * s + b * c) for a, b in HALFOFF]


def gauge_offset(z, i):
    """Gauge: phi = theta mod 90 deg in [0,90).  theta = phi + 90*o, so
    R(phi) NHAT[e'] = R(theta) NHAT[e] = R(90 o) R(phi) NHAT[e], and R(90 deg)
    sends NHAT[e] -> NHAT[e+1]: the gauge index is e' = (e + o) mod 4 (same for
    corners, since R(90) sends HALF[k] -> HALF[k+1])."""
    th = float(z[3 * i + 2])
    o_raw = math.floor(th / (math.pi / 2))
    phi = math.degrees(th - o_raw * (math.pi / 2))
    # gauge-boundary snap: theta a hair BELOW a multiple of 90 deg is an
    # axis-aligned square, phi = 0 in the next quarter, not phi = 90 - eps.
    if 90.0 - phi < 1e-5:
        o_raw += 1
        phi = 0.0
    return int(o_raw) % 4, phi


def classify_pair_geo(z, i, j, side):
    P = corners(z, i)
    Q = corners(z, j)
    best = None
    for (o, p, poly_o, poly_p) in ((i, j, P, Q), (j, i, Q, P)):
        cx, cy = float(z[3 * o]), float(z[3 * o + 1])
        th = float(z[3 * o + 2])
        c, s = math.cos(th), math.sin(th)
        for e in range(4):
            nx0, ny0 = NH[e]
            nx, ny = c * nx0 - s * ny0, s * nx0 + c * ny0
            vals = [nx * (qx - cx) + ny * (qy - cy) - 0.5 for qx, qy in poly_p]
            mn = min(vals)
            if best is None or mn > best[0]:
                best = (mn, o, p, e, vals, nx, ny, poly_o, poly_p)
    mn, o, p, e, vals, nx, ny, poly_o, poly_p = best
    if mn > TOL:
        return None
    hits = [t for t in range(4) if abs(vals[t]) <= TOL]
    tx, ty = -ny, nx
    to = [poly_o[e][0] * tx + poly_o[e][1] * ty,
          poly_o[(e + 1) % 4][0] * tx + poly_o[(e + 1) % 4][1] * ty]
    tp = [poly_p[h][0] * tx + poly_p[h][1] * ty for h in hits]
    ov = (min(max(to), max(tp)) - max(min(to), min(tp))) if len(tp) >= 2 else 0.0
    kind = ('flush' if (len(hits) >= 2 and ov > TOL)
            else ('corner-corner' if len(hits) >= 2 else 'corner-on-edge'))
    return dict(o=o, p=p, e=e, hits=hits, kind=kind, resid=mn)


def wall_contacts(z, side):
    wm = [0] * 11
    sw = {}
    detail = []
    for i in range(11):
        pts = corners(z, i)
        xs = [q[0] for q in pts]
        ys = [q[1] for q in pts]
        for b, d in enumerate([[x for x in xs], [y for y in ys],
                              [side - x for x in xs], [side - y for y in ys]]):
            mn = min(d)
            if abs(mn) <= TOL:
                wm[i] |= 1 << b
                hits = [t for t in range(4) if abs(d[t]) <= TOL]
                sw[(i, b)] = 'WF' if len(hits) >= 2 else 'CW'
                detail.append(dict(sq=i, wall=A.WALL_NAMES[b], hits=hits,
                                   type=sw[(i, b)], resid=mn))
    return wm, sw, detail


# ------------------------------------------------------------------ main
def main():
    src = os.path.join(ROOT, 'attempts', 'A87-drain-flow', 'results',
                       'cp87_fj_polished.jsonl')
    recs = [json.loads(l) for l in open(src)]
    tight = [r for r in recs if r.get('survivor_tight')]
    print('A87 records %d, tight survivors %d' % (len(recs), len(tight)),
          flush=True)
    out = []
    alarms = []
    for c, r in enumerate(tight):
        z = [T.str_frac(s) for s in r['z_polished']]
        sigma = float(r['sigma_polished'])
        side = float(z[33])
        rows, info = active_rows_at_point(z, TOL)
        rec = dict(tag=r['tag'], sigma=sigma, side=side,
                   n_active=(len(rows) if rows else 0),
                   point_infeasible=info['point_infeasible'])
        if not rows:
            rec['note'] = 'no active rows / infeasible point'
            out.append(rec)
            alarms.append((r['tag'], 'no active rows'))
            continue
        pt = [T._to_iv(x) for x in z]
        Amat = grad_matrix(pt, rows)
        res, lam, _ = cone_nnls(Amat)
        rec['cone_residual'] = res
        supp = [t for t in range(len(rows)) if lam is not None and lam[t] > 1e-9]
        H = [rows[t] for t in supp]
        rec['m_H'] = len(H)
        # loaded squares + support structure
        loaded = set()
        h_wall = {}
        h_pairs = defaultdict(list)
        for rr in H:
            if rr['kind'] == 'wall':
                loaded.add(rr['i'])
                h_wall.setdefault(rr['i'], set()).add(rr['wall'])
            else:
                loaded.add(rr['o'])
                loaded.add(rr['p'])
                h_pairs[(min(rr['o'], rr['p']), max(rr['o'], rr['p']))].append(rr)
        loaded = sorted(loaded)
        kH = len(loaded)
        rec['k_H'] = kH
        rec['H_pairs'] = [list(e) for e in sorted(h_pairs)]
        rec['H_wall'] = {str(i): sorted(v) for i, v in sorted(h_wall.items())}
        cols = []
        for i in loaded:
            cols += [3 * i, 3 * i + 1, 3 * i + 2]
        cols.append(33)
        AH = Amat[np.array(supp, dtype=int)][:, cols] if supp else np.zeros((0, 1))
        rank = int(np.linalg.matrix_rank(AH, tol=1e-9)) if AH.size else 0
        rec['rank_H'] = rank
        rec['d_H'] = 3 * kH + 1 - rank
        rec['sigma_H'] = rec['m_H'] - rank
        rec['identity_ok'] = (rec['m_H'] == 3 * kH + 1 + rec['sigma_H']
                              - rec['d_H'])
        rec['chi'] = rec['m_H'] - 3 * kH - 1
        rec['rigid_possible'] = bool(rec['chi'] >= 0)
        # --- T1 assertions
        wmH = [0] * 11
        for i, ws in h_wall.items():
            for w in ws:
                wmH[i] |= 1 << T.WALLS.index(w)
        degH = defaultdict(int)
        for (a, b) in h_pairs:
            degH[a] += 1
            degH[b] += 1
        l1 = all(degH[i] + A.POP[wmH[i]] >= 2 for i in loaded)
        adjH = A.adj_from_edges(11, list(h_pairs))
        comps = A.components(adjH, 11)
        cw = []
        for vs in comps:
            m = 0
            for v in vs:
                m |= wmH[v]
            cw.append(m)
        ch = True
        while ch:
            ch = False
            for a in range(len(cw)):
                for b in range(a + 1, len(cw)):
                    if cw[a] & cw[b] and cw[a] != cw[b]:
                        cw[a] = cw[b] = cw[a] | cw[b]
                        ch = True
        l6 = any((x & 5) == 5 or (x & 10) == 10 for x in cw)
        l3 = all((cw[t] != 0) for t, vs in enumerate(comps)
                 if set(vs) & set(loaded))
        rec['T1'] = dict(k_H_ge_3=bool(kH >= 3), m_H_ge_4=bool(rec['m_H'] >= 4),
                         L1=bool(l1), L3=bool(l3), L6=bool(l6))
        for nm, v in rec['T1'].items():
            if not v:
                alarms.append((r['tag'], 'T1 %s FAILS (k_H=%d m_H=%d)'
                               % (nm, kH, rec['m_H'])))
        # --- census membership on the ACTIVE structure
        wm, sw, wdet = wall_contacts(z, side)
        gedges = []
        sstype = {}
        degen = []
        for i in range(11):
            for j in range(i + 1, 11):
                cc = classify_pair_geo(z, i, j, side)
                if cc is None:
                    continue
                gedges.append((i, j))
                if cc['kind'] == 'flush':
                    oi, _ = gauge_offset(z, cc['o'])
                    eg = (cc['e'] + oi) % 4
                    e_j = eg if cc['o'] == j else (eg + 2) % 4
                    sstype[(i, j)] = ('F', e_j)
                elif cc['kind'] == 'corner-on-edge':
                    oi, phio = gauge_offset(z, cc['o'])
                    _, phip = gauge_offset(z, cc['p'])
                    sstype[(i, j)] = ('C', cc['o'], (cc['e'] + oi) % 4,
                                      phip > phio)
                else:
                    degen.append((i, j))
                    sstype[(i, j)] = None
        rec['n_G_ss'] = len(gedges)
        rec['n_G_sw'] = sum(A.POP[m] for m in wm)
        rec['wall_masks'] = wm
        rec['degenerate_corner_corner'] = [list(e) for e in degen]
        rec['n_flush'] = sum(1 for v in sstype.values() if v and v[0] == 'F')
        rec['n_wall_flush'] = sum(1 for v in sw.values() if v == 'WF')
        rec['E'] = len(gedges) + rec['n_G_sw']
        rec['F'] = rec['n_flush'] + rec['n_wall_flush']
        rec['m_G'] = rec['E'] + rec['F']
        # F0 on G (narrow and widened window)
        fG = A.f0_flags(11, gedges, wm)
        fGw = A.f0_flags(11, gedges, wm, s_hi=max(A.S_HI, sigma + 1e-6))
        rec['F0_G_narrow'] = {a: bool(b) for a, b in fG.items()}
        rec['F0_G_wide'] = {a: bool(b) for a, b in fGw.items()}
        # the same test with the degenerate corner-corner kisses removed (they
        # are contacts only at the 1e-6 tolerance and carry no menu type)
        gnd = [e for e in gedges if e not in degen]
        rec['L4b_planar_no_degenerate'] = bool(A.is_planar_struct(11, gnd, wm))
        for nm in ('L5b_masks', 'L4b_planar', 'L5d_deg12', 'L4a_euler'):
            if not fG[nm]:
                alarms.append((r['tag'], 'window-INDEPENDENT %s fails on G '
                               '(sigma=%.6f, %d degenerate kisses, planar '
                               'without them: %s)'
                               % (nm, sigma, len(degen),
                                  rec['L4b_planar_no_degenerate'])))
        for nm in ('L5a_metric', 'N1_wallcap3'):
            if not fGw[nm]:
                alarms.append((r['tag'], '%s fails with the WIDENED window' % nm))
        rec['narrow_L5a_or_N1_fail'] = bool(not fG['L5a_metric']
                                            or not fG['N1_wallcap3'])
        # decoration on the menu-representable part
        ss_ok = [e for e in sorted(gedges) if sstype[e] is not None]
        dec = A.Decoration(11, ss_ok, wm, [sstype[e] for e in ss_ok], sw)
        ts = dec.tilt_system()
        rec['tilt_feasible'] = bool(ts['feasible'])
        rec['tilt_reason'] = ts.get('reason')
        if not ts['feasible']:
            alarms.append((r['tag'], 'DECORATION TILT-INFEASIBLE: %s'
                           % ts.get('reason')))
            rec['K0_1'] = None
            rec['K0_3'] = None
        else:
            rec['K0_1'] = bool(dec.k0_1())
            rec['slot_squares'] = dec.slot_squares()
            ok3, i3 = dec.k0_3(ts)
            rec['K0_3_narrow'] = bool(ok3)
            # Lemma R's cap is s(|cos|+|sin|)-1: WINDOW-DEPENDENT, so the honest
            # test at these out-of-window points uses the widened side.
            ok3w, i3w = dec.k0_3(ts, s_hi=max(A.S_HI, side + 1e-6))
            rec['K0_3'] = bool(ok3w)
            rec['K0_3_info'] = {a: (list(b) if isinstance(b, (list, tuple)) else b)
                                for a, b in i3w.items()}
            rec['K0_3_narrow_info'] = {
                a: (list(b) if isinstance(b, (list, tuple)) else b)
                for a, b in i3.items()}
            if not rec['K0_1']:
                alarms.append((r['tag'], 'K0-1 FAILS (slot squares %s) on an '
                               'A85-k0 point' % rec['slot_squares']))
            if not ok3w:
                alarms.append((r['tag'], 'K0-3 FAILS with the WIDENED cap: %s'
                               % i3w.get('reason')))
        out.append(rec)
        if (c + 1) % 25 == 0:
            print('  %d / %d' % (c + 1, len(tight)), flush=True)

    def hist(key):
        h = defaultdict(int)
        for r in out:
            if key in r:
                h[r[key]] += 1
        return {str(a): h[a] for a in sorted(h)}

    ok = [r for r in out if 'k_H' in r]
    summ = dict(
        n_tight=len(tight), n_analysed=len(ok),
        k_H_hist=hist('k_H'), m_H_hist=hist('m_H'), chi_hist=hist('chi'),
        E_hist=hist('E'), F_hist=hist('F'), d_H_hist=hist('d_H'),
        sigma_range=[min(r['sigma'] for r in out), max(r['sigma'] for r in out)],
        n_rigid_possible=sum(1 for r in ok if r.get('rigid_possible')),
        n_identity_ok=sum(1 for r in ok if r.get('identity_ok')),
        T1_failures=sum(1 for r in ok if not all(r['T1'].values())),
        n_tilt_feasible=sum(1 for r in ok if r.get('tilt_feasible')),
        n_K0_1_pass=sum(1 for r in ok if r.get('K0_1')),
        n_K0_3_pass=sum(1 for r in ok if r.get('K0_3')),
        n_K0_3_pass_narrow_window=sum(1 for r in ok if r.get('K0_3_narrow')),
        n_planar_G_fail=sum(1 for r in ok
                            if not r.get('F0_G_narrow', {}).get('L4b_planar',
                                                                True)),
        planar_G_fail_tags=[r['tag'] for r in ok
                            if not r.get('F0_G_narrow', {}).get('L4b_planar',
                                                                True)],
        tilt_infeasible_tags=[(r['tag'], r.get('tilt_reason')) for r in ok
                              if not r.get('tilt_feasible')],
        n_planar_G_fail_no_degenerate=sum(
            1 for r in ok if not r.get('L4b_planar_no_degenerate', True)),
        sigma_of_alarmed=sorted(set(round(r['sigma'], 6) for r in ok
                                    if (not r.get('K0_3', True))
                                    or (not r.get('tilt_feasible', True))
                                    or (not r.get('F0_G_narrow', {})
                                        .get('L4b_planar', True)))),
        n_at_sigma_4=sum(1 for r in ok if abs(r['sigma'] - 4.0) < 1e-6),
        n_degenerate_corner_corner=sum(1 for r in ok
                                       if r.get('degenerate_corner_corner')),
        n_narrow_L5a_or_N1_fail=sum(1 for r in ok
                                    if r.get('narrow_L5a_or_N1_fail')),
        n_alarms=len(alarms),
        alarms=[list(a) for a in alarms[:200]],
        alarm_kinds={k: v for k, v in sorted(
            {a[1].split('(')[0].strip(): 0 for a in alarms}.items())},
    )
    kinds = defaultdict(int)
    for a in alarms:
        kinds[a[1].split('(')[0].split(':')[0].strip()] += 1
    summ['alarm_kinds'] = dict(kinds)
    with open(os.path.join(RES, 'd6_checks.json'), 'w') as fh:
        json.dump(dict(summary=summ, records=out), fh, indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == '__main__':
    main()
