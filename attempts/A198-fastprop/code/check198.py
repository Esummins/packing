"""A198 -- an INDEPENDENT float cross-check of a fastprop kill of the kind "slot p has no free cell" (A1/FC): sample
poses of a unit square with centre in p's meeter window and any tilt, and look for one that (i) lies in the
container, (ii) meets the OPEN widened box, (iii) is interior-disjoint from every pin's exact core square and from
every role's certified K' polygon (a pose meeting int K'(role) meets the role's square at every pose of its box).
Finding one would REFUTE the kill (the exact tests are conservative, so a pose can meet H at some poses and not
others and still be admissible here -- the check is one-sided: a hit means a bug, no hit means consistent)."""
import math
import sys

import numpy as np

import fastprop as FP


def sq(cx, cy, th):
    c, s_ = math.cos(th), math.sin(th)
    return [(cx + 0.5 * (dx * c - dy * s_), cy + 0.5 * (dx * s_ + dy * c)) for dx, dy in [(-1, -1), (1, -1), (1, 1), (-1, 1)]]


def sat_gap(P, Q):
    axes = []
    for poly_ in (P, Q):
        m = len(poly_)
        for i in range(m):
            a, b = poly_[i], poly_[(i + 1) % m]
            ex, ey = b[0] - a[0], b[1] - a[1]
            n = math.hypot(ex, ey)
            if n > 0:
                axes.append((-ey / n, ex / n))
    best = -9
    for ax in axes:
        pp = [x * ax[0] + y * ax[1] for x, y in P]
        qq = [x * ax[0] + y * ax[1] for x, y in Q]
        best = max(best, min(qq) - max(pp), min(pp) - max(qq))
    return best


def check(nid, slot, n=300000, seed=1):
    rec, cls, row = FP.load_page(nid)
    T = FP.Trace()
    pg = FP.Page(rec, cls, nid, T, depth=3, joint_depth=1)
    pg.role_slots, pg.role_corner = {}, {}
    nd = pg.normalise("base")
    it = pg.item[slot]
    wb = [float(v) for v in it["wb"]]
    win = [float(v) for v in it["win"]]
    box_poly = [(wb[0], wb[2]), (wb[1], wb[2]), (wb[1], wb[3]), (wb[0], wb[3])]
    polys = {k: [(float(a), float(b)) for a, b in nd.boxes[k].pc.verts] for k in nd.names if nd.boxes[k].pc is not None and len(nd.boxes[k].pc.verts) >= 3}
    s = float(pg.s)
    rng = np.random.default_rng(seed)
    hits = 0
    best = None
    for _ in range(n):
        cx = rng.uniform(win[0], win[1])
        cy = rng.uniform(win[2], win[3])
        th = rng.uniform(0, math.pi / 2)
        P = sq(cx, cy, th)
        if not all(0 <= x <= s and 0 <= y <= s for x, y in P):
            continue
        if sat_gap(P, box_poly) >= 0:
            continue                                        # misses the open box
        worst = min(sat_gap(P, K) for K in polys.values())
        if best is None or worst > best[0]:
            best = (worst, cx, cy, math.degrees(th))
        if worst >= 0:
            hits += 1
            if hits <= 5:
                print("  REFUTING POSE: centre (%.4f, %.4f) tilt %.2f deg: disjoint from every K' (min gap %.4f), meets the box" % (cx, cy, math.degrees(th), worst))
    print("%s %s: %d samples, %d poses meeting the box and clear of every K' -> %s; closest miss: gap %s" % (
        nid, slot, n, hits, "REFUTED" if hits else "consistent with the kill", None if best is None else "%.4f at (%.3f, %.3f, %.1f deg)" % best))
    return hits


if __name__ == "__main__":
    check(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 300000)
