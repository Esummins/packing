"""A157 T2a -- the HIGH-SAMPLE screen over the 196 UNDECIDED cells, before any cover.

A141's sweep screened with 8 000 poses.  `lane_lb = 0` there means "no free pose was DRAWN", not
"no free pose exists"; on `c0_Y0076 TL(0,0)` a 20 000-pose draw already realises `LANE_K' >= 1`
(2 free poses among 11 648 meeting the cell), which with `M = 1` makes a kill impossible.  So the
first thing A157 buys is a much bigger draw: a realised free pose is a SOUND lower bound and
retires a cell from the kill candidate list immediately, for a millionth of the cover's cost.

Per cell it records: drawn / meeting / overlapping-some-core / free, the best (largest) core
margin over the meeting poses (`max over poses of min over cores of -depth`, negative = every
pose is strictly inside some core), a free-pose witness with its per-core depths, and the
realised interior-disjoint pair when there is one.

    python screen157.py --sample 400000
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
for _p in (os.path.join(ROOT, "attempts", "A141-polycore-lane", "code"),
           os.path.join(ROOT, "attempts", "A118-lane-count", "code")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import blas1  # noqa: F401,E402
import numpy as np  # noqa: E402

import polylane as P              # noqa: E402  READ-ONLY
import polycore as PC             # noqa: E402  READ-ONLY
import lane as LANE               # noqa: E402  READ-ONLY
import lanelib as L               # noqa: E402  READ-ONLY
from caselp import Box            # noqa: E402  READ-ONLY


def build(rec, slot):
    c, i, j = LANE.L.parse_cell(slot)
    pin_b, cond_b = LANE.cframe_boxes(rec, c, i, j)
    pins = P.build_cond([Box(b.x0, b.x1, b.y0, b.y1, b.th0, b.th1) for b in pin_b],
                        tighten=False)
    cond = P.build_cond([Box(b.x0, b.x1, b.y0, b.y1, b.th0, b.th1) for b in cond_b],
                        tighten=False)
    for k, cs in enumerate(cond):
        cs.idx = len(pins) + k
    return pins + cond, [cs.idx for cs in cond], (float(i), float(i) + 1.0,
                                                  float(j), float(j) + 1.0)


def screen(conds, cell, rng, n, chunk=100000):
    tot = dict(drawn=0, meeting=0, overlapping=0, free=0)
    best_margin = -1e18
    witness = None
    pair = None
    free_keep_C, free_keep_T = [], []
    for start in range(0, n, chunk):
        m = min(chunk, n - start)
        C, T = P.sample_meeting(cell, P.S0, m, rng)
        tot["drawn"] += m
        tot["meeting"] += int(len(C))
        if not len(C):
            continue
        D = np.empty((len(conds), len(C)))
        for k, cs in enumerate(conds):
            D[k] = PC.poly_square_depth(cs.pc.P, C, T)
        hit = (D > 0.0).any(axis=0)
        tot["overlapping"] += int(hit.sum())
        tot["free"] += int((~hit).sum())
        marg = (-D.max(axis=0))                    # > 0 <=> free with that clearance
        k = int(np.argmax(marg))
        if marg[k] > best_margin:
            best_margin = float(marg[k])
            witness = dict(c=[float(C[k, 0]), float(C[k, 1])], theta_deg=float(np.degrees(T[k])),
                           depths=[float(D[q, k]) for q in range(len(conds))],
                           free=bool(not hit[k]))
        if (~hit).any() and len(free_keep_C) < 800:
            free_keep_C.append(C[~hit][:800])
            free_keep_T.append(T[~hit][:800])
    if free_keep_C:
        FC = np.concatenate(free_keep_C)[:800]
        FT = np.concatenate(free_keep_T)[:800]
        if len(FC) >= 2:
            G = L.pair_gaps(FC, FT)
            np.fill_diagonal(G, -1e9)
            q = int(np.argmax(G))
            u, v = divmod(q, len(FC))
            if G[u, v] > 0.0:
                pair = dict(gap=float(G[u, v]),
                            a=[float(FC[u, 0]), float(FC[u, 1]), float(np.degrees(FT[u]))],
                            b=[float(FC[v, 0]), float(FC[v, 1]), float(np.degrees(FT[v]))])
    lane_lb = 0 if tot["free"] == 0 else (2 if pair else 1)
    return dict(sample=tot, lane_lb=lane_lb, best_margin=best_margin, witness=witness,
                pair=pair)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", default=os.path.join(BASE, "results", "undecided_cells.jsonl"))
    ap.add_argument("--recs", default=os.path.join(BASE, "results", "recs157.json"))
    ap.add_argument("--out", default=os.path.join(BASE, "results", "screen157.jsonl"))
    ap.add_argument("--sample", type=int, default=400000)
    ap.add_argument("--shard", default="0/1")
    a = ap.parse_args()

    recs = json.load(open(a.recs, encoding="utf-8"))
    jobs, seen = [], set()
    with open(a.jobs, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln:
                continue
            j = json.loads(ln)
            k = (j["nid"], j["slot"])
            if k not in seen:
                seen.add(k)
                jobs.append(j)
    k, n = (int(v) for v in a.shard.split("/"))
    if n > 1:
        jobs = [j for i, j in enumerate(jobs) if i % n == k]
    done = set()
    if os.path.exists(a.out):
        with open(a.out, encoding="utf-8") as fh:
            for ln in fh:
                try:
                    d = json.loads(ln)
                    done.add((d["nid"], d["slot"]))
                except Exception:                  # noqa: BLE001
                    pass
    print("screen: %d cells (%d done), sample=%d" % (len(jobs), len(done), a.sample), flush=True)

    fh = open(a.out, "a", encoding="utf-8")
    rng = np.random.default_rng(15700 + k)
    t0 = time.time()
    n0 = 0
    for j in jobs:
        if (j["nid"], j["slot"]) in done:
            continue
        conds, meet, cell = build(recs[j["nid"]], j["slot"])
        r = screen(conds, cell, rng, a.sample)
        r.update(nid=j["nid"], slot=j["slot"], src=j["src"], key=j["key"], cls=j["cls"],
                 level=j["level"], a141_M=j["M"], a141_meeters=j["meeters"],
                 n_pins=len(conds) - len(meet), n_cond=len(meet))
        fh.write(json.dumps(r) + "\n")
        fh.flush()
        n0 += 1
        print("%-34s %-9s drawn=%d meet=%-7d free=%-6d lane_lb=%d margin=%+.3e"
              % (j["nid"], j["slot"], r["sample"]["drawn"], r["sample"]["meeting"],
                 r["sample"]["free"], r["lane_lb"], r["best_margin"]), flush=True)
    fh.close()
    print("screen done: %d cells, %.0f s" % (n0, time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
