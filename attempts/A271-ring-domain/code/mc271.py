"""A271 price: Monte-Carlo the fraction of the H1-H3 feasible set (uniform in adv271's box, A included) on which
each undelivered condition fails, and the fraction where ANY of them fails -- the RESIDUAL sub-domain a certificate
would have to cover (price = fraction x A266's strip266 price ~5e3 CPU-h for the whole (h_u, h_v, th, X_low, phi) domain).
    python mc271.py [n=200000] -> results/mc271.json"""
import json
import os
import sys
import time

import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ringdom271 as R                                                # noqa: E402
import adv271 as ADV                                                  # noqa: E402

RESID = ['U3', 'U4', 'U5', 'U6', 'U8']


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 200000
    rng = np.random.default_rng(3)
    t0, feas, fails, any_fail, betas = time.time(), 0, {k: 0 for k in R.COND}, 0, []
    for _ in range(n):
        q = ADV.LO + rng.random(8) * (ADV.HI - ADV.LO)
        if not ADV.feasible(q):
            continue
        feas += 1
        c = R.conditions(q)
        bad = [k for k in R.COND if c[k] <= 0]
        for k in bad:
            fails[k] += 1
        if any(k in RESID for k in bad):
            any_fail += 1
            betas.append(c['beta_deg'])
    out = dict(n=n, feasible=feas, seconds=time.time() - t0,
               fail_fraction={k: fails[k] / max(feas, 1) for k in R.COND},
               residual_fraction=any_fail / max(feas, 1),
               residual_beta_deg=[float(np.min(betas)), float(np.max(betas))] if betas else None,
               residual_beta_abs_min=float(np.min(np.abs(betas))) if betas else None)
    print(json.dumps(out, indent=1))
    json.dump(out, open(os.path.join(HERE, '..', 'results', 'mc271.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
