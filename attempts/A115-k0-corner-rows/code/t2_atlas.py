"""A89 / T2 TASK B: corner-blocker census at the 12 A37/A46 atlas families.

The 12 entries are the GENUINE ones A46 used (families 0,1,2,6,13,14,27,31,
A37-NEW-0..3), listed in attempts/A46-balanced-wedge/results/
atlas_mismatch_audit.json.  Extraction + loadability LP are A46's
(code/task1_audit.py -> A44 eval_atlas.lp_block, lambda_0 = 1 form,
forced = lambda_min > 1e-7, loadable = lambda_max > 1e-7); this driver only adds
the corner-box meeting test and the per-blocker bookkeeping.

Usage: python t2_atlas.py
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

sys.path.insert(0, os.path.join(L.ATT, 'A46-balanced-wedge', 'code'))
sys.path.insert(0, os.path.join(L.ATT, 'A44-fj-maxwell', 'code'))
sys.path.insert(0, os.path.join(L.ATT, 'A37-cp-atlas', 'code'))

import eval_atlas as EA                                       # noqa: E402
import task1_audit as TA                                      # noqa: E402

AUDIT = os.path.join(L.ATT, 'A46-balanced-wedge', 'results',
                     'atlas_mismatch_audit.json')
OUT = os.path.join(L.RESULTS, 't2_blockers_atlas.jsonl')
SUM = os.path.join(L.RESULTS, 't2_summary_atlas.json')


def load_bounds(entry, z):
    """A46 loadability, but keeping the per-row lambda_min / lambda_max."""
    st = EA.build_structure(entry, z)
    cols = EA.col_index(st['core'])
    rows, owner = EA.physical_rows(st, 'fact0')
    A = EA.jac(z, rows, cols)
    lp = EA.lp_block(A, rows, owner, st['k'], np.random.default_rng(EA.SEED))
    used = 'physical'
    if not lp.get('feasible'):
        rows, owner = EA.expanded_rows(st)
        A = EA.jac(z, rows, cols)
        lp = EA.lp_block(A, rows, owner, st['k'], np.random.default_rng(EA.SEED))
        used = 'expanded'
        if not lp.get('feasible'):
            return None, 'infeasible', st
    per = {}
    for k, ow in enumerate(owner):
        if ow[0] == 'wall':
            e = st['wall_edges'][ow[1]]
            key = ('wall', e['i'], e['wall'])
        else:
            e = st['pair_edges'][ow[1]]
            key = ('pair', min(e['i'], e['j']), max(e['i'], e['j']))
        lo = lp['lambda_min'][k]
        hi = lp['lambda_max'][k]
        d = per.setdefault(key, {'lam_min': None, 'lam_max': None, 'n_rows': 0})
        d['n_rows'] += 1
        for f, v in (('lam_min', lo), ('lam_max', hi)):
            if v is not None and not (isinstance(v, float) and math.isnan(v)):
                d[f] = v if d[f] is None else max(d[f], v)
    return per, used, st


def cls_of(per, key):
    if per is None:
        return 'unknown', None, None
    d = per.get(key)
    if d is None:
        return 'absent_from_LP', None, None
    lo, hi = d['lam_min'], d['lam_max']
    tag = ('forced' if (lo is not None and lo > L.LP_TOL)
           else 'loadable' if (hi is not None and hi > L.LP_TOL) else 'unloadable')
    return tag, lo, hi


def analyse(entry, zf, per, lp_used, st):
    x0, y0, sig = L.bbox_sigma(zf)
    s_var = float(zf[33])
    boxes = L.corner_boxes(x0, y0, sig)
    V = L.all_verts(zf)
    corner_of = {}
    for i in range(11):
        for c in L.CORNERS:
            ok, _m = L.meeting(V[i], boxes[c])
            if ok:
                corner_of.setdefault(c, []).append(i)
    tag = 'fam%s' % entry['family_id']
    out = []
    for c in L.CORNERS:
        mates = sorted(corner_of.get(c, []))
        cw = L.CORNER_WALLS[c]
        for i in mates:
            _ok, margin = L.meeting(V[i], boxes[c])
            th = float(zf[3 * i + 2])
            thd = math.degrees(th)
            tilt = L.mis90(thd)
            contacts = []
            lmins, lmaxs = [], []
            n_cw, cw_f, cw_l = set(), False, False
            for w in ('x=0', 'y=0', 'x=s', 'y=s'):
                touch, n_on, mg = L.wall_touch(zf, i, w, s_var)
                if not touch:
                    continue
                st_tag, lo, hi = cls_of(per, ('wall', i, w))
                lmins.append(lo); lmaxs.append(hi)
                contacts.append({'kind': 'wall', 'wall': w,
                                 'n_vertices_on_wall': n_on, 'wall_gap': mg,
                                 'contact': 'flush_edge_on_wall' if n_on >= 2
                                            else 'corner_on_wall',
                                 'is_corner_wall': w in cw,
                                 'load': st_tag, 'lam_min': lo, 'lam_max': hi})
                if w in cw:
                    n_cw.add(w)
                    cw_f = cw_f or st_tag == 'forced'
                    cw_l = cw_l or st_tag in ('forced', 'loadable')
            partners = []
            for p in range(11):
                if p == i:
                    continue
                tp = L.pair_contact_type(zf, min(i, p), max(i, p))
                if tp is None:
                    continue
                partners.append(p)
                st_tag, lo, hi = cls_of(per, ('pair', min(i, p), max(i, p)))
                lmins.append(lo); lmaxs.append(hi)
                contacts.append({'kind': 'pair', 'partner': p,
                                 'pair_type': L.pair_type_wrt(tp, i),
                                 'pair_gap': tp['gap'],
                                 'pair_rel_mismatch_deg': tp['rel_mismatch_deg'],
                                 'load': st_tag, 'lam_min': lo, 'lam_max': hi})
            forced = any(e['load'] == 'forced' for e in contacts)
            loadable = any(e['load'] in ('forced', 'loadable') for e in contacts)
            ghost = bool(L.TILT_POS < tilt < 5.0 and len(n_cw) >= 1
                         and any(p in mates for p in partners))
            cfx, cfy = L.corner_frame_centre(c, float(zf[3 * i]), float(zf[3 * i + 1]),
                                             x0, y0, sig)
            out.append({
                'source': 'A46-atlas-12', 'tag': tag, 'family_id': entry['family_id'],
                'cls': entry['class'], 'lp_used': lp_used,
                'square': i, 'corner': c, 'sigma': sig, 's_var': s_var,
                'theta_rad_exact': str(zf[3 * i + 2]),
                'theta_deg': thd, 'theta_mod90_deg': thd % 90.0,
                'tilt_deg': tilt,
                'tilt_exact_zero': bool(Fraction(zf[3 * i + 2]) == 0)
                                   if isinstance(zf[3 * i + 2], Fraction) else bool(th == 0.0),
                'centre': [float(zf[3 * i]), float(zf[3 * i + 1])],
                'centre_corner_frame': [cfx, cfy],
                'meeting_margin': margin,
                'n_active_rows': len(contacts),
                'is_rattler': len(contacts) == 0 or (i in st['rattlers']),
                'a46_rattler': i in st['rattlers'],
                'loaded_forced': forced, 'loaded_loadable': loadable,
                'n_corner_walls_touched': len(n_cw),
                'corner_walls_touched': sorted(n_cw),
                'corner_wall_forced': cw_f, 'corner_wall_loadable': cw_l,
                'partners': partners,
                'corner_mates': [m for m in mates if m != i],
                'partner_is_corner_mate': [p for p in partners if p in mates],
                'near_flush_ghost': ghost,
                'slot_square': bool(tilt < 1e-7 and
                                    max(abs(cfx - 0.5), abs(cfy - 0.5)) < 1e-6),
                'contacts': contacts})
    return out, {'tag': tag, 'family_id': entry['family_id'], 'cls': entry['class'],
                 's': s_var, 'sigma': sig, 'lp_used': lp_used,
                 'a46_rattlers': sorted(st['rattlers']),
                 'blockers_per_corner': {c: sorted(corner_of.get(c, []))
                                         for c in L.CORNERS}}


def main():
    t00 = time.time()
    print('free commit %.0f MB' % L.free_commit_mb(), flush=True)
    want = set(str(e['family_id'])
               for e in json.load(open(AUDIT))['entries'])
    print('A46 families:', sorted(want), flush=True)
    atlas = EA.load_atlas()
    ents = [e for e in atlas['entries'] if str(e['family_id']) in want]
    print('matched atlas entries: %d' % len(ents), flush=True)
    allrows, pts = [], []
    with open(OUT, 'w') as f:
        for e in ents:
            cert = EA.load_cert(e)
            zf = [Fraction(v) for v in cert['z_center']]
            zfl = [float(v) for v in zf]
            per, used, st = load_bounds(e, zfl)
            br, pt = analyse(e, zf, per, used, st)
            pts.append(pt)
            pt['n_blockers'] = len(br)
            for b in br:
                f.write(json.dumps(b, default=str) + '\n')
            allrows += br
            print(' fam %-10s %-16s s=%.6f lp=%-11s blockers=%d percorner=%s'
                  % (e['family_id'], e['class'], float(zf[33]), used, len(br),
                     {c: len(v) for c, v in pt['blockers_per_corner'].items()}),
                  flush=True)
    extra = {'n_families': len(ents),
             'families_lp_infeasible': [p['tag'] for p in pts
                                        if p['lp_used'] == 'infeasible'],
             'n_slot_squares': sum(1 for r in allrows if r['slot_square']),
             'slot_squares': [{'tag': r['tag'], 'square': r['square'],
                               'corner': r['corner'], 'tilt_deg': r['tilt_deg'],
                               'tilt_exact_zero': r['tilt_exact_zero'],
                               'centre_corner_frame': r['centre_corner_frame']}
                              for r in allrows if r['slot_square']],
             'per_point': pts}
    s = L.summarise(allrows, 'A46 12 genuine atlas families', extra)
    json.dump(s, open(SUM, 'w'), indent=1, default=str)
    print(json.dumps({k: v for k, v in s.items()
                      if k not in ('per_point', 'blockers_tilt_lt_10_wall_view',
                                   'K0_2_violations', 'near_flush_ghosts',
                                   'min_positive_tilt', 'slot_squares')},
                     indent=1, default=str), flush=True)
    print('min_positive_tilt:', json.dumps(
        {k: (None if v is None else {kk: vv for kk, vv in v.items() if kk != 'contacts'})
         for k, v in s['min_positive_tilt'].items()}, indent=1, default=str), flush=True)
    print('slot squares:', extra['n_slot_squares'], flush=True)
    print('ghosts n =', s['near_flush_ghosts']['n'], flush=True)
    print('total %.1f s' % (time.time() - t00), flush=True)


if __name__ == '__main__':
    main()
