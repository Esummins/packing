"""A169 lonely-region raster: for tilt theta of the first meeter Q1 and its centre on a grid over the meeter set of
the unit box, does a second meeter exist?  Lonely poses (no second meeter) are a NO-family for K0-BLOCKED.
Coarse Q2 search (pitch 0.05, 30 tilts + local refinement): a 'found' is a certificate (SAT gap >= 0 after refine),
a 'not found' is only evidence."""
import math, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from geo169 import *
PITCH1 = 0.08
res = {}
for deg in (0, 15, 30, 45, 60, 75):
    th = math.radians(deg); rows = []
    n = int(1.9 / PITCH1)
    for i in range(n):
        for j in range(n):
            cx, cy = 0.5 + i * PITCH1, 0.5 + j * PITCH1
            Q1 = verts(cx, cy, th)
            if not in_quadrant(Q1) or not meets_open_box(Q1, 1.0): continue
            ok, pose, g = second_meeter_exists(Q1, 1.0, pitch=0.05, ntilt=30)
            rows.append(dict(cx=round(cx, 4), cy=round(cy, 4), second=ok, gap=g,
                             q2=None if pose is None else [round(v, 4) for v in pose]))
    lonely = [r for r in rows if not r['second']]
    res[deg] = dict(n=len(rows), lonely=len(lonely), lonely_cells=[(r['cx'], r['cy'], round(r['gap'], 4)) for r in lonely])
    print(deg, len(rows), 'lonely', len(lonely), [(r['cx'], r['cy']) for r in lonely][:12], flush=True)
    json.dump(res, open(os.path.join(os.path.dirname(__file__), '..', 'results', 'lonely.json'), 'w'), indent=1)
