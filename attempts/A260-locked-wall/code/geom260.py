"""A260 geometry of the HYBRID ring (family258 s.7): every wall carries a START toucher s1 = (a, f1) and an END toucher
W = (b, fW), both of sense +; the wall is a ROW iff fW = f1 and the shift e = 0, else an OPEN PAIR.

Wall frame as geom259 (wrapped, never edited): a toucher of tilt f whose extent along the wall starts at delta has
vertices L = delta + sin f:  (L,0), (L+c,z), (L+c-z,c+z), (L-z,c).   s1: delta = a.   W: delta = s - b - w(fW).
    shift e := delta_W - (a + sec f1)      (= the open gap of family258 s.7 when fW = f1;  e = 0, fW = f1: a row)
    T  := s1 + sec(f1) e_wall   (the normal cell of s1),    T' := W - sec(fW) e_wall.
x = 16 numbers: (a_k, f1_k, b_k, fW_k) for k = 0..3  (radians), + s.
hyb_margin >= 0: eight squares in [0,s]^2, pairwise interior-disjoint (all 28 pairs), tilts in (0, 45 deg], a, b < 1
(every corner box doubly met) and -- adj=True -- every toucher reaches its far slot (all-ADJ: delta + w > s - 2).
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A259-normal-room', 'code'))
import geom259 as Z                                                   # noqa: E402

SHAT, DEG = Z.SHAT, Z.DEG


def w_of(f):
    return math.cos(f) + math.sin(f)


def toucher(delta, f, s, k):
    c, z = math.cos(f), math.sin(f)
    L = delta + z
    return Z.rot_k([(L, 0.0), (L + c, z), (L + c - z, c + z), (L - z, c)], s, k)


def wall_verts(a, f1, b, fW, s, k):
    return [toucher(a, f1, s, k), toucher(s - b - w_of(fW), fW, s, k)]


def hyb_verts(x, s):
    out = []
    for k in range(4):
        out += wall_verts(x[4 * k], x[4 * k + 1], x[4 * k + 2], x[4 * k + 3], s, k)
    return out


def shift(a, f1, b, fW, s):
    return s - b - w_of(fW) - a - 1.0 / math.cos(f1)


def cell_T(a, f1, s, k):
    return toucher(a + 1.0 / math.cos(f1), f1, s, k)


def hyb_margin(x, s, adj=True, Vs=None):
    Vs = hyb_verts(x, s) if Vs is None else Vs
    m = min(Z.contain_margin(V, s) for V in Vs)
    for i in range(8):
        for j in range(i):
            m = min(m, Z.poly_gap(Vs[i], Vs[j]))
    for k in range(4):
        a, f1, b, fW = x[4 * k:4 * k + 4]
        m = min(m, f1, fW, 45 * DEG - f1, 45 * DEG - fW, 1.0 - a, 1.0 - b)
        if adj:
            m = min(m, a + w_of(f1) - (s - 2.0), b + w_of(fW) - (s - 2.0))
    return float(m)


def from_normal(xn, s):
    """geom259's x = (delta_0..3, phi_0..3) as a hybrid x (all shifts 0)."""
    x = []
    for k in range(4):
        d, f = xn[k], xn[4 + k]
        x += [d, f, s - d - Z.span(f), f]
    return np.array(x, float)


def sample_H(rng, s, n, adj=True, same_tilt=False, tries=400000):
    """rejection sampler of the hybrid family (hard feasibility)."""
    out = []
    for _ in range(tries):
        x = []
        for k in range(4):
            f1 = rng.uniform(0.3, 40.0) * DEG
            fW = f1 if same_tilt else min(45.0, max(0.3, f1 / DEG + rng.normal() * 4.0)) * DEG
            lo1 = max(0.0, s - 2.0 - w_of(f1)) if adj else 0.0
            loW = max(0.0, s - 2.0 - w_of(fW)) if adj else 0.0
            x += [rng.uniform(lo1, 1.0), f1, rng.uniform(loW, 1.0), fW]
        x = np.array(x)
        if hyb_margin(x, s, adj) >= 0:
            out.append(x)
            if len(out) >= n:
                break
    return out


def corpus():
    """A258's corpus loader (A253's 44 ring + poker rows, A255's 2 controls): (name, s, [8 ring squares + poker])."""
    sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A258-normal-ring', 'code'))
    import norm258 as N                                               # noqa: E402
    return N.load(), N
