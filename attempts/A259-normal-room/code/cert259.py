"""A259 box-valid certificate of the CORNER-PAIR lemma (normal_room.md s.3) -- PIERCE by the container centre, per corner.

Statement certified on a parameter box B = [e0] x [phi0] x [delta1] x [phi1] at side s = SMAX (the corner frame is
monotone in s [T, s.2.3], so SMAX covers every s <= SMAX; the domain bounds use s >= SMIN):
    for EVERY pair configuration of B (in the pair domain) and EVERY unit square Q free of the four pair squares and
    inside the container:  NOT[(q-O).(-v) >= 1/2 and q_x >= s/2]  and  NOT[(q-O).u >= 1/2 and q_y <= s/2].
Soundness (pocket OVER-approximated, never the reverse):
  * CORE [T]: a unit square of centre c', tilt t' contains the square of centre c, tilt t, half-side 1/(2 w(|t-t'|)) - rho
    whenever |c - c'|_1 <= rho.  Over B: rho = r_pos + (1 + j sec.tan(phi_hi)) r_phi  (mean value bound on the centre).
  * KERNEL [T, A237]: every Q of a tilt bin [m - D, m + D] contains q + K, K of tilt m, half-side 1/(2 w(D)).
    So C_bin := {q : q + K inside container minus CORES} contains every admissible centre of the bin, over all of B.
  * the linear form over the bin: (q-O).n_psi <= (q-O).n_m + D |q-O|  (convex in q: maximal at polygon vertices).
  * LAYER: boxes inside {e0 >= 1 - ETA and delta1 >= 1 - ETA} are NOT certified (the closed limit e0 = delta1 = 1 has a
    unit square in the corner gap, so no box-valid certificate exists there): obligation CORNER-NOTCH.
  * a box is PRUNED only if two cores of different rows overlap (then every configuration of B overlaps) or B misses
    the domain:  e0 < 1, delta1 < 1, e0 > SMIN - 1 - span(phi0), delta1 > SMIN - 1 - span(phi1), containment at SMAX.
Floating point: shapely polygons, acceptance threshold margin <= -TOL (TOL = 1e-6).  [T-computed]
    python cert259.py --mode bench --n 200 --seed 1          (price)
    python cert259.py --mode run [--phimin 0 --phimax 45]    (adaptive tree; resumable by root-cell key; logs/STOP)
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np
from shapely.geometry import box as sbox

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom259 as Z                                                   # noqa: E402
import room259 as R                                                   # noqa: E402
import pair259 as P                                                   # noqa: E402

DEG = math.pi / 180.0
SMAX, SMIN, TOL = Z.SHAT, 3.82, 1e-6
ETA = 1.0 / 64                                                        # the OPEN double-limit layer e0, delta1 > 1 - ETA (s.3.3)
BINS = [(-45.0 + 1.0 * k + 0.5, 0.5) for k in range(90)]              # (mid, half-width) in degrees


def w_of(a):
    return math.cos(a) + math.sin(a)


def shrink(V, a):
    """the concentric square of half-side a with the same tilt as the unit square V."""
    ctr = V.mean(axis=0)
    return ctr + (V - ctr) * (2.0 * a)


def cores(lo, hi):
    mid, r = 0.5 * (lo + hi), 0.5 * (hi - lo)
    Vs = P.pair_verts(mid[0], mid[1], mid[2], mid[3], SMAX)
    out = []
    for i, V in enumerate(Vs):
        row, j = i // 2, i % 2
        rp, rf, fh = (r[0], r[1], hi[1]) if row == 0 else (r[2], r[3], hi[3])
        k = (1 - j) if row == 0 else j
        rho = rp + (1.0 + k * math.tan(fh) / math.cos(fh)) * rf
        a = 0.5 / w_of(rf) - rho
        if a <= 0.02:
            return None
        out.append(shrink(V, a))
    return out


def outside_domain(lo, hi):
    if lo[0] >= 1.0 or lo[2] >= 1.0:
        return True
    if hi[0] <= SMIN - 1.0 - Z.span(hi[1]) or hi[2] <= SMIN - 1.0 - Z.span(hi[3]):
        return True
    if lo[0] + Z.span(lo[1]) >= SMAX or lo[2] + Z.span(lo[3]) >= SMAX:
        return True
    return False


def check_box(lo, hi, bins=BINS):
    """('PRUNE'|'CERT'|'FAIL', margin).  margin = the certified upper bound of (q-O).n - 1/2 over the box (CERT: <= -TOL)."""
    lo, hi = np.array(lo, float), np.array(hi, float)
    if outside_domain(lo, hi):
        return 'PRUNE', None
    Cs = cores(lo, hi)
    if Cs is None:
        return 'FAIL', 9.0
    for i in (0, 1):
        for j in (2, 3):
            if Z.poly_gap(Cs[i], Cs[j]) < -1e-9:
                return 'PRUNE', None
    s = SMAX
    O = np.array([s / 2, s / 2])
    right, lower = sbox(s / 2, -1, s + 1, s + 1), sbox(-1, -1, s + 1, s / 2)
    worst = -9.0
    for md, hw in bins:
        psi, D = md * DEG, hw * DEG
        C = R.centre_set(Cs, s, psi, 0.5 / w_of(D))
        if C.is_empty:
            continue
        u = np.array([math.cos(psi), math.sin(psi)])
        v = np.array([-math.sin(psi), math.cos(psi)])
        for G, n in ((C.intersection(right), -v), (C.intersection(lower), u)):
            for Pg in R.polys_of(G):
                A = np.array(Pg.exterior.coords)[:-1] - O
                g = float((A @ n + D * np.linalg.norm(A, axis=1)).max()) - 0.5
                worst = max(worst, g)
        if worst > -TOL:
            return 'FAIL', worst
    return 'CERT', worst


def tree(lo, hi, depth, maxdepth, out, stats):
    if lo[0] >= 1.0 - ETA and lo[2] >= 1.0 - ETA:                     # CORNER-NOTCH layer: not certified, reported OPEN
        st, m = 'LAYER', None
    else:
        st, m = check_box(lo, hi)
    stats[st] = stats.get(st, 0) + 1
    if st != 'FAIL':
        out.append({'lo': list(map(float, lo)), 'hi': list(map(float, hi)), 'st': st, 'm': m})
        return True
    if depth >= maxdepth:
        out.append({'lo': list(map(float, lo)), 'hi': list(map(float, hi)), 'st': 'OPEN', 'm': m})
        return False
    r = (np.array(hi) - np.array(lo)) * np.array([1.0, 2.0, 1.0, 2.0])  # a tilt radian costs ~2x a position unit
    k = int(r.argmax())
    mid = 0.5 * (lo[k] + hi[k])
    ok = True
    for a, b in ((lo[k], mid), (mid, hi[k])):
        l2, h2 = list(lo), list(hi)
        l2[k], h2[k] = a, b
        ok = tree(l2, h2, depth + 1, maxdepth, out, stats) and ok
    return ok


def bench(n, seed, re, rf):
    rng = np.random.default_rng(seed)
    t0, res = time.time(), {}
    k = 0
    while k < n:
        f0, f1 = rng.uniform(0.0, 45, 2) * DEG
        e0, d1 = rng.uniform(max(0, SMIN - 1 - Z.span(f0)), 1), rng.uniform(max(0, SMIN - 1 - Z.span(f1)), 1)
        if SMAX - e0 - Z.span(f0) < 0 or SMAX - d1 - Z.span(f1) < 0 or P.pair_feas(e0, f0, d1, f1, SMAX) < 0:
            continue
        k += 1
        st, m = check_box([e0 - re, f0 - rf, d1 - re, f1 - rf], [e0 + re, f0 + rf, d1 + re, f1 + rf])
        res[st] = res.get(st, 0) + 1
    return res, (time.time() - t0) / n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', default='bench')
    ap.add_argument('--n', type=int, default=200)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--cells', type=int, default=9)                   # root grid per tilt axis (5-degree cells)
    ap.add_argument('--maxdepth', type=int, default=26)
    ap.add_argument('--only', default='')                             # "i,j" one root cell
    a = ap.parse_args()
    Z.belownormal()
    certs = os.path.join(HERE, '..', 'certs')
    os.makedirs(certs, exist_ok=True)
    if a.mode == 'bench':
        for re, rf in ((0.02, 0.01), (0.01, 0.005), (0.005, 0.0025), (0.0025, 0.00125)):
            res, dt = bench(a.n // 4, a.seed, re, rf)
            print(json.dumps({'r_pos': re, 'r_phi': rf, 'res': res, 'sec_per_box': round(dt, 3)}), flush=True)
        return
    stop = os.path.join(HERE, '..', 'logs', 'STOP')
    idx = os.path.join(certs, 'pair259_index.jsonl')
    done = {json.loads(l)['cell'] for l in open(idx)} if os.path.exists(idx) else set()
    step = 45.0 / a.cells
    for i in range(a.cells):
        for j in range(a.cells):
            cell = '%d,%d' % (i, j)
            if cell in done or (a.only and a.only != cell):
                continue
            if os.path.exists(stop):
                return
            t0, out, stats = time.time(), [], {}
            ok = tree([0.0, i * step * DEG, 0.0, j * step * DEG], [1.0, (i + 1) * step * DEG, 1.0, (j + 1) * step * DEG],
                      0, a.maxdepth, out, stats)
            with open(os.path.join(certs, 'pair259_cell_%d_%d.jsonl' % (i, j)), 'w') as fh:
                for row in out:
                    fh.write(json.dumps(row) + '\n')
            with open(idx, 'a') as fh:
                fh.write(json.dumps({'cell': cell, 'ok': ok, 'stats': stats, 'leaves': len(out),
                                     'sec': round(time.time() - t0, 1)}) + '\n')
            print(cell, ok, stats, round(time.time() - t0, 1), flush=True)


if __name__ == '__main__':
    main()
