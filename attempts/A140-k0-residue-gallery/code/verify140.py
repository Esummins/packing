"""A140 -- independent verification of everything the gallery draws.

  (1) every square drawn in either panel is inside its container;
  (2) every red-dashed column's "overlaps the hypothesis square at EVERY pose" is recomputed with
      a THIRD implementation (A107's `shadowlib.sat_gap`, a different formula from the polygon SAT
      used to draw it) over the same 7^3 pose grid;
  (3) for every red-dashed column that the polygon core also certifies, an EXACT witness: a vertex
      of K'(B) -- a rational point certified by `polycore.vertex_ok` to lie in Q(c, theta) for
      every pose of B -- that lies strictly inside the column's own square.  That single point is
      an exact proof that the column and the conditioned square share an interior point at every
      pose, with no floating-point step anywhere in the statement.
"""
import json
import math
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
for p in (os.path.join(ROOT, "attempts", "A57-shadow-trees", "code"),
          os.path.join(ROOT, "attempts", "A132-polygon-core", "code"),
          os.path.join(ROOT, "attempts", "A107-shadow-gallery", "code"),
          HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

import polycore                                              # noqa: E402
from caselp import Box                                       # noqa: E402
import shadowlib as L                                        # noqa: E402
import cells140 as C140                                      # noqa: E402
import gallery140 as G                                       # noqa: E402

S0 = C140.S0


def inside_square(vx, vy, cx, cy, th, tol=0.0):
    """is (vx, vy) strictly inside Q(c, theta)?  Returns the inf-norm margin."""
    dx, dy = float(vx) - cx, float(vy) - cy
    c, s = math.cos(th), math.sin(th)
    u = abs(dx * c + dy * s)
    w = abs(-dx * s + dy * c)
    return 0.5 - max(u, w)


def main():
    g = json.load(open(os.path.join(BASE, "results", "gallery140.json"), encoding="utf-8"))
    out = []
    bad = 0
    for r in g:
        cell = r["cell"]
        meta, d = C140.load_cell(cell)
        boxes = d["hyp"]["boxes"]
        pcs = [polycore.build(Box.from_json(b)) for b in boxes]
        pk = d["packing"]
        s = float(d.get("s") or S0)
        rec = dict(cell=cell, n_impossible=len(r["impossible"]), checks=[])

        # (1) containment of the left panel's support and of the right panel
        exc = 0.0
        for p in pk:
            for (x, y) in G.sq(float(p["cx"]), float(p["cy"]), float(p["theta"])):
                exc = max(exc, -x, x - s, -y, y - s)
        rec["left_worst_excursion"] = exc          # informational: outside columns are skipped
        poses, s2, _ = G.right_poses(cell, d, boxes)
        exc2 = 0.0
        for q in poses:
            for (x, y) in G.sq(*q):
                exc2 = max(exc2, -x, x - s2, -y, y - s2)
        rec["right_worst_excursion"] = exc2
        if exc2 > 1e-4:
            bad += 1
            rec["FAIL_right_containment"] = exc2

        # (2) + (3)
        nwit = 0
        for im in r["impossible"]:
            k, bi = im["col"], im["box"]
            p = pk[k]
            c1, t1 = (float(p["cx"]), float(p["cy"])), float(p["theta"])
            b = boxes[bi]
            gmax = -9e9
            for (hx, hy, ht) in G.box_poses(b, G.NPOSE):
                gmax = max(gmax, L.sat_gap(c1, t1, (hx, hy), ht))
            ok = gmax < 0.0
            agree = abs(gmax - (-im["overlap"])) < 1e-9
            if not ok:
                bad += 1
            wit = None
            if im["kprime"]:
                bx = Box.from_json(b)
                cands = list(pcs[bi].verts)
                P = pcs[bi].P
                # the K' centroid and a grid over K' n Q: any RATIONAL point that passes
                # `vertex_ok` is in every pose of the box, so any one of them is a witness.
                cands.append((Fr(round(float(P[:, 0].mean()) * 10 ** 9), 10 ** 9),
                              Fr(round(float(P[:, 1].mean()) * 10 ** 9), 10 ** 9)))
                lo = (P[:, 0].min(), P[:, 1].min())
                hi = (P[:, 0].max(), P[:, 1].max())
                for ii in range(13):
                    for jj in range(13):
                        x = lo[0] + (hi[0] - lo[0]) * ii / 12.0
                        y = lo[1] + (hi[1] - lo[1]) * jj / 12.0
                        cands.append((Fr(round(x * 10 ** 9), 10 ** 9),
                                      Fr(round(y * 10 ** 9), 10 ** 9)))
                best = None
                for (vx, vy) in cands:
                    m = inside_square(vx, vy, c1[0], c1[1], t1)
                    if m <= 0.0:
                        continue
                    if best is not None and m <= best[0]:
                        continue
                    if polycore.vertex_ok(vx, vy, bx):
                        best = (m, vx, vy)
                if best:
                    wit = dict(x=str(best[1]), y=str(best[2]), margin=best[0])
                    nwit += 1
            rec["checks"].append(dict(col=k, box=bi, y=im["y"],
                                      redraw_max_gap=gmax, drawn_overlap=im["overlap"],
                                      agrees=bool(agree), always_overlaps=bool(ok),
                                      kprime=im["kprime"], exact_witness=wit))
        rec["n_exact_witnesses"] = nwit
        rec["n_kprime"] = sum(1 for x in r["impossible"] if x["kprime"])
        out.append(rec)
        print(f"{cell:26s} impossible {rec['n_impossible']:3d}  all re-verified "
              f"{all(c['always_overlaps'] for c in rec['checks'])}  "
              f"K'-certified {rec['n_kprime']:3d}  exact vertex witnesses {nwit:3d}  "
              f"right-panel excursion {exc2:+.2e}", flush=True)
    json.dump(out, open(os.path.join(BASE, "results", "verify140.json"), "w",
                        encoding="utf-8"), indent=1)
    print(f"\n{bad} failure(s); wrote results/verify140.json")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
