"""A152 -- the slot-lane leaf with a tolerance-SHRUNK / TRANSLATED slot cell.

READ-ONLY imports of A141 (`polylane`, `emit141`), A118 (`lane`, `lanelib`, `corpus`), A132
(`polycore`) and A57 (`caselp`).  Nothing outside `attempts/A152-slot-lane-shrunk/**` is written.

Three cell variants are computed for every (node, usable slot):

  exact    C            = [i, i+1] x [j, j+1]           -- A141's leaf (A118-O1: EXACT pins)
  shrunk   C_h          = [i+h, i+1-h] x [j+h, j+1-h]   -- the PI's literal proposal (DIAGNOSTIC
                                                            ONLY: see notes/soundness.md, the
                                                            union-of-blocked-translates step is
                                                            FALSE, so this is not a leaf)
  trans(t) C + t        for t in the admissible translate set                -- the SOUND form

`h = delta / sqrt(2)` is the pin box half-width of the slack family (A57 `tree57.build_children`:
a square pin box of half-width `delta/sqrt(2)`), `delta = 1e-2` on the G1 tree.

The admissible translate set is
    A(t) = { t in [-h, h]^2 : C + t inside the container AND C + t interior-disjoint from every
             admissible position of every pin of the class }
computed in the cell's CORNER FRAME, where the container's two backed walls are u = 0 and v = 0
and the pin centre boxes are `lane.cframe_boxes`'s (hulled over m in [m_lo, s0]) fattened by the
node's own pin slack `pin_h` (7.0711e-3 for A57 / A57box, 0 for A60's exact pins).

The obstacle cores used by the LANE cover are the same K' polygon cores as A141's, EXCEPT that a
PIN box is fattened by `pin_h` first -- A141 used the un-fattened (exact-slot, m-hulled) pin box,
which is the sound obstacle only for an EXACT-pin class-S packing (A118-O1).
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
A141 = os.path.join(ROOT, "attempts", "A141-polycore-lane", "code")
A118 = os.path.join(ROOT, "attempts", "A118-lane-count", "code")
for _p in (HERE, A141, A118):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import blas1  # noqa: F401,E402  (must precede numpy)
import numpy as np  # noqa: E402

import polylane as P              # noqa: E402  READ-ONLY (A141)
import polycore as PC             # noqa: E402  READ-ONLY (A132)
import lane as LANE               # noqa: E402  READ-ONLY (A118)
import corpus as CP               # noqa: E402  READ-ONLY (A118)
from caselp import Box            # noqa: E402  READ-ONLY (A57)

SQ2 = math.sqrt(2.0)
DELTA_G1 = 1e-2                       # A57 G1 pin slack (lemmas.md T23)
H_G1 = DELTA_G1 / SQ2                 # 7.0710678e-3, the pin box HALF-WIDTH
EPS = 1e-12


def node_pin_h(rec):
    """The half-width of the node's own pin boxes.  A57 / A57box run the G1 delta = 1e-2 slack
    family (`tree57.build_children`); A60's `deepen.py` uses degenerate (EXACT) pin boxes."""
    return 0.0 if rec["src"] == "A60" else H_G1


# ------------------------------------------------------------------ boxes and cores
def build(rec, slot, pin_h):
    """(conds, meeter indices, (i, j), pin centre boxes) in the cell's corner frame.

    `pin_h > 0` fattens every pin CENTRE box by +-pin_h before its K' core is built, which is the
    sound obstacle for the slack-pin family (the core shrinks, so the LANE bound only weakens)."""
    c, i, j = LANE.L.parse_cell(slot)
    pin_b, cond_b = LANE.cframe_boxes(rec, c, i, j)
    pins = P.build_cond([Box(b.x0 - pin_h, b.x1 + pin_h, b.y0 - pin_h, b.y1 + pin_h,
                             b.th0, b.th1) for b in pin_b], tighten=False)
    cond = P.build_cond([Box(b.x0, b.x1, b.y0, b.y1, b.th0, b.th1) for b in cond_b],
                        tighten=False)
    for k, cs in enumerate(cond):
        cs.idx = len(pins) + k
    return pins + cond, [cs.idx for cs in cond], (int(i), int(j)), pin_b


# ------------------------------------------------------------------ the cell variants
def cell_exact(i, j):
    return (float(i), float(i) + 1.0, float(j), float(j) + 1.0)


def cell_shrunk(i, j, h):
    return (float(i) + h, float(i) + 1.0 - h, float(j) + h, float(j) + 1.0 - h)


def cell_trans(i, j, t):
    tu, tv = t
    return (float(i) + tu, float(i) + 1.0 + tu, float(j) + tv, float(j) + 1.0 + tv)


def admissible_translates(pin_b, i, j, hs, pin_h, s=P.S0, grid=(-1.0, 0.0, 1.0)):
    """The translates t of the slot square that are admissible for EVERY packing of the node.

    A translate is admissible iff (a) |t|_inf <= hs, so the snapped square is a pin of the
    extension class T within the slack tolerance; (b) C + t stays inside [0, s]^2 (in the corner
    frame the two backed walls are u = 0 and v = 0); (c) C + t is interior-disjoint from every
    position the class's pins may occupy -- pin centre box fattened by pin_h, pin square = centre
    +- 1/2 at zero tilt.  Returns the list of (tu, tv), most-inward first."""
    out = []
    for gu in grid:
        for gv in grid:
            tu, tv = gu * hs, gv * hs
            if i + tu < -EPS or j + tv < -EPS:
                continue                                     # leaves the container at a wall
            if i + 1.0 + tu > s + EPS or j + 1.0 + tv > s + EPS:
                continue
            u0, u1 = i + tu, i + 1.0 + tu
            v0, v1 = j + tv, j + 1.0 + tv
            ok = True
            for b in pin_b:
                X0, X1 = b.x0 - pin_h - 0.5, b.x1 + pin_h + 0.5
                Y0, Y1 = b.y0 - pin_h - 0.5, b.y1 + pin_h + 0.5
                if not (u1 <= X0 + EPS or u0 >= X1 - EPS or v1 <= Y0 + EPS or v0 >= Y1 - EPS):
                    ok = False
                    break
            if ok:
                out.append((tu, tv))
    out.sort(key=lambda t: -(t[0] + t[1]))                   # inward-diagonal retreat first
    return out


# ------------------------------------------------------------------ screens and full runs
def screen(cell, conds, rng, n, s=P.S0):
    """The cheap sampled screen (A141 `polylane._sample_screen`): lane_lb, M_lb, witnesses."""
    return P._sample_screen(cell, conds, s, rng, n)


def full(cell, conds, meet, rng, sample, maxopen, keep_cert=True, max_depth=34):
    res = P.lane_corner_generic(cell, conds, meeters=meet, rng=rng, sample=sample,
                                max_open=maxopen, keep_cert=keep_cert, max_depth=max_depth)
    return res


def sample_line(conds, cell, rng, n, s=P.S0):
    """drawn -> meeting the (shrunk / translated) cell -> free of every K'."""
    C, T = P.sample_meeting(cell, s, n, rng)
    hit = np.zeros(len(C), bool)
    per = {}
    for cs in conds:
        h = PC.poly_square_depth(cs.pc.P, C, T) > 0.0
        per[cs.idx] = int(h.sum())
        hit |= h
    return dict(drawn=n, meeting=int(len(C)), overlapping_some_core=int(hit.sum()),
                per_core=per, free=int((~hit).sum()))


# ------------------------------------------------------------------ corpus
def alive_records():
    """A57 (k5_11/k5_16) + A57box + A60 alive records, exactly A141 T2's corpus rule."""
    recs = CP.load_nodes()
    known = set(r["nid"] for r in recs)
    boxes, _ = CP.load_open_boxes(known)
    out = [r for r in recs if r["alive"] and r["cls"] in ("k5_11", "k5_16", "trump5")]
    for b in boxes:
        if b["alive"] and not b.get("covered_by_node"):
            out.append(b)
    return out
