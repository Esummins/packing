"""A17 — cutting-plane loop for the root kernel certificate.

python loop.py --s 3.84 --tag k384 [--iters 10] [--rank 120] [--resume] [--attack_only]

Loop: solve the kernel SDP (Burer-Monteiro blocks, warm-started) on the current row set, attack the
resulting kernel with the diag / pair oracles, add every violated (and near-active) row, repeat.
State (Y factors + all row placements) saved every iteration; --resume continues after a crash.
Final: strongest float attack, report lambda_cert = 1 + c*maxdiag, c = 1/min(1, -maxpair).
"""
import argparse, json, math, os, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--s", type=float, default=3.84)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--atoms", default="a07_384", choices=["a07_384", "cert382"])
    ap.add_argument("--iters", type=int, default=10)
    ap.add_argument("--rank", type=int, default=120)
    ap.add_argument("--delta_pair", type=float, default=1e-3)
    ap.add_argument("--maxiter", type=int, default=250, help="L-BFGS iterations per feasibility solve")
    ap.add_argument("--sdp_time", type=float, default=360.0, help="per-loop-iteration SDP time budget (s)")
    ap.add_argument("--lam_step", type=float, default=0.15)
    ap.add_argument("--n_diag0", type=int, default=900)
    ap.add_argument("--n_pair0", type=int, default=1300)
    ap.add_argument("--row_cap", type=int, default=3000)
    ap.add_argument("--gap0", type=float, default=0.08)
    ap.add_argument("--lam_floor", type=float, default=10.40)
    ap.add_argument("--tol_oracle", type=float, default=1e-6)
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--attack_only", action="store_true")
    ap.add_argument("--attack_scale", type=float, default=1.0)
    args = ap.parse_args()
    s = args.s
    rng = np.random.default_rng(args.seed)
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    logf = open(os.path.join(HERE, "logs", args.tag + ".log"), "a", encoding="utf-8")

    def log(msg):
        print(msg, flush=True)
        logf.write(msg + "\n")
        logf.flush()

    from features import (FeatureMap, load_atoms_a07_384, load_atoms_cert, structured_placements,
                          build_symmetry, stretch_1d)
    from sdp import KernelSDP
    from oracle_pair import KernelEval, pair_oracle, depth_matrix, tangent_pairs
    from oracle_diag import diag_oracle

    t0 = time.time()
    if args.atoms == "a07_384":
        A, w, s_at = load_atoms_a07_384()
        if abs(s_at - s) > 1e-12:
            A = np.stack([stretch_1d(A[:, 0], s_at, s), stretch_1d(A[:, 1], s_at, s)], 1)
    else:
        ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
        A, w, _ = load_atoms_cert(os.path.join(ROOT, "certs", "measure_certificate_3.82.json"), s_to=s)
    fm = FeatureMap(A, w, s)
    tau = float(w.sum())
    sym = build_symmetry(fm)
    log(f"[{args.tag}] s={s} atoms={len(A)} tau={tau:.4f} blocks={sym['SB']['m']} t={time.time()-t0:.0f}s")

    prob = KernelSDP(sym, delta_pair=args.delta_pair)
    meta = []          # per row: ('d', x) or ('p', x, y)
    keys = set()

    P_struct = structured_placements(s)
    Phi_struct = fm.phi(P_struct)
    dep_struct = depth_matrix(P_struct)
    log(f"[{args.tag}] structured set N={len(P_struct)}")

    def add_diag(pts):
        pts = np.atleast_2d(np.asarray(pts, float))
        pat = fm.patterns(pts)
        newp = []
        for i in range(len(pts)):
            nz = pat.indices[pat.indptr[i]:pat.indptr[i + 1]]
            k = ('d', fm.canon_key(nz))
            if k in keys:
                continue
            keys.add(k)
            newp.append(i)
            meta.append(('d', pts[i].copy(), None, k))
        if newp:
            prob.add_diag_rows(fm.phi(pat=pat[newp]))
        return len(newp)

    def add_pairs(X, Y):
        X = np.atleast_2d(np.asarray(X, float)); Y = np.atleast_2d(np.asarray(Y, float))
        pat1 = fm.patterns(X); pat2 = fm.patterns(Y)
        newp = []
        for i in range(len(X)):
            nz1 = pat1.indices[pat1.indptr[i]:pat1.indptr[i + 1]]
            nz2 = pat2.indices[pat2.indptr[i]:pat2.indptr[i + 1]]
            k = ('p', fm.canon_key_pair(nz1, nz2))
            if k in keys:
                continue
            keys.add(k)
            newp.append(i)
            meta.append(('p', X[i].copy(), Y[i].copy(), k))
        if newp:
            prob.add_pair_rows(fm.phi(pat=pat1[newp]), fm.phi(pat=pat2[newp]))
        return len(newp)

    state_path = os.path.join(HERE, "results", args.tag + "_state.npz")
    json_path = os.path.join(HERE, "results", args.tag + ".json")
    hist = []
    Y = None
    lam = None

    if (args.resume or args.attack_only) and os.path.exists(state_path):
        st = np.load(state_path, allow_pickle=True)
        dp = st["diag_pts"]
        px, py = st["pair_x"], st["pair_y"]
        nd = add_diag(dp) if len(dp) else 0
        npr = add_pairs(px, py) if len(px) else 0
        Y = {n: st["Y_" + n] for n in prob.names}
        lam = float(st["lam"])
        if os.path.exists(json_path):
            hist = json.load(open(json_path)).get("history", [])
        log(f"[{args.tag}] resumed: {nd} diag rows, {npr} pair rows, lam {lam:.4f}")
    else:
        # ---------------- initial rows
        nd = add_diag(P_struct)
        Pr = None
        from features import random_placements
        Pr = random_placements(s, 8000, rng)
        # keep the highest-K_LP random ones and a spread
        nd += add_diag(Pr[:args.n_diag0])
        log(f"[{args.tag}] initial diag rows: {nd}")
        iu = np.triu_indices(len(P_struct), 1)
        depv = dep_struct[iu]
        sel = np.nonzero((depv < 0) & (depv > -args.gap0))[0]
        order = sel[np.argsort(-depv[sel])]
        Xp = P_struct[iu[0][order[:4 * args.n_pair0]]]
        Yp = P_struct[iu[1][order[:4 * args.n_pair0]]]
        np_added = add_pairs(Xp[:args.n_pair0 * 2], Yp[:args.n_pair0 * 2])
        TX, TY = tangent_pairs(s, 1200, rng)
        np_added += add_pairs(TX[:500], TY[:500])
        log(f"[{args.tag}] initial pair rows: {np_added} (from {len(sel)} barely-disjoint structured pairs)")
        M0 = (1.0 + 2 * args.delta_pair) * fm.M_lp()
        Y = prob.init_Y(rank=args.rank, M0=M0)

    def save_state(Y, lam):
        dp = np.array([m[1] for m in meta if m[0] == 'd']).reshape(-1, 3)
        px = np.array([m[1] for m in meta if m[0] == 'p']).reshape(-1, 3)
        py = np.array([m[2] for m in meta if m[0] == 'p']).reshape(-1, 3)
        np.savez_compressed(state_path, diag_pts=dp, pair_x=px, pair_y=py, lam=lam,
                            **{"Y_" + n: Y[n] for n in prob.names})

    def save_json(extra=None):
        d = dict(tag=args.tag, s=s, atoms=args.atoms, n_atoms=len(A), tau=tau,
                 rank=args.rank, delta_pair=args.delta_pair, history=hist)
        if extra:
            d.update(extra)
        json.dump(d, open(json_path, "w"), indent=1, default=float)

    def make_ke(Y):
        L = np.vstack([Y[n] @ sym["Ts"][n][r].toarray().T
                       for n in prob.names for r in range(sym["SB"]["dims"][n])])
        return KernelEval(fm, L)

    # ---------------- main loop
    if not args.attack_only:
        for it in range(len(hist), args.iters):
            t1 = time.time()
            r = prob.minimize_lambda(Y={n: Y[n].copy() for n in prob.names}, lam0=lam,
                                     step0=args.lam_step, min_step=0.02, maxiter=args.maxiter,
                                     time_limit=args.sdp_time, log=log, lam_floor=args.lam_floor)
            Y = r["Y"]; lam = r["lam"]
            ke = make_ke(Y)
            rd = diag_oracle(ke, s, structP=P_struct, rng=rng, n_rand=40000, n_polish=50, log=log,
                             extra_seeds=(lowP_loop if 'lowP_loop' in dir() else None))
            from features import random_placements as _rp_
            hot = np.array([x for v, x in rd["cands"][:120]]).reshape(-1, 3)
            Pnodes = np.vstack([P_struct, _rp_(s, 600, rng), hot])
            rp = pair_oracle(ke, s, nodesP=Pnodes, rng=rng,
                             n_tangent=15000, n_polish=35, log=log,
                             viol_thresh=-1.0 - args.delta_pair + args.tol_oracle, viol_cap=700)
            maxd, xd = rd["best"]
            maxp, xp, yp = rp["best"]
            c = 1.0 / min(1.0, -maxp) if maxp < 0 else float("inf")
            lam_rep = 1.0 + c * maxd
            # rows to add: diag above lam-1 (violated) and near-active; pairs above -1-delta (rows) and -1 (real)
            dv = [x for v, x in rd["cands"] if v > lam - 1.0 + args.tol_oracle]
            dn = [x for v, x in rd["cands"] if lam - 1.0 - 0.03 < v <= lam - 1.0 + args.tol_oracle]
            pv = [(x, y) for v, x, y in rp["cands"] if v > -1.0 - args.delta_pair + args.tol_oracle]
            pv += [(x, y) for v, x, y in rp.get("viols", [])]
            nd_add = add_diag(np.array(dv + dn[:30])) if (dv or dn) else 0
            np_add = add_pairs(np.array([p[0] for p in pv[:1100]]), np.array([p[1] for p in pv[:1100]])) if pv else 0
            viol_d = maxd - (lam - 1.0)
            viol_p = maxp - (-1.0 - args.delta_pair)
            hist.append(dict(it=it, nrows=prob.nrows, lam_sdp=lam, maxdiag=maxd, maxpair=maxp,
                             viol_diag=viol_d, viol_pair=viol_p, lam_report=lam_rep,
                             added_diag=nd_add, added_pair=np_add,
                             diag_x=list(map(float, xd)), pair_xy=list(map(float, np.concatenate([xp, yp]))),
                             t=time.time() - t1))
            log(f"[{args.tag}] it {it}: lam_sdp {lam:.4f} | oracle maxdiag {maxd:.5f} (viol {viol_d:+.2e}) "
                f"maxpair {maxp:.6f} (viol {viol_p:+.2e}) | lam_report {lam_rep:.4f} | +{nd_add} diag +{np_add} pair rows "
                f"(total {prob.nrows}) | {time.time()-t1:.0f}s")
            save_state(Y, lam)
            save_json()
            # row cap: drop very slack pair rows
            if prob.nrows > args.row_cap:
                K = prob.row_values(Y)
                g = K - prob.rhs(lam)
                isd = prob._stack()["isd"]
                slack_pairs = np.nonzero((~isd) & (g < -0.25))[0]
                ndrop = prob.nrows - args.row_cap
                if len(slack_pairs) > 0 and ndrop > 0:
                    drop = set(slack_pairs[np.argsort(g[slack_pairs])][:ndrop].tolist())
                    keep = np.array([i not in drop for i in range(prob.nrows)])
                    for i in drop:
                        keys.discard(meta[i][3])
                    meta[:] = [m for i, m in enumerate(meta) if keep[i]]
                    prob.drop_rows(keep)
                    log(f"[{args.tag}]   dropped {len(drop)} slack pair rows -> {prob.nrows}")
            if viol_d <= args.tol_oracle and viol_p <= args.tol_oracle:
                log(f"[{args.tag}] oracles found no violation above {args.tol_oracle}: STOP at lam {lam:.4f}")
                break

    # ---------------- final strongest attack
    log(f"[{args.tag}] === final attack ===")
    from oracle_diag import low_coverage_placements
    lowP, lowcov = low_coverage_placements(fm, s, dth_deg=0.25, cstep=0.005, n_polish=250, log=log)
    log(f"[{args.tag}] covscan: exact min coverage {lowcov.min():.6f}")
    ke = make_ke(Y)
    sc = args.attack_scale
    best_d = -np.inf; best_p = -np.inf; arg_d = None; arg_p = None
    for seed in range(3):
        rr = np.random.default_rng(1000 + seed)
        rd = diag_oracle(ke, s, structP=(P_struct if seed == 0 else None), rng=rr,
                         n_rand=int(80000 * sc), n_polish=80, bnd_theta=181, bnd_step=0.02, log=log,
                         extra_seeds=lowP[:200])
        if rd["best"][0] > best_d:
            best_d, arg_d = rd["best"]
        rp = pair_oracle(ke, s, nodesP=(P_struct if seed == 0 else None),
                         node_dep=(dep_struct if seed == 0 else None), rng=rr,
                         n_tangent=int(40000 * sc), n_polish=60, log=log)
        if rp["best"][0] > best_p:
            v, x, y = rp["best"]
            best_p, arg_p = v, (x, y)
    c = 1.0 / min(1.0, -best_p) if best_p < 0 else float("inf")
    lam_cert = 1.0 + c * best_d
    log(f"[{args.tag}] ATTACK: maxdiag {best_d:.6f} at {arg_d}; maxpair {best_p:.8f}; "
        f"c {c:.6f}; lambda_cert = {lam_cert:.5f}  (lam_sdp {lam if lam else float('nan'):.5f})")
    M = prob.get_M(Y)
    np.save(os.path.join(HERE, "results", args.tag + "_M.npy"), M)
    save_state(Y, lam if lam is not None else lam_cert)
    save_json(extra=dict(final=dict(maxdiag=best_d, maxpair=best_p, c=c, lam_cert=lam_cert,
                                    arg_d=list(map(float, arg_d)) if arg_d is not None else None,
                                    arg_p=[list(map(float, arg_p[0])), list(map(float, arg_p[1]))] if arg_p else None,
                                    total_time=time.time() - t0)))
    log(f"[{args.tag}] done, total {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
