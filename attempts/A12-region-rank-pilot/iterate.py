"""Iterated region-rank cuts: each round boxes the current fractional support (rho, rho_theta), certifies
k(R) <= alpha(G_robust), adds R as a new dual variable, re-solves warm.  Records tau, lambda, x(R), and how far the
support moved.   python iterate.py --s 3.86 --start results/mid_up2_32_36_s3.86.json --rounds 8 --rho 0.05"""
import argparse, json, math, subprocess, sys, os, time
import numpy as np
from analyze import load_images
from make_regions import build, certify
from geom import DEG

ap = argparse.ArgumentParser()
ap.add_argument("--s", type=float, required=True)
ap.add_argument("--theta_box", default="0-2,32-36")
ap.add_argument("--start", required=True)
ap.add_argument("--rounds", type=int, default=6)
ap.add_argument("--rho", type=float, default=0.05)
ap.add_argument("--rho_theta", type=float, default=1.0)
ap.add_argument("--all", action="store_true")
ap.add_argument("--time_limit", type=float, default=400)
ap.add_argument("--tag", default="it")
a = ap.parse_args()

regions = []
prev = a.start
log = []
for rd in range(a.rounds):
    res = json.load(open(prev))
    s, P = load_images(res, 1e-3)
    boxes, noms, ws = build(P, a.rho, a.rho_theta, only_frac=not a.all)
    k, adj, wit, sel = certify(boxes, noms)
    xR = float(sum(ws))
    print(f"[round {rd}] source={prev} tau={res['tau']:.6f} support={len(P)} boxes={len(boxes)} k={k} x*(R)={xR:.3f} "
          f"{'VIOLATED' if xR > k + 1e-9 else 'NOT violated -> stop'}", flush=True)
    if xR <= k + 1e-9:
        break
    regions.append(dict(name=f"{a.tag}_rd{rd}", k=k, sym4=False,
                        boxes=[[b[0], b[1], b[2], b[3], b[4] / DEG, b[5] / DEG] for b in boxes],
                        nominal=[list(map(float, q)) for q in noms], weights=[float(w) for w in ws], xR=xR))
    regf = f"results/{a.tag}_regions_rd{rd}.json"
    json.dump(regions, open(regf, "w"))
    out = f"results/{a.tag}_rd{rd}.json"
    cmd = [sys.executable, "lp_region.py", "--s", str(a.s), "--theta_box", a.theta_box, "--regions", regf, "--warm", prev,
           "--time_limit", str(a.time_limit), "--fine", "--out", out]
    t0 = time.time()
    with open(f"logs/{a.tag}_rd{rd}.log", "w") as lf:
        subprocess.run(cmd, stdout=lf, stderr=subprocess.STDOUT)
    r2 = json.load(open(out))
    s2, P2 = load_images(r2, 1e-3)
    # movement: for each new fractional placement, distance to nearest old placement (centre)
    old = P[:, :2]; new = P2[P2[:, 3] < 1 - 1e-6][:, :2]
    d = np.linalg.norm(new[:, None] - old[None], axis=2).min(1) if len(new) and len(old) else np.array([0.0])
    print(f"    -> tau={r2['tau']:.6f} mu={r2['mu_total']:.4f} lam={np.round(r2['regions'][-1]['lam'],4)} all_lam={[round(x['lam'],3) for x in r2['regions']]} "
          f"xR={np.round(r2['xR'],3).tolist()} conv={r2['converged']} minmass={r2['minmass']:.4f} maxcov={r2['maxcov']:.4f} "
          f"support={len(P2)} moved: max {d.max():.3f} mean {d.mean():.3f}  LP {time.time()-t0:.0f}s", flush=True)
    log.append(dict(round=rd, tau=r2["tau"], mu=r2["mu_total"], lam=[x["lam"] for x in r2["regions"]], xR=r2["xR"], k=k, xR_before=xR,
                    conv=r2["converged"], minmass=r2["minmass"], maxcov=r2["maxcov"], moved_max=float(d.max()), moved_mean=float(d.mean()),
                    lp_time=time.time() - t0, support=len(P2)))
    json.dump(log, open(f"results/{a.tag}_log.json", "w"), indent=1)
    prev = out
    if r2["tau"] < 10.95 and r2["maxcov"] < 1.001:
        print("box DEAD (tau < 10.95)"); break
