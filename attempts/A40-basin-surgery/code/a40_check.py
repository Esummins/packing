#!/usr/bin/env python
"""a40_check.py -- STANDALONE re-checker for results/certs_a40/ring_*/*.json.

Lab standard (a36_check.py pattern): uses ONLY mpmath.iv + fractions + json +
math + glob + os + sys.  No producer library: not a40_grow, not a36_lib, not
strata_lib, not t3lib, not numpy, not scipy.  The order-2 interval jets and
the row language are transcribed (with attribution) from A36's standalone
re-checker `attempts/A36-levers/code/a36_check.py` (itself from A35's
m2_check_inflation.py).

WHAT IS VERIFIED (notes/theory.md S1-S7), per certificate, [IV] dps 60:

 [O]  all multipliers >= 0 (rows and cuts), rationals parse.
 [F]  the face cut matches the certificate's face (coord, sign, value -h_in);
      tie cuts have +-1 coefficients on two theta coordinates and value -+tau.
 [ROW] every loaded row's validity claim re-verified over the claimed scope
      box (ring box(h_out), or the face sub-box):
        wall      constraint kind 'wall' (valid for any packing, [EX]);
        aux       verbatim equal to A22 constraint 36 or 37 (incircle lemma);
        V         sup|t| < 1/2 and inf d > -1/2 (S1);
        safe      axis inf gap >= 0 (S4a);
        forced    the 7 other axes of the pair killed (S4b);
        branch    row's axis == its pair's branch axis; every axis of the
                  pair not listed alive is re-killed (S3);
        floor     claimed lower bound lb <= inf_box g (S7); anchor value
                  g(z-hat) - lb used in V0.
 [M]  the margin chain recomputed from scratch:
        anchor:  -CV - V0 - eps_w h_out - Hbar h_out^2 > 0
        leaf-empty:  V0 + eps'_w h_out + Hbar h_out^2 < 0
        empty:   sup of the named wall row over the face sub-box < 0
      with V0 the signed interval value sum, eps_w the l1 gradient residual
      (vs e_s for anchors, vs 0 for leaf-empty), and Hbar the ACCUMULATED
      interval Hessian of the loaded rows over box(h_out), off-diagonals by
      magnitude, diagonals by positive part (theory.md S5).
 [COV] per (ring, face): the certificates form a covering split tree: at
      each level either a branched pair (children = its alive axes, with
      every non-alive axis re-killed) or a tie-cut split (both sides
      present, same functional and tau).
 [CHAIN] rings tile [h0=37/10000, h_reached]: h_in(k) = h_out(k-1); every
      face (i, sgn) != (s, +) is certified in every ring.

Corruption controls (each MUST make the checker fail):
    omega-sign   flip the sign of one loaded row multiplier
    h-big        grow h_out by 8x without re-deriving
    drop-anchor  zero the face-cut multiplier of an anchor certificate
    floor-raise  raise one floor row's claimed lower bound by 0.01
    drop-sibling delete one branched certificate (coverage must fail)

Usage:  python a40_check.py [certdir] [krawczyk_cert.json]
                            [--corrupt {omega-sign,h-big,drop-anchor,
                                        floor-raise,drop-sibling}]
Exit 0 = all PASS (or, under --corrupt, failed as required).
"""
import glob
import json
import math
import os
import sys
from fractions import Fraction

from mpmath import iv

iv.dps = 60

NV = 34
S_IDX = 33
H0 = Fraction(37, 10000)
HALF = [(Fraction(-1, 2), Fraction(-1, 2)), (Fraction(1, 2), Fraction(-1, 2)),
        (Fraction(1, 2), Fraction(1, 2)), (Fraction(-1, 2), Fraction(1, 2))]
NHAT = [(0, -1), (1, 0), (0, 1), (-1, 0)]


def frac(s):
    if isinstance(s, str) and '/' in s:
        n, d = s.split('/')
        return Fraction(int(n), int(d))
    return Fraction(s)


def cnum(x):
    if isinstance(x, Fraction):
        return iv.mpf(x.numerator) / iv.mpf(x.denominator)
    return iv.mpf(x)


def mag(x):
    x = iv.mpf(x)
    return max(math.nextafter(abs(float(x.a)), math.inf),
               math.nextafter(abs(float(x.b)), math.inf))


def sup(x):
    return math.nextafter(float(iv.mpf(x).b), math.inf)


def inf(x):
    return -math.nextafter(float((-iv.mpf(x)).b), math.inf)


# ---- order-2 forward jets (transcribed from a36_check.py / A35) ----------
class J(object):
    __slots__ = ('v', 'g', 'h', 'd', 'o')

    def __init__(self, v, g, h, d, o):
        self.v, self.g, self.h, self.d, self.o = v, g, h, d, o

    @staticmethod
    def var(val, k, d, o):
        g = None
        if o >= 1:
            g = [iv.mpf(0)] * d
            g[k] = iv.mpf(1)
        return J(val, g, [[iv.mpf(0)] * d for _ in range(d)] if o >= 2
                 else None, d, o)

    def __add__(self, b):
        if not isinstance(b, J):
            return J(self.v + b, self.g, self.h, self.d, self.o)
        d, o = self.d, self.o
        return J(self.v + b.v,
                 [self.g[i] + b.g[i] for i in range(d)] if o >= 1 else None,
                 [[self.h[i][j] + b.h[i][j] for j in range(d)]
                  for i in range(d)] if o >= 2 else None, d, o)

    def __sub__(self, b):
        if not isinstance(b, J):
            return J(self.v - b, self.g, self.h, self.d, self.o)
        d, o = self.d, self.o
        return J(self.v - b.v,
                 [self.g[i] - b.g[i] for i in range(d)] if o >= 1 else None,
                 [[self.h[i][j] - b.h[i][j] for j in range(d)]
                  for i in range(d)] if o >= 2 else None, d, o)

    def __mul__(self, b):
        d, o = self.d, self.o
        if not isinstance(b, J):
            return J(self.v * b,
                     [self.g[i] * b for i in range(d)] if o >= 1 else None,
                     [[self.h[i][j] * b for j in range(d)]
                      for i in range(d)] if o >= 2 else None, d, o)
        g = [self.g[i] * b.v + self.v * b.g[i]
             for i in range(d)] if o >= 1 else None
        h = None
        if o >= 2:
            h = [[self.h[i][j] * b.v + self.g[i] * b.g[j] + self.g[j] * b.g[i]
                  + self.v * b.h[i][j] for j in range(d)] for i in range(d)]
        return J(self.v * b.v, g, h, d, o)

    __rmul__ = __mul__

    def _ch(self, f, df, d2f):
        d, o = self.d, self.o
        g = [df * self.g[i] for i in range(d)] if o >= 1 else None
        h = None
        if o >= 2:
            h = [[df * self.h[i][j] + d2f * self.g[i] * self.g[j]
                  for j in range(d)] for i in range(d)]
        return J(f, g, h, d, o)

    def cos(self):
        c, s = iv.cos(self.v), iv.sin(self.v)
        return self._ch(c, -s, -c)

    def sin(self):
        c, s = iv.cos(self.v), iv.sin(self.v)
        return self._ch(s, c, -s)


def row_vars(c):
    if c['kind'] == 'wall':
        i = c['i']
        vs = [3 * i, 3 * i + 1, 3 * i + 2]
        if c['wall'] in ('x=s', 'y=s'):
            vs.append(33)
        return vs
    if c['kind'] == 'edge':
        i, j = c['i'], c['j']
        return [3 * i, 3 * i + 1, 3 * i + 2, 3 * j, 3 * j + 1, 3 * j + 2]
    if c['kind'] == 'dist':
        i, j = c['i'], c['j']
        return [3 * i, 3 * i + 1, 3 * j, 3 * j + 1]
    raise ValueError(c['kind'])


def row_jet(box, c, order):
    vs = row_vars(c)
    d = len(vs)
    V = [J.var(box[gi], k, d, order) for k, gi in enumerate(vs)]
    half = cnum(Fraction(1, 2))
    if c['kind'] == 'wall':
        cx, cy, th = V[0], V[1], V[2]
        hx, hy = cnum(HALF[c['corner']][0]), cnum(HALF[c['corner']][1])
        co, si = th.cos(), th.sin()
        qx = cx + (co * hx - si * hy)
        qy = cy + (si * hx + co * hy)
        w = c['wall']
        if w == 'x=0':
            return qx, vs
        if w == 'y=0':
            return qy, vs
        S = V[3]
        return ((S - qx) if w == 'x=s' else (S - qy)), vs
    if c['kind'] == 'edge':
        cix, ciy, thi, cjx, cjy, thj = V
        hx, hy = cnum(HALF[c['corner']][0]), cnum(HALF[c['corner']][1])
        ci, si = thi.cos(), thi.sin()
        qx = cix + (ci * hx - si * hy)
        qy = ciy + (si * hx + ci * hy)
        nhx, nhy = NHAT[c['edge']]
        cj, sj = thj.cos(), thj.sin()
        nx = cj * iv.mpf(nhx) - sj * iv.mpf(nhy)
        ny = sj * iv.mpf(nhx) + cj * iv.mpf(nhy)
        return (nx * (qx - cjx) + ny * (qy - cjy)) - half, vs
    if c['kind'] == 'dist':
        dx = V[0] - V[2]
        dy = V[1] - V[3]
        return (dx * dx + dy * dy) - iv.mpf(1), vs
    raise ValueError(c['kind'])


def td_of(box, o, e, p, k):
    """(t, d) of corner k of p in owner o's edge-e frame (S1's coords)."""
    hx, hy = cnum(HALF[k][0]), cnum(HALF[k][1])
    cp, sp = iv.cos(box[3 * p + 2]), iv.sin(box[3 * p + 2])
    qx = box[3 * p] + (cp * hx - sp * hy)
    qy = box[3 * p + 1] + (sp * hx + cp * hy)
    nhx, nhy = NHAT[e]
    co, so = iv.cos(box[3 * o + 2]), iv.sin(box[3 * o + 2])
    nx = co * iv.mpf(nhx) - so * iv.mpf(nhy)
    ny = so * iv.mpf(nhx) + co * iv.mpf(nhy)
    wx, wy = qx - box[3 * o], qy - box[3 * o + 1]
    return (-ny * wx + nx * wy), (nx * wx + ny * wy - iv.mpf(1) / 2)


def axis_killed(box, o, e, p):
    """True iff some corner row of the axis has sup < 0 on box (S3 kill)."""
    for k in range(4):
        _, d = td_of(box, o, e, p, k)
        if sup(d) < 0:
            return True
    return False


def pair_axes(i, j):
    return [(i, e, j) for e in range(4)] + [(j, e, i) for e in range(4)]


def box_of(z0, r):
    out = []
    for x in z0:
        a = cnum(x - r)
        b = cnum(x + r)
        out.append(iv.mpf([a.a, b.b]))
    return out


def face_box(z0, i, sgn, h_in, h_out):
    out = []
    for q in range(NV):
        lo, hi = z0[q] - h_out, z0[q] + h_out
        if q == i:
            if sgn > 0:
                lo = z0[q] + h_in
            else:
                hi = z0[q] - h_in
        out.append(iv.mpf([cnum(lo).a, cnum(hi).b]))
    return out


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


def axis_of_edge_con(c):
    return (c['j'], c['edge'], c['i'])


def pair_of_edge_con(c):
    return tuple(sorted((c['i'], c['j'])))


def check_cert(cert, z0, K, ck):
    name = os.path.basename(cert['_file'])
    h_in = frac(cert['h_in'])
    h_out = frac(cert['h_out'])
    fc = cert['face']
    i, sgn = fc['coord'], fc['sign']
    rbox = box_of(z0, h_out)
    fbox = face_box(z0, i, sgn, h_in, h_out)
    pbox = [cnum(x) for x in z0]

    def scope_box(scope):
        return rbox if scope == 'ring' else fbox

    if cert['type'] == 'A40-empty':
        c = cert['empty_row']['con']
        ck('%s wall kind' % name, c['kind'] == 'wall')
        v, _ = row_jet(fbox, c, 0)
        ck('%s empty sup<0' % name, sup(v.v) < 0, 'sup=%g' % sup(v.v))
        return

    is_anchor = cert['type'] == 'A40-anchor'
    scope = cert.get('facts_scope', 'ring')
    sbox = scope_box(scope if scope == 'ring' else 'face')

    # [O] multipliers, [F] cuts
    rows = cert['rows']
    oms = [frac(r['omega']) for r in rows]
    ck('%s omega>=0' % name, all(q >= 0 for q in oms))
    cuts = cert.get('cuts', [])
    ocs = [frac(c.get('omega', '0')) for c in cuts]
    ck('%s cut omega>=0' % name, all(q >= 0 for q in ocs))
    branch_ctx = {tuple(b['pair']): tuple(b['branch_axis'])
                  for b in cert.get('branched_pairs', [])}
    if is_anchor:
        fcuts = [c for c in cuts if c['label'].startswith('face:')]
        ck('%s one face cut' % name, len(fcuts) == 1)
        if fcuts:
            c = fcuts[0]
            ok = (c['coeffs'] == {str(i): sgn} and
                  frac(c['value']) == -h_in)
            ck('%s face cut spec' % name, ok)
    for c in cuts:
        if c['label'].startswith('face:'):
            continue
        cf = {int(k): v for k, v in c['coeffs'].items()}
        ok = (len(cf) == 2 and sorted(cf.values()) == [-1, 1] and
              all(k < 33 and k % 3 == 2 for k in cf))
        ck('%s tie cut coeffs %s' % (name, c['label']), ok)

    # [ROW] validity claims + collect jets at z-hat and over box
    V0 = iv.mpf(0)
    acc = {}
    accH = {}
    for r, q in zip(rows, oms):
        if q == 0:
            continue
        c = r['con']
        val = r['validity']
        mode = val['mode']
        rsbox = scope_box(val.get('scope', 'ring'))
        if mode == 'wall':
            ck('%s wall row kind' % name, c['kind'] == 'wall')
        elif mode == 'aux':
            ok = c['kind'] == 'dist' and \
                any(c['i'] == a and c['j'] == b for a, b in
                    ((0, 1), (1, 0), (0, 3), (3, 0)))
            ck('%s aux row is A22 aux' % name, ok)
        elif mode == 'V':
            t, d = td_of(rsbox, c['j'], c['edge'], c['i'], c['corner'])
            ck('%s V row %s' % (name, r['tag']),
               mag(t) < 0.5 and inf(d) > -0.5,
               '|t|=%g d_inf=%g' % (mag(t), inf(d)))
        elif mode == 'safe':
            o, e, p = axis_of_edge_con(c)
            glo = min(inf(td_of(rsbox, o, e, p, k)[1]) for k in range(4))
            ck('%s safe axis %s' % (name, r['tag']), glo >= 0,
               'gap_inf=%g' % glo)
        elif mode == 'forced':
            o, e, p = axis_of_edge_con(c)
            pr = pair_of_edge_con(c)
            others = [a for a in pair_axes(*pr) if a != (o, e, p)]
            ck('%s forced axis %s' % (name, r['tag']),
               all(axis_killed(rsbox, *a) for a in others))
        elif mode == 'branch':
            ax = axis_of_edge_con(c)
            pr = pair_of_edge_con(c)
            ck('%s branch row axis matches ctx %s' % (name, r['tag']),
               branch_ctx.get(pr) == ax,
               '%s vs %s' % (branch_ctx.get(pr), ax))
        elif mode == 'floor':
            lb = frac(val['lower_bound'])
            v, _ = row_jet(rbox, c, 0)
            ck('%s floor lb %s' % (name, r['tag']),
               Fraction(inf(v.v)) >= lb,
               'inf=%g lb=%g' % (inf(v.v), float(lb)))
        elif mode == 'relfloor':
            # S7': g_a - g_b = nhat_e . R(theta_p - theta_o) (h_ka - h_kb),
            # with the sibling g_b pointwise-[V]-valid on the face sub-box.
            rc = val['ref_con']
            ok = (rc['kind'] == 'edge' and c['kind'] == 'edge' and
                  rc['j'] == c['j'] and rc['edge'] == c['edge'] and
                  rc['i'] == c['i'] and rc['corner'] != c['corner'])
            ck('%s relfloor same axis %s' % (name, r['tag']), ok)
            t, d = td_of(fbox, rc['j'], rc['edge'], rc['i'], rc['corner'])
            ck('%s relfloor sibling V %s' % (name, r['tag']),
               mag(t) < 0.5 and inf(d) > -0.5)
            o, e, p = rc['j'], rc['edge'], rc['i']
            # delta interval from the ring box, refined by this cert's cuts
            dlo, dhi = -2 * h_out, 2 * h_out
            for ct2 in cuts:
                cf = {int(kq): vq for kq, vq in ct2['coeffs'].items()}
                if set(cf) != {3 * o + 2, 3 * p + 2}:
                    continue
                vv = frac(ct2['value'])
                if cf[3 * p + 2] == 1:
                    dlo = max(dlo, -vv)
                else:
                    dhi = min(dhi, vv)
            dstar = z0[3 * p + 2] - z0[3 * o + 2]
            dd = cnum(dstar) + iv.mpf([cnum(dlo).a, cnum(dhi).b])
            ux = HALF[c['corner']][0] - HALF[rc['corner']][0]
            uy = HALF[c['corner']][1] - HALF[rc['corner']][1]
            cd, sd = iv.cos(dd), iv.sin(dd)
            rx = cd * cnum(ux) - sd * cnum(uy)
            ry = sd * cnum(ux) + cd * cnum(uy)
            nhx, nhy = NHAT[e]
            f = iv.mpf(nhx) * rx + iv.mpf(nhy) * ry
            lb = frac(val['lower_bound'])
            ck('%s relfloor lb %s' % (name, r['tag']),
               Fraction(inf(f)) >= lb,
               'inf f=%g lb=%g' % (inf(f), float(lb)))
        else:
            ck('%s known mode' % name, False, mode)
        # numeric ledger
        qi = cnum(q)
        j0, vs = row_jet(pbox, c, 1)
        vz = j0.v
        if mode in ('floor', 'relfloor'):
            vz = vz - cnum(frac(val['lower_bound']))
        V0 = V0 + qi * vz
        for loc, gi in enumerate(vs):
            acc[gi] = acc.get(gi, iv.mpf(0)) + qi * j0.g[loc]
        j2, vs2 = row_jet(rbox, c, 2)
        for a in range(len(vs2)):
            for b in range(len(vs2)):
                key = (vs2[a], vs2[b])
                t = qi * j2.h[a][b]
                accH[key] = t if key not in accH else accH[key] + t

    # branched pairs: every axis not listed alive must be killed on scope
    for b in cert.get('branched_pairs', []):
        pr = tuple(b['pair'])
        alive = {tuple(a) for a in b['alive_axes']}
        ck('%s branch axis in alive %s' % (name, pr),
           tuple(b['branch_axis']) in alive)
        for a in pair_axes(*pr):
            if a not in alive:
                ck('%s killed axis %s %s' % (name, pr, a),
                   axis_killed(sbox, *a))

    # [M] margin chain
    CV = sum((q * frac(c['value']) for q, c in zip(ocs, cuts)), Fraction(0))
    for q, c in zip(ocs, cuts):
        if q == 0:
            continue
        for k, cf in c['coeffs'].items():
            gi = int(k)
            acc[gi] = acc.get(gi, iv.mpf(0)) + cnum(q * cf)
    if is_anchor:
        acc[S_IDX] = acc.get(S_IDX, iv.mpf(0)) - iv.mpf(1)
    eps_w = sum(Fraction(mag(v)) for v in acc.values())
    hsum = Fraction(0)
    for (a, b), v in accH.items():
        if a == b:
            hsum += Fraction(max(0.0, sup(v)))
        else:
            hsum += Fraction(mag(v))
    Hbar = hsum / 2
    if is_anchor:
        margin = (-CV - Fraction(sup(V0)) - eps_w * h_out
                  - Hbar * h_out * h_out)
        ck('%s margin>0' % name, margin > 0, 'margin=%g' % float(margin))
    else:
        ck('%s no cuts loaded' % name, all(q == 0 for q in ocs))
        umax = Fraction(sup(V0)) + eps_w * h_out + Hbar * h_out * h_out
        ck('%s leaf-empty sup<0' % name, umax < 0, 'sup=%g' % float(umax))


def leaf_key(cert):
    ctx = tuple(sorted((tuple(b['pair']), tuple(b['branch_axis']))
                       for b in cert.get('branched_pairs', [])))
    tcuts = tuple(sorted(
        (c['label'], c['value']) for c in cert.get('cuts', [])
        if not c['label'].startswith('face:')))
    return ctx, tcuts


def check_coverage(certs, z0, ck, ringface):
    """[COV] the certificates of one (ring, face) form a covering tree."""
    leaves = [leaf_key(c) for c in certs]

    def rec(idx, fixed_pairs, fixed_cuts, depth):
        if depth > 12:
            return False
        if len(idx) == 1:
            ctx, tcuts = leaves[idx[0]]
            return (len(ctx) == len(fixed_pairs) and
                    len(tcuts) == len(fixed_cuts))
        # try a pair split: a pair present in every leaf (beyond fixed)
        cands = None
        for q in idx:
            prs = {pr for pr, ax in leaves[q][0] if pr not in fixed_pairs}
            cands = prs if cands is None else (cands & prs)
        for pr in sorted(cands or ()):
            groups = {}
            for q in idx:
                ax = dict(leaves[q][0])[pr]
                groups.setdefault(ax, []).append(q)
            # alive set of pr per the certificates must equal group keys
            alive = None
            for q in idx:
                for b in certs[q].get('branched_pairs', []):
                    if tuple(b['pair']) == pr:
                        al = {tuple(a) for a in b['alive_axes']}
                        alive = al if alive is None else (alive | al)
            if alive is None or set(groups) != alive:
                continue
            if all(rec(g, fixed_pairs | {pr}, fixed_cuts, depth + 1)
                   for g in groups.values()):
                return True
        # try a tie-cut split: a functional whose two sides partition idx
        labels = {}
        for q in idx:
            for lab, v in leaves[q][1]:
                if (lab, v) in fixed_cuts:
                    continue
                base = lab.rsplit(':', 1)[0]
                labels.setdefault((base, abs(frac(v))), set()).add((lab, v))
        for (base, tau), sides in labels.items():
            if len(sides) != 2:
                continue
            g1, g2 = [], []
            s1, s2 = sorted(sides)
            for q in idx:
                l1 = dict(leaves[q][1])
                if s1[0] in l1 and l1[s1[0]] == s1[1]:
                    g1.append(q)
                elif s2[0] in l1 and l1[s2[0]] == s2[1]:
                    g2.append(q)
                else:
                    g1 = None
                    break
            if not g1 or not g2:
                continue
            if rec(g1, fixed_pairs, fixed_cuts | {s1}, depth + 1) and \
                    rec(g2, fixed_pairs, fixed_cuts | {s2}, depth + 1):
                return True
        return False

    ck('COV %s tree covers' % ringface,
       rec(list(range(len(certs))), set(), set(), 0),
       '%d leaves' % len(certs))


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    args = list(sys.argv[1:])
    corrupt = None
    if '--corrupt' in args:
        q = args.index('--corrupt')
        corrupt = args[q + 1]
        del args[q:q + 2]
    cdir = args[0] if args else os.path.join(here, '..', 'results',
                                             'certs_a40')
    kpath = (args[1] if len(args) > 1 else
             os.path.join(here, '..', '..', 'A22-local-rigidity', 'results',
                          'krawczyk_cert.json'))
    K = json.load(open(kpath))
    z0 = [frac(x) for x in K['z0']]
    rings = sorted(glob.glob(os.path.join(cdir, 'ring_*')))
    if not rings:
        print('no rings in %s' % cdir)
        return 1
    ck = Check()
    certs_by_rf = {}
    chain = []
    for rd in rings:
        files = sorted(glob.glob(os.path.join(rd, '*.json')))
        ring_h = set()
        for fn in files:
            cert = json.load(open(fn))
            cert['_file'] = fn
            rf = (os.path.basename(rd), cert['face']['label'])
            certs_by_rf.setdefault(rf, []).append(cert)
            ring_h.add((cert['h_in'], cert['h_out']))
        ck('CHAIN %s single (h_in,h_out)' % os.path.basename(rd),
           len(ring_h) == 1, str(ring_h))
        chain.append(sorted(ring_h)[0])

    # ---- corruption injection
    if corrupt:
        print('*** CORRUPTION TEST: %s (this run MUST fail) ***' % corrupt)
        tgt = None
        for rf, cs in sorted(certs_by_rf.items()):
            for c in cs:
                if c['type'] == 'A40-anchor':
                    tgt = c
                    break
            if tgt:
                break
        if corrupt == 'omega-sign':
            for r in tgt['rows']:
                if frac(r['omega']) > 0:
                    r['omega'] = '-' + r['omega']
                    break
        elif corrupt == 'h-big':
            h8 = frac(tgt['h_out']) * 8
            tgt['h_out'] = '%d/%d' % (h8.numerator, h8.denominator)
        elif corrupt == 'drop-anchor':
            for c in tgt['cuts']:
                if c['label'].startswith('face:'):
                    c['omega'] = '0'
        elif corrupt == 'floor-raise':
            done = False
            for rf, cs in sorted(certs_by_rf.items()):
                for cert in cs:
                    for r in cert.get('rows', []):
                        if r['validity'].get('mode') == 'floor':
                            lb = frac(r['validity']['lower_bound']) + \
                                Fraction(1, 100)
                            r['validity']['lower_bound'] = \
                                '%d/%d' % (lb.numerator, lb.denominator)
                            done = True
                            break
                    if done:
                        break
                if done:
                    break
            if not done:
                print('no floor rows found; corruption not applicable')
                return 1
        elif corrupt == 'drop-sibling':
            done = False
            for rf, cs in sorted(certs_by_rf.items()):
                if len(cs) > 1:
                    cs.pop()
                    done = True
                    break
            if not done:
                print('no branched faces found; corruption not applicable')
                return 1
        else:
            print('unknown corruption %s' % corrupt)
            return 1

    # ---- chain tiling
    ck('CHAIN starts at A36 h0', frac(chain[0][0]) == H0,
       chain[0][0])
    for a, b in zip(chain, chain[1:]):
        ck('CHAIN contiguous', frac(a[1]) == frac(b[0]),
           '%s -> %s' % (a[1], b[0]))
    # every face present in every ring
    want = {'sq%d.%s%s' % (q, ax, sg)
            for q in range(11) for ax in 'xyt' for sg in '+-'} | {'s-'}
    for rd in rings:
        have = {rf[1] for rf in certs_by_rf if rf[0] == os.path.basename(rd)}
        ck('CHAIN faces complete %s' % os.path.basename(rd),
           want <= have, str(sorted(want - have))[:200])

    # ---- per-cert numerics + per-face coverage
    nc = 0
    for rf, cs in sorted(certs_by_rf.items()):
        for cert in cs:
            check_cert(cert, z0, K, ck)
            nc += 1
        if len(cs) > 1 or cs[0].get('branched_pairs') or \
                any(not c['label'].startswith('face:')
                    for c in cs[0].get('cuts', [])):
            check_coverage(cs, z0, ck, '%s/%s' % rf)

    print('checked %d certificates, %d checks, %d failures'
          % (nc, ck.n, len(ck.fails)))
    if corrupt:
        ok = len(ck.fails) > 0
        print('corruption %s: checker %s => %s'
              % (corrupt, 'FAILED as required' if ok else
                 'passed (BAD)', 'PASS' if ok else 'FAIL'))
        return 0 if ok else 1
    return 0 if not ck.fails else 1


if __name__ == '__main__':
    sys.exit(main())
