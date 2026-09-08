"""A125 probe -- the census at each (r, rho) of the grid: near pairs, possible selections per
pair, the interval leaf count, the root relaxed LP value, and the Trump canary.  Cheap (no tree),
so it says before any long run which cells are worth attacking and whether a Trump cut is needed.
"""
from __future__ import annotations
import argparse, json, math, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a125lib as G
import a116lib as A
import a119lib as L


def probe(tag, r, rho, cut=None):
    t0 = time.time()
    bodies, nv, s_sh, P = G.build_bodies125(tag, r, rho, tilt_floor_deg=cut)
    cells = {b.name: (b.t0, b.t1) for b in bodies if b.kind == "free"}
    near, far, imp = A.census(bodies, G.S_LO, G.S_HI, cells)
    nm = {i: b.name for i, b in enumerate(bodies)}
    leaves = 1
    for p in near.values():
        leaves *= len(p)
    R = L.build_krows(bodies, nv, G.S_LO, G.S_HI,
                      {pr: p[0] for pr, p in near.items() if len(p) == 1}, cells)
    v, x, y = R.solve()
    tr = A.trump_in_N(bodies, pin_slack=G.PIN_SLACK)
    return dict(tag=tag, r=r, rho=rho, cut=cut, n_bodies=len(bodies), nv=nv,
                n_near=len(near), n_far=len(far), n_impossible=len(imp),
                leaves_after_interval=leaves,
                near_pairs={"%s|%s" % (nm[i], nm[j]): len(p) for (i, j), p in sorted(near.items())},
                root_relaxed=(None if v in (math.inf, -math.inf) else v),
                root_relaxed_inf=(v == math.inf),
                trump=tr, seconds=round(time.time() - t0, 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tags", default="S33")
    ap.add_argument("--grid", default="0.2:20,0.2:10,0.2:5,0.1:20,0.1:10,0.1:5,0.05:20,0.05:10,0.05:5")
    a = ap.parse_args()
    out = []
    for tag in a.tags.split(","):
        for cell in a.grid.split(","):
            r, rho = cell.split(":")
            d = probe(tag, float(r), float(rho))
            out.append(d)
            print("%s r=%.2f rho=%4.1f: bodies %d nv %d  near %d far %d imp %d  leaves %.3g  "
                  "root %s  Trump inside %s %s  (%.1fs)"
                  % (tag, d["r"], d["rho"], d["n_bodies"], d["nv"], d["n_near"], d["n_far"],
                     d["n_impossible"], d["leaves_after_interval"],
                     "INFEAS" if d["root_relaxed_inf"] else ("%.6f" % d["root_relaxed"]),
                     d["trump"]["inside"], d["trump"]["ops"], d["seconds"]), flush=True)
    with open(os.path.join(G.RES, "probe.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)


if __name__ == "__main__":
    main()
