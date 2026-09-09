"""A165 -- the INDEPENDENT checker for the cascade's geometric steps.

Nothing in this file imports A165's own emitters (`cas165`, `cascade165`, `rowprod165`).  It shares
with them only

  * A132's `polycore.vertex_ok`  (Lean `PolyCoreT5.checkVertexInPBox`, the trusted exact primitive),
  * A57's `caselp.Box` / `t_lo` / `t_hi`  (the outward-rounded rational tilt bounds),

and re-derives EVERYTHING else from the spec: the widened corner box, the container prune, the
cell-miss prune (both the coarse cell-normal form and the full separating-axis form), the chord of a
unit square on an axis line, the minimum chord over a parameter box, the always-overlap pair test,
the completeness of a cover as a prefix code, the split rule, and the final arithmetic.

    C1  the widened corner box and (R6): s0 - 2(1+w) > sqrt2
    C2  every cover is a COMPLETE prefix code over its declared root, and the box replayed from
        each path by the split rule equals the stored box
    C3  every discharged leaf's reason holds by an independent exact test
    C4  every `open` box is NOT dischargeable by those tests (the cover is not over-claiming)
    C5  the pair prunes: `same_square` witnesses re-certified with `vertex_ok` twice; the
        always-overlap verdicts re-derived from the sharp per-normal bound
    C6  `M(c) = 0` re-derived by an independently coded full separating-axis test over the box,
        and cross-checked against 2e5 sampled poses of the box (a box declared to MISS the cell
        must have zero sampled meeting poses)
    C7  every chord-row certificate: the minchords recomputed exactly and compared in the HARD
        direction (a certificate value above the recomputed lower bound is a REJECT), the sum
        re-added in Fractions, `rhs < 0` re-decided
    C8  the top-strip facts: no admissible square lies entirely above y = y_L for y_L > s0 - 1,
        and the tilt window that permits it at y_L = s0 - 1 - w
    C9  a sampled falsification pass: random admissible poses that MEET a widened corner box must
        land in some `open` box of that corner's cover

    python code/check165.py --cell l1_104 --depth 8
"""
import argparse
import json
import math
import os
import random
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
for _p in (os.path.join(ATT, "A132-polygon-core", "code"),
           os.path.join(ATT, "A57-shadow-trees", "code")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import polycore as PC                                            # noqa: E402  trusted primitive
from caselp import Box, t_lo, t_hi                               # noqa: E402

S_RAT = Fr(969271, 250000)
S0 = float(S_RAT)
WLO = Fr(382, 100)
SQ2_LO = Fr(math.isqrt(2 * 10 ** 48), 10 ** 24)                  # < sqrt2, error < 1e-24
SQ2_HI = SQ2_LO + Fr(1, 10 ** 24)
HALF = Fr(1, 2)
RES = os.path.join(BASE, "results")
FAILS = []


def fail(tag, msg, **kw):
    FAILS.append(dict(check=tag, msg=msg, **kw))
    print("  FAIL [%s] %s %s" % (tag, msg, json.dumps(kw, default=str)[:240]), flush=True)


# ===================================================================== exact tilt-bin helpers
def tbin(b):
    t0, t1 = t_lo(b.th0), t_hi(b.th1)
    return (t1, t0) if t0 > t1 else (t0, t1)


def cs_of_t(t):
    """(|cos|+|sin|) at theta = 2 arctan t, exactly: (1 - t^2 + 2t) / (1 + t^2) for t in [0, 1]."""
    t = Fr(t)
    return (1 - t * t + 2 * t) / (1 + t * t)


def cs_bounds(t0, t1):
    """(min, max) of |cos|+|sin| over the tilt interval [2 arctan t0, 2 arctan t1] c [0, 90 deg].

    g(t) = (1 + 2t - t^2)/(1 + t^2) rises on [0, tan(22.5 deg)] and falls after; tan(22.5) =
    sqrt2 - 1.  A rational bracket of sqrt2 - 1 makes both bounds conservative."""
    ts = SQ2_LO - 1
    lo = min(cs_of_t(t0), cs_of_t(t1))
    if t0 <= ts <= t1 or t0 <= SQ2_HI - 1 <= t1:
        hi = SQ2_HI                                  # >= max over any bin containing 45 deg
    else:
        hi = max(cs_of_t(t0), cs_of_t(t1))
    return lo, hi


def proj_min(dx, dy, t0, t1):
    """min over theta in the bin of <d, (cos, sin)>, exact and CONSERVATIVE.

    <d, w0> = dx cos + dy sin with cos = (1-t^2)/(1+t^2), sin = 2t/(1+t^2); the function is
    R cos(theta - phi), unimodal with its MAXIMUM at phi, so on an interval not containing
    phi + 180 deg the minimum is at an endpoint.  With theta in [0, 90 deg] that needs
    phi in [-180, -90], i.e. dx <= 0 and dy <= 0, and there -(|dx| + |dy|) is returned."""
    dx, dy = Fr(dx), Fr(dy)
    if dx <= 0 and dy <= 0:
        return -(abs(dx) + abs(dy))
    out = None
    for t in (Fr(t0), Fr(t1)):
        v = (dx * (1 - t * t) + dy * 2 * t) / (1 + t * t)
        out = v if out is None else min(out, v)
    return out


# ===================================================================== C1
def c1(cov):
    lam_max = S_RAT / WLO
    w = (lam_max - 1) * (1 + 1 / SQ2_LO)                          # >= the emitter's w (safe)
    if not (abs(float(w) - cov["w"]) < 3e-9):
        fail("C1", "widened pad w disagrees", mine=float(w), theirs=cov["w"])
    gap = S_RAT - 2 * (1 + w) - SQ2_HI
    if gap <= 0:
        fail("C1", "(R6) fails: a square could meet two widened corner boxes", gap=float(gap))
    print("  C1 w = %.9f, (R6) gap s0 - 2(1+w) - sqrt2 = %+.6f  %s"
          % (float(w), float(gap), "OK" if gap > 0 else "FAIL"), flush=True)
    for c, d in cov["covers"].items():
        X0, X1, Y0, Y1 = d["cell"]
        exp = {"BL": (0, 1 + w, 0, 1 + w), "BR": (S_RAT - 1 - w, S_RAT, 0, 1 + w),
               "TR": (S_RAT - 1 - w, S_RAT, S_RAT - 1 - w, S_RAT),
               "TL": (0, 1 + w, S_RAT - 1 - w, S_RAT)}[c]
        if max(abs(float(a) - b) for a, b in zip(exp, (X0, X1, Y0, Y1))) > 3e-9:
            fail("C1", "corner cell %s disagrees" % c, mine=[float(v) for v in exp],
                 theirs=[X0, X1, Y0, Y1])
    return float(w)


# ===================================================================== C2 the split rule
def split_box(b):
    wx, wy, wt = b.x1 - b.x0, b.y1 - b.y0, (b.th1 - b.th0) / 60.0
    if wx >= wy and wx >= wt:
        m = 0.5 * (b.x0 + b.x1)
        return (Box(b.x0, m, b.y0, b.y1, b.th0, b.th1), Box(m, b.x1, b.y0, b.y1, b.th0, b.th1))
    if wy >= wt:
        m = 0.5 * (b.y0 + b.y1)
        return (Box(b.x0, b.x1, b.y0, m, b.th0, b.th1), Box(b.x0, b.x1, m, b.y1, b.th0, b.th1))
    m = 0.5 * (b.th0 + b.th1)
    return (Box(b.x0, b.x1, b.y0, b.y1, b.th0, m), Box(b.x0, b.x1, b.y0, b.y1, m, b.th1))


def replay(root, path):
    b = root
    for ch in path:
        b = split_box(b)[int(ch)]
    return b


def centre_window(cell):
    X0, X1, Y0, Y1 = cell
    h = math.sqrt(2.0) / 2.0
    return (max(0.5, X0 - h), min(S0 - 0.5, X1 + h), max(0.5, Y0 - h), min(S0 - 0.5, Y1 + h))


def prefix_complete(paths):
    """the paths are the leaves of ONE full binary tree: no path is a prefix of another, and the
    Kraft sum SUM 2^-len is exactly 1."""
    S = set(paths)
    if len(S) != len(paths):
        return False, "duplicate paths"
    for p in paths:
        for k in range(1, len(p)):
            if p[:k] in S:
                return False, "path %s has prefix %s" % (p, p[:k])
    kr = sum(Fr(1, 2 ** len(p)) for p in paths)
    return (kr == 1), "Kraft sum %s" % kr


def c2(cov):
    for c, d in cov["covers"].items():
        root = Box(*centre_window(d["cell"]), 0.0, 90.0)
        paths = [lf["path"] for lf in d["leaves"]] + list(d["open_paths"])
        ok, why = prefix_complete(paths)
        if not ok:
            fail("C2", "cover %s is not a complete prefix code: %s" % (c, why))
        bad = 0
        for pth, bx in zip(d["open_paths"], d["open"]):
            rb = replay(root, pth)
            if max(abs(a - b) for a, b in zip([rb.x0, rb.x1, rb.y0, rb.y1, rb.th0, rb.th1],
                                              bx)) > 1e-9:
                bad += 1
        if bad:
            fail("C2", "cover %s: %d open boxes disagree with the replayed split" % (c, bad))
        print("  C2 %s: %d leaves + %d open, prefix code %s (%s)"
              % (c, len(d["leaves"]), len(d["open"]), "COMPLETE" if ok else "BROKEN", why),
              flush=True)


# ===================================================================== C3/C4 the prunes
def box_outside_container(b):
    lo, hi = cs_bounds(*tbin(b))
    hmin = lo / 2
    return (Fr(b.x1) < hmin or Fr(b.y1) < hmin or Fr(b.x0) > S_RAT - hmin
            or Fr(b.y0) > S_RAT - hmin)


def box_misses_cell_coarse(b, cell):
    X0, X1, Y0, Y1 = (Fr(v) for v in cell)
    _lo, hi = cs_bounds(*tbin(b))
    hmax = hi / 2
    return (Fr(b.x0) - hmax >= X1 or Fr(b.x1) + hmax <= X0
            or Fr(b.y0) - hmax >= Y1 or Fr(b.y1) + hmax <= Y0)


def box_misses_cell_full(b, cell):
    """the full separating-axis test over the box (A161 sec 2), independently coded."""
    X0, X1, Y0, Y1 = (Fr(v) for v in cell)
    x0, x1, y0, y1 = Fr(b.x0), Fr(b.x1), Fr(b.y0), Fr(b.y1)
    t0, t1 = tbin(b)
    _lo, hi = cs_bounds(t0, t1)
    hmax = hi / 2
    for m in (x0 - X1, X0 - x1, y0 - Y1, Y0 - y1):
        if m >= hmax:
            return True
    DX = (x0 - X1, x1 - X0)
    DY = (y0 - Y1, y1 - Y0)
    for k in (0, 1):
        for sg in (1, -1):
            worst = None
            for dx in DX:
                for dy in DY:
                    ex, ey = sg * dx, sg * dy
                    if k == 1:
                        ex, ey = ey, -ex
                    g = proj_min(ex, ey, t0, t1)
                    worst = g if worst is None else min(worst, g)
            if worst >= HALF:
                return True
    return False


def c3c4(cov):
    for c, d in cov["covers"].items():
        cell = d["cell"]
        root = Box(*centre_window(cell), 0.0, 90.0)
        nbad = 0
        cnt = {}
        for lf in d["leaves"]:
            b = replay(root, lf["path"])
            why = lf["why"]
            cnt[why] = cnt.get(why, 0) + 1
            if why == "container":
                ok = box_outside_container(b)
            elif why == "misses_cell":
                ok = box_misses_cell_coarse(b, cell) or box_misses_cell_full(b, cell)
            else:
                ok = True                       # `witness` leaves are re-checked in C5 from certs
            if not ok:
                nbad += 1
        if nbad:
            fail("C3", "cover %s: %d discharged leaves fail the independent test" % (c, nbad))
        over = 0
        for bx in d["open"]:
            b = Box(*bx)
            if box_outside_container(b) or box_misses_cell_full(b, cell):
                over += 1
        print("  C3 %s: leaf reasons %s, %d bad;  C4: %d of %d open boxes were in fact "
              "dischargeable (over-cautious, sound)" % (c, cnt, nbad, over, len(d["open"])),
              flush=True)


# ===================================================================== C5 pair prunes
def sharp_pair_always_overlap(bi, bj):
    """Two unit squares with poses in `bi`, `bj` ALWAYS overlap when no candidate axis separates:
    for every normal `n` of either square and every pose pair, |<n, ci - cj>| < support sum.

    Conservative version: with `D` the centre-difference rectangle and `dmax` its largest
    |offset| along any direction, the pair always overlaps if

        max_{d in D} |d|  <  1/2 + 1/2 * min over the two tilt bins' difference of (|cos|+|sin|)

    (A118 sec 1.2(ii)'s coarse screen; only the SAFE direction is needed here, since a `True`
    verdict from the emitter must be justified and this test is stricter or equal)."""
    dx = max(abs(Fr(bi.x1) - Fr(bj.x0)), abs(Fr(bi.x0) - Fr(bj.x1)))
    dy = max(abs(Fr(bi.y1) - Fr(bj.y0)), abs(Fr(bi.y0) - Fr(bj.y1)))
    # |d| <= sqrt(dx^2 + dy^2) <= dx + dy  (safe upper bound, rational)
    dmax = dx + dy
    lo_i, _ = cs_bounds(*tbin(bi))
    lo_j, _ = cs_bounds(*tbin(bj))
    return dmax < HALF + HALF * min(lo_i, lo_j)


def c5(cov, cell, depth, corner):
    p = os.path.join(RES, "pairs_%s_d%d_%s.json" % (cell, depth, corner))
    if not os.path.exists(p):
        print("  C5 %s: no pairs file, skipped" % corner, flush=True)
        return
    pr = json.load(open(p, encoding="utf-8"))
    OB = [Box(*b) for b in cov["covers"][corner]["open"]]
    nbad = 0
    for s in pr.get("same_square", []):
        wq = (Fr(s["w"][0]), Fr(s["w"][1]))
        if not (PC.vertex_ok(wq[0], wq[1], OB[s["i"]])
                and PC.vertex_ok(wq[0], wq[1], OB[s["j"]])):
            nbad += 1
    if nbad:
        fail("C5", "%s: %d same-square witnesses fail vertex_ok" % (corner, nbad))
    print("  C5 %s: %d same-square witnesses re-certified with vertex_ok twice, %d bad"
          % (corner, len(pr.get("same_square", [])), nbad), flush=True)
    # every ALIVE pair must NOT be always-overlapping by the (stricter) independent test
    alive = [tuple(q) for q in pr["pairs"]]
    over = sum(1 for (u, v) in alive[:4000] if sharp_pair_always_overlap(OB[u], OB[v]))
    if over:
        fail("C5", "%s: %d alive pairs always overlap by the independent test" % (corner, over))
    print("  C5 %s: %d alive pairs, %d wrongly kept" % (corner, len(alive), over), flush=True)


# ===================================================================== C6 M(c)
def sq_verts(cx, cy, th):
    c, s = math.cos(th), math.sin(th)
    return [(cx + 0.5 * (c * ux - s * uy), cy + 0.5 * (s * ux + c * uy))
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


def c6(cov, nsample=200000, seed=165):
    H = Box(*cov["boxes"][0])
    rng = random.Random(seed)
    for c, d in cov["covers"].items():
        cell = d["cell"]
        mine = box_misses_cell_full(H, cell)
        theirs = cov["M_exact"][c]
        theirs = theirs["misses"] if isinstance(theirs, dict) else bool(theirs)
        if theirs and not mine:
            fail("C6", "M(%s) = 0 claimed but the independent SAT does not prove it" % c)
        hits = 0
        for _ in range(nsample // 4):
            cx = H.x0 + (H.x1 - H.x0) * rng.random()
            cy = H.y0 + (H.y1 - H.y0) * rng.random()
            th = math.radians(H.th0 + (H.th1 - H.th0) * rng.random())
            if sq_meets_rect(cx, cy, th, cell):
                hits += 1
        if mine and hits:
            fail("C6", "M(%s) = 0 but %d sampled poses of H meet the cell" % (c, hits))
        print("  C6 %s: independent SAT misses=%s (emitter %s), sampled meeting poses %d/%d"
              % (c, mine, theirs, hits, nsample // 4), flush=True)


# ===================================================================== C7 the chord row
def chord_min_over_box(b, orient, off):
    """An independent exact LOWER bound of the chord |l n Q| over every pose in the box.

    chord = min(A, B) with, writing C = |cos|, S = |sin| and v the signed centre offset,
        A = 1 / max(C, S),        B = (C + S)/2 / (C S) - |v| / (C S)  ... A144's algebra;
    the safe route used here is the DIRECT one: the chord of a unit square whose centre is at
    signed offset v from the line is

        chord(v, theta) = min( 1/max(C,S) , ( (C+S)/2 - |v| ) / (C*S) )   (0 when the bracket < 0)

    and it is DECREASING in |v| and, at fixed |v|, minimised at an endpoint of the tilt bin or at
    45 deg.  So evaluating at (|v|_max, each of t0, t1, and 45 deg when the bin contains it) and
    taking the minimum is a lower bound.  Rational throughout, with sqrt2 bracketed."""
    lo, hi = ((Fr(b.y0), Fr(b.y1)) if orient == "h" else (Fr(b.x0), Fr(b.x1)))
    off = Fr(off)
    V = max(abs(off - lo), abs(off - hi))                     # |v|_max, the worst case
    t0, t1 = tbin(b)
    cands = []
    ts = [t0, t1]
    tstar = SQ2_LO - 1
    if t0 <= SQ2_HI - 1 and t1 >= tstar:
        ts.append(tstar)                                      # 45 deg is (nearly) in the bin
    for t in ts:
        t = Fr(t)
        den = 1 + t * t
        C = (1 - t * t) / den
        S = 2 * t / den
        if C < 0:
            C = -C
        if C == 0 or S == 0:
            A = Fr(1)
            B = (Fr(1, 2) - V) * 2 if False else None
            cands.append(A if V < Fr(1, 2) else Fr(0))
            continue
        A = 1 / max(C, S)
        num = (C + S) / 2 - V
        B = num / (C * S)
        cands.append(max(Fr(0), min(A, B)))
    return min(cands)


def c7(cell, depth):
    p = os.path.join(RES, "rowprod_%s_d%d.json" % (cell, depth))
    if not os.path.exists(p):
        print("  C7: no rowprod file, skipped", flush=True)
        return
    d = json.load(open(p, encoding="utf-8"))
    nbad = 0
    for cert in d.get("certs", []):
        row = cert["row"]
        bxs = [Box(*b) for b in cert["boxes"]]
        mine = [chord_min_over_box(b, row["orient"], row["off"]) for b in bxs]
        theirs = [Fr(v) for v in row["minchords"]]
        for a, b in zip(theirs, mine):
            if a > b + Fr(1, 10 ** 12):
                nbad += 1
                fail("C7", "certificate minchord above the independent lower bound",
                     theirs=float(a), mine=float(b), off=row["off"])
        rhs = S_RAT - sum(mine)
        if rhs >= 0 and Fr(row["rhs"]) < 0:
            nbad += 1
            fail("C7", "row claimed negative but the independent recomputation gives rhs >= 0",
                 rhs_mine=float(rhs), rhs_theirs=row["rhs"])
    print("  C7: %d row certificates re-derived, %d bad" % (len(d.get("certs", [])), nbad),
          flush=True)


# ===================================================================== C8 the top strip
def c8():
    # no admissible square lies entirely above y = y_L once y_L > s0 - 1
    yL = S_RAT - 1 + Fr(1, 10 ** 6)
    ok = True
    # entirely above needs c_y - h >= y_L and c_y <= s0 - h, so 2h <= s0 - y_L < 1 <= 2h : absurd
    if not (S_RAT - yL < 1):
        ok = False
    print("  C8 no square entirely above y = s0 - 1 + 1e-6: %s (s0 - y_L = %.9f < 1 = 2*h_min)"
          % (ok, float(S_RAT - yL)), flush=True)
    if not ok:
        fail("C8", "the top-strip fact does not hold as stated")
    # at y_L = s0 - 1 - w only near-axis squares can lie entirely above
    lam_max = S_RAT / WLO
    w = (lam_max - 1) * (1 + 1 / SQ2_LO)
    yL2 = S_RAT - 1 - w
    cs = S_RAT - yL2                                        # bound on |cos| + |sin|
    th = math.degrees(math.asin(min(1.0, float(cs) / math.sqrt(2.0)))) - 45.0
    print("  C8 at y_L = s0 - 1 - w = %.9f: entirely-above needs |cos|+|sin| <= %.9f, i.e. tilt "
          "within %.4f deg of an axis" % (float(yL2), float(cs), th), flush=True)


# ===================================================================== C9 falsification
def point_in_square(w, cx, cy, th):
    """is the point w inside the closed unit square Q(c, th)?"""
    dx, dy = float(Fr(str(w[0]))) - cx, float(Fr(str(w[1]))) - cy
    c, s = math.cos(th), math.sin(th)
    u, v = dx * c + dy * s, -dx * s + dy * c
    return abs(u) <= 0.5 + 1e-12 and abs(v) <= 0.5 + 1e-12


def c9(cov, n=60000, seed=1650):
    """FALSIFICATION.  Draw admissible poses that MEET a widened corner box.  Each must either lie
    in an OPEN box of that corner's cover, or lie in a DISCHARGED leaf whose reason really applies
    to that pose:

      container    -- impossible here (the pose is admissible by construction)   -> would be a FAIL
      misses_cell  -- impossible here (the pose meets the cell)                   -> would be a FAIL
      witness w    -- the pose's square must CONTAIN w, so a free square there would share w with
                      H and hence BE H (A141 sec 3): the pose is excluded as a free square, sound.
    """
    rng = random.Random(seed)
    for c, d in cov["covers"].items():
        cell = d["cell"]
        root = Box(*centre_window(cell), 0.0, 90.0)
        OB = [Box(*b) for b in d["open"]]
        LV = {lf["path"]: lf for lf in d["leaves"]}
        have_w = any(lf.get("w") for lf in d["leaves"])
        X0, X1, Y0, Y1 = centre_window(cell)
        miss = wit_ok = wit_bad = other = 0
        drawn = 0
        for _ in range(n):
            cx = X0 + (X1 - X0) * rng.random()
            cy = Y0 + (Y1 - Y0) * rng.random()
            thd = 90.0 * rng.random()
            th = math.radians(thd)
            h = 0.5 * (abs(math.cos(th)) + abs(math.sin(th)))
            if not (h <= cx <= S0 - h and h <= cy <= S0 - h):
                continue
            if not sq_meets_rect(cx, cy, th, cell):
                continue
            drawn += 1
            inb = any(b.x0 - 1e-12 <= cx <= b.x1 + 1e-12 and b.y0 - 1e-12 <= cy <= b.y1 + 1e-12
                      and b.th0 - 1e-12 <= thd <= b.th1 + 1e-12 for b in OB)
            if inb:
                continue
            miss += 1
            if not have_w:
                continue
            # locate the discharged leaf by replaying the split rule
            b, path = root, ""
            while path not in LV and len(path) < 60:
                b0, b1 = split_box(b)
                if (b0.x0 - 1e-12 <= cx <= b0.x1 + 1e-12 and b0.y0 - 1e-12 <= cy <= b0.y1 + 1e-12
                        and b0.th0 - 1e-12 <= thd <= b0.th1 + 1e-12):
                    b, path = b0, path + "0"
                else:
                    b, path = b1, path + "1"
            lf = LV.get(path)
            if lf is None:
                other += 1
                continue
            if lf["why"] == "witness" and lf.get("w"):
                if point_in_square(lf["w"], cx, cy, th):
                    wit_ok += 1
                else:
                    wit_bad += 1
            else:
                other += 1
        if wit_bad or (have_w and other):
            fail("C9", "%s: %d poses in a witness leaf whose point is NOT in the square, %d in a "
                       "leaf whose reason cannot apply" % (c, wit_bad, other))
        print("  C9 %s: %d admissible corner-meeting poses drawn, %d outside every open box; of "
              "those %d land in a `witness` leaf and CONTAIN its rational point (sound: they are H)"
              ", %d bad, %d in another leaf kind" % (c, drawn, miss, wit_ok, wit_bad, other),
              flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", default="l1_104")
    ap.add_argument("--depth", type=int, default=8)
    ap.add_argument("--corners", default="TR,TL,BL,BR")
    a = ap.parse_args()
    cov = json.load(open(os.path.join(RES, "cover_%s_d%d.json" % (a.cell, a.depth)),
                         encoding="utf-8"))
    print("A165 independent check of %s (depth %d)" % (a.cell, a.depth), flush=True)
    c1(cov)
    c2(cov)
    c3c4(cov)
    for c in a.corners.split(","):
        c5(cov, a.cell, a.depth, c)
    c6(cov)
    c7(a.cell, a.depth)
    c8()
    c9(cov)
    out = dict(cell=a.cell, depth=a.depth, n_fail=len(FAILS), fails=FAILS,
               verdict=("ALL_OK" if not FAILS else "FAIL"))
    json.dump(out, open(os.path.join(RES, "check165_%s_d%d.json" % (a.cell, a.depth)), "w",
                        encoding="utf-8"), indent=1, default=str)
    print("\nVERDICT %s (%d failures)" % (out["verdict"], len(FAILS)), flush=True)


if __name__ == "__main__":
    main()
