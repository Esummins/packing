"""A16 driver: one case-tree node H on a finite placement graph.
  grid (D4-invariant, h, dtheta) [+ seeds: the node's LP fractional packing support + A15 root structures]
  -> admissible set (A14 hypothesis filter) -> induced graph G_H
  -> nu*_H (point-clique LP), theta'(G_H) (SDP, symmetry = stabiliser of the admissible set in D4, bracket from
     primal-feasible value / dual certificate), alpha(G_H) (CP-SAT), support sub-SDP (tight lower bound on theta').
Everything saved incrementally to results/<tag>.json.
"""
import argparse, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from graph import build_nodes, d4_action, overlap_matrix, DEG
from nodes import make_node, node_seeds, admissible_mask, node_init_points
from theta_sdp import (stabiliser, subgroup_rep, orbits, theta_prime, reconstruct_B, feasible_value, dual_certificate)
from lp_point import nu_point_lp
from alpha import max_independent_set


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--node", required=True)
    ap.add_argument("--s", type=float, required=True)
    ap.add_argument("--h", type=float, default=0.2)
    ap.add_argument("--dtheta", type=float, default=10.0)
    ap.add_argument("--unseeded", action="store_true", help="pure grid, no injected structure")
    ap.add_argument("--no_a15", action="store_true", help="seed only with the node's own LP support (not A15's root structures)")
    ap.add_argument("--ymin", type=float, default=0.01, help="dual-weight threshold for the node's own LP packing seeds")
    ap.add_argument("--a15_mode", type=str, default="all", help="all = A15 extras (A12 3.85/3.86/3.87 + A07 3.84 dual); s = only the A12 structure at this s")
    ap.add_argument("--tag", required=True)
    ap.add_argument("--eps", type=float, default=1e-6)
    ap.add_argument("--max_iters", type=int, default=200000)
    ap.add_argument("--sdp_time", type=float, default=2400.0)
    ap.add_argument("--alpha_time", type=float, default=300.0)
    ap.add_argument("--no_lp", action="store_true")
    ap.add_argument("--lp_time", type=float, default=1500.0)
    ap.add_argument("--lp_tol", type=float, default=5e-4)
    ap.add_argument("--no_sdp", action="store_true")
    ap.add_argument("--no_alpha", action="store_true")
    ap.add_argument("--no_support", action="store_true")
    ap.add_argument("--support_thr", type=float, default=1e-3)
    ap.add_argument("--support_time", type=float, default=1200.0)
    ap.add_argument("--warm", type=str, default=None, help="tag of a previous run of the same graph: warm-start SCS")
    args = ap.parse_args()
    s = args.s
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True); os.makedirs(os.path.join(HERE, "logs"), exist_ok=True)
    logf = open(os.path.join(HERE, "logs", args.tag + ".log"), "a", encoding="utf-8")

    def log(msg):
        print(msg, flush=True); logf.write(msg + "\n"); logf.flush()

    outpath = os.path.join(HERE, "results", args.tag + ".json")
    R = dict(tag=args.tag, node=args.node, s=s, h=args.h, dtheta=args.dtheta, seeded=not args.unseeded, a15_extras=(not args.unseeded and not args.no_a15))

    def save():
        json.dump(R, open(outpath, "w"), indent=1, default=float)

    t0 = time.time()
    hyp, budget, desc, seed_files = make_node(args.node, s)
    R.update(budget=budget, desc=desc, hyp=hyp.to_json())
    thetas = list(np.arange(0.0, 90.0, args.dtheta))
    # stage 1: pure D4-invariant grid -> stabiliser H of the admissible set (= symmetry group of the node)
    Pg = build_nodes(s, args.h, thetas)
    Gg = d4_action(Pg, s)
    gl = stabiliser(Gg, admissible_mask(hyp, Pg))
    # stage 2: add the seeds closed under H only (keeps N small at C1/Z2 nodes), H-action on the final set
    seeds = [] if args.unseeded else node_seeds(args.node, s, seed_files, ymin=args.ymin, with_a15=not args.no_a15, a15_mode=args.a15_mode)
    P = build_nodes(s, args.h, thetas, extra=seeds, extra_group=gl)
    Gfull = d4_action(P, s, gl)                      # (|H|, N_grid) action of H
    keep = admissible_mask(hyp, P)
    kidx = np.nonzero(keep)[0]
    gl2 = stabiliser(Gfull, keep)
    assert len(gl2) == len(gl), ("admissible set not H-invariant after seeding", gl, gl2)
    Gs, rho, gname = subgroup_rep(Gfull, list(range(len(gl))), kidx)
    oid, orbs = orbits(Gs)
    PK = P[kidx]
    ov = overlap_matrix(PK)
    N = len(PK); nE = int(ov.sum() // 2)
    log(f"[{args.tag}] node {args.node} ({desc}) s={s} budget={budget} h={args.h} dtheta={args.dtheta} seeded={not args.unseeded} "
        f"(seeds {len(seeds)}): grid {len(P)} -> admissible N={N}, group {gname} (|H|={len(gl)}), orbits={len(orbs)}, edges={nE}, "
        f"density={2*nE/max(1,N*(N-1)):.3f} t={time.time()-t0:.1f}s")
    R.update(N=N, N_grid=len(P), n_seeds=len(seeds), group=gname, group_order=len(gl), n_orbits=len(orbs), edges=nE, thetas_deg=[float(t) for t in thetas])
    np.savez_compressed(os.path.join(HERE, "results", args.tag + "_graph.npz"), P=PK, G=Gs, Pfull=P, kidx=kidx)
    save()

    if not args.no_lp:
        t1 = time.time()
        ipts = node_init_points(seed_files, s) if not args.unseeded else None
        log(f"  LP init points from A14 atoms: {0 if ipts is None else len(ipts)}")
        lp = nu_point_lp(PK, s, log=log, init_pts=ipts, time_limit=args.lp_time, tol=args.lp_tol)
        R.update(nu=lp["nu"], nu_maxcov=lp["maxcov"], nu_lb=lp["nu_lb"], lp_points=lp["n_points"], lp_time=time.time() - t1)
        x = lp["x"]
        sup = np.nonzero(x > 1e-6)[0]
        R["lp_support"] = [dict(cx=float(PK[i, 0]), cy=float(PK[i, 1]), theta_deg=float(np.degrees(PK[i, 2])), x=float(x[i])) for i in sup[np.argsort(-x[sup])]]
        np.save(os.path.join(HERE, "results", args.tag + "_lp_x.npy"), x)
        log(f"[{args.tag}] nu*_H = {lp['nu']:.6f} (maxcov {lp['maxcov']:.6f}, {lp['n_points']} points, {len(sup)} support, {time.time()-t1:.0f}s)  budget {budget}  slack {lp['nu']-budget:+.4f}")
        save()

    if not args.no_sdp:
        t1 = time.time()
        warm = None
        if args.warm:
            wp = os.path.join(HERE, "results", args.warm + "_scs_xys.npz")
            if os.path.exists(wp):
                d = np.load(wp); warm = dict(x=d["x"], y=d["y"], s=d["s"]); log(f"  warm start from {args.warm}")
        r = theta_prime(Gs, orbs, ov, rho, eps=args.eps, max_iters=args.max_iters, log=log, time_limit=args.sdp_time, verbose=True, warm=warm)
        np.savez_compressed(os.path.join(HERE, "results", args.tag + "_scs_xys.npz"), x=r["x"], y=r["y"], s=r["s"])
        B = reconstruct_B(r["SB"], r["X"])
        fv, mineig = feasible_value(B, ov)
        delta = max(0.0, -mineig)
        lb = (fv + N * delta) / (1 + N * delta)
        cert = dual_certificate(r, Gs, ov)
        R.update(theta_lb_feasible=float(lb), theta_ub_cert=cert["bound"], cert=cert)
        log(f"  bracket: {lb:.6f} <= theta'_H <= {cert['bound']:.6f}  (cert lam {cert['lam']:.6f}, min eig {cert['min_eig']:.1e}, eps {cert['eps_nonedge']:.1e})")
        diagB = np.diag(B)
        R.update(theta=r["theta"], theta_dual=r["theta_dual"], sdp_status=r["status"], sdp_iters=r["iters"], sdp_res_pri=r["res_pri"],
                 sdp_res_dual=r["res_dual"], sdp_gap=r["gap"], sdp_time=time.time() - t1, sdp_blocks=r["SB"]["m"],
                 sdp_pair_orbits=int(r["meta"]["npair"]), B_feasible_value=fv, B_min_eig=mineig)
        np.save(os.path.join(HERE, "results", args.tag + "_B_diag.npy"), diagB)
        xs = r["theta"] * diagB
        sup = np.nonzero(xs > 1e-4)[0]
        R["theta_support"] = [dict(cx=float(PK[i, 0]), cy=float(PK[i, 1]), theta_deg=float(np.degrees(PK[i, 2])), x=float(xs[i])) for i in sup[np.argsort(-xs[sup])][:400]]
        R["theta_support_size"] = int(len(sup))
        ev = np.linalg.eigvalsh(B)
        R["B_rank_1e-3"] = int((ev > 1e-3 * ev.max()).sum())
        log(f"[{args.tag}] theta'_H ~ {r['theta']:.6f} (dual {r['theta_dual']:.6f}, {r['status']}, {r['iters']} it, {time.time()-t1:.0f}s); bracket [{lb:.4f}, {cert['bound']:.4f}]; budget {budget}; ub slack {cert['bound']-budget:+.4f}")
        save()

        if not args.no_support:
            t2 = time.time()
            S = np.nonzero(xs > args.support_thr)[0]
            S = np.unique(Gs[:, S].ravel())
            idx = -np.ones(N, dtype=int); idx[S] = np.arange(len(S))
            GS = idx[Gs[:, S]]; oidS, orbsS = orbits(GS); ovS = ov[np.ix_(S, S)]
            log(f"  support sub-SDP: |S| = {len(S)} nodes, {len(orbsS)} orbits, {ovS.sum()//2} edges (thr {args.support_thr})")
            rs = theta_prime(GS, orbsS, ovS, rho, eps=1e-7, max_iters=300000, time_limit=args.support_time, log=log)
            BS = reconstruct_B(rs["SB"], rs["X"])
            fvS, meS = feasible_value(BS, ovS)
            dS = max(0.0, -meS); lbS = (fvS + len(S) * dS) / (1 + len(S) * dS)
            certS = dual_certificate(rs, GS, ovS)
            lpS = nu_point_lp(PK[S], s, log=lambda m: None)
            aS = max_independent_set(ovS, time_limit=120, workers=4)
            R["support_sub"] = dict(thr=args.support_thr, n=int(len(S)), orbits=len(orbsS), edges=int(ovS.sum() // 2), theta_lb=float(lbS), theta_ub=certS["bound"],
                                    scs_status=rs["status"], iters=int(rs["iters"]), nu=lpS["nu"], nu_maxcov=lpS["maxcov"], alpha=aS[0], alpha_status=aS[2], time=time.time() - t2)
            np.save(os.path.join(HERE, "results", args.tag + "_sub_nodes.npy"), S)
            log(f"[{args.tag}] theta'(G[S]) in [{lbS:.5f}, {certS['bound']:.5f}] ({rs['status']}, {rs['iters']} it); LP on G[S] {lpS['nu']:.5f}; alpha(G[S]) {aS[0]} ({aS[2]}); "
                f"=> theta'_H bracket [{max(lbS, lb):.4f}, {cert['bound']:.4f}]  ({time.time()-t2:.0f}s)")
            save()

    if not args.no_alpha:
        t1 = time.time()
        a, sel, st, bound = max_independent_set(ov, time_limit=args.alpha_time, workers=4)
        R.update(alpha=a, alpha_status=st, alpha_bound=bound, alpha_time=time.time() - t1,
                 alpha_set=[dict(cx=float(PK[i, 0]), cy=float(PK[i, 1]), theta_deg=float(np.degrees(PK[i, 2]))) for i in sel])
        log(f"[{args.tag}] alpha_H = {a} ({st}, bound {bound}, {time.time()-t1:.0f}s)  budget {budget}")
        save()
    log(f"[{args.tag}] done, total {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
