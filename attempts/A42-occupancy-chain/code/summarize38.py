#!/usr/bin/env python3
"""A38 task 3: kill matrix + summary -> results/l1_a38.json.

Reads the per-node checkpoints results/l1_nodes/node_XXX.rec.json (any of the 216 cover nodes
without one is 'notrun') and emits the kill matrix, aggregates, and the 3.84 comparison.
Re-runnable; preserves the extra sections ('w1_filter_ab', 'verification') if already present.
"""
from __future__ import annotations

import json, math, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")
NODEDIR = os.path.join(RES, "l1_nodes")
OUT = os.path.join(RES, "l1_a38.json")

KILL = ("w1kill", "dead(T1)")
SURV = ("alive(LP)", "undecided", "notrun", "error")

ANCHOR_384 = dict(where="A24/A27 level 1 at s = 96/25 = 3.84, same cover recipe, same LP, budget 10",
                  n=216, dead=117, alive=20, tau_quartiles=[9.00, 9.00, 9.56], tau_max=10.25,
                  median_seconds=655,
                  note="the 3.84 anchor's 117 dead includes T2 (wastage) kills; A38 level 1 ran T1 "
                       "(+ the W1/W2 node test) only, so the A38 kill count is a lower bound on the "
                       "same-recipe comparison")


def quart(v):
    v = sorted(x for x in v if x is not None and not (isinstance(x, float) and math.isnan(x)))
    if not v:
        return None
    def q(p):
        if len(v) == 1:
            return v[0]
        i = p * (len(v) - 1)
        lo, hi = int(math.floor(i)), int(math.ceil(i))
        return v[lo] + (v[hi] - v[lo]) * (i - lo)
    return dict(min=v[0], q1=q(0.25), median=q(0.5), q3=q(0.75), max=v[-1], n=len(v))


def main():
    cov = json.load(open(os.path.join(RES, "cover_l1.json")))
    scan = {d["idx"]: d for d in json.load(open(os.path.join(RES, "l1_node_scan.json")))["nodes"]}
    m = cov["s_float"] / 2.0
    rows = []
    for nd in cov["nodes"]:
        idx = nd["idx"]
        b = nd["box"]
        rp = os.path.join(NODEDIR, "node_%03d.rec.json" % idx)
        r = {}
        if os.path.exists(rp):
            try:
                r = json.load(open(rp))
            except Exception:
                r = {}
        cx, cy = (b["x0"] + b["x1"]) / 2.0, (b["y0"] + b["y1"]) / 2.0
        rows.append(dict(idx=idx, i=nd["i"], j=nd["j"], k=nd["k"], box=b,
                         theta_window=[b["th0"], b["th1"]],
                         dist_centre=math.hypot(cx - m, cy - m),
                         status=r.get("status", "notrun"),
                         tau=r.get("tau"), slack=r.get("slack"), minmass=r.get("minmass"),
                         maxcov=r.get("maxcov"),
                         c_core=r.get("c_core", scan[idx]["core_mlow"]),
                         thr_node=r.get("thr_node", scan[idx].get("thr_node")),
                         rows=r.get("rows"), orbits=r.get("orbits"), iters=r.get("iters"),
                         converged=r.get("converged"),
                         last_added_rows=r.get("last_added_rows"),
                         seconds=r.get("seconds"), error=r.get("error")))
    cnt = {}
    for r in rows:
        cnt[r["status"]] = cnt.get(r["status"], 0) + 1
    processed = [r for r in rows if r["status"] not in ("notrun",)]
    kills = [r for r in rows if r["status"] in KILL]
    surv = [r for r in rows if r["status"] in SURV]
    lp = [r for r in rows if r["tau"] is not None]
    agg = dict(
        n_total=len(rows), n_processed=len(processed), counts=cnt,
        f1_kills_over_processed=(len(kills) / len(processed)) if processed else None,
        f1_kills_over_216=len(kills) / len(rows),
        b_eff_processed=(8 * (1 - len(kills) / len(processed))) if processed else None,
        tau=quart([r["tau"] for r in lp]),
        seconds=quart([r["seconds"] for r in processed]),
        seconds_lp_only=quart([r["seconds"] for r in lp]),
        c_core=quart([r["c_core"] for r in rows]),
        n_c_core_gt1=sum(1 for r in rows if (r["c_core"] or 0) > 1.0),
        c_core_gt1_idx=[r["idx"] for r in rows if (r["c_core"] or 0) > 1.0],
        w1_node_kills=cnt.get("w1kill", 0),
        survivors=[dict(idx=r["idx"], i=r["i"], j=r["j"], k=r["k"], status=r["status"],
                        tau=r["tau"], maxcov=r["maxcov"], dist=r["dist_centre"])
                   for r in sorted(surv, key=lambda x: x["idx"])],
        survivor_cells=sorted({(r["i"], r["j"]) for r in surv}),
        survivor_theta_windows=sorted({r["k"] for r in surv}),
    )
    old = {}
    if os.path.exists(OUT):
        try:
            old = json.load(open(OUT))
        except Exception:
            old = {}
    doc = dict(format="A38-level1-kill-matrix-v1", when=time.strftime("%Y-%m-%dT%H:%M:%S"),
               s=cov["s"], s_float=cov["s_float"], budget=cov["budget"], CW=cov["CW"],
               config=dict(w1_lp_row_filter=False, w1w2_node_test=True, time_limit=480,
                           eps_geo=1e-4, workers=6, order="interior-first",
                           statuses="w1kill | dead(T1) | alive(LP) | undecided | notrun",
                           note="A27 semantics: kill needs converged-feasible LP (added_rows==0, "
                                "minmass>=1) with tau < budget; alive(LP) needs converged tau >= "
                                "budget and maxcov <= 1+1e-3; T2 (wastage) not run at level 1"),
               anchor_3p84=ANCHOR_384, aggregate=agg, matrix=rows)
    for k in ("root", "w1_filter_ab", "verification"):
        if k in old:
            doc[k] = old[k]
    rt = os.path.join(RES, "root_s0.json")
    if os.path.exists(rt):
        try:
            d = json.load(open(rt))
            doc["root"] = {k: v for k, v in d.items() if k not in ("atoms", "weights")}
        except Exception:
            pass
    json.dump(doc, open(OUT, "w"), indent=1)
    print(json.dumps(dict(counts=cnt, f1_proc=agg["f1_kills_over_processed"],
                          f1_216=agg["f1_kills_over_216"], tau=agg["tau"],
                          seconds=agg["seconds"], n_c_gt1=agg["n_c_core_gt1"],
                          survivor_cells=[list(c) for c in agg["survivor_cells"]]), indent=1))
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
