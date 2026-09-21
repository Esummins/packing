"""A261 tests: (1) the closed corner forms (verify261.form / cert261.point_form) against A258's numeric SAT forms
(dom258.corner_forms) -- every PUSH-admissible form must appear among A258's, with equal coefficients; (2) the centre
LP against dom258.min_side; (3) the interval bound encloses the point value.   python test261.py"""
import math
import os
import sys

import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', '..', 'A258-normal-ring', 'code')))
import cert261 as C                                                    # noqa: E402
import dom258 as D                                                     # noqa: E402
import verify261 as V                                                  # noqa: E402

rng = np.random.default_rng(261)
bad = n = 0
for _ in range(400):
    al, be = rng.uniform(0.02, 0.78, 2)
    sA, sB = rng.choice([1, -1], 2)
    ref = D.corner_forms(sA, al, 2, sB, be, 2)
    for which in (0, 1):
        ca, cb, c0 = C.point_form(which, sA, sB, al, be, math.cos(al) + math.sin(al), math.cos(be) + math.sin(be))
        n += 1
        # either the form is one of A258's live forms, or it cannot reach 0 on [0,1]^2 (A258 dropped it)
        hit = any(abs(ca - r[0]) + abs(cb - r[1]) + abs(c0 - r[2]) < 1e-9 for r in ref)
        if not hit and c0 + max(ca, 0) + max(cb, 0) >= 0:
            bad += 1
    # and A258 has no live form that is not one of ours
    mine = [C.point_form(q, sA, sB, al, be, math.cos(al) + math.sin(al), math.cos(be) + math.sin(be)) for q in (0, 1)]
    for r in ref:
        if not any(abs(m[0] - r[0]) + abs(m[1] - r[1]) + abs(m[2] - r[2]) < 1e-9 for m in mine):
            bad += 1
            print('A258 live form not PUSH-admissible?', sA, sB, math.degrees(al), math.degrees(be), r)
print('forms: %d checked, %d mismatches' % (n, bad))

bad2 = 0
for sg in ((1, 1, 1, -1), (1, -1, 1, -1), (1, 1, 1, 1)):
    job = dict(senses=sg, lengths=(2, 2, 2, 2), tdomain=C.FULL)
    for _ in range(40):
        t = rng.uniform(0.02, 0.98, 4)
        smin = D.min_side([v * V.PI4 for v in t], sg)[0]
        taus = [C.centre_lp(job, t, ch)[0] for ch in __import__('itertools').product((0, 1), repeat=4)]
        feas = min(taus) <= 1e-9
        if feas != (smin <= V.S0 + 1e-9) and abs(smin - V.S0) > 1e-6:
            bad2 += 1
            print('LP mismatch', sg, t, smin, min(taus))
print('centre LP vs dom258.min_side: mismatches', bad2)

bad3 = 0
job = dict(senses=[1, 1, 1, -1], lengths=[2, 2, 2, 2], tdomain=C.FULL)
for _ in range(200):
    t = rng.uniform(0.05, 0.95, 4)
    ch = tuple(rng.integers(0, 2, 4))
    tau, y, x = C.centre_lp(job, t, ch)
    y = np.asarray(y, np.float32).astype(float)
    Lpt = V.lower_bound(job, [(v, v) for v in t], [ch], [y])[0]
    Lbx = V.lower_bound(job, [(v - 1e-3, v + 1e-3) for v in t], [ch], [y])[0]
    if not (Lbx <= Lpt + 1e-12) or (tau > 1e-6 and Lpt < 0.5 * tau * y.sum() - 1e-6):
        bad3 += 1
        print('bound?', tau, Lpt, Lbx, y.sum())
print('interval bound: mismatches', bad3)
