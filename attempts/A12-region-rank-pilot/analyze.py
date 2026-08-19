"""A12 task 1: dissect the weight-11 fractional packing of an alive box.
  python analyze.py results/mid_up2_32_36_s3.86.json [--wmin 1e-3] [--plot]
Outputs: placement list (C4 images), conflict graph, MIS of the fractional part, rank-inequality violation search
(the finest possible (c,theta)-region-rank cut), region menu with x*(R) and realised lower bounds on k(R)."""
import argparse, json, math, sys
import numpy as np
from geom import overlap_matrix, max_independent_set, Region, realise_k, DEG, inside_container


def load_images(res, wmin=1e-4):
    s = res["s"]
    out = []
    for p in res["packing"]:
        if p["y"] < wmin:
            continue
        x, y, t = p["cx"], p["cy"], p["theta"]
        for k in range(4):
            out.append((x, y, t % (math.pi / 2), p["y"] / 4))
            x, y = s - y, x
    return s, np.array(out)


def rank_violation(adj, w, Kmax=10, verbose=True):
    """max over T of w(T) - alpha(T); lazily: for each K, max w(T) s.t. alpha(T) <= K."""
    from ortools.sat.python import cp_model
    n = len(w)
    best = (-1e9, None, None)
    for K in range(1, Kmax + 1):
        cuts = []
        for it in range(200):
            m = cp_model.CpModel()
            z = [m.NewBoolVar(f"z{i}") for i in range(n)]
            for I in cuts:
                m.Add(sum(z[i] for i in I) <= K)
            W = [int(round(v * 10**6)) for v in w]
            m.Maximize(sum(W[i] * z[i] for i in range(n)))
            sol = cp_model.CpSolver(); sol.parameters.max_time_in_seconds = 30; sol.parameters.num_workers = 4
            sol.Solve(m)
            T = [i for i in range(n) if sol.Value(z[i])]
            wT = sum(w[i] for i in T)
            if wT <= K + 1e-9:
                break
            sub = adj[np.ix_(T, T)]
            a, sel, st = max_independent_set(sub, time_limit=30)
            if a <= K:
                if verbose:
                    print(f"  K={K}: max w(T)={wT:.4f} with alpha(T)={a}  -> violation {wT-K:.4f}  |T|={len(T)}")
                if wT - K > best[0]:
                    best = (wT - K, K, T)
                break
            # find an independent set of size K+1 inside T (take any K+1 of the MIS found)
            cuts.append([T[i] for i in sel[:K + 1]])
        else:
            print(f"  K={K}: lazy loop did not terminate")
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("result")
    ap.add_argument("--wmin", type=float, default=1e-3)
    ap.add_argument("--plot", action="store_true")
    ap.add_argument("--regions", action="store_true")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    res = json.load(open(a.result))
    s, P = load_images(res, a.wmin)
    print(f"s={s} tau={res['tau']:.6f} nu={res['nu']:.6f} images={len(P)} total weight={P[:,3].sum():.4f}")
    order = np.argsort(-P[:, 3])
    frac = P[:, 3] < 1 - 1e-6
    print("placements (cx, cy, theta[deg], w):")
    for i in order:
        print(f"  {P[i,0]:.4f} {P[i,1]:.4f} {P[i,2]/DEG:7.3f} {P[i,3]:.4f}")
    adj = overlap_matrix(P[:, :3], tol=1e-9)
    # coverage sanity: heaviest overlapping pair
    W = P[:, 3]
    pair = np.max(np.where(adj, W[:, None] + W[None, :], 0))
    print(f"heaviest overlapping pair weight sum: {pair:.4f}; edges={int(adj.sum()//2)}")
    # MIS of the whole support and of the fractional part
    aS, selS, st = max_independent_set(adj)
    print(f"alpha(support) = {aS} vs sum x = {W.sum():.4f}   ({st})")
    idx = np.nonzero(frac)[0]
    aF, selF, st = max_independent_set(adj[np.ix_(idx, idx)])
    print(f"fractional part: |S|={len(idx)} sum x_S = {W[idx].sum():.4f}  alpha(S) = {aF}  ({st})")
    print("  MIS of S:", [(round(P[idx[i],0],3), round(P[idx[i],1],3), round(P[idx[i],2]/DEG,1)) for i in selF])
    print("rank-inequality violation search (finest (c,theta)-region cut):")
    viol, K, T = rank_violation(adj, W)
    if T is not None:
        print(f"  MAX violation {viol:.4f} at K={K}, T = ")
        for i in T:
            print(f"    {P[i,0]:.4f} {P[i,1]:.4f} {P[i,2]/DEG:7.3f} {P[i,3]:.4f}")
    out = dict(s=s, images=P.tolist(), alpha_support=aS, alpha_frac=aF, sum_frac=float(W[idx].sum()),
               rank_violation=dict(viol=viol, K=K, T=[P[i].tolist() for i in (T or [])]))
    if a.regions:
        c = s / 2
        menu = []
        for r in (0.6, 0.7, 0.85, 0.9, 1.0):
            menu.append(Region([("disc", c, c, r)], f"disc r={r}"))
        menu.append(Region([("annulus", c, c, 0.65, 0.95)], "annulus 0.65-0.95"))
        # side zone (left) : centres near the left wall, away from corners; C4 -> all four sides
        side = Region([("rect", 0.5, 0.75, 1.2, s - 1.2)], "side-left")
        menu.append(side); menu.append(side.sym4(s))
        corner = Region([("rect", s - 1.0, s - 0.5, s - 1.0, s - 0.5)], "corner-TR")
        menu.append(corner.sym4(s))
        menu.append(corner.sym4(s).union(Region([("disc", c, c, 0.85)], "disc0.85"), "corners+disc0.85"))
        menu.append(side.sym4(s).union(Region([("disc", c, c, 0.85)], "disc0.85"), "sides+disc0.85"))
        # tilted family blobs: discs of radius 0.12 around each tilted image centre with theta > 20 deg
        tilt = P[P[:, 2] > 20 * DEG]
        blobs = Region([("disc", x, y, 0.12) for x, y in tilt[:, :2]], "tilt-blobs r=.12")
        menu.append(blobs)
        menu.append(blobs.union(Region([("disc", c, c, 0.85)], "disc0.85"), "blobs+disc0.85"))
        # everything except one side zone
        allbut = Region([("rect", 0, s, 0, s)], "all")
        thetas = sorted(set([0.0, 1.0, 2.0] + [32.0, 33.0, 34.0, 35.0, 36.0]))
        rows = []
        for R in menu:
            inR = R.contains_many(P[:, 0], P[:, 1])
            xR = float(W[inR].sum())
            k_lb, pl, st, ncand = realise_k(R, s, thetas, step=0.1, time_limit=60)
            flag = "VIOLATED?" if xR > k_lb + 1e-6 else "not violated (k>=x)"
            print(f"  R={R.name:28s} x*(R)={xR:.4f}  k_lb(realised, {ncand} cands, {st})={k_lb}  {flag}")
            rows.append(dict(name=R.name, xR=xR, k_lb=k_lb, status=st, prims=R.prims, realisation=pl))
        out["regions"] = rows
    if a.plot:
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.patches import Polygon
        from geom import corners
        fig, ax = plt.subplots(figsize=(7, 7))
        ax.add_patch(plt.Rectangle((0, 0), s, s, fill=False, lw=2))
        cmap = {1.0: "k", 0.5: "tab:blue", 0.25: "tab:red"}
        for (x, y, t, w) in P:
            col = "tab:green" if t > 20 * DEG else ("k" if w > 0.99 else ("tab:blue" if w > 0.49 else "tab:red"))
            ax.add_patch(Polygon(corners(x, y, t), closed=True, fill=True, alpha=min(1, 0.15 + 0.5 * w), fc=col, ec=col, lw=0.5))
            ax.plot(x, y, "o", ms=3 + 8 * w, color=col)
            ax.text(x, y, f"{w:.2f}", fontsize=6)
        ax.set_aspect("equal"); ax.set_xlim(-0.1, s + 0.1); ax.set_ylim(-0.1, s + 0.1)
        ax.set_title(f"box {res['theta_box']} s={s} tau={res['tau']:.4f}: fractional packing (green=tilted, black=1, blue=1/2, red=1/4)")
        fn = a.result.replace("results", "plots").replace(".json", ".png")
        plt.savefig(fn, dpi=130); print("plot ->", fn)
    if a.out:
        json.dump(out, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
