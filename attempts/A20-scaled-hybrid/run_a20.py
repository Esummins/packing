"""A20 -- driver: hybrid kernel with the R-block scaled to the FULL tight structure,
D4-block-diagonalised (k+1)-cone (block_sdp.BlockHybridSDP).

python run_a20.py --s 3.80 --atoms cert380 --tag b380 --iters 8 --kcap 600
python run_a20.py --s 3.84 --atoms a07_384 --tag b384 --iters 8 --kcap 600

Differences vs A19's run_hybrid.py:
  * R selection targets the WHOLE tight set: binding inventory = F=0 attack candidates within
    --bind_margin (default 0.5) of the supremum + A12 images + A17 pair endpoints (NO radius
    filter) + (3.84) the exact LP-floor placements of lp_floor_384.json with jitters;
  * BlockHybridSDP (isotypic PSD blocks) so Clarabel survives k ~ 600;
  * optional --fdist cutoff on the F support (sqrt(2) = co-occurrence bound).
State saved at init and every iteration; --resume continues.
"""
import argparse, json, math, os, sys, time
from fractions import Fraction as Fr
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "attempts", "A19-hybrid-kernel"))
sys.path.insert(0, os.path.join(ROOT, "attempts", "A17-kernel-root"))
sys.path.insert(0, os.path.join(ROOT, "attempts", "A18-restricted-kernel"))

A18RES = os.path.join(ROOT, "attempts", "A18-restricted-kernel", "results")
A17RES = os.path.join(ROOT, "attempts", "A17-kernel-root", "results")
A12RES = os.path.join(ROOT, "attempts", "A12-region-rank-pilot", "results")
A19DIR = os.path.join(ROOT, "attempts", "A19-hybrid-kernel")


def lp_floor_placements(rng, n_jit=24):
    d = json.load(open(os.path.join(A19DIR, "lp_floor_384.json")))
    out = []
    for p in d["placements"]:
        cx = float(Fr(p["cx"])); cy = float(Fr(p["cy"]))
        th = math.atan2(float(Fr(p["sin"])), float(Fr(p["cos"]))) % (math.pi / 2)
        out.append((cx, cy, th))
        for _ in range(n_jit):
            out.append((cx + rng.normal(0, 0.15), cy + rng.normal(0, 0.15),
                        (th + rng.normal(0, 0.09)) % (math.pi / 2)))
    return np.array(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--s", type=float, required=True)
    ap.add_argument("--atoms", required=True, choices=["cert380", "cert382", "a07_384"])
    ap.add_argument("--tag", required=True)
    ap.add_argument("--iters", type=int, default=8)
    ap.add_argument("--cmin", type=int, default=2)
    ap.add_argument("--kcap", type=int, default=600)
    ap.add_argument("--fdist", type=float, default=0.0, help="F-support distance cutoff (0=off)")
    ap.add_argument("--delta_pair", type=float, default=1e-3)
    ap.add_argument("--bind_margin", type=float, default=0.5)
    ap.add_argument("--row_keep", type=float, default=0.9)
    ap.add_argument("--row_cap", type=int, default=3000)
    ap.add_argument("--pair_cap", type=int, default=1500)
    ap.add_argument("--n_rand", type=int, default=40000)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--solve_only", action="store_true", help="phase 1 + one solve, no loop")
    args = ap.parse_args()
    s = args.s
    fdist = args.fdist if args.fdist > 0 else None
    rng = np.random.default_rng(args.seed)
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    os.makedirs(os.path.join(HERE, "logs"), exist_ok=True)
    logf = open(os.path.join(HERE, "logs", args.tag + ".log"), "a", encoding="utf-8")

    def log(msg):
        print(msg, flush=True)
        logf.write(msg + "\n")
        logf.flush()

    from features import (FeatureMap, load_atoms_a07_384, load_atoms_cert, stretch_1d,
                          structured_placements)
    from oracle_diag import diag_oracle
    from oracle_pair import overlap_depth_many
    from hybrid import HybridKernel, atom_orbits
    from oracles import ratio_seeds_g, pair_oracle_local, tangent_pairs_local
    from block_sdp import BlockHybridSDP

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

    if resumed:
        st = np.load(state_path, allow_pickle=True)
        A = st["A"]; w = st["w"]
        fm = FeatureMap(A, w, s)
        r_mask = st["r_mask"].astype(bool)
        hs = BlockHybridSDP(fm, None, delta_pair=args.delta_pair, r_mask=r_mask, fdist=fdist)
        nd = hs.add_diag(st["diag_pts"])
        npr = 0
        if len(st["pair_x"]):
            PX, PY = st["pair_x"], st["pair_y"]
            if len(PX) > args.pair_cap and st["g_orb"].shape:
                ke_t = HybridKernel(hs, st["g_orb"], st["f"] if len(st["f"]) == hs.n_forb else None)
                kv = ke_t.kpair(PX, PY)
                keep = np.argsort(-kv)[:args.pair_cap]
                PX, PY = PX[keep], PY[keep]
            npr = hs.add_pairs(PX, PY)
        lam_auto = float(st["lam_auto"])
        it0 = int(st["it"]) + 1
        if os.path.exists(json_path):
            hist = json.load(open(json_path)).get("history", [])
        log(f"[{args.tag}] resumed at it {it0}: {nd} diag, {npr} pair, k={hs.k}, "
            f"n_forb={hs.n_forb}, lam_auto={lam_auto:.4f}")
    else:
        it0 = 0
        st18 = np.load(a18_state, allow_pickle=True)
        row_pts = np.asarray(st18["row_pts"])
        fm = FeatureMap(A, w, s)
        log(f"[{args.tag}] s={s} atoms={fm.m} tau={w.sum():.4f} | A18 rows {len(row_pts)} | "
            f"kcap={args.kcap} fdist={fdist}")

        # gate (a): F=0 SDP on the A18 row set == A18 GP value (k=0: pure convex, no blocks)
        hs0 = BlockHybridSDP(fm, None, delta_pair=args.delta_pair)
        nd0 = hs0.add_diag(row_pts)
        r0 = hs0.solve(allow_F=False)
        lam_auto = r0["lam"]
        log(f"[{args.tag}] GATE (a): F=0 SDP on A18 rows ({nd0}) lam = {lam_auto:.6f} "
            f"({r0['time']:.0f}s) [refs: r384 11.1438 / r380b 10.5063]")

        # binding inventory (FULL tight set)
        ke0 = HybridKernel(hs0, r0["g_orb"], None)
        extra = ratio_seeds_g(fm, s, ke0.g_atom, dth_deg=0.5, cstep=0.01, log=log)
        rd = diag_oracle(ke0, s, structP=structured_placements(s), rng=rng,
                         n_rand=args.n_rand, n_polish=60, topk=4000, log=log,
                         extra_seeds=extra)
        vb, xb = rd["best"]
        log(f"[{args.tag}] F=0 attack: lam = {1+vb:.6f} at ({xb[0]:.4f},{xb[1]:.4f},"
            f"{math.degrees(xb[2]):.2f}deg)")
        bind = [x for v, x in rd["cands"] if v > vb - args.bind_margin]
        n_att = len(bind)
        # + the near-binding subset of the accumulated A18 rows (the converged tight set)
        kd18 = ke0.kdiag(row_pts)
        near18 = row_pts[kd18 >= vb - args.bind_margin]
        bind.extend(list(near18))
        log(f"[{args.tag}] inventory: {n_att} fresh attack cands + {len(near18)} near-binding A18 rows")
        if args.atoms == "a07_384":
            d = json.load(open(os.path.join(A12RES, "analysis_s3.85.json")))
            fsc = s / 3.85
            for cx, cy, t, _ in d["images"]:
                if 0.2 < t < 1.4:
                    bind.append(np.array([cx * fsc, cy * fsc, t]))
            k17 = np.load(os.path.join(A17RES, "k384_state.npz"), allow_pickle=True)
            X17, Y17 = k17["pair_x"], k17["pair_y"]
            dep = overlap_depth_many(X17, Y17)
            sel = dep > -0.04
            for P in (X17[sel], Y17[sel]):
                for p in P:
                    if math.radians(10) < p[2] % (math.pi / 2) < math.radians(80):
                        bind.append(p)
            LF = lp_floor_placements(rng)
            # keep admissible ones
            wv = np.cos(LF[:, 2]) + np.sin(LF[:, 2])
            ok = ((LF[:, 0] >= wv / 2) & (LF[:, 0] <= s - wv / 2) &
                  (LF[:, 1] >= wv / 2) & (LF[:, 1] <= s - wv / 2))
            bind.extend(list(LF[ok]))
            log(f"[{args.tag}] inventory: {n_att} attack cands + A12/A17 + {int(ok.sum())} LP-floor pts")
        bind = np.array(bind).reshape(-1, 3)
        log(f"[{args.tag}] binding inventory: {len(bind)} placements")

        # R-atoms: top-kcap by binding-cover count, orbit by orbit
        pat_b = fm.patterns(bind)
        cnt = np.asarray(pat_b.sum(axis=0)).ravel()
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
        r_mask = in_R
        log(f"[{args.tag}] R selection: k={int(in_R.sum())} of {fm.m}")

        hs = BlockHybridSDP(fm, None, delta_pair=args.delta_pair, r_mask=r_mask, fdist=fdist)
        log(f"[{args.tag}] n_forb = {hs.n_forb}")
        hs.build_blocks(log=log)
        # prune A18 rows: near-binding OR R-covering, capped by kdiag rank
        kd0 = ke0.kdiag(row_pts)
        patR0 = fm.patterns(row_pts)[:, np.nonzero(r_mask)[0]]
        rcov = np.asarray(patR0.sum(axis=1)).ravel() > 0
        near = kd0 >= (lam_auto - 1.0) - args.row_keep
        sel = np.nonzero(near | rcov)[0]
        if len(sel) > args.row_cap:
            order = np.argsort(-kd0[sel])
            sel = sel[order[:args.row_cap]]
        log(f"[{args.tag}] row pruning: {len(row_pts)} -> {len(sel)} "
            f"(near {int(near.sum())}, R-cov {int(rcov.sum())})")
        hs.add_diag(row_pts[sel])
        hs.add_diag(bind)
        hs.add_diag(np.array([x for v, x in rd["cands"][:300]]))
        # initial pair rows: A17 + A19 inventories + localised tangent pairs
        ke_init = HybridKernel(hs, np.ones(hs.n_orb), None)
        hull = (fm.A[r_mask, 0].min(), fm.A[r_mask, 0].max(),
                fm.A[r_mask, 1].min(), fm.A[r_mask, 1].max())
        npr = 0
        if args.atoms == "a07_384":
            k17 = np.load(os.path.join(A17RES, "k384_state.npz"), allow_pickle=True)
            X17, Y17 = k17["pair_x"], k17["pair_y"]
            dep17 = overlap_depth_many(X17, Y17)
            selp = np.argsort(-dep17)[:args.pair_cap]
            npr = hs.add_pairs(X17[selp[:args.pair_cap * 2 // 3]], Y17[selp[:args.pair_cap * 2 // 3]])
        a19tag = {"a07_384": "h384", "cert380": "h380"}.get(args.atoms)
        if a19tag:
            st19 = np.load(os.path.join(A19DIR, "results", a19tag + "_state.npz"),
                           allow_pickle=True)
            if len(st19["pair_x"]):
                PX19, PY19 = st19["pair_x"], st19["pair_y"]
                room = max(0, args.pair_cap - npr)
                if len(PX19) > room:
                    dep19 = overlap_depth_many(PX19, PY19)
                    sel19 = np.argsort(-dep19)[:room]
                    PX19, PY19 = PX19[sel19], PY19[sel19]
                npr += hs.add_pairs(PX19, PY19)
        TX, TY = tangent_pairs_local(ke_init, s, 8000, rng, hull)
        room = max(0, args.pair_cap + 300 - npr)
        npr += hs.add_pairs(TX[:room], TY[:room])
        log(f"[{args.tag}] initial rows: {len(hs.diag_meta)} diag, {npr} pair "
            f"(t={time.time()-t0:.0f}s)")

    hull = (fm.A[r_mask, 0].min(), fm.A[r_mask, 0].max(),
            fm.A[r_mask, 1].min(), fm.A[r_mask, 1].max())
    c0 = s / 2
    rR = max(math.hypot(x - c0, y - c0) for x, y in fm.A[r_mask])
    log(f"[{args.tag}] R hull {tuple(round(h,3) for h in hull)}, radius {rR:.3f}")

    def save_state(it, sol):
        np.savez_compressed(state_path,
                            A=fm.A, w=fm.w, r_mask=r_mask,
                            diag_pts=np.array(hs.diag_meta),
                            pair_x=np.array([p[0] for p in hs.pair_meta]).reshape(-1, 3),
                            pair_y=np.array([p[1] for p in hs.pair_meta]).reshape(-1, 3),
                            g_orb=sol["g_orb"] if sol else np.zeros(0),
                            f=sol["f"] if sol else np.zeros(0), it=it, lam_auto=lam_auto)

    def save_json(extra=None):
        d = dict(tag=args.tag, s=s, atoms=args.atoms, m=fm.m, k=int(hs.k),
                 n_forb=int(hs.n_forb), fdist=fdist, lam_auto=lam_auto,
                 delta_pair=args.delta_pair, history=hist)
        if extra:
            d.update(extra)
        json.dump(d, open(json_path, "w"), indent=1, default=float)

    if not resumed:
        save_state(-1, None)
        save_json()

    structP = structured_placements(s)
    sol = None
    for it in range(it0, args.iters):
        t1 = time.time()
        sol = hs.solve(log=log)
        lam = sol["lam"]
        log(f"[{args.tag}] it {it}: SOLVE lam {lam:.6f} ({sol['time']:.0f}s, {sol['status']})")
        if args.solve_only:
            save_state(it, sol)
            save_json(extra=dict(solve_only_lam=lam))
            log(f"[{args.tag}] --solve_only: stop")
            return
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
            f"maxpair {maxp:.6f} (viol {viol_p:+.2e}) | +{nd_add}d +{np_add}p "
            f"({len(hs.diag_meta)}d/{len(hs.pair_meta)}p) | solve {sol['time']:.0f}s "
            f"tot {time.time()-t1:.0f}s")
        save_state(it, sol)
        save_json()
        if viol_d <= 1e-7 and viol_p <= 1e-7:
            log(f"[{args.tag}] oracles exhausted: STOP at lam {lam:.6f}")
            break

    # final same-rows F on/off comparison (the decisive number)
    if sol is not None:
        rF0 = hs.solve(allow_F=False, log=log)
        log(f"[{args.tag}] SAME-ROWS: hybrid {sol['lam']:.6f} vs F=0 {rF0['lam']:.6f} "
            f"-> F buys {rF0['lam']-sol['lam']:+.6f}")
        save_json(extra=dict(final=dict(lam_hybrid=sol["lam"], lam_F0=rF0["lam"],
                                        total_time=time.time() - t0)))
    log(f"[{args.tag}] done, total {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
