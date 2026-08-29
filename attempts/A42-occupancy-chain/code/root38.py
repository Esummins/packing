#!/usr/bin/env python3
"""A38 task 1: the ROOT interior-occupancy lemma at s0 = 969271/250000.

Hypothesis: NO square of the packing has its centre in Z = [1/2+CW, s0-1/2-CW]^2 (all theta).
Budget 11.  Kill = converged/feasible LP with tau < 11 (then certify exactly).

This is A24's root recipe (attempts/A24-composed-tree/certs/casetree_3.84/
root_interior_occupancy.json: tau = 8.000, cert total 1030019/125000 = 8.240152 < 11,
eps_geo = 0.003, D4 symmetry) re-run at s0.

    python root38.py --cw 0.6 --time_limit 1800
"""
from __future__ import annotations

import argparse, json, os, sys, time
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
RES = os.path.join(HERE, "..", "results")
LOGS = os.path.join(HERE, "..", "logs")

import lpbox                                                    # noqa: E402
import caselp                                                   # noqa: E402
from caselp import NoFam, Hyp, solve_node                        # noqa: E402
from node38 import classify                                      # noqa: E402

S0 = F("969271/250000")
S0F = float(S0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cw", type=float, default=0.6)
    ap.add_argument("--budget", type=int, default=11)
    ap.add_argument("--time_limit", type=float, default=1800)
    ap.add_argument("--eps_geo", type=float, default=0.003)   # A24 root value
    ap.add_argument("--max_iter", type=int, default=1000)
    ap.add_argument("--tag", default="cw06")
    a = ap.parse_args()

    cw = F(str(a.cw))
    lo, hi = F(1, 2) + cw, S0 - F(1, 2) - cw
    lpbox.EPS_GEO = a.eps_geo
    fam = NoFam(float(lo), float(hi), float(lo), float(hi), [(0.0, 90.0)])
    hyp = Hyp([], [fam])
    NoFam.s_hi = S0F - 0.5
    sym = "D4" if hyp.is_symmetric_D4(S0F) else "C1"
    logf = open(os.path.join(LOGS, "root_%s.log" % a.tag), "w")

    def log(*x):
        print(*x, flush=True)
        print(*x, file=logf, flush=True)

    log("A38 ROOT  s0 = %s (%.6f)  CW = %s  Z = [%s, %s]^2  budget %d  sym %s  eps_geo %g"
        % (S0, S0F, cw, lo, hi, a.budget, sym, a.eps_geo))
    t0 = time.time()
    out_node = os.path.join(RES, "root_node_%s.json" % a.tag)
    res = solve_node(S0F, hyp, a.budget, sym_kind=sym, time_limit=a.time_limit, out=None, log=log,
                     theta_box="0-90", max_rows_add=1500, max_cols_add=1500,
                     col_stop_iter=10 ** 6, col_stop_cov=1.01,
                     prune=6, prune_cols=2, alternate=True, max_iter=a.max_iter)
    wall = time.time() - t0
    json.dump(res, open(out_node, "w"))
    st = classify(res, a.budget)
    ht = (res.get("hist_tail") or [{}])[-1]
    summ = dict(kind="A38-root", s=str(S0), s_float=S0F, cw=str(cw), Z=[str(lo), str(hi)],
                budget=a.budget, sym=sym, eps_geo=a.eps_geo, tau=res["tau"],
                slack=res["tau"] - a.budget, converged=res["converged"], minmass=res["minmass"],
                maxcov=res["maxcov"], n_rows=res["n_rows"], n_orbits=res["n_orbits"],
                iters=ht.get("it"), last_added_rows=ht.get("added_rows"),
                last_added_cols=ht.get("added_cols"), status=st, seconds=wall,
                node_json=os.path.relpath(out_node, os.path.join(HERE, "..", "..", "..")))
    json.dump(summ, open(os.path.join(RES, "root_%s_summary.json" % a.tag), "w"), indent=1)
    log("ROOT tau=%.6f budget=%d status=%s conv=%s minmass=%.6f maxcov=%.9f rows=%d wall=%.1fs"
        % (res["tau"], a.budget, st, res["converged"], res["minmass"], res["maxcov"],
           res["n_rows"], wall))
    return 0


if __name__ == "__main__":
    sys.exit(main())
