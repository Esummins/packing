"""A230 -- Rule EPS, the successor of A227's eps227.py (docs/proofs/lemma_eps.md), with three levers:

  (1) ALL CANDIDATES (A230_ALLCAND=1): a role is a candidate at a slot when its position BOX comes within EPS_C of
      the slot centre (A224 tested the box CENTRE) and SOME piece's tilt bin is within DEG of alignment (A224 asked
      for EVERY piece), so a role that is near-simple in either of two cells is evaluated in both; the candidates
      are evaluated in a deterministic order, the SMALLEST box first, and EVERY one is evaluated (the verdict is
      taken from the first that leaves the cell with < 2 distinct non-pin meeters, but the record is complete).
      The filter stays HEURISTIC -- Lemma EPS-4 bounds C \\ F over ANY pose box, so widening it cannot be unsound.
  (2) TAPER (A230_TAPER=1): the strike tests the wedge POLYGON, not only its bounding rectangle -- a separating-axis
      test of the pose box against the convex polygon (A227 s.7 [C]).  Extra axes: the polygon's edge normals, with
      the square's support radius bounded by interval arithmetic in (cos, sin) over the tilt bin; plus the square's
      own two normals against the Minkowski difference (box corners) - (polygon vertices).  Sound: the actual wedge
      lies inside the polygon, which lies inside its bounding rectangle -- a strike here is a strike a fortiori.
  (3) NS-AT-WEDGE (A230_WEDGE_NS=1): where exactly ONE named role survives and the anonymous clause is CERTIFIED
      empty, that role must meet one of the targets it can still reach (Theorem FC + EPS-3/4/5), so
      "M meets W" / "M misses W" is an exhaustive split whose MISSES child is DEAD at once by FC+EPS, and whose
      MEETS child carries M's pieces clipped to the poses that reach W (`apply_wedge`).

READ-ONLY on A227 (eps227: the exact wedge polygons, the backing, the targets, the anonymous clause), A224
(snap224), A171 (multibox), A161 (chordlane), A204 (poly204).  Flags default OFF; every statement is n-general.
"""
import os
from fractions import Fraction as Fr

import multibox as MB                                         # noqa: E402  READ-ONLY (A171)
import poly204 as P                                           # noqa: E402  READ-ONLY (A204): hull_box
import snap224 as S                                           # noqa: E402  READ-ONLY (A224): misses_t, the filters
import eps227 as E                                            # noqa: E402  READ-ONLY (A227): wedges, targets, gate


def _flag(name, dflt):
    v = (os.environ.get(name) or "").strip().lower()
    return dflt if v == "" else v in ("1", "on", "yes")


ON = _flag("A230_EPS", False) or _flag("A227_EPS", False)
ALLCAND = _flag("A230_ALLCAND", True)
TAPER = _flag("A230_TAPER", True)
WEDGE_NS = _flag("A230_WEDGE_NS", True)
EPS_C = float(os.environ.get("A230_EPS_C") or S.EPS_C)
DEG = float(os.environ.get("A230_DEG") or S.DEG)
MAX_TESTS = int(os.environ.get("A230_MAXTESTS") or 40000)
MAX_DEN = int(os.environ.get("A230_MAXDEN") or 10 ** 30)      # polygon vertices coarser than this: no taper claim
MAX_VERTS = 12
HALF = Fr(1, 2)
SIDES = E.SIDES


# --------------------------------------------------------------------------- (1) the candidates
def box_dist(pg, k, p):
    """l-inf distance from the slot centre to the role's position BOX (0 when the centre is inside it)."""
    b = pg.roles[k]
    sx, sy = S.slot_centre(pg, p)
    return max(0.0, float(b[0]) - sx, sx - float(b[1]), float(b[2]) - sy, sy - float(b[3]))


def box_vol(pg, k):
    b = pg.roles[k]
    return (float(b[1]) - float(b[0])) * (float(b[3]) - float(b[2])) * max(1e-9, float(b[5]) - float(b[4]))


def candidates(pg):
    """every (role, slot) pair worth evaluating, SMALLEST box first; `old` marks the pairs A224's filter already
    returned (so the re-scan can say what the widening added)."""
    out = []
    for k in S.roles_of(pg):
        sp = S.tilt_span(pg, k)
        al_all = all(t1 <= DEG or t0 >= 90.0 - DEG for t0, t1 in sp)
        al_any = any(t1 <= DEG or t0 >= 90.0 - DEG for t0, t1 in sp)
        tilt = (round(min(t for t, _ in sp), 3), round(max(t for _, t in sp), 3), len(sp))
        b = pg.roles[k]
        for p in pg.slots:
            sx, sy = S.slot_centre(pg, p)
            dc = max(abs(0.5 * (b[0] + b[1]) - sx), abs(0.5 * (b[2] + b[3]) - sy))
            db = box_dist(pg, k, p)
            old = (dc <= EPS_C and al_all)
            new = (db <= EPS_C and al_any)
            if not (old or (ALLCAND and new)):
                continue
            out.append(dict(role=k, slot=p, dist=round(dc, 6), bdist=round(db, 6), old=bool(old), tilt=tilt,
                            vol=round(box_vol(pg, k), 9)))
    out.sort(key=lambda d: (d["vol"], d["role"], d["slot"]))
    return out


# --------------------------------------------------------------------------- (2) the polygon strike
def _iv(a, lo, hi):
    return (min(a * lo, a * hi), max(a * lo, a * hi))


def sq_radius(a, b, t0, t1):
    """exact rational UPPER bound of the unit square's support radius in the (unnormalised) direction (a, b) over
    the tilt bin: max over the bin of (|a cos + b sin| + |b cos - a sin|)/2, by interval arithmetic in (cos, sin)
    (cos decreasing, sin increasing in t on [0, 1]) -- the same relaxation Lemma EPS-4 uses."""
    c0, s0 = MB.cos_sin_t(t0)
    c1, s1 = MB.cos_sin_t(t1)
    cl, ch = min(c0, c1), max(c0, c1)
    sl, sh = min(s0, s1), max(s0, s1)
    Al, Ah = _iv(a, cl, ch)
    Bl, Bh = _iv(b, sl, sh)
    A = (Al + Bl, Ah + Bh)                                    # a cos + b sin
    Cl, Ch = _iv(-a, sl, sh)
    Dl, Dh = _iv(b, cl, ch)
    B = (Cl + Dl, Ch + Dh)                                    # b cos - a sin
    return (max(A[1], -A[0]) + max(B[1], -B[0])) / 2


def poly_ok(poly):
    return bool(poly) and 3 <= len(poly) <= MAX_VERTS and all(
        v[0].denominator <= MAX_DEN and v[1].denominator <= MAX_DEN for v in poly)


def misses_poly_t(x0, x1, y0, y1, t0, t1, poly):
    """SOUND, exact: True if EVERY pose in the box gives a square whose interior misses the convex polygon.  Same
    separating-axis scheme as A161's box_misses_cell_exact, with the polygon's edge normals added and the
    Minkowski difference D = {box corner} - {polygon vertex} (its extreme points) in place of the rectangle's."""
    if t0 < 0 or t1 > 1 or t1 < t0 or not poly_ok(poly):
        return False, None
    D = [(zx - v[0], zy - v[1]) for zx, zy in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)) for v in poly]
    axes = [(Fr(1), Fr(0)), (Fr(-1), Fr(0)), (Fr(0), Fr(1)), (Fr(0), Fr(-1))]
    n = len(poly)
    for i in range(n):                                        # family A': the polygon's own edge normals
        Pv, Qv = poly[i], poly[(i + 1) % n]
        ex, ey = Qv[0] - Pv[0], Qv[1] - Pv[1]
        if ex or ey:
            axes += [(ey, -ex), (-ey, ex)]
    for a, b in axes:
        r = sq_radius(a, b, t0, t1)
        m = min(a * dx + b * dy for dx, dy in D)
        if m >= r:
            return True, dict(axis="poly", w=[str(a), str(b)], margin=str(m - r), radius=str(r))
    cl = S.CL()                                               # family B: the SQUARE's own normals, radius 1/2
    for k in (0, 1):
        for sg in (1, -1):
            worst = None
            for dx, dy in D:
                ex, ey = sg * dx, sg * dy
                if k == 1:
                    ex, ey = ey, -ex
                g = cl._proj_min_exact(ex, ey, t0, t1)
                worst = g if worst is None else min(worst, g)
            if worst >= HALF:
                return True, dict(axis="polyw%d%s" % (k, "+" if sg > 0 else "-"), margin=str(worst - HALF))
    return False, None


def targets(box, C, back):
    """A227's target list, each free-side wedge rectangle paired with its EXACT polygon when the pairing is
    unambiguous (two polygons sharing a bounding box: no taper claim, the rectangle stands)."""
    tg, info = E.targets(box, C, back)
    pm = {}
    if TAPER:
        polys = E.wedge_polys(box, C)
        E.assign(polys, C)
        for Pp in polys:
            pm.setdefault(tuple(Pp["bbox"]), []).append(Pp["poly"])
    out = []
    for nm, T in tg:
        pl = pm.get(tuple(T)) if nm.startswith("wedge") else None
        out.append((nm, tuple(T), pl[0] if (pl and len(pl) == 1) else None))
    info["n_taper"] = sum(1 for _n, _T, pl in out if pl is not None)
    return out, info


# --------------------------------------------------------------------------- the strike, over ALL targets
def _miss1(bx, T, pl, bud):
    bud[0] -= 1
    if bud[0] < 0:
        return None
    if S.misses_t(*bx, T)[0]:
        return "rect"
    if pl is not None and misses_poly_t(*bx, pl)[0]:
        return "taper"
    return False


def reach(pg, k, tg, bud):
    """-> (the names of the targets role k can still reach, taper-only strikes) or (None, n) on budget."""
    boxes = [E.hull_box(pg, k)]
    boxes += [(Fr(r[0]), Fr(r[1]), Fr(r[2]), Fr(r[3]), bn.t0, bn.t1) for bn, r in (pg.pieces.get(k) or [])]
    got, tap = [], 0
    for nm, T, pl in tg:
        m = _miss1(boxes[0], T, pl, bud)
        if m is None:
            return None, tap
        if m:
            tap += 1 if m == "taper" else 0
            continue
        if len(boxes) == 1:
            got.append(nm)
            continue
        for bx in boxes[1:]:
            m2 = _miss1(bx, T, pl, bud)
            if m2 is None:
                return None, tap
            if not m2:
                got.append(nm)
                break
            tap += 1 if m2 == "taper" else 0
    return got, tap


def strike(pg, F, M, C, back, bud):
    """M is STRUCK iff it misses every target of F's hull box, or -- failing that -- for EVERY piece of F it misses
    every target of that piece (the true F lies in one piece).  Otherwise `reach` is the HULL target list it can
    still reach: the disjunction the NS-at-wedge split branches on."""
    tg, _info = targets(E.hull_box(pg, F), C, back)
    got, tap = reach(pg, M, tg, bud)
    if got is None:
        return dict(struck=False, via="budget", reach=[], taper=tap)
    if not got:
        return dict(struck=True, via="hull", reach=[], taper=tap)
    pcs = pg.pieces.get(F) or []
    if pcs:
        allmiss = True
        for bn, r in pcs:
            tgp, _i = targets((Fr(r[0]), Fr(r[1]), Fr(r[2]), Fr(r[3]), bn.t0, bn.t1), C, back)
            g2, t2 = reach(pg, M, tgp, bud)
            tap += t2
            if g2 is None or g2:
                allmiss = False
                break
        if allmiss:
            return dict(struck=True, via="pieces", reach=[], taper=tap)
    return dict(struck=False, via="hull", reach=got, taper=tap)
