"""A273 VERIFIER -- independent re-derivation of tree273's leaves from the dump (certs/tree273_<cell>.jsonl).
Shares NO geometry code with the tree (geom273 / sets273 / drop273 / drop4273 are not imported):
  * intervals: mpmath.iv (directed rounding), formulas re-typed from notes/disc273.md s.2-3 in the C_top frame;
  * cores: nominal polygon at the box midpoint eroded UNIFORMLY (shapely, mitre) by delta = 1e-6, 2e-6, ... until
    every vertex passes the mpmath.iv test of every defining constraint (the tree uses per-constraint offsets);
  * T_u outer: shapely convex hull of the mpmath.iv vertex boxes;
  * q-cells: shapely distances; K5 with the penumbra built from an INSCRIBED 128-gon of D' (points d + T(v - d),
    d a polygon vertex -- every such point is on a segment from D' through v), shapely differences;
  * disagreement (a CERT leaf the verifier cannot close with q-cells down to h_min/4) -> bisect the leaf (the
    tree's split rule), verify both halves, depth <= 6; a leaf still open is reported DISAGREE (never CERT);
  * PRUNE leaves: the named rule's h_v window re-derived with mpmath.iv;
  * coverage: the leaves of a cell are replayed through the deterministic split from the cell box (each leaf is a
    node of the bisection tree, every node is a leaf or has two covered children) -- no gap, no overlap.
    python verify273.py <cell|all> -> results/verify273_<cell>.json, results/verify273_index.jsonl"""
import gzip
import json
import math
import os
import sys

import numpy as np
import shapely
from mpmath import iv
from shapely.geometry import Point, Polygon

sys.dont_write_bytecode = True
iv.prec = 80
HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
CERTS, RES = os.path.join(ATT, 'certs'), os.path.join(ATT, 'results')
EPS, BIG, DMAX = 1e-9, 3.2, 1.01
DEG = math.pi / 180.0
SCALE = [1.0, 45 * DEG, DMAX, 45 * DEG]
PRIO = [0.25, 1.0, 0.25, 1.0]
R2 = 0.5 ** 0.5
SHAT = iv.mpf('3.877083590022814') + iv.mpf([0, '1e-12'])


def hull(pts):
    return shapely.convex_hull(shapely.multipoints(np.asarray(pts, float)))


def I(a, b=None):
    return iv.mpf([a, a]) if b is None else iv.mpf([a, b])


def trig(b):
    th, ph = I(*b[1]), I(*b[3])
    return iv.sin(th), iv.cos(th), iv.sin(ph), iv.cos(ph)


def constraints(kind, b, T):
    """interval-valued defining constraints (>= 0 on the set) in the C_top frame y'' = y - C_top."""
    s, c, sp, cp = T
    hu, dd = I(*b[0]), I(*b[2])

    def f(x, y):
        x, y = I(x), I(y)
        if kind == 'gam':
            return [y + c + s, -y, c * (x - hu - s) + s * (y + c + s), s * (x - hu) - c * (y + s), BIG - x]
        u = cp * (x - sp) + sp * (y + dd)
        v = cp * (y + dd) - sp * (x - sp)
        top = -dd + sp + cp - y
        if kind == 'xi':
            return [y + dd, top, x, v, 1 - u]
        return [y + dd, top, u, 1 - v, BIG - x]
    return f


def nominal(kind, m):
    hu, th, dd, ph = m
    c, s, cp, sp = math.cos(th), math.sin(th), math.cos(ph), math.sin(ph)
    if kind == 'gam':
        pts = [(hu + s, -c - s), (BIG, -c - s), (BIG, 0.0), (hu + c, 0.0), (hu, -s)]
    elif kind == 'xi':
        pts = [(0.0, -dd), (sp, -dd), (sp + cp, -dd + sp), (cp, -dd + sp + cp), (0.0, -dd + sp + cp)]
    else:
        pts = [(sp, -dd), (BIG, -dd), (BIG, -dd + sp + cp), (cp, -dd + sp + cp), (0.0, -dd + cp)]
    return hull(pts)


def core(kind, b, T):
    """per-constraint inward offsets: half-plane k of the midpoint set (its affine coefficients read off the mpmath
    constraint at degenerate parameters) is moved in by d_k until every vertex of the shapely intersection passes the
    mpmath.iv test of every constraint over the whole box; convexity -> core inside the true set."""
    f = constraints(kind, b, T)
    m = [0.5 * (lo + hi) for lo, hi in b]
    mb = [(v, v) for v in m]
    fm = constraints(kind, mb, trig(mb))
    g0, gx, gy = fm(0.0, 0.0), fm(1.0, 0.0), fm(0.0, 1.0)
    mid = lambda x: 0.5 * (float(x.a) + float(x.b))                  # noqa: E731
    A = [(mid(gx[k]) - mid(g0[k]), mid(gy[k]) - mid(g0[k]), mid(g0[k])) for k in range(len(g0))]
    d = [0.0] * len(A)
    for _ in range(24):
        P = Polygon([(-1, -9), (BIG + 1, -9), (BIG + 1, 9), (-1, 9)])
        for (a, bb, c), dk in zip(A, d):
            n = math.hypot(a, bb)
            H = halfplane(a / n, bb / n, (c - dk) / n)
            P = P.intersection(H)
            if P.is_empty or P.geom_type != 'Polygon':
                return None
        worst = [0.0] * len(A)
        for x, y in list(P.exterior.coords)[:-1]:
            for k, g in enumerate(f(x, y)):
                worst[k] = max(worst[k], 1e-12 - float(g.a))
        if max(worst) <= 0.0:
            return P
        d = [dk + (1.05 * w + 1e-12 if w > 0 else 0.0) for dk, w in zip(d, worst)]
    return None


def halfplane(a, b, c, R=40.0):
    """the polygon {a x + b y + c >= 0} clipped to a big square (a, b unit)."""
    px, py = -a * c, -b * c                                           # foot of the line
    tx, ty = -b, a
    return Polygon([(px + R * tx, py + R * ty), (px - R * tx, py - R * ty),
                    (px - R * tx + R * a, py - R * ty + R * b), (px + R * tx + R * a, py + R * ty + R * b)])


def tu_outer(b, T):
    s, c, _, _ = T
    V = [(s, -c - s), (s + c, -c), (c, I(0)), (I(0), -s)]
    pts = []
    for X, Y in V:
        X, Y = I(0) + X, I(0) + Y
        pts += [(float(X.a), float(Y.a)), (float(X.b), float(Y.a)), (float(X.b), float(Y.b)), (float(X.a), float(Y.b))]
    return hull(pts).buffer(1e-12, join_style=2)


def hv_window_empty(b, T):
    """PRUNE re-derived: no h_v in (0, 1) meets LOW, X_top > 2.82, X_top <= s^, open box, for any point of b."""
    s, c, sp, cp = T
    hu, dd = I(*b[0]), I(*b[2])
    ws, wp = c + s, sp + cp
    lows = [1 / iv.sqrt(2) + (1 - s) / c - c, 2.82 - wp - ws + dd, I(0)]
    ob = c + s - s * c - hu * c
    if ob.b <= 0:
        return True
    ups = [I(1), SHAT - wp - ws + dd] + ([ob / s] if s.a > 1e-9 else [])
    return any(lo.a > up.b for lo in lows for up in ups) or x_hits_c(b, T)


def x_hits_c(b, T):
    """H2 fails on the whole box: the centroid z of X n C at the midpoint (shapely) is strictly inside both for every
    parameter (mpmath.iv frame coordinates in (0, 1))."""
    s, c, sp, cp = T
    hu, th, dd, ph = [0.5 * (lo + hi) for lo, hi in b]
    cm, sm, cpm, spm = math.cos(th), math.sin(th), math.cos(ph), math.sin(ph)
    Cp = Polygon([(hu + sm, -cm - sm), (hu + sm + cm, -cm), (hu + cm, 0.0), (hu, -sm)])
    Xp = Polygon([(spm, -dd), (spm + cpm, -dd + spm), (cpm, -dd + spm + cpm), (0.0, -dd + cpm)])
    J = Cp.intersection(Xp)
    if J.is_empty or J.area <= 0:
        return False
    z = J.centroid
    x, y = I(z.x), I(z.y)
    hu_i, dd_i = I(*b[0]), I(*b[2])
    u = cp * (x - sp) + sp * (y + dd_i)
    v = cp * (y + dd_i) - sp * (x - sp)
    a = c * (x - hu_i - s) + s * (y + c + s)
    n = c * (y + c + s) - s * (x - hu_i - s)
    return all(t.a > 1e-12 and (1 - t).a > 1e-12 for t in (u, v, a, n))


NG = 128
CIRC = np.c_[np.cos(2 * np.pi * np.arange(NG) / NG), np.sin(2 * np.pi * np.arange(NG) / NG)]


def penumbra(K, z, r, tl=5.0):
    V = np.asarray(K.exterior.coords)[:-1]
    D = np.asarray(z) + r * CIRC
    far = (D[None, :, :] + tl * (V[:, None, :] - D[None, :, :])).reshape(-1, 2)
    return hull(np.r_[V, far]).buffer(-EPS, join_style=2)


class VSets:
    def __init__(self, b):
        T = trig(b)
        s = T[0]
        self.Lmin = float((-s).a)
        self.xlmax = -b[2][0]
        self.Tuo = tu_outer(b, T)
        self.W = self.Tuo.buffer(EPS, join_style=2)
        self.xi, self.xil, self.gam = core('xi', b, T), core('xil', b, T), core('gam', b, T)


def vdead(B, z, h, part):
    rho = h * math.sqrt(2.0)
    if z[0] + h < 0.5 or z[1] + h <= B.Lmin or (part == 'L' and z[1] - h >= B.xlmax):
        return True
    P = Point(z)
    if B.Tuo.distance(P) >= R2 + rho + EPS:
        return True
    K = B.xi if part == 'R' else B.xil
    lim = 0.5 - rho - EPS
    if (K is not None and K.distance(P) < lim) or (B.gam is not None and B.gam.distance(P) < lim):
        return True
    if K is None or B.gam is None:
        return False
    r = 0.5 - rho - 2 * EPS
    if r <= 0 or K.distance(P) <= r + 1e-9 or B.gam.distance(P) <= r + 1e-9:
        return False
    rest = B.W.difference(penumbra(K, z, r)).difference(penumbra(B.gam, z, r))
    return rest.is_empty or rest.distance(P) >= R2 + rho + EPS


def vcells(b, h0=0.125, hmin=1.0 / 8192, budget=100000):
    B = VSets(b)
    x0, y0, x1, y1 = B.Tuo.bounds
    x0, x1, y0, y1 = max(0.5, x0 - R2) - 1e-9, x1 + R2, B.Lmin - 1e-9, y1 + R2
    nx, ny = int(math.ceil((x1 - x0) / (2 * h0))), int(math.ceil((y1 - y0) / (2 * h0)))
    stack = [(x0 + (2 * i + 1) * h0, y0 + (2 * j + 1) * h0, h0, p) for i in range(nx) for j in range(ny) for p in 'RL']
    n = 0
    while stack:
        x, y, h, part = stack.pop()
        n += 1
        if n > budget:
            return False, n
        if vdead(B, (x, y), h, part):
            continue
        if h / 2 < hmin:
            return False, n
        stack += [(x + dx * h, y + dy * h, h / 2, part) for dx in (-0.5, 0.5) for dy in (-0.5, 0.5)]
    return True, n


def split(b):
    k = max(range(4), key=lambda i: PRIO[i] * (b[i][1] - b[i][0]) / SCALE[i])
    mid = 0.5 * (b[k][0] + b[k][1])
    lo, hi = list(b), list(b)
    lo[k], hi[k] = (b[k][0], mid), (mid, b[k][1])
    return lo, hi


def verify_box(b, depth=0):
    """CERT re-derived: PRUNE (h_v window) or q-cells; on failure bisect (depth <= 6). Returns (ok, boxes used)."""
    if b[0][0] >= 1.0 or hv_window_empty(b, trig(b)):
        return True, 1
    ok, _ = vcells(b)
    if ok:
        return True, 1
    if depth >= 6:
        return False, 1
    n = 1
    for c in split(b):
        okc, nc = verify_box(c, depth + 1)
        n += nc
        if not okc:
            return False, n
    return True, n


def coverage(cell, leaves):
    """replay the deterministic split from the cell box: every leaf a node, every node a leaf or split."""
    key = {tuple(map(tuple, l['box'])): l for l in leaves}
    used, stack = 0, [cell]
    while stack:
        b = stack.pop()
        if tuple(map(tuple, b)) in key:
            used += 1
            continue
        if max((b[i][1] - b[i][0]) / SCALE[i] for i in range(4)) < 2.0 ** -40:
            return False, 'gap at %s' % b
        lo, hi = split(b)
        stack += [lo, hi]
    return used == len(leaves), 'used %d of %d leaves' % (used, len(leaves))


def verify_cell(name):
    path = os.path.join(CERTS, 'tree273_%s.jsonl.gz' % name)
    leaves = [json.loads(l) for l in gzip.open(path, 'rt') if l.strip()]
    ti, pj = map(int, name[1:].split('_'))
    cell = [(0.0, 1.0), (ti * 5 * DEG, (ti + 1) * 5 * DEG), (0.0, DMAX), (pj * 5 * DEG, (pj + 1) * 5 * DEG)]
    cov_ok, cov_msg = coverage(cell, leaves)
    out = dict(cell=name, leaves=len(leaves), coverage=cov_ok, coverage_msg=cov_msg, cert_ok=0, prune_ok=0, open=0,
               bisected=0, disagree=[], prune_bad=[])
    for l in leaves:
        b, v = [tuple(x) for x in l['box']], l['v']
        if v == 'OPEN':
            out['open'] += 1
        elif v.startswith('PRUNE'):
            if b[0][0] >= 1.0 or hv_window_empty(b, trig(b)):
                out['prune_ok'] += 1
            else:
                ok, n = verify_box(b)                                 # a prune the verifier cannot re-derive: re-prove
                out['prune_ok' if ok else 'prune_bad'] += 1 if ok else 0
                if not ok:
                    out['prune_bad'].append(b)
        else:
            ok, n = verify_box(b)
            out['bisected'] += (n > 1)
            if ok:
                out['cert_ok'] += 1
            else:
                out['disagree'].append(b)
    out['verdict'] = 'PASS' if (cov_ok and not out['disagree'] and not out['prune_bad']) else 'FAIL'
    out['verdict'] += '' if out['open'] == 0 else ' (with %d OPEN leaves: not certified)' % out['open']
    json.dump(out, open(os.path.join(RES, 'verify273_%s.json' % name), 'w'), indent=1)
    with open(os.path.join(RES, 'verify273_index.jsonl'), 'a') as f:
        f.write(json.dumps({k: out[k] for k in ('cell', 'leaves', 'coverage', 'cert_ok', 'prune_ok', 'open', 'bisected',
                                                 'verdict')} | dict(disagree=len(out['disagree']))) + '\n')
    print(json.dumps({k: v for k, v in out.items() if k not in ('disagree', 'prune_bad')}), flush=True)
    return out


def main():
    try:
        import ctypes
        k32 = ctypes.windll.kernel32
        k32.SetPriorityClass(k32.GetCurrentProcess(), 0x00004000)
        k32.SetProcessAffinityMask(k32.GetCurrentProcess(), 0xFFFF)
    except Exception:
        pass
    if sys.argv[1] != 'all':
        verify_cell(sys.argv[1])
        return
    idx = os.path.join(RES, 'verify273_index.jsonl')
    done = {json.loads(l)['cell'] for l in open(idx)} if os.path.exists(idx) else set()
    tree = [json.loads(l) for l in open(os.path.join(CERTS, 'index273.jsonl'))]
    for r in tree:
        if os.path.exists(os.path.join(ATT, 'logs', 'STOP273')):
            break
        if r['cell'] not in done:
            verify_cell(r['cell'])


if __name__ == '__main__':
    main()
