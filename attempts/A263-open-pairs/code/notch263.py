"""A263 (a) WEDGE-NOTCH: the open notch between s1 (tilt f1) and W (tilt fW != f1) in closed form  (open_pairs.md s.1).
Notch frame: origin A_W = W's left vertex, x along the wall, y = depth - cos fW.  gam = horizontal gap from A_W to s1's
right-edge line;  T1 = s1's top vertex = (-gam - t sin f1, t cos f1),  t = (cos f1 + sin f1 - cos fW) / cos f1.
    W  = cone {x.uW >= 0, x.vW <= 0},   s1 = cone {(x-T1).u1 <= 0, (x-T1).v1 <= 0}   (valid while Q stays above depth sin f1)
A free square Q = P + [0,1]u + [0,1]v of tilt psi in [0, 45 deg] is disjoint from a cone iff ONE of its SAT options holds:
    R: Ra P.vW >= max(0, sin(fW-psi))      Rb (psi >= fW) P.v >= 0
    L: La (P-T1).u1 >= max(0, sin(psi-f1)) Lb (psi >= f1) (P-T1).u >= 0   Lc (P-T1).v1 >= max(0, sin(f1-psi))
       Ld (psi <= f1) (P-T1).v >= 0
NOTCH region: P.uW <= 0 and (P-T1).u1 >= 0.   value(obj) = min over the option pairs of a 2-variable LP (<= 12 explicit
vertex values) -- `closed`.  obj = (0,1): the least DEPTH - cos fW (OPEN-TOOTH);  obj = v: the MISS functional (P-A_W).v.
Principal values (psi <= fW):  miss  Na = sin(fW-psi) [cos(psi-f1) + k1 - gam cos f1] / cos(fW-f1),  k1 = max(0, sin(psi-f1))
                               depth Da = [cos f1 sin(fW-psi) + sin fW (k1 - gam cos f1)] / cos(fW-f1)
             (psi >= fW):      miss >= 0 (the APEX bound, s1-free);  depth = sin psi (k1 - gam cos f1) / cos(psi-f1)  (FAR)
    python notch263.py     -> results/notch263.json: closed vs EXACT centre sets (shapely, real squares) on a grid."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geo263 as G                                                    # noqa: E402
H, R, DEG = G.H, G.R, G.DEG
BOX = 3.0


def lp2(cons, obj):
    """min obj.P over {n.P >= k for (n, k) in cons} by vertex enumeration (the box |x|,|y| <= BOX is in cons)."""
    best = None
    for i in range(len(cons)):
        for j in range(i):
            A = np.array([cons[i][0], cons[j][0]], float)
            if abs(np.linalg.det(A)) < 1e-12:
                continue
            P = np.linalg.solve(A, np.array([cons[i][1], cons[j][1]], float))
            if all(np.dot(n, P) >= k - 1e-10 for n, k in cons):
                val = float(np.dot(obj, P))
                if best is None or val < best[0]:
                    best = (val, P)
    return best


def setup(gam, f1, fW):
    c1, g1, cW, gW = math.cos(f1), math.sin(f1), math.cos(fW), math.sin(fW)
    t = (c1 + g1 - cW) / c1
    return dict(T1=np.array([-gam - t * g1, t * c1]), u1=np.array([c1, g1]), v1=np.array([-g1, c1]),
                uW=np.array([cW, gW]), vW=np.array([-gW, cW]))


def closed(gam, f1, fW, psi, kind='miss'):
    """the closed form: least obj.P over the NOTCH region, psi in [0, 45 deg]; returns (value, P)."""
    F = setup(gam, f1, fW)
    u = np.array([math.cos(psi), math.sin(psi)])
    v = np.array([-math.sin(psi), math.cos(psi)])
    obj = v if kind == 'miss' else np.array([0.0, 1.0])
    T1 = F['T1']
    Rs = [(F['vW'], max(0.0, math.sin(fW - psi)))]
    if psi >= fW:
        Rs.append((v, 0.0))
    Ls = [(F['u1'], float(F['u1'] @ T1) + max(0.0, math.sin(psi - f1))),
          (F['v1'], float(F['v1'] @ T1) + max(0.0, math.sin(f1 - psi)))]
    if psi >= f1:
        Ls.append((u, float(u @ T1)))
    else:
        Ls.append((v, float(v @ T1)))
    region = [(-F['uW'], 0.0), (F['u1'], float(F['u1'] @ T1)),
              (np.array([1.0, 0]), -BOX), (np.array([-1.0, 0]), -BOX), (np.array([0, 1.0]), -BOX), (np.array([0, -1.0]), -BOX)]
    best = None
    for r in Rs:
        for l in Ls:
            got = lp2([r, l] + region, obj)
            if got is not None and (best is None or got[0] < best[0]):
                best = got
    return best


def principal(gam, f1, fW, psi):
    """the principal closed-form LOWER BOUNDS of open_pairs.md s.1 (miss, depth)."""
    k1 = max(0.0, math.sin(psi - f1))
    if psi <= fW:
        na = math.sin(fW - psi) * (math.cos(psi - f1) + k1 - gam * math.cos(f1)) / math.cos(fW - f1)
        nb = math.tan(fW - psi) * (1.0 + float(np.array([math.cos(psi), math.sin(psi)]) @ setup(gam, f1, fW)['T1']))
        return min(na, nb) if psi >= f1 else na
    return 0.0


def exact(gam, f1, fW, psi, kind='miss', s=8.0, dW=4.0):
    """the same minimum from the EXACT centre set of the two real squares on the floor of a big container."""
    e = gam - (math.cos(fW) - math.cos(f1)) * math.tan(f1)
    Vs = [H.toucher(dW - e - 1.0 / math.cos(f1), f1, s, 0), H.toucher(dW, fW, s, 0)]
    if G.Z.poly_gap(Vs[0], Vs[1]) < -1e-12:
        return None
    F = setup(gam, f1, fW)
    AW = np.array([dW, math.cos(fW)])
    off = G.near_offset(psi, 0)
    C = R.centre_set(Vs, s, psi)
    C = C.intersection(G.halfplane(AW - off, -F['uW'])).intersection(G.halfplane(AW + F['T1'] - off, F['u1']))
    v = np.array([-math.sin(psi), math.cos(psi)])
    obj = v if kind == 'miss' else np.array([0.0, 1.0])
    best = None
    for Pg in R.polys_of(C):
        A = np.array(Pg.exterior.coords)[:-1] + off - AW
        val = float((A @ obj).min())
        best = val if best is None else min(best, val)
    return best


def main():
    rng = np.random.default_rng(5)
    rows, worst, lb_viol = [], {'miss': 0.0, 'depth': 0.0}, 0
    tilts = [2.0, 8.0, 14.5, 20.0, 27.0, 35.0, 44.0]
    for f1d in tilts:
        for fWd in tilts:
            for gam in (0.0, 0.02, 0.1, 0.25):
                for psid in list(range(0, 46, 5)) + [f1d, fWd]:
                    f1, fW, psi = f1d * DEG, fWd * DEG, psid * DEG
                    for kind in ('miss', 'depth'):
                        ex = exact(gam, f1, fW, psi, kind)
                        if ex is None:
                            continue
                        cl = closed(gam, f1, fW, psi, kind)[0]
                        if cl > ex - 1e-9 and ex + math.cos(fW) * (kind == 'depth') < math.sin(f1) - 1e-9:
                            continue                                    # below s1's right vertex: outside the cone model
                        worst[kind] = max(worst[kind], abs(cl - ex))
                        if kind == 'miss' and principal(gam, f1, fW, psi) > ex + 1e-9:
                            lb_viol += 1
                        rows.append((f1d, fWd, gam, psid, kind, cl, ex))
    bad = [r for r in rows if abs(r[5] - r[6]) > 1e-7]
    out = dict(n=len(rows), max_abs_diff=worst, n_diff=len(bad), principal_lower_bound_violations=lb_viol,
               worst_rows=sorted(bad, key=lambda r: -abs(r[5] - r[6]))[:8])
    json.dump(out, open(os.path.join(HERE, '..', 'results', 'notch263.json'), 'w'), indent=1)
    print(json.dumps(out)[:1500])


if __name__ == '__main__':
    main()
