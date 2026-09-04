"""A89 / T2 ADDENDUM: REACH and SELF-JAMMING of BL corner 2-crowds.

Object.  Pairs (A, B) of unit squares in the quadrant {x >= 0, y >= 0} (the BL
corner frame), interior-disjoint, BOTH meeting the open slot (0,1)^2 (A58
blockers, docs/proofs/k0_route.md 4.4 Lemma K0-PAIR).

  x-extent(Q) = c_x + (|cos th| + |sin th|)/2      (= max x over Q's vertices)
  y-extent(Q) = c_y + (|cos th| + |sin th|)/2
  X0 = max(x-extent A, x-extent B),  Y0 = max(y-extent A, y-extent B)
  REACH(A,B) = max(X0, Y0)

Population: A85's level-2 pair census, attempts/A85-k0-route/results/
a85_pairs_BL.json (33 656 surviving unordered pair boxes; boxes, not poses).
Pair indices i, j address the SOUND box list of a85_reach_BL.json variant
sigma_closed_7 (644 boxes) -- verified against the file's own box_i / box_j.

(a) sound UPPER bound of REACH over a pair box:
      x-extent_ub(box) = box.x1 + h_max(box),  h_max = corner85.h_max_of
    (max of (cos+sin)/2 over [th0,th1], padded outward by 1e-12).  Floats with
    outward rounding; the box coordinates themselves are floats in A85's file.
(b) witness pose: a rational (c_x, c_y, t = tan(th/2)) grid pose INSIDE each
    centre/tilt box such that both squares meet the OPEN SLOT (0,1)^2 and their
    interiors are disjoint.  A85's stored witnesses are per-BOX and meet the
    WIDENED box (0, 1.026)^2, not the slot, and are not checked pairwise, so
    they cannot be reused directly; the slot version is recomputed here and
    re-verified in exact Fractions (corner85.f_min_max + exact SAT).

Closed forms used throughout (all exact for rational t):
  h(th)  = (|cos th| + |sin th|)/2  = max coord offset of a vertex
  Q in quadrant  iff  c_x >= h and c_y >= h
  SAT gap of two unit squares at angles thA, thB, d = thB - thA,
      r = (|cos d| + |sin d|)/2,  D = c_B - c_A:
    gap = max( |D.e1A| , |D.e2A| , |D.e1B| , |D.e2B| ) - 1/2 - r
    (max over the four candidate axes; >= 0 iff interiors are disjoint)
  meets int(0,v)^2  iff  f_min_max(Q) < v,  f_min_max = min over Q of max(x,y)

Usage: python t2b_reach.py [run|probe N]
"""
from __future__ import annotations

import os
for _v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
           'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ.setdefault(_v, '1')

import json
import math
import random
import re
import sys
import time
from fractions import Fraction as Fr

import numpy as np

import a89lib as L

A85 = os.path.join(L.ATT, 'A85-k0-route')
sys.path.insert(0, os.path.join(A85, 'code'))
RES85 = os.path.join(A85, 'results')

from caselp import Box, t_of_deg                              # noqa: E402
import corner85 as C85                                        # noqa: E402

OUT_J = os.path.join(L.RESULTS, 't2b_reach.json')
OUT_P = os.path.join(L.RESULTS, 't2b_pairs.jsonl')

TD = 10 ** 9                 # rational denominator for witness coordinates
NX = NY = 5                  # witness grid in the centre box
NT = 7                       # witness grid in t
A_WIDE = 1.026               # A85's WIDENED corner box (w = 0.026); fallback witness
FEAS_TOL = 1e-9              # slack allowed on quadrant / disjointness / caps
SLOT_OUT = 1e-9              # f_min_max >= 1 + SLOT_OUT  =>  slot no longer met
TR_MAX = 2.0                 # translation library range
TR_STEP_FINE = 1e-3
TR_STEP_COARSE = 2e-2
ROT_MAX = 90.0               # rotation library range, degrees
ROT_STEP_FINE = 0.05
ROT_STEP_COARSE = 0.5
SQRT2P1 = 1.0 + math.sqrt(2.0)
THETA0S = (1.7347, 23.891023311515532)
SEED = 20260903


# ------------------------------------------------------------------ closed forms
def hval(th):
    return 0.5 * (abs(np.cos(th)) + abs(np.sin(th)))


def sat_gap(cxA, cyA, thA, cxB, cyB, thB):
    """vectorised 4-axis SAT gap; >= 0 iff interiors disjoint."""
    d = thB - thA
    r = 0.5 * (np.abs(np.cos(d)) + np.abs(np.sin(d)))
    dx, dy = cxB - cxA, cyB - cyA
    cA, sA = np.cos(thA), np.sin(thA)
    cB, sB = np.cos(thB), np.sin(thB)
    p = np.maximum.reduce([np.abs(dx * cA + dy * sA), np.abs(-dx * sA + dy * cA),
                           np.abs(dx * cB + dy * sB), np.abs(-dx * sB + dy * cB)])
    return p - 0.5 - r


def verts_np(cx, cy, th):
    """(n,4,2) vertices."""
    c, s = np.cos(th), np.sin(th)
    u = np.array([-.5, .5, .5, -.5])
    v = np.array([-.5, -.5, .5, .5])
    X = cx[:, None] + c[:, None] * u[None, :] - s[:, None] * v[None, :]
    Y = cy[:, None] + s[:, None] * u[None, :] + c[:, None] * v[None, :]
    return np.stack([X, Y], axis=2)


def f_minmax_np(V):
    """min over Q of max(x, y), vectorised over the leading axis of V (n,4,2)."""
    best = np.min(np.maximum(V[:, :, 0], V[:, :, 1]), axis=1)
    for k in range(4):
        P = V[:, k, :]
        Q = V[:, (k + 1) % 4, :]
        dx, dy = Q[:, 0] - P[:, 0], Q[:, 1] - P[:, 1]
        den = dx - dy
        ok = np.abs(den) > 1e-300
        s = np.where(ok, (P[:, 1] - P[:, 0]) / np.where(ok, den, 1.0), -1.0)
        good = ok & (s >= 0.0) & (s <= 1.0)
        cand = np.where(good, P[:, 0] + s * dx, np.inf)
        best = np.minimum(best, cand)
    return best


# ---------------------------------------------------------- exact (Fractions)
def h_exact(t):
    co, si = C85.cos_sin_t(t)
    return (abs(co) + abs(si)) / 2


def sat_gap_exact(A, B):
    """exact 4-axis SAT gap for rational poses A = (cx, cy, t)."""
    cxA, cyA, tA = A
    cxB, cyB, tB = B
    coA, siA = C85.cos_sin_t(tA)
    coB, siB = C85.cos_sin_t(tB)
    dx, dy = cxB - cxA, cyB - cyA
    # cos(thB - thA), sin(thB - thA) exactly
    cd = coA * coB + siA * siB
    sd = coA * siB - siA * coB
    r = (abs(cd) + abs(sd)) / 2
    p = max(abs(dx * coA + dy * siA), abs(-dx * siA + dy * coA),
            abs(dx * coB + dy * siB), abs(-dx * siB + dy * coB))
    return p - Fr(1, 2) - r


def reach_exact(A):
    cx, cy, t = A
    h = h_exact(t)
    return cx + h, cy + h


# ------------------------------------------------------------------ the census
def load_boxes():
    R = json.load(open(os.path.join(RES85, 'a85_reach_BL.json')))
    V = R['variants']['sigma_closed_7']
    rows = [r for r in V['rows'] if r['sound']]
    return R, V, rows, [Box.from_json(r['box']) for r in rows]


def stream_pairs(path):
    pat = re.compile(r'"i":\s*(\d+),\s*"j":\s*(\d+),\s*"sense_i":\s*"(\w)",'
                     r'\s*"sense_j":\s*"(\w)"')
    out, tail = [], ''
    with open(path) as f:
        while True:
            chunk = f.read(1 << 22)
            if not chunk:
                break
            buf = tail + chunk
            last = 0
            for m in pat.finditer(buf):
                out.append((int(m.group(1)), int(m.group(2)), m.group(3), m.group(4)))
                last = m.end()
            tail = buf[max(last, len(buf) - 300):]
    return out


def verify_box_index(boxes, path):
    """confirm i, j address the SOUND box list, using the file's own box_i."""
    with open(path) as f:
        head = f.read(1 << 20)
    k = head.index('"surviving_level2"')
    m = re.search(r'"i":\s*(\d+),\s*"j":\s*(\d+),.*?"box_i":\s*\{(.*?)\}.*?'
                  r'"box_j":\s*\{(.*?)\}', head[k:], re.S)
    i, j = int(m.group(1)), int(m.group(2))
    bi = json.loads('{' + m.group(3) + '}')
    bj = json.loads('{' + m.group(4) + '}')
    ok = all(abs(getattr(boxes[i], f) - bi[f]) < 1e-12 for f in
             ('x0', 'x1', 'y0', 'y1', 'th0', 'th1')) and \
        all(abs(getattr(boxes[j], f) - bj[f]) < 1e-12 for f in
            ('x0', 'x1', 'y0', 'y1', 'th0', 'th1'))
    return bool(ok), i, j


# ------------------------------------------------------------------ witnesses
def t_inward(th0, th1):
    """rational t-range strictly inside [th0, th1] degrees."""
    lo = Fr(0) if th0 <= 0.0 else Fr(math.ceil(t_of_deg(th0) * TD) + 1, TD)
    hi = Fr(1) if th1 >= 90.0 else Fr(math.floor(t_of_deg(th1) * TD) - 1, TD)
    if lo > hi:
        mid = Fr(round(t_of_deg(0.5 * (th0 + th1)) * TD), TD)
        return mid, mid
    return lo, hi


def cand_poses(b):
    """rational grid poses inside box b: (list of (Fr cx, Fr cy, Fr t), arrays)."""
    tl, th = t_inward(b.th0, b.th1)
    xs = [Fr(round((b.x0 + (b.x1 - b.x0) * k / (NX - 1.0)) * TD), TD)
          for k in range(NX)]
    ys = [Fr(round((b.y0 + (b.y1 - b.y0) * k / (NY - 1.0)) * TD), TD)
          for k in range(NY)]
    ts = [tl + (th - tl) * Fr(k, NT - 1) for k in range(NT)] if th > tl else [tl]
    t45 = Fr(round(t_of_deg(45.0) * TD), TD)        # h is maximal at tilt 45 deg
    if tl < t45 < th:
        ts.append(t45)
    P = [(x, y, t) for t in ts for x in xs for y in ys]
    cx = np.array([float(p[0]) for p in P])
    cy = np.array([float(p[1]) for p in P])
    tt = np.array([float(p[2]) for p in P])
    thr = 2.0 * np.arctan(tt)
    return P, cx, cy, thr


_CACHE = {}


def box_cands(k, boxes):
    """all grid poses of box k that lie in the quadrant, with their f_min_max."""
    if k in _CACHE:
        return _CACHE[k]
    b = boxes[k]
    P, cx, cy, thr = cand_poses(b)
    h = hval(thr)
    keep = np.where((cx >= h) & (cy >= h))[0]
    fm = f_minmax_np(verts_np(cx[keep], cy[keep], thr[keep]))
    out = ([P[i] for i in keep], cx[keep], cy[keep], thr[keep], fm)
    if len(_CACHE) < 700:
        _CACHE[k] = out
    return out


def _pick(Pi, cxi, cyi, thi, fmi, Pj, cxj, cyj, thj, fmj, a):
    mi = np.where(fmi < a)[0]
    mj = np.where(fmj < a)[0]
    if not len(mi) or not len(mj):
        return None
    g = sat_gap(cxi[mi][:, None], cyi[mi][:, None], thi[mi][:, None],
                cxj[mj][None, :], cyj[mj][None, :], thj[mj][None, :])
    k = int(np.argmax(g))
    ia, ja = mi[k // g.shape[1]], mj[k % g.shape[1]]
    if g[k // g.shape[1], k % g.shape[1]] < 0.0:
        return None
    return {'A': Pi[ia], 'B': Pj[ja],
            'gap': float(g[k // g.shape[1], k % g.shape[1]]),
            'slot_A': float(fmi[ia]), 'slot_B': float(fmj[ja]),
            'cxA': float(cxi[ia]), 'cyA': float(cyi[ia]), 'thA': float(thi[ia]),
            'cxB': float(cxj[ja]), 'cyB': float(cyj[ja]), 'thB': float(thj[ja]),
            'n_cand': [int(len(mi)), int(len(mj))]}


def find_witness(i, j, boxes):
    """best (largest SAT gap) disjoint pose pair.  Primary target: both squares
    meet the OPEN SLOT (0,1)^2 (the addendum's / K0-PAIR's w = 0 definition).
    Fallback: both meet A85's WIDENED box (0, 1.026)^2 -- the census's actual
    hypothesis -- recorded as witness_kind 'widened'."""
    Ci = box_cands(i, boxes)
    Cj = box_cands(j, boxes)
    if not len(Ci[1]) or not len(Cj[1]):
        return None
    w = _pick(*Ci, *Cj, 1.0)
    if w is not None:
        w['kind'] = 'slot'
        return w
    w = _pick(*Ci, *Cj, A_WIDE)
    if w is not None:
        w['kind'] = 'widened'
    return w


def witness_exact(w, kind='slot'):
    """exact re-verification: disjoint, both meet the slot, exact reaches."""
    A, B = w['A'], w['B']
    g = sat_gap_exact(A, B)
    fa = C85.f_min_max(A[0], A[1], A[2])
    fb = C85.f_min_max(B[0], B[1], B[2])
    xa, ya = reach_exact(A)
    xb, yb = reach_exact(B)
    ha, hb = h_exact(A[2]), h_exact(B[2])
    X0 = max(xa, xb)
    Y0 = max(ya, yb)
    lim = 1 if kind == 'slot' else Fr(1026, 1000)
    return {'sat_gap_exact': str(g), 'sat_gap_exact_float': float(g),
            'disjoint_exact': bool(g >= 0),
            'f_minmax_A_exact': str(fa), 'f_minmax_B_exact': str(fb),
            'f_minmax_A_float': float(fa), 'f_minmax_B_float': float(fb),
            'kind': kind, 'target_a': str(lim),
            'both_meet_target_exact': bool(fa < lim and fb < lim),
            'both_meet_slot_exact': bool(fa < 1 and fb < 1),
            'in_quadrant_exact': bool(A[0] >= ha and A[1] >= ha
                                      and B[0] >= hb and B[1] >= hb),
            'X0_exact': float(X0), 'Y0_exact': float(Y0),
            'reach_exact': float(max(X0, Y0)),
            'X0_exact_str': str(X0), 'Y0_exact_str': str(Y0)}


# ------------------------------------------------------------- motion library
def _traj_feasible(cxA, cyA, thA, cxB, cyB, thB, X0, Y0):
    """boolean array: pose pair feasible (quadrant, disjoint, reach caps)."""
    hA, hB = hval(thA), hval(thB)
    ok = (cxA >= hA - FEAS_TOL) & (cyA >= hA - FEAS_TOL) \
        & (cxB >= hB - FEAS_TOL) & (cyB >= hB - FEAS_TOL)
    ok &= (cxA + hA <= X0 + FEAS_TOL) & (cyA + hA <= Y0 + FEAS_TOL)
    ok &= (cxB + hB <= X0 + FEAS_TOL) & (cyB + hB <= Y0 + FEAS_TOL)
    ok &= sat_gap(cxA, cyA, thA, cxB, cyB, thB) >= -FEAS_TOL
    return ok


def _prefix(ok):
    """length of the leading all-True run."""
    bad = np.flatnonzero(~ok)
    return int(bad[0]) if len(bad) else len(ok)


def _run_traj(TA, TB, X0, Y0):
    """-> (n_feasible_prefix, first index in prefix where the slot is singly met,
           end-state pose of the prefix)."""
    cxA, cyA, thA = TA
    cxB, cyB, thB = TB
    ok = _traj_feasible(cxA, cyA, thA, cxB, cyB, thB, X0, Y0)
    n = _prefix(ok)
    if n == 0:
        return 0, -1, None
    fa = f_minmax_np(verts_np(cxA[:n], cyA[:n], thA[:n]))
    fb = f_minmax_np(verts_np(cxB[:n], cyB[:n], thB[:n]))
    free = ((fa >= 1.0 + SLOT_OUT) | (fb >= 1.0 + SLOT_OUT))
    idx = np.flatnonzero(free)
    end = (cxA[n - 1], cyA[n - 1], thA[n - 1], cxB[n - 1], cyB[n - 1], thB[n - 1])
    return n, (int(idx[0]) if len(idx) else -1), end


def _translate(pose, which, ax, sgn, step, tmax=TR_MAX):
    """trajectory arrays for translating square `which` along +-x / +-y."""
    cxA, cyA, thA, cxB, cyB, thB = pose
    n = int(tmax / step) + 1
    d = np.arange(n) * step * sgn
    z = np.zeros(n)
    A = [cxA + z, cyA + z, thA + z]
    B = [cxB + z, cyB + z, thB + z]
    T = A if which == 0 else B
    T[0 if ax == 0 else 1] = T[0 if ax == 0 else 1] + d
    return A, B


def _translate_both(pose, ax, step, tmax=TR_MAX):
    cxA, cyA, thA, cxB, cyB, thB = pose
    n = int(tmax / step) + 1
    d = np.arange(n) * step
    z = np.zeros(n)
    A = [cxA + z, cyA + z, thA + z]
    B = [cxB + z, cyB + z, thB + z]
    A[0 if ax == 0 else 1] = A[0 if ax == 0 else 1] + d
    B[0 if ax == 0 else 1] = B[0 if ax == 0 else 1] + d
    return A, B


def _pivots(cx, cy, th):
    """centre + the 4 vertices."""
    c, s = math.cos(th), math.sin(th)
    P = [(cx, cy)]
    for (u, v) in ((-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5)):
        P.append((cx + c * u - s * v, cy + s * u + c * v))
    return P


def _rotate(pose, which, piv, sgn, step, amax=ROT_MAX):
    cxA, cyA, thA, cxB, cyB, thB = pose
    cx, cy, th = (cxA, cyA, thA) if which == 0 else (cxB, cyB, thB)
    px, py = _pivots(cx, cy, th)[piv]
    n = int(amax / step) + 1
    a = np.radians(np.arange(n) * step * sgn)
    ca, sa = np.cos(a), np.sin(a)
    rx, ry = cx - px, cy - py
    ncx = px + ca * rx - sa * ry
    ncy = py + sa * rx + ca * ry
    nth = th + a
    z = np.zeros(n)
    if which == 0:
        return [ncx, ncy, nth], [cxB + z, cyB + z, thB + z]
    return [cxA + z, cyA + z, thA + z], [ncx, ncy, nth]


def motion_list(pose, step_tr, step_rot, tier4=True):
    """(name, builder) pairs, cheapest / most likely first."""
    M = []
    for w in (0, 1):
        for ax in (0, 1):
            for sg in (-1, 1):
                M.append(('T%d%s%s' % (w, 'xy'[ax], '-+'[(sg + 1) // 2]),
                          lambda p, w=w, ax=ax, sg=sg: _translate(p, w, ax, sg, step_tr)))
    for ax in (0, 1):
        M.append(('Tboth%s+' % 'xy'[ax],
                  lambda p, ax=ax: _translate_both(p, ax, step_tr)))
    for w in (0, 1):
        for pv in range(5):
            for sg in (-1, 1):
                M.append(('R%d%s%s' % (w, ('c', 'v0', 'v1', 'v2', 'v3')[pv],
                                       '-+'[(sg + 1) // 2]),
                          lambda p, w=w, pv=pv, sg=sg: _rotate(p, w, pv, sg, step_rot)))
    if not tier4:
        return M
    rots = [(w, pv, sg) for w in (0, 1) for pv in range(5) for sg in (-1, 1)]
    trs = [(w, ax, sg) for w in (0, 1) for ax in (0, 1) for sg in (-1, 1)]

    def comp(p, m1, m2):
        A, B = m1(p)
        ok = _traj_feasible(A[0], A[1], A[2], B[0], B[1], B[2], comp.X0, comp.Y0)
        n = _prefix(ok)
        if n == 0:
            return None
        k = n - 1
        mid = (A[0][k], A[1][k], A[2][k], B[0][k], B[1][k], B[2][k])
        return m2(mid)
    for (w, pv, sg) in rots:
        for (ax, sg2) in ((0, -1), (0, 1), (1, -1), (1, 1)):
            M.append(('R%d%s%s>T%d%s%s' % (w, pv, '-+'[(sg + 1) // 2], w, 'xy'[ax],
                                           '-+'[(sg2 + 1) // 2]),
                      lambda p, w=w, pv=pv, sg=sg, ax=ax, sg2=sg2: comp(
                          p, lambda q: _rotate(q, w, pv, sg, step_rot),
                          lambda q: _translate(q, w, ax, sg2, step_tr))))
    for (w, ax, sg) in trs:
        for pv in range(5):
            for sg2 in (-1, 1):
                M.append(('T%d%s%s>R%d%s%s' % (w, 'xy'[ax], '-+'[(sg + 1) // 2],
                                               w, pv, '-+'[(sg2 + 1) // 2]),
                          lambda p, w=w, ax=ax, sg=sg, pv=pv, sg2=sg2: comp(
                              p, lambda q: _translate(q, w, ax, sg, step_tr),
                              lambda q: _rotate(q, w, pv, sg2, step_rot))))
    M.append(('__comp_holder', comp))
    return M


def library(pose, X0, Y0, coarse=True):
    """-> dict(jammed, motion, n_tried).  LIBRARY-JAMMED is an UPPER bound on
    self-jammed: a coarse-step false negative can only add pairs to it."""
    st = (TR_STEP_COARSE, ROT_STEP_COARSE) if coarse else (TR_STEP_FINE, ROT_STEP_FINE)
    M = motion_list(pose, st[0], st[1])
    comp = M[-1][1]
    comp.X0, comp.Y0 = X0, Y0
    M = M[:-1]
    for k, (name, mk) in enumerate(M, 1):
        tr = mk(pose)
        if tr is None:
            continue
        A, B = tr
        n, first, _end = _run_traj(A, B, X0, Y0)
        if first >= 0:
            return {'jammed': False, 'motion': name, 'n_tried': k,
                    'steps_to_free': first, 'prefix': n}
    return {'jammed': True, 'motion': None, 'n_tried': len(M)}


# ---------------------------------------------------------- jam classification
JAM_DEFS = {
    'order': ['near-slot', 'stacked-dipping-vertex', 'side-jam', 'floating', 'other'],
    'tol_wall': 0.02,
    'near-slot': 'min over the two squares of d_slot(Q) < 0.05, where '
                 'd_slot(Q) = max(|c_x - 0.5|, |c_y - 0.5|, tilt_deg / 90)',
    'stacked-dipping-vertex':
        'there is a wall w in {x=0, y=0} and a labelling (Q1, Q2) with '
        'tilt(Q1) < 5 deg, dist(Q1, w) <= 0.02, Q2 beyond Q1 along w-normal '
        '(centre_normal(Q2) > centre_normal(Q1)), min_normal(Q2) <= '
        'max_normal(Q1) + 0.02, and min_tangential(Q2) < min_tangential(Q1) '
        '(a vertex of Q2 dips into the gap between Q1 and the OTHER wall)',
    'side-jam': 'both squares within 0.02 of the SAME wall w and '
                '|delta centre along w| > |delta centre across w|',
    'floating': 'some square touches no wall: min_x > 0.02 and min_y > 0.02',
    'other': 'none of the above',
    'other_subtypes': {
        'diamond-wedge': 'both tilts in [35,45] deg, each square touches a wall '
                         '(min(min_x, min_y) <= 0.02) and each reaches its cap '
                         '(max(max_x, max_y) >= min(X0, Y0) - 0.02)',
        'other-unclassified': 'none of the above'},
}


def _sq(cx, cy, th):
    c, s = math.cos(th), math.sin(th)
    V = [(cx + c * u - s * v, cy + s * u + c * v)
         for (u, v) in ((-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5))]
    m = math.degrees(th) % 90.0
    return {'cx': cx, 'cy': cy, 'th': th, 'tilt': min(m, 90.0 - m), 'V': V,
            'minx': min(p[0] for p in V), 'miny': min(p[1] for p in V),
            'maxx': max(p[0] for p in V), 'maxy': max(p[1] for p in V)}


def other_subtype(pose, X0, Y0):
    cxA, cyA, thA, cxB, cyB, thB = pose
    A, B = _sq(cxA, cyA, thA), _sq(cxB, cyB, thB)
    cap = min(X0, Y0)
    if (35.0 <= A['tilt'] <= 45.0 and 35.0 <= B['tilt'] <= 45.0
            and min(A['minx'], A['miny']) <= 0.02
            and min(B['minx'], B['miny']) <= 0.02
            and max(A['maxx'], A['maxy']) >= cap - 0.02
            and max(B['maxx'], B['maxy']) >= cap - 0.02):
        return 'diamond-wedge'
    return 'other-unclassified'


def jam_type(pose):
    cxA, cyA, thA, cxB, cyB, thB = pose
    A, B = _sq(cxA, cyA, thA), _sq(cxB, cyB, thB)
    tw = JAM_DEFS['tol_wall']

    def dslot(Q):
        return max(abs(Q['cx'] - 0.5), abs(Q['cy'] - 0.5), Q['tilt'] / 90.0)
    if min(dslot(A), dslot(B)) < 0.05:
        return 'near-slot'
    # stacked dipping vertex, both walls, both labellings
    for (nrm, tan) in (('y', 'x'), ('x', 'y')):
        for (Q1, Q2) in ((A, B), (B, A)):
            dn1 = Q1['min' + nrm]
            if Q1['tilt'] >= 5.0 or dn1 > tw:
                continue
            if Q2['c' + nrm] <= Q1['c' + nrm]:
                continue
            if Q2['min' + nrm] > Q1['max' + nrm] + tw:
                continue
            if Q2['min' + tan] < Q1['min' + tan]:
                return 'stacked-dipping-vertex'
    for nrm in ('x', 'y'):
        if A['min' + nrm] <= tw and B['min' + nrm] <= tw:
            tan = 'y' if nrm == 'x' else 'x'
            if abs(A['c' + tan] - B['c' + tan]) > abs(A['c' + nrm] - B['c' + nrm]):
                return 'side-jam'
    if (A['minx'] > tw and A['miny'] > tw) or (B['minx'] > tw and B['miny'] > tw):
        return 'floating'
    return 'other'


# --------------------------------------------------------------------- H2
def bin_ok(th0, th1, t0):
    """tilt bin consistent with {0} u [t0, 90-t0] u {90}; straddling counts OK."""
    return not (th1 <= t0 or th0 >= 90.0 - t0)


# ------------------------------------------------------------------- canaries
def canaries():
    out = []

    # (a) K0-PAIR (b) exhibit, docs/proofs/k0_route.md 4.4, built from the doc's
    #     OWN vertex lists (centre = vertex mean, theta = first edge direction);
    #     the printed vertices are rounded, so `edge_len` reports the rounding.
    def from_verts(V):
        cx = sum(p[0] for p in V) / 4.0
        cy = sum(p[1] for p in V) / 4.0
        th = math.atan2(V[1][1] - V[0][1], V[1][0] - V[0][0]) % (math.pi / 2)
        el = math.hypot(V[1][0] - V[0][0], V[1][1] - V[0][1])
        return (cx, cy, th), el
    VA = [(0.643, 0.7), (1.409, 1.343), (0.766, 2.109), (0.0002, 1.466)]
    VB = [(0.95, 0.9), (1.45, 0.034), (2.316, 0.534), (1.816, 1.4)]
    A, elA = from_verts(VA)
    B, elB = from_verts(VB)
    out.append(('canary_a_k0route_4.4_exhibit', A, B,
                'docs/proofs/k0_route.md 4.4 exhibit rebuilt from its vertex lists '
                '(edge lengths %.4f / %.4f from the rounded print); doc reports '
                'SAT gap 0.0441; expected library-UNJAMMED (A floats, apex at 0.7)'
                % (elA, elB)))

    # (b) near-slot pocket: A axis-aligned at (0.51, 0.5); B flush on top at
    #     (0.51, 1.5) rotated 0.3 deg about its bottom-left vertex.
    A2 = (0.51, 0.5, 0.0)
    bx, by = 0.51 - 0.5, 1.5 - 0.5          # B's bottom-left vertex before rotation
    ph = math.radians(0.3)
    c, s = math.cos(ph), math.sin(ph)
    rx, ry = 0.51 - bx, 1.5 - by
    B2 = (bx + c * rx - s * ry, by + s * rx + c * ry, ph)
    out.append(('canary_b_near_slot_pocket', A2, B2,
                'axis-aligned A offset 0.01 from the slot + flush partner '
                'rotated 0.3 deg about its BL vertex'))

    # (c) Trump's TL crowd mapped to the BL frame (reflect y -> s - y about the
    #     TL corner): sq6 tilted 40.1819 deg + sq4, the eps-off upright.
    s0 = 3.877083590022814
    for (nm, cx, cy, thd) in (('sq6', 1.5362871813120151, 3.172475421161055,
                               40.181937290329716),
                              ('sq4', 0.5, 2.5325583153496147, 0.0)):
        pass
    A3 = (1.5362871813120151, s0 - 3.172475421161055,
          math.radians(-40.181937290329716) % (math.pi / 2))
    A3 = (1.5362871813120151, s0 - 3.172475421161055,
          math.radians(90.0 - 40.181937290329716))
    B3 = (0.5, s0 - 2.5325583153496147, 0.0)
    out.append(('canary_c_trump_TL_crowd_in_BL_frame', A3, B3,
                'Trump is k5; sanity classification only. TL box mapped by '
                'y -> s - y, so sq6 tilt 40.1819 -> theta 49.8181 (tilt 40.1819), '
                'sq4 stays axis-aligned'))

    recs = []
    for (nm, A, B, note) in out:
        pose = (A[0], A[1], A[2], B[0], B[1], B[2])
        SA, SB = _sq(*A), _sq(*B)
        fa = float(f_minmax_np(verts_np(np.array([A[0]]), np.array([A[1]]),
                                        np.array([A[2]])))[0])
        fb = float(f_minmax_np(verts_np(np.array([B[0]]), np.array([B[1]]),
                                        np.array([B[2]])))[0])
        g = float(sat_gap(np.array([A[0]]), np.array([A[1]]), np.array([A[2]]),
                          np.array([B[0]]), np.array([B[1]]), np.array([B[2]]))[0])
        hA, hB = hval(np.array([A[2]]))[0], hval(np.array([B[2]]))[0]
        X0 = max(A[0] + hA, B[0] + hB)
        Y0 = max(A[1] + hA, B[1] + hB)
        lib = library(pose, X0, Y0, coarse=False)
        recs.append({
            'name': nm, 'note': note,
            'A': {'cx': A[0], 'cy': A[1], 'theta_deg': math.degrees(A[2]),
                  'tilt_deg': SA['tilt'], 'minx': SA['minx'], 'miny': SA['miny']},
            'B': {'cx': B[0], 'cy': B[1], 'theta_deg': math.degrees(B[2]),
                  'tilt_deg': SB['tilt'], 'minx': SB['minx'], 'miny': SB['miny']},
            'f_minmax_A': fa, 'f_minmax_B': fb,
            'A_meets_slot': bool(fa < 1.0), 'B_meets_slot': bool(fb < 1.0),
            'sat_gap': g, 'interior_disjoint': bool(g >= 0.0),
            'in_quadrant': bool(SA['minx'] >= -1e-12 and SA['miny'] >= -1e-12
                                and SB['minx'] >= -1e-12 and SB['miny'] >= -1e-12),
            'X0': X0, 'Y0': Y0, 'reach': max(X0, Y0),
            'library': lib, 'jam_type': jam_type(pose) if lib['jammed'] else None})
    return recs


# --------------------------------------------------------------------- driver
def hist(vals, edges):
    out = {}
    for a, b in zip(edges[:-1], edges[1:]):
        out['[%g,%g)' % (a, b)] = int(sum(1 for v in vals if a <= v < b))
    return out


R_EDGES = [1.0, 1.2, 1.4, 1.6, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.42, 3.0]


def main(argv):
    t00 = time.time()
    fc = L.free_commit_mb()
    print('free commit %.0f MB' % fc, flush=True)
    lim = None
    if len(argv) >= 2 and argv[0] == 'probe':
        lim = int(argv[1])

    R, V, rows, boxes = load_boxes()
    ppath = os.path.join(RES85, 'a85_pairs_BL.json')
    idx_ok, vi, vj = verify_box_index(boxes, ppath)
    print('box index check (i,j address the sound list): %s (first pair %d,%d)'
          % (idx_ok, vi, vj), flush=True)
    pairs = stream_pairs(ppath)
    print('pairs streamed: %d' % len(pairs), flush=True)

    hmax = np.array([C85.h_max_of(b) for b in boxes])
    X1 = np.array([b.x1 for b in boxes]) + hmax
    Y1 = np.array([b.y1 for b in boxes]) + hmax
    TH0 = np.array([b.th0 for b in boxes])
    TH1 = np.array([b.th1 for b in boxes])

    order = list(range(len(pairs)))
    subsample = None
    if lim:
        random.Random(SEED).shuffle(order)
        order = sorted(order[:lim])
        subsample = {'seed': SEED, 'n': lim}

    n_wit = 0
    recs = []
    t_wit = t_lib = 0.0
    with open(OUT_P, 'w') as fo:
        for cnt, pk in enumerate(order, 1):
            i, j, si, sj = pairs[pk]
            xub = max(X1[i], X1[j])
            yub = max(Y1[i], Y1[j])
            rec = {'i': i, 'j': j, 'sense_i': si, 'sense_j': sj,
                   'th_i': [float(TH0[i]), float(TH1[i])],
                   'th_j': [float(TH0[j]), float(TH1[j])],
                   'x_i': [boxes[i].x0, boxes[i].x1],
                   'y_i': [boxes[i].y0, boxes[i].y1],
                   'x_j': [boxes[j].x0, boxes[j].x1],
                   'y_j': [boxes[j].y0, boxes[j].y1],
                   'X0_ub': float(xub), 'Y0_ub': float(yub),
                   'reach_ub': float(max(xub, yub))}
            for t0 in THETA0S:
                rec['h2_%g' % t0] = bool(bin_ok(TH0[i], TH1[i], t0)
                                         and bin_ok(TH0[j], TH1[j], t0))
            t1 = time.time()
            w = find_witness(i, j, boxes)
            t_wit += time.time() - t1
            if w is None:
                rec['witness_found'] = False
                fo.write(json.dumps(rec) + '\n')
                recs.append(rec)
                continue
            n_wit += 1
            ex = witness_exact(w, w['kind'])
            pose = (w['cxA'], w['cyA'], w['thA'], w['cxB'], w['cyB'], w['thB'])
            X0, Y0 = ex['X0_exact'], ex['Y0_exact']
            rec['witness_found'] = True
            rec['witness_kind'] = w['kind']
            rec['witness'] = {
                'kind': w['kind'],
                'A': [str(x) for x in w['A']], 'B': [str(x) for x in w['B']],
                'thA_deg': math.degrees(w['thA']), 'thB_deg': math.degrees(w['thB']),
                'tiltA_deg': L.mis90(math.degrees(w['thA'])),
                'tiltB_deg': L.mis90(math.degrees(w['thB'])),
                'sat_gap': w['gap'], 'f_minmax_A': w['slot_A'],
                'f_minmax_B': w['slot_B'], 'n_candidates': w['n_cand']}
            rec['witness_exact'] = ex
            rec['X0'] = X0
            rec['Y0'] = Y0
            rec['reach'] = ex['reach_exact']
            rec['reach_le_2_both_axes'] = bool(X0 < 2.0 and Y0 < 2.0)
            t1 = time.time()
            lib = library(pose, X0, Y0, coarse=False)
            t_lib += time.time() - t1
            rec['library'] = lib
            rec['jam_type'] = jam_type(pose) if lib['jammed'] else None
            rec['other_subtype'] = (other_subtype(pose, X0, Y0)
                                    if rec['jam_type'] == 'other' else None)
            fo.write(json.dumps(rec) + '\n')
            recs.append(rec)
            if cnt % 2000 == 0 or cnt == len(order):
                print('[%7.1fs] %6d/%6d witnesses=%d jammed=%d  (wit %.0fs lib %.0fs)'
                      % (time.time() - t00, cnt, len(order), n_wit,
                         sum(1 for r in recs if r.get('library', {}).get('jammed')),
                         t_wit, t_lib), flush=True)

    # ---------------------------------------------------------------- summary
    wit = [r for r in recs if r.get('witness_found')]
    jam = [r for r in wit if r['library']['jammed']]
    unj = [r for r in wit if not r['library']['jammed']]
    ex_bad = [[r['i'], r['j']] for r in wit
              if not (r['witness_exact']['disjoint_exact']
                      and r['witness_exact']['both_meet_target_exact']
                      and r['witness_exact']['in_quadrant_exact'])]

    def block(rs, key):
        v = [r[key] for r in rs if key in r]
        return {'n': len(v), 'max': (max(v) if v else None),
                'min': (min(v) if v else None),
                'mean': (sum(v) / len(v) if v else None),
                'hist': hist(v, R_EDGES)}

    jt, jts = {}, {}
    for r in jam:
        jt[r['jam_type']] = jt.get(r['jam_type'], 0) + 1
        if r.get('other_subtype'):
            jts[r['other_subtype']] = jts.get(r['other_subtype'], 0) + 1

    # necessary-condition check: reach >= 2 on an axis should be unjammable
    exc = [{'i': r['i'], 'j': r['j'], 'X0': r['X0'], 'Y0': r['Y0'],
            'reach': r['reach'], 'jam_type': r['jam_type']}
           for r in jam if r['X0'] >= 2.0 or r['Y0'] >= 2.0]

    def h2sel(rs, t0):
        return [r for r in rs if r['h2_%g' % t0]]

    n = len(recs)
    out = {
        'attempt': 'A89-tilt-floor / T2 ADDENDUM: reach + self-jamming of BL 2-crowds',
        'inputs': {
            'pairs': 'attempts/A85-k0-route/results/a85_pairs_BL.json (level 2)',
            'boxes': 'attempts/A85-k0-route/results/a85_reach_BL.json '
                     'variant sigma_closed_7, 644 sound boxes',
            'box_index_check_i_j_address_sound_list': idx_ok,
            'n_pairs_in_file': len(pairs), 'n_pairs_processed': n,
            'subsample': subsample},
        'definitions': {
            'x_extent': 'c_x + (|cos th| + |sin th|)/2 (= max x over the square)',
            'REACH': 'max(x-extent A, x-extent B, y-extent A, y-extent B)',
            'X0': 'max x-extent over the pair', 'Y0': 'max y-extent over the pair',
            'meets_slot': 'f_min_max(Q) = min over Q of max(x,y) < 1 '
                          '(corner85.meets_open_box with a = 1); EXACT for rational t',
            'reach_ub': 'box.x1 + h_max(box) per square, max over the pair; '
                        'h_max = corner85.h_max_of (outward padded 1e-12)',
            'witness': 'rational grid pose strictly inside each box '
                       '(%d x %d centres x %d t values), chosen to maximise the SAT '
                       'gap among slot-meeting quadrant poses; re-verified exactly'
                       % (NX, NY, NT),
            'self_jammed_H1': 'no continuous motion of the pair (other nine squares '
                              'absent) keeping X(t) <= X0 and Y(t) <= Y0 throughout '
                              'and ending with the open slot met by at most one square',
            'library': {'tier1_translations': 8, 'tier2_simultaneous': 2,
                        'tier3_rotations': 20,
                        'tier4_compositions': 160,
                        'total_motions': 190,
                        'translation_range': TR_MAX,
                        'rotation_range_deg': ROT_MAX,
                        'step_coarse': [TR_STEP_COARSE, ROT_STEP_COARSE],
                        'step_fine': [TR_STEP_FINE, ROT_STEP_FINE],
                        'soundness': 'LIBRARY-JAMMED is an UPPER BOUND on the '
                                     'self-jammed set: the library is finite and the '
                                     'coarse scan can only miss an escape. Every '
                                     'coarse SUCCESS is re-verified at the fine step.'},
            'H2': 'tilt bins in {0} u [theta_0, 90-theta_0] u {90}; a box straddling '
                  'the threshold counts as consistent (sound direction)',
            'jam_types': JAM_DEFS,
            'theoretical_max_single_blocker_reach': SQRT2P1},
        'H0_all_pairs': {
            'reach_ub': block(recs, 'reach_ub'),
            'X0_ub_max': max(r['X0_ub'] for r in recs),
            'Y0_ub_max': max(r['Y0_ub'] for r in recs),
            'n_reach_ub_ge_2': sum(1 for r in recs if r['reach_ub'] >= 2.0),
            'n_reach_ub_ge_1_plus_sqrt2': sum(1 for r in recs
                                              if r['reach_ub'] >= SQRT2P1),
            'n_witness_found': len(wit),
            'frac_witness_found': len(wit) / n if n else None,
            'n_witness_kind_slot': sum(1 for r in wit if r['witness_kind'] == 'slot'),
            'n_witness_kind_widened': sum(1 for r in wit
                                          if r['witness_kind'] == 'widened'),
            'witness_rate_by_reach_ub_bin': {
                '[%g,%g)' % (a, b): [
                    sum(1 for r in recs if a <= r['reach_ub'] < b
                        and r.get('witness_found')),
                    sum(1 for r in recs if a <= r['reach_ub'] < b)]
                for a, b in zip(R_EDGES[:-1], R_EDGES[1:])},
            'witness_rate_note':
                'a GRID LOWER BOUND on the realisable fraction: %d x %d centres x '
                '<= %d t values per box, so a pair box with a thin 2-crowd sliver '
                'can be missed.  A85 reports 586 / 644 boxes individually witnessed '
                'against the WIDENED box (0, 1.026)^2, which is a weaker target '
                'than the slot and is not a pairwise statement.' % (NX, NY, NT + 1),
            'n_witness_exact_verification_failed': len(ex_bad),
            'witness_reach': block(wit, 'reach'),
            'witness_X0_max': max((r['X0'] for r in wit), default=None),
            'witness_Y0_max': max((r['Y0'] for r in wit), default=None),
            'n_witness_reach_ge_2': sum(1 for r in wit if r['reach'] >= 2.0),
            'n_witness_X0_and_Y0_lt_2': sum(1 for r in wit
                                            if r['reach_le_2_both_axes'])},
        'H1_library_jamming': {
            'n_with_witness': len(wit),
            'n_library_jammed': len(jam),
            'n_library_unjammed': len(unj),
            'frac_library_jammed': len(jam) / len(wit) if wit else None,
            'frac_library_jammed_ci95': None,
            'max_reach_library_jammed': max((r['reach'] for r in jam), default=None),
            'max_X0_library_jammed': max((r['X0'] for r in jam), default=None),
            'max_Y0_library_jammed': max((r['Y0'] for r in jam), default=None),
            'reach_distribution_library_jammed': block(jam, 'reach'),
            'reach_distribution_library_unjammed': block(unj, 'reach'),
            'jam_type_counts': jt,
            'other_subtype_counts': jts,
            'unjamming_motion_counts': {},
            'necessary_condition_X0_lt2_and_Y0_lt2': {
                'n_jammed_with_both_lt_2': sum(1 for r in jam
                                               if r['reach_le_2_both_axes']),
                'n_jammed_with_an_axis_ge_2': len(exc),
                'exceptions': exc[:50],
                'claim': 'if a reach is >= 2 the slot can be freed by sliding a '
                         'square out along that axis; an exception is a '
                         'library-jammed pair with X0 >= 2 or Y0 >= 2'}},
        'sanity_by_witness_kind': {
            k: {'n': sum(1 for r in wit if r['witness_kind'] == k),
                'reach_min': min((r['reach'] for r in wit
                                  if r['witness_kind'] == k), default=None),
                'reach_max': max((r['reach'] for r in wit
                                  if r['witness_kind'] == k), default=None),
                'bound': (SQRT2P1 if k == 'slot' else A_WIDE + math.sqrt(2.0)),
                'n_violations': sum(1 for r in wit if r['witness_kind'] == k
                                    and r['reach'] > (SQRT2P1 if k == 'slot'
                                                      else A_WIDE + math.sqrt(2.0))
                                    + 1e-9),
                'n_reach_lt_2': sum(1 for r in wit if r['witness_kind'] == k
                                    and r['reach'] < 2.0)}
            for k in ('slot', 'widened')},
        'sanity_note':
            'a single blocker meeting the OPEN SLOT has reach < 1 + sqrt2 = '
            '%.9f (45-deg diamond on the wall with its left vertex at x < 1); '
            'against the WIDENED target (0, 1.026)^2 the bound is 1.026 + sqrt2 '
            '= %.9f.  An AXIS-ALIGNED blocker meeting the open slot has reach '
            '< 2 ([a,a+1] with a < 1).'
            % (SQRT2P1, A_WIDE + math.sqrt(2.0)),
        'theta0_sweep_of_jam_types': {},
        'H2_tilt_floor_consistent': {},
        'headline': {},
        'canaries': canaries(),
        'secs': time.time() - t00,
        'secs_witness': t_wit, 'secs_library': t_lib,
    }
    mc = {}
    for r in unj:
        k = r['library'].get('motion')
        mc[str(k)] = mc.get(str(k), 0) + 1
    out['H1_library_jamming']['unjamming_motion_counts'] = dict(
        sorted(mc.items(), key=lambda kv: -kv[1])[:25])
    if wit:
        p = len(jam) / len(wit)
        se = math.sqrt(max(p * (1 - p), 0.0) / len(wit))
        out['H1_library_jamming']['frac_library_jammed_ci95'] = \
            [max(0.0, p - 1.96 * se), min(1.0, p + 1.96 * se)]

    for t0 in (0.0, 0.5, 1.0, 1.7347, 2.0, 5.0, 7.2, 10.0, 14.3, 15.0, 20.0,
               23.891023311515532, 30.0):
        sel = [r for r in recs if bin_ok(r['th_i'][0], r['th_i'][1], t0)
               and bin_ok(r['th_j'][0], r['th_j'][1], t0)]
        sw = [r for r in sel if r.get('witness_found')]
        sj = [r for r in sw if r['library']['jammed']]
        out['theta0_sweep_of_jam_types']['%g' % t0] = {
            'n_pairs': len(sel), 'n_witness': len(sw), 'n_jammed': len(sj),
            'max_reach_jammed': max((r['reach'] for r in sj), default=None),
            'types': {t: sum(1 for r in sj if r['jam_type'] == t)
                      for t in JAM_DEFS['order']}}

    for t0 in THETA0S:
        sel = h2sel(recs, t0)
        selw = h2sel(wit, t0)
        selj = h2sel(jam, t0)
        p = (len(selj) / len(selw)) if selw else None
        se = (math.sqrt(max(p * (1 - p), 0.0) / len(selw)) if selw and p is not None
              else None)
        out['H2_tilt_floor_consistent']['theta0=%g' % t0] = {
            'n_pairs_consistent': len(sel),
            'frac_of_census': len(sel) / n if n else None,
            'reach_ub': block(sel, 'reach_ub'),
            'n_with_witness': len(selw),
            'witness_reach': block(selw, 'reach'),
            'max_reach_ub': max((r['reach_ub'] for r in sel), default=None),
            'max_witness_reach': max((r['reach'] for r in selw), default=None),
            'H1_cap_H2_n_library_jammed': len(selj),
            'H1_cap_H2_frac_jammed': p,
            'H1_cap_H2_frac_jammed_ci95': ([max(0.0, p - 1.96 * se),
                                            min(1.0, p + 1.96 * se)]
                                           if se is not None else None),
            'H1_cap_H2_max_reach': max((r['reach'] for r in selj), default=None),
            'H1_cap_H2_jam_type_counts': {t: sum(1 for r in selj
                                                 if r['jam_type'] == t)
                                          for t in JAM_DEFS['order']}}

    S0F = 3.877083590022814
    xj = [r['X0'] for r in jam]
    mrj = out['H1_library_jamming']['max_reach_library_jammed']
    mra = out['H0_all_pairs']['witness_reach']['max']
    out['headline'] = {
        '1_max_reach_library_jammed': mrj,
        '1_max_reach_all_pairs_witness': mra,
        '1_max_reach_ub_all_pairs_boxes': out['H0_all_pairs']['reach_ub']['max'],
        '1_theoretical_single_blocker_max': SQRT2P1,
        '2_two_times_max_reach_jammed': (2 * mrj if mrj else None),
        '2_adjacent_corner_contact_possible_s_3.82':
            (bool(2 * mrj >= 3.82) if mrj else None),
        '2_adjacent_corner_contact_possible_s_3.877084':
            (bool(2 * mrj >= 3.877083590022814) if mrj else None),
        '3_frac_library_jammed': out['H1_library_jamming']['frac_library_jammed'],
        '3_frac_needs_third_square_or_far_structure':
            (1 - out['H1_library_jamming']['frac_library_jammed']
             if out['H1_library_jamming']['frac_library_jammed'] is not None else None),
        '2_detail': {
            'note': 'BL and BR 2-crowds share the x axis: their reach envelopes '
                    'overlap iff X0(BL) + X0(BR) >= s.  By D4 the BR statistics '
                    'mirror the BL ones, so the extreme case is 2 * max X0.',
            'max_X0_library_jammed': (max(xj) if xj else None),
            'two_times_max_X0_jammed': (2 * max(xj) if xj else None),
            'n_jammed_with_X0_ge_half_s_3.82': sum(1 for v in xj if v >= 3.82 / 2),
            'n_jammed_with_X0_ge_half_s_hat': sum(1 for v in xj if v >= S0F / 2),
            'frac_jammed_with_X0_ge_half_s_hat':
                (sum(1 for v in xj if v >= S0F / 2) / len(xj)) if xj else None,
            'overlap_possible_at_s_3.82': (bool(2 * max(xj) >= 3.82) if xj else None),
            'overlap_possible_at_s_hat': (bool(2 * max(xj) >= S0F) if xj else None),
            'interpretation': 'X0(BL) + X0(BR) >= s is NECESSARY for the two corner '
                              '2-crowds to interfere, not sufficient (the envelopes '
                              'are axis-aligned bounding constraints, not the '
                              'squares).  A pair of jammed 2-crowds at opposite ends '
                              'of the bottom wall therefore is NOT excluded by reach '
                              'arithmetic alone.'},
    }
    json.dump(out, open(OUT_J, 'w'), indent=1, default=str)
    print(json.dumps({k: v for k, v in out.items()
                      if k not in ('definitions', 'canaries')}, indent=1,
                     default=str), flush=True)
    print('\ncanaries:', flush=True)
    for cr in out['canaries']:
        print(' %-38s slotA=%s slotB=%s gap=%+.4f reach=%.4f  lib=%s (%s) type=%s'
              % (cr['name'], cr['A_meets_slot'], cr['B_meets_slot'], cr['sat_gap'],
                 cr['reach'], 'JAMMED' if cr['library']['jammed'] else 'unjammed',
                 cr['library'].get('motion'), cr['jam_type']), flush=True)
    print('-> %s , %s   (%.1f s)' % (OUT_J, OUT_P, time.time() - t00), flush=True)


if __name__ == '__main__':
    main(sys.argv[1:])
