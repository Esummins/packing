"""A149 -- ONE A60 (trump5) node of the exact-core re-emission, in its own process.

The A57 lane runs A135's `emit135.certify`, which is hard-wired to A57: it rebuilds the pins from
`name_to_slots.json[k5_11|k5_16]` at half-width delta/sqrt(2) and warm-starts from A57's pool.
A60 is a different hypothesis, so this module does the same thing A135 does, for A60's shapes:

  * the hypothesis comes from the NODE RECORD (`res["hyp"]`), which A60 stores in full -- five
    DEGENERATE pin boxes at the exact slots (`deepen.py` builds `Box(x, x, y, y, 0, 0)`) plus the
    conditioned box H;
  * **only H's core is replaced** by A135's exact certified-maximal axis core.  A60's pins are
    already exact boxes, and their stock core `a = 16383999967232/32768001953125` is deliberately
    just under 1/2: at 1/2 exactly the cores of two slots 1.0 apart would TOUCH and the
    `budget = n - #cores` bridge would lose its pairwise-disjointness.  So the pins keep the core
    the corpus certified with, and `scope = "exH"`;
  * the certificate is emitted by A135's `make_cert`, which reads the LIVE `Hyp` -- `caselp`'s own
    `make_certificate` does `Hyp.from_json` and would silently recompute (and so discard) the
    exact core;
  * the arbiter is the FROZEN `verify_case.py`.  A57's and A60's copies are BYTE-IDENTICAL
    (sha256 521cb01f...), so "the frozen verifier" is unambiguous here.

`lpbox`: A57's and A60's copies differ in ONE constant, the oracle chunk size, which A57's own T19
note records as result-neutral bit for bit (each output element is a dot product over the full
inner dimension and each iteration writes a disjoint slice; only the loop count changes).  A135's
import chain puts A57's on the path first, and its smaller chunks are the safer of the two on this
box's commit limit, so that is what runs.  The choice is recorded on every row (`lpbox`).

Nothing under A60, A135, A141, A142 or A107 is written.  Certificates go to this attempt's
`certs/a60/`.
"""
import argparse
import json
import os
import sys
import time
import traceback
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, ".."))
A135 = os.path.join(ROOT, "A135-polycore-verifier", "code")
if A135 not in sys.path:
    sys.path.insert(0, A135)

S_STR = "969271/250000"


def build_hyp(res, scope, exactcore, Hyp):
    """A60's stored hypothesis with H's core replaced by the exact certified-maximal one."""
    hyp = Hyp.from_json(res["hyp"])
    n = len(hyp.boxes)
    if scope == "exH":
        idx = {n - 1}
    elif scope == "exall":
        idx = set(range(n))
    elif scope == "stock":
        idx = set()
    else:
        raise ValueError(scope)
    a_report = []
    for i, b in enumerate(hyp.boxes):
        a0 = hyp.cores[i].a
        if i in idx:
            hyp.cores[i] = exactcore.exact_core(b)
        a_report.append(dict(i=i, a_stock=str(a0), a_used=str(hyp.cores[i].a),
                             exact=(i in idx)))
    ok, pair, gap = exactcore.cores_pairwise_disjoint(hyp.cores[:n - 1])
    gate = dict(ok=bool(ok), pair=pair, gap=float(gap) if gap is not None else None)
    if not ok:
        raise RuntimeError("A60 pin cores are NOT pairwise disjoint (pair %s, gap %s); the "
                           "budget = n - #cores bridge would be unsound" % (pair, gap))
    return hyp, a_report, gate


def certify_a60(job, cap, rounds, jobs, depth, scale_cap, certdir, log):
    import emit135                                                       # noqa: E402
    import exactcore                                                     # noqa: E402
    from caselp import Hyp, solve_node, warm_from_result                 # noqa: E402

    nid, scope = job["id"], job.get("scope", "exH")
    res0 = json.load(open(job["node"]))
    s = res0["s"]
    budget = job.get("budget", res0.get("budget", 5))
    hyp, a_report, gate = build_hyp(res0, scope, exactcore, Hyp)
    sym = "D4" if hyp.is_symmetric_D4(s) else "C1"
    log("[%s/%s] cores: %s" % (nid, scope, ", ".join(
        "%.9f%s" % (float(Fr(r["a_used"])), "*" if r["exact"] else "") for r in a_report)))
    log("[%s/%s] pin-core disjointness gap %.9f, sym %s, budget %s, stored tau %s"
        % (nid, scope, gate["gap"], sym, budget, res0.get("tau")))

    rec = dict(id=nid, scope=scope, budget=budget, cap=cap, camp="A60", cls="trump5",
               a_report=a_report, pin_gate=gate, sym=sym, s=s, rounds=[],
               tau_before=res0.get("tau"), converged_before=res0.get("converged"),
               node=job["node"], lpbox="A57 copy (chunk 2e6); A60's differs only in that "
                                      "constant and A57 T19 records it result-neutral",
               lane="A60 exact-core re-emission (H core exact, pins at the corpus core)")

    t0 = time.time()
    warm = warm_from_result(res0)
    r = solve_node(s, hyp, budget, sym_kind=sym, warm=warm, time_limit=cap, max_iter=900,
                   out=None, log=lambda *x: None, prune=0, prune_cols=3,
                   col_stop_iter=10 ** 6, col_stop_cov=1.002, max_cols_add=400,
                   max_rows_add=2000, fine_slack=99.0, alternate=True, fine=True)
    rec["lp_wall_s"] = round(time.time() - t0, 1)
    rec["tau"] = r.get("tau")
    rec["converged"] = r.get("converged")
    rec["minmass"] = r.get("minmass")
    rec["support"] = len(r.get("packing") or [])
    log("[%s/%s] tau %s conv=%s (%.1f s, %d support)"
        % (nid, scope, rec["tau"], rec["converged"], rec["lp_wall_s"], rec["support"]))
    if rec["tau"] is None or rec["tau"] >= budget - 1e-9:
        rec["result"] = "NO-KILL"
        return rec
    if not rec["converged"]:
        rec["note"] = "LP hit the cap; tau is a lower bound only (A124: CAP is never a verdict)"

    os.makedirs(certdir, exist_ok=True)
    cert_path = os.path.join(certdir, "%s__%s.json" % (nid, scope))
    extra = []
    for rd in range(rounds + 1):
        scale = (max(1.005, min(scale_cap, (budget - 0.005) / r["tau"] - 0.002))
                 if r["tau"] > 1e-12 else 1.005)
        cert = emit135.make_cert(r, hyp, float(Fr(S_STR)), scale=scale)
        tot = float(Fr(cert["total"]))
        json.dump(cert, open(cert_path, "w"), indent=0)
        if tot >= budget:
            rec["result"] = "TOO-TIGHT"
            rec["rounds"].append(dict(round=rd, tau=r["tau"], total=tot))
            log("[%s/%s] certificate total %.5f >= budget %s" % (nid, scope, tot, budget))
            return rec
        tv = time.time()
        rc, txt = emit135.run_case(cert_path, jobs, depth)
        ver = emit135.tail_lines(txt)
        rec["rounds"].append(dict(round=rd, tau=r["tau"], scale=scale, total=tot, rc=rc,
                                  atoms=len(cert["atoms"]), verify_s=round(time.time() - tv, 1),
                                  verifier=ver))
        log("[%s/%s] round %d: total %.5f < %s, verify_case rc=%s (%.1f s) :: %s"
            % (nid, scope, rd, tot, budget, rc, time.time() - tv, " | ".join(ver[:3])))
        if rc == 0:
            rec["result"] = "PASS"
            rec["cert"] = cert_path
            return rec
        if rd == rounds:
            break
        wf = cert_path.replace(".json", ".witnesses.json")
        if not os.path.exists(wf):
            rec["result"] = "FAIL-NO-WITNESS"
            return rec
        import math
        new = []
        for w in json.load(open(wf))["witnesses"]:
            p = w.get("placement")
            if not p:
                continue
            th = math.radians(p["theta_deg"])
            new.append((p["cx_float"], p["cy_float"], th))
            for d in (0.002, 0.005):
                for dx, dy in ((d, 0), (-d, 0), (0, d), (0, -d), (d, d), (-d, -d), (d, -d),
                               (-d, d)):
                    new.append((p["cx_float"] + dx, p["cy_float"] + dy, th))
                for dth in (d, -d):
                    new.append((p["cx_float"], p["cy_float"], th + dth))
        extra += new
        log("[%s/%s] feeding back %d witness rows; re-solving" % (nid, scope, len(new)))
        r = solve_node(s, hyp, budget, sym_kind=sym, warm=warm_from_result(r), time_limit=cap,
                       out=None, log=lambda *x: None, extra_rows=extra, neigh_rows=0,
                       col_stop_iter=0, fine_slack=99.0, max_iter=1000)
        if r.get("tau") is None or r["tau"] >= budget:
            rec["result"] = "LOST-KILL-ON-RESOLVE"
            rec["tau_resolve"] = r.get("tau")
            return rec
    rec["result"] = "FAIL"
    rec["cert"] = cert_path
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cap", type=float, default=420.0)
    ap.add_argument("--rounds", type=int, default=2)
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--depth", type=int, default=56)
    ap.add_argument("--scale_cap", type=float, default=1.03)
    ap.add_argument("--certdir", default=os.path.join(BASE, "certs", "a60"))
    a = ap.parse_args()

    j = json.load(open(a.job))
    t0 = time.time()
    try:
        rec = certify_a60(j, a.cap, a.rounds, a.jobs, a.depth, a.scale_cap, a.certdir,
                          lambda *x: print(*x, flush=True))
    except Exception as e:
        rec = dict(id=j["id"], scope=j.get("scope", "exH"), camp="A60", result="ERROR",
                   error=repr(e)[:400], tb=traceback.format_exc()[-1500:])
    rec["wall_s"] = round(time.time() - t0, 1)
    rec["level"] = j.get("level")
    rec["families"] = j.get("families")
    json.dump(rec, open(a.out, "w"))
    print("RESULT " + str(rec.get("result")), flush=True)


if __name__ == "__main__":
    main()
