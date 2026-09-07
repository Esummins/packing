"""A115 follow-up (PI, 2026-09-06): the PLAIN warm re-solve pass -- NO corner rows -- over every
OPEN k0_00 cell of A99 (53) and A85 (11).

This is the incidental positive of A115's attribution control written out as a campaign: for
`l2_p95_001` the ordinary node certificate PASSED after a 240 s warm re-solve, with no new
mathematics, where the campaign's own stored LP result FAILED.  The question is how many of
A99/A85's open cells close the same way.

Protocol (PI):
  stage 1  plain warm re-solve, 240 s cap, warm-started from the campaign's own stored result
           (atoms_all + rows_all).  eta = tau - budget.
             eta <= -1e-3  -> straight to the ORDINARY node certificate
                              (caselp92.make_certificate + the frozen verify_case.py at depth 56),
                              converged or not.  The certificate is the verdict.
             |eta| < 1e-6  -> knife edge: stage 2 (900 s), then the same certificate test.
             else          -> alive.
  Certification is FIRST-PASS only (rounds = 0, no witness-feedback re-solve): that is A99/A85's
  own first-pass node certificate, and it is what the 5 CPU-h cap affords.

Discipline: READ-ONLY on A85/A99 (every node json is copied to results/nodes/<nid>.src.json
before it is touched); <= 2 BLAS-pinned processes; the 6144 MB commit / 3072 MB physical gate
before every LP and every verifier run; one resumable record per cell in results/t4/<nid>.json;
a HARD CPU-second cap per process (--cpu_cap), so the pass truncates instead of overrunning.

Cell order is minmass-DESCENDING: minmass is the smallest mass the stored LP gives any generated
row, so it is the campaign's own measure of how close that cell is to a valid certificate.  If
the cap truncates the pass, it truncates the least promising tail, and the record files say
exactly which cells were reached.
"""
import argparse
import glob
import json
import os
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import blas1  # noqa: F401  -- MUST precede numpy
import a115lib as L
import lpbox92
from caselp92 import Hyp, solve_node, warm_from_result, make_certificate
from certify115 import run_verifier, _tail, _holes

S_RAT = "969271/250000"
T4 = os.path.join(L.RES, "t4")
os.makedirs(T4, exist_ok=True)
SINK = os.path.join(L.RES, "t4_runs.jsonl")
KNIFE = 1e-6
KILL = 1e-3
SOURCES = (("A99", "attempts/A99-k0-tree-v2/results/nodes/k0_00/*.json"),
           ("A85", "attempts/A85-k0-route/results/nodes/k0_00/*.json"))
LPKW = dict(sym_kind="C1", max_iter=900, out=None, log=lambda *x: None,
            prune=0, prune_cols=3, col_stop_iter=10 ** 6, col_stop_cov=1.002,
            max_cols_add=400, max_rows_add=2000, fine_slack=99.0, alternate=True)


def cells():
    """every OPEN (dead == False) k0_00 cell of A99 and A85, minmass-descending."""
    out = []
    for tag, pat in SOURCES:
        for p in sorted(glob.glob(os.path.join(L.ROOT, pat))):
            try:
                d = json.load(open(p))
            except Exception:
                continue
            if d.get("dead"):
                continue
            out.append(dict(src=tag, nid=os.path.basename(p)[:-5],
                            path=os.path.relpath(p, L.ROOT).replace("\\", "/"),
                            tau0=d.get("tau"), budget=d.get("budget"),
                            eta0=round(float(d["tau"]) - float(d["budget"]), 6),
                            conv0=bool(d.get("converged")),
                            minmass0=float(d.get("minmass") or 0.0),
                            lp_s0=round(float(d.get("time") or 0.0))))
    out.sort(key=lambda r: (-r["minmass0"], r["eta0"], r["nid"]))
    return out


def certify_plain(res, nid, stage, log, depth=56, verify_timeout=300.0, scale_cap=1.4):
    """A99/A85's ORDINARY first-pass node certificate, checked by the frozen verify_case.py."""
    budget = res["budget"]
    scale = (max(1.005, min(scale_cap, (budget - 0.005) / res["tau"] - 0.002))
             if res["tau"] > 1e-12 else 1.005)
    cert = make_certificate(res, S_RAT, scale=scale)
    tot = float(Fr(cert["total"]))
    p = os.path.join(L.CERTS, "t4_%s_s%d.json" % (nid, stage))
    json.dump(cert, open(p, "w"), indent=0)
    if tot >= budget:
        return dict(result="FAIL(total>=budget)", total=tot, budget=budget, scale=scale,
                    cert=os.path.basename(p), verify_s=0.0)
    t0 = time.time()
    rc, txt = run_verifier(p, 1, depth, 32, verify_timeout)
    dt = round(time.time() - t0, 1)
    tail = _tail(txt)
    log("    cert %s: tau=%.5f scale=%.4f total=%.5f (< %d) rc=%d (%.0f s)"
        % (nid, res["tau"], scale, tot, budget, rc, dt))
    if tail:
        log("      | " + tail[-1][:150])
    return dict(result=("PASS" if rc == 0 else "FAIL"), rc=rc, total=tot, budget=budget,
                scale=scale, holes=_holes(txt), verifier=tail[:2],
                cert=os.path.basename(p), verify_s=dt, n_atoms=len(cert["atoms"]))


def one(c, log, lp_time=240.0, lp_time2=900.0, deadline=None):
    nid = c["nid"]
    recp = os.path.join(T4, nid + ".json")
    if os.path.exists(recp):
        return json.load(open(recp)), 0.0
    src = L.src_copy(nid, c["path"])
    res0 = json.load(open(src))
    hyp = Hyp.from_json(res0["hyp"])
    budget = res0["budget"]
    rec = dict(c)
    rec["ts"] = time.strftime("%Y-%m-%d %H:%M:%S")
    lpbox92.RHS_MULT, lpbox92.RHS_MAX, lpbox92.RHS_CELL = None, 1.0, None   # NO corner rows
    spent = 0.0
    if not L.gate(log, nid, deadline=deadline):
        rec.update(verdict="SKIPPED (headroom gate)")
        return rec, spent
    t0 = time.time()
    r = solve_node(res0["s"], hyp, budget, warm=warm_from_result(res0),
                   time_limit=lp_time, **LPKW)
    lp_s = round(time.time() - t0, 1)
    spent += lp_s
    stage = 1
    eta = r["tau"] - budget
    if abs(eta) < KNIFE:
        t1 = time.time()
        r = solve_node(res0["s"], hyp, budget, warm=warm_from_result(r),
                       time_limit=lp_time2, **LPKW)
        s2 = round(time.time() - t1, 1)
        spent += s2
        lp_s += s2
        stage = 2
        eta = r["tau"] - budget
    json.dump(r, open(os.path.join(L.NODES, nid + ".t4.lp.json"), "w"))
    rec.update(stage=stage, tau=r["tau"], eta=eta, converged=bool(r["converged"]),
               minmass=r["minmass"], maxcov=r["maxcov"], n_rows=r.get("n_rows"), lp_s=lp_s,
               dtau=r["tau"] - (c["tau0"] or 0.0))
    if eta <= -KILL:
        if L.gate(log, nid + ":cert", deadline=deadline):
            t2 = time.time()
            rec["cert"] = certify_plain(r, nid, stage, log)
            spent += time.time() - t2
        rec["verdict"] = ("CERTIFIED DEAD" if (rec.get("cert") or {}).get("result") == "PASS"
                          else "kill-candidate (cert %s)"
                               % (rec.get("cert") or {}).get("result", "not attempted"))
    else:
        rec["verdict"] = "alive (tau >= budget)" if eta > 0 else "knife-edge"
    json.dump(rec, open(recp, "w"), indent=1)
    with open(SINK, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
    log("  %-30s %s tau0=%7.4f -> %7.4f  eta=%+8.4f conv=%-5s minmass %.3f -> %.3f  %-34s %5.0fs"
        % (nid, c["src"], c["tau0"], r["tau"], eta, r["converged"], c["minmass0"],
           r["minmass"], rec["verdict"], spent))
    return rec, spent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--lp_time", type=float, default=240.0)
    ap.add_argument("--lp_time2", type=float, default=900.0)
    ap.add_argument("--cpu_cap", type=float, default=9000.0,
                    help="hard CPU-second cap for THIS process (2 processes x 9000 s = 5 CPU-h)")
    ap.add_argument("--minutes", type=float, default=240.0)
    A = ap.parse_args()
    i, n = (int(x) for x in A.shard.split("/"))
    log = L.logger("t4_s%d.log" % i)
    cs = cells()
    json.dump(dict(n=len(cs), order="minmass descending", cells=cs),
              open(os.path.join(L.RES, "t4_plan.json"), "w"), indent=1)
    mine = [c for k, c in enumerate(cs) if k % n == i]
    deadline = time.time() + 60 * A.minutes
    log("A115-T4 shard %d/%d: %d of %d open k0_00 cells (A99 %d, A85 %d); cpu_cap %.0f s"
        % (i, n, len(mine), len(cs), sum(1 for c in cs if c["src"] == "A99"),
           sum(1 for c in cs if c["src"] == "A85"), A.cpu_cap))
    spent = 0.0
    for c in mine:
        if spent >= A.cpu_cap or time.time() > deadline:
            log("CPU cap / deadline reached after %.0f s -- stopping (resumable)" % spent)
            break
        _, s = one(c, log, lp_time=A.lp_time, lp_time2=A.lp_time2, deadline=deadline)
        spent += s
    log("shard %d done: %.0f CPU-s spent" % (i, spent))


if __name__ == "__main__":
    main()
