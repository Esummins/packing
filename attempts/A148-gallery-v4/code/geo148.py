"""A148 -- the geometry behind the v4 pages.  Drawing lives in gallery148.py.

Everything here answers one question, the PI's: **can the remaining squares still fit in the white
space?**  Four objects do the work.

  FEASIBLE-CENTRE REGION  R = { c : SOME tilt t gives a unit square Q(c,t) inside the container,
      interior-disjoint from every pin's EXACT core and from K'(B) of every conditioned square }.
      Computed on a grid of pitch <= 0.02 x 36 tilts.  Both the GREEN (certified free) and the
      BLOCKED (certified no-square) verdicts carry a MARGIN, so the drawing is sound in both
      directions rather than a bare sample:

        clearance(c,t) = min( container clearance of the centre , min_j ( -depth(K_j, Q(c,t)) ) )

      is 1-Lipschitz in the centre and (sqrt2/2)-Lipschitz in the tilt (rotating a unit square by
      d moves every boundary point by at most (sqrt2/2)d, and SAT depth between convex sets is
      1-Lipschitz in Hausdorff distance).  With p the grid pitch and dth the tilt step,

        m = p*sqrt2/2  +  (sqrt2/2)*(dth/2)

      GREEN   cell:  max over sampled tilts of clearance(centre) >=  +m   -- then EVERY point of
                     the cell admits a feasible tilt (certified inner approximation of R);
      BLOCKED cell:  max over sampled tilts of clearance(centre) <   -m   -- then NO point of the
                     cell admits ANY tilt (certified outer approximation of the complement);
      otherwise the cell is UNDECIDED (the band between them, drawn pale).

  DISK BOUND.  A unit square contains the disk of radius 1/2 about its centre, so the centres of
      the `budget` remaining squares are a 1-separated set whose half-unit disks are disjoint and
      lie inside the container.  Every such centre lies in R, hence in (GREEN u UNDECIDED).  So

        budget  <=  area( (GREEN u UNDECIDED) (+) B(1/2)  n  [0,s]^2 )  /  (pi/4)

      -- a sound upper bound on how many more squares the node can hold, from the drawing alone.
      `n_max_disk < budget` is a geometric KILL with no LP.

  POCKETS.  Exact convex-polygon distance between every pair of obstacles and from each obstacle
      to each wall; a gap < 1 is a pocket no further unit square fits into.

  GUARD LINES (A144).  rhs(l) = s - SUM_j minchord(box_j, l) over the hypothesis boxes; the chord
      sum s - rhs(l) is what the hypothesis squares alone are guaranteed to occupy on l.  A line
      with rhs(l) < 0 is an outright contradiction; the pages print every line with rhs <= 0.15
      (chord sum within 0.15 of s0).

Read-only on every campaign: A132/A135/A131/A144/A141/A140/A142 are imported, never written.
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
for _p in (os.path.join(ATT, "A57-shadow-trees", "code"),
           os.path.join(ATT, "A132-polygon-core", "code"),
           os.path.join(ATT, "A135-polycore-verifier", "code"),
           os.path.join(ATT, "A131-pin-clip", "code"),
           os.path.join(ATT, "A144-guard-lines", "code"),
           os.path.join(ATT, "A107-shadow-gallery", "code"),
           os.path.join(ATT, "A140-k0-residue-gallery", "code"),
           HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import polycore                                                   # noqa: E402
import exactcore                                                  # noqa: E402
import guardline as GL                                            # noqa: E402
from caselp import Box                                            # noqa: E402

S0 = 969271.0 / 250000.0
SHAT = 3.877083590022814
ROOT2H = math.sqrt(2.0) / 2.0

PITCH_TARGET = 0.02
NTILT = 36


# ===================================================================== small primitives
def sqpoly(cx, cy, th, h=0.5):
    c, s = math.cos(th), math.sin(th)
    return [(cx + h * (dx * c - dy * s), cy + h * (dx * s + dy * c))
            for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


def sat_gap(P, Q):
    """separating-axis gap between convex polygons: > 0 disjoint, < 0 = overlap depth."""
    best = -9e9
    for A, B in ((P, Q), (Q, P)):
        n = len(A)
        for i in range(n):
            a, b = A[i], A[(i + 1) % n]
            ex, ey = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(ex, ey)
            if ln < 1e-15:
                continue
            ax, ay = -ey / ln, ex / ln
            pp = [x * ax + y * ay for x, y in A]
            qq = [x * ax + y * ay for x, y in B]
            best = max(best, min(qq) - max(pp), min(pp) - max(qq))
    return best


def _pt_seg(p, a, b):
    ex, ey = b[0] - a[0], b[1] - a[1]
    ln = ex * ex + ey * ey
    t = 0.0 if ln <= 0 else max(0.0, min(1.0, ((p[0] - a[0]) * ex + (p[1] - a[1]) * ey) / ln))
    return math.hypot(p[0] - (a[0] + t * ex), p[1] - (a[1] + t * ey))


def poly_dist(P, Q):
    """EXACT minimum distance between two convex polygons (0 when they meet).  A pocket claim
    needs an upper bound as well as a lower one, which the SAT gap does not give."""
    if sat_gap(P, Q) < 0.0:
        return 0.0
    d = 9e9
    for i in range(len(P)):
        a, b = P[i], P[(i + 1) % len(P)]
        for j in range(len(Q)):
            c, e = Q[j], Q[(j + 1) % len(Q)]
            d = min(d, _pt_seg(a, c, e), _pt_seg(b, c, e), _pt_seg(c, a, b), _pt_seg(e, a, b))
    return d


def closest_pair(P, Q):
    """(a in P, b in Q) realising (near enough) the minimum distance -- for drawing the pocket."""
    best = (9e9, P[0], Q[0])
    for i in range(len(P)):
        a, b = P[i], P[(i + 1) % len(P)]
        for q in Q:
            ex, ey = b[0] - a[0], b[1] - a[1]
            ln = ex * ex + ey * ey
            t = 0.0 if ln <= 0 else max(0.0, min(1.0, ((q[0] - a[0]) * ex + (q[1] - a[1]) * ey) / ln))
            f = (a[0] + t * ex, a[1] + t * ey)
            d = math.hypot(q[0] - f[0], q[1] - f[1])
            if d < best[0]:
                best = (d, f, q)
    for i in range(len(Q)):
        a, b = Q[i], Q[(i + 1) % len(Q)]
        for q in P:
            ex, ey = b[0] - a[0], b[1] - a[1]
            ln = ex * ex + ey * ey
            t = 0.0 if ln <= 0 else max(0.0, min(1.0, ((q[0] - a[0]) * ex + (q[1] - a[1]) * ey) / ln))
            f = (a[0] + t * ex, a[1] + t * ey)
            d = math.hypot(q[0] - f[0], q[1] - f[1])
            if d < best[0]:
                best = (d, q, f)
    return best[1], best[2]


# ===================================================================== the feasible-centre region
class Region:
    """the three-valued centre map on the grid, plus its soundness constants."""

    def __init__(self, s, pitch, ntilt, green, blocked, clear, xs, ys, margin):
        self.s, self.pitch, self.ntilt = s, pitch, ntilt
        self.green, self.blocked = green, blocked          # (ny, nx) bool
        self.clear = clear                                 # (ny, nx) best clearance over tilts
        self.xs, self.ys = xs, ys
        self.margin = margin
        self.undecided = ~(green | blocked)

    def area_green(self):
        return float(self.green.sum()) * self.pitch ** 2

    def area_open(self):
        return float((~self.blocked).sum()) * self.pitch ** 2

    def runs(self, mask):
        """horizontal runs of a boolean grid -> [(x0, x1, y0, y1)], for a compact SVG."""
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
                out.append((self.xs[i] - 0.5 * self.pitch, self.xs[k - 1] + 0.5 * self.pitch,
                            self.ys[j] - 0.5 * self.pitch, self.ys[j] + 0.5 * self.pitch))
                i = k
        return out


def clearance_grid(s, obstacles, pitch_target=PITCH_TARGET, ntilt=NTILT):
    """max over `ntilt` sampled tilts of clearance(c, t), on a grid of pitch <= pitch_target."""
    n = int(math.ceil(s / pitch_target))
    pitch = s / n
    xs = (np.arange(n) + 0.5) * pitch
    ys = (np.arange(n) + 0.5) * pitch
    X, Y = np.meshgrid(xs, ys)
    C = np.stack([X.ravel(), Y.ravel()], 1)
    best = np.full(len(C), -9e9)
    ths = (np.arange(ntilt) + 0.5) * (math.pi / 2.0) / ntilt
    for th in ths:
        w = 0.5 * (abs(math.cos(th)) + abs(math.sin(th)))
        cl = np.minimum.reduce([C[:, 0] - w, s - w - C[:, 0], C[:, 1] - w, s - w - C[:, 1]])
        for P in obstacles:
            d = polycore.poly_square_depth(P, C, np.full(len(C), th))
            cl = np.minimum(cl, -d)
        best = np.maximum(best, cl)
    return best.reshape(n, n), xs, ys, pitch


def feasible_region(s, obstacles, pitch_target=PITCH_TARGET, ntilt=NTILT):
    clear, xs, ys, pitch = clearance_grid(s, obstacles, pitch_target, ntilt)
    dth = (math.pi / 2.0) / ntilt
    margin = pitch * ROOT2H + ROOT2H * (dth / 2.0)
    return Region(s, pitch, ntilt, clear >= margin, clear < -margin, clear, xs, ys, margin)


def sample_confirm_region(reg, obstacles, n=10000, seed=148, ntilt_fine=360):
    """drawn -> tested -> hits.  n centres drawn uniformly inside the GREEN cells must each admit
    a feasible tilt; n drawn inside the BLOCKED cells must admit none.  An independent tilt sweep
    (`ntilt_fine`, ten times denser) and this file's own SAT decide, not the grid verdict."""
    rng = np.random.default_rng(seed)
    out = {}
    ths = (np.arange(ntilt_fine) + 0.5) * (math.pi / 2.0) / ntilt_fine
    for tag, mask, want in (("green", reg.green, True), ("blocked", reg.blocked, False)):
        jj, ii = np.nonzero(mask)
        if len(ii) == 0:
            out[tag] = dict(drawn=0, hits=0, note="empty")
            continue
        pick = rng.integers(0, len(ii), n)
        cx = reg.xs[ii[pick]] + rng.uniform(-0.5, 0.5, n) * reg.pitch
        cy = reg.ys[jj[pick]] + rng.uniform(-0.5, 0.5, n) * reg.pitch
        C = np.stack([cx, cy], 1)
        ok = np.zeros(n, bool)
        for th in ths:
            w = 0.5 * (abs(math.cos(th)) + abs(math.sin(th)))
            cl = np.minimum.reduce([C[:, 0] - w, reg.s - w - C[:, 0],
                                    C[:, 1] - w, reg.s - w - C[:, 1]])
            for P in obstacles:
                cl = np.minimum(cl, -polycore.poly_square_depth(P, C, np.full(n, th)))
            ok |= cl > 0.0
        hits = int((~ok).sum()) if want else int(ok.sum())
        out[tag] = dict(drawn=int(n), feasible=int(ok.sum()), hits=hits,
                        tilts=int(ntilt_fine),
                        claim=("every drawn centre admits a feasible tilt" if want else
                               "no drawn centre admits any feasible tilt"))
    return out


def disk_bound(reg):
    """budget <= area( (not-blocked) (+) B(1/2) n [0,s]^2 ) / (pi/4): a sound cap on how many more
    unit squares the node can hold, straight off the region."""
    open_mask = ~reg.blocked
    r = int(math.ceil(0.5 / reg.pitch)) + 1               # dilate OUTWARD (an over-estimate)
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    disk = (yy ** 2 + xx ** 2) <= (0.5 / reg.pitch + 1.0) ** 2
    ny, nx = open_mask.shape
    out = np.zeros((ny + 2 * r, nx + 2 * r), bool)        # shift-OR dilation by the disk
    for (dy, dx) in np.argwhere(disk):
        out[dy:dy + ny, dx:dx + nx] |= open_mask
    inside = out[r:r + ny, r:r + nx]                      # clipped back to the container
    area = float(inside.sum()) * reg.pitch ** 2
    return dict(area_dilated=area, n_max=int(math.floor(area / (math.pi / 4.0))),
                area_open=reg.area_open(), area_green=reg.area_green(),
                note="disks of radius 1/2 about the centres are disjoint and inside the container")


# ===================================================================== pockets
FLUSH = 0.05


def pockets(obstacles, names, s, walls=True, flush=FLUSH):
    """Every obstacle-to-obstacle and obstacle-to-wall clearance, narrowest first.

    A clearance below `flush` is NOT a pocket: it is two objects (or an object and a wall) in
    contact.  Every A57 pin touches two walls and its lattice neighbours, so those five squares
    would otherwise contribute ~20 uninformative 0.007-0.014 entries and bury the real pockets.
    Contacts are counted in `n_flush` (carried on every returned row) and dropped from the list."""
    out, nflush = [], 0
    for i in range(len(obstacles)):
        for j in range(i + 1, len(obstacles)):
            g = poly_dist(obstacles[i], obstacles[j])
            if g < flush:
                nflush += 1
                continue
            a, b = closest_pair(obstacles[i], obstacles[j])
            out.append(dict(kind="core-core", to=f"{names[i]}-{names[j]}", gap=float(g),
                            seg=[list(a), list(b)]))
    if walls:
        for i, P in enumerate(obstacles):
            xs = [v[0] for v in P]
            ys = [v[1] for v in P]
            mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
            for nm, g, seg in (("wall x=0", min(xs), [[min(xs), my], [0.0, my]]),
                               ("wall x=s", s - max(xs), [[max(xs), my], [s, my]]),
                               ("wall y=0", min(ys), [[mx, min(ys)], [mx, 0.0]]),
                               ("wall y=s", s - max(ys), [[mx, max(ys)], [mx, s]])):
                if g < flush:
                    nflush += 1
                    continue
                out.append(dict(kind="core-wall", to=f"{names[i]}->{nm}", gap=float(g),
                                seg=seg))
    out.sort(key=lambda r: r["gap"])
    for r in out:
        r["n_flush"] = nflush
    return out


def pocket_band(P, Q, a, b):
    """the hatched quadrilateral of a pocket: the strip between the two features, spanned by the
    closest segment a->b and the mutual shadow of P and Q perpendicular to it."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    ln = math.hypot(dx, dy)
    if ln < 1e-12:
        return None
    ux, uy = dx / ln, dy / ln
    px, py = -uy, ux
    pp = [v[0] * px + v[1] * py for v in P]
    qq = [v[0] * px + v[1] * py for v in Q]
    lo, hi = max(min(pp), min(qq)), min(max(pp), max(qq))
    if hi <= lo:
        lo, hi = (a[0] * px + a[1] * py) - 0.02, (a[0] * px + a[1] * py) + 0.02
    o = a[0] * ux + a[1] * uy
    return [(ux * o + px * lo, uy * o + py * lo),
            (ux * (o + ln) + px * lo, uy * (o + ln) + py * lo),
            (ux * (o + ln) + px * hi, uy * (o + ln) + py * hi),
            (ux * o + px * hi, uy * o + py * hi)]


# ===================================================================== guard lines
def guard_lines(boxes, pc_verts, s=S0, a_pin=None, max_lines=40, n_keep=6):
    """A144's <= 40-line family on this node, evaluated exactly; the tightest `n_keep` returned.

    rhs(l) = s - SUM over ALL hypothesis boxes of minchord(box, l); chord_sum = s - rhs."""
    bx = [Box.from_json(b) if isinstance(b, dict) else b for b in boxes]
    pins = [b for b in bx if b.th1 <= b.th0 + 1e-12]
    fam = GL.line_family(pins, bx[-1], s=Fr(969271, 250000), pc_verts=pc_verts,
                         a_pin=a_pin, max_lines=max_lines)
    rows = []
    for ln in fam:
        r = GL.guard_row(bx[:-1], bx[-1], ln, s=Fr(969271, 250000), pc_verts=pc_verts)
        chord_sum = float(Fr(969271, 250000) - r["rhs"])
        rows.append(dict(orient=ln.orient, off=float(ln.off), tag=ln.tag,
                         rhs=float(r["rhs"]), chord_sum=chord_sum,
                         per_box=[float(x) for x in r["pins_float"]] + [r["h_float"]],
                         n_full=int(r["n_pins_full"])))
    rows.sort(key=lambda r: r["rhs"])
    return rows[:n_keep], rows


# ===================================================================== node-level assembly
def obstacles_of(boxes, is_pin=None):
    """(polygons, names, kinds) for the node: K'(B) of every conditioned square, the EXACT core
    square of every pin."""
    P, names, kinds, extra = [], [], [], []
    npin = 0
    for i, bj in enumerate(boxes):
        b = Box.from_json(bj) if isinstance(bj, dict) else bj
        pin = (b.th1 <= b.th0 + 1e-12) if is_pin is None else bool(is_pin[i])
        if pin:
            cx, cy = 0.5 * (b.x0 + b.x1), 0.5 * (b.y0 + b.y1)
            try:
                a, a0, ok = exactcore.exact_a(b)
                af = float(a)
            except Exception:                                        # noqa: BLE001
                af, ok = float(b.core().a), False
            P.append(sqpoly(cx, cy, 0.0, af))
            names.append(f"P{npin}")
            kinds.append(dict(kind="pin", a_exact=af, certified=bool(ok), c=[cx, cy]))
            npin += 1
        else:
            pc = polycore.build(b)
            P.append([(float(u), float(v)) for u, v in pc.P])
            names.append("H" if sum(1 for k in kinds if k["kind"] == "H") == 0 else
                         f"H{sum(1 for k in kinds if k['kind'] == 'H')}")
            k = b.core()
            try:
                ax, a0, ok = exactcore.exact_a(b)
            except Exception:                                        # noqa: BLE001
                ax, a0, ok = None, k.a, False
            kinds.append(dict(kind="H", a_stock=float(k.a),
                              a_exact=(float(ax) if ax is not None else None),
                              exact_ok=bool(ok), area_poly=pc.area(), verts=len(pc.verts),
                              pc=pc, box=b))
        extra.append(b)
    return P, names, kinds, extra
