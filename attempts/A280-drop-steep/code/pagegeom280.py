"""A280 page data: the bad-centre TEST SET of a leaf (A273's per-box q-cell test, drop273.cell_dead over
drop4273.BoxSets4) on a uniform q-grid of half-side H, each cell labelled by the rule that kills it (K01 / KL / K4 /
K2 / K5), 'fine' (not dead at H but closed by the same recursion down to 1/4096 -- decided), or None (UNDECIDED at
1/4096: grey stipple), per part R / L; plus the exact polygons at the box midpoint and the geometry checks."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prune280 as P8                                                 # noqa: E402
import drop4273 as D4                                                 # noqa: E402
import drop273 as D3                                                  # noqa: E402
from shapely.geometry import Polygon, Point                           # noqa: E402

H = 1.0 / 32


def closes(B, z, h, part, hmin=1.0 / 4096, budget=4000):
    stack, n = [(z[0], z[1], h)], 0
    while stack:
        x, y, hh = stack.pop()
        n += 1
        if n > budget:
            return False
        if D3.cell_dead(B, (x, y), hh, part):
            continue
        if hh / 2 < hmin:
            return False
        stack += [(x + dx * hh, y + dy * hh, hh / 2) for dx in (-0.5, 0.5) for dy in (-0.5, 0.5)]
    return True


def polys(m):
    hu, th, dd, ph = m
    c, s, cp, sp = math.cos(th), math.sin(th), math.cos(ph), math.sin(ph)
    return dict(T=[(s, -c - s), (s + c, -c), (c, 0.0), (0.0, -s)],
                C=[(hu + s, -c - s), (hu + s + c, -c), (hu + c, 0.0), (hu, -s)],
                X=[(sp, -dd), (sp + cp, -dd + sp), (cp, -dd + sp + cp), (0.0, -dd + cp)])


def testset(b, part='R', fine=True):
    """q-grid cells of half-side H over the run_cells window; each (x, y, label)."""
    B = D4.BoxSets4(b)
    xs, ys = [p[0] for p in B.Tuo], [p[1] for p in B.Tuo]
    x0, x1 = max(0.5, min(xs) - D3.G.R2), max(xs) + D3.G.R2
    y0, y1 = B.Lmin, max(ys) + D3.G.R2
    out = []
    for i in range(int(math.ceil((x1 - x0) / (2 * H)))):
        for j in range(int(math.ceil((y1 - y0) / (2 * H)))):
            z = (x0 + (2 * i + 1) * H, y0 + (2 * j + 1) * H)
            k = D3.cell_dead(B, z, H, part)
            if not k and fine:
                k = 'fine' if closes(B, z, H, part) else None
            out.append((z[0], z[1], k))
    return out


def checks(m):
    """exact geometry at the midpoint: areas of X n T_u, X n C, T_u's top vertex, the D-low bound."""
    P = {k: Polygon(v) for k, v in polys(m).items()}
    hu, th, dd, ph = m
    return dict(XnTu=P['X'].intersection(P['T']).area, XnC=P['X'].intersection(P['C']).area,
                dlow=(math.cos(th) - math.sin(ph)) * math.tan(min(th, ph)), D=dd,
                Tu_top=(math.cos(th), 0.0), X_bottom=(math.sin(ph), -dd))


def corner_panel(hu=0.9999, thd=40.0, phd=32.88, ddel=1e-3):
    """the h_u -> 1 near-miss: q = (1/2, L_h'') at the wall, D(q, 1/2) touching the wall, C's left vertex and X."""
    th, ph = math.radians(thd), math.radians(phd)
    dd = (math.cos(th) - math.sin(ph)) * math.tan(ph) + ddel
    m = [hu, th, dd, ph]
    q = (0.5, -math.sin(th))
    P = {k: Polygon(v) for k, v in polys(m).items()}
    D = Point(q).buffer(0.5, 256)
    c, s = math.cos(th), math.sin(th)
    lowb = P8.lowb((th, th))
    ob_hv = (c + s - s * c - hu * c) / s
    return dict(m=m, q=q, polys=polys(m), disc_wall=q[0] - 0.5, disc_Cleft=math.hypot(hu - q[0], 0.0) - 0.5,
                disc_X=D.distance(P['X']) if not D.intersects(P['X']) else -D.intersection(P['X']).area,
                hv_low=lowb - c, hv_up_openbox=ob_hv, hu_max=(c + s - s * c - (lowb - c) * s) / c)
