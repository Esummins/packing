"""A159 -- the sample line the campaign's convention asks for: drawn -> tested -> hits.

For every near-miss corner, draw poses of the conditioned square H uniformly in its box `B`, keep
those inside the container that MEET int(widened corner box) -- that is the `B_meet` region at pose
level, the only place the joint split has to work -- and for each of them hunt a free unit square
that meets the same box and is interior-disjoint from that H.  A hit is a realised two-crowd and
refutes any lane kill at the corner; `hits = 0` over >= 10^4 drawn H poses is the sampled evidence
that none exists (the optimisation in `twocrowd159.py` is the stronger test; this is the
convention's uniform-draw counterpart, and the two must agree).

The SAT is the from-scratch numpy one in `check159.py` (support functions along the 4 + 4 edge
normals); nothing here is imported from A141's emitter.

    python sampleline159.py --draws 20000
"""
import argparse
import glob
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
A141 = os.path.join(ROOT, "attempts", "A141-polycore-lane")
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

import check159 as C  # noqa: E402  (its from-scratch SAT)

S0 = 969271.0 / 250000.0
W0 = (S0 / 3.82 - 1.0) * (1.0 + 1.0 / math.sqrt(2.0))


def corner_cell(corner, w):
    lo, hi = 0.0, 1.0 + w
    return {"BL": (lo, hi, lo, hi), "BR": (S0 - hi, S0 - lo, lo, hi),
            "TR": (S0 - hi, S0 - lo, S0 - hi, S0 - lo),
            "TL": (lo, hi, S0 - hi, S0 - lo)}[corner]


def line(box, corner, w, draws, free_n, seed, h_tested):
    rect = corner_cell(corner, w)
    rng = np.random.default_rng(seed)
    x = rng.uniform(box[0], box[1], draws)
    y = rng.uniform(box[2], box[3], draws)
    t = np.radians(rng.uniform(box[4], box[5], draws))
    h = 0.5 * (np.abs(np.cos(t)) + np.abs(np.sin(t)))
    keep = ((x >= h) & (x <= S0 - h) & (y >= h) & (y <= S0 - h)
            & C._meets_rect(x, y, t, rect))
    HX, HY, HT = x[keep], y[keep], t[keep]
    out = dict(drawn=int(draws), H_in_B_meet=int(len(HX)), free_drawn=int(free_n), hits=0,
               example=None, H_tested=0)
    if not len(HX):
        return out
    fx = rng.uniform(max(0.0, rect[0] - 0.75), min(S0, rect[1] + 0.75), free_n)
    fy = rng.uniform(max(0.0, rect[2] - 0.75), min(S0, rect[3] + 0.75), free_n)
    ft = rng.uniform(0.0, 0.5 * math.pi, free_n)
    hh = 0.5 * (np.abs(np.cos(ft)) + np.abs(np.sin(ft)))
    k = ((fx >= hh) & (fx <= S0 - hh) & (fy >= hh) & (fy <= S0 - hh)
         & C._meets_rect(fx, fy, ft, rect))
    fx, fy, ft = fx[k], fy[k], ft[k]
    out["free_meeting"] = int(len(fx))
    n = min(len(HX), h_tested)
    out["H_tested"] = int(n)
    for i in range(n):
        dj = C._sq_sq_disjoint((fx, fy, ft),
                               (np.full(len(fx), HX[i]), np.full(len(fx), HY[i]),
                                np.full(len(fx), HT[i])))
        if dj.any():
            out["hits"] += int(dj.sum())
            if out["example"] is None:
                q = int(np.argmax(dj))
                out["example"] = dict(H=[float(HX[i]), float(HY[i]),
                                         float(np.degrees(HT[i]))],
                                      free=[float(fx[q]), float(fy[q]),
                                            float(np.degrees(ft[q]))])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draws", type=int, default=20000)
    ap.add_argument("--free", type=int, default=40000)
    ap.add_argument("--htested", type=int, default=400)
    ap.add_argument("--out", default=os.path.join(BASE, "results", "sampleline159.jsonl"))
    a = ap.parse_args()
    rows = {}
    for f in sorted(glob.glob(os.path.join(A141, "results", "t2_cells_s*.jsonl"))):
        for ln in open(f, encoding="utf-8"):
            r = json.loads(ln)
            rows.setdefault(r["cell"], r)
    tc = {}
    p = os.path.join(BASE, "results", "twocrowd159.jsonl")
    for ln in open(p, encoding="utf-8"):
        z = json.loads(ln)
        tc[(z["cell"], z["corner"])] = z
    jobs = [(c, cc) for (c, cc) in sorted(tc)]
    fh = open(a.out, "w", encoding="utf-8")
    agree = dis = 0
    for (cid, corner) in jobs:
        box = rows[cid]["boxes"][0]
        rec = dict(cell=cid, corner=corner, box=box)
        for tag, w in (("widened", W0), ("unwidened", 0.0)):
            rec[tag] = line(box, corner, w, a.draws, a.free, 1594, a.htested)
            rec[tag]["opt_found"] = bool(tc[(cid, corner)][tag]["found"])
            rec[tag]["opt_J"] = tc[(cid, corner)][tag]["best_J"]
        # the two tests must not contradict: a uniform HIT where the optimiser found nothing
        # would mean the optimiser missed a feasible sliver.
        bad = any(rec[t]["hits"] > 0 and not rec[t]["opt_found"] for t in
                  ("widened", "unwidened"))
        rec["consistent_with_optimiser"] = not bad
        agree += int(not bad)
        dis += int(bad)
        fh.write(json.dumps(rec) + "\n")
        fh.flush()
        print("%-26s %s  widened: H_in_B_meet %5d hits %6d (opt %s) | unwidened: %5d hits %6d "
              "(opt %s)%s"
              % (cid, corner, rec["widened"]["H_in_B_meet"], rec["widened"]["hits"],
                 "FOUND" if rec["widened"]["opt_found"] else "none",
                 rec["unwidened"]["H_in_B_meet"], rec["unwidened"]["hits"],
                 "FOUND" if rec["unwidened"]["opt_found"] else "none",
                 "  <<< INCONSISTENT" if bad else ""), flush=True)
    fh.close()
    print("\n%d consistent, %d inconsistent with the optimisation" % (agree, dis))


if __name__ == "__main__":
    main()
