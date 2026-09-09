"""A161 -- the CHORD-LIMITED LANE leaf: A144's chord row splits the slot's meeters into a BAND
whose size the row caps, and an OUTSIDE set that A141's lane cover empties.

THE LEAF (stated in notes/leaf.md, sec 1; here is the shape the code computes).

Let `C = [i, i+1] x [j, j+1]` be a USABLE slot cell of a pinned class `S` in the cell's corner
frame, WALL-ADJACENT (`j = 0`, so the frame's bottom wall `y = 0` bounds the cell; the transpose
`i = 0` uses the left wall).  Let `l : y = y_L` with `0 < y_L < 1` be the WALL GUARD LINE, and let
`B_0 .. B_{m-1}` be the node's hypothesis boxes in that frame (the class pins and the conditioned
squares), every one hulled over the side window.  Put

    rhs(l)  =  s0  -  SUM_j minchord(B_j, l)                      (A144 LINE-2)
    beta    =  floor(rhs(l))                                      (the BAND cap)
    BAND    =  { poses with chord on l  >= 1 }
    LANE_out = max # of pairwise interior-disjoint FREE squares whose pose meets int C, avoids
               every K'(B_j), and is NOT in BAND
    M        = # conditioned squares that can meet int C

Then  #{non-pin squares meeting int C}  <=  beta + LANE_out + M, and SLOT-CROWD (A94/A109) forces
that count to be >= 2.  So `beta + LANE_out + M <= 1` KILLS the node.

WHY EACH TERM IS SOUND.

* `beta`: a square whose chord on `l` is `>= 1` charges `>= 1` against `rhs(l)`, and A144's LINE-1
  + LINE-2 cap the total charge of the NON-hypothesis squares at `rhs(l)`.  So at most
  `floor(rhs(l))` free squares are in BAND -- whether or not they meet `C`.  `minchord` is A144's
  exact five-point minimum over the box (a pin's zero-width tilt bin gives an EXACT 1 when `l` runs
  inside its core's height range).
* `LANE_out`: A141's lane cover with ONE extra sound prune, `band` -- a box every pose of which has
  chord `>= 1` is discharged, because its poses are counted by `beta` instead.  The other three
  prunes are A141's, unchanged: `container`, `misses_cell`, `witness`.
* `M`: A141's `cond_can_meet`, with a STRONGER exact `misses_cell` (below).
* the three sets cover every non-pin meeter of `int C`: a meeter is either a conditioned square
  (`M`), or free and in BAND (`beta`), or free and outside BAND (`LANE_out`).

ONE NEW PRIMITIVE, and it matters.  A141's `box_misses_cell` separates only along the CELL's own
two normals with the box's bounding half-width `hmax`; for a conditioned box at 50-65 deg whose
square clears the cell along one of its OWN edge normals that test can never fire, at any depth
(`k5_16_interior_Y0842`'s `H` is exactly this: `M = 1` there is a budget failure, not geometry).
`box_misses_cell_exact` below runs the FULL separating-axis test over the parameter box -- the
cell's two normals AND the square's two, each with both signs -- every bound an exact Fraction
evaluated by the two-endpoint rule of `_proj_min_exact`.  It is a sound sufficient condition for
"no pose of the box meets int C" and it subsumes A141's test.

FRAME AND SIDE.  Boxes come from A118's `lane.cframe_boxes` (imported READ-ONLY): the ORIGINAL
packing at side `m`, pulled into the cell's corner frame and hulled over `m in [m_lo, s0]`.  The
chord row is applied at `s = s0 >= m`, which only ENLARGES `rhs`, hence only enlarges `beta`:
conservative.  Outward-rounded tilt bounds `t_lo/t_hi` (A57's `caselp`) are used everywhere, so
every box statement is about a SUPERSET of the true box.

    import chordlane as CL;  CL.run_slot(rec, "BL(1,0)")
"""
import math
import os
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
A118 = os.path.join(ROOT, "attempts", "A118-lane-count", "code")
A132 = os.path.join(ROOT, "attempts", "A132-polygon-core", "code")
A141 = os.path.join(ROOT, "attempts", "A141-polycore-lane", "code")
A144 = os.path.join(ROOT, "attempts", "A144-guard-lines", "code")
A57C = os.path.join(ROOT, "attempts", "A57-shadow-trees", "code")
for _p in (A141, A118, A132, A144, A57C, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import blas1  # noqa: F401,E402  (must precede numpy; A141's single-thread guard)
import numpy as np  # noqa: E402

import polylane as P                      # noqa: E402  READ-ONLY  (A141)
import polycore as PC                     # noqa: E402  READ-ONLY  (A132)
import guardline as GL                    # noqa: E402  READ-ONLY  (A144)
import lane as LANE                       # noqa: E402  READ-ONLY  (A118)
import corpus as CP                       # noqa: E402  READ-ONLY  (A118)
from caselp import Box, t_lo, t_hi        # noqa: E402  READ-ONLY  (A57)

S_RAT = Fr(969271, 250000)
S0 = float(S_RAT)
HALF = Fr(1, 2)
SQRT2_LO = GL.SQRT2_LO
SQRT2_HI = SQRT2_LO + Fr(1, 10 ** 24)
LDEN = 10 ** 6                            # the rational grid the swept line offsets live on
PAIR_CAP = 4000                           # max open boxes the O(n^2) pair test will accept

# wall-adjacent slot cells and the orientation of their wall guard line
WALL_ORIENT = {}
for _i in range(0, 3):
    WALL_ORIENT[(_i, 0)] = ("h",) if _i > 0 else ("h", "v")
    WALL_ORIENT[(0, _i)] = ("v",) if _i > 0 else ("h", "v")


# ===================================================================== exact projections
def _u_of_t(t):
    """cos th + sin th at t = tan(th/2), exact."""
    return (1 - t * t + 2 * t) / (1 + t * t)


def cs_max_exact(t0, t1):
    """exact rational UPPER bound of max(|cos th| + |sin th|) over t in [t0, t1] c [0, 1]."""
    tlo, thi = SQRT2_LO - 1, SQRT2_HI - 1              # brackets tan(22.5 deg)
    if t0 <= thi and t1 >= tlo:
        return SQRT2_HI
    return max(_u_of_t(t0), _u_of_t(t1))


def cs_min_exact(t0, t1):
    """exact rational LOWER bound of min(|cos th| + |sin th|) over t in [t0, t1] c [0, 1]."""
    return min(_u_of_t(t0), _u_of_t(t1))               # u is unimodal with max inside: min at ends


def _proj_min_exact(dx, dy, t0, t1):
    """min over th with tan(th/2) in [t0, t1] c [0, 1] of  dx cos th + dy sin th , exactly.

    g(th) = R cos(th - phi) is unimodal with its MAXIMUM at phi, so its minimum over an interval
    is at an endpoint unless the interval contains phi + 180 deg.  With th in [0, 90] that needs
    phi in [-180, -90], i.e. dx <= 0 AND dy <= 0; in that one case a conservative rational lower
    bound -(|dx| + |dy|) <= -R is returned (it can never certify a separation, which is correct --
    a third-quadrant offset never separates)."""
    dx, dy = Fr(dx), Fr(dy)
    if dx <= 0 and dy <= 0:
        return -(abs(dx) + abs(dy))
    out = None
    for t in (Fr(t0), Fr(t1)):
        D = 1 + t * t
        g = (dx * (1 - t * t) + 2 * dy * t) / D
        out = g if out is None else min(out, g)
    return out


def _tbin(b):
    t0, t1 = t_lo(b.th0), t_hi(b.th1)
    return (t1, t0) if t0 > t1 else (t0, t1)


def box_misses_cell_exact(b, cell):
    """SOUND, exact: True if EVERY pose in `b` gives a square with int Q disjoint from int(cell).

    Full separating-axis test over the box.  For an axis `w` the square's support radius is exactly
    1/2 (w is one of its own edge normals) or `h(th) = (|cos|+|sin|)/2` (w is a cell normal).  A
    separation holds for every pose iff, for the Minkowski difference rectangle
    `D = box_centres (-) cell`, `min over d in D, th in bin of <d, w(th)>  >=  radius`; the minimum
    over `D` is at one of its four corners.  Returns (ok, detail)."""
    X0, X1, Y0, Y1 = (Fr(v) for v in cell)
    x0, x1 = Fr(b.x0), Fr(b.x1)
    y0, y1 = Fr(b.y0), Fr(b.y1)
    t0, t1 = _tbin(b)
    # --- family A: the CELL's normals; support radius of the square is h(th) <= cs_max/2
    hmax = cs_max_exact(t0, t1) / 2
    for nm, m in (("ex+", x0 - X1), ("ex-", X0 - x1), ("ey+", y0 - Y1), ("ey-", Y0 - y1)):
        if m >= hmax:
            return True, dict(axis=nm, margin=str(m - hmax), radius=str(hmax))
    # --- family B: the SQUARE's own normals w_0 = (cos, sin), w_1 = (-sin, cos); radius 1/2
    DX = (x0 - X1, x1 - X0)
    DY = (y0 - Y1, y1 - Y0)
    for k in (0, 1):
        for sg in (1, -1):
            worst = None
            for dx in DX:
                for dy in DY:
                    ex, ey = (sg * dx, sg * dy)
                    if k == 1:                       # <d, w_1(th)> = <R(-90) d, w_0(th)>
                        ex, ey = ey, -ex
                    g = _proj_min_exact(ex, ey, t0, t1)
                    worst = g if worst is None else min(worst, g)
            if worst >= HALF:
                return True, dict(axis="w%d%s" % (k, "+" if sg > 0 else "-"),
                                  margin=str(worst - HALF), radius="1/2")
    return False, None


# ===================================================================== the band
def band_ok(b, line):
    """SOUND, exact: True if EVERY pose in `b` has chord `>= 1` on `line`.

    chord = min(A, B) with A = 1/max(|cos|,|sin|) >= 1 always, so chord >= 1 iff B >= 1 iff
    |v| <= (C+S)/2 - CS = f(y), y = C + S.  `f(y) = (y + 1 - y^2)/2` is DECREASING on [1, sqrt2],
    so `f(cs_max)` is the minimum over the tilt bin and an UPPER bound of `cs_max` gives a lower
    bound of it: conservative.  `|v|` is maximised at a corner of the centre rectangle."""
    V = line.offset_range_frac(b.x0, b.x1, b.y0, b.y1)          # max |v| over the centre range
    Y = cs_max_exact(*_tbin(b))
    thr = (Y + 1 - Y * Y) / 2
    return (V <= thr), dict(V=str(V), thr=str(thr), cs_max=str(Y))


def not_band_ok(b, line):
    """SOUND, exact: True if EVERY pose in `b` has chord `< 1` on `line` (the mirror of `band_ok`).

    `chord >= 1 <=> |v| <= f(y) = (y + 1 - y^2)/2`, and `f` is DECREASING on [1, sqrt2], so the
    largest threshold over the tilt bin is `f(cs_min)`.  Hence every pose has chord < 1 as soon as
    `min |v| > f(cs_min)`; a LOWER bound of `cs_min` gives a LARGER `f`, so the test is strict in
    the safe direction.  `min |v|` is 0 whenever the line crosses the centre range."""
    lo, hi = ((b.y0, b.y1) if line.orient == "h" else (b.x0, b.x1))
    lo, hi = Fr(lo), Fr(hi)
    a_, b_ = line.off - hi, line.off - lo
    V = Fr(0) if (a_ <= 0 <= b_) else min(abs(a_), abs(b_))
    Y = cs_min_exact(*_tbin(b))
    thr = (Y + 1 - Y * Y) / 2
    return (V > thr), dict(V_min=str(V), thr=str(thr), cs_min=str(Y))


def chord_band_lo(TH, V):
    """vectorised chord (A144 (CH)) at half-side 1/2 -- for the sample line only."""
    return GL.chord_many(0.5, TH, V)


# ===================================================================== the chord budget
def guard_rhs(boxes, line, s=S_RAT):
    """(rhs, beta, per-box minchords).  `beta = floor(rhs)` caps the number of FREE band squares."""
    terms = []
    tot = Fr(0)
    for k, b in enumerate(boxes):
        mc = GL.minchord_box(b, line, a=HALF)
        terms.append(dict(j=k, minchord=str(mc["lo"]), minchord_float=mc["lo_float"],
                          V=mc["V"], method=mc["method"]))
        tot += mc["lo"]
    rhs = Fr(s) - tot
    beta = None if rhs < 0 else int(math.floor(rhs))
    return rhs, beta, terms


# ===================================================================== the covers
def _discharge_out(b, cell, conds, line, s, skip, exact=True, band_mode="out"):
    """(why, detail) for one box of the OUTSIDE lane cover, or None if it survives.

    Order: container, misses_cell (exact SAT), band, witness -- cheapest sound test first."""
    if P.box_outside_container(b, s):
        return ("container", {})
    if line is not None:                       # cheapest exact test: ~10 Fraction ops
        if band_mode == "out":                 # LANE_out: BAND poses are charged to beta
            ok, det = band_ok(b, line)
            if ok:
                return ("band", det)
        elif band_mode == "band":              # LANE_band: OUTSIDE poses are charged to LANE_out
            ok, det = not_band_ok(b, line)
            if ok:
                return ("not_band", det)
    ok, det = box_misses_cell_exact(b, cell)
    if ok:
        return ("misses_cell", det)
    w = P.find_witness(b, conds, skip=skip, exact=exact)
    if w is not None:
        j, pt, mb, mj = w
        return ("witness", dict(j=j, w=pt, margin_box=mb, margin_cond=mj))
    return None


def cover(root, cell, conds, line, s=S0, skip=None, depth0=0, max_depth=40, max_open=2500,
          exact=True, deadline=None, band_mode="out"):
    """A complete cover of `root` by boxes each DISCHARGED by one of the four prunes, or the set of
    open boxes if some survive.  `line = None` drops the band prune (then this is exactly A141's
    `cover_empty` with the stronger `misses_cell`)."""
    leaves, open_ = [], []
    stack = [("", root)]
    depth = 0
    nseen = 0
    why_stop = None
    while stack:
        p, b = stack.pop()
        depth = max(depth, len(p))
        nseen += 1
        if deadline is not None and (nseen & 511) == 0 and time.time() > deadline:
            # SOUND fallback: `leaves + open_ + the rest of the stack` still TILES the root, so the
            # pairwise-always-overlap test below can still certify LANE <= 1 even though no
            # complete DISCHARGE was found.  (LANE = 0 needs an empty open set, so it is lost.)
            open_.extend([(p, b)] + stack)
            stack = []
            why_stop = "time budget exhausted"
            break
        d = _discharge_out(b, cell, conds, line, s, skip, exact, band_mode)
        if d is not None:
            why, det = d
            leaves.append(dict(path=p, box=P.box_json(b), why=why, **det))
            continue
        if len(p) >= max_depth:
            open_.append((p, b))
            if len(open_) > max_open:
                open_.extend(stack)
                stack = []
                why_stop = "open budget exhausted"
                break
            continue
        b0, b1 = P.split_box(b)
        stack.append((p + "0", b0))
        stack.append((p + "1", b1))
        if len(stack) + len(open_) > 8 * max_open:
            open_.extend(stack)
            stack = []
            why_stop = "stack budget exhausted"
            break
    if not open_:
        return dict(ok=True, lane=0, leaves=leaves, open=[], depth=depth)
    if len(open_) > PAIR_CAP:
        return dict(ok=False, lane=None, leaves=leaves, open=[], depth=depth,
                    reason=(why_stop or "open set too large for the pair test"))
    bxs = [b for (_, b) in open_]
    BAD = ~LANE.L.pairs_always_overlap_matrix(bxs)
    if BAD.any():
        ii, jj = np.nonzero(np.triu(BAD))
        if len(ii) <= 60000:
            for (u, v) in zip(ii.tolist(), jj.tolist()):
                if LANE.L.pair_always_overlap(bxs[u], bxs[v]):
                    BAD[u, v] = BAD[v, u] = False
    lane = 1 if not BAD.any() else None
    return dict(ok=False, lane=lane, leaves=leaves,
                open=[dict(path=p, box=P.box_json(b)) for (p, b) in open_], depth=depth,
                reason=("LANE<=1 (pair test on the open set; cover stopped: %s)" % (why_stop or "budget")
                        if lane == 1 else (why_stop or "undischarged leaves")))


def lane_out(cell, conds, line, s=S0, max_depth=34, max_open=2500, deadline=None,
             band_mode="out"):
    """LANE_out for the cell: the cover of the whole meeting window with the band prune."""
    x0, x1, y0, y1 = P.centre_window(cell, s)
    if x1 <= x0 or y1 <= y0:
        return dict(ok=True, lane=0, leaves=[], open=[], depth=0,
                    root=[x0, x1, y0, y1, 0.0, 90.0], reason="empty centre window")
    root = Box(x0, x1, y0, y1, 0.0, 90.0)
    out = cover(root, cell, conds, line, s=s, max_depth=max_depth, max_open=max_open,
                deadline=deadline, band_mode=band_mode)
    out["root"] = [x0, x1, y0, y1, 0.0, 90.0]
    return out


def cond_excluded(cs, cell, conds, s=S0, max_depth=40, max_open=800, deadline=None):
    """Can the conditioned square `cs` meet int(cell)?  `ok=True` means EXCLUDED (it cannot).
    A141's `cond_can_meet`, with the exact SAT `misses_cell` and NO band prune (a band pose of a
    conditioned square still meets the cell)."""
    return cover(cs.box, cell, conds, None, s=s, skip=cs.idx, max_depth=max_depth,
                 max_open=max_open, deadline=deadline)


# ===================================================================== screens and sampling
def sample_pool(cell, conds, s, n, rng):
    """Draw the pose pool ONCE (it does not depend on the guard line) and mark the FREE poses."""
    Cs, Ts = P.sample_meeting(cell, s, n, rng)
    hit = np.zeros(len(Cs), bool)
    per = {}
    for cs in conds:
        if len(Cs):
            h = PC.poly_square_depth(cs.pc.P, Cs, Ts) > 0.0
            per[str(cs.idx)] = int(h.sum())
            hit |= h
    return dict(drawn=n, C=Cs, T=Ts, hit=hit, per_core=per)


def sample_split(pool, line):
    """Split the pool by the chord on `line`; report the FREE ones on each side.

    A free OUTSIDE pose is an exact realisation of `LANE_out >= 1` (the lane quantity is defined
    over poses avoiding the cores), so it RETIRES the cell for this line; two interior-disjoint
    free outside poses are A159's two-crowd witness and retire it outright."""
    Cs, Ts, hit = pool["C"], pool["T"], pool["hit"]
    out = dict(drawn=pool["drawn"], meeting=int(len(Cs)), per_core=pool["per_core"])
    if not len(Cs):
        return out
    per = pool["per_core"]
    V = line.foff - (Cs[:, 1] if line.orient == "h" else Cs[:, 0])
    ch = chord_band_lo(Ts, V)
    band = ch >= 1.0
    free = ~hit
    out.update(overlapping_some_core=int(hit.sum()), free=int(free.sum()),
               band=int(band.sum()), band_free=int((band & free).sum()),
               outside=int((~band).sum()), outside_free=int((~band & free).sum()),
               min_chord_band=float(ch[band].min()) if band.any() else None,
               max_chord_outside=float(ch[~band].max()) if (~band).any() else None)
    if (band & free).any():
        cs_ = np.abs(np.cos(Ts)) + np.abs(np.sin(Ts))
        thr = (cs_ + 1.0 - cs_ * cs_) / 2.0
        out["band_margin_min_free"] = float((thr - np.abs(V))[band & free].min())
    ix = np.nonzero(~band & free)[0]
    if len(ix):
        k = int(ix[0])
        out["outside_free_pose"] = [float(Cs[k, 0]), float(Cs[k, 1]), float(Ts[k]),
                                    float(ch[k])]
        if len(ix) >= 2:
            FC, FT = Cs[ix[:600]], Ts[ix[:600]]
            G = LANE.L.pair_gaps(FC, FT)
            np.fill_diagonal(G, -1e9)
            kk = int(np.argmax(G))
            a, b_ = divmod(kk, len(FC))
            out["max_pair_gap_outside_free"] = float(G[a, b_])
            if G[a, b_] > 0.0:
                out["two_crowd_outside"] = [float(FC[a, 0]), float(FC[a, 1]), float(FT[a]),
                                            float(FC[b_, 0]), float(FC[b_, 1]), float(FT[b_])]
    return out


def cond_meets_sample(cs, cell, conds, s, n, rng):
    """Sampled lower bound: does some pose of `cs` meet int(cell) while avoiding every OTHER core?"""
    b = cs.box
    C = np.column_stack([rng.uniform(b.x0, b.x1, n), rng.uniform(b.y0, b.y1, n)])
    T = np.radians(rng.uniform(b.th0, b.th1, n))
    h = 0.5 * (np.abs(np.cos(T)) + np.abs(np.sin(T)))
    ok = ((C[:, 0] >= h) & (C[:, 0] <= s - h) & (C[:, 1] >= h) & (C[:, 1] <= s - h))
    ok &= P.rect_square_meets(cell, C, T)
    for o in conds:
        if o.idx == cs.idx or not ok.any():
            continue
        ok &= (PC.poly_square_depth(o.pc.P, C, T) <= 0.0)
    return bool(ok.any()), int(ok.sum())


# ===================================================================== the node/slot driver
def frame_boxes(rec, slot):
    """(conds, meeter indices, cell, corner, i, j) in the cell's corner frame -- A141's `build`."""
    c, i, j = LANE.L.parse_cell(slot)
    pin_b, cond_b = LANE.cframe_boxes(rec, c, i, j)
    pins = P.build_cond([Box(b.x0, b.x1, b.y0, b.y1, b.th0, b.th1) for b in pin_b],
                        tighten=False)
    cond = P.build_cond([Box(b.x0, b.x1, b.y0, b.y1, b.th0, b.th1) for b in cond_b],
                        tighten=False)
    for k, cs in enumerate(cond):
        cs.idx = len(pins) + k
    cell = (float(i), float(i) + 1.0, float(j), float(j) + 1.0)
    return pins + cond, [cs.idx for cs in cond], cell, c, i, j


def line_candidates(orient, n=48, den=LDEN):
    """The swept offsets: an interior grid of (0, 1) on a rational grid, densest near 1 (where the
    band swallows the second row) and near 1/2 (where the wall-row pins are centred)."""
    out = []
    for k in range(1, n):
        out.append(Fr(round(k * den // n), den))
    for v in (Fr(985, 1000), Fr(990, 1000), Fr(992, 1000), Fr(9925, 10000),
              Fr(995, 1000), Fr(998, 1000), Fr(1, 2)):
        out.append(v)
    seen, uniq = set(), []
    for v in sorted(out):
        if 0 < v < 1 and v not in seen:
            seen.add(v)
            uniq.append(GL.Line(orient, v, tag="wall-band"))
    return uniq


def run_slot(rec, slot, rng=None, sample=20000, max_open=2500, max_depth=34, n_lines=48,
             cover_budget=2, keep_cert=True, s=S0, force_off=None, budget_s=None):
    """The chord-limited lane leaf at one (node, slot).  Returns the row + the certificate parts."""
    rng = rng if rng is not None else np.random.default_rng(1610)
    dl = None if budget_s is None else (time.time() + budget_s)
    conds, meet, cell, corner, i, j = frame_boxes(rec, slot)
    n_pins = len(conds) - len(meet)
    row = dict(slot=slot, cell=list(cell), corner=corner, ij=[i, j], n_pins=n_pins,
               cond_index=list(meet), verdict="UNDECIDED")
    orients = WALL_ORIENT.get((i, j))
    if not orients:
        row["verdict"] = "NOT-WALL-ADJACENT"
        return row, None

    # ---- M first: it is line-independent, cheap, and gates everything
    Mdet = []
    for cs in conds:
        if cs.idx not in meet:
            continue
        hit, nhit = cond_meets_sample(cs, cell, conds, s, 4000, rng)
        if hit:
            Mdet.append(dict(j=cs.idx, excluded=False, by="sample", n=nhit))
            continue
        r = cond_excluded(cs, cell, conds, s=s, max_depth=max_depth, deadline=dl)
        Mdet.append(dict(j=cs.idx, excluded=bool(r["ok"]), by="cover",
                         leaves=len(r["leaves"]), reason=r.get("reason"),
                         cert=(r["leaves"] if (keep_cert and r["ok"]) else None)))
    M = sum(0 if e["excluded"] else 1 for e in Mdet)
    row["M"] = M
    row["M_detail"] = [{k: v for k, v in e.items() if k != "cert"} for e in Mdet]
    if M >= 2:
        row["verdict"] = "M>=2"
        return row, None

    # ---- sweep the wall lines: exact beta, then the sampled outside screen (one pose pool)
    best = None
    ranked = []
    scan = []
    boxes = [c.box for c in conds]
    for orient in orients:
        pool = sample_pool(cell, conds, s, sample, rng)
        cand = ([GL.Line(orient, Fr(force_off), tag="forced")] if force_off is not None
                else line_candidates(orient, n=n_lines))
        for ln in cand:
            rhs, beta, terms = guard_rhs(boxes, ln, s=S_RAT)
            if beta is None:
                row["verdict"] = "CHORD-CONTRADICTION"
                row["line"] = ln.to_json()
                row["rhs"] = str(rhs)
                row["minchords"] = terms
                return row, None
            if beta + M >= 2:
                scan.append(dict(orient=orient, off=str(ln.off), rhs=str(rhs), beta=beta,
                                 skipped="beta+M>=2"))
                continue
            sm = sample_split(pool, ln)
            scan.append(dict(orient=orient, off=str(ln.off), rhs=str(rhs), beta=beta,
                             outside_free=sm.get("outside_free"), band=sm.get("band"),
                             free=sm.get("free"),
                             band_margin_min_free=sm.get("band_margin_min_free")))
            # prefer: no free outside pose, then the deepest band margin on the free poses
            # (that is what makes the cover's `band` prune close), then the smallest beta
            key = (sm.get("outside_free", 10 ** 9), -(sm.get("band_margin_min_free") or -9.0),
                   beta)
            ranked.append((key, orient, ln, rhs, beta, terms, sm))
            if best is None or key < best[0]:
                best = (key, orient, ln, rhs, beta, terms, sm)
    row["scan"] = scan
    if best is None:
        row["verdict"] = "NO-LINE (beta + M >= 2 on every swept offset)"
        return row, None

    key, orient, ln, rhs, beta, terms, sm = best
    sm = {k: v for k, v in sm.items() if k != "per_core"}
    row.update(line=ln.to_json(), rhs=str(rhs), rhs_float=float(rhs), beta=beta,
               minchords=terms, sample=sm)
    if sm.get("outside_free", 0) and beta + M + 1 >= 2:
        row["verdict"] = ("RETIRED-two-crowd-outside" if sm.get("two_crowd_outside")
                          else "RETIRED-outside-witness")
        row["retire_witness"] = sm.get("two_crowd_outside") or sm.get("outside_free_pose")
        return row, None

    # ---- the outside lane cover.  WHICH line is tried matters far more than how long: on
    # Y0842 the cover blows a 40,000-box budget at y_L = 0.9167 and closes in 163 leaves at
    # y_L = 0.7917.  So try the top `cover_budget` ranked offsets, each with its own slice of
    # the pair budget, and keep the first that closes.
    ranked.sort(key=lambda z: z[0])
    tries, cov, chosen = [], None, None
    kmax = max(1, cover_budget)
    per = None if budget_s is None else max(3.0, budget_s / float(kmax))
    seen_off = set()
    for cand in ranked:
        if len(tries) >= kmax:
            break
        if str(cand[2].off) in seen_off:
            continue
        seen_off.add(str(cand[2].off))
        if cand[4] + M >= 2 or (cand[6].get("outside_free") or 0) > 0:
            continue
        c = lane_out(cell, conds, cand[2], s=s, max_depth=max_depth, max_open=max_open,
                     deadline=(None if per is None else time.time() + per))
        tries.append(dict(off=str(cand[2].off), lane=c["lane"], leaves=len(c["leaves"]),
                          open=len(c["open"]), reason=c.get("reason")))
        if c["lane"] is not None and (cov is None or c["lane"] < cov["lane"]):
            cov, chosen = c, cand
            if c["lane"] == 0:
                break
    row["line_tries"] = tries
    if cov is None:
        row.update(lane_out=None, cover_reason=(tries[-1]["reason"] if tries else "no candidate"))
        row["verdict"] = "UNDECIDED"
        return row, None
    key, orient, ln, rhs, beta, terms, sm = chosen
    sm = {k: v for k, v in sm.items() if k != "per_core"}
    row.update(line=ln.to_json(), rhs=str(rhs), rhs_float=float(rhs), beta=beta,
               minchords=terms, sample=sm)
    row.update(lane_out=cov["lane"], cover_leaves=len(cov["leaves"]),
               cover_open=len(cov["open"]), cover_depth=cov["depth"],
               cover_reason=cov.get("reason"))
    total = beta + cov["lane"] + M
    row["total"] = total
    row["verdict"] = "KILL" if total <= 1 else ("NEAR-MISS" if total == 2 else "UNDECIDED")
    cert = None
    if row["verdict"] == "KILL" and keep_cert:
        cert = dict(
            leaf="chord_limited_lane_v1",
            claim="beta + LANE_out + M <= 1 contradicts SLOT-CROWD (>= 2 non-pin squares meet "
                  "int C at a usable slot); the node is DEAD",
            s=str(S_RAT), s_float=S0,
            nid=rec["nid"], src=rec["src"], cls=rec["cls"], level=rec["level"],
            slot=slot, corner=corner, ij=[i, j], cell=list(cell),
            cell_kind="usable_slot",
            extension=CP.CLASSES[rec["cls"]]["usable"][slot],
            extension_window="[191/50, 969271/250000] FULL (A56/A61/A114 scoreboard)",
            frame="A118 lane.cframe_boxes: original packing at side m, cell's corner frame, "
                  "every box hulled over m in [m_lo, s0]",
            m_lo=LANE.M_LO.get(rec["src"], 3.82),
            n_pins=n_pins, cond_index=list(meet),
            hyp_boxes=[P.box_json(c.box) for c in conds],
            guardline=dict(orient=ln.orient, off=str(ln.off), off_float=ln.foff,
                           tag=ln.tag, rhs=str(rhs), rhs_float=float(rhs), beta=beta,
                           minchords=terms,
                           band_rule="chord >= 1  <=>  |v| <= (y + 1 - y^2)/2 at y = cs_max"),
            lane_out=dict(value=cov["lane"], root=cov["root"], leaves=cov["leaves"],
                          open=cov["open"]),
            M=dict(value=M, detail=[dict(j=e["j"], excluded=e["excluded"], by=e["by"],
                                         cert=e.get("cert")) for e in Mdet]),
            total=total, sample_line=sm,
            split_rule="widest of (x, y, theta/60), deterministic (A141 polylane.split_box)",
        )
    return row, cert
