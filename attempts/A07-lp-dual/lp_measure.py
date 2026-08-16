"""
A07-lp-dual: discretised covering LP for the measure ("fractional unavoidable set") lower bound.

Problem.  Container [0,s]^2.  Find a non-negative measure mu with mu(Q) >= 1 for every closed unit
square Q inside the container (any orientation) and minimal total mass tau*(s).  If tau*(s) < n
then s(n) >= s.

Discretisation.  Atoms on the grid x_i = i*s/N (i = 0..N), weights on D4-orbits (variables).
Constraints = placements (cx, cy, theta), theta in [0, pi/4] (D4 symmetry of mu makes theta and
pi/2 - theta equivalent), added by row generation with a heuristic separation oracle
(histogram lower bounds on a fine (c,theta) grid + exact evaluation + pattern-search refinement).

LP solved with HiGHS (highspy) with warm start between row additions.

Usage:  python lp_measure.py --s 3.80 --N 76 [--n 11] [--out results/xxx.json]
"""
import argparse, json, math, sys, time, os
import numpy as np
import highspy

# ----------------------------------------------------------------------------------------------
# geometry helpers
# ----------------------------------------------------------------------------------------------

def rot_coords(P, theta):
    """coordinates of points P (K,2) in the frame rotated by theta:  u = R(-theta) p"""
    c, s = math.cos(theta), math.sin(theta)
    return np.stack([P[:, 0] * c + P[:, 1] * s, -P[:, 0] * s + P[:, 1] * c], axis=1)


def inside_mask(P, cx, cy, theta, tol=1e-9):
    """boolean mask of points inside the closed unit square centred (cx,cy) with angle theta"""
    c, s = math.cos(theta), math.sin(theta)
    dx = P[:, 0] - cx
    dy = P[:, 1] - cy
    ux = dx * c + dy * s
    uy = -dx * s + dy * c
    return (np.abs(ux) <= 0.5 + tol) & (np.abs(uy) <= 0.5 + tol)


def centre_range(s, theta):
    w = math.cos(theta) + math.sin(theta)
    return w / 2, s - w / 2


# ----------------------------------------------------------------------------------------------
# grid + D4 orbits
# ----------------------------------------------------------------------------------------------

class Grid:
    def __init__(self, s, N):
        self.s, self.N = s, N
        self.h = s / N
        I, J = np.meshgrid(np.arange(N + 1), np.arange(N + 1), indexing="ij")
        I = I.ravel(); J = J.ravel()
        self.I, self.J = I, J
        self.P = np.stack([I * self.h, J * self.h], axis=1)          # (M,2) point coordinates
        # canonical orbit representative: lexicographically smallest of the 8 images
        imgs = [(I, J), (N - I, J), (I, N - J), (N - I, N - J), (J, I), (N - J, I), (J, N - I), (N - J, N - I)]
        keys = np.stack([a * (N + 1) + b for a, b in imgs], axis=1)
        canon = keys.min(axis=1)
        uniq, inv, counts = np.unique(canon, return_inverse=True, return_counts=True)
        self.orbit_of = inv                    # point -> orbit index
        self.orbit_size = counts.astype(float)  # orbit -> number of points
        self.n_orb = len(uniq)
        self.orbit_rep = uniq                   # canonical key of orbit (i*(N+1)+j)

    def row(self, cx, cy, theta):
        """sparse row (orbit indices, coefficients) for the placement"""
        m = inside_mask(self.P, cx, cy, theta)
        cnt = np.bincount(self.orbit_of[m], minlength=self.n_orb)
        idx = np.nonzero(cnt)[0]
        return idx, cnt[idx].astype(float)


# ----------------------------------------------------------------------------------------------
# heuristic separation oracle
# ----------------------------------------------------------------------------------------------

class Oracle:
    def __init__(self, grid, wpts, delta=0.002, cstep=0.01, n_theta=181, quadrant=True):
        self.g = grid
        self.s = grid.s
        nz = wpts > 1e-12
        self.P = grid.P[nz]
        self.w = wpts[nz]
        self.K = len(self.w)
        self.delta, self.cstep, self.n_theta = delta, cstep, n_theta
        self.quadrant = quadrant

    def mass(self, cx, cy, theta):
        m = inside_mask(self.P, cx, cy, theta)
        return float(self.w[m].sum())

    def mass_many(self, C, theta):
        """exact masses for centres C (m,2) at angle theta (chunked broadcasting)"""
        out = np.empty(len(C))
        c, s = math.cos(theta), math.sin(theta)
        U = rot_coords(self.P, theta)          # atoms in rotated frame
        Cr = rot_coords(C, theta)
        chunk = max(1, int(2e7 // max(self.K, 1)))
        for a in range(0, len(C), chunk):
            cc = Cr[a:a + chunk]
            dx = np.abs(U[None, :, 0] - cc[:, None, 0]) <= 0.5 + 1e-9
            dy = np.abs(U[None, :, 1] - cc[:, None, 1]) <= 0.5 + 1e-9
            out[a:a + chunk] = (dx & dy) @ self.w
        return out

    def scan_theta(self, theta, thresh):
        """return centres (in original frame) whose histogram lower bound < thresh, with exact masses"""
        s = self.s
        lo, hi = centre_range(s, theta)
        n = int(math.ceil((hi - lo) / self.cstep))
        xs = np.linspace(lo, hi, n + 1)
        if self.quadrant:
            # C4 fundamental domain (rotations keep theta): cx >= s/2, cy >= s/2
            xs_q = xs[xs >= s / 2 - 1e-12]
            X, Y = np.meshgrid(xs_q, xs_q, indexing="ij")
        else:
            X, Y = np.meshgrid(xs, xs, indexing="ij")
        C = np.stack([X.ravel(), Y.ravel()], axis=1)
        # histogram of atoms in rotated frame
        U = rot_coords(self.P, theta)
        d = self.delta
        ox, oy = U[:, 0].min() - 1.0, U[:, 1].min() - 1.0
        nx = int((U[:, 0].max() - ox) / d) + 3
        ny = int((U[:, 1].max() - oy) / d) + 3
        ix = ((U[:, 0] - ox) / d).astype(int)
        iy = ((U[:, 1] - oy) / d).astype(int)
        H = np.zeros((nx + 1, ny + 1))
        np.add.at(H, (ix + 1, iy + 1), self.w)
        Pf = H.cumsum(0).cumsum(1)             # Pf[i,j] = sum of bins < i, < j
        Cr = rot_coords(C, theta)
        # inner bins: i >= ceil((lo-ox)/d), i <= floor((hi-ox)/d) - 1  -> exclusive upper = floor((hi-ox)/d)
        xlo = np.ceil((Cr[:, 0] - 0.5 - ox) / d).astype(int)
        xhi = np.floor((Cr[:, 0] + 0.5 - ox) / d).astype(int)
        ylo = np.ceil((Cr[:, 1] - 0.5 - oy) / d).astype(int)
        yhi = np.floor((Cr[:, 1] + 0.5 - oy) / d).astype(int)
        xlo = np.clip(xlo, 0, nx); xhi = np.clip(xhi, 0, nx)
        ylo = np.clip(ylo, 0, ny); yhi = np.clip(yhi, 0, ny)
        inner = Pf[xhi, yhi] - Pf[xlo, yhi] - Pf[xhi, ylo] + Pf[xlo, ylo]
        cand = np.nonzero(inner < thresh + 1e-9)[0]
        if len(cand) == 0:
            return np.zeros((0, 2)), np.zeros(0)
        Cc = C[cand]
        mexact = self.mass_many(Cc, theta)
        return Cc, mexact

    def refine(self, cx, cy, theta, iters=40):
        """pattern search minimising the (piecewise constant) mass; keeps placement feasible"""
        s = self.s
        best = self.mass(cx, cy, theta)
        step_c, step_t = self.cstep, math.pi / 4 / (self.n_theta - 1)
        for _ in range(iters):
            improved = False
            for dcx, dcy, dth in [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1),
                                  (1, 1, 0), (1, -1, 0), (-1, 1, 0), (-1, -1, 0)]:
                th = min(max(theta + dth * step_t, 0.0), math.pi / 4)
                lo, hi = centre_range(s, th)
                x = min(max(cx + dcx * step_c, lo), hi)
                y = min(max(cy + dcy * step_c, lo), hi)
                m = self.mass(x, y, th)
                if m < best - 1e-12:
                    best, cx, cy, theta = m, x, y, th
                    improved = True
                    break
            if not improved:
                step_c *= 0.5; step_t *= 0.5
                if step_c < 1e-6:
                    break
        return cx, cy, theta, best

    def search(self, thresh=1.0, max_refine=400, max_return=3000, verbose=False):
        """find placements with mass < thresh.  returns list of (cx,cy,theta,mass) sorted by mass"""
        thetas = np.linspace(0, math.pi / 4, self.n_theta)
        found = []
        for th in thetas:
            Cc, m = self.scan_theta(th, thresh)
            sel = np.nonzero(m < thresh - 1e-9)[0]
            for k in sel:
                found.append((Cc[k, 0], Cc[k, 1], th, m[k]))
        found.sort(key=lambda t: t[3])
        # refine the most violated (spread over theta: take best per theta first)
        refined = []
        seen = set()
        for (cx, cy, th, m) in found[:max_refine]:
            rcx, rcy, rth, rm = self.refine(cx, cy, th)
            key = (round(rcx, 5), round(rcy, 5), round(rth, 6))
            if key not in seen:
                seen.add(key)
                refined.append((rcx, rcy, rth, rm))
        out = refined + found[max_refine:max_return]
        out.sort(key=lambda t: t[3])
        return out, (found[0][3] if found else None)


# ----------------------------------------------------------------------------------------------
# LP with row generation
# ----------------------------------------------------------------------------------------------

class CoverLP:
    def __init__(self, grid, verbose=False):
        self.g = grid
        self.h = highspy.Highs()
        self.h.setOptionValue("output_flag", verbose)
        self.h.setOptionValue("solver", "simplex")
        self.h.setOptionValue("simplex_strategy", 1)  # dual simplex
        self.h.setOptionValue("threads", 1)
        n = grid.n_orb
        inf = highspy.kHighsInf
        self.h.addVars(n, np.zeros(n), np.full(n, inf))
        self.h.changeColsCost(n, np.arange(n, dtype=np.int32), grid.orbit_size)
        self.rows = []          # list of (cx,cy,theta)
        self.rowkeys = set()

    def add_rows(self, placements):
        added = 0
        for (cx, cy, th) in placements:
            idx, val = self.g.row(cx, cy, th)
            key = hash((idx.tobytes(), val.tobytes()))
            if key in self.rowkeys or len(idx) == 0:
                continue
            self.rowkeys.add(key)
            self.h.addRow(1.0, highspy.kHighsInf, len(idx), idx.astype(np.int32), val)
            self.rows.append((float(cx), float(cy), float(th)))
            added += 1
        return added

    def solve(self):
        self.h.run()
        st = self.h.getModelStatus()
        sol = self.h.getSolution()
        info = self.h.getInfo()
        w = np.array(sol.col_value)
        y = np.array(sol.row_dual)
        return info.objective_function_value, w, y, self.h.modelStatusToString(st)


def initial_placements(s, n_theta=10, cstep=0.1):
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


def run(s, N, n=11, max_iter=200, tol=1e-6, out=None, verbose=True, oracle_kw=None, init_kw=None,
        time_limit=None):
    t0 = time.time()
    grid = Grid(s, N)
    lp = CoverLP(grid)
    init = initial_placements(s, **(init_kw or {}))
    lp.add_rows(init)
    hist = []
    okw = dict(delta=0.002, cstep=0.01, n_theta=181)
    okw.update(oracle_kw or {})
    if verbose:
        print(f"[s={s} N={N} h={grid.h:.4f}] points={len(grid.P)} orbits={grid.n_orb} init rows={len(lp.rows)}", flush=True)
    for it in range(max_iter):
        obj, w, y, st = lp.solve()
        wpts = w[grid.orbit_of]
        orc = Oracle(grid, wpts, **okw)
        viol, minm = orc.search(thresh=1.0 - tol)
        # add most violated, capped
        cap = 1500
        add = [(a, b, c) for (a, b, c, m) in viol[:cap]]
        # also add the exact grid candidates found by refinement neighbours? keep simple
        nadd = lp.add_rows(add)
        hist.append(dict(it=it, obj=obj, rows=len(lp.rows), nnz_atoms=int((wpts > 1e-9).sum()),
                         minmass=(viol[0][3] if viol else None), added=nadd, t=time.time() - t0))
        if verbose:
            print(f"  it {it:3d} tau={obj:.6f} rows={len(lp.rows)} atoms>0={int((wpts>1e-9).sum())} "
                  f"minmass={viol[0][3] if viol else 'none':} added={nadd} t={time.time()-t0:.0f}s [{st}]", flush=True)
        if nadd == 0 or (viol and viol[0][3] >= 1 - tol):
            break
        if time_limit and time.time() - t0 > time_limit:
            print("  time limit reached", flush=True)
            break
    obj, w, y, st = lp.solve()
    wpts = w[grid.orbit_of]
    res = dict(s=s, N=N, h=grid.h, n=n, tau=obj, converged=bool(viol == [] or viol[0][3] >= 1 - tol),
               n_rows=len(lp.rows), n_orbits=grid.n_orb, n_points=len(grid.P), history=hist,
               time=time.time() - t0)
    nz = np.nonzero(wpts > 1e-9)[0]
    res["atoms"] = [dict(i=int(grid.I[k]), j=int(grid.J[k]), x=float(grid.P[k, 0]), y=float(grid.P[k, 1]),
                         w=float(wpts[k])) for k in nz]
    ynz = np.nonzero(np.abs(y) > 1e-9)[0]
    res["packing"] = [dict(cx=lp.rows[k][0], cy=lp.rows[k][1], theta=lp.rows[k][2], y=float(abs(y[k]))) for k in ynz]
    res["nu"] = float(np.abs(y).sum())
    if out:
        with open(out, "w") as f:
            json.dump(res, f, indent=1)
    if verbose:
        print(f"DONE s={s} N={N} tau={obj:.6f} nu={res['nu']:.6f} conv={res['converged']} rows={len(lp.rows)} "
              f"atoms={len(nz)} packing_support={len(ynz)} time={time.time()-t0:.0f}s", flush=True)
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--s", type=float, required=True)
    ap.add_argument("--N", type=int, required=True)
    ap.add_argument("--n", type=int, default=11)
    ap.add_argument("--out", type=str, default=None)
    ap.add_argument("--max_iter", type=int, default=200)
    ap.add_argument("--n_theta", type=int, default=181)
    ap.add_argument("--cstep", type=float, default=0.01)
    ap.add_argument("--time_limit", type=float, default=None)
    a = ap.parse_args()
    out = a.out or f"results/lp_n{a.n}_s{a.s:.4f}_N{a.N}.json"
    run(a.s, a.N, n=a.n, max_iter=a.max_iter, out=out, oracle_kw=dict(n_theta=a.n_theta, cstep=a.cstep),
        time_limit=a.time_limit)
