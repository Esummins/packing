"""A251 task 2: the BOX-VALID PIERCE certificate over the ring family, and its PRICE.

For a box of half-widths `rad` about a ring x0 the cores shrink by
    eps_i(rad) = 0.5 - (0.5 - rho_i) / w(dtheta_i)
(geom251), and PIERCE over the box is the PIERCE of the shrunk cores.  So the box radius a
certificate tolerates is governed by the SHRINK TOLERANCE eps* of the ring: the largest uniform
core shrink at which PIERCE(k) still has residual 0.  Then

    admissible radius r:   max_i eps_i(r * 1) <= eps*        (17 coordinates)
    box count             N(r) = prod_i (range_i / (2r)) / 8 (the D4 quotient)

    python cert251.py --stage tol|pilot|all [--sides ...] [--boxes 200]
        -> results/cert251.json   (resumable per stage+side; logs/STOP honoured)
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import geom251 as C                                                   # noqa: E402
import family251 as F                                                 # noqa: E402

RES = os.path.join(ATT, 'results', 'cert251.json')
STOP = os.path.join(ATT, 'logs', 'STOP')
SEED_X = [0.254, 0.891, 0.254, 0.695, 1.317, 0.695, 1.317, 0.891]


def belownormal():
    try:
        import psutil
        p = psutil.Process()
        p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        p.cpu_affinity(list(range(min(16, os.cpu_count() or 16))))
    except Exception:
        pass


def seed_ring():
    return list(SEED_X[:4]) + list(SEED_X[4:8]) + list(SEED_X[:4]) + list(SEED_X[4:8])


def load_rings(sides, per_side=2, restarts=8):
    """feasible rings for the pilot: A251's joint251.json store if it exists (the ladder runs the
    joint search first), else a short sampling seeded by A249's C2 witness."""
    src = os.path.join(ATT, 'results', 'joint251.json')
    out = []
    if os.path.exists(src):
        j = json.load(open(src, encoding='utf-8'))
        for k, v in j.items():
            for x in v.get('rings', {}).get('x', [])[:per_side]:
                out.append({'x': x, 'side': float(k)})
    if out:
        return out
    for s in sides:
        for r0 in F.sample_rings(s, restarts, sym_seed=SEED_X)[:per_side]:
            out.append({'x': r0['x'], 'side': s})
    if not out:
        out = [{'x': seed_ring(), 'side': 3.877084}]
    return out


def eps_of_radius(r):
    """the worst per-member effective core shrink of the uniform box of half-width r."""
    rad = [r] * 17
    rhos, dths = F.deviations(rad)
    return max(0.5 - C.core_half(rho, dth) for rho, dth in zip(rhos, dths))


def radius_for_eps(eps, lo=0.0, hi=0.25, iters=40):
    if eps_of_radius(hi) <= eps:
        return hi
    a, b = lo, hi
    for _ in range(iters):
        m = 0.5 * (a + b)
        if eps_of_radius(m) <= eps:
            a = m
        else:
            b = m
    return a


def box_count(r, s_lo=3.82, s_hi=4.0):
    n = 1.0
    for (a, b) in F.bounds(s_lo, s_hi):
        n *= max(1.0, (b - a) / (2.0 * r))
    return n / 8.0


def analyse_ring(x, s, step_deg=1.0, tol=1e-9):
    """PIERCE at the exact ring (eps = 0) and the shrink tolerances of PIERCE(1) / PIERCE(2)."""
    poses, names, _ = F.poses_of(x, s)
    mem = [(p[0], p[1], p[2], 0.5) for p in poses]
    t0 = time.time()
    free = C.free_bins(mem, s, step_deg)
    c = (s / 2.0, s / 2.0)
    r1 = C.pierce(mem, s, [c], free=free)
    r2, pts2 = C.best_pierce2(mem, s, free)
    out = {'side': s, 'margin': F.margin(x, s), 'poses': dict(zip(names, poses)),
           'pocket_area': float(C.pocket_bar(mem, s).area),
           'pierce1_centre': r1, 'pierce2_best': r2, 'pierce2_points': pts2,
           'capacity_le_1': bool(r1 <= tol), 'capacity_le_2': bool(r2 <= tol or r1 <= tol),
           'seconds_pierce': time.time() - t0}
    e1 = C.shrink_tolerance(poses, s, [c])
    e2, pts2b = C.shrink_tolerance2(poses, s)
    out['eps_star_pierce1'] = e1[0]
    out['eps_star_pierce2'] = max(e1[0], e2)
    out['pierce_points_used'] = pts2b or pts2
    for tag, eps in (('pierce1', e1[0]), ('pierce2', max(e1[0], e2))):
        r = radius_for_eps(eps)
        out['radius_' + tag] = r
        out['boxes_' + tag] = box_count(r) if r > 0 else float('inf')
    return out


def random_box(rng, rings, r, s_lo, s_hi):
    """a box centre: a feasible ring jittered inside the family's neighbourhood."""
    base = rings[rng.integers(len(rings))]
    x = np.array(base['x'][:16]) + rng.normal(0.0, 3.0 * r, 16)
    s = float(np.clip(base['side'] + rng.normal(0.0, 3.0 * r), s_lo, s_hi))
    return list(map(float, x)) + [s]


def pilot(rings, r, boxes, s_lo, s_hi, seed=251, step_deg=3.0):
    """the first `boxes` boxes of radius r: discard by margin_ub, else core + PIERCE(2)."""
    rng = np.random.default_rng(seed)
    rad = [r] * 17
    rows, t0 = [], time.time()
    empty = 0
    for k in range(boxes):
        if os.path.exists(STOP):
            break
        xc = random_box(rng, rings, r, s_lo, s_hi)
        ub = F.margin_ub(xc, rad)
        if ub < 0:
            rows.append({'kind': 'discarded', 'margin_ub': ub, 'seconds': 0.0})
            continue
        s_max = xc[16] + r
        poses, names, _ = F.poses_of(xc[:16], xc[16])
        rhos, dths = F.deviations(rad)
        mem = C.core_members(poses, rhos, dths)
        if min(m[3] for m in mem) <= 0:
            empty += 1
            rows.append({'kind': 'empty_core', 'margin_ub': ub, 'core_half': min(m[3] for m in mem),
                         'seconds': 0.0})
            continue
        t1 = time.time()
        free = C.free_bins(mem, s_max, step_deg)
        c = (s_max / 2.0, s_max / 2.0)
        p1 = C.pierce(mem, s_max, [c], free=free)
        p2, pts = C.best_pierce2(mem, s_max, free, g=3)
        rows.append({'kind': 'certified' if min(p1, p2) <= 1e-9 else 'failed', 'margin_ub': ub,
                     'core_half': float(min(m[3] for m in mem)), 'pierce1': p1, 'pierce2': p2,
                     'seconds': time.time() - t1})
    done = [r0 for r0 in rows if r0['kind'] in ('certified', 'failed')]
    return {'radius': r, 'boxes': len(rows), 'wall_seconds': time.time() - t0,
            'n_discarded': sum(1 for r0 in rows if r0['kind'] == 'discarded'),
            'n_empty_core': empty, 'n_certified': sum(1 for r0 in rows if r0['kind'] == 'certified'),
            'n_failed': sum(1 for r0 in rows if r0['kind'] == 'failed'),
            'seconds_per_live_box': (sum(r0['seconds'] for r0 in done) / len(done)) if done else None,
            'core_half_min': min([r0.get('core_half', 0.5) for r0 in rows] or [None]),
            'rows': rows[:40]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--stage', default='all')
    ap.add_argument('--sides', default='3.877084,3.90,3.95,3.99')
    ap.add_argument('--restarts', type=int, default=24)
    ap.add_argument('--boxes', type=int, default=200)
    a = ap.parse_args()
    belownormal()
    out = json.load(open(RES, encoding='utf-8')) if os.path.exists(RES) else {}
    sides = [float(v) for v in a.sides.split(',')]
    if a.stage in ('tol', 'all'):
        out.setdefault('rings', {})
        store = load_rings(sides, per_side=4, restarts=a.restarts)
        for s in sides:
            if os.path.exists(STOP):
                print('STOP present')
                break
            key = '%.6f' % s
            if key in out['rings']:
                continue
            rs = [{'x': r['x'], 'margin': F.margin(r['x'], s)} for r in store
                  if abs(r['side'] - s) < 1e-9]
            if not rs:
                rs = F.sample_rings(s, a.restarts, sym_seed=SEED_X)
            recs = []
            for r0 in rs[:4]:
                rec = analyse_ring(r0['x'], s)
                recs.append(rec)
                print('s %.6f margin %+.4f: pierce1 %.3e pierce2 %.3e eps* %.4f r %.2e boxes %.3g'
                      % (s, rec['margin'], rec['pierce1_centre'], rec['pierce2_best'],
                         rec['eps_star_pierce2'], rec['radius_pierce2'], rec['boxes_pierce2']),
                      flush=True)
            out['rings'][key] = {'n_found': len(rs), 'records': recs}
            json.dump(out, open(RES, 'w', encoding='utf-8'), indent=1)
    if a.stage in ('pilot', 'all'):
        rings = load_rings(sides)
        recs = [r for v in out.get('rings', {}).values() for r in v['records']]
        eps = min([r['eps_star_pierce2'] for r in recs] or [0.1396484375])
        r_adm = max(1e-4, radius_for_eps(eps))
        out['eps_star_used'] = eps
        out['pilot'] = {}
        for r in sorted({r_adm, 1e-3, 1e-2}):
            if os.path.exists(STOP):
                break
            p = pilot(rings, r, a.boxes, min(sides), max(sides))
            out['pilot']['%.5f' % r] = p
            print('radius %.5f: %d boxes, %d certified, %d failed, %d empty core, %.3f s/box, N = %.3g'
                  % (r, p['boxes'], p['n_certified'], p['n_failed'], p['n_empty_core'],
                     p['seconds_per_live_box'] or 0.0, box_count(r)), flush=True)
            json.dump(out, open(RES, 'w', encoding='utf-8'), indent=1)
    json.dump(out, open(RES, 'w', encoding='utf-8'), indent=1)


if __name__ == '__main__':
    main()
