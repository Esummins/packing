"""Continue an SCS run from saved results (warm start: x from the saved B, y from the saved multipliers, s = b - Ax),
longer time limit; update results/<tag>.json with the new bracket."""
import os, sys, json, time, math
import numpy as np
import scs
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from graph import orbits, overlap_matrix
from theta_sdp import symmetry_basis, build_scs, dual_certificate, dense_T, unpack, reconstruct_B, feasible_value, IRREPS, DIMS


def main(tag, time_limit, eps=1e-6, max_iters=200000):
    R = json.load(open(os.path.join(HERE, "results", tag + ".json")))
    d = np.load(os.path.join(HERE, "results", tag + "_graph.npz")); P, G = d["P"], d["G"]
    N = len(P); s = R["s"]
    oid, orbs = orbits(G); ov = overlap_matrix(P)
    SB = symmetry_basis(G, orbs)
    ts = float(N)
    data, cone, meta = build_scs(G, orbs, ov, SB, log=print, trace_scale=ts)
    meta["trace_scale"] = ts
    # warm start
    B = np.load(os.path.join(HERE, "results", tag + "_B.npy")).astype(float) * ts
    x = np.zeros(meta["nvar"])
    for n in IRREPS:
        m = SB["m"][n]
        if m == 0:
            continue
        T0 = dense_T(SB, n, 0)
        X = T0.T @ B @ T0
        sidx = meta["sidx"][n]; off = meta["off"][n]
        for bcol in range(m):
            for a in range(bcol, m):
                x[off + sidx[a, bcol]] = X[a, a] if a == bcol else X[a, bcol] * math.sqrt(2.0)
    y = np.load(os.path.join(HERE, "results", tag + "_scs_y.npy"))
    sv = data["b"] - data["A"] @ x
    t0 = time.time()
    solver = scs.SCS(data, cone, eps_abs=eps, eps_rel=eps, max_iters=max_iters, verbose=True, time_limit_secs=time_limit, acceleration_lookback=10)
    sol = solver.solve(warm_start=True, x=x, y=y, s=sv)
    info = sol["info"]
    print(f"SCS: {info['status']} iters {info['iter']} pobj {-info['pobj']:.6f} dobj {-info['dobj']:.6f} res_pri {info['res_pri']:.2e} res_dual {info['res_dual']:.2e} gap {info['gap']:.2e} t={time.time()-t0:.0f}s")
    X = unpack(sol["x"] / ts, SB, meta)
    B = reconstruct_B(SB, X)
    fv, mineig = feasible_value(B, ov)
    delta = max(0.0, -mineig); lb = (fv + N * delta) / (1 + N * delta)
    r = dict(meta=meta, y=sol["y"])
    cert = dual_certificate(r, G, ov)
    print(f"bracket: {lb:.6f} <= theta'_G <= {cert['bound']:.6f}  (cert {cert})")
    np.save(os.path.join(HERE, "results", tag + "_scs_y.npy"), sol["y"])
    np.save(os.path.join(HERE, "results", tag + "_B.npy"), B.astype(np.float32))
    np.save(os.path.join(HERE, "results", tag + "_B_diag.npy"), np.diag(B))
    R.update(theta=-info["pobj"], theta_dual=-info["dobj"], sdp_status=info["status"] + " (continued)", sdp_iters=int(R.get("sdp_iters", 0)) + int(info["iter"]),
             sdp_res_pri=info["res_pri"], sdp_res_dual=info["res_dual"], sdp_gap=info["gap"], sdp_time=float(R.get("sdp_time", 0.0)) + time.time() - t0,
             theta_lb_feasible=float(lb), theta_ub_cert=cert["bound"], cert=cert, B_feasible_value=fv, B_min_eig=mineig)
    xs = R["theta"] * np.diag(B); sup = np.nonzero(xs > 1e-4)[0]
    R["theta_support"] = [dict(cx=float(P[i, 0]), cy=float(P[i, 1]), theta_deg=float(np.degrees(P[i, 2])), x=float(xs[i])) for i in sup[np.argsort(-xs[sup])][:400]]
    R["theta_support_size"] = int(len(sup))
    ev = np.linalg.eigvalsh(B); R["B_eigs_top"] = [float(v) for v in ev[::-1][:20]]; R["B_rank_1e-3"] = int((ev > 1e-3 * ev.max()).sum())
    json.dump(R, open(os.path.join(HERE, "results", tag + ".json"), "w"), indent=1, default=float)


if __name__ == "__main__":
    main(sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else 1800.0)
