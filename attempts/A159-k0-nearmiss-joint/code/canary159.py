"""A159 T3 -- THE CANARY, in its decisive form: follow the exact witness down the split tree.

`l1_153` is a Trump-image cell.  A Trump image is doubly met at every corner in the widened sense
by construction (A143/A150; `residue_ledger` sec 4: Trump's lineage "can never die by K0-FREE --
Delta_lambda z-hat has >= 2 widened meeters at every corner"), and A159 T1 turns that into an
EXACT witness: `H* = (2.6264181294, 2.3826656154, 48.2135518219 deg)` inside `B`, a free square
`F* = (3.3489836281, 3.3617081337, 1.3973409799 deg)`, both meeting `int` of the widened TR box
(penetrations 3.32e-4 and 1.01) and interior-disjoint (separation 4.74e-3), all certified in
interval arithmetic at 60 dps.  If the joint split closes this corner the leaf is UNSOUND.

Running the whole split to exhaustion is the wasteful way to see that.  `lane_corner_split`
partitions `B` by a deterministic rule (`polylane.split_box`: halve the widest of x, y, theta/60),
so the piece containing `H*` is determined at every depth.  This file walks exactly that chain --
`B`, then the child containing `H*`, and so on -- and runs the ORDINARY leaf on each piece with
`K'(piece)` as the obstacle, reporting `(m_j, lane_ub, M_other, total)`.

That is the whole canary.  By Lemma A159-1 the chain must show `m_j = 1` (the piece contains a
pose that meets the cell) and `lane_ub >= 1` (F* is a free meeter that misses `K'(piece)`, since
`K'(piece)` is contained in `Q(H*)`), hence `total >= 2 > 1` at EVERY depth: the split can never
discharge the piece where the packing actually lives, so it can never close.  A depth at which
this chain reports `total <= 1` is a proof that the leaf, or its implementation, is unsound --
the run stops and says so.

    python canary159.py --depth 14
"""
import argparse
import glob
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
A141 = os.path.join(ROOT, "attempts", "A141-polycore-lane")
sys.path.insert(0, os.path.join(A141, "code"))

import blas1  # noqa: F401,E402
import numpy as np  # noqa: E402

import polylane as P              # noqa: E402
import polycore as PC             # noqa: E402
from caselp import Box            # noqa: E402


def in_box(b, pose):
    return (b.x0 <= pose[0] <= b.x1 and b.y0 <= pose[1] <= b.y1
            and b.th0 <= pose[2] <= b.th1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", default="l1_153")
    ap.add_argument("--corner", default="TR")
    ap.add_argument("--depth", type=int, default=14)
    ap.add_argument("--sample", type=int, default=8000)
    ap.add_argument("--out", default=os.path.join(BASE, "results", "canary159.jsonl"))
    a = ap.parse_args()

    rows = {}
    for f in sorted(glob.glob(os.path.join(A141, "results", "t2_cells_s*.jsonl"))):
        for ln in open(f, encoding="utf-8"):
            r = json.loads(ln)
            rows.setdefault(r["cell"], r)
    wit = None
    for r in json.load(open(os.path.join(A141, "results", "t5_twocrowd.json"),
                            encoding="utf-8")):
        if r["cell"] == a.cell and r["corner"] == a.corner:
            wit = r
    if wit is None:
        print("no recorded witness for %s %s" % (a.cell, a.corner))
        return 2
    exact = None
    for ln in open(os.path.join(BASE, "results", "xwitness159.jsonl"), encoding="utf-8"):
        z = json.loads(ln)
        if z["cell"] == a.cell and z["corner"] == a.corner:
            exact = z
    if not (exact and exact["SURVIVES"]):
        print("the witness for %s %s is NOT exact -- this cell cannot serve as the canary"
              % (a.cell, a.corner))
        return 2

    raw = [Box(*b) for b in rows[a.cell]["boxes"]]
    conds = P.build_cond(raw)
    cell = P.corner_cell(a.corner)
    j = 0
    Hstar = [float(v) for v in wit["H"]]
    Fstar = [float(v) for v in wit["free"]]
    others = [c for c in conds if c.idx != j]

    chain, b, path = [], conds[j].box, ""
    unsound = None
    t0 = time.time()
    for d in range(a.depth + 1):
        pc = P.build_cond([b], tighten=False)[0]
        pc.idx = j
        cs = others + [pc]
        misses = P.box_misses_cell(b, cell)
        res = P.lane_corner_generic(cell, cs, meeters=sorted({c.idx for c in conds} - {j}),
                                    rng=np.random.default_rng(1593), sample=a.sample,
                                    keep_cert=False)
        m_j = 0 if misses else 1
        tot = None if res["lane_ub"] is None else res["lane_ub"] + (res["M"] or 0) + m_j
        # is the exact free witness still a free meeter against K'(this piece)?
        dep = float(PC.poly_square_depth(pc.pc.P, np.array([[Fstar[0], Fstar[1]]]),
                                         np.array([np.radians(Fstar[2])]))[0])
        rec = dict(depth=d, path=path, box=P.box_json(b), contains_Hstar=in_box(b, Hstar),
                   misses_cell=bool(misses), m_j=m_j, lane_ub=res["lane_ub"],
                   M_other=res.get("M"), total=tot, verdict=res["verdict"],
                   Fstar_vs_Kprime_piece=dep, Fstar_still_free=bool(dep <= 0.0))
        chain.append(rec)
        print("d=%-2d path=%-14s m_j=%d lane_ub=%s M_other=%s total=%s  F*-vs-K'(piece)=%+0.6f"
              % (d, path or "(root)", m_j, res["lane_ub"], res.get("M"), tot, dep), flush=True)
        if tot is not None and tot <= 1:
            unsound = rec
            break
        b0, b1 = P.split_box(b)
        if in_box(b0, Hstar):
            b, path = b0, path + "0"
        elif in_box(b1, Hstar):
            b, path = b1, path + "1"
        else:
            print("H* fell out of both children at depth %d -- split rule mismatch" % d)
            break

    out = dict(cell=a.cell, corner=a.corner, kind="canary_witness_chain", split_index=j,
               Hstar=Hstar, Fstar=Fstar, depth=a.depth, chain=chain,
               exact_witness={k: exact[k] for k in
                              ("H_vs_widened", "free_vs_widened", "free_vs_H",
                               "H_vs_unwidened", "free_vs_unwidened", "SURVIVES")},
               fired=bool(unsound), secs=round(time.time() - t0, 1))
    with open(a.out, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(out) + "\n")
    if unsound:
        print("\n*** CANARY FIRED: the leaf discharges the piece that CONTAINS the exact "
              "witness (%s).  THE JOINT SPLIT IS UNSOUND. ***" % json.dumps(unsound)[:300])
        return 3
    print("\nCANARY CLEAN: over %d depths the piece containing H* keeps m_j = 1 and "
          "lane_ub >= 1, so total >= 2 > 1 -- the joint split cannot close l1_153 %s, exactly as "
          "Lemma A159-1 requires." % (len(chain), a.corner))
    return 0


if __name__ == "__main__":
    sys.exit(main())
