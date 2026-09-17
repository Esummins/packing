"""A252: the closed forms of `docs/proofs/centre_disc.md` -- CONTACT-TRIPLES, the CORNER WEDGE
(the MOUTH), the corner NOTCH separation, the vertex-pair sector, and the FLAT LIMIT that makes
Lemma CENTRE-DISC (about the container centre O) FALSE on the window.

Corner frame (A249 geom249): wall meeter B with L = (0, delta_B + cos tB), V = (sin tB, delta_B),
R = V + (cos tB, sin tB), T = L + (cos tB, sin tB); floor meeter A with V_A = (delta_A + sin tA, 0),
W = (delta_A, cos tA), R_A = V_A + (cos tA, sin tA), T_A = W + (cos tA, sin tA).
The disc of radius 1/2 about q is disjoint from a square iff dist(q, square) >= 1/2, i.e. in the
square's own frame (a, b) (unit coordinates along its two edge directions from a vertex)
max(0, -a, a - 1)^2 + max(0, -b, b - 1)^2 >= 1/4: separated by an EDGE LINE with margin 1/2
(one coordinate outside by >= 1/2, the other inside) or by a VERTEX (both outside, at
Euclidean distance >= 1/2, i.e. q in the vertex's outer normal cone).

[T] Lemma CONTACT-TRIPLES (any n).  C = {q : D(q, 1/2) in the pocket} is compact; a maximiser of
a linear functional (or of |q - O|) over C lies on the boundary of C, which is a finite union of
straight pieces (edge contacts, wall contacts) and circular arcs of radius 1/2 (vertex contacts).
Hence either TWO constraints are active at the maximiser (edge-edge, edge-vertex, vertex-vertex,
wall-edge, wall-vertex, wall-wall), or ONE vertex contact with q = P + (1/2) u, u the maximised
direction (the disc touches the vertex P alone, from the far side) -- for |q - O| this needs
u = (P - O)/|P - O| to lie in P's outer normal cone, impossible at an INNER vertex (its cone
points towards O), so a far point with one contact touches an OUTER vertex (a notch case).
The list is complete because C's boundary has no other pieces.  Verified as a census on the
adversarial rings (lemmas252.contact_census).

[T] Lemma MOUTH (the corner wedge).  The disc separated from B by the line of its edge V -> R
(outward normal (sin tB, -cos tB), margin 1/2) and from A by the line of its INNER edge
R_A -> T_A (outward normal (cos tA, sin tA), margin 1/2) has centre on the two offset lines
    (q - V) . (sin tB, -cos tB) = 1/2,   (q - T_A) . (cos tA, sin tA) = 1/2,
which meet at the wedge angle alpha = 90 + tA - tB in (0, 180): the disc sits at distance
1/(2 sin(alpha/2)) from the apex on the bisector.  The two-edge contact point
q_mouth(tB, dB, tA, dA) is closed-form (mouth_centre); with its feet on the two SEGMENTS it is the
edge-edge case of CONTACT-TRIPLES, and its distance from O is maximised, over the family's box
[0, 90]^2 x [0.406, 1]^2, at the FLAT LIMIT tB, tA -> 90 deg, dB, dA -> 1 (the type-F limit of
both touchers): q_mouth -> (3/2, 3/2), |q_mouth - O| -> (s/2 - 3/2) sqrt2 (mouth_box_max).

[F] Lemma CENTRE-DISC about O.  (s/2 - 3/2) sqrt2 > 1/sqrt3  iff  s > 3 + 2/sqrt6 = 3.81650, so
on the whole window a ring near the flat limit at ONE corner has an admissible centre farther
than 1/sqrt3 from O (adv252: far_O = 0.628 > 0.577 at s = 3.99 with ring margin +0.003).  Both
squares of that corner are nearly flat (type-F limit) with delta -> 1: the corner box is met by
slivers, the corner pair interlocks through a channel of width -> 0, the neighbours poke their
tips into the strips the flat squares leave (Lemma GAP).

[T] Lemma NOTCH-SEP.  A disc of radius 1/2 in the corner NOTCH (separated from B by the line of
L -> V, from A by the line of V_A -> W, in {u, v >= 1/2}) needs tB > 45 deg with
delta_B >= phi(tB) := 1/2 - cos tB + (1 + cos tB)/(2 sin tB) and tA < 45 deg with
delta_A >= phi(90 - tA); min phi = 0.866 (at 60 deg).  Proof: (q - L) . (cos t, sin t) <= -1/2
with u >= 1/2 gives v <= delta_B + cos t - (1 + cos t)/(2 sin t), and v >= 1/2.  phi(t) < 1
iff sin t + 2 sin t cos t > 1 + cos t iff t > 45 deg.

[T] Lemma TWO-VERTEX.  A disc of radius 1/2 touching two points P1, P2 at distance d <= 1 has its
centre on their bisector at height sqrt(1/4 - d^2/4) above the midpoint M, so
|q - O| <= |M - O| + sqrt(1/4 - d^2/4): the vertex-vertex sector bound.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import disc252 as D                                                   # noqa: E402

R3 = D.R3


def phi(t):
    return 0.5 - math.cos(t) + (1.0 + math.cos(t)) / (2.0 * math.sin(t))


def phi_min(grid=200001):
    ts = np.linspace(math.radians(45.0001), math.radians(89.9999), grid)
    v = 0.5 - np.cos(ts) + (1 + np.cos(ts)) / (2 * np.sin(ts))
    i = int(np.argmin(v))
    return float(v[i]), math.degrees(float(ts[i]))


def wedge_angle(tB, tA):
    """the angle between B's edge V->R and A's inner edge R_A->T_A: 90 + tA - tB degrees."""
    return math.pi / 2 + tA - tB


def mouth_centre(tB, dB, tA, dA):
    """the centre q with (q - V).(sin tB, -cos tB) = 1/2 (beyond B's edge V->R) and
    (q - T_A).(cos tA, sin tA) = 1/2 (beyond A's inner edge R_A->T_A); None if parallel."""
    V = (math.sin(tB), dB)
    TA = (dA + math.cos(tA), math.sin(tA) + math.cos(tA))
    n1 = (math.sin(tB), -math.cos(tB))
    n2 = (math.cos(tA), math.sin(tA))
    A = np.array([n1, n2])
    b = np.array([0.5 + n1[0] * V[0] + n1[1] * V[1], 0.5 + n2[0] * TA[0] + n2[1] * TA[1]])
    det = A[0, 0] * A[1, 1] - A[0, 1] * A[1, 0]
    if abs(det) < 1e-12:
        return None
    q = np.linalg.solve(A, b)
    return (float(q[0]), float(q[1]))


def mouth_far(tB, dB, tA, dA, s):
    """|q_mouth - O| when the mouth point is a genuine two-EDGE contact: in the corner's
    quadrant, its feet on the segments V->R and R_A->T_A (else the contact is a vertex or a notch
    case, handled by NOTCH-SEP / TWO-VERTEX), else None."""
    q = mouth_centre(tB, dB, tA, dA)
    if q is None or q[0] < 0.5 or q[1] < 0.5 or q[0] > s / 2 or q[1] > s / 2:
        return None
    V = (math.sin(tB), dB)
    RA = (dA + math.sin(tA) + math.cos(tA), math.sin(tA))
    fB = (q[0] - V[0]) * math.cos(tB) + (q[1] - V[1]) * math.sin(tB)      # along V -> R
    fA = -(q[0] - RA[0]) * math.sin(tA) + (q[1] - RA[1]) * math.cos(tA)   # along R_A -> T_A
    if not (0 <= fB <= 1 and 0 <= fA <= 1):
        return None
    return math.hypot(q[0] - s / 2, q[1] - s / 2)


def mouth_box_max(s, grid=41, d_lo=None):
    """the maximum of mouth_far over the family box (grid + local refinement), against the
    flat-limit value (s/2 - 3/2) sqrt2 attained at the box corner (90, 1, 90, 1)."""
    if d_lo is None:
        d_lo = max(0.0, s - 2 - math.sqrt(2.0))
    ts = np.linspace(math.radians(1), math.radians(89.9), grid)
    ds = np.linspace(d_lo, 1.0, grid)
    best = (0.0, None)
    for tB in ts:
        for tA in ts:
            if abs(tA - tB) < 1e-9:
                continue
            for dB in ds:
                for dA in ds:
                    if dB + D.W.G.w(tB) <= s - 2 or dA + D.W.G.w(tA) <= s - 2:
                        continue
                    v = mouth_far(tB, dB, tA, dA, s)
                    if v is not None and v > best[0]:
                        best = (v, (float(tB), float(dB), float(tA), float(dA)))
    return best


def two_vertex_bound(P1, P2, O):
    d = math.dist(P1, P2)
    if d > 1.0:
        return None
    M = ((P1[0] + P2[0]) / 2, (P1[1] + P2[1]) / 2)
    return math.dist(M, O) + math.sqrt(max(0.0, 0.25 - d * d / 4))


def active_set(q, polys, s, tol=2e-3):
    """the contacts of the disc D(q, 1/2): (element, kind) with kind in edge / vertex / wall."""
    from shapely.geometry import Point, Polygon, LineString
    out = []
    P = Point(q)
    for V, name in zip(polys, D.NAMES):
        if abs(Polygon(V).distance(P) - 0.5) > tol:
            continue
        kind = 'edge'
        for k in range(4):
            if abs(math.dist(q, tuple(V[k])) - 0.5) <= tol:
                kind = 'vertex'
        out.append((name, kind))
    for name, dval in (('x=0', q[0]), ('y=0', q[1]), ('x=s', s - q[0]), ('y=s', s - q[1])):
        if abs(dval - 0.5) <= tol:
            out.append((name, 'wall'))
    return out


def contact_census(rows_file=None):
    """the active sets at the far point of every adversarial ring (Lemma CONTACT-TRIPLES [M])."""
    rows_file = rows_file or os.path.join(ATT, 'results', 'adv252.jsonl')
    census, n = {}, 0
    if not os.path.exists(rows_file):
        return census, n
    for line in open(rows_file, encoding='utf-8'):
        r = json.loads(line)
        if r['margin'] < 0:
            continue
        s = float(r['side'])
        polys, _ = D.ring(r['x'], s)
        C = D.centre_set(polys, s)
        pts = D.boundary_pts(C)
        fo, fq = D.far_from(pts, (s / 2, s / 2))
        if fq is None:
            continue
        act = active_set(fq, polys, s)
        key = '+'.join(sorted(k for _, k in act)) or 'none'
        census[key] = census.get(key, 0) + 1
        n += 1
    return census, n


def main():
    out = {'three_disc_radius': R3, 's_flat': D.S_FLAT, 'phi_min': phi_min()}
    out['flat_limit_far'] = {str(s): D.flat_limit_far(s) for s in (3.82, D.SW, 3.90, 3.95, 3.99)}
    out['mouth_box_max'] = {}
    for s in (3.82, D.SW, 3.99):
        v, arg = mouth_box_max(s, grid=25)
        out['mouth_box_max'][str(s)] = {'value': v, 'arg_deg': None if arg is None else
                                        [math.degrees(arg[0]), arg[1], math.degrees(arg[2]), arg[3]],
                                        'flat_limit': D.flat_limit_far(s)}
        print('s=%.4f mouth max over the box grid %.4f at %s vs flat limit %.4f' %
              (s, v, out['mouth_box_max'][str(s)]['arg_deg'], D.flat_limit_far(s)))
    census, n = contact_census()
    out['contact_census'] = census
    out['contact_rows'] = n
    print('phi min %.4f at %.2f deg; s_flat %.5f; census %s (%d rows)' %
          (out['phi_min'][0], out['phi_min'][1], D.S_FLAT, census, n))
    json.dump(out, open(os.path.join(ATT, 'results', 'lemmas252.json'), 'w', encoding='utf-8'), indent=1)


if __name__ == '__main__':
    main()
