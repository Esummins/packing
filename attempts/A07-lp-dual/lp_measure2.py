"""
A07-lp-dual, version 2: covering LP with BOTH row generation (placements) and column generation
(atoms at arbitrary positions), i.e. a double cutting-plane method for the semi-infinite LP

    tau*(s) = min mu([0,s]^2)  s.t.  mu(Q) >= 1  for every closed unit square Q in [0,s]^2.

Why v2: with atoms restricted to a grid of spacing h the dual (fractional packing) exploits
sliver overlaps that avoid grid points (coverage checked only at grid nodes), which biases
tau upward by O(h) and produced tau_grid(3.80) = 11.000 exactly (a near-packing of 11 squares
with sliver overlaps).  Generating atoms exactly where the current fractional packing over-covers
removes that bias.

Variables  : D4-orbits of atoms (weight per point; objective = number of distinct points).
Constraints: placements (cx,cy,theta), theta in [0,pi/4], c in the C4 fundamental quadrant;
             coefficient = number of orbit points inside the eps-shrunk closed square
             |R(-theta)(p-c)|_inf <= 1/2 - EPS_GEO  (robustness margin for the rigorous verifier).
Row oracle : histogram lower bounds on a fine (c,theta) grid + exact evaluation + pattern search.
Col oracle : maximum of the D4-symmetrised fractional packing's coverage (fine grid + arrangement
             vertices + pattern search).
LP         : HiGHS via highspy, incremental rows/columns (warm start).

Usage: python lp_measure2.py --s 3.80 --n 11 [--N0 38] [--out results/...json]
"""
import argparse, json, math, time, os
import numpy as np
import highspy

EPS_GEO = 1e-4      # squares are shrunk by this margin in the LP rows (see verifier)


# ------------------------------------------------------------------ geometry
def rot_coords(P, theta):
    c, s = math.cos(theta), math.sin(theta)
    return np.stack([P[:, 0] * c + P[:, 1] * s, -P[:, 0] * s + P[:, 1] * c], axis=1)


def inside_mask(P, cx, cy, theta, half=0.5 - EPS_GEO):
    c, s = math.cos(theta), math.sin(theta)
    dx = P[:, 0] - cx; dy = P[:, 1] - cy
    ux = dx * c + dy * s; uy = -dx * s + dy * c
    return (np.abs(ux) <= half) & (np.abs(uy) <= half)


def centre_range(s, theta):
    w = math.cos(theta) + math.sin(theta)
    return w / 2, s - w / 2


def d4_point_images(x, y, s):
    pts = []
    for (a, b) in [(x, y), (s - x, y), (x, s - y), (s - x, s - y), (y, x), (s - y, x), (y, s - x), (s - y, s - x)]:
        pts.append((a, b))
    return pts


def d4_placement_images(cx, cy, th, s):
    out = []
    x, y, t = cx, cy, th
    for k in range(4):
        out.append((x, y, t))
        out.append((s - x, y, (math.pi / 2 - t) % (math.pi / 2)))
        x, y = s - y, x
    return out


def canon_point(x, y, s):
    """canonical representative of the D4 orbit: 0 <= x <= y <= s/2 (fundamental triangle)"""
    x = min(x, s - x); y = min(y, s - y)
    if x > y:
        x, y = y, x
    return x, y


# ------------------------------------------------------------------ model
class Model:
    def __init__(self, s, n, verbose=False):
        self.s, self.n = s, n
        self.h = highspy.Highs()
        self.h.setOptionValue("output_flag", False)
        self.h.setOptionValue("threads", 1)
        self.orbits = []           # list of dict(rep=(x,y), pts=np.array (m,2))
        self.P = np.zeros((0, 2))  # all atom points
        self.P_orb = np.zeros(0, dtype=int)
        self.rows = []             # (cx,cy,theta)
        self.rowkeys = set()
        self.orbkeys = set()
        self.w = None; self.y = None; self.obj = None

    # --- atoms
    def add_orbit(self, x, y, tol=1e-7):
        x, y = canon_point(x, y, self.s)
        key = (round(x / tol), round(y / tol))
        if key in self.orbkeys:
            return False
        pts = []
        for p in d4_point_images(x, y, self.s):
            if all(abs(p[0] - q[0]) > 1e-12 or abs(p[1] - q[1]) > 1e-12 for q in pts):
                pts.append(p)
        pts = np.array(pts)
        m = len(pts)
        # coefficients in existing rows
        idx, val = [], []
        for r, (cx, cy, th) in enumerate(self.rows):
            k = int(inside_mask(pts, cx, cy, th).sum())
            if k:
                idx.append(r); val.append(float(k))
        self.h.addCol(float(m), 0.0, highspy.kHighsInf, len(idx), np.array(idx, dtype=np.int32), np.array(val))
        self.orbkeys.add(key)
        self.orbits.append(dict(rep=(x, y), pts=pts))
        self.P = np.vstack([self.P, pts])
        self.P_orb = np.concatenate([self.P_orb, np.full(m, len(self.orbits) - 1)])
        return True

    # --- rows
    def add_row(self, cx, cy, th):
        m = inside_mask(self.P, cx, cy, th)
        cnt = np.bincount(self.P_orb[m], minlength=len(self.orbits))
        idx = np.nonzero(cnt)[0]
        if len(idx) == 0:
            return False
        key = hash((idx.tobytes(), cnt[idx].tobytes()))
        if key in self.rowkeys:
            return False
        self.rowkeys.add(key)
        self.h.addRow(1.0, highspy.kHighsInf, len(idx), idx.astype(np.int32), cnt[idx].astype(float))
        self.rows.append((float(cx), float(cy), float(th)))
        return True

    def solve(self):
        self.h.run()
        sol = self.h.getSolution()
        self.w = np.array(sol.col_value)
        self.y = np.abs(np.array(sol.row_dual))
        self.obj = self.h.getInfo().objective_function_value
        return self.obj

    def wpts(self):
        return self.w[self.P_orb]

    def packing_images(self, ymin=1e-9):
        """D4-symmetrised fractional packing: list of (cx,cy,theta,weight)"""
        out = []
        for r, yv in enumerate(self.y):
            if yv > ymin:
                cx, cy, th = self.rows[r]
                for (a, b, t) in d4_placement_images(cx, cy, th, self.s):
                    out.append((a, b, t, yv / 8))
        return out


# ------------------------------------------------------------------ row oracle
class RowOracle:
    def __init__(self, s, P, w, delta=0.002, cstep=0.02, n_theta=91):
        self.s = s
        nz = w > 1e-12
        self.P = P[nz]; self.w = w[nz]; self.K = len(self.w)
        self.delta, self.cstep, self.n_theta = delta, cstep, n_theta

    def mass(self, cx, cy, theta):
        return float(self.w[inside_mask(self.P, cx, cy, theta)].sum())

    def mass_many(self, C, theta):
        out = np.empty(len(C))
        U = rot_coords(self.P, theta); Cr = rot_coords(C, theta)
        chunk = max(1, int(2e7 // max(self.K, 1)))
        half = 0.5 - EPS_GEO
        for a in range(0, len(C), chunk):
            cc = Cr[a:a + chunk]
            dx = np.abs(U[None, :, 0] - cc[:, None, 0]) <= half
            dy = np.abs(U[None, :, 1] - cc[:, None, 1]) <= half
            out[a:a + chunk] = (dx & dy) @ self.w
        return out

    def scan_theta(self, theta, thresh):
        s = self.s
        lo, hi = centre_range(s, theta)
        n = int(math.ceil((hi - lo) / self.cstep))
        xs = np.linspace(lo, hi, n + 1)
        xs = xs[xs >= s / 2 - 1e-12]
        X, Y = np.meshgrid(xs, xs, indexing="ij")
        C = np.stack([X.ravel(), Y.ravel()], axis=1)
        U = rot_coords(self.P, theta)
        d = self.delta
        ox, oy = U[:, 0].min() - 1.0, U[:, 1].min() - 1.0
        nx = int((U[:, 0].max() - ox) / d) + 3; ny = int((U[:, 1].max() - oy) / d) + 3
        ix = ((U[:, 0] - ox) / d).astype(int); iy = ((U[:, 1] - oy) / d).astype(int)
        H = np.zeros((nx + 1, ny + 1)); np.add.at(H, (ix + 1, iy + 1), self.w)
        Pf = H.cumsum(0).cumsum(1)
        Cr = rot_coords(C, theta)
        half = 0.5 - EPS_GEO
        xlo = np.clip(np.ceil((Cr[:, 0] - half - ox) / d).astype(int), 0, nx)
        xhi = np.clip(np.floor((Cr[:, 0] + half - ox) / d).astype(int), 0, nx)
        ylo = np.clip(np.ceil((Cr[:, 1] - half - oy) / d).astype(int), 0, ny)
        yhi = np.clip(np.floor((Cr[:, 1] + half - oy) / d).astype(int), 0, ny)
        inner = Pf[xhi, yhi] - Pf[xlo, yhi] - Pf[xhi, ylo] + Pf[xlo, ylo]
        cand = np.nonzero(inner < thresh + 1e-9)[0]
        if len(cand) == 0:
            return np.zeros((0, 2)), np.zeros(0)
        Cc = C[cand]
        return Cc, self.mass_many(Cc, theta)

    def refine(self, cx, cy, theta, iters=60):
        s = self.s
        best = self.mass(cx, cy, theta)
        step_c, step_t = self.cstep, math.pi / 4 / (self.n_theta - 1)
        dirs = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1),
                (1, 1, 0), (1, -1, 0), (-1, 1, 0), (-1, -1, 0), (1, 0, 1), (-1, 0, 1), (0, 1, 1), (0, -1, 1),
                (1, 0, -1), (-1, 0, -1), (0, 1, -1), (0, -1, -1)]
        for _ in range(iters):
            improved = False
            for dcx, dcy, dth in dirs:
                th = min(max(theta + dth * step_t, 0.0), math.pi / 4)
                lo, hi = centre_range(s, th)
                x = min(max(cx + dcx * step_c, lo), hi); y = min(max(cy + dcy * step_c, lo), hi)
                m = self.mass(x, y, th)
                if m < best - 1e-12:
                    best, cx, cy, theta = m, x, y, th
                    improved = True
                    break
            if not improved:
                step_c *= 0.5; step_t *= 0.5
                if step_c < 1e-7:
                    break
        return cx, cy, theta, best

    def search(self, thresh=1.0, max_refine=300, max_return=2000, extra_thetas=()):
        thetas = list(np.linspace(0, math.pi / 4, self.n_theta)) + list(extra_thetas)
        found = []
        for th in thetas:
            Cc, m = self.scan_theta(th, thresh)
            sel = np.nonzero(m < thresh - 1e-9)[0]
            for k in sel:
                found.append((Cc[k, 0], Cc[k, 1], th, m[k]))
        found.sort(key=lambda t: t[3])
        # refine: best per theta first, then by mass
        by_theta = {}
        for f in found:
            by_theta.setdefault(round(f[2], 9), f)
        pri = list(by_theta.values()) + found
        refined, seen = [], set()
        for (cx, cy, th, m) in pri[:max_refine]:
            rcx, rcy, rth, rm = self.refine(cx, cy, th)
            key = (round(rcx, 6), round(rcy, 6), round(rth, 7))
            if key not in seen:
                seen.add(key); refined.append((rcx, rcy, rth, rm))
        out = refined + found[:max_return]
        out.sort(key=lambda t: t[3])
        return out


# ------------------------------------------------------------------ column oracle
class ColOracle:
    def __init__(self, s, images):
        self.s = s
        self.pl = np.array([(a, b, t, w) for (a, b, t, w) in images if w > 1e-12])   # (R,4)
        self.cos = np.cos(self.pl[:, 2]); self.sin = np.sin(self.pl[:, 2])
        self.half = 0.5 - EPS_GEO

    def coverage(self, pts):
        """coverage of points (m,2), chunked"""
        out = np.zeros(len(pts))
        R = len(self.pl)
        chunk = max(1, int(1e7 // max(R, 1)))
        for a in range(0, len(pts), chunk):
            p = pts[a:a + chunk]
            dx = p[:, None, 0] - self.pl[None, :, 0]; dy = p[:, None, 1] - self.pl[None, :, 1]
            ux = dx * self.cos[None, :] + dy * self.sin[None, :]
            uy = -dx * self.sin[None, :] + dy * self.cos[None, :]
            ins = (np.abs(ux) <= self.half) & (np.abs(uy) <= self.half)
            out[a:a + chunk] = ins @ self.pl[:, 3]
        return out

    def arrangement_vertices(self, max_pairs=200000):
        """intersection points of edges of pairs of placement squares (candidate maximisers)"""
        s = self.s
        pl = self.pl
        # corners of each square: (R,4,2)
        corn = np.array([[-1, -1], [1, -1], [1, 1], [-1, 1]]) * self.half
        R = len(pl)
        cs = np.stack([np.stack([self.cos, -self.sin], 1), np.stack([self.sin, self.cos], 1)], 1)  # (R,2,2) rotation
        V = np.einsum("rij,kj->rki", cs, corn) + pl[:, None, :2]     # (R,4,2)
        E0 = V; E1 = np.roll(V, -1, axis=1)                          # edges (R,4,2)
        # candidate pairs: centres within sqrt(2)
        d = np.linalg.norm(pl[:, None, :2] - pl[None, :, :2], axis=2)
        I, J = np.nonzero(np.triu(d < 1.5, 1))
        if len(I) > max_pairs:
            sel = np.random.default_rng(0).choice(len(I), max_pairs, replace=False); I, J = I[sel], J[sel]
        pts = []
        for ei in range(4):
            for ej in range(4):
                p = E0[I, ei]; r = E1[I, ei] - p
                q = E0[J, ej]; u = E1[J, ej] - q
                den = r[:, 0] * u[:, 1] - r[:, 1] * u[:, 0]
                ok = np.abs(den) > 1e-12
                qp = q - p
                t = (qp[:, 0] * u[:, 1] - qp[:, 1] * u[:, 0]) / np.where(ok, den, 1)
                v = (qp[:, 0] * r[:, 1] - qp[:, 1] * r[:, 0]) / np.where(ok, den, 1)
                good = ok & (t >= -1e-9) & (t <= 1 + 1e-9) & (v >= -1e-9) & (v <= 1 + 1e-9)
                pts.append(p[good] + t[good, None] * r[good])
        pts = np.vstack(pts) if pts else np.zeros((0, 2))
        # also square corners
        pts = np.vstack([pts, V.reshape(-1, 2)])
        # perturb into the 4 (8) neighbouring cells
        eps = 2e-5
        offs = np.array([[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]) * eps
        pts = (pts[:, None, :] + offs[None, :, :]).reshape(-1, 2)
        pts = pts[(pts[:, 0] >= 0) & (pts[:, 0] <= s) & (pts[:, 1] >= 0) & (pts[:, 1] <= s)]
        return pts

    def refine(self, x, y, step=0.005, iters=40):
        best = self.coverage(np.array([[x, y]]))[0]
        s = self.s
        for _ in range(iters):
            improved = False
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                nx = min(max(x + dx * step, 0), s); ny = min(max(y + dy * step, 0), s)
                c = self.coverage(np.array([[nx, ny]]))[0]
                if c > best + 1e-12:
                    best, x, y = c, nx, ny; improved = True; break
            if not improved:
                step *= 0.5
                if step < 1e-8:
                    break
        return x, y, best

    def search(self, thresh=1.0, grid=0.005, max_refine=80):
        s = self.s
        # fundamental triangle s/2<=x<=y<=s (1/8 of container) sampled on a grid
        xs = np.arange(s / 2, s + 1e-9, grid)
        X, Y = np.meshgrid(xs, xs, indexing="ij")
        m = X <= Y + 1e-12
        pts = np.stack([X[m], Y[m]], 1)
        cov = self.coverage(pts)
        av = self.arrangement_vertices()
        if len(av):
            av = av[(av[:, 0] >= s / 2 - 1e-9) & (av[:, 1] >= av[:, 0] - 1e-9)]
            cav = self.coverage(av)
            pts = np.vstack([pts, av]); cov = np.concatenate([cov, cav])
        order = np.argsort(-cov)
        out, seen = [], set()
        for k in order[:max_refine]:
            if cov[k] <= thresh + 1e-9:
                break
            x, y, c = self.refine(pts[k, 0], pts[k, 1])
            key = (round(x, 5), round(y, 5))
            if key not in seen:
                seen.add(key); out.append((x, y, c))
        # also include unrefined over-covered grid points (distinct)
        for k in order[max_refine:2000]:
            if cov[k] <= thresh + 1e-9:
                break
            key = (round(pts[k, 0], 5), round(pts[k, 1], 5))
            if key not in seen:
                seen.add(key); out.append((pts[k, 0], pts[k, 1], cov[k]))
        out.sort(key=lambda t: -t[2])
        return out, (cov.max() if len(cov) else 0.0)


def save_state(M, path, extra=None):
    st = dict(s=M.s, n=M.n, eps_geo=EPS_GEO, tau=float(M.obj) if M.obj is not None else None,
              rows=[list(r) for r in M.rows], orbits=[[float(o["rep"][0]), float(o["rep"][1])] for o in M.orbits],
              w=[float(v) for v in M.w] if M.w is not None else None,
              y=[float(v) for v in M.y] if M.y is not None else None)
    if extra: st.update(extra)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(st, f)
    os.replace(tmp, path)


def load_state(path):
    st = json.load(open(path))
    return [tuple(o) for o in st["orbits"]], [tuple(r) for r in st["rows"]]


# ------------------------------------------------------------------ driver
def initial_rows(s, n_theta=10, cstep=0.1):
    out = []
    for th in np.linspace(0, math.pi / 4, n_theta):
        lo, hi = centre_range(s, th)
        n = int(math.ceil((hi - lo) / cstep))
        xs = np.linspace(lo, hi, n + 1)
        xs = xs[xs >= s / 2 - 1e-12]
        for x in xs:
            for y in xs:
                out.append((x, y, th))
    return out


def run(s, n=11, N0=38, max_iter=300, tol=1e-6, out=None, verbose=True, time_limit=None,
        row_kw=None, col_kw=None, max_rows_add=1200, max_cols_add=60, init_atoms=None, init_rows=None,
        col_stop_iter=10**9, col_stop_cov=1.0, fine_row_kw=None, checkpoint=None, neigh_rows=0, neigh_d=0.003,
        extra_rows=None):
    """col_stop_iter / col_stop_cov: stop adding columns after that iteration or once maxcov < col_stop_cov
    (row-only phase -> primal-feasible mu).  fine_row_kw: settings for a final fine row search.
    checkpoint: path to write the full model state (all rows/orbits + solution) every iteration."""
    t0 = time.time()
    M = Model(s, n)
    # initial atoms: grid orbits (spacing s/N0) restricted to the fundamental triangle
    if init_atoms is not None:
        for (x, y) in init_atoms:
            M.add_orbit(x, y)
    else:
        h0 = s / N0
        for i in range(N0 // 2 + 1):
            for j in range(i, N0 // 2 + 1):
                M.add_orbit(i * h0, j * h0)
    for (cx, cy, th) in (init_rows if init_rows is not None else initial_rows(s)):
        M.add_row(cx, cy, th)
    if extra_rows:
        for (cx, cy, th) in extra_rows:
            # map to theta in [0,pi/4] and the C4 quadrant is unnecessary: rows are D4-invariant sums, any image works
            M.add_row(cx, cy, th)
    rkw = dict(delta=0.002, cstep=0.02, n_theta=91); rkw.update(row_kw or {})
    ckw = dict(grid=0.005); ckw.update(col_kw or {})
    hist = []
    if verbose:
        print(f"[s={s} n={n}] init orbits={len(M.orbits)} points={len(M.P)} rows={len(M.rows)}", flush=True)
    stall = 0
    for it in range(max_iter):
        obj = M.solve()
        wp = M.wpts()
        ro = RowOracle(s, M.P, wp, **rkw)
        viol = ro.search(thresh=1.0 - tol)
        nr = 0
        for (cx, cy, th, m) in viol[:max_rows_add]:
            nr += M.add_row(cx, cy, th)
        # neighbourhood rows around the most violated placements (stabilises the cutting-plane loop)
        for (cx, cy, th, m) in viol[:neigh_rows]:
            for dcx in (-1, 0, 1):
                for dcy in (-1, 0, 1):
                    for dth in (-1, 0, 1):
                        if dcx == dcy == dth == 0:
                            continue
                        th2 = min(max(th + dth * neigh_d, 0.0), math.pi / 4)
                        lo, hi = centre_range(s, th2)
                        nr += M.add_row(min(max(cx + dcx * neigh_d, lo), hi), min(max(cy + dcy * neigh_d, lo), hi), th2)
        co = ColOracle(s, M.packing_images())
        over, maxcov = co.search(thresh=1.0 + tol, **ckw)
        nc = 0
        cols_on = (it < col_stop_iter) and (maxcov >= col_stop_cov)
        if cols_on:
            for (x, y, c) in over[:max_cols_add]:
                nc += M.add_orbit(x, y)
        minmass = viol[0][3] if viol else 1.0
        if nr == 0 and not cols_on and fine_row_kw:
            # rows converged at coarse settings: run the fine search once before declaring convergence
            rof = RowOracle(s, M.P, wp, **fine_row_kw)
            violf = rof.search(thresh=1.0 - tol)
            for (cx, cy, th, m) in violf[:max_rows_add]:
                nr += M.add_row(cx, cy, th)
            if violf:
                minmass = min(minmass, violf[0][3])
            if verbose:
                print(f"    fine row search: minmass={violf[0][3] if violf else 1.0:.6f} +rows={nr}", flush=True)
        if checkpoint:
            save_state(M, checkpoint, dict(it=it, obj=obj, minmass=float(minmass), maxcov=float(maxcov)))
        hist.append(dict(it=it, obj=obj, rows=len(M.rows), orbits=len(M.orbits), atoms_nz=int((wp > 1e-9).sum()),
                         minmass=float(minmass), maxcov=float(maxcov), added_rows=nr, added_cols=nc, t=time.time() - t0))
        if verbose:
            print(f"  it {it:3d} tau={obj:.6f} rows={len(M.rows)} orbs={len(M.orbits)} atoms>0={int((wp>1e-9).sum())} "
                  f"minmass={minmass:.6f} maxcov={maxcov:.6f} +rows={nr} +cols={nc} t={time.time()-t0:.0f}s", flush=True)
        if nr == 0 and nc == 0:
            break
        if time_limit and time.time() - t0 > time_limit:
            print("  time limit", flush=True); break
    obj = M.solve()
    wp = M.wpts()
    res = dict(s=s, n=n, tau=obj, nu=float(M.y.sum()), eps_geo=EPS_GEO, converged=bool(nr == 0 and nc == 0),
               n_rows=len(M.rows), n_orbits=len(M.orbits), history=hist, time=time.time() - t0)
    res["atoms"] = [dict(rep=[float(o["rep"][0]), float(o["rep"][1])], m=int(len(o["pts"])), w=float(M.w[k]))
                    for k, o in enumerate(M.orbits) if M.w[k] > 1e-10]
    res["packing"] = [dict(cx=M.rows[r][0], cy=M.rows[r][1], theta=M.rows[r][2], y=float(M.y[r]))
                      for r in range(len(M.rows)) if M.y[r] > 1e-10]
    if out:
        with open(out, "w") as f:
            json.dump(res, f, indent=1)
    if verbose:
        print(f"DONE s={s} n={n} tau={obj:.6f} nu={res['nu']:.6f} conv={res['converged']} rows={len(M.rows)} "
              f"orbits={len(M.orbits)} atoms_nz={len(res['atoms'])} packing_support={len(res['packing'])} "
              f"time={time.time()-t0:.0f}s", flush=True)
    return res, M


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--s", type=float, required=True)
    ap.add_argument("--n", type=int, default=11)
    ap.add_argument("--N0", type=int, default=38)
    ap.add_argument("--out", type=str, default=None)
    ap.add_argument("--max_iter", type=int, default=300)
    ap.add_argument("--n_theta", type=int, default=91)
    ap.add_argument("--cstep", type=float, default=0.02)
    ap.add_argument("--time_limit", type=float, default=None)
    ap.add_argument("--warm", type=str, default=None, help="json result to warm start atoms/rows from")
    ap.add_argument("--state", type=str, default=None, help="checkpoint state file to resume from (all rows/orbits)")
    ap.add_argument("--col_stop_iter", type=int, default=10**9)
    ap.add_argument("--col_stop_cov", type=float, default=1.0)
    ap.add_argument("--max_cols_add", type=int, default=60)
    ap.add_argument("--fine", action="store_true", help="final fine row search (n_theta=361, cstep=0.005)")
    ap.add_argument("--neigh_rows", type=int, default=0, help="add 26 neighbourhood rows around the k most violated placements")
    ap.add_argument("--neigh_d", type=float, default=0.003)
    ap.add_argument("--extra_rows", type=str, default=None, help="json list of [cx,cy,theta] rows to add at start (e.g. verifier witnesses)")
    a = ap.parse_args()
    out = a.out or f"results/v2_n{a.n}_s{a.s:.4f}.json"
    ia = ir = None
    if a.warm:
        wr = json.load(open(a.warm))
        ia = [tuple(x["rep"]) for x in wr["atoms"]]
        ir = [(p["cx"], p["cy"], p["theta"]) for p in wr["packing"]] + initial_rows(a.s)
    if a.state:
        ia, ir = load_state(a.state)
    run(a.s, n=a.n, N0=a.N0, max_iter=a.max_iter, out=out, time_limit=a.time_limit,
        row_kw=dict(n_theta=a.n_theta, cstep=a.cstep), init_atoms=ia, init_rows=ir,
        col_stop_iter=a.col_stop_iter, col_stop_cov=a.col_stop_cov, max_cols_add=a.max_cols_add,
        fine_row_kw=(dict(n_theta=361, cstep=0.005, delta=0.001) if a.fine else None),
        checkpoint=out.replace(".json", "_state.json"), neigh_rows=a.neigh_rows, neigh_d=a.neigh_d,
        extra_rows=(json.load(open(a.extra_rows)) if a.extra_rows else None))
