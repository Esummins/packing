"""A273 geometry kernel (tree side): float intervals over a parameter box, convex-polygon utilities, and the SOUND
per-box sets of the DROP LEMMA.  Box b = [(lo, hi)] * 5 over (h_u, h_v, theta, X_low, phi), angles in [0, pi/4].
Soundness conventions (notes/disc273.md s.2):
  * every derived bound is an interval evaluation widened by WID; every decision needs a margin >= EPS;
    float error in these small computations is <= 1e-13, so EPS = 1e-9 dominates it by 4 orders;
  * cores (Xi_c, Xi'_c, Gam_c) are convex polygons whose VERTICES are verified inside the true set for every b in
    the box (interval lower bound of every defining affine constraint >= TOL): convexity of the true set gives
    core subset true set;  T_uo = hull of the four T_u vertex boxes (inflated by EPS where used) contains T_u(b).
Polygons: lists of (x, y), counter-clockwise, convex."""
import math

EPS = 1e-9
TOL = 1e-12
WID = 1e-15
R2 = 0.5 ** 0.5
SHAT = 3.877083590022814


# ---------------------------------------------------------------- intervals
def ival(a, b=None):
    return (a, a) if b is None else (a, b)


def iadd(x, y):
    return (x[0] + y[0] - WID, x[1] + y[1] + WID)


def isub(x, y):
    return (x[0] - y[1] - WID, x[1] - y[0] + WID)


def imul(x, y):
    p = (x[0] * y[0], x[0] * y[1], x[1] * y[0], x[1] * y[1])
    return (min(p) - WID * (1 + abs(min(p))), max(p) + WID * (1 + abs(max(p))))


def idiv_pos(x, y):                                                   # y > 0
    p = (x[0] / y[0], x[0] / y[1], x[1] / y[0], x[1] / y[1])
    return (min(p) - WID * (1 + abs(min(p))), max(p) + WID * (1 + abs(max(p))))


def isin(t):                                                          # t within [0, pi/2]: sin increasing
    return (math.sin(t[0]) - WID, math.sin(t[1]) + WID)


def icos(t):
    return (math.cos(t[1]) - WID, math.cos(t[0]) + WID)


def trig(b):
    th, ph = b[2], b[4]
    return isin(th), icos(th), isin(ph), icos(ph)


# ---------------------------------------------------------------- convex polygons
def cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def hull(pts):
    P = sorted(set(pts))
    if len(P) <= 2:
        return P
    lo, up = [], []
    for p in P:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(P):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


def halfplanes(P):
    """unit-normal half-planes (a, b, c): a x + b y + c >= 0 inside the ccw convex polygon P."""
    H = []
    for i in range(len(P)):
        (x1, y1), (x2, y2) = P[i], P[(i + 1) % len(P)]
        a, b = -(y2 - y1), (x2 - x1)
        n = math.hypot(a, b)
        if n < 1e-15:
            continue
        a, b = a / n, b / n
        H.append((a, b, -(a * x1 + b * y1)))
    return H


def clip(P, a, b, c):
    """P intersect {a x + b y + c >= 0} (Sutherland-Hodgman, one plane)."""
    out = []
    n = len(P)
    for i in range(n):
        p, q = P[i], P[(i + 1) % n]
        fp, fq = a * p[0] + b * p[1] + c, a * q[0] + b * q[1] + c
        if fp >= 0:
            out.append(p)
        if (fp >= 0) != (fq >= 0):
            t = fp / (fp - fq)
            out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    return out


def erode(P, e):
    for a, b, c in halfplanes(P):
        P = clip(P, a, b, c - e)
        if len(P) < 3:
            return []
    return P


def inflate(P, e, big=50.0):
    Q = [(-big, -big), (big, -big), (big, big), (-big, big)]
    for a, b, c in halfplanes(P):
        Q = clip(Q, a, b, c + e)
    return Q


def seg_dist(z, p, q):
    dx, dy = q[0] - p[0], q[1] - p[1]
    L = dx * dx + dy * dy
    t = 0.0 if L == 0 else max(0.0, min(1.0, ((z[0] - p[0]) * dx + (z[1] - p[1]) * dy) / L))
    return math.hypot(p[0] + t * dx - z[0], p[1] + t * dy - z[1])


def dist(z, P):
    """distance from z to the closed convex polygon P (0 inside)."""
    if len(P) == 0:
        return math.inf
    if len(P) >= 3 and all(a * z[0] + b * z[1] + c >= 0 for a, b, c in halfplanes(P)):
        return 0.0
    return min(seg_dist(z, P[i], P[(i + 1) % len(P)]) for i in range(len(P)))


def diff_pieces(W, P):
    """convex pieces whose union contains W minus int P (closed pieces: conservative)."""
    out, rest = [], W
    for a, b, c in halfplanes(P):
        if len(rest) < 3:
            break
        piece = clip(rest, -a, -b, -c)
        if len(piece) >= 3:
            out.append(piece)
        rest = clip(rest, a, b, c)
    return out
