"""A266 box-valid certificate of STRIP_2 (strip_plug.md s.1.1), the two-square, s-free lemma on 5 parameters
    x = (h_u, h_v, theta_C, y_X, phi_X):
  C = unit square, lowest vertex (h_u + sin th, h_v), tilt th in [0, 45 deg]  (h_u = its wall distance, h_v its floor
      distance; domain h_u, h_v in [0, 1) AND C meets the OPEN unit box (0,1)^2 -- the floater of a JAM corner; for a
      tilted C this is strictly more than h_u, h_v < 1, and without it STRIP_2 is FALSE: probe266);
  T_u = C - h_u e_x (its wall drop);
  X = unit square, LEFTMOST vertex (0, y_X) on the wall, edges (cos phi, sin phi) and (sin phi, -cos phi), phi in
      [0, 90 deg) (the JAM ring has phi in (0, 45]; [45, 90) is the mirrored orientation);  domain: X in the quadrant
      and ABOVE C (its lowest point y_X - cos phi >= max(0, h_v); in the JAM ring y_X - cos phi > 1 > h_v),
      int X /\\ int C = 0, int X /\\ int T_u != 0.
STATEMENT on a box B: for every x in B /\\ domain, NO unit square Q (any tilt psi) in the quadrant with
    int Q /\\ int C = 0 = int Q /\\ int X has an interior point in T_u  (<=> in T_u \\ C).
Centre-set form, per tilt psi:  bad centres q satisfy  q in (T_u (+) Q)^o = (P - h_u e_x)^o,  q notin P^o,
    q notin (X (+) Q)^o,  q + Q in quadrant,   P := C (+) Q_psi.
SOUNDNESS (the bad set is OVER-approximated, A259's CORE / KERNEL lemmas [T]):
  * over B every square S in {C, X} satisfies  core(S) c S c outer(S):  core = mid pose, half-side 1/(2 w(r_t)) - rho
    - TOL,  outer = mid pose, half-side w(r_t)/2 + rho + TOL,  rho = the |.|_1 radius of the centre over B
    (C: r_hu + r_hv + r_th;  X: r_yX + r_phi;  both from |d centre / d tilt|_1 <= 1);
  * over a tilt bin [m - D, m + D] of Q:  K := kernel (tilt m, half 1/(2 w(D))) c Q_psi c Qo := (tilt m, half w(D)/2);
  * hence  P_in := core(C) (+) K  c  P^o,   P (+) [-hi_hu, -lo_hu] e_x  c  P_out := hull(outer(C) (+) Qo - {lo, hi} e_x),
    (X (+) Q)^o  ⊇  core(X) (+) K,   and  q + Q in quadrant  =>  q_x, q_y >= the half-extent of K;
  * LEFT SHADOW [T]: P convex, q notin P^o, q + h_u e_x in P^o  =>  q_x < l_P(q_y) <= l_{P_in}(q_y)  (l = the left
    boundary), i.e. q notin RC(P_in) := P_in (+) [0, 20] e_x (its right-closure) -- this drops the annulus artefact
    on P's right, top and bottom that a plain P_out \\ P_in keeps (170 CPU-h per root cell before, time266).
  * TEST(bin) := {q_x, q_y >= k} /\\ P_out  \\ RC(P_in)  \\ (core(X) (+) K)  ⊇ the bad centres of the bin;  CERT iff
    every bin's TEST has area <= ATOL;  PRUNE iff B misses the domain for EVERY x in B:  hi_yX - cos(hi_phi) <
    max(0, lo_hv), or core(X) and core(C) overlap, or outer(X) and outer(T_u) are disjoint (T_u's outer: mid (h_v, th),
    rho = r_hv + r_th), or outer(C) misses the closed unit box.
PRICE (time266, left-shadow test): a 1/1200 sub-cell of root cell 1,1,0 costs 535 s and 18 133 leaves with h_u, h_v
refined to 2^-7 over the WHOLE square (the 1-degree tilt bins of Q cost a fixed 0.017 in the over-approximation and
the statement's own margin is 0.005-0.02 in parameter radius on random in-domain points: probe266) -- a root cell is
~6e5 s and the 27 cells ~5e3 CPU-h, not A265's 1-3 CPU-h.  Hence --budget: boxes per cell, the unvisited subtrees
are written OPEN 'budget' (tiled, honest); the index records the certified VOLUME fraction per cell.
    python strip266.py --mode bench      python strip266.py --mode run --lane jam|mir [--only i,j,k;...] [--budget N]"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np
from shapely.geometry import Polygon, box as sbox

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A259-normal-room', 'code'))
import geom259 as Z                                                   # noqa: E402

DEG = math.pi / 180.0
TOL, ATOL = 1e-6, 1e-10
BINS = [(-45.0 + 1.0 * k + 0.5, 0.5) for k in range(90)]              # (mid, half-width) of Q's tilt, degrees
WEIGHT = np.array([1.0, 1.0, 2.0, 1.0, 2.0])                          # a tilt radian costs 2 position units
LANES = {'jam': (0.0, 45.0), 'mir': (45.0, 90.0)}                     # phi_X ranges (degrees)
YX = (0.7, 3.5)                                                       # X meets T_u only for y_X in this range


def w_of(a):
    return math.cos(a) + math.sin(a)


def sq(cx, cy, th, half):
    return Z.sq_verts(cx, cy, th, half)


def mink(A, B):
    """Minkowski sum of two convex vertex arrays (hull of the vertex sums), as a vertex array."""
    H = Polygon([(a[0] + b[0], a[1] + b[1]) for a in A for b in B]).convex_hull
    return np.array(H.exterior.coords)[:-1]


def centres(mid):
    """centres of C, X, T_u at the box middle."""
    hu, hv, th, yx, ph = mid
    c, s = math.cos(th), math.sin(th)
    cx, sx = math.cos(ph), math.sin(ph)
    return ((hu + (c + s) / 2, hv + (c + s) / 2), ((cx + sx) / 2, yx + (sx - cx) / 2), ((c + s) / 2, hv + (c + s) / 2))


def squares(lo, hi):
    """(core_C, core_X, outer_C, outer_X, outer_Tu) or None when a core degenerates (box too big)."""
    lo, hi = np.array(lo, float), np.array(hi, float)
    mid, r = 0.5 * (lo + hi), 0.5 * (hi - lo)
    cC, cX, cT = centres(mid)
    rho = {'C': r[0] + r[1] + r[2], 'X': r[3] + r[4], 'T': r[1] + r[2]}
    rt = {'C': r[2], 'X': r[4], 'T': r[2]}
    th = {'C': mid[2], 'X': mid[4], 'T': mid[2]}
    ctr = {'C': cC, 'X': cX, 'T': cT}
    out = {}
    for k in ('C', 'X', 'T'):
        a_in = 0.5 / w_of(rt[k]) - rho[k] - TOL
        a_out = 0.5 * w_of(rt[k]) + rho[k] + TOL
        if a_in <= 0.02:
            return None
        out[k] = (sq(*ctr[k], th[k], a_in), sq(*ctr[k], th[k], a_out))
    return out


UNIT = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]])
RIGHT = np.array([[0.0, 0.0], [20.0, 0.0]])


def outside_domain(lo, hi, S):
    if hi[3] - math.cos(hi[4]) < max(0.0, lo[1]):                      # X's lowest point below the floor or below C's for every x in B
        return True
    if Z.poly_gap(S['C'][1], UNIT) >= 0.0:                              # outer(C) misses the closed unit box: C never meets (0,1)^2
        return True
    if Z.poly_gap(S['X'][0], S['C'][0]) < -1e-9:                        # cores of X and C overlap: X, C never disjoint
        return True
    if Z.poly_gap(S['X'][1], S['T'][1]) > 1e-9:                         # outers of X and T_u disjoint: X never meets T_u
        return True
    return False


def check_box(lo, hi, bins=BINS):
    """('PRUNE'|'CERT'|'FAIL', worst) -- worst = the largest TEST area over the bins (CERT: <= ATOL)."""
    lo, hi = np.array(lo, float), np.array(hi, float)
    S = squares(lo, hi)
    if S is None:
        return 'FAIL', 9.0
    if outside_domain(lo, hi, S):
        return 'PRUNE', None
    worst = 0.0
    shift = np.array([[-hi[0], 0.0], [-lo[0], 0.0]])
    for md, hw in bins:
        m, D = md * DEG, hw * DEG
        K = sq(0.0, 0.0, m, 0.5 / w_of(D))
        Qo = sq(0.0, 0.0, m, 0.5 * w_of(D))
        k = 0.5 / w_of(D) * (abs(math.cos(m)) + abs(math.sin(m)))
        P_out = mink(mink(S['C'][1], Qo), shift)
        RC = mink(mink(S['C'][0], K), RIGHT)                          # the right-closure of P_in: {q_x >= l_{P_in}(q_y)}
        XK = mink(S['X'][0], K)
        T = sbox(k, k, 9.0, 9.0).intersection(Polygon(P_out)).difference(Polygon(RC)).difference(Polygon(XK))
        worst = max(worst, T.area)
        if worst > ATOL:
            return 'FAIL', worst
    return 'CERT', worst


BUDGET = [10 ** 12]                                                   # boxes left for the cell


def tree(lo, hi, depth, maxdepth, out, stats):
    if BUDGET[0] <= 0:                                                 # budget exhausted: the subtree is OPEN (honest, tiled)
        stats['BUDGET'] = stats.get('BUDGET', 0) + 1
        out.append({'lo': list(map(float, lo)), 'hi': list(map(float, hi)), 'st': 'OPEN', 'm': 'budget'})
        return False
    st, m = check_box(lo, hi)
    stats[st] = stats.get(st, 0) + 1
    BUDGET[0] -= 1
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
        ok = tree(l2, h2, depth + 1, maxdepth, out, stats) and ok
    return ok


def root(lane, i, j, kk, n=3):
    """root cell (i: theta_C third, j: y_X third, kk: phi_X third of the lane): [0,1] x [0,1] x 15deg x 0.93 x 15deg."""
    p0, p1 = LANES[lane]
    dt, dy, dp = 45.0 / n, (YX[1] - YX[0]) / n, (p1 - p0) / n
    lo = [0.0, 0.0, i * dt * DEG, YX[0] + j * dy, (p0 + kk * dp) * DEG]
    hi = [1.0, 1.0, (i + 1) * dt * DEG, YX[0] + (j + 1) * dy, (p0 + (kk + 1) * dp) * DEG]
    return lo, hi


def bench(n, seed, rp, rt):
    rng = np.random.default_rng(seed)
    t0, res, k = time.time(), {}, 0
    while k < n:
        x = [rng.uniform(0.01, 0.99), rng.uniform(0.0, 0.99), rng.uniform(0, 45) * DEG, rng.uniform(*YX),
             rng.uniform(0, 45) * DEG]
        lo = [x[0] - rp, x[1] - rp, x[2] - rt, x[3] - rp, x[4] - rt]
        hi = [x[0] + rp, x[1] + rp, x[2] + rt, x[3] + rp, x[4] + rt]
        st, m = check_box(lo, hi)
        res[st] = res.get(st, 0) + 1
        k += 1
    return res, (time.time() - t0) / n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', default='bench')
    ap.add_argument('--n', type=int, default=100)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--lane', default='jam')
    ap.add_argument('--maxdepth', type=int, default=30)
    ap.add_argument('--only', default='')                             # "i,j,k" or "i,j,k;i,j,k;..." (subset of the 27 cells)
    ap.add_argument('--budget', type=int, default=0)                  # boxes per cell (0 = unlimited); the rest is OPEN 'budget'
    a = ap.parse_args()
    only = set(a.only.split(';')) if a.only else set()
    Z.belownormal()
    certs = os.path.join(HERE, '..', 'certs')
    os.makedirs(certs, exist_ok=True)
    if a.mode == 'bench':
        for rp, rt in ((0.05, 0.05), (0.02, 0.02), (0.01, 0.01), (0.005, 0.005)):
            res, dt = bench(a.n, a.seed, rp, rt)
            print(json.dumps({'r_pos': rp, 'r_tilt': rt, 'res': res, 'sec_per_box': round(dt, 3)}), flush=True)
        return
    stop = os.path.join(HERE, '..', 'logs', 'STOP')
    idx = os.path.join(certs, 'strip266_%s_index.jsonl' % a.lane)
    done = {json.loads(l)['cell'] for l in open(idx)} if os.path.exists(idx) else set()
    for i in range(3):
        for j in range(3):
            for kk in range(3):
                cell = '%d,%d,%d' % (i, j, kk)
                if cell in done or (only and cell not in only):
                    continue
                if os.path.exists(stop):
                    return
                lo, hi = root(a.lane, i, j, kk)
                t0, out, stats = time.time(), [], {}
                BUDGET[0] = a.budget if a.budget > 0 else 10 ** 12
                ok = tree(lo, hi, 0, a.maxdepth, out, stats)
                vol = {}
                for r in out:
                    v = float(np.prod((np.array(r['hi']) - np.array(r['lo'])) / (np.array(hi) - np.array(lo))))
                    vol[r['st']] = vol.get(r['st'], 0.0) + v
                with open(os.path.join(certs, 'strip266_%s_cell_%d_%d_%d.jsonl' % (a.lane, i, j, kk)), 'w') as fh:
                    for row in out:
                        fh.write(json.dumps(row) + '\n')
                with open(idx, 'a') as fh:
                    fh.write(json.dumps({'cell': cell, 'ok': ok, 'stats': stats, 'leaves': len(out),
                                         'sec': round(time.time() - t0, 1), 'lane': a.lane}) + '\n')
                print(a.lane, cell, ok, stats, len(out), round(time.time() - t0, 1), flush=True)


if __name__ == '__main__':
    main()
