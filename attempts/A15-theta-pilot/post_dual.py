"""Post-process: rebuild the dual certificate Z from saved SCS multipliers; report its spectrum (rank -> basis size
needed for a kernel K = phi^T M phi) and the structure of the primal B."""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from graph import d4_action, orbits, overlap_matrix
from theta_sdp import theta_prime, symmetry_basis, build_scs, dual_certificate, pair_orbit_of_all, IRREPS


def rebuild_Z(tag):
    R = json.load(open(os.path.join(HERE, "results", tag + ".json")))
    d = np.load(os.path.join(HERE, "results", tag + "_graph.npz")); P, G = d["P"], d["G"]
    s = R["s"]; N = len(P)
    oid, orbs = orbits(G); ov = overlap_matrix(P)
    SB = symmetry_basis(G, orbs)
    data, cone, meta = build_scs(G, orbs, ov, SB, log=lambda m: None, trace_scale=float(N))
    meta["trace_scale"] = float(N)
    y = np.load(os.path.join(HERE, "results", tag + "_scs_y.npy"))
    r = dict(meta=meta, y=y)
    isE = meta["isE"]; I = meta["I"]; J = meta["J"]; cnt = meta["cnt"]
    nz = int(isE.sum()) + 1; npos = int((~isE).sum())
    lam = y[0] * N; yE = y[1:nz] * N; yP = y[nz:nz + npos] * N
    ymul = np.zeros(len(I)); ymul[isE] = yE; ymul[~isE] = -yP
    II, JJ, o = pair_orbit_of_all(G, I, J)
    Z = lam * np.eye(N) - np.ones((N, N))
    v = ymul[o] * (0.5 / cnt[o]); Z[II, JJ] += v; Z[JJ, II] += v
    w, U = np.linalg.eigh(Z)
    return R, P, ov, Z, w, U, lam


if __name__ == "__main__":
    for tag in sys.argv[1:]:
        R, P, ov, Z, w, U, lam = rebuild_Z(tag)
        N = len(P)
        print(f"[{tag}] s={R['s']} N={N} nu={R.get('nu'):.4f} theta bracket [{R.get('theta_lb_feasible'):.4f}, {R.get('theta_ub_cert'):.4f}] alpha={R.get('alpha')}")
        print(f"   Z: lam={lam:.4f} eig min={w.min():.2e} max={w.max():.2f}; rank(>1e-3 max)={int((w > 1e-3 * w.max()).sum())} rank(>1e-2)={int((w > 1e-2 * w.max()).sum())} rank(>0.1)={int((w > 0.1 * w.max()).sum())}")
        print("   top eigs:", np.round(w[::-1][:15], 3))
        nonadj = ~ov & ~np.eye(N, dtype=bool)
        print(f"   non-edge entries: max {Z[nonadj].max():.4f}, mean {Z[nonadj].mean():.4f}; edge entries: min {Z[ov].min():.3f} max {Z[ov].max():.3f} mean {Z[ov].mean():.3f}; diag min {np.diag(Z).min():.3f} max {np.diag(Z).max():.3f}")
        R["Z_eigs_top"] = [float(x) for x in w[::-1][:30]]
        R["Z_rank_1e-2"] = int((w > 1e-2 * w.max()).sum()); R["Z_rank_1e-3"] = int((w > 1e-3 * w.max()).sum())
        json.dump(R, open(os.path.join(HERE, "results", tag + ".json"), "w"), indent=1, default=float)
