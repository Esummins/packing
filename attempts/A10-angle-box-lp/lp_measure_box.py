"""
A10-angle-box-lp: orientation-restricted measure LP  (modified COPY of A07's lp_measure2.py).

    tau*_B(s) = min mu([0,s]^2)  s.t.  mu(Q) >= alpha(theta(Q))  for every closed unit square Q in [0,s]^2
                                        whose orientation theta lies in the angle box Theta_B.

Theta_B is a union of closed intervals (degrees, inside [0,90], 90 == 0), given as --theta_box "0-10,30.18-50.18"
(a single number = degenerate interval = one orientation).  --alpha gives one class weight per interval
(default 1).  Only the ROWS (placements) and the row-generation search are restricted; atoms/columns are free.

Symmetry (WLOG by averaging the measure over the group; rotations by 90 deg map orientation class theta to
itself, reflections map theta -> 90-theta):
  * D4 (8-point orbits, theta in [0,45], centres in the quadrant [s/2,s]^2)  is only valid if Theta_B is closed
    under theta -> 90-theta (then the box is folded onto [0,45]);
  * C4 (4-point orbits = rotations only, theta in [0,90), centres in the quadrant [s/2,s]^2)  is valid for any box.
  --sym auto picks D4 iff the box is reflection-closed (and the alphas match), else C4.

Everything else (row oracle, column oracle, HiGHS incremental LP, checkpoints, warm starts) is A07's.
Row RHS = alpha of the interval containing theta (max over intervals if several).  Rows whose theta is outside
Theta_B or whose centre is not admissible for this s are silently rejected by Model.add_row (so warm-start rows,
extra rows and neighbourhood rows are always restricted).

Usage: python lp_measure_box.py --s 3.85 --theta_box "0-5,35.18-45.18" --out results/x.json [--warm A07result.json]
"""
import argparse, json, math, time, os
import numpy as np
import highspy

EPS_GEO = 1e-4      # squares are shrunk by this margin in the LP rows (see verifier)
DEG = math.pi / 180.0
THETA_STAR_DEG = 40.18193729032971646523   # Trump packing tilt (A03)


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


def norm_theta(th):
    """orientation class representative in [0, pi/2)"""
    t = th % (math.pi / 2)
    if t > math.pi / 2 - 1e-9:
        t = 0.0
    return t


# ------------------------------------------------------------------ angle box
class ThetaBox:
    """pieces = list of (lo, hi, alpha) in radians on the row domain of the chosen symmetry."""

    @staticmethod
    def parse(spec, alphas=None):
        ivs = []
        for k, tok in enumerate(spec.split(",")):
            tok = tok.strip()
            if not tok:
                continue
            if "-" in tok:
                a, b = tok.split("-", 1)
                lo, hi = float(a), float(b)
            else:
                lo = hi = float(tok)
            if not (0 - 1e-9 <= lo <= hi <= 90 + 1e-9):
                raise ValueError(f"interval {tok} must lie in [0,90]")
            al = 1.0 if alphas is None else float(alphas[k])
            ivs.append((max(lo, 0.0), min(hi, 90.0), al))
        return ivs

    @staticmethod
    def merged(ivs, tol=1e-9):
        """merge overlapping/adjacent intervals with equal alpha (list of (lo,hi,alpha) in degrees)"""
        ivs = sorted(ivs)
        out = []
        for lo, hi, al in ivs:
            if out and lo <= out[-1][1] + tol and abs(al - out[-1][2]) < 1e-12:
                out[-1] = (out[-1][0], max(out[-1][1], hi), al)
            else:
                out.append((lo, hi, al))
        return out

    @staticmethod
    def reflected(ivs):
        out = []
        for lo, hi, al in ivs:
            lo2, hi2 = 90 - hi, 90 - lo
            if lo2 >= 90 - 1e-9:          # the point 90 == 0
                lo2 = hi2 = 0.0
            out.append((lo2, hi2, al))
        return out

    @staticmethod
    def is_reflection_closed(ivs, tol=1e-9):
        a = ThetaBox.merged(ivs); b = ThetaBox.merged(ThetaBox.reflected(ivs))
        if len(a) != len(b):
            return False
        return all(abs(x[0] - y[0]) < tol and abs(x[1] - y[1]) < tol and abs(x[2] - y[2]) < 1e-12 for x, y in zip(a, b))

    def __init__(self, ivs_deg, sym):
        self.sym = sym
        self.ivs_deg = ivs_deg
        if sym == "D4":
            pieces = []
            for lo, hi, al in ivs_deg + ThetaBox.reflected(ivs_deg):
                l2, h2 = max(lo, 0.0), min(hi, 45.0)
                if l2 <= h2 + 1e-12:
                    pieces.append((l2, min(h2, 45.0), al))
            self.dom_hi = math.pi / 4
        else:
            pieces = list(ivs_deg)
            self.dom_hi = math.pi / 2
        pieces = ThetaBox.merged(pieces)
        self.pieces = [(lo * DEG, hi * DEG, al) for (lo, hi, al) in pieces]

    def fold(self, th):
        t = norm_theta(th)
        if self.sym == "D4":
            t = min(t, math.pi / 2 - t)
        return t

    def piece_of(self, th, tol=1e-9):
        """index of the piece containing theta (largest alpha if several), or -1"""
        t = self.fold(th)
        best, ba = -1, -1.0
        for k, (lo, hi, al) in enumerate(self.pieces):
            if lo - tol <= t <= hi + tol and al > ba:
                best, ba = k, al
        return best

    def alpha(self, th):
        k = self.piece_of(th)
        return self.pieces[k][2] if k >= 0 else None

    def contains(self, th):
        return self.piece_of(th) >= 0

    def clamp(self, th, k):
        lo, hi, _ = self.pieces[k]
        return min(max(th, lo), hi)

    def theta_grid(self, step):
        """(theta, piece index) list: each piece sampled with spacing <= step, endpoints included"""
        out = []
        for k, (lo, hi, al) in enumerate(self.pieces):
            if hi - lo < 1e-12:
                out.append((lo, k))
            else:
                n = max(1, int(math.ceil((hi - lo) / step - 1e-9)))
                for t in np.linspace(lo, hi, n + 1):
                    out.append((float(t), k))
        return out

    def describe(self):
        return ", ".join(f"[{lo/DEG:.4g},{hi/DEG:.4g}]x{al:g}" for lo, hi, al in self.pieces)


# ------------------------------------------------------------------ symmetry
class Sym:
    def __init__(self, kind, s):
        assert kind in ("D4", "C4")
        self.kind, self.s = kind, s
        self.n_img = 8 if kind == "D4" else 4

    def point_images(self, x, y):
        s = self.s
        rot = [(x, y), (s - y, x), (s - x, s - y), (y, s - x)]
        if self.kind == "C4":
            return rot
        return rot + [(s - a, b) for (a, b) in rot]

    def placement_images(self, cx, cy, th):
        s = self.s
        out = []
        x, y, t = cx, cy, th
        for k in range(4):
            out.append((x, y, t))
            if self.kind == "D4":
                out.append((s - x, y, (math.pi / 2 - t) % (math.pi / 2)))
            x, y = s - y, x
        return out

    def canon_point(self, x, y):
        s = self.s
        if self.kind == "D4":
            x = min(x, s - x); y = min(y, s - y)
            if x > y:
                x, y = y, x
            return x, y
        # C4: the image in the quadrant [s/2,s]^2 (lexicographic max among images, deterministic on boundaries)
        best = None
        for (a, b) in self.point_images(x, y):
            if a >= s / 2 - 1e-9 and b >= s / 2 - 1e-9:
                key = (round(a, 9), round(b, 9))
                if best is None or key > best[0]:
                    best = (key, (a, b))
        return best[1]

    def fund_grid(self, grid):
        """sample of the fundamental region for the column oracle"""
        s = self.s
        xs = np.arange(s / 2, s + 1e-9, grid)
        X, Y = np.meshgrid(xs, xs, indexing="ij")
        if self.kind == "D4":
            m = X <= Y + 1e-12
            return np.stack([X[m], Y[m]], 1)
        return np.stack([X.ravel(), Y.ravel()], 1)

    def in_fund(self, pts):
        s = self.s
        m = (pts[:, 0] >= s / 2 - 1e-9) & (pts[:, 1] >= s / 2 - 1e-9)
        if self.kind == "D4":
            m &= pts[:, 1] >= pts[:, 0] - 1e-9
        return m


# ------------------------------------------------------------------ model
class Model:
    def __init__(self, s, n, sym, tbox, verbose=False):
        self.s, self.n = s, n
        self.sym, self.tbox = sym, tbox
        self.h = highspy.Highs()
        self.h.setOptionValue("output_flag", False)
        self.h.setOptionValue("threads", 1)
        self.orbits = []           # list of dict(rep=(x,y), pts=np.array (m,2))
        self.P = np.zeros((0, 2))  # all atom points
        self.P_orb = np.zeros(0, dtype=int)
        self.rows = []             # (cx,cy,theta)
        self.row_alpha = []
        self.rowkeys = set()
        self.orbkeys = set()
        self.w = None; self.y = None; self.obj = None
        self.n_rejected = 0

    # --- atoms
    def add_orbit(self, x, y, tol=1e-7):
        x, y = self.sym.canon_point(x, y)
        key = (round(x / tol), round(y / tol))
        if key in self.orbkeys:
            return False
        pts = []
        for p in self.sym.point_images(x, y):
            if all(abs(p[0] - q[0]) > 1e-12 or abs(p[1] - q[1]) > 1e-12 for q in pts):
                pts.append(p)
        pts = np.array(pts)
        m = len(pts)
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
        if len(idx) == 0:
            return False
        key = hash((idx.tobytes(), cnt[idx].tobytes(), round(al, 12)))
        if key in self.rowkeys:
            return False
        self.rowkeys.add(key)
        self.h.addRow(al, highspy.kHighsInf, len(idx), idx.astype(np.int32), cnt[idx].astype(float))
        self.rows.append((float(cx), float(cy), float(th)))
        self.row_alpha.append(al)
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
        """symmetrised fractional packing: list of (cx,cy,theta,weight)"""
        out = []
        k = self.sym.n_img
        for r, yv in enumerate(self.y):
            if yv > ymin:
                cx, cy, th = self.rows[r]
                for (a, b, t) in self.sym.placement_images(cx, cy, th):
                    out.append((a, b, t, yv / k))
        return out


# ------------------------------------------------------------------ row oracle
class RowOracle:
    def __init__(self, s, P, w, tbox, delta=0.002, cstep=0.02, n_theta=91):
        self.s = s
        self.tbox = tbox
        nz = w > 1e-12
        self.P = P[nz]; self.w = w[nz]; self.K = len(self.w)
        self.delta, self.cstep, self.n_theta = delta, cstep, n_theta
        self.tstep = math.pi / 4 / (n_theta - 1)      # 91 -> 0.5 deg, 181 -> 0.25, 361 -> 0.125

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

    def refine(self, cx, cy, theta, piece, iters=60):
        """pattern search in (c, theta); theta stays inside its piece"""
        s = self.s
        best = self.mass(cx, cy, theta)
        step_c, step_t = self.cstep, self.tstep
        plo, phi, _ = self.tbox.pieces[piece]
        fixed_theta = (phi - plo) < 1e-12
        dirs = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1),
                (1, 1, 0), (1, -1, 0), (-1, 1, 0), (-1, -1, 0), (1, 0, 1), (-1, 0, 1), (0, 1, 1), (0, -1, 1),
                (1, 0, -1), (-1, 0, -1), (0, 1, -1), (0, -1, -1)]
        if fixed_theta:
            dirs = [d for d in dirs if d[2] == 0]
        for _ in range(iters):
            improved = False
            for dcx, dcy, dth in dirs:
                th = min(max(theta + dth * step_t, plo), phi)
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

    def search(self, tol=1e-6, max_refine=300, max_return=2000):
        """returns list of (cx, cy, theta, mass, alpha) sorted by mass/alpha (violated: mass < alpha - tol)"""
        found = []
        for th, k in self.tbox.theta_grid(self.tstep):
            al = self.tbox.pieces[k][2]
            Cc, m = self.scan_theta(th, al - tol)
            sel = np.nonzero(m < al - tol)[0]
            for j in sel:
                found.append((Cc[j, 0], Cc[j, 1], th, m[j], al, k))
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


# ------------------------------------------------------------------ column oracle
class ColOracle:
    def __init__(self, s, sym, images):
        self.s = s
        self.sym = sym
        self.pl = np.array([(a, b, t, w) for (a, b, t, w) in images if w > 1e-12]).reshape(-1, 4)   # (R,4)
        self.cos = np.cos(self.pl[:, 2]); self.sin = np.sin(self.pl[:, 2])
        self.half = 0.5 - EPS_GEO

    def coverage(self, pts):
        out = np.zeros(len(pts))
        R = len(self.pl)
        if R == 0:
            return out
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
        s = self.s
        pl = self.pl
        if len(pl) == 0:
            return np.zeros((0, 2))
        corn = np.array([[-1, -1], [1, -1], [1, 1], [-1, 1]]) * self.half
        cs = np.stack([np.stack([self.cos, -self.sin], 1), np.stack([self.sin, self.cos], 1)], 1)
        V = np.einsum("rij,kj->rki", cs, corn) + pl[:, None, :2]
        E0 = V; E1 = np.roll(V, -1, axis=1)
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
        pts = np.vstack([pts, V.reshape(-1, 2)])
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
        pts = self.sym.fund_grid(grid)
        cov = self.coverage(pts)
        av = self.arrangement_vertices()
        if len(av):
            av = av[self.sym.in_fund(av)]
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
        for k in order[max_refine:2000]:
            if cov[k] <= thresh + 1e-9:
                break
            key = (round(pts[k, 0], 5), round(pts[k, 1], 5))
            if key not in seen:
                seen.add(key); out.append((pts[k, 0], pts[k, 1], cov[k]))
        out.sort(key=lambda t: -t[2])
        return out, (cov.max() if len(cov) else 0.0)


def save_state(M, path, extra=None):
    st = dict(s=M.s, n=M.n, eps_geo=EPS_GEO, sym=M.sym.kind, theta_box=M.tbox.ivs_deg,
              tau=float(M.obj) if M.obj is not None else None,
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
def initial_rows(s, tbox, cstep=0.1):
    out = []
    for th, k in tbox.theta_grid(5 * DEG):
        lo, hi = centre_range(s, th)
        n = int(math.ceil((hi - lo) / cstep))
        xs = np.linspace(lo, hi, n + 1)
        xs = xs[xs >= s / 2 - 1e-12]
        for x in xs:
            for y in xs:
                out.append((x, y, th))
    return out


def run(s, tbox, sym, n=11, N0=38, max_iter=300, tol=1e-6, out=None, verbose=True, time_limit=None,
        row_kw=None, col_kw=None, max_rows_add=1200, max_cols_add=60, init_atoms=None, init_rows=None,
        col_stop_iter=10**9, col_stop_cov=1.0, fine_row_kw=None, checkpoint=None, neigh_rows=0, neigh_d=0.003,
        extra_rows=None, meta=None):
    t0 = time.time()
    M = Model(s, n, sym, tbox)
    if init_atoms is not None:
        for (x, y) in init_atoms:
            M.add_orbit(x, y)
    if N0 > 0:      # coarse grid of atoms (always, so that the LP is bounded and the restricted optimum is reachable)
        h0 = s / N0
        for i in range(N0 // 2 + 1):
            for j in range(N0 // 2 + 1):
                M.add_orbit(i * h0, j * h0)
    for (cx, cy, th) in (init_rows if init_rows is not None else initial_rows(s, tbox)):
        M.add_row(cx, cy, th)
    if init_rows is not None:
        for (cx, cy, th) in initial_rows(s, tbox):
            M.add_row(cx, cy, th)
    if extra_rows:
        for (cx, cy, th) in extra_rows:
            M.add_row(cx, cy, th)
    rkw = dict(delta=0.002, cstep=0.02, n_theta=91); rkw.update(row_kw or {})
    ckw = dict(grid=0.005); ckw.update(col_kw or {})
    hist = []
    if verbose:
        print(f"[s={s} n={n} sym={sym.kind} box={tbox.describe()}] init orbits={len(M.orbits)} points={len(M.P)} "
              f"rows={len(M.rows)} (rejected {M.n_rejected})", flush=True)
    nr = nc = 0
    for it in range(max_iter):
        obj = M.solve()
        wp = M.wpts()
        ro = RowOracle(s, M.P, wp, tbox, **rkw)
        viol = ro.search(tol=tol)
        nr = 0
        for (cx, cy, th, m, al) in viol[:max_rows_add]:
            nr += M.add_row(cx, cy, th)
        for (cx, cy, th, m, al) in viol[:neigh_rows]:
            k = tbox.piece_of(th)
            for dcx in (-1, 0, 1):
                for dcy in (-1, 0, 1):
                    for dth in (-1, 0, 1):
                        if dcx == dcy == dth == 0:
                            continue
                        th2 = tbox.clamp(th + dth * neigh_d, k)
                        lo, hi = centre_range(s, th2)
                        nr += M.add_row(min(max(cx + dcx * neigh_d, lo), hi), min(max(cy + dcy * neigh_d, lo), hi), th2)
        co = ColOracle(s, sym, M.packing_images())
        over, maxcov = co.search(thresh=1.0 + tol, **ckw)
        nc = 0
        cols_on = (it < col_stop_iter) and (maxcov >= col_stop_cov)
        if cols_on:
            for (x, y, c) in over[:max_cols_add]:
                nc += M.add_orbit(x, y)
        minmass = viol[0][3] / viol[0][4] if viol else 1.0
        if nr == 0 and not cols_on and fine_row_kw:
            rof = RowOracle(s, M.P, wp, tbox, **fine_row_kw)
            violf = rof.search(tol=tol)
            for (cx, cy, th, m, al) in violf[:max_rows_add]:
                nr += M.add_row(cx, cy, th)
            if violf:
                minmass = min(minmass, violf[0][3] / violf[0][4])
            if verbose:
                print(f"    fine row search: minmass={violf[0][3]/violf[0][4] if violf else 1.0:.6f} +rows={nr}", flush=True)
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
    res = dict(s=s, n=n, sym=sym.kind, theta_box=tbox.ivs_deg, pieces=[[lo / DEG, hi / DEG, al] for lo, hi, al in tbox.pieces],
               tau=obj, nu=float(np.dot(M.y, M.row_alpha)), eps_geo=EPS_GEO, converged=bool(nr == 0 and nc == 0),
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
        print(f"DONE s={s} n={n} sym={sym.kind} tau={obj:.6f} nu={res['nu']:.6f} conv={res['converged']} "
              f"minmass={res['minmass']:.6f} maxcov={res['maxcov']:.6f} rows={len(M.rows)} "
              f"orbits={len(M.orbits)} atoms_nz={len(res['atoms'])} packing_support={len(res['packing'])} "
              f"time={time.time()-t0:.0f}s", flush=True)
    return res, M


def warm_from(path, s, sym):
    """atoms and rows from a previous result json (A07 D4 format or ours); rows are expanded to all
    D4 images so that a D4 result can seed a C4 run (add_row filters theta and admissibility)."""
    wr = json.load(open(path))
    ia = []
    d4 = Sym("D4", wr.get("s", s))
    for x in wr["atoms"]:
        rx, ry = x["rep"]
        # re-express in this s: keep positions relative to the nearest wall structure is not attempted;
        # atoms are just re-used as positions (they are re-optimised by column generation anyway)
        for (a, b) in d4.point_images(rx, ry):
            if 0 <= a <= s and 0 <= b <= s:
                ia.append((a, b))
    ir = []
    for p in wr["packing"]:
        for (a, b, t) in d4.placement_images(p["cx"], p["cy"], p["theta"]):
            ir.append((a, b, t))
    return ia, ir


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--s", type=float, required=True)
    ap.add_argument("--n", type=int, default=11)
    ap.add_argument("--theta_box", type=str, required=True, help='degrees, e.g. "0-5,35.18-45.18" or "0,45"')
    ap.add_argument("--alpha", type=str, default=None, help="class weight per interval, e.g. 1,1.1")
    ap.add_argument("--sym", type=str, default="auto", choices=["auto", "D4", "C4"])
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
    ap.add_argument("--max_rows_add", type=int, default=1200)
    ap.add_argument("--fine", action="store_true", help="final fine row search (n_theta=361, cstep=0.005)")
    ap.add_argument("--neigh_rows", type=int, default=0)
    ap.add_argument("--neigh_d", type=float, default=0.003)
    ap.add_argument("--extra_rows", type=str, default=None)
    ap.add_argument("--tag", type=str, default="")
    a = ap.parse_args()
    ivs = ThetaBox.parse(a.theta_box, a.alpha.split(",") if a.alpha else None)
    closed = ThetaBox.is_reflection_closed(ivs)
    symk = a.sym if a.sym != "auto" else ("D4" if closed else "C4")
    if symk == "D4" and not closed:
        raise SystemExit("D4 symmetry requested but the box is not closed under theta -> 90-theta")
    sym = Sym(symk, a.s)
    tbox = ThetaBox(ivs, symk)
    out = a.out or f"results/box_s{a.s:.4f}_{a.theta_box.replace(',', '_')}.json"
    ia = ir = None
    if a.warm:
        ia, ir = warm_from(a.warm, a.s, sym)
    if a.state:
        ia, ir = load_state(a.state)
    run(a.s, tbox, sym, n=a.n, N0=a.N0, max_iter=a.max_iter, out=out, time_limit=a.time_limit,
        row_kw=dict(n_theta=a.n_theta, cstep=a.cstep), init_atoms=ia, init_rows=ir,
        col_stop_iter=a.col_stop_iter, col_stop_cov=a.col_stop_cov, max_cols_add=a.max_cols_add, max_rows_add=a.max_rows_add,
        fine_row_kw=(dict(n_theta=361, cstep=0.005, delta=0.001) if a.fine else None),
        checkpoint=out.replace(".json", "_state.json"), neigh_rows=a.neigh_rows, neigh_d=a.neigh_d,
        extra_rows=(json.load(open(a.extra_rows)) if a.extra_rows else None),
        meta=dict(tag=a.tag, alpha=a.alpha, args=vars(a)))
