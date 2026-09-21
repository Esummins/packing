"""A259: random scan of the PAIR domain at s = s_max (corner frame monotone in s [T]):  e0 > 2.82 - span(phi0),
delta1 > 2.82 - span(phi1)  (implied by D for every s >= 3.82), e0, delta1 < 1, pair feasible.  Rows -> results/pairscan259.jsonl"""
import json, math, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import geom259 as Z, pair259 as P
seed = int(sys.argv[1]); budget = float(sys.argv[2]); smax = Z.SHAT if len(sys.argv) < 4 else float(sys.argv[3])
smin = 3.82
rng = np.random.default_rng(seed); t0 = time.time(); n = 0
out = os.path.join(HERE, '..', 'results', 'pairscan259.jsonl')
while time.time() - t0 < budget:
    f0, f1 = rng.uniform(0.2, 45, 2) * Z.DEG
    lo0, lo1 = max(0, smin - 1 - Z.span(f0)), max(0, smin - 1 - Z.span(f1))
    e0, d1 = rng.uniform(lo0, 1), rng.uniform(lo1, 1)
    if smax - e0 - Z.span(f0) < 0 or smax - d1 - Z.span(f1) < 0: continue
    fe = P.pair_feas(e0, f0, d1, f1, smax)
    if fe < 0: continue
    m, pose = P.pair_margin(e0, f0, d1, f1, smax, 3.0)
    n += 1
    with open(out, 'a') as fh:
        fh.write(json.dumps({'seed': seed, 's': smax, 'e0': e0, 'phi0': f0 / Z.DEG, 'd1': d1, 'phi1': f1 / Z.DEG, 'feas': fe, 'margin': m, 'pose': pose}) + '\n')
print('rows', n)
