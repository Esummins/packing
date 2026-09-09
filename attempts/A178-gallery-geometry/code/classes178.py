"""A178 -- the FORCED cells of a pinned class, computed (not copied) from A53's class table and
the A56/A61/A114/A146 scoreboard.  READ-ONLY on every other attempt.

A cell (corner c, offsets i, j) of a Young class S is FORCED when Lemma SLOT-CROWD
(docs/proofs/slot_crowds.md section 2) applies: the cell is Young-completable (its predecessors
(i-1, j), (i, j-1) are pins of S or the corner's walls), UNCLIPPED (no pin's open square meets the
open slot box), not itself a pin, and its extension class S + {slot} is FULL on the window in the
scoreboard.  Then every packing of class S at a side m of the window has >= 2 NON-pin squares
meeting the open slot box B_p(m); docs/proofs/forced_corners.md transfers that to the s0 page.
A corner cell (i = j = 0) is a forced CORNER.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
S0 = 969271 / 250000
LAM_MAX = S0 / 3.82
SQ2H = 0.7071067811865476

NAME_TO_SLOTS = os.path.join(ROOT, "attempts", "A53-simple-strata", "results", "name_to_slots.json")
SCOREBOARD = os.path.join(ROOT, "attempts", "A56-sparametric", "results", "scoreboard.json")
CORNERS = ("BL", "BR", "TR", "TL")


def frame_to_xy(corner, u, v, s=S0):
    """corner-frame (u, v) = distances from the corner's two walls -> container (x, y)."""
    x = u if corner in ("BL", "TL") else s - u
    y = v if corner in ("BL", "BR") else s - v
    return x, y


def xy_to_frame(corner, x, y, s=S0):
    u = x if corner in ("BL", "TL") else s - x
    v = y if corner in ("BL", "BR") else s - y
    return u, v


def d4_images(pts, s=S0):
    out = []
    for f in (lambda x, y: (x, y), lambda x, y: (s - x, y), lambda x, y: (x, s - y),
              lambda x, y: (s - x, s - y), lambda x, y: (y, x), lambda x, y: (s - y, x),
              lambda x, y: (y, s - x), lambda x, y: (s - y, s - x)):
        out.append(tuple(sorted((round(a, 5), round(b, 5)) for a, b in (f(x, y) for x, y in pts))))
    return out


_N2S = None
_SB = None


def name_to_slots():
    global _N2S
    if _N2S is None:
        _N2S = {k: tuple(sorted((round(a, 5), round(b, 5)) for a, b in v))
                for k, v in json.load(open(NAME_TO_SLOTS, encoding="utf-8")).items()}
    return _N2S


def class_of(pts):
    """the census name of a pin set (any D4 image), or None."""
    tab = name_to_slots()
    inv = {v: k for k, v in tab.items()}
    for im in d4_images(pts):
        if im in inv:
            return inv[im]
    return None


def scoreboard_status(name):
    global _SB
    if _SB is None:
        _SB = json.load(open(SCOREBOARD, encoding="utf-8"))["rows"]
    r = _SB.get(name)
    if r is None:
        return None
    st = str(r.get("status", ""))
    return dict(result=r.get("result"), status=st, full=st.startswith("FULL [191/50, 969271/250000]"))


def pins_of(cls):
    return [tuple(p) for p in json.load(open(NAME_TO_SLOTS, encoding="utf-8"))[cls]]


def slot_centre(corner, i, j, s=S0):
    return frame_to_xy(corner, i + 0.5, j + 0.5, s)


def is_pin(pins, pt, eps=1e-6):
    return any(abs(pt[0] - p[0]) < eps and abs(pt[1] - p[1]) < eps for p in pins)


def clipped_by_pin(pins, corner, i, j, s=S0, eps=1e-9):
    """the OPEN slot box meets some pin's OPEN square (the clip census of slot_crowds section 1.2)."""
    cx, cy = slot_centre(corner, i, j, s)
    for px, py in pins:
        if abs(px - cx) < 1 - eps and abs(py - cy) < 1 - eps:
            return True
    return False


def forced_cells(cls, s=S0, max_off=2):
    """[dict(cell, corner, i, j, extension, status, usable, is_corner)] over all completable
    unclipped non-pin cells with offsets <= max_off."""
    pins = pins_of(cls)
    out = []
    for c in CORNERS:
        for i in range(max_off + 1):
            for j in range(max_off + 1):
                if i > 0 and j > 0:
                    pass
                pt = slot_centre(c, i, j, s)
                if is_pin(pins, pt):
                    continue
                pred_ok = True
                if i >= 1 and not is_pin(pins, slot_centre(c, i - 1, j, s)):
                    pred_ok = False
                if j >= 1 and not is_pin(pins, slot_centre(c, i, j - 1, s)):
                    pred_ok = False
                if not pred_ok:
                    continue
                if clipped_by_pin(pins, c, i, j, s):
                    continue
                ext = class_of(pins + [pt])
                st = scoreboard_status(ext) if ext else None
                out.append(dict(cell="%s(%d,%d)" % (c, i, j), corner=c, i=i, j=j, extension=ext,
                                status=(st or {}).get("status"), usable=bool(st and st["full"]),
                                is_corner=(i == 0 and j == 0)))
    return out


def pad(i):
    """the dilation pad on the far side of a cell at offset i (forced_corners.md section 2):
    (lambda_max - 1)(i + 1 + 1/sqrt2).  i = 0 gives K0-WIDEN's w = 0.025509."""
    return (LAM_MAX - 1) * (i + 1 + SQ2H)


def widened_box(corner, i, j, s=S0):
    """container-frame (X0, X1, Y0, Y1) of the widened open slot box (i, i+1+pad_i) x (j, j+1+pad_j)."""
    u0, u1, v0, v1 = i, i + 1 + pad(i), j, j + 1 + pad(j)
    xa, ya = frame_to_xy(corner, u0, v0, s)
    xb, yb = frame_to_xy(corner, u1, v1, s)
    return (min(xa, xb), max(xa, xb), min(ya, yb), max(ya, yb))


def meeter_window(corner, i, j, s=S0):
    """container-frame centre window of every unit square inside [0,s]^2 that can meet the
    widened open box: |c - p|_inf <= 1/sqrt2 for some box point p, and c in [1/2, s-1/2]^2."""
    X0, X1, Y0, Y1 = widened_box(corner, i, j, s)
    return (max(0.5, X0 - SQ2H), min(s - 0.5, X1 + SQ2H), max(0.5, Y0 - SQ2H), min(s - 0.5, Y1 + SQ2H))


def a2_cells(corner, s=S0, c=None):
    """Lemma A2 (sideband.md): the four cells of the 2x2 grid at threshold c = 1 + pad(0) in the
    corner frame, as container-frame centre rectangles restricted to the corner's meeter window.
    Names: SW (both < c), SE (u >= c, v < c), NW, NE."""
    c = 1 + pad(0) if c is None else c
    hi = c + SQ2H
    cells = {"SW": (0.5, c, 0.5, c), "SE": (c, hi, 0.5, c), "NW": (0.5, c, c, hi), "NE": (c, hi, c, hi)}
    out = {}
    for k, (u0, u1, v0, v1) in cells.items():
        xa, ya = frame_to_xy(corner, u0, v0, s)
        xb, yb = frame_to_xy(corner, u1, v1, s)
        out[k] = (min(xa, xb), max(xa, xb), min(ya, yb), max(ya, yb))
    return out


def box_dist(A, B):
    """Euclidean distance between two closed axis boxes (X0,X1,Y0,Y1)."""
    dx = max(0.0, A[0] - B[1], B[0] - A[1])
    dy = max(0.0, A[2] - B[3], B[2] - A[3])
    return (dx * dx + dy * dy) ** 0.5


if __name__ == "__main__":
    for cls in ("trump5", "k5_11", "k5_16"):
        print(cls, pins_of(cls))
        for r in forced_cells(cls):
            print("   ", r["cell"], r["extension"], "USABLE" if r["usable"] else "--", (r["status"] or "")[:40])
