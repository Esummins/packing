"""A154 independent re-checks (no LP, no verifier).

1. SEPARATION, exactly: s0 - 2 a_w > sqrt2 in rationals (so no unit square meets two widened
   corner boxes) -- (R6)(i).
2. The incidence oracle, independently: for every placement of every stored dual packing used by
   the screen, recompute "Q meets the widened box at corner c" by a SAT test between the rotated
   unit square and the axis-aligned box (shares no code with corner85.f_min_max) and compare.
3. The realised multiplicity: max over all those placements of #corners met (must be <= 1).

Writes results/verify154.json.
"""
import json
import math
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a154lib as L  # noqa: E402


def sat_meets_box(cx, cy, th, a):
    """does the CLOSED unit square centred (cx,cy) at tilt th meet the closed box [0,a]^2?
    SAT over the 4 distinct axes (box: e1, e2; square: its two edge normals)."""
    c, s = math.cos(th), math.sin(th)
    ex, ey = (c / 2.0, s / 2.0), (-s / 2.0, c / 2.0)
    sq = [(cx + ex[0] * i + ey[0] * j, cy + ex[1] * i + ey[1] * j)
          for (i, j) in ((1, 1), (1, -1), (-1, -1), (-1, 1))]
    bx = [(0.0, 0.0), (a, 0.0), (a, a), (0.0, a)]
    for ax in ((1.0, 0.0), (0.0, 1.0), (c, s), (-s, c)):
        p1 = [ax[0] * p[0] + ax[1] * p[1] for p in sq]
        p2 = [ax[0] * p[0] + ax[1] * p[1] for p in bx]
        if max(p1) < min(p2) - 1e-12 or max(p2) < min(p1) - 1e-12:
            return False
    return True


def main():
    fam = L.get_fam(0.0, log=lambda *a: None)
    aw_r = Fr(str(fam["a"]))
    s0_r = Fr(L.S_RAT)
    gap = s0_r - 2 * aw_r
    sep_ok = gap * gap > 2                       # gap > sqrt2, exact in rationals
    aw = float(aw_r)

    n_place = n_pack = 0
    disagree = []
    maxmult = 0
    seen = set()
    for f in ("screen154.jsonl", "screenall154.jsonl"):
        p = os.path.join(L.RES, f)
        if not os.path.exists(p):
            continue
        for ln in open(p, encoding="utf-8"):
            r = json.loads(ln)
            path = os.path.join(L.ROOT, r["lp"])
            if path in seen:
                continue
            seen.add(path)
            d = json.load(open(path, encoding="utf-8"))
            n_pack += 1
            for q in d.get("packing") or []:
                n_place += 1
                cx, cy, th = float(q["cx"]), float(q["cy"]), float(q["theta"])
                mult = 0
                for c in L.CORNERS:
                    u, v, t = L.to_corner(cx, cy, th, c)
                    a_hit = L.mu_corner(cx, cy, th, c) <= aw
                    s_hit = sat_meets_box(u, v, t, aw)
                    if a_hit != s_hit:
                        disagree.append(dict(lp=r["lp"], corner=c, cx=cx, cy=cy, th=th,
                                             mu=L.mu_corner(cx, cy, th, c), fmm=a_hit, sat=s_hit))
                    mult += int(a_hit)
                maxmult = max(maxmult, mult)

    out = dict(a_w=str(aw_r), s0=str(s0_r), gap=str(gap), gap_float=float(gap),
               sqrt2=math.sqrt(2.0), separation_exact_ok=bool(sep_ok),
               n_dual_packings=n_pack, n_placements=n_place,
               oracle_disagreements=len(disagree), disagreement_sample=disagree[:5],
               max_corner_multiplicity=maxmult,
               ALL_OK=bool(sep_ok and not disagree and maxmult <= 1))
    json.dump(out, open(os.path.join(L.RES, "verify154.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "disagreement_sample"}, indent=1))


if __name__ == "__main__":
    main()
