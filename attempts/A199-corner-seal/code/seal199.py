"""A199 -- the CORNER SEAL leaf (docs/proofs/corner_seal.md), n-general, on a gallery page at a reference side s.

At a pinned corner c with the two forced slots B = c(0,1) and A = c(1,0) (or the mirror), Theorem FC gives a FREE
meeter F of B.  The chain, every step an exact test (multibox / A161):
  (1) F's REACH: the meeter window of B bisected against every role's K' (pins, H) + the container + A161's miss test
      on B's box -> the surviving pieces (a sound superset of F's poses);
  (2) SEAL statistics per surviving piece (exact rationals in the corner frame): the rightmost vertex q, the descending
      edge's angle phi, x_r = q_x - q_y tan(phi), the chord on A's top line, the deep-regime test q_y < cos phi - sin phi;
  (3) F's pieces grouped into sub-boxes (a case split, sound); per sub-box the node {pins, H, F} normalised, then
      (FH) H's pieces / F's pieces against A's box (A161 miss test per piece) and (G) the node {pins, H, F, G_A} with
      G a free meeter of A distinct from F -- EmptyBox(G) kills every case with a further free meeter;
  (4) the corner is DEAD iff every sub-box case is dead; a page is DEAD iff some (corner, orientation) is.
Reference side s and slab factor lam: boxes carry the pad pi_i = (lam - 1)(i + 1 + 1/sqrt2) on their free sides, the
pins the slack eta = (lam - 1)/2, H's box the contraction s/s0 (docs/proofs/corner_seal.md section 5).
"""
import csv
import math
import os
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ATT = os.path.join(ROOT, "attempts")
for _p in (os.path.join(ATT, "A178-gallery-geometry", "code"), os.path.join(ATT, "A190-guardline-clause", "code"),
           os.path.join(ATT, "A161-chord-lane", "code")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import geo178 as G                                             # noqa: E402  READ-ONLY (A178; patches multibox for empty-K' roles)
import classes178 as CL                                        # noqa: E402  READ-ONLY (A178)
import multibox as MB                                          # noqa: E402  READ-ONLY (A171/A172/A173)
import chordlane as CLN                                        # noqa: E402  READ-ONLY (A161)

S0 = MB.S_RAT
HALF = Fr(1, 2)
SQ2H_UP = Fr(7071067812, 10 ** 10)          # > 1/sqrt2
SQ2H_LO = Fr(7071067811, 10 ** 10)          # < 1/sqrt2
EPS = Fr(1, 10 ** 9)
REVIEW = os.path.join(ROOT, "docs", "shadows", "a57v4", "review_a57v4.csv")


# ----------------------------------------------------------------------------- pages
def page_record(page):
    for r in csv.DictReader(open(REVIEW, encoding="utf-8")):
        if page in str(r.values()):
            return r["record"]
    raise KeyError(page)


def load_page(page):
    rp = page_record(page)
    rec = G.load_record(rp)
    cls = G.class_of_record(rec)
    return dict(page=page, record=rp, rec=rec, cls=cls, items={it["cell"]: it for it in G.forced_items(cls, rec)})


def seal_corners(pg):
    """[(corner, B cell, A cell)] -- pinned corners whose two neighbours along the walls are both forced (usable)."""
    pins = CL.pins_of(pg["cls"])
    out = []
    for c in CL.CORNERS:
        if not CL.is_pin(pins, CL.slot_centre(c, 0, 0)):
            continue
        b01, b10 = "%s(0,1)" % c, "%s(1,0)" % c
        if b01 in pg["items"] and b10 in pg["items"]:
            out.append((c, b01, b10))
            out.append((c, b10, b01))
    return out


# ----------------------------------------------------------------------------- frames and boxes at side s
def to_xy(corner, u, v, s):
    x = u if corner in ("BL", "TL") else s - u
    y = v if corner in ("BL", "BR") else s - v
    return x, y


def to_uv(corner, x, y, s):
    u = x if corner in ("BL", "TL") else s - x
    v = y if corner in ("BL", "BR") else s - y
    return u, v


def pad(i, lam):
    return (lam - 1) * (i + 1 + SQ2H_UP)


def cell_box(corner, i, j, s, lam):
    """exact container-frame (X0, X1, Y0, Y1) of the OPEN slot box (i, i+1+pi_i) x (j, j+1+pi_j), rounded outward."""
    u0, u1, v0, v1 = Fr(i), i + 1 + pad(i, lam), Fr(j), j + 1 + pad(j, lam)
    xa, ya = to_xy(corner, u0, v0, s)
    xb, yb = to_xy(corner, u1, v1, s)
    return (min(xa, xb) - EPS, max(xa, xb) + EPS, min(ya, yb) - EPS, max(ya, yb) + EPS)


def window(box, s):
    return (max(HALF, box[0] - SQ2H_UP), min(s - HALF, box[1] + SQ2H_UP), max(HALF, box[2] - SQ2H_UP), min(s - HALF, box[3] + SQ2H_UP))


def cell_of(name):
    c = name[:2]
    i, j = name[3:-1].split(",")
    return c, int(i), int(j)


def page_roles(pg, s, lam):
    """pins at the s-slots with slack eta = (lam-1)/2 (+1e-9), H contracted by s/s0."""
    roles = {}
    eta = (lam - 1) / 2 + Fr(1, 10 ** 9)
    for k, p in enumerate(pg["rec"]["pins"]):
        best = None
        for c in CL.CORNERS:
            u, v = to_uv(c, Fr(str(p["kx"])), Fr(str(p["ky"])), S0)
            if best is None or u + v < best[0]:
                best = (u + v, c, u, v)
        _, c, u, v = best
        us, vs = Fr(round(2 * float(u))) / 2, Fr(round(2 * float(v))) / 2          # the slot centre (half-integers)
        x, y = to_xy(c, us, vs, s)
        roles["P%d" % k] = (float(x - eta), float(x + eta), float(y - eta), float(y + eta), 0.0, 0.0)
    mu = float(s / S0)
    for k, h in enumerate(pg["rec"]["H"]):
        roles["H" if len(pg["rec"]["H"]) == 1 else "H%d" % k] = (h[0] * mu, h[1] * mu, h[2] * mu, h[3] * mu, h[4], h[5])
    return roles


# ----------------------------------------------------------------------------- nodes and exact tests
def run_node(roles, s, nsub=4, refine=2, max_pieces=96):
    t0 = time.time()
    nd = MB.Node(dict(roles), s=s, name="A199")
    try:
        nd.normalise(nsub=nsub, refine=refine, max_iter=10, strict_container=False, mode="poly", kmode="pieces",
                     max_pieces=max_pieces)
    except MB.EmptyBox as e:
        return None, dict(dead=e.name, detail=str(e.detail)[:200], seconds=round(time.time() - t0, 2))
    return nd, dict(dead=None, seconds=round(time.time() - t0, 2), kept={k: round(b.kept_fraction(), 6) for k, b in nd.boxes.items()},
                    hull={k: G.hull_of(nd, k) for k in nd.boxes}, n_pieces={k: len(b.pieces) for k, b in nd.boxes.items()})


def pieces_miss(mb, box):
    """A161 per piece: True iff EVERY surviving piece provably misses the open box."""
    n = 0
    for bn, r in mb.pieces:
        bx = MB.piece_box(bn, r)[0]
        if not CLN.box_misses_cell_exact(bx, box)[0]:
            return False, n
        n += 1
    return True, n


def reach(win, obst, box, s, depth=8, nsub=4, max_pieces=512):
    """pieces of (window x [0,90]) NOT provably dead: container clip, DEAD-CELL vs every obstacle, A161 MISS vs box."""
    stats = {"exact_calls": 0, "backoffs": 0, "passes": 0}
    R = tuple(Fr(v) for v in win)
    pieces = [(MB.Bin(a, b), R) for (a, b) in MB.sub_bins(Fr(0), Fr(1), nsub)]
    vol0 = sum(MB.rect_area(r) * (bn.t1 - bn.t0) for bn, r in pieces)
    n_tests = 0
    for d in range(depth + 1):
        nxt = []
        for bn, r in pieces:
            cur, _ = MB.container_clip(r, bn, s, strict=False)
            n_tests += 1
            for ob in (obst if cur is not None else []):
                cur = MB._clip_rect_obstacle(cur, ob, bn, stats)
                n_tests += 1
                if cur is None:
                    break
            if cur is None:
                continue
            n_tests += 1
            if box is not None and CLN.box_misses_cell_exact(MB.piece_box(bn, cur)[0], box)[0]:
                continue
            if d < depth and len(pieces) <= max_pieces:
                nxt.extend(MB.split_piece(bn, cur))
            else:
                nxt.append((bn, cur))
        pieces = nxt
        if not pieces:
            break
    vol = sum(MB.rect_area(r) * (bn.t1 - bn.t0) for bn, r in pieces)
    return pieces, float(vol / vol0) if vol0 else 0.0, n_tests


def hull(pcs):
    return [float(min(r[0] for _, r in pcs)), float(max(r[1] for _, r in pcs)), float(min(r[2] for _, r in pcs)),
            float(max(r[3] for _, r in pcs)), MB.deg_of_t(min(b.t0 for b, _ in pcs)), MB.deg_of_t(max(b.t1 for b, _ in pcs))]


def sub_boxes(pcs, nx=2, ny=2, nt=2):
    """group the pieces by a grid over their hull; each group's hull is one sub-box (tilt in degrees)."""
    x0, x1, y0, y1, t0, t1 = hull(pcs)
    groups = {}
    for bn, r in pcs:
        cx, cy = float((r[0] + r[1]) / 2), float((r[2] + r[3]) / 2)
        ct = MB.deg_of_t((bn.t0 + bn.t1) / 2)
        key = (min(nx - 1, int((cx - x0) / max(x1 - x0, 1e-12) * nx)), min(ny - 1, int((cy - y0) / max(y1 - y0, 1e-12) * ny)),
               min(nt - 1, int((ct - t0) / max(t1 - t0, 1e-12) * nt)))
        groups.setdefault(key, []).append((bn, r))
    return [hull(g) for _, g in sorted(groups.items())]


# ----------------------------------------------------------------------------- SEAL statistics (exact, per piece)
def _cs(t):
    return (1 - t * t) / (1 + t * t), 2 * t / (1 + t * t)


def seal_piece(bn, r, corner, s, swap):
    """corner frame (x = 1 - u, y = v - 1; the pin at [0,1] x [-1,0]; B above, A beside): exact bounds over the piece of
    q_y (rightmost vertex height), phi (descending edge from vertical), x_r, the deep-regime margin, the chord on y = 0."""
    x0, x1, y0, y1 = r
    us = [to_uv(corner, x, y, s) for x in (x0, x1) for y in (y0, y1)]
    if swap:
        us = [(v, u) for (u, v) in us]
    lx = [1 - u for u, _ in us]
    ly = [v - 1 for _, v in us]
    # local edge angle psi: the frame map is a composition of reflections (+ a swap); the count of axis reflections in
    # (x -> 1-u, y -> v-1) is (corner in BR/TR) + (corner in TL/TR) + 1 (x = 1 - u) [+ 1 more for the swap parity]
    nref = (corner in ("BR", "TR")) + (corner in ("TL", "TR")) + 1 + (1 if swap else 0)
    c0, s_0 = _cs(bn.t0)
    c1, s_1 = _cs(bn.t1)
    if nref % 2 == 0:
        cpsi, spsi = (min(c0, c1), max(c0, c1)), (min(s_0, s_1), max(s_0, s_1))      # psi = theta
    else:
        cpsi, spsi = (min(s_0, s_1), max(s_0, s_1)), (min(c0, c1), max(c0, c1))      # psi = 90 - theta
    # q = c + (cos psi + sin psi, sin psi - cos psi)/2 ;  phi = 90 - psi: tan phi = cos psi / sin psi
    qy = (min(ly) + (spsi[0] - cpsi[1]) / 2, max(ly) + (spsi[1] - cpsi[0]) / 2)
    qx = (min(lx) + (cpsi[0] + spsi[0]) / 2, max(lx) + (cpsi[1] + spsi[1]) / 2)
    tanphi = (cpsi[0] / spsi[1] if spsi[1] > 0 else None, cpsi[1] / spsi[0] if spsi[0] > 0 else None)
    xr_hi = qx[1] - (qy[0] * tanphi[0] if (tanphi[0] is not None and qy[0] >= 0) else (qy[0] * tanphi[1] if tanphi[1] is not None else 0))
    deep_margin = (spsi[0] - cpsi[1]) - qy[1]           # > 0: q_y < cos phi - sin phi for every pose: full chord 1/cos phi
    phi_deg = (math.degrees(math.atan2(float(cpsi[0]), float(spsi[1]))), math.degrees(math.atan2(float(cpsi[1]), float(spsi[0]))))
    return dict(qy=[float(qy[0]), float(qy[1])], qx=[float(qx[0]), float(qx[1])], phi=[round(phi_deg[0], 3), round(phi_deg[1], 3)],
                xr_max=float(xr_hi), deep_margin=float(deep_margin), chord_min=float(1 / spsi[1]) if spsi[1] > 0 else None)


def seal_summary(pcs, corner, s, swap):
    st = [seal_piece(bn, r, corner, s, swap) for bn, r in pcs]
    return dict(n=len(st), qy=[min(d["qy"][0] for d in st), max(d["qy"][1] for d in st)],
                phi=[min(d["phi"][0] for d in st), max(d["phi"][1] for d in st)], xr_max=max(d["xr_max"] for d in st),
                deep_all=all(d["deep_margin"] > 0 for d in st), deep_margin_min=min(d["deep_margin"] for d in st),
                chord_min=min(d["chord_min"] for d in st if d["chord_min"] is not None))
