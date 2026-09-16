"""A232 -- the leftover search: place `need - 1` further unit squares beside the corner slot,
inside [0, m_lo]^2, interior-disjoint from each other and from the slot, and MISSING the reach
set of every role outside X.

The search is float (shapely configuration spaces, greedy by clearance with restarts); every
pose it proposes is RATIONAL by construction (axis cells on a dyadic grid; tilted cells with
(cos, sin) = ((1 - u^2)/(1 + u^2), 2u/(1 + u^2)) at rational u, so all four vertices are exact)
and every accepted family is re-decided by `verify_swap232` before it is written out.  A search
failure is therefore never a claim -- only a PASS of the verifier is.
"""
import math
import random
from fractions import Fraction as Fr

from shapely.geometry import Polygon, box as sbox
from shapely.ops import unary_union
from shapely.algorithms.polylabel import polylabel

import verify_swap232 as V

# rational tan(theta/2): theta = 0 .. 45.2 deg (a unit square has period 90 deg)
US = [Fr(0), Fr(1, 12), Fr(1, 7), Fr(1, 5), Fr(1, 4), Fr(1, 3), Fr(2, 5), Fr(5, 12)]
GRID = Fr(1, 4096)


def cs(u):
    return (1 - u * u) / (1 + u * u), 2 * u / (1 + u * u)


def verts(cx, cy, u):
    c, s = cs(u)
    return [(cx + c * a - s * b, cy + s * a + c * b)
            for a, b in ((Fr(-1, 2), Fr(-1, 2)), (Fr(1, 2), Fr(-1, 2)),
                         (Fr(1, 2), Fr(1, 2)), (Fr(-1, 2), Fr(1, 2)))]


def fpoly(V4):
    return Polygon([(float(a), float(b)) for a, b in V4])


def cell_of(cx, cy, u):
    """the certificate object for a pose: an axis cell when u = 0, else the four exact vertices."""
    if u == 0:
        return dict(kind="axis", x=str(cx - Fr(1, 2)), y=str(cy - Fr(1, 2)))
    return dict(kind="poly", verts=[[str(a), str(b)] for a, b in verts(cx, cy, u)])


def _mink(obst, u):
    """obstacles dilated by the posed square (centred at the origin): the forbidden CENTRES."""
    c, s = (float(v) for v in cs(u))
    q = [(c * a - s * b, s * a + c * b) for a, b in ((-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5))]
    out = []
    for g in obst:
        for part in (g.geoms if hasattr(g, "geoms") else [g]):
            if part.is_empty:
                continue
            P = list(part.convex_hull.exterior.coords)[:-1]
            out.append(Polygon([(a[0] + b[0], a[1] + b[1]) for a in P for b in q]).convex_hull)
    return out


def cspace(obst, m_lo, u):
    c, s = (abs(float(v)) for v in cs(u))
    h = (c + s) / 2
    if m_lo - 2 * h <= 0:
        return Polygon()
    reg = sbox(h, h, m_lo - h, m_lo - h)
    d = _mink(obst, u)
    return reg.difference(unary_union(d)) if d else reg


def _candidates(reg, k=6):
    """the pole of inaccessibility of each component, plus a few interior samples."""
    out = []
    for p in (reg.geoms if hasattr(reg, "geoms") else [reg]):
        if p.is_empty or p.area < 1e-9:
            continue
        try:
            pt = polylabel(p, tolerance=2e-3)
            out.append((p.exterior.distance(pt), pt.x, pt.y))
        except Exception:                                        # noqa: BLE001
            c = p.representative_point()
            out.append((0.0, c.x, c.y))
        x0, y0, x1, y1 = p.bounds
        for _ in range(k):
            xx = random.uniform(x0, x1)
            yy = random.uniform(y0, y1)
            from shapely.geometry import Point
            if p.contains(Point(xx, yy)):
                out.append((p.exterior.distance(Point(xx, yy)), xx, yy))
    out.sort(reverse=True)
    return out


def snap(x):
    return Fr(round(x / float(GRID))) * GRID


def _exact_ok(cellobj, boxes, placed_polys):
    """the verifier's own tests: the pose misses every piece of every role outside X and is
    interior-disjoint from what is already placed."""
    P = V.poly_of(cellobj)
    for b in boxes:
        if cellobj["kind"] == "axis":
            ok, _ = V.box_misses_axis_cell(b, (Fr(cellobj["x"]), Fr(cellobj["x"]) + 1,
                                               Fr(cellobj["y"]), Fr(cellobj["y"]) + 1))
        else:
            ok, _ = V.box_misses_poly(b, cellobj["verts"])
        if not ok:
            return False
    for Q in placed_polys:
        if not V.polys_interior_disjoint(P, Q)[0]:
            return False
    return True


def greedy(obst, boxes, m_lo, need, rounds=60, seed=0):
    """one greedy pass: the slot square, then `need - 1` leftovers.  Returns (cells, polys)."""
    rnd = random.Random(seed)
    cells = [dict(kind="axis", x="0", y="0")]
    polys = [V.poly_of(cells[0])]
    fixed = [Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])] + list(obst)
    us = list(US)
    for step in range(need - 1):
        best = None
        rnd.shuffle(us)
        for u in us:
            reg = cspace(fixed, m_lo, u)
            if reg.is_empty:
                continue
            for (clr, x, y) in _candidates(reg)[:4]:
                for (sx, sy) in ((snap(x), snap(y)),):
                    co = cell_of(sx, sy, u)
                    if not _exact_ok(co, boxes, polys):
                        continue
                    sc = clr + rnd.random() * 1e-6
                    if best is None or sc > best[0]:
                        best = (sc, co, fpoly(V.poly_of(co)))
        if best is None:
            break
        cells.append(best[1])
        polys.append(V.poly_of(best[1]))
        fixed.append(best[2])
    return cells, polys


def axis_fill(obst, boxes, m_lo, need, pitch=Fr(1, 8), order="bl", seed=None):
    """the classic bottom-left lattice greedy over AXIS cells (the leaf prefers axis poses: the
    exact miss test is A161's full separating-axis test there).  At most floor(m_lo)^2 = 9 axis
    unit squares fit in [0, m_lo]^2 at all -- the fill measures how many survive the reach sets."""
    cells = [dict(kind="axis", x="0", y="0")]
    polys = [V.poly_of(cells[0])]
    hi = m_lo - 1
    n = int(hi / pitch)
    pos = [(i * pitch, j * pitch) for j in range(n + 1) for i in range(n + 1)]
    if order == "lb":
        pos = [(i * pitch, j * pitch) for i in range(n + 1) for j in range(n + 1)]
    elif order == "tr":
        pos = pos[::-1]
    if seed is not None:
        random.Random(seed).shuffle(pos)
    for (x, y) in pos:
        if len(cells) >= need:
            break
        co = dict(kind="axis", x=str(x), y=str(y))
        if _exact_ok(co, boxes, polys):
            cells.append(co)
            polys.append(V.poly_of(co))
    return cells, polys


def augment(cells, polys, obst, boxes, m_lo, need, seed=0):
    """add TILTED leftovers to an existing family, by clearance."""
    rnd = random.Random(seed)
    fixed = list(obst) + [fpoly(p) for p in polys]
    us = [u for u in US if u != 0]
    while len(cells) < need:
        best = None
        for u in us:
            reg = cspace(fixed, float(m_lo), u)
            if reg.is_empty:
                continue
            for (clr, x, y) in _candidates(reg)[:4]:
                co = cell_of(snap(x), snap(y), u)
                if not _exact_ok(co, boxes, polys):
                    continue
                sc = clr + rnd.random() * 1e-6
                if best is None or sc > best[0]:
                    best = (sc, co)
        if best is None:
            break
        cells.append(best[1])
        polys.append(V.poly_of(best[1]))
        fixed.append(fpoly(polys[-1]))
    return cells, polys


def search(obst, boxes, m_lo, need, restarts=6, wall=None, clock=None):
    """best of: the axis lattice fill (three orders x two pitches), each augmented with tilted
    leftovers, and the pure clearance greedy.  Returns (cells, k_found)."""
    best = None

    def keep(c):
        nonlocal best
        if best is None or len(c) > len(best):
            best = c
    for pitch in (Fr(1, 8), Fr(1, 16)):
        for order in ("bl", "lb", "tr"):
            if wall is not None and clock is not None and clock() > wall:
                return best, len(best or [])
            c, p = axis_fill(obst, boxes, m_lo, need, pitch=pitch, order=order)
            keep(list(c))
            c, p = augment(list(c), list(p), obst, boxes, m_lo, need, seed=hash(order) & 255)
            keep(c)
            if best is not None and len(best) >= need:
                return best, len(best)
    for r in range(restarts):
        if wall is not None and clock is not None and clock() > wall:
            break
        c, _p = greedy(obst, boxes, float(m_lo), need, seed=r)
        keep(c)
        if len(best) >= need:
            return best, len(best)
    for r in range(400):                                          # randomised lattice restarts
        if wall is not None and clock is not None and clock() > wall:
            break
        c, p = axis_fill(obst, boxes, m_lo, need, pitch=Fr(1, 4), order="bl", seed=r)
        if len(c) > len(best):
            keep(list(c))
            c, p = augment(list(c), list(p), obst, boxes, m_lo, need, seed=r)
            keep(c)
        if len(best) >= need:
            break
    return best, len(best or [])


def free_area(obst, m_lo):
    C = sbox(0.0, 0.0, float(m_lo), float(m_lo))
    return C.difference(unary_union(list(obst))).area if obst else C.area


def blocking(obst_named, m_lo):
    """the diagnostic the page draws: per obstacle, the area it takes out of the container."""
    C = sbox(0.0, 0.0, float(m_lo), float(m_lo))
    return {nm: round(g.intersection(C).area, 4) for nm, g in obst_named}


def eroded_capacity(obst, m_lo, u=Fr(0)):
    """a crude float read of how much room is left for further AXIS cells (drawing only)."""
    reg = cspace(list(obst), float(m_lo), u)
    return round(reg.area, 4) if not reg.is_empty else 0.0


def sanity():
    """the verifier's tests agree with a float SAT on random pairs (a smoke test, not a proof)."""
    rnd = random.Random(7)
    bad = 0
    for _ in range(300):
        u1, u2 = rnd.choice(US), rnd.choice(US)
        a = (snap(rnd.uniform(1, 3)), snap(rnd.uniform(1, 3)))
        b = (snap(rnd.uniform(1, 3)), snap(rnd.uniform(1, 3)))
        P, Q = verts(a[0], a[1], u1), verts(b[0], b[1], u2)
        ok, _ = V.polys_interior_disjoint(P, Q)
        inter = fpoly(P).intersection(fpoly(Q)).area
        if ok and inter > 1e-9:
            bad += 1
    return bad


if __name__ == "__main__":
    print("disjointness smoke test, contradictions:", sanity())
    print("math ok:", math.isclose(float(cs(Fr(5, 12))[0]) ** 2 + float(cs(Fr(5, 12))[1]) ** 2, 1.0))
