"""A263 (d) THE SLAB (0, 0.703 deg): the margin law of A261's ring LP near a FLAT wall  [M]  (open_pairs.md s.5).
For every A261 job whose tilt domain is not exactly flat on the probed wall, and every wall w, the least infeasibility
margin  tau*(t) = min over admissible form choices of the centre LP's tau  (cert261.centre_lp, all forms of the
near-flat wall ADMISSIBLE)  is minimised over the other three tilts (grid 6^3 x Nelder-Mead polish) at
eps_w in {TMIN, TMIN/4, TMIN/16, TMIN/256}.  A margin bounded away from 0 as eps -> 0 means the slab is certifiable by
the SAME engine (no h ~ eps law); a margin -> 0 means the first-order (derivative) certificate is needed.
Also: the LIMIT job (eps = 0 exactly, the flat wall's forms DROPPED: PUSH) for comparison.
    python slab263.py [--jobs M1,M2,M3] [--quick]   -> results/slab263.jsonl"""
import argparse
import json
import math
import os
import sys

import numpy as np
from scipy.optimize import minimize

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A261-box-meeters', 'code'))
import cert261 as C                                                   # noqa: E402
import verify261 as V                                                 # noqa: E402
TMIN = C.TMIN


def tau_star(job, t):
    worst = None
    for ch in V.admissible(job):
        tau, y, x = C.centre_lp(job, list(t), ch)
        if tau is None:
            continue
        worst = tau if worst is None else min(worst, tau)
    return 9.0 if worst is None else worst


def min_over_others(job, w, eps, quick):
    grid = [1.0 / 64, 0.1, 0.2, 0.3, 0.45, 0.7] if not quick else [1.0 / 64, 0.3, 0.7]
    best = None
    for g in np.array(np.meshgrid(grid, grid, grid, indexing='ij')).reshape(3, -1).T:
        t = list(g[:w]) + [eps] + list(g[w:])
        v = tau_star(job, t)
        if best is None or v < best[0]:
            best = (v, t)

    def f(z):
        z = np.clip(z, TMIN, 1.0)
        t = list(z[:w]) + [eps] + list(z[w:])
        return tau_star(job, t)
    z0 = np.array([v for i, v in enumerate(best[1]) if i != w])
    r = minimize(f, z0, method='Nelder-Mead', options=dict(xatol=1e-4, fatol=1e-6, maxiter=300 if not quick else 80))
    z = np.clip(r.x, TMIN, 1.0)
    t = list(z[:w]) + [eps] + list(z[w:])
    return dict(tau=float(min(r.fun, best[0])), t_deg=[float(v * 45) for v in (t if r.fun <= best[0] else best[1])])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--jobs', default='')
    ap.add_argument('--quick', action='store_true')
    a = ap.parse_args()
    J = C.jobs()
    names = a.jobs.split(',') if a.jobs else [n for n in J if not n.startswith('F')]
    out = os.path.join(HERE, '..', 'results', 'slab263.jsonl')
    done = {(json.loads(l)['job'], json.loads(l)['wall']) for l in open(out)} if os.path.exists(out) else set()
    for name in names:
        sg, ln, td = J[name]
        job = dict(senses=sg, lengths=ln, tdomain=td)
        for w in range(4):
            if (name, w) in done or td[w][1] == 0.0:
                continue
            rec = dict(job=name, wall=w, senses=sg, lengths=ln, rows=[])
            for eps in (TMIN, TMIN / 4, TMIN / 16, TMIN / 256):
                r = min_over_others(job, w, eps, a.quick)
                r['eps_deg'] = eps * 45
                rec['rows'].append(r)
            fl = dict(td=[list(v) for v in td])
            fl['td'][w] = [0.0, 0.0]
            jobf = dict(senses=sg, lengths=ln, tdomain=fl['td'])
            r = min_over_others(jobf, w, 0.0, a.quick)
            r['eps_deg'] = 0.0
            rec['rows'].append(r)
            with open(out, 'a') as fh:
                fh.write(json.dumps(rec) + '\n')
            print(name, 'wall', w, ' '.join('%.3f:%+.4f' % (r['eps_deg'], r['tau']) for r in rec['rows']), flush=True)


if __name__ == '__main__':
    main()
