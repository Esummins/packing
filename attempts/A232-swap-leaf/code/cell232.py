"""A232 -- cells for the SWAP leaf: load a k0_00 cell, normalise it to the BL corner frame,
build the roles' REACH SETS, decide the set X, split a cell, emit the certificate.

A CELL (A185's boxed-windows convention, `winlp185.WRole`) is n = 11 ROLES over the window
W = [m_lo, s0]; a role is BOXED when it carries pose pieces (centre rectangle x tilt bin, stated
at s0 on F = D_lambda P) and UNBOXED otherwise.  The k0v4 gallery's eleven converged-alive
k0_00 cells are recorded by A115 as ONE conditioned square `H` plus ten free squares
(`budget` = 10): so ten of the eleven roles are unboxed, which is exactly what the leaf feels.

The reach set of a boxed role in the corner frame is the union of the posed unit squares over
its (pulled back, flipped) pieces.  For the SEARCH it is over-approximated by a convex hull of
sampled poses dilated outward (sound direction: a bigger obstacle only makes the search harder);
every placement that the search proposes is then re-decided EXACTLY by `verify_swap232`.
"""
import json
import math
import os
import sys
from fractions import Fraction as Fr

import numpy as np
from shapely.geometry import Polygon, box as sbox
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
sys.path.insert(0, HERE)
import verify_swap232 as V                                       # noqa: E402  (the verifier is the oracle)

S0 = Fr(3877084, 10 ** 6)
M_LO = Fr(191, 50)
CORNERS = ("BL", "BR", "TR", "TL")
K0V4 = os.path.join(ROOT, "docs", "shadows", "k0v4", "review_k0v4.csv")


# ===================================================================== loading
def k0v4_cells():
    """[(node, record_path)] for the eleven converged-alive k0_00 cells of the k0v4 gallery."""
    out = []
    with open(K0V4, encoding="utf-8") as fh:
        head = fh.readline().split(",")
        i_node, i_rec = head.index("node"), head.index("record")
        for ln in fh:
            f = ln.split(",")
            if len(f) > i_rec:
                out.append((f[i_node], f[i_rec].replace("\\", "/")))
    return out


def load_cell(node, rec_rel):
    """the cell as recorded: n = 11 roles, the hypothesis boxes as `H`/`H2`..., the rest free."""
    d = json.load(open(os.path.join(ROOT, rec_rel), encoding="utf-8"))
    boxes = (d.get("hyp") or {}).get("boxes") or []
    roles = []
    for i, b in enumerate(boxes):
        roles.append(dict(name="H" if i == 0 else "H%d" % (i + 1),
                          pieces=[dict(x0=b["x0"], x1=b["x1"], y0=b["y0"], y1=b["y1"],
                                       th0=b["th0"], th1=b["th1"])]))
    for j in range(11 - len(roles)):
        roles.append(dict(name="F%d" % (j + 1), pieces=[]))
    return dict(node=node, label=node, record=rec_rel, n=11, roles=roles,
                s0=str(S0), m_lo=str(M_LO))


def split_cell(cell, nx=4, ny=4, nt=4):
    """ONE round of A185's own split: the boxed roles' pieces cut into nx x ny x nt children
    (<= 64 per cell).  Only the boxed roles carry pieces, so this is the cell's whole content."""
    boxed = [r for r in cell["roles"] if r["pieces"]]
    if len(boxed) != 1 or len(boxed[0]["pieces"]) != 1:
        return []
    p = boxed[0]["pieces"][0]
    x0, x1, y0, y1 = (float(p[k]) for k in ("x0", "x1", "y0", "y1"))
    t0, t1 = float(p["th0"]), float(p["th1"])
    kids = []
    for i in range(nx):
        for j in range(ny):
            for k in range(nt):
                q = dict(x0=x0 + (x1 - x0) * i / nx, x1=x0 + (x1 - x0) * (i + 1) / nx,
                         y0=y0 + (y1 - y0) * j / ny, y1=y0 + (y1 - y0) * (j + 1) / ny,
                         th0=t0 + (t1 - t0) * k / nt, th1=t0 + (t1 - t0) * (k + 1) / nt)
                kid = json.loads(json.dumps(cell))
                kid["label"] = "%s/s%d%d%d" % (cell["node"], i, j, k)
                for r in kid["roles"]:
                    if r["name"] == boxed[0]["name"]:
                        r["pieces"] = [q]
                kids.append(kid)
    return kids


# ===================================================================== the corner frame
def normalised_pieces(role, corner):
    """the role's pieces as m-free supersets in the frame that takes `corner` to BL -- computed
    by the VERIFIER's own routine, so the search never sees a different object."""
    return [V.normalise_piece(p, corner, M_LO, S0) for p in role["pieces"]]


def reach_poly(box, samples=13, pad=1e-4):
    """OVER-approximation (shapely) of the union of the posed unit squares over `box`."""
    x0, x1, y0, y1, t0, t1 = (float(v) for v in box)
    pts = []
    for k in range(samples):
        t = t0 + (t1 - t0) * k / max(1, samples - 1)
        th = 2 * math.atan(t)
        c, s = math.cos(th), math.sin(th)
        for ux, uy in ((-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5)):
            pts.append((c * ux - s * uy, s * ux + c * uy))
    q = Polygon(pts).convex_hull
    cen = sbox(x0, y0, x1, y1)
    hull = Polygon([(a[0] + b[0], a[1] + b[1])
                    for a in cen.exterior.coords[:-1] for b in q.exterior.coords[:-1]]).convex_hull
    return hull.buffer(pad)


SLOT = dict(kind="axis", x="0", y="0")


def role_sets(cell, corner):
    """(X, outside, obstacles): X = the roles that must be exchanged (every unboxed role, plus
    every boxed role whose reach is not CERTIFIED to miss the corner slot); outside = the rest;
    obstacles = shapely reach polygons of `outside`."""
    X, outside, obst = [], [], []
    for r in cell["roles"]:
        if not r["pieces"]:
            X.append(r["name"])
            continue
        boxes = normalised_pieces(r, corner)
        if all(V.box_misses_axis_cell(b, (Fr(0), Fr(1), Fr(0), Fr(1)))[0] for b in boxes):
            outside.append(r["name"])
            obst.append(unary_union([reach_poly(b) for b in boxes]))
        else:
            X.append(r["name"])
    return X, outside, obst


def make_cert(cell, corner, X, cells):
    return dict(format="swap-leaf-certificate-v1", n=cell["n"], cell=cell["node"],
                node=cell["label"], record=cell["record"], s0=str(S0), m_lo=str(M_LO),
                lambda_max=str(S0 / M_LO), corner=corner, corner_name=CORNERS[corner],
                roles=[dict(name=r["name"], pieces=r["pieces"]) for r in cell["roles"]],
                X=list(X), cells=cells, slot_index=0,
                claim=("SWAP-LEAF (docs/proofs/swap_leaf.md): the %d cells are pairwise "
                       "interior-disjoint unit squares in [0, m]^2 for every side m of the "
                       "window, cell 0 is the %s slot square, and every role outside X misses "
                       "every cell -- so |M(Pi)| <= |X| = |Pi| and Lemma CELLS (`cells_swap`) "
                       "exchanges every packing of the cell, at the same side, into one with "
                       "the corner settled.  With k1-a the cell is DEAD."
                       % (len(cells), CORNERS[corner])),
                cites=["swap_packing / cells_swap -- lean Statements/Open/RingSwap.lean (theorems)",
                       "swap_leaf_dead -- lean Statements/SwapLeaf.lean (theorem)",
                       "k1-a -- k0_route.md s.3 (DEPENDENCY: the k1_00 tree)",
                       "K0-WIDEN -- k0_route.md s.4.1 (the pull-back to the original side)"])


def container_poly():
    return sbox(0.0, 0.0, float(M_LO), float(M_LO))
