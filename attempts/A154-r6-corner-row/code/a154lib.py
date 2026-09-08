"""A154 shared library -- (R6) the corner-meeting COUNT row, as an LP row.

(R6) is A150 sec 1's proposed consumer of the four-corner mechanism:

    sum over placements p of  [Q_p meets some widened corner box B_c^w]  x_p  >=  8

for every K0-BLOCKED packing.  In the case-LP's measure form this is NOT a row on x but a
right-hand-side lift on the measure plus a budget bonus (Lemma CW, docs/proofs/k0_blocked_side.md
sec 2.4):

    rhs(Q) = 1 + e * [Q in the (dilated outer cover of the) union of the four widened corner boxes]
    budget = budget0 + floor(e * B),     B = 8 - sum over the node's cores of r_max(B+)

so it is EXACTLY A115's `d0` configuration.  Nothing here is new mathematics; A154's job is to
run it on populations A115 did not have (A140's exact axis cores, the converged-alive eleven,
A141's near-misses, A60's alive trump5 nodes) and to add the zero-LP-cost SCREEN that decides
most cells without an LP at all:

    tau(e) is the optimum of an LP whose rhs is affine in e  =>  tau convex, c(e) = dtau/de
    non-decreasing, and c(0+) = max over the OPTIMAL DUAL FACE at e = 0 of the corner incidence
    sum_Q a_Q y_Q.  Therefore for any stored optimal dual y of a CONVERGED node LP,

        c_stored := sum_Q a_Q y_Q  >=  B   ==>   eta(e) = eta0 + (tau(e)-tau0) - floor(eB)
                                              >= eta0 + c(0+) e - eB >= eta0   for every e > 0,

    i.e. the row provably cannot help that cell.  That is a THEOREM about the cell, obtained from
    a file, and it is the only sound direction: c_stored < B is inconclusive and needs the LP.

Read-only discipline: every engine module here is a byte copy of A115's (itself A92's), the frozen
verify_case.py is sha256 521cb01f...; nothing outside attempts/A154-r6-corner-row is written.
"""
import glob
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
sys.path.insert(0, HERE)

import blas1  # noqa: F401  -- MUST precede numpy
import numpy as np  # noqa: E402

import crowdfam92 as CF  # noqa: E402
from corner85 import f_min_max  # noqa: E402
from caselp92 import Box  # noqa: E402

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

A115 = os.path.join(ROOT, "attempts", "A115-k0-corner-rows")
A140 = os.path.join(ROOT, "attempts", "A140-k0-residue-gallery")
A141 = os.path.join(ROOT, "attempts", "A141-polycore-lane")
A60 = os.path.join(ROOT, "attempts", "A60-trump5-campaign")
A115N = os.path.join(A115, "results", "nodes")


# ------------------------------------------------------------------ corner frames (a115lib's)
def to_corner(cx, cy, th_rad, corner, s=S0):
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


# ------------------------------------------------------------------ family (own dir; reuse A115's)
def a_w(delta):
    return CF.a_w(delta)


_FAMC = {}


def get_fam(delta, log=print):
    key = round(float(delta), 6)
    if key in _FAMC:
        return _FAMC[key]
    p = os.path.join(FAMS, "fam_d%g.json" % key)
    if os.path.exists(p):
        d = json.load(open(p))
        if d.get("fam_build") == CF.FAM_BUILD:
            fam = CF.from_json(d)
            _FAMC[key] = fam
            return fam
    fam = CF.build(delta, log=log)
    d = CF.to_json(fam)
    json.dump(d, open(p, "w"))
    _FAMC[key] = fam
    return fam


class GCount:
    """per-corner counts for the DILATED outer cover G (a115lib.GCount, verbatim)."""

    def __init__(self, fam, eps_zone=CF.EPS_ZONE_G, eps_th=CF.EPS_TH_G):
        self.g = CF.GTest(fam, eps_zone=eps_zone, eps_th=eps_th)

    def counts(self, C, th_deg, extra=0.0, corners=CORNERS):
        g = self.g
        C = np.asarray(C, dtype=float).reshape(-1, 2)
        out = np.zeros(len(C), dtype=int)
        th = th_deg % 90.0
        ez = g.ez + extra
        for corner in corners:
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


# ------------------------------------------------------------------ core budget (a115lib's)
def core_plus(box_json):
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


def box_rmax(fam, b, corners=CORNERS, hstep=0.01, thstep=0.5):
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
        v = int(gc.counts(C, float(th) % 90.0, extra=pad, corners=corners).max())
        best = max(best, v)
        if best >= 1:
            break
    return min(best, 1)


def crowd_budget(fam, boxes, corners=CORNERS, pins=()):
    """(B, r_max per conditioned box).  boxes = the node's CONDITIONED boxes (pins excluded).
    B = 2 * len(corners) - sum r_max : the incidences the LP still has to pay for."""
    rmax = [box_rmax(fam, core_plus(b), corners=corners) for b in boxes]
    return 2 * len(corners) - sum(rmax), rmax


# ------------------------------------------------------------------ the screen
def incidence_of_packing(fam, packing, corners=CORNERS, exact=True):
    """c_stored = sum_Q y_Q [Q meets some widened corner box], on a stored dual (fractional)
    packing.  `exact` uses the exact corner functional mu_c <= a_w (corner85.f_min_max) rather
    than the dilated cover G, so it is the TRUE incidence of that dual solution."""
    aw = float(fam["a"])
    tot = 0.0
    hit = 0.0
    per = {c: 0.0 for c in corners}
    for q in packing:
        y = float(q["y"])
        tot += y
        cx, cy, th = float(q["cx"]), float(q["cy"]), float(q["theta"])
        best = None
        for c in corners:
            m = mu_corner(cx, cy, th, c)
            if m <= aw + (0.0 if exact else 1e-12):
                per[c] += y
                best = c
        if best is not None:
            hit += y
    return dict(c=hit, mass=tot, per_corner=per)


# ------------------------------------------------------------------ corpora
def _lp_for(nid):
    for pat in (nid + ".t5.lp.json", nid + ".t4.lp.json"):
        p = os.path.join(A115N, pat)
        if os.path.exists(p):
            return p
    g = sorted(glob.glob(os.path.join(A115N, nid + ".t*.lp.json")))
    return g[-1] if g else None


ELEVEN = [
    ("l1_071", 1, "l1_071_plain_warm.t4.lp.json"),
    ("l1_104", 1, "l1_104_plain_warm.t4.lp.json"),
    ("l1_124", 1, "node_124.t5.lp.json"),
    ("l1_148", 1, "node_148.t5.lp.json"),
    ("l1_153", 1, "node_153.t5.lp.json"),          # Trump-image cell -- canary, must stay alive
    ("l1_158", 1, "node_158.t5.lp.json"),
    ("l1_159", 1, "node_159.t5.lp.json"),
    ("l2_p114_001", 2, "l2_p114_001.t5.lp.json"),
    ("l2_p65_101", 2, "l2_p65_101.t5.lp.json"),
    ("l2_p65_111", 2, "l2_p65_111.t5.lp.json"),
    ("l2_p74_001", 2, "l2_p74_001.t5.lp.json"),
]


def corpus_eleven():
    out = []
    for (cell, lvl, fn) in ELEVEN:
        p = os.path.join(A115N, fn)
        out.append(dict(nid=cell, group="eleven", level=lvl, lp=p, cls="k0_00"))
    return out


def nearmiss_cells():
    """the 44 (cell, corner) near-miss rows of A141 notes/t2_table.md, as distinct cells."""
    p = os.path.join(A141, "notes", "t2_table.md")
    rows, on = [], False
    for ln in open(p, encoding="utf-8"):
        if ln.startswith("## Near-misses"):
            on = True
            continue
        if on and ln.startswith("## "):
            break
        if on and ln.startswith("| `"):
            f = [x.strip() for x in ln.strip().strip("|").split("|")]
            rows.append((f[0].strip("`"), f[1]))
    return rows


def corpus_nearmiss(n=20, seed=154):
    rows = nearmiss_cells()
    seen, cells = set(), []
    for (cell, corner) in rows:
        if cell in seen:
            continue
        seen.add(cell)
        lp = _lp_for(cell)
        if lp:
            cells.append(dict(nid=cell, group="nearmiss", level=None, lp=lp, cls="k0_00",
                              nm_corner=corner))
    random.Random(seed).shuffle(cells)
    return cells[:n]


def open_pool():
    last = {}
    for f in ("t4_runs.jsonl", "t5_runs.jsonl"):
        p = os.path.join(A115, "results", f)
        if not os.path.exists(p):
            continue
        for ln in open(p, encoding="utf-8"):
            ln = ln.strip()
            if ln:
                r = json.loads(ln)
                last[r["nid"]] = r
    out = []
    for nid, r in sorted(last.items()):
        if str(r.get("verdict", "")).upper().startswith("CERTIFIED"):
            continue
        lp = _lp_for(nid)
        if lp:
            out.append((nid, r.get("verdict"), lp))
    return out


def corpus_rand_l1(n=20, seed=1154, exclude=()):
    import re
    pool = [(nid, v, lp) for (nid, v, lp) in open_pool()
            if re.match(r"^(node_\d+|l1_\d+)", nid) and nid not in exclude]
    random.Random(seed).shuffle(pool)
    return [dict(nid=nid, group="rand_l1", level=1, lp=lp, cls="k0_00", a115_verdict=v)
            for (nid, v, lp) in pool[:n]]


TRUMP5_PINS = [(0.5, 0.5), (1.5, 0.5), (0.5, 1.5), (S0 - 0.5, 0.5), (S0 - 0.5, S0 - 0.5)]
TRUMP5_NONSIMPLE = ("TL",)


def corpus_trump5(n=10, seed=605):
    """A60's ALIVE cover nodes: verdict 'refused (tau ... >= budget ...)'."""
    recs = []
    for ln in open(os.path.join(A60, "results", "a60_cover_j0.jsonl"), encoding="utf-8"):
        ln = ln.strip()
        if not ln:
            continue
        r = json.loads(ln)
        if str(r.get("verdict", "")).startswith("refused"):
            p = os.path.join(A60, "results", "nodes", r["tag"] + ".json")
            if os.path.exists(p):
                recs.append(dict(nid=r["tag"], group="trump5", level=0, lp=p, cls="trump5",
                                 a60_tau=r.get("tau"), a60_budget=r.get("budget"),
                                 a60_conv=r.get("converged")))
    random.Random(seed).shuffle(recs)
    return recs[:n]


# ------------------------------------------------------------------ misc (a115lib's gate/logger)
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
