"""A165 T2 -- the FOUR-WALL CHORD-ROW PRODUCT: the cascade's steps (b) and (c), as a leaf.

The leaf
--------
Let `F` be the dilated family at `s0`, `H` the cell's conditioned square, and suppose K0-BLOCKED
holds, so each WIDENED corner box `C_c^w` is met by >= 2 squares of `F`.  By (R6) (A150 sec 1: the
widened corner boxes are `s0 - 2(1+w) = 1.826 > sqrt2` apart) no square meets two corner boxes, so
the four corner crowds are disjoint sets of squares.  Where `M(c) = 0` -- certified by A161's exact
`box_misses_cell_exact(B_H, C_c^w)` -- `H` is not among them either.

Fix an axis-parallel line `l`.  A144 LINE-1 gives, for the interior-disjoint family `F` inside
`[0, s0]^2`,

        SUM_{Q in F} |l n Q|   <=   s0 .

Every square of `F` whose pose is confined to a parameter box `B` contributes at least
`minchord(B, l)` (A144 LINE-2, `minchord_box`, exact).  Hence for a WALL `l` and the two corner
crowds it can reach (`top`: TR and TL; `right`: TR and BR; `bottom`: BL and BR; `left`: BL and TL)

  ROW(l)   minchord(B_H, l) + SUM_{the 2 boxes of crowd c1} + SUM_{the 2 boxes of crowd c2}  <=  s0

and a violation is a **(C) leaf**: the case is contradictory, with no LP.  This is the PI's step
(b) ("two TR meeters in the top strip each carry a chord >= 1, so at most ONE more square crosses")
and step (c) (the same row read at the left wall) in the form that composes: it is a constraint on
the EDGES of the four-corner cycle, so the surviving four-tuple count is a transfer-matrix
contraction exactly as in A150 sec 4, never an enumeration.

Soundness notes
---------------
* `minchord_box` is a certified LOWER bound; using it in a SUM that must stay `<= s0` is the sound
  direction.
* the five (or fewer) squares in a row are pairwise DISTINCT: (R6) for the two crowds, `M(c) = 0`
  for `H`.  Where `M(c) >= 1` the crowd may CONTAIN `H`; the case then carries one free box and
  `H`'s chord is still counted exactly once (`case.free` holds only the free boxes).
* nothing here needs the corner crowd to be free of `K'(H)` -- that was already used to build the
  cover, and it only shrinks the cover.

    python code/rowprod165.py --cell l1_104 --depth 8
"""
import argparse
import itertools
import json
import math
import os
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cas165 as K                                               # noqa: E402
import numpy as np                                               # noqa: E402
import guardline as GL                                           # noqa: E402
from caselp import Box                                           # noqa: E402
import cascade165 as CS                                          # noqa: E402

RES = os.path.join(K.BASE, "results")

# which two corner crowds a wall line can be fed by
WALLS = dict(top=("TR", "TL"), right=("TR", "BR"), bottom=("BL", "BR"), left=("BL", "TL"))


def cases_of(pr):
    """The case list at one corner: each case is the tuple of FREE cover-box indices.  With
    `M(c) = 0` every case is a pair; otherwise the mixed cases {H, one free box} are added."""
    out = [tuple(p) for p in pr["pairs"]]
    kinds = ["pair"] * len(out)
    for m in pr.get("mixed_cases", []):
        out.append(tuple(m))
        kinds.append("mixed")
    return out, kinds


def mc_table(boxes, lines):
    """float lower bounds: mc[line, box]"""
    T = np.zeros((len(lines), len(boxes)), np.float64)
    for i, l in enumerate(lines):
        for j, b in enumerate(boxes):
            T[i, j] = GL.minchord_box(b, l)["lo_float"]
    return T


def case_sums(T, cases):
    """S[line, case] = SUM of the case's free-box minchords."""
    S = np.zeros((T.shape[0], len(cases)), np.float64)
    for ci, cs in enumerate(cases):
        for b in cs:
            S[:, ci] += T[:, b]
    return S


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", default="l1_104")
    ap.add_argument("--depth", type=int, default=8)
    ap.add_argument("--nlines", type=int, default=32)
    ap.add_argument("--count", type=int, default=1, help="contract the 4-cycle for the total")
    ap.add_argument("--certs", type=int, default=6, help="exact certificates to emit per wall")
    a = ap.parse_args()

    cov = json.load(open(CS.cover_path(a.cell, a.depth), encoding="utf-8"))
    H = Box(*cov["boxes"][0])
    OB, CASES, KINDS = {}, {}, {}
    for c in K.CORNERS:
        pr = json.load(open(CS.pairs_path(a.cell, a.depth, c), encoding="utf-8"))
        OB[c] = [Box(*b) for b in cov["covers"][c]["open"]]
        CASES[c], KINDS[c] = cases_of(pr)
        print("%-3s %4d cover boxes, %6d cases (%s)" % (c, len(OB[c]), len(CASES[c]),
                                                        pr.get("case_family")), flush=True)

    # the canary's real case at each corner (the FREE meeter boxes of the Trump image), if any
    CAN = {}
    for h in cov.get("canary", {}).get("images", []):
        per = {}
        for c in K.CORNERS:
            free = tuple(sorted({m["box"] for m in h["corners"][c]["meeters"]
                                 if not m["is_H"] and m["box"] is not None}))
            # the real crowd may have more than two members; every 2-subset (or the 1-subset when
            # H is a member) is a case the real family reaches
            opts = []
            n_H = sum(1 for m in h["corners"][c]["meeters"] if m["is_H"])
            if n_H:
                opts += [(i,) for i in free]
            opts += [p for p in itertools.combinations_with_replacement(free, 2) if p[0] != p[1]]
            per[c] = [CASES[c].index(o) for o in opts if o in CASES[c]]
        CAN[h["image"]] = per
        print("canary %s real cases per corner: %s" % (h["image"],
              {c: len(per[c]) for c in K.CORNERS}), flush=True)

    LN = CS.wall_lines(a.nlines)
    out = dict(cell=a.cell, depth0=a.depth, nlines=a.nlines, s0=K.S0,
               n_cases={c: len(CASES[c]) for c in K.CORNERS},
               case_kinds={c: dict(pair=KINDS[c].count("pair"), mixed=KINDS[c].count("mixed"))
                           for c in K.CORNERS},
               walls={}, certs=[])
    EDGE = {}
    for wall, (c1, c2) in WALLS.items():
        t0 = time.time()
        lines = LN[wall]
        mcH = np.array([GL.minchord_box(H, l)["lo_float"] for l in lines])
        T1 = mc_table(OB[c1], lines)
        T2 = mc_table(OB[c2], lines)
        S1 = case_sums(T1, CASES[c1])
        S2 = case_sums(T2, CASES[c2])
        cap = K.S0 - mcH                                          # per-line budget for the crowds
        n1, n2 = S1.shape[1], S2.shape[1]
        alive = np.ones((n1, n2), bool)
        worst = np.full((n1, n2), -1e9, np.float32)
        S1f, S2f = S1.astype(np.float32), S2.astype(np.float32)
        CH = max(1, int(2e7 // max(1, n2)))                        # row chunk, ~20M floats
        for lo in range(0, n1, CH):
            hi = min(n1, lo + CH)
            wblk = worst[lo:hi]
            ablk = alive[lo:hi]
            for i in range(len(lines)):
                viol = S1f[i][lo:hi, None] + S2f[i][None, :] - np.float32(cap[i])
                np.maximum(wblk, viol, out=wblk)
                ablk &= viol <= 0.0
        EDGE[wall] = alive
        n = alive.size
        k = int(n - alive.sum())
        row = dict(corners=[c1, c2], n_pairs=int(n), n_killed=k, frac_killed=k / max(1, n),
                   max_violation=float(worst.max()),
                   line_lo=float(lines[0].off), line_hi=float(lines[-1].off),
                   wall_s=round(time.time() - t0, 1),
                   per_case_alive_c1=int((alive.any(axis=1)).sum()),
                   per_case_alive_c2=int((alive.any(axis=0)).sum()))
        out["walls"][wall] = row
        print("wall %-7s (%s,%s): %d x %d combos, killed %d (%.2f%%), max violation %+.4f, "
              "%.1fs" % (wall, c1, c2, S1.shape[1], S2.shape[1], k, 100.0 * k / max(1, n),
                         worst.max(), row["wall_s"]), flush=True)

        # CANARY: every real (case at c1, case at c2) of a Trump image must SURVIVE this row
        for img, per in CAN.items():
            tot = surv = 0
            for p in per[c1]:
                for q in per[c2]:
                    tot += 1
                    surv += int(bool(alive[p, q]))
            row.setdefault("canary", {})[img] = dict(combos=tot, survive=surv,
                                                     verdict=("PASS" if surv == tot else "FAIL"))
            print("   CANARY %s on the %s row: %d/%d real case pairs survive -- %s"
                  % (img, wall, surv, tot, "PASS" if surv == tot else "*** FAIL ***"), flush=True)

        # exact certificates for a few of the killed combos
        ii, jj = np.nonzero(~alive)
        order = np.argsort(-worst[ii, jj])
        for t in order[:a.certs]:
            p, q = int(ii[t]), int(jj[t])
            bxs = [H] + [OB[c1][b] for b in CASES[c1][p]] + [OB[c2][b] for b in CASES[c2][q]]
            best = None
            for l in lines:
                r = K.chord_row(bxs, l)
                if best is None or Fr(r["rhs"]) < Fr(best["rhs"]):
                    best = r
            out["certs"].append(dict(
                wall=wall, corners=[c1, c2], case1=list(CASES[c1][p]), case2=list(CASES[c2][q]),
                boxes=[K.bx_json(b) for b in bxs], row=best,
                claim="minchord sum on the line exceeds s0: LINE-1 violated, (C) leaf",
                exact_rhs_negative=bool(Fr(best["rhs"]) < 0)))

    # the four-cycle contraction TR -(top)- TL -(left)- BL -(bottom)- BR -(right)- TR
    if a.count:
        t0 = time.time()
        A_top = EDGE["top"].astype(np.float32)                      # TR x TL
        A_left = EDGE["left"][:, :]                                 # BL x TL  -> want TL x BL
        A_left = A_left.T.astype(np.float32)
        A_bot = EDGE["bottom"].astype(np.float32)                   # BL x BR
        A_right = EDGE["right"].astype(np.float32)                   # TR x BR -> want BR x TR
        try:
            N = A_left @ A_bot                                       # TL x BR
            Mx = A_top @ N                                           # TR x BR
            total = float((Mx * A_right).sum())
            out["four_cycle"] = dict(total=total, log10=(math.log10(total) if total > 0 else None),
                                     wall_s=round(time.time() - t0, 1))
        except MemoryError:
            out["four_cycle"] = dict(error="MemoryError")
        print("four-cycle survivors:", out.get("four_cycle"), flush=True)

    p = os.path.join(RES, "rowprod_%s.json" % CS.tag(a.cell, a.depth))
    K.jdump(out, p)
    np.savez_compressed(os.path.join(RES, "rowprod_edges_%s.npz" % CS.tag(a.cell, a.depth)),
                        **{w: EDGE[w] for w in WALLS})
    print("wrote", p, flush=True)


if __name__ == "__main__":
    main()
