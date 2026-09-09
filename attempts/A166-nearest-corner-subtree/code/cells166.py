"""A166 -- the eleven hard k0_00 cells, the NEAREST-CORNER metric, and the corner pair cover in
each corner's own frame.

READ-ONLY on every prior attempt.  A155's `cells155` (the pad-parametrised corner cover) and A150's
frame convention are imported / re-derived, never written.

THE METRIC (stated once, used everywhere).  For a cell whose conditioned box is
`B_H = [x0,x1] x [y0,y1] x [th0,th1]`, put `z_H = ((x0+x1)/2, (y0+y1)/2)` (the box's CENTRE, i.e.
the centre of the conditioned square's admissible centre rectangle -- the tilt window plays no part).
The nearest corner is `argmin_c |z_H - p_c|_2` over the four container corner POINTS
`p_BL = (0,0)`, `p_BR = (s0,0)`, `p_TR = (s0,s0)`, `p_TL = (0,s0)`.  Ties (none occur) would be
broken BL < BR < TR < TL.

FRAMES.  A150's convention verbatim: each corner carries the BL frame transported by a ROTATION
(never a reflection), so a local cell index means the same pose class at every corner and the local
tilt is always `theta mod 90`:

    BL: (u,v) = (x, y)        BR: (u,v) = (y, s-x)      TR: (u,v) = (s-x, s-y)   TL: (u,v) = (s-y, x)

and back  BL: (u,v)          BR: (s-v, u)              TR: (s-u, s-v)           TL: (v, s-u).

The cover itself is A155's: the zone `[1/2, a_w + sqrt2/2]^2` split 6 x 6 in position and `[0, 90)`
split into 6 tilt windows of 15 deg = 216 closed cells, each clipped against the container and
against "the square meets `[0, a_w]^2`".  **The transpose quotient of A143/A150 is NOT used here**:
once `H` is fixed the node is no longer symmetric under the corner's stabiliser, so the pair cover
runs over all `216*217/2 = 23 436` unordered pairs (`A = B` allowed as a cover element; it is always
killed by (P2), a unit square cannot be two interior-disjoint squares).
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, ".."))
for _p in (os.path.join(ATT, "A155-exact-cell-corner-band", "code"),
           os.path.join(ATT, "A143-corner-first-k0", "code"),
           os.path.join(ATT, "A140-k0-residue-gallery", "code"),
           os.path.join(ATT, "A57-shadow-trees", "code"),
           os.path.join(ATT, "A132-polygon-core", "code"),
           os.path.join(ATT, "A135-polycore-verifier", "code"),
           HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import cells155 as C155                                             # noqa: E402  READ-ONLY (A155)
from caselp import Box                                              # noqa: E402  READ-ONLY (A57)

S0 = C155.S0
S0_RAT = "969271/250000"
W_MAX = C155.W_MAX
CORNERS = ("BL", "BR", "TR", "TL")
CORNER_POINT = {"BL": (0.0, 0.0), "BR": (S0, 0.0), "TR": (S0, S0), "TL": (0.0, S0)}

A115_NODES = os.path.join(ATT, "A115-k0-corner-rows", "results", "nodes")

# the eleven converged-alive k0_00 cells: (name, level, A115 record file, family, s* of panel N)
ELEVEN = [
    ("l1_071",      1, "l1_071_plain_warm.t4.lp.json", "K01",  4.000000),
    ("l1_104",      1, "l1_104_plain_warm.t4.lp.json", "K04",  3.914214),
    ("l1_124",      1, "node_124.t5.lp.json",          "none", 3.942810),
    ("l1_148",      1, "node_148.t5.lp.json",          "K01",  4.000000),
    ("l1_153",      1, "node_153.t5.lp.json",          "none", 3.877084),
    ("l1_158",      1, "node_158.t5.lp.json",          "none", 3.902674),
    ("l1_159",      1, "node_159.t5.lp.json",          "K06",  3.886745),
    ("l2_p114_001", 2, "l2_p114_001.t5.lp.json",       "K20",  3.924402),
    ("l2_p65_101",  2, "l2_p65_101.t5.lp.json",        "K01",  4.000000),
    ("l2_p65_111",  2, "l2_p65_111.t5.lp.json",        "K03",  3.925149),
    ("l2_p74_001",  2, "l2_p74_001.t5.lp.json",        "K05",  3.912232),
]
TRUMP_IMAGE_CELL = "l1_153"


def load_eleven():
    """[(meta, H box, record)] for the eleven, READ-ONLY from A115's own LP records."""
    out = []
    for (name, lvl, fn, fam, sstar) in ELEVEN:
        p = os.path.join(A115_NODES, fn)
        d = json.load(open(p, encoding="utf-8"))
        boxes = d["hyp"]["boxes"]
        assert len(boxes) == 1, (name, len(boxes))
        assert not d["hyp"].get("nofams"), name
        b = Box(**{k: boxes[0][k] for k in ("x0", "x1", "y0", "y1", "th0", "th1")})
        meta = dict(cell=name, level=lvl, family=fam, s_star=sstar,
                    record=os.path.relpath(p, ROOT).replace("\\", "/"),
                    budget=d["budget"], tau=d["tau"], converged=d["converged"])
        out.append((meta, b, d))
    return out


def box_centre(b):
    return (0.5 * (b.x0 + b.x1), 0.5 * (b.y0 + b.y1))


def corner_distances(b):
    zx, zy = box_centre(b)
    return {c: math.hypot(zx - CORNER_POINT[c][0], zy - CORNER_POINT[c][1]) for c in CORNERS}


def nearest_corner(b):
    d = corner_distances(b)
    return min(CORNERS, key=lambda c: (d[c], CORNERS.index(c))), d


# ------------------------------------------------------------------ frames (A150 convention)
def to_global_rect(corner, u0, u1, v0, v1, s=S0):
    """local centre rectangle -> global centre rectangle (the tilt window is unchanged mod 90)."""
    if corner == "BL":
        return (u0, u1, v0, v1)
    if corner == "BR":
        return (s - v1, s - v0, u0, u1)
    if corner == "TR":
        return (s - u1, s - u0, s - v1, s - v0)
    if corner == "TL":
        return (v0, v1, s - u1, s - u0)
    raise ValueError(corner)


def to_local_pose(corner, x, y, th_deg, s=S0):
    """global pose -> the corner's local frame (rotation only; theta mod 90 is invariant)."""
    if corner == "BL":
        u, v = x, y
    elif corner == "BR":
        u, v = y, s - x
    elif corner == "TR":
        u, v = s - x, s - y
    elif corner == "TL":
        u, v = s - y, x
    else:
        raise ValueError(corner)
    return u, v, th_deg % 90.0


def global_box(corner, cell):
    b = cell.box
    X0, X1, Y0, Y1 = to_global_rect(corner, b.x0, b.x1, b.y0, b.y1)
    return Box(X0, X1, Y0, Y1, b.th0, b.th1)


def global_subbin_boxes(corner, cell, a_w, nsub=4):
    out = []
    for (a, b, cl) in C155.subbin_clip(*cell.raw, a_w=a_w, nsub=nsub):
        X0, X1, Y0, Y1 = to_global_rect(corner, cl[0], cl[1], cl[2], cl[3])
        out.append(Box(X0, X1, Y0, Y1, a, b))
    return out


def corner_rect(corner, a_w, s=S0):
    """the (widened) corner box in GLOBAL coordinates, as (X0, X1, Y0, Y1)."""
    if corner == "BL":
        return (0.0, a_w, 0.0, a_w)
    if corner == "BR":
        return (s - a_w, s, 0.0, a_w)
    if corner == "TR":
        return (s - a_w, s, s - a_w, s)
    if corner == "TL":
        return (0.0, a_w, s - a_w, s)
    raise ValueError(corner)


def cover(a_w):
    """A155's 216-cell cover in the LOCAL frame; every cell is live at both pads used here."""
    return C155.all_cells(a_w)


if __name__ == "__main__":
    rows = []
    for (meta, b, _d) in load_eleven():
        c, d = nearest_corner(b)
        zx, zy = box_centre(b)
        rows.append(dict(meta, box=b.to_json(), z=[zx, zy], nearest=c,
                         dist={k: round(v, 6) for k, v in d.items()},
                         second=sorted(d, key=lambda k: d[k])[1],
                         margin=round(sorted(d.values())[1] - sorted(d.values())[0], 6)))
        print("%-12s z=(%.5f, %.5f) th=[%.1f,%.1f]  nearest %s d=%.5f  (2nd %s %.5f)"
              % (meta["cell"], zx, zy, b.th0, b.th1, c, d[c],
                 rows[-1]["second"], d[rows[-1]["second"]]))
    json.dump(rows, open(os.path.join(BASE, "results", "nearest166.json"), "w"), indent=1)
    print("cover cells at wmax:", len(cover(1.0 + W_MAX)),
          "live:", sum(1 for c in cover(1.0 + W_MAX) if not c.empty))
    print("cover cells at w0:", len(cover(1.0)),
          "live:", sum(1 for c in cover(1.0) if not c.empty))
