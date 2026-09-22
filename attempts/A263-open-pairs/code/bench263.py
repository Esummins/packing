"""A263 benchmark of cert263.check_box: random feasible points of a factor family (independent tilts), boxes of fixed
radii around them; prints the CERT / FAIL / PRUNE tally and seconds per box (the price of a leaf and the radius at which
leaves certify).  Called by  cert263.py --mode bench --fam <P2|WE|WS> --n <n>."""
import json
import time

import numpy as np

import fact263 as F
import geo263 as G


def run(a, check_box):
    import cert263 as C
    for rp, rf in ((0.02, 0.01), (0.01, 0.005), (0.005, 0.0025)):
        rng = np.random.default_rng(a.seed)
        t0, res, worst, n = time.time(), {}, -9.0, 0
        while n < a.n // 3:
            p = F.sample(rng, a.fam, C.SMAX, bool(a.adj))
            if p is None or F.fam_dom(a.fam, p, C.SMIN, bool(a.adj)) < 0 and F.fam_dom(a.fam, p, C.SMAX, bool(a.adj)) < 0:
                continue
            n += 1
            r = np.array([rp, rf, rp, rf])
            lo, hi = p - r, p + r
            lo[[0, 2]] = np.maximum(lo[[0, 2]], 0.0)
            lo[[1, 3]] = np.maximum(lo[[1, 3]], 0.0)
            hi[[1, 3]] = np.minimum(hi[[1, 3]], 45 * G.DEG)
            st, m = check_box(a.fam, lo, hi, adj=bool(a.adj))
            res[st] = res.get(st, 0) + 1
            if st == 'CERT':
                worst = max(worst, m)
        print(json.dumps({'fam': a.fam, 'adj': a.adj, 'r_pos': rp, 'r_phi': rf, 'res': res, 'worst_cert_margin': worst,
                          'sec_per_box': round((time.time() - t0) / max(1, n), 3)}), flush=True)
