"""A260 benchmark of cert260.check_box: random feasible points of the family, boxes of fixed radii around them;
prints the CERT / FAIL / PRUNE tally and seconds per box for each radius (the price of a leaf and the radius at which
leaves certify).  Called by  cert260.py --mode bench --fam <fam> --n <n>."""
import json
import time

import numpy as np

import pairh260 as PH

Z = PH.Z


def sample(rng, fam, s, smin):
    while True:
        f, f1 = rng.uniform(0.3, 45, 2) * Z.DEG
        if fam == 'layer':
            b, a1 = rng.uniform(1 - 1 / 64, 1, 2)
        else:
            b, a1 = rng.uniform(max(0, smin - 1 - Z.span(f)), 1), rng.uniform(max(0, smin - 1 - Z.span(f1)), 1)
        e = rng.uniform(0.0, 0.2) if fam in ('hybA', 'hybAB') else 0.0
        e1 = rng.uniform(0.0, 0.2) if fam in ('hybB', 'hybAB') else 0.0
        p = (b, f, a1, f1, e, e1)
        if PH.in_domain(p, s, fam != 'layer') < 0 or PH.feas(p, s) < 0:
            continue
        return np.array(p)


def run(a, check_box, adj):
    import cert260 as C
    for rp, rf in ((0.02, 0.01), (0.01, 0.005), (0.005, 0.0025), (0.0025, 0.00125)):
        if a.fam == 'layer':
            rp = min(rp, 1 / 256)
        rng = np.random.default_rng(a.seed)
        t0, res, worst = time.time(), {}, -9.0
        for _ in range(a.n // 4):
            p = sample(rng, a.fam, C.SMAX, C.SMIN)
            r = np.array([rp, rf, rp, rf, rp if p[4] > 0 else 0.0, rp if p[5] > 0 else 0.0])
            lo, hi = p - r, p + r
            lo[4:] = np.maximum(lo[4:], 0.0)
            if a.fam == 'layer':
                lo[[0, 2]] = np.maximum(lo[[0, 2]], 1 - 1 / 64)
                hi[[0, 2]] = np.minimum(hi[[0, 2]], 1.0)
            st, m = check_box(lo, hi, adj=adj)
            res[st] = res.get(st, 0) + 1
            if st == 'CERT':
                worst = max(worst, m)
        print(json.dumps({'fam': a.fam, 'r_pos': rp, 'r_phi': rf, 'res': res, 'worst_cert_margin': worst,
                          'sec_per_box': round((time.time() - t0) / max(1, a.n // 4), 3)}), flush=True)
