"""A116 T2 -- the selection tree on S02 (k5_11 frame) and S07 (trump5 frame) over the (r, rho) grid.

Per run: bodies = class pins (A57 slack cores) + one box per load-bearing square (anchored at s0
by dilation), the tree (phase 1 = the kill; phase 2 = tightening of the certified bound up to a
budget), and for every DEAD verdict the measured checks: >= 10^4 sampled configurations in N
(none may be a packing at side <= s0), the box-constrained SLSQP minimum over N (the measured
chain minimum), and the Trump canary (no D4 image of Trump satisfies N's hypothesis).

Usage: python run116.py <job>   job in {S02, S07, extras}
Appends to results/t2_<job>.jsonl (resumable: finished (tag, cls, r, rho, cut, slack, L) are skipped).
"""
from __future__ import annotations
import argparse, json, math, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a116lib as A

R_GRID = (0.02, 0.05, 0.1, 0.2, 0.3)
RHO_GRID = (2.0, 5.0, 10.0, 20.0, 40.0)
THETA_CUT_T = round(A.THETA_T + 0.02, 3)     # 40.202: just above F_T(theta) = s0 (theta_T + 0.02 deg)
THETA_CUT_C = 41.565                          # the S07 family's grain boundary (A110)


def one_run(tag, cls, r, rho, cut, slack, log, time_cap, tighten_cap, n_samples, starts,
            anchor=A.S0, loadbearing=None, s_hi=A.S_HI_DEFAULT, ceil=None, label="", slot_radius=None):
    t0 = time.time()
    bodies, nv, s_sh, P = A.build_bodies(tag, cls, r, rho, anchor_side=anchor, pin_slack=slack,
                                         tilt_floor_deg=cut, tilt_ceil_deg=ceil, loadbearing=loadbearing,
                                         slot_radius=slot_radius)
    _, Pe, _, _ = A.anchored(tag, s_sh)
    ss = A.shadow_selections(bodies, Pe)
    margin = s_sh - A.S0
    T = A.Tree(bodies, nv, s_hi=s_hi, contact_pairs=list(ss), min_cell_deg=0.05, node_cap=2000000,
               time_cap=time_cap, target=A.S0 + 0.9 * margin, tighten_cap=tighten_cap)
    v = T.run()
    rec = dict(tag=tag, cls=cls, r=r, rho=rho, cut=cut, ceil=ceil, pin_slack=slack, anchor=anchor, label=label, slot_radius=slot_radius,
               bodies=[b.name for b in bodies], loadbearing=[b.name for b in bodies if b.kind == "free"],
               tree=v, seconds_tree=round(time.time() - t0, 1))
    rec["witnesses"] = T.witnesses[:5]
    rec["unresolved"] = T.unresolved[:5]
    rec["n_witnesses"] = len(T.witnesses)
    rec["n_unresolved"] = len(T.unresolved)
    if v["dead"]:
        t1 = time.time()
        rec["trump"] = A.trump_in_N(bodies, pin_slack=slack)
        rec["sampling"] = A.sample_check(bodies, nv, n_samples=n_samples, seed=int(1000 * r + rho))
        rec["local_min"] = A.local_min(bodies, nv, starts=starts, seed=7)
        rec["seconds_checks"] = round(time.time() - t1, 1)
    else:
        rec["trump"] = A.trump_in_N(bodies, pin_slack=slack)
    rec["seconds"] = round(time.time() - t0, 1)
    st = v["stats"]
    log("%s/%s r=%.3f rho=%4.1f cut=%s h=%.4f %s: %s  near %d  leaves(int) %d  nodes %d  closed %d  branch %d  bisect %d  qsplit %d  "
        "certmin %s  lm %s  samp hits %s  trump %s  (%.0fs)" %
        (tag, cls, r, rho, cut, slack, label, "DEAD" if v["dead"] else ("CAPPED" if v["capped"] else "ALIVE(%d wit,%d unres)" % (rec["n_witnesses"], rec["n_unresolved"])),
         v["n_near"], v["leaves_after_interval"], st["nodes"], v["n_closed"], st["branch"], st["bisect"], st["qsplit"],
         ("%.6f" % v["certified_min"]) if v["certified_min"] else "-",
         ("%.6f" % rec["local_min"]["side"]) if rec.get("local_min") else "-",
         rec["sampling"]["hits"] if rec.get("sampling") else "-",
         rec["trump"]["inside"], rec["seconds"]))
    if T.witnesses:
        w = T.witnesses[0]
        log("   witness side %.6f valid %s cells %s" % (w["witness_side"], w["witness_valid"], w["cells"]))
        log("   witness fixed %s" % w["fixed"])
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("job")
    ap.add_argument("--time_cap", type=float, default=900.0)
    ap.add_argument("--tighten_cap", type=int, default=4000)
    ap.add_argument("--samples", type=int, default=10000)
    ap.add_argument("--starts", type=int, default=30)
    a = ap.parse_args()
    out = os.path.join(A.RES, "t2_%s.jsonl" % a.job)
    logp = os.path.join(A.LOGS, "t2_%s.log" % a.job)

    def log(*x):
        s = " ".join(str(v) for v in x)
        print(s, flush=True)
        with open(logp, "a") as f:
            f.write(time.strftime("[%H:%M:%S] ") + s + "\n")

    done = set()
    if os.path.exists(out):
        for line in open(out):
            try:
                d = json.loads(line)
                done.add((d["tag"], d["cls"], d["r"], d["rho"], d["cut"], round(d["pin_slack"], 6), d["label"]))
            except Exception:
                pass
    jobs = []
    if a.job == "S02":
        for rho in RHO_GRID:
            for r in R_GRID:
                jobs.append(dict(tag="S02", cls="k5_11", r=r, rho=rho, cut=None, slack=A.PIN_SLACK, label="grid"))
    elif a.job == "S07":
        for rho in RHO_GRID:
            for r in R_GRID:
                jobs.append(dict(tag="S07", cls="trump5", r=r, rho=rho, cut=THETA_CUT_C, slack=A.PIN_SLACK, label="cut41.565"))
        for rho in (2.0, 5.0, 10.0):
            for r in (0.02, 0.05, 0.1):
                jobs.append(dict(tag="S07", cls="trump5", r=r, rho=rho, cut=None, slack=A.PIN_SLACK, label="nocut"))
        for rho in (5.0, 10.0, 20.0):
            for r in (0.05, 0.1, 0.2):
                jobs.append(dict(tag="S07", cls="trump5", r=r, rho=rho, cut=THETA_CUT_T, slack=A.PIN_SLACK, label="cutT"))
    elif a.job == "extras":
        jobs.append(dict(tag="S02", cls="k5_11", r=1e-6, rho=1e-4, cut=None, slack=0.0, label="canary_r0_exactpins_anchor_sstar",
                         anchor=A.L11.S02_S, s_hi=4.6))
        jobs.append(dict(tag="S07", cls="trump5", r=1e-6, rho=1e-4, cut=None, slack=0.0, label="canary_r0_exactpins_anchor_sstar",
                         anchor=A.L11.S07_S, s_hi=4.6))
        for (tag, cls) in (("S02", "k5_11"), ("S07", "trump5")):
            for (r, rho) in ((0.05, 5.0), (0.1, 10.0)):
                jobs.append(dict(tag=tag, cls=cls, r=r, rho=rho, cut=(THETA_CUT_C if tag == "S07" else None), slack=0.0, label="exactpins"))
        for (r, rho) in ((0.1, 10.0), (0.2, 20.0)):
            jobs.append(dict(tag="S07", cls="trump5", r=r, rho=rho, cut=THETA_CUT_C, slack=A.PIN_SLACK, label="with_f1",
                             loadbearing=("f0", "f1", "f2", "f4")))
        for (r, rho) in ((0.05, 5.0), (0.1, 10.0), (0.2, 20.0)):
            jobs.append(dict(tag="S02", cls="k5_16", r=r, rho=rho, cut=None, slack=A.PIN_SLACK, label="k5_16frame"))
        # the PI route: N at the minimum of the chain contacts' forced radii (stability.json, kappa = 100)
        jobs.append(dict(tag="S07", cls="trump5", r=0.024, rho=2.4, cut=None, slack=A.PIN_SLACK, label="PI_N_single_leaf"))
        jobs.append(dict(tag="S02", cls="k5_11", r=0.019, rho=1.9, cut=None, slack=A.PIN_SLACK, label="PI_N_single_leaf"))
        # S02 upper tilt cut (the mirror Trump boundary D = s0 at 49.818 deg) if the grid finds the D leaf live
        for (r, rho) in ((0.1, 10.0), (0.2, 20.0)):
            jobs.append(dict(tag="S02", cls="k5_11", r=r, rho=rho, cut=None, ceil=49.80, slack=A.PIN_SLACK, label="ceil49.80"))
        # the slot square BR(0,1) kept near its slot (radius 0.05) while the tilted squares get the full r
        for (r, rho) in ((0.3, 2.0), (0.3, 5.0), (0.3, 10.0)):
            jobs.append(dict(tag="S02", cls="k5_11", r=r, rho=rho, cut=None, slack=A.PIN_SLACK, label="slot_r0.05", slot_radius=0.05))
        # S02 with the strut f0 and TR(0,0) as extra boxes: does the diagonal dip beyond 49.8 deg go away?
        for (r, rho) in ((0.1, 5.0), (0.1, 10.0)):
            jobs.append(dict(tag="S02", cls="k5_11", r=r, rho=rho, cut=None, slack=A.PIN_SLACK, label="with_f0_TR",
                             loadbearing=("f1", "f2", "f3", "f0", "TR(0,0)"), slot_radius=0.05))
    for j in jobs:
        key = (j["tag"], j["cls"], j["r"], j["rho"], j["cut"], round(j["slack"], 6), j["label"])
        if key in done:
            continue
        try:
            rec = one_run(j["tag"], j["cls"], j["r"], j["rho"], j["cut"], j["slack"], log, a.time_cap, a.tighten_cap,
                          a.samples, a.starts, anchor=j.get("anchor", A.S0), loadbearing=j.get("loadbearing"),
                          s_hi=j.get("s_hi", A.S_HI_DEFAULT), ceil=j.get("ceil"), label=j["label"],
                          slot_radius=j.get("slot_radius"))
        except Exception as e:
            log("ERROR %s: %r" % (j, e))
            continue
        with open(out, "a") as f:
            f.write(json.dumps(rec) + "\n")
    log("job %s done" % a.job)


if __name__ == "__main__":
    main()
