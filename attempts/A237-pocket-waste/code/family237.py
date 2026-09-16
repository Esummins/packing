"""A237 Theorem POCKET-CAP on the n = 11 window family and the n-general table (docs/proofs/pocket_waste.md s.3).
The WINDOW FAMILY ring(S, theta): at each corner (frame u, v) a FLAT meeter A on one wall at the least offset
delta = sin(theta) + 0.02 that admits a partner of tilt theta (Lemma TILT-MIN, s.1) and the tilted meeter B in
mode (a) -- lowest vertex at (sin theta + eta, 1 - (delta - sin theta - eta) tan theta + eta), leftmost vertex
eta off the wall, resting eta above A's corner -- alternating floor / wall variants around the container as in
A226's ring11; p = 8.  For S in {3.82, 3.85, 3.877} and theta = 1..45 deg: the ring is verified as a packing
(SAT), the pocket's area / rigorous coverable-area bound / waste, PIERCE(1) at the centre, PIERCE(2) on the
diagonals, A222's greedy placer for k = 1, 2, 3 (measured capacity).  CLOSES iff PIERCE(2) certifies capacity <= 2
or the coverable area is < 3.
The n-GENERAL TABLE: one corner crowd at tilt theta in a large box gives the exact uncoverable area w_c(theta) of
the sealed corner region (strip + wedge); a four-crowd wastes >= 4 w_c(theta_min); the area bound closes at n iff
4 w_c(theta_min) > s(n)^2 - n; the table gives, per n < m, the least tilt floor theta* on the 1-degree grid that
closes, or none.
    python family237.py  -> results/family237.jsonl, results/table237.jsonl
"""
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
try:
    import psutil
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    psutil.Process().cpu_affinity(list(range(16)))
except Exception:
    pass
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'A236-ring-capacity', 'code'))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'A222-ring-swap', 'code'))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'A217-torque-probe', 'code'))
import geom237 as G                                                    # noqa: E402
import band236 as BD                                                   # noqa: E402

ATT = os.path.abspath(os.path.join(HERE, '..'))
OUT = os.path.join(ATT, 'results', 'family237.jsonl')
TAB = os.path.join(ATT, 'results', 'table237.jsonl')
ETA = 1e-3
STEP = 1.0


def crowd_pair(theta, margin=0.02, eta=ETA):
    """BL-frame poses (u, v, th) of A (flat, floor, offset delta) and B (tilt theta, wall side), floor variant."""
    th = math.radians(theta)
    delta = math.sin(th) + margin
    xv = math.sin(th) + eta
    yv = 1.0 - (delta - xv) * math.tan(th) + eta
    A = (delta + 0.5, 0.5, 0.0)
    cB = (xv + (math.cos(th) - math.sin(th)) / 2, yv + (math.sin(th) + math.cos(th)) / 2)
    B = (cB[0], cB[1], th)
    return A, B, delta


def to_container(c, S, u, v, th):
    if c == 'BL':
        return (u, v, th)
    if c == 'BR':
        return (S - u, v, -th)
    if c == 'TR':
        return (S - u, S - v, th)
    return (u, S - v, -th)


def ring(S, theta, margin=0.02):
    out = []
    for c, var in zip(BD.CORNERS, ('floor', 'wall', 'floor', 'wall')):
        A, B, delta = crowd_pair(theta, margin)
        if var == 'wall':
            A, B = (A[1], A[0], 0.0), (B[1], B[0], -B[2])
        out.append(to_container(c, S, *A))
        out.append(to_container(c, S, *B))
    return out, delta


def greedy_capacity(members, S):
    import region222 as RG
    thetas = [math.radians(t) for t in range(0, 90, 5)]
    k = 0
    for kk in (1, 2, 3):
        if RG.greedy(members, S, kk, thetas, beam=3) is None:
            break
        k = kk
    return k


def family():
    rows = []
    for S in (3.82, 3.85, 3.877):
        for theta in (1, 2, 5, 10, 15, 20, 25, 30, 35, 40, 45):
            t0 = time.time()
            R, delta = ring(S, theta)
            ok, gap, wall = BD.check_packing(R, S)
            ms = {c: BD.meeters(R, S, c) for c in BD.CORNERS}
            W = G.waste(R, S, STEP)
            c = S / 2.0
            p1 = G.pierce(R, S, [(c, c)], STEP, free=W['free'])
            best = None
            for t in (0.3, 0.4, 0.5, 0.6, 0.7):
                for pts in ([(c - t, c - t), (c + t, c + t)], [(c - t, c + t), (c + t, c - t)]):
                    v = G.pierce(R, S, pts, STEP, free=W['free'])
                    if best is None or v < best[0]:
                        best = (v, pts)
            verts, edges = G.features(W['pocket'])
            conv = [v['angle'] for v in verts if v['convex']]
            kcap = greedy_capacity(R, S) if ok else None
            row = {'S': S, 'theta': theta, 'delta': delta, 'packing_ok': bool(ok), 'gap': gap, 'wall': wall,
                   'four_crowd': bool(all(len(ms[cc]) >= 2 for cc in BD.CORNERS)), 'meeters': ms,
                   'area': W['area'], 'coverable': W['coverable_area'], 'waste': W['waste'],
                   'pierce1': p1, 'pierce2': best[0], 'pierce2_pts': best[1], 'pierce2_ok': bool(best[0] <= 1e-9),
                   'greedy_capacity': kcap, 'n_convex': len(conv), 'n_acute': sum(a < 90 - 1e-6 for a in conv),
                   'min_convex_angle': min(conv) if conv else None, 'n_reflex': len(verts) - len(conv),
                   'closes_area': bool(W['coverable_area'] < 3.0), 'closes_pierce': bool(best[0] <= 1e-9),
                   'ring': [list(p) for p in R], 'secs': time.time() - t0}
            row['closes'] = row['closes_area'] or row['closes_pierce']
            rows.append(row)
            print('S %.3f theta %2d ok %s crowd %s area %.3f cov %.3f waste %.3f p1 %.4f p2 %.4f greedy %s closes %s %.0fs' % (
                S, theta, ok, row['four_crowd'], row['area'], row['coverable'], row['waste'], p1, best[0], kcap,
                row['closes'], row['secs']), flush=True)
    with open(OUT, 'w', encoding='utf-8') as fh:
        for r in rows:
            fh.write(json.dumps(r) + '\n')
    return rows


def corner_waste(theta, box=6.0, margin=0.02):
    """uncoverable area attached to ONE crowd (A, B) at tilt theta in the BL corner of a large box."""
    A, B, delta = crowd_pair(theta, margin)
    W = G.waste([A, B], box, STEP)
    comps = G.components(W['uncov'])
    near = [c for c in comps if c['cx'] < 3.0 and c['cy'] < 3.0]
    return sum(c['area'] for c in near), delta


def table():
    rec = BD.records()
    wc = {}
    for theta in range(1, 46):
        wc[theta] = corner_waste(theta)[0]
        print('corner waste theta %2d: %.4f' % (theta, wc[theta]), flush=True)
    rows = []
    for n in range(5, 61):
        m = math.ceil(math.sqrt(n))
        s = rec[n]
        if s >= m - 1e-9:
            continue
        slack = s * s - n
        closing = [t for t in range(1, 46) if 4 * wc[t] > slack]
        rows.append({'n': n, 'm': m, 's': s, 'area_slack': slack, 'p': 8, 'need': n - 8,
                     'theta_star': closing[0] if closing else None, 'w4_at_45': 4 * wc[45], 'w4_at_20': 4 * wc[20],
                     'w4_at_10': 4 * wc[10]})
    with open(TAB, 'w', encoding='utf-8') as fh:
        fh.write(json.dumps({'corner_waste': wc}) + '\n')
        for r in rows:
            fh.write(json.dumps(r) + '\n')
    for r in rows:
        print('n %2d s %.4f slack %.3f theta* %s' % (r['n'], r['s'], r['area_slack'], r['theta_star']))


if __name__ == '__main__':
    if '--table-only' not in sys.argv:
        family()
    table()
