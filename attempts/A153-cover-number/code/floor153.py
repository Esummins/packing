"""A153 -- the FLOOR pass: how small could the cover number POSSIBLY be?

`price_node` already reports a greedy 1-separated set of cell centres inside F_outer.  That is a
lower bound on every cover number of F_outer, but F_outer is an OUTER approximation, so a sceptic
can answer "refine the grid and the undecided band goes away".  This pass answers that: it repeats
the greedy 1-separated construction on the **GREEN** cells only -- the cells A148 certifies
FEASIBLE, every point of which really does admit a unit square in the container disjoint from every
core.  So

    floor_green  <=  packing number of the TRUE feasible-centre region F
                 <=  every cover number of F, at any grid pitch, with pieces of any shape of
                     diameter < 1,

and `floor_green >= budget` says Leaf CN can NEVER kill the node, however much the region is
refined.  The same is done in the tilt frame for Lemma TC (L-infinity separation).

Writes results/floor153_<pop>.jsonl.  READ-ONLY on every campaign.
"""
import argparse
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
for _p in (HERE,):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import numpy as np                                                    # noqa: E402
import cover153 as C                                                  # noqa: E402
import run153 as R                                                    # noqa: E402


def sep_set(xs, ys, mask, sep=1.0, th=None):
    """greedy maximal set of cell centres of `mask`, pairwise Euclidean >= sep (th is None) or
    pairwise L-infinity >= sep in the frame `th`."""
    jj, ii = np.nonzero(mask)
    if len(ii) == 0:
        return []
    x, y = xs[ii], ys[jj]
    if th is None:
        u, v = x, y
    else:
        c, s = math.cos(th), math.sin(th)
        u, v = x * c + y * s, -x * s + y * c
    live = np.ones(len(u), bool)
    pts = []
    while live.any():
        k = int(np.argmax(live))
        pts.append((float(x[k]), float(y[k])))
        if th is None:
            live &= ~(((u - u[k]) ** 2 + (v - v[k]) ** 2 < sep * sep))
        else:
            live &= ~((np.abs(u - u[k]) < sep) & (np.abs(v - v[k]) < sep))
    return pts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pop", default="a148")
    ap.add_argument("--lo", type=int, default=0)
    ap.add_argument("--hi", type=int, default=10 ** 9)
    a = ap.parse_args()
    recs = R.POPS[a.pop]()[a.lo:a.hi]
    outp = os.path.join(BASE, "results", f"floor153_{a.pop}.jsonl")
    fh = open(outp, "a", encoding="utf-8")
    for i, r in enumerate(recs):
        t0 = time.time()
        try:
            reg, obst, onames, kinds = C.region_of(r["boxes"])
        except Exception as ex:                                       # noqa: BLE001
            print(f"[{i+1}] {r['id']} ERROR {ex}", flush=True)
            continue
        frames, win = R.tc_frames(r["boxes"])
        g = sep_set(reg.xs, reg.ys, reg.green)
        o = sep_set(reg.xs, reg.ys, ~reg.blocked)
        tcg = [len(sep_set(reg.xs, reg.ys, reg.green, th=t)) for (t, d) in frames if d == 0.0]
        row = dict(id=r["id"], camp=r["camp"], budget=r["budget"],
                   area_green=reg.area_green(), area_open=reg.area_open(),
                   floor_green=len(g), floor_outer=len(o),
                   floor_green_pts=[[round(x, 6), round(y, 6)] for x, y in g],
                   tc_floor_green=tcg, tc_floor_green_min=min(tcg) if tcg else None,
                   tilt_window_deg=[math.degrees(win[0]), math.degrees(win[1])],
                   can_ever_kill=bool(len(g) < r["budget"]),
                   tc_can_ever_kill=bool((min(tcg) if tcg else 99) < r["budget"]),
                   secs=round(time.time() - t0, 2))
        fh.write(json.dumps(row) + "\n")
        fh.flush()
        print(f"[{i+1:4d}/{len(recs)}] {r['id']:34s} b={r['budget']} floor_green="
              f"{row['floor_green']} floor_outer={row['floor_outer']} "
              f"tc_floor_green={row['tc_floor_green_min']} "
              f"{'CN-LEAF-POSSIBLE' if row['can_ever_kill'] else ''}"
              f"{' TC-POSSIBLE' if row['tc_can_ever_kill'] else ''} {row['secs']}s", flush=True)
    fh.close()
    print("wrote", outp)


if __name__ == "__main__":
    main()
