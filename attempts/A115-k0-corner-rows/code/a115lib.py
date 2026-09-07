"""A115 shared library -- corner-crowd rows (Lemma CW, k0_blocked_side.md sec 2.4) at the NODE
level of the k0_00 tree.

READ-ONLY discipline: every node json used is COPIED into results/nodes/<nid>.src.json before
anything touches it; the A92 engine is copied verbatim into A115/code (verify_case.py sha256
521cb01fe656707cf134864b75227c6051d43a97253749f50ecd1eb37cbef7af).

Geometry conventions follow corner85 / crowdfam92: for a corner c the D4 map g_c sends c to the
origin with the container in the positive quadrant, and

    mu_c(Q) = f_min_max(g_c(centre), tan(theta_c/2))   (exact min over Q of max(x, y))

so Q meets the CLOSED box [0,a]^2 in c's frame iff mu_c(Q) <= a, and the A90 corner depth is
d_c(Q) = max(0, 1 - mu_c(Q)).
"""
import glob
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
sys.path.insert(0, HERE)

import blas1  # noqa: F401  -- MUST precede numpy
import numpy as np

from corner85 import f_min_max
from caselp92 import Box
import crowdfam92 as CF

S_RAT = "969271/250000"
S0 = 969271.0 / 250000.0
CORNERS = ("BL", "BR", "TL", "TR")

RES = os.path.join(BASE, "results")
LOGS = os.path.join(BASE, "logs")
CERTS = os.path.join(BASE, "certs")
NODES = os.path.join(RES, "nodes")
FAMS = os.path.join(RES, "fams")
for _d in (RES, LOGS, CERTS, NODES, FAMS):
    os.makedirs(_d, exist_ok=True)

A107 = os.path.join(ROOT, "attempts", "A107-shadow-gallery", "results")


# ---------------------------------------------------------------- corner frames
def to_corner(cx, cy, th_rad, corner, s=S0):
    """(u, v, theta) of a pose in corner c's frame (c at the origin, container in x,y >= 0)."""
    if corner == "BL":
        return cx, cy, th_rad
    if corner == "BR":
        return s - cx, cy, -th_rad
    if corner == "TL":
        return cx, s - cy, -th_rad
    return s - cx, s - cy, th_rad


def mu_corner(cx, cy, th_rad, corner, s=S0):
    u, v, t = to_corner(cx, cy, th_rad, corner, s)
    return float(f_min_max(u, v, math.tan(t / 2.0)))


def mus(cx, cy, th_rad, s=S0):
    return {c: mu_corner(cx, cy, th_rad, c, s) for c in CORNERS}


def depth(mu):
    return max(0.0, 1.0 - mu)


# ---------------------------------------------------------------- node sources (READ-ONLY copy)
def extract_index():
    """nid -> record from A107's extract_k0.json (path, src, shard, level, cores, sup, frac...)."""
    d = json.load(open(os.path.join(A107, "extract_k0.json")))
    nodes = d["nodes"] if isinstance(d, dict) and "nodes" in d else d
    return {n["nid"]: n for n in nodes}


def shadow_nodes():
    return json.load(open(os.path.join(A107, "shadow_nodes_k0.json")))


def src_copy(nid, path):
    """copy the campaign's node json into A115/results/nodes/<nid>.src.json (once)."""
    dst = os.path.join(NODES, nid + ".src.json")
    if not os.path.exists(dst):
        with open(os.path.join(ROOT, path), "rb") as f:
            b = f.read()
        with open(dst, "wb") as f:
            f.write(b)
    return dst


# ---------------------------------------------------------------- families
def a_w(delta):
    return CF.a_w(delta)


def fam_path(delta):
    return os.path.join(FAMS, "fam_d%g.json" % round(float(delta), 6))


_FAMC = {}


def get_fam(delta, log=print):
    key = round(float(delta), 6)
    if key in _FAMC:
        return _FAMC[key]
    p = fam_path(delta)
    if os.path.exists(p):
        d = json.load(open(p))
        if d.get("fam_build") == CF.FAM_BUILD:
            fam = CF.from_json(d)
            _FAMC[key] = fam
            log("  fam reused d=%g a_w=%s G/corner=%d E=%d" %
                (delta, str(fam["a"]), fam["n_g_per_corner"], fam["n_e"]))
            return fam
    fam = CF.build(delta, log=log)
    d = CF.to_json(fam)
    d["d4_defect"] = CF.d4_closure_defect(fam)
    json.dump(d, open(p, "w"))
    _FAMC[key] = fam
    return fam


class GCount:
    """per-corner counts for the DILATED outer cover G used by the LP rhs (crowdfam92.GTest with
    the same EPS_ZONE_G / EPS_TH_G).  A unit square meets at most one corner box (the boxes are
    s0 - 2 a_w > sqrt2 apart), so the count is 0 or 1 for an exact pose; the count is returned as
    a sum over corners so that a dilated box straddling two corners can only OVER-count."""

    def __init__(self, fam, eps_zone=CF.EPS_ZONE_G, eps_th=CF.EPS_TH_G):
        self.g = CF.GTest(fam, eps_zone=eps_zone, eps_th=eps_th)

    def counts(self, C, th_deg, extra=0.0):
        g = self.g
        C = np.asarray(C, dtype=float).reshape(-1, 2)
        out = np.zeros(len(C), dtype=int)
        th = th_deg % 90.0
        ez = g.ez + extra
        for corner in CORNERS:
            u = C[:, 0] if corner in ("BL", "TL") else CF.SF - C[:, 0]
            v = C[:, 1] if corner in ("BL", "BR") else CF.SF - C[:, 1]
            thc = th if corner in ("BL", "TR") else 90.0 - th
            uu, vv = u - ez, v - ez
            i0 = np.clip(np.searchsorted(g.xs, uu, side="right") - 1, 0, g.NX - 1)
            inx = uu <= g.xs[-1]
            hit = np.zeros(len(C), dtype=bool)
            for b in g.bins:
                if not (b[0] - g.et <= thc <= b[1] + g.et):
                    continue
                hit |= inx & (vv <= g.ytop[b][i0])
            out += hit.astype(int)
        return out


# ---------------------------------------------------------------- the branched square's budget
def core_plus(box_json):
    """B+ = the poses of a UNIT square that CONTAINS the caselp core K(B) of a node hypothesis box
    B (a109lib.core_plus, verbatim): if Q (half-side 1/2, tilt phi) contains K (half-side a, tilt
    psi, centre k) then a(cos D + sin D) <= 1/2 and |k - q| <= sqrt2 (1/2 - a).  Returns a centre
    box x theta interval containing B+."""
    b = Box.from_json(box_json)
    c = b.core()
    a = float(c.a)
    r = math.sqrt(2.0) * (0.5 - a)
    g = min(math.sqrt(2.0), 0.5 / a) if a > 0 else math.sqrt(2.0)
    dmax = math.degrees(math.asin(min(1.0, g / math.sqrt(2.0)))) - 45.0
    dmax = max(0.0, min(45.0, dmax))
    thK = math.degrees(c.fth)
    return dict(x0=float(c.kx) - r, x1=float(c.kx) + r, y0=float(c.ky) - r, y1=float(c.ky) + r,
                th0=thK - dmax, th1=thK + dmax, a_core=a, radius=r, dtheta=dmax)


def box_rmax(fam, b, hstep=0.01, thstep=0.5):
    """conservative upper bound on the corner-crowd incidence r_G(Q) over every pose Q in the box
    b: grid of pitch <= hstep / thstep with the sample half-cell added to the (already dilated)
    zone tolerance, so the sampling can only OVER-count.  Capped at 1 -- a unit square meets at
    most one corner box (CC-1(ii) with the widening; k0_route.md sec 4.2)."""
    gc = GCount(fam)
    nx = max(2, int(math.ceil((b["x1"] - b["x0"]) / hstep)) + 1)
    ny = max(2, int(math.ceil((b["y1"] - b["y0"]) / hstep)) + 1)
    nt = max(1, int(math.ceil((b["th1"] - b["th0"]) / thstep)) + 1)
    xs = np.linspace(b["x0"], b["x1"], nx)
    ys = np.linspace(b["y0"], b["y1"], ny)
    ths = np.linspace(b["th0"], b["th1"], nt)
    pad = 0.5 * math.hypot((b["x1"] - b["x0"]) / (nx - 1), (b["y1"] - b["y0"]) / (ny - 1)) + 1e-9
    X, Y = np.meshgrid(xs, ys)
    C = np.stack([X.ravel(), Y.ravel()], 1)
    best = 0
    for th in ths:
        v = int(gc.counts(C, float(th) % 90.0, extra=pad).max())
        best = max(best, v)
        if best >= 1:
            break
    return min(best, 1)


def crowd_budget(fam, hyp_json):
    """(B, [r_max per core]) for a node: Lemma CW guarantees 8 corner-crowd incidences among the
    eleven squares; the k conditioned squares are exempt from the LP rows (charged to their
    cores) and may carry up to r_max each, so the squares the LP still pays for carry >= B."""
    rmax = [box_rmax(fam, core_plus(b)) for b in hyp_json.get("boxes", [])]
    return 8 - sum(rmax), rmax


# ---------------------------------------------------------------- misc
def memstat():
    import ctypes

    class MS(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    m = MS()
    m.dwLength = ctypes.sizeof(MS)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return m.ullAvailPageFile / 1048576.0, m.ullAvailPhys / 1048576.0


MIN_FREE_COMMIT_MB = 6144.0
MIN_FREE_PHYS_MB = 3072.0


def gate(log, tag, deadline=None, need=2, sleep=20):
    import time
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
        time.sleep(sleep)


def logger(name):
    import time
    p = os.path.join(LOGS, name)

    def log(*x):
        s = " ".join(str(v) for v in x)
        print(s, flush=True)
        with open(p, "a", encoding="utf-8") as f:
            f.write(time.strftime("[%H:%M:%S] ") + s + "\n")
    return log
