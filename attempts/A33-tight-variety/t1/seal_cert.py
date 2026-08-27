"""Bake a verified --scale-weights factor into a certificate so it re-verifies with no flags.

  python seal_cert.py certs/cert_X.json 127/125 certs/cert_X_final.json
The weights are multiplied by the exact rational scale (identical arithmetic to verify_measure.py's
--scale-weights), so a PASS at that scale is reproduced exactly.
"""
import json, sys
from fractions import Fraction as F

src, scale, dst = sys.argv[1], F(sys.argv[2]), sys.argv[3]
c = json.load(open(src))
w = [F(x) * scale for x in c["weights"]]
tot = sum(w, F(0))
c["weights"] = [str(x) for x in w]
c["total"] = str(tot)
c["claim"] = (f"FEASIBILITY certificate: every closed unit square Q in [0,{c['s']}]^2 satisfies "
              f"mu(Q) >= 1 for this atomic measure of exact total mass {tot} (~{float(tot):.9f}). "
              f"n={c['n']} is a dummy above the total, present only to pass verify_measure.py's "
              f"total<n gate; NO lower bound on s(11) is claimed.")
c.setdefault("provenance", {})["sealed_scale"] = str(scale)
c["provenance"]["sealed_from"] = src
json.dump(c, open(dst, "w"), indent=0)
print(f"{dst}: atoms {len(c['atoms'])} total {tot} = {float(tot):.9f} eta = {float(tot)-11:.9f}")
