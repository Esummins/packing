"""A165 -- the CASCADE library: forced-box case trees on a one-box k0_00 cell.

Everything here is READ-ONLY on prior attempts: A118 `lanelib`, A132 `polycore`, A135 `exactcore`,
A141 `polylane`, A144 `guardline`, A161 `chordlane`, A57 `caselp` are imported, never written.

The objects
-----------
`Role`      a named square of the case: `H` (the cell's conditioned square) or a corner meeter
            (`TR_a`, `TR_b`, `TL_a`, `TL_b`, ...), each carrying a `caselp.Box`.
`Case`      a tuple of Roles + the reason each was forced + the verdict.

The forcing steps, and where each is proved
-------------------------------------------
(R1)  K0-FREE / K0-BLOCKED dichotomy .............. `docs/proofs/k0_route.md` sec 3, sec 4.2
(R2)  Lemma K0-WIDEN: the widened corner box ...... `k0_route.md` sec 4.1  (w = 0.02550919...)
(R6)  no square meets two widened corner boxes .... A150 notes/composition.md sec 1
      (s0 - 2(1+w) = 1.826 > sqrt2 = diam of a unit square)
(M0)  M(c) = 0 at a corner  =>  H is not a meeter . A141 lane leaf, `cond_can_meet`
(TOP) no square lies entirely above y = y_L for y_L > s0 - 1 ..... proved in `top_row_facts`
(LINE-1/2) chords on an axis line sum to <= s0 .... A144 `guardline`
(PAIR) two boxes sharing a rational point in every pose are the SAME square ... A141 sec 3/sec 5
(OVL)  two boxes that always overlap cannot hold two interior-disjoint squares ... A118 sec 1.2(ii)

Nothing here writes a `case-lp-certificate-v1`; the LP leaf calls A57's `solve_node` and the
FROZEN `verify_case.py` through A150's driver shape, unchanged.
"""
import json
import math
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, ".."))
for _p in (os.path.join(ATT, "A118-lane-count", "code"),
           os.path.join(ATT, "A132-polygon-core", "code"),
           os.path.join(ATT, "A135-polycore-verifier", "code"),
           os.path.join(ATT, "A140-k0-residue-gallery", "code"),
           os.path.join(ATT, "A141-polycore-lane", "code"),
           os.path.join(ATT, "A144-guard-lines", "code"),
           os.path.join(ATT, "A161-chord-lane", "code"),
           os.path.join(ATT, "A57-shadow-trees", "code"),
           HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import blas1                                                     # noqa: F401,E402
import numpy as np                                               # noqa: E402

import lanelib as L                                              # noqa: E402  A118
import polycore as PC                                            # noqa: E402  A132
import polylane as PL                                            # noqa: E402  A141
import guardline as GL                                           # noqa: E402  A144
import chordlane as CL                                           # noqa: E402  A161
import cells140 as C140                                          # noqa: E402  A140
from caselp import Box                                           # noqa: E402  A57

SQ2 = math.sqrt(2.0)
S_RAT = Fr(969271, 250000)
S0 = float(S_RAT)
WLO = 3.82
LAM_MAX = S0 / WLO
W0 = PL.W0                       # Lemma K0-WIDEN pad, 0.02550919...
AW = 1.0 + W0                    # widened corner box side
CORNERS = ("BL", "BR", "TR", "TL")


# ------------------------------------------------------------------ the node
def load_node(cell):
    """(meta, record, [Box]) for one of A140's twelve converged-alive k0_00 cells."""
    meta, rec = C140.load_cell(cell)
    boxes = [Box(**b) for b in rec["hyp"]["boxes"]]
    return meta, rec, boxes


# ------------------------------------------------------------------ (R6) and the roles
def corner_cell(corner):
    return PL.corner_cell(corner, S0, W0)


def r6_gap():
    """s0 - 2*(1+w) - sqrt2 > 0 is (R6): no unit square meets two widened corner boxes."""
    return S0 - 2.0 * AW - SQ2


# ------------------------------------------------------------------ (TOP) the wall-row facts
def top_row_facts(y_L):
    """Facts about the horizontal line y = y_L, for y_L in (0, s0).

    `no_square_above`   : no admissible square lies entirely above l   (needs y_L > s0 - 1)
    `above_needs_cs_le` : if a square DOES lie entirely above l then |cos t| + |sin t| <= this
    `tilt_window_deg`   : the tilt window (about the axis) that allows lying entirely above
    Proof: c_y <= s0 - h and c_y - h >= y_L give 2h <= s0 - y_L, h = (|cos|+|sin|)/2.
    """
    cs = S0 - y_L                                   # bound on |cos| + |sin|
    out = dict(y_L=y_L, no_square_above=bool(y_L > S0 - 1.0), cs_le=cs)
    if cs >= SQ2:
        out["tilt_window_deg"] = 90.0
    elif cs <= 1.0:
        out["tilt_window_deg"] = 0.0
    else:
        # cos t + sin t = sqrt2 sin(t + 45deg) <= cs  =>  t <= asin(cs/sqrt2) - 45  (mod 90)
        out["tilt_window_deg"] = math.degrees(math.asin(min(1.0, cs / SQ2))) - 45.0
    return out


def corner_meeter_reaches(corner):
    """The coordinate a meeter of the WIDENED corner box is guaranteed to exceed."""
    X0, X1, Y0, Y1 = corner_cell(corner)
    return dict(x_gt=X0 if corner in ("TR", "BR") else None,
                x_lt=X1 if corner in ("TL", "BL") else None,
                y_gt=Y0 if corner in ("TR", "TL") else None,
                y_lt=Y1 if corner in ("BL", "BR") else None)


# ------------------------------------------------------------------ chord row (A144 LINE-1/2)
def line_h(off):
    return GL.Line("h", Fr(off) if not isinstance(off, Fr) else off)


def line_v(off):
    return GL.Line("v", Fr(off) if not isinstance(off, Fr) else off)


def minchord(box, line):
    """A144's exact five-point minimum chord of a unit square over a parameter box.  A144's
    `minchord_box` returns a DICT; `lo` is the certified rational lower bound."""
    return GL.minchord_box(box, line)["lo"]


def chord_row(boxes, line, s=S_RAT):
    """rhs(l) = s - SUM minchord(B_j, l);  beta = floor(rhs) caps the number of FREE squares
    whose chord on l is >= 1 (A161 Lemma CL, band half)."""
    mcs = [minchord(b, line) for b in boxes]
    rhs = Fr(s) - sum(mcs)
    return dict(off=str(line.off), orient=line.orient,
                minchords=[str(m) for m in mcs], minchords_f=[float(m) for m in mcs],
                rhs=str(rhs), rhs_f=float(rhs),
                beta=int(math.floor(float(rhs))) if rhs >= 0 else -1)


# ------------------------------------------------------------------ the meeter cover
def meeter_cover(corner, conds, depth0=9, max_depth=30, max_open=4000, exact=True):
    """A COMPLETE binary cover of the pose window of the widened corner box `corner`, with every
    box either discharged (container / misses the cell / shares a point with a conditioned box) or
    kept OPEN.  The open boxes are a sound over-approximation of the poses a meeter can take.

    Returns polylane.lane_cover's dict; `open` is the branching set of the case tree.
    """
    cell = corner_cell(corner)
    root = Box(*PL.centre_window(cell, S0), 0.0, 90.0)
    return PL.lane_cover(root, cell, conds, s=S0, exact=exact, depth0=depth0,
                         max_depth=max_depth, max_open=max_open, rounds=0)


def open_boxes(cov):
    return [Box(*o["box"]) for o in cov.get("open", [])]


# ------------------------------------------------------------------ pair prunes
def pair_always_overlap(bi, bj):
    """(OVL) A118 sec 1.2(ii): no separating axis for ANY pose pair -> the two squares always
    overlap -> they cannot be two distinct squares of a packing."""
    return bool(L.pair_always_overlap(bi, bj))


def pair_same_square(bi, bj):
    """(PAIR) one rational point in every pose of both boxes -> the SAME square (A141 sec 3).
    Returns the point, or None."""
    w, f, mb, mj = PL.best_shared_point(bi, bj)
    if w is None or f <= PL.MARGIN:
        return None
    wq = PL.rationalise(w)
    if PL.certify_point(wq, bi) and PL.certify_point(wq, bj):
        return [str(wq[0]), str(wq[1])]
    return None


def pair_matrix(boxes):
    """Boolean matrix: True where the two boxes ALWAYS overlap (so the pair is impossible)."""
    return L.pairs_always_overlap_matrix(boxes)


# ------------------------------------------------------------------ exact box/cell miss (A161)
def box_misses_cell_exact(b, cell):
    """A161's FULL separating-axis test over a parameter box.  Returns (bool, detail) -- note that
    `chordlane.box_misses_cell_exact` returns a TUPLE, so never use it in a boolean context."""
    ok, detail = CL.box_misses_cell_exact(b, cell)
    return bool(ok), detail


# ------------------------------------------------------------------ geometry helpers
def sq_verts(cx, cy, th, half=0.5):
    c, s = math.cos(th), math.sin(th)
    return [(cx + half * (c * ux - s * uy), cy + half * (s * ux + c * uy))
            for ux, uy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


def sq_meets_rect(cx, cy, th, rect, half=0.5, eps=0.0):
    """Exact-enough SAT: unit square (cx,cy,th) vs axis rectangle (X0,X1,Y0,Y1)."""
    X0, X1, Y0, Y1 = rect
    V = sq_verts(cx, cy, th, half)
    if max(v[0] for v in V) <= X0 + eps or min(v[0] for v in V) >= X1 - eps:
        return False
    if max(v[1] for v in V) <= Y0 + eps or min(v[1] for v in V) >= Y1 - eps:
        return False
    R = [(X0, Y0), (X1, Y0), (X1, Y1), (X0, Y1)]
    for ax in ((math.cos(th), math.sin(th)), (-math.sin(th), math.cos(th))):
        pv = [v[0] * ax[0] + v[1] * ax[1] for v in V]
        pr = [r[0] * ax[0] + r[1] * ax[1] for r in R]
        if max(pv) <= min(pr) + eps or min(pv) >= max(pr) - eps:
            return False
    return True


def chord_of(cx, cy, th, line, half=0.5):
    """Length of the intersection of the unit square with the axis line."""
    V = sq_verts(cx, cy, th, half)
    k = 1 if line.orient == "h" else 0
    off = float(line.off)
    xs = []
    for i in range(4):
        a, b = V[i], V[(i + 1) % 4]
        if (a[k] - off) * (b[k] - off) < 0:
            t = (off - a[k]) / (b[k] - a[k])
            xs.append(a[1 - k] + t * (b[1 - k] - a[1 - k]))
        elif a[k] == off:
            xs.append(a[1 - k])
    if len(xs) < 2:
        return 0.0
    return max(xs) - min(xs)


def in_box(cx, cy, th_deg, b, tol=1e-9):
    return (b.x0 - tol <= cx <= b.x1 + tol and b.y0 - tol <= cy <= b.y1 + tol
            and b.th0 - tol <= (th_deg % 90.0) <= b.th1 + tol)


def box_of_pose(cx, cy, th_deg, boxes):
    for i, b in enumerate(boxes):
        if in_box(cx, cy, th_deg, b):
            return i
    return None


def bx_json(b):
    return [b.x0, b.x1, b.y0, b.y1, b.th0, b.th1]


def jdump(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=1, default=str)
    return path


# ------------------------------------------------------------------ sentinels
OWN = [os.path.join(BASE, "PAUSE"), os.path.join(BASE, "STOP")]
GLOBAL = [os.path.join(ROOT, "PAUSE"), os.path.join(ROOT, "STOP")]


def sentinel():
    for p in OWN + GLOBAL:
        if os.path.exists(p):
            return p
    return None
