"""A43-H1 field layer: the sealed guard field + W1/W2 (N5/N6) primitives.

Field preference (A43 H1 brief): the A39 RESEALED field
    attempts/A39-early-cert/results/p2b/certs/A39_measure_feasible_3.877084.json
    total = 71268483/6250000,  eta_cert = 2518483/6250000 = 0.40295728 exactly,
    threshold 1 + eta = 8768483/6250000 = 1.40295728 exactly,
    standalone verification report (...report.json) result = PASS, margin 0, s = 969271/250000.
Fallback: the A33 sealed field (eta_cert = 1661717/3906250 = 0.425399552).

SOUNDNESS of W1 at side < s0 (stated here because A38's header phrases it via lambda-scaling):
the certificate property is (F1) mu(Q) >= 1 for EVERY closed unit square Q in [0,s0]^2, with
exact total mass 11 + eta.  A packing of 11 unit squares at side sigma <= s0 lives inside
[0,s0]^2 and its squares are interior-disjoint, so sum_i mu(S_i) <= 11 + eta while every other
square contributes >= 1; hence mu(S_i) <= 1 + eta for each i (W1) and mu(S_i) + mu(S_j) <= 2 + eta
for each pair (W2, A33.1(i) with |I| = 2).  No scaling argument is needed.

All bounds here are ONE-SIDED conservative (m_low never exceeds the true minimum coverage),
copied from attempts/A38-root-power/code/fieldcut.py (mlow_box / mlow_box_exact / build_grid).
"""
from __future__ import annotations

import json
import math
import os
import time
from fractions import Fraction as F

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

A39_CERT = os.path.join(REPO, "attempts", "A39-early-cert", "results", "p2b", "certs",
                        "A39_measure_feasible_3.877084.json")
A39_REPORT = A39_CERT.replace(".json", ".report.json")
A33_CERT = os.path.join(REPO, "attempts", "A33-tight-variety", "t1", "certs",
                        "A33_measure_feasible_3.877084.json")

SLOP = 1e-6
SLOP_F = F(1, 10 ** 6)
DT = 0.01
DC = 0.02

S0 = F(969271, 250000)          # 3.877084
S0F = float(S0)
S_LO = 3.80                     # certified lower bound s(11) >= 3.80 (A06/A07/A08)
SQRT2 = math.sqrt(2.0)
HALF = SQRT2 / 2.0


def pick_field():
    """Return (path, provenance dict).  A39 resealed if artifact + PASS report present."""
    if os.path.exists(A39_CERT) and os.path.exists(A39_REPORT):
        rep = json.load(open(A39_REPORT))
        if rep.get("result") == "PASS" and F(str(rep.get("s"))) == S0:
            return A39_CERT, dict(field="A39 resealed (results/p2b)", report="PASS",
                                  report_margin=str(rep.get("margin")),
                                  report_time_s=rep.get("time_s"))
    return A33_CERT, dict(field="A33 sealed (fallback)", report="not re-verified here")


class Field:
    def __init__(self, path):
        d = json.load(open(path))
        s = F(str(d["s"]))
        assert s == S0, (s, S0)
        self.path = path
        self.raw = {k: v for k, v in d.items() if k not in ("atoms", "weights")}
        self.atoms = [(F(str(x)), F(str(y))) for x, y in d["atoms"]]
        self.weights = [F(str(w)) for w in d["weights"]]
        self.n = len(self.atoms)
        self.total = sum(self.weights, F(0))
        assert self.total == F(str(d["total"])), "declared total mismatch"
        self.eta = self.total - 11
        self.thr1 = self.total - 10          # 1 + eta
        self.thr2 = self.total - 9           # 2 + eta
        self.PX = np.array([float(p[0]) for p in self.atoms])
        self.PY = np.array([float(p[1]) for p in self.atoms])
        self.W = np.array([float(w) for w in self.weights])
        # D4 closure audit (informational only; W1/W2 do not need it)
        m = dict(zip(self.atoms, self.weights))
        bad = 0
        for (x, y) in self.atoms:
            r = [(x, y), (s - y, x), (s - x, s - y), (y, s - x)]
            for (a, b) in r + [(s - a, b) for a, b in r]:
                if m.get((a, b)) != m[(x, y)]:
                    bad += 1
        self.d4_defects = bad


_F = None


def field(path=None):
    global _F
    if path is None:
        path = pick_field()[0]
    if _F is None or _F.path != path:
        _F = Field(path)
    return _F


# ------------------------------------------------------------------ interval primitives (A38)
def cs_box(t0, t1):
    C0 = (1 - t1 * t1) / (1 + t1 * t1)
    C1 = (1 - t0 * t0) / (1 + t0 * t0)
    Sa = 2 * t0 / (1 + t0 * t0)
    Sb = 2 * t1 / (1 + t1 * t1)
    return C0, C1, Sa, Sb


def inside_all_float(PX, PY, box, slop=SLOP):
    t0, t1, x0, x1, y0, y1 = box
    C0, C1, Sa, Sb = cs_box(t0, t1)
    dx0, dx1 = PX - x1, PX - x0
    dy0, dy1 = PY - y1, PY - y0
    a_lo = np.minimum(C0 * dx0, C1 * dx0)
    a_hi = np.maximum(C0 * dx1, C1 * dx1)
    b_lo = np.minimum(Sa * dy0, Sb * dy0)
    b_hi = np.maximum(Sa * dy1, Sb * dy1)
    c_lo = np.minimum(-Sb * dx1, -Sa * dx1)
    c_hi = np.maximum(-Sb * dx0, -Sa * dx0)
    d_lo = np.minimum(C0 * dy0, C1 * dy0)
    d_hi = np.maximum(C0 * dy1, C1 * dy1)
    h = 0.5 - slop
    return ((a_lo + b_lo >= -h) & (a_hi + b_hi <= h) &
            (c_lo + d_lo >= -h) & (c_hi + d_hi <= h))


def mlow_box(t0, t1, x0, x1, y0, y1, slop=SLOP, fld=None):
    f = fld or field()
    m = inside_all_float(f.PX, f.PY, (float(t0), float(t1), float(x0), float(x1),
                                      float(y0), float(y1)), slop)
    return float(f.W[m].sum())


def mlow_box_exact(t0, t1, x0, x1, y0, y1, slop=SLOP_F, fld=None):
    f = fld or field()
    t0, t1 = F(t0), F(t1)
    x0, x1, y0, y1 = F(x0), F(x1), F(y0), F(y1)
    C0, C1, Sa, Sb = cs_box(t0, t1)
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


def coverage_exact(t, cx, cy, fld=None):
    """EXACT mu(Q) at a single placement (no slop): canary use."""
    f = fld or field()
    t = F(t)
    c = (1 - t * t) / (1 + t * t)
    sn = 2 * t / (1 + t * t)
    cx, cy = F(cx), F(cy)
    acc = F(0)
    for (px, py), w in zip(f.atoms, f.weights):
        dx, dy = px - cx, py - cy
        u = c * dx + sn * dy
        v = -sn * dx + c * dy
        if abs(u) <= F(1, 2) and abs(v) <= F(1, 2):
            acc += w
    return acc


# ------------------------------------------------------------------------- dense m_low grid
def grid_geometry(dt=DT, dc=DC, s=S0F):
    clo, chi = 0.5, s - 0.5
    NT = int(round(1.0 / dt))
    NC = int(math.ceil((chi - clo) / dc))
    return dict(NT=NT, NC=NC, clo=clo, chi=chi, ht=1.0 / NT, hc=(chi - clo) / NC, s=s)


def build_grid(dt=DT, dc=DC, slop=SLOP, path=None, fld=None, verbose=False):
    f = fld or field()
    g = grid_geometry(dt, dc)
    NT, NC, clo, ht, hc = g["NT"], g["NC"], g["clo"], g["ht"], g["hc"]
    M = np.zeros((NT, NC, NC), dtype=np.float64)
    h = 0.5 - slop
    R = math.sqrt(0.5) + hc + 1e-9
    t0w = time.time()
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
            dx0 = px - xedge[j0 + 1:j1 + 1]
            dx1 = px - xedge[j0:j1]
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
        if verbose and (i + 1) % 20 == 0:
            print("   slab %d/%d %.0fs" % (i + 1, NT, time.time() - t0w), flush=True)
    meta = dict(g)
    meta.update(dt=dt, dc=dc, slop=slop, cert=os.path.relpath(f.path, REPO).replace("\\", "/"),
                n_atoms=f.n, total=str(f.total), eta_cert=str(f.eta), thr_cert=str(f.thr1),
                wall_s=time.time() - t0w)
    if path:
        np.savez_compressed(path, mlow=M, meta=np.array([json.dumps(meta)], dtype=object))
    return M, meta


def load_grid(path):
    z = np.load(path, allow_pickle=True)
    return z["mlow"], json.loads(z["meta"][0])


def grid_min_over_box(M, meta, t0, t1, x0, x1, y0, y1):
    """Certified lower bound on min_{x in B} mu(Q(x)) using the dense grid: min over ALL cells
    that intersect B (outward cell selection).  B must lie in the grid range; a box that leaves
    the grid returns 0.0 (one-sided safe)."""
    NT, NC, clo, ht, hc = meta["NT"], meta["NC"], meta["clo"], meta["ht"], meta["hc"]
    chi = clo + NC * hc
    if x0 < clo - 1e-12 or y0 < clo - 1e-12 or x1 > chi + 1e-12 or y1 > chi + 1e-12:
        return 0.0
    i0 = max(0, int(math.floor(t0 / ht)))
    i1 = min(NT - 1, int(math.floor(min(t1, 1.0 - 1e-15) / ht)))
    j0 = max(0, int(math.floor((x0 - clo) / hc)))
    j1 = min(NC - 1, int(math.floor((min(x1, chi) - clo) / hc)))
    k0 = max(0, int(math.floor((y0 - clo) / hc)))
    k1 = min(NC - 1, int(math.floor((min(y1, chi) - clo) / hc)))
    if i1 < i0 or j1 < j0 or k1 < k0:
        return 0.0
    return float(M[i0:i1 + 1, j0:j1 + 1, k0:k1 + 1].min())


def frac_exempt(M, meta, thr):
    """A38 Mask.frac_exempt semantics with the 3^3 erosion: cells whose own m_low and all 26
    neighbours' exceed thr, over the admissible centre range."""
    NEG = -1e18
    NT, NC = meta["NT"], meta["NC"]
    P = np.full((NT + 2, NC + 2, NC + 2), NEG)
    P[1:-1, 1:-1, 1:-1] = M
    E = P
    for ax in (0, 1, 2):
        E = np.minimum(np.minimum(np.roll(E, 1, ax), E), np.roll(E, -1, ax))
    ero = E[1:-1, 1:-1, 1:-1]
    Ex = ero > float(thr)
    clo, ht, hc, s = meta["clo"], meta["ht"], meta["hc"], meta["s"]
    cs = clo + (np.arange(NC) + 0.5) * hc
    tstar = math.tan(math.pi / 8)
    n_ex = n_ad = 0
    for i in range(NT):
        t0, t1 = i * ht, (i + 1) * ht
        tw = min(max(tstar, t0), t1)
        w = (1 - tw * tw) / (1 + tw * tw) + 2 * tw / (1 + tw * tw)
        ad = (cs >= 0.5 * w) & (cs <= s - 0.5 * w)
        adm = ad[:, None] & ad[None, :]
        n_ad += int(adm.sum())
        n_ex += int((Ex[i] & adm).sum())
    return dict(thr=float(thr), cells_exempt=n_ex, cells_admissible=n_ad,
                frac_admissible=(n_ex / n_ad if n_ad else 0.0),
                mlow_max=float(M.max()), mlow_mean=float(M.mean()))


# --------------------------------------------------------------- wall-mask centre boxes at s0
def box_s0(m):
    """lib0._box semantics with the EXACT s0 = 969271/250000 upper endpoint: the certified
    centre box of a square with wall-contact mask m, valid for EVERY container side in
    [S_LO, s0].  bits 0=L 1=B 2=R 3=T."""
    if m & 1:
        x = (0.5, HALF)
    elif m & 4:
        x = (S_LO - HALF, S0F - 0.5)
    else:
        x = (0.5, S0F - 0.5)
    if m & 2:
        y = (0.5, HALF)
    elif m & 8:
        y = (S_LO - HALF, S0F - 0.5)
    else:
        y = (0.5, S0F - 0.5)
    return x, y


WIDEN = 1e-9   # outward widening of every float box endpoint before certification:
               # a LARGER window can only LOWER m_low, so it is one-sided safe for a kill test.


def mask_mlow(masks, M=None, meta=None, fld=None):
    """Per wall-mask certified m_low over (full tilt t in [0,1]) x (centre box at s0).
    Returns {mask: dict(box, mlow_singlebox_exact, mlow_gridmin, mlow_certified)}.
    mlow_certified = max of the two valid lower bounds (both are lower bounds, so is the max)."""
    out = {}
    for m in masks:
        (x0, x1), (y0, y1) = box_s0(m)
        X0, X1, Y0, Y1 = x0 - WIDEN, x1 + WIDEN, y0 - WIDEN, y1 + WIDEN
        e = mlow_box_exact(0, 1, F(X0), F(X1), F(Y0), F(Y1), fld=fld)
        g = grid_min_over_box(M, meta, 0.0, 1.0, X0, X1, Y0, Y1) if M is not None else 0.0
        out[m] = dict(box=[x0, x1, y0, y1], mlow_singlebox_exact=str(e),
                      mlow_singlebox=float(e), mlow_gridmin=g,
                      mlow_certified=max(float(e), g))
    return out
