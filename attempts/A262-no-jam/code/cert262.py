"""A262 box-valid certificate kernels (A259's method; cert259 / room259 imported, never edited).  Corner frame BL,
side SMAX (the sector statement is monotone in s [T, normal_room.md s.2.3]).  Sectors: 'BL-floor' NOT[(q-O).(-v) >= 1/2
and q_x <= s/2], 'BL-left' NOT[(q-O).(-u) >= 1/2 and q_y <= s/2] for every unit square Q free of the obstacles.
FAMILY 'jam'   p = (d0, alpha, yX, phiX, cx, cy, th):  A, A2 = floor row of two (START offset d0, tilt alpha);  X touches
               x = 0, lowest point at height yX, tilt phiX;  C = the floater (centre, tilt), meets the open box.
               Domain (necessary for a DIRECT JAM, box_meeters.md s.1.2 / no_jam.md s.1): d0 < 1; yX >= 1 - cos phiX
               (X misses the open box); X inside [0, SMAX]; C meets the open box; X meets C's wall drop T_u; A or A2
               meets C's floor drop T_v; A, A2, X, C pairwise interior-disjoint.
FAMILY 'pair3' p = (b, phi, a', phi'):  A259's corner PAIR WITHOUT the wall row's second square -- here: left-wall
               row of two with END gap b at BL (tilt phi) + the floor's START square only (offset a', tilt phi').
               (the TL corner of a JAM ring, rotated; a', b < 1.)
Soundness: obstacles replaced by CORES inside them over the whole box (centre motion <= rho in |.|_1, tilt kernel
1/(2 w(r_tilt))); Q's tilt binned (A237 kernel): the pocket is OVER-approximated.  PRUNE only when NO configuration of
the box lies in the domain (outer approximations, slack = motion bounds) or two cores overlap.
    python cert262.py --mode bench [--n 40]     -> results/bench262.json"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np
from shapely.geometry import box as sbox

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import geom262 as G                                                   # noqa: E402
import room259 as R                                                   # noqa: E402
import cert259 as K                                                   # noqa: E402
Z = G.Z
SMAX, SMIN, TOL = K.SMAX, K.SMIN, K.TOL
BOXP = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], float)
H2 = math.sqrt(0.5)


def sec_tan(f):
    return math.tan(f) / math.cos(f)


def squares(p, s):
    row = Z.row_verts(p[0], p[1], s, 0)
    wx = math.cos(p[3]) + math.sin(p[3])
    X = Z.sq_verts(0.5 * wx, p[2] + 0.5 * wx, p[3])
    return [row[0], row[1], X, Z.sq_verts(p[4], p[5], p[6])]


def squares_pair3(p, s):
    wall = Z.row_verts(s - p[0] - Z.span(p[1]), p[1], s, 3)
    return [wall[0], wall[1], Z.row_verts(p[2], p[3], s, 0)[0]]


def cores_of(Vs, rho, rt):
    out = []
    for V, ro, f in zip(Vs, rho, rt):
        a = 0.5 / K.w_of(f) - ro
        if a <= 0.02:
            return None
        out.append(K.shrink(V, a))
    return out


def sectors_ok(Cs, bins, extra=()):
    s = SMAX
    O = np.array([s / 2, s / 2])
    left, lower = sbox(-1, -1, s / 2, s + 1), sbox(-1, -1, s + 1, s / 2)
    worst = -9.0
    for md, hw in bins:
        psi, D = md * Z.DEG, hw * Z.DEG
        C = R.centre_set(list(Cs) + list(extra), s, psi, 0.5 / K.w_of(D))
        if C.is_empty:
            continue
        u = np.array([math.cos(psi), math.sin(psi)])
        v = np.array([-math.sin(psi), math.cos(psi)])
        for Gm, n in ((C.intersection(left), -v), (C.intersection(lower), -u)):
            for Pg in R.polys_of(Gm):
                A = np.array(Pg.exterior.coords)[:-1] - O
                worst = max(worst, float((A @ n + D * np.linalg.norm(A, axis=1)).max()) - 0.5)
        if worst > -TOL:
            return 'FAIL', worst
    return 'CERT', worst


def check_box(lo, hi, bins=K.BINS):
    lo, hi = np.array(lo, float), np.array(hi, float)
    mid, r = 0.5 * (lo + hi), 0.5 * (hi - lo)
    s = SMAX
    if lo[0] >= 1.0 or hi[2] + 1.0 > s or hi[2] < 1.0 - math.cos(lo[3]):
        return 'PRUNE', None
    Vs = squares(mid, s)
    rho = [r[0] + r[1], r[0] + (1.0 + sec_tan(hi[1])) * r[1], r[2] + r[3], r[4] + r[5]]
    rt = [r[1], r[1], r[3], r[6]]
    mC = rho[3] + H2 * rt[3]                                           # C's vertices move by at most this
    if -Z.poly_gap(Vs[3], BOXP) + mC <= 0:                             # C never meets the open box
        return 'PRUNE', None
    C = Vs[3]
    Tu, Tv = C - [C[:, 0].min(), 0.0], C - [0.0, C[:, 1].min()]
    if Z.poly_gap(Vs[2], Tu) - (rho[2] + H2 * rt[2]) - 2 * mC >= 0:   # X never meets the wall drop
        return 'PRUNE', None
    if min(Z.poly_gap(Vs[0], Tv) - (rho[0] + H2 * rt[0]), Z.poly_gap(Vs[1], Tv) - (rho[1] + H2 * rt[1])) - 2 * mC >= 0:
        return 'PRUNE', None
    Cs = cores_of(Vs, rho, rt)
    if Cs is None:
        return 'FAIL', 9.0
    for i in range(4):
        for j in range(i):
            if (i, j) != (1, 0) and Z.poly_gap(Cs[i], Cs[j]) < -1e-9:
                return 'PRUNE', None
    return sectors_ok(Cs, bins)


def check_box_pair3(lo, hi, bins=K.BINS):
    lo, hi = np.array(lo, float), np.array(hi, float)
    mid, r = 0.5 * (lo + hi), 0.5 * (hi - lo)
    if lo[0] >= 1.0 or lo[2] >= 1.0:
        return 'PRUNE', None
    if hi[0] + K.w_of(hi[1]) < SMIN - 2.0:                              # the wall row's START offset a = s - b - span < 1
        return 'PRUNE', None
    Vs = squares_pair3(mid, SMAX)
    rho = [r[0] + (1.0 + sec_tan(hi[1])) * r[1], r[0] + r[1], r[2] + r[3]]
    rt = [r[1], r[1], r[3]]
    Cs = cores_of(Vs, rho, rt)
    if Cs is None:
        return 'FAIL', 9.0
    if Z.poly_gap(Cs[0], Cs[2]) < -1e-9 or Z.poly_gap(Cs[1], Cs[2]) < -1e-9:
        return 'PRUNE', None
    return sectors_ok(Cs, bins)


def p_of_ring(p, s):
    Vs = G.verts(np.array(p), s)
    return np.array([p[0], p[4], float(Vs[6][:, 1].min()), p[7], p[8], p[9], p[10] % (math.pi / 2)], float)


def bench(n):
    rows = [json.loads(l) for l in open(os.path.join(ATT, 'results', 'ring262.jsonl'))]
    rows = [r for r in rows if r['t'] > 1e-6][:n]
    W = np.array([1, 2, 1, 2, 1, 1, 2.0])
    out = []
    for r in rows:
        p = p_of_ring(r['p'], r['s'])
        t0, rad, st0 = time.time(), None, check_box(p, p)
        for k in range(3, 14):
            h = 2.0 ** (-k)
            if check_box(p - h / W, p + h / W)[0] == 'CERT':
                rad = h
                break
        out.append(dict(id=r['id'], point=st0[0], point_margin=st0[1], cert_radius=rad, sec=round(time.time() - t0, 1)))
        print(out[-1], flush=True)
    ok = [o['cert_radius'] for o in out if o['cert_radius']]
    summ = dict(n=len(out), point_cert=sum(o['point'] == 'CERT' for o in out), radii=sorted(set(ok)),
                median_radius=float(np.median(ok)) if ok else None)
    json.dump(dict(summary=summ, rows=out), open(os.path.join(ATT, 'results', 'bench262.json'), 'w'), indent=1)
    print(summ)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', default='bench')
    ap.add_argument('--n', type=int, default=40)
    a = ap.parse_args()
    Z.belownormal()
    bench(a.n)
