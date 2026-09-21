"""A258: the NINTH square of a normal ring [M].

find_ninth(sq, s, target) maximises, over the pose of one more unit square F,
    min( gap(F, Q) for the ring squares Q,  depth(F, target) )
with HARD containment: F's centre is parametrised inside [w/2, s - w/2]^2 (w = |cos| + |sin|), so F is in the
container for every parameter value -- no containment penalty.  target = a wall's RIBBON [s-2, 2] x [0, 1] (the
poker) or a corner BOX (a third box meeter).  A positive optimum is re-checked (containment, 8 gaps, Hall).

    python poker258.py          # table over the C4 slice of D: results/poker258.jsonl
"""
import json
import math
import os

import numpy as np
from scipy.optimize import minimize

import dom258 as Dm
import geo258 as G

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, '..', 'results', 'poker258.jsonl'))


def square(u, v, th, s):
    w = abs(math.cos(th)) + abs(math.sin(th))
    sig = lambda z: 1.0 / (1.0 + math.exp(-max(-40.0, min(40.0, z))))
    cx, cy = w / 2 + (s - w) * sig(u), w / 2 + (s - w) * sig(v)
    c, g = math.cos(th), math.sin(th)
    return np.array([[cx + 0.5 * (p * c - q * g), cy + 0.5 * (p * g + q * c)]
                     for p, q in ((-1, -1), (1, -1), (1, 1), (-1, 1))])


def inv(cx, cy, th, s):
    w = abs(math.cos(th)) + abs(math.sin(th))
    lg = lambda p: math.log(p / (1 - p))
    cl = lambda p: min(max(p, 1e-6), 1 - 1e-6)
    return [lg(cl((cx - w / 2) / (s - w))), lg(cl((cy - w / 2) / (s - w))), th]


def margin(z, sq, s, target):
    F = square(z[0], z[1], z[2], s)
    return min(min(G.sat_gap(F, Q) for Q in sq), G.depth(F, target))


def find_ninth(sq, s, target, starts, maxiter=900):
    best = (-9.0, None)
    for cx, cy, th in starts:
        r = minimize(lambda z: -margin(z, sq, s, target), inv(cx, cy, th, s), method='Nelder-Mead',
                     options=dict(xatol=1e-9, fatol=1e-12, maxiter=maxiter))
        if -r.fun > best[0]:
            best = (float(-r.fun), square(r.x[0], r.x[1], r.x[2], s))
    return best


def tooth_starts(s, w, a, phi, rng, k=6):
    """starts: a square standing in the tooth of wall w (same tilt), and jittered copies."""
    c, g = math.cos(phi), math.sin(phi)
    apex = np.array([a + 1 / c, c])
    ctr = apex + 0.5 * np.array([c - g, c + g])                       # the square sitting in the notch
    out = []
    for i in range(k):
        p = ctr + (rng.normal(0, 0.05, 2) if i else 0) + np.array([0.0, 0.02 * i])
        xy = G.wall_to_xy(w, s, [p])[0]
        out.append((float(xy[0]), float(xy[1]), phi + (rng.normal(0, 0.15) if i else 0.0)))
    return out


def box_starts(s, k, rng, n=8):
    out = []
    for _ in range(n):
        p = G.wall_to_xy(k, s, [(rng.uniform(0.9, 1.7), rng.uniform(0.9, 1.7))])[0]
        out.append((float(p[0]), float(p[1]), rng.uniform(0, math.pi / 2)))
    return out


def ninth_report(s, a, phi, rng, walls=(0,), boxes=(0,)):
    sq = G.ring(s, a, phi)
    rep = {}
    for w in walls:
        m, F = find_ninth(sq, s, G.ribbon(s, w), tooth_starts(s, w, a[w], phi[w], rng))
        rep['ribbon%d' % w] = m
        if m > 0:
            nine = sq + [F]
            cm, pg = G.check_packing(nine, s)
            rep['ribbon%d_check' % w] = dict(contain=cm, pair_gap=pg, hall_min=G.hall_min(nine, s, 1e-9)[0],
                                             F=[[round(float(v), 6) for v in p] for p in F])
    for k in boxes:
        m, F = find_ninth(sq, s, G.cells(s)[('C', k)], box_starts(s, k, rng))
        rep['box%d' % k] = m
    return rep


def main():
    rng = np.random.default_rng(258)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        for s in (3.82, G.SHAT, 3.95, 3.99):
            for deg in (2, 5, 8, 11, 14.545, 18, 22, 26):
                phi = [deg * G.DEG] * 4
                for kind in ('centre', 'tight'):
                    if kind == 'centre':
                        t, a = Dm.sup_margin(s, phi, slots=True)
                    else:
                        a0, _ = G.tight_ring(s, phi[0])
                        a, t = [a0] * 4, G.in_D(s, [a0] * 4, phi)
                    if a is None or t < -1e-9:
                        continue
                    rep = ninth_report(s, a, phi, rng)
                    row = dict(s=s, phi_deg=deg, kind=kind, a=a[0], b=G.end_offset(s, a[0], phi[0]), D_margin=t,
                               tooth=G.tooth_terms(s, a[0], phi[0]), **rep)
                    f.write(json.dumps(row) + '\n')
                    f.flush()
                    print('%.4f %6.3f %-6s a=%.4f  tooth=(%+.3f,%+.3f) ribbon=%+.5f box=%+.5f hall=%s' % (
                        s, deg, kind, a[0], row['tooth'][0], row['tooth'][1], rep['ribbon0'], rep['box0'],
                        rep.get('ribbon0_check', {}).get('hall_min')), flush=True)


if __name__ == '__main__':
    main()
