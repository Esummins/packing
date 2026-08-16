"""Stand-in rational certificate for s(11) <= 3877084/10^6, derived from A03's 60-digit exact
solution (attempts/A03-upper-reconstruct/trump11_exact.json), used until A03 publishes
certs/trump11_certificate_int.json.

Recipe (same as the pre-repo session): scale every centre by lam = s_c / s* about the origin
(unit squares keep their size, so every contact opens into a positive gap ~ (lam-1)),
round centres and t = tan(theta/2) to denominator 10^12, uprights get t = 0 exactly.
Validity does NOT depend on this derivation: lean/gen_cert_lean.py re-checks everything in
exact Fraction arithmetic and the Lean checker re-checks it again in Int arithmetic.
"""
import json
from decimal import Decimal, getcontext
from fractions import Fraction
from pathlib import Path

getcontext().prec = 80
SRC = Path(__file__).resolve().parents[1] / "A03-upper-reconstruct" / "trump11_exact.json"
OUT = Path(__file__).resolve().parent / "trump11_A06.json"
DEN = 10**12
S_C = Fraction(3877084, 10**6)

d = json.loads(SRC.read_text())
s_star = Fraction(Decimal(d["s"]))
lam = S_C / s_star
t_exact = Fraction(Decimal(d["t_tan_half_theta"]))
t_r = Fraction(round(t_exact * DEN), DEN)
theta = Decimal(d["theta_rad"])

squares = []
for q in d["squares"]:
    cx = Fraction(Decimal(q["cx"])) * lam
    cy = Fraction(Decimal(q["cy"])) * lam
    th = Decimal(q["theta"])
    if abs(th) < Decimal("1e-30"):
        t = Fraction(0)
    elif abs(th - theta) < Decimal("1e-30"):
        t = t_r
    elif abs(th + theta) < Decimal("1e-30"):
        t = -t_r
    else:
        raise SystemExit(f"unexpected angle {th}")
    squares.append({"center": [f"{round(cx*DEN)}/{DEN}", f"{round(cy*DEN)}/{DEN}"],
                    "t": f"{t.numerator}/{t.denominator}"})

cert = {
    "description": "A06 stand-in rational certificate for s(11) <= 3877084/10^6 (Trump 1979 packing), "
                   "built from A03 trump11_exact.json by scaling centres by s_c/s* and rounding to 1e-12; "
                   "each square = centre + t = tan(theta/2), corners exact rationals",
    "container_side": f"{S_C.numerator}/{S_C.denominator}",
    "squares": squares,
}
OUT.write_text(json.dumps(cert, indent=1))
print("wrote", OUT, " lam-1 =", float(lam - 1))
