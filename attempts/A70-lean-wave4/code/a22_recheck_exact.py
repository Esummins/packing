#!/usr/bin/env python3
"""a22_recheck_exact.py -- EXACT-RATIONAL re-checker for A22's Krawczyk
certificate (A70, depgraph E.A22 / checklist F6 rung (a): mpmath.iv OUT of the
decision path).

Same chain, same certificate, same corruption gates as the frozen
attempts/A22-local-rigidity/recheck.py (which is NOT modified), but every
decision is made in exact rational arithmetic: intervals are Fraction pairs
outward-rounded to the dyadic 2^-330 grid, and cos/sin enclosures use certified
alternating Taylor partial sums (|x| <= 1).  The interval kernel is shared with
`a36_check_exact.py` (same directory).  stdlib only.

Checks (transcribed from recheck.py):
  [G] centre residuals; [K] Krawczyk contraction on box(z0, r_N) (unique z-hat),
  on box(z0, r_0) (tight enclosure), and for the angle-equality system S2/Y2;
  [V] edge validity margins; [E] multiplier identity; [B] all 68 Farkas
  certificates (beta < 1, signs, completeness); [F] feasibility of z-hat.
Strict interval containments are decided on the EXACT interval endpoints
(sharper than the original's outward-rounded mpmath endpoints -- sound: strict
containment in the true box is what Krawczyk consumes).

Usage:  python a22_recheck_exact.py [krawczyk_cert.json] [--corrupt MODE]
        MODE in {z0-big, z0-small, mu, spec}  (each must make the check FAIL)
Exit code 0 = all PASS, 1 = FAIL.
"""
import json
import sys
from fractions import Fraction

from a36_check_exact import IV, IZERO, IONE, cos_iv, sin_iv, frac, rup

HALF = [(Fraction(-1, 2), Fraction(-1, 2)), (Fraction(1, 2), Fraction(-1, 2)),
        (Fraction(1, 2), Fraction(1, 2)), (Fraction(-1, 2), Fraction(1, 2))]
NHAT = [(0, -1), (1, 0), (0, 1), (-1, 0)]
NV = 34


def rot(th, vx, vy):
    c, s = cos_iv(th), sin_iv(th)
    return vx * c - vy * s, vx * s + vy * c


def drot(th, vx, vy):
    c, s = cos_iv(th), sin_iv(th)
    return -vx * s - vy * c, vx * c - vy * s


def corner_pos(z, i, corner):
    hx, hy = HALF[corner]
    rx, ry = rot(z[3 * i + 2], hx, hy)
    return z[3 * i] + rx, z[3 * i + 1] + ry


def eval_g(z, c):
    if c['kind'] == 'angeq':
        return z[3 * c['i'] + 2] - z[3 * c['j'] + 2]
    if c['kind'] == 'wall':
        qx, qy = corner_pos(z, c['i'], c['corner'])
        return {'x=0': qx, 'y=0': qy,
                'x=s': z[33] - qx, 'y=s': z[33] - qy}[c['wall']]
    if c['kind'] == 'edge':
        i, j = c['i'], c['j']
        qx, qy = corner_pos(z, i, c['corner'])
        nhx, nhy = NHAT[c['edge']]
        nx, ny = rot(z[3 * j + 2], nhx, nhy)
        return nx * (qx - z[3 * j]) + ny * (qy - z[3 * j + 1]) - Fraction(1, 2)
    if c['kind'] == 'dist':
        i, j = c['i'], c['j']
        dx = z[3 * i] - z[3 * j]
        dy = z[3 * i + 1] - z[3 * j + 1]
        return dx * dx + dy * dy - 1
    raise ValueError(c['kind'])


def grad_g(z, c):
    g = {}
    if c['kind'] == 'angeq':
        g[3 * c['i'] + 2] = IONE
        g[3 * c['j'] + 2] = IV.point(Fraction(-1))
        return g
    if c['kind'] == 'wall':
        i = c['i']
        hx, hy = HALF[c['corner']]
        dx, dy = drot(z[3 * i + 2], hx, hy)
        w = c['wall']
        if w == 'x=0':
            g[3 * i] = IONE
            g[3 * i + 2] = dx
        elif w == 'y=0':
            g[3 * i + 1] = IONE
            g[3 * i + 2] = dy
        elif w == 'x=s':
            g[3 * i] = IV.point(Fraction(-1))
            g[3 * i + 2] = -dx
            g[33] = IONE
        elif w == 'y=s':
            g[3 * i + 1] = IV.point(Fraction(-1))
            g[3 * i + 2] = -dy
            g[33] = IONE
        return g
    if c['kind'] == 'edge':
        i, j = c['i'], c['j']
        hx, hy = HALF[c['corner']]
        nhx, nhy = NHAT[c['edge']]
        nx, ny = rot(z[3 * j + 2], nhx, nhy)
        qx, qy = corner_pos(z, i, c['corner'])
        wx, wy = qx - z[3 * j], qy - z[3 * j + 1]
        dhx, dhy = drot(z[3 * i + 2], hx, hy)
        dnx, dny = drot(z[3 * j + 2], nhx, nhy)
        g[3 * i] = nx
        g[3 * i + 1] = ny
        g[3 * j] = -nx
        g[3 * j + 1] = -ny
        g[3 * i + 2] = nx * dhx + ny * dhy
        g[3 * j + 2] = dnx * wx + dny * wy
        return g
    if c['kind'] == 'dist':
        i, j = c['i'], c['j']
        dx = z[3 * i] - z[3 * j]
        dy = z[3 * i + 1] - z[3 * j + 1]
        g[3 * i] = 2 * dx
        g[3 * i + 1] = 2 * dy
        g[3 * j] = -2 * dx
        g[3 * j + 1] = -2 * dy
        return g
    raise ValueError(c['kind'])


def edge_aux(z, c):
    i, j = c['i'], c['j']
    qx, qy = corner_pos(z, i, c['corner'])
    nhx, nhy = NHAT[c['edge']]
    nx, ny = rot(z[3 * j + 2], nhx, nhy)
    wx, wy = qx - z[3 * j], qy - z[3 * j + 1]
    return nx * wx + ny * wy, -ny * wx + nx * wy


def box(z0, r):
    return [IV(x - r, x + r) for x in z0]


def iv_min(a, b):
    return IV(min(a.lo, b.lo), min(a.hi, b.hi), rnd=False)


def iv_max(a, b):
    return IV(max(a.lo, b.lo), max(a.hi, b.hi), rnd=False)


def pair_sep_lb(z, i, j):
    """Exact lower bound of the SAT separation of squares i, j over z."""
    ci = [corner_pos(z, i, c) for c in range(4)]
    cj = [corner_pos(z, j, c) for c in range(4)]
    best = None
    for sq in (i, j):
        th = z[3 * sq + 2]
        for nhx, nhy in ((1, 0), (0, 1)):
            nx, ny = rot(th, nhx, nhy)
            pi = [nx * qx + ny * qy for qx, qy in ci]
            pj = [nx * qx + ny * qy for qx, qy in cj]
            lo_i = hi_i = pi[0]
            lo_j = hi_j = pj[0]
            for p in pi[1:]:
                lo_i = iv_min(lo_i, p)
                hi_i = iv_max(hi_i, p)
            for p in pj[1:]:
                lo_j = iv_min(lo_j, p)
                hi_j = iv_max(hi_j, p)
            gap = iv_max(lo_j - hi_i, lo_i - hi_j)
            best = gap if best is None else iv_max(best, gap)
    return best.lo


def ffloat(x):
    return Fraction(x)


class Checker:
    def __init__(self, cert):
        self.cert = cert
        self.z0 = [frac(x) for x in cert['z0']]
        self.rN = frac(cert['r_N'])
        self.r0 = frac(cert['r_0'])
        self.cons = cert['constraints']
        self.fails = []

    def check(self, name, ok, detail=''):
        print('  [%s] %s %s' % ('PASS' if ok else 'FAIL', name, detail))
        if not ok:
            self.fails.append(name)

    # ---- G: centre residuals
    def check_centre(self):
        zc = [IV.point(x) for x in self.z0]
        mx = Fraction(0)
        for c in self.cons:
            mx = max(mx, eval_g(zc, c).mag())
        self.check('G centre residual',
                   mx <= ffloat(self.cert['claims']['centre_residual_max']),
                   'max |g_k(z0)| <= %.2e over all %d rows'
                   % (float(mx), len(self.cons)))

    # ---- K: Krawczyk
    def krawczyk(self, Sname, Yname, r, tag):
        S = self.cert[Sname]
        Y = [[frac(v) for v in row] for row in self.cert[Yname]]
        B = box(self.z0, r)
        zc = [IV.point(x) for x in self.z0]
        Fc = [eval_g(zc, self.cons[k]) for k in S]
        Jrows = [grad_g(B, self.cons[k]) for k in S]
        dbox = IV(-r, r)
        ok = True
        worst = Fraction(0)
        for i in range(NV):
            acc = IZERO
            for rr in range(NV):
                acc = acc + Y[i][rr] * Fc[rr]
            Ki = -acc
            for j in range(NV):
                m = IONE if i == j else IZERO
                ssum = IZERO
                for rr in range(NV):
                    v = Jrows[rr].get(j)
                    if v is not None:
                        ssum = ssum + Y[i][rr] * v
                Ki = Ki + (m - ssum) * dbox
            worst = max(worst, Ki.mag() / r)
            if not (Ki.lo > -r and Ki.hi < r):
                ok = False
        self.check('K Krawczyk %s' % tag, ok, 'max|K|/r = %.4g' % float(worst))
        return ok

    # ---- V: validity margins over N
    def check_validity(self):
        B = box(self.z0, self.rN)
        tmin = ffloat(self.cert['claims']['tan_margin_min'])
        ok = True
        worst = Fraction(1)
        for k in self.cert['S']:
            c = self.cons[k]
            if c['kind'] != 'edge':
                continue
            dep, tan = edge_aux(B, c)
            m = Fraction(1, 2) - tan.mag()
            worst = min(worst, m)
            if not (m >= tmin and dep.lo > Fraction(-1, 2)):
                ok = False
        self.check('V edge validity margins', ok,
                   'min tangential margin = %.5f' % float(worst))

    # ---- E: multiplier identity
    def check_lambda(self):
        zc = [IV.point(x) for x in self.z0]
        lam = [frac(x) for x in self.cert['lambda']]
        acc = [IZERO] * NV
        for lam_k, k in zip(lam, self.cert['S']):
            for j, v in grad_g(zc, self.cons[k]).items():
                acc[j] = acc[j] + lam_k * v
        mx = Fraction(0)
        allpos = all(l > 0 for l in lam)
        for j in range(NV):
            mx = max(mx, (acc[j] - (IONE if j == 33 else IZERO)).mag())
        okr = mx <= ffloat(self.cert['claims']['lambda_residual_max'])
        self.check('E multiplier identity', okr and allpos,
                   '||A^T lam - e_s||_inf <= %.2e, all lam > 0: %s'
                   % (float(mx), allpos))

    # ---- B: Farkas certificate residuals over N
    def check_certs(self):
        B = box(self.z0, self.rN)
        Grows = [grad_g(B, self.cons[k]) for k in self.cert['S']]
        bmax = Fraction(0)
        numax = Fraction(0)
        ok = True
        seen = set()
        for cert in self.cert['certificates']:
            i, sg = cert['i'], cert['sigma']
            seen.add((i, sg))
            nu = frac(cert['nu'])
            mu = [frac(x) for x in cert['mu']]
            if nu < 0 or any(m < 0 for m in mu):
                ok = False
            numax = max(numax, nu)
            acc = {}
            for m, row in zip(mu, Grows):
                if m == 0:
                    continue
                for j, v in row.items():
                    acc[j] = acc.get(j, IZERO) + m * v
            l1 = Fraction(0)
            for j in range(NV):
                rho = (IV.point(Fraction(sg if j == i else 0)
                                + (nu if j == 33 else 0)) - acc.get(j, IZERO))
                l1 += rho.mag()
            bmax = max(bmax, l1)
        complete = len(seen) == 2 * NV
        okb = bmax <= ffloat(self.cert['claims']['beta_max']) and bmax < 1
        oknu = numax <= ffloat(self.cert['claims']['nu_max'])
        self.check('B Farkas certificates', ok and okb and oknu and complete,
                   'beta = %.4f (need < 1), nu_max = %.2f, all 68 present = %s'
                   % (float(bmax), float(numax), complete))

    # ---- F: feasibility of z-hat on box(z0, r0)
    def check_feasibility(self):
        B = box(self.z0, self.r0)
        ok = True
        wsep = None
        for i, j in self.cert['noncontact_pairs']:
            lb = pair_sep_lb(B, i, j)
            if wsep is None or lb < wsep:
                wsep = lb
            if lb <= 0:
                ok = False
        wreal = None
        for ent in self.cert['contact_edge_pairs']:
            c = self.cons[ent['con']]
            i, j = c['i'], c['j']
            nhx, nhy = NHAT[c['edge']]
            nx, ny = rot(B[3 * j + 2], nhx, nhy)
            projs = []
            for corner in range(4):
                qx, qy = corner_pos(B, i, corner)
                projs.append(nx * qx + ny * qy)
            pc = projs[c['corner']]
            for corner in range(4):
                if corner == c['corner']:
                    continue
                gap = (projs[corner] - pc).lo
                if wreal is None or gap < wreal:
                    wreal = gap
                if gap <= 0:
                    ok = False
        wallset = {(c['i'], c['corner'], c['wall'])
                   for c in self.cons if c['kind'] == 'wall'}
        wcont = None
        sB = B[33]
        for i in range(11):
            for corner in range(4):
                qx, qy = corner_pos(B, i, corner)
                for wname, val in (('x=0', qx), ('y=0', qy),
                                   ('x=s', sB - qx), ('y=s', sB - qy)):
                    if (i, corner, wname) in wallset:
                        continue
                    lo = val.lo
                    if wcont is None or lo < wcont:
                        wcont = lo
                    if lo <= 0:
                        ok = False
        wex = Fraction(0)
        for k in self.cert['exact_rows_sanity']:
            wex = max(wex, eval_g(B, self.cons[k]).mag())
        if wex > Fraction(1, 10 ** 40):
            ok = False
        self.check('F feasibility of z-hat', ok,
                   'min noncontact sep = %.4f, min proj slack = %.4f, '
                   'min corner clearance = %.2e, exact-row sanity = %.1e'
                   % (float(wsep), float(wreal), float(wcont), float(wex)))

    def run(self):
        print('checking certificate (EXACT rational arithmetic): %s'
              % self.cert['description'])
        print('r_N = %s = %.3g, |S| = %d, |S2| = %d, %d certificates'
              % (self.cert['r_N'], float(self.rN), len(self.cert['S']),
                 len(self.cert['S2']), len(self.cert['certificates'])))
        self.check_centre()
        self.krawczyk('S', 'Y', self.rN, 'F on N (=> unique z-hat in N)')
        self.krawczyk('S', 'Y', self.r0, 'F on box(z0,r_0) (tight enclosure)')
        self.krawczyk('S2', 'Y2', self.rN,
                      'F~ on N (angle-equality system => z-hat exact structure)')
        self.check_validity()
        self.check_lambda()
        self.check_certs()
        self.check_feasibility()
        print('=> %s' % ('ALL CHECKS PASS' if not self.fails else
                         'FAILURES: %s' % self.fails))
        return 0 if not self.fails else 1


def main():
    argv = list(sys.argv[1:])
    corrupt = None
    if '--corrupt' in argv:
        i = argv.index('--corrupt')
        corrupt = argv[i + 1]
        del argv[i:i + 2]
    path = (argv[0] if argv
            else '../../A22-local-rigidity/results/krawczyk_cert.json')
    cert = json.load(open(path))
    if corrupt:
        print('*** CORRUPTION TEST: %s (this run MUST fail) ***' % corrupt)
        if corrupt == 'z0-big':      # centre off by 1e-3 > r_N
            f = frac(cert['z0'][20]) + Fraction(1, 1000)
            cert['z0'][20] = '%d/%d' % (f.numerator, f.denominator)
        elif corrupt == 'z0-small':  # centre off by 1e-8
            f = frac(cert['z0'][20]) + Fraction(1, 10 ** 8)
            cert['z0'][20] = '%d/%d' % (f.numerator, f.denominator)
        elif corrupt == 'mu':        # sign-flip one certificate weight
            c0 = cert['certificates'][10]
            f = -frac(c0['mu'][5]) - Fraction(1, 10)
            c0['mu'][5] = '%d/%d' % (f.numerator, f.denominator)
        elif corrupt == 'spec':      # tamper with one contact definition
            for c in cert['constraints']:
                if c['kind'] == 'edge':
                    c['edge'] = (c['edge'] + 1) % 4
                    break
        else:
            raise SystemExit('unknown corruption mode')
    rc = Checker(cert).run()
    if corrupt:
        print('corruption test %s: %s' % (corrupt,
              'OK (checker failed as required)' if rc else
              'PROBLEM: checker still passes!'))
        sys.exit(0 if rc else 2)
    sys.exit(rc)


if __name__ == '__main__':
    main()
