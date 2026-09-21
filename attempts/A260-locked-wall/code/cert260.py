"""A260 box-valid certificates, by A259's method (cert259 is imported, never edited), on p = (b, phi, a', phi', e, e'):
  --fam layer : A259's OPEN layer {b, a' >= 63/64}, e = e' = 0, certified WITH THE PLUG  (CORNER-NOTCH, locked_wall.md s.4)
  --fam hybA  : floor wall an OPEN PAIR of common tilt, shift e in (0, EMAX];  right wall a row         (5 coordinates)
  --fam hybB  : right wall an OPEN PAIR, shift e' in (0, EMAX];  floor wall a row                       (5 coordinates)
  --fam hybAB : both walls open pairs                                                                  (6 coordinates)
Statement per box (side SMAX, monotone in s [T]; domain bounds with s >= SMIN): EVERY pair configuration of the box in
the domain, EVERY unit square Q in [0,s]^2 free of the four squares: NOT (i) and NOT (ii)  (pairh260 / pair259).
Soundness (the pocket is OVER-approximated): CORE of each square over the box (centre moves by <= rho in |.|_1,
rho = sum of the position radii that move it + (1 + k sec.tan(phi_hi)) r_phi, k = 1 for s1 and W'); KERNEL per tilt bin;
PLUG [T]: added as a fifth obstacle only when the box has a' > PLUG_A = 0.354 + RHO (then no free square meets it).
PRUNE only if the box misses the domain (b, a' < 1; a, b' < 1; all-ADJ reaches for the hyb families; containment at
SMAX) or two cores of different walls overlap.  Leaves: CERT / PRUNE / OPEN (depth limit).  Resumable per root cell.
    python cert260.py --mode bench --fam hybA --n 120      python cert260.py --mode run --fam layer [--only i,j]"""
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
import pairh260 as PH                                                 # noqa: E402
import room259 as R                                                   # noqa: E402
import cert259 as K                                                   # noqa: E402  (SMAX, SMIN, TOL, BINS, shrink, w_of)
Z = PH.Z
DEG = math.pi / 180.0
SMAX, SMIN, TOL, ETA = K.SMAX, K.SMIN, K.TOL, K.ETA
PLUG_A = 0.354 + PH.RHO
EMAX = 0.5
WEIGHT = np.array([1.0, 2.0, 1.0, 2.0, 1.0, 1.0])


def sec(f):
    return 1.0 / math.cos(f)


def cores(lo, hi):
    mid, r = 0.5 * (lo + hi), 0.5 * (hi - lo)
    Vs = PH.pairh_verts(mid, SMAX)
    rho = [r[0] + r[4] + (1.0 + math.tan(hi[1]) * sec(hi[1])) * r[1], r[0] + r[1],
           r[2] + r[3], r[2] + r[5] + (1.0 + math.tan(hi[3]) * sec(hi[3])) * r[3]]
    rf = [r[1], r[1], r[3], r[3]]
    out = []
    for V, ro, f in zip(Vs, rho, rf):
        a = 0.5 / K.w_of(f) - ro
        if a <= 0.02:
            return None
        out.append(K.shrink(V, a))
    return out


def outside_domain(lo, hi, adj):
    if lo[0] >= 1.0 or lo[2] >= 1.0:
        return True
    if hi[0] + hi[4] <= SMIN - 1.0 - Z.span(hi[1]) or hi[2] + hi[5] <= SMIN - 1.0 - Z.span(hi[3]):   # a < 1, b' < 1
        return True
    if lo[0] + lo[4] + Z.span(lo[1]) >= SMAX or lo[2] + lo[5] + Z.span(lo[3]) >= SMAX:                # a > 0, b' > 0
        return True
    if adj:
        if lo[0] + lo[4] + sec(lo[1]) > 2.0 or lo[2] + lo[5] + sec(lo[3]) > 2.0:                     # s1, W' reach
            return True
        if hi[0] + K.w_of(hi[1]) < SMIN - 2.0 or hi[2] + K.w_of(hi[3]) < SMIN - 2.0:                 # W, S' reach
            return True
    return False


def check_box(lo, hi, bins=K.BINS, adj=True):
    lo, hi = np.array(lo, float), np.array(hi, float)
    if outside_domain(lo, hi, adj):
        return 'PRUNE', None
    Cs = cores(lo, hi)
    if Cs is None:
        return 'FAIL', 9.0
    for i in (0, 1):
        for j in (2, 3):
            if Z.poly_gap(Cs[i], Cs[j]) < -1e-9:
                return 'PRUNE', None
    s = SMAX
    if lo[2] > PLUG_A:
        Cs = Cs + [PH.plug(s)]
    O = np.array([s / 2, s / 2])
    right, lower = sbox(s / 2, -1, s + 1, s + 1), sbox(-1, -1, s + 1, s / 2)
    worst = -9.0
    for md, hw in bins:
        psi, D = md * DEG, hw * DEG
        C = R.centre_set(Cs, s, psi, 0.5 / K.w_of(D))
        if C.is_empty:
            continue
        u = np.array([math.cos(psi), math.sin(psi)])
        v = np.array([-math.sin(psi), math.cos(psi)])
        for G, n in ((C.intersection(right), -v), (C.intersection(lower), u)):
            for Pg in R.polys_of(G):
                A = np.array(Pg.exterior.coords)[:-1] - O
                worst = max(worst, float((A @ n + D * np.linalg.norm(A, axis=1)).max()) - 0.5)
        if worst > -TOL:
            return 'FAIL', worst
    return 'CERT', worst


def tree(lo, hi, depth, maxdepth, out, stats, adj):
    st, m = check_box(lo, hi, adj=adj)
    stats[st] = stats.get(st, 0) + 1
    if st != 'FAIL':
        out.append({'lo': list(map(float, lo)), 'hi': list(map(float, hi)), 'st': st, 'm': m})
        return True
    if depth >= maxdepth:
        out.append({'lo': list(map(float, lo)), 'hi': list(map(float, hi)), 'st': 'OPEN', 'm': m})
        return False
    k = int(((np.array(hi) - np.array(lo)) * WEIGHT).argmax())
    mid = 0.5 * (lo[k] + hi[k])
    ok = True
    for a, b in ((lo[k], mid), (mid, hi[k])):
        l2, h2 = list(lo), list(hi)
        l2[k], h2[k] = a, b
        ok = tree(l2, h2, depth + 1, maxdepth, out, stats, adj) and ok
    return ok


def root(fam, i, j, step):
    lo = [0.0, i * step * DEG, 0.0, j * step * DEG, 0.0, 0.0]
    hi = [1.0, (i + 1) * step * DEG, 1.0, (j + 1) * step * DEG, 0.0, 0.0]
    if fam == 'layer':
        lo[0] = lo[2] = 1.0 - ETA
    if fam in ('hybA', 'hybAB'):
        hi[4] = EMAX
    if fam in ('hybB', 'hybAB'):
        hi[5] = EMAX
    return lo, hi


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', default='bench')
    ap.add_argument('--fam', default='layer')
    ap.add_argument('--n', type=int, default=120)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--cells', type=int, default=9)
    ap.add_argument('--maxdepth', type=int, default=30)
    ap.add_argument('--only', default='')
    a = ap.parse_args()
    Z.belownormal()
    adj = a.fam != 'layer'
    certs = os.path.join(HERE, '..', 'certs')
    if a.mode == 'bench':
        import bench260
        bench260.run(a, check_box, adj)
        return
    stop = os.path.join(HERE, '..', 'logs', 'STOP')
    idx = os.path.join(certs, '%s260_index.jsonl' % a.fam)
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
            lo, hi = root(a.fam, i, j, step)
            ok = tree(lo, hi, 0, a.maxdepth, out, stats, adj)
            with open(os.path.join(certs, '%s260_cell_%d_%d.jsonl' % (a.fam, i, j)), 'w') as fh:
                for row in out:
                    fh.write(json.dumps(row) + '\n')
            with open(idx, 'a') as fh:
                fh.write(json.dumps({'cell': cell, 'ok': ok, 'stats': stats, 'leaves': len(out),
                                     'sec': round(time.time() - t0, 1)}) + '\n')
            print(a.fam, cell, ok, stats, round(time.time() - t0, 1), flush=True)


if __name__ == '__main__':
    main()
