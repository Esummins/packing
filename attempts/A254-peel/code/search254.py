"""A254: a small-budget FAMILY-STUCK search for general n (A250's search250 generalised to the border cells of
cells254): at a fixed side s minimise  overlap^2 + containment^2 + family-row deficits^2  over n unit squares, the
rows being every admissible family with |Pi| <= 2 and every MAXIMAL family (one split per wall), each needing
|Pi| + 1 squares to depth >= delta.  Every end point is re-checked by the full Hall test (all families).  [M] only.

    python search254.py --n 17 --sides 4.68,4.75,4.85,4.95 --starts 6
Resumable (rows keyed by n, side, start in results/search254.jsonl); logs/STOP stops between starts.
"""
import argparse
import itertools
import json
import math
import os
import sys
import time

import numpy as np
from scipy.optimize import minimize

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import cells254 as C          # noqa: E402

OUT = os.path.join(ATT, 'results', 'search254.jsonl')
STOP = os.path.join(ATT, 'logs', 'STOP')
BASE = np.array([(-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5)])


def quads(z):
    x, y, th = z[0::3], z[1::3], z[2::3]
    c, s_ = np.cos(th), np.sin(th)
    R = np.stack([np.stack([c, -s_], -1), np.stack([s_, c], -1)], -2)          # (n,2,2)
    return np.einsum('kj,nij->nki', BASE, R) + np.stack([x, y], -1)[:, None, :]


def gaps(A, B):
    """batched SAT gap for quads A, B of shape (N,4,2)."""
    best = np.full(len(A), -np.inf)
    for P in (A, B):
        e = np.roll(P, -1, 1) - P
        nrm = np.stack([e[..., 1], -e[..., 0]], -1)
        nrm = nrm / np.linalg.norm(nrm, axis=-1, keepdims=True)
        for i in range(4):
            a = np.einsum('nkj,nj->nk', A, nrm[:, i])
            b = np.einsum('nkj,nj->nk', B, nrm[:, i])
            best = np.maximum(best, np.maximum(a.min(1) - b.max(1), b.min(1) - a.max(1)))
    return best


class Problem:
    def __init__(self, n, s, delta=0.02):
        self.n, self.s, self.delta = n, s, delta
        self.m = math.ceil(math.sqrt(n) - 1e-12)
        self.cl = C.cells(self.m, s)
        self.conf = C.conflicts(self.cl)
        self.names = [c[0] for c in self.cl]
        self.cq = np.array([c[1] for c in self.cl])
        nc = len(self.cl)
        self.pi, self.pj = np.triu_indices(n, 1)
        self.qi, self.ci = np.repeat(np.arange(n), nc), np.tile(np.arange(nc), n)
        fams = [(i,) for i in range(nc)]
        fams += [p for p in itertools.combinations(range(nc), 2) if p not in self.conf]
        per = []
        for w in range(4):
            L = [self.names.index('%dL%d' % (w, j)) for j in range(1, self.m - 2)]
            R = [self.names.index('%dR%d' % (w, j)) for j in range(1, self.m - 2)]
            per.append([tuple(L[:a] + R[:self.m - 3 - a]) for a in range(self.m - 2)])
        corners = tuple(i for i, nm in enumerate(self.names) if nm[0] == 'C')
        fams += [corners + a + b + c + d for a in per[0] for b in per[1] for c in per[2] for d in per[3]]
        self.fams = [f for f in dict.fromkeys(fams) if len(f) + 1 <= n]

    def depth(self, z):
        Q = quads(z)
        return Q, -gaps(Q[self.qi], self.cq[self.ci]).reshape(self.n, len(self.cl))

    def parts(self, z):
        Q, D = self.depth(z)
        ov = np.maximum(0, -gaps(Q[self.pi], Q[self.pj]))
        out = np.maximum(0, -Q) + np.maximum(0, Q - self.s)
        row = []
        for f in self.fams:
            d = np.sort(D[:, list(f)].max(1))[::-1]
            row.append(max(0.0, self.delta - d[len(f)]))
        return ov, out, np.array(row), D

    def f(self, z):
        ov, out, row, _ = self.parts(z)
        return 50 * (ov ** 2).sum() + 50 * (out ** 2).sum() + (row ** 2).sum()

    def report(self, z):
        ov, out, row, D = self.parts(z)
        meet = [int(sum(1 << q for q in range(self.n) if D[q, c] > 1e-6)) for c in range(len(self.cl))]
        h = C.hall(self.cl, self.conf, meet, self.m)
        return dict(max_overlap=float(ov.max()), max_out=float(out.max()), rows_unmet=int((row > 1e-9).sum()),
                    n_rows=len(row), hall_min=h[0], hall_family=h[1],
                    feasible=bool(ov.max() < 1e-6 and out.max() < 1e-6),
                    family_stuck=bool(ov.max() < 1e-6 and out.max() < 1e-6 and h[0] >= 1))


def seed(pr, k, rng):
    """even k: pinwheel ring (tilt 4..12 deg) + the rest random in the hole (one near a narrow ribbon); odd: random."""
    n, s, m = pr.n, pr.s, pr.m
    z = np.zeros(3 * n)
    z[0::3], z[1::3] = rng.uniform(0.8, s - 0.8, n), rng.uniform(0.8, s - 0.8, n)
    z[2::3] = rng.uniform(0, math.pi / 2, n)
    r = C.best_ring(m, s, math.radians(rng.uniform(4, 12))) if k % 2 == 0 and 4 * (m - 2) < n else None
    if r is not None and r[0] > 0:
        for i, S in enumerate(r[4]):
            e = S[1] - S[0]
            z[3 * i:3 * i + 3] = (*S.mean(0), math.atan2(e[1], e[0]) % (math.pi / 2))
        q = 4 * (m - 2)
        z[3 * q:3 * q + 3] = (1.45, max(1.0, m - 2 - 0.5 * (m - s)) + 0.3, rng.uniform(0.1, 0.4))
    return z + rng.normal(0, 0.01, 3 * n)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, required=True)
    ap.add_argument('--sides', required=True)
    ap.add_argument('--starts', type=int, default=6)
    ap.add_argument('--maxiter', type=int, default=1500)
    ap.add_argument('--hops', type=int, default=10)
    a = ap.parse_args()
    try:
        import psutil
        psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        psutil.Process().cpu_affinity(list(range(16)))
    except Exception:
        pass
    done = set()
    if os.path.exists(OUT):
        for l in open(OUT, encoding='utf-8'):
            r = json.loads(l)
            done.add((r['n'], r['side'], r['start']))
    for s in [float(t) for t in a.sides.split(',')]:
        pr = Problem(a.n, s)
        for k in range(a.starts):
            if (a.n, s, k) in done:
                continue
            if os.path.exists(STOP):
                return
            t0 = time.time()
            z = seed(pr, k, np.random.default_rng(1000 * a.n + k))
            rng, best = np.random.default_rng(7 + k), None
            for rnd in range(a.hops):                 # basin hopping: perturb the best point, re-minimise, keep the best
                z0 = z if best is None else best[1] + rng.normal(0, 0.06, z.size)
                z1 = minimize(pr.f, z0, method='L-BFGS-B', options=dict(maxiter=a.maxiter, maxfun=200000)).x
                v = pr.f(z1)
                if best is None or v < best[0]:
                    best = (v, z1)
                if best[0] < 1e-14 or os.path.exists(STOP):
                    break
            z = best[1]
            rep = pr.report(z)
            rep.update(n=a.n, m=pr.m, side=s, start=k, penalty=float(pr.f(z)), seconds=round(time.time() - t0, 1),
                       poses=[round(float(v), 6) for v in z])
            with open(OUT, 'a', encoding='utf-8') as f:
                f.write(json.dumps(rep) + '\n')
            print(a.n, s, k, rep['penalty'], rep['feasible'], rep['hall_min'], rep['seconds'], flush=True)


if __name__ == '__main__':
    main()
