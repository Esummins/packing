"""A166 -- build the LP node list from the geometric survivors.

THE COVER OF A NODE, and why it is complete (this is the statement the LP list realises).

Let the node be "some square `H` of `F` has pose in `B_H`", plus K0-BLOCKED at the nearest corner
`c`: two DISTINCT squares `Q_1 != Q_2` of `F` meet `int B_c^w`.  Each `Q_i` has a pose in the reach
set `R_c^w`, which A143 (R3) covers by the 216 cells.  Classify each cover cell `X` (in `c`'s frame,
pulled to global coordinates) by A166's stages:

  DEAD_*       no pose of `X` can host a corner meeter that is a DIFFERENT square from `H`, and
               `X` cannot host `H` either (`X ∩ B_H = ∅` as parameter boxes) -- so `X` hosts nothing;
  DEGENERATE_* every pose of `X` overlaps every pose of `B_H`, so a square with a pose in `X` IS `H`;
  ALIVE        neither.

Then exactly two kinds of child exist:

  (a) BUDGET 8: `Q_1, Q_2` both `!= H`.  Neither can lie in a DEGENERATE cell (that would force it to
      be `H`) nor in a DEAD cell, so both lie in ALIVE cells and the unordered pair survives A143's
      pair chain on the clipped boxes.  Hypothesis: `[B_H, X_1^clip, X_2^clip]`, three distinct
      squares, budget `11 - 3 = 8`.

  (b) BUDGET 9 (DEGENERATE): one of them IS `H`.  Then `H` meets `int B_c^w` -- decided exactly by
      A161's `box_misses_cell_exact(B_H, corner box)` -- and the other, `Q != H`, lies in an ALIVE
      cell.  Hypothesis: `[B_H^meet, X^clip]`, two distinct squares, budget `11 - 2 = 9`.
      `B_H^meet` is the bounding box of the sub-boxes of `B_H` that are NOT certified to miss the
      corner box (A159's `B_meet`, here with A161's stronger exact test), which is a sound superset
      of the poses of `H` that can be a meeter.

If (b) is impossible (`H` certified to miss the corner box) then (a) alone is the whole cover, and an
empty (a) is a (C) leaf -- the node dies with NO LP at all.

    python code/pick166.py --pad wmax --nsample 10
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import geo166 as G                                              # noqa: E402
import cells166 as C                                            # noqa: E402
from caselp import Box                                          # noqa: E402  READ-ONLY (A57)

RES = os.path.join(BASE, "results")
PADS = {"w0": 0.0, "wmax": C.W_MAX}


def b_meet(bH, rect, npos=4, ntilt=4):
    """A159's `B_meet` as ONE box: the bounding box of the sub-boxes of `bH` that A161's exact test
    does NOT certify to miss the corner box.  Returns (box or None, kept, total)."""
    kept = []
    for i in range(npos):
        for j in range(npos):
            for k in range(ntilt):
                x0 = bH.x0 + (bH.x1 - bH.x0) * i / npos
                x1 = bH.x0 + (bH.x1 - bH.x0) * (i + 1) / npos
                y0 = bH.y0 + (bH.y1 - bH.y0) * j / npos
                y1 = bH.y0 + (bH.y1 - bH.y0) * (j + 1) / npos
                t0 = bH.th0 + (bH.th1 - bH.th0) * k / ntilt
                t1 = bH.th0 + (bH.th1 - bH.th0) * (k + 1) / ntilt
                sb = Box(x0, x1, y0, y1, t0, t1)
                can, _d = G.cell_can_meet(sb, rect)
                if can:
                    kept.append(sb)
    n = npos * npos * ntilt
    if not kept:
        return None, 0, n
    return (Box(min(b.x0 for b in kept), max(b.x1 for b in kept),
                min(b.y0 for b in kept), max(b.y1 for b in kept),
                min(b.th0 for b in kept), max(b.th1 for b in kept)), len(kept), n)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pad", default="wmax", choices=sorted(PADS))
    ap.add_argument("--nsample", type=int, default=10)
    ap.add_argument("--ndegen", type=int, default=3)
    ap.add_argument("--seed", type=int, default=1666)
    a = ap.parse_args()
    a_w = 1.0 + PADS[a.pad]
    import random
    rng = random.Random(a.seed)
    per_cell = {}
    meta_out = []
    for (meta, bH, _rec) in C.load_eleven():
        name = meta["cell"]
        p = os.path.join(RES, "survivors166_%s_%s.json" % (a.pad, name))
        if not os.path.exists(p):
            print("missing", p)
            continue
        d = json.load(open(p, encoding="utf-8"))
        corner = d["corner"]
        rect = C.corner_rect(corner, a_w)
        can, det = G.cell_can_meet(bH, rect)
        nodes = []
        # --- (a) budget 8
        S = d["survivors"]
        pick = S if len(S) <= a.nsample else rng.sample(S, a.nsample)
        for s in pick:
            tag = "%s_b8_%s_%s" % (name, "".join(map(str, s["a"])), "".join(map(str, s["b"])))
            nodes.append(dict(node=tag, cell=name, kind="budget8", pad=a.pad, budget=8,
                              boxes=s["boxes"], pair=[s["a"], s["b"]],
                              n_survivors=len(S), sampled=bool(len(S) > a.nsample)))
        # --- (b) budget 9, degenerate
        bm, kept, tot = (None, 0, 0)
        if can:
            bm, kept, tot = b_meet(bH, rect)
            alive_cells = [k for k, v in d["per_cell"].items() if v["verdict"] == "ALIVE"]
            pk = alive_cells if len(alive_cells) <= a.ndegen else rng.sample(alive_cells, a.ndegen)
            for k in sorted(pk):
                cb = d["per_cell"][k]["cbox"]
                nodes.append(dict(node="%s_b9_%s" % (name, k), cell=name, kind="degenerate",
                                  pad=a.pad, budget=9,
                                  boxes=[(bm or bH).to_json(), cb], pair=[None, [int(c) for c in k]],
                                  n_partners=len(alive_cells),
                                  b_meet_kept="%d/%d" % (kept, tot)))
        per_cell[name] = nodes
        meta_out.append(dict(cell=name, corner=corner, H_can_meet_corner=bool(can),
                             n_b8_survivors=len(S), n_alive_cells=sum(
                                 1 for v in d["per_cell"].values() if v["verdict"] == "ALIVE"),
                             n_degenerate_cells=sum(
                                 1 for v in d["per_cell"].values()
                                 if str(v["verdict"]).startswith("DEGENERATE")),
                             b_meet_kept="%d/%d" % (kept, tot) if can else None,
                             b_meet_box=(bm.to_json() if bm else None),
                             cover_complete_at_b8=bool(not can),
                             geometric_verdict=("DEAD (C leaf, no LP)" if (not can and not S)
                                                else "DEGENERATE-ONLY (budget 9)" if not S
                                                else "PAIR CELLS ALIVE (budget 8 LP)"),
                             n_nodes=len(nodes)))
        print("%-12s can_meet=%-5s b8_survivors=%4d alive_cells=%3d degen_cells=%2d -> %d LP nodes | %s"
              % (name, can, len(S), meta_out[-1]["n_alive_cells"],
                 meta_out[-1]["n_degenerate_cells"], len(nodes),
                 meta_out[-1]["geometric_verdict"]), flush=True)
    # interleave by cell so a deadline cut leaves a BALANCED sample
    order = []
    i = 0
    names = [m["cell"] for m in meta_out]
    while any(len(per_cell[n]) > i for n in names):
        for n in names:
            if len(per_cell[n]) > i:
                order.append(per_cell[n][i])
        i += 1
    json.dump(order, open(os.path.join(RES, "nodes166_%s.json" % a.pad), "w"), indent=1)
    json.dump(meta_out, open(os.path.join(RES, "coverplan166_%s.json" % a.pad), "w"), indent=1)
    print("wrote %d nodes" % len(order))


if __name__ == "__main__":
    main()
