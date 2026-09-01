"""Derive Trump's Level-0 residual grain from the A03 data, BY CODE.

Free squares are the six of Trump's eleven that are not at a trump5 pin:
A03 indices 4, 6, 7, 8, 9, 10 (0,1,3 = BL staircase, 2 = BR, 5 = TR).
"""
import json
import math
import os

import geomlib as G

TOL = 1e-9
SHRINK = 1e-7        # pull segment ends away from an exposed pin corner


def square_poly(cx, cy, th):
    c, s = math.cos(th), math.sin(th)
    out = []
    for dx, dy in ((-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)):
        out.append((cx + c * dx - s * dy, cy + s * dx + c * dy))
    return out


def _pt_seg(p, a, b):
    vx, vy = b[0] - a[0], b[1] - a[1]
    L2 = vx * vx + vy * vy
    if L2 <= 0:
        return math.hypot(p[0] - a[0], p[1] - a[1])
    t = ((p[0] - a[0]) * vx + (p[1] - a[1]) * vy) / L2
    t = max(0.0, min(1.0, t))
    return math.hypot(p[0] - (a[0] + t * vx), p[1] - (a[1] + t * vy))


def _seg_seg(a, b, c, d):
    def cr(o, p, q):
        return (p[0] - o[0]) * (q[1] - o[1]) - (p[1] - o[1]) * (q[0] - o[0])
    d1, d2 = cr(c, d, a), cr(c, d, b)
    d3, d4 = cr(a, b, c), cr(a, b, d)
    if ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)):
        return 0.0
    return min(_pt_seg(a, c, d), _pt_seg(b, c, d), _pt_seg(c, a, b), _pt_seg(d, a, b))


def _inside(p, poly):
    n = len(poly)
    sgn = 0
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        cr = (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
        if cr > 1e-12:
            if sgn < 0:
                return False
            sgn = 1
        elif cr < -1e-12:
            if sgn > 0:
                return False
            sgn = -1
    return True


def poly_seg_dist(poly, a, b):
    if _inside(a, poly) or _inside(b, poly):
        return 0.0
    n = len(poly)
    return min(_seg_seg(poly[i], poly[(i + 1) % n], a, b) for i in range(n))


def poly_pt_dist(poly, p):
    if _inside(p, poly):
        return 0.0
    n = len(poly)
    return min(_pt_seg(p, poly[i], poly[(i + 1) % n]) for i in range(n))


def poly_poly_dist(p1, p2):
    n1, n2 = len(p1), len(p2)
    best = min(_seg_seg(p1[i], p1[(i + 1) % n1], p2[j], p2[(j + 1) % n2])
               for i in range(n1) for j in range(n2))
    return best


def element_endpoints(i, s):
    """Endpoints of element i at side s (a point element returns (p,p))."""
    e = G.ELEMS[i]

    def aff(x):
        return x[0] + x[1] * s
    if e['kind'] == 'p':
        p = (aff(e['px']), aff(e['py']))
        return p, p
    pos, tl, th = aff(e['pos']), aff(e['tlo']), aff(e['thi'])
    if e['kind'] == 'v':
        return (pos, tl), (pos, th)
    return (tl, pos), (th, pos)


def shrunk_segment(i, s):
    """Segment i with each end that is an exposed pin corner pulled back by SHRINK
    (contacts exactly at a pin corner belong to the corner element ONLY)."""
    a, b = element_endpoints(i, s)
    corners = [element_endpoints(c, s)[0] for c in G.CORNER_ENDPOINTS.get(i, [])]
    ax, ay = a
    bx, by = b
    L = math.hypot(bx - ax, by - ay)
    ux, uy = (bx - ax) / L, (by - ay) / L
    for cp in corners:
        if math.hypot(ax - cp[0], ay - cp[1]) < 1e-12:
            ax, ay = ax + SHRINK * ux, ay + SHRINK * uy
        if math.hypot(bx - cp[0], by - cp[1]) < 1e-12:
            bx, by = bx - SHRINK * ux, by - SHRINK * uy
    return (ax, ay), (bx, by)


def derive():
    here = os.path.dirname(os.path.abspath(__file__))
    p = os.path.join(here, '..', '..', 'A03-upper-reconstruct', 'trump11_float.json')
    d = json.load(open(p))
    s = d['s']
    X = d['X']
    free = [4, 6, 7, 8, 9, 10]
    polys = {i: square_poly(*X[i]) for i in free}
    masks = {}
    for i in free:
        bits = 0
        for e in range(G.NE):
            if G.ELEMS[e]['kind'] == 'p':
                a, b = element_endpoints(e, s)
                dd = poly_pt_dist(polys[i], a)
            else:
                a, b = shrunk_segment(e, s)
                dd = poly_seg_dist(polys[i], a, b)
            if dd < TOL:
                bits |= 1 << e
        masks[i] = bits
    edges = []
    for a in range(len(free)):
        for b in range(a + 1, len(free)):
            i, j = free[a], free[b]
            if poly_poly_dist(polys[i], polys[j]) < TOL:
                edges.append((i, j))
    centres = {i: (X[i][0], X[i][1]) for i in free}
    return dict(s=s, free=free, masks=masks, edges=edges, centres=centres)


def bits_names(b):
    return [G.NAMES[i] for i in range(G.NE) if (b >> i) & 1]


if __name__ == '__main__':
    r = derive()
    for i in r['free']:
        print(i, bits_names(r['masks'][i]), r['centres'][i])
    print('E =', r['edges'])
