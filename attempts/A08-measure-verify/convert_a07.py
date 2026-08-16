"""Convert A07's raw LP result files (attempts/A07-lp-dual/results/*.json, floats) into the exact
certificate format read by certs/verify_measure.py, for stress-testing the verifier.

  v1 files (lp_measure.py):  atoms = [{i,j,x,y,w}], grid x = i*s/N exactly (N field).
  v2 files (lp_measure2.py): atoms = [{rep:[x,y], m, w}] = D4-orbit representatives, weight w per point,
                             m = orbit size;  we emit "symmetry": "D4" and let the verifier expand.
Floats are rationalised: grid coordinates exactly from (i, j, N, s); other floats through
Fraction(x).limit_denominator(10**9) (a coordinate change of < 1e-9 -- irrelevant for a stress test,
and any PASS would be a PASS of the *rationalised* certificate, which is what gets reported).
Weights are read as the exact decimal the float prints as (Fraction(repr(w))).

usage: python convert_a07.py <in.json> <out.json>
"""
import sys
import json
from fractions import Fraction as F


def conv(src, dst):
    d = json.load(open(src))
    s = F(repr(d["s"]))
    atoms, weights = [], []
    sym = None
    if d["atoms"] and "rep" in d["atoms"][0]:
        sym = "D4"
        for a in d["atoms"]:
            x = F(a["rep"][0]).limit_denominator(10 ** 9)
            y = F(a["rep"][1]).limit_denominator(10 ** 9)
            atoms.append((x, y))
            weights.append(F(repr(a["w"])))
    else:
        N = d.get("N")
        for a in d["atoms"]:
            if N is not None and "i" in a:
                x, y = s * a["i"] / N, s * a["j"] / N
                assert abs(float(x) - a["x"]) < 1e-9 and abs(float(y) - a["y"]) < 1e-9
            else:
                x = F(a["x"]).limit_denominator(10 ** 9)
                y = F(a["y"]).limit_denominator(10 ** 9)
            atoms.append((x, y))
            weights.append(F(repr(a["w"])))
    out = {"s": str(s), "n": int(d.get("n", 11)),
           "atoms": [[str(x), str(y)] for x, y in atoms],
           "weights": [str(w) for w in weights],
           "provenance": {"source": src, "converter": "attempts/A08-measure-verify/convert_a07.py",
                          "tau_reported": d.get("tau"), "converged": d.get("converged"),
                          "eps_geo": d.get("eps_geo")}}
    if sym:
        out["symmetry"] = sym
        out["provenance"]["note"] = "atoms are D4 orbit representatives; total = sum m_k w_k"
    json.dump(out, open(dst, "w"), indent=1)
    print(f"{src} -> {dst}: {len(atoms)} atoms{' (D4 reps)' if sym else ''}, tau={d.get('tau')}")


if __name__ == "__main__":
    conv(sys.argv[1], sys.argv[2])
