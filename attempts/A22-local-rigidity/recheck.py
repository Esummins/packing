#!/usr/bin/env python
"""Standalone re-checker for results/krawczyk_cert.json (A22-local-rigidity).

Verifies, using ONLY mpmath.iv validated interval arithmetic (+ fractions):

  [G] centre residual: |g_k(z0)| <= claims.centre_residual_max for all k in S
  [K] Krawczyk contraction on N = box(z0, r_N):  K(N) strictly inside N
      => F = (g_k)_{k in S} has EXACTLY ONE zero z-hat in N
  [K0] same on box(z0, r_0)  =>  ||z-hat - z0||_inf <= r_0
  [V] validity margins over N for every edge constraint in S:
      |tangential| <= 1/2 - tan_margin_min,  depth > -1/2
  [E] multiplier identity: || A_S^T lambda - e_s ||_inf <= lambda_residual_max
  [B] all 68 Farkas certificates: residual interval rho over N has
      ||rho||_1 <= beta_max < 1,  and mu >= 0, nu >= 0, nu <= nu_max
  [F] feasibility of z-hat (packing validity on box(z0, r_0)):
      noncontact pairs strictly separated (interval SAT); contact pairs:
      touching corner realises the strict minimum projection on the contact
      axis (so SAT gap = g_k(z-hat) = 0 exactly => interiors disjoint);
      containment: all non-wall-contact corners strictly inside.

Together (see notes.md for the four-line mathematical argument) these verify:
every valid 11-square packing configuration z with ||z - z0||_inf <= r_N has
container side s(z) >= s(z-hat), with equality if and only if z = z-hat.

Usage:  python recheck.py results/krawczyk_cert.json [--corrupt MODE]
        MODE in {z0-big, z0-small, mu, spec}  (each must make the check FAIL)
Exit code 0 = all PASS, 1 = FAIL.
"""
import json
import sys
from fractions import Fraction

from mpmath import iv

iv.dps = 65

HALF = [(Fraction(-1, 2), Fraction(-1, 2)), (Fraction(1, 2), Fraction(-1, 2)),
        (Fraction(1, 2), Fraction(1, 2)), (Fraction(-1, 2), Fraction(1, 2))]
NHAT = [(0, -1), (1, 0), (0, 1), (-1, 0)]
NV = 34


def frac(s):
    n, d = s.split('/')
    return Fraction(int(n), int(d))


def cnum(x):
    if isinstance(x, Fraction):
        return iv.mpf(x.numerator) / iv.mpf(x.denominator)
    return iv.mpf(x)


def rot(th, vx, vy):
    c, s = iv.cos(th), iv.sin(th)
    return vx * c - vy * s, vx * s + vy * c


def drot(th, vx, vy):
    c, s = iv.cos(th), iv.sin(th)
    return -vx * s - vy * c, vx * c - vy * s


def corner_pos(z, i, corner):
    hx, hy = cnum(HALF[corner][0]), cnum(HALF[corner][1])
    rx, ry = rot(z[3 * i + 2], hx, hy)
    return z[3 * i] + rx, z[3 * i + 1] + ry


def eval_g(z, c):
    half = cnum(Fraction(1, 2))
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
        nx, ny = rot(z[3 * j + 2], iv.mpf(nhx), iv.mpf(nhy))
        return nx * (qx - z[3 * j]) + ny * (qy - z[3 * j + 1]) - half
    if c['kind'] == 'dist':
        i, j = c['i'], c['j']
        dx = z[3 * i] - z[3 * j]
        dy = z[3 * i + 1] - z[3 * j + 1]
        return dx * dx + dy * dy - iv.mpf(1)
    raise ValueError(c['kind'])


def grad_g(z, c):
    g = {}
    if c['kind'] == 'angeq':
        g[3 * c['i'] + 2] = iv.mpf(1)
        g[3 * c['j'] + 2] = iv.mpf(-1)
        return g
    if c['kind'] == 'wall':
        i = c['i']
        hx, hy = cnum(HALF[c['corner']][0]), cnum(HALF[c['corner']][1])
        dx, dy = drot(z[3 * i + 2], hx, hy)
        w = c['wall']
        if w == 'x=0':
            g[3 * i] = iv.mpf(1); g[3 * i + 2] = dx
        elif w == 'y=0':
            g[3 * i + 1] = iv.mpf(1); g[3 * i + 2] = dy
        elif w == 'x=s':
            g[3 * i] = iv.mpf(-1); g[3 * i + 2] = -dx; g[33] = iv.mpf(1)
        elif w == 'y=s':
            g[3 * i + 1] = iv.mpf(-1); g[3 * i + 2] = -dy; g[33] = iv.mpf(1)
        return g
    if c['kind'] == 'edge':
        i, j = c['i'], c['j']
        hx, hy = cnum(HALF[c['corner']][0]), cnum(HALF[c['corner']][1])
        nhx, nhy = NHAT[c['edge']]
        nx, ny = rot(z[3 * j + 2], iv.mpf(nhx), iv.mpf(nhy))
        qx, qy = corner_pos(z, i, c['corner'])
        wx, wy = qx - z[3 * j], qy - z[3 * j + 1]
        dhx, dhy = drot(z[3 * i + 2], hx, hy)
        dnx, dny = drot(z[3 * j + 2], iv.mpf(nhx), iv.mpf(nhy))
        g[3 * i] = nx; g[3 * i + 1] = ny
        g[3 * j] = -nx; g[3 * j + 1] = -ny
        g[3 * i + 2] = nx * dhx + ny * dhy
        g[3 * j + 2] = dnx * wx + dny * wy
        return g
    if c['kind'] == 'dist':
        i, j = c['i'], c['j']
        dx = z[3 * i] - z[3 * j]
        dy = z[3 * i + 1] - z[3 * j + 1]
        two = iv.mpf(2)
        g[3 * i] = two * dx; g[3 * i + 1] = two * dy
        g[3 * j] = -two * dx; g[3 * j + 1] = -two * dy
        return g
    raise ValueError(c['kind'])


def edge_aux(z, c):
    i, j = c['i'], c['j']
    qx, qy = corner_pos(z, i, c['corner'])
    nhx, nhy = NHAT[c['edge']]
    nx, ny = rot(z[3 * j + 2], iv.mpf(nhx), iv.mpf(nhy))
    wx, wy = qx - z[3 * j], qy - z[3 * j + 1]
    return nx * wx + ny * wy, -ny * wx + nx * wy


def box(z0, r):
    out = []
    for x in z0:
        a = cnum(x - r)
        b = cnum(x + r)
        out.append(iv.mpf([a.a, b.b]))
    return out


def iv_min(a, b):
    return iv.mpf([min(a.a, b.a), min(a.b, b.b)])


def iv_max(a, b):
    return iv.mpf([max(a.a, b.a), max(a.b, b.b)])


def pair_sep_lb(z, i, j):
    """Lower bound of the SAT separation of squares i, j over interval config z."""
    ci = [corner_pos(z, i, c) for c in range(4)]
    cj = [corner_pos(z, j, c) for c in range(4)]
    best = None
    for sq in (i, j):
        th = z[3 * sq + 2]
        for nhx, nhy in ((1, 0), (0, 1)):
            nx, ny = rot(th, iv.mpf(nhx), iv.mpf(nhy))
            pi = [nx * qx + ny * qy for qx, qy in ci]
            pj = [nx * qx + ny * qy for qx, qy in cj]
            lo_i = hi_i = pi[0]
            lo_j = hi_j = pj[0]
            for p in pi[1:]:
                lo_i = iv_min(lo_i, p); hi_i = iv_max(hi_i, p)
            for p in pj[1:]:
                lo_j = iv_min(lo_j, p); hi_j = iv_max(hi_j, p)
            gap = iv_max(lo_j - hi_i, lo_i - hi_j)
            best = gap if best is None else iv_max(best, gap)
    return float(best.a)


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

    # ---- G: centre residuals (all 38 geometric constraints + 4 angle rows)
    def check_centre(self):
        zc = [cnum(x) for x in self.z0]
        mx = 0.0
        for c in self.cons:
            g = eval_g(zc, c)
            mx = max(mx, max(abs(float(g.a)), abs(float(g.b))))
        self.check('G centre residual', mx <= self.cert['claims']['centre_residual_max'],
                   'max |g_k(z0)| <= %.2e over all %d rows' % (mx, len(self.cons)))

    # ---- K: Krawczyk for the square system rows=Sname with preconditioner Yname
    def krawczyk(self, Sname, Yname, r, tag):
        S = self.cert[Sname]
        Y = [[frac(v) for v in row] for row in self.cert[Yname]]
        B = box(self.z0, r)
        zc = [cnum(x) for x in self.z0]
        Fc = [eval_g(zc, self.cons[k]) for k in S]
        Jrows = [grad_g(B, self.cons[k]) for k in S]
        Yiv = [[cnum(v) for v in row] for row in Y]
        rad = cnum(r)
        dbox = iv.mpf([(-rad).a, rad.b])
        ok = True
        worst = 0.0
        for i in range(NV):
            acc = iv.mpf(0)
            for rr in range(NV):
                acc += Yiv[i][rr] * Fc[rr]
            Ki = -acc
            for j in range(NV):
                m = iv.mpf(1) if i == j else iv.mpf(0)
                ssum = iv.mpf(0)
                for rr in range(NV):
                    v = Jrows[rr].get(j)
                    if v is not None:
                        ssum += Yiv[i][rr] * v
                Ki += (m - ssum) * dbox
            worst = max(worst, max(abs(float(Ki.a)), abs(float(Ki.b))) / float(r))
            if not (Ki.a > (-rad).a and Ki.b < rad.b):
                ok = False
        self.check('K Krawczyk %s' % tag, ok, 'max|K|/r = %.4g' % worst)
        return ok

    # ---- V: validity margins over N (edge rows used by the certificates)
    def check_validity(self):
        B = box(self.z0, self.rN)
        tmin = self.cert['claims']['tan_margin_min']
        ok = True
        worst = 1.0
        for k in self.cert['S']:
            c = self.cons[k]
            if c['kind'] != 'edge':
                continue
            dep, tan = edge_aux(B, c)
            m = 0.5 - max(abs(float(tan.a)), abs(float(tan.b)))
            worst = min(worst, m)
            if not (m >= tmin and dep.a > -0.5):
                ok = False
        self.check('V edge validity margins', ok, 'min tangential margin = %.5f' % worst)

    # ---- E: multiplier identity
    def check_lambda(self):
        zc = [cnum(x) for x in self.z0]
        lam = [frac(x) for x in self.cert['lambda']]
        acc = [iv.mpf(0)] * NV
        for lam_k, k in zip(lam, self.cert['S']):
            lk = cnum(lam_k)
            for j, v in grad_g(zc, self.cons[k]).items():
                acc[j] = acc[j] + lk * v
        mx = 0.0
        allpos = all(l > 0 for l in lam)
        for j in range(NV):
            t = acc[j] - (iv.mpf(1) if j == 33 else iv.mpf(0))
            mx = max(mx, max(abs(float(t.a)), abs(float(t.b))))
        okr = mx <= self.cert['claims']['lambda_residual_max']
        self.check('E multiplier identity', okr and allpos,
                   '||A^T lam - e_s||_inf <= %.2e, all lam > 0: %s' % (mx, allpos))

    # ---- B: Farkas certificate residuals over N
    def check_certs(self):
        B = box(self.z0, self.rN)
        Grows = [grad_g(B, self.cons[k]) for k in self.cert['S']]
        bmax = 0.0
        numax = 0.0
        ok = True
        seen = set()
        for cert in self.cert['certificates']:
            i, sg = cert['i'], cert['sigma']
            seen.add((i, sg))
            nu = frac(cert['nu'])
            mu = [frac(x) for x in cert['mu']]
            if nu < 0 or any(m < 0 for m in mu):
                ok = False
            numax = max(numax, float(nu))
            acc = {}
            for m, row in zip(mu, Grows):
                if m == 0:
                    continue
                mi = cnum(m)
                for j, v in row.items():
                    acc[j] = acc.get(j, iv.mpf(0)) + mi * v
            l1 = 0.0
            for j in range(NV):
                rho = (cnum(Fraction(sg if j == i else 0) +
                            (nu if j == 33 else 0)) - acc.get(j, iv.mpf(0)))
                l1 += max(abs(float(rho.a)), abs(float(rho.b)))
            bmax = max(bmax, l1)
        complete = len(seen) == 2 * NV
        okb = bmax <= self.cert['claims']['beta_max'] and bmax < 1.0
        oknu = numax <= self.cert['claims']['nu_max']
        self.check('B Farkas certificates', ok and okb and oknu and complete,
                   'beta = %.4f (need < 1), nu_max = %.2f, all 68 present = %s'
                   % (bmax, numax, complete))

    # ---- F: feasibility of z-hat on box(z0, r0)
    # Flush pairs and the wall contacts dropped from S/S2 are EXACT at z-hat
    # by the S2 pinning arguments (notes.md sec. "feasibility"); here we
    # machine-check everything else + tiny-enclosure sanity for the exact rows.
    def check_feasibility(self):
        B = box(self.z0, self.r0)
        ok = True
        # noncontact pairs strictly separated
        wsep = None
        for i, j in self.cert['noncontact_pairs']:
            lb = pair_sep_lb(B, i, j)
            if wsep is None or lb < wsep:
                wsep = lb
            if lb <= 0:
                ok = False
        # non-flush contact pairs: touching corner realises the strict min
        # projection on the contact axis among its square's corners
        wreal = None
        for ent in self.cert['contact_edge_pairs']:
            c = self.cons[ent['con']]
            i, j = c['i'], c['j']
            nhx, nhy = NHAT[c['edge']]
            nx, ny = rot(B[3 * j + 2], iv.mpf(nhx), iv.mpf(nhy))
            projs = []
            for corner in range(4):
                qx, qy = corner_pos(B, i, corner)
                projs.append(nx * qx + ny * qy)
            pc = projs[c['corner']]
            for corner in range(4):
                if corner == c['corner']:
                    continue
                gap = float((projs[corner] - pc).a)
                if wreal is None or gap < wreal:
                    wreal = gap
                if gap <= 0:
                    ok = False
        # containment: every corner not involved in ANY wall contact clears
        # the walls strictly (wall-contact corners sit exactly on the wall)
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
                    lo = float(val.a)
                    if wcont is None or lo < wcont:
                        wcont = lo
                    if lo <= 0:
                        ok = False
        # sanity: rows that are exactly zero at z-hat by the S2 argument have
        # tiny enclosures on B (angle equalities + second flush rows)
        wex = 0.0
        for k in self.cert['exact_rows_sanity']:
            g = eval_g(B, self.cons[k])
            wex = max(wex, max(abs(float(g.a)), abs(float(g.b))))
        if wex > 1e-40:
            ok = False
        self.check('F feasibility of z-hat', ok,
                   'min noncontact sep = %.4f, min proj slack = %.4f, '
                   'min corner clearance = %.2e, exact-row sanity = %.1e'
                   % (wsep, wreal, wcont, wex))

    def run(self):
        print('checking certificate: %s' % self.cert['description'])
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
    path = sys.argv[1] if len(sys.argv) > 1 else 'results/krawczyk_cert.json'
    cert = json.load(open(path))
    corrupt = None
    if '--corrupt' in sys.argv:
        corrupt = sys.argv[sys.argv.index('--corrupt') + 1]
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
