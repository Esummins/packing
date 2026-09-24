"""A273 WITNESS: A272's DISC LEMMA (strip_jam.md s.5, distance form) is FALSE on H1-H3 -- exact rational check.
Rational rotations (tan(t/2) rational), X flat (phi = 0), every test in Fractions, no floating point in the verdict:
  H1-H3 (ringdom271's 20 terms, re-derived exactly: SAT on edge normals of the rational squares),
  the disc point q: q_y > L_h, q_x >= 1/2, dist(q, Xi) >= 1/2, dist(q, Gam) >= 1/2 (squared, exact),
  the strip point p: p in int T_u, p outside C, Xi, Gam (strict half-plane tests), |p - q|^2 < 1/2.
The float search (disc272b.best_q) only proposes q, p; the verdict is the Fraction check.
    python witness273.py -> results/witness273.json"""
import json
import os
import sys
from fractions import Fraction as F

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, '..', 'results')
SHAT_LO = F(3877083590022814, 10 ** 15) - F(1, 10 ** 15)             # a lower bound of s-hat (geom259.SHAT)


def rot(t):                                                           # exact (cos, sin) from tan(half-angle) = t
    return (1 - t * t) / (1 + t * t), 2 * t / (1 + t * t)


def sq_low(px, py, cs):
    c, s = cs
    return [(px, py), (px + c, py + s), (px + c - s, py + s + c), (px - s, py + c)]


def axes(P):
    return [(P[i][1] - P[(i + 1) % len(P)][1], P[(i + 1) % len(P)][0] - P[i][0]) for i in range(len(P))]


def proj(P, n):
    v = [n[0] * x + n[1] * y for x, y in P]
    return min(v), max(v)


def interiors_meet(P, Q):
    """convex polygons: interiors intersect <=> every edge-normal axis has a strictly positive overlap."""
    for n in axes(P) + axes(Q):
        a, b = proj(P, n)
        c, d = proj(Q, n)
        if min(b, d) - max(a, c) <= 0:
            return False
    return True


def inside_strict(P, z):                                              # P ccw convex
    return all((P[(i + 1) % len(P)][0] - P[i][0]) * (z[1] - P[i][1]) - (P[(i + 1) % len(P)][1] - P[i][1]) * (z[0] - P[i][0]) > 0
               for i in range(len(P)))


def inside_closed(P, z):
    return all((P[(i + 1) % len(P)][0] - P[i][0]) * (z[1] - P[i][1]) - (P[(i + 1) % len(P)][1] - P[i][1]) * (z[0] - P[i][0]) >= 0
               for i in range(len(P)))


def seg_d2(z, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = ((z[0] - a[0]) * dx + (z[1] - a[1]) * dy) / (dx * dx + dy * dy)
    t = min(max(t, F(0)), F(1))
    ex, ey = a[0] + t * dx - z[0], a[1] + t * dy - z[1]
    return ex * ex + ey * ey


def poly_d2(P, z):                                                    # squared distance from z to the convex polygon P
    if inside_closed(P, z):
        return F(0)
    return min(seg_d2(z, P[i], P[(i + 1) % len(P)]) for i in range(len(P)))


def build(hu, hv, tC, xl, ax, tA, side, BIG=F(100)):
    cs = rot(tC)
    c, s = cs
    C = sq_low(hu + s, hv, cs)
    X = sq_low(F(0), xl, (F(1), F(0)))                                 # phi = 0
    A = sq_low(ax, F(0), rot(tA))
    Tu = [(x - hu, y) for x, y in C]
    Lh, Ctop = hv + c, hv + c + s
    Xi = [(F(0), xl), X[1], X[2], (F(0), X[2][1])]                    # phi = 0: X[0] = (0, xl) is the corner itself
    Gam = [C[0], (BIG, hv), (BIG, Ctop), C[2], C[3]]
    return dict(C=C, X=X, A=A, Tu=Tu, Xi=Xi, Gam=Gam, Lh=Lh, Ctop=Ctop, c=c, s=s)


def h1h3(G, hu, hv, xl, side):
    BOX = [(F(0), F(0)), (F(1), F(0)), (F(1), F(1)), (F(0), F(1))]
    X, C, A, Tu = G['X'], G['C'], G['A'], G['Tu']
    xtop = max(y for _, y in X)
    t = dict(hu=hu > 0, hv=hv > 0, th=0 <= G['s'] <= G['c'], side=F(382, 100) <= side <= SHAT_LO,
             C_meets_box=interiors_meet(C, BOX), A_in_quadrant=min(x for x, _ in A) >= 0 and min(y for _, y in A) >= 0,
             A_meets_box=interiors_meet(A, BOX), A_C_disjoint=not interiors_meet(A, C),
             X_top_gt=xtop > side - 1, X_top_le=xtop <= side, X_low_ge1=xl >= 1,
             X_meets_Tu=interiors_meet(X, Tu), X_C_disjoint=not interiors_meet(X, C), X_A_disjoint=not interiors_meet(X, A))
    return t


def disc_violation(G, q, p):
    R2 = F(1, 2)
    t = dict(q_above_Lh=q[1] > G['Lh'], q_x_ge_half=q[0] >= F(1, 2),
             dist_q_Xi_ge_half=poly_d2(G['Xi'], q) >= F(1, 4), dist_q_Gam_ge_half=poly_d2(G['Gam'], q) >= F(1, 4),
             p_in_int_Tu=inside_strict(G['Tu'], p), p_not_in_C=not inside_closed(G['C'], p),
             p_not_in_Xi=not inside_closed(G['Xi'], p), p_not_in_Gam=not inside_closed(G['Gam'], p),
             pq_lt_r2=(p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 < R2)
    return t


def search(hu, hv, tC, xl, ax, tA, side):
    """float proposal of (q, p): disc272b's best centre, then the nearest point of P pulled 1e-4 inside P."""
    import math
    import numpy as np
    sys.path.insert(0, os.path.join(HERE, '..', '..', 'A272-strip-jam', 'code'))
    import disc272b as DB                                             # noqa: E402
    from shapely.geometry import Point
    from shapely.ops import nearest_points
    th, al = 2 * math.atan(float(tC)), 2 * math.atan(float(tA))
    qv = np.array([float(hu), float(hv), th, float(xl), 0.0, float(ax), al, float(side)])
    pt, t = DB.best_q(qv, 'all')
    Xi, Gam, P, Lh, Ctop, _ = DB.sets(qv, 'all')
    P = P.difference(Gam).buffer(-1e-4)
    pp = nearest_points(P, Point(pt))[0]
    return (pt[0], pt[1]), (pp.x, pp.y), t, float(DB.R.constraints(qv).min())


def main():
    hu, hv, tC, xl = F(17, 20), F(199, 200), F(7, 100), F(211, 100)   # theta = 2 atan(0.07) = 8.01 deg, X_low = 2.11
    ax, tA, side = F(11, 10), F(1, 18), F(387, 100)                   # A: lowest vertex (1.1, 0), alpha = 6.36 deg
    q_f, p_f, t_f, h_f = search(hu, hv, tC, xl, ax, tA, side)
    q = (F(round(q_f[0] * 10 ** 6), 10 ** 6), F(round(q_f[1] * 10 ** 6), 10 ** 6) + F(1, 10 ** 5))
    p = (F(round(p_f[0] * 10 ** 6), 10 ** 6), F(round(p_f[1] * 10 ** 6), 10 ** 6))
    G = build(hu, hv, tC, xl, ax, tA, side)
    H, D = h1h3(G, hu, hv, xl, side), disc_violation(G, q, p)
    ok = all(H.values()) and all(D.values())
    out = dict(verdict='DISC LEMMA FALSE (exact)' if ok else 'witness NOT confirmed',
               params=dict(h_u=str(hu), h_v=str(hv), tan_half_theta=str(tC), X_low=str(xl), phi='0', a_x=str(ax),
                           tan_half_alpha=str(tA), side=str(side)),
               q=[str(v) for v in q], p=[str(v) for v in p], q_float=[float(v) for v in q], p_float=[float(v) for v in p],
               float_t_disc=t_f, float_H1H3_min=h_f, H1H3=H, disc_terms=D,
               margins=dict(dist2_q_Xi=float(poly_d2(G['Xi'], q)), dist2_q_Gam=float(poly_d2(G['Gam'], q)),
                            pq2=float((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2), L_h=float(G['Lh']), C_top=float(G['Ctop'])))
    json.dump(out, open(os.path.join(RES, 'witness273.json'), 'w'), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
