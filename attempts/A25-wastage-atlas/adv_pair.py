"""adversarial check for PAIR entries: seed at a REALISABLE instance of the two
cores (found by feasible.py's grid) and jitter, then scan legal placements."""
import json, math, sys
from fractions import Fraction as F
import numpy as np
from atlas_lib import clip_box
from feasible import feasible
from adversarial import check
S = F(sys.argv[2]) if len(sys.argv) > 2 else F(96, 25)
d = json.load(open(sys.argv[1]))
cells_ok = [c for c in d['cells'] if c.get('realisable', True)]
bad = 0
for c in cells_ok[:int(sys.argv[3]) if len(sys.argv) > 3 else 8]:
    bs = []
    for sub in (c['A'], c['B']):
        t0, t1 = F(sub['t'][0]), F(sub['t'][1])
        cl = clip_box(t0, t1, F(sub['cx'][0]), F(sub['cx'][1]),
                      F(sub['cy'][0]), F(sub['cy'][1]), S)
        bs.append((float(t0), float(t1)) + tuple(float(v) for v in cl))
    ok, w = feasible(bs, float(S), 7, 7)
    if not ok:
        print(c['id'], 'no realisation found'); continue
    (a, b) = w
    tA, tB = math.tan(a[2] / 2), math.tan(b[2] / 2)
    boxes = [(tA, tA, a[0], a[0], a[1], a[1]), (tB, tB, b[0], b[0], b[1], b[1])]
    tiles = np.array([[float(F(v)) for v in t] for t in c['regions']])
    nr, nl, nh, worst = check(boxes, tiles, float(S), 1, 60000)
    bad += nh
    print(f"{c['id']:26s} dead={c['dead_lb_float']:.4f} realisation "
          f"A=({a[0]:.3f},{a[1]:.3f},{math.degrees(a[2]):.1f}deg) "
          f"B=({b[0]:.3f},{b[1]:.3f},{math.degrees(b[2]):.1f}deg) "
          f"legal={nl} HITS={nh}", flush=True)
print('TOTAL HITS:', bad)
