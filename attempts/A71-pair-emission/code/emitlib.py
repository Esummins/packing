r"""
A71 T1 emission library (Fable lead).  Float-side machinery for the certification-in-the-loop
emission of pair-certificate-v1 certificates against the FROZEN verifier
attempts/A66-corners4-pair/code/verify_pair.py (sha256 d9b7a24a...662d, never modified).

Conventions mirror the verifier EXACTLY:
  * t = tan(theta/2) in [0,1]; cos = (1-t^2)/(1+t^2), sin = 2t/(1+t^2)
  * body frame PINNED as u = C*dx + S*dy, v = -S*dx + C*dy, d = p - c
    (p in Q(c,theta) iff |u|,|v| <= 1/2)
  * NONDISJOINT/EXEMPT thresholds as in spec docs/specs/pair_certificate_v1.md sect. 3.
Emission-side admissibility (row quantifier) uses the WEAK (correct) core test:
  Q separated from axis core (kx,ky,a) iff |dx|>=a+w/2 or |dy|>=a+w/2 or |u|>=1/2+a*w
  or |v|>=1/2+a*w  (body-axis thresholds differ from the coordinate-axis ones; pairlp.py's
  single-threshold filter is stricter on body axes and must NOT be used for row generation).
All float; the FINAL certificate is emitted in exact rationals and judged only by the frozen
verifier.  Floats here can cause missed rows (loop iterates) never an unsound accept.
"""
import os
for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json, math, time, sys
from fractions import Fraction as Fr
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(BASE, "..", ".."))
BOXSPEC = os.path.join(REPO, "attempts", "A65-low-k-closure", "results", "h10_boxspec.json")
CROWDFAM = os.path.join(REPO, "attempts", "A65-low-k-closure", "results", "crowdfam.json")
OCCM = os.path.join(REPO, "attempts", "A58-clear-corner", "results", "occupancy_matrix.json")
VERIFY_PAIR = os.path.join(REPO, "attempts", "A66-corners4-pair", "code", "verify_pair.py")

S0F = Fr(969271, 250000)
S0 = float(S0F)
SHAT = 3.877083590022814          # attained side (Trump), float; used only in the canary


def log(msg, fh=None):
    line = "[%s] %s" % (time.strftime("%H:%M:%S"), msg)
    print(line, flush=True)
    if fh is not None:
        fh.write(line + "\n")
        fh.flush()


# ---------------------------------------------------------------- class data
class ClassData(object):
    """Certificate-side data for one class at side s (floats + exact originals)."""

    def __init__(self, cls, delta=Fr(1, 1000), eps_box=Fr(1, 833), s=S0F):
        spec = json.load(open(BOXSPEC))
        if cls == "trump5":
            # not in the boxspec (k=5 canary class): slots hard-coded from
            # occupancy_matrix.json trump_canary + A58 sect. 2; unclipped boxes = the 6
            # canary boxes (BL_20/BR_10 are pin-clipped).
            h, s_ = Fr(1, 2), s
            pins = [(h, h), (Fr(3, 2), h), (h, Fr(3, 2)), (s_ - h, h), (s_ - h, s_ - h)]
            boxes = [(h, Fr(5, 2)), (Fr(3, 2), Fr(3, 2)), (s_ - h, Fr(3, 2)),
                     (s_ - h, s_ - Fr(3, 2)), (s_ - Fr(3, 2), s_ - h), (h, s_ - h)]
            self.N, self.k = 6, 5
        else:
            e = spec["classes"][cls]
            scale = s / S0F
            # slots are alpha + beta*s with beta in {0,1}: re-evaluate at s from the s0 values
            def at_s(q):
                q = Fr(q)
                return q if q < Fr(3) else q - S0F + s     # beta=1 slots are within 5/2 of s0
            pins = [(at_s(a), at_s(b)) for a, b in e["pins"]]
            boxes = [(at_s(b["slot"][0]), at_s(b["slot"][1])) for b in e["boxes"]]
            self.N, self.k = int(e["N"]), int(e["k"])
        self.cls = cls
        self.sF = s
        self.s = float(s)
        self.deltaF = Fr(delta)
        self.delta = float(delta)
        self.aF = Fr(1, 2) - Fr(delta)            # slack core half-side
        self.a = float(self.aF)
        self.eps_boxF = Fr(eps_box)
        self.hF = Fr(1, 2) + Fr(eps_box)          # widened box half-side
        self.h = float(self.hF)
        self.pinsF = pins
        self.boxesF = boxes
        self.pins = np.array([[float(a), float(b)] for a, b in pins])
        self.boxes = np.array([[float(a), float(b)] for a, b in boxes])
        self.m = len(boxes)
        self.thresh_base = self.N * (self.N - 1) // 2

    def threshold(self, beta):
        return self.thresh_base + beta * self.m


# ---------------------------------------------------------------- geometry (vectorised)
def cs_of_t(t):
    t = np.asarray(t, dtype=float)
    d = 1.0 + t * t
    return (1.0 - t * t) / d, 2.0 * t / d


def width_of_t(t):
    C, S = cs_of_t(t)
    return C + S            # t in [0,1] => both nonneg


def contain_margin(t, cx, cy, s):
    w = width_of_t(t)
    h = 0.5 * w
    return np.minimum.reduce([cx - h, cy - h, s - cx - h, s - cy - h])


def core_sep_margin(t, cx, cy, cd):
    """(n,) float: min over cores of (max over the 4 separating directions of |proj|-thr).
    >= 0 means the placement meets NO slack core (weak/correct per-axis thresholds)."""
    C, S = cs_of_t(t)
    w = C + S
    a = cd.a
    out = np.full(len(np.atleast_1d(t)), np.inf)
    for (kx, ky) in cd.pins:
        dx = cx - kx
        dy = cy - ky
        m = np.maximum.reduce([
            np.abs(dx) - (a + 0.5 * w), np.abs(dy) - (a + 0.5 * w),
            np.abs(dx * C + dy * S) - (0.5 + a * w),
            np.abs(dy * C - dx * S) - (0.5 + a * w)])
        out = np.minimum(out, m)
    return out


def box_meet_margins(t, cx, cy, cd):
    """(n, m) float: SAT-converse margin of 'open interior of Q meets open interior of
    widened box i' -- min over the 4 directions of (thr - |proj|); > 0 means meets."""
    C, S = cs_of_t(t)
    w = C + S
    h = cd.h
    n = len(np.atleast_1d(t))
    out = np.empty((n, cd.m))
    for i, (bx, by) in enumerate(cd.boxes):
        dx = cx - bx
        dy = cy - by
        out[:, i] = np.minimum.reduce([
            (h + 0.5 * w) - np.abs(dx), (h + 0.5 * w) - np.abs(dy),
            (0.5 + h * w) - np.abs(dx * C + dy * S),
            (0.5 + h * w) - np.abs(dy * C - dx * S)])
    return out


def sat_gap_pairs(tA, cxA, cyA, tB, cxB, cyB):
    """(n,) float max-over-4-normals SAT gap; >= 0 iff interiors disjoint."""
    CA, SA = cs_of_t(tA)
    CB, SB = cs_of_t(tB)
    dx = cxB - cxA
    dy = cyB - cyA
    g = np.abs(CA * CB + SA * SB) + np.abs(SA * CB - CA * SB)
    bound = 0.5 + 0.5 * g
    best = np.full(dx.shape, -np.inf)
    for (C, S) in ((CA, SA), (CB, SB)):
        best = np.maximum(best, np.abs(dx * C + dy * S) - bound)
        best = np.maximum(best, np.abs(dy * C - dx * S) - bound)
    return best


def point_depth(t, cx, cy, px, py):
    """depth of point (px,py) in the placement (t,cx,cy): 1/2 - max(|u|,|v|); > 0 inside.
    Broadcasting: placement arrays (n,), points (k,) -> (n,k)."""
    C, S = cs_of_t(t)
    dx = px[None, :] - cx[:, None]
    dy = py[None, :] - cy[:, None]
    u = dx * C[:, None] + dy * S[:, None]
    v = dy * C[:, None] - dx * S[:, None]
    return 0.5 - np.maximum(np.abs(u), np.abs(v))


# ---------------------------------------------------------------- placements
class Placements(object):
    """columnar store of placements (t, cx, cy) with cached per-placement data."""

    def __init__(self, cd, t, cx, cy):
        self.cd = cd
        self.t = np.asarray(t, float)
        self.cx = np.asarray(cx, float)
        self.cy = np.asarray(cy, float)
        self.n = len(self.t)
        self.contain = contain_margin(self.t, self.cx, self.cy, cd.s)
        self.coresep = core_sep_margin(self.t, self.cx, self.cy, cd)
        self.boxm = box_meet_margins(self.t, self.cx, self.cy, cd)
        self.admissible = (self.contain >= 0.0) & (self.coresep >= 0.0)

    @classmethod
    def concat(cls, cd, parts):
        t = np.concatenate([p.t for p in parts])
        cx = np.concatenate([p.cx for p in parts])
        cy = np.concatenate([p.cy for p in parts])
        return cls(cd, t, cx, cy)


def sample_placements(cd, tvals, cstep, rng=None, jitter=0.0):
    """grid placements at given tilts, admissibility-filtered."""
    T, X, Y = [], [], []
    for t in tvals:
        w = float(width_of_t(np.array([t]))[0])
        lo, hi = 0.5 * w, cd.s - 0.5 * w
        v = np.arange(lo, hi + 1e-12, cstep)
        if len(v) == 0 or v[-1] < hi - 1e-9:
            v = np.append(v, hi)
        XX, YY = np.meshgrid(v, v, indexing="ij")
        x = XX.ravel()
        y = YY.ravel()
        if jitter > 0 and rng is not None:
            x = np.clip(x + rng.uniform(-jitter, jitter, len(x)), lo, hi)
            y = np.clip(y + rng.uniform(-jitter, jitter, len(y)), lo, hi)
        T.append(np.full(len(x), float(t)))
        X.append(x)
        Y.append(y)
    P = Placements(cd, np.concatenate(T), np.concatenate(X), np.concatenate(Y))
    keep = P.admissible
    return Placements(cd, P.t[keep], P.cx[keep], P.cy[keep])


# ---------------------------------------------------------------- rows
class RowSet(object):
    """rows = ordered arrays over row index: (iA fields, iB fields, m2, rhs) with dedupe."""

    def __init__(self, cd, beta):
        self.cd = cd
        self.beta = beta
        self.tA = []; self.xA = []; self.yA = []
        self.tB = []; self.xB = []; self.yB = []
        self.m2 = []
        self.keys = set()
        self.tag = []

    def add_pairs(self, PA_t, PA_x, PA_y, PB_t, PB_x, PB_y, tag=""):
        """adds admissible disjoint pairs from parallel arrays; returns #added."""
        cd = self.cd
        tA = np.asarray(PA_t, float); xA = np.asarray(PA_x, float); yA = np.asarray(PA_y, float)
        tB = np.asarray(PB_t, float); xB = np.asarray(PB_x, float); yB = np.asarray(PB_y, float)
        A = Placements(cd, tA, xA, yA)
        B = Placements(cd, tB, xB, yB)
        gap = sat_gap_pairs(tA, xA, yA, tB, xB, yB)
        ok = A.admissible & B.admissible & (gap >= 0.0)
        idx = np.nonzero(ok)[0]
        added = 0
        mA = A.boxm > 0.0
        mB = B.boxm > 0.0
        m2v = (mA & mB).sum(axis=1)
        for i in idx:
            key = tuple(np.round([tA[i], xA[i], yA[i], tB[i], xB[i], yB[i]], 7))
            key2 = tuple(np.round([tB[i], xB[i], yB[i], tA[i], xA[i], yA[i]], 7))
            if key in self.keys or key2 in self.keys:
                continue
            self.keys.add(key)
            self.tA.append(tA[i]); self.xA.append(xA[i]); self.yA.append(yA[i])
            self.tB.append(tB[i]); self.xB.append(xB[i]); self.yB.append(yB[i])
            self.m2.append(int(m2v[i]))
            self.tag.append(tag)
            added += 1
        return added

    def arrays(self):
        return (np.array(self.tA), np.array(self.xA), np.array(self.yA),
                np.array(self.tB), np.array(self.xB), np.array(self.yB),
                np.array(self.m2, dtype=int))

    def __len__(self):
        return len(self.tA)


# ---------------------------------------------------------------- atoms & coverage
def snap(v, pitch):
    return np.round(np.asarray(v, float) / pitch) * pitch


class AtomSet(object):
    """unordered atom pairs ((px,py),(qx,qy)); positions snapped to a lattice so the emitted
    certificate has small exact denominators."""

    def __init__(self, cd, pitch=Fr(1, 32)):
        self.cd = cd
        self.pitchF = Fr(pitch)
        self.pitch = float(pitch)
        self.px = []; self.py = []; self.qx = []; self.qy = []
        self.keys = {}

    def _canon(self, p, q):
        return (p, q) if p <= q else (q, p)

    def add(self, px, py, qx, qy):
        """snap + dedupe; returns atom index (or existing).  Drops pairs with an endpoint
        inside a slack core or outside the container (useless mass)."""
        cd = self.cd
        pit = self.pitch
        p = (round(px / pit) * pit, round(py / pit) * pit)
        q = (round(qx / pit) * pit, round(qy / pit) * pit)
        for (x, y) in (p, q):
            if not (0.0 < x < cd.s and 0.0 < y < cd.s):
                return None
            for (kx, ky) in cd.pins:
                if abs(x - kx) <= cd.a and abs(y - ky) <= cd.a:
                    return None
        key = self._canon(p, q)
        if key in self.keys:
            return self.keys[key]
        i = len(self.px)
        self.keys[key] = i
        (a, b) = key
        self.px.append(a[0]); self.py.append(a[1]); self.qx.append(b[0]); self.qy.append(b[1])
        return i

    def arrays(self):
        return (np.array(self.px), np.array(self.py), np.array(self.qx), np.array(self.qy))

    def __len__(self):
        return len(self.px)


def coverage_matrix(rows, atoms, margin, chunk=800):
    """sparse boolean coverage: atom i covers row r iff (p in Q_A, q in Q_B at depth>margin)
    or the swap.  Returns scipy.sparse.csr_matrix (nrow, natom), dtype float64 (0/1)."""
    from scipy import sparse
    tA, xA, yA, tB, xB, yB, m2 = rows.arrays()
    px, py, qx, qy = atoms.arrays()
    nr = len(tA)
    blocks = []
    for r0 in range(0, nr, chunk):
        r1 = min(nr, r0 + chunk)
        sl = slice(r0, r1)
        dPA = point_depth(tA[sl], xA[sl], yA[sl], px, py) > margin
        dQA = point_depth(tA[sl], xA[sl], yA[sl], qx, qy) > margin
        dPB = point_depth(tB[sl], xB[sl], yB[sl], px, py) > margin
        dQB = point_depth(tB[sl], xB[sl], yB[sl], qx, qy) > margin
        cov = (dPA & dQB) | (dQA & dPB)
        blocks.append(sparse.csr_matrix(cov, dtype=np.float64))
    return sparse.vstack(blocks, format="csr") if blocks else \
        sparse.csr_matrix((0, len(px)))


def solve_cover_lp(cov, rhs, w_ub=30.0, time_limit=600.0):
    """min sum w  s.t.  cov @ w >= rhs, w >= 0.  Returns (w, value, duals, status)."""
    import highspy
    nr, na = cov.shape
    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.setOptionValue("threads", 1)
    h.setOptionValue("time_limit", float(time_limit))
    h.changeObjectiveSense(highspy.ObjSense.kMinimize)
    h.addCols(na, np.ones(na), np.zeros(na), np.full(na, w_ub),
              0, np.zeros(0, dtype=np.int32), np.zeros(0, dtype=np.int32), np.zeros(0))
    csr = cov.tocsr()
    st = csr.indptr[:-1].astype(np.int32)
    ind = csr.indices.astype(np.int32)
    h.addRows(nr, np.asarray(rhs, float), np.full(nr, 1e30),
              len(ind), st, ind, np.ones(len(ind)))
    h.run()
    status = h.getModelStatus()
    sol = h.getSolution()
    w = np.array(sol.col_value)
    duals = np.array(sol.row_dual)
    val = float(h.getInfo().objective_function_value)
    return w, val, duals, str(status)


# ---------------------------------------------------------------- exploit families
def exploit_grids(cd, eta_list, rng):
    """adversary placements that exploit membership shrunk by eta: grids of axis-aligned
    squares at spacing just above 1-2*eta (their eta-cores are pairwise disjoint while the
    squares overlap), plus one tilted variant.  Returns a Placements pool."""
    parts = []
    for eta in eta_list:
        g = 1.0 - 2.0 * eta + 0.012
        for t in (0.0, 0.05):
            w = float(width_of_t(np.array([t]))[0])
            lo, hi = 0.5 * w + 1e-6, cd.s - 0.5 * w - 1e-6
            for off in (0.0, g / 2.0, g / 3.0):
                v = np.arange(lo + off, hi + 1e-12, g)
                if len(v) < 2:
                    continue
                XX, YY = np.meshgrid(v, v, indexing="ij")
                parts.append(Placements(cd, np.full(XX.size, t), XX.ravel(), YY.ravel()))
    P = Placements.concat(cd, parts) if parts else None
    if P is None:
        return None
    keep = P.admissible
    return Placements(cd, P.t[keep], P.cx[keep], P.cy[keep])
