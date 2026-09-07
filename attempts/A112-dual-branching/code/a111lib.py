"""A111 -- load-path branching: shared helpers.

READ-ONLY on every campaign.  Node jsons of A57/A60/A61 are COPIED into
attempts/A111-loadpath-branch/results/nodes/ before anything touches them.

Contents
  * the two shadow families as CLASS-PINNED configurations (S02: 7 slots + 4 free, S07: 6 slots
    + 5 free), with the slot squares on their slot lines at the shadow's own side -- exactly the
    T1 object "class pins fixed, the load-path squares free" (S02's poses are the gallery's, good
    to 2.9e-7; S07's are A108's exact Q(sqrt2) ones, good to 4.4e-16);
  * exact SAT-gap geometry and its INTERVAL version (no finite differences anywhere);
  * the load-path selection census: for a loaded contact, which of the four separating axes and
    which sign of the projection the shadow uses;
  * the memory gate (commit 6144 MB, free physical 3072 MB) and the BLAS pin.
"""
from __future__ import annotations

import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import blas1  # noqa: F401  MUST precede numpy

import ctypes, glob, json, math, time
import numpy as np

BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
RES = os.path.join(BASE, "results")
NODES = os.path.join(RES, "nodes")
LOGS = os.path.join(BASE, "logs")
CERTS = os.path.join(BASE, "certs")
for d in (RES, NODES, LOGS, CERTS):
    os.makedirs(d, exist_ok=True)

S0 = 969271.0 / 250000.0          # 3.877084, the certified side
SHAT = 3.877083590022814
S_RAT = "969271/250000"

MIN_FREE_COMMIT_MB = 6144.0
MIN_FREE_PHYS_MB = 3072.0


# ------------------------------------------------------------------ machine gate
def memstat():
    class MS(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    m = MS()
    m.dwLength = ctypes.sizeof(MS)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return m.ullAvailPageFile / 1048576.0, m.ullAvailPhys / 1048576.0


def gate(log, tag, deadline=None, need=2):
    ok = 0
    while True:
        c, p = memstat()
        if c > MIN_FREE_COMMIT_MB and p > MIN_FREE_PHYS_MB:
            ok += 1
            if ok >= need:
                return True
        else:
            ok = 0
            log("  gate: commit %.0f MB phys %.0f MB -- waiting (%s)" % (c, p, tag))
        if deadline is not None and time.time() > deadline:
            log("  gate: deadline passed, SKIP %s" % tag)
            return False
        time.sleep(15)


# ------------------------------------------------------------------ geometry (floats)
def corners(cx, cy, th):
    c, s = math.cos(th), math.sin(th)
    return [(cx + 0.5 * (dx * c - dy * s), cy + 0.5 * (dx * s + dy * c))
            for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


def half_width(th):
    return (abs(math.cos(th)) + abs(math.sin(th))) / 2.0


AXES = ((0, 0), (0, 1), (1, 0), (1, 1))      # (owner index in the pair, axis 0 = e1 / 1 = e2)


def axis_vec(th, k):
    return (math.cos(th), math.sin(th)) if k == 0 else (-math.sin(th), math.cos(th))


def gap_axis(c1, t1, c2, t2, owner, k):
    """The SAT gap along the k-th edge normal of the `owner` square of the pair (0 = square 1).
    Signed: >= 0 means that axis separates.  Also returns the sign of the projection."""
    (cc, tt), (oc, ot) = ((c1, t1), (c2, t2)) if owner == 0 else ((c2, t2), (c1, t1))
    ax = axis_vec(tt, k)
    proj = (oc[0] - cc[0]) * ax[0] + (oc[1] - cc[1]) * ax[1]
    sup = abs(ax[0] * math.cos(ot) + ax[1] * math.sin(ot)) + abs(-ax[0] * math.sin(ot) + ax[1] * math.cos(ot))
    return abs(proj) - 0.5 - 0.5 * sup, (1 if proj >= 0 else -1)


def sat_gap(c1, t1, c2, t2):
    return max(gap_axis(c1, t1, c2, t2, o, k)[0] for (o, k) in AXES)


def sat_argmax(c1, t1, c2, t2):
    """(owner, k, sign, gap) of the separating axis the configuration actually uses."""
    best = None
    for (o, k) in AXES:
        g, sg = gap_axis(c1, t1, c2, t2, o, k)
        if best is None or g > best[3]:
            best = (o, k, sg, g)
    return best


def wall_gaps(cx, cy, th, s):
    w = half_width(th)
    return dict(left=cx - w, right=s - w - cx, bottom=cy - w, top=s - w - cy)


# ------------------------------------------------------------------ interval arithmetic
class IV:
    """A closed real interval with outward-rounded elementary operations (float arithmetic; the
    monotone envelopes are exact for the operations used, and every result is widened by one ulp
    on each side, so the enclosure is conservative)."""
    __slots__ = ("lo", "hi")

    def __init__(self, lo, hi=None):
        if hi is None:
            hi = lo
        self.lo, self.hi = float(lo), float(hi)
        assert self.lo <= self.hi + 1e-300, (lo, hi)

    def _w(self):
        e = 4 * 2.220446049250313e-16 * max(1.0, abs(self.lo), abs(self.hi))
        return IV(self.lo - e, self.hi + e)

    def __repr__(self):
        return "[%.9g, %.9g]" % (self.lo, self.hi)

    def __add__(self, o):
        o = o if isinstance(o, IV) else IV(o)
        return IV(self.lo + o.lo, self.hi + o.hi)._w()

    def __sub__(self, o):
        o = o if isinstance(o, IV) else IV(o)
        return IV(self.lo - o.hi, self.hi - o.lo)._w()

    def __neg__(self):
        return IV(-self.hi, -self.lo)

    def __mul__(self, o):
        o = o if isinstance(o, IV) else IV(o)
        p = (self.lo * o.lo, self.lo * o.hi, self.hi * o.lo, self.hi * o.hi)
        return IV(min(p), max(p))._w()

    __rmul__ = __mul__
    __radd__ = __add__

    def __rsub__(self, o):
        return IV(o) - self

    def abs(self):
        if self.lo >= 0:
            return IV(self.lo, self.hi)
        if self.hi <= 0:
            return IV(-self.hi, -self.lo)
        return IV(0.0, max(-self.lo, self.hi))

    def sign(self):
        """+1 / -1 if the interval is strictly one-signed, 0 otherwise."""
        if self.lo > 0:
            return 1
        if self.hi < 0:
            return -1
        return 0


def iv_cos(t):
    """cos over an interval of angles (radians), outward rounded."""
    lo, hi = t.lo, t.hi
    if hi - lo >= 2 * math.pi:
        return IV(-1.0, 1.0)
    vals = [math.cos(lo), math.cos(hi)]
    k0 = math.ceil(lo / math.pi)
    k = k0
    while k * math.pi <= hi:
        vals.append(1.0 if k % 2 == 0 else -1.0)
        k += 1
    return IV(min(vals), max(vals))._w()


def iv_sin(t):
    return iv_cos(t - IV(math.pi / 2))


def iv_axis(th, k):
    return (iv_cos(th), iv_sin(th)) if k == 0 else (-iv_sin(th), iv_cos(th))


def iv_gap_axis(B1, B2, owner, k):
    """Interval enclosure of the SAT gap along the k-th normal of the `owner` square, over the
    product of two pose boxes B = (xIV, yIV, thIV).  Also returns the enclosure of the SIGNED
    projection (whose sign is the second half of a selection)."""
    (cx, cy, tt), (ox, oy, ot) = (B1, B2) if owner == 0 else (B2, B1)
    ax, ay = iv_axis(tt, k)
    proj = (ox - cx) * ax + (oy - cy) * ay
    cO, sO = iv_cos(ot), iv_sin(ot)
    sup = (ax * cO + ay * sO).abs() + ((-ax) * sO + ay * cO).abs()
    return proj.abs() - IV(0.5) - IV(0.5) * sup, proj


def w_range(t0, t1):
    """(min, max) of w(theta) = |cos theta| + |sin theta| over [t0, t1] radians, EXACTLY.
    w has period pi/2, equals cos+sin on [0, pi/2] with max sqrt2 at pi/4 and min 1 at the ends,
    so the extrema over an interval are at its endpoints and at the multiples of pi/4 inside."""
    if t1 - t0 >= math.pi / 2:
        return 1.0, math.sqrt(2.0)
    def f(t):
        return abs(math.cos(t)) + abs(math.sin(t))
    vals = [f(t0), f(t1)]
    k = math.ceil(t0 / (math.pi / 4))
    while k * math.pi / 4 <= t1:
        vals.append(f(k * math.pi / 4))
        k += 1
    e = 1e-14
    return min(vals) - e, max(vals) + e


def box_iv(b):
    """(xIV, yIV, thIV in radians) from a dict with x0/x1/y0/y1/th0/th1 (degrees)."""
    return (IV(b["x0"], b["x1"]), IV(b["y0"], b["y1"]),
            IV(math.radians(b["th0"]), math.radians(b["th1"])))


# ------------------------------------------------------------------ the two shadows
S02_FREE = {                       # docs/shadows.md sec S02, the gallery landing at s* = 3.886746030
    "f0": (2.167757, 1.519508, 48.4351),
    "f1": (1.265647, 2.432705, 48.4351),
    "f2": (1.929115, 3.180910, 48.4351),
    "f3": (2.621099, 2.454041, 48.4351),
}
S02_SLOTS = ("BL(0,0)", "BL(0,1)", "BL(1,0)", "BR(0,0)", "BR(0,1)", "TL(0,0)", "TR(0,0)")
S02_S = 3.886746030
S02_LOADPATH = ("f1", "f2", "f3")            # A110 sec 2.2 (f0 is the strut/rattler)

S07_SLOTS = ("BL(0,0)", "BL(0,1)", "BL(0,2)", "BL(1,0)", "BR(0,0)", "TR(0,0)")
S07_S = 2 + 4 * math.sqrt(2) / 3
S07_FREE = {                       # attempts/A108-s07-certify/results/exact.json (Q(sqrt2), 45 deg)
    "f0": (1 + math.sqrt(2) / 2, 1 + 2 * math.sqrt(2) / 3, 45.0),
    "f1": (2 - math.sqrt(2) / 3, 2 + 5 * math.sqrt(2) / 6, 45.0),
    "f2": (1 + math.sqrt(2), 1 + 7 * math.sqrt(2) / 6, 45.0),
    "f3": (19.0 / 6, 1.5 + math.sqrt(2) / 3, 45.0),
    "f4": (1.5 + 2 * math.sqrt(2) / 3, 1.5 - math.sqrt(2) / 6, 45.0),
}
S07_LOADPATH = ("f0", "f1", "f2", "f4")      # A110 sec 2.1 (f3 is the rattler)


def slot_xy(name, s):
    """centre of a named slot cell at side s (A107 shadowlib.slot_cells)."""
    corner, ij = name[:2], name[3:-1].split(",")
    i, j = int(ij[0]), int(ij[1])
    x = 0.5 + i if corner in ("BL", "TL") else s - 0.5 - i
    y = 0.5 + j if corner in ("BL", "BR") else s - 0.5 - j
    return (x, y)


def shadow(tag):
    """(s, names, cfg, slot_names, free_names, loadpath) of the class-pinned shadow."""
    if tag == "S02":
        s, slots, free, lp = S02_S, S02_SLOTS, S02_FREE, S02_LOADPATH
    else:
        s, slots, free, lp = S07_S, S07_SLOTS, S07_FREE, S07_LOADPATH
    names = list(free) + list(slots)
    cfg = [(free[n][0], free[n][1], math.radians(free[n][2])) for n in free]
    cfg += [(slot_xy(n, s)[0], slot_xy(n, s)[1], 0.0) for n in slots]
    return s, names, cfg, list(slots), list(free), list(lp)


def worst_gap(s, cfg):
    """(worst pair SAT gap, worst wall gap) of a configuration."""
    wp = 1e9
    for i in range(len(cfg)):
        for j in range(i + 1, len(cfg)):
            wp = min(wp, sat_gap(cfg[i][:2], cfg[i][2], cfg[j][:2], cfg[j][2]))
    ww = min(min(wall_gaps(q[0], q[1], q[2], s).values()) for q in cfg)
    return wp, ww


# ------------------------------------------------------------------ node index (read-only)
SRC_GLOB = {
    "A57": "attempts/A57-shadow-trees/results/tree/*/*.json",
    "A60": "attempts/A60-trump5-campaign/results/nodes/*.json",
    "A61": "attempts/A61-window-stragglers/results/nodes/*.json",
}
_INDEX = None


def node_index():
    global _INDEX
    if _INDEX is None:
        _INDEX = {}
        for src, pat in SRC_GLOB.items():
            for p in glob.glob(os.path.join(ROOT, pat)):
                nid = os.path.splitext(os.path.basename(p))[0]
                _INDEX.setdefault((src, nid), p)
                _INDEX.setdefault(nid, p)
    return _INDEX


def copy_node(nid, src=None):
    dst = os.path.join(NODES, nid + ".src.json")
    if not os.path.exists(dst):
        p = node_index().get((src, nid)) or node_index().get(nid)
        if p is None:
            return None
        with open(p, "rb") as f:
            b = f.read()
        with open(dst, "wb") as f:
            f.write(b)
    return dst


# ------------------------------------------------------------------ D4 (A107 shadowlib.d4_ops)
def d4_ops(s):
    return {
        "e":    lambda x, y, t: (x, y, t),
        "r90":  lambda x, y, t: (s - y, x, t),
        "r180": lambda x, y, t: (s - x, s - y, t),
        "r270": lambda x, y, t: (y, s - x, t),
        "mx":   lambda x, y, t: (s - x, y, -t),
        "my":   lambda x, y, t: (x, s - y, -t),
        "diag": lambda x, y, t: (y, x, -t),
        "anti": lambda x, y, t: (s - y, s - x, -t),
    }


D4_INV = {"e": "e", "r90": "r270", "r180": "r180", "r270": "r90",
          "mx": "mx", "my": "my", "diag": "diag", "anti": "anti"}


def tmod_deg(t_rad):
    return math.degrees(t_rad) % 90.0
