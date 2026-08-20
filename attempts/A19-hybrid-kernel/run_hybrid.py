"""A19 -- driver: hybrid kernel (diag + free R-block) at full atom resolution.

python run_hybrid.py --s 3.84 --atoms a07_384 --tag h384 [--iters 10] [--resume]
    [--cmin 3] [--kcap 340] [--enrich 0.0] [--delta_pair 1e-3]

Phases: (0) init diag rows from the A18 state (same-rows gate (a): F=0 SDP must reproduce A18's GP
value), (1) binding inventory + R-atom selection (+ optional w=0 enrichment atoms), (2) cutting-
plane loop with diag oracle (A17) + localised pair oracle, (3) final strongest attack.
State saved every iteration; --resume continues.
"""
import argparse, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "A17-kernel-root"))
sys.path.insert(0, os.path.join(HERE, "..", "A18-restricted-kernel"))

A18RES = os.path.join(ROOT, "attempts", "A18-restricted-kernel", "results")
A17RES = os.path.join(ROOT, "attempts", "A17-kernel-root", "results")
A12RES = os.path.join(ROOT, "attempts", "A12-region-rank-pilot", "results")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--s", type=float, required=True)
    ap.add_argument("--atoms", required=True, choices=["cert380", "cert382", "a07_384"])
    ap.add_argument("--tag", required=True)
    ap.add_argument("--iters", type=int, default=10)
    ap.add_argument("--cmin", type=int, default=3, help="min #binding covers for an R-atom")
    ap.add_argument("--kcap", type=int, default=200)
    ap.add_argument("--enrich", type=float, default=0.0, help="grid step for w=0 enrichment atoms (0=off)")
    ap.add_argument("--delta_pair", type=float, default=1e-3)
    ap.add_argument("--bind_margin", type=float, default=0.30)
    ap.add_argument("--row_keep", type=float, default=0.9, help="diag rows kept within this of the F=0 optimum")
    ap.add_argument("--row_cap", type=int, default=3500)
    ap.add_argument("--pair_cap", type=int, default=1600)
    ap.add_argument("--solver", default=None, help="force solver for loop solves (e.g. SCS)")
    ap.add_argument("--n_rand", type=int, default=40000)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--resume", action="store_true")
    args = ap.parse_args()
    s = args.s
    rng = np.random.default_rng(args.seed)
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    os.makedirs(os.path.join(HERE, "logs"), exist_ok=True)
    logf = open(os.path.join(HERE, "logs", args.tag + ".log"), "a", encoding="utf-8")

    def log(msg):
        print(msg, flush=True)
        logf.write(msg + "\n")
        logf.flush()

    from features import (FeatureMap, load_atoms_a07_384, load_atoms_cert, stretch_1d,
                          structured_placements, random_placements)
    from oracle_diag import diag_oracle, boundary_sweep
    from oracle_pair import overlap_depth_many
    from hybrid import HybridSDP, HybridKernel, d4_orbit_pts
    from oracles import ratio_seeds_g, pair_oracle_local
    from full_sdp import fundamental_rep

    t0 = time.time()
    if args.atoms == "a07_384":
        A, w, s_at = load_atoms_a07_384()
        if abs(s_at - s) > 1e-12:
            A = np.stack([stretch_1d(A[:, 0], s_at, s), stretch_1d(A[:, 1], s_at, s)], 1)
        a18_state = os.path.join(A18RES, "r384_state.npz")
    else:
        cert = {"cert380": "measure_certificate_3.80.json",
                "cert382": "measure_certificate_3.82.json"}[args.atoms]
        A, w, _ = load_atoms_cert(os.path.join(ROOT, "certs", cert), s_to=s)
        a18_state = os.path.join(A18RES, "r380b_state.npz")

    state_path = os.path.join(HERE, "results", args.tag + "_state.npz")
    json_path = os.path.join(HERE, "results", args.tag + ".json")
    hist = []
    resumed = args.resume and os.path.exists(state_path)

    # ---------------- phase 0/1: rows + binding inventory + R selection (or resume)
    if resumed:
        st = np.load(state_path, allow_pickle=True)
        A = st["A"]; w = st["w"]
        fm = FeatureMap(A, w, s)
        r_mask = st["r_mask"].astype(bool)
        hs = HybridSDP(fm, None, delta_pair=args.delta_pair, r_mask=r_mask)
        nd = hs.add_diag(st["diag_pts"])
        npr = 0
        if len(st["pair_x"]):
            PX, PY = st["pair_x"], st["pair_y"]
            if len(PX) > args.pair_cap:
                ke_t = HybridKernel(hs, st["g_orb"], st["f"])
                kv = ke_t.kpair(PX, PY)
                keep = np.argsort(-kv)[:args.pair_cap]   # near-active pair rows only
                PX, PY = PX[keep], PY[keep]
            npr = hs.add_pairs(PX, PY)
        lam_auto = float(st["lam_auto"])
        it0 = int(st["it"]) + 1
        if os.path.exists(json_path):
            hist = json.load(open(json_path)).get("history", [])
        log(f"[{args.tag}] resumed at it {it0}: {nd} diag rows, {npr} pair rows, "
            f"k={hs.k}, lam_auto={lam_auto:.4f}")
    else:
        it0 = 0
        st18 = np.load(a18_state, allow_pickle=True)
        row_pts = np.asarray(st18["row_pts"])
        fm = FeatureMap(A, w, s)
        log(f"[{args.tag}] s={s} atoms={fm.m} tau={w.sum():.4f} | A18 rows {len(row_pts)}")

        # gate (a): F=0 SDP on the A18 row set == A18 GP value
        hs0 = HybridSDP(fm, None, delta_pair=args.delta_pair)
        nd0 = hs0.add_diag(row_pts)
        r0 = hs0.solve(allow_F=False)
        lam_auto = r0["lam"]
        log(f"[{args.tag}] GATE (a): F=0 SDP on A18 rows ({nd0} deduped) lam = {lam_auto:.6f} "
            f"({r0['time']:.0f}s)  [A18 lam_rows ref: r384 11.1438 / r380b 10.5063]")

        # binding inventory: attack the F=0 kernel
        ke0 = HybridKernel(hs0, r0["g_orb"], None)
        extra = ratio_seeds_g(fm, s, ke0.g_atom, dth_deg=0.5, cstep=0.01, log=log)
        rd = diag_oracle(ke0, s, structP=structured_placements(s), rng=rng,
                         n_rand=args.n_rand, n_polish=60, log=log, extra_seeds=extra)
        vb, xb = rd["best"]
        log(f"[{args.tag}] F=0 attack: lam = {1+vb:.6f} at ({xb[0]:.4f},{xb[1]:.4f},"
            f"{math.degrees(xb[2]):.2f}deg)")
        bind = [x for v, x in rd["cands"] if v > vb - args.bind_margin]
        # mid-tilt structures: A12 images (stretched) + A17 near-contact CENTRAL mid-tilt pair
        # endpoints (tight filter -- the inventory defines R, so it must stay local)
        if args.atoms == "a07_384":
            d = json.load(open(os.path.join(A12RES, "analysis_s3.85.json")))
            f = s / 3.85
            for cx, cy, t, _ in d["images"]:
                if 0.2 < t < 1.4:
                    bind.append(np.array([cx * f, cy * f, t]))
            k17 = np.load(os.path.join(A17RES, "k384_state.npz"), allow_pickle=True)
            X17, Y17 = k17["pair_x"], k17["pair_y"]
            dep = overlap_depth_many(X17, Y17)
            sel = dep > -0.04
            c0 = s / 2
            for P in (X17[sel], Y17[sel]):
                for p in P:
                    if (math.radians(18) < p[2] % (math.pi / 2) < math.radians(72)
                            and math.hypot(p[0] - c0, p[1] - c0) < 1.15):
                        bind.append(p)
        bind = np.array(bind).reshape(-1, 3)
        log(f"[{args.tag}] binding inventory: {len(bind)} placements")

        # enrichment atoms (w = 0) on a grid where binding coverage >= 2
        if args.enrich > 0:
            he = args.enrich
            gx = np.arange(he / 2, s / 2 + 1e-9, he)
            reps = [(x, y) for x in gx for y in gx if x <= y + 1e-12]
            reps = np.array(reps)
            # keep reps covered by >= 2 binding placements
            c, sn = np.cos(bind[:, 2])[:, None], np.sin(bind[:, 2])[:, None]
            dx = reps[None, :, 0] - bind[:, 0][:, None]
            dy = reps[None, :, 1] - bind[:, 1][:, None]
            uu = c * dx + sn * dy; vv = -sn * dx + c * dy
            cov = ((np.abs(uu) <= 0.5) & (np.abs(vv) <= 0.5)).sum(0)
            keep = reps[cov >= 2]
            from hybrid import enrich_atoms
            A, w, n_new = enrich_atoms(A, w, s, keep, w_new=0.0)
            fm = FeatureMap(A, w, s)
            log(f"[{args.tag}] enrichment: +{n_new} zero-weight atoms (grid {he}) -> m={fm.m}")

        # R-atoms: top-kcap by binding-cover count, added orbit by orbit (D4-exact)
        pat_b = fm.patterns(bind)
        cnt = np.asarray(pat_b.sum(axis=0)).ravel()
        from hybrid import atom_orbits
        oid0, orbs0 = atom_orbits(fm)
        score = np.array([cnt[mem].max() for mem in orbs0])
        order = np.argsort(-score)
        in_R = np.zeros(fm.m, bool)
        tot = 0
        for o in order:
            if score[o] < args.cmin:
                break
            if tot + len(orbs0[o]) > args.kcap:
                continue
            in_R[orbs0[o]] = True
            tot += len(orbs0[o])
        log(f"[{args.tag}] R selection: k={int(in_R.sum())} R-atoms of {fm.m} "
            f"(min score kept {score[order][in_R[np.array([orbs0[o][0] for o in order])].nonzero()[0][-1]] if in_R.any() else 0})")
        r_mask = in_R

        hs = HybridSDP(fm, None, delta_pair=args.delta_pair, r_mask=r_mask)
        # PRUNE the A18 row set: Clarabel chokes on ~7k dense rows x F-block. Keep the rows that
        # are near-binding for the automatic optimum, plus every R-covering row (they carry the
        # F quadratic), capped; the cutting-plane loop restores anything dropped in error.
        kd0 = ke0.kdiag(row_pts)
        patR0 = fm.patterns(row_pts)[:, np.nonzero(r_mask)[0]]
        rcov = np.asarray(patR0.sum(axis=1)).ravel() > 0
        near = kd0 >= (lam_auto - 1.0) - args.row_keep
        sel = np.nonzero(near | rcov)[0]
        if len(sel) > args.row_cap:
            order = np.argsort(-kd0[sel])
            sel = sel[order[:args.row_cap]]
        log(f"[{args.tag}] row pruning: {len(row_pts)} -> {len(sel)} "
            f"(near-binding {int(near.sum())}, R-covering {int(rcov.sum())})")
        hs.add_diag(row_pts[sel])
        hs.add_diag(bind)
        hs.add_diag(np.array([x for v, x in rd["cands"][:300]]))
        # initial pair rows: A17 inventory + localised tangent pairs
        ke_init = HybridKernel(hs, r0["g_orb"][:hs.n_orb] if len(r0["g_orb"]) == hs.n_orb
                               else np.ones(hs.n_orb), None)
        hull = (fm.A[r_mask, 0].min(), fm.A[r_mask, 0].max(),
                fm.A[r_mask, 1].min(), fm.A[r_mask, 1].max())
        if args.atoms == "a07_384":
            k17 = np.load(os.path.join(A17RES, "k384_state.npz"), allow_pickle=True)
            X17, Y17 = k17["pair_x"], k17["pair_y"]
            dep17 = overlap_depth_many(X17, Y17)
            selp = np.argsort(-dep17)[:args.pair_cap]      # barely-disjoint first
            npr = hs.add_pairs(X17[selp], Y17[selp])
        else:
            npr = 0
        from oracles import tangent_pairs_local
        TX, TY = tangent_pairs_local(ke_init, s, 8000, rng, hull)
        npr += hs.add_pairs(TX[:max(0, args.pair_cap - npr)], TY[:max(0, args.pair_cap - npr)])
        log(f"[{args.tag}] initial rows: {len(hs.diag_meta)} diag, {npr} pair "
            f"(t={time.time()-t0:.0f}s)")

    hull = (fm.A[r_mask, 0].min(), fm.A[r_mask, 0].max(),
            fm.A[r_mask, 1].min(), fm.A[r_mask, 1].max())
    c0 = s / 2
    rR = max(math.hypot(x - c0, y - c0) for x, y in fm.A[r_mask])
    log(f"[{args.tag}] R hull {tuple(round(h,3) for h in hull)}, radius {rR:.3f} "
        f"(pair-verif centres within {rR + 0.7072:.3f} of centre)")

    def save_state(it, lam_auto, sol):
        np.savez_compressed(state_path,
                            A=fm.A, w=fm.w, r_mask=r_mask,
                            diag_pts=np.array(hs.diag_meta),
                            pair_x=np.array([p[0] for p in hs.pair_meta]).reshape(-1, 3),
                            pair_y=np.array([p[1] for p in hs.pair_meta]).reshape(-1, 3),
                            g_orb=sol["g_orb"], f=sol["f"], it=it, lam_auto=lam_auto)

    def save_json(extra=None):
        d = dict(tag=args.tag, s=s, atoms=args.atoms, m=fm.m, k=int(hs.k),
                 n_forb=int(hs.n_forb), lam_auto=lam_auto, delta_pair=args.delta_pair,
                 history=hist)
        if extra:
            d.update(extra)
        json.dump(d, open(json_path, "w"), indent=1, default=float)

    # ---------------- phase 2: cutting-plane loop
    structP = structured_placements(s)
    sol = None
    for it in range(it0, args.iters):
        t1 = time.time()
        sol = hs.solve(solver=args.solver) if args.solver else hs.solve()
        lam = sol["lam"]
        ke = hs.kernel(sol["g_orb"], sol["f"])
        extra = ratio_seeds_g(fm, s, ke.g_atom, dth_deg=0.5, cstep=0.01, log=log)
        rd = diag_oracle(ke, s, structP=(structP if it % 2 == 0 else None), rng=rng,
                         n_rand=args.n_rand, n_polish=50, log=log, extra_seeds=extra)
        maxd, xd = rd["best"]
        hot = np.array([x for v, x in rd["cands"][:100]])
        rp = pair_oracle_local(ke, s, hull, rng,
                               nodesP=np.vstack([structP, hot]),
                               seed_pairs=(np.array([p[0] for p in hs.pair_meta]).reshape(-1, 3),
                                           np.array([p[1] for p in hs.pair_meta]).reshape(-1, 3))
                               if hs.pair_meta else None,
                               n_tangent=10000, n_polish=35,
                               viol_thresh=-1.0 - args.delta_pair + 1e-6, log=log)
        maxp = rp["best"][0]
        viol_d = maxd - (lam - 1.0)
        viol_p = maxp - (-1.0 - args.delta_pair)
        dv = [x for v, x in rd["cands"] if v > lam - 1.0 - 0.02]
        nd_add = hs.add_diag(np.array(dv)) if dv else 0
        pv = [(x, y) for v, x, y in rp["cands"] if v > -1.0 - args.delta_pair - 0.02 and x is not None]
        pv += [(x, y) for v, x, y in rp.get("viols", [])]
        np_add = hs.add_pairs(np.array([p[0] for p in pv]).reshape(-1, 3),
                              np.array([p[1] for p in pv]).reshape(-1, 3)) if pv else 0
        hist.append(dict(it=it, lam=lam, maxdiag=maxd, maxpair=maxp, viol_diag=viol_d,
                         viol_pair=viol_p, nd=len(hs.diag_meta), npair=len(hs.pair_meta),
                         added_d=nd_add, added_p=np_add, solve_t=sol["time"],
                         xd=list(map(float, xd)), t=time.time() - t1))
        log(f"[{args.tag}] it {it}: lam {lam:.6f} | maxdiag {maxd:.5f} (viol {viol_d:+.2e}) "
            f"maxpair {maxp:.6f} (viol {viol_p:+.2e}) | +{nd_add}d +{np_add}p rows "
            f"({len(hs.diag_meta)}d/{len(hs.pair_meta)}p) | solve {sol['time']:.0f}s "
            f"tot {time.time()-t1:.0f}s")
        save_state(it, lam_auto, sol)
        save_json()
        if viol_d <= 1e-7 and viol_p <= 1e-7:
            log(f"[{args.tag}] oracles exhausted: STOP at lam {lam:.6f}")
            break

    # ---------------- phase 3: final strongest attack
    log(f"[{args.tag}] === final attack ===")
    if sol is None:
        sol = hs.solve()
    ke = hs.kernel(sol["g_orb"], sol["f"])
    best_d, arg_d, best_p = -np.inf, None, -np.inf
    for seed in range(3):
        rr = np.random.default_rng(900 + seed)
        extra = ratio_seeds_g(fm, s, ke.g_atom, dth_deg=0.25, cstep=0.005, log=log)
        rd = diag_oracle(ke, s, structP=(structP if seed == 0 else None), rng=rr,
                         n_rand=70000, n_polish=80, bnd_theta=181, bnd_step=0.02,
                         log=log, extra_seeds=extra)
        if rd["best"][0] > best_d:
            best_d, arg_d = rd["best"]
        rp = pair_oracle_local(ke, s, hull, rr,
                               nodesP=(structP if seed == 0 else None),
                               seed_pairs=(np.array([p[0] for p in hs.pair_meta]).reshape(-1, 3),
                                           np.array([p[1] for p in hs.pair_meta]).reshape(-1, 3)),
                               n_tangent=30000, n_polish=60, log=log)
        if rp["best"][0] > best_p:
            best_p = rp["best"][0]
    c = 1.0 / min(1.0, -best_p) if best_p < 0 else float("inf")
    lam_cert = 1.0 + c * best_d
    log(f"[{args.tag}] FINAL: lam_sdp {sol['lam']:.6f} | attack maxdiag {best_d:.6f} at "
        f"{arg_d} | maxpair {best_p:.8f} | c {c:.6f} | lam_cert {lam_cert:.5f} "
        f"| lam_auto {lam_auto:.5f}")
    save_json(extra=dict(final=dict(lam_sdp=sol["lam"], maxdiag=best_d, maxpair=best_p,
                                    c=c, lam_cert=lam_cert,
                                    arg_d=list(map(float, arg_d)) if arg_d is not None else None,
                                    k=int(hs.k), total_time=time.time() - t0)))
    log(f"[{args.tag}] done, total {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
