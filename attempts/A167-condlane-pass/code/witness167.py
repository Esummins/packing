"""A167 T3 -- the EXACT two-crowd witness that RETIRES a cell (A159's rule, made rational).

WHAT IT CERTIFIES.  At a slot cell `C` of a pinned class, exhibit TWO unit squares `Q_H` and `Q_F`
with

    (W1)  both inside the container `[0, s0]^2`;
    (W2)  both meeting `int C`;
    (W3)  interiors pairwise DISJOINT;
    (W4)  each interior-disjoint from all five class PIN squares at side `s0`;
    (W5)  `Q_H`'s pose lies inside the node's conditioned box `B_H` (so it is a legal `H`).

Then TWO non-pin squares can meet `int C` while respecting every constraint the lane family's
counters are built from, so `LANE + M >= 2` there: **no leaf of the lane / chord-limited-lane family
can ever fire at this cell**, and the cell is RETIRED.  This is exactly A159's C8 two-crowd rule and
A161's `RETIRED-two-crowd-outside`, except that the pair is verified in EXACT rational arithmetic
instead of being read off a float sample.

It is a statement about the LEAF, not about the packing: it does not say the node is alive, only
that this cell cannot kill it.

Poses are rationalised onto a `1/DEN` grid (`c = (cx, cy)`, `t = tan(theta/2)`, so
`cos = (1 - t^2)/(1 + t^2)` and `sin = 2t/(1 + t^2)` are exact rationals and every vertex is
rational).  All five predicates are decided by the separating-axis test over the edge normals of the
two polygons, which is COMPLETE for convex polygons: interiors are disjoint iff some edge normal
separates them (non-strictly), and they meet iff none does.

    python witness167.py --rows ../results/pass_s0.jsonl --out ../results/nogo.jsonl
"""
import argparse
import glob
import hashlib
import json
import math
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
for _p in (os.path.join(ROOT, "attempts", "A161-chord-lane", "code"), HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import checkcl as K                      # noqa: E402  the class pin table + t_lo/t_hi (read-only)
import chordlane as CL                   # noqa: E402  frame boxes, sampling (read-only)
import numpy as np                       # noqa: E402
import polylane as P                     # noqa: E402
import polycore as PC                    # noqa: E402

DEN = 10 ** 6
S = K.S_RAT
HALF = Fr(1, 2)


# ===================================================================== exact convex geometry
def sq_poly(cx, cy, t):
    """The four vertices of the unit square with centre (cx, cy) and tan(theta/2) = t, exactly."""
    cx, cy, t = Fr(cx), Fr(cy), Fr(t)
    d = 1 + t * t
    co, si = (1 - t * t) / d, 2 * t / d
    ux, uy = co / 2, si / 2
    vx, vy = -si / 2, co / 2
    return [(cx + ux + vx, cy + uy + vy), (cx + ux - vx, cy + uy - vy),
            (cx - ux - vx, cy - uy - vy), (cx - ux + vx, cy - uy + vy)]


def rect_poly(x0, x1, y0, y1):
    x0, x1, y0, y1 = (Fr(v) for v in (x0, x1, y0, y1))
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def _axes(poly):
    out = []
    n = len(poly)
    for i in range(n):
        (ax, ay), (bx, by) = poly[i], poly[(i + 1) % n]
        out.append((-(by - ay), bx - ax))                 # outward normal of the edge
    return out


def _span(poly, ax):
    v = [ax[0] * x + ax[1] * y for (x, y) in poly]
    return min(v), max(v)


def separated(p, q):
    """EXACT and COMPLETE for convex polygons: some edge normal separates them non-strictly
    (touching counts as separated -- interiors are then disjoint)."""
    for ax in _axes(p) + _axes(q):
        if ax == (0, 0):
            continue
        a0, a1 = _span(p, ax)
        b0, b1 = _span(q, ax)
        if a1 <= b0 or b1 <= a0:
            return True
    return False


def inside_container(poly, s=S):
    return all(0 <= x <= s and 0 <= y <= s for (x, y) in poly)


def pins_at(cls, s=S):
    return [rect_poly(px - HALF, px + HALF, py - HALF, py + HALF) for (px, py) in K.PINS[cls]]


# ===================================================================== the frame's pin squares
def frame_pins(cls, corner, s=S):
    """The class pins in the CELL's corner frame at side `s` (the frame flips x and/or y)."""
    out = []
    flipx, flipy = corner in ("BR", "TR"), corner in ("TR", "TL")
    for (px, py) in K.PINS[cls]:
        px, py = Fr(px), Fr(py)
        if flipx:
            px = s - px
        if flipy:
            py = s - py
        out.append(rect_poly(px - HALF, px + HALF, py - HALF, py + HALF))
    return out


# ===================================================================== the search
def rationalise(cx, cy, th_deg, den=DEN):
    t = math.tan(math.radians(th_deg) / 2.0)
    return (Fr(round(cx * den), den), Fr(round(cy * den), den),
            Fr(round(t * den), den))


def verify(cls, corner, cell, B_H, wH, wF, s=S):
    """(ok, detail) for the five predicates, exactly."""
    C = rect_poly(*cell)
    pins = frame_pins(cls, corner, s)
    QH = sq_poly(*wH)
    QF = sq_poly(*wF)
    d = {}
    d["W1"] = bool(inside_container(QH, s) and inside_container(QF, s))
    d["W2"] = bool((not separated(QH, C)) and (not separated(QF, C)))
    d["W3"] = bool(separated(QH, QF))
    d["W4"] = bool(all(separated(QH, p) and separated(QF, p) for p in pins))
    x0, x1, y0, y1, th0, th1 = B_H
    tl, th = K.t_lo(th0), K.t_hi(th1)
    tl, th = (min(tl, th), max(tl, th))
    d["W5"] = bool(Fr(x0) <= wH[0] <= Fr(x1) and Fr(y0) <= wH[1] <= Fr(y1)
                   and Fr(tl) <= wH[2] <= Fr(th))
    return all(d.values()), d


def search(rec, slot, rng, n=60000, tries=6):
    """Sampled candidate pair, then EXACT verification of the rationalised poses."""
    conds, meet, cell, corner, i, j = CL.frame_boxes(rec, slot)
    jH = meet[0]
    B_H = P.box_json(conds[jH].box)
    pins = [c for c in conds if c.idx != jH]
    s = CL.S0
    b = conds[jH].box
    # H poses inside its box that meet int C and clear every pin core
    CH = np.column_stack([rng.uniform(b.x0, b.x1, n), rng.uniform(b.y0, b.y1, n)])
    TH = (np.radians(rng.uniform(b.th0, b.th1, n)) if b.th1 > b.th0
          else np.full(n, math.radians(b.th0)))
    h = 0.5 * (np.abs(np.cos(TH)) + np.abs(np.sin(TH)))
    okH = ((CH[:, 0] >= h) & (CH[:, 0] <= s - h) & (CH[:, 1] >= h) & (CH[:, 1] <= s - h)
           & P.rect_square_meets(cell, CH, TH))
    for pc in pins:
        okH &= (PC.poly_square_depth(pc.pc.P, CH, TH) <= 0.0)
    # free poses meeting int C clearing every pin core AND the H box's core
    CF, TF = P.sample_meeting(cell, s, n, rng)
    okF = np.ones(len(CF), bool)
    for pc in conds:
        okF &= (PC.poly_square_depth(pc.pc.P, CF, TF) <= 0.0)
    iH, iF = np.nonzero(okH)[0], np.nonzero(okF)[0]
    if not len(iH) or not len(iF):
        return None
    best = None
    for a in iH[:400]:
        for c in iF[:400]:
            g = float(CL.LANE.L.pair_gaps(np.array([CH[a], CF[c]]),
                                          np.array([TH[a], TF[c]]))[0, 1])
            if best is None or g > best[0]:
                best = (g, int(a), int(c))
    if best is None or best[0] <= 0.0:
        return None
    out = dict(cell=list(cell), corner=corner, B_H=B_H, gap=best[0], jH=jH,
               n_H_ok=int(okH.sum()), n_F_ok=int(okF.sum()))
    for k in range(tries):
        den = DEN * (10 ** k)
        wH = rationalise(CH[best[1]][0], CH[best[1]][1], math.degrees(TH[best[1]]), den)
        wF = rationalise(CF[best[2]][0], CF[best[2]][1], math.degrees(TF[best[2]]), den)
        ok, det = verify(rec["cls"], corner, cell, B_H, wH, wF)
        if ok:
            out.update(ok=True, den=den, H=[str(v) for v in wH], F=[str(v) for v in wF],
                       detail=det)
            return out
    out.update(ok=False, den=den, H=[str(v) for v in wH], F=[str(v) for v in wF], detail=det)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", nargs="*", default=[])
    ap.add_argument("--glob", default="")
    ap.add_argument("--verdict", default="NO-GO-witness")
    ap.add_argument("--sample", type=int, default=60000)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--certs", default=os.path.join(BASE, "certs_nogo"))
    ap.add_argument("--out", default=os.path.join(BASE, "results", "nogo.jsonl"))
    a = ap.parse_args()
    files = list(a.rows) + (sorted(glob.glob(a.glob)) if a.glob else [])
    rows = []
    for f in files:
        for ln in open(f, encoding="utf-8"):
            r = json.loads(ln)
            if r.get("verdict") == a.verdict:
                rows.append(r)
    os.makedirs(a.certs, exist_ok=True)
    recs = {r["nid"]: r for r in CL.CP.load_nodes()}
    boxes, _ = CL.CP.load_open_boxes(set(recs))
    for b in boxes:
        if not b.get("covered_by_node"):
            recs.setdefault(b["nid"], b)
    rng = np.random.default_rng(167167)
    done = set()
    if os.path.exists(a.out):
        for ln in open(a.out, encoding="utf-8"):
            q = json.loads(ln)
            done.add((q["nid"], q["slot"]))
    fh = open(a.out, "a", encoding="utf-8")
    nok = 0
    for k, r in enumerate(rows):
        if (r["nid"], r["slot"]) in done:
            continue
        if a.limit and k >= a.limit:
            break
        try:
            w = search(recs[r["nid"]], r["slot"], rng, n=a.sample)
        except Exception as e:                                       # noqa: BLE001
            w = dict(ok=False, error=repr(e)[:200])
        out = dict(nid=r["nid"], slot=r["slot"], cls=r["cls"], src=r["src"],
                   level=r["level"], **(w or dict(ok=False, why="no candidate pair")))
        if w and w.get("ok"):
            nok += 1
            cert = dict(leaf="nogo_two_crowd_v1", nid=r["nid"], slot=r["slot"], cls=r["cls"],
                        src=r["src"], level=r["level"], s=str(S), corner=w["corner"],
                        cell=w["cell"], B_H=w["B_H"], cond_index=w["jH"], den=w["den"],
                        H=w["H"], F=w["F"],
                        claim="two interior-disjoint unit squares, both inside [0, s0]^2, both "
                              "meeting int C, both clear of all five class pins, one of them a "
                              "legal pose of the conditioned square: LANE + M >= 2 at this cell, "
                              "so no lane-family leaf can fire here (A159 C8, exact form)")
            blob = json.dumps(cert, sort_keys=True, indent=1).encode("utf-8")
            q = os.path.join(a.certs, "nogo_%s__%s.json"
                             % (r["nid"], r["slot"].replace("(", "").replace(")", "")
                                .replace(",", "_")))
            open(q, "wb").write(blob)
            out["cert"] = os.path.relpath(q, ROOT).replace(os.sep, "/")
            out["sha256"] = hashlib.sha256(blob).hexdigest()
        fh.write(json.dumps(out) + "\n")
        fh.flush()
        print("%-30s %-9s %s  gap=%s  %s" % (r["nid"], r["slot"], "EXACT" if out.get("ok")
                                             else "no", round(out.get("gap") or 0, 4),
                                             out.get("detail")), flush=True)
    fh.close()
    print("\n%d rows, %d exact two-crowd witnesses" % (len(rows), nok))


if __name__ == "__main__":
    main()
