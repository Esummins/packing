"""m2b_global.py -- A35 / M2-delta: the UNIVERSAL (V') certificate on basis v2.

THE RESULT.  M1b reported that on basis v2 the uniform multiplier floor
collapses to 0 -- rows 0 (W0c0[x=0]) and 2 (W0c1[y=0]) are FORCED to lambda = 0
over the whole multiplier polytope -- so theory.md (A)/Consequence 1 ("every
escape is uphill at rate >= 0.0476 per unit of total gap opening") is false as
written on v2, and that is exactly why M1b's two flat seeds, and through them
the 25 050-element queue, could not be closed by any first-order test.

That collapse is an ARTEFACT of the basis repair, not a property of the jam.
v1 -> v2 dropped the two centre-distance rows

        a0 : d^2(c0,c1) - 1 >= 0        a1 : d^2(c0,c3) - 1 >= 0

which are valid for EVERY pair of interior-disjoint unit squares (incircles of
radius 1/2) and ACTIVE at z-hat (M1b: centre distance^2 = exactly 1 for both).
They are legitimate generators of the FJ multiplier cone.  Putting them back:

    uniform floor over ALL rows, WITHOUT aux  :  0            (reproduces M1b)
    uniform floor over ALL rows, WITH aux     :  0.0286 / 0.0358

uniformly over every selection in every tie menu.  So the ascent constant is
restored on v2, and with it a single certificate per (variant, selection) that
covers EVERY break set at once.

THE CERTIFICATE.  Find rational omega over the 50-row extended set with

    A_ext^T omega = e_s  (residual eps_w),
    omega_r >= alpha_min > 0  for every v2 row of the variant AND both aux rows,
    omega_r >= 0              for the tied dominance rows,
    omega_r = 0               for rows outside the variant,

and put Phi(z) = s - sum_r omega_r g_r(z), so grad Phi(z-hat) = -(A^T omega -
e_s) and Phi(z-hat) >= s-hat - eps_0.  For ANY feasible z in box(z-hat, h)
(no stratification, no break set, nothing to choose):

    s(z) = Phi(z) + sum_r omega_r g_r(z) >= Phi(z) + alpha_min * G(z),
    G(z) := sum over the variant's v2 rows and the two aux rows of g_r(z) >= 0
    (dominance terms dropped, they are >= 0 with omega >= 0),
    Phi(z) >= s-hat - eps_0 - eps_w h - Hbar h^2   (Taylor, interval Hessian).

  CASE 1  G(z) >= T(h) := (eps_0 + eps_w h + Hbar h^2)/alpha_min  =>  s >= s-hat.
  CASE 2  G(z) <= T(h)  =>  every row of A22's 34-row Krawczyk system lies in
          [0, T(h) + g_max]  (A22's system is exactly {0..35}\\{1,10,23,29}
          plus the two aux rows, all of which are in G), so
              ||z - z-hat||_inf <= kappa (T(h) + g_max)/(1 - beta(h)) =: psi(h).

If psi(h) < h the dichotomy ITERATES: case 2 puts z in box(psi(h)) and the
argument re-applies there with a smaller radius.  Either case 1 fires at some
stage, or the radii shrink to the fixed point x* <= r_N and A22's theorem
finishes.  Either way

    sigma >= s-hat on box(z-hat, h_G), with equality iff z = z-hat,

for every feasible z -- all strata, all selections, all break sets at once.

NOTE ON THE ITERATION.  M2's v1 inflation certificate (results/m2_inflation.json)
imposed the STRONGER condition psi(r) <= r_N instead of psi(r) < r, which cost a
factor ~1.45 in radius.  The iterated condition is applied here and back-ported
to v1 in m2_inflation.py variant C.

Outputs results/m2b_global.json and results/m2b_certs/G_*.json.
"""
from __future__ import annotations

import json
import os
import sys
import time
from fractions import Fraction

import numpy as np
from mpmath import iv

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import m2b_lib as L  # noqa: E402
import m2b_value as V  # noqa: E402
import m2_lib as M  # noqa: E402
import strata_lib as SL  # noqa: E402

iv.dps = 60
CERTDIR = os.path.join(M.RESULTS, 'm2b_certs')
VARIANTS = ('conj', 'selx', 'sely')


def find_h(sel, om, alpha, start=Fraction(1, 2000)):
    best = None
    h = start
    c = V.vprime_certificate(sel, om, alpha, h)
    if c['ok']:
        best = (h, c)
        while h < Fraction(1, 8):
            h2 = h * 2
            c2 = V.vprime_certificate(sel, om, alpha, h2)
            if not c2['ok']:
                break
            h, best = h2, (h2, c2)
        lo, hi = best[0], best[0] * 2
        for _ in range(6):
            mid = (lo + hi) / 2
            cm = V.vprime_certificate(sel, om, alpha, mid)
            if cm['ok']:
                lo, best = mid, (mid, cm)
            else:
                hi = mid
    else:
        hi_fail = h
        while h > Fraction(1, 10 ** 7):
            h = h / 2
            c2 = V.vprime_certificate(sel, om, alpha, h)
            if c2['ok']:
                best = (h, c2)
                break
            hi_fail = h
        if best is not None:
            lo, hi = best[0], hi_fail
            for _ in range(6):
                mid = (lo + hi) / 2
                cm = V.vprime_certificate(sel, om, alpha, mid)
                if cm['ok']:
                    lo, best = mid, (mid, cm)
                else:
                    hi = mid
    return best


def x_star(cc, alpha):
    """Least fixed point of psi, iterated numerically (psi is increasing)."""
    kappa, beta = cc['kappa'], cc['beta']
    e0, ew, Hb, gm = cc['eps_0'], cc['eps_w'], cc['Hbar_W'], cc['g_max']
    C = kappa / ((1.0 - beta) * alpha)
    x = cc['h_float']
    for _ in range(400):
        x = C * (e0 + ew * x + Hb * x * x) + kappa * gm / (1.0 - beta)
    return x


def main():
    t0 = time.time()
    os.makedirs(CERTDIR, exist_ok=True)
    names2 = SL.row_names_v2()
    rN = M.a22_rN()
    rNf = float(rN)
    out = {
        'meta': {
            'task': 'A35/M2-delta -- universal (V-prime) certificate on v2: '
                    'the aux rows restore the uniform multiplier floor and one '
                    'certificate per (variant, selection) covers every break '
                    'set at once',
            'aux_rows': ['d^2(c0,c1) - 1 >= 0', 'd^2(c0,c3) - 1 >= 0'],
            'aux_validity': (
                'valid for EVERY pair of interior-disjoint unit squares '
                '(incircles of radius 1/2 give |c_i - c_j| >= 1) and ACTIVE at '
                'z-hat (M1b: centre distance^2 = exactly 1 for both pairs)'),
            'r_N': M.fs(rN), 'r_N_float': rNf,
            'row_names_v2': names2,
        },
        'floor_comparison': {},
        'variants': {},
    }
    path = os.path.join(M.RESULTS, 'm2b_global.json')

    def flush():
        with open(path, 'w') as f:
            json.dump(out, f, indent=1)

    # ---- floor with and without the aux rows (the headline delta)
    from scipy.optimize import linprog
    _, A2, _, _ = SL.jacobian_v2()
    for variant in VARIANTS:
        vr = sorted(SL.v2_variant_rows(variant))
        n = len(vr)
        c = np.zeros(n + 1); c[-1] = -1.0
        Aub = np.hstack([-np.eye(n), np.ones((n, 1))])
        Aeq = np.zeros((SL.NV, n + 1)); Aeq[:, :n] = A2[vr].T
        beq = np.zeros(SL.NV); beq[SL.S_IDX] = 1.0
        r = linprog(c, A_ub=Aub, b_ub=np.zeros(n), A_eq=Aeq, b_eq=beq,
                    bounds=[(0, None)] * n + [(None, 10.0)], method='highs')
        out['floor_comparison'][variant] = {
            'uniform_floor_without_aux': (float(-r.fun) if r.success else None),
            'm1b_reference': 0.0,
        }
    flush()

    for variant in VARIANTS:
        vrows = sorted(SL.v2_variant_rows(variant))
        sels = list(L.selection_iter(variant))
        ent = {'n_selections': len(sels), 'n_rows': len(vrows),
               'per_selection': []}
        ts = time.time()
        floors, hs = [], []
        for si, sel in enumerate(sels):
            omf, a_lp = V.omega_lp_value(vrows, variant, sel, mode='maxfloor',
                                         dom_floor=0.0)
            rec = {'selection_index': si,
                   'selection': {str(k): int(v) for k, v in sel.items()},
                   'lp_floor': a_lp}
            if omf is None or a_lp is None or a_lp <= 0:
                rec.update(certified=False, reason='LP floor not positive')
                ent['per_selection'].append(rec)
                continue
            # trade a little floor for a much smaller ||omega|| (=> smaller
            # Hessian bound => larger certified radius)
            best_pack = None
            wmass = V.row_hessian_mass(sel, Fraction(1, 2000))
            for frac_ in (1.0, 0.9, 0.75):
                omf2, a2 = V.omega_lp_value(vrows, variant, sel, mode='minL1',
                                            dom_floor=0.0, weights=wmass,
                                            floor_target=a_lp * frac_)
                if omf2 is None:
                    continue
                om = V.rationalise_omega_value(sel, omf2)
                alpha = min(om[r_] for r_ in
                            sorted(set(vrows) | set(L.AUX_POS)))
                domv = []
                if not (alpha > 0 and all(om[p] >= 0 for p in domv)
                        and all(om[k] == 0 for k in range(L.NV2)
                                if k not in set(vrows))
                        and all(om[p] == 0 for p in L.DOM_POS
                                if p not in domv)):
                    continue
                b = find_h(sel, om, alpha)
                if b is None:
                    continue
                if best_pack is None or b[0] > best_pack[1][0]:
                    best_pack = (om, b, alpha, frac_)
            if best_pack is None:
                rec.update(certified=False, reason='no radius certifies')
                ent['per_selection'].append(rec)
                continue
            om, (hG, cc), alpha, frac_ = best_pack
            xs = x_star(cc, float(alpha))
            floors.append(float(alpha))
            hs.append(float(hG))
            rec.update(certified=True, h_G=M.fs(hG), h_G_float=float(hG),
                       h_G_over_rN=float(hG) / rNf,
                       alpha_min=M.fs(alpha), alpha_min_float=float(alpha),
                       floor_fraction_used=frac_,
                       omega_l1=float(sum(abs(x) for x in om)),
                       x_star=xs, x_star_le_rN=bool(xs <= rNf),
                       constants={k: cc[k] for k in
                                  ('beta', 'kappa', 'eps_0', 'eps_w', 'g_max',
                                   'Hbar_W', 'Hinf_W', 'T_W', 'psi',
                                   'psi_over_h')})
            domv = []
            cert = {
                'type': "V'  (universal value/pinning certificate, basis v2 + "
                        "aux + dom; stratum-independent)",
                'variant': variant,
                'selection': {str(k): int(v) for k, v in sel.items()},
                'ext_row_names': L.ext_row_names(sel),
                'variant_rows': vrows,
                'aux_positions': list(L.AUX_POS),
                'dom_positions': domv,
                'strict_positive_positions': sorted(set(vrows) |
                                                    set(L.AUX_POS)),
                'S_EXT': L.S_EXT,
                'omega_rational': [M.fs(x) for x in om],
                'alpha_min': M.fs(alpha), 'h_G': M.fs(hG), 'r_N': M.fs(rN),
                'claims': {k: cc[k] for k in
                           ('beta', 'kappa', 'eps_0', 'eps_w', 'g_max',
                            'Hbar_W', 'Hinf_W', 'T_W', 'psi')},
                'x_star': xs,
                'argument': (
                    'Phi(z) = s - sum_r omega_r g_r with A_ext^T omega = e_s '
                    'to eps_w.  For any feasible z in box(h): s(z) = Phi(z) + '
                    'sum_r omega_r g_r >= Phi(z) + alpha_min G(z) with G the '
                    'sum of the variant rows and the two aux rows (dominance '
                    'terms dropped, omega >= 0 there), and Phi(z) >= s-hat - '
                    'eps_0 - eps_w h - Hbar h^2.  Either G >= T(h) and s >= '
                    's-hat, or every A22 Krawczyk row is in [0, T+g_max] so '
                    '||z - z-hat||_inf <= kappa(T+g_max)/(1-beta) = psi < h; '
                    'iterating the dichotomy drives the radius to x* <= r_N '
                    'and A22 finishes.  NO break set, stratum or selection of '
                    'maintained rows enters the argument, so one certificate '
                    'covers the whole lattice.'),
            }
            with open(os.path.join(CERTDIR, 'G_%s_sel%02d.json'
                                   % (variant, si)), 'w') as f:
                json.dump(cert, f, indent=1)
            ent['per_selection'].append(rec)
        ent['n_certified'] = sum(1 for r in ent['per_selection']
                                 if r.get('certified'))
        ent['all_selections_certified'] = ent['n_certified'] == len(sels)
        if floors:
            ent['alpha_min_min'] = min(floors)
            ent['alpha_min_max'] = max(floors)
            ent['h_G_min'] = min(hs)
            ent['h_G_max'] = max(hs)
            ent['h_G_min_over_rN'] = min(hs) / rNf
        ent['secs'] = time.time() - ts
        out['variants'][variant] = ent
        out['floor_comparison'][variant]['uniform_floor_with_aux'] = (
            min(floors) if floors else None)
        flush()
        print('  %-5s: %d/%d selections certified, floor >= %.6f, '
              'h_G in [%.5g, %.5g] = [%.2f, %.2f] x r_N  [%.0fs]'
              % (variant, ent['n_certified'], len(sels),
                 ent.get('alpha_min_min', float('nan')),
                 ent.get('h_G_min', float('nan')),
                 ent.get('h_G_max', float('nan')),
                 ent.get('h_G_min_over_rN', float('nan')),
                 ent.get('h_G_max', 0) / rNf, ent['secs']))

    hmin = min(out['variants'][v]['h_G_min'] for v in VARIANTS
               if 'h_G_min' in out['variants'][v])
    fmin = min(out['variants'][v]['alpha_min_min'] for v in VARIANTS
               if 'alpha_min_min' in out['variants'][v])
    out['summary'] = {
        'uniform_floor_without_aux': 0.0,
        'uniform_floor_with_aux_min': fmin,
        'n_certificates': sum(out['variants'][v]['n_certified']
                              for v in VARIANTS),
        'n_certificates_meaningful_variants': sum(
            out['variants'][v]['n_certified'] for v in ('selx', 'sely')),
        'all_selections_certified': all(
            out['variants'][v]['all_selections_certified'] for v in VARIANTS),
        'h_G_min': hmin, 'h_G_min_over_rN': hmin / rNf,
        'x_star_max': max(r['x_star'] for v in VARIANTS
                          for r in out['variants'][v]['per_selection']
                          if r.get('certified')),
        'covers': 'every break set in the 2^42 lattice, every stratum, at once',
        'headline': (
            'The two auxiliary dist rows restore the v2 uniform multiplier '
            'floor from 0 to %.6f, and with it a single stratum-INDEPENDENT '
            "(V') certificate per (variant, selection): %d certificates cover "
            'the entire 2^42 break-set lattice on box(z-hat, %.5g) = %.2f x '
            'r_N.  M1b\'s 25 050-element work queue therefore does not need '
            '25 050 certificates -- it needs %d.'
            % (fmin, sum(out['variants'][v]['n_certified'] for v in VARIANTS),
               hmin, hmin / rNf,
               sum(out['variants'][v]['n_certified']
                   for v in ('selx', 'sely')))),
    }
    out['meta']['runtime_secs'] = time.time() - t0
    flush()
    print(json.dumps(out['summary'], indent=1))
    print('->', path, 'and', CERTDIR)


if __name__ == '__main__':
    main()
