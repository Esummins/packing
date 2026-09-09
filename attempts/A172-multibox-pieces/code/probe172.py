"""A172 probe -- re-derive the PI's measurement before touching A171's library.

Normalises A168's S2 node with A171's CURRENT code (K' from the union hull), then computes, on
exactly those surviving pieces, the exact intersection of the per-piece K' polygons, and prints the
two area tables side by side plus timings.  Nothing here is the deliverable: the prototype of every
function below moves into multibox.py once the numbers are confirmed.

    python probe172.py
"""
import math
import os
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
A171 = os.path.abspath(os.path.join(HERE, "..", "..", "A171-multibox-invariant", "code"))
sys.path.insert(0, A171)

import multibox as MB                                          # noqa: E402
import polycore as PC                                          # noqa: E402
from caselp import Box, t_lo, t_hi                             # noqa: E402

VDEN = 10 ** 9


def f_down(v):
    f = float(v)
    return f if Fr(f) <= v else math.nextafter(f, -math.inf)


def f_up(v):
    f = float(v)
    return f if Fr(f) >= v else math.nextafter(f, math.inf)


def piece_box(bn, rect):
    """a caselp.Box CONTAINING the piece: every float coordinate rounded OUTWARD."""
    x0, x1, y0, y1 = rect
    b = Box(f_down(x0), f_up(x1), f_down(y0), f_up(y1),
            MB.deg_of_t(bn.t0), MB.deg_of_t(bn.t1))
    pt0, pt1 = t_lo(b.th0), t_hi(b.th1)
    assert pt0 <= bn.t0 and pt1 >= bn.t1, "piece box narrower than the piece"
    return b, pt0, pt1


def clip_frac(poly, nx, ny, b):
    """Sutherland-Hodgman of a convex rational polygon by  nx x + ny y <= b.  Exact."""
    if not poly:
        return poly
    out = []
    m = len(poly)
    for i in range(m):
        px, py = poly[i]
        qx, qy = poly[(i + 1) % m]
        dp = nx * px + ny * py - b
        dq = nx * qx + ny * qy - b
        if dp <= 0:
            out.append((px, py))
        if (dp > 0) != (dq > 0):
            t = dp / (dp - dq)
            out.append((px + t * (qx - px), py + t * (qy - py)))
    return out


def dedupe(P):
    out = []
    for p in P:
        if not out or p != out[-1]:
            out.append(p)
    if len(out) > 1 and out[0] == out[-1]:
        out.pop()
    return out


def tri2(a, b, c):
    return abs((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]))


def simplify_in(P, max_v):
    """drop vertices of a convex ccw polygon (always INWARD: the cut triangle is removed)."""
    P = dedupe(list(P))
    while len(P) > 3:
        m = len(P)
        ar = [tri2(P[(i - 1) % m], P[i], P[(i + 1) % m]) for i in range(m)]
        j = min(range(m), key=lambda i: ar[i])
        if len(P) > max_v or ar[j] == 0:
            P.pop(j)
        else:
            break
    return P


def poly_area(P):
    a = Fr(0)
    m = len(P)
    for i in range(m):
        x0, y0 = P[i]
        x1, y1 = P[(i + 1) % m]
        a += x0 * y1 - x1 * y0
    return abs(a) / 2


def intersect_frac(polys, max_v=16, work_v=28):
    """exact intersection of convex ccw rational polygons."""
    P = list(polys[0])
    for Q in polys[1:]:
        m = len(Q)
        for i in range(m):
            ax, ay = Q[i]
            bx, by = Q[(i + 1) % m]
            nx, ny = (by - ay), -(bx - ax)          # outward normal of a ccw polygon
            if nx == 0 and ny == 0:
                continue
            P = clip_frac(P, nx, ny, nx * ax + ny * ay)
            if len(P) < 3:
                return []
        P = simplify_in(P, work_v)
        if len(P) < 3:
            return []
    return simplify_in(P, max_v)


def round_grid(P, shrink, den=VDEN):
    n = len(P)
    cx = sum(p[0] for p in P) / n
    cy = sum(p[1] for p in P) / n
    out = []
    for (x, y) in P:
        x = cx + (x - cx) * (1 - shrink)
        y = cy + (y - cy) * (1 - shrink)
        out.append((Fr(round(x * den), den), Fr(round(y * den), den)))
    return PC._hull_frac(out)


def pieces_poly(pieces, max_v=16, n_grid=97, cache=None, shrinks=(Fr(0), Fr(1, 10 ** 8),
                                                                  Fr(1, 10 ** 6), Fr(1, 10 ** 4))):
    """K'(B) = certified intersection of the per-piece K'.  Returns (verts, info)."""
    boxes = []
    polys = []
    for (bn, r) in pieces:
        pb, pt0, pt1 = piece_box(bn, r)
        boxes.append((pb, pt0, pt1))
        key = (str(bn.t0), str(bn.t1)) + tuple(str(v) for v in r)
        pc = None if cache is None else cache.get(key)
        if pc is None:
            pc = PC.build(pb, n_grid=n_grid, max_v=max_v)
            if cache is not None:
                cache[key] = pc
        polys.append(pc.verts)
    P = intersect_frac(polys, max_v=max_v)
    if len(P) < 3:
        return None, dict(reason="empty intersection")
    for sh in shrinks:
        V = round_grid(P, sh)
        if len(V) < 3:
            continue
        bad = 0
        for (vx, vy) in V:
            for (pb, pt0, pt1) in boxes:
                if not PC.vertex_ok(vx, vy, pb, pt0, pt1):
                    bad += 1
                    break
        if not bad:
            return V, dict(shrink=str(sh), n_pieces=len(pieces), nv=len(V))
    return None, dict(reason="no certified rounding")


def main():
    t0 = time.time()
    nd = MB.Node(MB.__dict__ and {
        "H": (2.5674485, 2.67226625, 2.357813, 2.46263075, 45.0, 60.0),
        "B1": (3.127084, 3.1733821433529026, 1.5015011950128963, 1.5785397484754269, 45.0, 50.625),
        "D": (3.223006893074939, 3.377084, 3.211365683498047, 3.377084, 0.0, 11.25)},
        name="A168 BR139/TRH-25")
    nd.normalise(nsub=4, refine=3)
    print(f"old normalise: {time.time() - t0:.1f} s  passes={nd.stats['passes']}  "
          f"kept=" + " ".join(f"{k}={v:.6f}" for k, v in nd.kept().items()))
    cache = {}
    news = {}
    for k, mb in nd.boxes.items():
        t = time.time()
        V, info = pieces_poly(mb.pieces, cache=cache)
        dt = time.time() - t
        if V is None:
            print(f"  {k}: FAILED {info}")
            continue
        news[k] = V
        print(f"  {k}: pieces={len(mb.pieces):3d}  union-hull area={mb.pc.area():.6f}  "
              f"per-piece area={float(poly_area(V)):.6f}  nv={len(V)}  {dt:.1f} s  {info}")
    # one more clip pass with the per-piece obstacles
    obst = {k: MB.Obstacle(V, name=k) for k, V in news.items()}
    for k, mb in nd.boxes.items():
        keep = []
        for (bn, r) in mb.pieces:
            cur = r
            for j in nd.names:
                if j == k or cur is None:
                    continue
                cur = MB._clip_rect_obstacle(cur, obst[j], bn, nd.stats)
            if cur is not None:
                keep.append((bn, cur))
        v = sum(MB.rect_area(r) * (b.t1 - b.t0) for (b, r) in keep)
        print(f"  {k}: kept {mb.kept_fraction():.4f} -> {float(v / mb.area0):.4f} "
              f"({len(mb.pieces)} -> {len(keep)} pieces)")
    print(f"total {time.time() - t0:.1f} s")


if __name__ == "__main__":
    main()
