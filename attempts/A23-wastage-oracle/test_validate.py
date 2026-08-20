#!/usr/bin/env python3
"""Validation cases for the dead-region certifier (task 1)."""
import time
from fractions import Fraction as F

from dead_region import (Certifier, Placed, Region, tilted_square_on_wall,
                         upright_square, poly_disjoint_from_placed, cos_sin, HALF)

S = F(77, 20)          # 3.85


def run(name, placed, D, mode, expect, depth=40, max_boxes=400000):
    cert = Certifier(S, placed, mode=mode, depth_max=depth)
    assert poly_disjoint_from_placed(D, placed), f"{name}: D not interior-disjoint from placed"
    t0 = time.time()
    r = cert.certify(D, max_boxes=max_boxes)
    dt = time.time() - t0
    ok = 'OK ' if r['passed'] == expect else 'MISMATCH'
    print(f"[{ok}] {name} ({mode}): passed={r['passed']} expect={expect} "
          f"boxes={r['boxes']} maxdepth={r.get('maxdepth')} wit={r.get('witness')} {dt:.1f}s "
          f"stats={cert.stats}")
    return r


# (a) 45-deg square touching both walls near the corner (0,0); pocket triangle
t45 = F(41421, 100000)             # tan(22.5deg) ~ 0.41421356; theta = 89.99...deg/2*2 ~ 45.000 - tiny
c45, s45 = cos_sin(t45)
w45 = (c45 + s45) / 2              # half-width of the rotated square's AABB
P45 = Placed(w45, w45, t45)        # touches x=0 and y=0
# pocket = triangle between corner and the near edge (line from (0, w) to (w, 0) at distance
# ... its near edge runs from leftmost corner (0, w45... compute corners:
lc = min(P45.corners, key=lambda p: p[0])   # leftmost ~ (0, 0.707)
bc = min(P45.corners, key=lambda p: p[1])   # lowest   ~ (0.707, 0)
# candidate D: the full pocket triangle shrunk by delta towards the corner
delta = F(1, 50)
D_pocket = Region([(0, 0), (bc[0] - delta, 0), (0, lc[1] - delta)])
print("pocket area (full triangle - delta):", float(D_pocket.area))
run("a1: 45deg corner pocket", [P45], D_pocket, 'float', True)

# smaller core of the pocket must certainly be dead
D_core = Region([(0, 0), (F(2, 5), 0), (0, F(2, 5))])
run("a2: 45deg corner pocket core", [P45], D_core, 'float', True)

# (b) region far from everything: must FAIL (not dead)
D_far = Region.rect(F(18, 10), F(18, 10), F(2), F(2))
run("b: free centre cell", [P45], D_far, 'float', False, depth=18)
run("b2: no squares at all", [], D_far, 'float', False, depth=18)

# (c) sliver between two parallel squares 0.9 apart (channel width 0.9 < 1): dead
P1 = upright_square(F(1, 2), F(14, 10))       # [0.5,1.5] x [1.4,2.4]
P2 = upright_square(F(24, 10), F(14, 10))     # [2.4,3.4] x [1.4,2.4]
# channel [1.5,2.4]x[1.4,2.4]: a corner dipping past the block corners reaches depth
# delta with chord 2*delta <= 0.9, i.e. 0.45 -- dead band only y in (1.85, 1.95)
D_sliver = Region.rect(F(19, 10), F(187, 100), F(2), F(193, 100))
run("c1: 0.9 channel sliver", [P1, P2], D_sliver, 'float', True)

# (c-neg) the naive "whole channel" region includes points reachable by dipping
# corners: certifier must FAIL on it (it did -- witness theta ~ 60deg, see notes)
D_naive = Region.rect(F(185, 100), F(17, 10), F(205, 100), F(21, 10))
run("c0: naive channel region (not dead)", [P1, P2], D_naive, 'float', False, depth=30)

# (c') gap 1.02 >= 1: an upright square slides in -> NOT dead
P2b = upright_square(F(252, 100), F(14, 10))  # gap [1.5, 2.52] width 1.02
D_sliver2 = Region.rect(F(196, 100), F(187, 100), F(206, 100), F(193, 100))
run("c2: 1.02 channel sliver (not dead)", [P1, P2b], D_sliver2, 'float', False, depth=18)

# exact reruns of the positives
run("a2 exact", [Placed(w45, w45, t45)], D_core, 'exact', True)
run("c1 exact", [upright_square(F(1, 2), F(14, 10)), upright_square(F(24, 10), F(14, 10))],
    D_sliver, 'exact', True)
run("a1 exact", [Placed(w45, w45, t45)], D_pocket, 'exact', True)
