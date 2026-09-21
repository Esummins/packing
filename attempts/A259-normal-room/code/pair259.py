"""A259 CORNER-PAIR lemma (the per-corner decoupling of PIERCE-by-O; docs/proofs/normal_room.md s.2).

Corner BR of the container [0,s]^2.  Obstacles: the FLOOR row (end gap e0 = s - delta0 - span(phi0), tilt phi0) and the
RIGHT-WALL row (offset delta1, tilt phi1) -- four squares -- plus the container.  Statement PAIR(e0, phi0, delta1, phi1; s):
    no unit square Q (centre q, tilt psi in [-45, 45) deg, u = (cos psi, sin psi), v = (-sin psi, cos psi)), free of the
    four squares and inside the container, has
        (i)  (q - O).(-v) >= 1/2  and  q_x >= s/2        (misses O on the floor side, right half),   or
        (ii) (q - O).( u) >= 1/2  and  q_y <= s/2        (misses O on the right-wall side, lower half).
pair_margin = max over psi of  max{ (q-O).n - 1/2 : q in C(psi), half-plane clip }  (< 0: PAIR holds at the sampled
tilts, with that margin).  A free square missing O has (q-O).n >= 1/2 for one of n = +-u, +-v and q in one of two
halves, so PAIR at the four corners (C4 images) => every free square contains O   [T, reduction].
"""
import math
import os
import sys

import numpy as np
from shapely.geometry import box as sbox

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom259 as Z                                                   # noqa: E402
import room259 as R                                                   # noqa: E402

DEG = math.pi / 180.0


def pair_verts(e0, phi0, d1, phi1, s):
    d0 = s - e0 - Z.span(phi0)
    return Z.row_verts(d0, phi0, s, 0) + Z.row_verts(d1, phi1, s, 1)


def pair_feas(e0, phi0, d1, phi1, s):
    Vs = pair_verts(e0, phi0, d1, phi1, s)
    m = min(Z.contain_margin(V, s) for V in Vs)
    for i in (0, 1):
        for j in (2, 3):
            m = min(m, Z.poly_gap(Vs[i], Vs[j]))
    return m


def lin_max(G, n, O):
    best, arg = -9.0, None
    for P in R.polys_of(G):
        A = np.array(P.exterior.coords)[:-1]
        g = (A - O) @ n
        i = int(g.argmax())
        if g[i] > best:
            best, arg = float(g[i]), (float(A[i, 0]), float(A[i, 1]))
    return best, arg


def pair_margin(e0, phi0, d1, phi1, s, step_deg=1.0, Vs=None, half=0.5, psis=None):
    Vs = pair_verts(e0, phi0, d1, phi1, s) if Vs is None else Vs
    O = np.array([s / 2, s / 2])
    right = sbox(s / 2, -1, s + 1, s + 1)
    lower = sbox(-1, -1, s + 1, s / 2)
    worst, pose = -9.0, None
    if psis is None:
        psis = np.arange(-45.0, 45.0 - 1e-9, step_deg)
    for pd in psis:
        psi = pd * DEG
        C = R.centre_set(Vs, s, psi, half)
        if C.is_empty:
            continue
        u = np.array([math.cos(psi), math.sin(psi)])
        v = np.array([-math.sin(psi), math.cos(psi)])
        for G, n, tag in ((C.intersection(right), -v, 'i'), (C.intersection(lower), u, 'ii')):
            g, q = lin_max(G, n, O)
            if q is not None and g - 0.5 > worst:
                worst, pose = g - 0.5, (q[0], q[1], psi, tag)
    return worst, pose


if __name__ == '__main__':
    import json
    rows = [json.loads(l) for l in open(os.path.join(HERE, '..', 'results', 'sample259.jsonl'))]
    for r in rows[:10]:
        x, s = np.array(r['x']), r['s']
        out = []
        for k in range(4):                                            # corner between wall k and wall k+1
            k1 = (k + 1) % 4
            e0 = s - x[k] - Z.span(x[4 + k])
            out.append(pair_margin(e0, x[4 + k], x[k1], x[4 + k1], s, 2.0)[0])
        print(r['key'], 'pierceO %+.4f' % r['pierceO'], 'pair max %+.4f' % max(out), [round(v, 4) for v in out])
