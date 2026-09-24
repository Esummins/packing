"""A273 per-box sets (tree side).  b = [(lo, hi)] * 5 over (h_u, h_v, theta, X_low, phi).
  T_u vertices (C - h_u e_x): (s, h_v), (s + c, h_v + s), (c, h_v + s + c), (0, h_v + c)            [A271 s.0]
  Xi   (Q right of X; strip_jam.md s.2 P2) = {y >= X_low, y <= X_top, x >= 0, v >= 0, u <= 1}
  Xi'  (Q left of X, case A1-left)          = {y >= X_low, y <= X_top, u >= 0, v <= 1}
  Gam  (LEFT, s.2 P1)                        = {y >= h_v, y <= C_top, a >= 0, b <= 0}
with X's frame at B_X = (sin phi, X_low): u = cos(x - sin) + sin(y - X_low), v = -sin(x - sin) + cos(y - X_low);
C's frame: a = c(x - h_u - s) + s(y - h_v) (from B along the lower-left edge), b = -s(x - h_u) + c(y - L_h).
Each constraint is an interval-valued function g(z, box) (lower bound >= TOL at every core vertex).
PRUNE rules (5-parameter NECESSARY conditions of H1-H3; each cited in notes/disc273.md s.3)."""
import math

import geom273 as G

BIG = 6.0


def T_boxes(b):
    S, Cc, _, _ = G.trig(b)
    hv = b[1]
    return [(S, hv), (G.iadd(S, Cc), G.iadd(hv, S)), (Cc, G.iadd(G.iadd(hv, S), Cc)), ((0.0, 0.0), G.iadd(hv, Cc))]


def T_outer(b):
    pts = []
    for X, Y in T_boxes(b):
        pts += [(X[0], Y[0]), (X[1], Y[0]), (X[1], Y[1]), (X[0], Y[1])]
    return G.hull(pts)


def cons_xi(b, trig):
    _, _, SP, CP = trig
    xl = b[3]
    xtop = G.iadd(G.iadd(xl, SP), CP)

    def f(z):
        x, y = G.ival(z[0]), G.ival(z[1])
        dx, dy = G.isub(x, SP), G.isub(y, xl)
        u = G.iadd(G.imul(CP, dx), G.imul(SP, dy))
        v = G.isub(G.imul(CP, dy), G.imul(SP, dx))
        return [G.isub(y, xl), G.isub(xtop, y), x, v, G.isub((1.0, 1.0), u)]
    return f


def cons_xil(b, trig):
    _, _, SP, CP = trig
    xl = b[3]
    xtop = G.iadd(G.iadd(xl, SP), CP)

    def f(z):
        x, y = G.ival(z[0]), G.ival(z[1])
        dx, dy = G.isub(x, SP), G.isub(y, xl)
        u = G.iadd(G.imul(CP, dx), G.imul(SP, dy))
        v = G.isub(G.imul(CP, dy), G.imul(SP, dx))
        return [G.isub(y, xl), G.isub(xtop, y), u, G.isub((1.0, 1.0), v), G.isub((BIG, BIG), x)]
    return f


def cons_gam(b, trig):
    S, Cc, _, _ = trig
    hu, hv = b[0], b[1]
    ctop = G.iadd(G.iadd(hv, Cc), S)
    Lh = G.iadd(hv, Cc)

    def f(z):
        x, y = G.ival(z[0]), G.ival(z[1])
        a = G.iadd(G.imul(Cc, G.isub(G.isub(x, hu), S)), G.imul(S, G.isub(y, hv)))
        mb = G.isub(G.imul(S, G.isub(x, hu)), G.imul(Cc, G.isub(y, Lh)))
        return [G.isub(y, hv), G.isub(ctop, y), a, mb, G.isub((BIG, BIG), x)]
    return f


def nominal(kind, m):
    """the true set at the midpoint parameters m (5 floats), as a ccw polygon (Gam, Xi' truncated at x = BIG)."""
    hu, hv, th, xl, ph = m
    c, s, cp, sp = math.cos(th), math.sin(th), math.cos(ph), math.sin(ph)
    if kind == 'xi':
        return [(0.0, xl), (sp, xl), (sp + cp, xl + sp), (cp, xl + sp + cp), (0.0, xl + sp + cp)] if sp > 0 else \
            [(0.0, xl), (1.0, xl), (1.0, xl + 1.0), (0.0, xl + 1.0)]
    if kind == 'xil':
        pts = [(sp, xl), (BIG, xl), (BIG, xl + sp + cp), (cp, xl + sp + cp), (0.0, xl + cp)]
        return G.hull(pts)
    return G.hull([(hu + s, hv), (BIG, hv), (BIG, hv + c + s), (hu + c, hv + c + s), (hu, hv + c)])


def verified(f, z):
    return all(g[0] >= G.TOL for g in f(z))


def affine(f, npl, k):
    """coefficients (alpha, beta, gamma) of the k-th constraint at the midpoint parameters (degenerate intervals)."""
    g0, gx, gy = f((0.0, 0.0))[k][0], f((1.0, 0.0))[k][0], f((0.0, 1.0))[k][0]
    return gx - g0, gy - g0, g0


def core(kind, b):
    """a convex polygon inside the true set for EVERY parameter in b (see core_from)."""
    trig = G.trig(b)
    mk = {'xi': cons_xi, 'xil': cons_xil, 'gam': cons_gam}[kind]
    m = [0.5 * (lo + hi) for lo, hi in b]
    mb = [(v, v) for v in m]
    return core_from(mk(b, trig), mk(mb, G.trig(mb)), None)


def core_from(f, fm, _nominal):
    """Each defining constraint's nominal half-plane (midpoint parameters, fm) is moved inward by its own offset d_k,
    raised by the interval deficit (f over the whole box) at the failing vertices until every vertex passes
    (<= 16 rounds); convexity of the true set then gives core subset true set.  [] = no core (no kill from it)."""
    nk = len(fm((0.0, 0.0)))
    A = [affine(fm, None, k) for k in range(nk)]
    d = [0.0] * nk
    for _ in range(16):
        P = [(-1.0, -9.0), (BIG + 1.0, -9.0), (BIG + 1.0, 9.0), (-1.0, 9.0)]
        for k in range(nk):
            a, bb, c = A[k]
            P = G.clip(P, a, bb, c - d[k])
            if len(P) < 3:
                return []
        P = G.hull(P)
        worst = [0.0] * nk
        for z in P:
            for k, g in enumerate(f(z)):
                worst[k] = max(worst[k], G.TOL - g[0])
        if max(worst) <= 0.0:
            return P
        for k in range(nk):
            if worst[k] > 0.0:
                d[k] += 1.05 * worst[k] + 1e-12
    return []


def prune(b):
    """a rule name if the box misses the H1-H3 set (5-parameter necessary conditions), else None."""
    S, Cc, SP, CP = G.trig(b)
    hu, hv, xl = b[0], b[1], b[3]
    if hu[0] >= 1.0 or hv[0] >= 1.0:
        return 'box_hu_hv'                                            # H3: C meets the open box => h_u, h_v < 1
    g = G.isub(G.isub(G.iadd(Cc, S), G.imul(S, Cc)), G.iadd(G.imul(hu, Cc), G.imul(hv, S)))
    if g[1] <= 0.0:
        return 'open_box'                                             # A266 open_box_tilted: h_u c + h_v s < c + s - sc
    xtop = G.iadd(G.iadd(xl, SP), CP)
    if xtop[1] <= 2.82 or xtop[0] > SHAT_HI:
        return 'X_top'                                                # F1: side - 1 < X_top <= side, side in [3.82, s^]
    if xl[0] >= G.iadd(G.iadd(hv, Cc), S)[1]:
        return 'X_low_lt_Ctop'                                        # F1/H2: X meets int T_u, T_u below C_top
    low = G.isub(G.iadd(hv, Cc), G.iadd((R2LO, R2HI), G.idiv_pos(G.isub((1.0, 1.0), S), Cc)))
    if low[1] < 0.0:
        return 'LOW'                                                  # Lemma LOW: L_h >= 1/sqrt2 + (1 - s)/c
    return None


SHAT_HI = G.SHAT + 1e-12
R2LO, R2HI = G.R2 - 1e-15, G.R2 + 1e-15
