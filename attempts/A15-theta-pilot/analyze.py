"""Dissect the LP solution x and the theta' primal B of a run: weight by angle class and by zone."""
import json, os, sys, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def zone(cx, cy, s):
    d = min(cx, cy, s - cx, s - cy)           # distance of the centre to the nearest wall
    dc = max(abs(cx - s / 2), abs(cy - s / 2))
    near_corner = (min(cx, s - cx) < 1.1) and (min(cy, s - cy) < 1.1)
    if near_corner:
        return "corner"
    if d < 0.75:
        return "side"
    return "interior"


def summarize(P, x, s, label, top=12):
    tot = x.sum()
    print(f"--- {label}: total {tot:.4f}, support(>1e-3) {(x > 1e-3).sum()}, max {x.max():.4f}")
    th = np.degrees(P[:, 2]); th = np.minimum(th, 90 - th)   # tilt in [0,45]
    bins = [(0, 2.5), (2.5, 10), (10, 20), (20, 28), (28, 37), (37, 45.01)]
    print("  by tilt:", "  ".join(f"[{a},{b}):{x[(th >= a) & (th < b)].sum():.3f}" for a, b in bins))
    z = np.array([zone(p[0], p[1], s) for p in P])
    print("  by zone:", "  ".join(f"{k}:{x[z == k].sum():.3f}" for k in ("corner", "side", "interior")))
    order = np.argsort(-x)[:top]
    for i in order:
        print(f"   ({P[i,0]:.3f},{P[i,1]:.3f},{np.degrees(P[i,2]):.1f}deg) {z[i]:8s} {x[i]:.4f}")


def main(tag):
    R = json.load(open(os.path.join(HERE, "results", tag + ".json")))
    G = np.load(os.path.join(HERE, "results", tag + "_graph.npz"))
    P = G["P"]; s = R["s"]
    print(f"[{tag}] s={s} N={R['N']} edges={R['edges']} nu={R.get('nu')} theta={R.get('theta')} alpha={R.get('alpha')}")
    if os.path.exists(os.path.join(HERE, "results", tag + "_lp_x.npy")):
        x = np.load(os.path.join(HERE, "results", tag + "_lp_x.npy"))
        summarize(P, x, s, "LP fractional packing x")
    if os.path.exists(os.path.join(HERE, "results", tag + "_B_diag.npy")):
        d = np.load(os.path.join(HERE, "results", tag + "_B_diag.npy"))
        xs = R["theta"] * d
        summarize(P, xs, s, "theta' x = theta*diag(B)")
        Bp = os.path.join(HERE, "results", tag + "_B.npy")
        if os.path.exists(Bp):
            B = np.load(Bp).astype(float)
            # row sums / sqrt(diag): the 'theta-body' vector  x_i = (B1)_i^2 / B_ii  normalised
            r = B.sum(1)
            with np.errstate(divide='ignore', invalid='ignore'):
                v = np.where(d > 1e-9, r ** 2 / np.maximum(d, 1e-12), 0.0)
            summarize(P, v, s, "theta' v_i = (B1)_i^2 / B_ii (sums to theta' at optimum)")
            ev = np.linalg.eigvalsh(B)[::-1]
            print("  top eigenvalues of B:", np.round(ev[:12], 4), " rank(1e-3):", int((ev > 1e-3 * ev[0]).sum()))


if __name__ == "__main__":
    for t in sys.argv[1:]:
        main(t)
