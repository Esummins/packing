"""Synthetic measure certificates for testing certs/verify_measure.py (A08).

  centre_s1.99.json   one atom (s/2,s/2) weight 1 at s=1.99  -> must PASS  (s(2) >= 1.99)
  centre_s2.01.json   same at s=2.01                          -> must FAIL (axis-aligned corner square misses centre)
  gobel_pass.json     Goebel 4-point set at s = 2+1/sqrt2 - 1e-3 (rational approx), weights 1 -> PASS
  gobel_fail.json     same points at s = 2.72                                          -> FAIL
  gobel_half.json     Goebel points with weights 1/2 plus centre weight 1/2 ... (total 2.5) at s=2.70:
                      is that a measure certificate? (exploratory: expected FAIL near corners)
  a05_10pt.json       A05's 10-point unavoidable set (weights 1, total 10) at its s0 -> PASS
"""
import json
import os
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "tests")
os.makedirs(OUT, exist_ok=True)


def dump(name, s, atoms, weights, note, n=11, symmetry=None):
    d = {"s": str(s), "n": n,
         "atoms": [[str(x), str(y)] for x, y in atoms],
         "weights": [str(w) for w in weights],
         "total": str(sum(weights, F(0))),
         "provenance": {"generator": "attempts/A08-measure-verify/make_tests.py", "note": note}}
    if symmetry:
        d["symmetry"] = symmetry
    with open(os.path.join(OUT, name), "w") as fh:
        json.dump(d, fh, indent=1)
    print("wrote", name, "s =", s, "total =", d["total"])


# (i) single centre atom
for s in (F("1.99"), F("2.01"), F(2)):
    dump(f"centre_s{float(s):.2f}.json", s, [(s / 2, s / 2)], [F(1)],
         "single atom at the centre; unavoidable iff s <= 2 (equality: corner square touches it)", n=2)

# (ii) Goebel's 4 points (1,1),(1,s-1),(s-1,1),(s-1,s-1): unavoidable iff s <= 2 + 1/sqrt2 = 2.70710678...
def gobel(s):
    return [(F(1), F(1)), (F(1), s - 1), (s - 1, F(1)), (s - 1, s - 1)]

s_pass = F("2.70610678")            # 2 + 1/sqrt2 - 1e-3 to 8 digits (below the exact critical value)
dump("gobel_pass.json", s_pass, gobel(s_pass), [F(1)] * 4, "Goebel 4-point set, s below 2+1/sqrt2", n=5)
s_fail = F("2.72")
dump("gobel_fail.json", s_fail, gobel(s_fail), [F(1)] * 4, "Goebel 4-point set, s above 2+1/sqrt2", n=5)
# same, via D4 symmetry expansion of a single representative
dump("gobel_pass_D4.json", s_pass, [(F(1), F(1))], [F(1)], "Goebel set given as one D4 orbit representative",
     n=5, symmetry="D4")
# very close to critical: 2+1/sqrt2 = 2.7071067811865475...
dump("gobel_close.json", F("2.7071"), gobel(F("2.7071")), [F(1)] * 4, "Goebel set, 6.8e-6 below critical", n=5)

# (iii) A05's 10-point set at its certified s0
src = os.path.join(HERE, "..", "A05-unavoidable-opt", "UNAVOIDABLE_10pt_3.7416.json")
if os.path.exists(src):
    d = json.load(open(src))
    s0 = F(d["s0"])
    pts = [(F(x), F(y)) for x, y in d["points"]]
    dump("a05_10pt.json", s0, pts, [F(1)] * len(pts), "A05 10-point unavoidable set (integral measure)")
    # and pushed slightly above its numerical optimum: should FAIL
    s1 = s0 + F("0.02")
    dump("a05_10pt_push.json", s1, pts, [F(1)] * len(pts), "A05 10-point set at s0+0.02 (expected FAIL)")

# (iv) fractional example: 4 Goebel points weight 1/2 each + centre 1... total 3 < 5, s = 2.5:
#   any unit square in [0,2.5]^2 contains the centre? no (corner square [0,1]^2 misses (1.25,1.25)).
#   corner square contains (1,1) [w=1/2] only -> mass 1/2 < 1 -> FAIL. Included as a FAIL test with holes.
s = F("2.5")
dump("frac_fail.json", s, gobel(s) + [(s / 2, s / 2)], [F(1, 2)] * 4 + [F(1)],
     "fractional toy: expected FAIL (corner square has mass 1/2)", n=5)
# fractional PASS example: two copies of Goebel-type structure ... use s=2 with atoms (1,1) w=1/2 and (1,1) w=1/2
dump("frac_pass.json", F("1.9"), [(F("0.95"), F("0.95")), (F("0.95"), F("0.95"))], [F(1, 3), F(2, 3)],
     "duplicate atoms with fractional weights summing to 1 at the centre; expected PASS", n=2)

# (v) ROBUSTIFIED Goebel set: the literal Goebel points (1,1) etc. sit exactly on the boundary of the
# corner square [0,1]^2 (an admissible placement), a tangency no positive-width box can certify.
# Move them inwards by delta toward the container corners: (1-delta, 1-delta) etc.  The centred 45-degree
# square then needs s <= 2 + 1/sqrt2 - 2 delta.
for delta, s in ((F("0.0004"), F("2.70610678")), (F("0.0004"), F("2.72")), (F("0.0002"), F("2.7065"))):
    pts = [(1 - delta, 1 - delta), (1 - delta, s - 1 + delta), (s - 1 + delta, 1 - delta), (s - 1 + delta, s - 1 + delta)]
    dump(f"gobel_robust_d{float(delta)}_s{float(s)}.json", s, pts, [F(1)] * 4,
         f"Goebel set moved {delta} toward the corners; unavoidable iff s <= 2+1/sqrt2-2*delta", n=5)
