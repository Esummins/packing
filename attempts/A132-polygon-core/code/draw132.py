"""A132 -- one figure per node: the hypothesis square H at the box centre and mid-tilt (cyan),
the certified polygon core K' inside it, the axis core K(a), and the dual-support columns, with
the OFFENDING ones (meet K' but not K(a)) hatched.

    python code/draw132.py k5_11_interior_Y0186_D00_D00 [more ids...]
"""
import glob
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, ".."))
A57 = os.path.join(ROOT, "A57-shadow-trees")
for p in (os.path.join(A57, "code"), os.path.join(ROOT, "A96-a57-parametric", "code"), HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

import polycore                                               # noqa: E402
from caselp import Box, EPS_CORE                              # noqa: E402

W = 760
PAD = 40


def sq(cx, cy, th):
    c, s = math.cos(th), math.sin(th)
    e1, e2 = np.array([c, s]), np.array([-s, c])
    return [np.array([cx, cy]) + 0.5 * (i * e1 + j * e2)
            for i, j in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


def draw(node_id, out_dir):
    d = None
    for p in glob.glob(os.path.join(A57, "results", "tree", "*", node_id + ".json")):
        d = json.load(open(p))
        break
    if d is None:
        print(f"{node_id}: no record")
        return
    boxes = [Box.from_json(b) for b in d["hyp"]["boxes"]]
    nb = boxes[-1]
    pc = polycore.build(nb)
    core = nb.core()
    P = np.array([[q["cx"], q["cy"], q["theta"], q["y"]] for q in d["packing"]], float).reshape(-1, 4)
    dp = polycore.poly_square_depth(pc.P, P[:, :2], P[:, 2])
    dc = polycore.core_depth_fast(core, P[:, :2], P[:, 2])
    off = (dp > EPS_CORE) & (dc <= EPS_CORE)

    cx, cy = 0.5 * (nb.x0 + nb.x1), 0.5 * (nb.y0 + nb.y1)
    th = math.radians(0.5 * (nb.th0 + nb.th1))
    R = 1.9
    lo = np.array([cx - R, cy - R])
    sc = (W - 2 * PAD) / (2 * R)

    def T(p):
        return (PAD + (p[0] - lo[0]) * sc, W - PAD - (p[1] - lo[1]) * sc)

    def poly(pts, **kw):
        s = " ".join(f"{T(p)[0]:.2f},{T(p)[1]:.2f}" for p in pts)
        at = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())
        return f'<polygon points="{s}" {at}/>'

    L = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{W + 46}" '
         f'viewBox="0 0 {W} {W + 46}">',
         '<defs><pattern id="hatch" width="6" height="6" patternTransform="rotate(45)" '
         'patternUnits="userSpaceOnUse"><line x1="0" y1="0" x2="0" y2="6" '
         'stroke="#c1121f" stroke-width="2.2"/></pattern></defs>',
         f'<rect width="{W}" height="{W + 46}" fill="#ffffff"/>']
    # the dual-support columns
    for k in range(len(P)):
        pts = sq(P[k, 0], P[k, 1], P[k, 2])
        if off[k]:
            L.append(poly(pts, fill="url(#hatch)", fill_opacity="0.55", stroke="#c1121f",
                          stroke_width="1.6"))
        else:
            L.append(poly(pts, fill="#9aa0a6", fill_opacity="0.13", stroke="#9aa0a6",
                          stroke_width="1.0"))
    # H: the hypothesis square at the box centre and mid-tilt
    L.append(poly(sq(cx, cy, th), fill="#00b7c2", fill_opacity="0.14", stroke="#0097a7",
                  stroke_width="2.4"))
    # K(a) and K'
    L.append(poly([np.array(v) for v in polycore.core_verts(core)], fill="none",
                  stroke="#7b1fa2", stroke_width="2.0", stroke_dasharray="7 4"))
    L.append(poly([np.array([float(a), float(b)]) for a, b in pc.verts], fill="#2e7d32",
                  fill_opacity="0.20", stroke="#2e7d32", stroke_width="2.2"))
    # the centre box
    L.append(poly([np.array(p) for p in ((nb.x0, nb.y0), (nb.x1, nb.y0), (nb.x1, nb.y1),
                                         (nb.x0, nb.y1))], fill="none", stroke="#111",
                  stroke_width="1.2"))
    lab = (f"{node_id}   box theta [{nb.th0:.2f},{nb.th1:.2f}] deg   "
           f"area K'/K(a) = {pc.area() / (2 * float(core.a)) ** 2:.3f}   "
           f"hatched: {int(off.sum())} of {len(P)} support columns meet K' but not K(a), "
           f"weight {float(P[off, 3].sum()):.2f} of tau {float(P[:, 3].sum()):.2f}")
    L.append(f'<text x="{PAD}" y="{W + 22}" font-family="monospace" font-size="13" '
             f'fill="#111">{lab}</text>')
    L.append('<text x="%d" y="%d" font-family="monospace" font-size="13" fill="#111">'
             'cyan H = hypothesis square (box centre, mid-tilt) | green = K\' | '
             'dashed purple = K(a) | grey = support | hatched red = offending</text>'
             % (PAD, W + 40))
    L.append("</svg>")
    out = os.path.join(out_dir, f"fig_{node_id}.svg")
    open(out, "w").write("\n".join(L))
    print(f"{out}  ({int(off.sum())}/{len(P)} offending, ratio "
          f"{pc.area() / (2 * float(core.a)) ** 2:.3f})")


if __name__ == "__main__":
    ids = sys.argv[1:] or ["k5_11_interior_Y0186_D00_D00"]
    od = os.path.join(BASE, "results")
    for i in ids:
        draw(i, od)
