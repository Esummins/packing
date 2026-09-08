"""A141 T5b -- the near-miss corners with NO realisable 2-crowd: try to certify LANE_K' = 0
outright (a deeper cover), which turns `LANE <= 1, M = 1` into a kill with no split at all.

`results/t5_twocrowd.json` records, for every near-miss corner, an explicit interior-disjoint
(free square, conditioned square) pair both meeting the widened corner cell — when one exists the
leaf's hypothesis is genuinely realisable and NOTHING (not the joint split either) can kill that
corner.  The corners with no such pair are the ones worth more cover budget.

    python t5_deep.py
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
import emit141 as EM              # noqa: E402
from caselp import Box            # noqa: E402

A140 = os.path.join(ROOT, "attempts", "A140-k0-residue-gallery", "results", "t1_polycore.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(BASE, "results", "t5_deep.jsonl"))
    ap.add_argument("--maxopen", type=int, default=9000)
    ap.add_argument("--depth", type=int, default=40)
    ap.add_argument("--depth0", type=int, default=24)
    a = ap.parse_args()

    d = json.load(open(A140, encoding="utf-8"))
    cp = {}
    for r in d["twelve"] + d["pool"]:
        cp.setdefault(r["cell"], r)
    rows = []
    for f in sorted(glob.glob(os.path.join(BASE, "results", "t2_cells_s*.jsonl"))):
        for ln in open(f, encoding="utf-8"):
            rows.append(json.loads(ln))
    by = {}
    for r in rows:
        by.setdefault(r["cell"], r)
    two = {(x["cell"], x["corner"]) for x in
           json.load(open(os.path.join(BASE, "results", "t5_twocrowd.json"), encoding="utf-8"))}
    jobs = []
    seen = set()
    for r in rows:
        for c in ("BL", "BR", "TR", "TL"):
            v = r["corners"][c]
            if not v["verdict"].startswith("NEAR-MISS"):
                continue
            if (r["cell"], c) in two or (r["cell"], c) in seen:
                continue
            seen.add((r["cell"], c))
            jobs.append((r["cell"], c, v))
    print("%d near-miss corners with no realised 2-crowd" % len(jobs), flush=True)

    done = set()
    if os.path.exists(a.out):
        for ln in open(a.out, encoding="utf-8"):
            try:
                z = json.loads(ln)
                done.add((z["cell"], z["corner"]))
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
        root = Box(*P.centre_window(cell), 0.0, 90.0)
        t0 = time.time()
        cov = P.lane_cover(root, cell, conds, depth0=a.depth0, max_depth=a.depth,
                           max_open=a.maxopen, rounds=10)
        row = dict(cell=nid, corner=corner, lane_ub=cov["lane"], M=v["M"],
                   leaves=len(cov["leaves"]), open=len(cov["open"]),
                   reason=cov.get("reason"), secs=round(time.time() - t0, 1))
        if (cov["lane"] is not None and v["M"] is not None and cov["lane"] + v["M"] <= 1
                and v["M"] == len(conds)):
            # every conditioned square is counted as a possible meeter, so the M side needs no
            # exclusion certificate at all (M = #boxes, the weakest and always-sound value)
            res = dict(cell=list(cell), root=P.box_json(root), lane_ub=cov["lane"],
                       lane_lb=0, M=v["M"], M_exact=True,
                       meeters=[c.idx for c in conds], verdict="KILL",
                       cover_cert=cov["leaves"], cover_open_cert=cov["open"],
                       M_cert=[None] * len(conds),
                       M_detail=[dict(j=c.idx, excluded=False, by="none") for c in conds],
                       sample=v.get("sample"))
            cd = EM.cert_dict("polycore_lane", nid, corner, conds, raw, res)
            p = os.path.join(BASE, "certs", f"deep_{nid}_{corner}.json")
            row["cert"] = os.path.relpath(p, ROOT)
            row["sha256"] = EM.write_cert(p, cd)
            row["kill"] = True
            nk += 1
        fh.write(json.dumps(row) + "\n")
        fh.flush()
        print("%-26s %s LANE<=%s M=%s leaves=%d open=%d %s %.0fs" %
              (nid, corner, cov["lane"], v["M"], len(cov["leaves"]), len(cov["open"]),
               "KILL" if row.get("kill") else "-", row["secs"]), flush=True)
    fh.close()
    print("done: %d new kills from the deep cover" % nk)


if __name__ == "__main__":
    main()
