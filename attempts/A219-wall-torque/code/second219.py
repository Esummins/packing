"""A219 addendum 2b -- second-order test at the four-crowd witnesses (8 HELD + 185 CROWD).
At a first-order stationary point (lam0 = 1 on the variant's rows) a direction y with e_s.y = 0 that is
first-order feasible (modes219: walls / external rows rate >= 0, every touching pair has an axis whose active
rows have rate >= 0) is a ZERO MODE.  Along x(t) = x* + t y + t^2 w/2 the side changes by t^2 (e_s.w)/2 and the
tight selected rows need grad g_r . w >= - y^T H_r y, so
    v2(y) = min { e_s.w : grad g_r . w >= - y^T H_r y, r tight }  = max over the multiplier polytope of
    y^T Hess(L) y   (LP duality: the reduced Hessian of the side on the mode).
v2(y) < 0 or unbounded below: the side DECREASES at second order along a feasible curve -- the point is not a
local minimum, hence no sigma-minimiser (Lemma STRUT / Theorem SO, docs/proofs/wall_torque.md s.5).
Candidates: STRUT rotations (a square whose loads are exactly two point contacts, about either, both senses),
eigen-modes of the reduced Hessian at the LP multiplier; unloaded squares complete the mode by LP.
Variants: bounded (all active rows), loaded_ext (walls + pairs + the LOADED tilt-bound / crowd rows only:
the load path as a constraint system), free (walls + pairs).
    python second219.py [--only RID]   -> results/second219.jsonl, prints the summary
"""
import json
import os
import sys
import time

import numpy as np
from scipy.linalg import null_space

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rows219 as R                        # noqa: E402
import ring219 as RING                     # noqa: E402
import modes219 as MO                      # noqa: E402
import geom217 as G                        # noqa: E402

OUT = os.path.join(RING.ATT, 'results', 'second219.jsonl')
LOAD_TOL = 1e-6
V2_TOL = 1e-7
VARIANTS = ('bounded', 'loaded_ext', 'core', 'free')


def contact_points(z, rows, lam, i):
    """loaded point loads on square i as {label: point}; external rows give point None."""
    q = G.corners(z)
    pts = {}
    for k, r in enumerate(rows):
        if lam[k] <= LOAD_TOL:
            continue
        if r['kind'] == 'wall' and r['i'] == i:
            pts['wall ' + r['wall']] = q[i, r['corner']]
        elif r['kind'] == 'edge' and i in (r['i'], r['j']):
            j = r['j'] if r['i'] == i else r['i']
            pts['sq %d' % j] = q[r['i'], r['corner']]
        elif r['kind'] in ('tiltbound', 'crowd') and r['i'] == i:
            pts[r['kind'] + ' %d' % k] = None
    return pts


def rotation_mode(z, i, P, omega):
    y = np.zeros(R.NV)
    y[3 * i:3 * i + 2] = omega * R.jrot(z[3 * i:3 * i + 2] - P)
    y[3 * i + 2] = omega
    return y


def contact_points_all(z, rows, i):
    """every active contact point of square i (loaded or not): {label: point}."""
    q = G.corners(z)
    pts = {}
    for r in rows:
        if r['kind'] == 'wall' and r['i'] == i:
            pts['wall ' + r['wall']] = q[i, r['corner']]
        elif r['kind'] == 'edge' and i in (r['i'], r['j']):
            j = r['j'] if r['i'] == i else r['i']
            p = q[r['i'], r['corner']]
            pts['sq %d @(%.3f,%.3f)' % (j, p[0], p[1])] = p
    return pts


def strut_candidates(z, rows, lam):
    """rotations of every square about every one of its active contact points, both senses; a candidate
    is labelled STRUT when the square's loads (multiplier lam) are exactly two point loads."""
    out = []
    for i in range(G.N):
        loads = contact_points(z, rows, lam, i)
        strut = len(loads) == 2 and all(p is not None for p in loads.values())
        for lab, P in contact_points_all(z, rows, i).items():
            for omega in (1.0, -1.0):
                out.append({'square': i, 'pivot': lab, 'sense': 'ccw' if omega > 0 else 'cw', 'strut': strut,
                            'other': ','.join(sorted(l for l in loads if l != lab)), 'y0': rotation_mode(z, i, P, omega),
                            'fixed': [3 * i, 3 * i + 1, 3 * i + 2]})
    return out


def eigen_candidates(A, Hs, rows, lam, nmax=6):
    L = [k for k in range(len(lam)) if lam[k] > LOAD_TOL]
    B = np.vstack([A[L], np.eye(R.NV)[R.S_IDX][None, :]]) if L else np.eye(R.NV)[R.S_IDX][None, :]
    Z = null_space(B)
    if Z.shape[1] == 0:
        return []
    H = -sum(lam[k] * Hs[k] for k in L) if L else np.zeros((R.NV, R.NV))
    Hz = Z.T @ H @ Z
    ev, V = np.linalg.eigh((Hz + Hz.T) / 2)
    fixed = [3 * i + a for i in MO.loaded_squares(rows, lam) for a in range(3)]
    out = []
    for a in np.argsort(ev)[:nmax]:
        if ev[a] > -1e-9:
            break
        for sg in (1.0, -1.0):
            out.append({'square': None, 'pivot': 'eigen', 'sense': '%s ev %.3e' % ('+' if sg > 0 else '-', ev[a]),
                        'other': '', 'y0': sg * (Z @ V[:, a]), 'fixed': fixed})
    return out


def variant_rows(rows_all, lam_all, variant):
    """bounded: every active row; loaded_ext: walls + pairs + the loaded external rows; core: loaded_ext
    restricted to the loaded squares (the rattlers' rows dropped: a rattler is unloaded and, for a GLOBAL
    minimiser, may be moved anywhere in its free region -- a caged rattler blocking a mode is reported);
    free: walls + pairs."""
    if variant == 'bounded':
        return list(range(len(rows_all)))
    if variant == 'free':
        return [k for k, r in enumerate(rows_all) if r['kind'] in ('wall', 'edge')]
    idx = [k for k, r in enumerate(rows_all) if r['kind'] in ('wall', 'edge') or (lam_all is not None and lam_all[k] > LOAD_TOL)]
    if variant == 'core' and lam_all is not None:
        core = MO.loaded_squares(rows_all, lam_all)
        idx = [k for k in idx if rows_all[k]['i'] in core and (rows_all[k]['kind'] != 'edge' or rows_all[k]['j'] in core)]
    return idx


def test_variant(z, rows_all, lam_all, variant):
    idx = variant_rows(rows_all, lam_all, variant)
    rows = [rows_all[k] for k in idx]
    vals, A, Hs = R.system(z, rows)
    lam, lam0 = R.feasible(A)
    res = {'variant': variant, 'n_rows': len(rows), 'stationary': lam0 == 1.0}
    if lam0 != 1.0:
        res['note'] = 'no lam0 = 1 multiplier: a first-order descent direction exists (Gordan); second order moot'
        return res
    groups = MO.group_rows(rows)
    cands = strut_candidates(z, rows, lam) + eigen_candidates(A, Hs, rows, lam)
    modes = []
    for c in cands:
        m = MO.make_mode(A, Hs, groups, c['y0'], c['fixed'])
        if m is None:
            continue
        lam_sel, lam0_sel = R.feasible(A[m['sel']])
        md = {'sel_fj': lam0_sel,'square': c['square'], 'pivot': c['pivot'], 'sense': c['sense'], 'other': c['other'],
              'strut': c.get('strut', False), 'v2': m['v2'], 'status': m['status'], 'n_tight': len(m['E']),
              'n_open': m['n_open'], 'moving': m['moving'], 'sel_stationary': lam0_sel == 1.0}
        if lam0_sel == 1.0 and m['w'] is not None and m['v2'] < -V2_TOL:
            md['curve'] = MO.curve_check(z, rows, m['y'], m['w'])
            tol3 = lambda c_: -(50.0 * c_['t'] ** 3 + 1e-12)             # third-order remainder of the curve
            md['curve_ok'] = all(c_['min_wall'] > tol3(c_) and c_['min_pair_gap'] > tol3(c_)
                                 and c_['min_ext_row'] > tol3(c_) and c_['ds'] < 0 for c_ in md['curve'])
        modes.append(md)
    res['n_rot_candidates'] = sum(1 for c in cands if c['square'] is not None)
    res['n_strut_candidates'] = sum(1 for c in cands if c.get('strut'))
    res['n_strut_modes'] = sum(1 for m in modes if m['strut'])
    res['n_eigen_candidates'] = sum(1 for c in cands if c['square'] is None)
    res['n_modes'] = len(modes)
    res['modes'] = modes
    res['saddle'] = any(m['v2'] < -V2_TOL for m in modes)
    res['first_order_other_selection'] = any(not m['sel_stationary'] for m in modes)
    res['not_fj_other_selection'] = any(m['sel_fj'] is None for m in modes)
    res['saddle_second_order'] = any(m['sel_stationary'] and m['v2'] < -V2_TOL for m in modes)
    res['saddle_verified'] = any(m.get('curve_ok') for m in modes)
    if modes:
        best = min(modes, key=lambda m: m['v2'])
        res['min_v2'] = best['v2']
        res['worst_mode'] = {k: best[k] for k in ('square', 'pivot', 'sense', 'other', 'status', 'moving')}
    return res


def verify_ring(w):
    """the PI's numbers on rand_0_0569|t20: square 6 is a two-force strut between 4 and 7; the rotation
    about the 7-contact by 1 mrad opens the floor gap, keeps the 7 contact, closes on 4 at second order."""
    rows, z = R.witness_rows(w)
    vals, A, Hs = R.system(z, rows)
    lam, lam0 = R.feasible(A)
    pts = contact_points(z, rows, lam, 6)
    out = {'loads_on_6': sorted(pts)}
    if 'sq 4' in pts and 'sq 7' in pts:
        P4, P7 = pts['sq 4'], pts['sq 7']
        F4 = sum(lam[k] * (1 if r['i'] == 6 else -1) * G.normals(z)[r['j'], r['edge']]
                 for k, r in enumerate(rows) if r['kind'] == 'edge' and {r['i'], r['j']} == {4, 6} and lam[k] > LOAD_TOL)
        d = P4 - P7
        out.update({'moment_of_F4_about_P7': float(d[0] * F4[1] - d[1] * F4[0]), 'F4_on_6': [float(v) for v in F4],
                    'floor_lam_6': float(sum(lam[k] for k, r in enumerate(rows) if r['kind'] == 'wall' and r['i'] == 6)),
                    'P4': [float(v) for v in P4], 'P7': [float(v) for v in P7]})
        for omega, name in ((-1e-3, 'cw'), (1e-3, 'ccw')):
            z2 = z + rotation_mode(z, 6, P7, omega)
            gaps = G.pair_gaps(z2)
            out['rot_1mrad_' + name] = {'floor_gap': float(G.corners(z2)[6][:, 1].min()),
                                        'gap_to_4': float(gaps[(4, 6)]), 'gap_to_7': float(gaps[(6, 7)]),
                                        'gap_to_0': float(gaps[(0, 6)])}
    return out


def main():
    only = sys.argv[sys.argv.index('--only') + 1] if '--only' in sys.argv else None
    t0 = time.time()
    ws = [w for w in RING.four_crowds() if only is None or only in (w['wid'], w['rid'])]
    res = []
    with open(OUT if only is None else os.devnull, 'w', encoding='utf-8') as f:
        for w in ws:
            rows, z = R.witness_rows(w)
            _, A_all, _ = R.system(z, rows)
            lam_all, lam0_all = R.feasible(A_all)
            o = {'wid': w['wid'], 'cls': w['cls'], 'rid': w['rid'], 's': float(z[R.S_IDX]), 'bounded_lam0': lam0_all}
            for v in VARIANTS:
                o[v] = test_variant(z, rows, lam_all, v)
            if w['rid'] == 'rand_0_0569|t20':
                o['ring_check'] = verify_ring(w)
                print(json.dumps(o['ring_check'], indent=1, default=float))
                for m in o['loaded_ext'].get('modes', []):
                    print({k: (round(v, 6) if isinstance(v, float) else v) for k, v in m.items()})
            o['t_s'] = round(time.time() - t0, 2)
            res.append(o)
            f.write(json.dumps(o, default=float) + '\n')
    print('%d witnesses, %.1f s' % (len(res), time.time() - t0))
    for cls in ('HELD', 'CROWD'):
        rs = [o for o in res if o['cls'] == cls]
        for v in VARIANTS:
            b = [o[v] for o in rs]
            print('%-5s %3d %-10s stationary %3d | >= 1 zero mode %3d (strut modes in %d) | EXCLUDED %3d: 2nd-order saddle %d, '
                  'not KKT under another selection %d (not even FJ %d) | curve-verified saddles %d' % (cls, len(rs), v, sum(x['stationary'] for x in b),
                  sum(x.get('n_modes', 0) > 0 for x in b), sum(x.get('n_strut_modes', 0) > 0 for x in b),
                  sum(x.get('saddle', False) for x in b), sum(x.get('saddle_second_order', False) for x in b),
                  sum(x.get('first_order_other_selection', False) for x in b), sum(x.get('not_fj_other_selection', False) for x in b),
                  sum(x.get('saddle_verified', False) for x in b)))


if __name__ == '__main__':
    main()
