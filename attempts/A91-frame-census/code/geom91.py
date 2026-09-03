"""A91 geometry adapter: read real packings, hand back A90-t3_90 geometry.

Imports (never edits) attempts/A90-nocrit-blocked/code/t3_90.py for
corner_state / all_pair_contacts / wall_contacts / cluster / wall_anchored /
intruder_anchored / depth_arg / unpack_z.
"""
from __future__ import annotations

import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

import json
import math

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
A91 = os.path.abspath(os.path.join(HERE, '..'))
ATT = os.path.abspath(os.path.join(A91, '..'))
ROOT = os.path.abspath(os.path.join(ATT, '..'))
A90C = os.path.join(ATT, 'A90-nocrit-blocked', 'code')
A88C = os.path.join(ATT, 'A88-fj-census', 'code')
A87 = os.path.join(ATT, 'A87-drain-flow')
A85C = os.path.join(ATT, 'A85-k0-route', 'code')
for p in (A90C, A88C, A85C):
    if p not in sys.path:
        sys.path.insert(0, p)

import t3_90 as T90                       # noqa: E402  (imports A85/A87 too)

RESULTS = os.path.join(A91, 'results')
NOTES = os.path.join(A91, 'notes')
LOGS = os.path.join(A91, 'logs')
CODE = HERE
for _d in (RESULTS, NOTES, LOGS):
    os.makedirs(_d, exist_ok=True)

CORNERS = ('BL', 'BR', 'TR', 'TL')          # A91 order (cycle)
WALLS = ('L', 'R', 'B', 'T')
SQRT2 = math.sqrt(2.0)
S_LO, S_HI = 3.82, 3.877084
M0 = 1.0 + 2.0 * SQRT2                      # 3.8284271...

# corner -> (vertical wall, horizontal wall); "away" signs (sx, sy)
CWALL = {'BL': ('L', 'B'), 'BR': ('R', 'B'), 'TR': ('R', 'T'), 'TL': ('L', 'T')}
CSGN = {'BL': (1, 1), 'BR': (-1, 1), 'TR': (-1, -1), 'TL': (1, -1)}
# wall -> its two corners, and the axis it is perpendicular to
WCORN = {'L': ('BL', 'TL'), 'R': ('BR', 'TR'),
         'B': ('BL', 'BR'), 'T': ('TL', 'TR')}
WAXIS = {'L': 'x', 'R': 'x', 'B': 'y', 'T': 'y'}
# far wall of corner c along its frame axis
FARWALL = {('BL', 'x'): 'R', ('BL', 'y'): 'T',
           ('BR', 'x'): 'L', ('BR', 'y'): 'T',
           ('TR', 'x'): 'L', ('TR', 'y'): 'B',
           ('TL', 'x'): 'R', ('TL', 'y'): 'B'}
# container direction of corner c's frame axis (away from c)
AXDIR = {}
for _c in CORNERS:
    sx, sy = CSGN[_c]
    AXDIR[(_c, 'x')] = np.array([float(sx), 0.0])
    AXDIR[(_c, 'y')] = np.array([0.0, float(sy)])


def trump_exact():
    """Trump's 11-square packing at s-hat, from A03's 60-digit certificate."""
    p = os.path.join(ATT, 'A03-upper-reconstruct', 'trump11_exact.json')
    d = json.load(open(p))
    s = float(d['s'])
    C = np.array([[float(q['cx']), float(q['cy'])] for q in d['squares']])
    TH = np.array([float(q['theta']) for q in d['squares']])
    return C, TH, s


def k0_endpoints():
    """The four exact-K0-BLOCKED polished endpoints of A87's k0dir87."""
    from fractions import Fraction
    p = os.path.join(A87, 'results', 'k0dir87.polish.jsonl')
    out = []
    for ln in open(p):
        if not ln.strip():
            continue
        r = json.loads(ln)
        if r.get('exact_K0_BLOCKED') and r.get('z_polished'):
            z = np.array([float(Fraction(v)) for v in r['z_polished']])
            C, TH, s = T90.unpack_z(z)
            out.append({'tag': r['tag'], 'sigma': r.get('sigma_polished'),
                        'C': C, 'TH': TH, 's': s,
                        'exact_n_block': r.get('exact_n_block')})
    return out


def geometry(C, TH, s):
    """corner state + contacts, in t3_90's conventions (tight bbox frames)."""
    bbox = T90.tight_bbox_of(C, TH)
    cst = T90.corner_state(C, TH, bbox)
    pcs = T90.all_pair_contacts(C, TH)
    wcs = T90.wall_contacts(C, TH, s)
    return bbox, cst, pcs, wcs


def argmin_type(A, tol=1e-9):
    """Lemma K trichotomy from the argmin set A (points in c's frame).

    S lies in {x = mu, y <= mu} u {y = mu, x <= mu}.
    X : S subset {x = mu} and S != {(mu,mu)}  (some point has p_x > p_y)
    Y : S subset {y = mu} and S != {(mu,mu)}  (some point has p_y > p_x)
    D : S = {(mu,mu)} exactly
    A numerically mixed set (points on both open sides) is reported as MIXED.
    """
    if not A:
        return None
    xside = [p for p in A if p[0] > p[1] + tol]      # y < x = mu : on {x = mu}
    yside = [p for p in A if p[1] > p[0] + tol]      # x < y = mu : on {y = mu}
    if xside and not yside:
        return 'X'
    if yside and not xside:
        return 'Y'
    if not xside and not yside:
        return 'D'
    return 'MIXED'


def argmin_type_ladder(A, ladder=(1e-11, 1e-9, 1e-7, 1e-5, 1e-3)):
    return {('%.0e' % t): argmin_type(A, t) for t in ladder}


def wall_mask_of(i, wcs, s, tol=1e-6):
    """omega(Q) subset {L,R,B,T} from the container-wall contacts."""
    m = set()
    for wc in wcs:
        if wc['i'] != i:
            continue
        w = {'x=0': 'L', 'x=s': 'R', 'y=0': 'B', 'y=s': 'T'}[wc['wall']]
        m.add(w)
    return frozenset(m)


def tilt_deg(th):
    return math.degrees(T90.tilt_of(th))
