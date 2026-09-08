"""A158 -- the STRONG refutation of the YES child: a realised two-meeter configuration.

`xover158.py` refutes the LEAF (a free pose clearing K'(S) means the certified bound
LANE_K'(C | S) cannot be 0).  That is weaker than refuting the PI's geometric claim, because
K'(S) is only the INTERSECTION of the poses in S: clearing K'(S) does not by itself mean the free
square is disjoint from the ACTUAL square in S.

This script closes that gap.  It looks for an explicit pair

    p in S            (a near-simple pose of the slot),
    q in R'(C)        (in the container, meeting int C, interior-disjoint from every pin core and
                       from the node's conditioned K'),

with Q(p) and Q(q) INTERIOR-DISJOINT.  Such a pair is a realised configuration in which the slot
box is occupied AND the cell has a second, free meeter -- i.e. the slot is doubly met with a
square in S, which is exactly what the YES child claims cannot happen.

    python pair158.py --jobs ../results/xover_jobs.jsonl --r 0.10 --tt 10
"""
import argparse
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import slotlib158 as SL  # noqa: E402
import numpy as np  # noqa: E402

L = SL.P.L                                    # A118 lanelib, via A141's polylane


def free_meeters(conds, cell, rng, n, cap=3000):
    C, T = SL.P.sample_meeting(cell, SL.S0, n, rng)
    if not len(C):
        return C, T, 0
    hit = np.zeros(len(C), bool)
    for cs in conds:
        hit |= (SL.PC.poly_square_depth(cs.pc.P, C, T) > 0.0)
    return C[~hit][:cap], T[~hit][:cap], int(len(C))


def s_poses(i, j, r, tt, rng, n, conds):
    """Poses in S (both tilt pieces) that a square of the packing could actually have: inside the
    container AND interior-disjoint from every node core (each K'(B) is contained in the square
    of every pose of B, so a square of the packing must clear all of them).  Without this filter
    the "realised pair" could put the S-square through a pin."""
    cx, cy = float(i) + 0.5, float(j) + 0.5
    C = np.column_stack([rng.uniform(cx - r, cx + r, n), rng.uniform(cy - r, cy + r, n)])
    lo = rng.uniform(0.0, tt, n)
    hi = rng.uniform(90.0 - tt, 90.0, n)
    TH = np.radians(np.where(rng.random(n) < 0.5, lo, hi))
    h = 0.5 * (np.abs(np.cos(TH)) + np.abs(np.sin(TH)))
    ok = ((C[:, 0] >= h) & (C[:, 0] <= SL.S0 - h) & (C[:, 1] >= h) & (C[:, 1] <= SL.S0 - h))
    C, TH = C[ok], TH[ok]
    if not len(C):
        return C, TH
    keep = np.ones(len(C), bool)
    for cs in conds:
        keep &= (SL.PC.poly_square_depth(cs.pc.P, C, TH) <= 0.0)
    return C[keep], TH[keep]


def run(rec, slot, r, tt, rng, n, ns):
    conds, meet, cell, (c, i, j) = SL.build_node(rec, slot)
    Q, TQ, nmeet = free_meeters(conds, cell, rng, n)
    P, TP = s_poses(i, j, r, tt, rng, ns, conds)
    out = dict(nid=rec["nid"], src=rec["src"], cls=rec["cls"], slot=slot, r=r, tt=tt,
               n_meeting=nmeet, n_free=int(len(Q)), n_S=int(len(P)))
    if not len(Q) or not len(P):
        out["pair"] = None
        return out
    G = L.cross_gaps(P[:1500], TP[:1500], Q[:1500], TQ[:1500])
    k = int(np.argmax(G))
    u, v = divmod(k, G.shape[1])
    out["max_gap"] = float(G[u, v])
    if G[u, v] > 0.0:
        out["pair"] = dict(
            in_S=[float(P[u, 0]), float(P[u, 1]), math.degrees(float(TP[u]))],
            free=[float(Q[v, 0]), float(Q[v, 1]), math.degrees(float(TQ[v]))],
            gap=float(G[u, v]))
    else:
        out["pair"] = None
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", default=os.path.join(BASE, "results", "xover_jobs.jsonl"))
    ap.add_argument("--recs", default=os.path.join(BASE, "results", "recs158.json"))
    ap.add_argument("--radii", default="0.10,0.05,0.01")
    ap.add_argument("--tt", default="10,2,0")
    ap.add_argument("--n", type=int, default=400000)
    ap.add_argument("--ns", type=int, default=200000)
    ap.add_argument("--out", default=os.path.join(BASE, "results", "pair158.jsonl"))
    a = ap.parse_args()

    recs = json.load(open(a.recs, encoding="utf-8"))
    jobs = [json.loads(l) for l in open(a.jobs, encoding="utf-8") if l.strip()]
    rng = np.random.default_rng(15800)
    fh = open(a.out, "a", encoding="utf-8")
    t0 = time.time()
    for j in jobs:
        for tt in [float(v) for v in a.tt.split(",")]:
            for r in [float(v) for v in a.radii.split(",")]:
                try:
                    row = run(recs[j["nid"]], j["slot"], r, tt, rng, a.n, a.ns)
                except Exception as e:                             # noqa: BLE001
                    row = dict(nid=j["nid"], slot=j["slot"], r=r, tt=tt, error=repr(e)[:200])
                fh.write(json.dumps(row) + "\n")
                fh.flush()
                p = row.get("pair")
                print("%-30s %-9s r=%-6g tt=%-5g free %-5s S %-6s -> %s"
                      % (j["nid"], j["slot"], r, tt, row.get("n_free"), row.get("n_S"),
                         ("PAIR gap %.4e  S=%s  free=%s"
                          % (p["gap"], [round(x, 6) for x in p["in_S"]],
                             [round(x, 6) for x in p["free"]])) if p else
                         ("none (max gap %s)" % row.get("max_gap"))), flush=True)
    fh.close()
    print("%.0f s" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
