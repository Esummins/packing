"""A141 T5 (the PI's refinement) -- the JOINT count: turn a NEAR-MISS (LANE_K' = 1, M = 1) into a
kill by splitting the conditioned square's parameter box.

`LANE_K'(C) + M(C) = 2` is not a kill only because the two counts are taken separately.  Split the
conditioned box `B_j` into a complete binary subdivision `B_1 … B_N`; the actual square j has its
pose in exactly one piece, and on each piece the ORDINARY leaf is re-run with `K'(B_k)` -- which
is strictly bigger than `K'(B_j)` -- in place of `K'(B_j)`:

  * `box_misses_cell(B_k)`  ==>  square j is not a meeter on that piece (`m_k = 0`), so
    `LANE_k <= 1` already gives "C singly met";
  * otherwise `m_k = 1` and the piece needs `LANE_k = 0`, i.e. C met by square j alone.

Both are the same leaf.  If every piece closes, C is singly met for EVERY realisation of the
hypothesis: K0-FREE, the cell is dead, with no LP.

    python t5_split.py --cells l2_p114_001              # the PI's first case
    python t5_split.py --all                            # every near-miss corner in the t2 table
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
sys.path.insert(0, HERE)

import blas1  # noqa: F401,E402
import numpy as np  # noqa: E402

import polylane as P              # noqa: E402
import polycore as PC             # noqa: E402
import emit141 as EM              # noqa: E402
from caselp import Box            # noqa: E402

A140 = os.path.join(ROOT, "attempts", "A140-k0-residue-gallery", "results", "t1_polycore.json")


def corpus():
    d = json.load(open(A140, encoding="utf-8"))
    out = {}
    for r in d["twelve"] + d["pool"]:
        out.setdefault(r["cell"], r)
    return out


def near_misses():
    rows = []
    for f in sorted(glob.glob(os.path.join(BASE, "results", "t2_cells_s*.jsonl"))):
        for ln in open(f, encoding="utf-8"):
            rows.append(json.loads(ln))
    seen, out = set(), []
    for r in rows:
        for c in ("BL", "BR", "TR", "TL"):
            v = r["corners"][c]
            if not v["verdict"].startswith("NEAR-MISS"):
                continue
            if (r["cell"], c) in seen:
                continue
            seen.add((r["cell"], c))
            out.append((r["cell"], c, v))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", default="")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--from-deep", dest="from_deep", default="")
    ap.add_argument("--out", default=os.path.join(BASE, "results", "t5_split.jsonl"))
    ap.add_argument("--maxpieces", type=int, default=128)
    ap.add_argument("--maxdepth", type=int, default=9)
    ap.add_argument("--sample", type=int, default=8000)
    a = ap.parse_args()

    cp = corpus()
    jobs = []
    if a.cells:
        for nid in a.cells.split(","):
            for (c, cc, v) in near_misses():
                if c == nid:
                    jobs.append((c, cc, v))
    if a.all:
        jobs = near_misses()
    if a.from_deep:
        # the near-miss corners with NO realised 2-crowd that the deep cover still left at
        # LANE <= 1: exactly the ones the joint split can still close
        keep = set()
        for ln in open(a.from_deep, encoding="utf-8"):
            z = json.loads(ln)
            if not z.get("kill"):
                keep.add((z["cell"], z["corner"]))
        jobs = [(c, cc, v) for (c, cc, v) in near_misses() if (c, cc) in keep]
    print("%d near-miss (cell, corner) jobs" % len(jobs), flush=True)

    done = set()
    if os.path.exists(a.out):
        for ln in open(a.out, encoding="utf-8"):
            try:
                r = json.loads(ln)
                done.add((r["cell"], r["corner"]))
            except Exception:
                pass
    fh = open(a.out, "a", encoding="utf-8")
    nk = 0
    for (nid, corner, v) in jobs:
        if (nid, corner) in done:
            continue
        rec = cp[nid]
        raw = [Box(*b["box"]) for b in rec["boxes"]]
        conds = P.build_cond(raw)
        cell = P.corner_cell(corner)
        meet = v.get("meeters") or []
        t0 = time.time()
        best = None
        for j in (meet or [c.idx for c in conds]):
            sp = P.lane_corner_split(cell, conds, j, rng=np.random.default_rng(1450 + j),
                                     max_pieces=a.maxpieces, max_depth=a.maxdepth,
                                     sample=a.sample, keep_cert=True)
            if best is None or sp["ok"]:
                best = sp
            if sp["ok"]:
                break
        row = dict(cell=nid, corner=corner, split_index=best["split_index"],
                   n_pieces=best["n_pieces"], closed=bool(best["ok"]),
                   open=len(best["open"]), secs=round(time.time() - t0, 1),
                   lane_ub_before=v["lane_ub"], M_before=v["M"], meeters=meet)
        if best["ok"]:
            # sample line: poses meeting the corner cell, tested against K'(piece) per piece
            rng = np.random.default_rng(7)
            C, T = P.sample_meeting(cell, P.S0, 200000, rng)
            worst = None
            for p in best["pieces"]:
                pc = P.build_cond([Box(*p["box"])], tighten=False)[0]
                cs = [c.pc for c in conds if c.idx != best["split_index"]] + [pc.pc]
                hit = np.zeros(len(C), bool)
                for k in cs:
                    hit |= PC.poly_square_depth(k.P, C, T) > 0.0
                free = int((~hit).sum())
                if worst is None or free > worst[1]:
                    worst = (p["path"], free, p["m_j"])
            row["sample_line"] = dict(drawn=200000, meeting=int(len(C)),
                                      worst_piece=worst[0], free_on_worst_piece=worst[1],
                                      m_j_on_worst_piece=worst[2])
            d = EM.split_cert_dict(nid, corner, conds, raw, cell, best,
                                   extra=dict(sample_line=row["sample_line"]))
            p = os.path.join(BASE, "certs", f"split_{nid}_{corner}.json")
            row["cert"] = os.path.relpath(p, ROOT)
            row["sha256"] = EM.write_cert(p, d)
            nk += 1
        fh.write(json.dumps(row) + "\n")
        fh.flush()
        print("%-26s %s split@%d pieces=%d %s %.0fs" %
              (nid, corner, row["split_index"], row["n_pieces"],
               "KILL" if row["closed"] else "open(%d)" % row["open"], row["secs"]), flush=True)
    fh.close()
    print("done: %d of %d near-miss corners closed by the joint split" % (nk, len(jobs)))


if __name__ == "__main__":
    main()
