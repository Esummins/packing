"""Hole characterisation: for a point set P and side s0, describe the uncovered part of (c,theta)-space.

usage: python holes.py best.jsonl OUT_PREFIX [--s0 3.79 3.80 3.82] [--reopt]
  For each target s0: (optionally) re-optimise the point set at that s0 (SLP, warm start from the record),
  then compute on a fine grid the set {(c,theta): d>0}, its volume fraction, its connected components
  (bounding boxes, max d, wall-adjacency) and write JSON + PNG.
"""
import sys, os, json, argparse
import numpy as np
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from unavoid import *
from unavoid import _transfer
from plot_set import plot


def hole_analysis(P, s0, nth=181, nc=301):
    th, uu, D = uncov_grid(P, s0, nth, nc)   # D[ith, iu, iv], c = w/2 + (s0-w)*(u,v)
    unc = D > 0
    # volume fraction: per theta the domain area is (s0-w)^2; weight accordingly
    w = np.cos(th) + np.sin(th)
    area = (s0 - w) ** 2
    frac_per_theta = unc.mean(axis=(1, 2))
    vol_frac = float((frac_per_theta * area).sum() / area.sum())
    # fraction of theta values that have any hole
    theta_frac = float(unc.any(axis=(1, 2)).mean())
    # connected components in the 3-D grid (theta periodic: identify 0 and pi/2 by wrapping)
    lab, ncomp = ndimage.label(unc)
    comps = []
    for k in range(1, ncomp + 1):
        m = lab == k
        idx = np.argwhere(m)
        dmax = float(D[m].max())
        imax = idx[np.argmax(D[m])]
        it, iu, iv = imax
        wt = w[it]
        cx = wt / 2 + (s0 - wt) * uu[iu]; cy = wt / 2 + (s0 - wt) * uu[iv]
        ths = th[idx[:, 0]]; us = uu[idx[:, 1]]; vs = uu[idx[:, 2]]
        wall = bool((us.min() <= 1e-9) or (us.max() >= 1 - 1e-9) or (vs.min() <= 1e-9) or (vs.max() >= 1 - 1e-9))
        comps.append(dict(max_d=dmax, worst=dict(cx=float(cx), cy=float(cy), theta_deg=float(np.degrees(th[it]))),
                          theta_deg_range=[float(np.degrees(ths.min())), float(np.degrees(ths.max()))],
                          u_range=[float(us.min()), float(us.max())], v_range=[float(vs.min()), float(vs.max())],
                          touches_wall=wall, ncells=int(m.sum()),
                          vol_frac=float((m.sum(axis=(1, 2)) * area).sum() / (nc * nc * area.sum()))))
    comps.sort(key=lambda c: -c["max_d"])
    return dict(s0=float(s0), max_d=float(D.max()), vol_frac_uncovered=vol_frac, theta_frac_with_hole=theta_frac,
                n_components=ncomp, components=comps, grid=dict(nth=nth, nc=nc))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("inp"); ap.add_argument("prefix")
    ap.add_argument("--s0", type=float, nargs="+", default=[3.79, 3.80, 3.82])
    ap.add_argument("--reopt", action="store_true")
    ap.add_argument("--index", type=int, default=0)
    a = ap.parse_args()
    recs = [json.loads(l) for l in open(a.inp)]
    recs.sort(key=lambda r: -r["s0"])
    r = recs[a.index]
    grp, spec = r["group"], r["spec"]
    p0 = Param(grp, spec, r["s0"]); z = np.array(r["z"])
    out = []
    for s0 in a.s0:
        pm = Param(grp, spec, s0)
        zz = _transfer(p0, z, pm)
        if a.reopt:
            zz, g, _, _ = slp(pm, zz, s0, iters=250, nth=90, nc=100, K=40)
        P = pm.P(zz)
        H = hole_analysis(P, s0)
        H["P"] = P.tolist(); H["family"] = f"{grp} {''.join(spec)}"; H["reoptimised"] = a.reopt
        wc = worst_configs(P, s0, nth=180, nc=200, K=30, polish=8)
        H["worst"] = [[float(x) for x in w] for w in wc[:12]]
        plot(P, s0, f"{a.prefix}_s{s0:.3f}.png", title=f"{grp} {''.join(spec)} at s0={s0}: max d={H['max_d']:+.4f}, uncovered vol frac={H['vol_frac_uncovered']:.2e}", worst=wc)
        print(f"s0={s0}: max d={H['max_d']:+.5f} uncovered vol frac={H['vol_frac_uncovered']:.3e} theta-frac={H['theta_frac_with_hole']:.3f} comps={H['n_components']}")
        for c in H["components"][:8]:
            print("   comp: max_d=%.4f at c=(%.3f,%.3f) th=%.1f deg; theta range %s; wall=%s; vol=%.2e" % (
                c["max_d"], c["worst"]["cx"], c["worst"]["cy"], c["worst"]["theta_deg"], c["theta_deg_range"], c["touches_wall"], c["vol_frac"]))
        out.append(H)
    json.dump(out, open(f"{a.prefix}.json", "w"), indent=1)
