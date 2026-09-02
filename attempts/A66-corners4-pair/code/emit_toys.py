#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""emit_toys.py -- tiny emitter for the two A66 end-to-end toy pair certificates.

  certs/pair_toy_s199.json     s = 199/100 < 2 = s(2)  -> expect PASS
                               (every two unit squares in [0,1.99]^2 overlap in
                               their interiors, so (P2') is vacuous: there is no
                               interior-disjoint pair to collect mass for)
  certs/pair_control_s201.json s = 201/100 > 2         -> expect FAIL
                               (opposite-corner axis-aligned unit squares are
                               interior-disjoint and collect mass 0 < 1)

Both have n = 2, k = 0 (so N = 2, C(N,2) = 1), m = 0, beta = 0, no atoms: W2 = 0 < 1,
so (P1') holds and the whole content of a PASS is (P2').
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CERTS = os.path.normpath(os.path.join(HERE, "..", "certs"))


def toy(s):
    return {
        "format": "pair-certificate-v1",
        "s": s,
        "n": 2,
        "k": 0,
        "m": 0,
        "beta": "0",
        "cores": [],
        "boxes": [],
        "atoms": [],
        "provenance": {
            "emitter": "attempts/A66-corners4-pair/code/emit_toys.py",
            "purpose": "end-to-end toy for verify_pair.py (pair-certificate-v1)",
            "claim": "N=2, threshold C(2,2)+beta*m = 1, W2 = 0; PASS iff no two "
                     "interior-disjoint unit squares fit in [0,s]^2, i.e. iff s < s(2) = 2",
        },
    }


def main():
    if not os.path.isdir(CERTS):
        os.makedirs(CERTS)
    for name, s in (("pair_toy_s199", "199/100"), ("pair_control_s201", "201/100")):
        p = os.path.join(CERTS, name + ".json")
        with open(p, "w") as fh:
            json.dump(toy(s), fh, indent=1, sort_keys=True)
        print("wrote %s" % p)
    p = os.path.join(CERTS, "pair_smoke_paths.json")
    with open(p, "w") as fh:
        json.dump(smoke(), fh, indent=1, sort_keys=True)
    print("wrote %s" % p)


def smoke():
    """A path-coverage smoke certificate (NOT a claim): a big core plus a dense atom
    grid, so that the EXEMPT-core and COVERED discharge branches are both exercised."""
    fr = lambda a, b: "%d/%d" % (a, b)
    atoms = []
    for i in range(1, 16):
        for j in range(1, 16):
            # genuine PAIR atoms: p and its reflection through the centre of [0,4]^2
            # (coincident atoms can never be collected -- spec section 2)
            atoms.append({"px": fr(i, 4), "py": fr(j, 4),
                          "qx": fr(64 - i, 4), "qy": fr(64 - j, 4), "w": "1/4"})
    return {
        "format": "pair-certificate-v1",
        "s": "4", "n": 13, "k": 1, "m": 1, "beta": "1/1000",
        "cores": [{"kx": "2", "ky": "2", "a": "1"}],
        "boxes": [{"bx": "2", "by": "2", "h": "1/2"}],
        "atoms": atoms,
        "provenance": {"purpose": "exercise EXEMPT-core + COVERED + bonus U branches"},
    }


if __name__ == "__main__":
    main()
