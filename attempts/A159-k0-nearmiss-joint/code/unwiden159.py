"""A159 T1b -- the PI's reading, taken literally: the lane test at the UNWIDENED corner cell.

A159 T1 shows every one of A141's 28 two-crowd witnesses is EXACT and real -- but 24 of the 28
have `H` missing the plain unit corner cell `TR(0,0) = [s0-1, s0]^2` by 0.003 to 0.036 and
reaching only the WIDENED box `[s0 - 1 - W0, s0]^2` of Lemma K0-WIDEN (`W0 = 0.0255100742`).
So the PI's reading ("TR(0,0) cannot be doubly met") is a statement about the UNWIDENED cell, and
the witnesses do not refute it.

A witness missing the unwidened cell is not a proof that nothing reaches it, so this file runs
A141's ordinary leaf with `w = 0`:

    LANE_K'(TR(0,0)) + M(TR(0,0)) <= 1     =>   TR(0,0) is singly met in every realisation.

WHAT SUCH A KILL IS WORTH -- read this before quoting the number.  The widening exists because
K0-FREE has to transport across the window `W = [3.82, s0]`: a corner box of the container at side
`s` pulls back to `[s0 - lambda*a, s0]` with `lambda <= lambda_max = s0/3.82`, and `W0 =
(lambda_max - 1)(1 + 1/sqrt2)` is exactly the slack that makes one fixed box work for every `s` in
`W` (A143/A150).  A kill at `w = 0` therefore certifies "singly met" AT THE FIXED SIDE s0 ONLY.
It is an s0-only kill, in the same sense as A63's s0-only certificates, and it does NOT by itself
remove the cell from the window tree.  It is emitted here labelled `k0_corner_unwidened` and
`scope: s0_only` so that nothing downstream can mistake it for a window kill.

    python unwiden159.py                # every near-miss corner, w = 0
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
import emit141 as EM              # noqa: E402
from caselp import Box            # noqa: E402


def t2_rows():
    rows = {}
    for f in sorted(glob.glob(os.path.join(A141, "results", "t2_cells_s*.jsonl"))):
        for ln in open(f, encoding="utf-8"):
            r = json.loads(ln)
            rows.setdefault(r["cell"], r)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(BASE, "results", "unwiden159.jsonl"))
    ap.add_argument("--sample", type=int, default=20000)
    ap.add_argument("--cells", default="")
    ap.add_argument("--depth0", type=int, default=20)
    ap.add_argument("--maxdepth", type=int, default=34)
    ap.add_argument("--maxopen", type=int, default=1500)
    ap.add_argument("--maxleaves", type=int, default=120000)
    a = ap.parse_args()
    rows = t2_rows()
    jobs = []
    for cid, r in sorted(rows.items()):
        for c in ("BL", "BR", "TR", "TL"):
            if r["corners"][c]["verdict"].startswith("NEAR-MISS"):
                jobs.append((cid, c, r["corners"][c]))
    if a.cells:
        want = set(a.cells.split(","))
        jobs = [j for j in jobs if j[0] in want]
    print("%d near-miss corners at w = 0" % len(jobs), flush=True)
    done = set()
    if os.path.exists(a.out):
        for ln in open(a.out, encoding="utf-8"):
            try:
                z = json.loads(ln)
                done.add((z["cell"], z["corner"]))
            except Exception:                                    # noqa: BLE001
                pass
    fh = open(a.out, "a", encoding="utf-8")
    nk = 0
    for (nid, corner, v) in jobs:
        if (nid, corner) in done:
            continue
        raw = [Box(*b) for b in rows[nid]["boxes"]]
        conds = P.build_cond(raw)
        cell = P.corner_cell(corner, P.S0, 0.0)            # w = 0: the plain unit corner cell
        t0 = time.time()
        res = P.lane_corner_generic(cell, conds, rng=np.random.default_rng(1591),
                                    sample=a.sample, keep_cert=True,
                                    lane_depth0=a.depth0, max_depth=a.maxdepth,
                                    max_open=a.maxopen, max_leaves=a.maxleaves)
        kill = (res["lane_ub"] is not None and res.get("M_exact")
                and res["lane_ub"] + res["M"] <= 1)
        row = dict(cell=nid, corner=corner, scope="s0_only", w=0.0,
                   lane_ub=res["lane_ub"], lane_lb=res["lane_lb"], M=res.get("M"),
                   M_exact=res.get("M_exact"), verdict=res["verdict"], kill=bool(kill),
                   secs=round(time.time() - t0, 1))
        if kill:
            d = EM.cert_dict("polycore_lane", nid, corner, conds, raw, res,
                             extra=dict(cell_kind="k0_corner_unwidened", scope="s0_only",
                                        attempt="A159", widen_w=0.0))
            p = os.path.join(BASE, "certs", f"unwiden_{nid}_{corner}.json")
            row["cert"] = os.path.relpath(p, ROOT)
            row["sha256"] = EM.write_cert(p, d)
            nk += 1
        fh.write(json.dumps(row) + "\n")
        fh.flush()
        print("%-26s %s w=0  LANE<=%s M=%s lb=%s  %s  %.0fs"
              % (nid, corner, row["lane_ub"], row["M"], row["lane_lb"],
                 "KILL(s0-only)" if kill else row["verdict"], row["secs"]), flush=True)
    fh.close()
    print("done: %d of %d near-miss corners are singly met at the UNWIDENED cell (s0 only)"
          % (nk, len(jobs)))


if __name__ == "__main__":
    main()
