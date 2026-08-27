#!/usr/bin/env python
"""a36_reach.py -- A36 Task 3: L2 reach optimisation.

(a) h-bisection with an inner LP over omega (a36_lib.omega_lp_eff), honestly
    derived from the inequality chain documented at the top of a36_lib.
(b) alternative pin bases P (A22's S; the load-bearing block avoiding the two
    statically dead rows {0,2} + an aux row; a local-search optimum), each with
    its own rational preconditioner Y.
(c) the iterated variant-C chain: the least fixed point x* of
        x = kappa_eff E(x)/(1-beta) + kappa g_max/(1-beta)
    must land <= r_N; that is what lets case 2 hand over to A22.

Output: results/a36_reach.json
"""
import json
import os
import sys
import time
from fractions import Fraction

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import a36_lib as L                      # noqa: E402
import strata_lib as SL                  # noqa: E402
import m2_lib as M                       # noqa: E402

_BOXJ = {}


def box_jac(h):
    key = str(h)
    if key in _BOXJ:
        return _BOXJ[key]
    box = M.box_around(SL.z_hat(), h)
    rows = L.v3_rows()
    mb = np.zeros((L.NEXT3, 34))
    rb = np.zeros((L.NEXT3, 34))
    for k, r in enumerate(rows):
        j = SL.eval_geo(box, r, order=1)
        for loc, gi in enumerate(r['vars']):
            m_, r_ = SL._iv_mid_rad(j.g[loc])
            mb[k, gi] = m_
            rb[k, gi] = r_
    _BOXJ[key] = (mb, rb)
    return mb, rb


_YC = {}


def pin_data(P, h, Y=None, tag=''):
    """(Y, beta, kappa, c) for pin set P at radius h; Y cached per P."""
    key = (tuple(P), tag)
    if Y is None:
        if key in _YC:
            Y = _YC[key]
        else:
            Y = L.make_Y(P)
            _YC[key] = Y
    beta, kappa = L.krawczyk_beta_kappa(P, Y, h)
    c = [max(abs(float(Y[i][r])) for i in range(34)) for r in range(34)]
    return Y, beta, kappa, c


def eval_at(V, P, Y, h, rational=True):
    """Design omega at h by LP, then [IV]-certify.  Returns (cert, omega)."""
    w = L.row_hessian_mass(h)
    Yv, beta, kappa, c = pin_data(P, h, Y=Y)
    om, margin = L.omega_lp_eff(V, P, h, c, w=w, beta=beta)
    if om is None:
        return None, None
    if not rational:
        omq = [Fraction(float(x)).limit_denominator(10 ** 14) for x in om]
    else:
        omq = L.rationalise_omega(P, om)
    RV = set(L.variant_rows(V))
    bad = [k for k in range(L.NEXT3)
           if (omq[k] < 0 and k in RV) or (omq[k] != 0 and k not in RV)]
    cert = L.vprime_certificate(omq, h, P, Yv, beta=beta, kappa=kappa)
    cert['lp_margin'] = margin
    cert['sign_violations'] = bad
    cert['ok'] = bool(cert['ok'] and not bad)
    return cert, omq


def bisect_reach(V, P, Y, lo=Fraction(1, 10000), hi=Fraction(8, 1000),
                 iters=22, rational=False):
    c0, _ = eval_at(V, P, Y, lo, rational=rational)
    if c0 is None or not c0['ok']:
        return None, c0
    best = (lo, c0)
    for _ in range(iters):
        mid = (lo + hi) / 2
        c, _ = eval_at(V, P, Y, mid, rational=rational)
        if c is not None and c['ok']:
            lo = mid
            best = (mid, c)
        else:
            hi = mid
        if float(hi - lo) < 1e-6 * float(lo):
            break
    return best[0], best[1]


def local_search_pin(V, h, iters=250, seed=3):
    """Local swap search over 34-row pin sets minimising kappa_eff*Hbar/(1-beta)
    (equivalently maximising the reach estimate (1-beta)/(kappa_eff Hbar))."""
    mid, _ = L.v3_jacobian()
    mb, rb = box_jac(h)
    w = L.row_hessian_mass(h)
    # The pin basis must be valid in EVERY variant, so it is drawn from the
    # UNIVERSAL rows only: A22's 0..35 plus the two aux rows.  (A variant-local
    # basis would need a separate Krawczyk preconditioner per variant and would
    # not be usable by the composed theorem.)
    RV = [k for k in (list(range(36)) + list(L.AUX_POS))
          if k in set(L.active_positions())]
    rng = np.random.default_rng(seed)

    def score(P):
        P = list(P)
        try:
            Yf = np.linalg.inv(mid[P])
        except Exception:
            return -1.0, None
        if not np.all(np.isfinite(Yf)):
            return -1.0, None
        kap = float(np.abs(Yf).sum(1).max())
        E = np.eye(34) - Yf @ mb[P]
        beta = float((np.abs(E) + np.abs(Yf) @ rb[P]).sum(1).max())
        if beta >= 0.9 or kap > 1e5:
            return -1.0, None
        c = np.abs(Yf).max(axis=0)
        om, mrg = L.omega_lp_eff(V, P, h, c, w=w, beta=beta)
        if om is None:
            return -1.0, None
        omP = np.array([om[r] for r in P])
        if omP.min() <= 0:
            return -1.0, None
        keff = float((c / omP).max())
        Hb = 0.5 * float(w @ np.abs(om))
        return (1 - beta) / (keff * Hb), (keff, Hb, beta, kap)

    cur = list(L.S_EXT)
    cs, cd = score(cur)
    best = (cs, sorted(cur), cd)
    for _ in range(iters):
        i = int(rng.integers(34))
        cand = [r for r in RV if r not in cur]
        t = list(cur)
        t[i] = cand[int(rng.integers(len(cand)))]
        s, d = score(t)
        if s > cs:
            cur, cs, cd = t, s, d
        if s > best[0]:
            best = (s, sorted(t), d)
    return best


def loadbearing_pin(V):
    """L2(b) candidate: avoid the two statically dead rows {0,2} (M1b sec. 2:
    the load-bearing block is rank 33) and complete with an aux row."""
    from scipy.linalg import qr
    mid, _ = L.v3_jacobian()
    act = set(L.active_positions())
    pool = [k for k in (list(range(36)) + list(L.AUX_POS))
            if k in act and k not in (0, 2)]
    sub = mid[pool]
    _, _, piv = qr(sub.T, pivoting=True, mode='economic')
    P = sorted(pool[p] for p in piv[:34])
    if len(set(P)) != 34:
        return None
    if abs(np.linalg.det(mid[P])) < 1e-14:
        return None
    return P


def main():
    t0 = time.time()
    os.makedirs(L.RESULTS, exist_ok=True)
    V0 = L.VARIANTS[0]
    hdes = Fraction(3, 1000)
    out = {'meta': {'task': 'A36 L2 reach optimisation', 'dps': 60,
                    'r_N': M.fs(L.R_N), 'n_variants': len(L.VARIANTS),
                    'design_h': M.fs(hdes)},
           'pin_bases': [], 'variants': []}

    # ---------------- (b) pin-basis candidates
    cands = [('A22-S', list(L.S_EXT), L.a22_Y_v3()),
             ('A22-S-refitY', list(L.S_EXT), None)]
    lb = loadbearing_pin(V0)
    if lb:
        cands.append(('loadbearing-noDead', lb, None))
    sc, Pb, det = local_search_pin(V0, hdes)
    cands.append(('localsearch', Pb, None))
    print('local search estimate h ~ %.4e  (keff=%.3f Hbar=%.3f beta=%.4f '
          'kappa=%.3f)' % ((sc,) + tuple(det)))

    best = None
    for nm, P, Y in cands:
        try:
            h_r, cert = bisect_reach(V0, P, Y, rational=False)
        except Exception as e:                                # noqa: BLE001
            print('  %-20s FAILED (%s)' % (nm, e))
            continue
        if h_r is None:
            print('  %-20s no reach' % nm)
            continue
        Yv, beta, kappa, c = pin_data(P, h_r, Y=Y)
        rec = {'name': nm, 'P': P, 'reach_float': float(h_r),
               'reach': M.fs(h_r), 'beta': cert['beta'], 'kappa': cert['kappa'],
               'kappa_eff': cert['kappa_eff'], 'Hbar': cert['Hbar'],
               'kappa_over_1mbeta': cert['kappa'] / (1 - cert['beta']),
               'x_star': cert['x_star']}
        out['pin_bases'].append(rec)
        print('  %-20s reach %.5e  keff=%.3f Hbar=%.3f beta=%.4f kappa=%.3f'
              % (nm, float(h_r), cert['kappa_eff'], cert['Hbar'],
                 cert['beta'], cert['kappa']))
        if best is None or float(h_r) > best[0]:
            best = (float(h_r), nm, P, Y)
    _, bname, BP, BY = best
    if BY is None:
        BY = L.make_Y(BP)
    out['chosen_pin'] = {'name': bname, 'P': BP}
    print('chosen pin basis: %s' % bname)

    # ---------------- (a)+(c) per-variant certified reach
    for V in L.VARIANTS:
        h_r, cert = bisect_reach(V, BP, BY, rational=False)
        if h_r is None:
            out['variants'].append({'variant': [L.AXIS_NAME[a] for a in V],
                                    'tag': L.variant_tag(V),
                                    'reach_float': 0.0, 'failed': True})
            print('  %-24s NO REACH' % L.variant_tag(V))
            continue
        # confirm with the RATIONAL omega at a slightly reduced radius
        h_use = Fraction(int(float(h_r) * 0.98 * 10 ** 7), 10 ** 7)
        cert_r, omq = eval_at(V, BP, BY, h_use, rational=True)
        rec = {'variant': [L.AXIS_NAME[a] for a in V],
               'tag': L.variant_tag(V),
               'reach_float': float(h_r), 'reach': M.fs(h_r),
               'reach_over_rN': float(h_r) / float(L.R_N),
               'rational_h': M.fs(h_use),
               'rational_ok': bool(cert_r and cert_r['ok']),
               'beta': cert['beta'], 'kappa': cert['kappa'],
               'kappa_eff': cert['kappa_eff'], 'Hbar': cert['Hbar'],
               'eps_0': cert['eps_0'], 'eps_w': cert['eps_w'],
               'psi_over_h': cert['psi_over_h'], 'x_star': cert['x_star'],
               'alpha_min': cert['alpha_min'],
               'psi_A35form_over_h': cert['psi_A35form'] / cert['h_float'],
               'n_valid_rows': len(L.variant_rows(V))}
        # name the binding constant
        num = cert['kappa_eff'] * cert['Hbar'] * cert['h_float']
        rec['binding'] = {
            'term': 'kappa_eff * Hbar * h / (1 - beta)',
            'kappa_eff*Hbar/(1-beta)': cert['kappa_eff'] * cert['Hbar'] /
            (1 - cert['beta']),
            'share_Hbar_term': num / (1 - cert['beta']) / cert['psi_over_h'],
        }
        out['variants'].append(rec)
        print('  %-24s h_V = %.5e = %.3f r_N  (keff=%.3f Hbar=%.3f '
              'beta=%.4f)  ratOK=%s'
              % (rec['tag'], rec['reach_float'], rec['reach_over_rN'],
                 cert['kappa_eff'], cert['Hbar'], cert['beta'],
                 rec['rational_ok']))
    hs = min(r['reach_float'] for r in out['variants'])
    out['h_star_float'] = hs
    out['h_star_over_rN'] = hs / float(L.R_N)
    argmin = [r['tag'] for r in out['variants'] if r['reach_float'] == hs]
    out['h_star_binding_variants'] = argmin
    l1 = json.load(open(os.path.join(L.RESULTS, 'a36_l1.json')))
    out['h_L1_max'] = l1['h_L1_max']
    out['h_composed'] = min(hs, l1['h_L1_max'])
    out['h_composed_over_rN'] = out['h_composed'] / float(L.R_N)
    out['meta']['wall_seconds'] = time.time() - t0
    with open(os.path.join(L.RESULTS, 'a36_reach.json'), 'w') as f:
        json.dump(out, f, indent=1)
    print('h* = %.6e = %.3f r_N   (L1 cap %.6e)  composed %.6e = %.3f r_N'
          % (hs, out['h_star_over_rN'], l1['h_L1_max'], out['h_composed'],
             out['h_composed_over_rN']))
    print('%.1f s' % out['meta']['wall_seconds'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
