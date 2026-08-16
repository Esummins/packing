"""Multi-start optimisation of k-point unavoidable sets.

usage:  python run_opt.py phaseA --npts 10 --s0 3.70 --starts 200 --out resA10.jsonl
        python run_opt.py phaseB --npts 10 --inp resA10.jsonl --top 6 --margin 0.0 --out resB10.jsonl
"""
import sys, os, json, time, argparse
import numpy as np
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unavoid import *

FAMILIES = {
    10: [("none", ["g"] * 10), ("C2", ["g"] * 5), ("axes", ["g", "g", "v"]), ("axes", ["g", "v", "v", "h"]),
         ("axes", ["g", "v", "v", "v"]), ("axes", ["v", "v", "v", "h", "h"]), ("diag", ["g", "g", "d"]),
         ("diag", ["g", "d", "d", "a"]), ("diag", ["g", "d", "d", "d"])],
    9: [("none", ["g"] * 9), ("C2", ["g"] * 4 + ["c"]), ("axes", ["g", "g", "c"]), ("axes", ["g", "v", "h", "c"]),
        ("axes", ["g", "v", "v", "c"]), ("D4", ["g", "c"]), ("D4", ["x", "d", "c"]), ("diag", ["g", "g", "c"]),
        ("diag", ["g", "d", "a", "c"])],
    11: [("none", ["g"] * 11), ("C2", ["g"] * 5 + ["c"]), ("axes", ["g", "g", "v", "c"]), ("axes", ["g", "v", "v", "h", "c"]),
         ("diag", ["g", "g", "d", "c"]), ("diag", ["g", "d", "d", "a", "c"])],
    4: [("none", ["g"] * 4), ("D4", ["d"]), ("axes", ["g"])],
}


def one_start(args):
    grp, spec, s0, seed, n_kicks = args
    rng = np.random.default_rng(seed)
    param = Param(grp, spec, s0)
    z0 = param.random_z(rng)
    kw = dict(iters=150, nth=48, nc=60, K=30)
    t0 = time.time()
    for attempt in range(3):
        try:
            z, g = basin_hop(param, z0, s0, rng=rng, n_kicks=n_kicks, slp_kw=kw)
            break
        except MemoryError:
            time.sleep(5)
    else:
        return dict(group=grp, spec=spec, s0=s0, seed=seed, g=9.0, g_fine=9.0, z=[], P=[], time=0.0)
    P = param.P(z)
    # accurate re-evaluation
    g_fine = worst_configs(P, s0, nth=120, nc=120, K=10, polish=3)[0][3]
    return dict(group=grp, spec=spec, s0=s0, seed=seed, g=float(g), g_fine=float(g_fine),
                z=z.tolist(), P=P.tolist(), time=time.time() - t0)


def phaseA(a):
    fams = FAMILIES[a.npts]
    if a.family:
        fams = [f for f in fams if f[0] == a.family]
    jobs = []
    for i in range(a.starts):
        grp, spec = fams[i % len(fams)]
        jobs.append((grp, spec, a.s0, a.seed + i, a.kicks))
    with Pool(a.procs) as pool, open(a.out, "a") as f:
        for r in pool.imap_unordered(one_start, jobs):
            f.write(json.dumps(r) + "\n"); f.flush()
            print(f"{r['group']:5s} {''.join(r['spec']):12s} seed={r['seed']} g={r['g']:.5f} g_fine={r['g_fine']:.5f} t={r['time']:.0f}s", flush=True)


def one_cont(args):
    rec, margin, tol_s, as_family, jitter, seed = args
    grp, spec = rec["group"], rec["spec"]
    param = Param(grp, spec, rec["s0"])
    z = np.array(rec["z"])
    if as_family is not None:
        # re-parametrise into a less symmetric family (none / C2), optionally jittered
        P0 = param.P(z)
        if jitter > 0:
            P0 = P0 + np.random.default_rng(seed).normal(0, jitter, P0.shape)
        if as_family == "none":
            grp, spec = "none", ["g"] * len(P0)
        elif as_family == "C2":
            grp, spec = "C2", ["g"] * (len(P0) // 2) + (["c"] if len(P0) % 2 else [])
        param = Param(grp, spec, rec["s0"])
        z = param.z_from_P(P0)
    kw = dict(iters=250, nth=90, nc=100, K=40)
    t0 = time.time()
    s_best, z_best, g_best, p_best = find_max_s0(grp, spec, z, rec["s0"], m_target=margin, tol_s=tol_s, slp_kw=kw)
    P = p_best.P(z_best)
    wc = worst_configs(P, s_best, nth=180, nc=200, K=20, polish=8)
    return dict(group=grp, spec=spec, margin=margin, s0=float(s_best), g=float(g_best), g_fine=float(wc[0][3]),
                z=z_best.tolist(), P=P.tolist(), worst=[[float(x) for x in w] for w in wc[:12]],
                seed=rec.get("seed"), time=time.time() - t0)


def phaseB(a):
    recs = [json.loads(l) for l in open(a.inp)]
    recs.sort(key=lambda r: r["g_fine"])
    # distinct by family, top overall
    chosen = recs[: a.top]
    jobs = [(r, a.margin, a.tol_s, a.as_family, a.jitter, 1000 + i) for i, r in enumerate(chosen)]
    with Pool(a.procs) as pool, open(a.out, "a") as f:
        for r in pool.imap_unordered(one_cont, jobs):
            f.write(json.dumps(r) + "\n"); f.flush()
            print(f"{r['group']:5s} {''.join(r['spec']):12s} margin={r['margin']} s0={r['s0']:.6f} g={r['g']:.6f} g_fine={r['g_fine']:.6f} t={r['time']:.0f}s", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("phase")
    ap.add_argument("--npts", type=int, default=10)
    ap.add_argument("--s0", type=float, default=3.70)
    ap.add_argument("--starts", type=int, default=100)
    ap.add_argument("--kicks", type=int, default=15)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--procs", type=int, default=4)
    ap.add_argument("--family", type=str, default=None)
    ap.add_argument("--out", type=str, required=True)
    ap.add_argument("--inp", type=str, default=None)
    ap.add_argument("--top", type=int, default=6)
    ap.add_argument("--margin", type=float, default=0.0)
    ap.add_argument("--tol_s", type=float, default=2e-5)
    ap.add_argument("--as_family", type=str, default=None)
    ap.add_argument("--jitter", type=float, default=0.0)
    a = ap.parse_args()
    if a.phase == "phaseA":
        phaseA(a)
    else:
        phaseB(a)
