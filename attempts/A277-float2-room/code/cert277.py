"""A277 box-valid kernel for CAP-2 at the BL corner by the DIAMETER test (A259's method; cert259 / room259 imported,
never edited).  Corner frame BL, side SMAX (monotone in s: A259 s.2.3).  Obstacles by kind, one parameter block each:
    F (floater)       (h_u, h_v, theta)   centre (h_u + w/2, h_v + w/2), w = cos + sin   [local261's pose]
    H (floor toucher) (a, alpha)          lowest vertex (a + sin alpha, 0)
    V (wall toucher)  (b, phi)            leftmost vertex (0, b + ... ) i.e. lowest point at height b
Families: 'float2' = F F (6 params: C, D both meet the open box);  'jam' = H F (5 params: A meets the box, C floats
and meets it);  'pair' = V F-drop... not here.  Over a box, each obstacle is replaced by its CORE (box-centre pose,
half-side 1/(2 w(r_tilt)) - rho, rho = |.|_1 bound on the centre motion), the free square's tilt is binned (A237
kernel), and the BL-sector centre region R_over = U_bins [(C_bin ∩ left ∩ HP(-v)) u (C_bin ∩ lower ∩ HP(-u))] with the
bin slack folded into the half-plane; CERT iff R_over is empty (ROOM) or diam(R_over) < 1 (CAP-2).  PRUNE iff some
obstacle certainly misses the open box, or two cores overlap.
    python cert277.py --mode bench --fam float2 [--n 12]   -> results/bench277_<fam>.json"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np
from shapely.geometry import Polygon, box as sbox
from shapely.ops import unary_union

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
for p in ('attempts/A259-normal-room/code', 'attempts/A262-no-jam/code'):
    sys.path.insert(0, os.path.join(ROOT, p))
import room259 as R                                                    # noqa: E402
import cert259 as K                                                    # noqa: E402
import geom259 as Z                                                    # noqa: E402

SMAX, TOL = K.SMAX, K.TOL
BOXP = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], float)
H2 = math.sqrt(0.5)
FAM = {'float2': 'FF', 'jam': 'HF'}
W = lambda t: abs(math.cos(t)) + abs(math.sin(t))


def split(fam, p):
    out, k = [], 0
    for kind in FAM[fam]:
        n = 3 if kind == 'F' else 2
        out.append((kind, list(p[k:k + n])))
        k += n
    return out


def verts_of(kind, q):
    if kind == 'F':
        w = W(q[2])
        return Z.sq_verts(q[0] + w / 2, q[1] + w / 2, q[2])
    w = W(q[1])
    return Z.sq_verts(q[0] + w / 2, w / 2, q[1]) if kind == 'H' else Z.sq_verts(w / 2, q[0] + w / 2, q[1])


def cores(fam, lo, hi):
    """(cores, outer-approximation slack per obstacle) or None if a core vanishes."""
    mid, r = 0.5 * (lo + hi), 0.5 * (hi - lo)
    Cs, slack = [], []
    for (kind, q), (_, rq) in zip(split(fam, mid), split(fam, r)):
        V = verts_of(kind, q)
        rt = rq[-1]
        rho = sum(rq[:-1]) + rt                                          # |.|_1 bound on the centre (w'/2 <= 1)
        a = 0.5 / K.w_of(rt) - rho
        if a <= 0.02:
            return None
        Cs.append(K.shrink(V, a))
        slack.append(rho + H2 * rt)
    return Cs, slack


def region(Cs, bins, s=SMAX):
    O = np.array([s / 2, s / 2])
    left, lower = sbox(-1, -1, s / 2, s + 1), sbox(-1, -1, s + 1, s / 2)
    big = 3 * s
    parts = []
    for md, hw in bins:
        psi, D = md * Z.DEG, hw * Z.DEG
        C = R.centre_set(list(Cs), s, psi, 0.5 / K.w_of(D))
        if C.is_empty:
            continue
        u = np.array([math.cos(psi), math.sin(psi)])
        v = np.array([-math.sin(psi), math.cos(psi)])
        for Gm, n in ((C.intersection(left), -v), (C.intersection(lower), -u)):
            if Gm.is_empty:
                continue
            # (q-O).n + D|q-O| >= 1/2 is implied by (q-O).n >= 1/2 - D * diam; over-approximate by that half-plane
            slack = D * s / math.sqrt(2.0)                                    # |q - O| <= s/sqrt2 in the container
            p0 = O + (0.5 - slack) * n
            t = np.array([-n[1], n[0]])
            hp = Polygon([p0 + big * t, p0 + big * t + big * n, p0 - big * t + big * n, p0 - big * t])
            parts += R.polys_of(Gm.intersection(hp))
    if not parts:
        return None, 0.0
    U = unary_union(parts)
    Hh = U.convex_hull
    pts = np.array(Hh.exterior.coords)[:-1] if Hh.geom_type == 'Polygon' else np.array(Hh.coords)
    d = np.linalg.norm(pts[:, None, :] - pts[None, :, :], axis=2)
    return U, float(d.max())


def check_box(fam, lo, hi, bins=K.BINS):
    lo, hi = np.array(lo, float), np.array(hi, float)
    cs = cores(fam, lo, hi)
    if cs is None:
        return 'FAIL', 9.0
    Cs, slack = cs
    mid = 0.5 * (lo + hi)
    for (kind, q), sl in zip(split(fam, mid), slack):                   # PRUNE: an obstacle certainly misses the open box
        if -Z.poly_gap(verts_of(kind, q), BOXP) + sl <= 0:
            return 'PRUNE', None
    for i in range(len(Cs)):
        for j in range(i):
            if Z.poly_gap(Cs[i], Cs[j]) < -1e-9:
                return 'PRUNE', None
    U, diam = region(Cs, bins)
    if U is None:
        return 'CERT-ROOM', 0.0
    return ('CERT-CAP2', diam) if diam < 1.0 - TOL else ('FAIL', diam)


def bench(fam, n, seed=277):
    rng = np.random.default_rng(seed)
    d = len(FAM[fam]) * 3 - FAM[fam].count('H') - FAM[fam].count('V')
    wts = np.array([1.0 if k < 2 else 2.0 for kind in FAM[fam] for k in range(3 if kind == 'F' else 2)][:d])
    pts = []
    if fam == 'float2':
        w = json.load(open(os.path.join(HERE, '..', 'results', 'float277_witness.json')))
        pts.append([w['h']['C'][0], w['h']['C'][1], math.radians(w['poses']['C'][2]), w['h']['D'][0], w['h']['D'][1], math.radians(w['poses']['D'][2])])
    while len(pts) < n:
        if fam == 'float2':                                             # six INDEPENDENT draws
            p = np.array([rng.uniform(0, 1), rng.uniform(0, 1), rng.uniform(0, math.pi / 2),
                          rng.uniform(0, 1), rng.uniform(0, 1), rng.uniform(0, math.pi / 2)])
        else:
            p = np.array([rng.uniform(0, 1), rng.uniform(0, math.pi / 2), rng.uniform(0, 1), rng.uniform(0, 1), rng.uniform(0, math.pi / 2)])
        Vs = [verts_of(kind, q) for kind, q in split(fam, p)]
        if any(-Z.poly_gap(V, BOXP) <= 1e-3 for V in Vs) or Z.poly_gap(Vs[0], Vs[1]) < 1e-3:
            continue
        pts.append(list(map(float, p)))
    rows = []
    for p in pts:
        p = np.array(p)
        t0 = time.time()
        st0 = check_box(fam, p, p)
        rad, stR = None, None
        for k in range(3, 12):
            h = 2.0 ** (-k)
            st = check_box(fam, p - h / wts[:d], p + h / wts[:d])
            if st[0].startswith('CERT'):
                rad, stR = h, st
                break
        rows.append(dict(point=list(map(float, p)), point_status=st0[0], point_diam=st0[1], cert_radius=rad,
                         cert_status=stR[0] if stR else None, sec=round(time.time() - t0, 2)))
        print(rows[-1], flush=True)
    ok = [r['cert_radius'] for r in rows if r['cert_radius']]
    summ = dict(fam=fam, n=len(rows), point_cert=sum(r['point_status'].startswith('CERT') for r in rows),
                point_room=sum(r['point_status'] == 'CERT-ROOM' for r in rows), radii=sorted(set(ok)),
                median_radius=float(np.median(ok)) if ok else None, sec_per_point=float(np.mean([r['sec'] for r in rows])))
    json.dump(dict(summary=summ, rows=rows), open(os.path.join(HERE, '..', 'results', 'bench277_%s.json' % fam), 'w'), indent=1)
    print(summ)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', default='bench')
    ap.add_argument('--fam', default='float2')
    ap.add_argument('--n', type=int, default=12)
    a = ap.parse_args()
    Z.belownormal()
    bench(a.fam, a.n)
