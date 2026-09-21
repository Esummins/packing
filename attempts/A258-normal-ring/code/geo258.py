"""A258 geometry: rows of common-tilt wall touchers, the NORMAL RING (pinwheel of four rows), its domain D.

WALL FRAME (t, d): t along the wall from the wall's START corner (walking counter-clockwise round the
container: floor from BL, right wall from BR, ceiling from TR, left wall from TL), d the depth off the wall.
    wall 0 floor (t, d) -> (t, d);  1 right -> (s - d, t);  2 top -> (s - t, s - d);  3 left -> (d, s - t)
(rotations, so a square's SENSE = sign of its global tilt in (-45, 45] is the same in every wall frame).

A ROW on wall w: sense sg in {+1, -1}, tilt phi in (0, 45 deg), length l, start offset a (the row's
bounding interval along the wall is [a, a + (l-1) sec phi + w(phi)], w = cos + sin); end offset
    b = s - a - (l - 1) sec phi - w(phi).
Sense +, member k (k = 0 .. l-1), vertices in the wall frame (c = cos phi, g = sin phi, p = a + k sec phi):
    (p + g, 0) wall vertex, (p + w, g), (p + c, w), (p, c)          -- 'A-type' at the start, 'B-type' at the end
Sense -: the mirror image  (p + c, 0), (p + w, c), (p + g, w), (p, g).
CORNER k (0 BL, 1 BR, 2 TR, 3 TL) lies between the END of wall k-1 and the START of wall k.
"""
import math

import numpy as np

DEG = math.pi / 180.0
SHAT = 3.877083590022814


def wall_to_xy(w, s, P):
    P = np.asarray(P, float)
    t, d = P[:, 0], P[:, 1]
    if w == 0:
        return np.stack([t, d], 1)
    if w == 1:
        return np.stack([s - d, t], 1)
    if w == 2:
        return np.stack([s - t, s - d], 1)
    return np.stack([d, s - t], 1)


def member(phi, p, sg):
    c, g = math.cos(phi), math.sin(phi)
    w = c + g
    if sg > 0:
        return [(p + g, 0.0), (p + w, g), (p + c, w), (p, c)]
    return [(p + c, 0.0), (p + w, c), (p + g, w), (p, g)]


def row(w, s, a, phi, sg=1, l=2):
    sec = 1.0 / math.cos(phi)
    return [wall_to_xy(w, s, member(phi, a + k * sec, sg)) for k in range(l)]


def end_offset(s, a, phi, l=2):
    return s - a - (l - 1) / math.cos(phi) - math.cos(phi) - math.sin(phi)


def ring(s, a, phi, sg=(1, 1, 1, 1), l=(2, 2, 2, 2)):
    """the rows of the four walls, flattened; order: wall 0 members from the start, wall 1, ..."""
    out = []
    for w in range(4):
        out += row(w, s, a[w], phi[w], sg[w], l[w])
    return out


def sat_gap(A, B):
    """signed separation of two convex polygons (>= 0 iff interior-disjoint), by SAT on both edge sets."""
    best = -1e9
    for P in (A, B):
        e = np.roll(P, -1, 0) - P
        n = np.stack([e[:, 1], -e[:, 0]], 1)
        n = n / np.linalg.norm(n, axis=1, keepdims=True)
        pa, pb = A @ n.T, B @ n.T
        g = np.maximum(pa.min(0) - pb.max(0), pb.min(0) - pa.max(0))
        best = max(best, float(g.max()))
    return best


def rect(x0, x1, y0, y1):
    return np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1]], float)


def depth(Q, R):
    """overlap depth of polygon Q with polygon R (> 0 iff interiors meet)."""
    return -sat_gap(Q, R)


def contain_margin(Q, s):
    return float(min(Q[:, 0].min(), Q[:, 1].min(), s - Q[:, 0].max(), s - Q[:, 1].max()))


def cells(s):
    """the twelve border cells at m = 4, in the WALL frames: box k = corner k; ('L', w) = [1,2] from the start
    of wall w; ('R', w) = [s-2, s-1]."""
    out = {}
    for k in range(4):
        out[('C', k)] = wall_to_xy(k, s, [(0, 0), (1, 0), (1, 1), (0, 1)])
    for w in range(4):
        out[('L', w)] = wall_to_xy(w, s, [(1, 0), (2, 0), (2, 1), (1, 1)])
        out[('R', w)] = wall_to_xy(w, s, [(s - 2, 0), (s - 1, 0), (s - 1, 1), (s - 2, 1)])
    return out


def ribbon(s, w):
    return wall_to_xy(w, s, [(s - 2, 0), (2, 0), (2, 1), (s - 2, 1)])


def meet_table(sq, s, tol=1e-9):
    cl = cells(s)
    return {k: [i for i, Q in enumerate(sq) if depth(Q, R) > tol] for k, R in cl.items()}


def families(s):
    """every admissible family at m = 4, s < 4: any subset of the boxes + per wall none / L / R."""
    import itertools
    for kb in range(16):
        boxes = [('C', k) for k in range(4) if kb >> k & 1]
        for ch in itertools.product((None, 'L', 'R'), repeat=4):
            fam = boxes + [(c, w) for w, c in enumerate(ch) if c]
            if fam:
                yield fam


def hall_min(sq, s, tol=1e-9):
    """min over admissible families of |M(Pi)| - |Pi| (family-stuck iff >= 1), with a minimising family."""
    mt = meet_table(sq, s, tol)
    best = (99, None)
    for fam in families(s):
        M = set()
        for k in fam:
            M.update(mt[k])
        v = len(M) - len(fam)
        if v < best[0]:
            best = (v, fam)
    return best


def check_packing(sq, s):
    """(min containment margin, min pairwise gap)."""
    cm = min(contain_margin(Q, s) for Q in sq)
    pg = min(sat_gap(sq[i], sq[j]) for i in range(len(sq)) for j in range(i))
    return cm, pg


# ---------------------------------------------------------------- the domain D (sense +, rows of two)
def E_corner(a, alpha, b, beta):
    """closed form of the corner condition between the A-type (start of a wall: offset a, tilt alpha) and the
    B-type (end of the previous wall: offset b, tilt beta), both of sense +:  max(E_A, E_B) >= 0."""
    k = max(0.0, math.sin(alpha - beta))
    EA = a * math.sin(alpha) + b * math.cos(alpha) - math.cos(alpha) ** 2 - math.sin(alpha) * math.sin(beta) - k
    EB = a * math.sin(beta) + b * math.cos(beta) - math.sin(beta) ** 2 - math.cos(alpha) * math.cos(beta) - k
    return EA, EB


def D_terms(s, a, phi, slots=True):
    """the inequalities of D as margins (all >= 0 <=> in the closure of D; > 0 <=> in D)."""
    out = []
    b = [end_offset(s, a[w], phi[w]) for w in range(4)]
    for w in range(4):
        sec = 1.0 / math.cos(phi[w])
        out += [('phi>0', phi[w]), ('phi<45', math.pi / 4 - phi[w]), ('a<1', 1 - a[w]), ('b<1', 1 - b[w]),
                ('a>0', a[w]), ('b>0', b[w])]
        if slots:
            out += [('L met by Q2', 2 - a[w] - sec), ('R met by Q1', 2 - b[w] - sec)]
        EA, EB = E_corner(a[w], phi[w], b[(w - 1) % 4], phi[(w - 1) % 4])
        out.append(('corner', max(EA, EB)))
    return out


def in_D(s, a, phi, slots=True):
    return min(v for _, v in D_terms(s, a, phi, slots))


def tooth_terms(s, a, phi):
    """necessary condition for a RIBBON POKER on a wall: the tooth between Q1 and Q2 (apex = Q2's vertex
    (a + sec, cos), below depth 1) meets the ribbon (s-2, 2)."""
    c, g = math.cos(phi), math.sin(phi)
    th = math.tan(phi / 2)
    return (a + 1 / c + c * th) - (s - 2), 2 - (a + 1 / c - g * th)


def tight_ring(s, phi):
    """the C4 TIGHT normal ring at common tilt: a sin + b cos = 1, a + b = K."""
    c, g = math.cos(phi), math.sin(phi)
    K = s - 1 / c - c - g
    a = (K * c - 1) / (c - g)
    return a, K - a
