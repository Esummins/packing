"""
A33 / T3(b) driver: tau*(s) at arbitrary side s (and hence eta(n) = tau*(s_n) - n).

Thin wrapper around t1/run_s.py's validated pipeline (A07 double cutting-plane + LAB-STANDARD
a-posteriori LP verification).  Differences from run_s.py:
  * --n is a real parameter (only used for reporting eta = tau - n; tau* itself is n-independent),
  * N0 (initial atom grid resolution) defaults to a side-PROPORTIONAL value so the atom spacing is
    ~0.1 at every s (run_s.py's N0=38 is tuned for s~3.88),
  * results go to t3b/results/field_n<N>_s<S>.json,
  * a residual-corrected UPPER bound tau_ub = tau_LP / (1 - row_violation) is recorded: scaling a
    field whose worst placement carries mass 1-v by 1/(1-v) makes it feasible, so tau* <= tau_ub.
  * the dual fractional packing gives tau* >= nu / maxcov (recorded as tau_lb).

Usage:
  python run_n.py --n 18 --s 4.82287565553229 --time_limit 2400 --tag a
"""
import argparse, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
T1 = os.path.join(os.path.dirname(HERE), "t1")
sys.path.insert(0, T1)

import lp_measure2 as L                                    # noqa: E402
from lp_measure2 import run, EPS_GEO                       # noqa: E402
import run_s as RS                                         # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--s", type=float, required=True)
    ap.add_argument("--warm", type=str, default=None)
    ap.add_argument("--phase", type=str, default="joint", choices=["joint", "rowonly", "polish"])
    ap.add_argument("--polish_rounds", type=int, default=0)
    ap.add_argument("--polish_target", type=float, default=1e-3)
    ap.add_argument("--time_limit", type=float, default=2400)
    ap.add_argument("--max_iter", type=int, default=400)
    ap.add_argument("--tag", type=str, default="a")
    ap.add_argument("--n_theta", type=int, default=181)
    ap.add_argument("--cstep", type=float, default=0.01)
    ap.add_argument("--col_stop_cov", type=float, default=1.002)
    ap.add_argument("--col_stop_iter", type=int, default=10**9)
    ap.add_argument("--N0", type=int, default=0, help="0 => round(9.8*s) rounded to even")
    ap.add_argument("--resid_theta", type=int, default=361)
    ap.add_argument("--resid_cstep", type=float, default=0.005)
    ap.add_argument("--no_final_residual", action="store_true")
    ap.add_argument("--extra_rows", type=str, default=None,
                    help="json list of [cx,cy,theta] rows (verify_measure witnesses) to inject")
    a = ap.parse_args()

    N0 = a.N0 or max(16, 2 * int(round(4.9 * a.s)))
    S = f"{a.s:.8f}".rstrip("0").rstrip(".")
    ck = os.path.join(HERE, "checkpoints", f"{a.tag}_n{a.n}_s{S}_state.json")
    t0 = time.time()

    ia = ir = None
    if a.warm:
        ia, ir = RS.load_warm(a.warm, a.s)
        ir = ir + L.initial_rows(a.s)
        print(f"warm: {len(ia)} atom reps, {len(ir)} rows from {a.warm}", flush=True)

    xr = None
    if a.extra_rows:
        xr = [tuple(r) for r in json.load(open(a.extra_rows))]
        print(f"extra rows: {len(xr)} from {a.extra_rows}", flush=True)

    if a.phase == "polish":
        assert ia is not None
        M = RS.build_model(a.s, ia, (ir or []) + (xr or []))
        if xr:      # dense neighbourhood around each injected witness placement
            import math as _m
            nb = 0
            for (cx, cy, th) in xr:
                for dcx in (-2, -1, 0, 1, 2):
                    for dcy in (-2, -1, 0, 1, 2):
                        for dth in (-2, -1, 0, 1, 2):
                            th2 = min(max(th + dth * 0.002, 0.0), _m.pi / 4)
                            lo, hi = L.centre_range(a.s, th2)
                            nb += M.add_row(min(max(cx + dcx * 0.002, lo), hi),
                                            min(max(cy + dcy * 0.002, lo), hi), th2)
            print(f"witness neighbourhood rows: +{nb}", flush=True)
        ph = RS.polish(M, rounds=(a.polish_rounds or 12), target=a.polish_target,
                       time_limit=a.time_limit, checkpoint=ck)
        res = dict(converged=bool(ph and ph[-1]["worst_violation"] <= a.polish_target),
                   n_rows=len(M.rows), n_orbits=len(M.orbits), history=ph)
    else:
        res, M = run(a.s, n=a.n, N0=N0, max_iter=a.max_iter, out=None, time_limit=a.time_limit,
                     row_kw=dict(n_theta=a.n_theta, cstep=a.cstep, delta=0.002),
                     init_atoms=ia, init_rows=ir,
                     col_stop_iter=(0 if a.phase == "rowonly" else a.col_stop_iter),
                     col_stop_cov=a.col_stop_cov, max_cols_add=60,
                     fine_row_kw=dict(n_theta=361, cstep=0.005, delta=0.001),
                     checkpoint=ck, neigh_rows=8, neigh_d=0.003)
        if a.polish_rounds:
            res["history"] = list(res["history"]) + RS.polish(
                M, rounds=a.polish_rounds, target=a.polish_target, checkpoint=ck,
                time_limit=max(120.0, a.time_limit / 3))
            res["n_rows"] = len(M.rows)

    ver = RS.verify_solve(M, note=f"final solve, n={a.n}, s={a.s}, phase={a.phase}")
    print("VERIFY", json.dumps(ver), flush=True)

    rowres, wit = (None, None)
    covshrunk = covexact = covclosed = None
    if not a.no_final_residual:
        rowres, wit = RS.row_residual(M, n_theta=a.resid_theta, cstep=a.resid_cstep)
        covshrunk = RS.col_residual(M, 0.0)
        covexact = RS.col_residual(M, EPS_GEO)
        print(f"RESID row_violation={rowres:.6f} maxcov_shrunk={covshrunk:.6f} "
              f"maxcov_exact={covexact:.6f}", flush=True)

    tau = float(sum(float(M.w[k]) * len(o["pts"]) for k, o in enumerate(M.orbits)))
    nu = float(M.y.sum())
    tau_ub = tau / (1.0 - rowres) if (rowres is not None and rowres < 0.5) else None
    tau_lb = nu / max(1.0, covshrunk) if covshrunk else None
    extra = dict(n=a.n, tag=a.tag, phase=a.phase, N0=N0, lp_verify=ver,
                 converged=res["converged"], n_rows=res["n_rows"], n_orbits=res["n_orbits"],
                 wall_time=time.time() - t0,
                 oracle_residuals=dict(row_violation=rowres, row_witness=wit,
                                       maxcov_shrunk=covshrunk, maxcov_exact=covexact),
                 nu_dual=nu, tau_ub=tau_ub, tau_lb=tau_lb,
                 eta=tau - a.n, eta_ub=(tau_ub - a.n) if tau_ub else None,
                 eta_lb=(tau_lb - a.n) if tau_lb else None,
                 W=a.s * a.s - a.n)
    f = RS.save_field(M, os.path.join(HERE, "results", f"field_n{a.n}_s{S}.json"), extra)
    RS.save_fracpack(M, os.path.join(HERE, "results", f"fracpack_n{a.n}_s{S}.json"), extra)
    json.dump(res["history"], open(os.path.join(HERE, "checkpoints", f"{a.tag}_n{a.n}_s{S}_hist.json"), "w"))
    W = a.s * a.s - a.n
    print(f"FINAL n={a.n} s={a.s} tau={tau:.6f} eta={tau-a.n:.6f} tau_ub={tau_ub} tau_lb={tau_lb} "
          f"W={W:.6f} rho={(tau-a.n)/W if W > 1e-9 else float('nan'):.6f} "
          f"rowres={rowres} t={time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
