"""A125 -- the local certificate around A122's S33 minimum (and S38 as a second data point).

New shadows for A116's Theorem-LOCAL machinery.  Everything under A116 / A119 / A122 is imported
READ-ONLY; this module only adds

  * the two minima as (s*, poses) in their CLASS FRAME (A122 results/exact.json, 50-digit
    Lagrange solutions, read as floats):
        S33min  class k6_07, frame = identity      (A122 notes/method.md sec 7)
        S38min  class k6_21, frame = the D4 element `diag`  (x, y, t) -> (y, x, -t)
  * the class pin sets k6_07 / k6_21 (A53 results/name_to_slots.json),
  * `build_bodies125`, A116's `build_bodies` for these shadows: L = the full load-bearing set,
    i.e. every NON-PIN square of the minimum (all eleven squares are load-bearing at S33min --
    A122 rigidity.json, no rattler -- so L = f0..f4 and P = the six slot cells).

No file outside attempts/A125-s33-local-cert is written by this module.
"""
from __future__ import annotations

import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
A116C = os.path.abspath(os.path.join(HERE, "..", "..", "A116-local-selection-tree", "code"))
A119C = os.path.abspath(os.path.join(HERE, "..", "..", "A119-local-cert-lean", "code"))
for p in (A119C, A116C):
    if p not in sys.path:
        sys.path.insert(0, p)

import a116lib as A      # noqa: E402  (imports blas1 before numpy: BLAS pinned to one thread)
import a119lib as L119   # noqa: E402  (KRows / RecTree: cell sharing + dual inheritance)

BASE = os.path.abspath(os.path.join(HERE, ".."))
RES = os.path.join(BASE, "results")
CERTS = os.path.join(BASE, "certs")
LOGS = os.path.join(BASE, "logs")
NOTES = os.path.join(BASE, "notes")
for d in (RES, CERTS, LOGS, NOTES):
    os.makedirs(d, exist_ok=True)

S0 = A.S0
SHAT = A.SHAT
S_LO = A.S_LO
S_HI = A.S_HI_DEFAULT
PIN_SLACK = A.PIN_SLACK

# ------------------------------------------------------------------ A122's exact minima
# results/exact.json `configuration` (50-digit strings, read as floats); name order = A122's.
S33_S = 3.9169308657139204
S33_CFG = {
    "f0":      (1.5,                1.9539595258991065,  3.953409291468777e-80),
    "f1":      (2.4351211119357155, 2.7132653842629697,  40.000496775347926),
    "f2":      (1.4743845784616623, 3.2125143049967435,  40.000496775347926),
    "f3":      (2.4813793557540142, 1.2557334538187392,  51.44852867103262),
    "f4":      (3.210293887431955,  1.9933960574381582,  47.08870461508636),
    "BL(0,0)": (0.5, 0.5, 0.0),
    "BL(0,1)": (0.5, 1.5, 0.0),
    "BL(0,2)": (0.5, 2.5, 0.0),
    "BL(1,0)": (1.5, 0.5, 0.0),
    "BR(0,0)": (3.4169308657139204, 0.5, 0.0),
    "TR(0,0)": (3.4169308657139204, 3.4169308657139204, 0.0),
}
S33_SLOTS = ("BL(0,0)", "BL(0,1)", "BL(0,2)", "BL(1,0)", "BR(0,0)", "TR(0,0)")

S38_S = 3.9289146852229777
S38_CFG = {
    "f0":      (1.3042029878146988, 2.4164954654484383, 41.75406267727139),
    "f1":      (0.7059723612698249, 3.2229423239531525, 41.75406267727139),
    "f2":      (2.0098917623815757, 1.7059723612698248, 41.75406267727139),
    "f3":      (2.046436683385486,  3.2229423239531525, 41.75406267727139),
    "f4":      (2.684421519409369,  2.4519825187216067, 41.75406267727139),
    "BL(0,0)": (0.5, 0.5, 0.0),
    "BL(0,1)": (0.5, 1.5, 0.0),
    "BL(1,0)": (1.5, 0.5, 0.0),
    "BR(0,0)": (3.4289146852229777, 0.5, 0.0),
    "BR(0,1)": (3.4289146852229777, 1.5, 0.0),
    "TR(0,0)": (3.4289146852229777, 3.4289146852229777, 0.0),
}
S38_SLOTS = ("BL(0,0)", "BL(0,1)", "BL(1,0)", "BR(0,0)", "BR(0,1)", "TR(0,0)")

# A53 name_to_slots.json (at s0):
#   k6_07 = (0.5,0.5) (0.5,1.5) (0.5,2.5) (1.5,0.5) (s0-.5,0.5) (s0-.5,s0-.5)
#   k6_21 = (0.5,0.5) (0.5,1.5) (0.5,s0-.5) (1.5,0.5) (1.5,s0-.5) (s0-.5,s0-.5)
CLASS_PINS = {
    "k6_07": ("BL(0,0)", "BL(0,1)", "BL(0,2)", "BL(1,0)", "BR(0,0)", "TR(0,0)"),
    "k6_21": ("BL(0,0)", "BL(0,1)", "TL(0,0)", "BL(1,0)", "TL(1,0)", "TR(0,0)"),
}


def _diag(s):
    """the D4 element `diag` at side s (A107 shadowlib / a111lib.d4_ops)."""
    return lambda x, y, t: (y, x, -t)


def _tmod(t_deg):
    """tilt reduced into [0, 90): a multiple of 90 deg is a symmetry of the unit square."""
    return t_deg % 90.0


SHADOWS = {
    "S33": dict(cls="k6_07", frame="e",    s=S33_S, cfg=S33_CFG, slots=S33_SLOTS,
                free=("f0", "f1", "f2", "f3", "f4")),
    "S38": dict(cls="k6_21", frame="diag", s=S38_S, cfg=S38_CFG, slots=S38_SLOTS,
                free=("f0", "f1", "f2", "f3", "f4")),
}


def shadow_frame(tag):
    """(s*, {name: (x, y, theta_rad)}) of the minimum IN ITS CLASS FRAME, at its own side s*.

    The frame map is applied at s = s*; slot squares land exactly on the class's slot cells at
    s* (checked by `selfcheck`), and their names are re-read from the image position.
    """
    S = SHADOWS[tag]
    s = S["s"]
    out = {}
    if S["frame"] == "e":
        for n, (x, y, t) in S["cfg"].items():
            out[n] = (x, y, math.radians(_tmod(t)))
        slots = list(S["slots"])
    elif S["frame"] == "diag":
        f = _diag(s)
        pins = list(CLASS_PINS[S["cls"]])
        # image of the slot squares, matched to the class's pin cells at s*
        img = {}
        for n, (x, y, t) in S["cfg"].items():
            X, Y, T = f(x, y, t)
            img[n] = (X, Y, math.radians(_tmod(T)))
        out = {}
        used = set()
        for n in S["free"]:
            out[n] = img[n]
        for n in S["slots"]:
            X, Y, T = img[n]
            hit = None
            for p in pins:
                if p in used:
                    continue
                px, py = A.slot_xy(p, s)
                if abs(X - px) < 1e-9 and abs(Y - py) < 1e-9:
                    hit = p
                    break
            if hit is None:
                raise ValueError("slot %s -> (%.6f, %.6f) is not a %s cell" % (n, X, Y, S["cls"]))
            used.add(hit)
            out[hit] = (X, Y, 0.0)
        slots = pins
    else:
        raise ValueError(S["frame"])
    return s, out, slots, list(S["free"])


def anchored125(tag, anchor_side):
    """A116's anchoring in the class frame: free squares dilated by anchor_side/s*, slot squares
    on their slot cells at anchor_side."""
    s_sh, P, slots, free = shadow_frame(tag)
    lam = anchor_side / s_sh
    out = {}
    for n, (x, y, t) in P.items():
        if n in slots:
            sx, sy = A.slot_xy(n, anchor_side)
            out[n] = (sx, sy, 0.0)
        else:
            out[n] = (x * lam, y * lam, t)
    return s_sh, out, slots, free


def build_bodies125(tag, r, rho_deg, anchor_side=S0, pin_slack=PIN_SLACK, loadbearing=None,
                    tilt_floor_deg=None, tilt_ceil_deg=None):
    """A116 `build_bodies` for S33 / S38: the class pins as slack cores, one FREE box (centre
    [c +- r]^2, tilt [theta +- rho]) per load-bearing NON-PIN square.  Default L = every free
    square of the minimum (all eleven squares are load-bearing at S33min; no rattler)."""
    S = SHADOWS[tag]
    cls = S["cls"]
    s_sh, P, slots, free = anchored125(tag, anchor_side)
    pins = list(CLASS_PINS[cls])
    lb = list(loadbearing if loadbearing is not None else free)
    bodies, nv = [], 1
    rho = math.radians(rho_deg)
    for n in lb:
        x, y, t = P[n]
        t0, t1 = t - rho, t + rho
        if n not in slots:
            if tilt_floor_deg is not None:
                t0 = max(t0, math.radians(tilt_floor_deg))
            if tilt_ceil_deg is not None:
                t1 = min(t1, math.radians(tilt_ceil_deg))
        if t1 < t0:
            raise ValueError("empty tilt box for %s" % n)
        bodies.append(A.Body(n, "free", x0=x - r, x1=x + r, y0=y - r, y1=y + r, t0=t0, t1=t1,
                             vi=nv, anchor=(x, y, t)))
        nv += 2
    for p in pins:
        ax, ay = A.slot_affine(p)
        px, py = A.slot_xy(p, anchor_side)
        bodies.append(A.Body(p, "pin", ax=ax, ay=ay, hh=pin_slack, vi=nv, anchor=(px, py, 0.0)))
        nv += 2
    for bd in bodies:
        if bd.kind == "free":
            bd.ti = nv
            nv += 1
    return bodies, nv, s_sh, P


# ------------------------------------------------------------------ self-check
def selfcheck(tag, verbose=True):
    """The class-frame poses are a packing at s*, its slot squares sit on the class's cells, and
    its side (worst wall / worst pair gap) reproduces A122's s*."""
    s, P, slots, free = shadow_frame(tag)
    cfg = dict(P)
    wp, ww = A.check_packing(s, cfg)
    cells_ok = all(abs(P[n][0] - A.slot_xy(n, s)[0]) < 1e-9 and abs(P[n][1] - A.slot_xy(n, s)[1]) < 1e-9
                   for n in slots)
    got = sorted(slots)
    want = sorted(CLASS_PINS[SHADOWS[tag]["cls"]])
    if verbose:
        print("%s  s*=%.13f  worst pair %.3e  worst wall %.3e  cells_ok %s  pins %s == %s : %s"
              % (tag, s, wp, ww, cells_ok, got, want, got == want))
    return dict(tag=tag, s_star=s, worst_pair=wp, worst_wall=ww, cells_ok=bool(cells_ok),
                pins_match=bool(got == want), slots=got, free=list(free))


if __name__ == "__main__":
    for t in ("S33", "S38"):
        selfcheck(t)
