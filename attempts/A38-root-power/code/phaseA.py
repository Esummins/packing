#!/usr/bin/env python3
"""A38 depth-probe PHASE A: census of the 172 level-1 survivors + the tree-level Trump canary.

(1) Build the survivor box list (alive(LP) + undecided + notrun) from results/l1_a38.json and run
    census38 classification on each -> results/census_l1survivors.json
(2) CANARY: for every one of the 216 level-1 cells decide whether it CONTAINS a D4 image of a
    family-0 (Trump) placement (exact containment: d_center == 0 and d_theta == 0).  A cell that
    contains one and is classified dead(T1) is a SOUNDNESS ALARM.
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
RES = os.path.join(HERE, "..", "results")

import census38 as cen  # noqa: E402


def box_of(r):
    b = r["box"]
    return [b["x0"], b["x1"], b["y0"], b["y1"], b["th0"], b["th1"]]


def main():
    t0 = time.time()
    mat = json.load(open(os.path.join(RES, "l1_a38.json")))["matrix"]
    A = cen.Atlas()

    # ---------------------------------------------------------------- (2) the canary, all 216
    trump = A.trump[0]
    canary = []
    for r in mat:
        x0, x1, y0, y1, th0, th1 = box_of(r)
        hits = []
        for mode in ("s0", "scaled"):
            for gname, P, TH in trump["img_" + mode]:
                dc = cen.center_dist_many(P, x0, x1, y0, y1)
                dt = cen.theta_dist_deg_many(TH, th0, th1)
                inside = np.where((dc <= 0.0) & (dt <= 0.0))[0]
                for i in inside:
                    hits.append(dict(mode=mode, d4=gname, placement=int(i),
                                     xytheta=[float(P[i, 0]), float(P[i, 1]), float(TH[i])]))
        if hits:
            canary.append(dict(idx=r["idx"], i=r["i"], j=r["j"], k=r["k"], box=box_of(r),
                               status=r["status"], tau=r.get("tau"),
                               kill_label=r.get("kill_label"), n_hits=len(hits), hits=hits))
    alarms = [c for c in canary if c["status"].startswith("dead")]
    print("CANARY: %d of 216 level-1 cells contain a D4 image of a Trump placement" % len(canary))
    for c in canary:
        print("   idx=%3d (i%d j%d k%d) status=%-10s tau=%s  hits=%d  first=%s"
              % (c["idx"], c["i"], c["j"], c["k"], c["status"],
                 ("%.4f" % c["tau"]) if c["tau"] is not None else "-", c["n_hits"],
                 json.dumps(c["hits"][0])))
    print("CANARY VERDICT:", "ALARM -- %d dead Trump cells: %s" % (len(alarms),
          [c["idx"] for c in alarms]) if alarms else "OK (no Trump-containing cell is dead)")

    # ------------------------------------------------------------- (1) census of the survivors
    SURV = ("alive(LP)", "undecided", "notrun")
    surv = [r for r in mat if r["status"] in SURV]
    print("\nsurvivors: %d (%s)" % (len(surv), {s: sum(1 for r in surv if r["status"] == s)
                                                for s in SURV}))
    recs, tally = [], {}
    per_status = {}
    for r in surv:
        b = tuple(box_of(r))
        c = A.classify(b, mode="s0")
        alt = A.classify(b, mode="scaled", topk=1)
        rec = dict(idx=r["idx"], i=r["i"], j=r["j"], k=r["k"], box=list(b),
                   status=r["status"], tau=r.get("tau"), maxcov=r.get("maxcov"),
                   c_core=r.get("c_core"), dist_centre=r.get("dist_centre"),
                   classification=c["classification"],
                   trump=c["trump"], nearest_other=c["nearest_other"], nearest=c["nearest"][:3],
                   alt_mode=dict(mode="scaled", classification=alt["classification"],
                                 trump=alt["trump"], nearest_other=alt["nearest_other"]))
        recs.append(rec)
        tally[c["classification"]] = tally.get(c["classification"], 0) + 1
        d = per_status.setdefault(r["status"], {})
        d[c["classification"]] = d.get(c["classification"], 0) + 1
    print("CENSUS all survivors:", json.dumps(tally))
    print("CENSUS by status:", json.dumps(per_status))
    print("CENSUS alive(LP) detail:")
    for r in recs:
        if r["status"] == "alive(LP)":
            print("   idx=%3d %-18s trump(d_c=%.4f d_th=%.3f %s#%d) other(e%d fam%s d_c=%.4f "
                  "d_th=%.3f) dist_centre=%.4f"
                  % (r["idx"], r["classification"], r["trump"]["d_center"],
                     r["trump"]["d_theta_deg"], r["trump"]["d4"], r["trump"]["placement"],
                     r["nearest_other"]["entry"], r["nearest_other"]["family_id"],
                     r["nearest_other"]["d_center"], r["nearest_other"]["d_theta_deg"],
                     r["dist_centre"]))

    # geography summary
    geo = {}
    for r in recs:
        key = r["status"]
        g = geo.setdefault(key, dict(n=0, dist=[], tau=[]))
        g["n"] += 1
        g["dist"].append(r["dist_centre"])
        if r["tau"] is not None:
            g["tau"].append(r["tau"])
    for k, g in geo.items():
        g["dist_min"] = min(g["dist"]); g["dist_max"] = max(g["dist"])
        g["dist_median"] = float(np.median(g["dist"]))
        if g["tau"]:
            g["tau_min"] = min(g["tau"]); g["tau_max"] = max(g["tau"])
            g["tau_median"] = float(np.median(g["tau"]))
        del g["dist"], g["tau"]
    print("GEOGRAPHY:", json.dumps(geo, indent=1))

    out = dict(format="A38-census-l1survivors-v1", when=time.strftime("%Y-%m-%dT%H:%M:%S"),
               s0=A.s0, mode="s0", tol_center=cen.TOL_C, tol_theta_deg=cen.TOL_TH,
               n_survivors=len(recs), tally=tally, tally_by_status=per_status, geography=geo,
               canary=dict(n_cells_with_trump_image=len(canary),
                           n_dead_trump_cells=len(alarms),
                           alarm=bool(alarms),
                           dead_idx=[c["idx"] for c in alarms],
                           cells=canary),
               records=recs, seconds=time.time() - t0)
    p = os.path.join(RES, "census_l1survivors.json")
    json.dump(out, open(p, "w"), indent=1)
    print("->", p, "in %.1f s" % (time.time() - t0))


if __name__ == "__main__":
    main()
