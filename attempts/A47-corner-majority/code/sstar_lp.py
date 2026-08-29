#!/usr/bin/env python3
"""
A47 leg (a) TASK 2 -- LP PRODUCER for the s*-exception measure certificates (float; the arbiter is
the exact verifier `verify_measure_obs.py`).

For one rational parameter box B it builds the rational obstacle C_shr(B) = P_L u P_U u P_R
(sstar_geom, exact) and then looks for an atomic measure mu = sum w_i delta_{p_i} on [0,s']^2,
s' = 383/100, with

    (i)  mu(Q) >= 1 for every closed unit square Q in [0,s']^2 whose interior misses C_shr,
    (ii) total mass < 8.

Producer = LP  min sum w  s.t.  sum_{p_i in Q(c,t) shrunk by EPS} w_i >= 1  for a grid of
placements (centre x tilt t = tan(theta/2) in [0,1]) that are admissible and NOT exempt, followed
by a cutting-plane loop (dense violation scan -> add rows -> re-solve) and an upward rational
rounding with a safety factor.  Shrinking each square by EPS before counting atoms is what gives
the certificate its ROBUSTNESS MARGIN (A08 notes sec.5): the exact box verifier needs box widths
below that margin, not below machine epsilon.

EXEMPTION RULE USED HERE (conservative w.r.t. the verifier's):  a placement is dropped from the LP
only if  Q(c,t) shrunk by RHO  meets  P shrunk by RHO  for some piece P; then Q n P contains a ball
of radius RHO and the exact verifier (which searches for a rational point of P inside Q for the
whole placement box) will discharge it as soon as its boxes are finer than RHO.  Every other
placement gets a row, so the LP never assumes an exemption the verifier cannot reproduce.
"""
import argparse
import json
import os
import sys
import time
from fractions import Fraction as F

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

import sstar_geom as G

SP = float(G.SP)
EPS = 1.0 / 64.0            # inward shrink of Q when counting atoms (robustness margin)
RHO = 1.0 / 128.0           # inward shrink used by the LP exemption rule


# ------------------------------------------------------------------ float views of the obstacle
def float_pieces(ob):
    out = []
    for name in G.PIECES:
        hp = np.array([[float(a), float(b), float(c)] for (a, b, c) in ob[name]["halfplanes"]])
        vt = np.array([[float(x), float(y)] for (x, y) in ob[name]["verts"]])
        out.append({"name": name, "hp": hp, "verts": vt})
    return out


def erode(hp, rho):
    n = np.hypot(hp[:, 0], hp[:, 1])
    out = hp.copy()
    out[:, 2] -= rho * n
    return out


def hull(points):
    """monotone chain convex hull (float)."""
    pts = sorted(set(map(tuple, np.round(points, 12))))
    if len(pts) <= 2:
        return np.array(pts)

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo = []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    up = []
    for p in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return np.array(lo[:-1] + up[:-1])


def poly_halfplanes(verts):
    """outward half-planes a.x <= c of a CCW convex polygon."""
    n = len(verts)
    hp = np.zeros((n, 3))
    for i in range(n):
        x0, y0 = verts[i]
        x1, y1 = verts[(i + 1) % n]
        a, b = (y1 - y0), -(x1 - x0)
        hp[i] = (a, b, a * x0 + b * y0)
    return hp


def sq_verts(cos, sin, h):
    """vertices of the square centred at 0, tilt theta, half-width h (edge half-length h)."""
    e1 = np.array([cos, sin]) * h
    e2 = np.array([-sin, cos]) * h
    return np.array([e1 + e2, -e1 + e2, -e1 - e2, e1 - e2])


def exempt_centre_regions(pieces, cos, sin, rho):
    """for each piece: half-planes of the set of centres c for which Q(c,theta) eroded by rho meets
    P eroded by rho  (= Minkowski sum of the two eroded convex bodies)."""
    out = []
    qv = sq_verts(cos, sin, 0.5 - rho)
    for pc in pieces:
        # eroded piece polygon: clip its vertices by the eroded half-planes
        hp = erode(pc["hp"], rho)
        pv = clip_float(pc["verts"], hp)
        if len(pv) < 3:
            out.append(None)
            continue
        sums = (pv[:, None, :] + qv[None, :, :]).reshape(-1, 2)
        H = hull(sums)
        out.append(poly_halfplanes(H))
    return out


def clip_float(verts, hps):
    poly = [tuple(v) for v in verts]
    for (a, b, c) in hps:
        new = []
        n = len(poly)
        if n == 0:
            return np.zeros((0, 2))
        for i in range(n):
            P = poly[i]
            Q = poly[(i + 1) % n]
            fp = a * P[0] + b * P[1] - c
            fq = a * Q[0] + b * Q[1] - c
            if fp <= 0:
                new.append(P)
            if (fp < 0 < fq) or (fq < 0 < fp):
                t = fp / (fp - fq)
                new.append((P[0] + t * (Q[0] - P[0]), P[1] + t * (Q[1] - P[1])))
        poly = new
    return np.array(poly) if poly else np.zeros((0, 2))


# ------------------------------------------------------------------ placements
def tilt_trig(t):
    return (1 - t * t) / (1 + t * t), 2 * t / (1 + t * t)


def placements_for_tilt(t, nc, pieces, rho=None):
    rho = RHO if rho is None else rho
    """returns (cx, cy) arrays of admissible, non-exempt centres on an nc x nc grid."""
    cos, sin = tilt_trig(t)
    w = cos + sin
    lo, hi = w / 2, SP - w / 2
    if lo >= hi:
        return np.zeros(0), np.zeros(0)
    g = np.linspace(0.0, SP, nc)
    g = g[(g >= lo - 1e-12) & (g <= hi + 1e-12)]
    g = np.clip(g, lo, hi)
    if len(g) == 0:
        g = np.array([(lo + hi) / 2])
    CX, CY = np.meshgrid(g, g, indexing="ij")
    cx, cy = CX.ravel(), CY.ravel()
    keep = np.ones(len(cx), bool)
    for M in exempt_centre_regions(pieces, cos, sin, rho):
        if M is None:
            continue
        inside = np.ones(len(cx), bool)
        for (a, b, c) in M:
            inside &= (a * cx + b * cy <= c + 1e-12)
        keep &= ~inside
    return cx[keep], cy[keep]


def rows_mass(atomsX, atomsY, weights, cos, sin, cx, cy, eps=None, chunk=4096):
    eps = EPS if eps is None else eps
    """mass of Q(c,theta) shrunk by eps, for each centre (float)."""
    au = cos * atomsX + sin * atomsY
    av = -sin * atomsX + cos * atomsY
    h = 0.5 - eps
    out = np.empty(len(cx))
    for i in range(0, len(cx), chunk):
        j = min(i + chunk, len(cx))
        cu = cos * cx[i:j] + sin * cy[i:j]
        cv = -sin * cx[i:j] + cos * cy[i:j]
        m = (np.abs(au[None, :] - cu[:, None]) <= h) & (np.abs(av[None, :] - cv[:, None]) <= h)
        out[i:j] = m @ weights
    return out


def row_indices(atomsX, atomsY, cos, sin, cx, cy, eps=None):
    eps = EPS if eps is None else eps
    au = cos * atomsX + sin * atomsY
    av = -sin * atomsX + cos * atomsY
    h = 0.5 - eps
    cu = cos * cx + sin * cy
    cv = -sin * cx + cos * cy
    m = (np.abs(au[None, :] - cu[:, None]) <= h) & (np.abs(av[None, :] - cv[:, None]) <= h)
    r, c = np.nonzero(m)
    return r, c


# ------------------------------------------------------------------ the producer
class Producer:
    """incremental LP producer: rows can be added (grid, violation scan, or exact-verifier
    witnesses) and the LP re-solved, until the EXACT verifier accepts the rounded certificate."""

    def __init__(self, box, na=61, eps=None, rho=None):
        global EPS, RHO
        if eps is not None:
            EPS = float(eps)
        if rho is not None:
            RHO = float(rho)
        self.box = box
        self.na = na
        self.ob = G.build_obstacle(box)
        self.pieces = float_pieces(self.ob)
        ga = np.linspace(0.0, SP, na)
        AX, AY = np.meshgrid(ga, ga, indexing="ij")
        self.aX, self.aY = AX.ravel(), AY.ravel()
        self.nA = len(self.aX)
        self.rowsR, self.rowsC = [], []
        self.nrows = 0
        self.w = None

    # -------- rows
    def _add(self, t, cx, cy):
        if len(cx) == 0:
            return 0
        cos, sin = tilt_trig(t)
        r, c = row_indices(self.aX, self.aY, cos, sin, np.asarray(cx), np.asarray(cy))
        self.rowsR.append(r + self.nrows)
        self.rowsC.append(c)
        self.nrows += len(cx)
        return len(cx)

    def add_grid(self, nc, nt):
        n = 0
        for i in range(nt + 1):
            t = i / nt
            cx, cy = placements_for_tilt(t, nc, self.pieces)
            n += self._add(t, cx, cy)
        return n

    def add_placements(self, plist):
        """plist: iterable of (t, cx, cy) floats (admissibility is the caller's business)."""
        byt = {}
        for (t, cx, cy) in plist:
            byt.setdefault(float(t), []).append((float(cx), float(cy)))
        n = 0
        for t, pts in byt.items():
            cos, sin = tilt_trig(t)
            w = cos + sin
            lo, hi = w / 2, SP - w / 2
            cx = np.clip(np.array([p[0] for p in pts]), lo, hi)
            cy = np.clip(np.array([p[1] for p in pts]), lo, hi)
            n += self._add(t, cx, cy)
        return n

    def add_box_rows(self, boxes, safety=1e-9):
        """ROBUST rows.  boxes: (t0,t1,x0,x1,y0,y1) float placement boxes.  The row counts only the
        atoms that are inside Q(c,theta) for EVERY placement of the box (float interval arithmetic,
        with a safety margin), i.e. exactly what the exact verifier can certify for that box.  A
        robust row therefore makes the verifier discharge the whole box, not just one placement."""
        n = 0
        for (t0, t1, x0, x1, y0, y1) in boxes:
            C0, S0 = tilt_trig(t0)
            C1, S1 = tilt_trig(t1)
            Clo, Chi = min(C0, C1), max(C0, C1)
            Slo, Shi = min(S0, S1), max(S0, S1)
            dx0, dx1 = self.aX - x1, self.aX - x0
            dy0, dy1 = self.aY - y1, self.aY - y0
            a0 = np.minimum(np.minimum(Clo * dx0, Clo * dx1), np.minimum(Chi * dx0, Chi * dx1))
            a1 = np.maximum(np.maximum(Clo * dx0, Clo * dx1), np.maximum(Chi * dx0, Chi * dx1))
            b0 = np.minimum(np.minimum(Slo * dy0, Slo * dy1), np.minimum(Shi * dy0, Shi * dy1))
            b1 = np.maximum(np.maximum(Slo * dy0, Slo * dy1), np.maximum(Shi * dy0, Shi * dy1))
            ok = (a1 + b1 <= 0.5 - safety) & (a0 + b0 >= -0.5 + safety)
            a0 = np.minimum(np.minimum(-Shi * dx0, -Shi * dx1), np.minimum(-Slo * dx0, -Slo * dx1))
            a1 = np.maximum(np.maximum(-Shi * dx0, -Shi * dx1), np.maximum(-Slo * dx0, -Slo * dx1))
            b0 = np.minimum(np.minimum(Clo * dy0, Clo * dy1), np.minimum(Chi * dy0, Chi * dy1))
            b1 = np.maximum(np.maximum(Clo * dy0, Clo * dy1), np.maximum(Chi * dy0, Chi * dy1))
            ok &= (a1 + b1 <= 0.5 - safety) & (a0 + b0 >= -0.5 + safety)
            idx = np.nonzero(ok)[0]
            if len(idx) == 0:
                continue            # infeasible row: skip (the verifier will still complain)
            self.rowsR.append(np.full(len(idx), self.nrows))
            self.rowsC.append(idx)
            self.nrows += 1
            n += 1
        return n

    # -------- LP
    def solve(self):
        A = coo_matrix((np.ones(sum(len(r) for r in self.rowsR)),
                        (np.concatenate(self.rowsR), np.concatenate(self.rowsC))),
                       shape=(self.nrows, self.nA)).tocsr()
        res = linprog(np.ones(self.nA), A_ub=-A, b_ub=-np.ones(self.nrows),
                      bounds=(0, None), method="highs")
        if not res.success:
            raise RuntimeError(f"LP failed: {res.message}")
        self.w = np.maximum(res.x, 0.0)
        return float(self.w.sum())

    def scan(self, nc, nt, w=None, tol=1e-7):
        """violated placements (t, cx, cy) on a fine grid; also returns the min mass."""
        w = self.w if w is None else w
        nz = np.nonzero(w > 1e-12)[0]          # only positive-weight atoms carry mass
        aX, aY, wnz = self.aX[nz], self.aY[nz], w[nz]
        viol, worst = [], 9e9
        for i in range(nt + 1):
            t = i / nt
            cx, cy = placements_for_tilt(t, nc, self.pieces)
            if len(cx) == 0:
                continue
            cos, sin = tilt_trig(t)
            m = rows_mass(aX, aY, wnz, cos, sin, cx, cy)
            if len(m):
                worst = min(worst, float(m.min()))
            bad = np.nonzero(m < 1 - tol)[0]
            for k in bad:
                viol.append((t, float(cx[k]), float(cy[k])))
        return viol, worst

    # -------- rounding
    def finalize(self, scale=F(102, 100), wden=10000):
        keep = np.nonzero(self.w > 1e-9)[0]
        wq, atoms = [], []
        for i in keep:
            wq.append(F(int(np.ceil(float(self.w[i]) * float(scale) * wden)), wden))
            ii, jj = divmod(int(i), self.na)
            atoms.append((G.SP * F(ii, self.na - 1), G.SP * F(jj, self.na - 1)))
        total = sum(wq, F(0))
        return atoms, wq, total, keep


def write_cert(path, box, ob, atoms, weights, total, prov):
    d = {
        "s": str(G.SP), "n": 8,
        "atoms": [[str(x), str(y)] for (x, y) in atoms],
        "weights": [str(w) for w in weights],
        "total": str(total),
        "obstacle": {
            "lambda": str(G.LAM), "delta": str(G.DELTA),
            "param_box": {"y0": [str(box[0]), str(box[1])], "b": [str(box[2]), str(box[3])]},
            "pieces": {name: {"halfplanes": [[str(a), str(b), str(c)] for (a, b, c) in ob[name]["halfplanes"]],
                              "verts": [[str(x), str(y)] for (x, y) in ob[name]["verts"]]}
                       for name in G.PIECES},
        },
        "provenance": dict(prov, producer="A47 sstar_lp.py"),
    }
    with open(path, "w") as fh:
        json.dump(d, fh)
    return d
