#!/usr/bin/env python3
"""
A39 P2b(ii) -- requantify W1's FIRST-KILL DEPTH under a resealed field.

W1 (A38 design.md): a core box B whose inflated m_low exceeds thr = 1 + eta_cert is entirely
exempt, so the node hypothesis "some packing square lies in B" is vacuous and the node dies with
NO LP.  eta_cert is therefore a direct dial on where in the tree W1 starts biting.

A38 measured c_core = m_low(B inflated) at depths 1-3 (medians 0.658 -> 0.85-1.21 -> 1.17-1.21)
and PROJECTED onset at depth 5-7 for thr = 1.4254.  This module replaces the projection with a
DIRECT measurement: from each level-1 survivor box it runs a beam descent over the octree of
child boxes (the same 3-way bisection caselp.Box.split uses, applied cyclically x/y/theta as the
tree does), recording per depth

    max c_core over the beam,  and the number of beam boxes with c_core > thr,

for any list of thresholds.  first-kill depth(thr) = the smallest depth at which some box in the
descent is entirely exempt.  Because the beam only ever UNDER-explores the octree, the reported
first-kill depth is an UPPER bound on the true one for that parent (and the excluded-volume
fraction is a lower bound) -- one-sided in the honest direction.

Usage:
  python w1_depth.py --cert <field cert json> --grid results/p2b/mlow_new.npz --out results/p2b/w1_depth.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from fractions import Fraction as F

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fieldcut as fc                                   # noqa: E402
from caselp import Box                                  # noqa: E402

A38R = os.path.abspath(os.path.join(HERE, "..", "..", "A38-root-power", "results"))


def field_eta(cert_path):
    d = json.load(open(cert_path))
    tot = F(str(d["total"]))
    return float(tot - 11), tot, len(d["atoms"])


def c_core(box, meta, fld):
    return fc.core_mlow(box, meta, fld=fld)


def split8(b):
    """the A38 tree's child rule: bisect x, y and theta simultaneously (8 children)."""
    xm, ym, tm = 0.5 * (b.x0 + b.x1), 0.5 * (b.y0 + b.y1), 0.5 * (b.th0 + b.th1)
    out = []
    for (a0, a1) in ((b.x0, xm), (xm, b.x1)):
        for (c0, c1) in ((b.y0, ym), (ym, b.y1)):
            for (e0, e1) in ((b.th0, tm), (tm, b.th1)):
                out.append(Box(a0, a1, c0, c1, e0, e1))
    return out


def descend(box, meta, fld, thrs, maxdepth=8, beam=8):
    """beam descent; returns per-depth stats and, per threshold, the first depth with a kill.
    `depth` counts A38 tree levels (level-1 box = depth 1), so depth d+1 boxes are the 8 children."""
    cur = [box]
    per_depth = []
    first = {t: None for t in thrs}
    for d in range(2, maxdepth + 1):
        kids = []
        for b in cur:
            kids.extend(split8(b))
        vals = np.array([c_core(k, meta, fld) for k in kids])
        order = np.argsort(-vals)
        top = order[:beam]
        cur = [kids[i] for i in top]
        rec = dict(depth=d, n=len(kids), max=float(vals.max()), med=float(np.median(vals)))
        for t in thrs:
            n = int((vals > t).sum())
            rec["n_gt_%.4f" % t] = n
            if n and first[t] is None:
                first[t] = d
        per_depth.append(rec)
    return per_depth, first


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cert", default=fc.CERT_PATH)
    ap.add_argument("--thrs", default=None, help="comma list; default = 1+eta of the cert and 1.4254")
    ap.add_argument("--maxdepth", type=int, default=8)
    ap.add_argument("--beam", type=int, default=8)
    ap.add_argument("--n_parents", type=int, default=40)
    ap.add_argument("--grid", default=None, help="npz for the mask meta (only ht/hc are used)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()
    eta, tot, natoms = field_eta(a.cert)
    fld = fc.Field(a.cert)
    meta = fc.grid_geometry()          # ht/hc only: the one-cell inflation used by W1
    thrs = ([float(x) for x in a.thrs.split(",")] if a.thrs
            else sorted({round(1.0 + eta, 9), 1.425399552}))
    print("cert %s: atoms=%d total=%s eta=%.9f  thresholds=%s"
          % (os.path.basename(a.cert), natoms, tot, eta, thrs), flush=True)

    l1 = json.load(open(os.path.join(A38R, "l1_a38.json")))
    surv = [r for r in l1["matrix"] if r["status"] in ("undecided", "alive(LP)", "notrun")]
    # deterministic spread over the survivor list
    step = max(1, len(surv) // a.n_parents)
    parents = surv[::step][:a.n_parents]
    print("level-1 survivors: %d, descending %d" % (len(surv), len(parents)), flush=True)

    out = dict(cert=os.path.abspath(a.cert), eta_cert=eta, total=str(tot), n_atoms=natoms,
               thresholds=thrs, beam=a.beam, maxdepth=a.maxdepth, parents=[])
    agg = {t: [] for t in thrs}
    depth_max = {d: [] for d in range(2, a.maxdepth + 1)}
    for r in parents:
        b = r["box"]
        box = Box(b["x0"], b["x1"], b["y0"], b["y1"], b["th0"], b["th1"])
        c0 = c_core(box, meta, fld)
        pd, first = descend(box, meta, fld, thrs, a.maxdepth, a.beam)
        out["parents"].append(dict(idx=r["idx"], status=r["status"], c_core_l1=c0,
                                   per_depth=pd, first_kill={str(k): v for k, v in first.items()}))
        for t in thrs:
            agg[t].append(first[t])
        for rec in pd:
            depth_max[rec["depth"]].append(rec["max"])
    summ = {}
    for t in thrs:
        got = [x for x in agg[t] if x is not None]
        summ["thr_%.6f" % t] = dict(
            n_parents=len(agg[t]), n_with_kill=len(got),
            frac_parents_with_kill=len(got) / len(agg[t]) if agg[t] else 0.0,
            first_kill_min=(min(got) if got else None),
            first_kill_median=(float(np.median(got)) if got else None),
            first_kill_max=(max(got) if got else None))
    out["summary"] = summ
    out["c_core_max_by_depth"] = {str(d): dict(median=float(np.median(v)), max=float(max(v)))
                                  for d, v in depth_max.items() if v}
    out["wall"] = time.time() - t0
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump(out, open(a.out, "w"), indent=1)
    print(json.dumps(summ, indent=1), flush=True)
    print(json.dumps(out["c_core_max_by_depth"], indent=1), flush=True)
    print("-> %s  (%.0fs)" % (a.out, time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
