"""A159 T1 -- EXACT re-examination of A141's T5 two-crowd witnesses.

A141 `results/t5_twocrowd.json` claims, for 28 of the 44 NEAR-MISS (LANE_K' <= 1, M = 1) k0
corners, a realised two-crowd: an interior-disjoint pair (free square, conditioned square H) both
meeting the WIDENED corner box of Lemma K0-WIDEN.  A realised pair is fatal to every lane leaf at
that corner (the hypothesis "corner met by <= 1 square" is simply false there), so the claim has
to be exact, not sampled.

FRAME.  A141 runs the lane test in the CONTAINER frame: `polylane.corner_cell(c, s, w)` returns
the widened corner box in container coordinates (TR = [s0-1-w, s0]^2, w = W0 = 0.0255100742...)
and `polylane.centre_window` is built from it.  The poses recorded in t5_twocrowd.json are
therefore container-frame poses in the units of the container ([0, s0]^2, unit squares, tilt in
DEGREES, 90-periodic).  This file re-derives that from the records themselves (H's pose must lie
in the cell's own box B, which is stated in container coordinates) rather than trusting either
A141's or A148's prose.

WHAT IS CHECKED, per witness, with rigorous interval arithmetic (mpmath.iv, 60 dps; every
reported sign comes from an enclosure that does not straddle 0, else INDETERMINATE and the
precision is raised):

  (1) pose_H_in_B       H = (x, y, th) has x in [x0,x1], y in [y0,y1], th in [th0,th1]   (exact,
                        floats compared as exact binary rationals; tilt also tried mod 90)
  (2) H_in_container    Q(H) contained in [0, s0]^2
  (3) free_in_container Q(free) contained in [0, s0]^2
  (4) H_meets_box       int Q(H) meets int(widened corner box)     -- SAT over the 4 candidate
  (5) free_meets_box    int Q(free) meets int(widened corner box)     axes (box normals e_x, e_y
                        and the square's own two normals); SAT is COMPLETE for convex polygons,
                        so "no axis separates" is a proof of intersection
  (6) disjoint          int Q(free) and int Q(H) are disjoint: some axis among the 4 normals of
                        the two squares separates them strictly (gap > 0)
  (7) free_avoids_core  int Q(free) misses K'(B_j) for every conditioned box (the LANE-membership
                        condition A141 samples with); informational -- (6) is what makes the pair
                        a genuine two-crowd

Also reported for context: `depth_into_unwidened_cell`, the quantity A148's page computed (it uses
`cell_rect` = the UNIT corner cell [s0-1, s0]^2, NOT the widened box), which is what made the
l1_124 witness look 0.026 short.

    python xwitness159.py                       # all 28
    python xwitness159.py --cells l1_153        # one
"""
import argparse
import glob
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
A141 = os.path.join(ROOT, "attempts", "A141-polycore-lane")

import mpmath  # noqa: E402
from fractions import Fraction  # noqa: E402

S0 = Fraction(969271, 250000)                       # 3.877084 exactly
WLO = Fraction(382, 100)
LAM_MAX = S0 / WLO                                  # rational
SQ2 = mpmath.mpf(2) ** mpmath.mpf(0.5)


def w0(prec):
    """W0 = (LAM_MAX - 1) * (1 + 1/sqrt2), as an interval."""
    with mpmath.workdps(prec):
        lam = mpmath.iv.mpf(LAM_MAX.numerator) / mpmath.iv.mpf(LAM_MAX.denominator)
        return (lam - 1) * (1 + 1 / mpmath.iv.sqrt(mpmath.iv.mpf(2)))


def corner_box(corner, prec, widen=True):
    """The widened corner box in CONTAINER coordinates, as intervals."""
    s = mpmath.iv.mpf(S0.numerator) / mpmath.iv.mpf(S0.denominator)
    hi = 1 + (w0(prec) if widen else mpmath.iv.mpf(0))
    lo = mpmath.iv.mpf(0)
    if corner == "BL":
        return (lo, hi, lo, hi)
    if corner == "BR":
        return (s - hi, s - lo, lo, hi)
    if corner == "TR":
        return (s - hi, s - lo, s - hi, s - lo)
    if corner == "TL":
        return (lo, hi, s - hi, s - lo)
    raise ValueError(corner)


# ------------------------------------------------------------------ interval square geometry
def sq_frame(pose):
    """(centre, e1, e2) of the unit square at an interval pose (x, y, theta in degrees)."""
    x, y, th = pose
    t = th * mpmath.iv.pi / 180
    c, s = mpmath.iv.cos(t), mpmath.iv.sin(t)
    return (x, y), (c, s), (-s, c)


def sq_corners(pose):
    (cx, cy), (e1x, e1y), (e2x, e2y) = sq_frame(pose)
    half = mpmath.iv.mpf(1) / 2
    out = []
    for a in (1, -1):
        for b in (1, -1):
            out.append((cx + half * (a * e1x + b * e2x), cy + half * (a * e1y + b * e2y)))
    return out


def _iv_lo(v):
    return float(mpmath.mpf(v.a))


def _iv_hi(v):
    return float(mpmath.mpf(v.b))


def sign_iv(v):
    """+1 / -1 if the enclosure is strictly one-signed, else 0 (INDETERMINATE)."""
    if _iv_lo(v) > 0.0:
        return 1
    if _iv_hi(v) < 0.0:
        return -1
    return 0


def support(pose, u):
    """max over Q(pose) of <p, u>, as an interval."""
    (cx, cy), e1, e2 = sq_frame(pose)
    half = mpmath.iv.mpf(1) / 2
    d1 = e1[0] * u[0] + e1[1] * u[1]
    d2 = e2[0] * u[0] + e2[1] * u[1]
    return cx * u[0] + cy * u[1] + half * (abs(d1) + abs(d2))


def box_support(box, u):
    """max over the axis box (X0,X1,Y0,Y1) of <p, u>, for u an axis-aligned +-e."""
    X0, X1, Y0, Y1 = box
    sx = X1 * u[0] if _iv_lo(u[0]) >= 0 else X0 * u[0]
    sy = Y1 * u[1] if _iv_lo(u[1]) >= 0 else Y0 * u[1]
    return sx + sy


def _ivmax(a, b):
    return mpmath.iv.mpf([max(_iv_lo(a), _iv_lo(b)), max(_iv_hi(a), _iv_hi(b))])


def sq_box_gap2(pose, box):
    (cx, cy), e1, e2 = sq_frame(pose)
    axes = [(mpmath.iv.mpf(1), mpmath.iv.mpf(0)), (mpmath.iv.mpf(-1), mpmath.iv.mpf(0)),
            (mpmath.iv.mpf(0), mpmath.iv.mpf(1)), (mpmath.iv.mpf(0), mpmath.iv.mpf(-1)),
            e1, (-e1[0], -e1[1]), e2, (-e2[0], -e2[1])]
    best = None
    for u in axes:
        n = mpmath.iv.sqrt(u[0] * u[0] + u[1] * u[1])
        g = -(support(pose, u) + box_support(box, (-u[0], -u[1]))) / n
        best = g if best is None else _ivmax(best, g)
    return best


def sq_sq_gap(p, q):
    """max over the 4+4 normals of (separation) between Q(p) and Q(q).  > 0 <=> disjoint."""
    _, e1p, e2p = sq_frame(p)
    _, e1q, e2q = sq_frame(q)
    best = None
    for u in (e1p, (-e1p[0], -e1p[1]), e2p, (-e2p[0], -e2p[1]),
              e1q, (-e1q[0], -e1q[1]), e2q, (-e2q[0], -e2q[1])):
        g = -(support(p, u) + support(q, (-u[0], -u[1])))
        best = g if best is None else _ivmax(best, g)
    return best


def container_slack(pose):
    """min over the container's 4 walls of the clearance of Q(pose).  >= 0 <=> inside."""
    s = mpmath.iv.mpf(S0.numerator) / mpmath.iv.mpf(S0.denominator)
    best = None
    for u, lim in (((mpmath.iv.mpf(1), mpmath.iv.mpf(0)), s),
                   ((mpmath.iv.mpf(0), mpmath.iv.mpf(1)), s),
                   ((mpmath.iv.mpf(-1), mpmath.iv.mpf(0)), mpmath.iv.mpf(0)),
                   ((mpmath.iv.mpf(0), mpmath.iv.mpf(-1)), mpmath.iv.mpf(0))):
        v = (lim if _iv_lo(u[0] + u[1]) > 0 else -lim) - support(pose, u)
        best = v if best is None else mpmath.iv.mpf([min(_iv_lo(best), _iv_lo(v)),
                                                     min(_iv_hi(best), _iv_hi(v))])
    return best


# ------------------------------------------------------------------ data (read-only)
def t2_rows():
    rows = {}
    for f in sorted(glob.glob(os.path.join(A141, "results", "t2_cells_s*.jsonl"))):
        for ln in open(f, encoding="utf-8"):
            r = json.loads(ln)
            rows.setdefault(r["cell"], r)
    return rows


def twocrowd():
    return json.load(open(os.path.join(A141, "results", "t5_twocrowd.json"), encoding="utf-8"))


def ivpose(p):
    return tuple(mpmath.iv.mpf(Fraction(float(v)).numerator) /
                 mpmath.iv.mpf(Fraction(float(v)).denominator) for v in p)


def check_one(rec, row, prec=60):
    mpmath.mp.dps = prec
    mpmath.iv.dps = prec
    corner = rec["corner"]
    box = corner_box(corner, prec, widen=True)
    unw = corner_box(corner, prec, widen=False)
    F = ivpose(rec["free"])
    H = ivpose(rec["H"])
    j = rec.get("j", 0)
    b = row["boxes"][j]
    th = float(rec["H"][2])
    in_b = (b[0] <= float(rec["H"][0]) <= b[1] and b[2] <= float(rec["H"][1]) <= b[3]
            and (b[4] <= th <= b[5] or b[4] <= th % 90.0 <= b[5]))
    out = dict(cell=rec["cell"], corner=corner, j=j, box=b,
               free=rec["free"], H=rec["H"], claimed_gap=rec.get("gap"))
    out["pose_H_in_B"] = bool(in_b)
    quantities = dict(
        H_container=container_slack(H),
        free_container=container_slack(F),
        H_vs_widened=sq_box_gap2(H, box),
        free_vs_widened=sq_box_gap2(F, box),
        H_vs_unwidened=sq_box_gap2(H, unw),
        free_vs_unwidened=sq_box_gap2(F, unw),
        free_vs_H=sq_sq_gap(F, H),
    )
    for k, v in quantities.items():
        out[k] = [_iv_lo(v), _iv_hi(v)]
        out[k + "_sign"] = sign_iv(v)
    # verdicts.  gap < 0 (sign -1) means the interiors MEET.
    out["H_in_container"] = quantities["H_container"] and sign_iv(quantities["H_container"]) >= 0
    out["free_in_container"] = sign_iv(quantities["free_container"]) >= 0
    out["H_meets_widened"] = sign_iv(quantities["H_vs_widened"]) == -1
    out["free_meets_widened"] = sign_iv(quantities["free_vs_widened"]) == -1
    out["H_meets_unwidened"] = sign_iv(quantities["H_vs_unwidened"]) == -1
    out["disjoint"] = sign_iv(quantities["free_vs_H"]) == 1
    out["indeterminate"] = any(out[k + "_sign"] == 0 for k in quantities)
    out["SURVIVES"] = bool(out["pose_H_in_B"] and out["H_in_container"]
                           and out["free_in_container"] and out["H_meets_widened"]
                           and out["free_meets_widened"] and out["disjoint"])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", default="")
    ap.add_argument("--prec", type=int, default=60)
    ap.add_argument("--out", default=os.path.join(BASE, "results", "xwitness159.jsonl"))
    a = ap.parse_args()
    rows = t2_rows()
    recs = twocrowd()
    if a.cells:
        want = set(a.cells.split(","))
        recs = [r for r in recs if r["cell"] in want]
    out = []
    with open(a.out, "w", encoding="utf-8") as fh:
        for rec in recs:
            r = check_one(rec, rows[rec["cell"]], a.prec)
            if r["indeterminate"]:
                r = check_one(rec, rows[rec["cell"]], a.prec * 4)
            out.append(r)
            fh.write(json.dumps(r) + "\n")
            print("%-24s %s  H_in_B=%d Hbox=%+.6f freebox=%+.6f gap=%+.6f Hunw=%+.6f  %s"
                  % (r["cell"], r["corner"], r["pose_H_in_B"],
                     r["H_vs_widened"][1], r["free_vs_widened"][1], r["free_vs_H"][0],
                     r["H_vs_unwidened"][0],
                     "SURVIVES" if r["SURVIVES"] else "FAILS"), flush=True)
    n = sum(1 for r in out if r["SURVIVES"])
    print("\n%d / %d two-crowd witnesses survive the exact re-examination" % (n, len(out)))
    print("failure modes:", json.dumps({
        k: sum(1 for r in out if not r["SURVIVES"] and not r[k])
        for k in ("pose_H_in_B", "H_in_container", "free_in_container",
                  "H_meets_widened", "free_meets_widened", "disjoint")}))


if __name__ == "__main__":
    main()
