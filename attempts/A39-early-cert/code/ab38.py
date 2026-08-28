#!/usr/bin/env python3
"""A38 task 4: attribution sample -- re-run a stratified set of level-1 nodes with the W1 LP ROW
FILTER ON and compare tau against the filter-OFF campaign run (expected delta-tau = 0, plus the
row-drop counters).  Appends 'w1_filter_ab' to results/l1_a38.json.

Strata: 2 interior already-dead (smallest distance to the container centre), 3 mid (median
distance band), 3 survivors (alive(LP)/undecided; padded with the largest-tau dead if short).

    python ab38.py --workers 6 --time_limit 480
"""
from __future__ import annotations

import argparse, json, os, sys, time, traceback
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import concurrent.futures as cf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
RES = os.path.join(HERE, "..", "results")
LOGS = os.path.join(HERE, "..", "logs")
ABDIR = os.path.join(RES, "l1_ab_w1on")
S0F = 3.877084


def _work(args):
    idx, bjson, budget, tl, eps_geo = args
    t0 = time.time()
    try:
        import node38
        from caselp import Box
        os.makedirs(ABDIR, exist_ok=True)
        lg = os.path.join(LOGS, "l1", "ab%03d.log" % idx)

        def log(*a):
            with open(lg, "a") as f:
                f.write(" ".join(str(x) for x in a) + "\n")
        r = node38.solve_a38_node(S0F, [Box.from_json(bjson)], budget, w1=True, w2=True,
                                  time_limit=tl, out=None, log=log, eps_geo=eps_geo,
                                  sym_kind="C1", theta_box="0-90")
        rec = dict(idx=idx, status=r["status"], tau=r.get("tau"), minmass=r.get("minmass"),
                   maxcov=r.get("maxcov"), rows=r.get("n_rows"), iters=r.get("iters"),
                   converged=r.get("converged"), filter=r.get("filter"),
                   field=r.get("field"), seconds=time.time() - t0)
        json.dump(rec, open(os.path.join(ABDIR, "ab_%03d.json" % idx), "w"), indent=1)
        return rec
    except Exception:
        return dict(idx=idx, status="error", error=traceback.format_exc()[-1200:],
                    seconds=time.time() - t0)


def pick(mat, n_int=2, n_mid=3, n_surv=3):
    dead = sorted([r for r in mat if r["status"] == "dead(T1)"], key=lambda r: r["dist_centre"])
    surv = [r for r in mat if r["status"] in ("alive(LP)", "undecided")]
    sel, why = [], {}
    for r in dead[:n_int]:
        sel.append(r); why[r["idx"]] = "interior-dead"
    if dead:
        h = len(dead) // 2
        for r in dead[max(0, h - n_mid // 2): max(0, h - n_mid // 2) + n_mid]:
            if r["idx"] not in why:
                sel.append(r); why[r["idx"]] = "mid-dead"
    surv = sorted(surv, key=lambda r: -(r["tau"] or 0))
    for r in surv[:n_surv]:
        sel.append(r); why[r["idx"]] = "survivor(%s)" % r["status"]
    if len(sel) < n_int + n_mid + n_surv:      # pad with the hardest dead nodes
        for r in sorted(dead, key=lambda r: -(r["tau"] or 0)):
            if r["idx"] not in why:
                sel.append(r); why[r["idx"]] = "pad-hardest-dead"
            if len(sel) >= n_int + n_mid + n_surv:
                break
    return sel, why


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--time_limit", type=float, default=480)
    ap.add_argument("--budget", type=int, default=10)
    ap.add_argument("--eps_geo", type=float, default=1e-4)
    a = ap.parse_args()
    os.makedirs(ABDIR, exist_ok=True)
    os.makedirs(os.path.join(LOGS, "l1"), exist_ok=True)
    p = os.path.join(RES, "l1_a38.json")
    d = json.load(open(p))
    mat = {r["idx"]: r for r in d["matrix"]}
    sel, why = pick([r for r in d["matrix"] if r["status"] not in ("notrun", "error")])
    print("A/B sample:", [(r["idx"], why[r["idx"]]) for r in sel], flush=True)
    t0 = time.time()
    jobs = [(r["idx"], r["box"], a.budget, a.time_limit, a.eps_geo) for r in sel]
    out = []
    with cf.ProcessPoolExecutor(max_workers=a.workers) as ex:
        for rec in ex.map(_work, jobs):
            base = mat[rec["idx"]]
            rec["stratum"] = why[rec["idx"]]
            rec["tau_off"] = base["tau"]
            rec["status_off"] = base["status"]
            rec["delta_tau"] = (None if (rec.get("tau") is None or base["tau"] is None)
                                else rec["tau"] - base["tau"])
            rec["seconds_off"] = base["seconds"]
            out.append(rec)
            print("  node %3d %-18s tau_on=%s tau_off=%s dtau=%s rows_dropped_w1=%s "
                  "w2=%s  %.0fs (off %.0fs)"
                  % (rec["idx"], rec["stratum"],
                     ("%.5f" % rec["tau"]) if rec.get("tau") is not None else "-",
                     ("%.5f" % base["tau"]) if base["tau"] is not None else "-",
                     ("%+.2e" % rec["delta_tau"]) if rec["delta_tau"] is not None else "-",
                     (rec.get("filter") or {}).get("rows_dropped_w1"),
                     (rec.get("filter") or {}).get("rows_dropped_w2"),
                     rec["seconds"], base["seconds"] or -1), flush=True)
    out.sort(key=lambda r: r["idx"])
    dts = [r["delta_tau"] for r in out if r["delta_tau"] is not None]
    d["w1_filter_ab"] = dict(
        when=time.strftime("%Y-%m-%dT%H:%M:%S"), n=len(out), time_limit=a.time_limit,
        max_abs_delta_tau=(max(abs(x) for x in dts) if dts else None),
        n_status_changed=sum(1 for r in out if r["status_off"] != r.get("status")),
        median_wall_ratio=(sorted(r["seconds"] / r["seconds_off"] for r in out
                                  if r.get("seconds_off"))[len(out) // 2] if out else None),
        records=out, seconds=time.time() - t0)
    json.dump(d, open(p, "w"), indent=1)
    print("appended w1_filter_ab to", p, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
