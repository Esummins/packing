"""A119 T3 -- the blocking squares as boxes (does the radius grow past A116's 0.2?) and the
rho >= 20 deg time cap with the accelerated tree.

Jobs
  S02b   S02 / k5_11 with the blocking squares of the r = 0.3 limiter added as boxes:
         L = f1, f2, f3, BR(0,1) + f0 + TR(0,0)          (A116 sec 5, "the r = 0.3 limiter, dissected")
  S07b   S07 / trump5 with the ladder's blockers added as boxes:
         L = f0, f2, f4 + f1 + f3 + BL(0,2)              (A116 sec 5, S07 limiter)
  cap    the ORIGINAL L at the cells that hit A116's 900 s cap: (0.2, 20 deg), (0.2, 40 deg)
  base   A116's own (r, rho) re-run with the A119 tree (regression + wall comparison)

Every DEAD verdict is followed by A116's measured checks (>= 10^4 samples in N, the SLSQP
minimum, the Trump canary).  Appends to results/t3_<job>.jsonl (resumable).

Read-only on A116 and on every campaign.  <= 2 processes, BLAS pinned via a116lib -> blas1.
"""
from __future__ import annotations
import argparse, json, math, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a119lib as L
import a116lib as A

CUT_C = 41.565

S02_BLOCK = ("f1", "f2", "f3", "f0", "TR(0,0)")     # + BR(0,1) auto (load-bearing slot square)
S07_BLOCK = ("f0", "f2", "f4", "f1", "f3", "BL(0,2)")


def one(job, tag, cls, r, rho, cut, label, loadbearing, slot_radius, time_cap, samples, starts, log):
    t0 = time.time()
    bodies, nv, s_sh, P = A.build_bodies(tag, cls, r, rho, anchor_side=A.S0, pin_slack=A.PIN_SLACK,
                                         tilt_floor_deg=cut, loadbearing=loadbearing,
                                         slot_radius=slot_radius)
    _, Pe, _, _ = A.anchored(tag, s_sh)
    ss = A.shadow_selections(bodies, Pe)
    T = L.RecTree(bodies, nv, contact_pairs=list(ss), min_cell_deg=0.05, node_cap=4000000,
                  time_cap=time_cap, record=False, inherit=False)
    v = T.run()
    rec = dict(job=job, tag=tag, cls=cls, r=r, rho=rho, cut=cut, label=label,
               slot_radius=slot_radius,
               bodies=[b.name for b in bodies],
               loadbearing=[b.name for b in bodies if b.kind == "free"],
               tree=v, seconds_tree=round(time.time() - t0, 1))
    rec["n_witnesses"] = len(T.witnesses)
    rec["n_unresolved"] = len(T.unresolved)
    rec["witnesses"] = T.witnesses[:3]
    rec["unresolved"] = T.unresolved[:3]
    rec["trump"] = A.trump_in_N(bodies, pin_slack=A.PIN_SLACK)
    if v["dead"]:
        t1 = time.time()
        rec["sampling"] = A.sample_check(bodies, nv, n_samples=samples, seed=int(1000 * r + rho))
        rec["local_min"] = A.local_min(bodies, nv, starts=starts, seed=7)
        rec["seconds_checks"] = round(time.time() - t1, 1)
    rec["seconds"] = round(time.time() - t0, 1)
    st = v["stats"]
    log("%s %s/%s r=%.2f rho=%4.1f cut=%s L=%d %-12s: %-10s nodes %-7d lp %-7d inh %-6d qdrop %d "
        "near %d closed %d  certmin %s  lm %s  samp %s  trump %s  (%.0fs)" %
        (job, tag, cls, r, rho, cut, len(rec["loadbearing"]), label,
         "DEAD" if v["dead"] else ("CAP" if v["capped"] else "ALIVE(%dw,%du)" % (rec["n_witnesses"], rec["n_unresolved"])),
         st["nodes"], st["lp_calls"], st["dead_inherited"], st["qdrop"], v["n_near"], v["n_closed"],
         ("%.6f" % v["certified_min"]) if v["certified_min"] else "-",
         ("%.6f" % rec["local_min"]["side"]) if rec.get("local_min") else "-",
         rec["sampling"]["hits"] if rec.get("sampling") else "-",
         rec["trump"]["inside"], rec["seconds"]))
    if T.witnesses:
        w = T.witnesses[0]
        log("   witness side %.6f valid %s  cfg %s" % (w["witness_side"], w["witness_valid"],
                                                       json.dumps(w.get("witness_cfg", {}))[:400]))
    return rec


def jobs_for(job):
    J = []
    if job == "S02b":
        for (r, rho) in ((0.2, 10.0), (0.3, 10.0), (0.2, 20.0), (0.4, 10.0), (0.3, 20.0), (0.4, 20.0)):
            J.append(dict(tag="S02", cls="k5_11", r=r, rho=rho, cut=None, label="block_f0_TR",
                          loadbearing=S02_BLOCK, slot_radius=None))
    elif job == "S07b":
        for (r, rho) in ((0.2, 10.0), (0.3, 10.0), (0.2, 20.0), (0.4, 10.0), (0.3, 20.0), (0.4, 20.0)):
            J.append(dict(tag="S07", cls="trump5", r=r, rho=rho, cut=CUT_C, label="block_f1_f3_BL02",
                          loadbearing=S07_BLOCK, slot_radius=None))
    elif job in ("S02e", "S07e"):
        # the frontier ladder with the blocking boxes: easy first, then the slot square confined
        tag, cls, cut, lb = ("S02", "k5_11", None, S02_BLOCK) if job == "S02e"             else ("S07", "trump5", CUT_C, S07_BLOCK)
        lab = "block_ladder"
        for (r, rho, sr) in ((0.1, 10.0, None), (0.15, 10.0, None), (0.2, 5.0, None),
                             (0.2, 10.0, 0.05), (0.3, 10.0, 0.05), (0.4, 10.0, 0.05),
                             (0.3, 20.0, 0.05)):
            J.append(dict(tag=tag, cls=cls, r=r, rho=rho, cut=cut, label=lab,
                          loadbearing=lb, slot_radius=sr))
    elif job == "block2":
        # the promising points of the blocking-box route: narrower tilt (rho = 5 deg) where the
        # six-box tree can still close, and the slot square confined to 0.05 at r >= 0.2
        for (tag, cls, cut, lb) in (("S02", "k5_11", None, S02_BLOCK),
                                    ("S07", "trump5", CUT_C, S07_BLOCK)):
            for (r, rho, sr) in ((0.1, 5.0, None), (0.2, 5.0, None), (0.2, 10.0, 0.05)):
                J.append(dict(tag=tag, cls=cls, r=r, rho=rho, cut=cut, label="block_ladder",
                              loadbearing=lb, slot_radius=sr))
    elif job == "block3":
        # do the blocking boxes kill the ALIVE cells the `cap` job found with the original L?
        J.append(dict(tag="S07", cls="trump5", r=0.2, rho=20.0, cut=CUT_C, label="block_vs_alive",
                      loadbearing=S07_BLOCK, slot_radius=None))
        J.append(dict(tag="S07", cls="trump5", r=0.2, rho=40.0, cut=CUT_C, label="block_vs_alive",
                      loadbearing=S07_BLOCK, slot_radius=None))
        J.append(dict(tag="S02", cls="k5_11", r=0.2, rho=40.0, cut=None, label="block_vs_alive",
                      loadbearing=S02_BLOCK, slot_radius=None))
        J.append(dict(tag="S02", cls="k5_11", r=0.2, rho=20.0, cut=None, label="block_vs_alive",
                      loadbearing=S02_BLOCK, slot_radius=None))
    elif job == "cap":
        for (tag, cls, cut) in (("S02", "k5_11", None), ("S07", "trump5", CUT_C)):
            for (r, rho) in ((0.2, 20.0), (0.2, 40.0)):
                J.append(dict(tag=tag, cls=cls, r=r, rho=rho, cut=cut, label="cap_original_L",
                              loadbearing=None, slot_radius=None))
    elif job == "base":
        for (tag, cls, cut) in (("S02", "k5_11", None), ("S07", "trump5", CUT_C)):
            for (r, rho) in ((0.1, 10.0), (0.2, 10.0)):
                J.append(dict(tag=tag, cls=cls, r=r, rho=rho, cut=cut, label="base_A119tree",
                              loadbearing=None, slot_radius=None))
    else:
        raise SystemExit("unknown job")
    return J


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("job")
    ap.add_argument("--time_cap", type=float, default=1200.0)
    ap.add_argument("--samples", type=int, default=10000)
    ap.add_argument("--starts", type=int, default=30)
    a = ap.parse_args()
    out = os.path.join(L.RES, "t3_%s.jsonl" % a.job)
    logp = os.path.join(L.LOGS, "t3_%s.log" % a.job)

    def log(*x):
        s = " ".join(str(v) for v in x)
        print(s, flush=True)
        with open(logp, "a", encoding="utf-8") as f:
            f.write(time.strftime("[%H:%M:%S] ") + s + "\n")

    done = set()
    if os.path.exists(out):
        for line in open(out, encoding="utf-8"):
            try:
                d = json.loads(line)
                done.add((d["tag"], d["cls"], d["r"], d["rho"], d["cut"], d["label"], d.get("slot_radius")))
            except Exception:
                pass
    for j in jobs_for(a.job):
        key = (j["tag"], j["cls"], j["r"], j["rho"], j["cut"], j["label"], j["slot_radius"])
        if key in done:
            continue
        try:
            rec = one(a.job, j["tag"], j["cls"], j["r"], j["rho"], j["cut"], j["label"],
                      j["loadbearing"], j["slot_radius"], a.time_cap, a.samples, a.starts, log)
        except Exception as e:
            log("ERROR %s: %r" % (j, e))
            continue
        with open(out, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
    log("job %s done" % a.job)


if __name__ == "__main__":
    main()
