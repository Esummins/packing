"""A85 chore `cases85.py` -- the THREE CORNER-CROWD CASES and the 21 four-corner patterns.

PI direction (A85, 2026-09-04): the corner-crowd cases have very different REACH, which
turns "which four-corner patterns are feasible" into a quantitative question.

Task 1  classify each of the 7 044 realisable pair boxes (realise85.pairs.json) by case,
        using SOUND box/atom bounds only:
          JAM    one member's tilt cell contains 0 (mod 90) AND that member can sit within
                 g <= G_JAM = 0.1 of the slot, AND the partner's tilt cell reaches within
                 JAM-0's bound arcsin(g) (tilt_floor_k0.md Lemma JAM-0);
          BLOCK  the two tilt cells overlap mod 90 (same grain) AND the pair can be
                 edge-to-edge (|D.n| = 1 for a grain normal n, |D.t| <= 1);
          WEDGE  both tilt cells lie entirely >= TH_WEDGE = 10 deg from an axis;
          OTHER  none of the above.
        A pair is a CANDIDATE for a case if SOME surviving atom-pair of the pair satisfies
        the case predicate (over-inclusive = sound).  The reported PARTITION is by the
        priority JAM > BLOCK > WEDGE > OTHER.  Reach/depth maxima per case are taken over
        CANDIDATES (a superset of the partition class), so R_case is a sound upper bound
        for every pair assigned to that case.

Task 2  the 21 D4-classes of case assignments to the four corners; (a) touchability,
        (b) free-square demand of JAM corners, (c) anchoring supply.

Task 3  sanity: Trump's TL 2-crowd; the four k0dir87 exact-K0_BLOCKED polished endpoints.

One process, OMP_NUM_THREADS=1.  Writes only attempts/A85-k0-route/{results,notes}/cases85.*
"""
from __future__ import annotations

import os
for _v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
           'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ[_v] = '1'

import itertools
import json
import math
import sys
import time
from decimal import Decimal, getcontext

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, '..'))
ATT = os.path.abspath(os.path.join(BASE, '..'))
sys.path.insert(0, HERE)

import blas1                                                   # noqa: F401,E402
import numpy as np                                             # noqa: E402
from caselp import Box                                         # noqa: E402
import realise85 as R85                                        # noqa: E402
import t2b_reach as TB                                         # noqa: E402  (via realise85)

RES = os.path.join(BASE, 'results')
NOTES = os.path.join(BASE, 'notes')
OUT = os.path.join(RES, 'cases85.json')
OUT_PAIRS = os.path.join(RES, 'cases85.pairs.jsonl')

# ---------------------------------------------------------------- parameters
S_LO, S0 = 3.82, 3.877084
G_JAM = 0.1                     # JAM-0's g <= 0.1 pocket (tilt_floor_k0.md 5.1)
TOL_AX = 1e-9                   # "tilt cell contains 0 or 90"
TH_WEDGE = 10.0                 # WEDGE: both tilt cells >= 10 deg from axis
TOL_GRAIN = 0.0                 # BLOCK: grain cells must overlap mod 90 (closed overlap)
CHUNK = 400
SQRT2 = math.sqrt(2.0)


def hmax_deg(t0, t1):
    """max of h(th) = (cos+sin)/2 over [t0,t1] degrees."""
    if t0 <= 45.0 <= t1:
        return SQRT2 / 2.0
    a, b = math.radians(t0), math.radians(t1)
    return max((math.cos(a) + math.sin(a)) / 2.0, (math.cos(b) + math.sin(b)) / 2.0)


def tilt_iv(t0, t1):
    """[min tilt, max tilt] over theta in [t0,t1] subset [0,90]; tilt = min(th, 90-th)."""
    f = lambda t: min(t, 90.0 - t)
    lo = min(f(t0), f(t1))
    hi = 45.0 if (t0 <= 45.0 <= t1) else max(f(t0), f(t1))
    return lo, hi


# ---------------------------------------------------------------- atoms (+ depth)
def atoms_with_depth(b):
    """realise85.box_atoms, but carrying the per-atom sound depth upper bound."""
    T = R85.cell_table(b)
    per = max(1, int(round(R85.ATOM_DEG / R85.CELL_DEG)))
    ng = int(math.ceil(T['n'] / float(per)))
    if ng > R85.NA_MAX:
        per = int(math.ceil(T['n'] / float(R85.NA_MAX)))
        ng = int(math.ceil(T['n'] / float(per)))
    at = []
    for g in range(ng):
        sl = slice(g * per, min((g + 1) * per, T['n']))
        m = T['alive'][sl]
        if not m.any():
            continue
        t0 = float(T['lo'][sl][m].min())
        t1 = float(T['hi'][sl][m].max())
        x0 = float(T['Xlb'][sl][m].min())
        x1 = min(b.x1, float(T['capx'][sl][m].max()))
        y0 = float(T['Ylb'][sl][m].min())
        y1 = min(b.y1, float(T['capy'][sl][m].max()))
        if x1 < x0 - 1e-15 or y1 < y0 - 1e-15:
            continue
        d = float(T['depth_ub'][sl][m].max())
        at.append((t0, t1, x0, x1, y0, y1, d))
    return at


def build_atoms():
    _R, _V, rows, boxes = TB.load_boxes()
    A = [atoms_with_depth(b) for b in boxes]
    return boxes, A


# ---------------------------------------------------------------- case predicates
def atom_props(a):
    t0, t1, x0, x1, y0, y1, d = a
    tlo, thi = tilt_iv(t0, t1)
    return dict(t0=t0, t1=t1, x0=x0, x1=x1, y0=y0, y1=y1, d=d, tlo=tlo, thi=thi,
                axis=(tlo <= TOL_AX),
                g_lo=max(x0, y0) - 0.5, g_hi=max(x1, y1) - 0.5,
                reach=max(x1, y1) + hmax_deg(t0, t1),
                X0=x1 + hmax_deg(t0, t1), Y0=y1 + hmax_deg(t0, t1))


def jam_ok(pa, pb, with_depth=False):
    """pa is the axis member.  Sound: EXISTS a pose pair meeting the JAM description."""
    if not pa['axis'] or pa['g_lo'] > G_JAM:
        return False
    g = min(G_JAM, max(pa['g_hi'], 0.0))
    if g < 0.0:
        return False
    if pb['tlo'] > math.degrees(math.asin(min(1.0, g))) + 1e-12:
        return False
    if with_depth and pb['d'] > g * g / math.sqrt(1.0 - g * g) + 1e-12:
        return False       # JAM-0's depth clause on the partner
    return True


def wedge_ok(pa, pb):
    return pa['tlo'] >= TH_WEDGE and pb['tlo'] >= TH_WEDGE


def _grain_overlaps(pa, pb):
    """theta cells overlap mod 90 -> list of common-grain [lo,hi] intervals (in a's frame)."""
    out = []
    for sh in (-90.0, 0.0, 90.0):
        lo = max(pa['t0'], pb['t0'] + sh)
        hi = min(pa['t1'], pb['t1'] + sh)
        if lo <= hi + TOL_GRAIN:
            out.append((lo, min(hi, max(lo, hi))))
    return out


def _iv_mul(a, b):
    p = (a[0] * b[0], a[0] * b[1], a[1] * b[0], a[1] * b[1])
    return (min(p), max(p))


def _cos_iv(lo, hi):
    """interval of cos over [lo,hi] radians (0 <= lo <= hi <= pi/2 here)."""
    return (math.cos(hi) - 1e-15, math.cos(lo) + 1e-15)


def _sin_iv(lo, hi):
    return (math.sin(lo) - 1e-15, math.sin(hi) + 1e-15)


def block_ok(pa, pb):
    """same grain AND edge-to-edge reachable: |D.n| = 1 for a grain normal, |D.t| <= 1."""
    gs = _grain_overlaps(pa, pb)
    if not gs:
        return False
    dx = (pb['x0'] - pa['x1'], pb['x1'] - pa['x0'])
    dy = (pb['y0'] - pa['y1'], pb['y1'] - pa['y0'])
    for (glo, ghi) in gs:
        lo, hi = math.radians(max(0.0, glo)), math.radians(min(90.0, ghi))
        if hi < lo:
            continue
        C, S = _cos_iv(lo, hi), _sin_iv(lo, hi)
        # n1 = (cos, sin), t1 = (-sin, cos)
        p1 = tuple(map(sum, zip(_iv_mul(dx, C), _iv_mul(dy, S))))
        q1 = tuple(map(sum, zip(_iv_mul(dx, (-S[1], -S[0])), _iv_mul(dy, C))))
        for (nn, tt) in ((p1, q1), (q1, p1)):
            if (nn[0] <= 1.0 <= nn[1] or nn[0] <= -1.0 <= nn[1]) and \
               (tt[0] <= 1.0 and tt[1] >= -1.0):
                return True
    return False


# ---------------------------------------------------------------- pair pass
def classify_pairs(boxes, A, pairs):
    NA = max(1, max(len(a) for a in A))
    P = [[atom_props(a) for a in A[k]] for k in range(len(A))]
    n = len(pairs)
    cls = np.zeros((n, 5), bool)          # JAM, BLOCK, WEDGE, OTHER, JAM+depth clause
    X0 = np.zeros(n)
    Y0 = np.zeros(n)
    RCH = np.zeros(n)
    DMAX = np.zeros(n)
    DMIN = np.zeros(n)
    nAP = np.zeros(n, np.int64)
    # per-case extremes restricted to the atom pairs that REALISE the case
    cX0 = np.zeros((n, 5))
    cY0 = np.zeros((n, 5))
    cR = np.zeros((n, 5))
    cD = np.zeros((n, 5))
    cd = np.full((n, 5), np.nan)
    # flags: 0 some axis member, 1 axis member with g<=G_JAM, 2 grain overlap possible,
    #        3 both tilt cells >= TH_WEDGE
    FL = np.zeros((n, 4), bool)
    I = np.array([p[0] for p in pairs])
    J = np.array([p[1] for p in pairs])
    A6 = [[a[:6] for a in A[k]] for k in range(len(A))]
    t0 = time.time()
    for s in range(0, n, CHUNK):
        e = min(s + CHUNK, n)
        Ai = R85.stack(A6, I[s:e], NA)
        Aj = R85.stack(A6, J[s:e], NA)
        g = R85.gap_ub(Ai, Aj)
        ok = (g >= 0.0) & Ai['ok'][:, :, None] & Aj['ok'][:, None, :]
        for r in range(e - s):
            k = s + r
            ii, jj = I[k], J[k]
            aa, bb = np.nonzero(ok[r])
            nAP[k] = len(aa)
            if len(aa) == 0:
                continue
            hit = [False] * 5
            x0m = y0m = rm = dM = 0.0
            dm = 1e9
            for u, v in zip(aa, bb):
                pa, pb = P[ii][u], P[jj][v]
                w = [jam_ok(pa, pb) or jam_ok(pb, pa),
                     block_ok(pa, pb),
                     wedge_ok(pa, pb),
                     False,
                     jam_ok(pa, pb, True) or jam_ok(pb, pa, True)]
                w[3] = not (w[0] or w[1] or w[2])
                X_ = max(pa['X0'], pb['X0'])
                Y_ = max(pa['Y0'], pb['Y0'])
                R_ = max(pa['reach'], pb['reach'])
                D_ = max(pa['d'], pb['d'])
                d_ = max(min(pa['d'], pb['d']), 0.0)
                for c in range(5):
                    if w[c]:
                        hit[c] = True
                        cX0[k, c] = max(cX0[k, c], X_)
                        cY0[k, c] = max(cY0[k, c], Y_)
                        cR[k, c] = max(cR[k, c], R_)
                        cD[k, c] = max(cD[k, c], D_)
                        cd[k, c] = d_ if math.isnan(cd[k, c]) else min(cd[k, c], d_)
                FL[k, 0] |= (pa['axis'] or pb['axis'])
                FL[k, 1] |= ((pa['axis'] and pa['g_lo'] <= G_JAM) or
                             (pb['axis'] and pb['g_lo'] <= G_JAM))
                FL[k, 2] |= bool(_grain_overlaps(pa, pb))
                FL[k, 3] |= (min(pa['tlo'], pb['tlo']) >= TH_WEDGE)
                x0m = max(x0m, X_)
                y0m = max(y0m, Y_)
                rm = max(rm, R_)
                dM = max(dM, D_)
                dm = min(dm, d_)
            cls[k] = hit
            X0[k], Y0[k], RCH[k], DMAX[k], DMIN[k] = x0m, y0m, rm, dM, dm
        if (s // CHUNK) % 5 == 0:
            print('  pairs %d/%d  %.0fs' % (e, n, time.time() - t0), flush=True)
    return dict(cls=cls, X0=X0, Y0=Y0, RCH=RCH, DMAX=DMAX, DMIN=DMIN, nAP=nAP,
                cX0=cX0, cY0=cY0, cR=cR, cD=cD, cd=cd, FL=FL, secs=time.time() - t0)


CASES = ['JAM', 'BLOCK', 'WEDGE', 'OTHER', 'JAM_depth']
REDGES = [1.0, 1.2, 1.4, 1.6, 1.8, 1.91, 2.0, 2.2, 2.42]
DEDGES = [0.0, 0.01, 0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1.01]


def hist_of(v, edges=None):
    edges = edges or REDGES
    v = np.asarray(v, float)
    v = v[~np.isnan(v)]
    return {('[%g,%g)' % (edges[k], edges[k + 1])):
            int(((v >= edges[k]) & (v < edges[k + 1])).sum())
            for k in range(len(edges) - 1)}


def partition(cls):
    """priority JAM > BLOCK > WEDGE > OTHER."""
    lab = np.full(cls.shape[0], 3, np.int8)
    for c in (2, 1, 0):
        lab[cls[:, c]] = c
    return lab


# ---------------------------------------------------------------- patterns
D4 = []
for r in range(4):
    D4.append(tuple((i + r) % 4 for i in range(4)))            # rotations
for r in range(4):
    D4.append(tuple((r - i) % 4 for i in range(4)))            # reflections
# corners in cyclic order BL(0) BR(1) TR(2) TL(3)
ADJ = [(0, 1), (1, 2), (2, 3), (3, 0)]
OPP = [(0, 2), (1, 3)]


def canon(a):
    return min(tuple(a[p[i]] for i in range(4)) for p in D4)


def patterns3():
    seen = {}
    for a in itertools.product(range(3), repeat=4):
        c = canon(a)
        seen.setdefault(c, []).append(a)
    return seen


def analyse_pattern(a, Rc, s=S_LO, jam_locker=1):
    """a = (case index per corner) in cyclic order BL,BR,TR,TL."""
    R = [Rc[c] for c in a]
    touch = {}
    for (i, j) in ADJ + OPP:
        touch[(i, j)] = bool(R[i] + R[j] >= s)
    near = {}                       # within one free-square hop (diameter sqrt2)
    for (i, j) in ADJ + OPP:
        near[(i, j)] = bool(R[i] + R[j] + SQRT2 >= s)
    unt = []
    for i in range(4):
        if not any(touch[k] for k in touch if i in k):
            unt.append(i)
    njam = sum(1 for c in a if c == 0)
    # (b) free-square demand of JAM corners
    ok_b = (njam * jam_locker) <= 3
    # (c) anchoring supply: corners needing >=1 adjacent free square = JAM corners
    #     (external locker) union un-touchable corners (anchoring column's 2nd square).
    need = sorted(set(unt) | set(i for i in range(4) if a[i] == 0))
    dem = min_free_squares(need, near)
    ok_c = dem <= 3
    return dict(cases=[CASES[c] for c in a], reach=R, touch_adj=[touch[k] for k in ADJ],
                touch_opp=[touch[k] for k in OPP], untouchable=unt, n_jam=njam,
                need_free_at=need, free_demand=dem, ok_b=ok_b, ok_c=ok_c,
                survives=bool(ok_b and ok_c))


def min_free_squares(need, near):
    """minimum number of free squares covering `need`; one free square serves at most 2
    corners and only if their crowds are within sqrt2 (a unit square has diameter sqrt2)."""
    if not need:
        return 0
    best = len(need)
    for k in range(len(need)):
        for l in range(k + 1, len(need)):
            i, j = need[k], need[l]
            key = (min(i, j), max(i, j))
            if near.get(key, False):
                rest = [x for x in need if x not in (i, j)]
                best = min(best, 1 + min_free_squares(rest, near))
    return best


# ---------------------------------------------------------------- task 3
def cover_boxes(boxes, cx, cy, thd):
    return [k for k, b in enumerate(boxes)
            if b.x0 - 1e-9 <= cx <= b.x1 + 1e-9 and b.y0 - 1e-9 <= cy <= b.y1 + 1e-9
            and b.th0 - 1e-7 <= thd <= b.th1 + 1e-7]


def classify_boxpair(boxes, A, i, j):
    """classify one (i,j) box pair directly (used for task 3)."""
    NA = max(1, max(len(A[i]), len(A[j]), 1))
    A6 = {i: [a[:6] for a in A[i]], j: [a[:6] for a in A[j]]}
    Z = R85.stack([A6[i], A6[j]], [0, 1], NA)
    g = R85.gap_ub({k: v[0:1] for k, v in Z.items() if k != 'ok'},
                   {k: v[1:2] for k, v in Z.items() if k != 'ok'})
    ok = (g[0] >= 0.0) & Z['ok'][0][:, None] & Z['ok'][1][None, :]
    Pi = [atom_props(a) for a in A[i]]
    Pj = [atom_props(a) for a in A[j]]
    cj = cb = cw = False
    rm = 0.0
    dM = 0.0
    aa, bb = np.nonzero(ok)
    for u, v in zip(aa, bb):
        pa, pb = Pi[u], Pj[v]
        cj |= (jam_ok(pa, pb) or jam_ok(pb, pa))
        cb |= block_ok(pa, pb)
        cw |= wedge_ok(pa, pb)
        rm = max(rm, pa['reach'], pb['reach'])
        dM = max(dM, pa['d'], pb['d'])
    lab = 'JAM' if cj else ('BLOCK' if cb else ('WEDGE' if cw else 'OTHER'))
    return dict(i=int(i), j=int(j), n_atom_pairs=int(len(aa)),
                JAM=bool(cj), BLOCK=bool(cb), WEDGE=bool(cw), label=lab,
                reach_ub=rm, depth_ub=dM)


FRAME = {'BL': lambda x, y, th, s: (x, y, th),
         'BR': lambda x, y, th, s: (s - x, y, (90.0 - th) % 90.0),
         'TR': lambda x, y, th, s: (s - x, s - y, th % 90.0),
         'TL': lambda x, y, th, s: (x, s - y, (90.0 - th) % 90.0)}


def sq_verts(cx, cy, th):
    c, sn = math.cos(th), math.sin(th)
    return [(cx + c * u - sn * v, cy + sn * u + c * v)
            for (u, v) in ((-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5))]


def fmm(V):
    best = min(max(x, y) for x, y in V)
    for k in range(4):
        px, py = V[k]
        qx, qy = V[(k + 1) % 4]
        dx, dy = qx - px, qy - py
        if abs(dx - dy) < 1e-300:
            continue
        t = (py - px) / (dx - dy)
        if 0.0 <= t <= 1.0:
            best = min(best, px + t * dx)
    return best


def corners_of_packing(z, boxes, A, tag):
    """z = [(cx,cy,th)*11, s] (Fraction strings) -> per-corner crowd, BL boxes, case."""
    from fractions import Fraction as Fr
    zz = [float(Fr(v)) if isinstance(v, str) else float(v) for v in z]
    assert len(zz) == 34
    s = zz[33]
    sq = [(zz[3 * i], zz[3 * i + 1], zz[3 * i + 2]) for i in range(11)]
    out = []
    for cn, F in FRAME.items():
        mem = []
        for i, (cx, cy, th) in enumerate(sq):
            bx, by, bt = F(cx, cy, math.degrees(th) % 90.0, s)
            V = sq_verts(bx, by, math.radians(bt))
            f = fmm(V)
            if f < 1.0 - 1e-9:
                mem.append(dict(sq=i, cx=bx, cy=by, th_deg=bt, depth=1.0 - f,
                                tilt_deg=min(bt, 90.0 - bt),
                                boxes=cover_boxes(boxes, bx, by, bt)))
        rec = dict(tag=tag, corner=cn, s=s, n_intruders=len(mem), members=mem)
        if len(mem) == 2 and mem[0]['boxes'] and mem[1]['boxes']:
            cc = []
            for bi in mem[0]['boxes']:
                for bj in mem[1]['boxes']:
                    if bi == bj or not A[bi] or not A[bj]:
                        continue
                    cc.append(classify_boxpair(boxes, A, min(bi, bj), max(bi, bj)))
            rec['box_pairs'] = cc
            labs = set(c['label'] for c in cc)
            rec['label'] = ('JAM' if any(c['JAM'] for c in cc) else
                            'BLOCK' if any(c['BLOCK'] for c in cc) else
                            'WEDGE' if any(c['WEDGE'] for c in cc) else
                            ('OTHER' if cc else None))
            rec['labels_seen'] = sorted(labs)
        else:
            rec['label'] = None
        out.append(rec)
    return out


def trump_TL(boxes, A):
    getcontext().prec = 200
    d = json.load(open(os.path.join(ATT, 'A03-upper-reconstruct', 'trump11_exact.json')))
    s = float(Decimal(d['s']))
    si = float(Decimal(d['sin_theta']))
    rec = []
    bl = []
    for i in (4, 6):
        sqd = d['squares'][i]
        cx, cy = float(Decimal(sqd['cx'])), float(Decimal(sqd['cy']))
        thd = 0.0 if i == 4 else math.degrees(math.asin(si))
        bx, by, bt = FRAME['TL'](cx, cy, thd, s)
        V = sq_verts(bx, by, math.radians(bt))
        f = fmm(V)
        hits = cover_boxes(boxes, bx, by, bt)
        rec.append(dict(square=i, cx_BL=bx, cy_BL=by, th_BL_deg=bt,
                        tilt_deg=min(bt, 90.0 - bt), depth=1.0 - f, boxes=hits))
        bl.append(hits)
    cc = []
    for bi in bl[0]:
        for bj in bl[1]:
            if bi == bj:
                continue
            cc.append(classify_boxpair(boxes, A, min(bi, bj), max(bi, bj)))
    lab = ('JAM' if any(c['JAM'] for c in cc) else 'BLOCK' if any(c['BLOCK'] for c in cc)
           else 'WEDGE' if any(c['WEDGE'] for c in cc) else 'OTHER')
    return dict(squares=rec, box_pairs=cc, label=lab)


# ---------------------------------------------------------------- main
def main():
    t00 = time.time()
    res = dict(attempt='A85 cases85 -- corner-crowd cases and the 21 four-corner patterns',
               params=dict(G_JAM=G_JAM, TH_WEDGE=TH_WEDGE, TOL_AX=TOL_AX,
                           TOL_GRAIN=TOL_GRAIN, s_window=[S_LO, S0]))
    print('building atoms ...', flush=True)
    boxes, A = build_atoms()
    res['n_boxes'] = len(boxes)
    res['n_realisable_boxes'] = int(sum(1 for a in A if a))
    pairs = json.load(open(os.path.join(RES, 'realise85.pairs.json')))['surviving']
    pairs = [(int(i), int(j)) for (i, j) in pairs]
    res['n_pairs'] = len(pairs)
    print('classifying %d pairs ...' % len(pairs), flush=True)
    C = classify_pairs(boxes, A, pairs)
    cls, lab = C['cls'], partition(C['cls'])
    res['candidate_counts'] = {CASES[c]: int(cls[:, c].sum()) for c in range(5)}
    res['overlap_counts'] = {}
    for c1 in range(3):
        for c2 in range(c1 + 1, 3):
            res['overlap_counts']['%s&%s' % (CASES[c1], CASES[c2])] = \
                int((cls[:, c1] & cls[:, c2]).sum())
    res['overlap_counts']['JAM&BLOCK&WEDGE'] = int((cls[:, 0] & cls[:, 1] & cls[:, 2]).sum())
    res['partition_counts'] = {CASES[c]: int((lab == c).sum()) for c in range(4)}

    # per-case reach / depth over CANDIDATES, restricted to the atom pairs REALISING
    # the case (sound: if a corner is in case c, its poses lie in such an atom pair)
    tab = {}
    for c in range(5):
        m = cls[:, c]
        if not m.any():
            tab[CASES[c]] = None
            continue
        def q(v, mm=m):
            w = np.sort(v[mm])
            w = w[~np.isnan(w)]
            return dict(min=float(w[0]), median=float(w[len(w) // 2]),
                        p90=float(w[int(0.9 * (len(w) - 1))]), max=float(w[-1]))
        tab[CASES[c]] = dict(
            n_candidates=int(m.sum()),
            X0=q(C['cX0'][:, c]), Y0=q(C['cY0'][:, c]), reach=q(C['cR'][:, c]),
            depth_max_of_pair=q(C['cD'][:, c]), depth_min_of_pair=q(C['cd'][:, c]),
            reach_unrestricted_max=float(C['RCH'][m].max()),
            X0_hist=hist_of(C['cX0'][m, c]), Y0_hist=hist_of(C['cY0'][m, c]),
            depth_hist=hist_of(C['cD'][m, c], DEDGES))
    res['per_case'] = tab
    tabp = {}
    for c in range(4):
        m = (lab == c)
        if not m.any():
            tabp[CASES[c]] = None
            continue
        tabp[CASES[c]] = dict(n=int(m.sum()), reach_max=float(C['cR'][m, c].max()),
                              X0_max=float(C['cX0'][m, c].max()),
                              Y0_max=float(C['cY0'][m, c].max()),
                              depth_max=float(C['cD'][m, c].max()))
    res['per_case_partition'] = tabp
    mo = (lab == 3)
    FL = C['FL']
    res['OTHER_subcensus'] = dict(
        n=int(mo.sum()),
        axis_member_present=int((mo & FL[:, 0]).sum()),
        axis_member_deep_offset_only=int((mo & FL[:, 0] & ~FL[:, 1]).sum()),
        axis_member_g_le_0p1_but_partner_too_tilted=int((mo & FL[:, 1]).sum()),
        grain_overlap_possible=int((mo & FL[:, 2]).sum()),
        no_axis_no_grain=int((mo & ~FL[:, 0] & ~FL[:, 2]).sum()),
        reach_max=float(C['cR'][mo, 3].max()),
        note='OTHER = neither JAM nor BLOCK nor WEDGE; the deep-offset axis-aligned '
             'blocker + tilted partner (case (iii), Trump TL) lives here.')

    with open(OUT_PAIRS, 'w') as f:
        for k, (i, j) in enumerate(pairs):
            f.write(json.dumps(dict(i=i, j=j, label=CASES[int(lab[k])],
                                    JAM=bool(cls[k, 0]), BLOCK=bool(cls[k, 1]),
                                    WEDGE=bool(cls[k, 2]),
                                    JAM_depth=bool(cls[k, 4]),
                                    X0=float(C['cX0'][k, int(lab[k])]),
                                    Y0=float(C['cY0'][k, int(lab[k])]),
                                    reach=float(C['cR'][k, int(lab[k])]),
                                    depth_max=float(C['cD'][k, int(lab[k])]),
                                    depth_min=(None if math.isnan(C['cd'][k, int(lab[k])])
                                               else float(C['cd'][k, int(lab[k])])),
                                    reach_any=float(C['RCH'][k]),
                                    n_atom_pairs=int(C['nAP'][k]))) + '\n')

    # ---------------- task 2
    Rc = [tab[CASES[c]]['reach']['max'] for c in range(3)]
    res['R_case_sound'] = {CASES[c]: Rc[c] for c in range(3)}
    pats = patterns3()
    rows = []
    for c, members in sorted(pats.items()):
        r = analyse_pattern(c, Rc)
        r['canonical'] = [CASES[x] for x in c]
        r['n_labelled'] = len(members)
        rows.append(r)
    res['patterns'] = rows
    res['n_patterns'] = len(rows)
    res['n_surviving_patterns'] = sum(1 for r in rows if r['survives'])
    # observed-locker variant (2 free squares per JAM corner)
    rows2 = [analyse_pattern(c, Rc, jam_locker=2) for c in sorted(pats)]
    res['n_surviving_patterns_locker2'] = sum(1 for r in rows2 if r['survives'])
    res['patterns_locker2'] = [dict(cases=r['cases'], survives=r['survives'],
                                    ok_b=r['ok_b'], ok_c=r['ok_c']) for r in rows2]
    # variant: JAM with JAM-0's depth clause added (tighter R_JAM)
    if tab.get('JAM_depth'):
        Rd = [tab['JAM_depth']['reach']['max'], Rc[1], Rc[2]]
        rows3 = [analyse_pattern(c, Rd) for c in sorted(pats)]
        res['R_case_JAMdepth'] = {CASES[c]: Rd[c] for c in range(3)}
        res['patterns_JAMdepth'] = [dict(cases=r['cases'], survives=r['survives'],
                                         untouchable=r['untouchable'],
                                         free_demand=r['free_demand'],
                                         ok_b=r['ok_b'], ok_c=r['ok_c']) for r in rows3]
        res['n_surviving_patterns_JAMdepth'] = sum(1 for r in rows3 if r['survives'])
    # sensitivity: what R_JAM would make a JAM-JAM adjacency untouchable
    res['touchability_thresholds'] = dict(
        s_lo=S_LO, half_s_lo=S_LO / 2.0,
        JAM_plus_JAM=Rc[0] * 2.0, JAM_plus_BLOCK=Rc[0] + Rc[1],
        JAM_plus_WEDGE=Rc[0] + Rc[2], BLOCK_plus_WEDGE=Rc[1] + Rc[2],
        note='a corner pair can touch only if R_a + R_b >= s; s = 3.82 is the easiest case')

    N = len(pairs)
    ncase = [res['partition_counts'][CASES[c]] for c in range(3)]
    surv = {c for c, _m in pats.items() if analyse_pattern(c, Rc)['survives']}
    surv2 = {c for c, _m in pats.items() if analyse_pattern(c, Rc, jam_locker=2)['survives']}
    numer = numer2 = 0
    for a in itertools.product(range(3), repeat=4):
        w = ncase[a[0]] * ncase[a[1]] * ncase[a[2]] * ncase[a[3]]
        if canon(a) in surv:
            numer += w
        if canon(a) in surv2:
            numer2 += w
    tot3 = sum(ncase) ** 4
    res['box_combination_fraction'] = dict(
        N_pairs=N, n_per_case={CASES[c]: ncase[c] for c in range(3)},
        n_OTHER=res['partition_counts']['OTHER'],
        labelled_4tuples_total=N ** 4,
        labelled_4tuples_in_JBW=tot3,
        labelled_4tuples_surviving=numer,
        labelled_4tuples_surviving_locker2=numer2,
        frac_of_all=numer / float(N ** 4),
        frac_of_all_locker2=numer2 / float(N ** 4),
        frac_of_JBW_only=(numer / float(tot3)) if tot3 else None,
        frac_of_JBW_only_locker2=(numer2 / float(tot3)) if tot3 else None,
        frac_JBW_of_all=tot3 / float(N ** 4),
        a85_attemptable_after_realisability=0.128,
        composed_attemptable=0.128 * numer / float(N ** 4),
        composed_attemptable_locker2=0.128 * numer2 / float(N ** 4),
        note='D4-canonical counts differ from labelled counts by the same Burnside factor '
             'in numerator and denominator, so the fraction is unchanged.')

    # ---------------- task 2b: per-BOX-PAIR (anisotropic) 4-tuple Monte Carlo
    # A corner's own frame fixes which wall its X0 runs along, so a NAMED 4-tuple of box
    # pairs admits the sharper wall-by-wall test.  Cyclic order BL, BR, TR, TL:
    #   bottom  X(BL)+X(BR)   right  Y(BR)+Y(TR)   top  X(TR)+X(TL)   left  Y(TL)+Y(BL)
    #   diagonal BL-TR: X(BL)+X(TR) >= s AND Y(BL)+Y(TR) >= s;  BR-TL likewise.
    print('4-tuple Monte Carlo ...', flush=True)
    rng = np.random.default_rng(20260904)
    NS = 2000000
    Xa = np.array([C['cX0'][k, int(lab[k])] for k in range(N)])
    Ya = np.array([C['cY0'][k, int(lab[k])] for k in range(N)])
    isj = (lab == 0)
    s = S0                       # separation is easiest at the TOP of the window
    tot = dict(n=0, any_untouchable=0, fail_b=0, fail_b2=0, fail_c=0, survive=0,
               survive_locker2=0, in_JBW=0, survive_and_JBW=0)
    BATCH = 250000
    done = 0
    while done < NS:
        n = min(BATCH, NS - done)
        idx = rng.integers(0, N, size=(4, n))
        X = Xa[idx]
        Y = Ya[idx]
        J = isj[idx]
        t = {}
        t[(0, 1)] = X[0] + X[1] >= s
        t[(1, 2)] = Y[1] + Y[2] >= s
        t[(2, 3)] = X[2] + X[3] >= s
        t[(3, 0)] = Y[3] + Y[0] >= s
        t[(0, 2)] = (X[0] + X[2] >= s) & (Y[0] + Y[2] >= s)
        t[(1, 3)] = (X[1] + X[3] >= s) & (Y[1] + Y[3] >= s)
        nr = {}
        nr[(0, 1)] = X[0] + X[1] + SQRT2 >= s
        nr[(1, 2)] = Y[1] + Y[2] + SQRT2 >= s
        nr[(2, 3)] = X[2] + X[3] + SQRT2 >= s
        nr[(3, 0)] = Y[3] + Y[0] + SQRT2 >= s
        nr[(0, 2)] = (X[0] + X[2] + SQRT2 >= s) & (Y[0] + Y[2] + SQRT2 >= s)
        nr[(1, 3)] = (X[1] + X[3] + SQRT2 >= s) & (Y[1] + Y[3] + SQRT2 >= s)
        unt = np.ones((4, n), bool)
        for (i, j), v in t.items():
            unt[i] &= ~v
            unt[j] &= ~v
        need = unt | J
        njam = J.sum(axis=0)
        okb = njam <= 3
        okb2 = njam <= 1
        # free-square demand: cover `need` corners, one free square per corner unless two
        # needing corners are within sqrt2 (then one square may serve both)
        nn = need.sum(axis=0)
        pair_ok = np.zeros(n, np.int8)
        for (i, j) in list(nr):
            pair_ok = np.maximum(pair_ok, (need[i] & need[j] & nr[(i, j)]).astype(np.int8))
        # a sound LOWER bound on the demand: ceil(nn/2) if any needing pair is near,
        # else nn (no sharing possible)
        dem = np.where(pair_ok.astype(bool), (nn + 1) // 2, nn)
        okc = dem <= 3
        inJBW = ((lab[idx] != 3).all(axis=0))
        msurv = okb & okc
        nu = unt.sum(axis=0)
        for v in range(5):
            tot['n_untouchable_%d' % v] = tot.get('n_untouchable_%d' % v, 0) + \
                int((nu == v).sum())
        for v in range(6):
            tot['demand_%d' % v] = tot.get('demand_%d' % v, 0) + int((dem == v).sum())
        tot['n'] += n
        tot['any_untouchable'] += int(unt.any(axis=0).sum())
        tot['fail_b'] += int((~okb).sum())
        tot['fail_b2'] += int((~okb2).sum())
        tot['fail_c'] += int((~okc).sum())
        tot['survive'] += int(msurv.sum())
        tot['survive_locker2'] += int((okb2 & okc).sum())
        tot['in_JBW'] += int(inJBW.sum())
        tot['survive_and_JBW'] += int((msurv & inJBW).sum())
        done += n
    res['four_tuple_MC'] = dict(
        n_samples=tot['n'], s_used=s, seed=20260904,
        frac_any_corner_untouchable=tot['any_untouchable'] / float(tot['n']),
        frac_fail_b_locker1=tot['fail_b'] / float(tot['n']),
        frac_fail_b_locker2=tot['fail_b2'] / float(tot['n']),
        frac_fail_c=tot['fail_c'] / float(tot['n']),
        frac_survive=tot['survive'] / float(tot['n']),
        frac_survive_locker2=tot['survive_locker2'] / float(tot['n']),
        frac_in_JBW=tot['in_JBW'] / float(tot['n']),
        frac_survive_and_JBW=tot['survive_and_JBW'] / float(tot['n']),
        n_untouchable_hist={k: v for k, v in tot.items() if k.startswith('n_untouchable_')},
        free_demand_hist={k: v for k, v in tot.items() if k.startswith('demand_')},
        note='uniform i.i.d. box pair per corner; the D4 quotient does not change a '
             'uniform product fraction.  X/Y are the per-corner-frame extents, so this '
             'is the anisotropic sharpening of the case-level test.')

    # ---------------- task 3
    print('task 3 ...', flush=True)
    res['trump_TL'] = trump_TL(boxes, A)
    stuck = []
    for L in open(os.path.join(ATT, 'A87-drain-flow', 'results', 'k0dir87.polish.jsonl')):
        r = json.loads(L)
        if r.get('exact_K0_BLOCKED') and r.get('z_polished'):
            stuck.append(r)
    sr = []
    for r in stuck:
        cs = corners_of_packing(r['z_polished'], boxes, A, r['tag'])
        labs = [c['label'] for c in cs]
        pat = tuple(sorted(labs)) if all(labs) else None
        cyc = [c['label'] for c in cs]                   # BL, BR, TR, TL (cyclic order)
        can = None
        if all(l in CASES[:3] for l in cyc):
            can = [CASES[x] for x in canon(tuple(CASES.index(l) for l in cyc))]
        sr.append(dict(tag=r['tag'], sigma=r['sigma_polished'],
                       exact_n_block=r['exact_n_block'],
                       corners=[{k: v for k, v in c.items() if k != 'box_pairs'} for c in cs],
                       labels_BL_BR_TR_TL=cyc, multiset=pat, canonical_pattern=can,
                       in_surviving=(bool(canon(tuple(CASES.index(l) for l in cyc)) in surv)
                                     if can else None)))
    res['k0dir87_stuck'] = sr
    res['secs'] = time.time() - t00
    json.dump(res, open(OUT, 'w'), indent=1)
    print('wrote', OUT, '%.0fs' % res['secs'])
    return res


if __name__ == '__main__':
    main()
