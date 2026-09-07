"""A115 attribution control.

For every cell that CERTIFIED with the corner rows, ask whether the rows are what made it
certifiable, or whether the same cell certifies WITHOUT them once it is given the same LP wall.

  ctrlA  the campaign's OWN stored LP result, plain certificate (caselp92.make_certificate,
         budget = budget0, no crowd rhs), frozen verify_case.py.
  ctrlB  a PLAIN re-solve (no crowd rhs) warm-started from the same stored result, with the same
         240 s cap A115's stage 1 used, then the same plain certificate.

If ctrlB PASSes, the kill is NOT attributable to Lemma CW's rows -- it is A99/A85's own node
certificate arriving late.  If ctrlB FAILs and the corner-row certificate PASSes, the rows are
what closed the cell.
"""
import argparse
import json
import os
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import blas1  # noqa: F401
import a115lib as L
import lpbox92
from caselp92 import Hyp, solve_node, warm_from_result, make_certificate
from certify115 import run_verifier, _tail

S_RAT = "969271/250000"
SINK = os.path.join(L.RES, "control.jsonl")
LPKW = dict(sym_kind="C1", max_iter=900, out=None, log=lambda *x: None,
            prune=0, prune_cols=3, col_stop_iter=10 ** 6, col_stop_cov=1.002,
            max_cols_add=400, max_rows_add=2000, fine_slack=99.0, alternate=True)


def plain_cert(res, tag, kind, log, depth=56, verify_timeout=900.0):
    budget = res["budget"]
    scale = (max(1.005, min(1.4, (budget - 0.005) / res["tau"] - 0.002))
             if res["tau"] > 1e-12 else 1.005)
    cert = make_certificate(res, S_RAT, scale=scale)
    tot = float(Fr(cert["total"]))
    p = os.path.join(L.CERTS, "ctrl%s_%s.json" % (kind, tag))
    json.dump(cert, open(p, "w"), indent=0)
    if tot >= budget:
        log("  ctrl%s %s: total %.5f >= budget %d -- cannot certify" % (kind, tag, tot, budget))
        return dict(kind=kind, tag=tag, result="FAIL(total>=budget)", tau=res["tau"],
                    converged=bool(res["converged"]), total=tot, budget=budget)
    rc, txt = run_verifier(p, 1, depth, 32, verify_timeout)
    log("  ctrl%s %s tau=%.5f conv=%s total=%.5f (< %d) -> rc=%d" %
        (kind, tag, res["tau"], res["converged"], tot, budget, rc))
    log("    | " + " ; ".join(_tail(txt)[:2]))
    return dict(kind=kind, tag=tag, result=("PASS" if rc == 0 else "FAIL"), rc=rc,
                tau=res["tau"], converged=bool(res["converged"]), total=tot, budget=budget,
                minmass=res.get("minmass"), verifier=_tail(txt)[:2], cert=os.path.basename(p))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tags", nargs="*", help="A115 run tags whose SOURCE cell is to be controlled")
    ap.add_argument("--lp_time", type=float, default=240.0)
    ap.add_argument("--shard", default="0/1")
    A = ap.parse_args()
    i, n = (int(x) for x in A.shard.split("/"))
    log = L.logger("control_s%d.log" % i)
    tags = [t for k, t in enumerate(A.tags) if k % n == i]
    for tag in tags:
        nid = tag.split("__")[0]
        src = os.path.join(L.NODES, nid + ".src.json")
        res0 = json.load(open(src))
        hyp = Hyp.from_json(res0["hyp"])
        log("[control] %s (from %s): tau0=%.5f budget0=%d conv0=%s"
            % (nid, tag, res0["tau"], res0["budget"], res0.get("converged")))
        if not L.gate(log, nid + ":ctrlA"):
            continue
        rA = plain_cert(res0, nid, "A", log)
        t0 = time.time()
        lpbox92.RHS_MULT, lpbox92.RHS_MAX, lpbox92.RHS_CELL = None, 1.0, None
        r = solve_node(res0["s"], hyp, res0["budget"], warm=warm_from_result(res0),
                       time_limit=A.lp_time, **LPKW)
        lp_s = round(time.time() - t0, 1)
        json.dump(r, open(os.path.join(L.NODES, nid + ".plain.lp.json"), "w"))
        rB = plain_cert(r, nid, "B", log)
        rB["lp_s"] = lp_s
        with open(SINK, "a", encoding="utf-8") as f:
            f.write(json.dumps(dict(nid=nid, from_tag=tag, ctrlA=rA, ctrlB=rB)) + "\n")
        log("  => %s ctrlA=%s ctrlB=%s (plain re-solve tau=%.5f conv=%s, %.0f s)"
            % (nid, rA["result"], rB["result"], r["tau"], r["converged"], lp_s))


if __name__ == "__main__":
    main()
