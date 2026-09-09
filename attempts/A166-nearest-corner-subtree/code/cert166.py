"""A166 -- diagnose the ONE converged budget-8 kill whose certificate FAILs.

`l2_p65_101_b8_005_512` converges at `tau = 7.000000` against budget 8 (`eta = -1.000000`) in 124-134 s,
and the frozen verifier reports the SAME 32 HOLES ("a placement with exact mass < 1") at every one of
five separation rounds -- the A13/A14 loop makes no progress, which is A150's pattern too (2 of its 7
converged kills failed the same way and reproduced under a raised scale cap).

Two hypotheses, both cheap to test and neither needing another LP:

    (H1) the SCALE is too aggressive -- try a ladder of scales, including 1.005 (the minimum);
    (H2) the certificate's RATIONAL ROUNDING makes the holes -- `caselp.make_certificate` rounds atom
         positions and weights onto a 1e-6 grid; try 1e-9 and 1e-12.

The LP is solved ONCE and every (scale, denominator) pair is emitted from the same result and handed to
the FROZEN `verify_case.py`, so the comparison is exact.

    python code/cert166.py --node l2_p65_101_b8_005_512
"""
import argparse
import json
import os
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import lp166 as L                                               # noqa: E402
import cells166 as C                                            # noqa: E402
from caselp import Box, make_certificate, solve_node            # noqa: E402  READ-ONLY (A57)

RES = os.path.join(BASE, "results")
CERTS = os.path.join(BASE, "certs")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--node", required=True)
    ap.add_argument("--pad", default="wmax")
    ap.add_argument("--cap", type=float, default=300.0)
    ap.add_argument("--scales", default="1.005,1.02,1.05,1.10,1.14,1.20")
    ap.add_argument("--denoms", default="1000000,1000000000,1000000000000")
    a = ap.parse_args()
    nodes = json.load(open(os.path.join(RES, "nodes166_%s.json" % a.pad), encoding="utf-8"))
    n = [x for x in nodes if x["node"] == a.node]
    if not n:
        raise SystemExit("no such node")
    n = n[0]
    boxes = [Box(**b) for b in n["boxes"]]
    budget = n["budget"]
    H = L.ExactHyp(boxes, [])
    t0 = time.time()
    res = solve_node(C.S0, H, budget, sym_kind="C1", warm=L.load_warm(n["cell"]),
                     time_limit=a.cap, max_iter=900, out=None, log=lambda *x: None, prune=0,
                     prune_cols=3, col_stop_iter=10 ** 6, col_stop_cov=1.002, max_cols_add=400,
                     max_rows_add=2000, fine_slack=99.0, alternate=True, fine=False)
    print("LP: tau=%.9f budget=%d converged=%s minmass=%s  %.0f s"
          % (res["tau"], budget, res["converged"], res.get("minmass"), time.time() - t0), flush=True)
    out = []
    os.makedirs(CERTS, exist_ok=True)
    for dn in [int(x) for x in a.denoms.split(",")]:
        for sc in [float(x) for x in a.scales.split(",")]:
            tag = "%s_sc%s_dn%d" % (a.node, ("%.3f" % sc).replace(".", "p"), dn)
            p = os.path.join(CERTS, tag + ".json")
            cert = make_certificate(res, L.S_RAT, scale=sc, denom_pos=dn, denom_w=dn)
            tot = float(Fr(cert["total"]))
            json.dump(cert, open(p, "w"), indent=0)
            if tot >= budget:
                out.append(dict(scale=sc, denom=dn, total=tot, result="MARGIN"))
                print("  scale %.3f denom %d: total %.6f >= budget -> MARGIN" % (sc, dn, tot),
                      flush=True)
                continue
            rc, txt = L.run_verifier(p, jobs=2, depth=56)
            tail = [l for l in txt.splitlines() if l.startswith(("PASS", "FAIL", "boxes",
                                                                "MALFORMED"))]
            out.append(dict(scale=sc, denom=dn, total=tot, rc=rc,
                            result=("PASS" if rc == 0 else "FAIL"), verifier=tail[:3]))
            print("  scale %.3f denom %d: total %.6f -> %s | %s"
                  % (sc, dn, tot, "PASS" if rc == 0 else "FAIL",
                     (tail[-1][:130] if tail else "")), flush=True)
    json.dump(dict(node=a.node, budget=budget, tau=res["tau"], converged=res["converged"],
                   verifier_sha=L.VERIFIER_SHA, trials=out),
              open(os.path.join(RES, "cert166_%s.json" % a.node), "w"), indent=1)
    print("wrote results/cert166_%s.json" % a.node, flush=True)


if __name__ == "__main__":
    main()
