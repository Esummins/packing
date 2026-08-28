#!/usr/bin/env python3
"""
A38 / W1 + W2 -- the certified-field DOMAIN cut (design.md section W1/W2).

The sealed field certificate
    attempts/A33-tight-variety/t1/certs/A33_measure_feasible_3.877084.json
is a finite atomic measure mu = sum_i w_i delta_{p_i} on [0, s0]^2, s0 = 969271/250000, with the
machine-checked property (F1) mu(Q) >= 1 for EVERY closed unit square Q contained in [0, s0]^2,
and exact total mass

    total = 44630467/3906250 = 11 + eta,   eta = eta_cert = 1661717/3906250 = 0.425399552 exactly.

Lemma A33.1(i)/Corollary A33.2: for any 11-packing at side sigma <= s-hat, the lambda-scaled
placements (lambda = s0/sigma in (1, 1+1.3e-8]) of any subfamily I of its squares satisfy
    sum_{i in I} mu(S_i)  <=  |I| + eta .
Hence:

  W1  (|I| = 1)   a placement Q with mu(Q) > 1 + eta belongs to NO 11-packing at s0.
  W2  (|I| = k+1) if the node's k cores are known to carry coverage >= c_j each, then the
                  remaining square obeys mu(Q) <= 1 + eta - sum_j (c_j - 1); using
                  max(0, c_j - 1) only RAISES the threshold, i.e. is conservative.

This module provides
  * mlow_box(t0,t1,x0,x1,y0,y1)          conservative FLOAT lower bound on
                                         min_{x in box} mu(Q(x)), interval arithmetic with an
                                         inward SLOP of 1e-6 (absorbs the lambda displacement
                                         <= 1e-7 and all float rounding; direction = undercount);
  * mlow_box_exact(...)                  the same quantity in exact Fractions (mapper.mlow_exact
                                         semantics, reimplemented self-contained);
  * build_grid()/Mask                    a dense precomputed m_low grid (dt = 0.01, dc = 0.02)
                                         with 3^3-neighbour EROSION: a row is exempt only if its
                                         own cell and all 26 neighbours clear the threshold;
  * THR_CERT = 1 + eta_cert              the SOUND threshold (5567967/3906250 = 1.425399552);
  * THR_FLOAT = 1.243                    [NUM] sensitivity threshold, never composed.

Parameterisation (mapper.py's P_s):  x = (t, cx, cy), theta = 2*atan(t), t in [0, 1]
(theta in [0, 90 deg]; Q(c, theta) = Q(c, theta + 90 deg)), centres in [0.5, s0 - 0.5]^2.

Conservativeness of every primitive here is ONE-SIDED: m_low is never larger than the true
min coverage, thresholds are never lowered without a sound reason, and boundary/erosion failures
always report NOT-exempt.
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from fractions import Fraction as F

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

CERT_PATH = os.path.join(REPO, "attempts", "A33-tight-variety", "t1", "certs",
                         "A33_measure_feasible_3.877084.json")
GRID_PATH = os.path.join(HERE, "..", "results", "mlow_grid.npz")

SLOP = 1e-6                 # inward erosion of the unit square in the membership test
SLOP_F = F(1, 10 ** 6)
DT = 0.01                   # grid resolution in t
DC = 0.02                   # grid resolution in cx, cy

S0 = F(969271, 250000)
S0F = float(S0)
TOTAL = F(44630467, 3906250)
ETA_CERT = TOTAL - 11                       # 1661717/3906250 = 0.425399552
THR_CERT = TOTAL - 10                       # 5567967/3906250 = 1 + eta_cert
THR_CERT_F = float(THR_CERT)
THR_FLOAT = 1.243                           # [NUM] only -- 1 + eta_float bracket, never composed


# --------------------------------------------------------------------------- certificate loading
def load_cert_exact(path=CERT_PATH):
    """mapper.load_cert_exact semantics: (raw dict, s, [(x,y) Fractions], [w Fractions])."""
    d = json.load(open(path))
    s = F(str(d["s"]))
    atoms = [(F(str(x)), F(str(y))) for x, y in d["atoms"]]
    weights = [F(str(w)) for w in d["weights"]]
    return d, s, atoms, weights


class Field:
    """The sealed guard field: exact atoms/weights + float mirrors for the fast bounds."""

    def __init__(self, path=CERT_PATH):
        d, s, atoms, weights = load_cert_exact(path)
        assert s == S0, (s, S0)
        tot = sum(weights, F(0))
        assert tot == TOTAL, (tot, TOTAL)
        self.path = path
        self.raw = d
        self.s = s
        self.sf = float(s)
        self.atoms = atoms
        self.weights = weights
        self.n = len(atoms)
        self.PX = np.array([float(p[0]) for p in atoms])
        self.PY = np.array([float(p[1]) for p in atoms])
        self.W = np.array([float(w) for w in weights])
        # D4 closure audit (the cert must already be D4-expanded for W1 to bound ANY placement)
        m = dict(zip(atoms, weights))
        bad = 0
        for (x, y) in atoms:
            r = [(x, y), (s - y, x), (s - x, s - y), (y, s - x)]
            for (a, b) in r + [(s - a, b) for a, b in r]:
                if m.get((a, b)) != m[(x, y)]:
                    bad += 1
        self.d4_closed = (bad == 0)
        self.d4_defects = bad


_FIELD = None


def field(path=CERT_PATH):
    global _FIELD
    if _FIELD is None or _FIELD.path != path:
        _FIELD = Field(path)
    return _FIELD


# ------------------------------------------------------------------------- interval primitives
def cs_box(t0, t1):
    """[C0,C1] x [S0,S1] enclosures of (cos theta, sin theta), theta = 2 atan t, on t in [t0,t1]
    subset [0,1].  cos is decreasing, sin increasing on that range, so the enclosure is exact."""
    C0 = (1 - t1 * t1) / (1 + t1 * t1)
    C1 = (1 - t0 * t0) / (1 + t0 * t0)
    Sa = 2 * t0 / (1 + t0 * t0)
    Sb = 2 * t1 / (1 + t1 * t1)
    return C0, C1, Sa, Sb


def uv_bounds(PX, PY, t0, t1, x0, x1, y0, y1):
    """mapper.uv_bounds: interval enclosures of u = C dx + S dy, v = -S dx + C dy over the box.
    Valid because C, S >= 0 throughout t in [0,1]."""
    C0, C1, Sa, Sb = cs_box(t0, t1)
    dx0 = PX - x1
    dx1 = PX - x0
    dy0 = PY - y1
    dy1 = PY - y0
    a_lo = np.minimum(C0 * dx0, C1 * dx0)
    a_hi = np.maximum(C0 * dx1, C1 * dx1)
    b_lo = np.minimum(Sa * dy0, Sb * dy0)
    b_hi = np.maximum(Sa * dy1, Sb * dy1)
    c_lo = np.minimum(-Sb * dx1, -Sa * dx1)
    c_hi = np.maximum(-Sb * dx0, -Sa * dx0)
    d_lo = np.minimum(C0 * dy0, C1 * dy0)
    d_hi = np.maximum(C0 * dy1, C1 * dy1)
    return a_lo + b_lo, a_hi + b_hi, c_lo + d_lo, c_hi + d_hi


def inside_all_float(PX, PY, box, slop=SLOP):
    """CONSERVATIVE mask: atoms provably inside Q(x) for EVERY x in the box."""
    u_lo, u_hi, v_lo, v_hi = uv_bounds(PX, PY, *box)
    h = 0.5 - slop
    return (u_lo >= -h) & (u_hi <= h) & (v_lo >= -h) & (v_hi <= h)


def mlow_box(t0, t1, x0, x1, y0, y1, slop=SLOP, fld=None):
    """CONSERVATIVE float lower bound on min_{x in B} mu(Q(x)).  B = [t0,t1]x[x0,x1]x[y0,y1]."""
    f = fld or field()
    m = inside_all_float(f.PX, f.PY, (float(t0), float(t1), float(x0), float(x1),
                                      float(y0), float(y1)), slop)
    return float(f.W[m].sum())


# --------------------------------------------------------------------------------- exact backend
def _cs_box_exact(t0, t1):
    t0 = F(t0)
    t1 = F(t1)
    C0 = (1 - t1 * t1) / (1 + t1 * t1)
    C1 = (1 - t0 * t0) / (1 + t0 * t0)
    Sa = 2 * t0 / (1 + t0 * t0)
    Sb = 2 * t1 / (1 + t1 * t1)
    return C0, C1, Sa, Sb


def mlow_box_exact(t0, t1, x0, x1, y0, y1, slop=SLOP_F, fld=None):
    """Exact-rational m_low (mapper.mlow_exact semantics).  All inputs must be exactly
    representable rationals (Fractions, ints or exact decimal strings); floats are converted
    EXACTLY (Fraction(float)), which is what the caller wants for an audit of a float box."""
    f = fld or field()
    t0, t1 = F(t0), F(t1)
    x0, x1, y0, y1 = F(x0), F(x1), F(y0), F(y1)
    C0, C1, Sa, Sb = _cs_box_exact(t0, t1)
    h = F(1, 2) - F(slop)
    acc = F(0)
    for (px, py), w in zip(f.atoms, f.weights):
        dx0, dx1 = px - x1, px - x0
        dy0, dy1 = py - y1, py - y0
        a_lo = min(C0 * dx0, C1 * dx0)
        a_hi = max(C0 * dx1, C1 * dx1)
        b_lo = min(Sa * dy0, Sb * dy0)
        b_hi = max(Sa * dy1, Sb * dy1)
        if a_lo + b_lo < -h or a_hi + b_hi > h:
            continue
        c_lo = min(-Sb * dx1, -Sa * dx1)
        c_hi = max(-Sb * dx0, -Sa * dx0)
        d_lo = min(C0 * dy0, C1 * dy0)
        d_hi = max(C0 * dy1, C1 * dy1)
        if c_lo + d_lo < -h or c_hi + d_hi > h:
            continue
        acc += w
    return acc


def coverage_at(t, cx, cy, fld=None):
    """float mu(Q) at a single placement (no slop) -- diagnostics / canary only."""
    f = fld or field()
    t = float(t)
    c = (1 - t * t) / (1 + t * t)
    sn = 2 * t / (1 + t * t)
    dx = f.PX - cx
    dy = f.PY - cy
    u = c * dx + sn * dy
    v = -sn * dx + c * dy
    return float(f.W[(np.abs(u) <= 0.5) & (np.abs(v) <= 0.5)].sum())


# ------------------------------------------------------------------------------ the dense grid
def grid_geometry(dt=DT, dc=DC, s=S0F):
    clo, chi = 0.5, s - 0.5
    NT = int(round(1.0 / dt))
    NC = int(math.ceil((chi - clo) / dc))
    hc = (chi - clo) / NC
    return dict(NT=NT, NC=NC, clo=clo, chi=chi, ht=1.0 / NT, hc=hc, s=s)


def build_grid(dt=DT, dc=DC, slop=SLOP, path=GRID_PATH, verbose=True, fld=None):
    """Precompute m_low on the uniform grid.  Cell (i,j,k) is the CLOSED box
        t  in [i*ht, (i+1)*ht],  cx in [clo+j*hc, clo+(j+1)*hc],  cy in [clo+k*hc, ...].
    Cost is kept down by windowing each atom into the |dx|,|dy| <= sqrt(2)/2 + hc neighbourhood
    (outside it the atom cannot be inside any Q of the cell)."""
    f = fld or field()
    g = grid_geometry(dt, dc)
    NT, NC, clo, ht, hc = g["NT"], g["NC"], g["clo"], g["ht"], g["hc"]
    M = np.zeros((NT, NC, NC), dtype=np.float64)
    h = 0.5 - slop
    R = math.sqrt(0.5) + hc + 1e-9          # |dx|,|dy| bound for any atom inside Q
    t_start = time.time()
    PX, PY, W = f.PX, f.PY, f.W
    xedge = clo + hc * np.arange(NC + 1)
    for i in range(NT):
        t0, t1 = i * ht, (i + 1) * ht
        C0, C1, Sa, Sb = cs_box(t0, t1)
        for a in range(f.n):
            px, py, w = PX[a], PY[a], W[a]
            j0 = max(0, int(math.floor((px - R - clo) / hc)))
            j1 = min(NC, int(math.ceil((px + R - clo) / hc)))
            k0 = max(0, int(math.floor((py - R - clo) / hc)))
            k1 = min(NC, int(math.ceil((py + R - clo) / hc)))
            if j1 <= j0 or k1 <= k0:
                continue
            dx0 = px - xedge[j0 + 1:j1 + 1]          # min dx over each x-cell
            dx1 = px - xedge[j0:j1]                  # max dx
            dy0 = py - xedge[k0 + 1:k1 + 1]
            dy1 = py - xedge[k0:k1]
            a_lo = np.minimum(C0 * dx0, C1 * dx0)
            a_hi = np.maximum(C0 * dx1, C1 * dx1)
            c_lo = np.minimum(-Sb * dx1, -Sa * dx1)
            c_hi = np.maximum(-Sb * dx0, -Sa * dx0)
            b_lo = np.minimum(Sa * dy0, Sb * dy0)
            b_hi = np.maximum(Sa * dy1, Sb * dy1)
            d_lo = np.minimum(C0 * dy0, C1 * dy0)
            d_hi = np.maximum(C0 * dy1, C1 * dy1)
            ok = ((a_lo[:, None] + b_lo[None, :] >= -h) &
                  (a_hi[:, None] + b_hi[None, :] <= h) &
                  (c_lo[:, None] + d_lo[None, :] >= -h) &
                  (c_hi[:, None] + d_hi[None, :] <= h))
            if ok.any():
                M[i, j0:j1, k0:k1] += w * ok
        if verbose and (i + 1) % 10 == 0:
            print("   grid slab %d/%d  %.0fs" % (i + 1, NT, time.time() - t_start), flush=True)
    wall = time.time() - t_start
    meta = dict(g)
    meta.update(dt=dt, dc=dc, slop=slop, cert=os.path.relpath(f.path, REPO).replace("\\", "/"),
                n_atoms=f.n, total=str(TOTAL), eta_cert=str(ETA_CERT), thr_cert=str(THR_CERT),
                thr_float=THR_FLOAT, wall_s=wall,
                cell="t in [i*ht,(i+1)*ht], cx in [clo+j*hc,clo+(j+1)*hc], cy likewise")
    if path:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        np.savez_compressed(path, mlow=M, meta=np.array([json.dumps(meta)], dtype=object))
    return M, meta


# ---------------------------------------------------------------------------------- the mask
class Mask:
    """3^3-eroded exemption mask over the dense m_low grid.

    exempt(theta_deg, cx, cy, thr) is True only if the containing cell AND all 26 neighbours have
    m_low > thr.  Any query that falls outside the grid (or whose neighbourhood leaves it) reports
    NOT exempt -- one-sided in the safe direction."""

    NEG = -1.0e18

    def __init__(self, path=GRID_PATH, mlow=None, meta=None):
        if mlow is None:
            z = np.load(path, allow_pickle=True)
            mlow = z["mlow"]
            meta = json.loads(z["meta"][0])
        self.mlow = mlow
        self.meta = meta
        self.NT = int(meta["NT"])
        self.NC = int(meta["NC"])
        self.clo = float(meta["clo"])
        self.ht = float(meta["ht"])
        self.hc = float(meta["hc"])
        # erosion: pad with -inf so that boundary cells can never be exempt
        P = np.full((self.NT + 2, self.NC + 2, self.NC + 2), self.NEG, dtype=np.float64)
        P[1:-1, 1:-1, 1:-1] = mlow
        E = P
        for ax in (0, 1, 2):
            E = np.minimum(np.minimum(np.roll(E, 1, ax), E), np.roll(E, -1, ax))
        self.ero = E[1:-1, 1:-1, 1:-1]
        self._cache = {}

    # -- index helpers (vectorised); -1 marks "outside the grid"
    def _idx(self, theta_deg, C):
        th = np.mod(np.asarray(theta_deg, dtype=float), 90.0)
        t = np.tan(np.radians(th) / 2.0)
        i = np.floor(t / self.ht).astype(np.int64)
        i = np.clip(i, 0, self.NT - 1)
        j = np.floor((C[:, 0] - self.clo) / self.hc).astype(np.int64)
        k = np.floor((C[:, 1] - self.clo) / self.hc).astype(np.int64)
        bad = (j < 0) | (j >= self.NC) | (k < 0) | (k >= self.NC)
        j = np.clip(j, 0, self.NC - 1)
        k = np.clip(k, 0, self.NC - 1)
        return i, j, k, bad

    def mask_for(self, thr):
        """boolean (NT,NC,NC) array: cells whose eroded m_low exceeds thr."""
        key = round(float(thr), 12)
        m = self._cache.get(key)
        if m is None:
            m = self.ero > float(thr)
            self._cache[key] = m
        return m

    def exempt_many(self, theta_deg, C, thr):
        C = np.asarray(C, dtype=float).reshape(-1, 2)
        if len(C) == 0:
            return np.zeros(0, dtype=bool)
        i, j, k, bad = self._idx(theta_deg, C)
        i = np.broadcast_to(np.atleast_1d(i), (len(C),))
        out = self.mask_for(thr)[i, j, k]
        out = out & ~bad
        return out

    def exempt(self, theta_deg, cx, cy, thr):
        return bool(self.exempt_many(theta_deg, np.array([[cx, cy]]), thr)[0])

    def frac_exempt(self, thr, s=S0F):
        """(cell fraction in dt measure, in dtheta measure) over ADMISSIBLE cells, plus raw counts.
        A cell counts as admissible if its centre satisfies w(t)/2 <= c <= s - w(t)/2 at the
        slab's WIDEST w (t at the 45 deg end), i.e. a conservative admissible set."""
        E = self.mask_for(thr)
        ts = (np.arange(self.NT) + 0.5) * self.ht
        cs = self.clo + (np.arange(self.NC) + 0.5) * self.hc
        num_t = den_t = num_th = den_th = 0.0
        n_ex = n_ad = 0
        tstar = math.tan(math.pi / 8)          # w = cos+sin is maximal at theta = 45 deg
        for i in range(self.NT):
            t0, t1 = i * self.ht, (i + 1) * self.ht
            tw = min(max(tstar, t0), t1)       # argmax of w over the slab
            w = (1 - tw * tw) / (1 + tw * tw) + 2 * tw / (1 + tw * tw)
            lo, hi = 0.5 * w, s - 0.5 * w
            ad = (cs >= lo) & (cs <= hi)
            adm = ad[:, None] & ad[None, :]
            na = int(adm.sum())
            ne = int((E[i] & adm).sum())
            n_ad += na
            n_ex += ne
            jw = 2.0 / (1.0 + ts[i] ** 2)
            den_t += na
            num_t += ne
            den_th += na * jw
            num_th += ne * jw
        return dict(thr=float(thr), frac_dt=(num_t / den_t if den_t else 0.0),
                    frac_dtheta=(num_th / den_th if den_th else 0.0),
                    cells_exempt=n_ex, cells_admissible=n_ad,
                    frac_all_cells=float(E.mean()))


# ------------------------------------------------------------------------- node-level primitives
def box_to_t(th0_deg, th1_deg):
    """degrees -> t = tan(theta/2) window, rounded OUTWARD (widens the box: conservative)."""
    t0 = math.tan(math.radians(th0_deg) / 2.0)
    t1 = math.tan(math.radians(th1_deg) / 2.0)
    return max(0.0, t0 * (1 - 1e-12) - 1e-12), min(1.0, t1 * (1 + 1e-12) + 1e-12)


def inflate(t0, t1, x0, x1, y0, y1, meta):
    """inflate a box by ONE grid cell in each direction (design.md W1/W2)."""
    ht, hc = float(meta["ht"]), float(meta["hc"])
    return (max(0.0, t0 - ht), min(1.0, t1 + ht), x0 - hc, x1 + hc, y0 - hc, y1 + hc)


def core_mlow(box, meta, slop=SLOP, fld=None):
    """c_j = mlow_box over the core box B_j INFLATED by one grid cell (W2)."""
    t0, t1 = box_to_t(box.th0, box.th1)
    b = inflate(t0, t1, box.x0, box.x1, box.y0, box.y1, meta)
    return mlow_box(*b, slop=slop, fld=fld)


def node_kill(box, meta, thr, slop=SLOP, fld=None):
    """W1-node-kill: the ENTIRE core box (inflated by one grid cell) is exempt -> the hypothesis
    'some packing square has (c,theta) in B' is vacuous; the node dies without an LP."""
    t0, t1 = box_to_t(box.th0, box.th1)
    b = inflate(t0, t1, box.x0, box.x1, box.y0, box.y1, meta)
    m = mlow_box(*b, slop=slop, fld=fld)
    return (m > float(thr)), m


def thr_node(cores_mlow, eta=None):
    """W2 node threshold: 1 + eta - sum_j max(0, c_j - 1)."""
    e = float(ETA_CERT if eta is None else eta)
    return 1.0 + e - sum(max(0.0, c - 1.0) for c in cores_mlow)


# ---------------------------------------------------------------------------------- module CLI
def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--dt", type=float, default=DT)
    ap.add_argument("--dc", type=float, default=DC)
    ap.add_argument("--out", default=GRID_PATH)
    ap.add_argument("--stats", action="store_true")
    a = ap.parse_args()
    f = field()
    print("field: %d atoms, D4-closed=%s, total=%s, eta_cert=%s, thr_cert=%s (%.9f)"
          % (f.n, f.d4_closed, TOTAL, ETA_CERT, THR_CERT, THR_CERT_F), flush=True)
    if a.build:
        M, meta = build_grid(a.dt, a.dc, path=a.out)
        print("grid %s built in %.1fs -> %s" % (M.shape, meta["wall_s"], a.out), flush=True)
    if a.stats:
        mk = Mask(a.out)
        for thr in (THR_CERT_F, THR_FLOAT):
            print(json.dumps(mk.frac_exempt(thr)), flush=True)


if __name__ == "__main__":
    main()
