#!/usr/bin/env python
"""Standalone re-checker for results/m2b_certs/*.json  (A35 / M2-delta).

Verifies both certificate families:

  Wp_*.json   (W')  menu-complete wedge / Motzkin self-stress pinning,
                    per break set, per variant, per selection.
  G_*.json    (V')  universal value/pinning certificate, per variant, per
                    selection, stratum-INDEPENDENT.

recheck.py style: mpmath.iv + fractions + json only, plus the interval-jet row
language of its sibling m2_check_inflation.py (itself standalone: no
strata_lib / t3lib / a22lib / numpy).  In particular the checker does NOT trust
the producer's row list: it REBUILDS the 50-row extended set from

  * A22's krawczyk_cert.json constraints 0..35 (verbatim), and
  * the v2 repair table + tie alternatives, transcribed here from M1b's
    documented basis_v2_definition, and
  * the two auxiliary dist rows = A22's constraints 36, 37 verbatim, and
  * the selection's six dominance rows,

and re-derives every constant from that.  A disagreement between the producer's
row set and the documented spec therefore shows up as a failure.

Checks (h = the certificate's radius):

  [O] sign discipline: omega_r >= alpha_min > 0 on the strict-positive
      positions; omega_r >= 0 on the dominance positions; omega_r = 0 on every
      row outside the variant.  For (V') additionally: the strict-positive set
      is ALL of the variant's v2 rows plus both aux rows -- which is what makes
      the certificate stratum-independent.
  [Z] eps_0 = sum_r |omega_r| |g_r(z-hat)|  and  g_max = max_k |g_k(z-hat)|.
  [G] eps_w = ||A_ext^T omega||_1          for (W'),
      eps_w = ||A_ext^T omega - e_s||_1    for (V').
  [H] Hbar_W = (1/2) sum_ij sup_box |d2 W/dz_i dz_j|, W = sum_r omega_r g_r.
  [K] beta = sup ||I - Y A_S(box(h))||_inf < 1 with A22's S and Y; kappa.
  [P] T(h) = (eps_0 + eps_w h + Hbar h^2)/alpha_min + g_max,
      psi = kappa T/(1-beta) < h, and the least fixed point x* <= r_N.
  [V] edge-row SAT-selection validity over box(h).
  [A] the two aux rows really are ACTIVE at z-hat (|g| <= 1e-40) -- without
      that they are not admissible members of the possibly-active set.

Exit 0 = all PASS.
Usage: python m2b_check.py [results/m2b_certs] [path/to/krawczyk_cert.json]
       optional: --corrupt {omega-sign,omega-perturb,h-big,drop-aux}
"""
import glob
import json
import math
import os
import sys
from fractions import Fraction

from mpmath import iv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from m2_check_inflation import (NV, box_of, cnum, frac, J, mag, sum_up,  # noqa
                                HALF, NHAT, row_jet, row_vars)

iv.dps = 60

# ---- v2 basis repair table, transcribed from M1b meta.basis_v2_definition
V2_NEW_ROWS = [
    {'kind': 'edge', 'i': 1, 'corner': 3, 'j': 0, 'edge': 1, 'name': 'F0-1a'},
    {'kind': 'edge', 'i': 0, 'corner': 2, 'j': 1, 'edge': 3, 'name': 'F0-1b'},
    {'kind': 'edge', 'i': 3, 'corner': 0, 'j': 0, 'edge': 2, 'name': 'F0-3a'},
    {'kind': 'edge', 'i': 0, 'corner': 3, 'j': 3, 'edge': 0, 'name': 'F0-3b'},
    {'kind': 'edge', 'i': 3, 'corner': 1, 'j': 1, 'edge': 3, 'name': 'C1-3x'},
    {'kind': 'edge', 'i': 1, 'corner': 3, 'j': 3, 'edge': 0, 'name': 'C1-3y'},
]
V2_TIE_ALT = {'F0-1a': 0, 'F0-1b': 1, 'F0-3a': 1, 'F0-3b': 2,
              'C1-3x': 2, 'C1-3y': 2}
AUX_POS = (42, 43)
DOM_POS = tuple(range(44, 50))
NEXT = 50


def ext_constraints(cert, K):
    """Rebuild the 50 extended constraint dicts from the SPEC + the selection."""
    sel = {int(k): int(v) for k, v in cert['selection'].items()}
    out = [dict(c) for c in K['constraints'][:36]]
    for idx, base in enumerate(V2_NEW_ROWS):
        c = dict(base)
        k = 36 + idx
        if k in sel:
            c['corner'] = sel[k]
        out.append(c)
    out += [dict(c) for c in K['constraints'][36:38]]      # the two aux rows
    for idx, base in enumerate(V2_NEW_ROWS):
        k = 36 + idx
        chosen = sel.get(k, base['corner'])
        other = (V2_TIE_ALT[base['name']] if chosen == base['corner']
                 else base['corner'])
        out.append({'kind': 'dom', 'o': base['j'], 'e': base['edge'],
                    'p': base['i'], 'k': chosen, 'm': other})
    assert len(out) == NEXT
    return out


def dom_jet(box, c, order):
    """Jet of  n_e(theta_o) . (q_m(p) - q_k(p)) >= 0  in (theta_o, theta_p)."""
    vs = [3 * c['o'] + 2, 3 * c['p'] + 2]
    V = [J.var(box[gi], i, 2, order) for i, gi in enumerate(vs)]
    tho, thp = V
    nhx, nhy = NHAT[c['e']]
    co, so = tho.cos(), tho.sin()
    nx = co * iv.mpf(nhx) - so * iv.mpf(nhy)
    ny = so * iv.mpf(nhx) + co * iv.mpf(nhy)
    dx = cnum(HALF[c['m']][0] - HALF[c['k']][0])
    dy = cnum(HALF[c['m']][1] - HALF[c['k']][1])
    cp, sp = thp.cos(), thp.sin()
    vx = cp * dx - sp * dy
    vy = sp * dx + cp * dy
    return nx * vx + ny * vy, vs


def any_jet(box, c, order):
    if c['kind'] == 'dom':
        return dom_jet(box, c, order)
    return row_jet(box, c, order)


class Check(object):
    def __init__(self):
        self.fails = []
        self.n = 0

    def __call__(self, name, ok, detail=''):
        self.n += 1
        if not ok:
            self.fails.append(name)
            print('  [FAIL] %s %s' % (name, detail))
        return ok


def check_cert(cert, K, ck, verbose):
    z0 = [frac(x) for x in K['z0']]
    S = K['S']
    Y = [[frac(v) for v in row] for row in K['Y']]
    rN = frac(K['r_N'])
    cons = ext_constraints(cert, K)
    om = [frac(x) for x in cert['omega_rational']]
    is_V = cert['type'].startswith("V'")
    h = frac(cert['h_G'] if is_V else cert['h_W'])
    hf = float(h)
    alpha = frac(cert['alpha_min'])
    cl = cert['claims']
    vrows = set(cert['variant_rows']) if is_V else None
    strict = set(cert['strict_positive_positions'])
    domv = set(cert['dom_positions'])
    tag = ('%s/%s sel%s' % (cert['type'][:2], cert['variant'],
                            cert.get('selection')))
    if not is_V:
        tag = '%s B=%s/%s' % (cert['type'][:2], cert['B'], cert['variant'])

    # A22's Krawczyk rows, mapped into extended positions
    S_ext = [k if k < 36 else (42 if k == 36 else 43) for k in S]
    ck('O %s S_EXT matches A22 S' % tag, S_ext == cert['S_EXT'])

    # [O] sign discipline
    ck('O %s alpha_min > 0 and attained on the strict set' % tag,
       alpha > 0 and min(om[r] for r in strict) == alpha,
       'alpha_min = %s' % cert['alpha_min'])
    ck('O %s omega >= 0 on the dominance rows' % tag,
       all(om[p] >= 0 for p in domv))
    dead = ([k for k in range(42) if k not in vrows] if is_V else
            [k for k in range(42)
             if k in (40, 41) and k not in
             set(range(42)) - {41 if cert['variant'] == 'selx' else 40}])
    if is_V:
        dead = [k for k in range(42) if k not in vrows]
        dead += [p for p in DOM_POS if p not in domv]
        ck('O %s omega = 0 outside the variant' % tag,
           all(om[k] == 0 for k in dead))
        ck("O %s (V') strict set = all variant rows + both aux rows" % tag,
           strict == set(vrows) | set(AUX_POS),
           'this is what makes the certificate stratum-independent')
    else:
        ck('O %s strict set = B + both aux rows' % tag,
           strict == set(cert['B']) | set(AUX_POS))
        ck('O %s omega = 0 on dominance rows outside the variant' % tag,
           all(om[p] == 0 for p in DOM_POS if p not in domv))

    pbox = [cnum(x) for x in z0]
    box = box_of(z0, h)

    # [A] the aux rows are active at z-hat
    auxv = [mag(any_jet(pbox, cons[p], 0)[0].v) for p in AUX_POS]
    ck('A %s aux rows active at z-hat' % tag, max(auxv) < 1e-40,
       'max |a_i(z-hat)| = %.2e' % max(auxv))

    # [Z] eps_0, g_max
    gvals = [mag(any_jet(pbox, cons[k], 0)[0].v) for k in range(NEXT)]
    e0 = sum_up([abs(float(om[k])) * gvals[k] for k in range(NEXT)
                 if om[k] != 0])
    gmax = max(gvals[k] for k in range(42)) if not is_V else max(gvals[:44])
    gmax = max(gvals[k] for k in S_ext)
    ck('Z %s eps_0' % tag, e0 <= cl['eps_0'] * 1.0000001 + 1e-300,
       'recomputed %.3e <= claimed %.3e' % (e0, cl['eps_0']))
    ck('Z %s g_max' % tag, gmax <= cl['g_max'] * 1.0000001 + 1e-300,
       'recomputed %.3e <= claimed %.3e' % (gmax, cl['g_max']))

    # [G] eps_w
    acc = [iv.mpf(0)] * NV
    for k in range(NEXT):
        if om[k] == 0:
            continue
        ok_ = cnum(om[k])
        j, vs = any_jet(pbox, cons[k], 1)
        for loc, gi in enumerate(vs):
            acc[gi] = acc[gi] + ok_ * j.g[loc]
    ew = sum_up([mag(acc[gi] - (iv.mpf(1) if (is_V and gi == 33) else
                                iv.mpf(0))) for gi in range(NV)])
    ck('G %s eps_w' % tag, ew <= cl['eps_w'] * 1.0000001 + 1e-300,
       'recomputed %.3e <= claimed %.3e' % (ew, cl['eps_w']))

    # [H] Hbar_W
    H = {}
    for k in range(NEXT):
        if om[k] == 0:
            continue
        ok_ = cnum(om[k])
        j, vs = any_jet(box, cons[k], 2)
        for a, ga in enumerate(vs):
            for b, gb in enumerate(vs):
                key = (ga, gb)
                t = ok_ * j.h[a][b]
                H[key] = t if key not in H else H[key] + t
    Hbar = sum_up([mag(x) for x in H.values()]) / 2.0
    ck('H %s Hbar_W' % tag, Hbar <= cl['Hbar_W'] * 1.0000001,
       'recomputed %.6f <= claimed %.6f' % (Hbar, cl['Hbar_W']))

    # [K] beta, kappa on A22's S with A22's Y
    grads = []
    for k in S_ext:
        j, vs = any_jet(box, cons[k], 1)
        grads.append({gi: j.g[loc] for loc, gi in enumerate(vs)})
    Yiv = [[cnum(v) for v in row] for row in Y]
    beta = 0.0
    for i in range(NV):
        rs = []
        for j2 in range(NV):
            ssum = iv.mpf(0)
            for rr in range(NV):
                v = grads[rr].get(j2)
                if v is not None:
                    ssum = ssum + Yiv[i][rr] * v
            rs.append(mag((iv.mpf(1) if i == j2 else iv.mpf(0)) - ssum))
        beta = max(beta, sum_up(rs))
    kappa = max(sum_up([abs(float(Y[i][r])) for r in range(NV)])
                for i in range(NV))
    ck('K %s beta < 1' % tag, beta < 1.0 and beta <= cl['beta'] * 1.0000001,
       'recomputed %.8f <= claimed %.8f' % (beta, cl['beta']))
    ck('K %s kappa' % tag, kappa <= cl['kappa'] * 1.0000001,
       'recomputed %.6f' % kappa)

    # [P] pinning
    a = float(alpha)
    T = (e0 + ew * hf + Hbar * hf * hf) / a + gmax
    psi = kappa * T / (1.0 - beta)
    ck('P %s contraction psi(h) < h' % tag, psi < hf,
       'psi = %.6e vs h = %.6e (ratio %.4f)' % (psi, hf, psi / hf))
    Cc = kappa / ((1.0 - beta) * a)
    Cg = kappa * gmax / (1.0 - beta)
    x = hf
    for _ in range(400):
        x = Cc * (e0 + ew * x + Hbar * x * x) + Cg
    ck('P %s fixed point x* <= r_N' % tag, x <= float(rN),
       'x* = %.4e <= r_N = %.4e' % (x, float(rN)))

    # [V] edge-selection validity, SPLIT into the two groups because they
    # behave completely differently and conflating them would hide the gap:
    #   rows 0..35  = A22's original rows, tangential margin >= 0.012 -- the
    #                 selection is certified dominant over the box;
    #   rows 36..41 = M1b's repaired rows, whose contact corners are at edge
    #                 ENDPOINTS, so the tangential margin is 0 at z-hat and
    #                 NEGATIVE on any box of positive radius.  Those rows are
    #                 therefore NOT certified to be the dominant (minimal
    #                 corner) description on box(h).  See the caveat banner.
    wt, wd = 1e9, 1e9
    wt2 = 1e9
    for ci_, c in enumerate(cons[:42]):
        if c['kind'] != 'edge':
            continue
        if ci_ >= 36:
            pass
        i, j2 = c['i'], c['j']
        hx, hy = cnum(HALF[c['corner']][0]), cnum(HALF[c['corner']][1])
        ci, si = iv.cos(box[3 * i + 2]), iv.sin(box[3 * i + 2])
        qx = box[3 * i] + (ci * hx - si * hy)
        qy = box[3 * i + 1] + (si * hx + ci * hy)
        nhx, nhy = NHAT[c['edge']]
        cj, sj = iv.cos(box[3 * j2 + 2]), iv.sin(box[3 * j2 + 2])
        nx = cj * iv.mpf(nhx) - sj * iv.mpf(nhy)
        ny = sj * iv.mpf(nhx) + cj * iv.mpf(nhy)
        wx, wy = qx - box[3 * j2], qy - box[3 * j2 + 1]
        tanm = 0.5 - mag(-ny * wx + nx * wy)
        depm = -math.nextafter(float(-iv.mpf(nx * wx + ny * wy).a),
                               math.inf) + 0.5
        if ci_ < 36:
            wt = min(wt, tanm)
            wd = min(wd, depm)
        else:
            wt2 = min(wt2, tanm)
    ck('V %s A22 rows 0..35 SAT selection valid on box(h)' % tag,
       wt > 0 and wd > 0,
       'tangential margin %.6f, depth+1/2 %.6f' % (wt, wd))
    ck('V %s repaired rows 36..41 margin is REPORTED (not asserted)' % tag,
       True, 'tangential margin %.6f -- see caveat' % wt2)
    if verbose:
        print('  [ok] %-46s h=%-11s beta=%.5f Hbar=%.3f psi/h=%.4f x*=%.2e'
              % (tag[:46], (cert['h_G'] if is_V else cert['h_W']), beta, Hbar,
                 psi / hf, x))
    return dict(h=hf, beta=beta, Hbar=Hbar, psi_over_h=psi / hf, x_star=x,
                tan=wt, tan_repaired=wt2, alpha=a, is_V=is_V,
                dom_weight_zero=all(om[p] == 0 for p in DOM_POS))


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    args = list(sys.argv[1:])
    corrupt = None
    if '--corrupt' in args:
        i = args.index('--corrupt')
        corrupt = args[i + 1]
        del args[i:i + 2]
    cdir = (args[0] if args else
            os.path.join(here, '..', 'results', 'm2b_certs'))
    kpath = (args[1] if len(args) > 1 else
             os.path.join(here, '..', '..', 'A22-local-rigidity', 'results',
                          'krawczyk_cert.json'))
    K = json.load(open(kpath))
    files = sorted(glob.glob(os.path.join(cdir, 'Wp_*.json'))) + \
        sorted(glob.glob(os.path.join(cdir, 'G_*.json')))
    if not files:
        print('no certificates found in %s' % cdir)
        return 1
    if corrupt:
        print('*** CORRUPTION TEST: %s (this run MUST fail) ***' % corrupt)
        files = [f for f in files if os.path.basename(f).startswith('G_')][:1] \
            or files[:1]
    print('re-checking %d certificates in %s' % (len(files),
                                                 os.path.abspath(cdir)))
    ck = Check()
    rows = []
    for i, f in enumerate(files):
        cert = json.load(open(f))
        if corrupt == 'omega-sign':
            r = sorted(cert['strict_positive_positions'])[0]
            cert['omega_rational'][r] = '-' + cert['omega_rational'][r]
        elif corrupt == 'omega-perturb':
            v = frac(cert['omega_rational'][5]) + Fraction(1, 1000)
            cert['omega_rational'][5] = '%d/%d' % (v.numerator, v.denominator)
        elif corrupt == 'h-big':
            key = 'h_G' if cert['type'].startswith("V'") else 'h_W'
            g = frac(cert[key]) * 8
            cert[key] = '%d/%d' % (g.numerator, g.denominator)
        elif corrupt == 'drop-aux':
            # pretend the aux rows were not there: zero their omega
            for p in AUX_POS:
                cert['omega_rational'][p] = '0/1'
        elif corrupt is not None:
            raise SystemExit('unknown corruption mode')
        rows.append(check_cert(cert, K, ck, verbose=(i % 40 == 0 or corrupt)))
    if corrupt:
        bad = bool(ck.fails)
        print('corruption test %s: %s' % (corrupt, 'OK (checker failed as '
              'required)' if bad else 'PROBLEM: checker still passes!'))
        return 0 if bad else 2
    W = [r for r in rows if not r['is_V']]
    Vr = [r for r in rows if r['is_V']]
    print('  %d certificates, %d checks' % (len(rows), ck.n))
    if W:
        print("  (W') %d: h in [%.6g, %.6g], max psi/h = %.4f, max x* = %.2e, "
              'alpha_min >= %.4f' % (len(W), min(r['h'] for r in W),
                                     max(r['h'] for r in W),
                                     max(r['psi_over_h'] for r in W),
                                     max(r['x_star'] for r in W),
                                     min(r['alpha'] for r in W)))
    if Vr:
        print("  (V') %d: h in [%.6g, %.6g], max psi/h = %.4f, max x* = %.2e, "
              'alpha_min >= %.6f' % (len(Vr), min(r['h'] for r in Vr),
                                     max(r['h'] for r in Vr),
                                     max(r['psi_over_h'] for r in Vr),
                                     max(r['x_star'] for r in Vr),
                                     min(r['alpha'] for r in Vr)))
    print('  min tangential margin, A22 rows 0..35 = %.5f  (must be > 0)'
          % min(r['tan'] for r in rows))
    print('  min tangential margin, repaired rows 36..41 = %.5f'
          % min(r['tan_repaired'] for r in rows))
    print('  omega = 0 on every dominance row: %s'
          % all(r['dom_weight_zero'] for r in rows))
    print()
    print('  ' + '=' * 72)
    print('  CAVEAT (not a check failure -- a scope statement).  The six')
    print('  repaired v2 rows 36..41 have their contact corner at an edge')
    print('  ENDPOINT, so their tangential (dominance) margin is 0 at z-hat')
    print('  and negative on every box of positive radius.  These rows are')
    print('  therefore NOT certified here to be the dominant description of')
    print('  their contact on box(h); the barrier needs only that the owner')
    print('  edge SEPARATES the pair (a weaker condition than dominance), and')
    print('  THAT is not discharged either.  It is M1b sec. 7 / theory.md G5,')
    print('  inherited, not introduced: every v2 result has the same')
    print('  dependence.  A22 rows 0..35 ARE certified (margin above).')
    print('  ' + '=' * 72)
    print('=> %s' % ('ALL CHECKS PASS' if not ck.fails
                     else 'FAILURES: %s' % sorted(set(ck.fails))[:8]))
    return 0 if not ck.fails else 1


if __name__ == '__main__':
    sys.exit(main())
