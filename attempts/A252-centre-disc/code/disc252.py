"""A252: the CENTRE SET of a ring's pocket and its metrics.

For a ring x (16 parameters, A249 / A251 order: per corner BL, BR, TR, TL the wall meeter's
(theta_B, delta_B) then the floor meeter's (theta_A, delta_A)) at side s, the pocket is
P = [0, s]^2 minus the eight squares and the CENTRE SET is

    C := { q : the closed disc of radius 1/2 about q lies in P }  =  P (-) D_{1/2},

the set of admissible centres of unit squares in the pocket (Lemma INRADIUS: a unit square in P
has its centre in C).  Capacity criteria on C (each n-free, each a theorem given INRADIUS):

    diam(C) < 1                        => capacity <= 1
    C inside a disc of radius < 1/sqrt3 (ANY centre) => capacity <= 2   (THREE-DISC)
    C = X1 u X2 with diam(Xi) < 1     => capacity <= 2   (pigeonhole; Lean two_pieces)
    disp3(C) := max over triples of the least pairwise distance < 1 => capacity <= 2

Metrics computed here: far_O = max |q - O| over C (A251's Lemma CENTRE-DISC about the container
centre O), the smallest enclosing circle of C (centre free), the diameters of the two halves
{y <= s/2}, {y >= s/2} and of the four quadrants, disp3, diam, the pocket's inradius, and the
CONTACTS of the far point (which squares / walls the far disc touches).
"""
import math
import os
import sys

import numpy as np
from scipy.optimize import minimize
from shapely.geometry import Point, Polygon, box

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
for a in ('A249-type-t-chase', 'A248-corner-chase', 'A251-ring-pocket'):
    sys.path.insert(0, os.path.join(ROOT, 'attempts', a, 'code'))
import twotilted249 as W                                              # noqa: E402

HALF = math.pi / 2
R3 = 1.0 / math.sqrt(3.0)
NAMES = ('B_BL', 'A_BL', 'B_BR', 'A_BR', 'B_TR', 'A_TR', 'B_TL', 'A_TL')
SW = 3.877084


def belownormal():
    try:
        import ctypes
        k = ctypes.windll.kernel32
        k.SetPriorityClass.argtypes = [ctypes.c_void_p, ctypes.c_uint]
        k.SetProcessAffinityMask.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
        k.SetPriorityClass(ctypes.c_void_p(-1), 0x00004000)
        k.SetProcessAffinityMask(ctypes.c_void_p(-1), 0xFFFF)
    except Exception as e:                                             # noqa
        print('belownormal failed: %r' % (e,))


def ring(x, s):
    polys, names, _ = W.ring_polys(list(x), s, False)
    return polys, names


def margin(x, s):
    return float(W.ring_margin(list(x), s, False))


def pocket(polys, s):
    from shapely.ops import unary_union
    return box(0, 0, s, s).difference(unary_union([Polygon(V) for V in polys]))


def centre_set(polys, s, r=0.5, res=64):
    return pocket(polys, s).buffer(-r, res)


def geoms(C):
    if C.is_empty:
        return []
    return list(C.geoms) if hasattr(C, 'geoms') else [C]


def boundary_pts(C, step=0.01):
    pts = []
    for g in geoms(C):
        n = max(8, int(g.exterior.length / step))
        pts += [g.exterior.interpolate(k / n, normalized=True).coords[0] for k in range(n)]
    return np.array(pts) if pts else np.zeros((0, 2))


def far_from(pts, o):
    if len(pts) == 0:
        return 0.0, None
    d = np.hypot(pts[:, 0] - o[0], pts[:, 1] - o[1])
    i = int(np.argmax(d))
    return float(d[i]), (float(pts[i, 0]), float(pts[i, 1]))


def sec(pts):
    """smallest enclosing circle (radius, centre) of a point cloud (convex minimax, Nelder-Mead)."""
    if len(pts) == 0:
        return 0.0, None
    f = lambda c: float(np.max(np.hypot(pts[:, 0] - c[0], pts[:, 1] - c[1])))
    r = minimize(f, pts.mean(axis=0), method='Nelder-Mead',
                 options={'xatol': 1e-10, 'fatol': 1e-12, 'maxiter': 4000})
    return float(r.fun), (float(r.x[0]), float(r.x[1]))


def diam(pts):
    if len(pts) < 2:
        return 0.0
    D = np.hypot(pts[:, None, 0] - pts[None, :, 0], pts[:, None, 1] - pts[None, :, 1])
    return float(D.max())


def disp3(pts):
    """max over triples of the least pairwise distance (< 1: no three admissible centres)."""
    n = len(pts)
    if n < 3:
        return 0.0
    D = np.hypot(pts[:, None, 0] - pts[None, :, 0], pts[:, None, 1] - pts[None, :, 1])
    best = 0.0
    for i in range(n):
        m = D[i] > best
        for j in np.nonzero(m)[0]:
            if j <= i:
                continue
            v = np.minimum(D[i], D[j])
            v[i] = v[j] = 0.0
            t = min(D[i, j], float(v.max()))
            if t > best:
                best = t
    return float(best)


def inradius(P):
    lo, hi = 0.0, 2.0
    for _ in range(30):
        m = 0.5 * (lo + hi)
        if P.buffer(-m).is_empty:
            hi = m
        else:
            lo = m
    return lo


def contacts(q, polys, s, k=4):
    out = [(n, float(Polygon(V).distance(Point(q)))) for V, n in zip(polys, NAMES)]
    out += [('x=0', q[0]), ('y=0', q[1]), ('x=s', s - q[0]), ('y=s', s - q[1])]
    return sorted(out, key=lambda t: t[1])[:k]


def metrics(x, s, full=True):
    """every metric of the centre set of ring x at side s."""
    polys, _ = ring(x, s)
    P = pocket(polys, s)
    C = centre_set(polys, s)
    pts = boundary_pts(C)
    O = (s / 2, s / 2)
    fo, fq = far_from(pts, O)
    out = {'side': s, 'margin': margin(x, s), 'far_O': fo, 'far_pt': fq, 'C_area': float(C.area),
           'C_components': len(geoms(C)), 'pocket_area': float(P.area)}
    if not full or len(pts) == 0:
        return out
    r, c = sec(pts)
    out.update({'sec_r': r, 'sec_c': c, 'diam': diam(pts), 'disp3': disp3(pts),
                'inradius': inradius(P), 'contacts': contacts(fq, polys, s)})
    lo, hi = pts[pts[:, 1] <= s / 2 + 1e-9], pts[pts[:, 1] >= s / 2 - 1e-9]
    le, ri = pts[pts[:, 0] <= s / 2 + 1e-9], pts[pts[:, 0] >= s / 2 - 1e-9]
    out['halves_diam'] = max(diam(lo), diam(hi), diam(le), diam(ri))
    out['halves'] = {'bottom': diam(lo), 'top': diam(hi), 'left': diam(le), 'right': diam(ri)}
    quads = {}
    for name, sx, sy in (('BL', -1, -1), ('BR', 1, -1), ('TR', 1, 1), ('TL', -1, 1)):
        m = (sx * (pts[:, 0] - s / 2) >= -1e-9) & (sy * (pts[:, 1] - s / 2) >= -1e-9)
        quads[name] = far_from(pts[m], O)[0]
    out['quadrant_far'] = quads
    return out


def flat_limit_far(s):
    """[T] the corner-mouth limit: a corner whose two touchers tend to the flat squares
    [0,1] x [1,2] and [1,2] x [0,1] (in the corner frame) admits the centre (3/2, 3/2), at
    distance (s/2 - 3/2) sqrt2 from O; it exceeds 1/sqrt3 iff s > 3 + 2/sqrt6 = 3.81650."""
    return (s / 2 - 1.5) * math.sqrt(2.0)


S_FLAT = 3.0 + 2.0 / math.sqrt(6.0)


def flat_witness(s, corner=2, eps_deg=1.5, eta=0.02, base=None, maxiter=8000, seed=252):
    """a ring of the family with corner `corner` (index in BL, BR, TR, TL) near the flat limit:
    the corner's four parameters are FIXED at (90 - eps, 1 - eta, 90 - eps/2, 1 - eta/2) and the
    other twelve maximise the ring margin (Nelder-Mead from `base` or A249's s-hat ring).
    Returns (x, margin)."""
    rng = np.random.default_rng(seed)
    if base is None:
        base = [0.254, 0.891, 0.254, 0.695, 1.317, 0.695, 1.317, 0.891]
        base = list(base[:4]) + list(base[4:8]) + list(base[:4]) + list(base[4:8])
    fixed = [math.radians(90 - eps_deg), 1 - eta, math.radians(90 - eps_deg / 2), 1 - eta / 2]
    idx = [i for i in range(16) if i // 4 != corner]

    def full(y):
        x = list(base)
        for k, i in enumerate(idx):
            x[i] = y[k]
        x[4 * corner:4 * corner + 4] = fixed
        return x
    best = None
    for k in range(3):
        y0 = [base[i] for i in idx] if k == 0 else list(W.random_start(rng, 3, k))
        r = minimize(lambda y: -margin(full(y), s), y0, method='Nelder-Mead',
                     options={'xatol': 1e-9, 'fatol': 1e-12, 'maxiter': maxiter, 'adaptive': True})
        if best is None or r.fun < best.fun:
            best = r
    x = full(best.x)
    x = W.polish(lambda z, ss, t=False: W.ring_margin(z, ss, False, t), np.array(x), s)
    return [float(v) for v in x], margin(x, s)


if __name__ == '__main__':
    belownormal()
    import json
    j = json.load(open(os.path.join(ROOT, 'attempts', 'A249-type-t-chase', 'results', 'twotilted249_ring2.json')))
    y = j['3.877084']['result']['x']
    x16 = list(y[:4]) + list(y[4:8]) + list(y[:4]) + list(y[4:8])
    m = metrics(x16, SW)
    print('s-hat ring: ' + ', '.join('%s=%s' % (k, round(v, 4) if isinstance(v, float) else v)
                                     for k, v in m.items() if k not in ('contacts', 'halves', 'quadrant_far')))
    print('  contacts', m['contacts'], 'halves', m['halves'])
    print('flat limit far_O at s-hat %.4f (> 1/sqrt3 = %.5f iff s > %.5f)' % (flat_limit_far(SW), R3, S_FLAT))
    for s in (3.82, SW, 3.99):
        x, mg = flat_witness(s)
        mm = metrics(x, s)
        print('flat witness s=%.4f margin %+.5f far_O %.4f at %s sec_r %.4f halves %.4f disp3 %.4f diam %.4f'
              % (s, mg, mm['far_O'], mm['far_pt'], mm['sec_r'], mm['halves_diam'], mm['disp3'], mm['diam']))
        print('  contacts', mm['contacts'])
