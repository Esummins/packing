"""A242 -- the CROWD ROOT H_B: the k0 hypothesis with the EIGHT corner meeters boxed, as a cell.

THE ROOT (`k0_route.md` s.4.2, Lemma K0-BLOCKED (structure); `local_lock.md` s.2.1 LOCALITY (i)).
------------------------------------------------------------------------------------------------
Fix a BAND [m_lo, m_hi] of sides and put S := m_hi, lam := S/m in [1, S/m_lo] for a packing P at
side m in the band, F := Delta_lam P (centres scaled by lam about the origin, tilts and sizes
unchanged).  Lemma B.0 (`closed_disjoint_bridge.md`): F is a strictly disjoint closed 11-family
inside [0, S]^2 with positive wall margins.  Lemma K0-WIDEN (`k0_route.md` s.4.1, proved there for
s0 and lam >= 1; its proof uses only lam >= 1 and the container, so it holds verbatim with S in
place of s0): a square of P meeting int B_c(m) has its image meeting int B_c^w(S) with

    w = (lam_max - 1) (1 + sqrt(2)/2),   lam_max = m_hi / m_lo.                         (WIDEN)

So if EVERY corner box of P is doubly met (P is TELEPORT-STUCK, `Statements/Open/LocalLock.lean`
`TeleportStuck`), then F has at each corner two distinct squares meeting int B_c^w(S), and by
CC-1(ii) with the widening the four pairs are pairwise disjoint sets of squares (a unit square has
diameter sqrt 2 < S - 2 - 2w for every band used here): EIGHT distinct squares of F localised to
the four widened corner reach sets, three free.

THE ROLE BOX.  In the frame of corner c a meeter Q has centre z with (i) z_u, z_v >= h(theta) =
w(theta)/2 >= 1/2 (containment, F2) and (ii) a point p in Q with p_u, p_v < 1 + w and
|p - z|_inf <= w(theta)/2 <= sqrt(2)/2, so z_u, z_v < 1 + w + sqrt(2)/2 (F1; `local_lock.md` s.2.1
Lemma LOCALITY (i) with the widening).  Hence

    R_c^w  is contained in  [1/2, 1 + w + sqrt(2)/2]^2 x [0 deg, 90 deg)                (ROLEBOX)

(tilts mod 90 deg: a unit square's pose set is 90-deg periodic).  That box, mapped into container
coordinates by the corner's frame map, is the ROOT box of both of c's roles.

WHAT THE ROOT COVERS.  H_B(band) = "there is a packing P at some side m in [m_lo, m_hi] all four of
whose corner boxes are doubly met".  Every teleport-stuck packing below 4 lies in exactly one band
of `BANDS`, so the bands' union covers "teleport-stuck k0 below 4" on [3.82, 4).  The LOCKED
hypothesis of STUCK-4(11) is NOT used by the root or by leaf L1 -- L1 kills every K0-BLOCKED
packing of its cell, locked or not.  D4 (Lemma K0-D4 (ii)) is NOT quotiented in the cascade; it is
worth a factor 8 on the price and is left on the table (see `notes/crowd242.md` s.5).
"""
import math

SQ2 = math.sqrt(2.0)
CORNERS = ("BL", "BR", "TR", "TL")

# The band table.  [3.82, s0] is A85's window (s0 = 969271/250000 = 3.877084 >= s-hat); the rest
# climb to 4 in steps whose widening w stays below 0.03, the value A85's tree was designed for.
BANDS = [
    ("W", 3.82, 3.877084),
    ("B1", 3.877084, 3.92),
    ("B2", 3.92, 3.96),
    ("B3", 3.96, 4.0),
]


def band_widening(m_lo, m_hi):
    """w of (WIDEN)."""
    return (m_hi / m_lo - 1.0) * (1.0 + SQ2 / 2.0)


def band_ok(m_lo, m_hi):
    """CC-1(ii) with the widening: distinct widened corner boxes are more than sqrt 2 apart, so the
    four meeter pairs are disjoint sets of squares.  Returns (ok, slack)."""
    w = band_widening(m_lo, m_hi)
    return (m_hi - 2.0 - 2.0 * w > SQ2, m_hi - 2.0 - 2.0 * w - SQ2)


def corner_box(c, S, w):
    """(ROLEBOX) in container coordinates: [x0, x1, y0, y1, th0, th1], degrees."""
    lo, hi = 0.5, 1.0 + w + SQ2 / 2.0
    if hi > S - 0.5:                       # the reach set cannot leave the container's centre box
        hi = S - 0.5
    if c == "BL":
        return [lo, hi, lo, hi, 0.0, 90.0]
    if c == "BR":
        return [S - hi, S - lo, lo, hi, 0.0, 90.0]
    if c == "TR":
        return [S - hi, S - lo, S - hi, S - lo, 0.0, 90.0]
    return [lo, hi, S - hi, S - lo, 0.0, 90.0]


def root_cell(band="W", n=11):
    """The root cell: eight boxed roles (two per corner) and n - 8 = 3 anonymous free squares."""
    tag, m_lo, m_hi = [b for b in BANDS if b[0] == band][0]
    S = m_hi
    w = band_widening(m_lo, m_hi)
    ok, slack = band_ok(m_lo, m_hi)
    roles = {}
    for c in CORNERS:
        b = corner_box(c, S, w)
        roles["%sA" % c] = list(b)
        roles["%sB" % c] = list(b)
    return dict(band=tag, m_lo=m_lo, m_hi=m_hi, S=S, w=w, lam_max=m_hi / m_lo,
                disjoint_ok=bool(ok), disjoint_slack=slack, n=n, m=n - 8,
                label="H_B(%s)" % tag, depth=0, roles=roles,
                split_log=[], parent=None)


def pair_order_ok(cell):
    """NO symmetry quotient is taken.  The tempting one -- the two meeters of a corner are an
    UNORDERED pair, so drop every child whose B box is lexicographically below its A box -- is NOT
    sound for THIS tree, and the reason is worth recording (`notes/crowd242.md` s.1.4):

    the prune is sound only if, whenever the cell (P, P') is dropped, the mirror cell (P', P) is
    itself a cell of the tree.  The refinement here splits the WIDEST role of the whole cell, a
    rule that is not equivariant under the A <-> B swap (the tie-break prefers A), so A and B of a
    corner can reach different refinement depths and the mirror of a dropped cell need not exist.
    The cover would then have a hole -- an unsound kill.  A245 may reinstate it by splitting a
    corner's two roles in LOCKSTEP, which makes the refinement equivariant; it is worth 2^4 = 16,
    and D4 (Lemma K0-D4 (ii)) a further 8, on a price that needs 10^17 (s.5).  Kept as a named
    hook so that the choice is visible in the code, not only in the notes."""
    return True


def split_axis(box):
    """The widest axis of a role box, in comparable units: centre widths in units of 1, tilt width
    in units of 90 deg scaled to the centre scale by the Lipschitz factor of a unit square's support
    (a tilt change of dth moves a vertex by <= (sqrt 2 / 2) dth radians)."""
    x0, x1, y0, y1, t0, t1 = box
    wx, wy = x1 - x0, y1 - y0
    wt = (t1 - t0) * math.pi / 180.0 * SQ2 / 2.0
    if wx >= wy and wx >= wt:
        return 0, wx
    if wy >= wt:
        return 1, wy
    return 2, wt


def split_role(cell, role):
    """Bisect `role`'s widest axis -> two children (A211's centre / tilt bisection)."""
    import copy
    ax, _ = split_axis(cell["roles"][role])
    lo_i, hi_i = (0, 1) if ax == 0 else ((2, 3) if ax == 1 else (4, 5))
    b = cell["roles"][role]
    mid = 0.5 * (b[lo_i] + b[hi_i])
    kids = []
    for half in (0, 1):
        kid = copy.deepcopy(cell)
        nb = list(b)
        if half == 0:
            nb[hi_i] = mid
        else:
            nb[lo_i] = mid
        kid["roles"][role] = nb
        kid["parent"] = cell["label"]
        kid["depth"] = cell["depth"] + 1
        kid["label"] = "%s/%s%s%d" % (cell["label"], role, "xyt"[ax], half)
        kid["split_log"] = list(cell["split_log"]) + ["%s:%s" % (role, "xyt"[ax])]
        kids.append(kid)
    return [k for k in kids if pair_order_ok(k)]


def widest_role(cell):
    """The role whose box is widest (the split rule: refine the coarsest meeter first)."""
    best, bw = None, -1.0
    for r, b in cell["roles"].items():
        _, w = split_axis(b)
        if w > bw:
            best, bw = r, w
    return best, bw


if __name__ == "__main__":
    import json
    for tag, lo, hi in BANDS:
        c = root_cell(tag)
        print(json.dumps({k: v for k, v in c.items() if k != "roles"}))
        print("   BL role box", [round(x, 4) for x in c["roles"]["BLA"]])
