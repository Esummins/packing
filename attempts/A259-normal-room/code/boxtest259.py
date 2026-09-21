"""A259 probe: the BOX form  C(theta) inside O + [-1/(2w), 1/(2w)]^2  (sufficient for PIERCE by O) on sampled rings."""
import json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import geom259 as Z, room259 as R
rows = [json.loads(l) for l in open(os.path.join(HERE, '..', 'results', 'sample259.jsonl'))]
for r in rows[:12]:
    x, s = np.array(r['x']), r['s']
    Vs = Z.ring_verts(x, s)
    worst = (-9, None)
    for t in range(0, 90, 2):
        th = t * Z.DEG
        w = math.cos(th) + math.sin(th)
        C = R.centre_set(Vs, s, th)
        for P in R.polys_of(C):
            A = np.array(P.exterior.coords) - s / 2
            g = np.abs(A).max() - 1 / (2 * w)
            if g > worst[0]: worst = (float(g), t)
    print(r['key'], 'pierceO %+.4f' % r['pierceO'], 'box %+.4f at theta %s' % worst, 'phi', [round(v / Z.DEG, 1) for v in x[4:]])
