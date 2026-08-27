"""
A33 / T1 driver: eta(s) = tau*(s) - 11 by the A07 double cutting-plane (row gen over placements,
col gen over free atoms, HiGHS, D4 symmetry), with LAB-STANDARD a-posteriori verification of every
LP solve (primal feasibility, dual feasibility, objective recomputed from (w,y) with numpy).

Usage:
  python run_s.py --s 3.86 --warm <field_or_result.json|state.json> --phase joint|rowonly
                  --time_limit 2400 --tag r1

Outputs (all under t1/):
  checkpoints/<tag>_s<S>_state.json   full LP state every iteration (rows+orbits+w+y) -> resumable
  checkpoints/<tag>_s<S>_verify.json  a-posteriori verification record of the final solve
  results/field_<S>.json              D4-expanded atoms [[x,y,w],...], tau, oracle residuals
  results/fracpack_<S>.json           dual fractional packing (placements+weights), lower bound
"""
import argparse, json, math, os, time
import numpy as np

import lp_measure2 as L
from lp_measure2 import (Model, RowOracle, ColOracle, initial_rows, inside_mask,
                         d4_point_images, d4_placement_images, EPS_GEO, run)

HERE = os.path.dirname(os.path.abspath(__file__))


# ----------------------------------------------------------------- warm start
def load_warm(path, s_new):
    """Return (atom reps, rows) from an A07 result json, an A33 field json, or a *_state.json.

    Atom orbit representatives live in the fundamental triangle 0<=x<=y<=s/2, i.e. they are
    distances-to-the-nearest-two-walls; the guard measure of this problem lives on the
    unit-offset lines x,y in {1, s-1}, so the correct transport to a new side length is the
    IDENTITY on representatives (wall offsets preserved), not a rescaling.
    Row centres live in the far quadrant (c >= s/2); they are transported by c -> c + (s_new-s_old)
    (far-wall offset preserved) and also kept unmapped.
    """
    d = json.load(open(path))
    s_old = float(d["s"])
    ds = s_new - s_old
    if "orbits" in d:                       # *_state.json checkpoint or A33 field json
        reps = [(float(o[0]), float(o[1])) for o in d["orbits"]]
        rows_old = [tuple(r) for r in d.get("rows", [])]
    elif "atoms" in d and isinstance(d["atoms"], list) and d["atoms"] and isinstance(d["atoms"][0], dict):
        reps = [tuple(a["rep"]) for a in d["atoms"]]
        rows_old = [(p["cx"], p["cy"], p["theta"]) for p in d.get("packing", [])]
    else:                                   # A33 field json: expanded atoms
        reps = []
        seen = set()
        for (x, y, w) in d["atoms"]:
            rx, ry = L.canon_point(x, y, s_old)
            k = (round(rx, 7), round(ry, 7))
            if k not in seen:
                seen.add(k); reps.append((rx, ry))
        rows_old = []
    rows = []
    if abs(ds) < 1e-12:
        rows = list(rows_old)
    else:
        # far-wall-preserving transport only (one image per row; carrying 4 images per row makes
        # the warm LP several times larger for no gain, the oracle regenerates what is missing)
        for (cx, cy, th) in rows_old:
            rows.append((cx + ds, cy + ds, th))
    # clip to admissible centre region for the new s
    out = []
    for (cx, cy, th) in rows:
        lo, hi = L.centre_range(s_new, th)
        if lo - 1e-9 <= cx <= hi + 1e-9 and lo - 1e-9 <= cy <= hi + 1e-9:
            out.append((cx, cy, th))
    return reps, out


# ------------------------------------------------- a-posteriori LP verification
def verify_solve(M, note=""):
    """LAB STANDARD: never trust solver status. Recompute primal/dual feasibility and both
    objectives from the returned (w, y) with numpy on an INDEPENDENTLY rebuilt constraint matrix
    (rebuilt row by row from the geometry, never read back from HiGHS)."""
    R, K = len(M.rows), len(M.orbits)
    c = np.array([len(o["pts"]) for o in M.orbits], dtype=float)   # objective = orbit size
    w = np.asarray(M.w, dtype=float)
    y = np.asarray(M.y, dtype=float)
    Aw = np.zeros(R)
    ATy = np.zeros(K)
    for r, (cx, cy, th) in enumerate(M.rows):
        m = inside_mask(M.P, cx, cy, th)
        if not m.any():
            continue
        cnt = np.bincount(M.P_orb[m], minlength=K).astype(float)
        idx = np.nonzero(cnt)[0]
        v = cnt[idx]
        Aw[r] = float(v @ w[idx])
        if y[r] != 0.0:
            ATy[idx] += v * y[r]
    A = None
    rec = dict(
        note=note, n_rows=int(R), n_cols=int(K),
        primal_min_row_activity=float(Aw.min()) if len(Aw) else None,
        primal_max_row_violation=float(max(0.0, 1.0 - Aw.min())) if len(Aw) else 0.0,
        primal_min_w=float(w.min()) if len(w) else 0.0,
        primal_neg_w_violation=float(max(0.0, -w.min())) if len(w) else 0.0,
        dual_max_col_violation=float(max(0.0, (ATy - c).max())) if len(c) else 0.0,
        dual_min_y=float(y.min()) if len(y) else 0.0,
        obj_primal_recomputed=float(c @ w),
        obj_dual_recomputed=float(y.sum()),
        obj_solver=float(M.obj),
        gap_primal_dual=float(abs(c @ w - y.sum())),
        gap_solver_recomputed=float(abs(float(M.obj) - c @ w)),
        model_status=str(M.h.getModelStatus()),
    )
    rec["ok"] = bool(rec["primal_max_row_violation"] < 1e-7 and rec["primal_neg_w_violation"] < 1e-9
                     and rec["dual_max_col_violation"] < 1e-6 and rec["dual_min_y"] > -1e-9
                     and rec["gap_primal_dual"] < 1e-6 and rec["gap_solver_recomputed"] < 1e-6)
    return rec


# ------------------------------------------------------------------- residuals
def row_residual(M, n_theta=361, cstep=0.005, max_refine=250):
    """max over placements of (1 - mu(Q)) : the amount by which primal feasibility can still fail."""
    ro = RowOracle(M.s, M.P, M.wpts(), n_theta=n_theta, cstep=cstep, delta=0.001)
    v = ro.search(thresh=1.0 + 1e-9, max_refine=max_refine)
    if not v:
        return 0.0, None
    best = v[0]
    return float(1.0 - best[3]), [float(best[0]), float(best[1]), float(best[2])]


def polish(M, rounds=10, target=2e-3, n_theta=361, cstep=0.005, max_add=2000, neigh=40,
           neigh_d=0.002, time_limit=None, checkpoint=None, verbose=True):
    """Endgame row separation with the SAME (stronger) oracle settings used for the final residual.

    The in-loop oracle searches for placements with mass < 1 - tol and only refines candidates whose
    histogram lower bound is already below that threshold; it therefore declares convergence while
    a pattern search started from EXACTLY-tight placements still descends into pockets with a
    0.5-1.5% deficit (the A07 lesson: LP vertices have many tight placements and the pockets next to
    them are a few 1e-3 wide).  Here we search with threshold 1 + 1e-9, i.e. we refine from the tight
    placements too, add every violated placement found (plus a small neighbourhood), and re-solve,
    until the search itself can no longer find a violation above `target`.
    """
    t0 = time.time()
    hist = []
    for k in range(rounds):
        obj = M.solve()
        ro = RowOracle(M.s, M.P, M.wpts(), n_theta=n_theta, cstep=cstep, delta=0.001)
        v = ro.search(thresh=1.0 + 1e-9, max_refine=400)
        viol = [x for x in v if x[3] < 1.0 - 1e-9]
        worst = float(1.0 - viol[0][3]) if viol else 0.0
        nr = 0
        for (cx, cy, th, m) in viol[:max_add]:
            nr += M.add_row(cx, cy, th)
        for (cx, cy, th, m) in viol[:neigh]:
            for dcx in (-1, 0, 1):
                for dcy in (-1, 0, 1):
                    for dth in (-1, 0, 1):
                        if dcx == dcy == dth == 0:
                            continue
                        th2 = min(max(th + dth * neigh_d, 0.0), math.pi / 4)
                        lo, hi = L.centre_range(M.s, th2)
                        nr += M.add_row(min(max(cx + dcx * neigh_d, lo), hi),
                                        min(max(cy + dcy * neigh_d, lo), hi), th2)
        hist.append(dict(round=k, obj=float(obj), worst_violation=worst, added_rows=int(nr),
                         n_rows=len(M.rows), t=time.time() - t0))
        if verbose:
            print(f"  polish {k:2d} tau={obj:.6f} worst_viol={worst:.6f} +rows={nr} "
                  f"rows={len(M.rows)} t={time.time()-t0:.0f}s", flush=True)
        if checkpoint:
            L.save_state(M, checkpoint, dict(polish_round=k, obj=float(obj), worst_violation=worst))
        if worst <= target or nr == 0:
            break
        if time_limit and time.time() - t0 > time_limit:
            print("  polish time limit", flush=True)
            break
    M.solve()
    return hist


def build_model(s, reps, rows, verbose=True):
    M = Model(s, 11)
    for (x, y) in reps:
        M.add_orbit(x, y)
    for (cx, cy, th) in rows:
        M.add_row(cx, cy, th)
    if verbose:
        print(f"[polish s={s}] orbits={len(M.orbits)} points={len(M.P)} rows={len(M.rows)}", flush=True)
    return M


def col_residual(M, half_extra=0.0, grid=0.004):
    """max over points of coverage by the dual fractional packing (squares half-width 0.5-EPS_GEO+extra)."""
    co = ColOracle(M.s, M.packing_images())
    co.half = 0.5 - EPS_GEO + half_extra
    out, maxcov = co.search(thresh=1.0 + 1e-9, grid=grid, max_refine=120)
    if out:
        maxcov = max(maxcov, max(o[2] for o in out))
    return float(maxcov)


# ------------------------------------------------------------------ output
def save_field(M, path, extra):
    atoms, orbs = [], []
    for k, o in enumerate(M.orbits):
        wk = float(M.w[k])
        if wk <= 1e-11:
            continue
        orbs.append([float(o["rep"][0]), float(o["rep"][1]), wk, int(len(o["pts"]))])
        for (px, py) in o["pts"]:
            atoms.append([float(px), float(py), wk])
    d = dict(s=M.s, n_atoms=len(atoms), atoms=atoms, orbits=orbs,
             tau=float(sum(a[2] for a in atoms)), tau_solver=float(M.obj), eps_geo=EPS_GEO)
    d.update(extra)
    json.dump(d, open(path, "w"))
    return d


def save_fracpack(M, path, extra):
    pl = [[float(a), float(b), float(t), float(w)] for (a, b, t, w) in M.packing_images()]
    d = dict(s=M.s, n_placements=len(pl), placements=pl,
             weight_total=float(sum(p[3] for p in pl)), eps_geo=EPS_GEO)
    d.update(extra)
    json.dump(d, open(path, "w"))
    return d


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--s", type=float, required=True)
    ap.add_argument("--warm", type=str, default=None)
    ap.add_argument("--phase", type=str, default="joint", choices=["joint", "rowonly", "polish"])
    ap.add_argument("--polish_rounds", type=int, default=0)
    ap.add_argument("--polish_target", type=float, default=2e-3)
    ap.add_argument("--time_limit", type=float, default=2400)
    ap.add_argument("--max_iter", type=int, default=400)
    ap.add_argument("--tag", type=str, default="r1")
    ap.add_argument("--n_theta", type=int, default=181)
    ap.add_argument("--cstep", type=float, default=0.01)
    ap.add_argument("--col_stop_cov", type=float, default=1.002)
    ap.add_argument("--col_stop_iter", type=int, default=10**9)
    ap.add_argument("--N0", type=int, default=38)
    ap.add_argument("--no_final_residual", action="store_true")
    ap.add_argument("--extra_rows", type=str, default=None,
                    help="json list of [cx,cy,theta] rows (e.g. verify_measure witnesses) to inject")
    ap.add_argument("--resid_theta", type=int, default=361)
    ap.add_argument("--resid_cstep", type=float, default=0.005)
    a = ap.parse_args()

    S = f"{a.s:.6f}".rstrip("0").rstrip(".")
    ck = os.path.join(HERE, "checkpoints", f"{a.tag}_s{S}_state.json")
    t0 = time.time()

    ia = ir = None
    if a.warm:
        ia, ir = load_warm(a.warm, a.s)
        ir = ir + initial_rows(a.s)
        print(f"warm: {len(ia)} atom reps, {len(ir)} rows from {a.warm}", flush=True)
    xr = None
    if a.extra_rows:
        xr = [tuple(r) for r in json.load(open(a.extra_rows))]
        print(f"extra rows: {len(xr)} from {a.extra_rows}", flush=True)

    if a.phase == "polish":
        assert ia is not None, "--phase polish needs --warm <state.json>"
        M = build_model(a.s, ia, (ir or []) + (xr or []))
        ph = polish(M, rounds=(a.polish_rounds or 12), target=a.polish_target,
                    time_limit=a.time_limit, checkpoint=ck)
        res = dict(converged=bool(ph and ph[-1]["worst_violation"] <= a.polish_target),
                   n_rows=len(M.rows), n_orbits=len(M.orbits), history=ph)
    else:
        res, M = run(a.s, n=11, N0=a.N0, max_iter=a.max_iter, out=None, time_limit=a.time_limit,
                 row_kw=dict(n_theta=a.n_theta, cstep=a.cstep, delta=0.002),
                 init_atoms=ia, init_rows=ir,
                 col_stop_iter=(0 if a.phase == "rowonly" else a.col_stop_iter),
                 col_stop_cov=a.col_stop_cov, max_cols_add=60,
                 fine_row_kw=dict(n_theta=361, cstep=0.005, delta=0.001),
                 checkpoint=ck, neigh_rows=(60 if xr else 8), neigh_d=0.003, extra_rows=xr)
        if a.polish_rounds:
            res["history"] = list(res["history"]) + polish(
                M, rounds=a.polish_rounds, target=a.polish_target, checkpoint=ck)
            res["n_rows"] = len(M.rows)

    ver = verify_solve(M, note=f"final solve, phase={a.phase}, s={a.s}")
    print("VERIFY", json.dumps(ver), flush=True)
    json.dump(ver, open(os.path.join(HERE, "checkpoints", f"{a.tag}_s{S}_verify.json"), "w"), indent=1)

    rowres, wit = (None, None)
    covshrunk = covexact = covclosed = None
    if not a.no_final_residual:
        rowres, wit = row_residual(M, n_theta=a.resid_theta, cstep=a.resid_cstep)
        covshrunk = col_residual(M, 0.0)             # half = 0.5 - EPS_GEO (the LP's own squares)
        covexact = col_residual(M, EPS_GEO)          # half = 0.5 exactly (closed unit squares)
        covclosed = col_residual(M, 2 * EPS_GEO)     # enlarged squares -> conservative dual check
        print(f"RESID row_violation={rowres:.6f} maxcov_shrunk={covshrunk:.6f} "
              f"maxcov_exact={covexact:.6f} maxcov_closed={covclosed:.6f}", flush=True)

    nu = float(M.y.sum())
    lb = nu / max(1.0, covshrunk) if covshrunk else None
    lb_exact = nu / max(1.0, covexact) if covexact else None
    lb_closed = nu / max(1.0, covclosed) if covclosed else None
    extra = dict(tag=a.tag, phase=a.phase, lp_verify=ver, converged=res["converged"],
                 n_rows=res["n_rows"], n_orbits=res["n_orbits"], wall_time=time.time() - t0,
                 oracle_residuals=dict(row_violation=rowres, row_witness=wit,
                                       maxcov_shrunk=covshrunk, maxcov_exact=covexact,
                                       maxcov_closed=covclosed),
                 nu_dual=nu, fracpack_lower_bound=lb,
                 fracpack_lower_bound_exact=lb_exact, fracpack_lower_bound_closed=lb_closed)
    f = save_field(M, os.path.join(HERE, "results", f"field_{S}.json"), extra)
    save_fracpack(M, os.path.join(HERE, "results", f"fracpack_{S}.json"), extra)
    json.dump(res["history"], open(os.path.join(HERE, "checkpoints", f"{a.tag}_s{S}_history.json"), "w"))
    print(f"FINAL s={a.s} tau={f['tau']:.6f} eta={f['tau']-11:.6f} nu={nu:.6f} "
          f"lb={lb if lb is None else round(lb,6)} rowres={rowres} t={time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
