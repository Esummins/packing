"""A237 pocket geometry (n-general, shapely): the POCKET of a ring = container minus the interiors of the ring
members; its boundary features (vertices with interior angles, convex / reflex, edges flush / tilted); the
rigorous COVERABLE-SET sandwich over tilt bins (docs/proofs/pocket_waste.md s.2, Lemma JAGGED (J1)):

    coverable(P) := union of every unit square inside P  =  U_theta ( C(theta) (+) Q_theta ),  C(theta) = {c : c + Q_theta in P}
    for a tilt bin [t1, t2] of width D with mid m:  K := Q_m / w(D/2)  is inside every Q_theta of the bin and
    H := w(D/2) Q_m contains every one  (w(a) = cos a + sin a; the infinity-norm of a point changes by at most that
    factor under a rotation by <= a);  hence  C(theta) subset  P (-) K  and  Q_theta subset H, so
    coverable(P)  subset  U_bins ( (P (-) K_bin) (+) H_bin )  =: COV_bar,   WASTE(P) := area(P) - area(COV_bar) <= true waste.

    PIERCE(k): points p_1..p_k with  P (-) K_bin  subset  U_i (p_i + K_bin)  for every bin  =>  every unit square in P
    contains some p_i  =>  at most k interior-disjoint unit squares fit in P (capacity <= k).
Poses are (cx, cy, theta) in a y-up frame.  Minkowski sums: convex (+) convex = hull of vertex sums; a polygon (+) a
convex H containing 0 = the polygon U (each boundary edge (+) H).
"""
import math

import numpy as np
from shapely.geometry import Polygon, MultiPolygon, Point, box as sbox
from shapely.ops import unary_union

DEG = math.pi / 180.0


def w_of(a):
    return abs(math.cos(a)) + abs(math.sin(a))


def sq_verts(cx, cy, th, half=0.5):
    c, d = math.cos(th), math.sin(th)
    return [(cx + c * x - d * y, cy + d * x + c * y) for x, y in ((-half, -half), (half, -half), (half, half), (-half, half))]


def sq_poly(pose, half=0.5):
    return Polygon(sq_verts(*pose, half=half))


def polys_of(g):
    if g.is_empty:
        return []
    if isinstance(g, MultiPolygon):
        return [p for p in g.geoms if p.area > 1e-14]
    if isinstance(g, Polygon):
        return [g] if g.area > 1e-14 else []
    return [p for p in getattr(g, 'geoms', []) if isinstance(p, Polygon) and p.area > 1e-14]


def pocket(members, s):
    """container minus the ring members (closed squares removed; the pocket is the closure of the open complement)."""
    P = sbox(0.0, 0.0, s, s)
    if members:
        P = P.difference(unary_union([sq_poly(m) for m in members]))
    return P


def minkowski_convex(A, B):
    """hull of the vertex sums of two convex polygons (vertex lists)."""
    return Polygon([(a[0] + b[0], a[1] + b[1]) for a in A for b in B]).convex_hull


def erode_by_square(P, s, members, th, half):
    """{c : c + Q in P} for the square Q of tilt th and half-side `half` (Lemma GRAIN-LP's fixed-tilt free space):
    the container shrunk by Q's axis half-width minus every member (+) Q."""
    h = half * w_of(th)
    if s - 2 * h <= 0:
        return Polygon()
    region = sbox(h, h, s - h, s - h)
    q0 = sq_verts(0.0, 0.0, th, half)
    sums = [minkowski_convex(sq_verts(*m), q0) for m in members]
    if sums:
        region = region.difference(unary_union(sums))
    return region


def dilate_by_convex(G, Hv):
    """G (+) H for a convex H (vertex list) containing the origin: G U (each boundary edge (+) H)."""
    parts = []
    for poly in polys_of(G):
        parts.append(poly)
        for ring in [poly.exterior] + list(poly.interiors):
            pts = list(ring.coords)
            for a, b in zip(pts[:-1], pts[1:]):
                parts.append(minkowski_convex([a, b], Hv))
    return unary_union(parts) if parts else Polygon()


def bins(step_deg=1.0):
    n = int(round(90.0 / step_deg))
    return [(k * step_deg * DEG, (k + 1) * step_deg * DEG) for k in range(n)]


def kernel_hull(t1, t2):
    """(K, H, mid): the inner and outer squares of a tilt bin."""
    m, D = 0.5 * (t1 + t2), 0.5 * (t2 - t1)
    f = w_of(D)
    return sq_verts(0.0, 0.0, m, 0.5 / f), sq_verts(0.0, 0.0, m, 0.5 * f), m, f


def coverable(members, s, step_deg=1.0):
    """COV_bar (a superset of the coverable set) and the per-bin free-centre regions."""
    parts, free = [], []
    for t1, t2 in bins(step_deg):
        K, H, m, f = kernel_hull(t1, t2)
        Cbar = erode_by_square(None, s, members, m, 0.5 / f)
        free.append((t1, t2, Cbar))
        if not Cbar.is_empty:
            parts.append(dilate_by_convex(Cbar, H))
    COV = unary_union(parts) if parts else Polygon()
    return COV, free


def waste(members, s, step_deg=1.0):
    P = pocket(members, s)
    COV, free = coverable(members, s, step_deg)
    COV = COV.intersection(P)
    U = P.difference(COV)
    return {'area': P.area, 'coverable_area': COV.area, 'waste': P.area - COV.area, 'pocket': P, 'cov': COV,
            'uncov': U, 'free': free}


def pierce(members, s, points, step_deg=1.0, free=None):
    """max over bins of the area of  (P (-) K_bin) minus U_i (p_i + K_bin);  0 (<= tol) certifies capacity <= len(points)."""
    worst = 0.0
    if free is None:
        free = coverable(members, s, step_deg)[1]
    for t1, t2, Cbar in free:
        if Cbar.is_empty:
            continue
        K, H, m, f = kernel_hull(t1, t2)
        cover = unary_union([Polygon([(p[0] + k[0], p[1] + k[1]) for k in K]) for p in points])
        worst = max(worst, Cbar.difference(cover).area)
    return worst


def features(P):
    """boundary features of the pocket polygon(s): vertices with interior angle (deg) and convexity, edges with
    length and tilt (deg mod 90, folded to [0, 45])."""
    verts, edges = [], []
    for poly in polys_of(P):
        for ring, outer in [(poly.exterior, True)] + [(r, False) for r in poly.interiors]:
            pts = list(ring.coords)[:-1]
            if not outer:
                pts = pts[::-1]
            # orient the exterior counter-clockwise so that the interior is on the left
            area2 = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
            if (area2 < 0) == outer:
                pts = pts[::-1]
            n = len(pts)
            for i in range(n):
                a, b, c = np.array(pts[i - 1]), np.array(pts[i]), np.array(pts[(i + 1) % n])
                u, v = a - b, c - b
                if np.linalg.norm(u) < 1e-12 or np.linalg.norm(v) < 1e-12:
                    continue
                ang = math.degrees(math.atan2(u[0] * v[1] - u[1] * v[0], u @ v)) % 360.0
                # interior angle measured from the outgoing edge to the incoming edge, counter-clockwise interior
                inner = (360.0 - ang) % 360.0 if outer else (360.0 - ang) % 360.0
                if abs(inner - 180.0) < 1e-6:
                    continue
                verts.append({'x': float(b[0]), 'y': float(b[1]), 'angle': inner, 'convex': inner < 180.0,
                              'hole': not outer})
                e = c - b
                L = float(np.linalg.norm(e))
                t = math.degrees(math.atan2(e[1], e[0])) % 90.0
                edges.append({'x0': float(b[0]), 'y0': float(b[1]), 'x1': float(c[0]), 'y1': float(c[1]), 'len': L,
                              'tilt': min(t, 90.0 - t), 'flush': min(t, 90.0 - t) < 1e-6})
    return verts, edges


def components(U):
    """connected components of the uncoverable set: area, centroid."""
    out = []
    for poly in polys_of(U):
        c = poly.centroid
        out.append({'area': poly.area, 'cx': c.x, 'cy': c.y, 'poly': poly})
    out.sort(key=lambda r: -r['area'])
    return out


def attribute(comps, verts):
    """attach each uncoverable component to the nearest pocket vertex (its feature)."""
    for comp in comps:
        best, bd = None, 1e9
        for v in verts:
            d = comp['poly'].distance(Point(v['x'], v['y']))
            if d < bd:
                best, bd = v, d
        comp['vertex'] = best
        comp['vertex_dist'] = bd
    return comps


def wedge_radius_bound(alpha_deg):
    """Lemma WEDGE [T]: no unit square inside a wedge of angle alpha <= 90 deg comes closer to its apex than
    (1 + w(alpha)) / (4 sin(alpha/2)) - 1/sqrt2."""
    a = alpha_deg * DEG
    if alpha_deg >= 90.0:
        return 0.0
    return max(0.0, (1.0 + w_of(a)) / (4.0 * math.sin(a / 2)) - 1.0 / math.sqrt(2.0))


def wedge_radius_exact(alpha_deg, grid=721):
    """the least distance from the apex of a unit square inside the wedge [M]: over the tilt psi, the square's
    lowest vertex on ray 0 or leftmost vertex on ray alpha, minimising the distance (numeric, for the table)."""
    a = alpha_deg * DEG
    if alpha_deg >= 90.0:
        return 0.0
    best = 1e9
    n2 = (math.sin(a), -math.cos(a))
    for k in range(grid):
        psi = (k / (grid - 1)) * math.pi / 2
        V = np.array(sq_verts(0.0, 0.0, psi))
        # slide along ray 0 until touching y = 0 (already: put min y = 0), then along ray alpha
        V[:, 1] -= V[:, 1].min()
        need = -min(v[0] * n2[0] + v[1] * n2[1] for v in V)        # shift right by need / sin(alpha) puts Q inside
        if need > 0:
            V[:, 0] += need / math.sin(a)
        d = Polygon(V).distance(Point(0.0, 0.0))
        best = min(best, d)
    return best
