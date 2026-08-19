"""Lower bound on theta'(G) via the induced subgraph on the (D4-closed) support of the approximate primal B:
theta'(G[S]) <= theta'(G), and G[S] (a few hundred nodes) is solved accurately. Also reports the LP on G[S]."""
import os, sys, json, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from graph import orbits, overlap_matrix
from theta_sdp import theta_prime, reconstruct_B, feasible_value, dual_certificate
from lp_point import nu_point_lp
from alpha import max_independent_set


def main(tag, thr=1e-3, time_limit=900.0):
    R = json.load(open(os.path.join(HERE, "results", tag + ".json")))
    d = np.load(os.path.join(HERE, "results", tag + "_graph.npz")); P, G = d["P"], d["G"]
    N = len(P); s = R["s"]
    diag = np.load(os.path.join(HERE, "results", tag + "_B_diag.npy"))
    xs = R["theta"] * diag
    S = np.nonzero(xs > thr)[0]
    S = np.unique(G[:, S].ravel())            # D4-closed
    idx = -np.ones(N, dtype=int); idx[S] = np.arange(len(S))
    PS = P[S]; GS = idx[G[:, S]]
    oid, orbs = orbits(GS); ov = overlap_matrix(PS)
    print(f"[{tag}] support threshold {thr}: |S| = {len(S)} nodes, {len(orbs)} orbits, {ov.sum()//2} edges")
    t0 = time.time()
    r = theta_prime(GS, orbs, ov, eps=1e-7, max_iters=100000, time_limit=time_limit, log=print)
    B = reconstruct_B(r["SB"], r["X"])
    fv, mineig = feasible_value(B, ov)
    delta = max(0.0, -mineig); lb = (fv + len(S) * delta) / (1 + len(S) * delta)
    cert = dual_certificate(r, GS, ov)
    print(f"[{tag}] theta'(G[S]) bracket: {lb:.5f} <= . <= {cert['bound']:.5f}   (SCS {r['status']}, {r['iters']} it, {time.time()-t0:.0f}s)")
    lp = nu_point_lp(PS, s, log=lambda m: None)
    a = max_independent_set(ov, time_limit=60, workers=4)
    print(f"[{tag}] LP on G[S]: nu = {lp['nu']:.5f} (maxcov {lp['maxcov']:.5f});  alpha(G[S]) = {a[0]} {a[2]}")
    R["support_sub"] = dict(thr=thr, n=int(len(S)), orbits=len(orbs), edges=int(ov.sum() // 2), theta_lb=float(lb), theta_ub=cert["bound"],
                            scs_status=r["status"], iters=int(r["iters"]), nu=lp["nu"], nu_maxcov=lp["maxcov"], alpha=a[0], alpha_status=a[2])
    json.dump(R, open(os.path.join(HERE, "results", tag + ".json"), "w"), indent=1, default=float)
    np.save(os.path.join(HERE, "results", tag + "_sub_B.npy"), B)
    np.save(os.path.join(HERE, "results", tag + "_sub_nodes.npy"), S)


if __name__ == "__main__":
    main(sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else 1e-3, float(sys.argv[3]) if len(sys.argv) > 3 else 900.0)
