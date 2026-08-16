"""
Build a measure certificate JSON (format 'measure-certificate-v1') from an LP result JSON.

  python make_cert.py results/v2_s3.80.json 19/5 1.03 certs/measure_certificate_3.80.json

Format (frozen 2026-08-16, see attempts/A07-lp-dual/notes.md):
{
  "format": "measure-certificate-v1",
  "n": 11,                       # claim: s(n) >= s
  "s": "19/5",                   # container side, exact rational string
  "atoms": [["x","y"], ...],     # ALL atoms, exact rational strings (D4 images expanded; no symmetry assumed)
  "weights": ["p/q", ...],       # same length, positive rationals
  "total": "p/q",                # exact sum of weights (must be < n)
  "claim": "...",
  "provenance": {...}
}
Verification statement: for every closed unit square Q contained in [0,s]^2 (any orientation),
sum of weights of atoms in Q is >= 1; total < n  =>  no n pairwise-disjoint closed unit squares
fit in [0,s]^2  =>  s(n) >= s.
"""
import json, sys, math
from fractions import Fraction
from lp_measure2 import d4_point_images


def build(res, s_rat, scale, denom_pos=10**6, denom_w=10**6):
    s = Fraction(s_rat)
    assert abs(float(s) - res["s"]) < 1e-9, "s mismatch"
    atoms, weights = [], []
    seen = {}
    for a in res["atoms"]:
        if a["w"] <= 1e-10:
            continue
        x = Fraction(round(a["rep"][0] * denom_pos), denom_pos)
        y = Fraction(round(a["rep"][1] * denom_pos), denom_pos)
        wq = Fraction(math.ceil(a["w"] * scale * denom_w), denom_w)   # round UP
        imgs = []
        for (px, py) in [(x, y), (s - x, y), (x, s - y), (s - x, s - y), (y, x), (s - y, x), (y, s - x), (s - y, s - x)]:
            if (px, py) not in imgs:
                imgs.append((px, py))
        for p in imgs:
            if p in seen:
                weights[seen[p]] += wq
            else:
                seen[p] = len(atoms)
                atoms.append(p); weights.append(wq)
    total = sum(weights)
    cert = dict(format="measure-certificate-v1", n=res["n"], s=str(s),
                atoms=[[str(p[0]), str(p[1])] for p in atoms], weights=[str(w) for w in weights],
                total=str(total),
                claim=f"every closed unit square Q in [0,{s}]^2 has mu(Q) >= 1 and mu(total) = {float(total):.6f} < {res['n']}; hence s({res['n']}) >= {s} = {float(s):.6f}",
                provenance=dict(method="A07 discretised covering LP with row+column generation (HiGHS), D4-symmetric; weights scaled by %.4f and rounded up to 1/%d; atoms rounded to 1/%d" % (scale, denom_w, denom_pos),
                                lp_tau=res["tau"], eps_geo=res.get("eps_geo"), source=sys.argv[1] if len(sys.argv) > 1 else None))
    return cert


if __name__ == "__main__":
    res = json.load(open(sys.argv[1]))
    cert = build(res, sys.argv[2], float(sys.argv[3]))
    with open(sys.argv[4], "w") as f:
        json.dump(cert, f, indent=0)
    print("atoms", len(cert["atoms"]), "total", cert["total"], float(Fraction(cert["total"])))
