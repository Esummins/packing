"""A122 shared library: load the gallery landings S33 / S34 / S35 (Part I) and K19 (Part II, k0),
re-express each as a full eleven-square configuration, and give A106's and A107's engines a common
vocabulary.  Deliberately a near-clone of A108's a108lib so the two certificates are comparable
line for line.

Variable orderings (they are NOT the same):

  A107 order  z107 = [s, (x,y,th) * n]                (slots affine in s, not variables)
  A106 order  z106 = [(x,y,th) * 11, s]               (shadow11.Reduction with k = 0 pins)

A122's object of study is the FULL problem: all eleven squares free, s free, 34 variables.

READ-ONLY on every campaign: A106/A107/A108 modules are imported, never written.
"""
from __future__ import annotations

import os
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
           'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ[_v] = '1'
os.environ.setdefault('PYTHONDONTWRITEBYTECODE', '1')

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

S0 = L.S0                    # 969271/250000 = 3.877084
SHAT = L.SHAT                # 3.877083590022814 (Trump)

RES = os.path.join(ROOT, 'attempts', 'A122-s33-certify', 'results')

SLOTS = ('BL(0,0)', 'BL(0,1)', 'BL(0,2)', 'BL(1,0)', 'BR(0,0)', 'TR(0,0)')
FREE = ('f0', 'f1', 'f2', 'f3', 'f4')
NAMES = FREE + SLOTS                       # the A122 index order, free squares first

GAL = os.path.join(ROOT, 'attempts', 'A107-shadow-gallery', 'results')


def _gallery(part):
    fn = 'shadows.json' if part == 'I' else 'shadows_k0.json'
    with open(os.path.join(GAL, fn), encoding='utf-8') as f:
        return json.load(f)


#: the S33 family (and Trump / S07) all sit on the trump5 six-slot skeleton; S38 uses a different
#: one (BR(0,1) instead of BL(0,2)).  `names_for` returns the A122 index order for an entry.
SLOTS_S38 = ('BL(0,0)', 'BL(0,1)', 'BL(1,0)', 'BR(0,0)', 'BR(0,1)', 'TR(0,0)')


def slots_for(sid):
    return SLOTS_S38 if sid == 'S38' else SLOTS


def names_for(sid):
    return FREE + slots_for(sid)


def load_shadow(sid):
    """Gallery landing `sid` as (s, [(cx,cy,th)] * 11) ordered free-then-slot.

    For a Part II entry (K19) the split is 5 slot + 6 free, so the free square that occupies the
    missing slot cell is moved into the slot position and the remaining five keep the f0..f4 labels
    in gallery order.  The eleven-square SET is what is compared, never the labels.
    """
    part = 'II' if sid.startswith('K') else 'I'
    rec = next(r for r in _gallery(part) if r['id'] == sid)
    s = float(rec['s'])
    free = [tuple(map(float, c)) for c in rec['free']]
    slots = list(rec['slots'])
    want = slots_for(sid)
    have = {}
    for nm in slots:
        a, b, c, d = MZ.slot_affine(nm)
        have[nm] = (a + b * s, c + d * s, 0.0)
    leftover = []
    for nm in want:
        if nm in have:
            continue
        a, b, c, d = MZ.slot_affine(nm)
        tx, ty = a + b * s, c + d * s
        k = min(range(len(free)), key=lambda i: (free[i][0] - tx) ** 2 + (free[i][1] - ty) ** 2)
        have[nm] = free[k]
        leftover.append(k)
    fr = [free[i] for i in range(len(free)) if i not in leftover]
    cfg = list(fr) + [have[nm] for nm in want]
    assert len(cfg) == 11, (sid, len(cfg))
    return s, cfg, rec


# --------------------------------------------------------------------- Trump / S07
TRUMP_JSON = os.path.join(ROOT, 'attempts', 'A03-upper-reconstruct', 'trump11_exact.json')


def load_trump():
    """Trump's exact configuration in A122 NAMES order (A108's `order`)."""
    with open(TRUMP_JSON, encoding='utf-8') as f:
        d = json.load(f)
    s = float(d['s'])
    q = [(float(sq['cx']), float(sq['cy']), float(sq['theta'])) for sq in d['squares']]
    order = [7, 6, 9, 10, 8, 0, 3, 4, 1, 2, 5]
    return s, [q[i] for i in order]


def load_s07_exact():
    """A108's certified S07: s = 2 + 4 sqrt2 / 3, in A122 NAMES order."""
    r = math.sqrt(2.0)
    S = 2 + 4 * r / 3
    d45 = math.pi / 4
    cfg = [(1 + r / 2, 1 + 2 * r / 3, d45),
           (2 - r / 3, 2 + 5 * r / 6, d45),
           (1 + r, 1 + 7 * r / 6, d45),
           (19 / 6, 1.5 + r / 3, d45),
           (1.5 + 2 * r / 3, 1.5 - r / 6, d45),
           (0.5, 0.5, 0.0), (0.5, 1.5, 0.0), (0.5, 2.5, 0.0), (1.5, 0.5, 0.0),
           (S - 0.5, 0.5, 0.0), (S - 0.5, S - 0.5, 0.0)]
    return S, cfg


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
    n = len(cfg)
    wp = 1e9
    for i in range(n):
        for j in range(i + 1, n):
            wp = min(wp, L.sat_gap(cfg[i][:2], cfg[i][2], cfg[j][:2], cfg[j][2]))
    wc = min(min(L.wall_gaps(x, y, t, s).values()) for (x, y, t) in cfg)
    return float(wp), float(wc)


# --------------------------------------------------------------------- the side function sigma
def sigma(u, th):
    """Exact side of a NORMALISED configuration (A108 s. 1): a closed-form max over pairs/walls of
    a min over the four body axes.  No optimisation, so it cannot be fooled by a slightly
    infeasible landing."""
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
            best = math.inf
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


# --------------------------------------------------------------------- configuration matching
def tmod(t):
    """tilt modulo 90 deg, folded into [0, 90)."""
    d = math.degrees(t) % 90.0
    return d


def match_configs(cfgA, cfgB, s=None):
    """Greedy nearest-centre bijection A -> B; returns (perm, total centre distance, tilt diffs)."""
    n = len(cfgA)
    used = [False] * n
    perm = [None] * n
    tot = 0.0
    order = sorted(range(n), key=lambda i: -max(cfgA[i][0], cfgA[i][1]))
    for i in order:
        bj, bd = None, 1e18
        for j in range(n):
            if used[j]:
                continue
            d = math.hypot(cfgA[i][0] - cfgB[j][0], cfgA[i][1] - cfgB[j][1])
            if d < bd:
                bj, bd = j, d
        used[bj] = True
        perm[i] = bj
        tot += bd
    dt = [min(abs(tmod(cfgA[i][2]) - tmod(cfgB[perm[i]][2])),
              90 - abs(tmod(cfgA[i][2]) - tmod(cfgB[perm[i]][2]))) for i in range(n)]
    return perm, tot, dt
