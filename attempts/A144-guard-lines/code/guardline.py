"""A144 T1 -- GUARD LINES: the "four chords on one line" cut, as an exact LP row.

THE CUT (n-general, sound for every packing).  Let P be a packing of pairwise interior-disjoint
closed unit squares inside the container [0, s]^2 and let l be a line.  The chords l n Q_i are
sub-intervals of l n [0,s]^2 with pairwise disjoint interiors, so

    SUM_i |l n Q_i|  <=  |l n [0,s]^2|  =  s          (for l axis-parallel, inside the container).

At a NODE of the case tree the squares split into the hypothesis squares (the pins P_j and the
conditioned square H, each known only up to its parameter box) and the `budget = n - #cores`
others, which are exactly the placements the node LP ranges over.  Hence

    SUM_{others} |l n Q|  <=  s - SUM_j minchord(P_j, l) - minchord(H, l)  =:  rhs(l).      (GL)

HOW IT ENTERS THE LP.  A57's node LP is the COVERING LP

    tau = min mu([0,s]^2)   s.t.   mu(Q) >= 1 for every admissible non-exempt placement Q,

with mu supported on atoms (the primal columns) and one row per placement.  (GL) is a valid
inequality for the packing = for the DUAL, so in the PRIMAL it is a new COLUMN: a "line measure"
of density z >= 0 on l, contributing |l n Q| * z to every row and rhs(l) * z -- NOT s * z -- to
the objective.  The bridge argument is unchanged:

    budget <= SUM_i mu(Q_i)                                    (rows, one per packed square)
            = SUM_k w_k [atom k in Q_i] + z SUM_i |l n Q_i|
           <= SUM_k m_k w_k + z * rhs(l)                       (atoms disjoint-covered; (GL))
            = objective,

so tau < budget still kills the node.  Adding columns can only LOWER tau: a guard line is a
strictly cheaper way to cover, and the discount it buys over a plain measure on l is exactly the
length that the pins and H are guaranteed to occupy -- the part of l the LP is otherwise forced
to pay for twice.  The pins' part of the discount is achievable by ordinary atoms (a measure on
l minus the pins is a genuine measure); the -minchord(H, l) part is NOT, because H's position is
unknown, and that is the part the LP has never had.

THE CHORD, IN CLOSED FORM.  For a square of half-side a at pose (c, theta) and a horizontal line
at height h, put v = h - c_y (the chord does not depend on c_x at all), C = |cos th|, S = |sin th|.
The chord is the intersection of two intervals of half-lengths a/C, a/S whose centres are |v|/(CS)
apart, so

    chord(a, th, v) = max(0, min( (a(C+S) - |v|)/(CS),  2a/max(C,S) )).                    (CH)

Two consequences used below: a chord through OPPOSITE sides has length 2a/max(C,S) >= 2a (the
"stack of four" reading), and (CH) depends on theta only through  y := C + S = sqrt2 cos(th - 45),
which is what makes the minimum over a tilt bin a two-point evaluation.

THE MINIMUM OVER A BOX (exact).  With  y = C + S in [1, sqrt2]  and  CS = (y^2 - 1)/2:

    A(y) = 4a/(y + sqrt(2 - y^2))   is INCREASING in y      (A = 2a/max(C,S))
    B(y) = 2(a y - |v|)/(y^2 - 1)   has  dB/dy  of the sign of  q(y) = -a y^2 + 2|v| y - a,
        whose roots multiply to 1, so on [1, sqrt2] B is either strictly decreasing (|v| < a,
        q < 0 everywhere) or increasing-then-decreasing (|v| >= a).  EITHER WAY the minimum of B
        over a y-interval is attained at an ENDPOINT.

chord is also decreasing in |v|, so over a centre rectangle the minimum is at V = max |h - c_y|
over the rectangle.  Hence, for a box B = [x0,x1]x[y0,y1]x[th0,th1],

    minchord(B, l) = max(0, min( A(t0), A(t1), B(y(t0)), B(y(t1)), B(sqrt2) if 45 in [th0,th1] ))

-- five rational evaluations (B(sqrt2) = 2(sqrt2 a - V) is rounded DOWN to a rational, which is
conservative).  t0 = caselp.t_lo(th0), t1 = caselp.t_hi(th1) are the corpus's own OUTWARD-rounded
tilt bounds, so the certified statement is about a tilt range CONTAINING [th0,th1] (A132's rule).
A zero-width tilt bin (the PINS, th0 = th1 = 0) is evaluated exactly at that single t, where the
chord is 2a for every V <= a: the pins' chord is EXACTLY 1 whenever the line runs through the pin
core's height range, which is the reading the PI made.  A bin of positive width that touches
theta = 0 or 90 uses the LIMIT value of B there (the chord is discontinuous at those two tilts
when V = a exactly), which is an infimum, hence still a lower bound.

The cheap alternative bound is |l n K'(B)|, the chord of A132's certified polygon core; K' is
contained in Q at every pose, so it is a valid but weaker bound.  Both are reported.

Nothing here is wired into any driver: A57/A131/A132/A135/A142 are imported read-only.
"""
import math
import os
import sys
from fractions import Fraction as Fr

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, ".."))
A53 = os.path.join(ATT, "A53-simple-strata")
A57 = os.path.join(ATT, "A57-shadow-trees")
A131 = os.path.join(ATT, "A131-pin-clip")
A132 = os.path.join(ATT, "A132-polygon-core")
A135 = os.path.join(ATT, "A135-polycore-verifier")
for _p in (os.path.join(A57, "code"), os.path.join(A132, "code"), os.path.join(A135, "code"),
           os.path.join(A131, "code"), HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from caselp import Box, t_lo, t_hi                                   # noqa: E402 (read-only)
import lpbox                                                         # noqa: E402 (read-only)

S_RAT = Fr(969271, 250000)                 # s0 = 3.877084
S0 = float(S_RAT)
DELTA = Fr(1, 100)                         # A57 slack-core delta = 1e-2
HALF = Fr(1, 2)
# a rational LOWER bound of sqrt(2): floor(sqrt2 * 10^24) / 10^24, error < 1e-24
SQRT2_LO = Fr(math.isqrt(2 * 10 ** 48), 10 ** 24)
assert SQRT2_LO ** 2 < 2 and (SQRT2_LO + Fr(1, 10 ** 24)) ** 2 > 2
LDEN = 10 ** 9                             # rational grid the line offsets live on
INF = float("inf")


# ===================================================================== the line
class Line:
    """An axis-parallel line inside the container.  `orient` in {"h","v"}; the line is
    y = off (h) or x = off (v).  `off` is an exact Fraction; `tag` records its provenance."""

    __slots__ = ("orient", "off", "foff", "tag", "cost", "rhs_exact")

    def __init__(self, orient, off, tag=""):
        assert orient in ("h", "v")
        self.orient = orient
        self.off = Fr(off)
        self.foff = float(self.off)
        self.tag = tag
        self.cost = None                 # rhs(l), set by guardlp.attach_costs
        self.rhs_exact = None

    def key(self):
        return (self.orient, self.off)

    def to_json(self):
        return dict(orient=self.orient, off=str(self.off), off_float=self.foff, tag=self.tag)

    def __repr__(self):
        return f"L({self.orient}={self.foff:.6f} {self.tag})"

    def offset_of(self, cx, cy):
        """the signed distance v from the placement centre to the line, along the normal."""
        return self.foff - (cy if self.orient == "h" else cx)

    def offset_range(self, x0, x1, y0, y1):
        """[|v| min, |v| max] over a centre rectangle."""
        lo, hi = (y0, y1) if self.orient == "h" else (x0, x1)
        a, b = self.foff - hi, self.foff - lo
        return (0.0 if a <= 0 <= b else min(abs(a), abs(b))), max(abs(a), abs(b))

    def offset_range_frac(self, x0, x1, y0, y1):
        lo, hi = (Fr(y0), Fr(y1)) if self.orient == "h" else (Fr(x0), Fr(x1))
        a, b = self.off - hi, self.off - lo
        return max(abs(a), abs(b))


# ===================================================================== (CH), float and exact
def chord_float(a, th, v):
    """|l n Q| for a square of half-side `a` at tilt `th` (radians) whose centre is at signed
    distance -v from the line (formula (CH); v may have either sign)."""
    C, S = abs(math.cos(th)), abs(math.sin(th))
    V = abs(v)
    mx = max(C, S)
    if mx <= 0.0:
        return 0.0
    A = 2.0 * a / mx
    if C <= 0.0 or S <= 0.0:                     # theta = 0 or 90 exactly
        return A if V <= a * mx + 1e-300 else 0.0
    B = (a * (C + S) - V) / (C * S)
    return max(0.0, min(A, B))


def chord_interval(a, cx, cy, th, line):
    """the chord as an INTERVAL along the line: (lo, hi) in the coordinate the line runs along
    (x for a horizontal line, y for a vertical one).  Empty -> None."""
    C, S = math.cos(th), math.sin(th)
    v = line.foff - (cy if line.orient == "h" else cx)
    base = cx if line.orient == "h" else cy
    if line.orient == "v":                       # swap roles: run along y, offset along x
        C, S = S, -C
    iv = []
    for (p, q) in ((C, S), (-S, C)):             # |u p + v q| <= a
        if abs(p) < 1e-15:
            if abs(v * q) > a:
                return None
            continue
        lo, hi = (-a - v * q) / p, (a - v * q) / p
        iv.append((min(lo, hi), max(lo, hi)))
    if not iv:
        return None
    lo = max(i[0] for i in iv)
    hi = min(i[1] for i in iv)
    return None if hi <= lo else (base + lo, base + hi)


def chord_many(a, TH, V):
    """vectorised (CH): TH radians, V signed offsets (arrays)."""
    C, S = np.abs(np.cos(TH)), np.abs(np.sin(TH))
    V = np.abs(V)
    mx = np.maximum(C, S)
    A = 2.0 * a / np.maximum(mx, 1e-300)
    den = C * S
    with np.errstate(divide="ignore", invalid="ignore"):
        B = np.where(den > 0, (a * (C + S) - V) / np.where(den > 0, den, 1.0),
                     np.where(V <= a * mx, np.inf, -np.inf))
    return np.maximum(0.0, np.minimum(A, B))


def cs_of_t(t):
    """exact (Cn, Sn, D) with cos = Cn/D, sin = Sn/D for t = tan(theta/2) in [0,1]."""
    t = Fr(t)
    return 1 - t * t, 2 * t, 1 + t * t


def chord_exact_t(a, t, V):
    """(CH) in exact rationals at t = tan(theta/2) in [0,1], V = |v| >= 0.  Returns a Fraction
    (the chord is rational in t)."""
    a, V = Fr(a), abs(Fr(V))
    Cn, Sn, D = cs_of_t(t)
    mx = max(Cn, Sn)
    if mx == 0:
        return Fr(0)
    A = 2 * a * D / mx                                     # = 2a / max(C,S)
    if Cn == 0 or Sn == 0:                                 # theta = 90 or 0 exactly
        return A if V * D <= a * mx else Fr(0)
    B = (a * (Cn + Sn) - V * D) * D / (Cn * Sn)
    return max(Fr(0), min(A, B))


def _A_of_t(a, t):
    Cn, Sn, D = cs_of_t(t)
    mx = max(Cn, Sn)
    return None if mx == 0 else 2 * Fr(a) * D / mx


def _y_of_t(t):
    """y = cos th + sin th, exact."""
    Cn, Sn, D = cs_of_t(t)
    return (Cn + Sn) / D


def _B_of_y(a, y, V):
    """B(y) = 2(a y - V)/(y^2 - 1); the limit value at y = 1 (an infimum, hence a lower bound)."""
    a, V, y = Fr(a), Fr(V), Fr(y)
    if y == 1:
        if V < a:
            return INF
        if V == a:
            return a                                        # lim_{y->1+} 2a(y-1)/(y^2-1) = a
        return -INF
    return 2 * (a * y - V) / (y * y - 1)


def minchord_box(box, line, a=HALF, want_witness=False):
    """EXACT lower bound of |l n Q(c,theta)| over every pose (c, theta) in `box`.

    Returns dict(lo=Fraction, lo_float, method, terms, V) -- `lo` is a certified lower bound and,
    except for the sqrt2 rounding when 45 deg is interior to the tilt bin, is the exact minimum."""
    a = Fr(a)
    V = line.offset_range_frac(box.x0, box.x1, box.y0, box.y1)
    t0, t1 = t_lo(box.th0), t_hi(box.th1)
    if t0 > t1:
        t0, t1 = t1, t0
    if t0 == t1:                                            # zero-width tilt bin: the PINS
        c = chord_exact_t(a, t0, V)
        return dict(lo=c, lo_float=float(c), method="degenerate-tilt",
                    terms=dict(t=str(t0), chord=str(c)), V=float(V))
    cands, terms = [], {}
    for nm, t in (("A(t0)", t0), ("A(t1)", t1)):
        A = _A_of_t(a, t)
        if A is not None:
            cands.append(A)
            terms[nm] = float(A)
    for nm, t in (("B(y(t0))", t0), ("B(y(t1))", t1)):
        B = _B_of_y(a, _y_of_t(t), V)
        cands.append(B)
        terms[nm] = B if B in (INF, -INF) else float(B)
    tstar = SQRT2_LO - 1                                    # a rational < tan(22.5 deg)
    if t0 <= tstar + Fr(1, 10 ** 15) and t1 >= tstar:       # 45 deg inside the (outward) tilt bin
        B45 = 2 * (SQRT2_LO * a - V)                        # <= 2(sqrt2 a - V) = B(sqrt2)
        cands.append(B45)
        terms["B(45deg)"] = float(B45)
    m = min(cands)
    m = Fr(0) if (m == -INF or m < 0) else (None if m == INF else Fr(m))
    if m is None:                                           # every B branch infinite: A decides
        m = min(x for x in cands if x != INF)
    lo = max(Fr(0), Fr(m))
    return dict(lo=lo, lo_float=float(lo), method="two-endpoint (A inc, B endpoint-min)",
                terms=terms, V=float(V))


# ===================================================================== the polygon-core chord
def poly_chord(verts, line):
    """|l n P| for a convex polygon given by exact rational ccw vertices.  Exact Fraction."""
    off = line.off
    j = 1 if line.orient == "h" else 0                      # coordinate compared with the offset
    i = 1 - j
    xs = []
    n = len(verts)
    for k in range(n):
        p, q = verts[k], verts[(k + 1) % n]
        dp, dq = Fr(p[j]) - off, Fr(q[j]) - off
        if dp == 0:
            xs.append(Fr(p[i]))
        if (dp < 0) != (dq < 0) and dp != 0 and dq != 0:
            xs.append(Fr(p[i]) + (Fr(q[i]) - Fr(p[i])) * (-dp) / (dq - dp))
    if len(xs) < 2:
        return Fr(0)
    return max(xs) - min(xs)


# ===================================================================== the line family
def pin_core_edges(pins, a_pin):
    """the guaranteed pin core's edge abscissae/heights: for a zero-tilt pin whose centre lies in
    [x0,x1]x[y0,y1], the square [x1-a, x0+a] x [y1-a, y0+a] with a = 1/2 lies in Q at every pose;
    the family uses the CORE half-side a_pin (A135's certified 1/2 - delta/sqrt2) as specified."""
    out = []
    for b in pins:
        cx, cy = (Fr(b.x0) + Fr(b.x1)) / 2, (Fr(b.y0) + Fr(b.y1)) / 2
        out.append(("v", cx - a_pin, "pin core x0"))
        out.append(("v", cx + a_pin, "pin core x1"))
        out.append(("v", cx, "pin midline x"))
        out.append(("h", cy - a_pin, "pin core y0"))
        out.append(("h", cy + a_pin, "pin core y1"))
        out.append(("h", cy, "pin midline y"))
    return out


def line_family(pins, hbox, s=S_RAT, pc_verts=None, a_pin=None, max_lines=40, extra=()):
    """The <= 40 guard lines of a node: through each pin core's edges and midlines, through K'(B)'s
    extreme and mid x/y, and the container-parallel lines at k*(1/8)*s.  Deduplicated, clipped to
    the open container, priority-ordered (pins, K', grid) and capped."""
    if a_pin is None:
        a_pin = HALF - DELTA / SQRT2_LO                     # A135's certified exact pin core
    cand = list(pin_core_edges(pins, a_pin))
    if pc_verts:
        xs = [Fr(v[0]) for v in pc_verts]
        ys = [Fr(v[1]) for v in pc_verts]
        cand += [("v", min(xs), "K' xmin"), ("v", max(xs), "K' xmax"),
                 ("v", (min(xs) + max(xs)) / 2, "K' xmid"),
                 ("h", min(ys), "K' ymin"), ("h", max(ys), "K' ymax"),
                 ("h", (min(ys) + max(ys)) / 2, "K' ymid")]
    else:
        cx = (Fr(hbox.x0) + Fr(hbox.x1)) / 2
        cy = (Fr(hbox.y0) + Fr(hbox.y1)) / 2
        cand += [("v", cx, "H xmid"), ("h", cy, "H ymid")]
    grid = [("h", Fr(k, 8) * s, f"grid h {k}/8") for k in range(1, 8)]
    grid += [("v", Fr(k, 8) * s, f"grid v {k}/8") for k in range(1, 8)]
    cand += grid
    cand = [(o, Fr(round(off * LDEN), LDEN), tg) for (o, off, tg) in cand] + \
           [(l.orient, l.off, l.tag) for l in extra]
    out, seen = [], set()
    for (o, off, tg) in cand:
        if not (Fr(0) < off < Fr(s)):
            continue
        if (o, off) in seen:
            continue
        seen.add((o, off))
        out.append(Line(o, off, tg))
        if len(out) >= max_lines:
            break
    return out


# ===================================================================== the row of one node
def node_boxes(rec):
    """(pins, conditioned box) from a stored node record: `Hyp(pins + [b])` order, pins are the
    zero-tilt-width boxes."""
    boxes = [Box.from_json(b) for b in rec["hyp"]["boxes"]]
    return boxes[:-1], boxes[-1]


def guard_row(pins, hbox, line, s=S_RAT, pc_verts=None, a=HALF):
    """rhs(l) = s - SUM_pins minchord - minchord(H), with every term exact."""
    pin_terms = [minchord_box(p, line, a=a) for p in pins]
    h_term = minchord_box(hbox, line, a=a)
    kprime = poly_chord(pc_verts, line) if pc_verts else None
    rhs = Fr(s) - sum((t["lo"] for t in pin_terms), Fr(0)) - h_term["lo"]
    return dict(line=line, rhs=rhs, rhs_float=float(rhs),
                pins=[t["lo"] for t in pin_terms], pins_float=[t["lo_float"] for t in pin_terms],
                h=h_term["lo"], h_float=h_term["lo_float"], h_terms=h_term["terms"],
                h_V=h_term["V"], h_method=h_term["method"],
                kprime=kprime, kprime_float=(float(kprime) if kprime is not None else None),
                uses="minchord(H)" if (kprime is None or h_term["lo"] >= kprime) else "K'(B) chord",
                n_pins_full=sum(1 for t in pin_terms if t["lo"] >= 1 - Fr(1, 10 ** 12)))


def support_chords(rec, line, a=0.5):
    """the dual support's per-column chord coefficients and their weighted sum."""
    pk = rec.get("packing") or []
    out = []
    for p in pk:
        c = chord_float(a, float(p["theta"]), line.offset_of(float(p["cx"]), float(p["cy"])))
        out.append(dict(cx=float(p["cx"]), cy=float(p["cy"]), theta=float(p["theta"]),
                        y=float(p.get("y", 0.0)), chord=c, wchord=c * float(p.get("y", 0.0))))
    return out, sum(o["wchord"] for o in out)


def column_coefficients_exact(rows, line, a=None, tden=1 << 24):
    """|l n Q_p| as EXACT rationals for a list of placements (cx, cy, theta): theta is snapped to
    the corpus's t-grid (t = tan(theta/2) rounded to 1/tden, the grid caselp.t_lo/t_hi use) and
    the centre to 1/10^9, so the coefficient the verifier recomputes is the one used here."""
    if a is None:
        a = HALF - Fr(round(lpbox.EPS_GEO * LDEN), LDEN)
    out = []
    for (cx, cy, th) in rows:
        t = Fr(round(math.tan(float(th) / 2.0) * tden), tden)
        t = min(max(t, Fr(0)), Fr(1))
        cxq, cyq = Fr(round(cx * LDEN), LDEN), Fr(round(cy * LDEN), LDEN)
        V = abs(line.off - (cyq if line.orient == "h" else cxq))
        out.append(chord_exact_t(a, t, V))
    return out


# ===================================================================== sampled confirmation
def sample_confirm(box, line, a=0.5, n=10000, seed=0):
    """10^4 poses of the square drawn uniformly in `box`: the true chord must be >= minchord."""
    mc = minchord_box(box, line, a=Fr(a))
    rng = np.random.default_rng(seed)
    cx = rng.uniform(box.x0, box.x1, n) if box.x1 > box.x0 else np.full(n, box.x0)
    cy = rng.uniform(box.y0, box.y1, n) if box.y1 > box.y0 else np.full(n, box.y0)
    th = np.radians(rng.uniform(box.th0, box.th1, n)) if box.th1 > box.th0 \
        else np.full(n, math.radians(box.th0))
    V = line.foff - (cy if line.orient == "h" else cx)
    ch = chord_many(a, th, V)
    lo = mc["lo_float"]
    return dict(n=int(n), minchord=lo, min_drawn=float(ch.min()), max_drawn=float(ch.max()),
                hits=int((ch < lo - 1e-12).sum()), slack=float(ch.min() - lo))


def sample_packings(s=S0, n_trial=10000, k=11, seed=1):
    """10^4 random interior-disjoint square sets in [0,s]^2 (rejection-greedy), each tested on a
    random axis-parallel line: SUM chords <= s.  The lemma is trivial; this is the drawn->tested
    ->hits line for it."""
    rng = np.random.default_rng(seed)
    worst, hits, tot_sq = -9e9, 0, 0
    for _ in range(n_trial):
        m = 3 * k
        th = rng.uniform(0, math.pi / 2, m)
        w = (np.cos(th) + np.sin(th)) / 2
        cx = rng.uniform(w, s - w)
        cy = rng.uniform(w, s - w)
        keep = []
        for i in range(m):
            ok = True
            for j in keep:
                if _sat_gap(cx[i], cy[i], th[i], cx[j], cy[j], th[j]) < 0:
                    ok = False
                    break
            if ok:
                keep.append(i)
            if len(keep) >= k:
                break
        if not keep:
            continue
        tot_sq += len(keep)
        horiz = rng.random() < 0.5
        off = rng.uniform(0, s)
        V = off - (cy[keep] if horiz else cx[keep])
        tot = float(chord_many(0.5, th[keep], V).sum())
        worst = max(worst, tot - s)
        hits += int(tot > s + 1e-9)
    return dict(trials=int(n_trial), squares=int(tot_sq), hits=int(hits),
                worst_excess=float(worst))


def _sat_gap(ax, ay, at, bx, by, bt):
    """SAT gap between two unit squares (>0 disjoint)."""
    best = -9e9
    d = np.array([bx - ax, by - ay])
    for th in (at, bt):
        for e in (np.array([math.cos(th), math.sin(th)]),
                  np.array([-math.sin(th), math.cos(th)])):
            g = 0.0
            for t2 in (at, bt):
                g += 0.5 * (abs(e[0] * math.cos(t2) + e[1] * math.sin(t2)) +
                            abs(-e[0] * math.sin(t2) + e[1] * math.cos(t2)))
            best = max(best, abs(float(d @ e)) - g)
    return best


# ===================================================================== self-test
if __name__ == "__main__":
    import json
    b = Box(2.357813, 2.49757, 2.637327, 2.777084, 82.3718503314193, 90.0)
    hh = float(DELTA) / math.sqrt(2.0)
    pins = [Box(x - hh, x + hh, y - hh, y + hh, 0.0, 0.0)
            for (x, y) in ((0.5, 0.5), (0.5, 1.5), (0.5, 3.3770839), (1.5, 0.5), (3.3770839, 0.5))]
    ln = Line("h", Fr(round((S0 - 0.99) * LDEN), LDEN), "PI 0.99 below the top")
    r = guard_row(pins, b, ln)
    print("line", ln, "rhs", float(r["rhs"]), "pins", r["pins_float"], "minchord(H)", r["h_float"])
    print("minchord(H) terms", r["h_terms"], "V", r["h_V"])
    print("sample H:", sample_confirm(b, ln))
    for p in pins:
        print("sample pin:", sample_confirm(p, ln))
    print("packings:", json.dumps(sample_packings(n_trial=400)))
    fam = line_family(pins, b)
    print(f"{len(fam)} lines:", [str(l) for l in fam[:6]])
