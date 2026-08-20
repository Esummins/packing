"""
A14 copy of A13 caselp.py (+ checkpoint passthrough in solve_node); imports the A14 lpbox.

A13-case-lp-bnb: node LP of the case-LP branch-and-bound.

A NODE is a set of hypotheses H about an (unknown) packing P of n pairwise-disjoint closed unit squares in [0,s]^2:
  * cores   : parameter boxes B = [x0,x1]x[y0,y1] (centre) x [th0,th1] (degrees) with the hypothesis "some square
              Q0 of P has (centre, orientation) in B".  K(B) = a rational SQUARE provably contained in EVERY Q in B
              (centre = box midpoint k, orientation theta_m from t_m = (t0+t1)/2, half-side a = (1/2 - hd)/(1 + (t1-t0)),
              hd >= half diagonal of the centre box, t = tan(theta/2) bounds rounded outward).  Every other square of
              P is disjoint from Q0 and hence from K(B).
  * nofams  : families F = zone [x0,x1]x[y0,y1] x list of theta intervals with the hypothesis "NO square of P has
              (centre, orientation) in F".
  budget = n - #cores  (the cores' squares are accounted for; the remaining squares each have mu-mass >= 1).
NODE LP:  min mu(total)  s.t.  mu(Q) >= 1  for every admissible closed unit square Q that is NOT provably in a
          NO-family and NOT provably meeting a core.   tau < budget  ==>  no packing satisfies H  (node DEAD).
Conservativeness of the float filter: a row is DROPPED only if it is inside a NO-family by margin EPS_ZONE (centre)
/ EPS_TH (deg), or penetrates a core by depth > EPS_CORE on every separating axis (SAT).  Rows are never dropped
wrongly (dropping fewer rows only raises tau); the rigorous verifier (verify_case.py) exempts a box only if it is
provably (closed) inside a family / meeting a core, and the margins guarantee that placements near the boundary of
the exempt region are covered by mu.
"""
import json, math, os, sys, time
from fractions import Fraction as Fr
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lpbox
from lpbox import DEG, ThetaBox, Sym, centre_range

EPS_CORE = 2e-3      # LP drops a row only if it penetrates the core by more than this on all 4 axes
EPS_ZONE = 2e-3      # LP drops a row only if its centre is inside the NO-zone by this margin
EPS_TH = 0.3         # ... and its orientation inside the theta interval(s) by this margin (degrees; > fine oracle step 0.25)
TDEN = 1 << 24       # rational rounding grid for t = tan(theta/2)
XDEN = 10 ** 9       # rational rounding grid for centre coordinates


# ------------------------------------------------------------------ rational helpers
def t_of_deg(th):
    return math.tan(math.radians(th) / 2)


def t_lo(th):   # rational t <= tan(th/2)
    return Fr(math.floor(t_of_deg(th) * TDEN) - 1, TDEN) if th > 0 else Fr(0)


def t_hi(th):   # rational t >= tan(th/2)
    return Fr(math.ceil(t_of_deg(th) * TDEN) + 1, TDEN) if th < 90 else Fr(1)


def q(x):       # float -> nearby rational (exact decimal at 1e-9)
    return Fr(round(x * XDEN), XDEN)


def q_up(x):
    return Fr(math.ceil(x * XDEN) + 1, XDEN)


def cos_sin_t(t):
    tt = t * t
    return (1 - tt) / (1 + tt), 2 * t / (1 + tt)


# ------------------------------------------------------------------ hypotheses
class Box:
    """parameter box: centre in [x0,x1]x[y0,y1], orientation in [th0,th1] degrees (0 <= th0 <= th1 <= 90)."""

    def __init__(self, x0, x1, y0, y1, th0, th1):
        self.x0, self.x1, self.y0, self.y1, self.th0, self.th1 = float(x0), float(x1), float(y0), float(y1), float(th0), float(th1)

    def to_json(self):
        return dict(x0=self.x0, x1=self.x1, y0=self.y0, y1=self.y1, th0=self.th0, th1=self.th1)

    @staticmethod
    def from_json(d):
        return Box(d["x0"], d["x1"], d["y0"], d["y1"], d["th0"], d["th1"])

    def key(self):
        return (round(self.x0, 6), round(self.x1, 6), round(self.y0, 6), round(self.y1, 6), round(self.th0, 4), round(self.th1, 4))

    def __repr__(self):
        return f"B([{self.x0:.3f},{self.x1:.3f}]x[{self.y0:.3f},{self.y1:.3f}]x[{self.th0:.2f},{self.th1:.2f}]deg)"

    def vacuous(self, s):
        """True if certainly no admissible placement: w(theta)/2 > x1 (or y1) or s - w/2 < x0 for all theta in the box.
        w = cos+sin is unimodal in theta (max at 45): min over the interval is at an endpoint."""
        w0 = math.cos(math.radians(self.th0)) + math.sin(math.radians(self.th0))
        w1 = math.cos(math.radians(self.th1)) + math.sin(math.radians(self.th1))
        wmin = min(w0, w1)
        return (self.x1 < wmin / 2 - 1e-12 or self.y1 < wmin / 2 - 1e-12 or
                self.x0 > s - wmin / 2 + 1e-12 or self.y0 > s - wmin / 2 + 1e-12)

    def core(self):
        """rational core square (kx, ky, t_m, a) with cos/sin of theta_m rational; None if empty (a <= 0)."""
        t0, t1 = t_lo(self.th0), t_hi(self.th1)
        tm = (t0 + t1) / 2
        kx = (q(self.x0) + q(self.x1)) / 2
        ky = (q(self.y0) + q(self.y1)) / 2
        hd = q_up(0.5 * math.hypot(self.x1 - self.x0, self.y1 - self.y0))
        a = (Fr(1, 2) - hd) / (1 + (t1 - t0))
        if a <= 0:
            return None
        return Core(kx, ky, tm, a, self)

    def split(self, tscale=1.0):
        """bisect along the widest dimension (theta width measured in t-units * tscale... here degrees/60 ~ t)"""
        wx, wy = self.x1 - self.x0, self.y1 - self.y0
        wt = (t_of_deg(self.th1) - t_of_deg(self.th0)) * tscale
        if wx >= wy and wx >= wt:
            m = 0.5 * (self.x0 + self.x1)
            return [Box(self.x0, m, self.y0, self.y1, self.th0, self.th1), Box(m, self.x1, self.y0, self.y1, self.th0, self.th1)]
        if wy >= wt:
            m = 0.5 * (self.y0 + self.y1)
            return [Box(self.x0, self.x1, self.y0, m, self.th0, self.th1), Box(self.x0, self.x1, m, self.y1, self.th0, self.th1)]
        m = 0.5 * (self.th0 + self.th1)
        return [Box(self.x0, self.x1, self.y0, self.y1, self.th0, m), Box(self.x0, self.x1, self.y0, self.y1, m, self.th1)]

    def contains(self, cx, cy, th_deg):
        return self.x0 <= cx <= self.x1 and self.y0 <= cy <= self.y1 and self.th0 <= th_deg <= self.th1


class Core:
    def __init__(self, kx, ky, tm, a, box=None):
        self.kx, self.ky, self.tm, self.a = kx, ky, tm, a       # Fractions
        self.box = box
        c, s = cos_sin_t(tm)
        self.cm, self.sm = c, s
        # floats for the LP
        self.fk = np.array([float(kx), float(ky)])
        self.fc, self.fs, self.fa = float(c), float(s), float(a)
        self.fth = 2 * math.atan(float(tm))

    def to_json(self):
        return dict(kx=str(self.kx), ky=str(self.ky), tm=str(self.tm), a=str(self.a),
                    box=self.box.to_json() if self.box else None,
                    float=dict(kx=float(self.kx), ky=float(self.ky), theta_deg=math.degrees(self.fth), a=float(self.a)))

    def vertices(self):
        k = self.fk
        e1 = np.array([self.fc, self.fs]); e2 = np.array([-self.fs, self.fc])
        return [k + self.fa * (i * e1 + j * e2) for i, j in ((-1, -1), (1, -1), (1, 1), (-1, 1))]

    def depth_many(self, C, theta):
        """min SAT overlap depth (over the 4 axes) between Q(c, theta) and the core, for centres C (m,2).
        depth > 0 <=> the closed squares intersect with positive overlap on every axis."""
        c, s = math.cos(theta), math.sin(theta)
        g = abs(c * self.fc + s * self.fs) + abs(-s * self.fc + c * self.fs)   # |cos(th-thm)| + |sin(th-thm)|
        d = C - self.fk[None, :]
        pe1 = np.abs(d[:, 0] * self.fc + d[:, 1] * self.fs)
        pe2 = np.abs(-d[:, 0] * self.fs + d[:, 1] * self.fc)
        pf1 = np.abs(d[:, 0] * c + d[:, 1] * s)
        pf2 = np.abs(-d[:, 0] * s + d[:, 1] * c)
        de = np.minimum(self.fa + 0.5 * g - pe1, self.fa + 0.5 * g - pe2)
        df = np.minimum(0.5 + self.fa * g - pf1, 0.5 + self.fa * g - pf2)
        return np.minimum(de, df)


class NoFam:
    """zone [x0,x1]x[y0,y1] x union of theta intervals (degrees, in [0,90], 90 == 0)"""

    s_hi = 1e9     # set by Hyp to s - 0.5 (upper domain boundary of admissible centres)

    def __init__(self, x0, x1, y0, y1, thetas):
        self.x0, self.x1, self.y0, self.y1 = float(x0), float(x1), float(y0), float(y1)
        self.thetas = [(float(a), float(b)) for a, b in thetas]

    def to_json(self):
        return dict(x0=self.x0, x1=self.x1, y0=self.y0, y1=self.y1, thetas=self.thetas)

    @staticmethod
    def from_json(d):
        return NoFam(d["x0"], d["x1"], d["y0"], d["y1"], d["thetas"])

    def __repr__(self):
        return f"NO([{self.x0:.3f},{self.x1:.3f}]x[{self.y0:.3f},{self.y1:.3f}]x{self.thetas})"

    def inside_many(self, C, th_deg, eps=EPS_ZONE, eps_th=EPS_TH):
        """rows to drop: centre inside the zone and theta inside a theta-interval, both by a safety margin EXCEPT at
        the domain boundary (theta = 0 or 90, centre coordinate 0.5 or s-0.5 are closed ends: no margin there)"""
        def lo_m(a):   # margin at an interval start (none at theta = 0)
            return a + (eps_th if a > 1e-9 else -1e-9)
        def hi_m(b):
            return b - (eps_th if b < 90 - 1e-9 else -1e-9)
        okth = any(lo_m(a) <= th_deg <= hi_m(b) for a, b in self.thetas)
        if not okth:
            # 90 == 0 wrap: theta near 90 also counts as near 0
            okth = any(lo_m(a) <= th_deg - 90 <= hi_m(b) for a, b in self.thetas)
        if not okth:
            return np.zeros(len(C), dtype=bool)
        x0 = self.x0 + (eps if self.x0 > 0.5 + 1e-9 else -1e-9)
        y0 = self.y0 + (eps if self.y0 > 0.5 + 1e-9 else -1e-9)
        x1 = self.x1 - (eps if self.x1 < self.s_hi - 1e-9 else -1e-9)
        y1 = self.y1 - (eps if self.y1 < self.s_hi - 1e-9 else -1e-9)
        return (C[:, 0] >= x0) & (C[:, 0] <= x1) & (C[:, 1] >= y0) & (C[:, 1] <= y1)

    def contains(self, cx, cy, th_deg):
        okth = any(a <= th_deg <= b for a, b in self.thetas) or any(a <= th_deg - 90 <= b for a, b in self.thetas)
        return okth and self.x0 <= cx <= self.x1 and self.y0 <= cy <= self.y1

    def weight_in(self, packing):
        return sum(w for (cx, cy, th, w) in packing if self.contains(cx, cy, math.degrees(th) % 90))


class Hyp:
    """hypothesis set: list of core boxes (with their cores) and NO-families; provides the LP row filter."""

    def __init__(self, boxes=(), nofams=()):
        self.boxes = list(boxes)
        self.cores = [b.core() for b in self.boxes]
        assert all(c is not None for c in self.cores), "a core box is too large (empty core)"
        self.nofams = list(nofams)

    def to_json(self):
        return dict(boxes=[b.to_json() for b in self.boxes], nofams=[f.to_json() for f in self.nofams],
                    cores=[c.to_json() for c in self.cores])

    @staticmethod
    def from_json(d):
        return Hyp([Box.from_json(b) for b in d["boxes"]], [NoFam.from_json(f) for f in d["nofams"]])

    def describe(self):
        return f"{len(self.boxes)} cores {[repr(b) for b in self.boxes]} ; {len(self.nofams)} nofams {[repr(f) for f in self.nofams]}"

    def m(self):
        return len(self.boxes)

    def ok_many(self, C, theta):
        """boolean mask: rows to KEEP (not provably exempt) for centres C at orientation theta (radians)"""
        C = np.asarray(C, dtype=float).reshape(-1, 2)
        keep = np.ones(len(C), dtype=bool)
        th_deg = math.degrees(theta) % 90.0
        for f in self.nofams:
            keep &= ~f.inside_many(C, th_deg)
        for c in self.cores:
            keep &= ~(c.depth_many(C, theta) > EPS_CORE)
        return keep

    def ok(self, cx, cy, theta):
        return bool(self.ok_many(np.array([[cx, cy]]), theta)[0])

    def shell_points(self, theta, s):
        """extra row-oracle candidates in the thin KEPT shells next to the exempt regions (the arrangement-cell
        sampling of the oracle is blind to them): for each core, centres c whose Q(c,theta) meets the core with SAT depth
        d0 in {1e-5, 1e-3} (boundary of the octagon {c: depth >= d0}); for each NO-family, points along the zone edges
        offset inward by 1e-3.  Returns (m,2) array (may be empty)."""
        pts = []
        c, sn = math.cos(theta), math.sin(theta)
        for core in self.cores:
            g = abs(c * core.fc + sn * core.fs) + abs(-sn * core.fc + c * core.fs)
            axes = [(np.array([core.fc, core.fs]), core.fa + 0.5 * g), (np.array([-core.fs, core.fc]), core.fa + 0.5 * g),
                    (np.array([c, sn]), 0.5 + core.fa * g), (np.array([-sn, c]), 0.5 + core.fa * g)]
            phi = np.linspace(0, 2 * math.pi, 240, endpoint=False)
            U = np.stack([np.cos(phi), np.sin(phi)], 1)
            for d0 in (1e-5, 1e-3):
                r = np.full(len(phi), np.inf)
                for e, L in axes:
                    den = np.abs(U @ e)
                    with np.errstate(divide="ignore"):
                        r = np.minimum(r, np.where(den > 1e-12, (L - d0) / np.maximum(den, 1e-12), np.inf))
                pts.append(core.fk[None, :] + r[:, None] * U)
        th_deg = math.degrees(theta) % 90.0
        for f in self.nofams:
            if not f.inside_many(np.array([[0.5 * (f.x0 + f.x1), 0.5 * (f.y0 + f.y1)]]), th_deg)[0]:
                continue        # theta not (robustly) in the family: no shell in c
            d0 = 1e-3
            xs = np.arange(f.x0, f.x1 + 1e-9, 0.005); ys = np.arange(f.y0, f.y1 + 1e-9, 0.005)
            pts.append(np.stack([xs, np.full(len(xs), f.y0 + d0)], 1)); pts.append(np.stack([xs, np.full(len(xs), f.y1 - d0)], 1))
            pts.append(np.stack([np.full(len(ys), f.x0 + d0), ys], 1)); pts.append(np.stack([np.full(len(ys), f.x1 - d0), ys], 1))
        if not pts:
            return np.zeros((0, 2))
        P = np.vstack(pts)
        lo, hi = centre_range(s, theta)
        P = P[(P[:, 0] >= lo - 1e-12) & (P[:, 0] <= hi + 1e-12) & (P[:, 1] >= lo - 1e-12) & (P[:, 1] <= hi + 1e-12)]
        return P

    def is_symmetric_D4(self, s):
        """True if the hypothesis set is invariant under D4 (only NO-families, and their D4 images are all present)"""
        if self.boxes:
            return False
        keys = set()
        for f in self.nofams:
            keys.add((round(f.x0, 6), round(f.x1, 6), round(f.y0, 6), round(f.y1, 6), tuple(sorted(f.thetas))))
        for f in self.nofams:
            for (a0, a1, b0, b1, ths) in d4_rect_images(f.x0, f.x1, f.y0, f.y1, f.thetas, s):
                if (round(a0, 6), round(a1, 6), round(b0, 6), round(b1, 6), tuple(sorted(ths))) not in keys:
                    return False
        return True


def d4_rect_images(x0, x1, y0, y1, thetas, s):
    """images of a (rect x theta-set) family under D4; reflection maps theta -> 90 - theta"""
    def refl(ths):
        out = []
        for a, b in ths:
            a2, b2 = 90 - b, 90 - a
            out.append((a2, b2))
        return out
    rot = [(x0, x1, y0, y1), (s - y1, s - y0, x0, x1), (s - x1, s - x0, s - y1, s - y0), (y0, y1, s - x1, s - x0)]
    out = [(r[0], r[1], r[2], r[3], thetas) for r in rot]
    out += [(s - r[1], s - r[0], r[2], r[3], refl(thetas)) for r in rot]
    return out


# ------------------------------------------------------------------ node LP
def solve_node(s, hyp, budget, sym_kind="C1", warm=None, time_limit=240, max_iter=200, fine=True, log=None,
               out=None, N0=38, max_rows_add=1500, max_cols_add=150, theta_box="0-90", prune=0, fine_slack=0.05, col_stop_iter=40, col_stop_cov=1.02,
               extra_rows=None, neigh_rows=0, checkpoint=None, prune_cols=0, alternate=False):
    """Solve the node LP.  warm = dict(atoms=[(x,y)], rows=[(cx,cy,th)]) or None.
    Returns result dict (tau, converged, minmass, maxcov, packing, atoms, ...)."""
    if log is None:
        log = lambda *a: print(*a, flush=True)
    NoFam.s_hi = s - 0.5
    sym = Sym(sym_kind, s)
    ivs = ThetaBox.parse(theta_box, None)
    tbox = ThetaBox(ivs, sym_kind if sym_kind == "D4" else "C4")
    ia = ir = None
    if warm:
        ia = [tuple(p) for p in warm.get("atoms", [])]
        ir = [tuple(r) for r in warm.get("rows", [])]
    if sym_kind == "D4":
        n_theta, N0_, grid, ig, fine_kw = 91, N0, 0.005, (0.1, 5.0), dict(n_theta=361, cstep=0.005, delta=0.001)
    else:   # C1: whole square -> coarser oracles (row oracle step 0.75 deg, column grid 0.01), fine search 0.25 deg
        n_theta, N0_, grid, ig, fine_kw = 61, min(N0, 24), 0.01, (0.2, 10.0), dict(n_theta=181, cstep=0.01, delta=0.001)
    res, M = lpbox.run(s, tbox, sym, n=budget, N0=N0_, max_iter=max_iter, out=None, verbose=True, time_limit=time_limit,
                       row_kw=dict(n_theta=n_theta, cstep=0.02), col_kw=dict(grid=grid, max_refine=30), init_atoms=ia, init_rows=ir,
                       max_rows_add=max_rows_add, max_cols_add=max_cols_add,
                       fine_row_kw=(fine_kw if fine else None), fine_if=(lambda tau: tau < budget + fine_slack),
                       checkpoint=checkpoint, hyp=hyp, log=log, prune=prune, init_grid=ig,
                       col_stop_iter=col_stop_iter, col_stop_cov=col_stop_cov, extra_rows=extra_rows, neigh_rows=neigh_rows,
                       prune_cols=prune_cols, alternate=alternate)
    res["budget"] = budget
    res["hyp"] = hyp.to_json()
    res["dead"] = bool(res["converged"] and res["tau"] < budget - 1e-6)
    res["dead_unconverged"] = bool(res["tau"] < budget - 1e-6)
    # symmetrised fractional packing (all images) and all atoms with positive weight (all images)
    res["packing_images"] = [list(p) for p in M.packing_images()]
    atoms_all = []
    for k, o in enumerate(M.orbits):
        if M.w[k] > 1e-10:
            for p in o["pts"]:
                atoms_all.append([float(p[0]), float(p[1]), float(M.w[k])])
    res["atoms_all"] = atoms_all
    res["rows_all"] = [list(r) for r in M.rows]
    del res["history"]
    if out:
        with open(out, "w") as f:
            json.dump(res, f)
    return res


def warm_from_result(res, s_new=None):
    """warm-start data (atoms + rows, all images) from a node result (this module) or an A07/A10 result json"""
    if "atoms_all" in res:
        atoms = [(a[0], a[1]) for a in res["atoms_all"]]
        rows = [tuple(r) for r in res["rows_all"]]
        return dict(atoms=atoms, rows=rows)
    s = res["s"]
    d4 = Sym("D4", s)
    atoms, rows = [], []
    for a in res["atoms"]:
        for p in d4.point_images(*a["rep"]):
            atoms.append(p)
    for p in res["packing"]:
        for (a, b, t) in d4.placement_images(p["cx"], p["cy"], p["theta"]):
            rows.append((a, b, t))
    return dict(atoms=atoms, rows=rows)


# ------------------------------------------------------------------ certificate
def make_certificate(res, s_rat, scale=1.03, denom_pos=10 ** 6, denom_w=10 ** 6):
    """rational measure certificate for a DEAD node: atoms rounded to 1/10^6, weights x scale rounded up.
    Includes the hypotheses (rational cores, NO-families) and the budget."""
    s = Fr(s_rat)
    assert abs(float(s) - res["s"]) < 1e-9
    seen = {}
    atoms, weights = [], []
    for (x, y, w) in res["atoms_all"]:
        if w <= 1e-10:
            continue
        p = (Fr(round(x * denom_pos), denom_pos), Fr(round(y * denom_pos), denom_pos))
        wq = Fr(math.ceil(w * scale * denom_w), denom_w)
        if p in seen:
            weights[seen[p]] += wq
        else:
            seen[p] = len(atoms); atoms.append(p); weights.append(wq)
    total = sum(weights, Fr(0))
    hyp = Hyp.from_json(res["hyp"])
    cert = dict(format="case-measure-certificate-v1", n=11, s=str(s), budget=res["budget"],
                atoms=[[str(p[0]), str(p[1])] for p in atoms], weights=[str(w) for w in weights], total=str(total),
                hypotheses=dict(cores=[dict(kx=str(c.kx), ky=str(c.ky), tm=str(c.tm), a=str(c.a), box=c.box.to_json()) for c in hyp.cores],
                                nofams=[dict(x0=str(q(f.x0)), x1=str(q(f.x1)), y0=str(q(f.y0)), y1=str(q(f.y1)),
                                             t_intervals=[[str(t_lo(a)), str(t_hi(b))] for a, b in f.thetas]) for f in hyp.nofams]),
                claim=(f"every admissible closed unit square Q in [0,{s}]^2 that is not in a NO-family and is disjoint from every core "
                       f"has mu(Q) >= 1, and mu(total) = {float(total):.6f} < budget {res['budget']} = 11 - #cores; hence no packing of 11 "
                       f"unit squares in side <= {s} satisfies the hypotheses"),
                provenance=dict(method="A13 case-LP node (caselp.solve_node), weights x %.4f rounded up to 1/%d, atoms rounded to 1/%d" % (scale, denom_w, denom_pos),
                                lp_tau=res["tau"], eps_geo=lpbox.EPS_GEO, eps_core=EPS_CORE, eps_zone=EPS_ZONE, eps_th=EPS_TH))
    return cert


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--s", type=float, required=True)
    ap.add_argument("--sym", default="C1")
    ap.add_argument("--budget", type=int, default=11)
    ap.add_argument("--hyp", default=None, help="json file with hypotheses (Hyp.to_json format)")
    ap.add_argument("--warm", default=None)
    ap.add_argument("--time_limit", type=float, default=240)
    ap.add_argument("--theta_box", default="0-90")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    hyp = Hyp.from_json(json.load(open(a.hyp))) if a.hyp else Hyp()
    warm = warm_from_result(json.load(open(a.warm))) if a.warm else None
    res = solve_node(a.s, hyp, a.budget, sym_kind=a.sym, warm=warm, time_limit=a.time_limit, out=a.out, theta_box=a.theta_box)
    print("tau", res["tau"], "budget", a.budget, "dead", res["dead"], "conv", res["converged"])
