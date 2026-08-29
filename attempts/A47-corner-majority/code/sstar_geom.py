#!/usr/bin/env python3
"""
A47 leg (a) / TASK 2 -- exact rational geometry of the s* exception structure.

THE STRUCTURE (theory.md Corollary T1a(ii)).  s* = 2 sqrt2 + 1.  Chain C(y0,b) = D_L u U u D_R:
    D_L : diamond |x - sqrt2/2| + |y - y0| <= sqrt2/2
    U   : [sqrt2, sqrt2+1] x [b, b+1]
    D_R : diamond |x - (3 sqrt2/2 + 1)| + |y - y0| <= sqrt2/2
with y0 in [sqrt2/2, sqrt2 + 1/2] (up-down symmetry half) and b in [max(0,y0-1), y0]
(b >= 0 because U must lie in the container [0,s*]^2).

MONOTONE RATIONAL RELAXATION (this module).  Fix a rational lambda with 1 < lambda and
lambda*s* <= s' = 383/100.  If 8 unit squares with pairwise disjoint interiors lie in [0,s*]^2
and are interior-disjoint from C(y0,b), then scaling by lambda about the origin and shrinking
each square about its centre back to side 1 gives 8 PAIRWISE DISJOINT CLOSED unit squares inside
[0,s']^2, each interior-disjoint from lambda*C(y0,b).  (Shrinking is strict: two convex sets with
disjoint interiors are separated by a line; the lambda-square's support radius R >= 1/2 about its
centre gives the shrunk square slack (lambda-1)R > 0 on each side.)

So it suffices to exhibit, for each rational parameter box B = [y0lo,y0hi] x [blo,bhi], a RATIONAL
convex polygon C_shr(B) (here: a union of three convex polygons P_L, P_U, P_R) with

        C_shr(B)  contained in  lambda * C(y0,b)      for every (y0,b) in B,          (*)

and a measure certificate with total mass < 8 such that every closed unit square in [0,s']^2 whose
interior misses C_shr has mass >= 1.  Then the 8 squares would have total mass >= 8 > total.

(*) is certified HERE, exactly.  Each piece of C is an intersection of four half-planes
a.p <= c(y0 or b) whose right-hand sides are AFFINE in the parameter (coefficient +-1) plus a
multiple of sqrt2; multiplying by lambda scales the right-hand sides.  A certified rational LOWER
bound for min over B of the true right-hand side is obtained by taking the worse parameter endpoint
and replacing sqrt2 by R2LO or R2HI as the sign demands.  P is then defined by those lower bounds
minus an inward margin DELTA, so every point of P satisfies each true half-plane STRICTLY with slack
>= DELTA, i.e. P is contained in the INTERIOR of lambda*C.  `check_piece_containment` re-derives the
bounds and checks every vertex of P against them (exact Fractions).

Interiority matters: the verifier's exemption rule discharges a placement box when some rational
point p lies (i) in P (hence in the interior of lambda*C) and (ii) inside Q(c,theta) for EVERY
placement of the box.  Such a Q has int(Q) meeting int(lambda*C), so Q is not one of the 8 squares.
"""
from fractions import Fraction as F

# ---------------------------------------------------------------- constants (all exact rationals)
R2LO = F(1414213562, 10 ** 9)          # < sqrt2
R2HI = F(1414213563, 10 ** 9)          # > sqrt2
assert R2LO ** 2 < 2 < R2HI ** 2

SP = F(383, 100)                       # s' : relaxed container side
LAM = F(10001, 10000)                  # lambda > 1 with lambda*s* <= s'
S_STAR_HI = 2 * R2HI + 1               # > s*
S_STAR_LO = 2 * R2LO + 1               # < s*
assert LAM > 1 and LAM * S_STAR_HI <= SP, "lambda*s* must fit in [0,s']"

DELTA = F(1, 256)                      # inward margin of the rational obstacle

PIECES = ("D_L", "U", "D_R")

# parameter domain (exact rational super-interval of the true one)
Y0_MIN = F(70, 100)                    # < sqrt2/2 = 0.70710678
Y0_MAX = F(1915, 1000)                 # > sqrt2 + 1/2 = 1.91421356
assert Y0_MIN <= R2LO / 2 and Y0_MAX >= R2HI + F(1, 2)


# ---------------------------------------------------------------- half-planes of lambda * piece
def piece_rhs_lower(name, y0lo, y0hi, blo, bhi):
    """Four half-planes (ax, ay, c) with ax*x + ay*y <= c, where c is a certified rational LOWER
    bound of  min over the parameter box  of the true right-hand side of that half-plane of
    lambda * piece.  (a.p <= c  ==>  a.p <= true rhs for every parameter in the box.)"""
    L = LAM
    if name == "D_L":
        # |x - sqrt2/2| + |y - y0| <= sqrt2/2   ->  rhs: sqrt2+y0, sqrt2-y0, y0, -y0
        return [(F(1), F(1), L * (R2LO + y0lo)),
                (F(1), F(-1), L * (R2LO - y0hi)),
                (F(-1), F(1), L * y0lo),
                (F(-1), F(-1), L * (-y0hi))]
    if name == "D_R":
        # centre 3 sqrt2/2 + 1, radius sqrt2/2 : c+r = 2 sqrt2 + 1, c-r = sqrt2 + 1
        return [(F(1), F(1), L * (2 * R2LO + 1 + y0lo)),
                (F(1), F(-1), L * (2 * R2LO + 1 - y0hi)),
                (F(-1), F(1), L * (-(R2HI + 1) + y0lo)),
                (F(-1), F(-1), L * (-(R2HI + 1) - y0hi))]
    if name == "U":
        # [sqrt2, sqrt2+1] x [b, b+1]
        return [(F(-1), F(0), L * (-R2HI)),
                (F(1), F(0), L * (R2LO + 1)),
                (F(0), F(-1), L * (-bhi)),
                (F(0), F(1), L * (blo + 1))]
    raise ValueError(name)


def piece_halfplanes(name, box, delta=DELTA):
    """the rational half-planes DEFINING P (the shrunk piece): rhs lower bound minus delta."""
    y0lo, y0hi, blo, bhi = box
    return [(a, b, c - delta) for (a, b, c) in piece_rhs_lower(name, y0lo, y0hi, blo, bhi)]


# ---------------------------------------------------------------- exact convex polygon clipping
BIGBOX = [(F(-2), F(-2)), (SP + 2, F(-2)), (SP + 2, SP + 2), (F(-2), SP + 2)]


def clip_poly(poly, hp):
    a, b, c = hp
    out = []
    n = len(poly)
    for i in range(n):
        P = poly[i]
        Q = poly[(i + 1) % n]
        fp = a * P[0] + b * P[1] - c
        fq = a * Q[0] + b * Q[1] - c
        if fp <= 0:
            out.append(P)
        if (fp < 0 < fq) or (fq < 0 < fp):
            tt = fp / (fp - fq)
            out.append((P[0] + tt * (Q[0] - P[0]), P[1] + tt * (Q[1] - P[1])))
    return out


def piece_polygon(name, box, delta=DELTA):
    """vertices (exact) of P = the rational shrunk piece; [] if empty."""
    poly = list(BIGBOX)
    for hp in piece_halfplanes(name, box, delta):
        poly = clip_poly(poly, hp)
        if not poly:
            return []
    return poly


def check_piece_containment(name, box, verts, delta=DELTA):
    """REQUIRED exact check: every vertex of P satisfies every half-plane of lambda*piece with
    slack >= delta, for EVERY parameter in the box.  Returns (ok, min_slack)."""
    y0lo, y0hi, blo, bhi = box
    hps = piece_rhs_lower(name, y0lo, y0hi, blo, bhi)
    if not verts:
        return False, None
    best = None
    for (vx, vy) in verts:
        for (a, b, c) in hps:
            slack = c - (a * vx + b * vy)
            if best is None or slack < best:
                best = slack
            if slack < delta:
                return False, slack
    return True, best


# ---------------------------------------------------------------- independent sampled sanity check
R2LO_T = F(141421356237309504880168872420969807856, 10 ** 38)
R2HI_T = F(141421356237309504880168872420969807857, 10 ** 38)
assert R2LO_T ** 2 < 2 < R2HI_T ** 2


def true_piece_rhs_lower_at(name, y0, b):
    """certified rational lower bounds for the right-hand sides of lambda*piece at a SINGLE exact
    parameter value (tight sqrt2, 38 digits) -- used only as an independent bug-catcher."""
    L = LAM
    if name == "D_L":
        return [(F(1), F(1), L * (R2LO_T + y0)), (F(1), F(-1), L * (R2LO_T - y0)),
                (F(-1), F(1), L * y0), (F(-1), F(-1), L * (-y0))]
    if name == "D_R":
        return [(F(1), F(1), L * (2 * R2LO_T + 1 + y0)), (F(1), F(-1), L * (2 * R2LO_T + 1 - y0)),
                (F(-1), F(1), L * (-(R2HI_T + 1) + y0)), (F(-1), F(-1), L * (-(R2HI_T + 1) - y0))]
    if name == "U":
        return [(F(-1), F(0), L * (-R2HI_T)), (F(1), F(0), L * (R2LO_T + 1)),
                (F(0), F(-1), L * (-b)), (F(0), F(1), L * (b + 1))]
    raise ValueError(name)


def sampled_containment_ok(name, box, verts, nsamp=5):
    y0lo, y0hi, blo, bhi = box
    for i in range(nsamp):
        y0 = y0lo + (y0hi - y0lo) * F(i, max(1, nsamp - 1))
        for j in range(nsamp):
            b = blo + (bhi - blo) * F(j, max(1, nsamp - 1))
            hps = true_piece_rhs_lower_at(name, y0, b)
            for (vx, vy) in verts:
                for (a, bb, c) in hps:
                    if a * vx + bb * vy > c:
                        return False
    return True


# ---------------------------------------------------------------- obstacle bundle
def build_obstacle(box, delta=DELTA):
    """returns dict: name -> {"halfplanes": [(a,b,c)], "verts": [...]}, all exact; raises on failure."""
    out = {}
    for name in PIECES:
        verts = piece_polygon(name, box, delta)
        if not verts:
            raise ValueError(f"piece {name} empty for box {box}")
        ok, slack = check_piece_containment(name, box, verts, delta)
        if not ok:
            raise AssertionError(f"containment check FAILED for {name} on {box} (slack {slack})")
        out[name] = {"halfplanes": piece_halfplanes(name, box, delta), "verts": verts,
                     "min_slack": slack}
    return out


def poly_area(verts):
    a = F(0)
    n = len(verts)
    for i in range(n):
        x0, y0 = verts[i]
        x1, y1 = verts[(i + 1) % n]
        a += x0 * y1 - x1 * y0
    return abs(a) / 2


# ---------------------------------------------------------------- parameter box grid
def b_range(y0lo, y0hi):
    """physical range of b over the y0 box: b in [max(0, y0-1), y0]."""
    return max(F(0), y0lo - 1), y0hi


def param_boxes(y0_step=F(1, 8), b_step=F(1, 4)):
    boxes = []
    y = Y0_MIN
    while y < Y0_MAX:
        y1 = min(y + y0_step, Y0_MAX)
        b0, b1 = b_range(y, y1)
        bb = b0
        while bb < b1:
            bb1 = min(bb + b_step, b1)
            boxes.append((y, y1, bb, bb1))
            bb = bb1
        y = y1
    return boxes


def box_name(box):
    def f(x):
        return str(F(x)).replace("/", "_")
    return "y%s-%s_b%s-%s" % tuple(f(v) for v in box)


if __name__ == "__main__":
    import sys
    bs = param_boxes()
    print(f"{len(bs)} parameter boxes (y0 step 1/8, b step 1/4)")
    tot_bad = 0
    for box in bs:
        ob = build_obstacle(box)
        ar = sum(poly_area(ob[n]["verts"]) for n in PIECES)
        sm = all(sampled_containment_ok(n, box, ob[n]["verts"]) for n in PIECES)
        if not sm:
            tot_bad += 1
        print(f"  {box_name(box):34s} obstacle area {float(ar):.4f}  "
              f"minslack {float(min(ob[n]['min_slack'] for n in PIECES)):.5f}  sampled_ok={sm}")
    print("sampled sanity failures:", tot_bad)
    sys.exit(1 if tot_bad else 0)
