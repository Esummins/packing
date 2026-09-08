"""A143 -- the K' LANE test (A141's `polylane`, imported unchanged and read-only) on the
corner-first cells.

A118's lane leaf makes a free square avoid the AXIS core K(a) of each conditioned box; A141's makes
it avoid the whole polygon core K'(B), and discharges each cover box by a single EXACT rational
point shared with a conditioned box.  On the corner-first root that is exactly where a kill could
come from: at BL the conditioned square already counts (M = 1 in the single root), so the kill needs
LANE(BL) = 0 -- "no OTHER square can meet BL past the conditioned K'" -- and A118's weaker core left
20 of 216 cells at LANE(BL) <= 1.

    python code/polylane143.py --mode single [--cells N] [--corners BL,BR,TR,TL]
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
A141 = os.path.join(ROOT, "attempts", "A141-polycore-lane", "code")
A118 = os.path.join(ROOT, "attempts", "A118-lane-count", "code")
_A57 = os.path.join(ROOT, "attempts", "A57-shadow-trees", "code")
_A132 = os.path.join(ROOT, "attempts", "A132-polygon-core", "code")
for _p in (A141, A118, _A57, _A132, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import blas1                                                    # noqa: F401,E402
import numpy as np                                              # noqa: E402
import polylane as PL                                           # noqa: E402
import cells143 as C                                            # noqa: E402
import pairs143 as P                                            # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="single", choices=("single", "pair"))
    ap.add_argument("--corners", default="BL;BR;TR;TL")
    ap.add_argument("--cells", type=int, default=0)
    ap.add_argument("--canon", action="store_true")
    ap.add_argument("--out", default=None)
    ap.add_argument("--sample", type=int, default=8000)
    a = ap.parse_args()
    corners = a.corners.split(";")
    out = a.out or os.path.join(BASE, "results", f"polylane143_{a.mode}.jsonl")
    print(f"A141 widened corner box w0 = {PL.W0:.8f}  (A143 a_w = {C.A_W:.8f})", flush=True)

    byk = {P.cell_key(c): c for c in C.all_cells() if not c.empty}
    if a.mode == "single":
        jobs = [(c.name, [c.box]) for c in C.all_cells() if not c.empty
                and (c.canon or not a.canon)]
    else:
        rows = [json.loads(l) for l in
                open(os.path.join(BASE, "results", "pairs143_geom.jsonl"), encoding="utf-8")]
        alive = [r for r in rows if r["verdict"] == "ALIVE-CORE"]
        jobs = []
        for r in alive:
            k1, k2 = tuple(r["pair"][0]), tuple(r["pair"][1])
            jobs.append(("p_%d%d%d__%d%d%d" % (k1 + k2), [byk[k1].box, byk[k2].box]))
    if a.cells:
        jobs = jobs[:a.cells]
    done = set()
    if os.path.exists(out):
        for ln in open(out, encoding="utf-8"):
            try:
                done.add(json.loads(ln)["cell"])
            except Exception:                                   # noqa: BLE001
                pass
    print(f"{len(jobs)} jobs, corners {corners}, done {len(done)} -> {out}", flush=True)
    fh = open(out, "a", encoding="utf-8")
    t00 = time.time()
    nkill = 0
    for (name, boxes) in jobs:
        if name in done:
            continue
        t0 = time.time()
        rec = dict(cell=name, n_boxes=len(boxes))
        try:
            conds = PL.build_cond(boxes)
        except Exception as e:                                  # noqa: BLE001
            rec.update(error=repr(e)[:200])
            fh.write(json.dumps(rec) + "\n"); fh.flush()
            continue
        res = {}
        kill_at = None
        for cn in corners:
            try:
                r = PL.lane_corner(cn, conds, rng=np.random.default_rng(abs(hash(name + cn))
                                                                       % (2 ** 31)),
                                   keep_cert=False, sample=a.sample)
            except Exception as e:                              # noqa: BLE001
                r = dict(verdict="ERROR", error=repr(e)[:200])
            res[cn] = {k: r.get(k) for k in ("verdict", "lane_ub", "lane_lb", "M", "M_lb",
                                             "meeters", "cover_leaves", "cover_open")}
            if r.get("verdict") == "KILL":
                kill_at = cn
                break
        rec["lanes"] = res
        rec["verdict"] = ("KILL:" + kill_at) if kill_at else "ALIVE"
        rec["secs"] = round(time.time() - t0, 2)
        nkill += bool(kill_at)
        fh.write(json.dumps(rec) + "\n"); fh.flush()
        print(f"{name:24s} {rec['verdict']:12s} " +
              " ".join(f"{c}={res[c]['verdict']}/ub={res[c]['lane_ub']}/M={res[c].get('M') if res[c].get('M') is not None else res[c].get('M_lb')}"
                       for c in res) + f"  {rec['secs']}s", flush=True)
    fh.close()
    print(f"polylane143 {a.mode} done: {nkill} kills, {time.time()-t00:.0f} s", flush=True)


if __name__ == "__main__":
    main()
