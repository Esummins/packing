"""A143 -- the CORNER-FIRST level-1 cover of k0_00: condition on the square that meets the BL
corner box, not on an interior-zone square.

ROOT LEMMA (k0_route.md sec 3, 4.2; Lean `teleport_packing` / `k0free_kill`).  For a packing P at
side m in [3.82, shat] either

    (K0-FREE)     some corner box B_c(m) = the closed unit box at corner c is met by <= 1 square
                  of P  ==>  P does not exist (m < shat) or P is a Trump image (m = shat);
or
    (K0-BLOCKED)  every corner box is met by >= 2 squares.

Under K0-BLOCKED the BL box is met, so SOME square Q0 of P has a pose in

    R_BL := {(c, th) : Q(c, th) subset [0, m]^2  and  int Q(c, th) meets int [0, 1]^2}.

Transported to the dilate F = Delta_lambda P at s0 this is Lemma K0-WIDEN; the tree below is built
at s0 on the UNWIDENED box, which is the conservative direction for a REACH statement only if the
widening is carried.  A143 states the cover at s0 with the widened box a_w = 1 + w,
w = (lambda_max - 1)(1 + 1/sqrt2) = 0.025509 (k0_route.md sec 1), exactly as A118's k0 pad does.

THE TILT CLAUSE, CORRECTED.  The brief expected "k0 means no simple square, so the BL intruder is
tilted".  The Lean definition (`Skeleton.lean` `OccupiesSlot`) is EXACT: a square occupies a slot
iff it is axis-aligned AND centred exactly on the slot centre.  `skeleton = empty` therefore
excludes, in the th = 0 slice of R_BL, exactly the single pose (1/2, 1/2, 0) (the BL(0,0) slot;
BL(1,0) at (3/2, 1/2) does not meet the OPEN unit box) and its th = 90 twin.  There is no
delta_simple tolerance anywhere in the k0 root definition, and no positive-measure tilt exclusion
is available in the FORALL-packings form the k0_00 tree is stated in.  The cover therefore runs
over the FULL tilt range [0, 90).

D4.  The stabiliser of the BL corner in D4 is {id, transpose}; the transpose fixes BL, swaps
x and y and sends th -> 90 - th, and both K0-BLOCKED and "BL is met" are invariant under it.  So
WLOG the BL intruder's pose has x >= y: the position grid may be quotiented to its upper triangle
(Lemma K0-D4 with X_n the D4_BL-set of cells).  Both counts are reported.
"""
import math
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
A57 = os.path.join(ROOT, "attempts", "A57-shadow-trees", "code")
A132 = os.path.join(ROOT, "attempts", "A132-polygon-core", "code")
A135 = os.path.join(ROOT, "attempts", "A135-polycore-verifier", "code")
A115 = os.path.join(ROOT, "attempts", "A115-k0-corner-rows", "code")
for _p in (A57, A132, A135, A115, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from caselp import Box, t_lo, t_hi, cos_sin_t          # noqa: E402  (read-only import)

S0 = 969271.0 / 250000.0
S0_RAT = "969271/250000"
LAM_MAX = S0 / 3.82
# Lemma K0-WIDEN: the crowd of P at side m transfers to F = Delta_lambda P with the box grown by w
W_WIDEN = (LAM_MAX - 1.0) * (1.0 + math.sqrt(0.5))      # 0.0255094...
A_W = 1.0 + W_WIDEN                                     # the widened BL box [0, A_W]^2

SQ2H = math.sqrt(0.5)                                   # max half-extent h(45deg)

# the corner-meeting zone: cx in [h(th), s0 - h(th)] and cx - h(th) < a_w
ZLO = 0.5
ZHI = A_W + SQ2H                                        # 1.7326162...

NPOS = 6                # position cells per axis
NTILT = 6               # tilt windows
TILT_W = 90.0 / NTILT   # 15 degrees
NSUB = 8                # tilt sub-bins for the A131 per-sub-bin clip


def h_of(th_deg):
    t = math.radians(th_deg)
    return 0.5 * (math.cos(t) + math.sin(t))


def h_range(th0, th1):
    """(min, max) of h over [th0, th1] (h is unimodal with its max at 45 deg)."""
    vals = [h_of(th0), h_of(th1)]
    lo, hi = min(vals), max(vals)
    if th0 <= 45.0 <= th1:
        hi = SQ2H
    return lo, hi


def clip_box(x0, x1, y0, y1, th0, th1, s=S0, a_w=A_W):
    """The CONTAINER clip (walls as pins, A131's mechanism: the pose must keep the square inside
    [0, s]^2) intersected with the REACH clip (the square must meet [0, a_w]^2 at the BL corner).

    Sound: an admissible pose (c, th) in the cell has c_i >= h(th) >= h_min and c_i <= s - h(th)
    <= s - h_min, and meeting [0, a_w]^2 forces min_Q x < a_w, i.e. c_x < a_w + h(th) <= a_w+h_max.
    Returns None if the clipped box is empty."""
    hlo, hhi = h_range(th0, th1)
    X0 = max(x0, hlo)
    X1 = min(x1, a_w + hhi, s - hlo)
    Y0 = max(y0, hlo)
    Y1 = min(y1, a_w + hhi, s - hlo)
    if X1 <= X0 or Y1 <= Y0:
        return None
    return (X0, X1, Y0, Y1)


def subbin_clip(x0, x1, y0, y1, th0, th1, nsub=NSUB, s=S0, a_w=A_W):
    """A131's per-tilt-sub-bin clip: subdivide the tilt window and clip each sub-bin separately.
    Returns the list of (sub_th0, sub_th1, clipped box) that survive.  The cell is EMPTY iff the
    list is empty -- strictly stronger than the whole-window clip whenever the two clip directions
    fight in different sub-bins."""
    out = []
    for k in range(nsub):
        a = th0 + (th1 - th0) * k / nsub
        b = th0 + (th1 - th0) * (k + 1) / nsub
        c = clip_box(x0, x1, y0, y1, a, b, s=s, a_w=a_w)
        if c is not None:
            out.append((a, b, c))
    return out


class Cell:
    __slots__ = ("ix", "iy", "it", "raw", "box", "empty", "subbins", "canon")

    def __init__(self, ix, iy, it):
        self.ix, self.iy, self.it = ix, iy, it
        w = (ZHI - ZLO) / NPOS
        x0, x1 = ZLO + ix * w, ZLO + (ix + 1) * w
        y0, y1 = ZLO + iy * w, ZLO + (iy + 1) * w
        th0, th1 = it * TILT_W, (it + 1) * TILT_W
        self.raw = (x0, x1, y0, y1, th0, th1)
        self.subbins = subbin_clip(x0, x1, y0, y1, th0, th1)
        c = clip_box(x0, x1, y0, y1, th0, th1)
        self.empty = (c is None) or (not self.subbins)
        self.box = None if self.empty else Box(c[0], c[1], c[2], c[3], th0, th1)
        # D4_BL canonical representative under the transpose (x,y,th) -> (y,x,90-th)
        self.canon = (ix >= iy)

    @property
    def name(self):
        return "c1_%d%d_t%d" % (self.ix, self.iy, self.it)

    def mate(self):
        """the transpose image cell (iy, ix, NTILT-1-it)."""
        return (self.iy, self.ix, NTILT - 1 - self.it)

    def to_json(self):
        return dict(name=self.name, ix=self.ix, iy=self.iy, it=self.it,
                    raw=list(self.raw), canon=bool(self.canon), empty=bool(self.empty),
                    box=(self.box.to_json() if self.box else None),
                    n_subbins=len(self.subbins))


def all_cells():
    return [Cell(ix, iy, it) for ix in range(NPOS) for iy in range(NPOS) for it in range(NTILT)]


# ------------------------------------------------------------------ exact "meets the corner box"
def _verts(cx, cy, t):
    co, si = cos_sin_t(t)
    h = Fr(1, 2)
    e1 = (h * co, h * si)
    e2 = (-h * si, h * co)
    return [(cx + su * e1[0] + sv * e2[0], cy + su * e1[1] + sv * e2[1])
            for su, sv in ((1, 1), (1, -1), (-1, -1), (-1, 1))]


def f_min_max(cx, cy, t):
    """exact min over Q(c, theta) of max(x, y)  (corner85.f_min_max, re-derived here so A143 does
    not import A85's module).  Q meets the OPEN box [0, a)^2 iff f_min_max < a."""
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


def meets_bl(cx, cy, th_deg, a_w=A_W):
    """float test: does Q(c, th) meet the open widened BL box?"""
    t = Fr(math.tan(math.radians(th_deg) / 2.0)).limit_denominator(10 ** 12)
    return float(f_min_max(Fr(cx).limit_denominator(10 ** 12),
                           Fr(cy).limit_denominator(10 ** 12), t)) < a_w


def in_container(cx, cy, th_deg, s=S0):
    h = h_of(th_deg)
    return (h <= cx <= s - h) and (h <= cy <= s - h)


def locate(cx, cy, th_deg):
    """(ix, iy, it) of the cell containing the pose, after the D4_BL canonicalisation
    (transpose if x < y).  Returns None if the pose is outside the zone."""
    x, y, th = cx, cy, th_deg % 90.0
    if x < y:
        x, y, th = y, x, (90.0 - th) % 90.0
    w = (ZHI - ZLO) / NPOS
    if not (ZLO - 1e-12 <= x <= ZHI + 1e-12 and ZLO - 1e-12 <= y <= ZHI + 1e-12):
        return None
    ix = min(NPOS - 1, max(0, int((x - ZLO) / w)))
    iy = min(NPOS - 1, max(0, int((y - ZLO) / w)))
    it = min(NTILT - 1, max(0, int(th / TILT_W)))
    return (ix, iy, it)


if __name__ == "__main__":
    import json
    cs = all_cells()
    live = [c for c in cs if not c.empty]
    can = [c for c in live if c.canon]
    print(f"zone [{ZLO:.6f}, {ZHI:.6f}]^2  a_w = {A_W:.7f}  w = {W_WIDEN:.7f}")
    print(f"cells {len(cs)}  non-empty after container+reach clip {len(live)}  "
          f"D4_BL-canonical of those {len(can)}")
    print(json.dumps(cs[0].to_json()))

S0_RAT_F = S0
