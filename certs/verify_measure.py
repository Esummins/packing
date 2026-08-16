#!/usr/bin/env python3
"""
verify_measure.py -- exact-arithmetic verifier for MEASURE certificates (lower bounds for the
square-packing problem).  Written independently of the LP code that produces the certificates
(attempt A08-measure-verify); shares no code with attempts/A07-lp-dual.

CLAIM CERTIFIED
    Let mu = sum_i w_i * delta_{p_i} be a finite non-negative atomic measure on [0,s]^2 with
    total mass  M = sum_i w_i  <  n  (n = 11 by default; field "n" of the certificate).
    If every CLOSED unit square Q contained in the closed square [0,s]^2 (any orientation)
    satisfies mu(Q) >= 1, then no n pairwise-disjoint closed unit squares fit in [0,s]^2, and
    therefore s(n) >= s.   (Proof: if n unit squares with disjoint interiors fit in side s' < s,
    scale by s/s' > 1 and shrink each square about its centre back to a unit square; the n
    closed unit squares are now pairwise disjoint inside [0,s]^2, so mu([0,s]^2) >= n > M,
    contradiction.  Hence s(n) >= s.)

    The verifier decides the hypothesis "mu(Q) >= 1 for every closed unit square Q in [0,s]^2"
    by exact rational interval branch-and-bound; nothing is proved about the conclusion inside
    this program -- the two-line argument above is the only mathematics taken on trust, plus the
    symmetry remark below.

PARAMETRISATION
    Q(c, theta) = closed unit square with centre c = (cx, cy) and edge direction theta.
    Q(c, theta) = Q(c, theta + pi/2), so theta in [0, pi/2] suffices.  Put t = tan(theta/2) in
    [0, 1]:  cos theta = (1 - t^2)/(1 + t^2)  (decreasing on [0,1]),
             sin theta = 2t/(1 + t^2)         (increasing on [0,1]),
    so for a rational t-interval [t0, t1] the enclosures  C = [cos(t1), cos(t0)]  and
    S = [sin(t0), sin(t1)]  are exact rationals.  Everything below is fractions.Fraction; the
    only floating point is an OPTIONAL pre-pass that shortlists atoms (numpy) -- every accept
    decision is re-derived exactly.

    p is inside Q(c, theta)  <=>  |u| <= 1/2 and |v| <= 1/2   where
        u =  cos*(px-cx) + sin*(py-cy),    v = -sin*(px-cx) + cos*(py-cy).
    Q(c, theta) is inside [0,s]^2  <=>  w/2 <= cx <= s - w/2 and w/2 <= cy <= s - w/2,
        w = cos theta + sin theta  (>= 1, unimodal in t: min over an interval at an endpoint).

BRANCH AND BOUND over boxes B = [t0,t1] x [x0,x1] x [y0,y1]  (root: [0,1] x [1/2, s-1/2]^2;
    every admissible centre lies there because w >= 1).  A box is DISCHARGED if
      (a) VACUOUS: no admissible placement in B, certified by  x1 < wmin/2  or  x0 > s - wmin/2
          (or the same in y) with wmin = min(w(t0), w(t1)), a lower bound for w on all of [t0,t1];
      (b) COVERED: sum{ w_i : p_i inside Q(c,theta) for EVERY (t,c) in B } >= 1 + margin,
          the inclusion being decided by exact interval arithmetic on u, v.
    Otherwise it is bisected along its widest side (t-width scaled by --tscale) and the two halves
    are examined; boxes reaching --depth bisections undischarged are FAIL witnesses.

USAGE
    python verify_measure.py cert.json [--depth D] [--strict-margin m] [--report [path]]
                             [--jobs J] [--max-witnesses K] [--tscale T] [--no-float-prepass]
                             [--witness-file path] [--n N] [--quiet]
    exit code 0 = PASS, 1 = FAIL, 2 = certificate malformed / total mass >= n.

CERTIFICATE FORMAT (JSON; all numbers are exact rationals written as strings, e.g. "19/5",
    "3.8", "0.4022988505747193" -- decimal strings are read EXACTLY as the rational they denote)
    {"s": "19/5",
     "n": 11,                                   optional, default 11
     "atoms":   [["x","y"], ...],
     "weights": ["w", ...],                     same length as atoms; all >= 0
     "total":   "...",                          optional; checked against sum(weights)
     "symmetry": "D4",                          optional; if present every atom is expanded to
                                                its D4-orbit under the symmetries of [0,s]^2
                                                (distinct images only), each image getting the
                                                listed weight
     "provenance": {...}}                       ignored
    Also accepted: "atoms": [{"x":..,"y":..,"w":..}, ...] (weights inline).
"""
import sys
import os
import json
import time
import math
import argparse
from fractions import Fraction as F

try:
    import numpy as np
except Exception:  # pragma: no cover
    np = None

HALF = F(1, 2)
ONE = F(1)
ZERO = F(0)


# ----------------------------------------------------------------------------- exact core
# (this block is what a Lean port needs: cos_t/sin_t, imul, atom_inside, vacuous)

_cs_cache = {}


def cos_sin_t(t):
    """exact (cos theta, sin theta) for t = tan(theta/2) (rational)."""
    r = _cs_cache.get(t)
    if r is None:
        tt = t * t
        d = 1 + tt
        r = ((1 - tt) / d, 2 * t / d)
        _cs_cache[t] = r
    return r


def imul(a0, a1, b0, b1):
    """exact interval product [a0,a1]*[b0,b1]"""
    p1 = a0 * b0
    p2 = a0 * b1
    p3 = a1 * b0
    p4 = a1 * b1
    return min(p1, p2, p3, p4), max(p1, p2, p3, p4)


def atom_inside(px, py, C0, C1, S0, S1, x0, x1, y0, y1):
    """True iff atom (px,py) lies in Q(c,theta) for EVERY cx in [x0,x1], cy in [y0,y1],
    cos theta in [C0,C1], sin theta in [S0,S1]  (sound over-approximation by interval arithmetic)."""
    dx0, dx1 = px - x1, px - x0
    dy0, dy1 = py - y1, py - y0
    a0, a1 = imul(C0, C1, dx0, dx1)
    b0, b1 = imul(S0, S1, dy0, dy1)
    if a1 + b1 > HALF or a0 + b0 < -HALF:      # u = C*dx + S*dy
        return False
    a0, a1 = imul(-S1, -S0, dx0, dx1)
    b0, b1 = imul(C0, C1, dy0, dy1)
    if a1 + b1 > HALF or a0 + b0 < -HALF:      # v = -S*dx + C*dy
        return False
    return True


def wmin_of(t0, t1):
    """lower bound of w = cos+sin over t in [t0,t1] (w unimodal in t => min at an endpoint)"""
    c0, s0 = cos_sin_t(t0)
    c1, s1 = cos_sin_t(t1)
    return min(c0 + s0, c1 + s1)


def vacuous(s, t0, t1, x0, x1, y0, y1):
    """True iff certainly no admissible placement (Q inside [0,s]^2) has (t,c) in the box."""
    h = wmin_of(t0, t1) / 2
    return x1 < h or x0 > s - h or y1 < h or y0 > s - h


# ----------------------------------------------------------------------------- float helpers
def f_mass_at(s, PX, PY, W, t, cx, cy, tol=1e-12):
    """float mass of the closed unit square Q((cx,cy),theta(t)); tol widens the square slightly."""
    c = (1 - t * t) / (1 + t * t)
    sn = 2 * t / (1 + t * t)
    dx = PX - cx
    dy = PY - cy
    u = c * dx + sn * dy
    v = -sn * dx + c * dy
    m = (np.abs(u) <= 0.5 + tol) & (np.abs(v) <= 0.5 + tol)
    return float(W[m].sum()), m


def f_admissible_centre(s, t, x0, x1, y0, y1):
    """an admissible centre in [x0,x1]x[y0,y1] at parameter t, or None"""
    c = (1 - t * t) / (1 + t * t)
    sn = 2 * t / (1 + t * t)
    h = (c + sn) / 2
    lo, hi = h, s - h
    ax0, ax1 = max(x0, lo), min(x1, hi)
    ay0, ay1 = max(y0, lo), min(y1, hi)
    if ax0 > ax1 or ay0 > ay1:
        return None
    return (0.5 * (ax0 + ax1), 0.5 * (ay0 + ay1))


# ----------------------------------------------------------------------------- the search
class Verifier:
    def __init__(self, s, atoms, weights, margin=ZERO, depth=48, tscale=2, use_float=True,
                 max_witnesses=200, verbose=True, progress_every=200000):
        self.s = s
        self.margin = margin
        self.need = ONE + margin
        self.depth = depth
        self.tscale = F(tscale)
        self.max_witnesses = max_witnesses
        self.verbose = verbose
        self.progress_every = progress_every
        # sort atoms by decreasing weight so that early exit hits heavy atoms first
        order = sorted(range(len(atoms)), key=lambda i: -weights[i])
        self.atoms = [atoms[i] for i in order]
        self.weights = [weights[i] for i in order]
        self.use_float = use_float and np is not None and len(atoms) > 0
        if np is not None:
            self.PX = np.array([float(p[0]) for p in self.atoms])
            self.PY = np.array([float(p[1]) for p in self.atoms])
            self.W = np.array([float(w) for w in self.weights])
        self.fneed = float(self.need) - 1e-9
        self.reset_stats()

    def reset_stats(self):
        self.n_boxes = 0
        self.n_vac = 0
        self.n_cov = 0
        self.n_split = 0
        self.n_exact = 0
        self.n_float_reject = 0
        self.hist_cov = {}
        self.hist_vac = {}
        self.witnesses = []
        self.max_depth_seen = 0

    # -- float shortlist: indices of atoms that MIGHT be inside for the whole box
    def float_candidates(self, ft0, ft1, fx0, fx1, fy0, fy1):
        eps = 1e-9
        # cos, sin >= 0 exactly on t in [0,1], so clamping the lower bounds at 0 keeps them valid
        C0 = max(0.0, (1 - ft1 * ft1) / (1 + ft1 * ft1) - eps)
        C1 = (1 - ft0 * ft0) / (1 + ft0 * ft0) + eps
        S0 = max(0.0, 2 * ft0 / (1 + ft0 * ft0) - eps)
        S1 = 2 * ft1 / (1 + ft1 * ft1) + eps
        dx0 = self.PX - fx1
        dx1 = self.PX - fx0
        dy0 = self.PY - fy1
        dy1 = self.PY - fy0
        # C, S >= 0 (up to eps) so the interval products are monotone in dx, dy
        a_hi = np.maximum(C0 * dx1, C1 * dx1)
        a_lo = np.minimum(C0 * dx0, C1 * dx0)
        b_hi = np.maximum(S0 * dy1, S1 * dy1)
        b_lo = np.minimum(S0 * dy0, S1 * dy0)
        ok = (a_hi + b_hi <= 0.5 + eps) & (a_lo + b_lo >= -0.5 - eps)
        # v = -S*dx + C*dy : -S in [-S1,-S0] <= 0
        a_hi = np.maximum(-S1 * dx0, -S0 * dx0)
        a_lo = np.minimum(-S1 * dx1, -S0 * dx1)
        b_hi = np.maximum(C0 * dy1, C1 * dy1)
        b_lo = np.minimum(C0 * dy0, C1 * dy0)
        ok &= (a_hi + b_hi <= 0.5 + eps) & (a_lo + b_lo >= -0.5 - eps)
        return np.nonzero(ok)[0]

    def covered(self, t0, t1, x0, x1, y0, y1):
        """exact: is the covered mass >= 1 + margin on the whole box?"""
        C1, S0 = cos_sin_t(t0)          # cos decreasing, sin increasing in t
        C0, S1 = cos_sin_t(t1)
        if self.use_float:
            cand = self.float_candidates(float(t0), float(t1), float(x0), float(x1),
                                         float(y0), float(y1))
            if self.W[cand].sum() < self.fneed:
                self.n_float_reject += 1
                return False
            idx = cand.tolist()
        else:
            idx = range(len(self.atoms))
        acc = ZERO
        atoms, weights = self.atoms, self.weights
        for i in idx:
            self.n_exact += 1
            px, py = atoms[i]
            if atom_inside(px, py, C0, C1, S0, S1, x0, x1, y0, y1):
                acc += weights[i]
                if acc >= self.need:
                    return True
        return False

    def exact_mass_at(self, t, cx, cy):
        """exact mu(Q(c,theta(t))) for rational t, cx, cy (closed square)."""
        c, sn = cos_sin_t(t)
        acc = ZERO
        for (px, py), w in zip(self.atoms, self.weights):
            dx, dy = px - cx, py - cy
            u = c * dx + sn * dy
            if u > HALF or u < -HALF:
                continue
            v = -sn * dx + c * dy
            if v > HALF or v < -HALF:
                continue
            acc += w
        return acc

    def make_witness(self, d, t0, t1, x0, x1, y0, y1):
        w = {"depth": d,
             "box": {"t": [str(t0), str(t1)], "cx": [str(x0), str(x1)], "cy": [str(y0), str(y1)]}}
        s = self.s
        # candidate placements: box centre and corners, restricted to admissible ones (exact test)
        cands = []
        for tt in ((t0 + t1) / 2, t0, t1):
            c, sn = cos_sin_t(tt)
            h = (c + sn) / 2
            for fx in ((x0 + x1) / 2, x0, x1):
                if fx < h or fx > s - h:
                    continue
                for fy in ((y0 + y1) / 2, y0, y1):
                    if fy < h or fy > s - h:
                        continue
                    cands.append((tt, fx, fy))
        if not cands:
            # box centre in t; clip the centre to the admissible range at that t (still exact)
            tt = (t0 + t1) / 2
            c, sn = cos_sin_t(tt)
            h = (c + sn) / 2
            fx = min(max((x0 + x1) / 2, h), s - h)
            fy = min(max((y0 + y1) / 2, h), s - h)
            if h <= fx <= s - h and h <= fy <= s - h:
                cands.append((tt, fx, fy))
        if not cands:
            w["placement"] = None
            w["kind"] = "undecided"
            return w
        best = None
        for (tt, fx, fy) in cands:
            m = self.exact_mass_at(tt, fx, fy)
            if best is None or m < best[0]:
                best = (m, tt, fx, fy)
        m, tt, fx, fy = best
        theta = 2 * math.atan(float(tt))
        w["placement"] = {"t": str(tt), "cx": str(fx), "cy": str(fy),
                          "t_float": float(tt), "theta_deg": math.degrees(theta),
                          "cx_float": float(fx), "cy_float": float(fy)}
        w["exact_mass"] = str(m)
        w["float_mass"] = float(m)
        if m < self.need:
            w["kind"] = "hole"          # rigorous: this placement has mass < 1 + margin
        else:
            # mass ok at the samples; is an atom sitting on the boundary of Q (tight)?
            if np is not None:
                mi, _ = f_mass_at(float(s), self.PX, self.PY, self.W, float(tt), float(fx), float(fy), tol=-1e-9)
                w["float_mass_interior"] = mi
                w["kind"] = "tight" if mi < float(self.need) - 1e-9 else "undecided"
            else:
                w["kind"] = "undecided"
        return w

    def run(self, boxes, per_box_cap=None):
        """boxes: iterable of (depth, t0,t1,x0,x1,y0,y1) Fractions.  Returns True iff no witness.
        per_box_cap: stop exploring an initial box after that many witnesses (diversity of witnesses)."""
        s = self.s
        need_stop = False
        tstart = time.time()
        for box in boxes:
            if need_stop:
                break
            stack = [box]
            nw0 = len(self.witnesses)
            while stack:
                d, t0, t1, x0, x1, y0, y1 = stack.pop()
                self.n_boxes += 1
                if d > self.max_depth_seen:
                    self.max_depth_seen = d
                if vacuous(s, t0, t1, x0, x1, y0, y1):
                    self.n_vac += 1
                    self.hist_vac[d] = self.hist_vac.get(d, 0) + 1
                    continue
                if self.covered(t0, t1, x0, x1, y0, y1):
                    self.n_cov += 1
                    self.hist_cov[d] = self.hist_cov.get(d, 0) + 1
                    continue
                if d >= self.depth:
                    self.witnesses.append(self.make_witness(d, t0, t1, x0, x1, y0, y1))
                    if len(self.witnesses) >= self.max_witnesses:
                        need_stop = True
                        break
                    if per_box_cap is not None and len(self.witnesses) - nw0 >= per_box_cap:
                        break
                    continue
                self.n_split += 1
                wt = (t1 - t0) * self.tscale
                wx = x1 - x0
                wy = y1 - y0
                if wx >= wy and wx >= wt:
                    m = (x0 + x1) / 2
                    stack.append((d + 1, t0, t1, m, x1, y0, y1))
                    stack.append((d + 1, t0, t1, x0, m, y0, y1))
                elif wy >= wt:
                    m = (y0 + y1) / 2
                    stack.append((d + 1, t0, t1, x0, x1, m, y1))
                    stack.append((d + 1, t0, t1, x0, x1, y0, m))
                else:
                    m = (t0 + t1) / 2
                    stack.append((d + 1, m, t1, x0, x1, y0, y1))
                    stack.append((d + 1, t0, m, x0, x1, y0, y1))
                if self.verbose and self.n_boxes % self.progress_every == 0:
                    print(f"  ... {self.n_boxes} boxes ({self.n_cov} covered, {self.n_vac} vacuous, "
                          f"{len(self.witnesses)} witnesses), stack {len(stack)}, {time.time()-tstart:.0f}s",
                          flush=True)
        self.stopped_early = need_stop
        return len(self.witnesses) == 0

    def stats(self):
        return {"boxes": self.n_boxes, "covered": self.n_cov, "vacuous": self.n_vac,
                "split": self.n_split, "exact_atom_checks": self.n_exact,
                "float_rejects": self.n_float_reject, "max_depth": self.max_depth_seen,
                "depth_hist_covered": dict(sorted(self.hist_cov.items())),
                "depth_hist_vacuous": dict(sorted(self.hist_vac.items())),
                "witnesses": len(self.witnesses)}


# ----------------------------------------------------------------------------- certificate I/O
def _rat(x):
    if isinstance(x, F):
        return x
    if isinstance(x, bool):
        raise ValueError("boolean is not a number")
    if isinstance(x, int):
        return F(x)
    if isinstance(x, float):
        raise ValueError(f"float {x!r} in certificate: numbers must be exact strings or ints")
    return F(str(x).strip())


def d4_images(x, y, s):
    return [(x, y), (s - x, y), (x, s - y), (s - x, s - y),
            (y, x), (s - y, x), (y, s - x), (s - y, s - x)]


def load_certificate(path, n_override=None):
    with open(path) as fh:
        d = json.load(fh)
    s = _rat(d["s"])
    n = int(n_override if n_override is not None else d.get("n", 11))
    raw_atoms = d["atoms"]
    atoms, weights = [], []
    if raw_atoms and isinstance(raw_atoms[0], dict):
        for a in raw_atoms:
            atoms.append((_rat(a["x"]), _rat(a["y"])))
            weights.append(_rat(a["w"]))
    else:
        ws = d["weights"]
        if len(ws) != len(raw_atoms):
            raise ValueError("atoms/weights length mismatch")
        for (x, y), w in zip(raw_atoms, ws):
            atoms.append((_rat(x), _rat(y)))
            weights.append(_rat(w))
    sym = d.get("symmetry")
    if sym:
        if str(sym).upper() != "D4":
            raise ValueError(f"unknown symmetry {sym!r}")
        ex_atoms, ex_w = [], []
        for (x, y), w in zip(atoms, weights):
            seen = []
            for q in d4_images(x, y, s):
                if q not in seen:
                    seen.append(q)
            for q in seen:
                ex_atoms.append(q)
                ex_w.append(w)
        atoms, weights = ex_atoms, ex_w
    for (x, y), w in zip(atoms, weights):
        if w < 0:
            raise ValueError("negative weight")
        if not (0 <= x <= s and 0 <= y <= s):
            raise ValueError(f"atom ({x},{y}) outside [0,s]^2")
    total = sum(weights, ZERO)
    if "total" in d and _rat(d["total"]) != total:
        print(f"WARNING: declared total {d['total']} != computed total {total} "
              f"(~{float(total):.12f}); using computed", file=sys.stderr)
    return d, s, n, atoms, weights, total


# ----------------------------------------------------------------------------- parallel driver
def initial_boxes(s, k):
    """split the root box [0,1] x [1/2,s-1/2]^2 into 4^k sub-boxes (k bisections in x and in y)"""
    lo, hi = HALF, s - HALF
    m = 2 ** k
    out = []
    for i in range(m):
        for j in range(m):
            out.append((2 * k, ZERO, ONE, lo + (hi - lo) * i / m, lo + (hi - lo) * (i + 1) / m,
                        lo + (hi - lo) * j / m, lo + (hi - lo) * (j + 1) / m))
    return out


_G = {}


def _worker_init(s, atoms, weights, margin, depth, tscale, use_float, max_w, per_box_cap):
    _G["v"] = Verifier(s, atoms, weights, margin=margin, depth=depth, tscale=tscale,
                       use_float=use_float, max_witnesses=max_w, verbose=False)
    _G["cap"] = per_box_cap


def _worker(box):
    v = _G["v"]
    v.reset_stats()
    v.run([box], per_box_cap=_G["cap"])
    return v.stats(), v.witnesses


def merge_stats(acc, st):
    for k, val in st.items():
        if isinstance(val, dict):
            dd = acc.setdefault(k, {})
            for kk, vv in val.items():
                dd[kk] = dd.get(kk, 0) + vv
        elif k == "max_depth":
            acc[k] = max(acc.get(k, 0), val)
        else:
            acc[k] = acc.get(k, 0) + val
    return acc


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cert")
    ap.add_argument("--depth", type=int, default=48,
                    help="max number of bisections per box (default 48 ~ width 2^-16 of the root in each dim)")
    ap.add_argument("--strict-margin", type=str, default="0",
                    help="require exact covered mass >= 1 + m on every box (rational string)")
    ap.add_argument("--report", nargs="?", const="__auto__", default=None,
                    help="write a JSON report (default path <cert>.report.json)")
    ap.add_argument("--witness-file", type=str, default=None,
                    help="where to write witnesses on FAIL (default <cert>.witnesses.json)")
    ap.add_argument("--max-witnesses", type=int, default=200, help="stop after this many witness boxes in total")
    ap.add_argument("--max-witnesses-per-box", type=int, default=8,
                    help="stop exploring one of the 4^k initial boxes after this many witnesses (diversity)")
    ap.add_argument("--jobs", type=int, default=1, help="worker processes (each takes initial boxes from the 4^k split)")
    ap.add_argument("--split", type=int, default=3, help="k: the root is first split into 4^k boxes in (cx,cy)")
    ap.add_argument("--scale-weights", type=str, default="1",
                    help="multiply every weight by this rational before verifying (e.g. 1.00000001 to absorb LP rounding)")
    ap.add_argument("--tscale", type=str, default="2", help="weight of the t-width when choosing the split axis")
    ap.add_argument("--no-float-prepass", action="store_true", help="exact checks on ALL atoms (slow; for auditing)")
    ap.add_argument("--n", type=int, default=None, help="override n (default: certificate field or 11)")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)

    t_start = time.time()
    try:
        d, s, n, atoms, weights, total = load_certificate(a.cert, a.n)
    except Exception as e:
        print(f"MALFORMED certificate: {e}")
        return 2
    margin = F(a.strict_margin)
    scale = F(a.scale_weights)
    if scale != 1:
        weights = [w * scale for w in weights]
        total = sum(weights, ZERO)
        print(f"weights scaled by {scale}")
    verbose = not a.quiet
    print(f"certificate: {a.cert}")
    print(f"s = {s} (~{float(s):.10f}), n = {n}, atoms = {len(atoms)}, "
          f"total mass = {total} (~{float(total):.10f}), margin = {margin}")
    if total >= n:
        print(f"FAIL: total mass {float(total):.6f} >= n = {n}: certificate proves nothing")
        return 2
    if s < 1:
        print("s < 1: no unit square fits; vacuous PASS")
        return 0

    use_float = not a.no_float_prepass
    boxes = initial_boxes(s, a.split)
    stats = {}
    witnesses = []
    if a.jobs > 1:
        import multiprocessing as mp
        with mp.Pool(a.jobs, initializer=_worker_init,
                     args=(s, atoms, weights, margin, a.depth, F(a.tscale), use_float, a.max_witnesses,
                           a.max_witnesses_per_box)) as pool:
            done = 0
            for st, ws in pool.imap_unordered(_worker, boxes):
                merge_stats(stats, st)
                witnesses.extend(ws)
                done += 1
                if verbose and (done % max(1, len(boxes) // 16) == 0):
                    print(f"  ... {done}/{len(boxes)} top boxes, {stats['boxes']} boxes, "
                          f"{len(witnesses)} witnesses, {time.time()-t_start:.0f}s", flush=True)
                if len(witnesses) >= a.max_witnesses:
                    pool.terminate()
                    break
    else:
        v = Verifier(s, atoms, weights, margin=margin, depth=a.depth, tscale=F(a.tscale),
                     use_float=use_float, max_witnesses=a.max_witnesses, verbose=verbose)
        v.run(boxes, per_box_cap=a.max_witnesses_per_box)
        stats = v.stats()
        witnesses = v.witnesses
    stats["witnesses"] = len(witnesses)
    elapsed = time.time() - t_start
    passed = len(witnesses) == 0

    print(f"boxes = {stats['boxes']}  covered = {stats['covered']}  vacuous = {stats['vacuous']}  "
          f"split = {stats['split']}  exact atom checks = {stats['exact_atom_checks']}  "
          f"max depth = {stats['max_depth']}  time = {elapsed:.1f}s")
    if verbose:
        print("depth histogram (covered leaves):",
              " ".join(f"{k}:{v}" for k, v in sorted(stats['depth_hist_covered'].items())))
    if passed:
        print(f"PASS: every closed unit square in [0,{s}]^2 has mass >= {ONE + margin} ; total {total} < {n}"
              f"  ==>  s({n}) >= {s} (~{float(s):.10f})")
    else:
        holes = [w for w in witnesses if w.get("kind") == "hole"]
        tight = [w for w in witnesses if w.get("kind") == "tight"]
        und = [w for w in witnesses if w.get("kind") == "undecided"]
        print(f"FAIL: {len(witnesses)} witness boxes at depth {a.depth}: {len(holes)} HOLES (a placement with exact "
              f"mass < {ONE + margin}), {len(tight)} tight (mass ok at samples but an atom on the boundary of Q), "
              f"{len(und)} undecided at this depth"
              + ("  [stopped at --max-witnesses]" if len(witnesses) >= a.max_witnesses else ""))
        pick = min(witnesses, key=lambda w: w.get("float_mass", 9e9))
        if pick.get("placement"):
            p = pick["placement"]
            print(f"  worst witness: theta = {p['theta_deg']:.6f} deg, centre = ({p['cx_float']:.9f}, {p['cy_float']:.9f}), "
                  f"exact mass = {pick['exact_mass']} (~{pick['float_mass']:.12f})")
        # coarse summary of where the witnesses are (theta to 1 deg, centre to 0.05)
        cl = {}
        for w in witnesses:
            p = w.get("placement")
            if not p:
                continue
            key = (round(p["theta_deg"]), round(p["cx_float"] / 0.05) * 0.05, round(p["cy_float"] / 0.05) * 0.05)
            cl.setdefault(key, []).append(w["float_mass"])
        print(f"  {len(cl)} witness clusters (theta~1deg, centre~0.05):")
        for key, ms in sorted(cl.items(), key=lambda kv: min(kv[1]))[:12]:
            print(f"    theta~{key[0]:3d} deg centre~({key[1]:.2f},{key[2]:.2f})  n={len(ms):3d}  min mass {min(ms):.9f}")
        wf = a.witness_file or (os.path.splitext(a.cert)[0] + ".witnesses.json")
        with open(wf, "w") as fh:
            json.dump({"cert": a.cert, "s": str(s), "depth": a.depth, "margin": str(margin),
                       "scale_weights": str(scale), "witnesses": witnesses}, fh, indent=1)
        print(f"  witnesses written to {wf}")
    if a.report is not None:
        rp = a.report if a.report != "__auto__" else os.path.splitext(a.cert)[0] + ".report.json"
        with open(rp, "w") as fh:
            json.dump({"cert": a.cert, "s": str(s), "n": n, "atoms": len(atoms), "total": str(total),
                       "total_float": float(total), "margin": str(margin), "depth": a.depth,
                       "tscale": a.tscale, "jobs": a.jobs, "float_prepass": use_float,
                       "result": "PASS" if passed else "FAIL", "time_s": elapsed, "stats": stats,
                       "witnesses_preview": witnesses[:20]}, fh, indent=1)
        print(f"  report written to {rp}")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
