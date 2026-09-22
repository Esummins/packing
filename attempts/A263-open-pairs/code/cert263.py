"""A263 box-valid certificates of the FACTORS of the hybrid corner PAIR with INDEPENDENT tilts (open_pairs.md s.2-3),
by A259's method (cert259 / room259 imported, never edited).  Corner BR, side SMAX (corner-frame monotone in s [T]),
domain bounds with s >= SMIN.  Families (4 parameters each):
  P2 : p = (b, fW, a', f1')   squares W (floor END), S' (right-wall START) [+ PLUG when a' > 0.604]
       (i) with P in RIGHT(floor):  (P - A_W).uW >= 0;   (ii) with P' in LEFT(right wall):  (P' - T1').u1' <= 0
  WE : p = (b, fW, e, f1)     squares s1, W on the floor;  (i) with (P - A_W).uW <= 0;      all-ADJ reaches (--adj 1)
  WS : p = (a', f1', e', fW') squares S', W' on the right wall;  (ii) with (P' - T1').u1' >= 0;  all-ADJ reaches
PRINCIPAL-NORMAL clips (geo263): (i) psi >= 0: (q-O).(-v-u) >= 0;  (ii) psi <= 0: (q-O).(u+v) >= 0.
Soundness (every admissible centre is kept): CORE of each square over the box (A259: centre-pose at the box centre,
half-side 1/(2 w(r_phi)) - rho, rho = |.|_1 mean-value bound of the centre); KERNEL per tilt bin; every region / normal
clip is RELAXED by its variation over the box and the bin: slack = 0.7072 D + rho_point + DIAM r_tilt (region),
1.4143 D DIAM (normal), DIAM = 5.5 >= the container's diagonal;  linear forms bounded by value_mid + D |q - O|.
PRUNE only off-domain or on core overlap (then the squares overlap at EVERY parameter of the box).
    python cert263.py --mode bench --fam WE --n 40     python cert263.py --mode run --fam P2 [--only i,j]"""
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
import geo263 as G                                                    # noqa: E402
import cert259 as K                                                   # noqa: E402  (SMAX, SMIN, TOL, BINS, shrink, w_of)
H, Z, R, DEG = G.H, G.Z, G.R, G.DEG
SMAX, SMIN, TOL = K.SMAX, K.SMIN, K.TOL
RHO_PLUG, PLUG_A, EMAX, DIAM = 0.25, 0.604, 0.5, 5.5
WEIGHT = {'P2': np.array([1.0, 2.0, 1.0, 2.0]), 'WE': np.array([1.0, 2.0, 1.0, 2.0]), 'WS': np.array([1.0, 2.0, 1.0, 2.0])}
sec = G.sec


def st(f):
    return math.tan(f) / math.cos(f)


def squares(fam, p, s):
    if fam == 'P2':
        return [G.floor_sq((p[0], p[1], 0.0, p[1]), s)[1], G.right_sq((p[2], p[3], 0.0, p[3]), s)[0]]
    return G.floor_sq(tuple(p), s) if fam == 'WE' else G.right_sq(tuple(p), s)


def cores(fam, lo, hi):
    mid, r = 0.5 * (lo + hi), 0.5 * (hi - lo)
    Vs = squares(fam, mid, SMAX)
    if fam == 'P2':
        rho, rf = [r[0] + r[1], r[2] + r[3]], [r[1], r[3]]
    elif fam == 'WE':                                                 # s1 moves with b, w(fW), e, sec f1
        rho, rf = [r[0] + r[1] + r[2] + (1.0 + st(hi[3])) * r[3], r[0] + r[1]], [r[3], r[1]]
    else:                                                             # W' moves with a', sec f1', e'
        rho, rf = [r[0] + r[1], r[0] + st(hi[1]) * r[1] + r[2] + r[3]], [r[1], r[3]]
    out = []
    for V, ro, f in zip(Vs, rho, rf):
        a = 0.5 / K.w_of(f) - ro
        if a <= 0.02:
            return None
        out.append(K.shrink(V, a))
    return out


def outside_domain(fam, lo, hi, adj):
    if fam == 'P2':                                                   # b, a' < 1;  (adj) W and S' reach their far slots
        if lo[0] >= 1.0 or lo[2] >= 1.0:
            return True
        return adj and (hi[0] + K.w_of(hi[1]) < SMIN - 2.0 or hi[2] + K.w_of(hi[3]) < SMIN - 2.0)
    if fam == 'WE':                                                   # (b, fW, e, f1);  a = s - b - w(fW) - e - sec f1
        if lo[0] >= 1.0 or hi[0] + K.w_of(hi[1]) + hi[2] + sec(hi[3]) <= SMIN - 1.0:       # b < 1, a < 1
            return True
        if lo[0] + K.w_of(lo[1]) + lo[2] + sec(lo[3]) >= SMAX:                             # a > 0
            return True
        if adj and (hi[0] + K.w_of(hi[1]) < SMIN - 2.0 or                                  # W reaches: delta_W <= 2
                    lo[0] + K.w_of(lo[1]) + lo[2] + sec(lo[3]) - K.w_of(hi[3]) > 2.0):     # s1 reaches
            return True
        return False
    if lo[0] >= 1.0 or lo[0] + sec(lo[1]) + lo[2] + K.w_of(lo[3]) >= SMAX:                 # a' < 1, b' > 0
        return True
    if hi[0] + sec(hi[1]) + hi[2] + K.w_of(hi[3]) <= SMIN - 1.0:                           # b' < 1
        return True
    if adj and (lo[0] + sec(lo[1]) + lo[2] > 2.0 or hi[0] + K.w_of(hi[1]) < SMIN - 2.0):   # W', S' reach
        return True
    return False


def check_box(fam, lo, hi, bins=K.BINS, adj=True):
    lo, hi = np.array(lo, float), np.array(hi, float)
    if outside_domain(fam, lo, hi, adj):
        return 'PRUNE', None
    Cs = cores(fam, lo, hi)
    if Cs is None:
        return 'FAIL', 9.0
    if Z.poly_gap(Cs[0], Cs[1]) < -1e-9:
        return 'PRUNE', None
    s, mid, r = SMAX, 0.5 * (lo + hi), 0.5 * (hi - lo)
    if fam == 'P2' and lo[2] > PLUG_A:
        Cs = Cs + [np.array([(s - RHO_PLUG, 0.0), (s, 0.0), (s, RHO_PLUG), (s - RHO_PLUG, RHO_PLUG)])]
    O = np.array([s / 2, s / 2])
    right, lower = sbox(s / 2, -1, s + 1, s + 1), sbox(-1, -1, s + 1, s / 2)
    fr = G.frames(s, (mid[0], mid[1], 0, 0) if fam != 'WS' else None,
                  (mid[2], mid[3], 0, 0) if fam == 'P2' else ((mid[0], mid[1], 0, 0) if fam == 'WS' else None))
    ptA = r[0] + 2.0 * r[1] + DIAM * r[1]                              # A_W (floor):  moves <= r_b + 2 r_fW; uW turns r_fW
    ptT = (r[2] + 2.0 * r[3] + DIAM * r[3]) if fam == 'P2' else (r[0] + 2.0 * r[1] + DIAM * r[1])
    worst = -9.0
    for md, hw in bins:
        psi, D = md * DEG, hw * DEG
        C = R.centre_set(Cs, s, psi, 0.5 / K.w_of(D))
        if C.is_empty:
            continue
        u = np.array([math.cos(psi), math.sin(psi)])
        v = np.array([-math.sin(psi), math.cos(psi)])
        cases = []
        if fam in ('P2', 'WE'):
            sl = 0.7072 * D + ptA
            sign = 1.0 if fam == 'P2' else -1.0
            Gm = C.intersection(right).intersection(
                G.halfplane(fr['AW'] - G.near_offset(psi, 0) - sign * sl * fr['uW'], sign * fr['uW']))
            if md - hw >= 0:
                Gm = Gm.intersection(G.halfplane(O + 1.4143 * D * DIAM * (u + v) / math.sqrt(2), -v - u))
            cases.append((Gm, -v))
        if fam in ('P2', 'WS'):
            sl = 0.7072 * D + ptT
            sign = -1.0 if fam == 'P2' else 1.0
            Gm = C.intersection(lower).intersection(
                G.halfplane(fr['T1'] - G.near_offset(psi, 1) - sign * sl * fr['u1'], sign * fr['u1']))
            if md + hw <= 0:
                Gm = Gm.intersection(G.halfplane(O - 1.4143 * D * DIAM * (u + v) / math.sqrt(2), u + v))
            cases.append((Gm, u))
        for Gm, n in cases:
            for Pg in R.polys_of(Gm):
                A = np.array(Pg.exterior.coords)[:-1] - O
                worst = max(worst, float((A @ n + D * np.linalg.norm(A, axis=1)).max()) - 0.5)
        if worst > -TOL:
            return 'FAIL', worst
    return 'CERT', worst


def tree(fam, lo, hi, depth, maxdepth, out, stats, adj):
    stt, m = check_box(fam, lo, hi, adj=adj)
    stats[stt] = stats.get(stt, 0) + 1
    if stt != 'FAIL':
        out.append({'lo': list(map(float, lo)), 'hi': list(map(float, hi)), 'st': stt, 'm': m})
        return True
    if depth >= maxdepth:
        out.append({'lo': list(map(float, lo)), 'hi': list(map(float, hi)), 'st': 'OPEN', 'm': m})
        return False
    k = int(((np.array(hi) - np.array(lo)) * WEIGHT[fam]).argmax())
    mid = 0.5 * (lo[k] + hi[k])
    ok = True
    for a, b in ((lo[k], mid), (mid, hi[k])):
        l2, h2 = list(lo), list(hi)
        l2[k], h2[k] = a, b
        ok = tree(fam, l2, h2, depth + 1, maxdepth, out, stats, adj) and ok
    return ok


def root(fam, i, j, step, emax=None):
    """tilt cell (i, j) of the family's two tilt coordinates (indices 1 and 3)."""
    top = 1.0 if fam == 'P2' else (EMAX if emax is None else emax)
    return [0.0, i * step * DEG, 0.0, j * step * DEG], [1.0, (i + 1) * step * DEG, top, (j + 1) * step * DEG]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', default='bench')
    ap.add_argument('--fam', default='WE')
    ap.add_argument('--adj', type=int, default=1)
    ap.add_argument('--n', type=int, default=40)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--cells', type=int, default=9)
    ap.add_argument('--maxdepth', type=int, default=30)
    ap.add_argument('--only', default='')
    ap.add_argument('--emax', type=float, default=None, help='shift range (default 0.5 all-ADJ; the non-ADJ runs use 1.2)')
    a = ap.parse_args()
    Z.belownormal()
    tag = a.fam if a.adj else a.fam + 'n'
    if not a.adj and a.emax is None:
        a.emax = 1.2
    certs = os.path.join(HERE, '..', 'certs')
    if a.mode == 'bench':
        import bench263
        bench263.run(a, check_box)
        return
    stop = os.path.join(HERE, '..', 'logs', 'STOP')
    idx = os.path.join(certs, '%s263_index.jsonl' % tag)
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
            lo, hi = root(a.fam, i, j, step, a.emax)
            ok = tree(a.fam, lo, hi, 0, a.maxdepth, out, stats, bool(a.adj))
            with open(os.path.join(certs, '%s263_cell_%d_%d.jsonl' % (tag, i, j)), 'w') as fh:
                for row in out:
                    fh.write(json.dumps(row) + '\n')
            with open(idx, 'a') as fh:
                fh.write(json.dumps({'cell': cell, 'ok': ok, 'stats': stats, 'leaves': len(out),
                                     'sec': round(time.time() - t0, 1)}) + '\n')
            print(tag, cell, ok, stats, round(time.time() - t0, 1), flush=True)


if __name__ == '__main__':
    main()
