"""A168 -- the CASCADE library (Fable lead).  Geometry-forced case trees on a one-box k0_00 cell,
with MUTUAL CLIPPING of every box against every other box's certified core BEFORE anything else.

READ-ONLY imports of prior attempts: A118 `lanelib`, A131 `pinclip` (the exact per-tilt-sub-bin
clip predicates), A132 `polycore` (K' and the exact vertex test = Lean `checkVertexInPBox`),
A135 `exactcore`, A140 `cells140`, A141 `polylane` (covers, witnesses), A144 `guardline` (exact
chords), A161 `chordlane` (exact cell-miss SAT, band tests, LANE_out cover), A57 `caselp.Box`.
Nothing under a prior attempt is written.

The objects
-----------
Node   := a list of named boxes (roles) each carrying a caselp.Box, its A132 polygon core K'(B)
          and its A135 exact axis core; a `forced_by` list naming the leaf that created it; a
          verdict.
Every box of a node is a SUPERSET hypothesis for a DISTINCT square of the family F = D_lambda P at
side s0 (K0-BLOCKED pairs are distinct by definition; corner crowds are disjoint by (R6); H is
distinct from the meeters wherever M(c) = 0 is certified; in the M(c) = 1 mixed case the free
meeter is distinct from H by construction).  Hence:

  CLIP   (A131 pin-clip with A158's rule, exact)   a centre of box B_i at which the square meets the
         inscribed axis core of B_j at EVERY tilt of a tilt sub-bin carries no square of F under
         the node's hypothesis (it would overlap the distinct square j), and is discarded.  The
         inscribed axis core is certified by A132's `vertex_ok` on its four corners (exact), so it
         is inside every pose of B_j and the clip removes LESS than the truth.  A box every centre
         of which is discarded is EMPTY and the node is DEAD (C).
  PAIR   (A141 sec 3, Lean `shared_point_same_square`)  a rational point in every pose of both
         boxes forces the two witnesses to be the same square: contradiction, the node is DEAD (C).
  OVL    (A118 sec 1.2(ii))  every pose pair of two boxes overlaps: the two witnesses cannot be
         distinct squares of a packing, DEAD (C).
  ROW    (A144 LINE-1/LINE-2)  SUM_j minchord(B_j, l) > s0 on an axis-parallel line l inside the
         container: DEAD (C).  beta(l) = floor(s0 - SUM_j minchord) caps the FREE squares whose
         chord on l is >= 1 (A161 Lemma CL, band half).
  BAND / OUT (A161 exact)  every pose of a box has chord >= 1 (resp. < 1) on l.
  LANE_out (A161)  certified max number of pairwise interior-disjoint FREE non-band squares meeting
         a corner cell and clear of every core: an A141 cover with the `band` prune.
  MEET   K'(B) meets int C (exact polygon/rect clip in Fractions): EVERY pose of B meets int C, with
         the certified reach of K' into C.
"""
import json
import math
import os
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, ".."))
for _p in (os.path.join(ATT, "A118-lane-count", "code"),
           os.path.join(ATT, "A131-pin-clip", "code"),
           os.path.join(ATT, "A132-polygon-core", "code"),
           os.path.join(ATT, "A135-polycore-verifier", "code"),
           os.path.join(ATT, "A140-k0-residue-gallery", "code"),
           os.path.join(ATT, "A141-polycore-lane", "code"),
           os.path.join(ATT, "A144-guard-lines", "code"),
           os.path.join(ATT, "A161-chord-lane", "code"),
           os.path.join(ATT, "A99-k0-tree-v2", "code"),
           os.path.join(ATT, "A57-shadow-trees", "code"),
           HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import blas1                                                     # noqa: F401,E402
import numpy as np                                               # noqa: E402

import lanelib as L                                              # noqa: E402  A118 (read-only)
import pinclip as PCLIP                                          # noqa: E402  A131 (read-only)
import polycore as PC                                            # noqa: E402  A132 (read-only)
import exactcore as EC                                           # noqa: E402  A135 (read-only)
import cells140 as C140                                          # noqa: E402  A140 (read-only)
import polylane as PL                                            # noqa: E402  A141 (read-only)
import guardline as GL                                           # noqa: E402  A144 (read-only)
from caselp import Box, Core, t_lo, t_hi, cos_sin_t              # noqa: E402  A57  (read-only)

_CL = None


def CL():
    """A161 chordlane, imported lazily (it pulls A118's corpus)."""
    global _CL
    if _CL is None:
        import chordlane as _cl                                  # noqa: E402  A161 (read-only)
        _CL = _cl
    return _CL


S_RAT = Fr(969271, 250000)
S0 = float(S_RAT)
WLO = Fr(382, 100)
LAM_MAX = S_RAT / WLO
SQ2_LO = Fr(math.isqrt(2 * 10 ** 48), 10 ** 24)
SQ2_HI = SQ2_LO + Fr(1, 10 ** 24)
W0_RAT = (LAM_MAX - 1) * (1 + 1 / SQ2_LO)        # >= the float pad: sound (a wider box)
W0 = PL.W0                                        # A141's float pad 0.02550919... (the boxes)
AW = 1.0 + W0
CORNERS = ("BL", "BR", "TR", "TL")
HALF = Fr(1, 2)
MAXV = 24                                          # K' vertex cap for cover boxes (H uses 40)
RES = os.path.join(BASE, "results")
CERTS = os.path.join(BASE, "certs")
LOGS = os.path.join(BASE, "logs")
FIGS = os.path.join(BASE, "figs")
for _d in (RES, CERTS, LOGS, FIGS):
    os.makedirs(_d, exist_ok=True)


# ===================================================================== sentinels / box ceiling
def sentinel():
    for p in (os.path.join(BASE, "PAUSE"), os.path.join(BASE, "STOP"),
              os.path.join(ROOT, "PAUSE"), os.path.join(ROOT, "STOP")):
        if os.path.exists(p):
            return p
    return None


def jdump(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=1, default=str)
    return path


def jload(path):
    return json.load(open(path, encoding="utf-8"))


def bx(b):
    return [b.x0, b.x1, b.y0, b.y1, b.th0, b.th1]


def unbx(v):
    return Box(*v)


# ===================================================================== the cell
def load_cell(cell):
    meta, rec = C140.load_cell(cell)
    boxes = [Box(**b) for b in rec["hyp"]["boxes"]]
    return meta, rec, boxes


def corner_cell(corner):
    return PL.corner_cell(corner, S0, W0)


def corner_cell_rat(corner):
    """the widened corner box with the RATIONAL pad (>= the float one: sound for 'meets')."""
    lo, hi = Fr(0), 1 + W0_RAT
    return {"BL": (lo, hi, lo, hi), "BR": (S_RAT - hi, S_RAT, lo, hi),
            "TR": (S_RAT - hi, S_RAT, S_RAT - hi, S_RAT), "TL": (lo, hi, S_RAT - hi, S_RAT)}[corner]


def r6_gap():
    """(R6): s0 - 2(1+w) - sqrt2 > 0 => no unit square meets two widened corner boxes."""
    return S_RAT - 2 * (1 + W0_RAT) - SQ2_HI


def box_misses_cell_exact(b, cell):
    ok, det = CL().box_misses_cell_exact(b, cell)
    return bool(ok), det


# ===================================================================== cores
def kprime(box, max_v=MAXV):
    return PC.build(box, max_v=max_v)


def exact_core(box):
    k = box.core()
    if k is None:
        return None
    a, _a0, ok = EC.exact_a(box)
    if not ok:
        raise RuntimeError("exact core vertex test fails for %r" % (box,))
    return Core(k.kx, k.ky, k.tm, a, box)


def _inside_poly(P, x, y):
    E = np.roll(P, -1, axis=0) - P
    return bool(np.all(E[:, 0] * (y - P[:, 1]) - E[:, 1] * (x - P[:, 0]) >= 0.0))


def axis_core_certified(box, pc=None, iters=48):
    """The largest axis-aligned square about the box's midpoint certified (A132 `vertex_ok`, exact,
    on its four corners) to lie in Q(c, theta) for EVERY pose of the box.

    Search: float bisection inside K'; certificate: the exact vertex test on the rational corners,
    with the half-side walked DOWN by 1e-9 steps until it certifies.  Returns (kx, ky, a) as
    Fractions; a = 0 means 'no certified core' (the clip is then skipped: conservative)."""
    pc = pc if pc is not None else kprime(box)
    kx, ky = 0.5 * (box.x0 + box.x1), 0.5 * (box.y0 + box.y1)
    a = 0.0
    if _inside_poly(pc.P, kx, ky):
        lo, hi = 0.0, 0.5
        for _ in range(iters):
            mid = 0.5 * (lo + hi)
            if all(_inside_poly(pc.P, kx + sx * mid, ky + sy * mid)
                   for sx in (-1.0, 1.0) for sy in (-1.0, 1.0)):
                lo = mid
            else:
                hi = mid
        a = lo
    kq, kyq = Fr(kx), Fr(ky)
    aq = Fr(int(a * 10 ** 12), 10 ** 12)
    t0, t1 = t_lo(box.th0), t_hi(box.th1)
    for _ in range(8):
        if aq <= 0:
            return kq, kyq, Fr(0)
        ok = all(PC.vertex_ok(kq + sx * aq, kyq + sy * aq, box, t0, t1)
                 for sx in (-1, 1) for sy in (-1, 1))
        if ok:
            return kq, kyq, aq
        aq -= Fr(1, 10 ** 9)
    return kq, kyq, Fr(0)


class RoleBox:
    """a named box of a node with its cores."""

    __slots__ = ("name", "box", "pc", "axis", "ec")

    def __init__(self, name, box, build=True):
        self.name = name
        self.box = box
        self.pc = self.axis = self.ec = None
        if build:
            self.rebuild()

    def rebuild(self):
        self.pc = kprime(self.box, max_v=(40 if self.name == "H" else MAXV))
        self.axis = axis_core_certified(self.box, self.pc)
        self.ec = None

    def exact(self):
        if self.ec is None:
            self.ec = exact_core(self.box)
        return self.ec

    def json(self):
        kx, ky, a = self.axis
        return dict(name=self.name, box=bx(self.box),
                    kprime=dict(n_verts=len(self.pc.verts), area=self.pc.area(),
                                verts=[[str(v[0]), str(v[1])] for v in self.pc.verts]),
                    axis_core=dict(kx=str(kx), ky=str(ky), a=str(a), a_float=float(a)))


# ===================================================================== the clip (A131 + A158)
def deg_of_t(t):
    return math.degrees(2.0 * math.atan(float(t)))


def clip_box(box, cores, nsub=4, trace=None):
    """Clip `box` against the axis cores [(kx, ky, a)] of the OTHER boxes of the node, per tilt
    sub-bin, with A131's exact predicates (`Oct`, `clip_rect`).  Returns (Box or None, info).

    info: bins=[(t0, t1, rect|None)], kept_vol (fraction of centre x tilt volume), n_empty.
    The tilt range of the result is the union of the NON-EMPTY sub-bins (rounded outward), the
    centre rectangle the union of their rects: a sound superset of every surviving pose."""
    rect0 = PCLIP.outer_rect(box)
    A0 = PCLIP.area(rect0)
    bins = PCLIP.sub_bins(box.th0, box.th1, nsub)
    Ttot = bins[-1][1] - bins[0][0]
    stats = {"exact_calls": 0, "backoffs": 0}
    out, kept, n_empty = [], Fr(0), 0
    ux = None
    tlo = thi = None
    for (t0, t1) in bins:
        rect = rect0
        tr = [] if trace is not None else None
        # container clip, once, at this sub-bin's w_min
        o0 = PCLIP.Oct(t0, t1, Fr(1, 4))
        rect, _ = PCLIP.clip_rect(rect, [], o0, S_RAT, stats=stats, trace=tr)
        for (kx, ky, a) in cores:
            if rect is None or a <= 0:
                continue
            o = PCLIP.Oct(t0, t1, a)
            rect, _ = PCLIP.clip_rect(rect, [(kx, ky)], o, S_RAT, stats=stats, trace=tr)
        if trace is not None:
            trace.append(dict(t0=str(t0), t1=str(t1), steps=tr,
                              rect=None if rect is None else [str(v) for v in rect]))
        out.append((t0, t1, rect))
        if rect is None:
            n_empty += 1
            continue
        w = (t1 - t0) / Ttot if Ttot > 0 else Fr(1, len(bins))
        kept += w * (PCLIP.area(rect) / A0 if A0 > 0 else Fr(0))
        if ux is None:
            ux = list(rect)
            tlo, thi = t0, t1
        else:
            ux = [min(ux[0], rect[0]), max(ux[1], rect[1]), min(ux[2], rect[2]),
                  max(ux[3], rect[3])]
            tlo, thi = min(tlo, t0), max(thi, t1)
    info = dict(kept_vol=float(kept), n_empty=n_empty, n_bins=len(bins),
                bins=[(str(t0), str(t1), None if r is None else [str(v) for v in r])
                      for (t0, t1, r) in out])
    if ux is None:
        return None, info
    th0 = box.th0 if tlo == bins[0][0] else max(box.th0, deg_of_t(tlo) - 1e-9)
    th1 = box.th1 if thi == bins[-1][1] else min(box.th1, deg_of_t(thi) + 1e-9)
    nb = Box(float(ux[0]), float(ux[1]), float(ux[2]), float(ux[3]), th0, th1)
    # never let float rounding ENLARGE the box beyond the original (the outer_rect is a superset)
    nb = Box(max(nb.x0, box.x0), min(nb.x1, box.x1), max(nb.y0, box.y0), min(nb.y1, box.y1),
             nb.th0, nb.th1)
    if nb.x1 <= nb.x0 or nb.y1 <= nb.y0:
        return None, info
    return nb, info


def mutual_clip(roles, nsub=4, passes=3, fixed=(), traces=None):
    """Clip every role box against every other role's certified axis core, rebuilding K' after
    each pass, until nothing moves.  `fixed` names roles never clipped (none by default: H is
    clipped too -- it is distinct from every meeter).  Returns (roles or None, report)."""
    rep = dict(passes=[], dead=None, kept={r.name: 1.0 for r in roles})
    for p in range(passes):
        moved = False
        row = {}
        for i, r in enumerate(roles):
            if r.name in fixed:
                continue
            cores = [o.axis for j, o in enumerate(roles) if j != i and o.axis[2] > 0]
            tr = [] if traces is not None else None
            nb, info = clip_box(r.box, cores, nsub=nsub, trace=tr)
            if traces is not None:
                traces.append(dict(pass_=p, role=r.name, box=bx(r.box),
                                   cores=[[str(k[0]), str(k[1]), str(k[2])] for k in cores],
                                   bins=tr, result=None if nb is None else bx(nb)))
            row[r.name] = dict(kept_vol=info["kept_vol"], n_empty=info["n_empty"],
                               empty=nb is None)
            if nb is None:
                rep["passes"].append(row)
                rep["dead"] = "box %s EMPTY after the clip (pass %d)" % (r.name, p)
                return None, rep
            rep["kept"][r.name] *= info["kept_vol"]
            if bx(nb) != bx(r.box):
                moved = True
                r.box = nb
                r.rebuild()
        rep["passes"].append(row)
        if not moved:
            break
    return roles, rep


# ===================================================================== pair leaves
def pair_ovl(bi, bj):
    return bool(L.pair_always_overlap(bi, bj))


def pair_same_square(bi, bj):
    """a rational point in every pose of BOTH boxes (A132 vertex_ok twice) -> the same square."""
    w, f, _mb, _mj = PL.best_shared_point(bi, bj)
    if w is None or f <= PL.MARGIN:
        return None
    wq = PL.rationalise(w)
    if PL.certify_point(wq, bi) and PL.certify_point(wq, bj):
        return [str(wq[0]), str(wq[1])]
    return None


# ===================================================================== covers (A141)
def cover_corner(corner, cond_boxes, depth=8, max_open=6000):
    """A COMPLETE prefix-code cover of the corner's meeter pose window with A141's three discharges
    (container / misses the cell / shares a rational point with a conditioned box).  The open
    boxes over-approximate the poses a FREE meeter (distinct from every conditioned square) can
    take.  Returns (root Box, cover dict)."""
    cell = corner_cell(corner)
    conds = PL.build_cond(cond_boxes, tighten=False)
    root = Box(*PL.centre_window(cell, S0), 0.0, 90.0)
    cov = PL.lane_cover(root, cell, conds, s=S0, exact=True, depth0=depth, max_depth=30,
                        max_open=max_open, rounds=0)
    return root, cov


def cover_record(root, cov):
    return dict(root=bx(root), complete=cov.get("complete"), reason=cov.get("reason"),
                n_leaves=len(cov.get("leaves", [])), n_open=len(cov.get("open", [])),
                open=[o["box"] for o in cov.get("open", [])],
                open_paths=[o["path"] for o in cov.get("open", [])],
                leaves=[dict(path=lf["path"], why=lf["why"], j=lf.get("j"), w=lf.get("w"))
                        for lf in cov.get("leaves", [])])


# ===================================================================== rows (A144)
def line_h(off):
    return GL.Line("h", Fr(off))


def line_v(off):
    return GL.Line("v", Fr(off))


def wall_lines(wall, n=40, den=10 ** 6):
    """exact rational lines in the wall strip of width 1 + w (the strip a meeter must reach)."""
    lo, hi = (S_RAT - 1 - W0_RAT, S_RAT) if wall in ("top", "right") else (Fr(0), 1 + W0_RAT)
    out = []
    for k in range(1, n + 1):
        v = lo + (hi - lo) * Fr(k, n + 1)
        off = Fr(round(v * den), den)
        if lo < off < hi:
            out.append(GL.Line("h" if wall in ("top", "bottom") else "v", off, tag=wall))
    return out


def minchord(box, line):
    return GL.minchord_box(box, line)["lo"]


def chord_row(boxes, line):
    mcs = [minchord(b, line) for b in boxes]
    rhs = S_RAT - sum(mcs, Fr(0))
    return dict(off=str(line.off), off_f=float(line.off), orient=line.orient,
                minchords=[str(m) for m in mcs], minchords_f=[float(m) for m in mcs],
                rhs=str(rhs), rhs_f=float(rhs),
                beta=(int(math.floor(rhs)) if rhs >= 0 else -1))


def best_row(boxes, lines):
    best = None
    for ln in lines:
        r = chord_row(boxes, ln)
        if best is None or Fr(r["rhs"]) < Fr(best["rhs"]):
            best = r
    return best


# ===================================================================== band / out (A161)
def band_class(box, line):
    ok, _ = CL().band_ok(box, line)
    if ok:
        return "BAND"
    ok, _ = CL().not_band_ok(box, line)
    if ok:
        return "OUT"
    return "MIXED"


def band_split(box, line, max_depth=6):
    """tautologous subdivision of a box into BAND / OUT / (residual MIXED) pieces on `line`."""
    out = []
    stack = [("", box)]
    while stack:
        p, b = stack.pop()
        c = band_class(b, line)
        if c != "MIXED" or len(p) >= max_depth:
            out.append((p, b, c))
            continue
        b0, b1 = PL.split_box(b)
        stack.append((p + "0", b0))
        stack.append((p + "1", b1))
    return out


# ===================================================================== K' meets a rect (exact)
def _clip_poly_rect(V, rect):
    """exact Sutherland-Hodgman clip of a convex polygon (rational verts, ccw) by an axis rect."""
    X0, X1, Y0, Y1 = rect
    P = [(Fr(a), Fr(b)) for a, b in V]

    def clip(poly, inside, inter):
        out = []
        m = len(poly)
        for i in range(m):
            p, q = poly[i], poly[(i + 1) % m]
            ip, iq = inside(p), inside(q)
            if ip:
                out.append(p)
            if ip != iq:
                out.append(inter(p, q))
        return out

    def lerp_x(p, q, x):
        t = (x - p[0]) / (q[0] - p[0])
        return (x, p[1] + t * (q[1] - p[1]))

    def lerp_y(p, q, y):
        t = (y - p[1]) / (q[1] - p[1])
        return (p[0] + t * (q[0] - p[0]), y)

    for inside, inter in ((lambda p: p[0] >= X0, lambda p, q: lerp_x(p, q, X0)),
                          (lambda p: p[0] <= X1, lambda p, q: lerp_x(p, q, X1)),
                          (lambda p: p[1] >= Y0, lambda p, q: lerp_y(p, q, Y0)),
                          (lambda p: p[1] <= Y1, lambda p, q: lerp_y(p, q, Y1))):
        P = clip(P, inside, inter)
        if not P:
            return []
    return P


def poly_area(P):
    if len(P) < 3:
        return Fr(0)
    s = Fr(0)
    for i in range(len(P)):
        a, b = P[i], P[(i + 1) % len(P)]
        s += a[0] * b[1] - b[0] * a[1]
    return abs(s) / 2


def kprime_meets_rect(pc, rect):
    """EXACT: does K'(B) (hence every pose of B) meet the OPEN rect?  Returns (bool, area, reach)
    where reach = (xmin, xmax, ymin, ymax) of K' n rect -- the certified penetration."""
    P = _clip_poly_rect(pc.verts, rect)
    A = poly_area(P)
    if A <= 0:
        return False, Fr(0), None
    xs = [p[0] for p in P]
    ys = [p[1] for p in P]
    return True, A, (min(xs), max(xs), min(ys), max(ys))


# ===================================================================== LANE_out (A161)
def lane_out(corner, cond_boxes, line, deadline_s=90.0, max_depth=34, max_open=2500):
    conds = PL.build_cond(cond_boxes, tighten=False)
    cell = corner_cell(corner)
    r = CL().lane_out(cell, conds, line, s=S0, max_depth=max_depth, max_open=max_open,
                      deadline=time.time() + deadline_s, band_mode="out")
    return r


# ===================================================================== sampling (drawn -> tested -> hits)
def sq_verts(cx, cy, th, half=0.5):
    c, s = math.cos(th), math.sin(th)
    return [(cx + half * (c * ux - s * uy), cy + half * (s * ux + c * uy))
            for ux, uy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


def sq_meets_rect(cx, cy, th, rect):
    X0, X1, Y0, Y1 = rect
    V = sq_verts(cx, cy, th)
    if max(v[0] for v in V) <= X0 or min(v[0] for v in V) >= X1:
        return False
    if max(v[1] for v in V) <= Y0 or min(v[1] for v in V) >= Y1:
        return False
    R = [(X0, Y0), (X1, Y0), (X1, Y1), (X0, Y1)]
    for ax in ((math.cos(th), math.sin(th)), (-math.sin(th), math.cos(th))):
        pv = [v[0] * ax[0] + v[1] * ax[1] for v in V]
        pr = [r[0] * ax[0] + r[1] * ax[1] for r in R]
        if max(pv) <= min(pr) or min(pv) >= max(pr):
            return False
    return True


def in_box(cx, cy, th_deg, b, tol=1e-9):
    return (b.x0 - tol <= cx <= b.x1 + tol and b.y0 - tol <= cy <= b.y1 + tol
            and b.th0 - tol <= (th_deg % 90.0) <= b.th1 + tol)


def sample_poses_in(box, n, rng):
    C = np.column_stack([rng.uniform(box.x0, box.x1, n), rng.uniform(box.y0, box.y1, n)])
    T = np.radians(rng.uniform(box.th0, box.th1, n)) if box.th1 > box.th0 \
        else np.full(n, math.radians(box.th0))
    return C, T


def admissible_mask(C, T, cores_pc, s=S0):
    """inside the container and interior-disjoint from every polygon core (float SAT)."""
    h = 0.5 * (np.abs(np.cos(T)) + np.abs(np.sin(T)))
    ok = (C[:, 0] >= h) & (C[:, 0] <= s - h) & (C[:, 1] >= h) & (C[:, 1] <= s - h)
    for pc in cores_pc:
        if not ok.any():
            break
        ok &= (PC.poly_square_depth(pc.P, C, T) <= 0.0)
    return ok


def region_raster(cores_pc, th0, th1, cell=None, line=None, band=None, pitch=0.02, ntilt=12,
                  s=S0):
    """DRAWING AID (sampled, not certified): the set of centres admitting SOME sampled tilt in
    [th0, th1] whose square is inside the container, clear of every polygon core, meets int(cell)
    (if given) and is BAND (chord >= 1) / OUT (chord < 1) on `line` (if given).  Returns
    (xs, ys, mask)."""
    xs = np.arange(0.5 * pitch, s, pitch)
    ys = np.arange(0.5 * pitch, s, pitch)
    X, Y = np.meshgrid(xs, ys, indexing="ij")
    Cc = np.column_stack([X.ravel(), Y.ravel()])
    mask = np.zeros(len(Cc), bool)
    ths = np.radians(np.linspace(th0, th1, ntilt)) if th1 > th0 else np.array([math.radians(th0)])
    for th in ths:
        T = np.full(len(Cc), th)
        ok = admissible_mask(Cc, T, cores_pc, s)
        if cell is not None and ok.any():
            idx = np.flatnonzero(ok)
            ok[idx] = PL.rect_square_meets(cell, Cc[idx], T[idx])
        if line is not None and band is not None and ok.any():
            V = line.foff - (Cc[:, 1] if line.orient == "h" else Cc[:, 0])
            ch = GL.chord_many(0.5, T, V)
            ok &= (ch >= 1.0) if band == "BAND" else (ch < 1.0)
        mask |= ok
    return xs, ys, mask.reshape(len(xs), len(ys))


# ===================================================================== the Trump canary
def trump_images():
    import class84 as K84                                        # noqa: E402  A99 (read-only)
    Y0, s_trump, lam = K84.trump_scaled()
    out = []
    for k in range(8):
        Z = K84.symmetry(Y0, k)
        out.append((k, [(float(x), float(y), math.degrees(float(th)) % 90.0) for x, y, th in Z]))
    return out, float(s_trump), float(lam)


def image_hits(boxes):
    """[(k, poses, [(sq, box)])] for the images with a square inside some hypothesis box."""
    IM, s_t, lam = trump_images()
    out = []
    for k, Z in IM:
        hits = [(i, j) for i, p in enumerate(Z) for j, b in enumerate(boxes)
                if in_box(p[0], p[1], p[2], b)]
        if hits:
            out.append((k, Z, hits))
    return out, s_t, lam


def image_corner_meeters(Z, corner, widened=True):
    cell = corner_cell(corner) if widened else {
        "BL": (0.0, 1.0, 0.0, 1.0), "BR": (S0 - 1.0, S0, 0.0, 1.0),
        "TR": (S0 - 1.0, S0, S0 - 1.0, S0), "TL": (0.0, 1.0, S0 - 1.0, S0)}[corner]
    return [i for i, p in enumerate(Z) if sq_meets_rect(p[0], p[1], math.radians(p[2]), cell)]


WALL_OF = {"TR": ("top", "right"), "TL": ("top", "left"), "BL": ("bottom", "left"),
           "BR": ("bottom", "right")}


# ===================================================================== classification (the PI's D/S)
def classify_tr(rb, corner="TR"):
    """where in the corner's approach a (clipped) meeter box sits, and what it certifiably does:
    side RIGHT/TOP/DIAG, band flags on the wall lines (minchord >= 1 on SOME wall line of the
    strip), and the certified reach of K' into the widened corner box."""
    b = rb.box
    X0, X1, Y0, Y1 = corner_cell(corner)
    mx, my = 0.5 * (b.x0 + b.x1), 0.5 * (b.y0 + b.y1)
    if corner == "TR":
        a1, a2 = S0 - mx, S0 - my
        side = "TOP" if a2 < a1 - 0.05 else ("RIGHT" if a1 < a2 - 0.05 else "DIAG")
    elif corner == "TL":
        a1, a2 = mx, S0 - my
        side = "TOP" if a2 < a1 - 0.05 else ("LEFT" if a1 < a2 - 0.05 else "DIAG")
    elif corner == "BL":
        a1, a2 = mx, my
        side = "BOTTOM" if a2 < a1 - 0.05 else ("LEFT" if a1 < a2 - 0.05 else "DIAG")
    else:
        a1, a2 = S0 - mx, my
        side = "BOTTOM" if a2 < a1 - 0.05 else ("RIGHT" if a1 < a2 - 0.05 else "DIAG")
    out = dict(side=side, mid=[round(mx, 4), round(my, 4)], tilt=[b.th0, b.th1])
    for wall in WALL_OF[corner]:
        lines = wall_lines(wall, n=24)
        best = max((minchord(b, ln) for ln in lines), default=Fr(0))
        out["band_%s" % wall] = bool(best >= 1)
        out["maxminchord_%s" % wall] = float(best)
    meets, area, reach = kprime_meets_rect(rb.pc, corner_cell_rat(corner))
    out["kprime_meets_cell"] = bool(meets)
    if meets:
        out["kprime_reach"] = [float(v) for v in reach]
        out["kprime_area_in_cell"] = float(area)
    return out


# ===================================================================== H_meet (A159 B_meet, exact)
def h_meet_box(H, corner, depth=(4, 4, 4)):
    """bounding box of the sub-boxes of H's box (nx x ny x nt) NOT certified (A161 exact SAT) to
    miss the widened corner box; None if every sub-box misses (then M(c) = 0)."""
    cell = corner_cell(corner)
    nx, ny, nt = depth
    keep = []
    n_sub = n_miss = 0
    for i in range(nx):
        for j in range(ny):
            for k in range(nt):
                sb = Box(H.x0 + (H.x1 - H.x0) * i / nx, H.x0 + (H.x1 - H.x0) * (i + 1) / nx,
                         H.y0 + (H.y1 - H.y0) * j / ny, H.y0 + (H.y1 - H.y0) * (j + 1) / ny,
                         H.th0 + (H.th1 - H.th0) * k / nt, H.th0 + (H.th1 - H.th0) * (k + 1) / nt)
                n_sub += 1
                ok, _ = box_misses_cell_exact(sb, cell)
                if ok:
                    n_miss += 1
                else:
                    keep.append(sb)
    if not keep:
        return None, dict(n_sub=n_sub, n_miss=n_miss)
    bb = Box(min(b.x0 for b in keep), max(b.x1 for b in keep), min(b.y0 for b in keep),
             max(b.y1 for b in keep), min(b.th0 for b in keep), max(b.th1 for b in keep))
    return bb, dict(n_sub=n_sub, n_miss=n_miss, n_keep=len(keep), pieces=[bx(b) for b in keep])


