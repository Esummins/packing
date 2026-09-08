"""A142 -- independent re-verification of everything the gallery draws.

Deliberately a SECOND implementation: overlap is decided by edge-crossing + point-in-polygon on
the Minkowski sense (no separating axis anywhere in this file), so a bug in `sat_poly` cannot hide
in both.  Per page it checks

  A  every RED-DASHED column really does overlap its owning hypothesis square at all 7^3 poses of
     that square's box (that is the claim the red dash makes);
  B  a control: for every column NOT red-dashed there exists a pose of every box at which it is
     disjoint (the dash is not being handed out for free);
  C  each pin's EXACT core square sits inside the pin's unit square at all 7^3 poses of the pin
     box (A135's certification, re-checked numerically), and the exact half-side is >= the stock;
  D  every vertex of K'(B) sits inside the conditioned unit square at all 7^3 poses of B (A132's
     certification, re-checked numerically), and area K' >= area K(a_stock);
  E  the pin-clipped rects are sub-rects of the original centre box.

    set PYTHONDONTWRITEBYTECODE=1 && python code/verify142.py
"""
import glob
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import gallery142 as G                                        # noqa: E402

NP = 7


def _ccw(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _cross(p1, p2, p3, p4):
    d1, d2 = _ccw(p3, p4, p1), _ccw(p3, p4, p2)
    d3, d4 = _ccw(p1, p2, p3), _ccw(p1, p2, p4)
    return ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0))


def _inside(P, q):
    """q strictly inside the convex, ccw-or-cw polygon P."""
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
    """True iff the interiors of two convex polygons meet.  Edge crossing OR containment."""
    for i in range(len(P)):
        for j in range(len(Q)):
            if _cross(P[i], P[(i + 1) % len(P)], Q[j], Q[(j + 1) % len(Q)]):
                return True
    return _inside(Q, P[0]) or _inside(P, Q[0])


def contains(P, Q):
    """every vertex of Q inside P, and no edge of Q crosses an edge of P."""
    for q in Q:
        if not _inside(P, q):
            return False
    for i in range(len(P)):
        for j in range(len(Q)):
            if _cross(P[i], P[(i + 1) % len(P)], Q[j], Q[(j + 1) % len(Q)]):
                return False
    return True


def main():
    files = sorted(glob.glob(os.path.join(BASE, "results", "gallery142_*.json")))
    tot = dict(pages=0, A_cols=0, A_poses=0, A_fail=0, B_cols=0, B_fail=0,
               C_pins=0, C_poses=0, C_fail=0, D_verts=0, D_poses=0, D_fail=0,
               E_rects=0, E_fail=0)
    bad = []
    for f in files:
        camp = os.path.basename(f).split("_")[1]
        for sm in json.load(open(f, encoding="utf-8"))["summary"]:
            nid = sm["id"]
            d, _ = G.load_node(camp, nid)
            boxes = d["hyp"]["boxes"]
            npin = len(boxes) - 1
            tot["pages"] += 1
            pk = d.get("packing", [])

            # --- A: the red-dashed claim
            flagged = {r["col"]: r for r in sm["impossible"]}
            for k, r in flagged.items():
                p = pk[k]
                P = G.sq(float(p["cx"]), float(p["cy"]), float(p["theta"]))
                b = boxes[r["box"]]
                tot["A_cols"] += 1
                for (hx, hy, ht) in G.box_poses(b, NP):
                    tot["A_poses"] += 1
                    if not overlaps(P, G.sq(hx, hy, ht)):
                        tot["A_fail"] += 1
                        bad.append((nid, "A", k, r["box"]))
                        break

            # --- B: control on the columns that were NOT flagged
            for k, p in enumerate(pk):
                if k in flagged:
                    continue
                P = G.sq(float(p["cx"]), float(p["cy"]), float(p["theta"]))
                if not all(-1e-6 <= x <= sm.get("side", G.S0) + 1e-6 for x, _ in P):
                    pass
                tot["B_cols"] += 1
                ok = True
                for j, b in enumerate(boxes):
                    if not any(not overlaps(P, G.sq(hx, hy, ht))
                               for (hx, hy, ht) in G.box_poses(b, NP)):
                        ok = False
                        break
                if not ok:
                    tot["B_fail"] += 1
                    bad.append((nid, "B", k, j))

            # --- C: the exact pin cores
            for i in range(npin):
                if not sm["pin_is_pin"][i]:
                    continue                       # a hypothesis box with a tilt window is not
                    # a pin: it is a further conditioned square, drawn cyan and checked as such
                b = boxes[i]
                cx, cy = 0.5 * (b["x0"] + b["x1"]), 0.5 * (b["y0"] + b["y1"])
                K = G.sq(cx, cy, 0.0, sm["pincore_as"][i])
                tot["C_pins"] += 1
                if sm["pincore_as"][i] < sm["pincore_a_stock"] - 1e-15:
                    tot["C_fail"] += 1
                    bad.append((nid, "C-shrunk", i, None))
                for (hx, hy, ht) in G.box_poses(b, NP):
                    tot["C_poses"] += 1
                    if not contains(G.sq(hx, hy, ht), K):
                        tot["C_fail"] += 1
                        bad.append((nid, "C", i, None))
                        break

            # --- D: K'(B)
            from caselp import Box
            import polycore
            pc = polycore.build(Box.from_json(boxes[-1]))
            V = [tuple(v) for v in pc.P]
            if pc.area() < (2.0 * sm["a_stock"]) ** 2 - 1e-12:
                tot["D_fail"] += 1
                bad.append((nid, "D-area", None, None))
            for (hx, hy, ht) in G.box_poses(boxes[-1], NP):
                tot["D_poses"] += 1
                if not contains(G.sq(hx, hy, ht), V):
                    tot["D_fail"] += 1
                    bad.append((nid, "D", None, None))
                    break
            tot["D_verts"] += len(V)

            # --- E: the clip
            b = boxes[-1]
            for (t0, t1, r) in sm["clip_bins"]:
                if r is None:
                    continue
                tot["E_rects"] += 1
                # pinclip.outer_rect rounds the box OUTWARD onto the 1/XDEN = 1e-9 grid (an outer
                # approximation, sound by construction), so the tolerance here is 3 grid steps.
                if not (r[0] >= b["x0"] - 3e-9 and r[1] <= b["x1"] + 3e-9
                        and r[2] >= b["y0"] - 3e-9 and r[3] <= b["y1"] + 3e-9):
                    tot["E_fail"] += 1
                    bad.append((nid, "E", t0, t1))

    out = dict(totals=tot, failures=bad[:200], n_failures=len(bad),
               note="second implementation: edge-crossing + strict point-in-polygon, no "
                    "separating axis anywhere in verify142.py")
    p = os.path.join(BASE, "results", "verify142.json")
    json.dump(out, open(p, "w", encoding="utf-8"), indent=1)
    for k, v in tot.items():
        print(f"  {k:10s} {v}")
    print("FAILURES", len(bad), bad[:10])
    print("wrote", p)


if __name__ == "__main__":
    main()
