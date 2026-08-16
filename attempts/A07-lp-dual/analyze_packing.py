"""Expand the D4-symmetric fractional packing (dual solution) into all images and measure its true
maximum coverage on a fine grid; report the rigorous-ish scaled packing value nu/maxcov."""
import json, math, sys
import numpy as np


def d4_images(cx, cy, th, s):
    """8 images (cx,cy,theta) of a placement under D4 of the container [0,s]^2"""
    out = []
    # rotations by k*90 deg about centre: (x,y)->(s-y,x); theta->theta
    x, y, t = cx, cy, th
    for k in range(4):
        out.append((x, y, t))
        out.append((s - x, y, (math.pi / 2 - t) % (math.pi / 2)))  # reflection x->s-x : theta -> -theta = pi/2 - theta mod pi/2
        x, y = s - y, x
    return out


def coverage(placements, s, pts):
    cov = np.zeros(len(pts))
    for (cx, cy, th, wt) in placements:
        c, sn = math.cos(th), math.sin(th)
        dx = pts[:, 0] - cx; dy = pts[:, 1] - cy
        ux = dx * c + dy * sn; uy = -dx * sn + dy * c
        cov += wt * ((np.abs(ux) <= 0.5) & (np.abs(uy) <= 0.5))
    return cov


def expand(res):
    s = res["s"]
    pl = []
    for p in res["packing"]:
        imgs = d4_images(p["cx"], p["cy"], p["theta"], s)
        # weight per image = y / 8  (orbit of size <8 -> images coincide, weights add up correctly)
        for (x, y, t) in imgs:
            pl.append((x, y, t, p["y"] / 8))
    return pl


if __name__ == "__main__":
    res = json.load(open(sys.argv[1]))
    s = res["s"]
    pl = expand(res)
    print(f"s={s} tau={res['tau']:.6f} nu={res['nu']:.6f}  images={len(pl)}")
    # fine grid check
    for hh in [0.05, 0.02, 0.005]:
        xs = np.arange(0, s + 1e-9, hh)
        X, Y = np.meshgrid(xs, xs, indexing="ij")
        pts = np.stack([X.ravel(), Y.ravel()], axis=1)
        cov = coverage(pl, s, pts)
        print(f"  grid {hh}: max coverage {cov.max():.4f}, mean {cov.mean():.4f}, frac>1: {(cov>1+1e-9).mean():.4f}")
    rng = np.random.default_rng(0)
    pts = rng.uniform(0, s, size=(400000, 2))
    cov = coverage(pl, s, pts)
    print(f"  random 4e5: max coverage {cov.max():.4f}; scaled packing value nu/maxcov = {res['nu']/cov.max():.4f}")
    # coverage histogram
    vals, cnts = np.unique(np.round(cov, 4), return_counts=True)
    print("  coverage value distribution (random pts):", [(float(v), int(c)) for v, c in zip(vals, cnts)][-12:])
