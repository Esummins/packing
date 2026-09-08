"""A125 -- the sampling confirmation of a certified N, vectorised.

A116's `sample_check` is a Python loop (~10^4 draws/s); with |L| = 5 free boxes the fraction of
draws whose free block is pairwise disjoint is 3e-4 .. 4e-3, so reaching 10^4 TESTED samples needs
10^6 .. 3x10^7 draws.  This is the same test, done with numpy over whole batches:

  drawn   uniform poses in N: centre uniform in each free box, tilt uniform in its interval,
          pin offset uniform in its delta-core;
  tested  the draws whose FREE block is pairwise interior-disjoint (max over the eight signed
          selections >= -1e-9 for every free pair) -- these are carried to 30 sides in
          [s_lo, s0] and fully tested: all |L|+|P| pairwise selections and all wall rows;
  hits    a draw that IS a packing of L u P at some side <= s0.  Any hit is a counterexample to
          "N is dead".

`--xcheck` re-runs A116's own scalar sampler on the same seeds and compares the counts.

Read-only on A116/A119/A122; writes results/sampling.json (merged, resumable).
"""
from __future__ import annotations
import argparse, json, math, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a125lib as G
import a116lib as A
import numpy as np

SELS = A.SELS


def _axis(t, k):
    return (np.cos(t), np.sin(t)) if k == 0 else (-np.sin(t), np.cos(t))


def _w(d):
    return np.abs(np.cos(d)) + np.abs(np.sin(d))


def pair_gap(xa, ya, ta, xb, yb, tb):
    """max over the eight signed selections of the pair gap (a116lib.sat_gap), vectorised."""
    best = None
    for (o, k, e) in SELS:
        if o == 0:
            xw, yw, tw, xo, yo, to = xa, ya, ta, xb, yb, tb
        else:
            xw, yw, tw, xo, yo, to = xb, yb, tb, xa, ya, ta
        ax, ay = _axis(tw, k)
        g = e * ((xo - xw) * ax + (yo - yw) * ay) - 0.5 - 0.5 * _w(tw - to)
        best = g if best is None else np.maximum(best, g)
    return best


def batch(bodies, n, rng, s_lo, s_hi, n_side, tol=-1e-9):
    free = [b for b in bodies if b.kind == "free"]
    pins = [b for b in bodies if b.kind == "pin"]
    nf, npn = len(free), len(pins)
    X = np.empty((nf, n)); Y = np.empty((nf, n)); T = np.empty((nf, n))
    for i, b in enumerate(free):
        X[i] = rng.uniform(b.x0, b.x1, n)
        Y[i] = rng.uniform(b.y0, b.y1, n)
        T[i] = rng.uniform(b.t0, b.t1, n)
    U = np.empty((npn, n)); V = np.empty((npn, n))
    for i, b in enumerate(pins):
        U[i] = rng.uniform(-b.hh, b.hh, n)
        V[i] = rng.uniform(-b.hh, b.hh, n)
    # -- the free block (side-independent)
    ok = np.ones(n, dtype=bool)
    worst = -np.inf
    for i in range(nf):
        for j in range(i + 1, nf):
            g = pair_gap(X[i], Y[i], T[i], X[j], Y[j], T[j])
            bad = g < tol
            if bad.any():
                worst = max(worst, float(g[bad].max()))
            ok &= ~bad
    idx = np.nonzero(ok)[0]
    tested = int(idx.size)
    if tested == 0:
        return dict(drawn=n, tested=0, hits=0, worst=worst, examples=[])
    x, y, t = X[:, idx], Y[:, idx], T[:, idx]
    u, v = U[:, idx], V[:, idx]
    hf = 0.5 * _w(t)                                   # half-width of each free square
    hits_any = np.zeros(tested, dtype=bool)
    ex = []
    for s in np.linspace(s_lo, s_hi, n_side):
        good = np.ones(tested, dtype=bool)
        good &= ((x - hf) >= tol).all(axis=0) & ((s - x - hf) >= tol).all(axis=0)
        good &= ((y - hf) >= tol).all(axis=0) & ((s - y - hf) >= tol).all(axis=0)
        if not good.any():
            continue
        px = np.empty((npn, tested)); py = np.empty((npn, tested))
        for i, b in enumerate(pins):
            px[i] = b.ax[0] + b.ax[1] * s + u[i]
            py[i] = b.ay[0] + b.ay[1] * s + v[i]
        good &= ((px - 0.5) >= tol).all(axis=0) & ((s - px - 0.5) >= tol).all(axis=0)
        good &= ((py - 0.5) >= tol).all(axis=0) & ((s - py - 0.5) >= tol).all(axis=0)
        if not good.any():
            continue
        zero = np.zeros(tested)
        for i in range(nf):
            for j in range(npn):
                good &= pair_gap(x[i], y[i], t[i], px[j], py[j], zero) >= tol
            if not good.any():
                break
        if not good.any():
            continue
        for i in range(npn):
            for j in range(i + 1, npn):
                good &= pair_gap(px[i], py[i], zero, px[j], py[j], zero) >= tol
        if good.any():
            for q in np.nonzero(good)[0][:3]:
                ex.append(dict(side=float(s),
                               free={b.name: [float(x[i, q]), float(y[i, q]),
                                              math.degrees(float(t[i, q]))]
                                     for i, b in enumerate(free)},
                               pins={b.name: [float(px[i, q]), float(py[i, q])]
                                     for i, b in enumerate(pins)}))
            hits_any |= good
    return dict(drawn=n, tested=tested, hits=int(hits_any.sum()),
                worst=(None if worst == -np.inf else worst), examples=ex[:3])


def run(bodies, tested_target, seed, batch_size=200000, draw_cap=400000000, n_side=30,
        s_lo=None, s_hi=None, log=print):
    s_lo = G.S_LO if s_lo is None else s_lo
    s_hi = G.S0 if s_hi is None else s_hi
    rng = np.random.default_rng(seed)
    drawn = tested = hits = 0
    worst = None
    ex = []
    t0 = time.time()
    while tested < tested_target and drawn < draw_cap:
        b = batch(bodies, batch_size, rng, s_lo, s_hi, n_side)
        drawn += b["drawn"]; tested += b["tested"]; hits += b["hits"]
        ex += b["examples"]
        if b["worst"] is not None:
            worst = b["worst"] if worst is None else max(worst, b["worst"])
        log("      drawn %-11d tested %-8d hits %-4d  (%.0f s, %.0f k draws/s)"
            % (drawn, tested, hits, time.time() - t0, drawn / 1000.0 / max(1e-9, time.time() - t0)))
    return dict(drawn=drawn, tested=tested, hits=hits, sides_tested=n_side,
                side_range=[s_lo, s_hi], worst_free_overlap_of_rejects=worst,
                examples=ex[:3], seconds=round(time.time() - t0, 1),
                vectorised=True, tested_target=tested_target)


def xcheck(bodies, nv, n=20000, seed=11):
    """A116's scalar sampler vs this one on the same population size (counts, not seeds)."""
    a = A.sample_check(bodies, nv, n_samples=n, seed=seed, s_lo=G.S_LO, s_hi=G.S0, n_side=30)
    rng = np.random.default_rng(seed)
    b = batch(bodies, n, rng, G.S_LO, G.S0, 30)
    return dict(scalar=dict(drawn=a["n_samples"], tested=a["free_pairs_disjoint"], hits=a["hits"]),
                vector=dict(drawn=b["drawn"], tested=b["tested"], hits=b["hits"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("targets", nargs="+", help="tag:r:rho[:cut]")
    ap.add_argument("--tested", type=int, default=10000)
    ap.add_argument("--batch", type=int, default=200000)
    ap.add_argument("--xcheck", action="store_true")
    a = ap.parse_args()
    logp = os.path.join(G.LOGS, "sampling.log")

    def log(*x):
        s = " ".join(str(v) for v in x)
        print(s, flush=True)
        with open(logp, "a", encoding="utf-8") as f:
            f.write(time.strftime("[%H:%M:%S] ") + s + "\n")

    p = os.path.join(G.RES, "sampling.json")
    out = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
    for spec in a.targets:
        parts = spec.split(":")
        tag, r, rho = parts[0], float(parts[1]), float(parts[2])
        cut = float(parts[3]) if len(parts) > 3 and parts[3] not in ("", "None") else None
        cid = "%s_%s_r%.2f_rho%g" % (tag, G.SHADOWS[tag]["cls"], r, rho)
        bodies, nv, s_sh, P = G.build_bodies125(tag, r, rho, anchor_side=G.S0,
                                                pin_slack=G.PIN_SLACK, tilt_floor_deg=cut)
        log("%s  (L = %s)" % (cid, [b.name for b in bodies if b.kind == "free"]))
        rec = dict(id=cid, tag=tag, r=r, rho=rho, cut=cut)
        if a.xcheck:
            rec["xcheck"] = xcheck(bodies, nv)
            log("      xcheck scalar %s  vector %s" % (rec["xcheck"]["scalar"], rec["xcheck"]["vector"]))
        rec.update(run(bodies, a.tested, seed=int(1000 * r + rho), batch_size=a.batch, log=log))
        out[cid] = rec
        with open(p, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1)
        log("%-26s drawn %d -> tested %d -> hits %d   (%.0f s)"
            % (cid, rec["drawn"], rec["tested"], rec["hits"], rec["seconds"]))


if __name__ == "__main__":
    main()
