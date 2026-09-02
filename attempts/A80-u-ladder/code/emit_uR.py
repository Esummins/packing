"""
A80 T3: emit U_R certificates (removed set R, |R| >= 2): cores at the tight poses of the
squares NOT in R (half-side 1/2 - delta), one pocket zone F_i (hw_c, hw_t) per i in R,
budget |R|; C0 form (no atoms, Sigma w = 0) or C1 form (atoms given explicitly, Sigma w < |R|).

    python code\emit_uR.py --R 0,1 --delta 1/10000 --hwc 3/10000 --hwt 3/10000 [--atoms "px,py,w;..."]
"""
import argparse, json, os
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))


def tight_squares():
    tight = json.load(open(os.path.join(ROOT, "certs", "trump11_certificate_tight.json")))
    return F(tight["side"]), [{k: F(q[k]) for k in ("cx", "cy", "t")} for q in tight["squares"]]


def emit_R(R, delta, hw, atoms=None, tag=None, outdir=None, control=False):
    """hw: dict i -> (hw_c, hw_t) or a single (hw_c, hw_t) pair for all i in R."""
    s2, sq = tight_squares()
    a_core = F(1, 2) - delta
    R = sorted(R)
    cores = [{"kx": str(sq[j]["cx"]), "ky": str(sq[j]["cy"]), "tm": str(sq[j]["t"]),
              "a": str(a_core)} for j in range(11) if j not in R]
    nofams = []
    for i in R:
        hwc, hwt = hw[i] if isinstance(hw, dict) else hw
        if i >= 6:
            t_ints = [[str(sq[i]["t"] - hwt), str(sq[i]["t"] + hwt)]]
        else:
            h1 = 2 * hwt / (1 + hwt)
            t_ints = [["0", str(hwt)], [str(1 - h1), "1"]]
        nofams.append({"x0": str(sq[i]["cx"] - hwc), "x1": str(sq[i]["cx"] + hwc),
                       "y0": str(sq[i]["cy"] - hwc), "y1": str(sq[i]["cy"] + hwc),
                       "t_intervals": t_ints})
    atoms = atoms or []
    total = sum(F(w) for (_, _, w) in atoms)
    assert total < len(R)
    rname = "".join("%d" % i for i in R) if len(R) <= 4 else "-".join(str(i) for i in R)
    tag = tag or "R%s_d%s" % (rname, str(delta).replace("/", "_"))
    cert = {"format": "case-lp-certificate-v1",
            "claim": "U_R removal R=%s at core slack %s: no 11-packing at side s'' contains the "
                     "%d slack cores of z-hat minus R with a non-owner square outside the pocket "
                     "zones (budget %d, Sigma w = %s)%s"
                     % (R, delta, 11 - len(R), len(R), total, " [CONTROL]" if control else ""),
            "s": str(s2), "n": 11, "budget": len(R),
            "atoms": [[str(F(px)), str(F(py))] for (px, py, _) in atoms],
            "weights": [str(F(w)) for (_, _, w) in atoms], "total": str(total),
            "hypotheses": {"cores": cores, "nofams": [] if control else nofams},
            "provenance": {"attempt": "A80-u-ladder", "emitter": "code/emit_uR.py",
                           "coordinates": "certs/trump11_certificate_tight.json",
                           "truth_anchor": "A22 krawczyk_cert.json z0, r_0=1e-50",
                           "delta": str(delta), "R": R,
                           "hw": {str(i): [str(x) for x in (hw[i] if isinstance(hw, dict) else hw)]
                                  for i in R}}}
    outdir = outdir or os.path.join(BASE, "certs")
    os.makedirs(outdir, exist_ok=True)
    fn = os.path.join(outdir, "uR_%s%s.json" % (tag, "_control" if control else ""))
    with open(fn, "w") as fh:
        json.dump(cert, fh, indent=1)
    return fn


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--R", required=True)
    ap.add_argument("--delta", required=True)
    ap.add_argument("--hwc", required=True)
    ap.add_argument("--hwt", required=True)
    ap.add_argument("--atoms", default="")
    ap.add_argument("--control", action="store_true")
    a = ap.parse_args()
    R = [int(x) for x in a.R.split(",")]
    atoms = [tuple(F(v) for v in s.split(",")) for s in a.atoms.split(";") if s.strip()]
    print(emit_R(R, F(a.delta), (F(a.hwc), F(a.hwt)), atoms, control=a.control))
