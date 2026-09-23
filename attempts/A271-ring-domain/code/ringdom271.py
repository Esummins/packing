"""A271: the JAM-corner hypotheses H1-H3 as HARD constraints and the STRIP_2-IN-RING domain conditions (D1)-(D2),
(U1)-(U9) of strip_enclosure.md s.3 as signed margins, from the poses alone (no ring needed).
Corner frame BL: wall x = 0, floor y = 0.  q = (h_u, h_v, th, X_low, phi, a_x, alpha, side):
  C  floater, lowest vertex (h_u + sin th, h_v), tilt th in [0, 45 deg]
  X  wall toucher, leftmost vertex (0, X_low + cos phi), tilt phi in [0, 45 deg]
  A  floor toucher, lowest vertex (a_x, 0), tilt alpha in [0, 90 deg)
  side in [3.82, s-hat]
H1: X meets the open TL box (X_top > side - 1), X in the container (X_top <= side), X misses the open BL box (X_low >= 1).
H2: int X meets int T_u (T_u = C - h_u e_x), X and C interior-disjoint.
H3: C meets the open BL box, floats (h_u, h_v > 0); A meets the open box, lies in the quadrant, A and C interior-disjoint.
geom259.poly_gap (imported, never edited) is the exact SAT check used for every gap / depth."""
import math
import os
import sys

import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A259-normal-room', 'code'))
import geom259 as Z                                                   # noqa: E402

SHAT = Z.SHAT
DEG = math.pi / 180.0
BOX = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], float)
NAMES = ['h_u', 'h_v', 'th', 'X_low', 'phi', 'a_x', 'alpha', 'side']
COND = ['D1', 'D2', 'U1', 'U2', 'U3', 'U4', 'U5', 'U6', 'U8', 'U9']


def sq_low(px, py, t):
    """unit square with lowest vertex (px, py), tilt t in [0, 90 deg): vertices ccw from the lowest vertex."""
    c, s = math.cos(t), math.sin(t)
    return np.array([[px, py], [px + c, py + s], [px + c - s, py + s + c], [px - s, py + c]])


def squares(q):
    hu, hv, th, xlow, phi, ax, al, side = q
    C = sq_low(hu + math.sin(th), hv, th)
    X = sq_low(math.sin(phi), xlow, phi)
    A = sq_low(ax, 0.0, al)
    Tu = C - np.array([hu, 0.0])
    return C, X, A, Tu


def depth(P, Q):
    return -Z.poly_gap(P, Q)


def constraints(q):
    """all >= 0 <=> H1-H3 hold (open conditions strict up to the optimiser's eps)."""
    hu, hv, th, xlow, phi, ax, al, side = q
    C, X, A, Tu = squares(q)
    xtop = float(X[:, 1].max())
    return np.array([
        hu, hv, th, 45 * DEG - th, phi, 45 * DEG - phi, al, 90 * DEG - al - 1e-9, side - 3.82, SHAT - side,
        depth(C, BOX),                       # H3: C meets the open box
        float(A[:, 0].min()), depth(A, BOX), Z.poly_gap(A, C),     # H3: A in the quadrant, meets the box, misses C
        xtop - (side - 1.0), side - xtop, xlow - 1.0,                # H1
        depth(X, Tu), Z.poly_gap(X, C), Z.poly_gap(X, A)])          # H2 (+ packing)


def conditions(q):
    """signed margins of (D1)-(D2), (U1)-(U9), exactly as hyp267 (A267) computes them on the rings."""
    hu, hv, th, xlow, phi, ax, al, side = q
    c, s = math.cos(th), math.sin(th)
    C, X, A, Tu = squares(q)
    Lh, Ctop, xtop = hv + c, hv + c + s, float(X[:, 1].max())
    g = hu + s - (1.0 - hv) * math.tan(th)
    L = np.array([hu, Lh])
    e, n = np.array([c, s]), np.array([-s, c])
    ab = lambda P: (float(e @ (P - L)), float(n @ (P - L)))          # noqa: E731
    (aB, bB), (aR, bR) = ab(X[0]), ab(X[1])
    beta = math.atan2(bR - bB, aR - aB)
    bX = lambda a: bB + (a - aB) * math.tan(beta)                    # noqa: E731
    a1, a2, astar = max(aB, 0.0), min(aR, 1.0), 1.0 - hu * c
    wmax = max(bX(a1), bX(a2))
    sig = max(-(p[0] - aB) * math.sin(beta) + (p[1] - bB) * math.cos(beta) for p in (ab(P) for P in Tu))
    sX, cphi, sphi = math.sin(phi), math.cos(phi), math.sin(phi)
    rX = lambda y: (sX + (y - xlow) / math.tan(phi) if phi > 1e-12 and y <= xlow + sphi else   # noqa: E731
                    (sX + cphi - (y - xlow - sphi) * math.tan(phi) if phi > 1e-12 else 1.0))
    lC = lambda y: hu + (y - Lh) / math.tan(th) if (y >= Lh and th > 1e-12) else hu + s - (y - hv) * math.tan(th)  # noqa
    y0 = max(xlow, Lh)
    U4 = 1.0 - max(lC(Ctop) - rX(Ctop), lC(y0) - rX(y0), lC(xlow) if xlow > Lh else hu)
    return dict(D1=min(1.0 - hv, Lh - 1.0, 1.0 - g), D2=min(xlow - hv, depth(X, Tu), Z.poly_gap(X, C)),
                U1=astar - a1, U2=min(bX(a1), bX(a2)), U3=a2 - astar - wmax / 2, U4=U4,
                U5=aR - max(0.0, math.sin(beta)) - astar, U6=1.0 - (hu + c - cphi),
                U8=xtop - Ctop - 0.5 ** 0.5, U9=1.0 - sig,
                Lh=Lh, g=g, a_B=aB, b_B=bB, a_R=aR, b_R=bR, beta_deg=beta / DEG, a_star=astar, w_max=wmax)


def from_ring(r):
    """q from an A262 ring row (geom262.verts imported through measure267's convention: 0 = A, 6 = X, 7 = C)."""
    sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A262-no-jam', 'code'))
    import geom262 as G                                                # noqa: E402
    V = G.verts(r['p'], r['s'])
    A, X, C = V[0], V[6], V[7]

    def low_tilt(P):
        lo = P[np.argmin(P[:, 1])]
        nxt = P[(np.argmin(P[:, 1]) + 1) % 4]
        t = math.atan2(nxt[1] - lo[1], nxt[0] - lo[0]) % (math.pi / 2)
        return lo, t
    (lc, tc), (lx, tx), (la, ta) = low_tilt(C), low_tilt(X), low_tilt(A)
    return np.array([float(C[:, 0].min()), float(lc[1]), tc, float(lx[1]), tx, float(la[0]), ta, r['s']])
