"""
A12: orientation-restricted measure LP + REGION-RANK CUTS  (extends A10's lp_measure_box.py, imported).

Primal (covering) form:   min  mu(total) + sum_R k(R) lambda_R
                          s.t. mu(Q) + sum_{R : Q in R} lambda_R  >= alpha(theta(Q))   for every admissible Q
                               mu >= 0, lambda >= 0
Dual = fractional packing with the extra rows  sum_{Q in R} x_Q <= k(R).
A region R is a C4-symmetric union of (c,theta)-boxes  [x0,x1]x[y0,y1]x[th0,th1] (degrees; theta mod 90);
k(R) is supplied (certified elsewhere: robust-overlap graph alpha, incircle bound, sub-LP ...).

Regions file (json):  [ {"name":..., "k": 6, "boxes": [[x0,x1,y0,y1,th0,th1], ...]}, ... ]   (boxes are C4-expanded here)
Usage:  python lp_region.py --s 3.86 --theta_box "0-2,32-36" --regions regs.json --out results/x.json [--warm A10result.json]
"""
import argparse, json, math, time, os, sys
import numpy as np
import highspy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lp_measure_box as base
from lp_measure_box import (EPS_GEO, DEG, ThetaBox, Sym, ColOracle, RowOracle, centre_range, inside_mask,
                            initial_rows, save_state, load_state, warm_from, norm_theta)


class Region:
    def __init__(self, name, k, boxes_deg, s, sym4=True):
        self.name, self.k = name, float(k)
        B = []
        for (x0, x1, y0, y1, t0, t1) in boxes_deg:
            imgs = [(x0, x1, y0, y1)]
            if sym4:
                imgs = [(x0, x1, y0, y1), (s - y1, s - y0, x0, x1), (s - x1, s - x0, s - y1, s - y0), (y0, y1, s - x1, s - x0)]
            for (a0, a1, b0, b1) in imgs:
                B.append((a0, a1, b0, b1, t0 * DEG, t1 * DEG))
        self.boxes = np.array(B).reshape(-1, 6)

    def contains(self, cx, cy, th):
        t = norm_theta(th)
        B = self.boxes
        m = (B[:, 0] - 1e-12 <= cx) & (cx <= B[:, 1] + 1e-12) & (B[:, 2] - 1e-12 <= cy) & (cy <= B[:, 3] + 1e-12) & \
            (B[:, 4] - 1e-12 <= t) & (t <= B[:, 5] + 1e-12)
        return bool(m.any())

    def contains_many(self, C, th):
        t = norm_theta(th)
        B = self.boxes
        okt = (B[:, 4] - 1e-12 <= t) & (t <= B[:, 5] + 1e-12)
        out = np.zeros(len(C), dtype=bool)
        for b in B[okt]:
            out |= (b[0] - 1e-12 <= C[:, 0]) & (C[:, 0] <= b[1] + 1e-12) & (b[2] - 1e-12 <= C[:, 1]) & (C[:, 1] <= b[3] + 1e-12)
        return out


class RModel(base.Model):
    def __init__(self, s, n, sym, tbox, regions):
        super().__init__(s, n, sym, tbox)
        self.regions = regions
        self.lam = np.zeros(len(regions))
        self.reg_col = []          # HiGHS column index of each region variable
        for R in regions:
            self.h.addCol(R.k, 0.0, highspy.kHighsInf, 0, np.array([], dtype=np.int32), np.array([]))
            self.reg_col.append(self.h.getNumCol() - 1)
        self.n_atom_cols = 0

    # atoms are appended after region columns; keep book-keeping of which columns are atoms
    def add_orbit(self, x, y, tol=1e-7):
        ok = super().add_orbit(x, y, tol)
        return ok

    def add_row(self, cx, cy, th):
        al = self.tbox.alpha(th)
        if al is None:
            self.n_rejected += 1
            return False
        lo, hi = centre_range(self.s, th)
        if not (lo - 1e-9 <= cx <= hi + 1e-9 and lo - 1e-9 <= cy <= hi + 1e-9):
            self.n_rejected += 1
            return False
        m = inside_mask(self.P, cx, cy, th)
        cnt = np.bincount(self.P_orb[m], minlength=len(self.orbits))
        idx = np.nonzero(cnt)[0]
        regs = [r for r, R in enumerate(self.regions) if R.contains(cx, cy, th)]
        if len(idx) == 0 and not regs:
            return False
        key = hash((idx.tobytes(), cnt[idx].tobytes(), round(al, 12), tuple(regs)))
        if key in self.rowkeys:
            return False
        self.rowkeys.add(key)
        # column indices: orbit k -> column reg_ncol + k
        nreg = len(self.regions)
        cols = np.concatenate([np.array(regs, dtype=np.int32), (idx + nreg).astype(np.int32)])
        vals = np.concatenate([np.ones(len(regs)), cnt[idx].astype(float)])
        self.h.addRow(al, highspy.kHighsInf, len(cols), cols, vals)
        self.rows.append((float(cx), float(cy), float(th)))
        self.row_alpha.append(al)
        self.rowkey_list.append(key)
        self.row_strikes.append(0)
        return True

    def solve(self):
        self.h.run()
        sol = self.h.getSolution()
        cv = np.array(sol.col_value)
        nreg = len(self.regions)
        self.lam = cv[:nreg]
        self.w = cv[nreg:]
        self.y = np.abs(np.array(sol.row_dual))
        self.obj = self.h.getInfo().objective_function_value
        return self.obj

    def lam_of(self, cx, cy, th):
        return float(sum(self.lam[r] for r, R in enumerate(self.regions) if self.lam[r] > 1e-12 and R.contains(cx, cy, th)))

    def lam_many(self, C, th):
        out = np.zeros(len(C))
        for r, R in enumerate(self.regions):
            if self.lam[r] > 1e-12:
                out += self.lam[r] * R.contains_many(C, th)
        return out


class RRowOracle(RowOracle):
    """row oracle for mass(Q) = mu(Q) + Lambda(Q).  The arrangement search enumerates cells with mu < alpha
    (a superset), samples centre + corners + a 3x3 interior grid, adds Lambda, keeps violated ones; region-box
    boundary shells are sampled explicitly; pattern-search refine uses mu + Lambda."""

    def __init__(self, s, P, w, tbox, model, **kw):
        super().__init__(s, P, w, tbox, **kw)
        self.M = model

    def mass(self, cx, cy, theta):
        return float(self.w[inside_mask(self.P, cx, cy, theta)].sum()) + self.M.lam_of(cx, cy, theta)

    def mass_many(self, C, theta):
        return super().mass_many(C, theta) + self.M.lam_many(C, theta)

    def exact_theta(self, theta, thresh, max_cand=4000):
        # NOTE: parent's exact_theta uses self.mass_many (now includes Lambda) on the sample points and cell masses
        # from the mu-arrangement only (Mc < thresh) => superset of violated cells.  We add a 3x3 grid of samples.
        s = self.s
        half = 0.5 - EPS_GEO
        lo, hi = centre_range(s, theta)
        U = base.rot_coords(self.P, theta)
        dom = np.array([[s / 2, s / 2], [hi, s / 2], [hi, hi], [s / 2, hi]])
        domr = base.rot_coords(dom, theta)
        umin, umax = domr[:, 0].min(), domr[:, 0].max()
        vmin, vmax = domr[:, 1].min(), domr[:, 1].max()
        xb = np.unique(np.concatenate([U[:, 0] - half, U[:, 0] + half, [umin, umax]]))
        yb = np.unique(np.concatenate([U[:, 1] - half, U[:, 1] + half, [vmin, vmax]]))
        xb = xb[(xb >= umin - 1e-12) & (xb <= umax + 1e-12)]
        yb = yb[(yb >= vmin - 1e-12) & (yb <= vmax + 1e-12)]
        nx, ny = len(xb) - 1, len(yb) - 1
        if nx < 1 or ny < 1:
            return np.zeros((0, 2)), np.zeros(0)
        i0 = np.searchsorted(xb, U[:, 0] - half, side="left"); i1 = np.searchsorted(xb, U[:, 0] + half, side="left")
        j0 = np.searchsorted(yb, U[:, 1] - half, side="left"); j1 = np.searchsorted(yb, U[:, 1] + half, side="left")
        i0 = np.clip(i0, 0, nx); i1 = np.clip(i1, 0, nx); j0 = np.clip(j0, 0, ny); j1 = np.clip(j1, 0, ny)
        D = np.zeros((nx + 1, ny + 1))
        np.add.at(D, (i0, j0), self.w); np.add.at(D, (i1, j0), -self.w)
        np.add.at(D, (i0, j1), -self.w); np.add.at(D, (i1, j1), self.w)
        Mc = D.cumsum(0).cumsum(1)[:nx, :ny]
        cu = 0.5 * (xb[:-1] + xb[1:]); cv = 0.5 * (yb[:-1] + yb[1:])
        du = xb[1:] - xb[:-1]; dv = yb[1:] - yb[:-1]
        cand = np.nonzero(Mc < thresh - 1e-12)
        if len(cand[0]) == 0:
            return np.zeros((0, 2)), np.zeros(0)
        I, J = cand
        c, sn = math.cos(theta), math.sin(theta)
        cx = cu[I] * c - cv[J] * sn; cy = cu[I] * sn + cv[J] * c
        tol = 0.5 * np.sqrt(du[I] ** 2 + dv[J] ** 2) + 1e-9
        ok = (cx >= s / 2 - tol) & (cx <= hi + tol) & (cy >= s / 2 - tol) & (cy <= hi + tol)
        I, J, mm = I[ok], J[ok], Mc[I, J][ok]
        if len(I) == 0:
            return np.zeros((0, 2)), np.zeros(0)
        if len(I) > max_cand:
            sel = np.argpartition(mm, max_cand)[:max_cand]
            I, J, mm = I[sel], J[sel], mm[sel]
        eps = 1e-9
        fr = [(0.5, 0.5), (eps, eps), (1 - eps, eps), (eps, 1 - eps), (1 - eps, 1 - eps)]
        fr += [(a, b) for a in (0.2, 0.5, 0.8) for b in (0.2, 0.5, 0.8) if (a, b) != (0.5, 0.5)]
        pts = []
        for fu, fv in fr:
            u = xb[I] + fu * du[I]; v = yb[J] + fv * dv[J]
            x = u * c - v * sn; y = u * sn + v * c
            x = np.clip(x, max(lo, s / 2), hi); y = np.clip(y, max(lo, s / 2), hi)
            pts.append(np.stack([x, y], 1))
        C = np.vstack(pts)
        m = self.mass_many(C, theta)
        keep = m < thresh - 1e-12
        C, m = C[keep], m[keep]
        if len(C):
            key = np.round(C, 7)
            _, ui = np.unique(key, axis=0, return_index=True)
            C, m = C[np.sort(ui)], m[np.sort(ui)]
        return C, m

    def shell_search(self, tol=1e-6, d=2e-4, ngrid=12):
        """sample just outside / on the boundary of every region box (with lambda > 0) at thetas inside and just
        outside the box's theta-interval; returns violated (cx,cy,theta,mass,alpha,piece)."""
        s = self.s
        out = []
        for r, R in enumerate(self.M.regions):
            if self.M.lam[r] <= 1e-12:
                continue
            for (x0, x1, y0, y1, t0, t1) in R.boxes:
                if x1 < s / 2 - 0.5 or y1 < s / 2 - 0.5:      # only boxes meeting the fundamental quadrant matter
                    continue
                ths = [t0 - d, t1 + d, t0, t1, 0.5 * (t0 + t1)]
                for th in ths:
                    k = self.tbox.piece_of(th)
                    if k < 0:
                        continue
                    al = self.tbox.pieces[k][2]
                    lo, hi = centre_range(s, th)
                    xs = np.linspace(x0 - d, x1 + d, ngrid); ys = np.linspace(y0 - d, y1 + d, ngrid)
                    X, Y = np.meshgrid(xs, ys, indexing="ij")
                    C = np.stack([X.ravel(), Y.ravel()], 1)
                    C = C[(C[:, 0] >= max(lo, s / 2) - 1e-12) & (C[:, 0] <= hi + 1e-12) & (C[:, 1] >= max(lo, s / 2) - 1e-12) & (C[:, 1] <= hi + 1e-12)]
                    if len(C) == 0:
                        continue
                    m = self.mass_many(C, th)
                    for j in np.nonzero(m < al - tol)[0]:
                        out.append((C[j, 0], C[j, 1], th, m[j], al, k))
        return out

    def search(self, tol=1e-6, max_refine=300, max_return=2000):
        found = []
        for th, k in self.tbox.theta_grid(self.tstep):
            al = self.tbox.pieces[k][2]
            Cc, m = self.exact_theta(th, al - tol)
            sel = np.nonzero(m < al - tol)[0]
            for j in sel:
                found.append((Cc[j, 0], Cc[j, 1], th, m[j], al, k))
        found += self.shell_search(tol=tol)
        found.sort(key=lambda t: t[3] / t[4])
        by_theta = {}
        for f in found:
            by_theta.setdefault(round(f[2], 9), f)
        pri = list(by_theta.values()) + found
        refined, seen = [], set()
        for (cx, cy, th, m, al, k) in pri[:max_refine]:
            rcx, rcy, rth, rm = self.refine(cx, cy, th, k)
            key = (round(rcx, 6), round(rcy, 6), round(rth, 7))
            if key not in seen:
                seen.add(key); refined.append((rcx, rcy, rth, rm, al))
        out = refined + [f[:5] for f in found[:max_return]]
        out.sort(key=lambda t: t[3] / t[4])
        return out


def run(s, tbox, sym, regions, n=11, N0=38, max_iter=300, tol=1e-6, out=None, verbose=True, time_limit=None,
        row_kw=None, col_kw=None, max_rows_add=1200, max_cols_add=60, init_atoms=None, init_rows=None,
        col_stop_iter=10**9, col_stop_cov=1.0, fine_row_kw=None, checkpoint=None, meta=None, prune=2):
    t0 = time.time()
    M = RModel(s, n, sym, tbox, regions)
    if init_atoms is not None:
        for (x, y) in init_atoms:
            M.add_orbit(x, y)
    if N0 > 0:
        h0 = s / N0
        for i in range(N0 // 2 + 1):
            for j in range(N0 // 2 + 1):
                M.add_orbit(i * h0, j * h0)
    for (cx, cy, th) in (init_rows if init_rows is not None else initial_rows(s, tbox)):
        M.add_row(cx, cy, th)
    if init_rows is not None:
        for (cx, cy, th) in initial_rows(s, tbox):
            M.add_row(cx, cy, th)
    rkw = dict(delta=0.002, cstep=0.02, n_theta=91); rkw.update(row_kw or {})
    ckw = dict(grid=0.005); ckw.update(col_kw or {})
    hist = []
    if verbose:
        print(f"[s={s} n={n} sym={sym.kind} box={tbox.describe()} regions={[(R.name, R.k, len(R.boxes)) for R in regions]}] "
              f"init orbits={len(M.orbits)} rows={len(M.rows)}", flush=True)
    nr = nc = 0
    for it in range(max_iter):
        obj = M.solve()
        npr = M.prune_rows(strikes=prune) if prune else 0
        wp = M.wpts()
        ro = RRowOracle(s, M.P, wp, tbox, M, **rkw)
        viol = ro.search(tol=tol)
        nr = 0
        for (cx, cy, th, m, al) in viol[:max_rows_add]:
            nr += M.add_row(cx, cy, th)
        co = ColOracle(s, sym, M.packing_images())
        over, maxcov = co.search(thresh=1.0 + tol, **ckw)
        nc = 0
        cols_on = (it < col_stop_iter) and (maxcov >= col_stop_cov)
        if cols_on:
            for (x, y, c) in over[:max_cols_add]:
                nc += M.add_orbit(x, y)
        minmass = viol[0][3] / viol[0][4] if viol else 1.0
        # region-cut slack in the dual (fractional packing): x(R) vs k(R)
        xR = region_loads(M)
        if nr == 0 and not cols_on and fine_row_kw:
            rof = RRowOracle(s, M.P, wp, tbox, M, **fine_row_kw)
            violf = rof.search(tol=tol)
            for (cx, cy, th, m, al) in violf[:max_rows_add]:
                nr += M.add_row(cx, cy, th)
            if violf:
                minmass = min(minmass, violf[0][3] / violf[0][4])
            if verbose:
                print(f"    fine row search: minmass={violf[0][3]/violf[0][4] if violf else 1.0:.6f} +rows={nr}", flush=True)
        if checkpoint:
            save_state(M, checkpoint, dict(it=it, obj=obj, minmass=float(minmass), maxcov=float(maxcov), lam=M.lam.tolist()))
        hist.append(dict(it=it, obj=obj, mu_total=float(obj - np.dot(M.lam, [R.k for R in regions])), lam=M.lam.tolist(), xR=xR,
                         rows=len(M.rows), orbits=len(M.orbits), atoms_nz=int((wp > 1e-9).sum()),
                         minmass=float(minmass), maxcov=float(maxcov), added_rows=nr, added_cols=nc, t=time.time() - t0))
        if verbose:
            print(f"  it {it:3d} tau={obj:.6f} mu={hist[-1]['mu_total']:.4f} lam={np.round(M.lam,4).tolist()} xR={np.round(xR,3).tolist()} "
                  f"rows={len(M.rows)} orbs={len(M.orbits)} minmass={minmass:.6f} maxcov={maxcov:.6f} +rows={nr} -rows={npr} +cols={nc} t={time.time()-t0:.0f}s", flush=True)
        if nr == 0 and nc == 0:
            break
        if time_limit and time.time() - t0 > time_limit:
            print("  time limit", flush=True); break
    obj = M.solve()
    wp = M.wpts()
    res = dict(s=s, n=n, sym=sym.kind, theta_box=tbox.ivs_deg, pieces=[[lo / DEG, hi / DEG, al] for lo, hi, al in tbox.pieces],
               regions=[dict(name=R.name, k=R.k, boxes=R.boxes.tolist(), lam=float(M.lam[r])) for r, R in enumerate(regions)],
               tau=obj, mu_total=float(obj - np.dot(M.lam, [R.k for R in regions])), nu=float(np.dot(M.y, M.row_alpha)),
               xR=region_loads(M), eps_geo=EPS_GEO, converged=bool(nr == 0 and nc == 0),
               minmass=float(hist[-1]["minmass"]) if hist else None, maxcov=float(hist[-1]["maxcov"]) if hist else None,
               n_rows=len(M.rows), n_orbits=len(M.orbits), history=hist, time=time.time() - t0)
    if meta: res.update(meta)
    res["atoms"] = [dict(rep=[float(o["rep"][0]), float(o["rep"][1])], m=int(len(o["pts"])), w=float(M.w[k]))
                    for k, o in enumerate(M.orbits) if M.w[k] > 1e-10]
    res["packing"] = [dict(cx=M.rows[r][0], cy=M.rows[r][1], theta=M.rows[r][2], y=float(M.y[r]), alpha=M.row_alpha[r])
                      for r in range(len(M.rows)) if M.y[r] > 1e-10]
    if out:
        with open(out, "w") as f:
            json.dump(res, f, indent=1)
    if verbose:
        print(f"DONE s={s} tau={obj:.6f} mu={res['mu_total']:.4f} lam={np.round(M.lam,4).tolist()} nu={res['nu']:.6f} conv={res['converged']} "
              f"minmass={res['minmass']:.6f} maxcov={res['maxcov']:.6f} rows={len(M.rows)} orbits={len(M.orbits)} "
              f"time={time.time()-t0:.0f}s", flush=True)
    return res, M


def region_loads(M):
    """x(R) = total dual weight (over all C4 images) of rows with placement in R"""
    out = []
    for R in M.regions:
        tot = 0.0
        for r, yv in enumerate(M.y):
            if yv > 1e-12 and R.contains(*M.rows[r]):
                tot += yv       # y is the orbit weight (= sum over the 4 images, each y/4, all in the symmetric R)
        out.append(float(tot))
    return out


def load_regions(path, s):
    J = json.load(open(path))
    return [Region(r["name"], r["k"], r["boxes"], s, sym4=r.get("sym4", True)) for r in J]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--s", type=float, required=True)
    ap.add_argument("--n", type=int, default=11)
    ap.add_argument("--theta_box", type=str, required=True)
    ap.add_argument("--regions", type=str, required=True)
    ap.add_argument("--sym", type=str, default="C4", choices=["C4"])
    ap.add_argument("--N0", type=int, default=38)
    ap.add_argument("--out", type=str, default=None)
    ap.add_argument("--max_iter", type=int, default=300)
    ap.add_argument("--n_theta", type=int, default=91)
    ap.add_argument("--cstep", type=float, default=0.02)
    ap.add_argument("--time_limit", type=float, default=None)
    ap.add_argument("--warm", type=str, default=None)
    ap.add_argument("--state", type=str, default=None)
    ap.add_argument("--col_stop_iter", type=int, default=10**9)
    ap.add_argument("--max_cols_add", type=int, default=60)
    ap.add_argument("--max_rows_add", type=int, default=1200)
    ap.add_argument("--fine", action="store_true")
    ap.add_argument("--tag", type=str, default="")
    ap.add_argument("--prune", type=int, default=2)
    a = ap.parse_args()
    ivs = ThetaBox.parse(a.theta_box, None)
    sym = Sym("C4", a.s)
    tbox = ThetaBox(ivs, "C4")
    regions = load_regions(a.regions, a.s)
    out = a.out or f"results/reg_s{a.s:.4f}.json"
    ia = ir = None
    if a.warm:
        ia, ir = warm_from(a.warm, a.s, sym)
    if a.state:
        ia, ir = load_state(a.state)
    run(a.s, tbox, sym, regions, n=a.n, N0=a.N0, max_iter=a.max_iter, out=out, time_limit=a.time_limit,
        row_kw=dict(n_theta=a.n_theta, cstep=a.cstep), init_atoms=ia, init_rows=ir,
        col_stop_iter=a.col_stop_iter, max_cols_add=a.max_cols_add, max_rows_add=a.max_rows_add,
        fine_row_kw=(dict(n_theta=361, cstep=0.005, delta=0.001) if a.fine else None),
        checkpoint=out.replace(".json", "_state.json"), meta=dict(tag=a.tag, args=vars(a)), prune=a.prune)
