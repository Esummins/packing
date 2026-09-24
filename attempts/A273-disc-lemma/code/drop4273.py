"""A273 the DROP test in 4 parameters.  The drop lemma is invariant under the vertical translation by h_v (T_u, C,
Gam, Xi and L_h all move with h_v once X is placed by its DIP D := C_top - X_low; only the wall x = 0 and q_x >= 1/2
are used, both vertical), so it is stated in the C_TOP FRAME y'' = y - C_top over the box (h_u, theta, D, phi):
  T_u'' vertices (s, -c-s), (s+c, -c), (c, 0), (0, -s);  L_h'' = -s;  X_low'' = -D, X_top'' = -D + sin phi + cos phi;
  Gam'' = {y'' >= -(c+s), y'' <= 0, c(x - h_u - s) + s(y'' + c + s) >= 0, -s(x - h_u) + c(y'' + s) <= 0}.
h_v enters ONLY through PRUNE: the box is pruned when no h_v in (0, 1) satisfies the H1-H3 necessary conditions for
any parameter of the box (lower bounds: X_top > 2.82, h_v > 0 -- Lemma LOW deliberately NOT used; upper: h_v < 1, open box, X_top <= s^), or when X and C
share an interior point for every parameter of the box (H2).
Cells, rules and soundness as drop273 (whose cell_dead is reused unchanged)."""
import math

import geom273 as G
import sets273 as SE
import drop273 as D3

DMAX = 1.01


def trig4(b):
    return G.isin(b[1]), G.icos(b[1]), G.isin(b[3]), G.icos(b[3])


def cons_xi4(b, trig):
    _, _, SP, CP = trig
    xl = (-b[2][1], -b[2][0])
    return SE.cons_xi([None, None, None, xl, None], trig)


def cons_xil4(b, trig):
    xl = (-b[2][1], -b[2][0])
    return SE.cons_xil([None, None, None, xl, None], trig)


def cons_gam4(b, trig):
    S, Cc, _, _ = trig
    hu = b[0]
    ws = G.iadd(Cc, S)

    def f(z):
        x, y = G.ival(z[0]), G.ival(z[1])
        a = G.iadd(G.imul(Cc, G.isub(G.isub(x, hu), S)), G.imul(S, G.iadd(y, ws)))
        mb = G.isub(G.imul(S, G.isub(x, hu)), G.imul(Cc, G.iadd(y, S)))
        return [G.iadd(y, ws), G.isub((0.0, 0.0), y), a, mb, G.isub((SE.BIG, SE.BIG), x)]
    return f


def nominal4(kind, m):
    hu, th, dd, ph = m
    c, s = math.cos(th), math.sin(th)
    if kind == 'gam':
        return G.hull([(hu + s, -c - s), (SE.BIG, -c - s), (SE.BIG, 0.0), (hu + c, 0.0), (hu, -s)])
    return SE.nominal(kind, [hu, 0.0, th, -dd, ph])


def core4(kind, b):
    trig = trig4(b)
    mk = {'xi': cons_xi4, 'xil': cons_xil4, 'gam': cons_gam4}[kind]
    f = mk(b, trig)
    m = [0.5 * (lo + hi) for lo, hi in b]
    mb = [(v, v) for v in m]
    fm = mk(mb, trig4(mb))
    return SE.core_from(f, fm, lambda: nominal4(kind, m))


def T_outer4(b):
    S, Cc, _, _ = trig4(b)
    nws = G.isub((0.0, 0.0), G.iadd(Cc, S))
    boxes = [(S, nws), (G.iadd(S, Cc), G.isub((0.0, 0.0), Cc)), (Cc, (0.0, 0.0)), ((0.0, 0.0), G.isub((0.0, 0.0), S))]
    pts = []
    for X, Y in boxes:
        pts += [(X[0], Y[0]), (X[1], Y[0]), (X[1], Y[1]), (X[0], Y[1])]
    return G.hull(pts)


def prune4(b):
    S, Cc, SP, CP = trig4(b)
    hu, dd = b[0], b[2]
    if hu[0] >= 1.0:
        return 'box_hu'
    ws, wp = G.iadd(Cc, S), G.iadd(SP, CP)
    lows = [('X_top_gt', G.iadd(G.isub(G.isub((2.82, 2.82), wp), ws), dd)), ('hv_pos', (0.0, 0.0))]   # Lemma LOW NOT used
    ups = [('hv_lt1', (1.0, 1.0)), ('X_top_le', G.iadd(G.isub(G.isub((SE.SHAT_HI, SE.SHAT_HI), wp), ws), dd))]
    ob = G.isub(G.isub(G.iadd(Cc, S), G.imul(S, Cc)), G.imul(hu, Cc))
    if ob[1] <= 0.0:
        return 'open_box'
    if S[0] > 1e-9:
        ups.append(('open_box', G.idiv_pos(ob, S)))
    for nl, lo in lows:
        for nu, up in ups:
            if lo[0] > up[1] + 1e-12:
                return '%s>%s' % (nl, nu)
    if x_hits_c(b, (S, Cc, SP, CP)):
        return 'X_hits_C'
    return None


def x_hits_c(b, trig):
    """H2 (int X misses int C) fails on the whole box: a point z (the centroid of X n C at the midpoint) is strictly
    inside X and C for every parameter of b (interval lower bounds of the eight frame coordinates > TOL)."""
    S, Cc, SP, CP = trig
    m = [0.5 * (lo + hi) for lo, hi in b]
    hu, th, dd, ph = m
    c, s, cp, sp = math.cos(th), math.sin(th), math.cos(ph), math.sin(ph)
    C = [(hu + s, -c - s), (hu + s + c, -c), (hu + c, 0.0), (hu, -s)]
    X = [(sp, -dd), (sp + cp, -dd + sp), (cp, -dd + sp + cp), (0.0, -dd + cp)]
    P = X
    for a, bb, cc in G.halfplanes(C):
        P = G.clip(P, a, bb, cc)
        if len(P) < 3:
            return False
    z = (sum(p[0] for p in P) / len(P), sum(p[1] for p in P) / len(P))
    x, y = G.ival(z[0]), G.ival(z[1])
    hu_i, dd_i = b[0], b[2]
    dx, dy = G.isub(x, SP), G.iadd(y, dd_i)
    u = G.iadd(G.imul(CP, dx), G.imul(SP, dy))
    v = G.isub(G.imul(CP, dy), G.imul(SP, dx))
    ex, ey = G.isub(G.isub(x, hu_i), S), G.iadd(G.iadd(y, Cc), S)
    a = G.iadd(G.imul(Cc, ex), G.imul(S, ey))
    n = G.isub(G.imul(Cc, ey), G.imul(S, ex))
    one = (1.0, 1.0)
    return all(t[0] > G.TOL for t in (u, G.isub(one, u), v, G.isub(one, v), a, G.isub(one, a), n, G.isub(one, n)))


class BoxSets4:
    def __init__(self, b):
        S, Cc, _, _ = trig4(b)
        self.b = b
        self.Lmin = -S[1]
        self.xlmax = -b[2][0]
        self.Tuo = T_outer4(b)
        self.W = G.inflate(self.Tuo, G.EPS)
        self.xi, self.xil, self.gam = core4('xi', b), core4('xil', b), core4('gam', b)


def box_test4(b, **kw):
    rule = prune4(b)
    if rule:
        return 'PRUNE:' + rule, {}
    return D3.run_cells(BoxSets4(b), **kw)
