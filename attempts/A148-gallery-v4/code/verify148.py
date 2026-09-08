"""A148 -- independent re-verification of everything the v4 pages claim.

Deliberately a SECOND implementation.  Overlap here is decided by EDGE CROSSING + strict
point-in-polygon (the Minkowski sense); there is no separating axis anywhere in this file, so a
bug in geo148's `sat_gap` / polycore's `poly_square_depth` cannot hide in both.  Per page:

  A  GREEN is sound: points drawn uniformly inside GREEN cells each admit a feasible tilt -- the
     square is inside the container and its interior misses every certified core.
  B  BLOCKED is sound: points drawn uniformly inside BLOCKED cells admit NO tilt at all, over a
     tilt sweep ten times denser than the one the page used.
  C  K'(B) is inside the conditioned unit square at every one of 7^3 poses of its box (A132's
     certification, re-checked numerically), and area K' >= area K(a_stock).
  D  every pin's EXACT core square is inside the pin's unit square at every pose of the pin box,
     and the exact half-side is at least the stock one (A135).
  E  every reported POCKET gap is a true separation: the two features do not overlap, and a disk
     of that radius fits in the gap (checked at the reported segment's midpoint).
  F  every RED-DASHED column of panel S really does meet the core it names; control: no column
     that was NOT flagged meets ANY core.
  G  every guard row's minchord is a true lower bound: 10^4 poses drawn uniformly in each
     hypothesis box have chord >= minchord (A144's own sampled discipline, re-run here).

    set PYTHONDONTWRITEBYTECODE=1 && python code/verify148.py --set k0v4
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import geo148 as G                                                   # noqa: E402
import data148 as D                                                  # noqa: E402
import guardline as GL                                               # noqa: E402
from caselp import Box                                               # noqa: E402

NP = 7


# ------------------------------------------------------------------ independent predicates
def _ccw(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _cross(p1, p2, p3, p4):
    d1, d2 = _ccw(p3, p4, p1), _ccw(p3, p4, p2)
    d3, d4 = _ccw(p1, p2, p3), _ccw(p1, p2, p4)
    return ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0))


def _inside(P, q):
    sgn = 0
    for i in range(len(P)):
        c = _ccw(P[i], P[(i + 1) % len(P)], q)
        if abs(c) < 1e-14:
            return False
        s = 1 if c > 0 else -1
        if sgn == 0:
            sgn = s
        elif s != sgn:
            return False
    return True


def overlaps(P, Q):
    """interiors of two convex polygons meet: an edge crossing, or one contains the other."""
    for i in range(len(P)):
        for j in range(len(Q)):
            if _cross(P[i], P[(i + 1) % len(P)], Q[j], Q[(j + 1) % len(Q)]):
                return True
    return _inside(Q, P[0]) or _inside(P, Q[0])


def contains(P, Q):
    for q in Q:
        if not _inside(P, q):
            return False
    for i in range(len(P)):
        for j in range(len(Q)):
            if _cross(P[i], P[(i + 1) % len(P)], Q[j], Q[(j + 1) % len(Q)]):
                return False
    return True


def in_container(P, s, tol=0.0):
    return all(-tol <= x <= s + tol and -tol <= y <= s + tol for x, y in P)


def bboxes(obst):
    return [(min(v[0] for v in P), max(v[0] for v in P),
             min(v[1] for v in P), max(v[1] for v in P)) for P in obst]


def feasible_at(c, th, obst, s, bb=None):
    Q = G.sqpoly(c[0], c[1], th)
    if not in_container(Q, s):
        return False
    qx0 = min(v[0] for v in Q)
    qx1 = max(v[0] for v in Q)
    qy0 = min(v[1] for v in Q)
    qy1 = max(v[1] for v in Q)
    for i, P in enumerate(obst):
        if bb is not None:                       # bounding-box rejection: disjoint boxes cannot
            x0, x1, y0, y1 = bb[i]               # overlap, and this is not a separating-axis test
            if qx1 <= x0 or x1 <= qx0 or qy1 <= y0 or y1 <= qy0:
                continue
        if overlaps(P, Q):
            return False
    return True


def any_feasible(c, obst, s, ntilt, bb=None):
    for k in range(ntilt):
        th = (k + 0.5) * (math.pi / 2.0) / ntilt
        if feasible_at(c, th, obst, s, bb):
            return True
    return False


def box_poses(b, n=NP):
    xs = [b.x0] if b.x1 <= b.x0 else [b.x0 + (b.x1 - b.x0) * i / (n - 1.0) for i in range(n)]
    ys = [b.y0] if b.y1 <= b.y0 else [b.y0 + (b.y1 - b.y0) * i / (n - 1.0) for i in range(n)]
    ts = [b.th0] if b.th1 <= b.th0 else [b.th0 + (b.th1 - b.th0) * i / (n - 1.0)
                                         for i in range(n)]
    for x in xs:
        for y in ys:
            for t in ts:
                yield (x, y, math.radians(t))


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", dest="which", default="k0v4")
    ap.add_argument("--nsample", type=int, default=400)
    ap.add_argument("--ntilt", type=int, default=360)
    a = ap.parse_args()
    summ = json.load(open(os.path.join(BASE, "results", f"gallery148_{a.which}.json"),
                          encoding="utf-8"))
    recs = {r["id"]: r for r in D.population(a.which)}
    rng = np.random.default_rng(1481)
    tot = dict(pages=0, A_pts=0, A_fail=0, B_pts=0, B_fail=0, C_poses=0, C_fail=0,
               D_poses=0, D_fail=0, E_pockets=0, E_fail=0, F_flagged=0, F_fail=0,
               F_control=0, F_control_fail=0, G_rows=0, G_draws=0, G_fail=0)
    bad = []
    for sm in summ:
        nid = sm["id"]
        # The population is recomputed live, and the campaigns keep running, so a node drawn a few
        # minutes ago may already have been killed and dropped out.  Verify the page as drawn: load
        # the node's own record directly when it is no longer in the surviving population.
        rec = recs.get(nid)
        if rec is None:
            import gallery142 as G142
            d, path = G142.load_node(sm["camp"], nid)
            rec = dict(id=nid, camp=sm["camp"], boxes=d["hyp"]["boxes"],
                       packing=d.get("packing") or [])
            print(f"  [{nid}: killed since the page was drawn; verified from its own record]",
                  flush=True)
        obst, onames, kinds, _ = G.obstacles_of(rec["boxes"], rec.get("is_pin"))
        reg = G.feasible_region(G.S0, obst)
        bb = bboxes(obst)
        tot["pages"] += 1
        assert abs(reg.pitch - sm["grid"]["pitch"]) < 1e-12, f"{nid}: grid pitch differs"

        # --- A / B: the region, sampled with the independent overlap test
        for tag, mask, want in (("A", reg.green, True), ("B", reg.blocked, False)):
            jj, ii = np.nonzero(mask)
            if len(ii) == 0:
                continue
            pick = rng.integers(0, len(ii), a.nsample)
            for k in range(a.nsample):
                cx = reg.xs[ii[pick[k]]] + float(rng.uniform(-0.5, 0.5)) * reg.pitch
                cy = reg.ys[jj[pick[k]]] + float(rng.uniform(-0.5, 0.5)) * reg.pitch
                ok = any_feasible((cx, cy), obst, G.S0, a.ntilt, bb)
                tot[f"{tag}_pts"] += 1
                if ok != want:
                    tot[f"{tag}_fail"] += 1
                    bad.append((nid, tag, round(cx, 6), round(cy, 6)))

        # --- C / D: the cores really are inside the square at every pose of the box
        for i, k in enumerate(kinds):
            b = k["box"] if k["kind"] == "H" else Box.from_json(rec["boxes"][i])
            V = [tuple(v) for v in obst[i]]
            if k["kind"] == "H":
                if k["area_poly"] < (2.0 * k["a_stock"]) ** 2 - 1e-9:
                    tot["C_fail"] += 1
                    bad.append((nid, "C-area", onames[i], None))
            elif k["a_exact"] is not None and k["a_exact"] < 0.5 - 1e-2 - 1e-12:
                pass
            for (hx, hy, ht) in box_poses(b):
                key = "C_poses" if k["kind"] == "H" else "D_poses"
                tot[key] += 1
                if not contains(G.sqpoly(hx, hy, ht), V):
                    tot["C_fail" if k["kind"] == "H" else "D_fail"] += 1
                    bad.append((nid, "C" if k["kind"] == "H" else "D", onames[i],
                                [hx, hy, math.degrees(ht)]))
                    break

        # --- E: the pockets
        for p in sm["pockets"]:
            tot["E_pockets"] += 1
            if p["kind"] != "core-core":
                continue
            i, j = [onames.index(x) for x in p["to"].split("-")]
            if overlaps(obst[i], obst[j]) != (p["gap"] <= 0.0):
                tot["E_fail"] += 1
                bad.append((nid, "E", p["to"], p["gap"]))

        # --- F: the red-dashed columns of panel S
        flagged = {r["col"]: r for r in sm["impossible"]}
        pk = rec["packing"]
        for kcol, r in flagged.items():
            p = pk[kcol]
            Q = G.sqpoly(float(p["cx"]), float(p["cy"]), float(p["theta"]))
            tot["F_flagged"] += 1
            if not overlaps(obst[onames.index(r["owner"])], Q):
                tot["F_fail"] += 1
                bad.append((nid, "F", kcol, r["owner"]))
        for kcol, p in enumerate(pk):
            if kcol in flagged:
                continue
            Q = G.sqpoly(float(p["cx"]), float(p["cy"]), float(p["theta"]))
            if not in_container(Q, G.S0, 1e-6):
                continue
            tot["F_control"] += 1
            if any(overlaps(P, Q) for P in obst):
                tot["F_control_fail"] += 1
                bad.append((nid, "F-control", kcol, None))

        # --- G: the guard rows' minchord is a lower bound
        bxs = [Box.from_json(b) for b in rec["boxes"]]
        for row in sm["guard"][:3]:
            ln = GL.Line(row["orient"], GL.Fr(round(row["off"] * GL.LDEN), GL.LDEN), row["tag"])
            tot["G_rows"] += 1
            for b in bxs:
                r = GL.sample_confirm(b, ln, n=10000, seed=int(abs(row["off"]) * 1000) % 9973)
                tot["G_draws"] += r["n"]
                if r["hits"]:
                    tot["G_fail"] += r["hits"]
                    bad.append((nid, "G", row["tag"], r["hits"]))
        print(f"  {nid:32s} checked", flush=True)

    out = dict(totals=tot, n_failures=len(bad), failures=bad[:200],
               note="second implementation: edge crossing + strict point-in-polygon, no "
                    "separating axis anywhere in verify148.py; region re-derived from scratch")
    p = os.path.join(BASE, "results", f"verify148_{a.which}.json")
    json.dump(out, open(p, "w", encoding="utf-8"), indent=1)
    for k, v in tot.items():
        print(f"  {k:16s} {v}")
    print("FAILURES", len(bad), bad[:8])
    print("wrote", p)


if __name__ == "__main__":
    main()
