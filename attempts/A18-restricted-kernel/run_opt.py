"""A18 -- driver: optimise the restricted-class kernel (= two-measure family, by the collapse
theorem) at a given s over a growing row set, with A17-style float oracle attacks.

python run_opt.py --s 3.80 --atoms cert380 --tag r380 [--iters 8] [--resume]
python run_opt.py --s 3.84 --atoms a07_384 --tag r384

Reports: lambda(u=1) (calibration: must equal tau/m_min), lambda(u*) after convex u-optimisation
(the exact class optimum for these atoms/weights, up to oracle completeness), row-LP tau*_rows
(the value the class would reach with w re-optimised = the plain LP), all under the strongest
float attack.  State saved every iteration; --resume continues.
"""
import argparse, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "A17-kernel-root"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--s", type=float, required=True)
    ap.add_argument("--atoms", required=True, choices=["cert380", "cert381", "cert382", "a07_384"])
    ap.add_argument("--tag", required=True)
    ap.add_argument("--iters", type=int, default=8)
    ap.add_argument("--n_rand", type=int, default=50000)
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--final_scale", type=float, default=1.0)
    ap.add_argument("--inject", default=None, help="npy file of placements (N,3) to add as rows")
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
    from oracle_diag import boundary_sweep, low_coverage_placements
    from two_measure import TwoMeasureKernel, attack
    import scipy.sparse as sp

    t0 = time.time()
    if args.atoms == "a07_384":
        A, w, s_at = load_atoms_a07_384()
        if abs(s_at - s) > 1e-12:
            A = np.stack([stretch_1d(A[:, 0], s_at, s), stretch_1d(A[:, 1], s_at, s)], 1)
    else:
        cert = {"cert380": "measure_certificate_3.80.json",
                "cert381": "measure_certificate_3.81.json",
                "cert382": "measure_certificate_3.82.json"}[args.atoms]
        A, w, _ = load_atoms_cert(os.path.join(ROOT, "certs", cert), s_to=s)
    fm = FeatureMap(A, w, s)
    tau = float(w.sum())
    ke = TwoMeasureKernel(fm)
    log(f"[{args.tag}] s={s} atoms={len(A)} ({ke.n_orb} orbits) tau={tau:.6f} t={time.time()-t0:.0f}s")

    # ---------------- rows (placements; patterns rebuilt on the fly), dedup by canon key
    keys = set()
    row_pts = []          # list of placements
    pat_blocks = []

    def add_rows(pts):
        pts = np.atleast_2d(np.asarray(pts, float))
        pat = fm.patterns(pts)
        newp = []
        for i in range(len(pts)):
            nz = pat.indices[pat.indptr[i]:pat.indptr[i + 1]]
            if len(nz) == 0:
                continue
            k = fm.canon_key(nz)
            if k in keys:
                continue
            keys.add(k)
            newp.append(i)
            row_pts.append(pts[i].copy())
        if newp:
            pat_blocks.append(pat[newp])
        return len(newp)

    def pat_all():
        return sp.vstack(pat_blocks, format="csr") if pat_blocks else None

    state_path = os.path.join(HERE, "results", args.tag + "_state.npz")
    json_path = os.path.join(HERE, "results", args.tag + ".json")
    hist = []
    it0 = 0
    lam_u1 = None

    if args.resume and os.path.exists(state_path):
        st = np.load(state_path, allow_pickle=True)
        add_rows(st["row_pts"])
        ke.theta_orb = st["theta_orb"]
        it0 = int(st["it"]) + 1
        lam_u1 = float(st["lam_u1"])
        if os.path.exists(json_path):
            hist = json.load(open(json_path)).get("history", [])
        log(f"[{args.tag}] resumed at it {it0}: {len(row_pts)} rows")
        if args.inject:
            ninj = add_rows(np.load(args.inject))
            log(f"[{args.tag}] injected {ninj} new rows from {args.inject}")
    else:
        n0 = add_rows(structured_placements(s))
        n0 += add_rows(random_placements(s, 6000, rng))
        n0 += add_rows(boundary_sweep(s, n_theta=121, step_c=0.03))
        lowP, lowcov = low_coverage_placements(fm, s, dth_deg=0.5, cstep=0.01, n_polish=150, log=log)
        n0 += add_rows(lowP)
        log(f"[{args.tag}] initial rows: {n0} (min exact coverage {lowcov.min():.6f})")

        # ---------------- calibration: u = 1 (C = 0, the pure LP-form kernel), full-strength attack
        ke.theta_orb[:] = 0.0
        v1, x1 = -np.inf, None
        for seed in range(3):
            rr = np.random.default_rng(5000 + seed)
            rd = attack(ke, fm, s, rr, structP=None, n_rand=50000, n_polish=60,
                        bnd_theta=181, bnd_step=0.02, with_ratio=(seed == 0),
                        dth_deg=0.25, cstep=0.005, log=log)
            add_rows(np.array([x for v, x in rd["cands"][:300]]))
            if rd["best"][0] > v1:
                v1, x1 = rd["best"]
        lam_u1 = 1.0 + v1
        log(f"[{args.tag}] CALIBRATION u=1: lambda = {lam_u1:.6f} "
            f"(= tau/m_min: m_min from this = {tau/lam_u1:.6f}) at "
            f"({x1[0]:.4f},{x1[1]:.4f},{math.degrees(x1[2]):.2f}deg)")

    def save_state(it):
        np.savez_compressed(state_path, row_pts=np.array(row_pts), theta_orb=ke.theta_orb,
                            it=it, lam_u1=lam_u1)

    def save_json(extra=None):
        d = dict(tag=args.tag, s=s, atoms=args.atoms, n_atoms=len(A), n_orbits=ke.n_orb,
                 tau=tau, lam_u1=lam_u1, history=hist)
        if extra:
            d.update(extra)
        json.dump(d, open(json_path, "w"), indent=1, default=float)

    # ---------------- cutting-plane loop on the diagonal (the only side that exists here)
    clean = 0
    for it in range(it0, args.iters):
        t1 = time.time()
        pat = pat_all()
        lam_rows = ke.optimize(pat, log=log)
        rd = attack(ke, fm, s, rng, structP=(structured_placements(s) if it % 3 == 0 else None),
                    n_rand=args.n_rand, n_polish=70, bnd_theta=181, bnd_step=0.02,
                    with_ratio=True, dth_deg=0.25, cstep=0.005, log=log)
        vb, xb = rd["best"]
        lam_att = 1.0 + vb
        viol = lam_att - lam_rows
        cands = [x for v, x in rd["cands"] if 1.0 + v > lam_rows - 0.02]
        nadd = add_rows(np.array(cands)) if cands else 0
        hist.append(dict(it=it, nrows=len(row_pts), lam_rows=lam_rows, lam_attack=lam_att,
                         viol=viol, added=nadd,
                         x=[float(xb[0]), float(xb[1]), float(math.degrees(xb[2]))],
                         t=time.time() - t1, n_zero_cov=ke.n_zero))
        log(f"[{args.tag}] it {it}: lam_rows {lam_rows:.6f} | attack {lam_att:.6f} "
            f"(viol {viol:+.2e}) at ({xb[0]:.3f},{xb[1]:.3f},{math.degrees(xb[2]):.2f}deg) "
            f"| +{nadd} rows (total {len(row_pts)}) | {time.time()-t1:.0f}s")
        save_state(it)
        save_json()
        clean = clean + 1 if (viol <= 1e-7 and nadd == 0) else 0
        if clean >= 2:
            log(f"[{args.tag}] oracle exhausted twice in a row: STOP")
            break

    # ---------------- final strongest attack + row-LP reference
    log(f"[{args.tag}] === final attack ===")
    best = (-np.inf, None)
    sc = args.final_scale
    for seed in range(3):
        rr = np.random.default_rng(2000 + seed)
        rd = attack(ke, fm, s, rr, structP=(structured_placements(s) if seed == 0 else None),
                    n_rand=int(70000 * sc), n_polish=80, bnd_theta=181, bnd_step=0.02,
                    with_ratio=(seed == 0), dth_deg=0.25, cstep=0.005, log=log)
        add_rows(np.array([x for v, x in rd["cands"][:200]]))   # feed back for later --resume
        if rd["best"][0] > best[0]:
            best = rd["best"]
    save_state(len(hist) - 1 if hist else 0)
    lam_final = 1.0 + best[0]
    xb = best[1]
    log(f"[{args.tag}] FINAL lambda(u*) = {lam_final:.6f} at "
        f"({xb[0]:.4f},{xb[1]:.4f},{math.degrees(xb[2]):.2f}deg)   [lambda(u=1) = {lam_u1:.6f}]")

    # row-LP: what the class reaches with w free (= the plain LP on these rows)
    from scipy.optimize import linprog
    pat = pat_all()
    lp = linprog(c=np.ones(fm.m), A_ub=-pat, b_ub=-np.ones(pat.shape[0]),
                 bounds=(0, None), method="highs")
    tau_rows = float(lp.fun) if lp.status == 0 else float("nan")
    log(f"[{args.tag}] row-LP tau*_rows = {tau_rows:.6f} (class bound with w free; "
        f"continuum tau*(s) from A07 applies)")
    save_json(extra=dict(final=dict(lam_final=lam_final, lam_u1=lam_u1,
                                    x=[float(xb[0]), float(xb[1]), float(math.degrees(xb[2]))],
                                    tau_rows=tau_rows, n_rows=len(row_pts),
                                    total_time=time.time() - t0)))
    np.save(os.path.join(HERE, "results", args.tag + "_theta.npy"), ke.theta_orb)
    log(f"[{args.tag}] done, total {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
