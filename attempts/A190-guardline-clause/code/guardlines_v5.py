"""
guardlines_v5.py -- A190.  The EXACT primitives of the guard-line clause (A144 notes/spec.md sec. 1-2, 4;
docs/proofs/guardline_clause.md), in Fractions only.  No float decides anything here.

THE CHORD.  For a closed square of half-side a at tilt theta (t = tan(theta/2) in [0,1]; C = |cos|, S = |sin|)
whose centre is at distance V >= 0 from an axis-parallel line l,
    chord(a, t, V) = max(0, min( 2a / max(C,S) ,  (a (C+S) - V) / (C S) ))                       (CH)
(A144 spec sec. 2): exact rational in t.  It is antitone in V and depends on theta only through y = C + S in
[1, sqrt2]; A(y) = 2a/max(C,S) is increasing in y and B(y) = 2(a y - V)/(y^2 - 1) attains its minimum over a
y-interval at an endpoint (its derivative has the sign of -a y^2 + 2 V y - a, whose roots multiply to 1).  So the
minimum over a pose box [t0,t1] x [x0,x1] x [y0,y1] is the FIVE-POINT evaluation `minchord` below, with V = the
largest distance from the line over the centre rectangle and B(sqrt2) rounded DOWN through a rational lower bound
of sqrt2 whenever 45 deg may lie in the bin.  Zero-width tilt bins are evaluated at their single t.

THE HYPOTHESIS OBJECTS.  A `guardlines` entry declares (orient, off, z, rhs).  The right-hand side is RE-DERIVED
(`rederive`): for every core j NOT attached to a window, its square carries at least
    chord_lo(j, l) = max( chord of the core square K_j itself ,  minchord over the core's declared `pbox` )
where `pbox` (optional, rational) is the pose box of the hypothesis square that contains K_j; the verifier binds
it to the core by A135's `point_in_all_poses` on K_j's four corners (HARD REJECT otherwise).  The cores with a
positive term must be in pairwise DISTINCT squares and in no WINDOW square (`distinct_cores`, `core_off_window`:
pose boxes disjoint, or two corners further apart than sqrt2, or a corner further than sqrt2/2 from every centre
of a piece) -- HARD REJECT otherwise.  Then rhs*(l) = s - SUM_j chord_lo(j, l) and the verifier uses
min(declared rhs, rhs*).
"""
import math
from fractions import Fraction as F

HALF = F(1, 2)
ZERO = F(0)
SQRT2_LO = F(math.isqrt(2 * 10 ** 48), 10 ** 24)            # floor(sqrt2 * 10^24) / 10^24
SQRT2_HI = SQRT2_LO + F(1, 10 ** 24)
assert SQRT2_LO * SQRT2_LO < 2 < SQRT2_HI * SQRT2_HI
INF = float("inf")
T45_LO, T45_HI = SQRT2_LO - 1, SQRT2_HI - 1                 # tan(22.5 deg) = sqrt2 - 1 lies in [T45_LO, T45_HI]


# ===================================================================== (CH) and the five-point minimum
def cs_of_t(t):
    """(Cn, Sn, D): cos = Cn/D, sin = Sn/D at t = tan(theta/2) in [0,1] (both >= 0)."""
    return 1 - t * t, 2 * t, 1 + t * t


def chord_at(a, t, V):
    """(CH) exactly at one t in [0,1], V >= 0."""
    Cn, Sn, D = cs_of_t(t)
    mx = max(Cn, Sn)
    A = 2 * a * D / mx
    if Cn == 0 or Sn == 0:                                  # theta = 0 or 90 exactly: chord 2a iff V <= a
        return A if V * D <= a * mx else ZERO
    B = (a * (Cn + Sn) - V * D) * D / (Cn * Sn)
    return max(ZERO, min(A, B))


def _B_of_y(a, y, V):
    """B(y) = 2(a y - V)/(y^2 - 1); at y = 1 its one-sided limit (an infimum, hence a lower bound)."""
    if y == 1:
        return INF if V < a else (a if V == a else -INF)
    return 2 * (a * y - V) / (y * y - 1)


def minchord(a, t0, t1, x0, x1, y0, y1, orient, off):
    """EXACT lower bound (the minimum, up to the sqrt2 rounding) of |l n Q| over every pose in the closed box
    [t0,t1] x [x0,x1] x [y0,y1] of a square of half-side a; l is y = off ('h') or x = off ('v')."""
    lo, hi = (y0, y1) if orient == "h" else (x0, x1)
    V = max(abs(off - lo), abs(off - hi))
    if t0 == t1:
        return chord_at(a, t0, V)
    cands = []
    for t in (t0, t1):
        Cn, Sn, D = cs_of_t(t)
        cands.append(2 * a * D / max(Cn, Sn))                # A at the endpoint
        cands.append(_B_of_y(a, (Cn + Sn) / D, V))           # B at the endpoint's y
    if t0 <= T45_HI and t1 >= T45_LO:                        # 45 deg MAY lie in the bin: B(sqrt2), rounded down
        cands.append(2 * (SQRT2_LO * a - V))
    m = min(cands)
    if m == -INF or m < 0:
        return ZERO
    if m == INF:                                             # cannot happen (the A terms are finite); guarded
        m = min(c for c in cands if c != INF)
    return F(m)


# ===================================================================== hypothesis geometry (exact)
def core_corners(k):
    """the four rational corners of a v1 core K = (kx, ky, tm, a) with cm = cos, sm = sin of theta_m."""
    return [(k.kx + k.a * (i * k.cm - j * k.sm), k.ky + k.a * (i * k.sm + j * k.cm))
            for i, j in ((1, 1), (1, -1), (-1, -1), (-1, 1))]


def core_chord(k, orient, off):
    """|l n K| for the core square itself: a valid lower bound of the chord of ANY square containing K."""
    V = abs(off - (k.ky if orient == "h" else k.kx))
    return chord_at(k.a, k.tm, V)


def boxes_disjoint(P, Q):
    """closed (x0,x1,y0,y1,t0,t1) pose boxes; disjoint => the squares they hold are distinct (one pose each)."""
    return (P[1] < Q[0] or Q[1] < P[0] or P[3] < Q[2] or Q[3] < P[2] or P[5] < Q[4] or Q[5] < P[4])


def corners_far(k1, k2):
    """two corners at squared distance > 2: no closed unit square (diameter sqrt2) contains both cores."""
    return any((ax - bx) ** 2 + (ay - by) ** 2 > 2 for (ax, ay) in core_corners(k1) for (bx, by) in core_corners(k2))


def _dist2_rect(vx, vy, x0, x1, y0, y1):
    dx = max(x0 - vx, ZERO, vx - x1)
    dy = max(y0 - vy, ZERO, vy - y1)
    return dx * dx + dy * dy


def core_off_piece(k, piece):
    """K has a corner further than sqrt2/2 from EVERY centre of the piece (Q(pose) lies in the closed disc of
    radius sqrt2/2 about its centre), so no square with a pose in the piece contains K."""
    x0, x1, y0, y1, t0, t1 = piece
    return any(_dist2_rect(vx, vy, x0, x1, y0, y1) > HALF for (vx, vy) in core_corners(k))


def distinct_cores(ki, kj, pi, pj):
    """the squares of cores i and j are provably distinct."""
    return (pi is not None and pj is not None and boxes_disjoint(pi, pj)) or corners_far(ki, kj)


def core_off_window(k, pbox, pieces):
    """core k is provably in no square whose pose lies in the window (list of pieces)."""
    for pc in pieces:
        if pbox is not None and boxes_disjoint(pbox, pc):
            continue
        if not core_off_piece(k, pc):
            return False
    return True


# ===================================================================== the certificate field
class GuardLineH:
    """One `guardlines` entry: (orient, off, z, rhs) as declared; `rhs_star` and `rhs_eff` set by `rederive`."""

    __slots__ = ("idx", "orient", "off", "z", "rhs", "rhs_star", "rhs_eff", "terms")

    def __init__(self, i, d, s, rat):
        self.idx = i
        self.orient = str(d.get("orient", ""))
        if self.orient not in ("h", "v"):
            raise ValueError("guardline %d: orient must be 'h' or 'v'" % i)
        self.off = rat(d["off"])
        if not (ZERO < self.off < s):
            raise ValueError("guardline %d: offset %s not inside (0, s)" % (i, self.off))
        self.z = rat(d["z"])
        if self.z < 0:
            raise ValueError("guardline %d: negative density" % i)
        self.rhs = rat(d["rhs"])
        self.rhs_star = self.rhs_eff = None
        self.terms = []

    def minchord(self, t0, t1, x0, x1, y0, y1, a=HALF):
        return minchord(a, t0, t1, x0, x1, y0, y1, self.orient, self.off)

    def to_json(self):
        return dict(orient=self.orient, off=str(self.off), off_float=float(self.off), z=str(self.z),
                    z_float=float(self.z), rhs=str(self.rhs), rhs_star=str(self.rhs_star),
                    rhs_eff=str(self.rhs_eff), rhs_eff_float=float(self.rhs_eff),
                    terms=[(j, str(c)) for j, c in self.terms])


def rederive(lines, cores, pboxes, windows, attached, s):
    """(G1): rhs*(l) = s - SUM over UNATTACHED cores j with chord_lo > 0; HARD REJECT (ValueError) if the
    declared rhs exceeds rhs*, or the contributing cores are not provably in distinct, non-window squares."""
    for L in lines:
        terms = []
        for j, k in enumerate(cores):
            if j in attached:
                continue                                     # its square is COUNTED by the window clause (V2)
            c = core_chord(k, L.orient, L.off)
            if pboxes[j] is not None:
                c = max(c, L.minchord(pboxes[j][4], pboxes[j][5], *pboxes[j][:4]))
            if c > 0:
                terms.append((j, c))
        J = [j for j, _ in terms]
        for u in range(len(J)):
            for v in range(u + 1, len(J)):
                i_, j_ = J[u], J[v]
                if not distinct_cores(cores[i_], cores[j_], pboxes[i_], pboxes[j_]):
                    raise ValueError("guardline %d: cores %d and %d are not provably distinct squares" % (L.idx, i_, j_))
        for j in J:
            for w in windows:
                if not core_off_window(cores[j], pboxes[j], w.pieces):
                    raise ValueError("guardline %d: core %d may lie in window %s (would be double-counted)" % (L.idx, j, w.name))
        L.terms = terms
        L.rhs_star = s - sum((c for _, c in terms), ZERO)
        # SOUNDNESS FIX (external review 2026-09-10, P0): the proved inequality bounds the counted chord sum by
        # rhs_star only; a declared rhs SMALLER than rhs_star is not justified by anything the verifier checks
        # (min(rhs, rhs_star) accepted a false PASS: four lines with rhs 0 "excluded" one unit square).  The
        # declared field is a consistency check and must equal the independently re-derived value exactly.
        if L.rhs != L.rhs_star:
            raise ValueError("guardline %d: declared rhs %s differs from the independently re-derived rhs* %s"
                             % (L.idx, L.rhs, L.rhs_star))
        L.rhs_eff = L.rhs_star
    return lines
