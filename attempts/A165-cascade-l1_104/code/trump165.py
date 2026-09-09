"""A165 -- the Trump witness for the canary.

`class84.trump_scaled()` gives Trump's family dilated to s0 and `class84.symmetry(Y, k)` the eight
D4 images.  For a k0 cell (one hypothesis box `H`) this module finds every (image, square) pair
whose pose lies in `H`'s box, and for each such image reports the actual widened-corner meeters,
the actual chords on a wall line, and the actual top-strip occupancy.  Nothing here is a proof --
it is the FALSIFIER for every forced step of the cascade.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cas165 as K                                               # noqa: E402
for _p in (os.path.join(K.ATT, "A99-k0-tree-v2", "code"),):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import class84 as K84                                            # noqa: E402


def images():
    """[(k, [(cx, cy, theta_deg) x 11])] for the eight D4 images at s0."""
    Y0, s_trump, lam = K84.trump_scaled()
    out = []
    for k in range(8):
        Z = K84.symmetry(Y0, k)
        out.append((k, [(float(x), float(y), math.degrees(float(th)) % 90.0) for x, y, th in Z]))
    return out, float(s_trump), float(lam)


def in_hyp(pose, box):
    return K.in_box(pose[0], pose[1], pose[2], box)


def image_report(Z, boxes):
    """Everything the canary needs from one image."""
    rep = dict(hyp_hits=[], corners={}, n=len(Z))
    for i, p in enumerate(Z):
        for j, b in enumerate(boxes):
            if in_hyp(p, b):
                rep["hyp_hits"].append(dict(sq=i, box=j, pose=[round(v, 9) for v in p]))
    for c in K.CORNERS:
        cell = K.corner_cell(c)
        plain = (0.0, 1.0, 0.0, 1.0) if c == "BL" else None
        ms = []
        for i, p in enumerate(Z):
            if K.sq_meets_rect(p[0], p[1], math.radians(p[2]), cell):
                ms.append(dict(sq=i, pose=[round(v, 9) for v in p]))
        # the same count on the UNWIDENED unit corner box
        cell0 = {"BL": (0.0, 1.0, 0.0, 1.0), "BR": (K.S0 - 1.0, K.S0, 0.0, 1.0),
                 "TR": (K.S0 - 1.0, K.S0, K.S0 - 1.0, K.S0),
                 "TL": (0.0, 1.0, K.S0 - 1.0, K.S0)}[c]
        n0 = sum(1 for p in Z if K.sq_meets_rect(p[0], p[1], math.radians(p[2]), cell0))
        rep["corners"][c] = dict(n_widened=len(ms), n_plain=n0, meeters=ms)
        del plain
    return rep


def chords_on(Z, line):
    return [K.chord_of(p[0], p[1], math.radians(p[2]), line) for p in Z]
