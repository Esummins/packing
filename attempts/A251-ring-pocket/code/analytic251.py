"""A251 task 3: the ANALYTIC pocket -- INRADIUS, THREE-DISC, GAP, MID-NOTCH, and what is left.

[T] Lemma INRADIUS.  A unit square contains the open disc of radius 1/2 about its centre; two
interior-disjoint unit squares therefore have centres at distance >= 1.

[T] Lemma THREE-DISC.  Three points pairwise at distance >= 1 do not lie in a closed disc of
radius R < 1/sqrt3.  (Seen from the disc's centre two of them subtend an angle <= 120 deg, so
their distance is at most 2 R sin 60 = sqrt3 R.)

[T] Corollary CENTRE-DISC => RING-POCKET.  If every unit square in the pocket has its centre
within R < 1/sqrt3 = 0.57735 of a fixed point, the pocket holds at most two unit squares.

[T] Lemma GAP (family251): the two touchers of a wall leave a gap < 4 - s along it.

[T] Lemma MID-NOTCH (the wall's middle notch holds no half-disc).  Let B, B' be the two touchers
of the wall x = 0, tilts theta, theta', offsets delta, delta' < 1, both reaching the far slot
(delta + w(theta) > s - 2, likewise B').  Let D be a closed disc of radius 1/2 with

    D subset {x >= 0},  D above the line of B's edge L -> T,  D below the line of B' -> T'.

Then s >= 4.  Proof.  The three half-planes bound the triangle with base
h = (s - delta' - cos theta') - (delta + cos theta) on x = 0 and apex at
x* = h / (tan theta + tan theta'); its inradius is r = h / (tan + sec + tan' + sec').  D fits only
if r >= 1/2, i.e. h >= [(1 + sin t)/cos t + (1 + sin t')/cos t'] / 2.  All-ADJ gives
delta > s - 2 - w(theta) and delta' > s - 2 - w(theta'), so h < 4 - s + sin theta + sin theta'.
Hence g(theta) + g(theta') < 2 (4 - s) with g(t) := (1 + sin t)/cos t - 2 sin t, and
min_t g = g(t*) = 0.72355 at t* = 26.261 deg, so 1.44711 < 2 (4 - s), i.e. s < 4 - 0.72355.  Since
the window is s >= 3.82 > 3.27645 this is a contradiction: on [3.82, 4) the middle notch of every
wall of an all-ADJ ring holds no disc of radius 1/2, i.e. NO unit square of the pocket has its
INSCRIBED DISC there.  (A249's poking free square pokes a CORNER into the notch; its disc is in
the centre -- consistent.)  QED

ROBUST form: a disc of radius 1/2 disjoint from a square is beyond SOME edge line of it by at
least mu = 1/(2 sqrt2) (in a vertex cone the larger of the two edge distances is >= |q - P|/sqrt2),
so the case analysis only ever gets margin mu, not 1/2.  The same computation with mu gives
g2(t) := tan t / 2 + mu sec t - sin t, min g2 = 0.19658 at 28.904 deg, and the notch is dead for
s > 4 - 0.19658 = 3.80342 -- the window [3.82, 4) clears it, by 0.017.

What is NOT closed analytically: the corner wedge (between B's lower edge and A's left edge) and
the vertex sectors of the separation case analysis; see s.3 of the note.  This module computes the
constants and checks every lemma on the family's samples.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import family251 as F                                                 # noqa: E402
import geom248 as G                                                   # noqa: E402

HALF = math.pi / 2


def g(t):
    return (1.0 + math.sin(t)) / math.cos(t) - 2.0 * math.sin(t)


def g_min(grid=2000001):
    ts = np.linspace(1e-9, HALF - 1e-6, grid)
    v = (1.0 + np.sin(ts)) / np.cos(ts) - 2.0 * np.sin(ts)
    i = int(np.argmin(v))
    return float(v[i]), math.degrees(float(ts[i]))


def g_min_exact():
    """the stationary point of g: sec t (sec t + tan t) = 2 cos t (bisection)."""
    def d(t):
        return 1.0 / math.cos(t) * (1.0 / math.cos(t) + math.tan(t)) - 2.0 * math.cos(t)
    a, b = 1e-9, HALF - 1e-6
    for _ in range(200):
        m = 0.5 * (a + b)
        if d(m) < 0:
            a = m
        else:
            b = m
    t = 0.5 * (a + b)
    return g(t), math.degrees(t)


def g2(t, mu=None):
    """the ROBUST form: the separation margin from each edge line is only mu = 1/(2 sqrt2) (a disc
    of radius 1/2 disjoint from a square is beyond SOME edge line of it by at least mu), while the
    container still gives x >= 1/2.  Then h >= tan/2 + mu sec per toucher."""
    if mu is None:
        mu = 0.5 / math.sqrt(2.0)
    return 0.5 * math.tan(t) + mu / math.cos(t) - math.sin(t)


def g2_min(mu=None, grid=2000001):
    ts = np.linspace(1e-9, HALF - 1e-6, grid)
    v = np.array([g2(float(t), mu) for t in ts[::max(1, grid // 20001)]])
    tt = ts[::max(1, grid // 20001)]
    i = int(np.argmin(v))
    return float(v[i]), math.degrees(float(tt[i]))


def mid_notch_side_bound():
    """the largest side at which the middle-notch triangle can hold a disc of radius 1/2:
    s < 4 - min g.  (The window starts at 3.82, so the notch is dead on the whole window.)"""
    gm, td = g_min_exact()
    return 4.0 - gm, gm, td


def notch_inradius(theta, thetap, delta, deltap, s):
    """the exact inradius of the wall's middle triangle for given parameters (0 if empty)."""
    h = (s - deltap - math.cos(thetap)) - (delta + math.cos(theta))
    if h <= 0:
        return 0.0
    den = (math.tan(theta) + 1.0 / math.cos(theta) + math.tan(thetap) + 1.0 / math.cos(thetap))
    return h / den


def corner_wedge_bound(thetaB, deltaB, thetaA, deltaA):
    """the corner case: a disc of radius 1/2 below B's lower edge and above A's left edge has
    centre (u, v) with u (tan A - tan B) <= deltaB + deltaA tan A - (cos A + 1/(2 cos A))
    - (sin^2 B + 1/2)/cos B.  Returns (coef, rhs): coef * u <= rhs (a bound only when coef != 0)."""
    coef = math.tan(thetaA) - math.tan(thetaB)
    rhs = (deltaB + deltaA * math.tan(thetaA)
           - (math.cos(thetaA) + 0.5 / math.cos(thetaA))
           - (math.sin(thetaB) ** 2 + 0.5) / math.cos(thetaB))
    return float(coef), float(rhs)


def check_disc_free(q, polys, r=0.5, tol=1e-9):
    """is the disc of radius r about q disjoint from every ring square?"""
    from shapely.geometry import Point, Polygon
    d = Point(q[0], q[1]).buffer(r, 64)
    return all(Polygon(V).intersection(d).area <= tol for V in polys)


def family_checks(records, tol=1e-7):
    """GAP, MID-NOTCH (the inradius of every wall's triangle < 1/2) and the notch triangle stats
    over a list of {'x', 'side'} family samples."""
    rows = []
    for rec in records:
        x, s = rec['x'], rec['side']
        gl = F.gap_lemma(x, s)
        pairs = {'x=0': ('BL', 0, 'TL', 0), 'y=0': ('BL', 2, 'BR', 2),
                 'x=s': ('BR', 0, 'TR', 0), 'y=s': ('TL', 2, 'TR', 2)}
        ir = []
        for wname, (c1, j1, c2, j2) in pairs.items():
            i1, i2 = F.CORNERS.index(c1), F.CORNERS.index(c2)
            t1, d1 = x[4 * i1 + j1], x[4 * i1 + j1 + 1]
            t2, d2 = x[4 * i2 + j2], x[4 * i2 + j2 + 1]
            ir.append({'wall': wname, 'inradius': notch_inradius(t1, t2, d1, d2, s),
                       'g_sum': g(t1) + g(t2), 'two_gap': 2.0 * (4.0 - s),
                       'h': (s - d2 - math.cos(t2)) - (d1 + math.cos(t1))})
        rows.append({'side': s, 'margin': F.margin(x, s), 'walls': gl['walls'], 'notches': ir,
                     'gap_ok': all(w['ok'] for w in gl['walls']),
                     'notch_ok': all(r['inradius'] < 0.5 - tol for r in ir),
                     'gsum_ok': all(r['g_sum'] > r['two_gap'] for r in ir)})
    return rows


def main():
    gm, td = g_min_exact()
    gmg, tdg = g_min()
    sb, _, _ = mid_notch_side_bound()
    g2m, t2d = g2_min()
    out = {'g_min': gm, 'g_argmin_deg': td, 'g_min_grid': gmg, 'g_argmin_grid_deg': tdg,
           'g2_min': g2m, 'g2_argmin_deg': t2d, 'mid_notch_side_bound_robust': 4.0 - g2m,
           'mid_notch_side_bound': sb, 'three_disc_radius': 1.0 / math.sqrt(3.0),
           'window': [3.82, 4.0], 'mid_notch_dead_on_window': bool(3.82 >= sb)}
    src = os.path.join(ATT, 'results', 'joint251.json')
    recs = []
    if os.path.exists(src):
        j = json.load(open(src, encoding='utf-8'))
        for k, v in j.items():
            for x in v.get('rings', {}).get('x', []):
                recs.append({'x': x, 'side': float(k)})
    if not recs:
        seed = [0.254, 0.891, 0.254, 0.695, 1.317, 0.695, 1.317, 0.891]
        recs = [{'x': list(seed[:4]) + list(seed[4:8]) + list(seed[:4]) + list(seed[4:8]),
                 'side': 3.877084}]
    rows = family_checks(recs)
    out['samples'] = len(rows)
    out['gap_violations'] = sum(1 for r in rows if not r['gap_ok'])
    out['notch_violations'] = sum(1 for r in rows if not r['notch_ok'])
    out['gsum_violations'] = sum(1 for r in rows if not r['gsum_ok'])
    out['max_notch_inradius'] = max(n['inradius'] for r in rows for n in r['notches'])
    out['min_g_sum'] = min(n['g_sum'] for r in rows for n in r['notches'])
    out['rows'] = rows[:20]
    json.dump(out, open(os.path.join(ATT, 'results', 'analytic251.json'), 'w', encoding='utf-8'),
              indent=1)
    print('min g = %.5f at %.3f deg (grid %.5f at %.3f); MID-NOTCH dead for s > %.5f (window 3.82) %s'
          % (gm, td, gmg, tdg, sb, out['mid_notch_dead_on_window']))
    print('robust form (margin 1/(2 sqrt2)): min g2 = %.5f at %.3f deg -> dead for s > %.5f'
          % (g2m, t2d, 4.0 - g2m))
    print('samples %d: GAP violations %d, MID-NOTCH violations %d (max notch inradius %.4f, min g-sum %.4f vs 2(4-s) <= %.4f)'
          % (out['samples'], out['gap_violations'], out['notch_violations'],
             out['max_notch_inradius'], out['min_g_sum'], 2 * (4.0 - 3.82)))


if __name__ == '__main__':
    main()
