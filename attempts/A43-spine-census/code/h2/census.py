#!/usr/bin/env python3
"""A43-H2 census layer: the C0/C1/C2 ablation stages, the reachable-window
extraction, C3/C4/C5/C6 columns, and the anchor count.

Ablation semantics (formalization.md Part 2, 'Ablation order'):
  raw : all types of length k, up to reversal symmetry.
  C0  : span identity + containment + consecutive distance ONLY.  Every square's
        tilt window is the full [0, 90] deg gauge range EXCEPT a wall-flush end,
        whose phi = 0 is part of the END IDENTITY (span arithmetic), not of the
        tilt-coupling subsystem.  Link dx sets are the branch unions over those
        full windows with the tilt-coupling (zero-class) rules switched OFF.
  +C1 : tilt-coupling feasibility (A31 level1 semantics), applied structurally --
        FL merges classes, wall-flush pins a class to 0, CE forces a strict
        inequality between two classes, the zero class has in-degree 0, and a
        wall-corner end may not sit in a zero class.  On a PATH the class digraph
        is itself a path (possibly closed into one cycle when both ends are F), so
        an acyclic orientation with the zero class as a source always exists once
        those local rules hold: C1 reduces EXACTLY to the local rules.
  +C2 : 3-degree tilt bins x span propagation (the layered DP in spine.Geom) plus
        the y-column capacity lemma on the propagated windows.
  +C3 : per-square tight-variety cut (W1) over the propagated windows.
  +C4 : A25 interface-wastage budget over the propagated windows.
"""
from __future__ import annotations

import math

import numpy as np

import spine as S
from ivl import I, h_deg, SQRT2

FULL = (0.0, 90.0)


# --------------------------------------------------------------------- C0
def end_window(e):
    """Certified tilt window of an end square from the END IDENTITY alone."""
    return (0.0, 0.0) if e == S.END_F else FULL


def c0_alive(s, eL, eR, links, windows=None, zero=None):
    """Interval feasibility of span + containment + consecutive distance."""
    k = len(links) + 1
    if windows is None:
        windows = [FULL] * k
        windows[0] = end_window(eL)
        windows[-1] = end_window(eR)
    if zero is None:
        zero = [False] * k
    H = [h_deg(*w) for w in windows]
    X = I(H[0].lo, H[0].hi)                       # x_1 = h(phi_1)
    for i in range(k - 1):
        br = S.branches_p(links[i], windows[i], windows[i + 1],
                          zero[i], zero[i + 1])
        if not br:
            return False
        D = I(min(d.lo for _, d in br), max(d.hi for _, d in br))
        X = X + D
        box = I(H[i + 1].lo, s - H[i + 1].lo)     # containment (outward)
        X = X.inter(box)
        if X is None:
            return False
    end = I(s - H[-1].hi, s - H[-1].lo)           # x_k = s - h(phi_k)
    return X.inter(end) is not None


def runs_of(links):
    k = len(links) + 1
    run = [0] * k
    for i in range(1, k):
        run[i] = run[i - 1] if links[i - 1] == S.FL else run[i - 1] + 1
    return run, run[-1] + 1


def c1_structural(eL, eR, links):
    """Tilt-coupling feasibility (see module docstring).  Returns
    (ok, zero_run_set)."""
    run, nrun = runs_of(links)
    zr = set()
    if eL == S.END_F:
        zr.add(run[0])
    if eR == S.END_F:
        zr.add(run[-1])
    if eL == S.END_C and run[0] in zr:
        return False, zr
    if eR == S.END_C and run[-1] in zr:
        return False, zr
    for i, t in enumerate(links):
        if t in (S.CEAB, S.CEBA) and run[i] in zr and run[i + 1] in zr:
            return False, zr                 # strict edge between zero classes
    return True, zr


def c0c1_alive(s, eL, eR, links):
    ok, zr = c1_structural(eL, eR, links)
    if not ok:
        return False
    run, nrun = runs_of(links)
    k = len(links) + 1
    windows = [(0.0, 0.0) if run[i] in zr else FULL for i in range(k)]
    zero = [run[i] in zr for i in range(k)]
    return c0_alive(s, eL, eR, links, windows, zero)


# --------------------------------------------------------------------- C2
def reach(geo, eL, eR, links):
    """Forward-and-backward reachable (state, cell) sets per position.
    Returns None if the type is C0-C2 dead, else a list of boolean vectors."""
    k = len(links) + 1
    pins = geo.pins(k)
    F = [geo.start_vec(eL)]
    for t, (a, b) in zip(links, pins):
        v = geo.step(F[-1], t, a, b)
        if not v.any():
            return None
        F.append(v)
    B = [None] * k
    B[k - 1] = geo.end_mask(eR)
    for i in range(k - 2, -1, -1):
        T = geo.trans(links[i], pins[i][0], pins[i][1])
        idx = np.flatnonzero(B[i + 1])
        B[i] = T[:, idx].any(axis=1) if idx.size else np.zeros_like(B[i + 1])
    R = [F[i] & B[i] for i in range(k)]
    if any(not r.any() for r in R):
        return None
    return R


def windows_from_reach(geo, R):
    """Per-square certified (tilt window, x window) from the reachable sets."""
    out = []
    for r in R:
        idx = np.flatnonzero(r)
        st = sorted(set(int(i) // geo.ncell for i in idx))
        cl = sorted(set(int(i) % geo.ncell for i in idx))
        plo = min(S.st_phi(x)[0] for x in st)
        phi = max(S.st_phi(x)[1] for x in st)
        xlo = min(geo.cells[c].lo for c in cl)
        xhi = max(geo.cells[c].hi for c in cl)
        out.append(dict(states=st, cells=cl, phi=(plo, phi), x=(xlo, xhi)))
    return out


def capacity_kill(geo, R):
    """C2b: the y-column capacity lemma applied to the propagated x windows.
    Kill only if violated for EVERY realization, i.e. using the tightest
    certified per-square windows."""
    xw = []
    for r in R:
        idx = np.flatnonzero(r)
        cl = sorted(set(int(i) % geo.ncell for i in idx))
        xw.append((geo.cells[cl[0]].lo, geo.cells[cl[-1]].hi))
    from canary import capacity_ok
    return not capacity_ok(xw, geo.s)


# ---------------------------------------------------------------- C3 / C4
class Columns:
    """Cached per-(state, cell) evaluations of the W1 field cut and the A25
    wastage atlas, with y ranging over its FULL certified window (the spine
    pins no transverse coordinate -- that is the measurement)."""

    def __init__(self, geo, field=None, atlas=None):
        self.geo = geo
        self.field = field
        self.atlas = atlas
        self._m = {}
        self._a = {}

    def mlow(self, st, ci):
        if self.field is None:
            return None
        key = (st, ci)
        if key in self._m:
            return self._m[key]
        import fieldx
        from ivl import tan_half_deg
        g = self.geo
        A = g.cellbox(st, ci)
        h = S.st_h(st)
        p = S.st_phi(st)
        t = tan_half_deg(*p)
        ylo, yhi = h.lo, g.s - h.lo
        v = fieldx.mlow(max(0.0, t.lo), min(1.0, t.hi),
                        A.lo, A.hi, ylo, yhi)
        self._m[key] = v
        return v

    def wastage(self, st, ci):
        """(Fraction lower bound, regions) from the A25 single atlas."""
        if self.atlas is None:
            return None, []
        key = (st, ci)
        if key in self._a:
            return self._a[key]
        from fractions import Fraction as Fr
        g = self.geo
        A = g.cellbox(st, ci)
        h = S.st_h(st)
        p = S.st_phi(st)
        v, r = self.atlas.lookup((Fr(A.lo), Fr(A.hi)),
                                 (Fr(h.lo), Fr(g.s - h.lo)), p)
        self._a[key] = (v, r)
        return v, r

    def c3_kill(self, R, thr):
        """Kill iff SOME square's every reachable window certifies mlow > thr."""
        if self.field is None:
            return False, None
        best = None
        for r in R:
            idx = np.flatnonzero(r)
            mn = min(self.mlow(int(i) // self.geo.ncell, int(i) % self.geo.ncell)
                     for i in idx)
            best = mn if best is None else max(best, mn)
            if mn > thr:
                return True, mn
        return False, best

    def c4_floor(self, R):
        """Conservative certified wastage FLOOR: sum over squares of the minimum
        atlas value over that square's reachable windows.  (min of a sum >= sum
        of the mins, so this under-states the true floor -- conservative.)"""
        if self.atlas is None:
            return None
        from fractions import Fraction as Fr
        tot = Fr(0)
        per = []
        for r in R:
            idx = np.flatnonzero(r)
            mn = None
            for i in idx:
                v, _ = self.wastage(int(i) // self.geo.ncell,
                                    int(i) % self.geo.ncell)
                mn = v if mn is None else min(mn, v)
                if mn == 0:
                    break
            per.append(mn)
            tot += mn
        return tot, per


# --------------------------------------------------------------- C5 / C6
THM3_BINS = set()
for _b in range(S.NBIN):
    _lo, _hi = S.BW * _b, S.BW * (_b + 1)
    if (18.0 <= _lo and _hi <= 27.0) or (63.0 <= _lo and _hi <= 72.0):
        THM3_BINS.add(_b)


def c5_column(geo, R):
    """True iff EVERY branch forces EVERY tilt into (18,27) u (63,72)."""
    for r in R:
        idx = np.flatnonzero(r)
        sts = set(int(i) // geo.ncell for i in idx)
        if any(st not in THM3_BINS for st in sts):
            return False
    return True


def c6_column(geo, R):
    """N8 band count: number of spine squares for which the wall clearance
    R = d(centre, nearest wall) - h(theta) >= w is CERTIFIED, w > (s-2)/2.
    y is free over [h, s-h], so min(y, s-y) can be as small as h and the
    certified clearance lower bound is <= 0 for every square: the column is
    identically 0 here.  Computed rather than assumed."""
    w = (geo.s - 2.0) / 2.0
    n = 0
    for r in R:
        idx = np.flatnonzero(r)
        lo = None
        for i in idx:
            st, ci = int(i) // geo.ncell, int(i) % geo.ncell
            A = geo.cellbox(st, ci)
            h = S.st_h(st)
            dx = min(A.lo, geo.s - A.hi)
            dy = h.lo                       # free y: nearest-wall distance >= h
            v = min(dx, dy) - h.hi
            lo = v if lo is None else min(lo, v)
        if lo is not None and lo >= w:
            n += 1
    return n, w


# --------------------------------------------------------------- anchors
def anchor_count(geo, eL, eR, links):
    """Arc-consistent count of surviving floor anchors
    (tilt-bin per class x geometric branch per link x x-cell per square).
    UPPER BOUND: arc (pairwise) consistency is exact for a chain only when the
    per-anchor propagation is run, and this DP relaxes to pairwise cell tests."""
    v = geo.start_vec(eL).astype(np.float32)
    for t, (a, b) in zip(links, geo.pins(len(links) + 1)):
        v = v @ geo.mult(t, a, b)
        if not v.any():
            return 0.0
    return float(v[geo.end_mask(eR)].sum())
