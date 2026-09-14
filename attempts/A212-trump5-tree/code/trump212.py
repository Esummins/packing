"""A212 -- the Trump image, the containment GATE and the TUBE LEAF (notes/trump5_tree.md s.0-s.3).

The image: A22's jam z-hat (trump11_exact.json, 60 digits -> exact rationals) EMBEDDED at s0 (squares 2 and 5 on
their slots), its eight D4 images (rotation: tilt kept; reflection: theta -> 90 deg - theta, t -> (1 - t)/(1 + t)),
tilts read modulo 90 deg (an upright square has the two representatives t = 0 and t = 1).
gate(pg): the first g in D4 with an injective assignment of the node's named squares (pins, H, F_i) to the image's
squares satisfying pins / pieces / named slots / NS misses (exact rationals, margins IN FAVOUR of containment).
tube(pg, g, assign): every piece of every named role inside the tube box (r_c' = r_c - 2 (s0 - s-hat), r_theta)
about its assigned square -- Lemma TUBE-LEAF; aligned_split(...) the cut at the tube wall (s.3)."""
import json
import math
import os
import time
from fractions import Fraction as Fr

import poly204 as P

FP, MB = P.FP, P.MB
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
EXACT = os.path.join(ROOT, "attempts", "A03-upper-reconstruct", "trump11_exact.json")
TUBE_CERT = os.path.join(ROOT, "certs", "tube_scale_T5.71e-2_window.json")
S0 = MB.S_RAT
EPS = Fr(1, 10 ** 9)                   # the gate's margin (in favour of containment)
PIN_TOL = Fr(1, 10 ** 6)               # the pins: the R-family shift + rounding
TILT_MARGIN = 1e-9                     # float atan / tan margin on the tilt window (r_theta = 2.1e-3 >> this)
_IMG = {}


def _fr(s):
    return Fr(str(s))


def base():
    """z-hat embedded at s0: list of dict(i, cx, cy, t (tan theta/2), c, s (cos, sin theta), theta) -- exact rationals."""
    if "base" in _IMG:
        return _IMG["base"]
    d = json.load(open(EXACT, encoding="utf-8"))
    th, t, c, s = _fr(d["theta_rad"]), _fr(d["t_tan_half_theta"]), _fr(d["cos_theta"]), _fr(d["sin_theta"])
    out = []
    for i, q in enumerate(d["squares"]):
        cx, cy = _fr(q["cx"]), _fr(q["cy"])
        tilted = abs(_fr(q["theta"])) > Fr(1, 1000)
        if i == 2:
            cx, cy = S0 - Fr(1, 2), Fr(1, 2)
        if i == 5:
            cx, cy = S0 - Fr(1, 2), S0 - Fr(1, 2)
        out.append(dict(i=i, cx=cx, cy=cy, t=(t if tilted else Fr(0)), c=(c if tilted else Fr(1)), s=(s if tilted else Fr(0)),
                        theta=(th if tilted else Fr(0)), tilted=tilted))
    _IMG["base"] = out
    _IMG["shat"] = _fr(d["s"])
    return out


def shat():
    base()
    return _IMG["shat"]


D4 = [("id", lambda x, y: (x, y), False), ("rot90", lambda x, y: (S0 - y, x), False), ("rot180", lambda x, y: (S0 - x, S0 - y), False),
      ("rot270", lambda x, y: (y, S0 - x), False), ("refl_x", lambda x, y: (S0 - x, y), True), ("refl_y", lambda x, y: (x, S0 - y), True),
      ("refl_d", lambda x, y: (y, x), True), ("refl_ad", lambda x, y: (S0 - y, S0 - x), True)]


def images():
    """the eight D4 images: name -> list of squares dict(i, cx, cy, reps=[(t, theta, cos, sin)...], upright)."""
    if "images" in _IMG:
        return _IMG["images"]
    out = {}
    for name, f, refl in D4:
        sq = []
        for q in base():
            cx, cy = f(q["cx"], q["cy"])
            if refl and q["tilted"]:
                t = (1 - q["t"]) / (1 + q["t"])                      # theta -> 90 - theta
                reps = [(t, Fr(math.pi / 2) - q["theta"], q["s"], q["c"])]
            elif q["tilted"]:
                reps = [(q["t"], q["theta"], q["c"], q["s"])]
            else:
                reps = [(Fr(0), Fr(0), Fr(1), Fr(0)), (Fr(1), Fr(math.pi / 2), Fr(0), Fr(1))]
            sq.append(dict(i=q["i"], cx=cx, cy=cy, reps=reps, upright=not q["tilted"]))
        out[name] = sq
    _IMG["images"] = out
    return out


# ------------------------------------------------------------------ exact geometry
def in_piece(q, rect, bn):
    x0, x1, y0, y1 = rect
    if not (x0 - EPS <= q["cx"] <= x1 + EPS and y0 - EPS <= q["cy"] <= y1 + EPS):
        return False
    return any(bn.t0 - EPS <= t <= bn.t1 + EPS for (t, _th, _c, _s) in q["reps"])


def in_pin(q, box):
    x0, x1, y0, y1 = (Fr(v) for v in box[:4])
    return q["upright"] and x0 - PIN_TOL <= q["cx"] <= x1 + PIN_TOL and y0 - PIN_TOL <= q["cy"] <= y1 + PIN_TOL


def meets_open_box(q, wb, eps):
    """the closed unit square at q meets the open box wb (X0, X1, Y0, Y1): separating axes, exact rationals; eps > 0 leans to
    'meets', eps < 0 to 'misses'."""
    t, th, c, s = q["reps"][0]
    r = (abs(c) + abs(s)) / 2
    X0, X1, Y0, Y1 = (Fr(v) for v in wb)
    if not (max(q["cx"] - r, X0) < min(q["cx"] + r, X1) + eps and max(q["cy"] - r, Y0) < min(q["cy"] + r, Y1) + eps):
        return False
    corners = [(X0, Y0), (X1, Y0), (X0, Y1), (X1, Y1)]
    for (ux, uy) in ((c, s), (-s, c)):
        pc = q["cx"] * ux + q["cy"] * uy
        pb = [bx * ux + by * uy for bx, by in corners]
        if not (max(pc - Fr(1, 2), min(pb)) < min(pc + Fr(1, 2), max(pb)) + eps):
            return False
    return True


# ------------------------------------------------------------------ the gate
def box_pieces(box):
    """a role that carries no pieces yet (before its first cascade) is constrained by its hull BOX: rect x the tilt interval as one piece."""
    x0, x1, y0, y1, d0, d1 = box
    t0 = Fr(round(math.tan(math.radians(float(d0)) / 2) * 10 ** 12) - 1) / 10 ** 12 if float(d0) > 0 else Fr(0)
    t1 = Fr(round(math.tan(math.radians(float(d1)) / 2) * 10 ** 12) + 1) / 10 ** 12 if float(d1) < 90 else Fr(1)
    return [(MB.Bin(max(Fr(0), t0), min(Fr(1), t1)), (Fr(x0), Fr(x1), Fr(y0), Fr(y1)))]


def _assign(pg, sq, pins_used, roles, k, cur, checks):
    if k == len(roles):
        return dict(cur)
    r = roles[k]
    pcs = pg.pieces.get(r) or box_pieces(pg.roles[r])
    for q in sq:
        if q["i"] in pins_used or q["i"] in cur.values():
            continue
        if not any(in_piece(q, rect, bn) for bn, rect in pcs):
            continue
        slots = set(pg.forced_H) if r == pg.H else set(pg.role_slots.get(r, ()))
        if any(not meets_open_box(q, pg.item[p]["wb"], EPS) for p in slots):
            checks.append(dict(role=r, square=q["i"], fail="named slot not met", slots=sorted(slots)))
            continue
        miss = set(pg.miss.get(r, ()))
        if any(meets_open_box(q, pg.item[p]["wb"], -EPS) for p in miss):
            checks.append(dict(role=r, square=q["i"], fail="NS miss violated", slots=sorted(miss)))
            continue
        cur[r] = q["i"]
        res = _assign(pg, sq, pins_used, roles, k + 1, cur, checks)
        if res is not None:
            return res
        del cur[r]
    return None


def gate(pg):
    """-> dict(contains, g, assignment {role: square index}, pins {P: square}, checks, seconds): the first D4 image the node contains."""
    t0 = time.time()
    roles = [r for r in sorted(pg.roles) if not r.startswith("P")]             # H (H0, H1), every instantiated role; pieceless -> its box
    out = dict(contains=False, g=None, assignment=None, pins=None, checks=[], seconds=0.0, n_roles=len(roles))
    for name, sq in images().items():
        pins, used, ok = {}, set(), True
        for pn, box in sorted(pg.pins.items()):
            hit = next((q for q in sq if q["i"] not in used and in_pin(q, box)), None)
            if hit is None:
                ok = False
                break
            pins[pn], used = hit["i"], used | {hit["i"]}
        if not ok:
            out["checks"].append(dict(g=name, fail="pins"))
            continue
        checks = []
        a = _assign(pg, sq, used, roles, 0, {}, checks)
        out["checks"].append(dict(g=name, fail=None if a is not None else "no assignment", detail=checks[:6]))
        if a is not None:
            out.update(contains=True, g=name, assignment=a, pins=pins)
            break
    out["seconds"] = round(time.time() - t0, 3)
    return out


# ------------------------------------------------------------------ the tube leaf
def radii():
    c = json.load(open(TUBE_CERT, encoding="utf-8"))
    rc, rt, T = Fr(c["r_c"]), Fr(c["r_theta"]), Fr(c["T"])
    return dict(cert=os.path.relpath(TUBE_CERT, ROOT).replace("\\", "/"), r_c=rc, r_theta=rt, T=T, r_c_eff=rc - 2 * (S0 - shat()), r_s=Fr(c["r_s"]))


def theta_window(q, rt):
    """the admissible t-intervals (floats, shrunk by TILT_MARGIN) about each tilt representative of the image square."""
    out = []
    for (t, th, _c, _s) in q["reps"]:
        lo, hi = float(th) - float(rt), float(th) + float(rt)
        out.append((math.tan(max(lo, -math.pi / 2 + 1e-9) / 2) + TILT_MARGIN, math.tan(min(hi, math.pi / 2 - 1e-9) / 2) - TILT_MARGIN, float(th)))
    return out


def tube(pg, g, assign, pins):
    """-> dict(fits, radii, roles {role: dict(square, fits, dx, dy, dt)}, worst): Lemma TUBE-LEAF's containment, exact on the centres."""
    R = radii()
    rc, rt = R["r_c_eff"] - EPS, R["r_theta"]
    sq = {q["i"]: q for q in images()[g]}
    rep, fits_all, worst = {}, True, None
    for pn, box in sorted(pg.pins.items()):
        q = sq[pins[pn]]
        x0, x1, y0, y1 = (Fr(v) for v in box[:4])
        ok = q["cx"] - rc <= x0 and x1 <= q["cx"] + rc and q["cy"] - rc <= y0 and y1 <= q["cy"] + rc
        rep[pn] = dict(square=q["i"], fits=bool(ok), dx=float(max(x1 - q["cx"], q["cx"] - x0)), dy=float(max(y1 - q["cy"], q["cy"] - y0)), dt=0.0)
        fits_all &= ok
    for r, i in assign.items():
        q = sq[i]
        pcs = pg.pieces.get(r) or []
        x0, x1, y0, y1, t0, t1 = FP.pieces_hull(pcs)
        okc = q["cx"] - rc <= x0 and x1 <= q["cx"] + rc and q["cy"] - rc <= y0 and y1 <= q["cy"] + rc
        win = theta_window(q, rt)
        okt = any(all(lo <= float(bn.t0) and float(bn.t1) <= hi for bn, _ in pcs) for lo, hi, _th in win)
        dx, dy = float(max(x1 - q["cx"], q["cx"] - x0)), float(max(y1 - q["cy"], q["cy"] - y0))
        dt = min(max(abs(MB.deg_of_t(t0) - math.degrees(th)), abs(MB.deg_of_t(t1) - math.degrees(th))) for _lo, _hi, th in win)
        rep[r] = dict(square=i, fits=bool(okc and okt), fits_centre=bool(okc), fits_tilt=bool(okt), dx=dx, dy=dy, dt_deg=dt, n_pieces=len(pcs),
                      hull=[float(v) for v in (x0, x1, y0, y1)] + [MB.deg_of_t(t0), MB.deg_of_t(t1)])
        fits_all &= (okc and okt)
        ex = max(dx / float(rc), dy / float(rc), math.radians(dt) / float(rt))
        if worst is None or ex > worst[1]:
            worst = (r, ex)
    return dict(fits=bool(fits_all), radii={k: (str(v) if isinstance(v, Fr) else v) for k, v in R.items()}, r_c_eff_float=float(R["r_c_eff"]),
                roles=rep, worst=worst, g=g, assignment=dict(assign), pins=dict(pins))


def aligned_split(pg, g, assign):
    """the cut at the tube wall (s.3): the (role, dim, m, side-with-the-image) of the largest excess over the tube box, or None."""
    R = radii()
    rc, rt = R["r_c_eff"] - EPS, R["r_theta"]
    sq = {q["i"]: q for q in images()[g]}
    best = None
    for r, i in assign.items():
        q = sq[i]
        pcs = pg.pieces.get(r) or []
        if not pcs:
            continue
        x0, x1, y0, y1, t0, t1 = FP.pieces_hull(pcs)
        for dim, (u0, u1, lo, hi, scale) in (("x", (x0, x1, q["cx"] - rc, q["cx"] + rc, float(rc))), ("y", (y0, y1, q["cy"] - rc, q["cy"] + rc, float(rc)))):
            for m, side, ex in ((hi, "lo", float(u1 - hi) / scale), (lo, "hi", float(lo - u0) / scale)):
                if ex > 0 and u0 < m < u1 and (best is None or ex > best["excess"]):
                    best = dict(role=r, dim=dim, m=m, side=side, excess=round(ex, 4), square=i)
        win = theta_window(q, rt)
        lo, hi, th = min(win, key=lambda w: abs(w[2] - MB.deg_of_t((t0 + t1) / 2) * math.pi / 180))
        for mf, side, ex in ((hi, "lo", (float(t1) - hi) / float(rt)), (lo, "hi", (lo - float(t0)) / float(rt))):
            m = Fr(round(mf * 10 ** 12)) / 10 ** 12
            if ex > 0 and t0 < m < t1 and (best is None or ex > best["excess"]):
                best = dict(role=r, dim="t", m=m, side=side, excess=round(ex, 4), square=i)
    return best


if __name__ == "__main__":
    for g, sq in images().items():
        print(g, [(q["i"], round(float(q["cx"]), 4), round(float(q["cy"]), 4), [round(float(t), 4) for t, *_ in q["reps"]]) for q in sq[:3]])
    print(radii())
