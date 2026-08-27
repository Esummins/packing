#!/usr/bin/env python
"""Standalone re-checker for results/m2_certs/*.json  (A35 / M2 Task 3, (W) certs).

recheck.py style.  Uses ONLY mpmath.iv + fractions + json, plus the interval-jet
row language of its sibling m2_check_inflation.py (which is itself standalone:
no strata_lib / t3lib / a22lib / numpy).  Nothing from the producing code is
imported, and no [NUM] object (kernel, rank-deficiency, mechanism direction)
enters the verification: the (W) certificate is a pure inequality argument.

For each certificate file it verifies, over box(z-hat, h_W):

  [O] omega is rational, ||omega||_inf <= 1, and omega_b >= alpha_min > 0 for
      every broken row b in B (this is the Motzkin witness: nonnegativity on
      the broken rows is what makes W a barrier).
  [Z] eps_0 := sum_k |omega_k| |g_k(z-hat)|                   <= claimed,
      g_max := max_k |g_k(z-hat)|                              <= claimed
  [G] eps_w := || A(z-hat)^T omega ||_1                        <= claimed
      (omega is a self-stress up to eps_w; rank(A) = 34 is A22/M1's, but the
      re-check needs only the residual bound, not the rank)
  [H] Hbar_W := (1/2) sum_{i,j} sup_box |d2 W / dz_i dz_j|     <= claimed,
      W = sum_k omega_k g_k, order-2 interval jets
  [K] beta := sup ||I - Y A_S(box(h_W))||_inf < 1 and <= claimed;
      kappa := ||Y||_inf                                       == claimed
  [P] the pinning inequality, with
          T_W(x) := (eps_0 + eps_w x + Hbar_W x^2)/alpha_min + g_max
      (the g_max term is there because the rigidity step bounds
       ||F_S(z) - F_S(z-hat)||_inf, and F_S(z-hat) is only ~1e-59, not 0):
          psi := kappa T_W(h)/(1-beta) < h
      and the least fixed point x* of x -> kappa T_W(x)/(1-beta) satisfies
      x* <= r_N.
  [V] edge-row SAT-selection validity over box(h_W): |tangential| < 1/2 and
      depth > -1/2 (without it the 38 rows are not the physical contacts).

Conclusion certified per file:
  every z with g_m(z) = 0 for the retained rows m and g_b(z) >= 0 for the
  broken rows b, lying in box(z-hat, h_W), satisfies ||z - z-hat||_inf <= x*
  <= r_N; hence by A22's theorem sigma(z) >= s-hat with equality iff z = z-hat.

Exit 0 = all PASS.
Usage: python m2_check_route.py [results/m2_certs] [path/to/krawczyk_cert.json]
"""
import glob
import json
import math
import os
import sys
from fractions import Fraction

from mpmath import iv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from m2_check_inflation import (NV, box_of, cnum, frac, mag, row_jet,  # noqa
                                sum_up, HALF, NHAT)

iv.dps = 60


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
    cons = K['constraints'][:38]
    S = cert['S_rows']
    Y = [[frac(v) for v in row] for row in K['Y']]
    rN = frac(K['r_N'])
    om = [frac(x) for x in cert['omega_rational']]
    B = list(cert['B'])
    alpha = frac(cert['alpha_min'])
    h = frac(cert['h_W'])
    hf = float(h)
    cl = cert['claims']
    tag = 'B=%s' % B

    # [O]
    ck('O %s alpha_min = min_{b in B} omega_b' % tag,
       alpha == min(om[b] for b in B) and alpha > 0,
       'alpha_min = %s' % cert['alpha_min'])
    ck('O %s omega_b >= alpha_min > 0 on B' % tag,
       all(om[b] >= alpha for b in B) and alpha > 0)
    ck('O %s ||omega||_inf <= 1' % tag, max(abs(x) for x in om) <= 1)

    box = box_of(z0, h)
    pbox = [cnum(x) for x in z0]

    # [Z] and [G] at the centre
    gvals = [mag(row_jet(pbox, cons[k], 0)[0].v) for k in range(38)]
    e0 = sum_up([abs(float(om[k])) * gvals[k]
                 for k in range(38) if om[k] != 0])
    gmax = max(gvals)
    ck('Z %s eps_0' % tag, e0 <= cl['eps_0'] * 1.0000001 + 1e-300,
       'recomputed %.3e <= claimed %.3e' % (e0, cl['eps_0']))
    ck('Z %s g_max' % tag, gmax <= cl['g_max'] * 1.0000001 + 1e-300,
       'recomputed %.3e <= claimed %.3e' % (gmax, cl['g_max']))
    acc = [iv.mpf(0)] * NV
    for k in range(38):
        if om[k] == 0:
            continue
        ok_ = cnum(om[k])
        j, vs = row_jet(pbox, cons[k], 1)
        for loc, gi in enumerate(vs):
            acc[gi] = acc[gi] + ok_ * j.g[loc]
    ew = sum_up([mag(acc[gi]) for gi in range(NV)])
    ck('G %s eps_w = ||A^T omega||_1' % tag,
       ew <= cl['eps_w'] * 1.0000001 + 1e-300,
       'recomputed %.3e <= claimed %.3e' % (ew, cl['eps_w']))

    # [H] Hessian of W over the box
    H = {}
    for k in range(38):
        if om[k] == 0:
            continue
        ok_ = cnum(om[k])
        j, vs = row_jet(box, cons[k], 2)
        for a, ga in enumerate(vs):
            for b, gb in enumerate(vs):
                key = (ga, gb)
                t = ok_ * j.h[a][b]
                H[key] = t if key not in H else H[key] + t
    Hsum = sum_up([mag(x) for x in H.values()])
    Hbar = Hsum / 2.0
    ck('H %s Hbar_W' % tag, Hbar <= cl['Hbar_W'] * 1.0000001,
       'recomputed %.6f <= claimed %.6f' % (Hbar, cl['Hbar_W']))

    # [K] beta, kappa
    grads = []
    for k in S:
        j, vs = row_jet(box, cons[k], 1)
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
    ck('K %s kappa = ||Y||_inf' % tag, kappa <= cl['kappa'] * 1.0000001,
       'recomputed %.6f' % kappa)

    # [P] pinning
    a = float(alpha)
    Cc = kappa / ((1.0 - beta) * a)
    Cg = kappa * gmax / (1.0 - beta)
    psi = Cc * (e0 + ew * hf + Hbar * hf * hf) + Cg
    ck('P %s contraction psi(h) < h' % tag, psi < hf,
       'psi = %.6e vs h = %.6e (ratio %.4f)' % (psi, hf, psi / hf))
    x = hf
    for _ in range(400):
        x = Cc * (e0 + ew * x + Hbar * x * x) + Cg
    ck('P %s fixed point x* <= r_N' % tag, x <= float(rN),
       'x* = %.4e <= r_N = %.4e' % (x, float(rN)))
    ck('P %s x* <= claimed' % tag, x <= cl['x_star'] * 1.0000001 + 1e-300,
       'recomputed %.4e <= claimed %.4e' % (x, cl['x_star']))

    # [V] edge selection validity on box(h_W)
    wt, wd = 1e9, 1e9
    for c in cons:
        if c['kind'] != 'edge':
            continue
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
        wt = min(wt, 0.5 - mag(-ny * wx + nx * wy))
        wd = min(wd, -math.nextafter(float(-iv.mpf(nx * wx + ny * wy).a),
                                     math.inf) + 0.5)
    ck('V %s edge SAT selection valid on box(h_W)' % tag, wt > 0 and wd > 0,
       'tangential margin %.6f, depth+1/2 %.6f' % (wt, wd))
    if verbose:
        print('  [ok] %-28s h_W=%-10s beta=%.5f Hbar=%.4f psi/h=%.4f '
              'x*=%.2e' % (tag, cert['h_W'], beta, Hbar, psi / hf, x))
    return dict(B=B, h_W=hf, beta=beta, Hbar=Hbar, psi_over_h=psi / hf,
                x_star=x, tan=wt)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    args = list(sys.argv[1:])
    if '--corrupt' in args:
        i = args.index('--corrupt')
        del args[i:i + 2]
    cdir = (args[0] if len(args) > 0 else
            os.path.join(here, '..', 'results', 'm2_certs'))
    kpath = (args[1] if len(args) > 1 else
             os.path.join(here, '..', '..', 'A22-local-rigidity', 'results',
                          'krawczyk_cert.json'))
    K = json.load(open(kpath))
    files = sorted(glob.glob(os.path.join(cdir, 'W_*.json')))
    if not files:
        print('no certificates found in %s' % cdir)
        return 1
    print('re-checking %d (W) certificates in %s' % (len(files),
                                                     os.path.abspath(cdir)))
    corrupt = None
    if '--corrupt' in sys.argv:
        corrupt = sys.argv[sys.argv.index('--corrupt') + 1]
        print('*** CORRUPTION TEST: %s (this run MUST fail) ***' % corrupt)
        files = files[:1]
    ck = Check()
    rows = []
    for i, f in enumerate(files):
        cert = json.load(open(f))
        if corrupt == 'omega-sign':        # flip omega on a broken row
            b = cert['B'][0]
            cert['omega_rational'][b] = '-' + cert['omega_rational'][b]
        elif corrupt == 'omega-perturb':   # break the self-stress identity
            v = frac(cert['omega_rational'][5]) + Fraction(1, 1000)
            cert['omega_rational'][5] = '%d/%d' % (v.numerator, v.denominator)
        elif corrupt == 'h-big':           # claim 4x the certified radius
            cert['h_W'] = '%d/%d' % ((frac(cert['h_W']) * 4).numerator,
                                     (frac(cert['h_W']) * 4).denominator)
        elif corrupt == 'spec':            # tamper with a contact definition
            K = json.loads(json.dumps(K))
            for c in K['constraints']:
                if c['kind'] == 'edge':
                    c['edge'] = (c['edge'] + 1) % 4
                    break
        elif corrupt is not None:
            raise SystemExit('unknown corruption mode')
        rows.append(check_cert(cert, K, ck, verbose=(i % 20 == 0)))
    if corrupt:
        bad = bool(ck.fails)
        print('corruption test %s: %s' % (corrupt, 'OK (checker failed as '
              'required)' if bad else 'PROBLEM: checker still passes!'))
        return 0 if bad else 2
    hs = [r['h_W'] for r in rows]
    print('  %d certificates, %d checks, h_W in [%.6g, %.6g], '
          'max psi/h = %.4f, max x* = %.3e, min tangential margin = %.5f'
          % (len(rows), ck.n, min(hs), max(hs),
             max(r['psi_over_h'] for r in rows),
             max(r['x_star'] for r in rows), min(r['tan'] for r in rows)))
    print('=> %s' % ('ALL CHECKS PASS' if not ck.fails
                     else 'FAILURES: %s' % sorted(set(ck.fails))[:10]))
    return 0 if not ck.fails else 1


if __name__ == '__main__':
    sys.exit(main())
