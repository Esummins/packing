"""A254 tests [M]: Lemma POKE (depth of a unit square into a slot of width g < 1 is <= (g/2) sin 2phi, one vertex only),
HOLE-POKE's inequality f(w) = 1 - (w-1)^2 + e w (w^2 - 2) < 1, the pinwheel pocket decomposition for m = 4..8, and the
BAND bound 4(m-2) on the tight pinwheel."""
import math
import sys
import os

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cells254 as C          # noqa: E402
from pages254 import pinwheel, notches      # noqa: E402

rng = np.random.default_rng(254)
bad = tested = 0
for _ in range(200000):
    g = rng.uniform(0.05, 0.999)
    phi, cx, cy = rng.uniform(0, math.pi / 2), rng.uniform(1.0, 2.2), rng.uniform(-1, 1)
    c, s_ = math.cos(phi), math.sin(phi)
    V = np.array([(cx + a * c - b * s_, cy + a * s_ + b * c) for a, b in ((-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5))])
    ins = V[V[:, 0] < 1]
    if len(ins) == 0:
        continue
    # the part of the square in x < 1: its y-extent (vertices inside + crossings of x = 1)
    ys = list(ins[:, 1])
    for i in range(4):
        p, q = V[i], V[(i + 1) % 4]
        if (p[0] - 1) * (q[0] - 1) < 0:
            t = (1 - p[0]) / (q[0] - p[0])
            ys.append(p[1] + t * (q[1] - p[1]))
    if max(ys) - min(ys) > g:
        continue                                   # does not fit a slot of width g
    tested += 1
    depth = 1 - V[:, 0].min()
    if len(ins) != 1 or depth > g / 2 * math.sin(2 * phi) + 1e-12:
        bad += 1
print('POKE: %d squares fitting a slot, %d violations' % (tested, bad))
assert bad == 0 and tested > 1000
w = np.linspace(1, math.sqrt(2), 2001)
for e in np.linspace(1e-3, 0.999, 500):
    f = 1 - (w - 1) ** 2 + e * w * (w ** 2 - 2)
    assert f.max() < 1
print('HOLE-POKE inequality: f(w) < 1 on the grid, max over grid', float(max(
    (1 - (w - 1) ** 2 + e * w * (w ** 2 - 2)).max() for e in (1e-3, 0.1, 0.5))))
from shapely.geometry import Polygon, box       # noqa: E402
from shapely.ops import unary_union             # noqa: E402
for m in range(4, 9):
    for s in (m - 0.9, m - 0.5, m - 0.123, m - 0.01):
        ring = pinwheel(m, s)
        assert len(ring) == 4 * (m - 2)
        assert min(C.sat_gap(ring[i], ring[j]) for i in range(len(ring)) for j in range(i)) > -1e-12
        pocket = box(0, 0, s, s).difference(unary_union([Polygon(P) for P in ring]))
        parts = sorted(pocket.geoms, key=lambda q: -q.area) if hasattr(pocket, 'geoms') else [pocket]
        assert len(parts) == 5, (m, s, len(parts))
        assert abs(parts[0].area - (s - 2) ** 2) < 1e-9 and all(abs(q.area - (s - m + 1)) < 1e-9 for q in parts[1:])
print('pinwheel pocket = hole (s-2)^2 + four isolated 1 x (s-m+1) notches: m = 4..8, 4 sides each: OK')
