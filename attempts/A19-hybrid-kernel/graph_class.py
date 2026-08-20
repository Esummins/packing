"""A19 -- decisive diagnostic (dispatch item 4): the EXACT value of the pattern-kernel class on
the finite A15 c384 graph (N = 2337, true theta' = 10.376-10.392, LP = 11.000, alpha = 10).

Class: K(x,y) = phi(x)^T M phi(y), phi = (1, a/m) over A07's 1181 atoms; constraints ONLY on the
graph: K(v,v) <= lam - 1 for all nodes, K(u,v) <= -1 for all NON-adjacent pairs (disjoint
interiors; this graph's adjacency = interior overlap, so non-edges include touching pairs --
slightly STRONGER than the continuum requirement, i.e. this value UPPER-bounds what the touching-
exempt class could do... we exclude touching pairs by SAT depth < -1e-9 to match the bridge).
Solved with A17's Burer-Monteiro machinery; the pair oracle is EXACT (finite graph: full K).

Variants: (a) full class (all cross terms), (b) hybrid restriction... (b) is approximated by
projecting out non-R cross terms is NOT valid for BM; instead we report (a) and compare with the
convex hybrid value from the runs. If (a) >= 11 on the graph where theta' = 10.38, the indicator
class is INTRINSICALLY too weak at 3.84 -- the gap is the feature basis, not the oracles.
"""
import json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "A17-kernel-root"))


def main(rank=120, iters=30, tag="gclass384"):
    from features import FeatureMap, load_atoms_a07_384, build_symmetry
    from sdp import KernelSDP
    from oracle_pair import overlap_depth_many
    logf = open(os.path.join(HERE, "logs", tag + ".log"), "a", encoding="utf-8")

    def log(msg):
        print(msg, flush=True)
        logf.write(msg + "\n"); logf.flush()

    t0 = time.time()
    A, w, s = load_atoms_a07_384()
    fm = FeatureMap(A, w, s)
    sym = build_symmetry(fm)
    g = np.load(os.path.join(ROOT, "attempts", "A15-theta-pilot", "results", "c384_graph.npz"),
                allow_pickle=True)
    P = np.asarray(g["P"], float)
    N = len(P)
    log(f"[{tag}] graph N={N}; atoms {fm.m}; blocks {sym['SB']['m']}")
    # SAT depth matrix (chunked) -> strictly disjoint pairs mask
    from oracle_pair import depth_matrix
    dep = depth_matrix(P, chunk=400)
    disj = dep < -1e-9
    np.fill_diagonal(disj, False)
    log(f"[{tag}] strictly disjoint pairs: {disj.sum()//2} of {N*(N-1)//2}")
    Phi = fm.phi(P)

    prob = KernelSDP(sym, delta_pair=1e-4)
    # all node diag rows (orbit-dedup happens implicitly through identical patterns? no --
    # KernelSDP has no dedup; add all N as rows, fine)
    prob.add_diag_rows(Phi)
    # initial pair rows: barely-disjoint pairs
    iu = np.triu_indices(N, 1)
    dv = dep[iu]
    sel = np.nonzero((dv < -1e-9) & (dv > -0.05))[0]
    sel = sel[np.argsort(-dv[sel])][:2500]
    prob.add_pair_rows(Phi[iu[0][sel]], Phi[iu[1][sel]])
    log(f"[{tag}] initial rows: {prob.nrows}")

    M0 = (1.0 + 2e-4) * fm.M_lp()
    Y = prob.init_Y(rank=rank, M0=M0)
    lam = None
    added_hist = []
    for it in range(iters):
        t1 = time.time()
        r = prob.minimize_lambda(Y={n: Y[n].copy() for n in prob.names}, lam0=lam,
                                 step0=0.12, min_step=0.01, maxiter=300,
                                 time_limit=420, log=lambda m: None, lam_floor=10.35)
        Y = r["Y"]; lam = r["lam"]
        # EXACT oracle on the graph: full K
        L = np.vstack([Y[n] @ sym["Ts"][n][rr].toarray().T
                       for n in prob.names for rr in range(sym["SB"]["dims"][n])])
        U = np.asarray(Phi @ L.T)
        K = U @ U.T
        kd = np.diag(K)
        maxdiag = kd.max()
        Km = np.where(disj, K, -np.inf)
        kv = Km[iu]
        mx = kv.max()
        viol = np.nonzero(kv > -1.0 - 1e-4 + 1e-7)[0]
        viol = viol[np.argsort(-kv[viol])][:1200]
        nadd = 0
        if len(viol):
            nadd = len(viol)
            prob.add_pair_rows(Phi[iu[0][viol]], Phi[iu[1][viol]])
        log(f"[{tag}] it {it}: lam {lam:.6f} | graph maxdiag {maxdiag:.5f} "
            f"(viol {maxdiag-(lam-1):+.1e}) maxpair {mx:.6f} | +{nadd} pair rows "
            f"(total {prob.nrows}) | {time.time()-t1:.0f}s")
        json.dump(dict(it=it, lam=lam, maxdiag=float(maxdiag), maxpair=float(mx),
                       nrows=prob.nrows, t=time.time() - t0),
                  open(os.path.join(HERE, "results", tag + ".json"), "w"), indent=1)
        if maxdiag - (lam - 1.0) <= 1e-7 and mx <= -1.0 - 1e-4 + 1e-7:
            log(f"[{tag}] EXACT graph oracles clean: pattern-class value on c384 graph = "
                f"{lam:.6f}  (theta' = 10.38, LP = 11.000)")
            break
    log(f"[{tag}] done ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()
