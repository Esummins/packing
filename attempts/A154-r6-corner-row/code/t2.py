"""A115 T2 -- Lemma CW corner incidence rows in a k0_00 NODE LP.

For one alive K01 cell (hypothesis = the node's OWN conditioned box, copied into
results/nodes/<nid>.src.json) and one delta:

    rhs(Q) = 1 + e * [Q in the dilated outer cover G of U_c F_c(a_w(delta))]
    budget = budget0 + floor(e * B),   B = 8 - sum over the node's CORES of r_max(B+)

Lemma CW guarantees 8 corner-crowd incidences among the eleven squares (two per corner; the four
widened corner boxes are s0 - 2 a_w > sqrt2 apart, so a unit square carries at most ONE of them
and the incidence budget is exact -- no A109-style multiplicity re-pricing).  The k conditioned
squares are exempt from the LP rows (charged to their cores) and can carry at most r_max(B+) of
the eight, so the squares the LP still pays for carry >= B.

PROTOCOL (PI, 2026-09-06).
  stage 1  LP at 240 s (with a 60 s probe: tau >= budget at the probe is a sound refusal -- tau
           is a lower bound that only rises as rows are added -- so the cell is alive and the run
           stops there).  eta = tau - budget.
             eta <= -1e-3  -> KILL CANDIDATE: goes straight to the A92 two-run frozen
                              certification (certify115.py), converged or not.  The CERTIFICATE
                              is the verdict; the LP value never is.
             |eta| < 1e-6  -> knife edge: stage 2.
             else          -> alive.
  stage 2  the knife-edge cells only, 900 s cap (--stage2).

Decision rule for e (A109's, valid because tau(e) is the optimum of an LP whose rhs is affine in
e, hence convex and increasing, so c(e) = (tau(e) - tau0)/e is non-decreasing): a kill at e needs
c(e) < B; if the smallest e that buys a bonus already returns c >= B, no larger e can kill.
"""
import argparse
import json
import math
import os
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import blas1  # noqa: F401  -- MUST precede numpy
import a115lib as L
import lpbox92
import crowdfam92 as CF
from caselp92 import Box, Hyp, solve_node, warm_from_result

RECD = os.path.join(L.RES, "rec")
os.makedirs(RECD, exist_ok=True)
SINK = os.path.join(L.RES, "t2_runs.jsonl")
CFGS = {"d0": 0.0, "d0.05": 0.05, "d0.1": 0.1}
KNIFE = 1e-6
KILL = 1e-3

LPKW = dict(sym_kind="C1", max_iter=900, out=None, log=lambda *x: None,
            prune=0, prune_cols=3, col_stop_iter=10 ** 6, col_stop_cov=1.002,
            max_cols_add=400, max_rows_add=2000, fine_slack=99.0, alternate=True)


def _put(rec):
    with open(SINK, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


_WARM0 = {}


def root_warm():
    """fallback warm pool for a cell with no LP result of its own (crowd92.warm_pool sources):
    A38's root_s0 certificate atoms."""
    if "w" in _WARM0:
        return _WARM0["w"]
    atoms, seen = [], set()
    p = os.path.join(L.ROOT, "attempts", "A38-root-power", "results", "certs_l1_sample",
                     "root_s0_cert.json")
    if os.path.exists(p):
        for (a, b) in json.load(open(p))["atoms"]:
            x, y = float(Fr(a)), float(Fr(b))
            k = (round(x, 7), round(y, 7))
            if k not in seen:
                seen.add(k)
                atoms.append((x, y))
    _WARM0["w"] = dict(atoms=atoms[:1600], rows=[])
    return _WARM0["w"]


def load_cell(nid, path):
    """(res0 or None, hyp, budget0, s, hyp_json).  A cell with only a *.rec.json (A38 'notrun') is
    rebuilt from its box: the hypothesis is exactly the conditioned box, budget0 = 11 - 1."""
    src = L.src_copy(nid, path)
    d = json.load(open(src))
    if "hyp" in d:
        return d, Hyp.from_json(d["hyp"]), d["budget"], d["s"], d["hyp"]
    b = json.loads(d["box"]) if isinstance(d["box"], str) else d["box"]
    hj = dict(boxes=[b], nofams=[])
    return None, Hyp([Box.from_json(b)], []), 10, L.S0, hj


def classify(rec):
    if rec.get("tau") is None:
        return rec.get("verdict", "n/a")
    eta = rec["eta"]
    if eta <= -KILL:
        return "kill-candidate"
    if abs(eta) < KNIFE:
        return "knife-edge"
    return "alive"


def one(nid, path, cfg, e, log, lp_time=240.0, probe_time=60.0, deadline=None, force=False,
        stage=1):
    tag = "%s__%s__e%s" % (nid, cfg, str(e).replace("/", "o"))
    recp = os.path.join(RECD, tag + ".json")
    if os.path.exists(recp) and not force:
        r = json.load(open(recp))
        if stage <= r.get("stage", 1):
            return r
    delta = CFGS[cfg]
    fam = L.get_fam(delta, log=lambda *a: None)
    res0, hyp, budget0, s, hj = load_cell(nid, path)
    B, rmax = L.crowd_budget(fam, hj)
    bonus = int(math.floor(float(e) * B))
    budget = budget0 + bonus
    tau0 = res0["tau"] if res0 else None
    rec = dict(nid=nid, cfg=cfg, delta=delta, e=str(e), tag=tag, stage=stage,
               a_w=str(fam["a"]), a_w_f=float(fam["a"]),
               n_G_per_corner=fam["n_g_per_corner"], n_E=fam["n_e"],
               rmax_cores=rmax, B=B, bonus=bonus, budget0=budget0, budget=budget,
               n_cert=11 + bonus, n_cores=len(hj.get("boxes", [])),
               tau0=tau0, eta0=(tau0 - budget0) if tau0 is not None else None,
               conv0=bool(res0.get("converged")) if res0 else None,
               ts=time.strftime("%Y-%m-%d %H:%M:%S"))
    if bonus <= 0:
        rec.update(verdict="NO BONUS (B=%d, floor(eB)=0)" % B, tau=None, dead=False)
        json.dump(rec, open(recp, "w"), indent=1)
        _put(rec)
        return rec
    if not L.gate(log, tag, deadline=deadline):
        rec.update(verdict="SKIPPED (headroom gate)", tau=None, dead=False)
        return rec
    outp = os.path.join(L.NODES, tag + ".lp.json")
    prev = json.load(open(outp)) if (stage > 1 and os.path.exists(outp)) else None
    warm = (warm_from_result(prev) if prev is not None
            else (warm_from_result(res0) if res0 else root_warm()))
    warm["rows"] = warm.get("rows", [])[:20000]
    t0 = time.time()
    CF.install_rhs(fam, e, lpbox92)
    try:
        if prev is not None:
            r = solve_node(s, hyp, budget, warm=warm, time_limit=lp_time, **LPKW)
        else:
            tp = min(probe_time, lp_time)
            r = solve_node(s, hyp, budget, warm=warm, time_limit=tp, **LPKW)
            rec["tau_probe"] = r["tau"]
            rec["probe_s"] = round(time.time() - t0, 1)
            if r["tau"] < budget - 1e-9 and not r["converged"] and lp_time > tp + 20:
                r = solve_node(s, hyp, budget, warm=warm_from_result(r),
                               time_limit=lp_time - tp, **LPKW)
            else:
                rec["refused_at_probe"] = bool(r["tau"] >= budget - 1e-9)
    finally:
        CF.install_rhs(None, None, lpbox92)
    lp_s = round(time.time() - t0, 1)
    if prev is not None:
        lp_s += prev.get("a115", {}).get("lp_s", 0.0)
    r["a115"] = dict(nid=nid, cfg=cfg, delta=delta, e=str(e), B=B, bonus=bonus, budget=budget,
                     n_cert=11 + bonus, rmax_cores=rmax, a_w=str(fam["a"]), lp_s=lp_s,
                     stage=stage, src_path=path)
    json.dump(r, open(outp, "w"))
    tau = r["tau"]
    rec.update(tau=tau, eta=tau - budget, converged=bool(r["converged"]),
               minmass=r["minmass"], maxcov=r["maxcov"], n_rows=r.get("n_rows"),
               n_atoms=len([x for x in r.get("atoms_all", []) if x[2] > 1e-10]),
               lp_s=lp_s, lp_path=os.path.relpath(outp, L.BASE).replace("\\", "/"),
               c=((tau - tau0) / float(e)) if tau0 is not None else None)
    rec["c_ge_B"] = (rec["c"] is not None and rec["c"] >= B - 1e-9)
    rec["verdict"] = classify(rec)
    json.dump(rec, open(recp, "w"), indent=1)
    _put(rec)
    log("  %-42s B=%d n=%2d tau=%8.4f eta=%+8.4f c=%6s conv=%-5s %-14s %5.0fs"
        % (tag, B, budget, tau, rec["eta"],
           ("%.2f" % rec["c"]) if rec["c"] is not None else "n/a",
           rec["converged"], rec["verdict"], lp_s))
    return rec


def items_for(plan, which):
    if which == "canary":
        return [(c["nid"], c["path"]) for c in plan["canary"]]
    inplan = [(x["nid"], x["path"]) for x in plan["nodes"]]
    if which == "plan":
        return inplan
    seen = {n for n, _ in inplan}
    idx = L.extract_index()
    rest = [(r["nid"], idx[r["nid"]]["path"])
            for r in json.load(open(os.path.join(L.RES, "t1_corners.json")))["recs"]
            if r["nid"] not in seen]
    return inplan + rest if which == "all" else rest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--cfgs", default="d0,d0.05,d0.1")
    ap.add_argument("--which", default="all", choices=("plan", "rest", "all", "canary"))
    ap.add_argument("--lp_time", type=float, default=240.0)
    ap.add_argument("--probe_time", type=float, default=60.0)
    ap.add_argument("--minutes", type=float, default=600.0)
    ap.add_argument("--stage2", action="store_true", help="re-solve the knife-edge cells at 900 s")
    ap.add_argument("--e", default="auto")
    A = ap.parse_args()
    i, n = (int(x) for x in A.shard.split("/"))
    log = L.logger("t2_s%d.log" % i)
    plan = json.load(open(os.path.join(L.RES, "t2_plan.json")))
    items = [it for k, it in enumerate(items_for(plan, A.which)) if k % n == i]
    deadline = time.time() + 60 * A.minutes
    log("A115 T2 shard %d/%d (%s%s): %d cells x %s  lp=%.0fs probe=%.0fs"
        % (i, n, A.which, " STAGE2" if A.stage2 else "", len(items), A.cfgs,
           A.lp_time, A.probe_time))
    for (nid, path) in items:
        for cfg in A.cfgs.split(","):
            if time.time() > deadline:
                log("deadline reached -- stopping (resumable)")
                return
            fam = L.get_fam(CFGS[cfg], log=lambda *a: None)
            _, _, _, _, hj = load_cell(nid, path)
            B, _ = L.crowd_budget(fam, hj)
            es = [Fr(1, max(1, B))] if A.e == "auto" else [Fr(A.e)]
            for e in es:
                if A.stage2:
                    tag = "%s__%s__e%s" % (nid, cfg, str(e).replace("/", "o"))
                    p = os.path.join(RECD, tag + ".json")
                    if not os.path.exists(p) or json.load(open(p)).get("verdict") != "knife-edge":
                        continue
                    one(nid, path, cfg, e, log, lp_time=900.0, probe_time=900.0,
                        deadline=deadline, stage=2)
                    continue
                rec = one(nid, path, cfg, e, log, lp_time=A.lp_time,
                          probe_time=A.probe_time, deadline=deadline)
                if A.e == "auto" and rec.get("c") is not None and not rec.get("c_ge_B", True) \
                        and rec.get("verdict") == "alive" and time.time() < deadline:
                    one(nid, path, cfg, Fr(1), log, lp_time=A.lp_time,
                        probe_time=A.probe_time, deadline=deadline)
    log("shard %d done" % i)


if __name__ == "__main__":
    main()
