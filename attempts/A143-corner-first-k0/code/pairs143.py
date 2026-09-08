"""A143 T1b -- the DOUBLY-MET corner-first cover: both BL meeters carried in the hypothesis.

K0-BLOCKED gives, at BL, two DISTINCT squares Q1, Q2 with poses in R_BL (k0_route.md sec 4.2,
Lemma K0-BLOCKED).  The level-1 pair cover is the set of unordered pairs {A, B} of level-1 cells
(A = B allowed: the two meeters may share a cell), quotiented by the BL stabiliser {id, transpose}
acting on the unordered pair.

Geometric leaves, all sound over-approximations, in cost order:

  (P0) container + reach clip of each cell (cells143);
  (P2) max centre distance over the two clipped boxes < 1  ==>  the two squares overlap  ==>  (C);
  (P1) K'(A) meets K'(B)  ==>  EVERY square realising A overlaps EVERY square realising B  ==> (C)
       (A132 polygon cores; strictly stronger than the axis-core `cores_meet`);
  (P1s) A131's per-tilt-sub-bin refinement: subdivide B's tilt window into NSUB bins, clip each
       sub-bin against the container, and test K'(A) against K'(B_sub).  If EVERY surviving sub-bin
       is contradictory the pair cell is empty even when the whole-window test is not.

Survivors then go to the K' LANE test on all four corners with M = the number of conditioned
squares that can meet the corner (2 at BL, so BL can never kill in the pair root -- the kill moves
to BR / TR / TL).

    python code/pairs143.py --stage geom
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

import blas1                                                    # noqa: F401,E402
import numpy as np                                              # noqa: E402
import polycore                                                 # noqa: E402
import lane as LANE                                             # noqa: E402
from caselp import Box                                          # noqa: E402
import cells143 as C                                            # noqa: E402

CORNERS = ["BR(0,0)", "TR(0,0)", "TL(0,0)", "BL(0,0)"]
MAXV = 16
NSUB_PAIR = 4


def cell_key(c):
    return (c.ix, c.iy, c.it)


def transpose_key(k):
    return (k[1], k[0], C.NTILT - 1 - k[2])


def pair_canonical(k1, k2):
    """canonical representative of the unordered pair under the BL transpose."""
    a = tuple(sorted((k1, k2)))
    b = tuple(sorted((transpose_key(k1), transpose_key(k2))))
    return min(a, b)


def max_centre_dist(b1, b2):
    dx = max(abs(b1.x1 - b2.x0), abs(b2.x1 - b1.x0))
    dy = max(abs(b1.y1 - b2.y0), abs(b2.y1 - b1.y0))
    return (dx * dx + dy * dy) ** 0.5


def build_cores(cells):
    K, KS = {}, {}
    for c in cells:
        if c.empty:
            continue
        K[cell_key(c)] = polycore.build(c.box, max_v=MAXV)
        subs = []
        for (a, b, cl) in C.subbin_clip(*c.raw, nsub=NSUB_PAIR):
            bx = Box(cl[0], cl[1], cl[2], cl[3], a, b)
            try:
                subs.append((bx, polycore.build(bx, max_v=MAXV)))
            except Exception:                                   # noqa: BLE001
                subs.append((bx, None))
        KS[cell_key(c)] = subs
    return K, KS


def geom_stage(out):
    cells = [c for c in C.all_cells() if not c.empty]
    byk = {cell_key(c): c for c in cells}
    t0 = time.time()
    K, KS = build_cores(cells)
    print(f"polygon cores built for {len(K)} cells ({sum(len(v) for v in KS.values())} sub-bins) "
          f"in {time.time()-t0:.0f} s", flush=True)

    keys = sorted(byk)
    seen = set()
    rows = []
    n_all = 0
    stats = dict(total=0, canonical=0, P2=0, P1=0, P1s=0, alive=0)
    for i, k1 in enumerate(keys):
        for k2 in keys[i:]:
            n_all += 1
            cc = pair_canonical(k1, k2)
            if cc in seen:
                continue
            seen.add(cc)
            stats["canonical"] += 1
            a, b = cc
            b1, b2 = byk[a].box, byk[b].box
            if max_centre_dist(b1, b2) < 1.0:
                stats["P2"] += 1
                rows.append(dict(pair=[list(a), list(b)], verdict="P2-CENTRE-DIST"))
                continue
            if polycore.poly_poly_depth(K[a].P, K[b].P) > 0.0:
                stats["P1"] += 1
                rows.append(dict(pair=[list(a), list(b)], verdict="P1-CORES-MEET"))
                continue
            # per-sub-bin refinement on BOTH members
            alive_sub = 0
            for (_bx1, p1) in KS[a]:
                if p1 is None:
                    alive_sub += 1
                    continue
                for (_bx2, p2) in KS[b]:
                    if p2 is None:
                        alive_sub += 1
                        continue
                    if polycore.poly_poly_depth(p1.P, p2.P) <= 0.0:
                        alive_sub += 1
            if alive_sub == 0:
                stats["P1s"] += 1
                rows.append(dict(pair=[list(a), list(b)], verdict="P1s-SUBBIN"))
                continue
            stats["alive"] += 1
            rows.append(dict(pair=[list(a), list(b)], verdict="ALIVE-CORE",
                             n_alive_subpairs=alive_sub))
    stats["total"] = n_all
    print(json.dumps(stats), flush=True)
    with open(out, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    json.dump(stats, open(out.replace(".jsonl", ".stats.json"), "w"), indent=1)
    print(f"wrote {out} ({len(rows)} rows) in {time.time()-t0:.0f} s", flush=True)


def lane_rec(b1, b2):
    return dict(src="A143", nid="pair", cls="k0_00", level=1,
                cond=[dict(x0=b.x0, x1=b.x1, y0=b.y0, y1=b.y1, th0=b.th0, th1=b.th1)
                      for b in (b1, b2)])


def lane_stage(inp, out, limit=0, seed=1430, shard=0, nshards=1):
    byk = {cell_key(c): c for c in C.all_cells() if not c.empty}
    rows = [json.loads(l) for l in open(inp, encoding="utf-8")]
    alive = [r for r in rows if r["verdict"] == "ALIVE-CORE"]
    rng0 = np.random.default_rng(seed)
    if limit and len(alive) > limit:
        idx = rng0.choice(len(alive), size=limit, replace=False)
        sample = [alive[i] for i in sorted(idx)]
        frame = dict(sampled=True, n_alive=len(alive), n_sample=limit, seed=seed)
    else:
        sample = alive
        frame = dict(sampled=False, n_alive=len(alive), n_sample=len(alive))
    sample = [x for i, x in enumerate(sample) if i % nshards == shard]
    print(f"lane stage shard {shard}/{nshards}: {len(sample)} pairs  {frame}", flush=True)
    done = set()
    if os.path.exists(out):
        for ln in open(out, encoding="utf-8"):
            try:
                done.add(json.loads(ln)["key"])
            except Exception:                                   # noqa: BLE001
                pass
    fh = open(out, "a", encoding="utf-8")
    t0 = time.time()
    for r in sample:
        a, b = tuple(r["pair"][0]), tuple(r["pair"][1])
        key = "%d%d_t%d__%d%d_t%d" % (a[0], a[1], a[2], b[0], b[1], b[2])
        if key in done:
            continue
        rec = dict(key=key, pair=r["pair"])
        rc = lane_rec(byk[a].box, byk[b].box)
        rng = np.random.default_rng(abs(hash(key)) % (2 ** 31))
        lanes, kill_at = {}, None
        for cn in CORNERS:
            try:
                v = LANE.run_cell(rc, cn, rng, rigorous=True)
            except Exception as e:                              # noqa: BLE001
                v = dict(verdict="ERROR", error=repr(e)[:160])
            lanes[cn] = {kk: v.get(kk) for kk in
                         ("verdict", "lane_ub", "ncond_pot", "kill")}
            if v.get("kill"):
                kill_at = cn
                break
        rec["lanes"] = lanes
        rec["verdict"] = ("LANE-KILL:" + kill_at) if kill_at else "ALIVE-GEOM"
        fh.write(json.dumps(rec) + "\n"); fh.flush()
    fh.close()
    json.dump(frame, open(out.replace(".jsonl", ".frame.json"), "w"), indent=1)
    print("lane stage done in %.0f s" % (time.time() - t0), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="geom", choices=("geom", "lane"))
    ap.add_argument("--inp", default=os.path.join(BASE, "results", "pairs143_geom.jsonl"))
    ap.add_argument("--out", default=None)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--nshards", type=int, default=1)
    a = ap.parse_args()
    if a.stage == "geom":
        geom_stage(a.out or os.path.join(BASE, "results", "pairs143_geom.jsonl"))
    else:
        lane_stage(a.inp, a.out or os.path.join(BASE, "results",
                                                f"pairs143_lane_s{a.shard}.jsonl"),
                   limit=a.limit, shard=a.shard, nshards=a.nshards)


if __name__ == "__main__":
    main()
