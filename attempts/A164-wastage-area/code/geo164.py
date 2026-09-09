"""A164 -- the UNCOVERABLE SET U(node) and its area, as a certified LOWER bound.

    U(node) = { p in [0,s]^2 : NO admissible square contains p }

with, for a node carrying pins (A135 exact cores), conditioned squares H (A132 polycore K'(H))
and `budget` free squares,

  * a FREE square is ADMISSIBLE iff it is inside the container and interior-disjoint from every
    pin's exact core and from K'(H) of every conditioned square;
  * a CONDITIONED square's possible cover is the union of its poses over its centre/tilt box;
  * a PIN's likewise over its box.

**Why the area is a leaf.**  In any 11-packing consistent with the node the eleven square
interiors are disjoint and inside [0, m]^2, so they cover exactly 11; every square's point set
lies inside its own coverable set, so U is covered by nothing and

    |U|  <=  m^2 - 11  =  E(m)        (A89 Lemma ID's budget, `docs/proofs/tilt_floor_k0.md` §7)

Hence  |U| > m^2 - 11  KILLS the node, with no LP.  We charge against
B0 = s0^2 - 11 = 4.031780343056, the LARGEST budget on the window slab [3.81794, s0].

**Soundness of the raster.**  A cell C of the output raster is certified C subset U only when NO
admissible pose MEETS the closed cell -- never merely "the centre is not covered".  Everything
below is therefore an OUTER approximation of the cover and so an INNER approximation of U; the
reported area is a LOWER bound.  Two Lipschitz facts do the work (A148 geo148.py):

    clearance(c, th) = min( container clearance of the centre , min_j -depth(K_j, Q(c, th)) )

is 1-Lipschitz in the centre and (sqrt2/2)-Lipschitz in the tilt.

Free-square cover, per tilt bin k of width dth about th_k, cover square of side lam >= 1:

    m1 = q*sqrt2/2 + (sqrt2/2)*(dth/2)                      admissible-centre slack
    A_k = { rotated-grid nodes n : clearance(n, th_k) >= -m1 }        (OUTER: every admissible
           centre whose tilt lies in bin k has a grid node of A_k within q*sqrt2/2)
    H  = lam/2 + lam*(sqrt2/2)*(dth/2) + q/2 + p_out*sqrt2/2         half-width, th_k frame
    cover_k = { p : some n in A_k has |u_p - u_n| <= H and |v_p - v_n| <= H }

evaluated by a separable binary dilation of A_k by a box of radius R = ceil(H/q + 1/2) nodes in
the th_k-ROTATED frame (where Q(., th_k) is axis-aligned), read off at the node nearest p.  The
p_out*sqrt2/2 term inflates the test from the cell CENTRE to the whole closed cell.

Box cover (conditioned squares and pins), box = rect x [t0, t1] sampled at th_j, step dt:

    p in Q_lam(c, th)  <=>  c in Q_lam(p, th)  (the square is centrally symmetric)
    so p is covered only if  gap( rect , Q_lam(p, th_j) )  <=  lam*(sqrt2/2)*(dt/2) + p_out*sqrt2/2

for some j -- an exact rect-vs-rotated-square SAT gap, vectorised over p.

**Window variant.**  Admissibility stays at side 1 while the COVER square grows to
lam_max = s0/3.81794: a side-lam square (lam in [1, lam_max]) that is admissible contains the
concentric admissible UNIT square, and its cover is inside the concentric lam_max square.  So the
lam_max raster is sound for every m in the slab, against the same budget B0.

Read-only on every campaign: A132/A135/A140/A148 are imported, never written.
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, ".."))
for _p in (os.path.join(ATT, "A148-gallery-v4", "code"),
           os.path.join(ATT, "A132-polygon-core", "code"),
           os.path.join(ATT, "A135-polycore-verifier", "code"),
           os.path.join(ATT, "A57-shadow-trees", "code"),
           HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import polycore                                                       # noqa: E402
import geo148 as G148                                                 # noqa: E402

S0 = 969271.0 / 250000.0
M_WINDOW_LO = 3.81794                       # the low side of the A57 window slab
LAM_MAX = S0 / M_WINDOW_LO
B0 = S0 * S0 - 11.0                         # = 4.031780343056, the largest wastage budget
ROOT2H = math.sqrt(2.0) / 2.0

PITCH = 0.01
NTILT = 36


# ===================================================================== rect vs rotated square
def rect_square_gap(rect, PX, PY, th, half):
    """SAT gap between the axis-aligned rect (x0,x1,y0,y1) and the square of half-side `half`
    centred at (PX, PY) with tilt `th` (radians).  > 0 disjoint, <= 0 they meet.  Vectorised."""
    x0, x1, y0, y1 = rect
    c, s = math.cos(th), math.sin(th)
    best = -9e9
    # rect's own two axes
    for (ax, ay, lo, hi) in ((1.0, 0.0, x0, x1), (0.0, 1.0, y0, y1)):
        hw = half * (abs(ax * c + ay * s) + abs(-ax * s + ay * c))
        qc = PX * ax + PY * ay
        best = np.maximum(best, np.maximum(lo - (qc + hw), (qc - hw) - hi))
    # the square's two axes
    for (ax, ay) in ((c, s), (-s, c)):
        pp = np.array([x0 * ax + y0 * ay, x1 * ax + y0 * ay,
                       x1 * ax + y1 * ay, x0 * ax + y1 * ay])
        lo, hi = pp.min(), pp.max()
        qc = PX * ax + PY * ay
        best = np.maximum(best, np.maximum(lo - (qc + half), (qc - half) - hi))
    return best


# ===================================================================== the free-square cover
def _dilate_box(A, R):
    """binary dilation of a 2-D bool array by the (2R+1)^2 box, separable, no scipy needed."""
    if R <= 0:
        return A
    B = A
    for axis in (0, 1):
        n = B.shape[axis]
        cs = np.cumsum(np.concatenate(
            [np.zeros((1,) + B.shape[1:], np.int32) if axis == 0 else
             np.zeros(B.shape[:1] + (1,), np.int32), B.astype(np.int32)], axis=axis), axis=axis)
        lo = np.clip(np.arange(n) - R, 0, n)
        hi = np.clip(np.arange(n) + R + 1, 0, n)
        if axis == 0:
            B = (cs[hi] - cs[lo]) > 0
        else:
            B = (cs[:, hi] - cs[:, lo]) > 0
    return B


def free_cover(s, obstacles, xs, ys, p_out, lam=1.0, q=PITCH, ntilt=NTILT, want_admis=False):
    """OUTER approximation, on the output raster (xs, ys), of the set of points that some
    ADMISSIBLE free square can contain -- inflated from the cell centre to the whole closed cell.

    Returns (cover_mask, meta) and, with want_admis, also the container-frame OUTER mask of
    admissible centres (max over the sampled tilts), which the one-meeter bound needs."""
    ny, nx = len(ys), len(xs)
    PXo, PYo = np.meshgrid(xs, ys)
    cover = np.zeros((ny, nx), bool)
    admis = np.zeros((ny, nx), bool) if want_admis else None

    dth = (math.pi / 2.0) / ntilt
    m1 = q * ROOT2H + ROOT2H * (dth / 2.0)
    Hw = 0.5 * lam + lam * ROOT2H * (dth / 2.0) + 0.5 * q + p_out * ROOT2H
    R = int(math.ceil(Hw / q + 0.5))

    # the centre bbox: an admissible centre is >= 1/2 from every wall; keep m1 + a hair of slack
    pad = m1 + 0.02
    lo, hi = 0.5 - pad, s - 0.5 + pad
    corners = np.array([[lo, lo], [hi, lo], [hi, hi], [lo, hi]])

    ths = (np.arange(ntilt) + 0.5) * (math.pi / 2.0) / ntilt
    n_nodes = 0
    for th in ths:
        c, sn = math.cos(th), math.sin(th)
        U = corners[:, 0] * c + corners[:, 1] * sn
        V = -corners[:, 0] * sn + corners[:, 1] * c
        u0, v0 = U.min(), V.min()
        nu = int(math.ceil((U.max() - u0) / q)) + 1
        nv = int(math.ceil((V.max() - v0) / q)) + 1
        uu = u0 + np.arange(nu) * q
        vv = v0 + np.arange(nv) * q
        UU, VV = np.meshgrid(uu, vv)                       # (nv, nu)
        CX = UU * c - VV * sn
        CY = UU * sn + VV * c
        w = 0.5 * (abs(c) + abs(sn))
        cl = np.minimum.reduce([CX - w, s - w - CX, CY - w, s - w - CY])
        live = cl >= -m1
        n_nodes += int(live.sum())
        if live.any() and obstacles:
            Cl = np.stack([CX[live], CY[live]], 1)
            TH = np.full(len(Cl), th)
            cs = cl[live]
            for P in obstacles:
                cs = np.minimum(cs, -polycore.poly_square_depth(P, Cl, TH))
            tmp = np.full(cl.shape, -9e9)
            tmp[live] = cs
            cl = tmp
        elif not live.any():
            cl = np.full(cl.shape, -9e9)
        A = cl >= -m1
        if not A.any():
            continue
        Ap = np.pad(A, R, constant_values=False)
        S = _dilate_box(Ap, R)
        # read S off at the node nearest each output cell centre
        Up = PXo * c + PYo * sn
        Vp = -PXo * sn + PYo * c
        iu = np.rint((Up - u0) / q).astype(np.int64) + R
        iv = np.rint((Vp - v0) / q).astype(np.int64) + R
        ok = (iu >= 0) & (iu < S.shape[1]) & (iv >= 0) & (iv < S.shape[0])
        hit = np.zeros((ny, nx), bool)
        hit[ok] = S[iv[ok], iu[ok]]
        cover |= hit
        if want_admis:
            # radius 2, not 1: an admissible centre c sits in an output cell whose CENTRE p can be
            # p_out*sqrt2/2 away, and p's nearest rotated node another q/2, so the nearest node to
            # p is up to (p_out*sqrt2/2 + q/2) + q/2 = 1.71 q from c's own nearest node.  (The
            # first draft used 1 and so under-reported the outer admissible-centre mask, which
            # would make the one-meeter counts and the crowd row optimistic.)
            rad = 2
            Sa = _dilate_box(np.pad(A, rad, constant_values=False), rad)
            iu2 = np.rint((Up - u0) / q).astype(np.int64) + rad
            iv2 = np.rint((Vp - v0) / q).astype(np.int64) + rad
            ok2 = (iu2 >= 0) & (iu2 < Sa.shape[1]) & (iv2 >= 0) & (iv2 < Sa.shape[0])
            h2 = np.zeros((ny, nx), bool)
            h2[ok2] = Sa[iv2[ok2], iu2[ok2]]
            admis |= h2
    meta = dict(q=q, ntilt=ntilt, lam=lam, m1=m1, half_width=Hw, R_nodes=R,
                n_centre_nodes=int(n_nodes), p_out=p_out)
    return (cover, meta, admis) if want_admis else (cover, meta)


# ===================================================================== the box covers
def box_cover(box, xs, ys, p_out, lam=1.0, dt_deg=0.5):
    """OUTER approximation of the union of the poses of one hypothesis square over its box,
    inflated from the cell centre to the whole closed cell."""
    x0, x1 = float(box.x0), float(box.x1)
    y0, y1 = float(box.y0), float(box.y1)
    t0, t1 = math.radians(float(box.th0)), math.radians(float(box.th1))
    rng = t1 - t0
    nt = max(1, int(math.ceil(rng / math.radians(dt_deg))))
    dt = rng / nt if nt else 0.0
    ths = [t0 + (j + 0.5) * dt for j in range(nt)] if rng > 0 else [t0]
    r = lam * ROOT2H * (dt / 2.0) + p_out * ROOT2H
    PX, PY = np.meshgrid(xs, ys)
    out = np.zeros(PX.shape, bool)
    for th in ths:
        out |= rect_square_gap((x0, x1, y0, y1), PX, PY, th, 0.5 * lam) <= r
    return out, dict(n_theta=len(ths), dt_deg=math.degrees(dt), margin=r, lam=lam)


# ===================================================================== regions
REGIONS = ["corner_BL", "corner_BR", "corner_TR", "corner_TL",
           "strip_S", "strip_E", "strip_N", "strip_W", "interior"]


def region_labels(s, xs, ys):
    """a disjoint partition of [0,s]^2: the four unit corner boxes, the four wall strips between
    them, and the interior (s-2)^2."""
    X, Y = np.meshgrid(xs, ys)
    lab = np.full(X.shape, 8, np.int8)                          # interior
    lo, hi = 1.0, s - 1.0
    L, R_, B, T = X < lo, X > hi, Y < lo, Y > hi
    lab[B & L] = 0
    lab[B & R_] = 1
    lab[T & R_] = 2
    lab[T & L] = 3
    lab[B & ~L & ~R_] = 4
    lab[R_ & ~B & ~T] = 5
    lab[T & ~L & ~R_] = 6
    lab[L & ~B & ~T] = 7
    return lab


def named_bands(s):
    """the extra, OVERLAPPING regions the PI's reading names, for reporting only."""
    return {"right_wall_strip(x>=s-1)": (s - 1.0, s, 0.0, s),
            "right_wall_half(x>=s-0.5)": (s - 0.5, s, 0.0, s),
            "top_wall_strip(y>=s-1)": (0.0, s, s - 1.0, s),
            "left_wall_strip(x<=1)": (0.0, 1.0, 0.0, s),
            "bottom_wall_strip(y<=1)": (0.0, s, 0.0, 1.0)}


# ===================================================================== the one-meeter refinement
def cap_area(a, b, lam):
    """an upper bound on |Q ∩ W| for one square of side lam and W an a x b rectangle: it is
    inside Q (<= lam^2), inside W (<= ab), and inside a slab of width min(a,b) (<= lam*sqrt2*t)."""
    t = min(a, b)
    return min(lam * lam, a * b, lam * math.sqrt(2.0) * t)


def _cell_cover_bound(CW, p_out, side=0.7):
    """max # of 1-SEPARATED points in CW <= # of axis-aligned squares of side `side` (diameter
    side*sqrt2 = 0.99 < 1, so each holds at most one) that meet CW.  Much tighter than the disk
    bound on thin bands."""
    k = max(1, int(math.floor(side / p_out)))
    ny, nx = CW.shape
    py = (ny + k - 1) // k
    px = (nx + k - 1) // k
    pad = np.zeros((py * k, px * k), bool)
    pad[:ny, :nx] = CW
    return int(pad.reshape(py, k, px, k).any(axis=(1, 3)).sum())


def one_meeter(s, admis, xs, ys, p_out, rects, boxes, lam=1.0):
    """The PI's wastage row, LP-free.  For each rectangle W:

      C_W  = OUTER set of admissible free centres whose square can meet W
           subset  admis  ∩  (W (+) B(lam*sqrt2/2))
      n_W  <= max number of 1-separated points in C_W, bounded by
                 1 when diam(C_W) < 1, else |C_W (+) B(1/2)| / (pi/4)
      N_W  = n_W + #(hypothesis boxes whose cover can meet W)
      waste(W)  >=  |W| - N_W * cap(W)

    Reduces to Lemma ID when n_W = 0 and W is a corner box."""
    X, Y = np.meshgrid(xs, ys)
    out = {}
    for name, (x0, x1, y0, y1) in rects.items():
        reach = lam * ROOT2H
        near = (X >= x0 - reach) & (X <= x1 + reach) & (Y >= y0 - reach) & (Y <= y1 + reach)
        CW = admis & near
        nc = int(CW.sum())
        if nc == 0:
            nW, how = 0, "no admissible centre can reach W"
        else:
            jj, ii = np.nonzero(CW)
            px, py = xs[ii], ys[jj]
            # diameter of the closed cells (add the cell diagonal)
            d = 0.0
            if nc <= 4000:
                d = float(np.sqrt(((px[:, None] - px[None, :]) ** 2
                                   + (py[:, None] - py[None, :]) ** 2).max()))
            else:
                d = float(math.hypot(px.max() - px.min(), py.max() - py.min()))
            d += p_out * math.sqrt(2.0)
            if d < 1.0:
                nW, how = 1, f"diam(C_W) = {d:.4f} < 1, so at most one 1-separated centre"
            else:
                r = int(math.ceil(0.5 / p_out)) + 1
                yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
                disk = (yy ** 2 + xx ** 2) <= (0.5 / p_out + 1.0) ** 2
                ny, nx = CW.shape
                acc = np.zeros((ny + 2 * r, nx + 2 * r), bool)
                for (dy, dx) in np.argwhere(disk):
                    acc[dy:dy + ny, dx:dx + nx] |= CW
                a = float(acc[r:r + ny, r:r + nx].sum()) * p_out ** 2
                nd = int(math.floor(a / (math.pi / 4.0)))
                nb = _cell_cover_bound(CW, p_out)
                nW = min(nd, nb)
                how = (f"disk bound {nd} (|C_W (+) B(1/2)| = {a:.4f}), 0.7-cell cover bound "
                       f"{nb}; diam {d:.4f}")
        nbox = 0
        for b in boxes:
            bx0, bx1 = float(b.x0) - reach, float(b.x1) + reach
            by0, by1 = float(b.y0) - reach, float(b.y1) + reach
            if bx1 >= x0 and bx0 <= x1 and by1 >= y0 and by0 <= y1:
                nbox += 1
        cap = cap_area(x1 - x0, y1 - y0, lam)
        area = (x1 - x0) * (y1 - y0)
        waste = area - (nW + nbox) * cap
        out[name] = dict(area=area, n_free_max=nW, n_boxes=nbox, cap=cap,
                         waste_lb=max(0.0, waste), how=how, n_cells_CW=nc)
    return out


def _disk_dilate(mask, r_units):
    r = int(math.ceil(r_units)) + 1
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    disk = (yy ** 2 + xx ** 2) <= (r_units + 1.0) ** 2
    ny, nx = mask.shape
    acc = np.zeros((ny + 2 * r, nx + 2 * r), bool)
    for (dy, dx) in np.argwhere(disk):
        acc[dy:dy + ny, dx:dx + nx] |= mask
    return acc[r:r + ny, r:r + nx]


def crowd_bound(s, admis, boxcov, xs, ys, p_out, n_boxes, lam=1.0, n_per_corner=2,
                n_pins=0):
    """CONDITIONAL wastage (the PI's counting), for a node whose class asserts that every corner
    unit box is met by at least `n_per_corner` squares (K0-FREE', A141's LANE >= 2 tags).

    The four corner boxes are pairwise s - 2 = 1.877 > sqrt2 apart, so a square meets at most one:
    4*n_per_corner DISTINCT squares are corner-committed, and each has its centre in that corner's
    OUTER reach set R_c = admis ∩ { c : dist(c, corner box) <= lam*sqrt2/2 }.  Their cover lies in
    A_c = R_c (+) B(lam*sqrt2/2).  Adding the hypothesis boxes' own covers,

        A = union_c A_c  union  boxcov,      B = container \\ A,
        n_loose = 11 - 4*n_per_corner - n_boxes,
        covered(B) <= n_loose * lam^2,   waste >= |B| - n_loose*lam^2,

    so |B| - n_loose*lam^2 > m^2 - 11 KILLS the node under that hypothesis.  Reported, never
    folded into the unconditional |U|.

    APPLICABILITY.  The hypothesis is k0_00's crowd hypothesis K0-FREE'; it is only stated for a
    node with NO pins.  On a node that already pins squares INTO its corners (every A57/A60 node
    does) the 4*n_per_corner corner-committed squares and the n_boxes hypothesis squares are not
    distinct, `n_loose` goes negative and the row is nonsense -- so it is refused there, and the
    row is reported with applicable = false.  (The first draft did not refuse it and flagged a
    spurious CROWD-KILL on k5_16_interior_Y1117 with n_loose = -3.)"""
    X, Y = np.meshgrid(xs, ys)
    n_loose = 11 - 4 * n_per_corner - n_boxes
    if n_pins > 0 or n_loose < 0:
        return dict(applicable=False, n_per_corner=n_per_corner, n_loose=int(n_loose),
                    kill=False, waste_lb=0.0, area_B=None,
                    note=f"REFUSED: the crowd hypothesis K0-FREE' is only stated for a node with "
                         f"no pins, and this node has {n_pins} pin(s) / {n_boxes} hypothesis "
                         f"box(es), leaving n_loose = {n_loose}")
    reach = lam * ROOT2H
    A = np.zeros(X.shape, bool)
    per = {}
    for nm, (x0, x1, y0, y1) in (("BL", (0.0, 1.0, 0.0, 1.0)), ("BR", (s - 1.0, s, 0.0, 1.0)),
                                 ("TR", (s - 1.0, s, s - 1.0, s)), ("TL", (0.0, 1.0, s - 1.0, s))):
        dx = np.maximum.reduce([x0 - X, X - x1, np.zeros_like(X)])
        dy = np.maximum.reduce([y0 - Y, Y - y1, np.zeros_like(Y)])
        Rc = admis & (np.hypot(dx, dy) <= reach + p_out * math.sqrt(2.0))
        Ac = _disk_dilate(Rc, (reach + p_out * math.sqrt(2.0)) / p_out)
        per[nm] = dict(area_Rc=float(Rc.sum()) * p_out ** 2, area_Ac=float(Ac.sum()) * p_out ** 2)
        A |= Ac
    A |= boxcov
    Bm = ~A
    areaB = float(Bm.sum()) * p_out ** 2
    return dict(applicable=True, n_per_corner=n_per_corner, n_loose=int(n_loose), area_B=areaB,
                waste_lb=max(0.0, areaB - n_loose * lam * lam),
                kill=bool(areaB - n_loose * lam * lam > B0), per_corner=per,
                note="conditional on >= n_per_corner meeters at every corner (K0-FREE')")


# ===================================================================== the node-level driver
def uncoverable(s, obstacles, boxes, lam=1.0, pitch=PITCH, ntilt=NTILT, want_extra=True,
                n_pins=0):
    """the certified-uncoverable mask and its area, plus the region breakdown."""
    n = int(math.ceil(s / pitch))
    p = s / n
    xs = (np.arange(n) + 0.5) * p
    ys = (np.arange(n) + 0.5) * p
    cov, meta, admis = free_cover(s, obstacles, xs, ys, p, lam=lam, q=pitch, ntilt=ntilt,
                                  want_admis=True)
    bmeta = []
    boxcov = np.zeros(cov.shape, bool)
    for b in boxes:
        bc, bm = box_cover(b, xs, ys, p, lam=lam)
        boxcov |= bc
        bmeta.append(bm)
    cov |= boxcov
    Umask = ~cov
    cell = p * p
    lab = region_labels(s, xs, ys)
    by_region = {}
    for k, nm in enumerate(REGIONS):
        sel = lab == k
        by_region[nm] = dict(area_region=float(sel.sum()) * cell,
                             area_U=float((sel & Umask).sum()) * cell)
    bands = {}
    X, Y = np.meshgrid(xs, ys)
    for nm, (x0, x1, y0, y1) in named_bands(s).items():
        sel = (X >= x0) & (X <= x1) & (Y >= y0) & (Y <= y1)
        bands[nm] = dict(area_region=float(sel.sum()) * cell,
                         area_U=float((sel & Umask).sum()) * cell)
    res = dict(s=s, pitch=p, n=n, ntilt=ntilt, lam=lam, area_U=float(Umask.sum()) * cell,
               budget_B0=B0, budget_at_s=s * s - 11.0,
               free=meta, boxes=bmeta, by_region=by_region, bands=bands)
    if want_extra:
        rects = dict(named_bands(s))
        rects.update({f"corner_{c}": r for c, r in
                      (("BL", (0.0, 1.0, 0.0, 1.0)), ("BR", (s - 1.0, s, 0.0, 1.0)),
                       ("TR", (s - 1.0, s, s - 1.0, s)), ("TL", (0.0, 1.0, s - 1.0, s)))})
        res["one_meeter"] = one_meeter(s, admis, xs, ys, p, rects, boxes, lam=lam)
        res["area_admis_centres"] = float(admis.sum()) * cell
        # Lemma ID's own row, exactly: the four corner boxes are pairwise s - 2 > sqrt2 apart, so
        # a square meets at most one and the shallow ones each strand their whole unit box.
        om = res["one_meeter"]
        res["sep_corner_waste"] = sum(max(0.0, 1.0 - om[f"corner_{c}"]["n_free_max"]
                                          - om[f"corner_{c}"]["n_boxes"])
                                      for c in ("BL", "BR", "TR", "TL"))
        res["crowd"] = crowd_bound(s, admis, boxcov, xs, ys, p, len(boxes), lam=lam,
                                   n_pins=n_pins)
    return Umask, xs, ys, res


# ===================================================================== the sampled cross-check
def sample_confirm(s, obstacles, boxes, Umask, xs, ys, lam=1.0, n=100000, seed=164,
                   n_contain=30000):
    """drawn -> tested -> hits.  n free poses drawn with the centre uniform in [w, s-w]^2 and the
    tilt uniform in [0, 90); each pose that this file's own SAT certifies ADMISSIBLE must contain
    NO certified-uncoverable cell centre.  The same for n/10 poses of each hypothesis box.  Any
    hit refutes the raster."""
    rng = np.random.default_rng(seed)
    p = float(xs[1] - xs[0])
    ny, nx = Umask.shape
    jj, ii = np.nonzero(Umask)
    UX, UY = xs[ii], ys[jj]

    def hits_of(CX, CY, TH, half):
        # the containment test is O(#poses x #U-cells); on a fine raster with a large U that is
        # billions of element ops, so it is capped at `n_contain` poses (a uniform subsample of
        # the ADMISSIBLE ones) and the count actually tested is reported.
        if len(CX) > n_contain:
            k = rng.choice(len(CX), n_contain, replace=False)
            CX, CY, TH = CX[k], CY[k], TH[k]
        h = 0
        c, sn = np.cos(TH), np.sin(TH)
        for k in range(len(CX)):
            dx, dy = UX - CX[k], UY - CY[k]
            u = dx * c[k] + dy * sn[k]
            v = -dx * sn[k] + dy * c[k]
            if np.any((np.abs(u) <= half) & (np.abs(v) <= half)):
                h += 1
        return h, len(CX)

    th = rng.uniform(0.0, math.pi / 2.0, n)
    w = 0.5 * (np.abs(np.cos(th)) + np.abs(np.sin(th)))
    cx = rng.uniform(0.0, 1.0, n) * (s - 2 * w) + w
    cy = rng.uniform(0.0, 1.0, n) * (s - 2 * w) + w
    C = np.stack([cx, cy], 1)
    ok = np.ones(n, bool)
    for P in obstacles:
        ok &= polycore.poly_square_depth(P, C, th) <= 0.0
    hf, nf = hits_of(cx[ok], cy[ok], th[ok], 0.5 * lam)
    out = dict(free=dict(drawn=int(n), admissible=int(ok.sum()), tested=int(nf), hits=hf,
                         claim="no admissible free pose contains a certified-uncoverable cell "
                               "centre"))
    nb = max(1000, n // 10)
    for i, b in enumerate(boxes):
        bx = rng.uniform(float(b.x0), float(b.x1), nb)
        by = rng.uniform(float(b.y0), float(b.y1), nb)
        bt = rng.uniform(math.radians(float(b.th0)), math.radians(float(b.th1)) + 1e-15, nb)
        hb, nbt = hits_of(bx, by, bt, 0.5 * lam)
        out[f"box{i}"] = dict(drawn=int(nb), tested=int(nbt), hits=hb,
                              claim="no pose of this hypothesis box contains a certified-"
                                    "uncoverable cell centre")
    return out


def runs_of(mask, xs, ys, p):
    """horizontal runs of a bool grid -> [(x0, x1, y0, y1)] for a compact SVG (A148's `runs`)."""
    out = []
    ny, nx = mask.shape
    for j in range(ny):
        row = mask[j]
        i = 0
        while i < nx:
            if not row[i]:
                i += 1
                continue
            k = i
            while k < nx and row[k]:
                k += 1
            out.append((xs[i] - 0.5 * p, xs[k - 1] + 0.5 * p, ys[j] - 0.5 * p, ys[j] + 0.5 * p))
            i = k
    return out


def obstacles_of(boxes):
    """A148's `obstacles_of`, verbatim (K'(B) of each conditioned square, the A135 exact core
    square of each pin) -- imported so the two attempts cannot drift apart."""
    return G148.obstacles_of(boxes)
