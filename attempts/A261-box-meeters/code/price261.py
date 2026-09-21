"""A261 O3 pricing [M]: Monte-Carlo estimate of the leaf count of a job.  For random t in the tilt domain find the
largest dyadic cube (half-width 2^-k, clipped to the domain) around t that try_box certifies; N ~ vol * E[1/h^4]
(a bisection tree needs up to 2^4 more).  python price261.py JOB TMIN NSAMP"""
import sys
import time

import numpy as np

sys.dont_write_bytecode = True
import cert261 as C                                                    # noqa: E402

name, tmin, ns = sys.argv[1], float(sys.argv[2]), int(sys.argv[3])
sg, l, dom = C.jobs()[name]
dom = [[max(a, tmin) if b > 0 else 0.0, b] for a, b in dom]
job = dict(senses=list(sg), lengths=list(l), tdomain=dom)
rng = np.random.default_rng(7)
vol = float(np.prod([b - a for a, b in dom if b > a]))
inv, ks, t0, feas = [], [], time.time(), 0
for _ in range(ns):
    t = [rng.uniform(a, b) for a, b in dom]
    rows, k = [], 2
    while k <= 16:
        h = 2.0 ** -k
        box = tuple((max(a, v - h), min(b, v + h)) for v, (a, b) in zip(t, dom))
        leaf, f, rows = C.try_box(job, box, rows)
        if f is not None:
            feas += 1
            break
        if leaf is not None:
            break
        k += 1
    ks.append(k)
    inv.append(1.0 / float(np.prod([b - a for a, b in box if b > a])))
inv = np.array(inv)
print('%s tmin=%.4f  samples=%d  feasible=%d  k hist=%s  N_est=%.3g (top sample share %.2f)  %.0fs' % (
    name, tmin, ns, feas, np.bincount(ks).tolist(), vol * inv.mean(), inv.max() / inv.sum(), time.time() - t0))
