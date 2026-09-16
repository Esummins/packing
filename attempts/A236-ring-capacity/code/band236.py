"""A236 band geometry (n-general): the unit BAND W = [0,s]^2 \\ (1, s-1)^2, the open CENTRE C = (1, s-1)^2, the
trichotomy of a packing's squares at band width 1 (docs/proofs/ring_capacity.md s.1):
  BAND      int Q meets no point of C         (Lemma BAND-FLUSH: then Q is flush and touches a wall),
  CORE      Q inside the closed centre [1, s-1]^2,
  STRADDLER neither (meets C and pokes out of it; every tilted non-core square is one: Lemma TILT-BAND),
the intrusion depth of a square into the centre, wall touchers with their WALL-EXCESS chords, corner meeters, and
the packing numbers N(sigma) from the proven values (s(k^2) = s(k^2-1) = s(k^2-2) = k, Goebel 5, Kearney-Shiu 6-8,
Stromquist 10, Bentz 13 / 46, Nagamochi 22 / 23 / 33 -> literature.md) and from the record table (survey226).
Poses are (cx, cy, theta) in a y-up frame; a packing is a list of poses plus the side s.
"""
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ATTS = os.path.abspath(os.path.join(HERE, '..', '..'))
SURVEY = os.path.join(ATTS, 'A226-one-flush', 'results', 'survey226.jsonl')
CORNERS = ('BL', 'BR', 'TR', 'TL')
WALLS = ('floor', 'right', 'ceil', 'left')
TOL = 1e-7
GTOL = 1e-6        # geometric tolerance of the stored packings (certificate offsets ~5e-8, SAT gaps ~1e-9)
SQ2 = math.sqrt(2.0)


def verts(p):
    cx, cy, th = p
    c, d = math.cos(th), math.sin(th)
    return np.array([(cx + c * x - d * y, cy + d * x + c * y) for x, y in ((-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5))])


def sep_polys(A, B, axes):
    """separating-axis gap of two convex polygons over the given unit axes (>= 0 iff interior-disjoint)."""
    best = -1e9
    for ax in axes:
        a, b = A @ ax, B @ ax
        best = max(best, a.min() - b.max(), b.min() - a.max())
    return best


def axes_of(th):
    return [np.array((math.cos(th), math.sin(th))), np.array((-math.sin(th), math.cos(th)))]


def sep(p, q):
    return sep_polys(verts(p), verts(q), axes_of(p[2]) + axes_of(q[2]))


def sep_box(p, x0, x1, y0, y1):
    """gap between a unit square and the axis box [x0,x1] x [y0,y1] (< 0 iff the interiors meet)."""
    B = np.array([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], float)
    return sep_polys(verts(p), B, axes_of(p[2]) + axes_of(0.0))


def phi_of(th):
    """tilt mod 90 deg folded to [0, 45]."""
    r = th % (math.pi / 2)
    return min(r, math.pi / 2 - r)


def is_flush(th):
    return phi_of(th) < TOL


def extent(th):
    return abs(math.cos(th)) + abs(math.sin(th))


def iota(th):
    """the PI's intrusion of a wall-touching square of tilt theta beyond the unit band: cos + sin - 1."""
    return extent(th) - 1.0


def chord(th):
    """WALL-EXCESS chord of a wall toucher on the line at distance 1/sqrt2 from its wall: 1/max(cos, sin)."""
    return 1.0 / max(abs(math.cos(th)), abs(math.sin(th)))


def touches(p, s, tol=1e-6):
    """walls touched by the square: subset of WALLS."""
    v = verts(p)
    out = []
    if v[:, 1].min() <= tol:
        out.append('floor')
    if v[:, 0].max() >= s - tol:
        out.append('right')
    if v[:, 1].max() >= s - tol:
        out.append('ceil')
    if v[:, 0].min() <= tol:
        out.append('left')
    return out


def meets_corner(p, s, c, size=1.0):
    """interior of the square meets the open corner box (0, size)^2 of corner c."""
    x0 = 0.0 if c in ('BL', 'TL') else s - size
    y0 = 0.0 if c in ('BL', 'BR') else s - size
    return sep_box(p, x0, x0 + size, y0, y0 + size) < -1e-9


def meeters(poses, s, c):
    return [i for i, p in enumerate(poses) if meets_corner(p, s, c)]


def centre_class(p, s):
    """'band' / 'core' / 'straddle' at band width 1."""
    v = verts(p)
    if (v[:, 0] >= 1 - GTOL).all() and (v[:, 0] <= s - 1 + GTOL).all() and (v[:, 1] >= 1 - GTOL).all() \
            and (v[:, 1] <= s - 1 + GTOL).all():
        return 'core'
    if sep_box(p, 1.0, s - 1.0, 1.0, s - 1.0) >= -GTOL:
        return 'band'
    return 'straddle'


def depth_into_centre(p, s):
    """d(Q) = sup{t : Q meets [1+t, s-1-t]^2} (>= 0), the infinity-depth of the square's reach into the centre;
    0 for a band square, (s-2)/2 at most; by bisection on the SAT gap."""
    if sep_box(p, 1.0, s - 1.0, 1.0, s - 1.0) >= -GTOL:
        return 0.0
    lo, hi = 0.0, (s - 2.0) / 2.0
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        if sep_box(p, 1.0 + mid, s - 1.0 - mid, 1.0 + mid, s - 1.0 - mid) < -GTOL:
            lo = mid
        else:
            hi = mid
    return lo


def check_packing(poses, s, tol=1e-6):
    """(ok, min pair gap, min wall margin)."""
    worst_gap, worst_wall = 1e9, 1e9
    for p in poses:
        v = verts(p)
        worst_wall = min(worst_wall, v[:, 0].min(), v[:, 1].min(), s - v[:, 0].max(), s - v[:, 1].max())
    for i in range(len(poses)):
        for j in range(i + 1, len(poses)):
            worst_gap = min(worst_gap, sep(poses[i], poses[j]))
    return worst_gap >= -tol and worst_wall >= -tol, worst_gap, worst_wall


def classify(poses, s):
    """per-square record and the counts of the trichotomy, the wall touchers, the corner meeters."""
    n = len(poses)
    sq = []
    for i, p in enumerate(poses):
        cls = centre_class(p, s)
        sq.append({'i': i, 'tilt_deg': math.degrees(phi_of(p[2])), 'flush': is_flush(p[2]), 'cls': cls,
                   'walls': touches(p, s), 'chord': chord(p[2]), 'iota': iota(p[2]),
                   'depth': depth_into_centre(p, s)})
    B = sum(q['cls'] == 'band' for q in sq)
    K = sum(q['cls'] == 'core' for q in sq)
    X = sum(q['cls'] == 'straddle' for q in sq)
    walls = {}
    for w in WALLS:
        T = [q for q in sq if w in q['walls']]
        walls[w] = {'touchers': [q['i'] for q in T], 'flush': sum(q['flush'] for q in T),
                    'tilted': sum(not q['flush'] for q in T), 'chord_sum': sum(q['chord'] for q in T)}
    corners = {c: meeters(poses, s, c) for c in CORNERS}
    n2 = sum(len(v) >= 2 for v in corners.values())
    tilted_meeters = sorted({i for c in CORNERS for i in corners[c] if not sq[i]['flush']})
    return {'n': n, 's': s, 'B': B, 'K': K, 'X': X, 'n_tilted': sum(not q['flush'] for q in sq),
            'squares': sq, 'walls': walls, 'corners': corners, 'doubly_met': n2,
            'four_crowd': n2 == 4, 'tilted_meeters': tilted_meeters,
            'band_all_flush_touchers': all((q['flush'] or q['tilt_deg'] < 1e-3) and q['walls'] for q in sq if q['cls'] == 'band'),
            'tilted_all_intrude': all(q['depth'] > 0 for q in sq if not q['flush'] and q['tilt_deg'] > 1e-3),
            'max_meeter_depth': max([sq[i]['depth'] for c in CORNERS for i in corners[c]] or [0.0]),
            'min_meeter_depth': min([sq[i]['depth'] for c in CORNERS for i in corners[c]] or [0.0])}


# ---- packing numbers -------------------------------------------------------------------------------------------
PROVEN = {1: 1.0, 2: 2.0, 3: 2.0, 4: 2.0, 5: 2 + 1 / SQ2, 6: 3.0, 7: 3.0, 8: 3.0, 9: 3.0, 10: 3 + 1 / SQ2,
          13: 4.0, 22: 5.0, 33: 6.0, 46: 7.0}
for _k in range(2, 12):
    PROVEN[_k * _k] = float(_k)
    PROVEN[_k * _k - 1] = float(_k)
    PROVEN[_k * _k - 2] = float(_k)
LOWER = {11: 2 + 4 / math.sqrt(5)}          # Stromquist 2003


def proven_lower(k):
    """a proven lower bound on s(k): the largest proven value or bound at some j <= k (s is non-decreasing)."""
    best = 0.0
    for j, v in list(PROVEN.items()) + list(LOWER.items()):
        if j <= k:
            best = max(best, v)
    return best


def records():
    """best-known s(n), n = 1..64: the survey's 21 records below ceil(sqrt n), ceil(sqrt n) otherwise."""
    rec = {n: float(math.ceil(math.sqrt(n))) for n in range(1, 65)}
    rec[2] = rec[3] = 2.0
    if os.path.exists(SURVEY):
        for l in open(SURVEY, encoding='utf-8'):
            r = json.loads(l)
            rec[r['n']] = min(rec[r['n']], r['side'])
    return rec


def N_proved(sigma):
    """an upper bound on the packing number of a square of side sigma, from proven lower bounds only."""
    k = 0
    while proven_lower(k + 1) <= sigma + 1e-12 and k < 120:
        k += 1
    return k


def N_record(sigma, rec=None):
    """the packing number of a square of side sigma if the record table is optimal."""
    rec = rec or records()
    k = 0
    while (k + 1) in rec and rec[k + 1] <= sigma + 1e-12:
        k += 1
    return k
