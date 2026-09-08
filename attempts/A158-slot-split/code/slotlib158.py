"""A158 -- the SLOT SPLIT library: the near-simple slot box S, its two children, and the frames.

THE LEAF (a tautology, then two existing leaves)
------------------------------------------------
For a USABLE slot cell C = [i, i+1] x [j, j+1] of a pinned class (A118 / corpus.CLASSES), let

    S(r, tt) := { poses : centre in [i+1/2-r, i+1/2+r] x [j+1/2-r, j+1/2+r],
                          tilt in [0, tt] u [90-tt, 90] }                    (the corner frame)

-- the NEAR-SIMPLE poses of the slot.  Then, tautologously,

    node  =  YES(S)  u  NO(S),
    YES(S): some square of the packing has its pose in S,
    NO(S) : no square of the packing has its pose in S.

* YES(S) is killed by A141's leaf with ONE extra obstacle.  Add K'(S) -- A132's certified polygon
  core of the box S -- to the conditioned cores.  A `find_witness` discharge against K'(S) says
  "this pose and the S-square share a rational point", hence (Zones.core_meet_same_square, A135
  PolyCoreT5.shared_point_same_square) they ARE the same square -- an IDENTIFICATION, not a
  contradiction, so it costs nothing.  Counting distinct meeters of int C:

      #meeters  <=  1 (the S-square)  +  LANE_K'(C | S)  +  M(C | S)

  where LANE_K'(C | S) is A141's certified lane bound with K'(S) among the obstacles and M(C | S)
  is A141's certified count of the node's conditioned squares that can still meet int C with K'(S)
  among the obstacles.  So

      LANE_K'(C | S) = 0  AND  M(C | S) = 0   ==>   int C is met by <= 1 square
                                              ==>   K0-FREE / teleport ==> the certified-dead
                                                    k6 extension class of the slot.

  Every ingredient is A141's, unchanged; the only new content is the extra CondSq.

* NO(S) is A112's `caselp` NO-family clause: one `NoFam` whose zone is S, written through A136's
  `a136lib` wrapper (bounds rounded INWARD, ZONE subset BOX decided on the written rationals), the
  node LP re-solved with A135 exact cores, certified by the frozen `verify_case.py`.

FRAMES.  The lane leaf runs in the cell's CORNER FRAME on the ORIGINAL packing at side m
(lane.cframe_boxes); the LP runs in the WORLD frame at s0 on the DILATED family.  The map is

      frame X = (v m / s0)          if the corner is not flipped in x
      frame X = m - (v m / s0)      if it is                        (and the same in y)

with v the world-at-s0 coordinate.  For the NO child the zone must satisfy

      dilated pose in Z  ==>  original pose in S           (for the REALISED, unknown m),

so Z is the INTERSECTION over m in [m_lo, s0] of the pullbacks of S -- inward, never outward.
The endpoints are affine/monotone in m, so the intersection is over the two endpoints.  For A60
(m_lo = s0) the map is exact and Z is S itself, moved by a rigid motion.

Tilt: the dilation does not move tilt; a corner flip maps theta -> 90 - theta, and S's tilt set
[0, tt] u [90-tt, 90] is invariant under that map, so the world tilt set is the same.

READ-ONLY on A118 / A132 / A135 / A136 / A141 / A57 / A60: every module below is imported.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
A141 = os.path.join(ROOT, "attempts", "A141-polycore-lane", "code")
A132 = os.path.join(ROOT, "attempts", "A132-polygon-core", "code")
A118 = os.path.join(ROOT, "attempts", "A118-lane-count", "code")
for _p in (A141, A132, A118):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import blas1  # noqa: F401,E402   single-thread BLAS pin, before numpy
import numpy as np  # noqa: E402

import polylane as P               # noqa: E402  READ-ONLY (A141)
import polycore as PC              # noqa: E402  READ-ONLY (A132)
import lane as LANE                # noqa: E402  READ-ONLY (A118)
import corpus as CP                # noqa: E402  READ-ONLY (A118)
from caselp import Box             # noqa: E402  READ-ONLY (A118 copy of A13)

S0 = P.S0
R_DEFAULT = 0.10
TT_DEFAULT = 10.0


# ------------------------------------------------------------------ the S box, corner frame
def s_boxes_frame(i, j, r=R_DEFAULT, tt=TT_DEFAULT):
    """The two caselp.Box pieces of S in the CORNER FRAME (tilt in [0, 90])."""
    cx, cy = float(i) + 0.5, float(j) + 0.5
    lo = Box(cx - r, cx + r, cy - r, cy + r, 0.0, tt)
    hi = Box(cx - r, cx + r, cy - r, cy + r, 90.0 - tt, 90.0)
    return [lo, hi]


def s_zone_world(rec, corner, i, j, r=R_DEFAULT, tt=TT_DEFAULT):
    """The world-at-s0 zone Z of the NO child: the INTERSECTION over m in [m_lo, s0] of the
    pullbacks of S's centre rectangle.  Returns dict(x0, x1, y0, y1, thetas) or None if empty.

    frame X = v*m/s0            (not flipped)      ->  v in [X0*s0/m, X1*s0/m]
    frame X = m - v*m/s0        (flipped)          ->  v in [s0*(m-X1)/m, s0*(m-X0)/m]
    """
    m_lo = LANE.M_LO.get(rec["src"], 3.82)
    ms = (m_lo, S0)
    flipx, flipy = LANE._corner_xy(corner)
    cx, cy = float(i) + 0.5, float(j) + 0.5
    X0, X1, Y0, Y1 = cx - r, cx + r, cy - r, cy + r

    def pull(A0, A1, flip):
        los, his = [], []
        for m in ms:
            if flip:
                los.append(S0 * (m - A1) / m)
                his.append(S0 * (m - A0) / m)
            else:
                los.append(A0 * S0 / m)
                his.append(A1 * S0 / m)
        return max(los), min(his)

    x0, x1 = pull(X0, X1, flipx)
    y0, y1 = pull(Y0, Y1, flipy)
    if x1 <= x0 or y1 <= y0:
        return None
    return dict(x0=x0, x1=x1, y0=y0, y1=y1,
                thetas=[[0.0, tt], [90.0 - tt, 90.0]])


# ------------------------------------------------------------------ the node's cores, A141's
def build_node(rec, slot):
    """A141 t4_slots.build / A157 run157.build, verbatim: (conds, meeter idx, cell rect)."""
    c, i, j = LANE.L.parse_cell(slot)
    pin_b, cond_b = LANE.cframe_boxes(rec, c, i, j)
    pins = P.build_cond([Box(b.x0, b.x1, b.y0, b.y1, b.th0, b.th1) for b in pin_b],
                        tighten=False)
    cond = P.build_cond([Box(b.x0, b.x1, b.y0, b.y1, b.th0, b.th1) for b in cond_b],
                        tighten=False)
    for k, cs in enumerate(cond):
        cs.idx = len(pins) + k
    return pins + cond, [cs.idx for cs in cond], (float(i), float(i) + 1.0,
                                                  float(j), float(j) + 1.0), (c, i, j)


def add_s(conds, i, j, r=R_DEFAULT, tt=TT_DEFAULT, piece=None):
    """conds + [K'(S_piece)].  `piece` = 0 (tilt near 0) or 1 (tilt near 90); None = both, which
    is NOT a single box and must be run as two sub-cases."""
    bs = s_boxes_frame(i, j, r, tt)
    if piece is None:
        raise ValueError("S is a union of two tilt boxes: run piece 0 and piece 1 separately")
    sc = P.build_cond([bs[piece]], tighten=False)[0]
    sc.idx = max([c.idx for c in conds]) + 1
    return conds + [sc], sc


# ------------------------------------------------------------------ the conditional screen
def screen_conditional(conds, cell, rng, n):
    """Sampled LOWER bounds for the YES child, with K'(S) already among `conds`.

    A realised free pose (meets int C, in the container, clear of EVERY core incl. K'(S)) is a
    sound LANE_K'(C | S) >= 1 and so a sound REFUTATION of the YES kill -- no cover needed.
    """
    C, T = P.sample_meeting(cell, S0, n, rng)
    out = dict(drawn=n, meeting=int(len(C)))
    if not len(C):
        out.update(free=0, lane_lb=0)
        return out
    hit = np.zeros(len(C), bool)
    per = {}
    depth_min = np.full(len(C), 1e9)
    for cs in conds:
        d = PC.poly_square_depth(cs.pc.P, C, T)
        per[cs.idx] = int((d > 0.0).sum())
        hit |= (d > 0.0)
        depth_min = np.minimum(depth_min, -d)
    out.update(overlapping_some_core=int(hit.sum()), per_core=per, free=int((~hit).sum()),
               lane_lb=1 if (~hit).any() else 0)
    if (~hit).any():
        k = int(np.argmax(np.where(~hit, depth_min, -1e9)))
        out["free_pose"] = [float(C[k, 0]), float(C[k, 1]), math.degrees(float(T[k]))]
        out["clearance"] = float(depth_min[k])
    return out


def screen_cond_meet(conds, meet, cell, rng, n):
    """Sampled lower bound on M(C | S): for each meeter j, a pose of B_j that meets int C, is
    admissible, and clears every OTHER core (K'(S) included).  A realised one is a sound M >= 1
    and so refutes the YES kill."""
    rows = []
    for cs in conds:
        if cs.idx not in meet:
            continue
        b = cs.box
        C = np.column_stack([rng.uniform(b.x0, b.x1, n), rng.uniform(b.y0, b.y1, n)])
        T = np.radians(rng.uniform(b.th0, b.th1, n))
        h = 0.5 * (np.abs(np.cos(T)) + np.abs(np.sin(T)))
        ok = ((C[:, 0] >= h) & (C[:, 0] <= S0 - h) & (C[:, 1] >= h) & (C[:, 1] <= S0 - h))
        ok &= P.rect_square_meets(cell, C, T)
        for o in conds:
            if o.idx == cs.idx or not ok.any():
                continue
            ok &= (PC.poly_square_depth(o.pc.P, C, T) <= 0.0)
        rows.append(dict(j=cs.idx, can_meet=bool(ok.any()), n=int(ok.sum())))
    return dict(per=rows, M_lb=sum(1 for e in rows if e["can_meet"]))


# ------------------------------------------------------------------ the population metric
def slot_square_world(rec, corner, i, j, m=None):
    """The EXACT slot square (the closed unit cell) in world-at-s0 coordinates.

    The cell is [i, i+1] x [j, j+1] in the corner frame at side m; pulled back to the dilated
    family at s0 it is a rectangle.  Used only to weigh the node's LP atoms, never in a proof.
    """
    m = m if m is not None else S0
    flipx, flipy = LANE._corner_xy(corner)

    def back(A0, A1, flip):
        if flip:
            return S0 * (m - A1) / m, S0 * (m - A0) / m
        return A0 * S0 / m, A1 * S0 / m

    x0, x1 = back(float(i), float(i) + 1.0, flipx)
    y0, y1 = back(float(j), float(j) + 1.0, flipy)
    return (x0, x1, y0, y1)


def atom_weight_in(atoms, rect):
    """Total LP atom weight inside a world rectangle."""
    x0, x1, y0, y1 = rect
    tot = 0.0
    for a in atoms:
        if isinstance(a, dict):
            (ax, ay), w = a["rep"], float(a.get("w", 0.0))
        else:
            ax, ay, w = float(a[0]), float(a[1]), float(a[2])
        if x0 <= ax <= x1 and y0 <= ay <= y1:
            tot += w
    return tot
