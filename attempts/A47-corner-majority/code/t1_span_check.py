#!/usr/bin/env python3
"""
A47 leg (a) / TASK 1 -- permanent exact-rational verification of the window arithmetic of
Theorem T1 (attempts/A47-corner-majority/notes/theory.md, section 1).

WHAT IS CHECKED (all with Python Fractions; no floats enter any decision)

  T1 says the wall-to-wall span of a flush-free thin chain is exactly

        S(o, r) = o * sqrt(2) + r          (o >= 2 tilted-45 squares, r >= 0 class-0 squares)

  and the certified live window of side lengths for s(11) is

        W = [ 382/100 , 969271/250000 ]    ( = [3.82, s0], s0 = 3.877084 ).

  Claim (Corollary T1a).  For integers o >= 2, r >= 0 with o + r <= 11 (a chain has at most 11
  squares), S(o,r) meets W  <=>  (o,r) = (2,1).

  Certification.  Fix rationals r2lo < sqrt(2) < r2hi with r2lo^2 < 2 < r2hi^2 (verified exactly
  here, 18 significant digits).  Then

        S(o,r) in [ o*r2lo + r , o*r2hi + r ]   =: [lo(o,r), hi(o,r)]      (o >= 0)

  and the two decisions are exact:
     * "S(o,r) is NOT in W"  is certified by   hi(o,r) < 382/100   or   lo(o,r) > 969271/250000.
     * "S(o,r) IS in W"      is certified by   382/100 <= lo(o,r)  and  hi(o,r) <= 969271/250000.
  Every (o,r) in range is decided by one of the two (the enclosure width o*(r2hi-r2lo) <= 11e-18
  is far below the distance of every S(o,r) from the endpoints of W), so the enumeration is
  complete and the answer is exact.

  Additionally (used verbatim in the theory notes):
        S(2,2) = 2 sqrt2 + 2 > s0     and     S(3,0) = 3 sqrt2 > s0,
  certified by lo(2,2) > s0 and lo(3,0) > s0.

OUTPUT: results/t1_span_check.json   {"pass": true, "solutions": [[2,1]], ...}
"""
import json
import os
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                      # attempts/A47-corner-majority

# ---- rational enclosure of sqrt(2): 18 significant digits ----------------------------------
DEN = 10 ** 18
R2LO = F(1414213562373095048, DEN)
R2HI = F(1414213562373095049, DEN)

# ---- the live window ------------------------------------------------------------------------
S_LO = F(382, 100)                 # 3.82   (certified lower bound on s(11))
S0 = F(969271, 250000)             # 3.877084 = certified upper bound (Trump)

NMAX = 11                          # a chain of the 11-square packing has at most 11 squares


def span_bounds(o, r):
    """exact rational enclosure [lo, hi] of S(o,r) = o*sqrt2 + r."""
    return o * R2LO + r, o * R2HI + r


def main():
    assert R2LO ** 2 < 2 < R2HI ** 2, "sqrt(2) enclosure is wrong"
    assert R2LO < R2HI

    solutions = []
    decided = []
    undecided = []
    for o in range(2, NMAX + 1):
        for r in range(0, NMAX - o + 1):
            lo, hi = span_bounds(o, r)
            if hi < S_LO:
                verdict = "below"
            elif lo > S0:
                verdict = "above"
            elif S_LO <= lo and hi <= S0:
                verdict = "inside"
                solutions.append([o, r])
            else:
                verdict = "UNDECIDED"
                undecided.append([o, r])
            decided.append({"o": o, "r": r, "lo": str(lo), "hi": str(hi),
                            "approx": float(lo), "verdict": verdict})

    # explicit checks quoted in theory.md
    lo22, _ = span_bounds(2, 2)
    lo30, _ = span_bounds(3, 0)
    s22_gt_s0 = lo22 > S0
    s30_gt_s0 = lo30 > S0

    # the unique solution, for the record
    lo21, hi21 = span_bounds(2, 1)

    ok = (solutions == [[2, 1]]) and not undecided and s22_gt_s0 and s30_gt_s0
    out = {
        "pass": bool(ok),
        "claim": ("For integers o>=2, r>=0, o+r<=11, the flush-free thin-chain span "
                  "S(o,r)=o*sqrt2+r meets the live window [3.82, 969271/250000] only at (o,r)=(2,1); "
                  "s* = 2 sqrt2 + 1."),
        "solutions": solutions,
        "undecided": undecided,
        "bounds_used": {
            "sqrt2_lo": str(R2LO), "sqrt2_hi": str(R2HI),
            "sqrt2_lo_sq_lt_2": bool(R2LO ** 2 < 2), "sqrt2_hi_sq_gt_2": bool(R2HI ** 2 > 2),
            "window_lo": str(S_LO), "window_hi": str(S0),
            "window_lo_float": float(S_LO), "window_hi_float": float(S0),
            "o_range": [2, NMAX], "r_range": [0, NMAX], "constraint": "o + r <= 11",
        },
        "s_star": {"lo": str(lo21), "hi": str(hi21), "approx": float(lo21),
                   "exact": "2*sqrt(2) + 1"},
        "extra_checks": {
            "S(2,2) > s0": bool(s22_gt_s0), "S(2,2)_lo": str(lo22), "S(2,2)_approx": float(lo22),
            "S(3,0) > s0": bool(s30_gt_s0), "S(3,0)_lo": str(lo30), "S(3,0)_approx": float(lo30),
        },
        "enumeration": decided,
        "arithmetic": "exact (fractions.Fraction); floats appear only in *_approx display fields",
    }
    outdir = os.path.join(ROOT, "results")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "t1_span_check.json")
    with open(path, "w") as fh:
        json.dump(out, fh, indent=1)
    print(f"pass = {ok}; solutions = {solutions}; undecided = {undecided}")
    print(f"S(2,1) in [{float(lo21):.15f}, {float(hi21):.15f}]  (= s*)")
    print(f"S(2,2) >= {float(lo22):.9f} > s0 : {s22_gt_s0};  S(3,0) >= {float(lo30):.9f} > s0 : {s30_gt_s0}")
    print(f"written {path}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
