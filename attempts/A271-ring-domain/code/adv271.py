"""A271 adversary: for each domain condition, minimise its margin over (C, X, A, side) subject to H1-H3 HARD
(ringdom271.constraints >= EPS, exact SAT), from the 43 JAM rings + rejection-sampled random feasible starts;
every reported minimiser is re-checked exactly before it is written.  A NEGATIVE minimum is a drawn configuration
satisfying H1-H3 that violates the condition (a sanity result, not a proof either way).
    python adv271.py [seconds=150] [seed=0] -> results/adv271.json"""
import json
import os
import sys
import time

import numpy as np
from scipy.optimize import minimize

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ringdom271 as R                                                # noqa: E402

EPS = 1e-6
LO = np.array([0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 3.82])
HI = np.array([1.0, 1.0, 45 * R.DEG, 2.9, 45 * R.DEG, 2.5, 90 * R.DEG, R.SHAT])


def feasible(q):
    return bool(R.constraints(q).min() >= EPS)


def penalised(key):
    def f(q):
        v = R.constraints(q) - EPS
        pen = float(np.sum(np.minimum(v, 0.0) ** 2)) * 1e4 + float(np.sum(np.minimum(v, 0.0) < 0)) * 1e-2
        try:
            return R.conditions(q)[key] + pen
        except (ValueError, ZeroDivisionError):
            return 1e3
    return f


def random_feasible(rng, tries=20000):
    for _ in range(tries):
        q = LO + rng.random(8) * (HI - LO)
        if feasible(q):
            return q
    return None


def starts(rng, n_random):
    out = []
    for line in open(os.path.join(R.ROOT, 'attempts', 'A262-no-jam', 'results', 'ring262.jsonl')):
        r = json.loads(line)
        if r.get('t', -1) > 0:
            out.append(('ring', R.from_ring(r)))
    k = 0
    while k < n_random:
        q = random_feasible(rng)
        if q is None:
            break
        out.append(('random', q))
        k += 1
    return out


def main():
    budget = float(sys.argv[1]) if len(sys.argv) > 1 else 150.0
    rng = np.random.default_rng(int(sys.argv[2]) if len(sys.argv) > 2 else 0)
    S = starts(rng, 60)
    t0, res = time.time(), {}
    per = budget / len(R.COND)
    for key in R.COND:
        f, best, tk = penalised(key), None, time.time()
        order = rng.permutation(len(S))
        for i in order:
            if time.time() - tk > per:
                break
            kind, q0 = S[i]
            r = minimize(f, q0, method='Nelder-Mead', options=dict(maxfev=4000, xatol=1e-7, fatol=1e-9))
            q = np.clip(r.x, LO, HI)
            if not feasible(q):
                continue
            m = R.conditions(q)[key]
            if best is None or m < best['margin']:
                best = dict(margin=float(m), q=[float(v) for v in q], start=kind, min_constraint=float(R.constraints(q).min()))
        res[key] = best
        print('%-3s min margin %+.5f  (%s start)  %.0fs' % (key, best['margin'], best['start'], time.time() - t0), flush=True)
    out = dict(budget=budget, n_starts=len(S), seconds=time.time() - t0, results=res)
    json.dump(out, open(os.path.join(HERE, '..', 'results', 'adv271.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
