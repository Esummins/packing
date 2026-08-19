"""A15 driver: build graph, compute nu*_G (point LP), theta'(G) (SDP), alpha(G) (CP-SAT); save results/<tag>.json."""
import argparse, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from graph import build_nodes, d4_action, orbits, overlap_matrix, DEG, admissible
from lp_point import nu_point_lp
from theta_sdp import theta_prime, reconstruct_B, feasible_value, dual_certificate
from alpha import max_independent_set

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))


def extra_placements(s, mid_only=False, a07_ymin=0.05):
    """A12 1/4-structure supports (3.85/3.86/3.87 images) + A07 3.84 dual support (orbit reps with y >= a07_ymin),
    clamped into the admissible region of the container of side s.  Returns list of (cx, cy, theta_rad)."""
    out = []
    for ss in ("3.85", "3.86", "3.87"):
        d = json.load(open(os.path.join(ROOT, "attempts/A12-region-rank-pilot/results", f"analysis_s{ss}.json")))
        for cx, cy, th, w in d["images"]:
            out.append((cx, cy, th))
    d = json.load(open(os.path.join(ROOT, "attempts/A07-lp-dual/results/v2_s3.84.json")))
    for r in d["packing"]:
        if r["y"] >= a07_ymin:
            out.append((r["cx"], r["cy"], r["theta"]))
    res = []
    for cx, cy, th in out:
        th = th % (math.pi / 2)
        thd = math.degrees(th)
        if mid_only and not (thd <= 2.0 or thd >= 88.0 or 30.0 <= thd <= 36.0 or 54.0 <= thd <= 60.0):
            continue
        w = math.cos(th) + math.sin(th)
        cx = min(max(cx, w / 2), s - w / 2); cy = min(max(cy, w / 2), s - w / 2)
        res.append((cx, cy, th))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--s", type=float, required=True)
    ap.add_argument("--h", type=float, default=0.2)
    ap.add_argument("--dtheta", type=float, default=10.0)
    ap.add_argument("--mid", action="store_true", help="mid-tilt restricted angle set {0} u [30,36] (step 1 deg)")
    ap.add_argument("--mid_step", type=float, default=1.0)
    ap.add_argument("--no_extra", action="store_true")
    ap.add_argument("--tag", type=str, required=True)
    ap.add_argument("--eps", type=float, default=1e-5)
    ap.add_argument("--max_iters", type=int, default=50000)
    ap.add_argument("--sdp_time", type=float, default=3600.0)
    ap.add_argument("--alpha_time", type=float, default=300.0)
    ap.add_argument("--no_alpha", action="store_true")
    ap.add_argument("--no_lp", action="store_true")
    ap.add_argument("--no_sdp", action="store_true")
    args = ap.parse_args()
    s = args.s
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    os.makedirs(os.path.join(HERE, "logs"), exist_ok=True)
    logf = open(os.path.join(HERE, "logs", args.tag + ".log"), "a", encoding="utf-8")

    def log(msg):
        print(msg, flush=True); logf.write(msg + "\n"); logf.flush()

    outpath = os.path.join(HERE, "results", args.tag + ".json")
    R = dict(tag=args.tag, s=s, h=args.h, dtheta=args.dtheta, mid=args.mid, extra=not args.no_extra)

    def save():
        json.dump(R, open(outpath, "w"), indent=1, default=float)

    t0 = time.time()
    if args.mid:
        thetas = [0.0] + list(np.arange(30.0, 36.0 + 1e-9, args.mid_step))
    else:
        thetas = list(np.arange(0.0, 90.0, args.dtheta))
    extra = [] if args.no_extra else extra_placements(s, mid_only=args.mid)
    P = build_nodes(s, args.h, thetas, extra=extra)
    G = d4_action(P, s); oid, orbs = orbits(G); ov = overlap_matrix(P)
    N = len(P); nE = int(ov.sum() // 2)
    log(f"[{args.tag}] s={s} h={args.h} thetas={len(thetas)} extra={len(extra)}: N={N} orbits={len(orbs)} edges={nE} density={2*nE/(N*(N-1)):.3f} t={time.time()-t0:.1f}s")
    R.update(N=N, n_orbits=len(orbs), edges=nE, thetas_deg=[float(t) for t in thetas], n_extra=len(extra))
    np.savez_compressed(os.path.join(HERE, "results", args.tag + "_graph.npz"), P=P, G=G)
    save()

    if not args.no_lp:
        t1 = time.time()
        lp = nu_point_lp(P, s, log=log)
        R.update(nu=lp["nu"], nu_maxcov=lp["maxcov"], nu_lb=lp["nu_lb"], lp_points=lp["n_points"], lp_time=time.time() - t1)
        x = lp["x"]
        sup = np.nonzero(x > 1e-6)[0]
        R["lp_support"] = [dict(cx=float(P[i, 0]), cy=float(P[i, 1]), theta_deg=float(np.degrees(P[i, 2])), x=float(x[i])) for i in sup[np.argsort(-x[sup])]]
        np.save(os.path.join(HERE, "results", args.tag + "_lp_x.npy"), x)
        log(f"[{args.tag}] nu*_G = {lp['nu']:.6f} (maxcov {lp['maxcov']:.6f}, {lp['n_points']} points, {len(sup)} support placements, {time.time()-t1:.0f}s)")
        save()

    if not args.no_sdp:
        t1 = time.time()
        r = theta_prime(G, orbs, ov, eps=args.eps, max_iters=args.max_iters, log=log, time_limit=args.sdp_time, verbose=True)
        np.save(os.path.join(HERE, "results", args.tag + "_scs_y.npy"), r["y"])
        B = reconstruct_B(r["SB"], r["X"])
        fv, mineig = feasible_value(B, ov)
        # rigorous-in-spirit bracket: primal-feasible lower bound (B cleaned + delta I) and dual certificate upper bound
        delta = max(0.0, -mineig)
        lb = (fv + N * delta) / (1 + N * delta)
        cert = dual_certificate(r, G, ov)
        R.update(theta_lb_feasible=float(lb), theta_ub_cert=cert["bound"], cert=cert)
        log(f"  bracket: {lb:.6f} <= theta'_G <= {cert['bound']:.6f}  (cert lam {cert['lam']:.6f}, min eig {cert['min_eig']:.1e}, eps {cert['eps_nonedge']:.1e})")
        diagB = np.diag(B)
        R.update(theta=r["theta"], theta_dual=r["theta_dual"], sdp_status=r["status"], sdp_iters=r["iters"], sdp_res_pri=r["res_pri"],
                 sdp_res_dual=r["res_dual"], sdp_gap=r["gap"], sdp_time=time.time() - t1, sdp_blocks=r["SB"]["m"],
                 sdp_pair_orbits=int(r["meta"]["npair"]), B_feasible_value=fv, B_min_eig=mineig,
                 B_min_entry=float(B.min()), B_edge_max=float(np.abs(B[ov]).max()) if ov.any() else 0.0)
        np.save(os.path.join(HERE, "results", args.tag + "_B_diag.npy"), diagB)
        np.save(os.path.join(HERE, "results", args.tag + "_B.npy"), B.astype(np.float32))
        xs = r["theta"] * diagB          # fractional-independent vector (sums to theta')
        sup = np.nonzero(xs > 1e-4)[0]
        R["theta_support"] = [dict(cx=float(P[i, 0]), cy=float(P[i, 1]), theta_deg=float(np.degrees(P[i, 2])), x=float(xs[i])) for i in sup[np.argsort(-xs[sup])][:400]]
        R["theta_support_size"] = int(len(sup))
        ev = np.linalg.eigvalsh(B)
        R["B_eigs_top"] = [float(v) for v in ev[::-1][:20]]
        R["B_rank_1e-3"] = int((ev > 1e-3 * ev.max()).sum())
        log(f"[{args.tag}] theta'_G = {r['theta']:.6f} (dual {r['theta_dual']:.6f}, {r['status']}, {r['iters']} it, {time.time()-t1:.0f}s); cleaned-B value {fv:.6f} (min eig {mineig:.1e}); B rank(1e-3) {R['B_rank_1e-3']}, support {len(sup)}")
        save()

    if not args.no_alpha:
        t1 = time.time()
        hint = None
        a, sel, st, bound = max_independent_set(ov, time_limit=args.alpha_time, workers=4)
        R.update(alpha=a, alpha_status=st, alpha_bound=bound, alpha_time=time.time() - t1,
                 alpha_set=[dict(cx=float(P[i, 0]), cy=float(P[i, 1]), theta_deg=float(np.degrees(P[i, 2]))) for i in sel])
        log(f"[{args.tag}] alpha_G = {a} ({st}, bound {bound}, {time.time()-t1:.0f}s)")
        save()
    log(f"[{args.tag}] done, total {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
