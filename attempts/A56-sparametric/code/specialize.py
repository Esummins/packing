#!/usr/bin/env python3
"""
specialize.py -- A56 T2(B).  parametric-kill-certificate-v1 + rational s  ->  plain
case-measure-certificate-v1 at that s (exact rationals; budget / n / weights unchanged).

Purpose: the cross-check path.  The specialised file is fed to the UNMODIFIED audited verifier
attempts/A53-simple-strata/code/verify_case.py, which is the arbiter for canaries C1 (s = s0
must reproduce the base certificate exactly) and C2 (sampled-s cross-check of a parametric PASS).

Usage:  python specialize.py PARAM.json --s 191/50 -o OUT.json
"""
import argparse
import json
import os
import sys
from fractions import Fraction as F

S0 = F(969271, 250000)
S_LO = F(191, 50)


def rat(x):
    return x if isinstance(x, F) else F(str(x).strip())


def specialize(p, s):
    if p.get("format") != "parametric-kill-certificate-v1":
        raise ValueError(f"unexpected format {p.get('format')!r}")
    if not (S_LO <= s <= S0):
        raise ValueError(f"s = {s} outside the census window [{S_LO}, {S0}]")   # canary C3
    atoms, weights = [], []
    for a in p["atoms"]:
        x = rat(a["ax"]) + rat(a["bx"]) * s
        y = rat(a["ay"]) + rat(a["by"]) * s
        if not (0 <= x <= s and 0 <= y <= s):
            raise ValueError(f"specialised atom ({x},{y}) outside [0,{s}]^2")
        atoms.append([str(x), str(y)])
        weights.append(str(rat(a["w"])))
    cores = []
    for c in p["hypotheses"]["cores"]:
        cores.append({"kx": str(rat(c["akx"]) + rat(c["bkx"]) * s),
                      "ky": str(rat(c["aky"]) + rat(c["bky"]) * s),
                      "tm": c["tm"], "a": c["a"]})
    total = sum(rat(w) for w in weights)
    if str(total) != str(rat(p["total"])):
        raise ValueError("weights changed under specialisation")
    return {
        "format": "case-measure-certificate-v1",
        "n": p["n"],
        "s": str(s),
        "budget": p["budget"],
        "atoms": atoms,
        "weights": weights,
        "total": str(total),
        "hypotheses": {"cores": cores, "nofams": []},
        "claim": (f"every admissible closed unit square Q in [0,{s}]^2 disjoint from every core has "
                  f"mu(Q) >= 1, and mu(total) = {total} < budget {p['budget']}"),
        "provenance": {"tool": "A56 specialize.py", "param_name": p.get("name"),
                       "s": str(s), "anchoring": p.get("anchoring")},
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("param")
    ap.add_argument("--s", required=True)
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args(argv)
    p = json.load(open(a.param))
    s = F(a.s)
    out = specialize(p, s)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=1)
    print(f"specialised {p.get('name')} at s = {s} (~{float(s):.9f}) -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
