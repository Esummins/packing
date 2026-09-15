"""A227 -- Lemma EPS (docs/proofs/lemma_eps.md): the WEDGES a near-simple square F leaves uncovered in its cell C,
as exact rational polygons over F's pose box, and Rule EPS: a second meeter of C (Theorem FC demands two distinct
non-pin meeters of a forced cell) must have an interior point in a TARGET of (F, C) -- the bounding rectangle of a
free-side wedge polygon (EPS-3/4) or a corner END ZONE of a pin- or wall-backed side (EPS-5, GATE).  A role that
misses every target EXACTLY (A161's separating-axis test taken in t, snap224.misses_t) is STRUCK; an anonymous
square is struck unless an alive option cell of the slot lies within 1/sqrt2 (l-inf) of a target (EPS-6).
No candidate left -> DEAD by FC+EPS.  Otherwise the survivors and the targets they reach are the Rule NS geometry.

READ-ONLY on A224 (snap224: misses_t, near, slot_cell, roles_of, n_anon), A171 (multibox), A57 (caselp).
Flag A227_EPS=1 (default OFF).  Every statement here is n-general: one cell, one near-simple square, its neighbours.
"""
import os
from fractions import Fraction as Fr

import multibox as MB                                         # noqa: E402  READ-ONLY (A171): t_lo, t_hi, cos_sin_t
import snap224 as S                                           # noqa: E402  READ-ONLY (A224): the exact miss test

ON = (os.environ.get("A227_EPS") or "").strip().lower() in ("1", "on", "yes")
MAX_TESTS = int(os.environ.get("A227_EPS_MAXTESTS") or 20000)   # SAT tests per (F, M) pair before "no claim"
HALF = Fr(1, 2)
SQ2I_HI = Fr(7072, 10000)                                     # > 1/sqrt2: the anonymous l-inf reach (EPS-6)
SIDES = ("L", "R", "B", "T")


# --------------------------------------------------------------------------- exact convex polygons
def clip(poly, a, b, k):
    """poly (list of (x, y) Fractions, convex, ccw or cw) cut by the CLOSED half-plane a x + b y >= k."""
    out = []
    n = len(poly)
    for i in range(n):
        P, Q = poly[i], poly[(i + 1) % n]
        fp, fq = a * P[0] + b * P[1] - k, a * Q[0] + b * Q[1] - k
        if fp >= 0:
            out.append(P)
        if (fp < 0 < fq) or (fq < 0 < fp):
            lam = fp / (fp - fq)
            out.append((P[0] + lam * (Q[0] - P[0]), P[1] + lam * (Q[1] - P[1])))
    return out


def area2(poly):
    return abs(sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
                   for i in range(len(poly)))) if len(poly) >= 3 else Fr(0)


def bbox(poly):
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    return (min(xs), max(xs), min(ys), max(ys))


# --------------------------------------------------------------------------- EPS-4: the wedge polygons of a box
def wedge_polys(box, C):
    """box = (x0, x1, y0, y1, t0, t1) exact, t in [0, 1]; C = (X0, X1, Y0, Y1).  The union over the box of C \\ F is
    inside the union of the returned polygons (Lemma EPS-4: sup over the box of (p - z).nu at the box corner
    minimising z.nu, cos/sin relaxed to their bin intervals, one convex polygon per sign quadrant of the offset)."""
    x0, x1, y0, y1, t0, t1 = (Fr(v) for v in box)
    X0, X1, Y0, Y1 = (Fr(v) for v in C)
    c0, s0 = MB.cos_sin_t(t0)
    c1, s1 = MB.cos_sin_t(t1)                                # c0 >= c1 >= 0, 0 <= s0 <= s1
    CI, SI = (c1, c0), (s0, s1)
    rect = [(X0, Y0), (X1, Y0), (X1, Y1), (X0, Y1)]
    # (name, sa, xa, coeff interval of A = sa (x - xa), sb, yb, coeff interval of B = sb (y - yb))
    fams = (("e", 1, x0, CI, 1, y0, SI), ("-e", -1, x1, CI, -1, y1, SI),
            ("e^", -1, x1, SI, 1, y0, CI), ("-e^", 1, x0, SI, -1, y1, CI))
    out = []
    for nm, sa, xa, (pa_lo, pa_hi), sb, yb, (pb_lo, pb_hi) in fams:
        for qa in (1, -1):                                   # sign of A: A >= 0 uses pa_hi, A <= 0 uses pa_lo
            for qb in (1, -1):
                pa = pa_hi if qa > 0 else pa_lo
                pb = pb_hi if qb > 0 else pb_lo
                poly = clip(rect, qa * sa, 0, qa * sa * xa)           # qa * sa (x - xa) >= 0
                poly = clip(poly, 0, qb * sb, qb * sb * yb)           # qb * sb (y - yb) >= 0
                poly = clip(poly, pa * sa, pb * sb, HALF + pa * sa * xa + pb * sb * yb)   # V+ >= 1/2
                if area2(poly) > 0:
                    out.append(dict(nu=nm, quad=(qa, qb), poly=poly, bbox=bbox(poly)))
    return out


def sides_of(bb, C):
    X0, X1, Y0, Y1 = C
    return tuple(s for s, hit in (("L", bb[0] == X0), ("R", bb[1] == X1), ("B", bb[2] == Y0), ("T", bb[3] == Y1)) if hit)


def assign(polys, C):
    """assign each polygon to the side it is THIN along (minimum depth among the sides its bbox touches); w_sigma =
    the largest depth of the polygons assigned to sigma.  The strips S_sigma of depth w_sigma then cover every
    polygon (EPS-5's R and K'_rect)."""
    X0, X1, Y0, Y1 = C
    w = dict(L=Fr(0), R=Fr(0), B=Fr(0), T=Fr(0))
    for P in polys:
        bb = P["bbox"]
        ds = {s: {"L": bb[1] - X0, "R": X1 - bb[0], "B": bb[3] - Y0, "T": Y1 - bb[2]}[s] for s in sides_of(bb, C)}
        P["side"] = min(ds, key=ds.get) if ds else None
        if ds:
            w[P["side"]] = max(w[P["side"]], ds[P["side"]])
    return w


# --------------------------------------------------------------------------- EPS-5: the backing of the sides
def pin_core(b):
    """the axis-aligned square every pose of a PIN box [x0,x1,y0,y1,d0,d1] contains: half-width h = 1/(2(cos+sin))
    at the bin's largest t (h decreasing on [0, 45 deg]); (x1 - h, x0 + h) x (y1 - h, y0 + h)."""
    t = MB.t_hi(float(b[5]))
    if t > Fr(414, 1000):                                    # beyond 45 deg: no claim
        return None
    c, s = MB.cos_sin_t(t)
    h = 1 / (2 * (c + s))
    x0, x1, y0, y1 = (Fr(float(v)) for v in b[:4])
    return (x1 - h, x0 + h, y1 - h, y0 + h)


GAP_MAX = Fr(1, 1000)


def backing(pg, C):
    """per side: ('wall', None, None, g), ('pin', name, blocked span along the side, g) or ('free',).  g >= 0 is the
    GAP between the side's line and the obstacle (the wall, or the pin core's facing edge; at most GAP_MAX): the
    GATE region is extended outward by g so that its outer side lies on the obstacle.  A pin backs a side when its
    core lies outside the cell and its facing edge is within GAP_MAX of the side's line (it may poke in)."""
    X0, X1, Y0, Y1 = C
    s = Fr(pg.s)
    out = {}
    for sd in SIDES:
        line = {"L": X0, "R": X1, "B": Y0, "T": Y1}[sd]
        wg = {"L": line, "R": s - line, "B": line, "T": s - line}[sd]      # outward distance to the wall
        if wg <= GAP_MAX:
            out[sd] = ("wall", None, None, max(Fr(0), wg))
            continue
        best = None
        for k in sorted(pg.roles):
            if not k.startswith("P"):
                continue
            K = pin_core(pg.roles[k])
            if K is None:
                continue
            near, far = {"L": (K[1], K[0]), "R": (K[0], K[1]), "B": (K[3], K[2]), "T": (K[2], K[3])}[sd]
            gap = (line - near) if sd in "LB" else (near - line)
            outside = (far < line) if sd in "LB" else (far > line)
            if gap > GAP_MAX or not outside:
                continue
            ext = (Y0, Y1) if sd in "LR" else (X0, X1)           # the side's own extent
            sp = (K[2], K[3]) if sd in "LR" else (K[0], K[1])
            span = (max(sp[0], ext[0]), min(sp[1], ext[1]))     # the blocked part of the side
            if span[1] - span[0] <= 0:
                continue
            if best is None or (span[1] - span[0]) > (best[2][1] - best[2][0]):
                best = ("pin", k, span, max(Fr(0), gap))
        out[sd] = best or ("free",)
    return out


def targets(box, C, back):
    """the target rectangles of (F-box, C): free-side polygon bboxes + corner zones of the backed sides.  When the
    GATE hypotheses fail (strip area >= 1, or no core rectangle left) every side is taken FREE."""
    X0, X1, Y0, Y1 = C
    polys = wedge_polys(box, C)
    w = assign(polys, C)
    g = {s: (back[s][3] if back[s][0] != "free" else Fr(0)) for s in SIDES}
    strips = sum(((w[s] + g[s]) * ((X1 - X0) if s in "BT" else (Y1 - Y0)) for s in SIDES if back[s][0] != "free"), Fr(0))
    gate_ok = strips < 1 and (X0 + w["L"] < X1 - w["R"]) and (Y0 + w["B"] < Y1 - w["T"])
    bk = {s: back[s] if gate_ok else ("free",) for s in SIDES}
    info = dict(n_polys=len(polys), depths={k: round(float(v), 6) for k, v in w.items()}, gate=gate_ok,
                backed=[s for s in SIDES if bk[s][0] != "free"])
    tg = []
    for P in polys:
        if P["side"] is None or bk[P["side"]][0] == "free":
            tg.append(("wedge-%s-%s" % (P["nu"], P["side"] or "?"), P["bbox"]))
    # corner zones: corner (sx, sy), adjacent sides sx in {L, R}, sy in {B, T}
    for sx, cx in (("L", X0), ("R", X1)):
        for sy, cy in (("B", Y0), ("T", Y1)):
            bx, by = bk[sx], bk[sy]
            gx = Fr(0)                                       # gap sliver of side sx at this corner (along y)
            if bx[0] == "pin":
                gx = max(Fr(0), (bx[2][0] - cy) if sy == "B" else (cy - bx[2][1]))
            gy = Fr(0)                                       # gap sliver of side sy at this corner (along x)
            if by[0] == "pin":
                gy = max(Fr(0), (by[2][0] - cx) if sx == "L" else (cx - by[2][1]))
            ex = (bx[0] != "free" and w[sx] > 0 and (by[0] == "free" or gx > 0 or gy > 0)) or                  (by[0] != "free" and w[sy] > 0 and (bx[0] == "free" or gx > 0 or gy > 0))
            if not ex:
                continue
            dx, dy = max(w[sx], gy), max(w[sy], gx)
            ox, oy = (g[sx] if bx[0] != "free" else Fr(0)), (g[sy] if by[0] != "free" else Fr(0))
            rx = (cx - ox, min(X1, cx + dx)) if sx == "L" else (max(X0, cx - dx), cx + ox)
            ry = (cy - oy, min(Y1, cy + dy)) if sy == "B" else (max(Y0, cy - dy), cy + oy)
            tg.append(("zone-%s%s" % (sx, sy), (rx[0], rx[1], ry[0], ry[1])))
    return tg, info


# --------------------------------------------------------------------------- the strike
class Budget:
    def __init__(self, n):
        self.left = n


def misses_all(pg, k, tg, bud):
    """role k misses every target rectangle, for every pose it still has (hull box, then pieces); -> (True, None)
    or (False, the first target some pose may reach) or (None, 'budget')."""
    b = pg.roles[k]
    hull = (Fr(float(b[0])), Fr(float(b[1])), Fr(float(b[2])), Fr(float(b[3])), MB.t_lo(b[4]), MB.t_hi(b[5]))
    pcs = pg.pieces.get(k) or []
    boxes = [hull] + [(Fr(r[0]), Fr(r[1]), Fr(r[2]), Fr(r[3]), bn.t0, bn.t1) for bn, r in pcs]
    for nm, T in tg:
        bud.left -= 1
        if bud.left < 0:
            return None, "budget"
        if S.misses_t(*hull, T)[0]:
            continue
        if not pcs:
            return False, nm
        for bx in boxes[1:]:
            bud.left -= 1
            if bud.left < 0:
                return None, "budget"
            if not S.misses_t(*bx, T)[0]:
                return False, nm
    return True, None


def strike(pg, F, M, C, back):
    """M is STRUCK iff it misses every target of (F's hull box, C), or -- failing that -- for EVERY piece of F it
    misses every target of (that piece, C).  Returns dict(struck, via, reach)."""
    bud = Budget(MAX_TESTS)
    tg, info = targets(hull_box(pg, F), C, back)
    ok, why = misses_all(pg, M, tg, bud)
    if ok:
        return dict(struck=True, via="hull", n_targets=len(tg))
    if ok is None:
        return dict(struck=False, via="budget", reach=None)
    pcs = pg.pieces.get(F) or []
    if not pcs:
        return dict(struck=False, via="hull", reach=why)
    for bn, r in pcs:
        tgp, _i = targets((Fr(r[0]), Fr(r[1]), Fr(r[2]), Fr(r[3]), bn.t0, bn.t1), C, back)
        ok2, why2 = misses_all(pg, M, tgp, bud)
        if not ok2:
            return dict(struck=False, via="pieces" if ok2 is False else "budget", reach=why2 if ok2 is False else why)
    return dict(struck=True, via="pieces", n_pieces=len(pcs))


def hull_box(pg, k):
    b = pg.roles[k]
    return (Fr(float(b[0])), Fr(float(b[1])), Fr(float(b[2])), Fr(float(b[3])), MB.t_lo(b[4]), MB.t_hi(b[5]))


def anon_survivors(pg, p, tg):
    """alive option cells of slot p whose centre rectangle lies within 1/sqrt2 (l-inf) of some target: the only
    cells an ANONYMOUS meeter of a target can have its centre in (EPS-6).  None = no claim (no fresh table)."""
    if S.n_anon(pg) <= 0:
        return []
    if not getattr(pg, "rounds", None) or pg.rounds[-1].get("instantiated"):
        return None
    keep = []
    for c in sorted((pg.rounds[-1].get("single") or {}).get(p, {})):
        r = [Fr(str(v)) for v in pg.cells[int(c)]["rect"]]
        for _nm, T in tg:
            if not (r[1] < T[0] - SQ2I_HI or r[0] > T[1] + SQ2I_HI or r[3] < T[2] - SQ2I_HI or r[2] > T[3] + SQ2I_HI):
                keep.append(int(c))
                break
    return keep


def evaluate(pg, label, log=None):
    """-> None (no candidate) or a record; verdict DEAD by FC+EPS when some near-simple (F, p) leaves no possible
    second meeter of p, else None with the survivors and the targets they reach."""
    cands = S.candidates(pg)
    if not cands:
        return None
    rec = dict(label=label, n_cands=len(cands), n_anon=S.n_anon(pg), verdict=None, cands=[])
    for c in cands:
        F, p = c["role"], c["slot"]
        C = S.slot_cell(pg, p)
        back = backing(pg, C)
        tg, info = targets(hull_box(pg, F), C, back)
        row = dict(role=F, slot=p, dist=c["dist"], tilt=c["tilt"], backing={s: back[s][0] for s in SIDES}, gate=info["gate"],
                   backed=info["backed"],
                   depths=info["depths"], targets=[(nm, [str(v) for v in T]) for nm, T in tg], struck=[], survivors={})
        for M in S.roles_of(pg):
            if M == F:
                continue
            st = strike(pg, F, M, C, back)
            if st["struck"]:
                row["struck"].append(M)
            else:
                row["survivors"][M] = dict(reach=st.get("reach"), via=st["via"])
        an = anon_survivors(pg, p, tg)
        row["anon_cells"] = an
        row["dead"] = (not row["survivors"]) and an == []
        rec["cands"].append(row)
        if row["dead"] and rec["verdict"] is None:
            rec["verdict"] = "DEAD"
            rec["kill"] = row
            rec["leaf"] = ("FC+EPS at %s: %s is near-simple in the forced cell %s (dist %s, tilt %s); Theorem FC demands a "
                           "second non-pin meeter of B_p+, which must meet a wedge target of (%s, %s) (Lemma EPS-3/4/5: "
                           "%s); every other role misses every target exactly (%s) and no anonymous cell is within "
                           "1/sqrt2 of one -- no second meeter exists" % (
                               label, F, p, c["dist"], c["tilt"], F, p, "; ".join("%s=[%s]" % (nm, ",".join(str(round(float(v), 5)) for v in T)) for nm, T in tg),
                               ", ".join(row["struck"])))
            rec["verifier"] = "[T: Lemma EPS + Theorem FC + A161 exact miss certificates; docs/proofs/lemma_eps.md]"
    if log and rec["verdict"]:
        log("   FC+EPS at %s: %s at %s -- DEAD" % (label, rec["kill"]["role"], rec["kill"]["slot"]))
    return rec
