"""m2_inflation.py -- A35 / M2 Task 1: the LAYER-1 INFLATION CERTIFICATE.

theory.md T0.2-(A), Consequence 2.  With lambda* >= 0 exact (M1, floor
0.047644...) put

    Phi(z) = s - sum_{k=1..38} lambda*_k g_k(z),      Phi(z-hat) = s-hat.

Over box(r) = box(z-hat, r) we certify, all in mpmath.iv:

  (i)   r_res(r) := sup_{box(r)} || A(z)^T lambda* - e_s ||_1        [theory G-g]
  (ii)  Hbar(r)  := (1/2) * sum_{i,j} sup_{box(r)} |d2 Phi/dz_i dz_j|
        NORM INEQUALITY (exact statement).  For d = z - z-hat, ||d||_inf <= r,
        Taylor with integral remainder gives
            Phi(z) = Phi(z-hat) + grad Phi(z-hat).d + (1/2) d^T H(xi) d
        with H(xi) in the interval Hessian over the (convex) box, and
            |d^T H d| = |sum_{i,j} H_ij d_i d_j| <= sum_{i,j}|H_ij| |d_i||d_j|
                      <= ( sum_{i,j} sup_box |H_ij| ) * ||d||_inf^2 .
        Hence |(1/2) d^T H d| <= Hbar(r) r^2.  We also report the interval
        matrix inf-norm  Hinf = max_i sum_j sup|H_ij|; the coarser (valid but
        weaker) form is  |d^T H d| <= ||d||_1 ||H||_inf ||d||_inf <= 34*Hinf*r^2,
        and always Hsum <= 34*Hinf.  We use the Hsum form.
        Also |grad Phi(z-hat).d| <= ||grad Phi(z-hat)||_1 r <= r_res(r) * r
        (r_res(r) >= the residual at the centre, so this is conservative).
        =>   Phi(z) >= s-hat - Hbar(r) r^2 - r_res(r) r  on box(r).           (A1')
  (iii) beta(r) = sup ||I - Y A_S(box(r))||_inf and kappa = ||Y||_inf for A22's
        34-row S-subsystem with A22's rational preconditioner Y.

CONSEQUENCE 2 (the certificate).  Let feasible z in box(r) (so g_k(z) >= 0 for
all 38 rows) and G(z) = sum_k g_k(z).  Since lambda*_k >= lambda_floor,
    s(z) = Phi(z) + sum_k lambda*_k g_k(z) >= Phi(z) + lambda_floor * G(z)
         >= s-hat + lambda_floor G(z) - Hbar r^2 - r_res r .                  (A1)
Put T(r) := (Hbar(r) r^2 + r_res(r) r)/lambda_floor.
 * If G(z) >= T(r):  s(z) >= s-hat + lambda_floor (G(z) - T(r)) >= s-hat.
 * If G(z) <= T(r):  every g_k(z) in [0, T(r)], so ||F_S(z)||_inf <= T(r) with
   F_S the 34 retained S-rows.  Mean value + the Krawczyk data:
       z - z-hat = Y F_S(z) - Y F_S(z-hat) + (I - Y A_avg)(z - z-hat)
   with A_avg = int_0^1 A_S(z-hat + t(z - z-hat)) dt inside the interval
   Jacobian over the (convex) box, hence
       ||z - z-hat||_inf <= kappa T(r) / (1 - beta(r)) =: rho_1(r).
   If rho_1(r) <= r_N = 1/2000, A22's theorem applies to z and gives
   s(z) >= s-hat with equality iff z = z-hat.
The two cases overlap at G = T so they cover box(r).  CONCLUSION: for the
largest grid r with  rho_1(r) <= r_N  and  beta(r) < 1,
      sigma >= s-hat on box(z-hat, r_1),  with equality iff z = z-hat.
(The equality case: case 1 gives equality only when G = T(r) > 0, and such a z
also satisfies case 2, so it lies in box(r_N) where A22 forces z = z-hat; but
G(z-hat) = 0 != T(r), contradiction.  So equality happens only at z-hat.)

SELECTION CAVEAT (honest).  The 16 'edge' rows are SAT-separation surrogates for
a fixed axis/corner selection.  They are valid lower bounds for the true
separation only while the selection is dominant.  We therefore also certify
A22's validity margins (|tangential| <= 1/2, depth > -1/2) over box(r) for every
edge row, and report the reach of that too: the inflation certificate is only
sound out to min(r_1, r_valid).

Outputs results/m2_inflation.json.
"""
from __future__ import annotations

import json
import os
import sys
import time
from fractions import Fraction

import numpy as np
from mpmath import iv, mp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import m2_lib as M  # noqa: E402
import strata_lib as SL  # noqa: E402
import t3lib  # noqa: E402

iv.dps = 60
mp.dps = 60

GRID = [Fraction(2, 10000), Fraction(5, 10000), Fraction(1, 1000),
        Fraction(2, 1000), Fraction(5, 1000), Fraction(1, 100)]

# refinement scan (honest crossover location, not part of the brief's grid)
REFINE = [Fraction(n, 1000000) for n in
          (25, 50, 75, 100, 125, 150, 175, 190, 200, 210, 225, 250, 275, 300,
           350, 400, 450, 500, 600, 700, 800)]


def edge_validity(box):
    """A22 validity margins over box for all 'edge' rows among the 38.

    Returns (min tangential margin = 1/2 - max|tan|, min depth lower bound).
    """
    C = M.cons()
    zh = box
    worst_t = 1e9
    worst_d = 1e9
    for c in C:
        if c['kind'] != 'edge':
            continue
        i, j = c['i'], c['j']
        hx = t3lib._hiv(M.HALF[c['corner']][0])
        hy = t3lib._hiv(M.HALF[c['corner']][1])
        th_i = zh[3 * i + 2]
        ci, si = iv.cos(th_i), iv.sin(th_i)
        qx = zh[3 * i] + (ci * hx - si * hy)
        qy = zh[3 * i + 1] + (si * hx + ci * hy)
        nhx, nhy = M.NHAT[c['edge']]
        th_j = zh[3 * j + 2]
        cj, sj = iv.cos(th_j), iv.sin(th_j)
        nx = cj * iv.mpf(nhx) - sj * iv.mpf(nhy)
        ny = sj * iv.mpf(nhx) + cj * iv.mpf(nhy)
        wx, wy = qx - zh[3 * j], qy - zh[3 * j + 1]
        dep = nx * wx + ny * wy
        tan = -ny * wx + nx * wy
        worst_t = min(worst_t, 0.5 - M.iv_mag(tan))
        worst_d = min(worst_d, float(dep.a) + 0.5)
    return worst_t, worst_d


def main():
    t0 = time.time()
    zh = SL.z_hat()
    lam = M.lam_star()
    floor = M.lam_floor()
    floor_f = float(floor)
    S = M.a22_S()
    Yq = M.a22_Y()
    rN = M.a22_rN()
    rNf = float(rN)

    out = {
        'meta': {
            'task': 'A35/M2 Task 1 -- Layer-1 inflation certificate (theory.md '
                    'T0.2-(A) Consequence 2)',
            'source_lambda': 'results/m1_strata.json task1.lambda_star '
                             '(exact rationals, floor 0.047644046807669954)',
            'source_krawczyk': 'attempts/A22-local-rigidity/results/'
                               'krawczyk_cert.json (z0, S, Y, r_N)',
            'iv_dps': 60,
            'r_N': M.fs(rN),
            'r_N_float': rNf,
            'lambda_floor_exact': M.fs(floor),
            'lambda_floor_float': floor_f,
            'norm_inequality':
                'For d = z - zhat with ||d||_inf <= r:  |d^T H d| = '
                '|sum_ij H_ij d_i d_j| <= sum_ij |H_ij| |d_i| |d_j| <= '
                '(sum_ij sup_box |H_ij|) ||d||_inf^2 =: Hsum * r^2.  We set '
                'Hbar := Hsum/2 so that the Taylor remainder (1/2) d^T H d is '
                'bounded by Hbar * r^2.  Also reported: Hinf = '
                'max_i sum_j sup|H_ij| (interval matrix inf-norm of the '
                'magnitude matrix); the alternative bound |d^T H d| <= '
                '||d||_1 ||H||_inf ||d||_inf <= 34*Hinf*r^2 is valid but '
                'weaker since Hsum <= 34*Hinf.',
            'consequence2_inequality':
                'rho_1(r) = kappa*(Hbar(r) r^2 + r_res(r) r)/'
                '(lambda_floor*(1-beta(r))) <= r_N  and  beta(r) < 1',
        },
        'grid': [],
        'lambda_star_rational': [M.fs(x) for x in lam],
        'S_rows': S,
        'row_names': M.row_names(),
    }

    # --- residual of lambda* at the centre (sanity, matches M1's 9.68e-45)
    pbox = [t3lib._to_iv(x) for x in zh]
    r0, _ = M.res_l1_box(pbox, lam)
    out['meta']['r_res_at_centre'] = r0
    gmax = M.g_max_at_zhat()
    out['meta']['g_max_at_zhat'] = gmax
    out['meta']['g_max_note'] = (
        'max_k |g_k(z-hat)|.  The rigidity step bounds ||F_S(z) - F_S(z-hat)||'
        "_inf <= T(r) + g_max, not ||F_S(z)||_inf, because z-hat is A22's "
        'rational centre and the rows vanish there only to this accuracy.  It '
        'is added to T in both variants (it changes nothing numerically: '
        '%.2e vs T ~ 1e-5).' % gmax)

    def measure(r, verbose=True):
        t1 = time.time()
        rf = float(r)
        box = M.box_around(zh, r)
        r_res, res_mags = M.res_l1_box(box, lam)
        Hsum, Hinf = M.hess_bounds_box(box, lam)
        Hbar = Hsum / 2.0
        kr = M.krawczyk_iv(zh, r, S, Yq)
        beta, kappa = kr['beta'], kr['kappa']
        vt, vd = edge_validity(box)
        # variant A: the brief's formula (box-sup residual carried linearly)
        TA = (Hbar * rf * rf + r_res * rf) / floor_f + gmax
        # variant B: the exact Taylor form (centre residual + Hessian remainder)
        TB = (Hbar * rf * rf + r0 * rf) / floor_f + gmax
        if beta < 1.0:
            rhoA = kappa * TA / (1.0 - beta)
            rhoB = kappa * TB / (1.0 - beta)
        else:
            rhoA = rhoB = float('inf')
        okA = bool(beta < 1.0 and rhoA <= rNf)
        okB = bool(beta < 1.0 and rhoB <= rNf)
        # variant C: variant B's constants with the ITERATED dichotomy.
        # Case 2 puts z in box(rho_B(r)) with rho_B(r) < r, so the SAME
        # dichotomy re-applies at radius rho_B(r): either case 1 fires (and
        # s >= s-hat), or the radius shrinks again.  The iterates decrease to
        # the least fixed point x* of x -> kappa (Hbar x^2 + r_res(0) x)/
        # (lambda_floor (1-beta)) + kappa g_max/(1-beta), which is ~1e-57, far
        # below r_N, so A22 finishes.  The certified condition is therefore
        # rho_B(r) < r, NOT rho_B(r) <= r_N -- strictly weaker, hence a strictly
        # larger radius.  (beta and Hbar are monotone in r, so the map being
        # iterated dominates the true one at every smaller radius.)
        okC = bool(beta < 1.0 and rhoB < rf)
        xstarC = float('inf')
        if okC:
            Ck = kappa / ((1.0 - beta) * floor_f)
            x = rf
            for _ in range(400):
                x = Ck * (Hbar * x * x + r0 * x) + kappa * gmax / (1.0 - beta)
            xstarC = x
            okC = bool(xstarC <= rNf)
        valid = bool(vt > 0.0 and vd > 0.0)
        ent = {
            'r': M.fs(r), 'r_float': rf,
            'r_res_l1_upper_box': r_res,
            'r_res_max_coord': max(res_mags),
            'r_res_at_centre': r0,
            'Hsum_upper': Hsum, 'Hinf_upper': Hinf, 'Hbar_used': Hbar,
            'Hsum_over_34Hinf': Hsum / (34.0 * Hinf) if Hinf > 0 else None,
            'beta_upper': beta, 'kappa_Yinf': kappa,
            'krawczyk_S_contracts': bool(kr['ok']),
            'krawczyk_radK': kr['radK'],
            'G_threshold_T_variantA': TA, 'rho_1_variantA': rhoA,
            'rho_1_over_rN_variantA': rhoA / rNf, 'holds_variantA': okA,
            'G_threshold_T_variantB': TB, 'rho_1_variantB': rhoB,
            'rho_1_over_rN_variantB': rhoB / rNf, 'holds_variantB': okB,
            'rho_1_over_r_variantC': rhoB / rf, 'holds_variantC': okC,
            'x_star_variantC': xstarC,
            'holds_variantBC': bool(okB or okC),
            'edge_selection_valid': valid,
            'edge_tangential_margin_min': vt,
            'edge_depth_lower_plus_half': vd,
            'secs': time.time() - t1,
        }
        if verbose:
            print('r=%-9.4g r_res_box=%.3e Hbar=%.4f beta=%.4f kappa=%.3f '
                  'rhoA/rN=%.4g rhoB/rN=%.4g rhoB/r=%.4g A=%s B=%s C=%s '
                  'valid=%s tan=%.4f'
                  % (rf, r_res, Hbar, beta, kappa, rhoA / rNf, rhoB / rNf,
                     rhoB / rf, okA, okB, okC, valid, vt))
        return ent

    out['grid'] = [measure(r) for r in GRID]
    print('--- refinement scan ---')
    out['refinement_scan'] = [measure(r, verbose=False) for r in REFINE]
    for e in out['refinement_scan']:
        print('  r=%-9.4g rhoA/rN=%-9.4g rhoB/rN=%-9.4g A=%d B=%d valid=%d'
              % (e['r_float'], e['rho_1_over_rN_variantA'],
                 e['rho_1_over_rN_variantB'], e['holds_variantA'],
                 e['holds_variantB'], e['edge_selection_valid']))

    def best_of(entries, key):
        ok = [e for e in entries if e[key] and e['edge_selection_valid']]
        return max(ok, key=lambda e: e['r_float']) if ok else None

    bA = best_of(out['grid'], 'holds_variantA')
    bB = best_of(out['grid'], 'holds_variantB')
    bC = best_of(out['grid'], 'holds_variantC')
    rA = best_of(out['refinement_scan'], 'holds_variantA')
    rB = best_of(out['refinement_scan'], 'holds_variantB')
    rC = best_of(out['refinement_scan'], 'holds_variantC')
    out['variantC_note'] = (
        "Variant C uses variant B's constants with the ITERATED dichotomy: "
        'case 2 lands in box(rho_B(r)); if rho_B(r) < r the same dichotomy '
        're-applies at the smaller radius and the iterates fall to a fixed '
        'point x* ~ 1e-57 << r_N, so A22 finishes.  Condition: rho_B(r) < r.  '
        'NEITHER B NOR C IMPLIES THE OTHER: below r_N, C (rho < r) is STRICTER '
        'than B (rho <= r_N); above r_N it is the weaker one.  Since every '
        'radius certified here is below r_N, C buys nothing for v1 -- its '
        'refined crossover 2.75e-4 is SMALLER than the 3.5e-4 of B.  The '
        'iteration '
        'is what makes the v2 certificates work (m2b_global.py, h ~ 1.2e-3 > '
        'r_N), and it is recorded here for completeness and to correct the '
        'record: the sound condition is the DISJUNCTION B or C (variant BC), '
        'and for v1 that disjunction equals B.')
    out['r_1_variantC'] = bC['r'] if bC else None
    out['r_1_variantC_float'] = bC['r_float'] if bC else None
    out['r_1_refined_variantC'] = rC['r_float'] if rC else None
    bBC = best_of(out['grid'], 'holds_variantBC')
    rBC = best_of(out['refinement_scan'], 'holds_variantBC')
    out['r_1_variantBC'] = bBC['r'] if bBC else None
    out['r_1_variantBC_float'] = bBC['r_float'] if bBC else None
    out['r_1_refined_variantBC'] = rBC['r_float'] if rBC else None
    out['variantBC_note'] = (
        'Variant BC = B or C, the full sound condition (either branch of the '
        'dichotomy finishes).  This is the value reported as r_1.')

    out['variantA_note'] = (
        "Variant A is the brief's literal inequality kappa*(Hbar r^2 + "
        "r_res(r) r)/(lambda_floor (1-beta)) <= r_N with r_res(r) the BOX "
        "supremum of ||A(z)^T lambda* - e_s||_1.  It is sound but double-counts "
        "curvature: r_res(r) is itself ~ Hsum*r (measured slope 22.2 per unit "
        "r, vs Hsum = 15.7), so the first-order term silently re-adds the "
        "second-order one.")
    out['variantB_note'] = (
        "Variant B replaces r_res(r) by r_res(0) = ||A(z-hat)^T lambda* - "
        "e_s||_1 (M1's 9.7e-45).  This is the EXACT Taylor form -- Phi(z) = "
        "Phi(z-hat) + grad Phi(z-hat).d + (1/2) d^T H(xi) d with H over the "
        "box -- and is equally rigorous; it is the recommended constant.")

    out['r_1_variantA'] = bA['r'] if bA else None
    out['r_1_variantA_float'] = bA['r_float'] if bA else None
    out['r_1_variantB'] = bB['r'] if bB else None
    out['r_1_variantB_float'] = bB['r_float'] if bB else None
    out['r_1_refined_variantA'] = rA['r_float'] if rA else None
    out['r_1_refined_variantB'] = rB['r_float'] if rB else None
    out['r_1'] = out['r_1_variantBC'] or out['r_1_variantB']
    out['r_1_float'] = (out['r_1_variantBC_float']
                        or out['r_1_variantB_float'])

    if bB is None:
        out['conclusion'] = ('NO grid radius satisfies Consequence 2 in either '
                             'variant; the layer-1 inflation certificate is '
                             'VACUOUS on the brief grid.')
    else:
        out['conclusion'] = (
            'sigma >= s-hat on box(z-hat, r_1) with r_1 = %s = %.4g '
            '(variant B), with equality iff z = z-hat.  Certified constants '
            'over box(r_1) [all mpmath.iv, dps 60]: r_res(0) = %.3e, '
            'r_res(box) = %.4e, Hbar = %.6f (Hsum = %.6f, Hinf = %.6f), '
            'beta = %.6f < 1, kappa = ||Y||_inf = %.5f, lambda_floor = '
            '%.12f, T = %.4e, rho_1 = %.4e <= r_N = %.4e.  Edge-selection '
            'validity margin over box(r_1): tangential %.5f > 0, depth+1/2 '
            '%.5f > 0.'
            % (bB['r'], bB['r_float'], bB['r_res_at_centre'],
               bB['r_res_l1_upper_box'], bB['Hbar_used'], bB['Hsum_upper'],
               bB['Hinf_upper'], bB['beta_upper'], bB['kappa_Yinf'], floor_f,
               bB['G_threshold_T_variantB'], bB['rho_1_variantB'], rNf,
               bB['edge_tangential_margin_min'],
               bB['edge_depth_lower_plus_half']))
    out['verdict'] = (
        'r_1 (variant B, recommended) = %s vs r_N = %.4g -> ratio %.3f.  '
        'r_1 (variant A, brief formula) = %s -> ratio %s.  Refined crossovers: '
        'A at r ~ %.3g, B at r ~ %.3g, C at r ~ %.3g.  HONEST READING: r_1 < r_N; the '
        'inflation certificate does NOT inflate -- it covers a box a factor '
        '~%.1f SMALLER than A22 already covers, so it is strictly subsumed by '
        'A22 as a standalone statement.  theory.md predicted "same ORDER as '
        'r_N" (float estimate 3e-4); measured 2e-4, i.e. the prediction is '
        'confirmed in order of magnitude and the sign of the comparison is '
        'unfavourable.'
        % (out['r_1_variantB_float'], rNf,
           (out['r_1_variantB_float'] / rNf) if bB else float('nan'),
           out['r_1_variantA_float'],
           ('%.3f' % (bA['r_float'] / rNf)) if bA else 'n/a',
           out['r_1_refined_variantA'] or float('nan'),
           out['r_1_refined_variantB'] or float('nan'),
           out['r_1_refined_variantC'] or float('nan'),
           (rNf / out['r_1_variantB_float']) if bB else float('nan')))
    out['meta']['runtime_secs'] = time.time() - t0

    path = os.path.join(M.RESULTS, 'm2_inflation.json')
    with open(path, 'w') as f:
        json.dump(out, f, indent=1)
    print('\n', out['verdict'])
    print(out['conclusion'])
    print('->', path)


if __name__ == '__main__':
    main()
