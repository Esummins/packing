"""A89 / T2 TASK A: corner-blocker census at A87's 167 certified k0 FJ points.

'certified k0 FJ point at tol 1e-6' = final.k0 true AND the ladder entry with
tol 1e-6 has fj_feasible true, in attempts/A87-drain-flow/results/
cp87_fj_polished.jsonl.  Row construction and contact classification are A87's
(jobs87.active_rows_at_point via fjpolish87.classify + pilot87.grad_matrix),
NOT re-derived.

Usage: python t2_a87.py [probe|run]
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from fractions import Fraction

import numpy as np

import a89lib as L

sys.path.insert(0, os.path.join(L.ATT, 'A87-drain-flow', 'code'))
import t3lib as T                                             # noqa: E402
import pilot87 as P                                           # noqa: E402
import jobs87 as J                                            # noqa: E402
import fjpolish87 as FJ                                       # noqa: E402


def classify_exact(zfrac, tol):
    """jobs87.active_rows_at_point WITHOUT A87's float round-trip.

    fjpolish87.classify maps every coordinate through float() and
    limit_denominator(1e15) first; on a 60-digit exact certificate that
    perturbation (1e-16) makes tangent pairs certainly-overlapping for the
    interval SAT test.  For an exact input we feed the Fractions straight in.
    """
    return J.active_rows_at_point(zfrac, tol)


def grad_exact(zfrac, rows):
    return P.grad_matrix([T._to_iv(v) for v in zfrac], rows)

SRC = os.path.join(L.ATT, 'A87-drain-flow', 'results', 'cp87_fj_polished.jsonl')
OUT = os.path.join(L.RESULTS, 't2_blockers_a87.jsonl')
SUM = os.path.join(L.RESULTS, 't2_summary_a87.json')


def certified():
    recs = [json.loads(ln) for ln in open(SRC) if ln.strip()]
    sel = []
    for r in recs:
        f = r.get('final')
        if not f or not f.get('k0'):
            continue
        e = [x for x in f['ladder'] if x.get('tol') == 1e-6]
        if e and e[0].get('fj_feasible') and r.get('z_polished'):
            sel.append(r)
    return recs, sel


def row_label(r):
    if r['kind'] == 'wall':
        return 'wall(i=%d,c=%d,%s)' % (r['i'], r['corner'], r['wall'])
    if r['kind'] == 'sep':
        return 'sep(o=%d,e=%d,p=%d,k=%d)' % (r['o'], r['e'], r['p'], r['k'])
    return 'dom(o=%d,e=%d,p=%d,k=%d,m=%d)' % (r['o'], r['e'], r['p'], r['k'], r['m'])


def row_squares(r):
    return (r['i'],) if r['kind'] == 'wall' else (r['o'], r['p'])


def analyse(tag, zfrac, meta, exact=False):
    """-> (blocker rows, point record)."""
    cls_fn = classify_exact if exact else FJ.classify
    grd_fn = grad_exact if exact else FJ.gradA
    zf = [float(v) for v in zfrac]
    x0, y0, sig = L.bbox_sigma(zf)
    boxes = L.corner_boxes(x0, y0, sig)
    V = L.all_verts(zf)
    s_var = float(zfrac[33])

    rows, info = cls_fn(zfrac, L.CONTACT_TOL)
    pt = {'tag': tag, 'sigma': sig, 's_var': s_var, 'origin': [x0, y0]}
    pt.update({k: info.get(k) for k in
               ('point_infeasible', 'point_reason', 'n_wall_active',
                'n_contact_pairs', 'n_pairs_no_consistent_selection')})
    if rows is None:
        pt['rows'] = None
        return [], pt
    A = grd_fn(zfrac, rows)
    lb = L.lam_bounds(A)
    lb46 = L.lam_bounds_a46(A)
    pt['m_active'] = len(rows)
    pt['lp_feasible'] = lb.get('feasible')
    pt['lp_a46_feasible'] = lb46.get('feasible')
    pt['lam0_min'] = lb.get('lam0_min')
    pt['lam0_max'] = lb.get('lam0_max')
    pt['lam0_zero_branch'] = lb.get('lam0_zero_branch')

    # rows incident to each square
    inc = {i: [] for i in range(11)}
    for k, r in enumerate(rows):
        for i in row_squares(r):
            inc[i].append(k)

    def bnd(k):
        lo = lb.get('lam_min', [None] * len(rows))[k] if lb.get('feasible') else None
        hi = lb.get('lam_max', [None] * len(rows))[k] if lb.get('feasible') else None
        lo46 = lb46.get('lam_min', [None] * len(rows))[k] if lb46.get('feasible') else None
        hi46 = lb46.get('lam_max', [None] * len(rows))[k] if lb46.get('feasible') else None
        return lo, hi, lo46, hi46

    # ------- which squares meet which corner box
    blockers = []
    corner_of = {}
    for i in range(11):
        for c in L.CORNERS:
            ok, margin = L.meeting(V[i], boxes[c])
            if ok:
                corner_of.setdefault(c, []).append(i)
    pt['blockers_per_corner'] = {c: sorted(corner_of.get(c, [])) for c in L.CORNERS}

    for c in L.CORNERS:
        mates = sorted(corner_of.get(c, []))
        for i in mates:
            _ok, margin = L.meeting(V[i], boxes[c])
            th = float(zfrac[3 * i + 2])
            thd = math.degrees(th)
            tilt = L.mis90(thd)
            exact0 = (Fraction(zfrac[3 * i + 2]) == 0) if isinstance(
                zfrac[3 * i + 2], Fraction) else (th == 0.0)
            ks = inc[i]
            lmins = [bnd(k)[0] for k in ks]
            lmaxs = [bnd(k)[1] for k in ks]
            forced, loadable = L.cls_from_bounds(lmins, lmaxs)
            contacts = []
            cw = L.CORNER_WALLS[c]
            n_cw, cw_f, cw_l = set(), False, False
            for k in ks:
                r = rows[k]
                lo, hi, lo46, hi46 = bnd(k)
                e = {'row': row_label(r), 'kind': r['kind'],
                     'lam_min': lo, 'lam_max': hi,
                     'lam_min_a46': lo46, 'lam_max_a46': hi46,
                     'forced': bool(lo is not None and lo > L.LP_TOL),
                     'loadable': bool(hi is not None and hi > L.LP_TOL)}
                if r['kind'] == 'wall':
                    _t, n_on, mg = L.wall_touch(zf, i, r['wall'], s_var)
                    e.update({'wall': r['wall'], 'n_vertices_on_wall': n_on,
                              'wall_gap': mg,
                              'contact': 'flush_edge_on_wall' if n_on >= 2
                                         else 'corner_on_wall',
                              'is_corner_wall': r['wall'] in cw})
                    if r['wall'] in cw:
                        n_cw.add(r['wall'])
                        cw_f = cw_f or e['forced']
                        cw_l = cw_l or e['loadable']
                else:
                    p = r['p'] if r['o'] == i else r['o']
                    tp = L.pair_contact_type(zf, min(i, p), max(i, p))
                    e.update({'partner': p, 'pair_type': L.pair_type_wrt(tp, i),
                              'pair_gap': (tp or {}).get('gap'),
                              'pair_rel_mismatch_deg': (tp or {}).get('rel_mismatch_deg')})
                contacts.append(e)
            partners = sorted(set(e['partner'] for e in contacts if 'partner' in e))
            ghost = bool(L.TILT_POS < tilt < 5.0 and len(n_cw) >= 1
                         and any(p in mates for p in partners))
            cfx, cfy = L.corner_frame_centre(c, float(zfrac[3 * i]),
                                             float(zfrac[3 * i + 1]), x0, y0, sig)
            blockers.append({
                'source': 'A87-167', 'tag': tag, 'square': i, 'corner': c,
                'sigma': sig, 's_var': s_var,
                'theta_rad_exact': str(zfrac[3 * i + 2]),
                'theta_deg': thd, 'theta_mod90_deg': thd % 90.0,
                'tilt_deg': tilt, 'tilt_exact_zero': bool(exact0),
                'centre': [float(zfrac[3 * i]), float(zfrac[3 * i + 1])],
                'centre_corner_frame': [cfx, cfy],
                'meeting_margin': margin,
                'n_active_rows': len(ks),
                'is_rattler': len(ks) == 0,
                'loaded_forced': forced, 'loaded_loadable': loadable,
                'n_corner_walls_touched': len(n_cw),
                'corner_walls_touched': sorted(n_cw),
                'corner_wall_forced': cw_f, 'corner_wall_loadable': cw_l,
                'partners': partners,
                'corner_mates': [m for m in mates if m != i],
                'partner_is_corner_mate': [p for p in partners if p in mates],
                'near_flush_ghost': ghost,
                'contacts': contacts})
    return blockers, pt


def main(argv):
    t00 = time.time()
    fc = L.free_commit_mb()
    print('free commit %.0f MB' % fc, flush=True)
    recs, sel = certified()
    print('cp87 lines %d ; certified k0 FJ at tol 1e-6 = %d' % (len(recs), len(sel)),
          flush=True)
    lim = int(argv[0]) if argv and argv[0].isdigit() else None
    if lim:
        sel = sel[:lim]
    allrows = []
    pts = []
    with open(OUT, 'w') as f:
        for n, r in enumerate(sel, 1):
            t0 = time.time()
            z = [T.str_frac(x) for x in r['z_polished']]
            br, pt = analyse(r['tag'], z, r)
            pt['sigma_polished_a87'] = r['sigma_polished']
            pt['secs'] = time.time() - t0
            pt['n_blockers'] = len(br)
            pts.append(pt)
            for b in br:
                b['sigma_polished_a87'] = r['sigma_polished']
                f.write(json.dumps(b) + '\n')
            allrows += br
            if n % 10 == 0 or n == len(sel):
                print('[%6.1fs] %3d/%3d %-10s blockers=%d m=%s %.1fs'
                      % (time.time() - t00, n, len(sel), r['tag'], len(br),
                         pt.get('m_active'), pt['secs']), flush=True)
    extra = {'n_certified_points_confirmed': len(sel),
             'cp87_lines': len(recs),
             'points_with_no_consistent_selection':
                 [p['tag'] for p in pts
                  if (p.get('n_pairs_no_consistent_selection') or 0) > 0],
             'points_lp_infeasible': [p['tag'] for p in pts if not p.get('lp_feasible')],
             'points_with_lam0_zero_branch':
                 [p['tag'] for p in pts if p.get('lam0_zero_branch')],
             'per_point': pts}
    s = L.summarise(allrows, 'A87 167 certified k0 FJ points (tol 1e-6)', extra)
    json.dump(s, open(SUM, 'w'), indent=1, default=str)
    print('blockers %d -> %s' % (len(allrows), OUT), flush=True)
    print(json.dumps({k: v for k, v in s.items()
                      if k not in ('per_point', 'blockers_tilt_lt_10_wall_view',
                                   'K0_2_violations', 'near_flush_ghosts',
                                   'min_positive_tilt')},
                     indent=1, default=str), flush=True)
    print('min_positive_tilt:', json.dumps(
        {k: (None if v is None else {kk: vv for kk, vv in v.items() if kk != 'contacts'})
         for k, v in s['min_positive_tilt'].items()}, indent=1, default=str), flush=True)
    print('ghosts n =', s['near_flush_ghosts']['n'], flush=True)
    print('total %.1f s' % (time.time() - t00), flush=True)


if __name__ == '__main__':
    main(sys.argv[1:])
