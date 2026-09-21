"""A260 task 3 probe [M]: GAP-DEPTH in its s-free, m-free QUADRANT form.  Corner BR of a large container (s = 9: the far
walls never act), floor row ending with END gap b (tilt phi), right-wall row starting at offset a' (tilt phi'), rows of
two (the far squares only shrink the free set near the corner; a row of m-2 has the same END / START squares).
  g1 = least height of the LOWEST vertex P of a free unit square with P right of W's top vertex   (END-gap zone)
  g2 = least right-wall depth of the RIGHTMOST vertex P with P below S''s far vertex                (START-gap zone)
(gapscan259.gap_dips, exact centre sets, 3-degree tilt grid).  Reported against the two forms:
  GAP-DEPTH-ONE: g >= 1;      GAP-DEPTH-COS (what R_cos needs): g1 >= cos(phi), g2 >= cos(phi').
Domain: 0 < b, a' < 1, tilts in (0, 45], W and S' interior-disjoint; rows 'plug=1' also list whether a' > 0.604.
    python gapdepth260.py seed budget_sec [bmin]"""
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom260 as H                                                   # noqa: E402
import gapscan259 as G                                                # noqa: E402
Z = H.Z

if __name__ == '__main__':
    seed, budget = int(sys.argv[1]), float(sys.argv[2])
    bmin = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
    s = 9.0
    rng = np.random.default_rng(seed)
    t0, rows = time.time(), []
    while time.time() - t0 < budget:
        f0, f1 = rng.uniform(0.3, 45, 2) * Z.DEG
        b, a1 = rng.uniform(bmin, 1), rng.uniform(bmin, 1)
        Vs = [H.toucher(s - b - H.w_of(f0) - 1 / math.cos(f0), f0, s, 0), H.toucher(s - b - H.w_of(f0), f0, s, 0),
              H.toucher(a1, f1, s, 1), H.toucher(a1 + 1 / math.cos(f1), f1, s, 1)]
        if min(Z.poly_gap(Vs[i], Vs[j]) for i in (0, 1) for j in (2, 3)) < 0:
            continue
        g1, p1, g2, p2 = G.gap_dips(b, f0, a1, f1, s, 3.0, Vs)
        rows.append({'b': b, 'phi': f0 / Z.DEG, 'a1': a1, 'phi1': f1 / Z.DEG, 'g1': g1, 'p1': p1, 'g2': g2, 'p2': p2,
                     'c0': math.cos(f0), 'c1': math.cos(f1)})
    out = os.path.join(HERE, '..', 'results', 'gapdepth260.jsonl')
    with open(out, 'a') as fh:
        for r in rows:
            fh.write(json.dumps(r) + '\n')
    n = len(rows)
    print(n, 'pairs;  g1 < 1:', sum(r['g1'] < 1 - 1e-9 for r in rows), ' g1 < cos:', sum(r['g1'] < r['c0'] - 1e-9 for r in rows),
          ' g2 < 1:', sum(r['g2'] < 1 - 1e-9 for r in rows), ' g2 < cos:', sum(r['g2'] < r['c1'] - 1e-9 for r in rows))
    for key, ck in (('g1', 'c0'), ('g2', 'c1')):
        rows.sort(key=lambda r: r[key] - r[ck])
        for r in rows[:4]:
            print(key, {k: round(v, 4) for k, v in r.items() if isinstance(v, float)},
                  None if r['p' + key[1]] is None else [round(float(t), 3) for t in r['p' + key[1]]])
