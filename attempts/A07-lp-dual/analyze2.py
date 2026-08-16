"""Structure of a v2 LP solution: atoms (mu), fractional packing (dual), coverage map, pinwheel check.
usage: python analyze2.py results/v2_s3.80_rowonly.json [plots/prefix]"""
import json, math, sys, itertools
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from lp_measure2 import d4_point_images, d4_placement_images, EPS_GEO
from shapely.geometry import Polygon


def square_poly(cx, cy, th, half=0.5):
    c, s = math.cos(th), math.sin(th)
    corn = np.array([[-half, -half], [half, -half], [half, half], [-half, half]])
    R = np.array([[c, -s], [s, c]])
    return Polygon(corn @ R.T + [cx, cy])


def main(path, prefix):
    res = json.load(open(path)); s = res["s"]
    atoms = [(a["rep"][0], a["rep"][1], a["w"], a["m"]) for a in res["atoms"]]
    print(f"s={s} tau={res['tau']:.6f} nu={res['nu']:.6f} orbits={len(atoms)} packing rows={len(res['packing'])}")
    # atoms
    P, W = [], []
    for (x, y, w, m) in atoms:
        for p in set(d4_point_images(x, y, s)):
            P.append(p); W.append(w)
    P = np.array(P); W = np.array(W)
    print(f"atoms: {len(P)} points, total {W.sum():.6f}, max weight {W.max():.4f}")
    big = sorted(atoms, key=lambda a: -a[2] * a[3])[:15]
    print("heaviest orbits (rep x,y | weight per point | orbit size | orbit mass):")
    for (x, y, w, m) in big:
        print(f"   ({x:.4f},{y:.4f})  w={w:.4f}  m={m}  mass={w*m:.4f}")
    # mass by region
    d_edge = np.minimum.reduce([P[:, 0], P[:, 1], s - P[:, 0], s - P[:, 1]])
    for lo, hi in [(0, 0.9), (0.9, 1.1), (1.1, 1.5), (1.5, 1.9), (1.9, 2.0)]:
        m = (d_edge >= lo) & (d_edge < hi)
        print(f"   mass with distance-to-boundary in [{lo},{hi}): {W[m].sum():.4f}")
    # packing
    pl = []
    for p in res["packing"]:
        for (a, b, t) in d4_placement_images(p["cx"], p["cy"], p["theta"], s):
            pl.append((a, b, t, p["y"] / 8))
    print(f"packing: {len(pl)} images, total weight {sum(q[3] for q in pl):.6f}")
    top = sorted(res["packing"], key=lambda p: -p["y"])[:15]
    print("heaviest placement orbits (cx,cy,theta_deg | orbit weight y):")
    for p in top:
        print(f"   ({p['cx']:.4f},{p['cy']:.4f},{math.degrees(p['theta']):.2f}deg) y={p['y']:.4f}")
    # angle histogram of packing weight
    ang = np.array([math.degrees(p["theta"]) for p in res["packing"]]); yy = np.array([p["y"] for p in res["packing"]])
    for lo in range(0, 45, 5):
        m = (ang >= lo) & (ang < lo + 5)
        print(f"   theta in [{lo},{lo+5}): weight {yy[m].sum():.4f}")
    # pinwheels: triples of pairwise-overlapping squares (positive area) with empty triple intersection
    polys = [square_poly(a, b, t) for (a, b, t, w) in pl if w > 1e-6]
    wts = [w for (a, b, t, w) in pl if w > 1e-6]
    n = len(polys)
    inter = {}
    for i in range(n):
        for j in range(i + 1, n):
            if polys[i].distance(polys[j]) == 0:
                I = polys[i].intersection(polys[j])
                if I.area > 1e-9:
                    inter[(i, j)] = I
    pin = 0; pin_w = 0.0; examples = []
    for (i, j), I in inter.items():
        for k in range(j + 1, n):
            if (i, k) in inter and (j, k) in inter:
                if I.intersection(polys[k]).area < 1e-9:
                    pin += 1; pin_w += min(wts[i], wts[j], wts[k])
                    if len(examples) < 5:
                        examples.append((i, j, k))
    print(f"pinwheels (3-cliques of pairwise-overlapping squares with empty common intersection): {pin}; "
          f"pairs overlapping: {len(inter)}")
    for (i, j, k) in examples:
        print("   e.g.", [(round(pl[q][0], 3), round(pl[q][1], 3), round(math.degrees(pl[q][2]), 1), round(pl[q][3], 4)) for q in (i, j, k)])
    # plots
    fig, ax = plt.subplots(1, 3, figsize=(20, 6.5))
    ax[0].scatter(P[:, 0], P[:, 1], s=2000 * W, c="k", alpha=0.7)
    ax[0].set_xlim(0, s); ax[0].set_ylim(0, s); ax[0].set_aspect("equal"); ax[0].set_title(f"optimal mu, s={s}, total={W.sum():.4f}")
    for k in range(1, 4):
        ax[0].axhline(k, color="gray", lw=0.3); ax[0].axvline(k, color="gray", lw=0.3)
    for (a, b, t, w) in pl:
        pol = square_poly(a, b, t); xs, ys = pol.exterior.xy
        ax[1].plot(xs, ys, "-", lw=0.3 + 8 * w, alpha=0.5)
    ax[1].set_xlim(0, s); ax[1].set_ylim(0, s); ax[1].set_aspect("equal"); ax[1].set_title(f"fractional packing, weight {sum(q[3] for q in pl):.4f}")
    hh = 0.01; xs = np.arange(0, s + 1e-9, hh); X, Y = np.meshgrid(xs, xs, indexing="ij")
    pts = np.stack([X.ravel(), Y.ravel()], 1); cov = np.zeros(len(pts))
    for (a, b, t, w) in pl:
        c, sn = math.cos(t), math.sin(t); dx = pts[:, 0] - a; dy = pts[:, 1] - b
        ux = dx * c + dy * sn; uy = -dx * sn + dy * c
        cov += w * ((np.abs(ux) <= 0.5) & (np.abs(uy) <= 0.5))
    im = ax[2].imshow(cov.reshape(X.shape).T, origin="lower", extent=[0, s, 0, s], vmin=0, vmax=max(1.0, cov.max()))
    plt.colorbar(im, ax=ax[2]); ax[2].set_title(f"coverage of packing (max {cov.max():.3f})")
    plt.tight_layout(); plt.savefig(prefix + "_structure.png", dpi=110)
    print("max coverage of expanded packing on 0.01 grid:", cov.max())


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "plots/" + sys.argv[1].split("/")[-1].replace(".json", ""))
