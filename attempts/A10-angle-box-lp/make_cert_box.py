"""
A10: build a RESTRICTED measure certificate JSON (same 'measure-certificate-v1' layout as A07/A08, plus a
"theta_box" field) from an lp_measure_box.py result JSON.  Symmetry images (C4 or D4, as recorded in the result)
are expanded, atoms rounded to 1/10^6, weights scaled by `scale` and rounded UP to 1/10^6.

  python make_cert_box.py results/trump_d2_s3.85_ro.json 77/20 1.03 certs_wip/box_cert_3.85_d2.json

The claim of such a certificate is ONLY: no packing of n unit squares with ALL orientations in theta_box has
side <= s.  It does NOT prove s(n) >= s.  Verify with verify_measure_restricted.py --theta-range ...
"""
import json, sys, math
from fractions import Fraction


def images(x, y, s, sym):
    rot = [(x, y), (s - y, x), (s - x, s - y), (y, s - x)]
    if sym == "C4":
        return rot
    return rot + [(s - a, b) for (a, b) in rot]


def build(res, s_rat, scale, denom_pos=10**6, denom_w=10**6):
    s = Fraction(s_rat)
    assert abs(float(s) - res["s"]) < 1e-9, "s mismatch"
    sym = res["sym"]
    atoms, weights = [], []
    seen = {}
    for a in res["atoms"]:
        if a["w"] <= 1e-10:
            continue
        x = Fraction(round(a["rep"][0] * denom_pos), denom_pos)
        y = Fraction(round(a["rep"][1] * denom_pos), denom_pos)
        wq = Fraction(math.ceil(a["w"] * scale * denom_w), denom_w)   # round UP
        imgs = []
        for p in images(x, y, s, sym):
            if p not in imgs:
                imgs.append(p)
        for p in imgs:
            if p in seen:
                weights[seen[p]] += wq
            else:
                seen[p] = len(atoms)
                atoms.append(p); weights.append(wq)
    total = sum(weights)
    box = res["theta_box"]
    box_str = ",".join(f"{lo:.6f}-{hi:.6f}" if hi > lo else f"{lo:.6f}" for lo, hi, al in box)
    cert = dict(format="measure-certificate-v1", n=res["n"], s=str(s),
                atoms=[[str(p[0]), str(p[1])] for p in atoms], weights=[str(w) for w in weights],
                total=str(total), theta_box=box_str, theta_box_deg=box,
                claim=f"RESTRICTED: every closed unit square Q in [0,{s}]^2 with orientation in {box_str} deg has mu(Q) >= 1 "
                      f"and mu(total) = {float(total):.6f} < {res['n']}; hence no packing of {res['n']} unit squares with ALL "
                      f"orientations in {box_str} deg has side <= {s} = {float(s):.6f}.  This does NOT prove s({res['n']}) >= {s}.",
                provenance=dict(method="A10 orientation-restricted covering LP (lp_measure_box.py, %s symmetry); weights scaled by %.4f "
                                       "and rounded up to 1/%d; atoms rounded to 1/%d" % (sym, scale, denom_w, denom_pos),
                                lp_tau=res["tau"], eps_geo=res.get("eps_geo"), source=sys.argv[1] if len(sys.argv) > 1 else None))
    return cert


if __name__ == "__main__":
    res = json.load(open(sys.argv[1]))
    cert = build(res, sys.argv[2], float(sys.argv[3]))
    with open(sys.argv[4], "w") as f:
        json.dump(cert, f, indent=0)
    print("atoms", len(cert["atoms"]), "total", cert["total"], float(Fraction(cert["total"])), "box", cert["theta_box"])
