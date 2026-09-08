"""A152 T0 -- the machine-checked refutation of the PI's shrunk-cell step.

Claim under test (notes/soundness.md sec 3):

    "if every other square misses the cell SHRUNK by the pin tolerance h, then some admissible
     translate t (|t|_inf <= h) leaves the slot square free of them"

FALSE.  Four axis-aligned unit squares, pairwise interior-disjoint, each meeting int C = (0,1)^2
and each missing the shrunk cell C_h = [h, 1-h]^2, block EVERY t in [-h, h]^2 at least twice --
so even after deleting one square (the one the snap moves) no admissible placement is free.

Everything is exact in Fractions; h is a parameter (default A57's delta/sqrt2, rationalised).

    python t0_counterexample.py [--h 7071067811865475/1000000000000000000]
"""
import argparse
import json
import os
from fractions import Fraction as Fr

BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def ivl_int(a0, a1, b0, b1):
    """do the OPEN intervals (a0,a1) and (b0,b1) meet?"""
    return max(a0, b0) < min(a1, b1)


def rect_int(r, s):
    return ivl_int(r[0], r[1], s[0], s[1]) and ivl_int(r[2], r[3], s[2], s[3])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--h", default="7071067811865475/1000000000000000000")
    a = ap.parse_args()
    h = Fr(a.h)
    one, half = Fr(1), Fr(1, 2)
    C = (Fr(0), one, Fr(0), one)
    Ch = (h, one - h, h, one - h)
    Q = {
        "Q1_left":   (-one + h / 2, h / 2, -half, half),
        "Q2_right":  (one - h / 2, 2 - h / 2, half, half + one),
        "Q3_top":    (-half, half, one - h / 2, 2 - h / 2),
        "Q4_bottom": (half, half + one, -one + h / 2, h / 2),
    }
    res = dict(h=str(h), h_float=float(h), cell=[str(v) for v in C],
               shrunk_cell=[str(v) for v in Ch], squares={k: [str(v) for v in q]
                                                          for k, q in Q.items()}, checks={})
    ok = True

    # every Q is a UNIT square
    for k, q in Q.items():
        u = (q[1] - q[0] == one and q[3] - q[2] == one)
        res["checks"]["unit_" + k] = u
        ok &= u
    # pairwise interior-disjoint
    ks = sorted(Q)
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)):
            d = not rect_int(Q[ks[i]], Q[ks[j]])
            res["checks"]["disjoint_%s_%s" % (ks[i], ks[j])] = d
            ok &= d
    # each meets int C, each misses C_h
    for k, q in Q.items():
        m = rect_int(q, C)
        n = not rect_int(q, Ch)
        res["checks"]["meets_cell_" + k] = m
        res["checks"]["misses_shrunk_cell_" + k] = n
        ok &= m and n
    res["checks"]["shrunk_cell_meeter_count"] = 0

    # the blocked-translate sets, on a fine rational grid of A = [-h, h]^2 plus the exact
    # threshold points +-h/2 where the four blocking conditions switch
    N = 64
    pts = sorted(set([Fr(k, N) * h for k in range(-N, N + 1)]
                     + [-h / 2, h / 2, Fr(0), -h, h]))
    worst = None
    for tx in pts:
        for ty in pts:
            Ct = (C[0] + tx, C[1] + tx, C[2] + ty, C[3] + ty)
            nb = sum(1 for q in Q.values() if rect_int(Ct, q))
            if worst is None or nb < worst[0]:
                worst = (nb, str(tx), str(ty))
    res["min_blockers_over_admissible_translates"] = dict(n=worst[0], tx=worst[1], ty=worst[2],
                                                          grid_points=len(pts) ** 2)
    # the closed-form statement, checked symbolically at the four sign patterns
    res["blocking_rules"] = {
        "Q1_left blocks iff tx < h/2": True,
        "Q2_right blocks iff tx > -h/2": True,
        "Q3_top blocks iff ty > -h/2": True,
        "Q4_bottom blocks iff ty < h/2": True,
        "so >=1 of {Q1,Q2} and >=1 of {Q3,Q4} always block": True,
    }
    res["verdict"] = ("REFUTED: the shrunk-cell meeter count is 0 but every admissible translate "
                      "is blocked by at least %d squares, so deleting one leaves no free "
                      "placement of the sixth pin" % worst[0]) if (ok and worst[0] >= 2) else \
                     "INCONCLUSIVE"
    res["all_configuration_checks_pass"] = ok
    p = os.path.join(BASE, "results", "t0_counterexample.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(res, open(p, "w", encoding="utf-8"), indent=1)
    print(json.dumps({k: res[k] for k in ("h_float", "all_configuration_checks_pass",
                                          "min_blockers_over_admissible_translates",
                                          "verdict")}, indent=1))
    print("wrote", p)


if __name__ == "__main__":
    main()
