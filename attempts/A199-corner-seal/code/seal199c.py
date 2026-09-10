"""A199 -- the SEAL LEAF (docs/proofs/corner_seal.md section 3, Lemma NO-SECOND): a per-piece EXACT test that the free
meeter F of B (at every pose of the piece) leaves A with NO second meeter at all -- no unit square interior-disjoint
from F and the pin, inside the container, meets int A.  Then Theorem FC (two distinct non-pin meeters of A) is
violated and the page is DEAD.  The test uses F, the pin and the two walls only; the page enters through F's reach
region (pins' and H's K' as obstacles).

Per piece (centre rect x tilt sub-bin), in the corner frame (x = 1 - u, y = v - 1; exact rationals in t = tan(theta/2)):
    q = (q_x, q_y) the rightmost vertex, phi the leaning edge's angle from the vertical (cos phi = sin psi, sin phi = cos psi
    with psi the local edge angle), b = q - (sin phi, cos phi), l = b + (-cos phi, sin phi),
    y_bl = b_y + (b_x + 1) tan phi   (where F's lower-left edge crosses A's left side),  h = 1 + y_bl,  c = -1 - l_x.
  SEALED iff  (deep)  q_y < cos phi - sin phi,   (left)  l_x < -1,   (low)  y_bl < 0,
              (no-second)  c^2 (1 - h^2) > h^2 (1 + l_y)^2   [i.e. c sqrt(1-h^2)/h > 1 + l_y],
  every inequality taken at its worst end over the piece (sound).
The leaf bisects B's meeter window: a piece is DROPPED when provably dead (container clip, multibox dead test against
every role's K', A161's miss test on B's box), SEALED when the four inequalities hold, else SPLIT; at the depth cap
the unsealed survivors are the residue.  DEAD iff the residue is empty.
"""
import time
from fractions import Fraction as Fr

import seal199 as S
from seal199 import HALF, SQ2H_UP
import multibox as MB          # noqa: E402  READ-ONLY (via seal199's sys.path)
import chordlane as CLN        # noqa: E402  READ-ONLY


def _cs(t):
    return (1 - t * t) / (1 + t * t), 2 * t / (1 + t * t)


def piece_bounds(bn, r, corner, s, swap):
    """exact interval bounds over the piece of the local quantities; returns dict of Fractions (lo, hi)."""
    x0, x1, y0, y1 = r
    us = [S.to_uv(corner, x, y, s) for x in (x0, x1) for y in (y0, y1)]
    if swap:
        us = [(v, u) for (u, v) in us]
    lx = [1 - u for u, _ in us]
    ly = [v - 1 for _, v in us]
    nref = (corner in ("BR", "TR")) + (corner in ("TL", "TR")) + 1 + (1 if swap else 0)
    c0, s_0 = _cs(bn.t0)
    c1, s_1 = _cs(bn.t1)
    if nref % 2 == 0:
        cpsi, spsi = (min(c0, c1), max(c0, c1)), (min(s_0, s_1), max(s_0, s_1))
    else:
        cpsi, spsi = (min(s_0, s_1), max(s_0, s_1)), (min(c0, c1), max(c0, c1))
    cosphi, sinphi = spsi, cpsi                      # phi = 90 - psi
    qy = (min(ly) + (cosphi[0] - sinphi[1]) / 2, max(ly) + (cosphi[1] - sinphi[0]) / 2)
    qx = (min(lx) + (sinphi[0] + cosphi[0]) / 2, max(lx) + (sinphi[1] + cosphi[1]) / 2)
    return dict(qx=qx, qy=qy, cosphi=cosphi, sinphi=sinphi)


def sealed(bd):
    """the four inequalities at their worst ends.  -> (ok, detail)"""
    qx, qy, cph, sph = bd["qx"], bd["qy"], bd["cosphi"], bd["sinphi"]
    if qy[1] < 0:
        return "drop", "q_y < 0 at every pose: no pose meets int B clear of the pin (SEAL (b))"
    if qx[1] <= 0:
        return "drop", "q_x <= 0 at every pose: F's rightmost point is left of the pin's side, F misses int B"
    if cph[0] <= 0:
        return False, dict(fail="axis")
    tanphi = (sph[0] / cph[1], sph[1] / cph[0])
    if qy[1] - cph[0] < 0 and qx[0] > qy[1] * tanphi[1]:
        return "drop", "every pose dips (b_y < 0) and has x_r > 0: the leaning edge enters the pin (SEAL (b))"
    deep = (cph[0] - sph[1]) - qy[1]                    # > 0: every pose deep, hence dipping (b_y < -sin phi < 0)
    det = dict(deep=float(deep))
    if deep <= 0:
        return False, dict(det, fail="deep")
    qx_eff = min(qx[1], qy[1] * tanphi[1])              # SEAL (b): a dipping meeter has q_x <= q_y tan phi (sound tightening)
    lx_max = qx_eff - sph[0] - cph[0]                   # l_x = q_x - sin phi - cos phi   (< -1/cos phi automatically)
    ly_max = qy[1] - cph[0] + sph[1]                    # l_y = q_y - cos phi + sin phi
    by_max = qy[1] - cph[0]
    bx_max = qx_eff - sph[0]
    ybl_max = by_max + (bx_max + 1) * (tanphi[1] if bx_max + 1 >= 0 else tanphi[0])
    det.update(lx_max=float(lx_max), ly_max=float(ly_max), ybl_max=float(ybl_max))
    if lx_max >= -1:
        return False, dict(det, fail="left")
    if ybl_max >= 0:
        return False, dict(det, fail="low")
    c = -1 - lx_max
    h = 1 + ybl_max
    g = 1 + ly_max                                      # the height of l above the floor (> 0)
    # exact minimum of f(u) = u + c sqrt(1-u^2)/u over u = cos psi' in (0, h]: f decreases up to u* (u*^2 sqrt(1-u*^2) = c),
    # so min = f(h) when h^2 (1-h^2) <= c^2, else f(u*) = u*(2 - u*^2) >= sqrt(c) (2 - h^2).  Sealed iff min > g.
    if h * h * (1 - h * h) <= c * c:
        ok = (g <= h) or (c * c * (1 - h * h) > h * h * (g - h) * (g - h))
        det["margin"] = float(c * c * (1 - h * h) - h * h * (g - h) * (g - h)) if g > h else float(h - g)
    else:
        ok = c * (2 - h * h) ** 2 > g * g
        det["margin"] = float(c * (2 - h * h) ** 2 - g * g)
    if ok:
        return True, det
    return False, dict(det, fail="no-second")


def seal_leaf(win, obst, box, s, corner, swap, depth=12, nsub=4, max_pieces=4096, wall=None):
    """-> dict(dead, sealed=[...], residue=[...], dropped, n_tests, seconds, vol_sealed, vol_residue)."""
    t0 = time.time()
    stats = {"exact_calls": 0, "backoffs": 0, "passes": 0}
    R = tuple(Fr(v) for v in win)
    pieces = [(MB.Bin(a, b), R) for (a, b) in MB.sub_bins(Fr(0), Fr(1), nsub)]
    vol0 = sum(MB.rect_area(r) * (bn.t1 - bn.t0) for bn, r in pieces)
    sealed_p, dropped, n_tests = [], 0, 0
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
                dropped += 1
                continue
            n_tests += 1
            if CLN.box_misses_cell_exact(MB.piece_box(bn, cur)[0], box)[0]:
                dropped += 1
                continue
            ok, det = sealed(piece_bounds(bn, cur, corner, s, swap))
            n_tests += 1
            if ok == "drop":
                dropped += 1
                continue
            if ok:
                sealed_p.append((bn, cur, det))
                continue
            if d < depth and len(pieces) <= max_pieces and not (wall and time.time() - t0 > wall):
                nxt.extend(MB.split_piece(bn, cur))
            else:
                nxt.append((bn, cur, det))
        if d == depth or not nxt or (wall and time.time() - t0 > wall) or len(pieces) > max_pieces:
            pieces = nxt
            break
        pieces = nxt
    residue = [(p[0], p[1], p[2] if len(p) > 2 else None) for p in pieces]
    gbox = None
    if residue and all(isinstance(d_, dict) and d_.get("deep", 0) > 0 and d_.get("ybl_max", 1) < 0 for _, _, d_ in residue):
        # page-level fallback (Lemma NO-SECOND (ii) + the vertex localisation): a second meeter G has its rightmost
        # vertex in (-1, -1 + h/2] x [-1, y_bl) (corner frame), so its CENTRE lies in the box below; if no unit square
        # with centre there clears the pins' and H's K' and the container, there is no G.  h = max over the residue.
        h = max(1 + Fr(str(d_["ybl_max"])) for _, _, d_ in residue)
        lo_x, hi_x = Fr(-1) - SQ2H_UP, Fr(-1) + h / 2 - HALF
        lo_y, hi_y = Fr(-3, 2), Fr(-1) + h + HALF
        pts = []
        for xl in (lo_x, hi_x):
            for yl in (lo_y, hi_y):
                u, v = (1 - xl, yl + 1) if not swap else (yl + 1, 1 - xl)
                pts.append(S.to_xy(corner, u, v, s))
        gw = (max(HALF, min(p[0] for p in pts)), min(s - HALF, max(p[0] for p in pts)), max(HALF, min(p[1] for p in pts)), min(s - HALF, max(p[1] for p in pts)))
        if gw[0] < gw[1] and gw[2] < gw[3]:
            gp, gfrac, gt = S.reach(gw, obst, None, s, depth=10, nsub=nsub)
            gbox = dict(h=float(h), box=[float(v) for v in gw], n_pieces=len(gp), vol_frac=gfrac, n_tests=gt, empty=(len(gp) == 0))
        else:
            gbox = dict(h=float(h), box=[float(v) for v in gw], n_pieces=0, vol_frac=0.0, n_tests=0, empty=True, note="centre box outside the container")
        if gbox["empty"]:
            residue = []
    vol = lambda ps: float(sum(MB.rect_area(r) * (bn.t1 - bn.t0) for bn, r, *_ in ps) / vol0) if vol0 else 0.0
    fl = lambda ps: [[round(float(v), 5) for v in r] + [round(MB.deg_of_t(bn.t0), 2), round(MB.deg_of_t(bn.t1), 2)] for bn, r, *_ in ps]
    return dict(dead=(len(residue) == 0), n_sealed=len(sealed_p), n_residue=len(residue), dropped=dropped, n_tests=n_tests, gbox=gbox,
                vol_sealed=vol(sealed_p), vol_residue=vol(residue), seconds=round(time.time() - t0, 1),
                sealed_hull=S.hull([(bn, r) for bn, r, _ in sealed_p]) if sealed_p else None,
                sealed_margin_min=min(d_["margin"] for _, _, d_ in sealed_p) if sealed_p else None,
                residue=fl(residue)[:40], residue_hull=S.hull([(bn, r) for bn, r, _ in residue]) if residue else None,
                residue_fail={k: sum(1 for _, _, d_ in residue if isinstance(d_, dict) and d_.get("fail") == k) for k in ("deep", "left", "low", "no-second", "axis")})


def run_corner_leaf(pg, corner, Bcell, Acell, s, lam, nsub=4, refine=2, depth=12, log=print, wall=None):
    """the SEAL leaf on one (corner, orientation): base node, then the leaf on B's meeter window."""
    T0 = time.time()
    swap = Bcell.endswith("(1,0)")
    roles = S.page_roles(pg, s, lam)
    nd0, i0 = S.run_node(roles, s, nsub, refine)
    if i0["dead"]:
        return dict(verdict="DEAD", leaf="base node EmptyBox(%s)" % i0["dead"], base=i0, seconds=round(time.time() - T0, 1))
    cB, iB, jB = S.cell_of(Bcell)
    boxB = S.cell_box(cB, iB, jB, s, lam)
    obst = [nd0.boxes[k].obstacle("poly") for k in roles]
    r = seal_leaf(S.window(boxB, s), obst, boxB, s, cB, swap, depth=depth, nsub=nsub, wall=wall)
    log("    %s/%s: leaf %s -- sealed %d pieces (vol %.5f, margin >= %s), residue %d (vol %.6f, fails %s), dropped %d, %d tests, G-box %s, %.0fs" % (
        corner, Bcell, "DEAD" if r["dead"] else "alive", r["n_sealed"], r["vol_sealed"], r["sealed_margin_min"], r["n_residue"],
        r["vol_residue"], r["residue_fail"], r["dropped"], r["n_tests"], (("EMPTY" if r["gbox"]["empty"] else "%d pieces" % r["gbox"]["n_pieces"]) + " h=%.3f" % r["gbox"]["h"]) if r["gbox"] else "-", r["seconds"]))
    return dict(verdict="DEAD" if r["dead"] else "ALIVE", leaf=("SEAL leaf at %s: every free meeter of %s is sealed (Lemma NO-SECOND): "
                                                              "%s has no second meeter" % (corner, Bcell, Acell)) if r["dead"] else None,
                base=dict(kept=i0["kept"], seconds=i0["seconds"]), leaf_result=r, seconds=round(time.time() - T0, 1))


def run_page_leaf(page, s=None, lam=None, log=print, stop_first=True, **kw):
    s = S.S0 if s is None else s
    lam = Fr(1) if lam is None else lam
    pg = S.load_page(page)
    corners = S.seal_corners(pg)
    out = dict(page=page, cls=pg["cls"], record=pg["record"], s=float(s), lam=float(lam), pad0=float(S.pad(0, lam)),
               mode="leaf", corners=[c for c in corners], runs=[], verdict="ALIVE" if corners else "N/A", kill=None)
    if not corners:
        out["leaf"] = "no pinned corner with both neighbours forced"
        return out
    T0 = time.time()
    for (c, B, A) in corners:
        log("  %s: corner %s, F meets %s, A = %s (leaf)" % (page, c, B, A))
        r = run_corner_leaf(pg, c, B, A, s, lam, log=log, **kw)
        r["corner"], r["B"], r["A"] = c, B, A
        out["runs"].append(r)
        if r["verdict"] == "DEAD":
            out["verdict"], out["kill"], out["leaf"] = "DEAD", dict(corner=c, B=B, A=A), r["leaf"]
            if stop_first:
                break
    out["seconds"] = round(time.time() - T0, 1)
    return out
