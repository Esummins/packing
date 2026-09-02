#!/usr/bin/env python
# -*- coding: ascii -*-
"""test_clauses.py -- positive-path unit tests for verify_pair2's COVERED and
COVERED-F clauses (the B&B toy corpus never reaches them; v1 had the same gap).
Constructions are checked against brute-force float sampling as well."""
import math
import random
import sys
from fractions import Fraction as Fr

import verify_pair2 as vp


class FakeCert(object):
    def __init__(self, atoms, cores=(), beta=Fr(0), boxes=(), m=0, s=Fr(4)):
        self.atoms = [tuple(Fr(x) for x in a) for a in atoms]
        self.cores = [tuple(Fr(x) for x in c) for c in cores]
        self.beta = Fr(beta)
        self.boxes = list(boxes)
        self.m = m
        self.s = Fr(s)


def approx_field(F):
    return tuple(Fr(x) for x in F)


def main():
    ok = True

    # ---- 1. COVERED: deep atom over tight pair box
    FA = approx_field((0, "1/100", "3/2", "31/20", "3/2", "31/20"))
    FB = approx_field((0, "1/100", "3", "61/20", "3", "61/20"))
    cert = FakeCert([("31/20", "31/20", "3", "3", "6/5")])
    got, mass, cset = vp.covered_try(cert, FA, FB, Fr(1))
    print("COVERED deep atom: %s mass=%s" % (got, mass))
    ok &= got and mass == Fr(6, 5)

    # swapped orientation
    cert2 = FakeCert([("3", "3", "31/20", "31/20", "6/5")])
    got2, mass2, _ = vp.covered_try(cert2, FA, FB, Fr(1))
    print("COVERED swapped orientation: %s mass=%s" % (got2, mass2))
    ok &= got2 and mass2 == Fr(6, 5)

    # ---- 2. COVERED-F, MEM/MEM handoff along cx (same factor, u-type)
    # t in [0, 1/100], FA wide in x: [1, 8/5]; atom1 p=(1, 5/4), atom2 p=(8/5, 5/4)
    FAW = approx_field((0, "1/100", "1", "8/5", "5/4", "5/4"))
    FBT = approx_field((0, "1/100", "3", "61/20", "3", "61/20"))
    atoms = [("1", "5/4", "3", "3", "6/5"),
             ("8/5", "5/4", "3", "3", "11/10")]
    cert3 = FakeCert(atoms)
    okc, mass3, cset3 = vp.covered_try(cert3, FAW, FBT, Fr(1))
    print("COVERED on wide box (should FAIL): %s mass=%s" % (okc, mass3))
    ok &= (not okc)
    okf, add, used = vp.covered_f_try(cert3, FAW, FBT, Fr(1), mass3, cset3)
    print("COVERED-F handoff: %s add=%s used=%s" % (okf, add, used))
    ok &= okf and add >= Fr(11, 10)
    # brute-force check of the disjunction it certifies
    rng = random.Random(7)
    for _ in range(4000):
        t = rng.random() * 0.01
        cx = 1.0 + rng.random() * 0.6
        cy = 1.25
        got_any = False
        for (px, py, qx, qy, w) in cert3.atoms:
            u, v = vp._sample_uv(float(px), float(py), t, cx, cy)
            if abs(u) <= 0.5 + 1e-12 and abs(v) <= 0.5 + 1e-12:
                got_any = True
        if not got_any:
            print("BRUTE-FORCE HOLE at t=%.4f cx=%.4f" % (t, cx))
            ok = False
            break

    # ---- 3. COVERED-F, MEM/EXC handoff: core takes over where the atom exits
    # factor cx in [1, 8/5]; atom p=(1, 5/4) serves cx <= 3/2; core at kx=2.1
    # (a=1/2) overlaps Q(theta~0) when cx >= 2.1 - 0.5 - 0.5 = 1.1 <= 3/2: overlap.
    FAW2 = approx_field((0, "1/100", "1", "8/5", "5/4", "5/4"))
    cert4 = FakeCert([("1", "5/4", "3", "3", "11/10")],
                     cores=[("21/10", "5/4", "1/2")])
    okc4, mass4, cset4 = vp.covered_try(cert4, FAW2, FBT, Fr(1))
    okf4, add4, used4 = vp.covered_f_try(cert4, FAW2, FBT, Fr(1), mass4, cset4)
    print("COVERED-F MEM/EXC: covered=%s cf=%s add=%s used=%s"
          % (okc4, okf4, add4, used4))
    ok &= (not okc4) and okf4 and add4 == Fr(11, 10)
    for _ in range(4000):
        t = rng.random() * 0.01
        cx = 1.0 + rng.random() * 0.6
        cy = 1.25
        u, v = vp._sample_uv(1.0, 1.25, t, cx, cy)
        collected = abs(u) <= 0.5 + 1e-12 and abs(v) <= 0.5 + 1e-12
        exempt = vp._sat_overlap_f((Fr(21, 10), Fr(5, 4), Fr(1, 2)), t, cx, cy)
        if not (collected or exempt):
            print("BRUTE-FORCE HOLE (MEM/EXC) at t=%.4f cx=%.4f" % (t, cx))
            ok = False
            break

    # ---- 4. EXEMPT exactness spot: factor box fully overlapping a fat core
    FAC = approx_field((0, "1", "1", "3/2", "1", "3/2"))
    core = (Fr(5, 4), Fr(5, 4), Fr(1))
    got_e = vp.exc_certain(core, FAC)
    print("EXEMPT fat core: %s" % got_e)
    ok &= got_e

    print("ALL %s" % ("OK" if ok else "FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
