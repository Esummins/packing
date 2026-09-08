"""A143 T1 -- the geometric leaves of the corner-first level-1 cover, applied BEFORE any LP.

  (a) CONTAINER CLIP (walls as pins, A131's mechanism).  Per tilt sub-bin: c_i in [h(th),
      s0 - h(th)] and c_i <= a_w + h(th).  cells143.clip_box / subbin_clip.
  (b) POLYGON CORE vs WALLS.  K'(B) = intersection over the box of Q(c, th) (A132, certified
      vertex-by-vertex in exact rationals).  Every admissible pose has K'(B) subset Q subset
      [0, s0]^2, so a K' vertex outside the container empties the cell (a (C) leaf).
  (c) K' LANE TEST on all four corners INCLUDING BL's own (A118 `lane.run_cell`, unchanged and
      read-only).  LANE(C) = max number of pairwise interior-disjoint unit squares whose poses
      meet the corner cell C, lie in the container and avoid the conditioned core; M = the number
      of conditioned squares that can meet C.  LANE + M <= 1  ==>  C is met by <= 1 square  ==>
      K0-FREE (`teleport_packing`)  ==>  dead.  At BL, M = 1 by construction, so the kill is
      LANE(BL) = 0: no OTHER square can meet BL past the conditioned square's core.

    python code/geom143.py [--canon] [--corners BL,BR,TR,TL] [--cells N]
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
A118 = os.path.join(ROOT, "attempts", "A118-lane-count", "code")
_A57 = os.path.join(ROOT, "attempts", "A57-shadow-trees", "code")
_A132 = os.path.join(ROOT, "attempts", "A132-polygon-core", "code")
_A135 = os.path.join(ROOT, "attempts", "A135-polycore-verifier", "code")
for _p in (A118, _A57, _A132, _A135, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import blas1                                            # noqa: F401,E402  (must precede numpy)
import numpy as np                                      # noqa: E402
import lane as LANE                                     # noqa: E402
import polycore                                         # noqa: E402
import cells143 as C                                    # noqa: E402

CORNERS = ["BL(0,0)", "BR(0,0)", "TR(0,0)", "TL(0,0)"]
MAXV = 16                       # A132: a 16-gon is within 5e-4 of K' in area, 2.5x cheaper


def poly_wall_verdict(box, s=C.S0):
    """(certified, n_vertices, area, outside) -- `outside` True means a certified K' vertex lies
    outside [0, s]^2, so no pose of the box is admissible (a (C) leaf)."""
    try:
        pc = polycore.build(box, max_v=MAXV)
    except Exception as e:                              # noqa: BLE001
        return dict(certified=False, err=repr(e)[:120])
    out = []
    for (vx, vy) in pc.verts:
        if vx < 0 or vy < 0 or vx > C.S0_RAT_F or vy > C.S0_RAT_F:
            out.append([str(vx), str(vy)])
    return dict(certified=bool(pc.certified), nv=len(pc.verts), area=pc.area(),
                outside=len(out) > 0, outside_verts=out[:3],
                margin=min(min(float(vx), float(vy),
                               C.S0_RAT_F - float(vx), C.S0_RAT_F - float(vy))
                           for (vx, vy) in pc.verts))


def lane_rec(cell):
    b = cell.box
    return dict(src="A143", nid=cell.name, cls="k0_00", level=1,
                cond=[dict(x0=b.x0, x1=b.x1, y0=b.y0, y1=b.y1, th0=b.th0, th1=b.th1)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--canon", action="store_true", help="D4_BL-canonical cells only")
    ap.add_argument("--corners", default=";".join(CORNERS))
    ap.add_argument("--cells", type=int, default=0)
    ap.add_argument("--out", default=os.path.join(BASE, "results", "geom143.jsonl"))
    a = ap.parse_args()
    corners = a.corners.split(";")

    cells = C.all_cells()
    if a.canon:
        cells = [c for c in cells if c.canon]
    if a.cells:
        cells = cells[:a.cells]
    done = set()
    if os.path.exists(a.out):
        for ln in open(a.out, encoding="utf-8"):
            try:
                done.add(json.loads(ln)["cell"])
            except Exception:                           # noqa: BLE001
                pass
    print(f"A143 geometry: {len(cells)} cells, corners {corners}, done {len(done)}", flush=True)
    fh = open(a.out, "a", encoding="utf-8")
    t00 = time.time()
    for cell in cells:
        if cell.name in done:
            continue
        rec = dict(cell=cell.name, ix=cell.ix, iy=cell.iy, it=cell.it, canon=bool(cell.canon),
                   raw=list(cell.raw))
        if cell.empty:
            rec.update(verdict="CLIP-EMPTY", clip=None)
            fh.write(json.dumps(rec) + "\n"); fh.flush()
            continue
        b = cell.box
        rec["clip"] = b.to_json()
        rec["clip_area_ratio"] = ((b.x1 - b.x0) * (b.y1 - b.y0)) / \
            ((cell.raw[1] - cell.raw[0]) * (cell.raw[3] - cell.raw[2]))
        rec["n_subbins"] = len(cell.subbins)
        t0 = time.time()
        rec["poly"] = poly_wall_verdict(b)
        k = b.core()
        rec["core_a"] = float(k.a) if k else None
        rec["poly_over_axis"] = (rec["poly"].get("area") / (2 * float(k.a)) ** 2) if k else None
        if rec["poly"].get("outside"):
            rec.update(verdict="POLY-WALL", secs=round(time.time() - t0, 2))
            fh.write(json.dumps(rec) + "\n"); fh.flush()
            print(f"{cell.name} POLY-WALL", flush=True)
            continue
        r = lane_rec(cell)
        rng = np.random.default_rng(143 + 7 * cell.ix + 31 * cell.iy + 101 * cell.it)
        lanes = {}
        kill_at = None
        for cn in corners:
            try:
                v = LANE.run_cell(r, cn, rng, rigorous=True)
            except Exception as e:                      # noqa: BLE001
                v = dict(verdict="ERROR", error=repr(e)[:160])
            lanes[cn] = {kk: v.get(kk) for kk in
                         ("verdict", "lane_ub", "lane_lb", "ncond_pot", "kill", "secs")}
            if v.get("kill"):
                kill_at = cn
                break
        rec["lanes"] = lanes
        rec["verdict"] = ("LANE-KILL:" + kill_at) if kill_at else "ALIVE-GEOM"
        rec["secs"] = round(time.time() - t0, 2)
        fh.write(json.dumps(rec) + "\n"); fh.flush()
        print(f"{cell.name:12s} {rec['verdict']:18s} "
              + " ".join(f"{c[:2]}={lanes[c]['verdict']}" for c in lanes)
              + f"  {rec['secs']}s", flush=True)
    fh.close()
    print("geom143 done in %.0f s" % (time.time() - t00), flush=True)


if __name__ == "__main__":
    main()
