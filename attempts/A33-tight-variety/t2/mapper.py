#!/usr/bin/env python3
"""
A33 / T2 -- certified exclusion mapper over the placement space P_s.

P_s = { x = (t, cx, cy) : Q(x) = closed unit square, centre (cx,cy), theta = 2*atan(t),
        Q(x) subset [0,s]^2 },  t in [0,1]  (theta in [0, pi/2]; Q(c,theta)=Q(c,theta+pi/2)).

Given a guard field mu = sum w_i delta_{p_i} and a threshold thr = 1 + eta, a parameter box
B = [t0,t1] x [x0,x1] x [y0,y1] is EXCLUDED if

        m_low(B) := sum { w_i : p_i in Q(x) for EVERY x in B }   >   thr ,

because then min_{x in B} mu(Q(x)) >= m_low(B) > 1 + eta, so no point of B lies in the tight
variety T_eta(mu) = { x : mu(Q(x)) <= 1 + eta }.  By Lemma A33.1/Corollary A33.2 no square of
any 11-packing at side < s has its (lambda-scaled) placement in B.

The membership test "p_i in Q(x) for every x in B" is the exact interval predicate of
certs/verify_measure.py (atom_inside_int), so in mode=exact every EXCLUSION is certified by exact
rational/integer arithmetic.  A float interval pre-pass with OUTWARD slop (conservative: it can
only under-count atoms) shortlists the candidates; in mode=float the exclusion decision is taken
on that conservative float bound alone (fast, still one-sided, but NOT certified -- labelled).

A box that is not excluded is SURVIVING; refinement stops early when a sampled admissible
placement inside B already has coverage <= thr (so B really does meet T_eta -- refining it would
not shrink the reported outer measure much), and otherwise at the target resolution.  The reported
surviving volume is therefore an OUTER measure of T_eta and the excluded volume an INNER measure
of the certified exclusion cover; both are one-sided in the safe direction.

Volumes are reported in two measures:
    vol_t     : dt dcx dcy on t in [0,1]
    vol_theta : dtheta dcx dcy, dtheta = 2 dt/(1+t^2)  (the natural rotation measure)
Both are restricted to the admissible set  w(t)/2 <= cx, cy <= s - w(t)/2,  w = cos+sin.
"""
import os
import sys
import json
import time
import math
import argparse
from fractions import Fraction as F

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(_REPO, "certs"))
from verify_measure import atom_inside_int, box_trig, clip_int, trig_int  # noqa: E402

EPS = 1e-9


# ------------------------------------------------------------------ field / certificate loading
def load_field_atoms(path):
    """Return (s_float, atoms Nx2 float array, weights N float array, meta) for either an A33
    field json (floats, already D4-expanded in 'atoms') or a measure-certificate json (exact)."""
    d = json.load(open(path))
    if "orbits" in d and "atoms" in d and isinstance(d["atoms"][0], list) and len(d["atoms"][0]) == 3:
        A = np.array([[a[0], a[1]] for a in d["atoms"]], float)
        W = np.array([a[2] for a in d["atoms"]], float)
        return float(d["s"]), A, W, {"kind": "field", "tau": d.get("tau"), "tag": d.get("tag")}
    # certificate
    s = F(str(d["s"]))
    A = np.array([[float(F(x)), float(F(y))] for x, y in d["atoms"]], float)
    W = np.array([float(F(w)) for w in d["weights"]], float)
    return float(s), A, W, {"kind": "cert", "total": d.get("total")}


def load_cert_exact(path):
    d = json.load(open(path))
    s = F(str(d["s"]))
    atoms = [(F(str(x)), F(str(y))) for x, y in d["atoms"]]
    weights = [F(str(w)) for w in d["weights"]]
    return d, s, atoms, weights


def field_to_exact(path, DP=10 ** 7, DW=10 ** 10):
    """Rationalise a float field for use as the arithmetic backend of an EXPLORATORY map.
    (Rounding here is not certified; float maps are labelled as such.)"""
    d = json.load(open(path))
    s = F(round(d["s"] * 10 ** 6), 10 ** 6)
    atoms, weights = [], []
    for a in d["atoms"]:
        atoms.append((F(round(a[0] * DP), DP), F(round(a[1] * DP), DP)))
        weights.append(F(round(a[2] * DW), DW))
    return d, s, atoms, weights


# ------------------------------------------------------------------------------- float interval
def _cs_box(t0, t1):
    C0 = (1 - t1 * t1) / (1 + t1 * t1)
    C1 = (1 - t0 * t0) / (1 + t0 * t0)
    S0 = 2 * t0 / (1 + t0 * t0)
    S1 = 2 * t1 / (1 + t1 * t1)
    return C0, C1, S0, S1


def uv_bounds(PX, PY, t0, t1, x0, x1, y0, y1):
    """Interval enclosures of u = C dx + S dy and v = -S dx + C dy over the box (C,S >= 0)."""
    C0, C1, S0, S1 = _cs_box(t0, t1)
    dx0 = PX - x1
    dx1 = PX - x0
    dy0 = PY - y1
    dy1 = PY - y0
    a_lo = np.minimum(C0 * dx0, C1 * dx0)
    a_hi = np.maximum(C0 * dx1, C1 * dx1)
    b_lo = np.minimum(S0 * dy0, S1 * dy0)
    b_hi = np.maximum(S0 * dy1, S1 * dy1)
    u_lo, u_hi = a_lo + b_lo, a_hi + b_hi
    c_lo = np.minimum(-S1 * dx1, -S0 * dx1)
    c_hi = np.maximum(-S1 * dx0, -S0 * dx0)
    d_lo = np.minimum(C0 * dy0, C1 * dy0)
    d_hi = np.maximum(C0 * dy1, C1 * dy1)
    return u_lo, u_hi, c_lo + d_lo, c_hi + d_hi


def inside_all_float(PX, PY, box, eps=EPS):
    """CONSERVATIVE: atoms provably inside Q(x) for every x in the box (outward slop eps)."""
    u_lo, u_hi, v_lo, v_hi = uv_bounds(PX, PY, *box)
    h = 0.5 - eps
    return (u_lo >= -h) & (u_hi <= h) & (v_lo >= -h) & (v_hi <= h)


def inside_some_float(PX, PY, box, eps=EPS):
    """OPTIMISTIC: atoms that might be inside Q(x) for some x in the box (monotone under refine)."""
    u_lo, u_hi, v_lo, v_hi = uv_bounds(PX, PY, *box)
    h = 0.5 + eps
    return (u_hi >= -h) & (u_lo <= h) & (v_hi >= -h) & (v_lo <= h)


def coverage_at(PX, PY, W, t, cx, cy):
    """float mu(Q) at a placement (arrays broadcast over placements: t,cx,cy may be 1-D)."""
    t = np.atleast_1d(np.asarray(t, float))
    cx = np.atleast_1d(np.asarray(cx, float))
    cy = np.atleast_1d(np.asarray(cy, float))
    c = ((1 - t * t) / (1 + t * t))[:, None]
    sn = (2 * t / (1 + t * t))[:, None]
    dx = PX[None, :] - cx[:, None]
    dy = PY[None, :] - cy[:, None]
    u = c * dx + sn * dy
    v = -sn * dx + c * dy
    m = (np.abs(u) <= 0.5) & (np.abs(v) <= 0.5)
    return m @ W


# --------------------------------------------------------------------------------- the mapper
STATUS = {"EXCLUDED": 0, "INSIDE": 1, "UNRESOLVED": 2, "VACUOUS": 3}


class Mapper:
    def __init__(self, s, atoms, weights, thr, res_t=0.005, res_c=0.01, mode="exact",
                 cbits=10, tbits=12, sample_tol=1e-7, verbose=True):
        self.s = F(s)
        self.sf = float(self.s)
        self.thr = F(thr)
        self.thrf = float(self.thr)
        self.mode = mode
        self.res_t = res_t
        self.res_c = res_c
        self.sample_tol = sample_tol
        self.verbose = verbose
        # ---- integer scale (independent of verify_measure's depth-driven one)
        self.K = tbits
        self.T_ROOT = 1 << self.K
        self.D = self.s.denominator << cbits
        self.SD = self.s.numerator << cbits
        order = sorted(range(len(atoms)), key=lambda i: -weights[i])   # heavy first: early exit
        atoms = [atoms[i] for i in order]
        weights = [weights[i] for i in order]
        self.atoms = atoms
        self.weights = weights
        self.PXn, self.PYn, self.PD = [], [], []
        for (px, py) in atoms:
            pd = px.denominator * py.denominator // math.gcd(px.denominator, py.denominator)
            self.PXn.append(px.numerator * (pd // px.denominator))
            self.PYn.append(py.numerator * (pd // py.denominator))
            self.PD.append(pd)
        WD = 1
        for w in weights:
            WD = WD * w.denominator // math.gcd(WD, w.denominator)
        self.WD = WD
        self.WI = [w.numerator * (WD // w.denominator) for w in weights]
        self.THRn, self.THRd = self.thr.numerator, self.thr.denominator   # excluded iff acc*THRd > THRn*WD
        # ---- floats
        self.PX = np.array([float(p[0]) for p in atoms])
        self.PY = np.array([float(p[1]) for p in atoms])
        self.W = np.array([float(w) for w in weights])
        self.n_atoms = len(atoms)
        self.reset()

    def reset(self):
        self.excluded_boxes = []          # (T0,T1,X0,X1,Y0,Y1) -- the certified exclusion cover
        self.n_leaves = 0
        self.n_boxes = 0
        self.n_exact = 0
        self.vol = {k: [0.0, 0.0] for k in STATUS}
        # ---- raster on a uniform grid at the target resolution (255 = not admissible / unvisited)
        self.NT = max(1, int(round(1.0 / self.res_t)))
        self.clo = 0.5
        self.chi = self.sf - 0.5
        self.NC = max(1, int(math.ceil((self.chi - self.clo) / self.res_c)))
        self.hc = (self.chi - self.clo) / self.NC
        self.grid = np.full((self.NT, self.NC, self.NC), 255, dtype=np.uint8)

    # -- conversions
    def tf(self, T):
        return T / self.T_ROOT

    def xf(self, X):
        return X / self.D

    # -- admissible volume of a (clipped) box, in dt and dtheta measure  (pure python, nq-point midpoint)
    def box_volume(self, T0, T1, X0, X1, Y0, Y1, nq=4):
        t0, t1 = self.tf(T0), self.tf(T1)
        x0, x1, y0, y1 = self.xf(X0), self.xf(X1), self.xf(Y0), self.xf(Y1)
        s = self.sf
        dt = (t1 - t0) / nq
        vt = vth = 0.0
        for q in range(nq):
            tt = t0 + dt * (q + 0.5)
            q2 = 1.0 + tt * tt
            w = (1.0 - tt * tt + 2.0 * tt) / q2
            lo, hi = 0.5 * w, s - 0.5 * w
            lx = min(x1, hi) - max(x0, lo)
            if lx <= 0.0:
                continue
            ly = min(y1, hi) - max(y0, lo)
            if ly <= 0.0:
                continue
            a = lx * ly
            vt += a
            vth += a * 2.0 / q2
        return vt * dt, vth * dt

    def total_volume(self, nq=20000):
        s = self.sf
        ts = (np.arange(nq) + 0.5) / nq
        w = (1 - ts * ts) / (1 + ts * ts) + 2 * ts / (1 + ts * ts)
        a = np.clip(s - w, 0, None) ** 2
        return float(a.sum() / nq), float((a * 2.0 / (1 + ts * ts)).sum() / nq)

    # -- exact m_low over an index subset
    def mlow_exact(self, T0, T1, X0, X1, Y0, Y1, idx):
        Clo, Chi, Slo, Shi, E = box_trig(T0, T1, self.K)
        acc = 0
        D = self.D
        NEED = self.THRn * self.WD          # excluded as soon as acc*THRd > NEED
        THRd = self.THRd
        PXn, PYn, PD, WI = self.PXn, self.PYn, self.PD, self.WI
        ne = 0
        for i in idx:                        # idx ascending == weights descending
            ne += 1
            if atom_inside_int(PXn[i], PYn[i], PD[i], D,
                               Clo, Chi, Slo, Shi, E, X0, X1, Y0, Y1):
                acc += WI[i]
                if acc * THRd > NEED:
                    break
        self.n_exact += ne
        return acc

    def excluded_int(self, acc):
        return acc * self.THRd > self.THRn * self.WD

    # -- sampled coverage (float) inside the clipped box
    def sample_min(self, T0, T1, X0, X1, Y0, Y1, cand):
        t0, t1 = self.tf(T0), self.tf(T1)
        x0, x1, y0, y1 = self.xf(X0), self.xf(X1), self.xf(Y0), self.xf(Y1)
        s = self.sf
        TS, XS, YS = [], [], []
        for tt in (t0, 0.5 * (t0 + t1), t1):
            w = (1 - tt * tt) / (1 + tt * tt) + 2 * tt / (1 + tt * tt)
            lo, hi = w / 2, s - w / 2
            if x1 < lo or x0 > hi or y1 < lo or y0 > hi:
                continue
            for fx in (x0, 0.5 * (x0 + x1), x1):
                fx = min(max(fx, lo), hi)
                for fy in (y0, 0.5 * (y0 + y1), y1):
                    fy = min(max(fy, lo), hi)
                    TS.append(tt); XS.append(fx); YS.append(fy)
        if not TS:
            return None
        cv = coverage_at(self.PX[cand], self.PY[cand], self.W[cand],
                         np.array(TS), np.array(XS), np.array(YS))
        return float(cv.min())

    def root_boxes(self, nt=8, nc=12):
        lo = self.D >> 1
        hi = self.SD - lo
        out = []
        for a in range(nt):
            T0 = (self.T_ROOT * a) // nt
            T1 = (self.T_ROOT * (a + 1)) // nt
            for i in range(nc):
                X0 = lo + ((hi - lo) * i) // nc
                X1 = lo + ((hi - lo) * (i + 1)) // nc
                for j in range(nc):
                    Y0 = lo + ((hi - lo) * j) // nc
                    Y1 = lo + ((hi - lo) * (j + 1)) // nc
                    out.append((T0, T1, X0, X1, Y0, Y1, None))
        return out

    def run(self, roots=None, report_every=500000):
        """Three sound verdicts per box B (all one-sided in the safe direction):
             m_low(B) > thr            -> EXCLUDED   (B disjoint from T_eta; exact in mode=exact)
             m_up(B)  <= thr           -> INSIDE     (B contained in T_eta)
           otherwise refine to the target resolution; leftovers are UNRESOLVED.
           vol(T_eta) in [vol_INSIDE, vol_INSIDE + vol_UNRESOLVED]  and the certified exclusion
           cover has volume vol_EXCLUDED."""
        t_start = time.time()
        stack = [(b[0], b[1], b[2], b[3], b[4], b[5], None)
                 for b in (roots if roots is not None else self.root_boxes())]
        rt, rc = self.res_t, self.res_c
        thrf = self.thrf
        PX, PY, W = self.PX, self.PY, self.W
        while stack:
            T0, T1, X0, X1, Y0, Y1, cand = stack.pop()
            self.n_boxes += 1
            clipped = clip_int(self.SD, self.D, self.K, T0, T1, X0, X1, Y0, Y1)
            if clipped is None:
                self.record(T0, T1, X0, X1, Y0, Y1, "VACUOUS", 0.0, novol=True)
                continue
            X0, X1, Y0, Y1 = clipped
            if cand is None:
                cand = np.arange(self.n_atoms)
            px, py = PX[cand], PY[cand]
            u_lo, u_hi, v_lo, v_hi = uv_bounds(px, py, self.tf(T0), self.tf(T1),
                                               self.xf(X0), self.xf(X1), self.xf(Y0), self.xf(Y1))
            hp = 0.5 + EPS
            some = (u_hi >= -hp) & (u_lo <= hp) & (v_hi >= -hp) & (v_lo <= hp)
            cand = cand[some]
            u_lo, u_hi, v_lo, v_hi = u_lo[some], u_hi[some], v_lo[some], v_hi[some]
            wc = W[cand]
            m_up = float(wc.sum())
            if m_up <= thrf:
                self.record(T0, T1, X0, X1, Y0, Y1, "INSIDE", m_up)
                continue
            hm = 0.5 - EPS
            allin = (u_lo >= -hm) & (u_hi <= hm) & (v_lo >= -hm) & (v_hi <= hm)
            mlow_f = float(wc[allin].sum())
            if mlow_f > thrf:
                if self.mode == "exact":
                    acc = self.mlow_exact(T0, T1, X0, X1, Y0, Y1, cand[allin].tolist())
                    if self.excluded_int(acc):
                        self.record(T0, T1, X0, X1, Y0, Y1, "EXCLUDED", acc / self.WD)
                        continue
                    mlow_f = acc / self.WD
                else:
                    self.record(T0, T1, X0, X1, Y0, Y1, "EXCLUDED", mlow_f)
                    continue
            # ---- refine?
            wt = (T1 - T0) / self.T_ROOT
            wx = (X1 - X0) / self.D
            wy = (Y1 - Y0) / self.D
            if wt <= rt and wx <= rc and wy <= rc:
                self.record(T0, T1, X0, X1, Y0, Y1, "UNRESOLVED", mlow_f)
                continue
            nt, nx, ny = wt / rt, wx / rc, wy / rc
            if nx >= ny and nx >= nt:
                mmid = (X0 + X1) >> 1
                stack.append((T0, T1, X0, mmid, Y0, Y1, cand))
                stack.append((T0, T1, mmid, X1, Y0, Y1, cand))
            elif ny >= nt:
                mmid = (Y0 + Y1) >> 1
                stack.append((T0, T1, X0, X1, Y0, mmid, cand))
                stack.append((T0, T1, X0, X1, mmid, Y1, cand))
            else:
                mmid = (T0 + T1) >> 1
                stack.append((T0, mmid, X0, X1, Y0, Y1, cand))
                stack.append((mmid, T1, X0, X1, Y0, Y1, cand))
            if self.verbose and self.n_boxes % report_every == 0:
                print(f"   ... {self.n_boxes} boxes, stack {len(stack)}, "
                      f"excl_vol {self.vol['EXCLUDED'][0]:.5f}, {time.time()-t_start:.0f}s", flush=True)
        self.wall = time.time() - t_start
        return self.summary()

    def record(self, T0, T1, X0, X1, Y0, Y1, status, mlow, novol=False):
        if novol:
            return
        vt, vth = self.box_volume(T0, T1, X0, X1, Y0, Y1)
        self.vol[status][0] += vt
        self.vol[status][1] += vth
        self.n_leaves += 1
        code = STATUS[status]
        if code == 0:
            self.excluded_boxes.append((T0, T1, X0, X1, Y0, Y1))
        # ---- paint the grid cells whose CENTRE lies in this leaf
        NT, NC, hc, clo = self.NT, self.NC, self.hc, self.clo
        i0 = int(math.ceil(NT * self.tf(T0) - 0.5))
        i1 = int(math.floor(NT * self.tf(T1) - 0.5)) + 1
        if i1 <= i0:
            return
        j0 = int(math.ceil((self.xf(X0) - clo) / hc - 0.5))
        j1 = int(math.floor((self.xf(X1) - clo) / hc - 0.5)) + 1
        if j1 <= j0:
            return
        k0 = int(math.ceil((self.xf(Y0) - clo) / hc - 0.5))
        k1 = int(math.floor((self.xf(Y1) - clo) / hc - 0.5)) + 1
        if k1 <= k0:
            return
        i0 = max(i0, 0); j0 = max(j0, 0); k0 = max(k0, 0)
        i1 = min(i1, NT); j1 = min(j1, NC); k1 = min(k1, NC)
        if i1 > i0 and j1 > j0 and k1 > k0:
            self.grid[i0:i1, j0:j1, k0:k1] = code

    def summary(self):
        Vt, Vth = self.total_volume()
        ex_t, ex_th = self.vol["EXCLUDED"]
        in_t, in_th = self.vol["INSIDE"]
        un_t, un_th = self.vol["UNRESOLVED"]
        acc_t = ex_t + in_t + un_t
        acc_th = ex_th + in_th + un_th
        return {
            "mode": self.mode, "thr": str(self.thr), "thr_float": self.thrf,
            "s": str(self.s), "n_atoms": self.n_atoms,
            "res_t": self.res_t, "res_c": self.res_c,
            "boxes": self.n_boxes, "leaves": self.n_leaves, "exact_atom_checks": self.n_exact,
            "wall_s": getattr(self, "wall", None),
            "vol_total_dt": Vt, "vol_total_dtheta": Vth,
            "vol_accounted_dt": acc_t, "vol_accounted_dtheta": acc_th,
            "vol_excluded_dt": ex_t, "vol_inside_dt": in_t, "vol_unresolved_dt": un_t,
            "vol_excluded_dtheta": ex_th, "vol_inside_dtheta": in_th, "vol_unresolved_dtheta": un_th,
            "frac_excluded_dt": ex_t / acc_t if acc_t else 0.0,
            "frac_excluded_dtheta": ex_th / acc_th if acc_th else 0.0,
            "frac_T_lower_dt": in_t / acc_t if acc_t else 0.0,
            "frac_T_upper_dt": (in_t + un_t) / acc_t if acc_t else 0.0,
            "frac_T_lower_dtheta": in_th / acc_th if acc_th else 0.0,
            "frac_T_upper_dtheta": (in_th + un_th) / acc_th if acc_th else 0.0,
        }

    def save(self, path, extra=None, max_boxes_json=600000):
        """JSON: summary + the EXCLUDED box list (the certified exclusion cover E, as integer
        box coordinates T/T_ROOT, X/D, Y/D).  NPZ (same stem): the status raster on the uniform
        target-resolution grid (0 EXCLUDED, 1 INSIDE, 2 UNRESOLVED, 255 inadmissible)."""
        E = self.excluded_boxes
        trunc = len(E) > max_boxes_json
        Ew = E[:max_boxes_json]
        obj = {"summary": self.summary(), "status_codes": STATUS,
               "int_scale": {"K": self.K, "T_ROOT": self.T_ROOT, "D": self.D, "SD": self.SD,
                             "t": "t = T/T_ROOT", "c": "cx = X/D, cy = Y/D"},
               "grid": {"NT": self.NT, "NC": self.NC, "c_lo": self.clo, "c_hi": self.chi,
                        "cell_t": 1.0 / self.NT, "cell_c": self.hc,
                        "centre": "t=(i+.5)/NT, cx=c_lo+(j+.5)*cell_c, cy=c_lo+(k+.5)*cell_c"},
               "extra": extra or {},
               "n_excluded_boxes": len(E), "excluded_boxes_truncated": trunc,
               "excluded_boxes": {"T0": [b[0] for b in Ew], "T1": [b[1] for b in Ew],
                                  "X0": [b[2] for b in Ew], "X1": [b[3] for b in Ew],
                                  "Y0": [b[4] for b in Ew], "Y1": [b[5] for b in Ew]}}
        with open(path, "w") as fh:
            json.dump(obj, fh)
        np.savez_compressed(os.path.splitext(path)[0] + "_raster.npz", grid=self.grid,
                            meta=np.array([json.dumps(obj["grid"])], dtype=object))
        return path
