"""A237 tests: (1) the kernel / hull sandwich of geom237 (K_bin inside and H_bin outside every square of the bin, 3 000
random tilts); (2) TILT-MIN's exact curve by random search (a flat floor meeter at offset delta and a tilted
partner meeting the box: sin theta <= delta always, and the partner exists whenever sin theta < delta); (3) the
DEPTH-BUDGET d_A + d_B <= 1 on 20 000 random interior-disjoint meeter pairs; (4) Lemma WEDGE's bound below the numeric
minimum for every angle; (5) PIERCE / waste sanity on a box (waste 0, PIERCE(1) at the centre for side < 2).
    python test237.py   (exit 1 on any failure)
"""
import math
import os
import sys

import numpy as np
from shapely.geometry import Polygon, Point

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'A236-ring-capacity', 'code'))
import geom237 as G           # noqa: E402
import band236 as BD          # noqa: E402
import tiltmin237 as TM       # noqa: E402

rng = np.random.default_rng(237)
fails = []


def check(name, ok):
    print('%-60s %s' % (name, 'ok' if ok else 'FAIL'))
    if not ok:
        fails.append(name)


# (1) sandwich
bad = 0
for _ in range(3000):
    t1 = rng.uniform(0, math.pi / 2 - 0.02)
    t2 = t1 + rng.uniform(0.001, 0.02)
    K, H, m, f = G.kernel_hull(t1, t2)
    th = rng.uniform(t1, t2)
    Q = G.sq_poly((0.0, 0.0, th))
    if not Polygon(K).within(Q.buffer(1e-12)) or not Q.within(Polygon(H).buffer(1e-12)):
        bad += 1
check('(1) K_bin inside / H_bin outside every square of the bin (3000)', bad == 0)

# (2) TILT-MIN random search: flat A = [delta, 1+delta] x [0,1], partner of tilt theta meeting (0,1)^2
viol, exist = 0, 0
for _ in range(20000):
    delta = rng.uniform(0.0, 1.0)
    th = rng.uniform(0.01, math.pi / 2 - 0.01)
    A = (delta + 0.5, 0.5, 0.0)
    cx, cy = rng.uniform(0.3, 1.3), rng.uniform(0.6, 1.9)
    B = (cx, cy, th)
    V = BD.verts(B)
    if V.min() < 0 or BD.sep(A, B) < 0 or not BD.meets_corner(B, 10.0, 'BL'):
        continue
    exist += 1
    thd, low = TM.tilt_in_frame(V, 'floor')
    if math.sin(math.radians(thd)) > delta + 1e-9 or low < 1 - (delta - math.sin(math.radians(thd))) * math.tan(math.radians(thd)) - 1e-9:
        viol += 1
check('(2) TILT-MIN: sin theta <= delta and the low-point bound on %d random pairs' % exist, viol == 0)
# the curve is exact: at delta > sin theta the mode-(a) partner exists
ok = True
for th in (5, 20, 40, 60, 80):
    t = math.radians(th)
    delta = math.sin(t) + 0.01
    xv, yv = math.sin(t) + 1e-4, 1 - (delta - math.sin(t) - 1e-4) * math.tan(t) + 1e-4
    B = (xv + (math.cos(t) - math.sin(t)) / 2, yv + (math.sin(t) + math.cos(t)) / 2, t)
    A = (delta + 0.5, 0.5, 0.0)
    ok &= BD.sep(A, B) >= -1e-9 and BD.verts(B).min() >= -1e-9 and BD.meets_corner(B, 10.0, 'BL')
check('(2b) the partner exists at delta = sin theta + 0.01 (5 tilts)', ok)

# (3) DEPTH-BUDGET
viol, cnt, worst = 0, 0, 0.0
for _ in range(200000):
    A = (rng.uniform(0.3, 1.6), rng.uniform(0.3, 1.6), rng.choice([0.0, rng.uniform(0, math.pi / 2)]))
    B = (rng.uniform(0.3, 1.6), rng.uniform(0.3, 1.6), rng.choice([0.0, rng.uniform(0, math.pi / 2)]))
    VA, VB = BD.verts(A), BD.verts(B)
    if VA.min() < 0 or VB.min() < 0 or BD.sep(A, B) < 0:
        continue
    if not (BD.meets_corner(A, 10.0, 'BL') and BD.meets_corner(B, 10.0, 'BL')):
        continue
    cnt += 1
    d = TM.depth(VA) + TM.depth(VB)
    worst = max(worst, d)
    if d > 1 + 1e-9:
        viol += 1
check('(3) DEPTH-BUDGET d_A + d_B <= 1 on %d random meeter pairs (max %.4f)' % (cnt, worst), viol == 0)

# (4) WEDGE
ok = True
for a in range(5, 91, 5):
    ok &= G.wedge_radius_bound(a) <= G.wedge_radius_exact(a, 361) + 1e-9
check('(4) WEDGE bound <= numeric minimum, alpha = 5..90', ok)

# (5) box sanity
W = G.waste([], 1.9, 5.0)
check('(5a) a side-1.9 box has waste 0', abs(W['waste']) < 1e-9)
check('(5b) PIERCE(1) at the centre of a side-1.9 box', G.pierce([], 1.9, [(0.95, 0.95)], 5.0, free=W['free']) <= 1e-9)
W = G.waste([], 2.1, 5.0)
check('(5c) PIERCE(1) at the centre of a side-2.1 box FAILS', G.pierce([], 2.1, [(1.05, 1.05)], 5.0, free=W['free']) > 1e-6)

print('FAILURES:', fails)
sys.exit(1 if fails else 0)
