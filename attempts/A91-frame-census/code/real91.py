"""A91 T2 (4)-(6) + T3 pilot: sampling L1/L2/L3, R6 realisability, cost.

R6 realisability relaxation (A88 p88_triage's method, rebuilt for A91 frames).
LP variables: the 22 centre coordinates + s.  Tilts are BINS (theta_i in a
sub-interval of [0, 45 deg]; a unit square's pose is 90-deg periodic and
reflection-symmetric, so [0,45] covers every tilt class).  Every row below is
SOUND: it holds for every genuine packing realising the frame with tilts in the
bins, so LP infeasibility => the frame has no realisation in those bins.

rows
  (containment)  hx_i <= x_i <= s - hx_i with hx_i = (cos+sin)/2 in [hlo,hhi]:
                 sound one-sided  x_i >= hlo, x_i + hlo <= s   (same in y)
  (wall mask)    w in omega(i)  ->  the touching coordinate equals hx_i:
                 x_i in [hlo, hhi]   (L),  s - x_i in [hlo,hhi]  (R), etc.
  (intrusion)    home square of c: Q meets c's closed unit box, so in c's frame
                 x_c, y_c <= 1 + sqrt2/2 and (x_c-1)+(y_c-1) <= 1
  (type)         Lemma K argmin side, in c's frame, over a tilt bin [tlo,thi]:
                 X: y - x <= -cos(thi)  (0 if tlo == 0)
                 Y: x - y <= -cos(thi)  (0 if tlo == 0)
                 D: |y - x| <= cos(tlo)
  (link)         (M,N) touching: |c_N - c_M| <= sqrt2 (8 supporting directions)
                 and (c_N - c_M).e >= -1                      (Lemma F6)
  (span)         implied by containment + wall + link rows (Lemma COL is the
                 k*sqrt2 >= m - 1 - sqrt2 statement the LP reproduces)
"""
from __future__ import annotations

import itertools
import json
import math
import os
import random
import time
from collections import defaultdict

import numpy as np
from scipy.optimize import linprog

import frame91 as F
import census91 as C

SQRT2 = math.sqrt(2.0)
H2 = SQRT2 / 2.0
S_LO, S_HI = F.S_LO, F.S_HI
CORNERS = F.CORNERS
WALLS = F.WALLS
DIRS8 = [(math.cos(k * math.pi / 4), math.sin(k * math.pi / 4)) for k in range(8)]
KILL_TOL = 1e-9


# ==================================================================== sampling
def shape_weights():
    ws = []
    for (ov, tv, nf) in C.shapes():
        v = C.shape_value(ov, tv, nf, 'L0')
        if v > 0:
            ws.append(((ov, tv, nf), v * float(C.label_mult(ov, tv, nf))))
    tot = sum(w for _, w in ws)
    return ws, tot


def random_frame_L0(rng, ws, tot, maxtry=4000):
    """uniform over R1-surviving L0 structures: pick a shape with probability
    proportional to its exact L0 count, then reject-sample colours."""
    r = rng.random() * tot
    acc = 0.0
    shape = ws[-1][0]
    for sh, w in ws:
        acc += w
        if r <= acc:
            shape = sh
            break
    ov, tv, nf = shape
    labels = list(range(11))
    for _ in range(maxtry):
        rng.shuffle(labels)
        f = F.Frame(11)
        k = 0
        for ci, c in enumerate(CORNERS):
            for _j in range(ov[ci]):
                i = labels[k]; k += 1
                f.home[i] = c
                f.open[i] = True
                f.tau[i] = rng.choice(('X', 'Y', 'D'))
                ws_ = F.CWALLS[c]
                f.mask[i] = frozenset(rng.choice(
                    [(), (ws_[0],), (ws_[1],), ws_]))
            for _j in range(tv[ci]):
                i = labels[k]; k += 1
                f.home[i] = c
                f.open[i] = False
                f.tau[i] = rng.choice(('X', 'Y', 'D'))
                ws_ = F.CWALLS[c]
                f.mask[i] = frozenset(rng.choice([(), (ws_[0],), (ws_[1],)]))
        for _j in range(nf):
            i = labels[k]; k += 1
            f.mask[i] = frozenset(rng.choice([(), ('L',), ('R',), ('B',), ('T',)]))
        if not F.R1(f):
            return f, shape
    return None, shape


def l1_count(f):
    """exact number of L1 refinements of this L0 = prod_slots #terminals."""
    p = 1
    for s in f.slots():
        p *= len(f.term_candidates(s))
    return p


def sample_terminals(f, rng):
    for s in f.slots():
        cand = f.term_candidates(s)
        if not cand:                    # R2 fails: this L0 carries no frame
            return None
        f.terminal[s] = rng.choice(cand)
    return f


def first_link_candidates(f, s):
    """admissible N1 for slot s given its terminal (L2 datum), with R5 boxes."""
    Q, a = s
    N, kind = f.terminal[s]
    e = f.edir(s)
    B = [F.cbox(f, i) for i in range(f.n)]
    termset = {n for (n, _k) in f.term_candidates(s)}
    out = []
    if kind == 'I':
        cand = [N] + [x for x in range(f.n) if x != Q and x not in termset]
    else:
        cand = [x for x in f.middle_candidates(s) if x != N]
    for x in cand:
        lo, _hi = F._bxdist(B[Q], B[x])
        if lo > SQRT2 + 1e-12:
            continue
        _dl, dh = F._dot_range(B[Q], B[x], e)
        if dh <= -1.0 + 1e-12:
            continue
        out.append(x)
    return out


def l2_count(f):
    p = 1
    per = {}
    for s in f.slots():
        k = len(first_link_candidates(f, s))
        per[s] = k
        p *= k
    return p, per


def chains(f, s, cap=20000):
    """all minimal columns Q -> ... -> terminal (distinct, box-feasible links).
    Returns (list of columns, capped flag)."""
    Q, a = s
    N, kind = f.terminal[s]
    e = f.edir(s)
    B = [F.cbox(f, i) for i in range(f.n)]
    termset = {n for (n, _k) in f.term_candidates(s)}
    mids = set(f.middle_candidates(s)) if kind == 'W' else \
        {x for x in range(f.n) if x != Q and x not in termset}

    def linkok(u, v):
        lo, _ = F._bxdist(B[u], B[v])
        if lo > SQRT2 + 1e-12:
            return False
        _d, dh = F._dot_range(B[u], B[v], e)
        return dh > -1.0 + 1e-12

    out = []
    capped = [False]

    def dfs(path, used):
        if len(out) >= cap:
            capped[0] = True
            return
        u = path[-1]
        if linkok(u, N) and (len(path) >= 2 or kind == 'I'):
            out.append(tuple(path) + (N,))
        if len(path) >= 5:
            return
        for v in mids:
            if v in used or v == N:
                continue
            if linkok(u, v):
                dfs(path + [v], used | {v})
    dfs([Q], {Q})
    return out, capped[0]


def l3_count(f, cap=20000):
    """(product of per-slot chain counts, sign-consistent fraction estimate)."""
    tot = 1
    capped = False
    per = {}
    for s in f.slots():
        ch, cp = chains(f, s, cap)
        capped = capped or cp
        per[s] = len(ch)
        tot *= max(len(ch), 0)
        if tot == 0:
            break
    return tot, per, capped


def sign_consistent_fraction(f, rng, ntry=40, cap=4000):
    """fraction of random full chain systems that are sign-consistent."""
    ch = {}
    for s in f.slots():
        c, _ = chains(f, s, cap)
        if not c:
            return 0.0, 0
        ch[s] = c
    ok = 0
    for _ in range(ntry):
        for s in f.slots():
            f.column[s] = rng.choice(ch[s])
        good, _sig, _conf = F.sign_consistency(f)
        ok += 1 if good else 0
    return ok / float(ntry), ntry


# ============================================================ R6 realisability
def _hbounds(tlo, thi):
    """half-extent (cos t + sin t)/2 range over [tlo, thi] subset [0,45deg]."""
    f = lambda t: 0.5 * (math.cos(t) + math.sin(t))
    return min(f(tlo), f(thi)), max(f(tlo), f(thi), f(min(max(math.pi / 4, tlo), thi)))


def build_rows(f, bins, s_lo=S_LO, s_hi=S_HI):
    """returns (A_ub, b_ub, bounds) in variables [x0,y0,...,x10,y10,s,t]."""
    n = f.n
    nv = 2 * n + 1
    A, b, fam = [], [], []

    def row(coef, rhs, kind):
        r = np.zeros(nv + 1)
        for j, v in coef.items():
            r[j] += v
        r[nv] = 1.0                       # margin variable
        A.append(r)
        b.append(rhs)
        fam.append(kind)

    X = lambda i: 2 * i
    Y = lambda i: 2 * i + 1
    SS = 2 * n
    for i in range(n):
        tlo, thi = bins[i]
        hlo, hhi = _hbounds(tlo, thi)
        # containment
        row({X(i): -1.0}, -hlo, 'contain')
        row({Y(i): -1.0}, -hlo, 'contain')
        row({X(i): 1.0, SS: -1.0}, -hlo, 'contain')
        row({Y(i): 1.0, SS: -1.0}, -hlo, 'contain')
        m = f.mask[i]
        if 'L' in m:
            row({X(i): 1.0}, hhi, 'wall')
            row({X(i): -1.0}, -hlo, 'wall')
        if 'B' in m:
            row({Y(i): 1.0}, hhi, 'wall')
            row({Y(i): -1.0}, -hlo, 'wall')
        if 'R' in m:
            row({X(i): -1.0, SS: 1.0}, hhi, 'wall')
            row({X(i): 1.0, SS: -1.0}, -hlo, 'wall')
        if 'T' in m:
            row({Y(i): -1.0, SS: 1.0}, hhi, 'wall')
            row({Y(i): 1.0, SS: -1.0}, -hlo, 'wall')
        h = f.home[i]
        if h is not None:
            # corner-frame coordinates: u = x or s-x ; v = y or s-y
            sx = 1 if F.VW[h] == 'L' else -1
            sy = 1 if F.HW[h] == 'B' else -1
            def uco(k):
                return ({X(i): 1.0} if sx > 0 else {X(i): -1.0, SS: 1.0}) if k == 'u' \
                    else ({Y(i): 1.0} if sy > 0 else {Y(i): -1.0, SS: 1.0})
            U, V = uco('u'), uco('v')
            row(U, 1.0 + H2, 'intrude')
            row(V, 1.0 + H2, 'intrude')
            cc = defaultdict(float)
            for d in (U, V):
                for j, v in d.items():
                    cc[j] += v
            row(dict(cc), 3.0, 'intrude')
            # type rows (Lemma K argmin side) in the corner frame
            tau = f.tau[i]
            ctlo, cthi = math.cos(tlo), math.cos(thi)
            d = defaultdict(float)
            for j, v in V.items():
                d[j] += v
            for j, v in U.items():
                d[j] -= v
            if tau == 'X':
                row(dict(d), (0.0 if tlo <= 1e-12 else -cthi), 'type')
            elif tau == 'Y':
                row({j: -v for j, v in d.items()},
                    (0.0 if tlo <= 1e-12 else -cthi), 'type')
            else:
                row(dict(d), ctlo, 'type')
                row({j: -v for j, v in d.items()}, ctlo, 'type')
    # links
    for s_, col in f.column.items():
        e = f.edir(s_)
        for M, N in zip(col[:-1], col[1:]):
            for (ux, uy) in DIRS8:
                row({X(N): ux, Y(N): uy, X(M): -ux, Y(M): -uy}, SQRT2, 'link')
            row({X(N): -float(e[0]), Y(N): -float(e[1]),
                 X(M): float(e[0]), Y(M): float(e[1])}, 1.0, 'press')
    bounds = [(0.0, s_hi)] * (2 * n) + [(s_lo, s_hi), (-10.0, 1.0)]
    return np.array(A), np.array(b), bounds, fam


def lp_margin(f, bins, s_lo=S_LO, s_hi=S_HI):
    A, b, bounds, fam = build_rows(f, bins, s_lo, s_hi)
    c = np.zeros(A.shape[1])
    c[-1] = -1.0
    r = linprog(c, A_ub=A, b_ub=b, bounds=bounds, method='highs')
    if not r.success:
        return -1e9, len(b)
    return float(-r.fun), len(b)


def realisable(f, s_lo=S_LO, s_hi=S_HI, nbin=1):
    """one-shot R6 triage with tilt bins = nbin uniform bins on [0,45deg] for
    every square (nbin=1 -> the single bin [0,45])."""
    edges = [k * (math.pi / 4) / nbin for k in range(nbin + 1)]
    best = -1e9
    for combo in ([0] * 11,) if nbin == 1 else itertools.product(range(nbin), repeat=1):
        bins = [(edges[0], edges[-1])] * 11
        m, nr = lp_margin(f, bins, s_lo, s_hi)
        best = max(best, m)
    return best > -KILL_TOL, best


def bnb(f, s_lo=S_LO, s_hi=S_HI, box_cap=20000, time_cap=600.0, min_w=1e-3):
    """T3 pilot: bisect tilt bins until every leaf is LP-infeasible (CLOSED) or
    the caps are hit (OPEN).  Cost measurement only, no certificate."""
    t0 = time.time()
    root = [(0.0, math.pi / 4)] * f.n
    stack = [root]
    boxes = 0
    killed = 0
    depth_closed = 0
    while stack:
        if boxes >= box_cap or time.time() - t0 > time_cap:
            return {'verdict': 'OPEN', 'boxes': boxes, 'killed': killed,
                    'seconds': time.time() - t0, 'depth': depth_closed}
        bins = stack.pop()
        boxes += 1
        m, _nr = lp_margin(f, bins, s_lo, s_hi)
        if m < -KILL_TOL:
            killed += 1
            continue
        j = max(range(f.n), key=lambda k: bins[k][1] - bins[k][0])
        lo, hi = bins[j]
        if hi - lo < min_w:
            return {'verdict': 'OPEN', 'boxes': boxes, 'killed': killed,
                    'seconds': time.time() - t0, 'depth': depth_closed,
                    'reason': 'bin_floor'}
        mid = 0.5 * (lo + hi)
        a1 = list(bins); a1[j] = (lo, mid)
        a2 = list(bins); a2[j] = (mid, hi)
        stack.append(a1)
        stack.append(a2)
        depth_closed = max(depth_closed, int(round(math.log2(
            (math.pi / 4) / max(mid - lo, 1e-12)))))
    return {'verdict': 'CLOSED', 'boxes': boxes, 'killed': killed,
            'seconds': time.time() - t0, 'depth': depth_closed}


# ------------------------------------------------------------ corner sharing
def corner_sharing(f):
    """which corner pairs share a column member; #free squares that are middles."""
    mem = defaultdict(set)
    for s, col in f.column.items():
        c = f.home[s[0]]
        for v in col:
            mem[v].add(c)
    pairs = set()
    for v, cs in mem.items():
        for a, b in itertools.combinations(sorted(cs), 2):
            pairs.add((a, b))
    mids = set()
    for s, col in f.column.items():
        for v in col[1:-1]:
            mids.add(v)
    nfree_mid = sum(1 for v in mids if f.home[v] is None)
    return {'shared_pairs': sorted(pairs), 'n_shared_pairs': len(pairs),
            'n_free_middles': nfree_mid,
            'n_squares_in_2plus_corners': sum(1 for v, cs in mem.items()
                                              if len(cs) >= 2)}
