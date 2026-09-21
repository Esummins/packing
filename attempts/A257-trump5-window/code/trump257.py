"""A257 -- the SLOT-RAY tube containment, stated exactly as Lemma TUBE-KILL states it (A256
notes/trump5_closure.md s.3, hypothesis (ii)) -- and why A256's `trump256.tube` cannot be used unchanged at a
window pad with SLACK pins.

Lemma TUBE-KILL (ii): "there are g in D4 and an injective assignment of N's named FREE roles to the free squares of
g.z-hat such that every piece of every named free role lies inside the box of half-widths (r_c - 2(s0 - s-hat),
r_theta) about its assigned square, **the pins being matched to g.z-hat's pins corner by corner**."

The box test is on the FREE roles only, and the proof says why (s.3, and contraction_tube.md s.4.1): a PINNED centre
coordinate of the packing P at side m is alpha + beta m EXACTLY -- P's class pins are corner squares of the container
at side m -- so its pull-back is z-hat_i - t v_i with **w_i = 0**, whatever the node's pin BOX looks like at s0.  The
node's pin box enters the lemma only through hypothesis (iv) (Lemma SEAM's (K) condition on delta_pin): F = Delta_lam
P has its pin squares up to (lam - 1)|alpha| off slots(s0), and it must still meet the node's delta_pin-slack core.

`trump256.tube` was written for A212's PAD-0 leaf on the SCALE ray, where the pins do NOT ride the ray, and it
therefore demands the pin box itself inside r_c (1.6e-3).  At a window pad with the slack pins the window needs
(delta_pin = 1e-2, A256 s.4 / contraction_tube.md s.4.4 item 1) the pin box is +-1e-2 and that test can NEVER pass:
A256's implementation is STRICTER than the lemma it implements, and strictly so on exactly the population the window
row is about.  This module implements (ii) as stated: the box test on the free roles (A256's code, reused verbatim
through `TR.tube`'s arithmetic) and, on the pins, the corner-by-corner match plus the exact slot data (alpha, beta)
the seam condition is computed from.  Nothing is weakened: the free-role test is A256's, and the pin test is a
STRENGTHENING of "matched corner by corner" (the box must be centred on that corner's slot at s0 and be no wider
than the record's own delta_pin)."""
import math
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import trump256 as TR                                          # noqa: E402  READ-ONLY (A256)

S0, FP, MB = TR.S0, TR.FP, TR.MB
SLOT_TOL = Fr(1, 10 ** 6)              # the R-family shift (s0 - s-hat = 4.1e-7) + the 1e-50 rounding of z0
A_TRUMP5 = Fr(3, 2)                    # Lemma SEAM's A for trump5 (max |alpha| over the five pins)


def slot_of(c):
    """the corner slot (alpha, beta) of an s0 coordinate c: c = alpha + beta s0, beta in {0, 1} (ray256.pin_alpha)."""
    return (c, Fr(0)) if c * 2 <= S0 else (c - S0, Fr(1))


def pin_match(box, q, dpin):
    """Lemma TUBE-KILL (ii) on ONE pin: the image square q is upright and the node's pin box is the delta_pin box
    about the SAME corner slot -- centre within SLOT_TOL of q's centre, half-widths <= delta_pin.
    -> dict(ok, alpha, beta, dc, halfwidth, ...) with everything exact."""
    x0, x1, y0, y1 = (Fr(str(v)) for v in box[:4])
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    hx, hy = (x1 - x0) / 2, (y1 - y0) / 2
    d = Fr(str(dpin))
    ax, bx = slot_of(q["cx"])
    ay, by = slot_of(q["cy"])
    dc = max(abs(cx - q["cx"]), abs(cy - q["cy"]))
    ok = bool(q["upright"] and dc <= SLOT_TOL and hx <= d and hy <= d and max(abs(ax), abs(ay)) <= A_TRUMP5)
    return dict(square=q["i"], ok=ok, upright=bool(q["upright"]), dc=float(dc), half=[float(hx), float(hy)],
                alpha=[str(ax), str(ay)], beta=[str(bx), str(by)], max_abs_alpha=float(max(abs(ax), abs(ay))),
                A=str(A_TRUMP5), dpin=float(d),
                why=None if ok else ("pin box not the delta_pin box of image square %d's corner slot "
                                     "(upright %s, centre offset %.3g > %.3g, half-widths %s > delta_pin %g, "
                                     "|alpha| %.3f > A %s)" % (q["i"], q["upright"], float(dc), float(SLOT_TOL),
                                                               [float(hx), float(hy)], float(d),
                                                               float(max(abs(ax), abs(ay))), A_TRUMP5)))


def theta_window(q, rt):
    """A256's `trump256.theta_window` with the two ENDPOINT representatives handled exactly (a fix, not a widening).

    A212 s.0: tilts are read modulo 90 deg and the machinery keeps t = tan(theta/2) in [0, 1], so an UPRIGHT image
    square has the two representatives t = 0 and t = 1 and they are the SAME orientation.  A256 clamps the window to
    theta in [-pi/2 + 1e-9, pi/2 - 1e-9] before taking the tangent, so the 90 deg representative gets the window
    [tan((90 - r_theta)/2), 1 - 5e-10]: a piece bin that reaches t = 1 -- the commonest shape for an upright role --
    then fails the containment although every pose in it is within r_theta of 90 deg == 0 deg, and the aligned cut
    computed from that window puts the image on the WRONG side (measured here: cut 15 of the g1 spine).  The window
    is therefore closed at the endpoints: t_hi = 1 when theta + r_theta >= 90 deg, t_lo = 0 when theta - r_theta <= 0.
    -> [(t_lo, t_hi, theta_rad, t_rep)] with t_lo/t_hi/t_rep floats in [0, 1]."""
    out = []
    for (t, th, _c, _s) in q["reps"]:
        lo, hi = float(th) - float(rt), float(th) + float(rt)
        tl = 0.0 if lo <= 0 else math.tan(lo / 2) + TR.TILT_MARGIN
        thh = 1.0 if hi >= math.pi / 2 else math.tan(hi / 2) - TR.TILT_MARGIN
        out.append((max(0.0, tl), min(1.0, thh), float(th), float(t)))
    return out


def tube_slot(pg, g, assign, pins, dpin):
    """Lemma TUBE-KILL (ii) on the whole node, SLOT ray: A256's box test on every named free role (identical
    arithmetic to trump256.tube) + `pin_match` on every pin.  -> dict(fits, radii, roles, pins, worst, ...)."""
    R = TR.radii("slot")
    rc, rt = R["r_c_eff"] - TR.EPS, R["r_theta"]
    sq = {q["i"]: q for q in TR.images()[g]}
    rep, prep, fits, worst = {}, {}, True, None
    for pn, box in sorted(pg.pins.items()):
        m = pin_match(box, sq[pins[pn]], dpin)
        prep[pn] = m
        fits &= m["ok"]
    for r, i in assign.items():
        q = sq[i]
        pcs = pg.pieces.get(r) or []
        if not pcs:                                            # a role with no pieces yet constrains nothing: not fitted
            rep[r] = dict(square=i, fits=False, why="the role carries no pieces yet (before its first cascade)")
            fits = False
            continue
        x0, x1, y0, y1, t0, t1 = FP.pieces_hull(pcs)
        okc = q["cx"] - rc <= x0 and x1 <= q["cx"] + rc and q["cy"] - rc <= y0 and y1 <= q["cy"] + rc
        win = theta_window(q, rt)
        okt = any(all(lo <= float(bn.t0) and float(bn.t1) <= hi for bn, _ in pcs) for lo, hi, _th, _tr in win)
        dx, dy = float(max(x1 - q["cx"], q["cx"] - x0)), float(max(y1 - q["cy"], q["cy"] - y0))
        dt = min(max(abs(MB.deg_of_t(t0) - math.degrees(th)), abs(MB.deg_of_t(t1) - math.degrees(th)))
                 for _lo, _hi, th, _tr in win)
        rep[r] = dict(square=i, fits=bool(okc and okt), fits_centre=bool(okc), fits_tilt=bool(okt), dx=dx, dy=dy,
                      dt_deg=dt, n_pieces=len(pcs),
                      hull=[float(v) for v in (x0, x1, y0, y1)] + [MB.deg_of_t(t0), MB.deg_of_t(t1)])
        fits &= (okc and okt)
        ex = max(dx / float(rc), dy / float(rc), math.radians(dt) / float(rt))
        if worst is None or ex > worst[1]:
            worst = (r, round(ex, 3))
    return dict(fits=bool(fits), ray="slot", radii={k: (str(v) if isinstance(v, Fr) else v) for k, v in R.items()},
                r_c_eff_float=float(R["r_c_eff"]), roles=rep, pins=prep, worst=worst, g=g,
                assignment=dict(assign), pin_assignment=dict(pins),
                clause="Lemma TUBE-KILL (ii) as stated (A256 notes/trump5_closure.md s.3): the tube box on the named "
                       "FREE roles, the pins matched corner by corner (w_pin = 0 on the slot ray, "
                       "contraction_tube.md s.4.1) -- see code/trump257.py for why A256's trump256.tube, which also "
                       "boxes the pins, is stricter than the lemma and cannot pass at delta_pin = 1e-2.")


def aligned_split(pg, g, assign):
    """The cut at the tube wall (A212 notes/trump5_tree.md s.3) on the SLOT-ray radii, with the IMAGE-SIDE GUARD.

    A256's `trump256.aligned_split` names the side the image is on from the geometry of the wall alone; with the
    clamped 90 deg window above that name can be wrong, and the spine then descends into the child the gate rejects
    (the image is still in the OTHER child -- Lemma ROLE-SPLIT is exhaustive either way, so nothing unsound
    happens; the descent just stops).  Here every candidate is checked against the image square's OWN coordinate:
    a cut is kept only when the image lies strictly on the named side.  Steering only -- soundness is Lemma
    ROLE-SPLIT's (any m strictly inside the hull gives two exhaustive children)."""
    R = TR.radii("slot")
    rc, rt = R["r_c_eff"] - TR.EPS, R["r_theta"]
    sq = {q["i"]: q for q in TR.images()[g]}
    best = None
    for r, i in assign.items():
        q = sq[i]
        pcs = pg.pieces.get(r) or []
        if not pcs:
            continue
        x0, x1, y0, y1, t0, t1 = FP.pieces_hull(pcs)
        for dim, (u0, u1, c) in (("x", (x0, x1, q["cx"])), ("y", (y0, y1, q["cy"]))):
            for m, side, ex in ((c + rc, "lo", float(u1 - c - rc) / float(rc)), (c - rc, "hi", float(c - rc - u0) / float(rc))):
                if ex > 0 and u0 < m < u1 and (side == "lo") == (c < m) and (best is None or ex > best["excess"]):
                    best = dict(role=r, dim=dim, m=m, side=side, excess=round(ex, 4), square=i)
        win = theta_window(q, rt)
        tm = float(t0 + t1) / 2
        lo, hi, _th, ti = min(win, key=lambda w: abs((w[0] + w[1]) / 2 - tm))
        for mf, side, ex in ((hi, "lo", (float(t1) - hi) / float(rt)), (lo, "hi", (lo - float(t0)) / float(rt))):
            # round the wall INTO the window: side "lo" keeps t <= m and needs m <= hi (floor), side "hi" keeps
            # t >= m and needs m >= lo (ceil).  Plain rounding overshoots by up to 5e-13 and the child then misses
            # the tilt window by that much -- measured: the g1 spine stalled at dt = r_theta exactly, 14 cuts in.
            m = (Fr(math.floor(mf * 10 ** 12), 10 ** 12) if side == "lo" else Fr(math.ceil(mf * 10 ** 12), 10 ** 12))
            if ex > 0 and t0 < m < t1 and (side == "lo") == (ti < float(m)) and (best is None or ex > best["excess"]):
                best = dict(role=r, dim="t", m=m, side=side, excess=round(ex, 4), square=i)
    return best
