"""A235 -- the second-order test over the FULL ROLLING SUBSPACE at a tilted vertex-on-vertex contact (n = 11
witnesses, rows219's analytic Hessians, modes219's selection + completion + v2 LP, Theorem SO).
At a VV contact of squares A, B at the common vertex P the two rows g_A (B's vertex on A's separating edge
line) and g_B (A's vertex on B's) are EXACTLY zero along every rotation of A about P and of B about P: the
2-dimensional rolling family y(phi) = cos(phi) rho_A + sin(phi) rho_B keeps the contact.  For each selection
S_A (row g_B dropped), S_B (g_A dropped) and the corner system S_AB (both kept), every phi on the circle is
completed by LP (the other squares move for free), tested for first-order feasibility, and scored
v2(y) = min { e_s.w : grad g_r.w >= -y^T H_r y, r tight } = max over the multiplier polytope of y^T Hess L y;
v2 < 0 on a stationary selection = the side decreases at second order along a feasible curve = not a local
minimiser (curve-verified).  The witness's external rows (tilt bound / crowd) are KEPT: the point is tested as
a local optimum of the problem it was found in.  Then the measured relaxation: SLSQP from the descent curve.
    python roll235.py [--only RID] [--no-drain]   -> results/novv235.jsonl
"""
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vv235 as V             # noqa: E402
import stress234 as ST        # noqa: E402
import rows219 as R           # noqa: E402
import modes219 as MO         # noqa: E402
import second219 as S2        # noqa: E402
import geom217 as G           # noqa: E402
import opt217 as O            # noqa: E402
import crowd217 as C          # noqa: E402

OUT = os.path.join(V.ATT, 'results', 'novv235.jsonl')
V2_TOL = 1e-7
PHI_COARSE = 5.0
PHI_FINE = 0.25


def rot_mode(z, i, P):
    return S2.rotation_mode(z, i, P, 1.0)


def contact_terms(z, rows, ka, kb, P, i, j):
    """the VV rows' curvature along the pure rotations: y_j^T H_A y_j = h_B = n_e.(c_B - P) > 0,
    y_j^T H_B y_j = 1/2; y_i^T H_A y_i = 1/2, y_i^T H_B y_i = h_A (the inverted-pendulum terms)."""
    yi, yj = rot_mode(z, i, P), rot_mode(z, j, P)
    HA, HB = R.row_hessian(z, rows[ka]), R.row_hessian(z, rows[kb])
    n_e = G.normals(z)[rows[ka]['j'], rows[ka]['edge']]
    n_f = G.normals(z)[rows[kb]['j'], rows[kb]['edge']]
    cA, cB = z[3 * i:3 * i + 2], z[3 * j:3 * j + 2]
    return {'yj_HA_yj': float(yj @ HA @ yj), 'h_B': float(n_e @ (cB - P)), 'yj_HB_yj': float(yj @ HB @ yj),
            'yi_HB_yi': float(yi @ HB @ yi), 'h_A': float(n_f @ (cA - P)), 'yi_HA_yi': float(yi @ HA @ yi),
            'rows_exact_zero_along_rotation': max(abs(R.row_gj(z + 1e-3 * yj + 0.5e-6 * np.concatenate(
                [np.zeros(3 * j), -(cB - P), [0.0], np.zeros(R.NV - 3 * j - 3)]), rows[k])[0]) for k in (ka, kb))}


def scan(z, rows_v, A, Hs, i, j, P, phis):
    groups = MO.group_rows(rows_v)
    yi, yj = rot_mode(z, i, P), rot_mode(z, j, P)
    fixed = [3 * i, 3 * i + 1, 3 * i + 2, 3 * j, 3 * j + 1, 3 * j + 2]
    out = []
    for phi in phis:
        y0 = math.cos(math.radians(phi)) * yi + math.sin(math.radians(phi)) * yj
        m = MO.make_mode(A, Hs, groups, y0, fixed)
        if m is None:
            out.append({'phi': phi, 'feasible': False})
            continue
        lam_sel, lam0_sel = R.feasible(A[m['sel']])
        out.append({'phi': phi, 'feasible': True, 'v2': m['v2'], 'status': m['status'], 'n_tight': len(m['E']),
                    'n_open': m['n_open'], 'moving': m['moving'], 'sel_fj': lam0_sel, 'y': m['y'], 'w': m['w']})
    return out


def test_selection(z, rows, ka, kb, i, j, P, variant, drain_fn=None):
    drop = {'S_A': [kb], 'S_B': [ka], 'S_AB': []}[variant]
    idx = [k for k in range(len(rows)) if k not in drop]
    rows_v = [rows[k] for k in idx]
    _, A, Hs = R.system(z, rows_v)
    lam, lam0 = R.feasible(A)
    res = {'variant': variant, 'n_rows': len(rows_v), 'fj': 'KKT' if lam0 == 1.0 else ('self-stress' if lam0 == 0.0 else 'none')}
    if lam0 != 1.0:
        return res
    ka_v = idx.index(ka) if ka in idx else None
    kb_v = idx.index(kb) if kb in idx else None
    res['lam_A'] = float(lam[ka_v]) if ka_v is not None else 0.0
    res['lam_B'] = float(lam[kb_v]) if kb_v is not None else 0.0
    sc = scan(z, rows_v, A, Hs, i, j, P, np.arange(0.0, 360.0, PHI_COARSE))
    feas = [m for m in sc if m['feasible']]
    res['n_phi'] = len(sc)
    res['n_feasible'] = len(feas)
    res['pure'] = {str(int(p)): (next(m for m in sc if m['phi'] == p)['v2'] if next(m for m in sc if m['phi'] == p)['feasible'] else None)
                   for p in (0.0, 90.0, 180.0, 270.0)}
    if not feas:
        res['verdict'] = 'ROLLING-BLOCKED'
        return res
    best = min(feas, key=lambda m: m['v2'])
    fine = scan(z, rows_v, A, Hs, i, j, P, np.arange(best['phi'] - PHI_COARSE, best['phi'] + PHI_COARSE + 1e-9, PHI_FINE))
    ffeas = [m for m in fine if m['feasible']]
    if ffeas:
        best = min(ffeas + [best], key=lambda m: m['v2'])
    res['min_v2'] = best['v2']
    res['phi_min'] = float(best['phi'] % 360.0)
    res['status_min'] = best['status']
    res['moving_min'] = best['moving']
    res['sel_fj_min'] = best['sel_fj']
    res['feasible_arcs'] = [float(m['phi']) for m in sc if m['feasible']]
    res['not_kkt_other_selection'] = any(m['sel_fj'] != 1.0 for m in feas)
    if best['v2'] < -V2_TOL and best['sel_fj'] == 1.0 and best['w'] is not None:
        cur = MO.curve_check(z, rows_v, best['y'], best['w'])
        ok = all(c['min_wall'] > -(50 * c['t'] ** 3 + 1e-12) and c['min_pair_gap'] > -(50 * c['t'] ** 3 + 1e-12)
                 and c['min_ext_row'] > -(50 * c['t'] ** 3 + 1e-12) and c['ds'] < 0 for c in cur)
        res['curve'] = cur
        res['curve_ok'] = ok
        res['verdict'] = 'SADDLE' + ('-verified' if ok else '-unverified')
        if drain_fn is not None and ok:
            res['drain'] = drain_fn(z + 1e-2 * best['y'] + 0.5e-4 * best['w'])
    elif best['v2'] < -V2_TOL:
        res['verdict'] = 'SADDLE-other-selection' if best['sel_fj'] != 1.0 else 'SADDLE-unbounded-w'
    else:
        res['verdict'] = 'STABLE-on-rolling-plane'
    return res


def make_drain(w):
    """SLSQP relaxation of the witness's own problem (bounded tilt / crowd rows) from a perturbed point; reports
    the new side and the type of the pair's contact afterwards."""
    tmin = math.radians(w['tmin_deg']) if w.get('tmin_deg') is not None and w['cls'] in ('HELD', 'BOXK0') else None
    extra = None
    if w.get('crowd_delta') is not None and w['cls'] == 'CROWD':
        desq = {cn: [int(i) for i in w['designated'][cn]] for cn in G.CORNER_NAMES}
        extra = C.make_extra_fixed(desq, w['crowd_delta'])

    def drain(z0, pair=None):
        z1, hist = O.local_opt(z0, tmin=tmin, extra=extra, max_outer=20)
        return {'s_after': float(z1[R.S_IDX]), 'ds': float(z1[R.S_IDX] - w['z'][R.S_IDX]), 'outer': len(hist),
                'min_pair_gap': float(min(G.pair_gaps(z1).values())), 'z_after': [float(v) for v in z1]}
    return drain


def contact_type_after(w, z1, i, j):
    ww = ST.w11('after', w['cls'], z1)
    cts = V.pair_contacts(ww)
    d = cts.get((min(i, j), max(i, j)))
    return d['type'] if d else 'open (gap %.2e)' % G.pair_gaps(z1)[(min(i, j), max(i, j))]


def main():
    ST.set_priority()
    only = sys.argv[sys.argv.index('--only') + 1] if '--only' in sys.argv else None
    do_drain = '--no-drain' not in sys.argv
    t0 = time.time()
    res = []
    with open(OUT if only is None else os.devnull, 'w', encoding='utf-8') as f:
        for l in open(ST.WIT, encoding='utf-8'):
            raw = json.loads(l)
            if raw['cls'] not in ('HELD', 'CROWD'):
                continue
            if only is not None and only not in (raw['wid'], raw['rid']):
                continue
            w = ST.from_w217(raw)
            w['rid'] = raw['rid']
            w.update({k: raw.get(k) for k in ('tmin_deg', 'crowd_delta', 'designated')})
            cen, _ = V.analyse(w)
            for e in cen['vv']:
                if not e['loadable']:
                    continue
                z, rows = w['z'], w['rows']
                i, j = e['pair']
                P = np.array(e['P'])
                o = {'wid': raw['wid'], 'rid': raw['rid'], 'cls': raw['cls'], 's': float(z[R.S_IDX]), 'pair': [i, j],
                     'P': e['P'], 'tilt_gap_deg': e['tilt_gap_deg'], 'tilts_deg': [math.degrees(z[3 * i + 2]), math.degrees(z[3 * j + 2])],
                     'load_range': e['load_range'], 'necessarily_loaded': e['necessarily_loaded'], 'first_order': e['first_order'],
                     'sel_A': e['sel_A'], 'sel_B': e['sel_B'], 'terms': contact_terms(z, rows, e['rowA'], e['rowB'], P, i, j)}
                dr = make_drain(w) if do_drain else None
                for var in ('S_A', 'S_B', 'S_AB'):
                    o[var] = test_selection(z, rows, e['rowA'], e['rowB'], i, j, P, var, dr)
                    if 'drain' in o[var]:
                        o[var]['drain']['pair_after'] = contact_type_after(w, np.array(o[var]['drain']['z_after']), i, j)
                        del o[var]['drain']['z_after']
                vs = [o[v]['verdict'] for v in ('S_A', 'S_B') if 'verdict' in o[v]]
                fj = [o[v]['fj'] for v in ('S_A', 'S_B')]
                o['verdict'] = ('EXCL-1 (not FJ under a selection)' if 'none' in fj else
                                'EXCL-2 (saddle on the rolling plane)' if any(v.startswith('SADDLE-verified') for v in vs) else
                                'EXCL-2? (saddle, unverified / other selection)' if any(v.startswith('SADDLE') for v in vs) else
                                'SURVIVES (loadable, both selections KKT, rolling stable or blocked)')
                o['t_s'] = round(time.time() - t0, 1)
                res.append(o)
                f.write(json.dumps(o, default=float) + '\n')
                print('%s %s pair %s tilt-gap %.1f load %s | %s | S_A %s S_B %s S_AB %s' % (
                    raw['wid'], raw['cls'], (i, j), e['tilt_gap_deg'], [round(v, 3) for v in e['load_range']], o['verdict'],
                    o['S_A'].get('verdict', o['S_A']['fj']), o['S_B'].get('verdict', o['S_B']['fj']), o['S_AB'].get('verdict', o['S_AB']['fj'])), flush=True)
                if only is not None:
                    print(json.dumps({k: o[k] for k in ('terms', 'S_A', 'S_B', 'S_AB')}, indent=1, default=float))
    print('%d loadable tilted VV contacts, %.0f s' % (len(res), time.time() - t0))
    for k in sorted({o['verdict'] for o in res}):
        print('  %-70s %d' % (k, sum(o['verdict'] == k for o in res)))


if __name__ == '__main__':
    main()
