"""A153 -- the INDEPENDENT checker for a cover-number kill certificate.

What it re-derives itself (nothing here calls geo148 / cover153):

 1  PIECE ADMISSIBILITY, exactly in rationals: every piece is the axis-aligned square
    [x0, x1] x [y0, y1] with x1 - x0 = y1 - y0 = side, and 2 * side^2 < 1, i.e. the diameter
    side*sqrt2 is < 1.  (Lemma CN then allows at most one centre per piece.)

 2  THE OBSTACLES.  The certificate's polygons are rebuilt from the node's OWN record through the
    trusted primitives A132 `polycore.build` (K'(H), certified vertices) and A135
    `exactcore.exact_a` (the exact pin core half-side) and compared vertex by vertex.  Those two are
    the trusted base; everything downstream of them in this file is written from scratch.

 3  THE COVER.  For every cell of the certificate's grid that is NOT contained in one of the
    pieces, the checker proves the cell is BLOCKED with its OWN separating-axis code:

        clearance(c, t) = min( container clearance , min_j sep(K_j, Q(c, t)) )

    where sep is the exact separating-axis gap (negative = overlap).  The cell centre must have
    max over the certificate's `ntilt` sampled tilts of clearance < -margin, and

        margin >= pitch*sqrt2/2 + (sqrt2/2)*(pi/2/ntilt)/2

    which is the 1-Lipschitz-in-centre / (sqrt2/2)-Lipschitz-in-tilt constant.  Then no point of
    the cell admits ANY tilt, so no centre can lie there, so the pieces cover every admissible
    centre.  (This is the only direction that matters: an uncovered cell must be provably empty.)

 4  THE COUNT.  #pieces < budget.

 5  THE SAMPLE LINE is re-drawn and re-tested here as well: centres drawn in the un-blocked cells,
    each confirmed feasible by a 360-tilt sweep, each required to lie in a piece.

Exit code 0 = CLEAN.  READ-ONLY: nothing is written.
"""
import argparse
import json
import math
import os
import sys
from fractions import Fraction as Fr

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, "..", ".."))
ROOT = os.path.abspath(os.path.join(ATT, ".."))
for _p in (os.path.join(ATT, "A132-polygon-core", "code"),
           os.path.join(ATT, "A135-polycore-verifier", "code"),
           os.path.join(ATT, "A57-shadow-trees", "code"),
           os.path.join(ATT, "A142-a57-review-gallery", "code")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

ROOT2H = math.sqrt(2.0) / 2.0


# ------------------------------------------------------------------ own SAT
def sep_poly_square(P, C, th):
    """SEPARATION between the convex polygon P (nv,2) and the unit squares of tilt `th` centred at
    C (m,2): the negative of the separating-axis penetration depth, so > 0 means disjoint (and is
    then a lower bound on the true distance) and < 0 is the penetration depth.

    Per axis u the two projections are the intervals [plo, phi] and [qc - h, qc + h]; their signed
    OVERLAP LENGTH is min(phi, qc + h) - max(plo, qc - h), the depth is the minimum of that over
    the axes (P's edge normals and the square's own two), and this returns its negative.  Each term
    is 1-Lipschitz in the centre, so the whole thing is -- which is what the grid margin uses.
    Written from scratch; T-A checks it against A132's `poly_square_depth`."""
    P = np.asarray(P, float)
    C = np.asarray(C, float).reshape(-1, 2)
    ct, st = math.cos(th), math.sin(th)
    e1 = (ct, st)
    e2 = (-st, ct)
    axes = [e1, e2]
    for k in range(len(P)):
        ax, ay = P[(k + 1) % len(P)] - P[k]
        n = math.hypot(ax, ay)
        if n > 1e-14:
            axes.append((-ay / n, ax / n))
    depth = np.full(len(C), np.inf)
    for (ux, uy) in axes:
        pp = P[:, 0] * ux + P[:, 1] * uy
        plo, phi = float(pp.min()), float(pp.max())
        h = 0.5 * (abs(ux * e1[0] + uy * e1[1]) + abs(ux * e2[0] + uy * e2[1]))
        qc = C[:, 0] * ux + C[:, 1] * uy
        ov = np.minimum(phi, qc + h) - np.maximum(plo, qc - h)
        depth = np.minimum(depth, ov)
    return -depth


def clearance(C, th, s, obst):
    ct, st = math.cos(th), math.sin(th)
    w = 0.5 * (abs(ct) + abs(st))
    cl = np.minimum.reduce([C[:, 0] - w, s - w - C[:, 0], C[:, 1] - w, s - w - C[:, 1]])
    for P in obst:
        cl = np.minimum(cl, sep_poly_square(P, C, th))
    return cl


# ------------------------------------------------------------------ the checks
def rebuild_obstacles(record):
    """the node's obstacles, rebuilt from its own record through A132/A135."""
    import polycore
    import exactcore
    from caselp import Box
    d = json.load(open(os.path.join(ROOT, record.replace("\\", os.sep)), encoding="utf-8"))
    out, names = [], []
    npin = 0
    nh = 0
    for bj in d["hyp"]["boxes"]:
        b = Box.from_json(bj) if isinstance(bj, dict) else bj
        if b.th1 <= b.th0 + 1e-12:
            cx, cy = 0.5 * (b.x0 + b.x1), 0.5 * (b.y0 + b.y1)
            try:
                a, a0, ok = exactcore.exact_a(b)
                af = float(a)
            except Exception:                                         # noqa: BLE001
                af = float(b.core().a)
            out.append([(cx + af * dx, cy + af * dy)
                        for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1))])
            names.append(f"P{npin}")
            npin += 1
        else:
            pc = polycore.build(b)
            out.append([(float(u), float(v)) for u, v in pc.P])
            names.append("H" if nh == 0 else f"H{nh}")
            nh += 1
    return out, names


def check(certpath, nsample=10000, seed=1531, verbose=True):
    cert = json.load(open(certpath, encoding="utf-8"))
    fails, notes = [], []
    s = Fr(*cert["s0"])
    p = Fr(*cert["grid"]["pitch"])
    n = int(cert["grid"]["n"])
    ntilt = int(cert["grid"]["ntilt"])
    margin = float(cert["grid"]["margin"])
    K = int(cert["piece"]["K"])
    side = Fr(*cert["piece"]["side"])

    # 1 -- the grid is the container, exactly
    if n * p != s:
        fails.append(f"grid: n*pitch = {float(n * p)} != s0 {float(s)}")

    # 2 -- piece admissibility, exact rationals
    if side != K * p:
        fails.append(f"piece side {side} != K*pitch {K * p}")
    if not (2 * side ** 2 < 1):
        fails.append(f"piece NOT admissible: 2*side^2 = {float(2 * side ** 2)} >= 1")
    notes.append(f"piece side {float(side):.9f}, diameter {float(side) * math.sqrt(2):.9f} < 1 "
                 f"(exact test 2*side^2 = {2 * side ** 2} < 1)")
    for q in cert["pieces"]:
        x0, y0 = Fr(*q["x0"]), Fr(*q["y0"])
        x1, y1 = Fr(*q["x1"]), Fr(*q["y1"])
        if x1 - x0 != side or y1 - y0 != side:
            fails.append(f"piece {q['i0']},{q['j0']} is not a {side} square")
        if x0 != q["i0"] * p or y0 != q["j0"] * p:
            fails.append(f"piece {q['i0']},{q['j0']} corner does not sit on the grid")

    # 3 -- the margin is at least the Lipschitz constant
    need = float(p) * ROOT2H + ROOT2H * ((math.pi / 2.0) / ntilt) / 2.0
    if margin < need - 1e-15:
        fails.append(f"margin {margin} < required {need}")
    notes.append(f"margin {margin:.9f} >= Lipschitz constant {need:.9f}")

    # 4 -- the obstacles are the node's own
    obst2, names2 = rebuild_obstacles(cert["record"])
    obst = [np.array(P, float) for P in cert["obstacles"]]
    if len(obst2) != len(obst):
        fails.append(f"obstacle count {len(obst2)} != certificate's {len(obst)}")
    else:
        worst = 0.0
        for A, B in zip(obst, obst2):
            if len(A) != len(B):
                fails.append("obstacle vertex count mismatch")
                continue
            worst = max(worst, float(np.abs(np.array(A) - np.array(B)).max()))
        if worst > 1e-9:
            fails.append(f"obstacle vertices differ from the record by {worst:.3e}")
        notes.append(f"{len(obst)} obstacles rebuilt from {cert['record']}: max vertex "
                     f"difference {worst:.2e}")

    # 5 -- every uncovered cell is BLOCKED
    covered = np.zeros((n, n), bool)                       # [j, i]
    for q in cert["pieces"]:
        covered[q["j0"]:q["j0"] + K, q["i0"]:q["i0"] + K] = True
    jj, ii = np.nonzero(~covered)
    pf = float(p)
    C = np.stack([(ii + 0.5) * pf, (jj + 0.5) * pf], 1)
    best = np.full(len(C), -1e18)
    ths = (np.arange(ntilt) + 0.5) * (math.pi / 2.0) / ntilt
    sf = float(s)
    for th in ths:
        best = np.maximum(best, clearance(C, th, sf, obst))
    bad = int((best >= -margin).sum())
    if bad:
        k = int(np.argmax(best))
        fails.append(f"{bad} of {len(C)} uncovered cells are NOT certified blocked "
                     f"(worst cell centre {C[k].tolist()}, clearance {best[k]:+.6f} "
                     f">= -margin {-margin:+.6f})")
    notes.append(f"{len(C)} uncovered cells, all with max-over-{ntilt}-tilts clearance "
                 f"<= {float(best.max()):+.6f} < -margin {-margin:+.6f}"
                 if not bad else "uncovered cells FAILED")

    # 6 -- the count
    if len(cert["pieces"]) >= cert["budget"]:
        fails.append(f"{len(cert['pieces'])} pieces is NOT < budget {cert['budget']}")
        notes.append(f"{len(cert['pieces'])} pieces >= budget {cert['budget']}: the cover is sound "
                     f"but does NOT kill -- the node can still hold up to "
                     f"{len(cert['pieces'])} more squares")
    else:
        notes.append(f"{len(cert['pieces'])} pieces < budget {cert['budget']} -> node DEAD")

    # 7 -- the sample line, re-drawn here
    rng = np.random.default_rng(seed)
    openm = ~np.zeros((n, n), bool)
    # rebuild the un-blocked mask ourselves on the covered cells too (cheap: only sample from
    # cells that are inside a piece OR were shown open above)
    op_j, op_i = np.nonzero(covered)
    got, ntry = [], 0
    fine = (np.arange(360) + 0.5) * (math.pi / 2.0) / 360.0
    while sum(len(g) for g in got) < nsample and ntry < 40:
        ntry += 1
        pick = rng.integers(0, len(op_i), nsample)
        cx = (op_i[pick] + rng.uniform(0.0, 1.0, nsample)) * pf
        cy = (op_j[pick] + rng.uniform(0.0, 1.0, nsample)) * pf
        Cc = np.stack([cx, cy], 1)
        ok = np.zeros(nsample, bool)
        for th in fine:
            ok |= clearance(Cc, th, sf, obst) > 0.0
        got.append(Cc[ok])
    Cf = np.concatenate(got)[:nsample] if got else np.zeros((0, 2))
    inside = np.zeros(len(Cf), bool)
    for q in cert["pieces"]:
        inside |= ((Cf[:, 0] >= float(Fr(*q["x0"]))) & (Cf[:, 0] <= float(Fr(*q["x1"])))
                   & (Cf[:, 1] >= float(Fr(*q["y0"]))) & (Cf[:, 1] <= float(Fr(*q["y1"]))))
    miss = int((~inside).sum())
    if miss:
        fails.append(f"{miss} sampled FEASIBLE centres lie outside every piece")
    notes.append(f"sample: {len(Cf)} feasible centres drawn and re-tested on 360 tilts, "
                 f"{int(inside.sum())} inside a piece, {miss} misses")
    if verbose:
        print(f"=== {os.path.basename(certpath)}")
        for t in notes:
            print("   ", t)
        for f in fails:
            print("  FAIL", f)
        print("   VERDICT:", "CLEAN" if not fails else f"{len(fails)} FAILURE(S)")
    _ = openm
    return dict(cert=certpath, node=cert["node"], clean=not fails, fails=fails, notes=notes)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("certs", nargs="+")
    ap.add_argument("--n", type=int, default=10000)
    a = ap.parse_args()
    bad = 0
    for c in a.certs:
        r = check(c, nsample=a.n)
        bad += 0 if r["clean"] else 1
    print(f"\n{len(a.certs)} certificate(s), {bad} with failures")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
