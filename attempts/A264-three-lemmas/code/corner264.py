"""A264 -- exact corner geometry of a ring corner (wall START square A, floor END square B) for all four
sense pairs, the two ADMISSIBLE separating-axis forms in closed form, and an exact SAT check.

Corner frame: corner at the origin, floor y = 0 (x = distance from the corner), wall x = 0 (y = distance).
Offsets as in A258 (normal_ring.md s.2): a = START offset of the wall row (its y-extent is [a, a + w]),
b = END offset of the floor row (its x-extent is [b, b + w]); w = cos + sin.  The identity a_w + b_w =
s - sec phi_w - cos phi_w - sin phi_w holds for both senses.  Vertices (derived by hand from A258's Q1 and
its mirror; three_lemmas.md s.3.1):
  A(+): (0,a+g) (g,a+w) (w,a+c) (c,a)         A(-): (0,a+c) (g,a) (w,a+g) (c,a+w)
  B(+): (b+c,0) (b,g) (b+g,w) (b+w,c)         B(-): (b+g,0) (b+w,g) (b+c,w) (b,c)
Forms (E >= 0 <=> separation along that square's admissible edge normal):
  (+,+): EA = g_a*a + c_a*b - c_a^2 - g_a*g_b - max(0, sin(al-be));  EB = g_b*a + c_b*b - g_b^2 - c_b*c_a - max(0, sin(al-be))
  (+,-): EA = g_a*a + c_a*b - c_a^2 - g_a*c_b;                       EB = c_b*a + g_b*b - c_b^2 - g_b*c_a
  (-,+): EA = c_a*a + g_a*b - c_a*w_b - g_a^2 + g_a*g_b;             EB = g_b*a + c_b*b - c_b*w_a - g_b^2 + g_b*g_a
  (-,-): the (+,+) corner reflected in the diagonal:  EA(-,-)(a,al;b,be) = EB(+,+)(b,be;a,al), EB likewise.
These equal A261's `point_form` (cert261.py) algebraically; `check_forms` tests them against exact SAT.
"""
import math
import random


def vertsA(a, al, sg):
    c, g = math.cos(al), math.sin(al)
    w = c + g
    if sg > 0:
        return [(0.0, a + g), (g, a + w), (w, a + c), (c, a)]
    return [(0.0, a + c), (g, a), (w, a + g), (c, a + w)]


def vertsB(b, be, sg):
    c, g = math.cos(be), math.sin(be)
    w = c + g
    if sg > 0:
        return [(b + c, 0.0), (b, g), (b + g, w), (b + w, c)]
    return [(b + g, 0.0), (b + w, g), (b + c, w), (b, c)]


def sat_gap(P, Q):
    """largest separation over the 4 edge normals (>= 0 <=> interior-disjoint), exact for convex polygons."""
    best = -1e9
    for poly in (P, Q):
        n = len(poly)
        for i in range(n):
            x0, y0 = poly[i]
            x1, y1 = poly[(i + 1) % n]
            nx, ny = -(y1 - y0), x1 - x0
            L = math.hypot(nx, ny)
            nx, ny = nx / L, ny / L
            pP = [nx * x + ny * y for x, y in P]
            pQ = [nx * x + ny * y for x, y in Q]
            best = max(best, min(pQ) - max(pP), min(pP) - max(pQ))
    return best


def forms(sA, sB, a, al, b, be):
    """(EA, EB) of the corner with wall START square A (a, al, sense sA) and floor END square B (b, be, sB)."""
    ca, ga = math.cos(al), math.sin(al)
    cb, gb = math.cos(be), math.sin(be)
    wa, wb = ca + ga, cb + gb
    if sA > 0 and sB > 0:
        return (ga * a + ca * b - ca * ca - ga * gb - max(0.0, math.sin(al - be)),
                gb * a + cb * b - gb * gb - cb * ca - max(0.0, math.sin(al - be)))
    if sA > 0 and sB < 0:
        return (ga * a + ca * b - ca * ca - ga * cb, cb * a + gb * b - cb * cb - gb * ca)
    if sA < 0 and sB > 0:
        return (ca * a + ga * b - ca * wb - ga * ga + ga * gb, gb * a + cb * b - cb * wa - gb * gb + gb * ga)
    ea, eb = forms(1, 1, b, be, a, al)      # reflect in the diagonal: A <-> B, senses flip
    return eb, ea


def a261_form(which, sA, sB, al, be):
    """A261 cert261.point_form, verbatim: returns (ca, cb, c0) with form ca*a + cb*b + c0 >= 0."""
    wa, wb = math.cos(al) + math.sin(al), math.cos(be) + math.sin(be)
    own, sg = (al, sA) if which == 0 else (be, sB)
    c, g = math.cos(own), math.sin(own)
    ca, cb, P = (g, c, c - g) if sg > 0 else (c, g, g - c)
    arg = (al - be) if sA * sB > 0 else (al + be)
    return ca, cb, 0.5 * P * (wb - wa) - 0.5 * (1 + math.cos(arg) + abs(math.sin(arg)))


def check_forms(n=20000, tmax=0.05, seed=1):
    """[T-computed] (i) forms == A261's point_form; (ii) SAT-disjoint <=> EA >= 0 or EB >= 0 when a, b < 1."""
    rng = random.Random(seed)
    worst_alg, bad = 0.0, 0
    for _ in range(n):
        sA, sB = rng.choice((1, -1)), rng.choice((1, -1))
        al, be = rng.uniform(0, tmax), rng.uniform(0, tmax)
        a, b = rng.uniform(0, 1), rng.uniform(0, 1)
        if rng.random() < 0.5:                     # concentrate near the boundary, where the forms decide
            a, b = 1 - rng.uniform(0, 0.05), 1 - rng.uniform(0, 0.05)
        EA, EB = forms(sA, sB, a, al, b, be)
        for which, E in ((0, EA), (1, EB)):
            ca, cb, c0 = a261_form(which, sA, sB, al, be)
            worst_alg = max(worst_alg, abs(ca * a + cb * b + c0 - E))
        gap = sat_gap(vertsA(a, al, sA), vertsB(b, be, sB))
        ok = (gap >= -1e-12) == (max(EA, EB) >= -1e-12)
        if not ok and abs(gap) > 1e-9 and abs(max(EA, EB)) > 1e-9:
            bad += 1
    return dict(n=n, worst_alg=worst_alg, bad=bad)


if __name__ == '__main__':
    print(check_forms())
