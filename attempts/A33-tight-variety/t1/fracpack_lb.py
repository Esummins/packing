"""
Fractional-packing (dual) LOWER bound on tau*(s) from a saved fracpack_<S>.json.

    nu*(s) = max int dy(Q)  s.t.  int 1[p in Q] dy(Q) <= 1 for every p in [0,s]^2,
    nu*(s) <= tau*(s)   (weak duality),  so ANY feasible fractional packing lower-bounds tau*.

The y that comes straight out of the covering LP is only constrained at that LP's atom points, so it
over-covers elsewhere and its raw weight sum is not a bound.  Here the weights on the same placement
support are re-optimised with row generation over the coverage constraint until the coverage oracle
finds no point with coverage > 1 + 1e-6.

Symmetry: fracpack_<S>.json lists the placements as consecutive blocks of 8 D4 images of one LP row,
so tying each block to a single variable keeps the packing D4-symmetric; then the coverage function
is D4-invariant and it suffices to impose the constraint on one eighth of the container
(s/2 <= x <= y <= s).  Membership uses CLOSED squares slightly ENLARGED (half = 0.5 + 1e-9), which
only makes the constraint harder, so the bound errs on the safe side.

  python fracpack_lb.py results/fracpack_3.84.json
"""
import argparse, json, math, os, time
import numpy as np
import highspy

HERE = os.path.dirname(os.path.abspath(__file__))
HALF = 0.5 + 1e-9


class Pack:
    def __init__(self, placements, s, block=8):
        P = np.array(placements, dtype=float)
        self.s = s
        self.pl = P[:, :3]
        self.cs, self.sn = np.cos(P[:, 2]), np.sin(P[:, 2])
        self.R = len(P)
        self.grp = np.arange(self.R) // block
        self.K = int(self.grp.max()) + 1
        self.cost = np.bincount(self.grp, minlength=self.K).astype(float)   # weight per unit z

    def counts(self, pts, half=HALF):
        """(m, K) matrix of how many placements of each orbit contain each point"""
        out = np.zeros((len(pts), self.K))
        chunk = max(1, int(4e6 // max(self.R, 1)))
        for a in range(0, len(pts), chunk):
            p = pts[a:a + chunk]
            dx = p[:, None, 0] - self.pl[None, :, 0]
            dy = p[:, None, 1] - self.pl[None, :, 1]
            u = dx * self.cs[None, :] + dy * self.sn[None, :]
            v = -dx * self.sn[None, :] + dy * self.cs[None, :]
            ins = ((np.abs(u) <= half) & (np.abs(v) <= half)).astype(float)
            for k in range(self.K):
                pass
            # accumulate per orbit
            blk = np.zeros((len(p), self.K))
            np.add.at(blk.T, self.grp, ins.T)
            out[a:a + chunk] = blk
        return out

    def coverage(self, z, pts, half=HALF):
        w = z[self.grp]
        out = np.zeros(len(pts))
        chunk = max(1, int(4e6 // max(self.R, 1)))
        for a in range(0, len(pts), chunk):
            p = pts[a:a + chunk]
            dx = p[:, None, 0] - self.pl[None, :, 0]
            dy = p[:, None, 1] - self.pl[None, :, 1]
            u = dx * self.cs[None, :] + dy * self.sn[None, :]
            v = -dx * self.sn[None, :] + dy * self.cs[None, :]
            out[a:a + chunk] = ((np.abs(u) <= half) & (np.abs(v) <= half)) @ w
        return out

    def refine(self, z, x, y, step=0.004, iters=45):
        best = self.coverage(z, np.array([[x, y]]))[0]
        s = self.s
        for _ in range(iters):
            moved = False
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                nx, ny = min(max(x + dx * step, 0), s), min(max(y + dy * step, 0), s)
                c = self.coverage(z, np.array([[nx, ny]]))[0]
                if c > best + 1e-12:
                    best, x, y, moved = c, nx, ny, True
                    break
            if not moved:
                step *= 0.5
                if step < 1e-8:
                    break
        return x, y, best


def wedge(s, step):
    """one eighth of the container: s/2 <= x <= y <= s"""
    xs = np.arange(s / 2, s + 1e-9, step)
    X, Y = np.meshgrid(xs, xs, indexing="ij")
    m = X <= Y + 1e-12
    return np.stack([X[m], Y[m]], 1)


def corner_pts(pk, eps=2e-5, max_pts=40000, seed=0):
    """corners of the placement squares, nudged into the 8 neighbouring cells (coverage maxima
    of a union of squares are attained at corners / edge crossings of the arrangement)"""
    corn = np.array([[-1, -1], [1, -1], [1, 1], [-1, 1]]) * HALF
    rot = np.stack([np.stack([pk.cs, -pk.sn], 1), np.stack([pk.sn, pk.cs], 1)], 1)
    V = (np.einsum("rij,kj->rki", rot, corn) + pk.pl[:, None, :2]).reshape(-1, 2)
    offs = np.array([[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]) * eps
    pts = (V[:, None, :] + offs[None, :, :]).reshape(-1, 2)
    s = pk.s
    pts = pts[(pts[:, 0] >= s / 2 - 1e-9) & (pts[:, 0] <= s) & (pts[:, 1] >= pts[:, 0] - 1e-9) & (pts[:, 1] <= s)]
    if len(pts) > max_pts:
        pts = pts[np.random.default_rng(seed).choice(len(pts), max_pts, replace=False)]
    return pts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fracpack")
    ap.add_argument("--out", default=None)
    ap.add_argument("--rounds", type=int, default=30)
    ap.add_argument("--grid", type=float, default=0.01)
    ap.add_argument("--fine_grid", type=float, default=0.004)
    ap.add_argument("--wmin", type=float, default=1e-10)
    ap.add_argument("--time_limit", type=float, default=1500)
    ap.add_argument("--extra_state", default=None,
                    help="LP *_state.json: add the D4 images of (a sample of) ALL its rows as "
                         "candidate placements, not only those with a non-zero dual")
    ap.add_argument("--extra_cap", type=int, default=1500)
    a = ap.parse_args()

    d = json.load(open(a.fracpack))
    s = float(d["s"])
    pls = [p for p in d["placements"]]
    if a.extra_state:
        import lp_measure2 as L
        st = json.load(open(a.extra_state))
        have = set((round(p[0], 6), round(p[1], 6), round(p[2], 7)) for p in pls)
        cand = [r for r in st["rows"] if (round(r[0], 6), round(r[1], 6), round(r[2], 7)) not in have]
        if len(cand) > a.extra_cap:
            sel = np.random.default_rng(0).choice(len(cand), a.extra_cap, replace=False)
            cand = [cand[i] for i in sel]
        for (cx, cy, th) in cand:
            for (x, y, t) in L.d4_placement_images(cx, cy, th, s):
                pls.append([x, y, t, 0.0])
        print(f"extra candidate placements from {a.extra_state}: {len(cand)} rows "
              f"-> {8*len(cand)} images", flush=True)
    assert len(pls) % 8 == 0, f"placement list length {len(pls)} is not a multiple of 8"
    pk = Pack(pls, s)
    keep = np.array([pk.cost[k] > 0 for k in range(pk.K)])
    t0 = time.time()
    raw = sum(p[3] for p in pls)
    print(f"s={s} placements={pk.R} orbits={pk.K} raw_weight={raw:.6f}", flush=True)

    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.setOptionValue("threads", 1)
    for k in range(pk.K):
        h.addCol(-pk.cost[k], 0.0, highspy.kHighsInf, 0, np.array([], dtype=np.int32), np.array([]))
    seen, nrows = set(), 0

    def add_points(newpts):
        nonlocal nrows
        if len(newpts) == 0:
            return 0
        C = pk.counts(newpts)
        added = 0
        for r in range(len(C)):
            idx = np.nonzero(C[r])[0]
            if len(idx) == 0:
                continue
            key = (idx.tobytes(), C[r][idx].tobytes())
            if key in seen:
                continue
            seen.add(key)
            h.addRow(-highspy.kHighsInf, 1.0, len(idx), idx.astype(np.int32), C[r][idx])
            nrows += 1; added += 1
        return added

    add_points(wedge(s, a.grid))
    add_points(corner_pts(pk))
    print(f"initial rows {nrows} ({time.time()-t0:.0f}s)", flush=True)

    fpts = wedge(s, a.fine_grid)
    hist, z = [], np.zeros(pk.K)
    for k in range(a.rounds):
        h.run()
        z = np.array(h.getSolution().col_value)
        val = float(pk.cost @ z)
        cov = pk.coverage(z, fpts)
        cp = corner_pts(pk, seed=k)
        ccov = pk.coverage(z, cp) if len(cp) else np.zeros(0)
        maxcov = float(max(cov.max(), ccov.max() if len(ccov) else 0.0))
        cand = []
        for i in np.argsort(-cov)[:60]:
            if cov[i] <= 1 + 1e-9:
                break
            x, y, c = pk.refine(z, fpts[i, 0], fpts[i, 1])
            cand.append([x, y]); maxcov = max(maxcov, c)
        for i in (np.argsort(-ccov)[:60] if len(ccov) else []):
            if ccov[i] <= 1 + 1e-9:
                break
            x, y, c = pk.refine(z, cp[i, 0], cp[i, 1])
            cand.append([x, y]); maxcov = max(maxcov, c)
        newp = [fpts[np.argsort(-cov)[:400]]]
        if len(cp):
            newp.append(cp[np.argsort(-ccov)[:400]])
        if cand:
            newp.append(np.array(cand))
        na = add_points(np.vstack(newp))
        hist.append(dict(round=k, value=val, maxcov=maxcov, added=na, rows=nrows, t=time.time() - t0))
        print(f"  lb {k:2d} value={val:.6f} maxcov={maxcov:.6f} +pts={na} rows={nrows} "
              f"t={time.time()-t0:.0f}s", flush=True)
        if na == 0 or maxcov <= 1 + 1e-6:
            break
        if time.time() - t0 > a.time_limit:
            print("  time limit", flush=True); break

    # a-posteriori: recompute objective and max coverage ourselves from z
    cov = pk.coverage(z, np.vstack([fpts, corner_pts(pk, seed=999)]))
    maxcov_final = float(cov.max())
    value = float(pk.cost @ z)
    bound = value / max(1.0, maxcov_final)
    out = dict(s=s, n_placements=pk.R, n_orbits=pk.K, raw_weight=raw,
               lb_value=value, maxcov_final=maxcov_final, lower_bound=bound, eta_lower=bound - 11,
               rows=nrows, history=hist, half=HALF, source=os.path.basename(a.fracpack),
               placements=[[float(pk.pl[i, 0]), float(pk.pl[i, 1]), float(pk.pl[i, 2]),
                            float(z[pk.grp[i]])] for i in range(pk.R) if z[pk.grp[i]] > 1e-12],
               wall_time=time.time() - t0)
    op = a.out or os.path.join(HERE, "results",
                               "fracpack_lb_" + os.path.basename(a.fracpack).split("_", 1)[1])
    json.dump(out, open(op, "w"))
    print(f"LB s={s} value={value:.6f} maxcov={maxcov_final:.6f} bound={bound:.6f} "
          f"eta_lb={bound-11:.6f} -> {op}", flush=True)


if __name__ == "__main__":
    main()
