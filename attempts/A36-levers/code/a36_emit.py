#!/usr/bin/env python
"""a36_emit.py -- A36 Task 4: emit the (V') certificate family on basis v3.

Emits, into results/a36_certs/:
  * G3_<variant>.json   -- 16 per-variant (V') certificates at the composed
                           radius h*, each loading its branch's corner rows
                           with omega >= branch_floor > 0 (so that the
                           drop-branch / wrong-branch corruption gates bite).
  * G3_UNIVERSAL.json   -- the branch-free control: the same barrier with
                           omega supported on rows 0..35 + the two aux rows
                           only.  It needs NO branch rows and NO L1, and is
                           reported as the honest headline; the 16 variant
                           certificates buy the extra 2.4 % of radius.

Pin basis: A22's own S and Y, verbatim from krawczyk_cert.json (mapped into v3
positions).  a36_reach.json records the alternatives that were tried.
"""
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import a36_lib as L                      # noqa: E402
import a36_reach as R                    # noqa: E402
import m2_lib as M                       # noqa: E402

BRANCH_FLOOR = 0.01
CERTS = os.path.join(L.RESULTS, 'a36_certs')


def fs(x):
    return '%d/%d' % (x.numerator, x.denominator)


def build(V, P, Y, h, branch_floor, universal=False):
    w = L.row_hessian_mass(h)
    Yv, beta, kappa, c = R.pin_data(P, h, Y=Y)
    if universal:
        orig = L.variant_rows
        L.variant_rows = lambda _V: sorted(set(range(36)) | set(L.AUX_POS))
        try:
            om, mg = L.omega_lp_eff(V, P, h, c, w=w, beta=beta)
        finally:
            L.variant_rows = orig
        RV = sorted(set(range(36)) | set(L.AUX_POS))
    else:
        om, mg = L.omega_lp_eff(V, P, h, c, w=w, beta=beta,
                                branch_floor=branch_floor)
        RV = L.variant_rows(V)
    if om is None:
        return None
    omq = L.rationalise_omega(P, om)
    cert = L.vprime_certificate(omq, h, P, Yv, beta=beta, kappa=kappa)
    bad = [k for k in range(L.NEXT3)
           if (omq[k] < 0 and k in set(RV)) or (omq[k] != 0 and
                                                k not in set(RV))]
    if bad or not cert['ok']:
        return None
    branch_rows = sorted(set(RV) - set(range(36)) - set(L.AUX_POS))
    d = {
        'type': "V'-v3-maxform",
        'basis': 'v3 (44 geometric rows + 2 aux + 24 alternative corner rows)',
        'universal': bool(universal),
        'variant': None if universal else [L.AXIS_NAME[a] for a in V],
        'variant_axes': None if universal else list(V),
        'h': fs(h), 'h_float': float(h),
        'r_N': fs(L.R_N),
        'P': list(P),
        'P_source': "A22 krawczyk_cert.json 'S', mapped 36->44, 37->45",
        'Y_source': "A22 krawczyk_cert.json 'Y', verbatim",
        'valid_rows': list(RV),
        'branch_rows': branch_rows,
        'branch_rows_with_positive_omega':
            [k for k in branch_rows if omq[k] > 0],
        'omega_rational': [fs(x) for x in omq],
        'omega_denominator_max': max(x.denominator for x in omq),
        'claims': {k: cert[k] for k in
                   ('eps_0', 'eps_w', 'Hbar', 'Hinf', 'beta', 'kappa',
                    'kappa_eff', 'kappa_over_alpha', 'g_max', 'alpha_min',
                    'E', 'psi', 'psi_over_h', 'psi_A35form', 'x_star',
                    'omega_l1')},
        'lp_margin': mg,
    }
    return d, cert


def main():
    os.makedirs(CERTS, exist_ok=True)
    P, Y = list(L.S_EXT), L.a22_Y_v3()

    # ---- per-variant certified reach with the branch floor enforced
    orig = L.omega_lp_eff

    def lp_bf(V, P_, h, c, w=None, beta=0.0, cap=200.0, only_active=True):
        return orig(V, P_, h, c, w=w, beta=beta, cap=cap,
                    only_active=only_active, branch_floor=BRANCH_FLOOR)
    L.omega_lp_eff = lp_bf
    reach = {}
    for V in L.VARIANTS:
        h_r, _ = R.bisect_reach(V, P, Y, rational=False)
        reach[L.variant_tag(V)] = float(h_r) if h_r else 0.0
        print('  %-24s branch-loaded reach %.6e = %.3f r_N'
              % (L.variant_tag(V), reach[L.variant_tag(V)],
                 reach[L.variant_tag(V)] / float(L.R_N)))
    L.omega_lp_eff = orig
    hmin = min(reach.values())
    # emit at a clean rational strictly below the certified reach
    h_star = Fraction(int(hmin * 0.999 * 10 ** 6), 10 ** 6)
    print('h* = %s = %.6e = %.3f r_N' % (fs(h_star), float(h_star),
                                         float(h_star) / float(L.R_N)))

    # ---- branch-free universal control
    L.variant_rows_backup = L.variant_rows
    hu, _ = None, None
    lo, hi = Fraction(1, 10000), Fraction(8, 1000)
    origvr = L.variant_rows
    L.variant_rows = lambda _V: sorted(set(range(36)) | set(L.AUX_POS))
    try:
        hu, _cu = R.bisect_reach(L.VARIANTS[0], P, Y, rational=False)
    finally:
        L.variant_rows = origvr
    h_univ = Fraction(int(float(hu) * 0.999 * 10 ** 6), 10 ** 6)
    print('universal (branch-free) reach %.6e = %.3f r_N; emitting at %s'
          % (float(hu), float(hu) / float(L.R_N), fs(h_univ)))

    out, n = [], 0
    for V in L.VARIANTS:
        res = build(V, P, Y, h_star, BRANCH_FLOOR)
        assert res is not None, L.variant_tag(V)
        d, cert = res
        fn = os.path.join(CERTS, 'G3_%s.json' % L.variant_tag(V))
        with open(fn, 'w') as f:
            json.dump(d, f, indent=1)
        n += 1
        out.append({'tag': L.variant_tag(V), 'file': os.path.basename(fn),
                    'reach_float': reach[L.variant_tag(V)],
                    'branch_rows_loaded': d['branch_rows_with_positive_omega'],
                    **{k: cert[k] for k in ('beta', 'kappa', 'kappa_eff',
                                            'Hbar', 'eps_0', 'eps_w',
                                            'psi_over_h', 'x_star',
                                            'alpha_min')}})
    res = build(L.VARIANTS[0], P, Y, h_univ, 0.0, universal=True)
    assert res is not None
    d, cert = res
    with open(os.path.join(CERTS, 'G3_UNIVERSAL.json'), 'w') as f:
        json.dump(d, f, indent=1)
    n += 1
    print('emitted %d certificates into %s' % (n, CERTS))

    # ---- fold into a36_reach.json
    rp = os.path.join(L.RESULTS, 'a36_reach.json')
    J = json.load(open(rp))
    J['emitted'] = {
        'branch_floor': BRANCH_FLOOR,
        'pin_basis_used': 'A22-S (S and Y verbatim from krawczyk_cert.json)',
        'h_star': fs(h_star), 'h_star_float': float(h_star),
        'h_star_over_rN': float(h_star) / float(L.R_N),
        'per_variant_branch_loaded_reach': reach,
        'min_branch_loaded_reach': hmin,
        'universal_branch_free_reach': float(hu),
        'universal_branch_free_reach_over_rN': float(hu) / float(L.R_N),
        'h_universal_emitted': fs(h_univ),
        'certificates': out,
        'n_certificates': n,
    }
    J['h_composed'] = max(float(h_star), float(h_univ))
    J['h_composed_over_rN'] = J['h_composed'] / float(L.R_N)
    with open(rp, 'w') as f:
        json.dump(J, f, indent=1)
    return 0


if __name__ == '__main__':
    sys.exit(main())
