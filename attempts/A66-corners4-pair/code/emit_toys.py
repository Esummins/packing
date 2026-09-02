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


if __name__ == "__main__":
    main()
