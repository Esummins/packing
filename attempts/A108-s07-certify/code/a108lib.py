"""A108 shared library: load A107's S07 landing, re-express it as a full 11-square configuration,
and give the two engines a common vocabulary.

Two variable orderings live in this lab and they are NOT the same:

  A107 order  z107 = [s, (x,y,th) * nfree]                    (slots are affine in s, not variables)
  A106 order  z106 = [(x,y,th) * 11, s]                       (shadow11.Reduction with k = 0 pins)

A108's object of study is the FULL problem: all eleven squares free, s free, 34 variables.  Both
orderings can express it (A107 with slots = (), nfree = 11), so both engines are usable and are
cross-checked against each other.

READ-ONLY on every campaign: A106/A107 modules are imported, never written.
"""
from __future__ import annotations

import os
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
           'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ[_v] = '1'

import json
import math
import sys

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
A106 = os.path.join(ROOT, 'attempts', 'A106-shadow-diameter', 'code')
A107 = os.path.join(ROOT, 'attempts', 'A107-shadow-gallery', 'code')
for p in (A107, A106):
    if p not in sys.path:
        sys.path.insert(0, p)

import shadowlib as L        # noqa: E402  (A107)
import minimise as MZ        # noqa: E402  (A107)
import analyse as AN         # noqa: E402  (A107)
import shadow11 as S11       # noqa: E402  (A106)

S0 = L.S0                    # 969271/250000 = 3.877084, the certified side
SHAT = L.SHAT                # 3.877083590022814

RES = os.path.join(ROOT, 'attempts', 'A108-s07-certify', 'results')

# --------------------------------------------------------------------- S07 from A107
S07_KEY = ('["A60", ["BL(0,0)", "BL(0,1)", "BL(1,0)", "BR(0,0)", "TR(0,0)"], '
           '[["BL(0,0)", "BL(0,1)", "BL(0,2)", "BL(1,0)", "BR(0,0)", "TR(0,0)"], 5]]')
MINIMA = os.path.join(ROOT, 'attempts', 'A107-shadow-gallery', 'results', 'minima.json')

SLOTS = ('BL(0,0)', 'BL(0,1)', 'BL(0,2)', 'BL(1,0)', 'BR(0,0)', 'TR(0,0)')
FREE = ('f0', 'f1', 'f2', 'f3', 'f4')
NAMES = FREE + SLOTS                       # the A108 index order, free squares first


def load_s07():
    """A107's S07 landing as (s, [(cx,cy,th)] * 11) in NAMES order."""
    with open(MINIMA, encoding='utf-8') as f:
        rec = json.load(f)[S07_KEY]
    s, z = rec['best'][0], rec['best'][1]
    cfg = [(z[1 + 3 * i], z[2 + 3 * i], z[3 + 3 * i]) for i in range(5)]
    for nm in SLOTS:
        a, b, c, d = MZ.slot_affine(nm)
        cfg.append((a + b * s, c + d * s, 0.0))
    return float(s), cfg


# --------------------------------------------------------------------- Trump
TRUMP_JSON = os.path.join(ROOT, 'attempts', 'A03-upper-reconstruct', 'trump11_exact.json')


def load_trump():
    """Trump's exact configuration, re-ordered into A108's NAMES order.

    Trump indices (A03): 0 (0.5,0.5), 1 (1.5,0.5), 2 (s-.5,.5), 3 (0.5,1.5), 4 (0.5,2.5325583),
    5 (s-.5,s-.5) are the six uprights; 6..10 are the five 40.18 deg squares.  The correspondence
    with S07 below is the nearest-centre bijection and is verified in trump_compare.py.
    """
    with open(TRUMP_JSON, encoding='utf-8') as f:
        d = json.load(f)
    s = float(d['s'])
    q = [(float(sq['cx']), float(sq['cy']), float(sq['theta'])) for sq in d['squares']]
    # A108 order: f0..f4 then BL(0,0) BL(0,1) BL(0,2) BL(1,0) BR(0,0) TR(0,0)
    order = [7, 6, 9, 10, 8, 0, 3, 4, 1, 2, 5]
    return s, [q[i] for i in order], order


# --------------------------------------------------------------------- ordering conversions
def to107(s, cfg):
    z = [float(s)]
    for (x, y, t) in cfg:
        z += [float(x), float(y), float(t)]
    return np.array(z)


def from107(z):
    n = (len(z) - 1) // 3
    return float(z[0]), [(z[1 + 3 * i], z[2 + 3 * i], z[3 + 3 * i]) for i in range(n)]


def to106(s, cfg):
    z = []
    for (x, y, t) in cfg:
        z += [float(x), float(y), float(t)]
    z.append(float(s))
    return np.array(z)


def from106(z):
    n = (len(z) - 1) // 3
    return float(z[-1]), [(z[3 * i], z[3 * i + 1], z[3 * i + 2]) for i in range(n)]


# --------------------------------------------------------------------- feasibility
def worst_gaps(s, cfg):
    """(worst pairwise SAT gap, worst containment gap).  Both must be >= 0 for a packing."""
    n = len(cfg)
    wp = 1e9
    for i in range(n):
        for j in range(i + 1, n):
            wp = min(wp, L.sat_gap(cfg[i][:2], cfg[i][2], cfg[j][:2], cfg[j][2]))
    wc = min(min(L.wall_gaps(x, y, t, s).values()) for (x, y, t) in cfg)
    return float(wp), float(wc)


# --------------------------------------------------------------------- the side function sigma
def sigma(u, th):
    """The exact side of a NORMALISED configuration: the smallest s such that unit squares with
    angles th at centres s*u_i are pairwise interior-disjoint and inside [0, s]^2.

    Every constraint is monotone in s (a pairwise SAT gap along a fixed axis is
    s*|du.a| - 1/2 - (support of the other square)/2, a containment gap is s*u - w or
    s*(1-u) - w), so the answer is a max/min of closed-form thresholds - no optimisation.
    """
    u = np.asarray(u, float)
    n = len(th)
    need = 0.0
    for i in range(n):
        w = L.half_width(th[i])
        for c in (u[i][0], u[i][1]):
            if c <= 0:
                return math.inf
            need = max(need, w / c)
        for c in (1.0 - u[i][0], 1.0 - u[i][1]):
            if c <= 0:
                return math.inf
            need = max(need, w / c)
    for i in range(n):
        for j in range(i + 1, n):
            du = u[i] - u[j]
            best = math.inf                     # smallest s that separates on SOME axis
            for (tt, ot) in ((th[i], th[j]), (th[j], th[i])):
                co, si = math.cos(tt), math.sin(tt)
                for ax in ((co, si), (-si, co)):
                    p = abs(du[0] * ax[0] + du[1] * ax[1])
                    g = (abs(ax[0] * math.cos(ot) + ax[1] * math.sin(ot))
                         + abs(-ax[0] * math.sin(ot) + ax[1] * math.cos(ot)))
                    thr = 0.5 + 0.5 * g
                    best = min(best, math.inf if p <= 0 else thr / p)
            need = max(need, best)
    return float(need)


def normalise(s, cfg):
    u = np.array([[c[0] / s, c[1] / s] for c in cfg])
    th = np.array([c[2] for c in cfg])
    return u, th
