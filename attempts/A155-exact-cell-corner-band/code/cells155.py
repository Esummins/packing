"""A155 -- A143's corner-first level-1 cover, PARAMETRISED BY THE K0-WIDEN PAD.

A143/A150 fix the pad at its window-wide maximum

    w_max = (lambda_max - 1)(1 + sqrt2/2) = 0.0255094...,   lambda_max = s0/3.82,

because their tree is built once at s0 and must carry every side of W = [3.82, s0] by dilation
(k0_route.md sec 4.1, Lemma K0-WIDEN).  A tree built for a DECLARED reach T' (a slab
[s0 - T', s0], i.e. lambda(T') = s0/(s0 - T')) only owes the pad

    w(T') = (lambda(T') - 1)(1 + sqrt2/2) = (T'/(s0 - T'))(1 + sqrt2/2),

and a FIXED-SIDE tree (T' = 0) owes NOTHING: the corner box is the exact closed unit box, which is
also the box the teleport dichotomy (Lemma K0-FREE, k0_route.md sec 3) is stated with.  This module
is A143's `cells143` with `a_w = 1 + w` a parameter of the cover instead of a module constant.
Everything else -- the zone, the 6 x 6 positions x 6 tilt windows, the container+reach clip, the
A131 per-sub-bin clip, the exact rational meet test, the BL transpose canonicalisation -- is A143's,
re-derived here so A155 imports nothing mutable from a prior attempt.

Note the ZONE ITSELF moves with the pad:  z in [1/2, a_w + sqrt2/2]^2, so the six position cells are
0.20118 wide at pad 0 and 0.20543 wide at the full pad.  "216 cells" therefore means the same COVER
STRUCTURE at every pad, not the same boxes.
"""
import math
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
for _p in (os.path.join(ROOT, "attempts", "A57-shadow-trees", "code"),
           os.path.join(ROOT, "attempts", "A132-polygon-core", "code"),
           os.path.join(ROOT, "attempts", "A135-polycore-verifier", "code"),
           HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from caselp import Box, cos_sin_t                       # noqa: E402  (read-only import)

S0 = 969271.0 / 250000.0
LAM_MAX = S0 / 3.82
W_MAX = (LAM_MAX - 1.0) * (1.0 + math.sqrt(0.5))        # 0.0255094...  (A143's A_W - 1)
SQ2H = math.sqrt(0.5)

NPOS = 6
NTILT = 6
TILT_W = 90.0 / NTILT
NSUB = 8


def pad_of_slab(T):
    """the K0-WIDEN pad owed by a tree declared over the slab [s0 - T, s0]."""
    return (T / (S0 - T)) * (1.0 + math.sqrt(0.5))


def slab_of_pad(w):
    """inverse of pad_of_slab."""
    r = w / (1.0 + math.sqrt(0.5))
    return S0 * r / (1.0 + r)


def zone(a_w):
    return 0.5, a_w + SQ2H


def h_of(th_deg):
    t = math.radians(th_deg)
    return 0.5 * (math.cos(t) + math.sin(t))


def h_range(th0, th1):
    vals = [h_of(th0), h_of(th1)]
    lo, hi = min(vals), max(vals)
    if th0 <= 45.0 <= th1:
        hi = SQ2H
    return lo, hi


def clip_box(x0, x1, y0, y1, th0, th1, a_w, s=S0):
    """container clip (the square must fit in [0, s]^2) + reach clip (it must meet [0, a_w]^2)."""
    hlo, hhi = h_range(th0, th1)
    X0 = max(x0, hlo)
    X1 = min(x1, a_w + hhi, s - hlo)
    Y0 = max(y0, hlo)
    Y1 = min(y1, a_w + hhi, s - hlo)
    if X1 <= X0 or Y1 <= Y0:
        return None
    return (X0, X1, Y0, Y1)


def subbin_clip(x0, x1, y0, y1, th0, th1, a_w, nsub=NSUB, s=S0):
    out = []
    for k in range(nsub):
        a = th0 + (th1 - th0) * k / nsub
        b = th0 + (th1 - th0) * (k + 1) / nsub
        c = clip_box(x0, x1, y0, y1, a, b, a_w, s=s)
        if c is not None:
            out.append((a, b, c))
    return out


class Cell:
    __slots__ = ("ix", "iy", "it", "a_w", "raw", "box", "empty", "subbins", "canon",
                 "npos", "ntilt")

    def __init__(self, ix, iy, it, a_w, npos=NPOS, ntilt=NTILT):
        self.ix, self.iy, self.it, self.a_w = ix, iy, it, a_w
        self.npos, self.ntilt = npos, ntilt
        zlo, zhi = zone(a_w)
        w = (zhi - zlo) / npos
        tw = 90.0 / ntilt
        x0, x1 = zlo + ix * w, zlo + (ix + 1) * w
        y0, y1 = zlo + iy * w, zlo + (iy + 1) * w
        th0, th1 = it * tw, (it + 1) * tw
        self.raw = (x0, x1, y0, y1, th0, th1)
        self.subbins = subbin_clip(x0, x1, y0, y1, th0, th1, a_w)
        c = clip_box(x0, x1, y0, y1, th0, th1, a_w)
        self.empty = (c is None) or (not self.subbins)
        self.box = None if self.empty else Box(c[0], c[1], c[2], c[3], th0, th1)
        self.canon = (ix >= iy)

    @property
    def key(self):
        return (self.ix, self.iy, self.it)

    @property
    def name(self):
        return "c1_%d%d_t%d" % (self.ix, self.iy, self.it)

    def to_json(self):
        return dict(name=self.name, ix=self.ix, iy=self.iy, it=self.it, a_w=self.a_w,
                    raw=list(self.raw), canon=bool(self.canon), empty=bool(self.empty),
                    box=(self.box.to_json() if self.box else None),
                    n_subbins=len(self.subbins))


def all_cells(a_w, npos=NPOS, ntilt=NTILT):
    return [Cell(ix, iy, it, a_w, npos, ntilt)
            for ix in range(npos) for iy in range(npos) for it in range(ntilt)]


def transpose_key(k, ntilt=NTILT):
    return (k[1], k[0], ntilt - 1 - k[2])


def pair_canonical(k1, k2, ntilt=NTILT):
    a = tuple(sorted((k1, k2)))
    b = tuple(sorted((transpose_key(k1, ntilt), transpose_key(k2, ntilt))))
    return min(a, b)


# ------------------------------------------------------------------ exact "meets the corner box"
def _verts(cx, cy, t):
    co, si = cos_sin_t(t)
    h = Fr(1, 2)
    e1 = (h * co, h * si)
    e2 = (-h * si, h * co)
    return [(cx + su * e1[0] + sv * e2[0], cy + su * e1[1] + sv * e2[1])
            for su, sv in ((1, 1), (1, -1), (-1, -1), (-1, 1))]


def f_min_max(cx, cy, t):
    """exact min over Q(c, theta) of max(x, y); Q meets the OPEN box [0, a)^2 iff this is < a."""
    V = _verts(cx, cy, t)
    best = None
    for (x, y) in V:
        v = max(x, y)
        best = v if best is None else min(best, v)
    for i in range(4):
        (px, py) = V[i]
        (qx, qy) = V[(i + 1) % 4]
        dx, dy = qx - px, qy - py
        if dx == dy:
            continue
        sfr = (py - px) / (dx - dy)
        if 0 <= sfr <= 1:
            best = min(best, px + sfr * dx)
    return best


def meets_bl_exact(cx, cy, th_deg, a_w):
    t = Fr(math.tan(math.radians(th_deg) / 2.0)).limit_denominator(10 ** 12)
    return float(f_min_max(Fr(cx).limit_denominator(10 ** 12),
                           Fr(cy).limit_denominator(10 ** 12), t)) < a_w


def locate(cx, cy, th_deg, a_w, npos=NPOS, ntilt=NTILT):
    """(ix, iy, it) of the cell containing the pose after the BL transpose canonicalisation."""
    x, y, th = cx, cy, th_deg % 90.0
    if x < y:
        x, y, th = y, x, (90.0 - th) % 90.0
    zlo, zhi = zone(a_w)
    w = (zhi - zlo) / npos
    if not (zlo - 1e-12 <= x <= zhi + 1e-12 and zlo - 1e-12 <= y <= zhi + 1e-12):
        return None
    ix = min(npos - 1, max(0, int((x - zlo) / w)))
    iy = min(npos - 1, max(0, int((y - zlo) / w)))
    it = min(ntilt - 1, max(0, int(th / (90.0 / ntilt))))
    return (ix, iy, it)


# ------------------------------------------------------------------ the pads A155 measures
PADS = [
    ("w0", 0.0, "fixed side (exact unit corner box)"),
    ("w5e-4", pad_of_slab(1e-3), "slab of 1e-3"),
    ("w2.6e-3", pad_of_slab(5e-3), "slab of 5e-3"),
    ("w1.3e-2", pad_of_slab(2.5e-2), "slab of 2.5e-2"),
    ("wmax", W_MAX, "whole window [3.82, s0] (A143/A150)"),
]


if __name__ == "__main__":
    import json
    for tag, w, why in PADS:
        cs = all_cells(1.0 + w)
        live = [c for c in cs if not c.empty]
        zlo, zhi = zone(1.0 + w)
        print("%-8s w=%.7f  slab=%.6f  zone [%.6f, %.6f]  cells %d live %d canon %d  (%s)"
              % (tag, w, slab_of_pad(w), zlo, zhi, len(cs), len(live),
                 sum(1 for c in live if c.canon), why))
    print(json.dumps(all_cells(1.0)[0].to_json()))
