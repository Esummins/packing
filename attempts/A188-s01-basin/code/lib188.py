"""A188 -- the S01 ("room at side 4") basin: shared helpers.  READ-ONLY on every other attempt.

The object.  S01 is A107's side-4.000 family: the LP support of a page flows to a configuration in
which FOUR squares (pins included) are crossed by one axis-parallel line through their unit-chord
bands, so the chord sum is >= 4 > s0 (A144's Lemma LINE-1/LINE-2, `attempts/A144-guard-lines`).
The basin of that family is therefore a LINE object, not a Hessian ball: any configuration with
(4 - k) non-pin squares whose centres lie within w of a line that already carries k full pin chords
has side >= 4, whatever the x-coordinates and tilts of those squares.

  gamma(theta) = (cos + sin)/2 - sin cos   is the half-height of the unit-chord band of a square at
  tilt theta (chord(v) >= 1  iff  |v| <= gamma(theta)); gamma is minimal at 45 deg, (sqrt2 - 1)/2 =
  0.2071..., so W_ANY = 207/1000 is a tilt-free band half-width.

Every number below is exact (Fraction) and every chord bound is A144's `minchord_box` (imported
read-only), which is the corpus's own certified lower bound of |l n Q| over a parameter box.
"""
from __future__ import annotations

import json, math, os, sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
ATT = os.path.join(ROOT, "attempts")
RES = os.path.join(BASE, "results")
NOTES = os.path.join(BASE, "notes")
LOGS = os.path.join(BASE, "logs")
CERTS = os.path.join(BASE, "certs")
for _d in (RES, NOTES, LOGS, CERTS):
    os.makedirs(_d, exist_ok=True)

A144C = os.path.join(ATT, "A144-guard-lines", "code")
if A144C not in sys.path:
    sys.path.insert(0, A144C)
import guardline as GL                       # noqa: E402  (A144, read-only; pulls caselp/lpbox)
from caselp import Box                       # noqa: E402  (A57, read-only)

S_RAT = Fr(969271, 250000)
S0 = float(S_RAT)
PIN_H = Fr(1, 100) / GL.SQRT2_LO             # a rational UPPER bound of delta/sqrt2 (safe: wider core)
W_ANY = Fr(207, 1000)                        # < (sqrt2 - 1)/2: tilt-free unit-chord band half-width
CLASS_PINS = {
    "k5_11": ("BL(0,0)", "BL(0,1)", "TL(0,0)", "BL(1,0)", "BR(0,0)"),
    "k5_16": ("BL(0,0)", "BL(0,1)", "TL(0,0)", "BR(0,0)", "TR(0,0)"),
    "trump5": ("BL(0,0)", "BL(1,0)", "BL(0,1)", "BR(0,0)", "TR(0,0)"),
}


def frame_of(cls):
    return "trump5" if cls.startswith("trump5") else cls


def slot_xy(name, s=S_RAT):
    corner, ij = name[:2], name[3:-1].split(",")
    i, j = int(ij[0]), int(ij[1])
    x = Fr(1, 2) + i if corner in ("BL", "TL") else s - Fr(1, 2) - i
    y = Fr(1, 2) + j if corner in ("BL", "BR") else s - Fr(1, 2) - j
    return x, y


def pin_box(name, s=S_RAT, h=PIN_H):
    x, y = slot_xy(name, s)
    return Box(float(x - h), float(x + h), float(y - h), float(y + h), 0.0, 0.0)


def gamma(theta_deg):
    t = math.radians(theta_deg % 90.0)
    t = min(t, math.pi / 2 - t)
    return 0.5 * (math.cos(t) + math.sin(t)) - math.sin(t) * math.cos(t)


def band_box(orient, c, w, th0=0.0, th1=90.0, s=S_RAT):
    """the free box of one band member: centre within w of the line, ANY position along it."""
    c, w = Fr(c), Fr(w)
    if orient == "h":
        return Box(0.0, float(s), float(c - w), float(c + w), th0, th1)
    return Box(float(c - w), float(c + w), 0.0, float(s), th0, th1)


def minchord(box, orient, c):
    return GL.minchord_box(box, GL.Line(orient, Fr(c)))["lo"]


def band_halfwidth(th0, th1, c=Fr(3, 2), tol=Fr(1, 20000)):
    """largest w (to tol, exact and SAFE: the returned w satisfies minchord >= 1) such that every
    pose in [0,s] x [c-w, c+w] x [th0, th1] has chord >= 1 on the line y = c."""
    lo, hi = Fr(0), Fr(1, 2)
    if minchord(band_box("h", c, lo, th0, th1), "h", c) < 1:
        return Fr(0)
    while hi - lo > tol:
        m = (lo + hi) / 2
        if minchord(band_box("h", c, m, th0, th1), "h", c) >= 1:
            lo = m
        else:
            hi = m
    return lo


def pin_full_range(name, orient, s=S_RAT, h=PIN_H):
    """the c-interval on which the pin's whole slack core has chord exactly 1 (axis-aligned:
    |v| <= 1/2 for every centre of the core)."""
    x, y = slot_xy(name, s)
    p = y if orient == "h" else x
    return (p - (Fr(1, 2) - h), p + (Fr(1, 2) - h))


def pin_lines(pins, s=S_RAT):
    """{(orient, group key): (names, c_lo, c_hi)} -- the axis-parallel lines through the frame's
    pin rows and columns on which every named pin carries a full unit chord."""
    out = {}
    for orient in ("h", "v"):
        groups = {}
        for p in pins:
            x, y = slot_xy(p, s)
            key = y if orient == "h" else x
            groups.setdefault(key, []).append(p)
        for key, names in groups.items():
            los, his = zip(*(pin_full_range(n, orient, s) for n in names))
            out[(orient, str(key))] = (sorted(names), max(los), min(his))
    return out


def record_pins_and_box(rec):
    """(pins as Box list, conditioned Box list) from a stored A57/A60 node record."""
    boxes = [Box.from_json(b) for b in rec["hyp"]["boxes"]]
    pins = [b for b in boxes if abs(b.th1 - b.th0) <= 1e-12]
    free = [b for b in boxes if abs(b.th1 - b.th0) > 1e-12]
    return pins, free


def pin_name_of(box, s=S_RAT):
    """match a record's zero-tilt core to a slot name (centre within 0.02)."""
    cx, cy = 0.5 * (box.x0 + box.x1), 0.5 * (box.y0 + box.y1)
    best = None
    for corner in ("BL", "BR", "TL", "TR"):
        for i in range(3):
            for j in range(3):
                n = "%s(%d,%d)" % (corner, i, j)
                x, y = slot_xy(n, s)
                d = max(abs(float(x) - cx), abs(float(y) - cy))
                if best is None or d < best[0]:
                    best = (d, n)
    return best[1] if best and best[0] < 0.02 else None


def chord_of_pose(x, y, theta_rad, orient, c):
    """|l n Q| of a unit square at pose (x, y, theta) on the line `orient` = c (A144's (CH))."""
    v = float(c) - (y if orient == "h" else x)
    return GL.chord_float(0.5, theta_rad, v)


def load_pages():
    d = json.load(open(os.path.join(ATT, "A187-basin-map", "results", "basin_map187.json"),
                       encoding="utf-8"))
    return d["pages"]


def load_extract():
    ex = {}
    for f in ("extract.json", "extract_k0.json"):
        p = os.path.join(ATT, "A107-shadow-gallery", "results", f)
        if os.path.exists(p):
            for n in json.load(open(p, encoding="utf-8"))["nodes"]:
                ex.setdefault(n["nid"], n)
    return ex


def load_gallery():
    gal = {}
    for which in ("a57v4", "k0v4"):
        for e in json.load(open(os.path.join(ATT, "A148-gallery-v4", "results",
                                             "gallery148_%s.json" % which), encoding="utf-8")):
            gal[e["id"]] = e
    return gal


def load_record(rel):
    p = os.path.join(ROOT, rel.replace("\\", os.sep))
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None


def fr(x):
    return str(Fr(x))
