"""A280 the missing H2 prune of A273's 4-parameter box (h_u, theta, D, phi) (tree side; float intervals of geom273).
A273's prune4 used the h_v window and 'X hits int C' but NOT the first half of H2: int X meets int T_u.  Two sound
box rules, each a NECESSARY condition of int X n int T_u != 0 evaluated with outward-rounded intervals:
  DLOW  (strip_jam.md s.2 (D-low), [T]): D >= (c - sin phi) tan(min(theta, phi)).  Box pruned when
        D_hi < (cos th_hi - sin ph_hi) * tan(min(th_lo, ph_lo)) - 1e-12.
  SEP   separating axis: for one of the 8 edge normals n of T_u'' / X'' (interval vectors over the box) every
        n.(x_i - t_j) (x_i X's vertices, t_j T_u's) has lower bound >= 0 (or all upper bounds <= 0): then for
        every parameter of the box a line separates X from T_u, so their interiors are disjoint.
  LOWF  Lemma LOW, full range of A's tilt (ring_domain.md (F4), [T]: cases (a), (b) L_h >= 1/sqrt2 + tan(45 - th/2);
        case (c) L_h > G(al, th) = cos al + c - s + (c + s - 1) tan al, al in [45, 90) -- minimised over al by
        interval pieces of 1 deg and the tail [89, 90) where cos al > 0), i.e. h_v >= LOWB(th) - c, against the
        h_v upper bounds of drop4273.prune4 (h_v < 1, X_top <= s^, the open box).
C_top frame (drop4273): T_u'' = (s, -c-s), (s+c, -c), (c, 0), (0, -s);  X'' = (sp, -D), (sp+cp, -D+sp),
(cp, -D+sp+cp), (0, -D+cp).  Both lists counter-clockwise."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
A273 = os.path.abspath(os.path.join(HERE, '..', '..', 'A273-disc-lemma', 'code'))
if A273 not in sys.path:
    sys.path.insert(0, A273)
import geom273 as G                                                   # noqa: E402
import drop4273 as D4                                                 # noqa: E402

Z = (0.0, 0.0)


def ineg(x):
    return (-x[1], -x[0])


def verts(b):
    S, Cc, SP, CP = D4.trig4(b)
    dd = b[2]
    T = [(S, ineg(G.iadd(Cc, S))), (G.iadd(S, Cc), ineg(Cc)), (Cc, Z), (Z, ineg(S))]
    md = ineg(dd)
    X = [(SP, md), (G.iadd(SP, CP), G.iadd(md, SP)), (CP, G.iadd(md, G.iadd(SP, CP))), (Z, G.iadd(md, CP))]
    return T, X


def dlow(b):
    th, ph, dd = b[1], b[3], b[2]
    a = math.cos(th[1]) - math.sin(ph[1]) - 4 * G.WID
    if a <= 0.0:
        return False
    lb = a * math.tan(min(th[0], ph[0])) * (1 - 1e-14) - 1e-15
    return dd[1] < lb - 1e-12


def sep(b):
    T, X = verts(b)
    for P in (T, X):
        for k in range(4):
            p, q = P[k], P[(k + 1) % 4]
            n = (G.isub(p[1], q[1]), G.isub(q[0], p[0]))            # left normal of edge p -> q (interval)
            lo, hi = math.inf, -math.inf
            for x in X:
                for t in T:
                    g = G.iadd(G.imul(n[0], G.isub(x[0], t[0])), G.imul(n[1], G.isub(x[1], t[1])))
                    lo, hi = min(lo, g[0]), max(hi, g[1])
            if lo >= 1e-12 or hi <= -1e-12:
                return True
    return False


def lowb(th):
    """a lower bound of L_h over theta in th (both LOW cases), outward-rounded."""
    t0, t1 = th
    ab = G.R2 * (1 - 1e-15) + math.tan(math.pi / 4 - t1 / 2) * (1 - 1e-14)
    k1 = math.cos(t1) - math.sin(t1) - 4 * G.WID
    k2 = max(0.0, math.cos(t0) + math.sin(t0) - 1 - 4 * G.WID)
    dg = math.pi / 180
    gc = k1 + k2 * math.tan(89 * dg) * (1 - 1e-14)                   # tail al in [89, 90): cos al > 0
    for i in range(45, 89):
        gc = min(gc, math.cos((i + 1) * dg) * (1 - 1e-14) - G.WID + k1 + k2 * math.tan(i * dg) * (1 - 1e-14))
    return min(ab, gc) - 1e-12


def lowf(b):
    S, Cc, SP, CP = D4.trig4(b)
    hu, dd = b[0], b[2]
    lo = lowb(b[1]) - Cc[1] - G.WID                                  # h_v >= L_h - c
    ws, wp = G.iadd(Cc, S), G.iadd(SP, CP)
    ups = [1.0, G.iadd(G.isub(G.isub((D4.SE.SHAT_HI, D4.SE.SHAT_HI), wp), ws), dd)[1]]
    ob = G.isub(G.isub(G.iadd(Cc, S), G.imul(S, Cc)), G.imul(hu, Cc))
    if S[0] > 1e-9:
        ups.append(G.idiv_pos(ob, S)[1] if ob[1] > 0 else -1.0)
    return lo > min(ups) + 1e-12


def prune280(b):
    """'DLOW' / 'SEP' (int X misses int T_u on the whole box: H2 fails) / 'LOWF' (no h_v), else None."""
    if dlow(b):
        return 'DLOW'
    if sep(b):
        return 'SEP'
    if lowf(b):
        return 'LOWF'
    return None
