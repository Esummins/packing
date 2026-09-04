"""A85 chore `realise85.py` -- make the blocker-pair prune SOUND about REALISABILITY.

A85's level-2 pair prune (corner85.r2) never asked whether a cover box, or a pair of
them, admits an actual placement of unit squares that

  (R1) lies inside the container [0, s]^2   (BL corner frame: the walls x = 0, y = 0
       give c_x >= h(theta), c_y >= h(theta), h(theta) = (cos th + sin th)/2; the far
       walls give c_x + h <= s, c_y + h <= s -- checked, never binding on this cover),
  (R2) MEETS THE OPEN CORNER SLOT (0,1)^2 with certified depth > DEPTH_MIN
       (K0-BLOCKED: a tangency is not a block).  depth = 1 - f_min_max (A89
       t2b_depth), f_min_max(Q) = min over Q of max(x, y) (corner85.f_min_max),
  (R3) pairwise INTERIOR-DISJOINT.

Everything below is a NECESSARY condition, outward-rounded: a box or a pair is
DROPPED only when no placement (resp. placement pair) inside it can satisfy
(R1)-(R3).  Soundness ingredients, all used in the outward direction:

 (a) f_min_max is nondecreasing in c_x and in c_y separately (max(c + q) is
     pointwise nondecreasing, hence so is its min over q) -- A89's part-1 lemma.
     So over a theta-cell the smallest reachable f_min_max sits at the WALL-AWARE
     lower-left corner  X_lb = max(x0, min_cell h),  Y_lb = max(y0, min_cell h).
 (b) f_min_max is (sqrt2/2)-Lipschitz in theta at a fixed centre (the minimiser
     lies on Q, at distance <= circumradius sqrt2/2 from the centre), and
     1-Lipschitz nondecreasing in each centre coordinate.
 (c) EXACT per-cell reach cap.  f_min_max(c_x, c_y, th) < v  iff  Q meets the open
     quadrant (-inf, v)^2, i.e. iff some p in Q(0, c_y, th) has p_x + c_x < v and
     p_y < v.  Hence
         c_x  <  v - min{ p_x : p in Q(0, Y_lb, th_mid), p_y <= v },   v = SLOT_LIM + slack
     with the min taken over the polygon clipped by y <= v (exact, O(1)).  Same for
     c_y.  This is the constraint A85 never had: it caps how FAR from the corner a
     slot-meeting square can sit, which is what kills e.g. two axis-aligned
     blockers at one corner.
 (d) pair test: 4-axis SAT.  Two unit squares are interior-disjoint iff
         gap = max(|D.e1A|, |D.e2A|, |D.e1B|, |D.e2B|) - 1/2 - r  >=  0,
         r = (|cos d| + |sin d|)/2,  d = th_B - th_A,  D = c_B - c_A
     (t2b_reach's closed form).  An INTERVAL UPPER BOUND of gap over a pair of
     realisability-reduced atoms is computed; a pair is dropped iff every atom pair
     has gap_ub < 0 (every placement pair overlaps) -- which subsumes A85's
     max-centre-distance prune.

Stages: `python realise85.py boxes|pairs|gate|all`.
Writes only attempts/A85-k0-route/{results,notes}/realise85.*  One process, OMP=1.
"""
from __future__ import annotations

import os
for _v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
           'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ.setdefault(_v, '1')

import json
import math
import random
import sys
import time
from decimal import Decimal, getcontext
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, '..'))
ATT = os.path.abspath(os.path.join(BASE, '..'))
REPO = os.path.abspath(os.path.join(ATT, '..'))
sys.path.insert(0, HERE)

import blas1                                                   # noqa: F401,E402
import numpy as np                                             # noqa: E402
from caselp import Box                                         # noqa: E402
import corner85 as C85                                         # noqa: E402
import alive84                                                 # noqa: E402
from pinguard import cores_meet                                # noqa: E402
import gate85 as G85                                           # noqa: E402

sys.path.append(os.path.join(ATT, 'A89-tilt-floor', 'code'))
import t2b_reach as TB                                         # noqa: E402  (A89 machinery)

RES = os.path.join(BASE, 'results')
NOTES = os.path.join(BASE, 'notes')
OUT = os.path.join(RES, 'realise85.json')
OUT_BOX = os.path.join(RES, 'realise85.boxes.json')
OUT_PAIR = os.path.join(RES, 'realise85.pairs.json')

S0 = Fr(969271, 250000)
S0F = float(S0)
S_LO = 3.82                     # low end of the window
DEPTH_MIN = 1e-9                # certified depth > 1e-9  =>  f_min_max < 1 - 1e-9
SLOT_LIM = 1.0 - DEPTH_MIN
CELL_DEG = 0.01                 # theta cell for the Lipschitz-slacked per-cell tests
ATOM_DEG = 0.5                  # theta atom for the interval SAT pair test
NA_MAX = 32
LIP_TH = math.sqrt(0.5)         # |d f_min_max / d theta| <= circumradius sqrt2/2
PAD = 1e-12                     # outward float pad
CHUNK = 512
SEED = 20260903
D2_DELTA = 0.10                 # the (hypothetical) d2 cut
CPU_H_LO = 0.47                 # A85 §8.3 measured per decided node (PASS first pass)
CPU_H_HI = 1.1                  # ... with two eps_geo repairs
CPU_H_ATT = 1700.0 / 3600.0     # A85 §7.2's "1700 s per attempt"


def free_commit_mb():
    import ctypes

    class MS(ctypes.Structure):
        _fields_ = [('dwLength', ctypes.c_ulong), ('dwMemoryLoad', ctypes.c_ulong),
                    ('ullTotalPhys', ctypes.c_ulonglong), ('ullAvailPhys', ctypes.c_ulonglong),
                    ('ullTotalPageFile', ctypes.c_ulonglong),
                    ('ullAvailPageFile', ctypes.c_ulonglong),
                    ('ullTotalVirtual', ctypes.c_ulonglong),
                    ('ullAvailVirtual', ctypes.c_ulonglong),
                    ('ullAvailExtendedVirtual', ctypes.c_ulonglong)]
    m = MS()
    m.dwLength = ctypes.sizeof(MS)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return m.ullAvailPageFile / 2.0 ** 20, m.ullAvailPhys / 2.0 ** 20


# ------------------------------------------------------------------ vector geometry
def hval(th):
    return TB.hval(th)


def fmm(cx, cy, th):
    return TB.f_minmax_np(TB.verts_np(np.asarray(cx, float), np.asarray(cy, float),
                                      np.asarray(th, float)))


def _clip_min(A, Bc, c):
    """min of coordinate A over the polygon clipped by  Bc <= c.  (n,4) arrays."""
    best = np.where(Bc <= c[:, None], A, np.inf).min(axis=1)
    for k in range(4):
        a0, b0 = A[:, k], Bc[:, k]
        a1, b1 = A[:, (k + 1) % 4], Bc[:, (k + 1) % 4]
        db = b1 - b0
        ok = (np.abs(db) > 1e-300) & (((b0 <= c) & (b1 >= c)) | ((b0 >= c) & (b1 <= c)))
        s = np.where(ok, (c - b0) / np.where(np.abs(db) > 1e-300, db, 1.0), 0.0)
        best = np.minimum(best, np.where(ok, a0 + s * (a1 - a0), np.inf))
    return best


def cell_table(b):
    """per-theta-cell sound quantities for one cover box."""
    n = max(1, int(math.ceil((b.th1 - b.th0) / CELL_DEG)))
    e = np.linspace(b.th0, b.th1, n + 1)
    lo, hi = e[:-1], e[1:]
    mid = 0.5 * (lo + hi)
    thm = np.radians(mid)
    half = np.radians(hi - lo) / 2.0
    s_th = LIP_TH * half * (1.0 + 1e-12) + 1e-15
    hlo = np.minimum(hval(np.radians(lo)), hval(np.radians(hi)))       # min h over cell
    Xlb = np.maximum(b.x0, hlo)
    Ylb = np.maximum(b.y0, hlo)
    feas = (Xlb <= b.x1 + PAD) & (Ylb <= b.y1 + PAD)                  # quadrant reachable
    f0 = fmm(Xlb, Ylb, thm) - s_th                                    # sound LOWER bound
    alive = feas & (f0 < SLOT_LIM)
    v = SLOT_LIM + s_th
    V = TB.verts_np(np.zeros(n), Ylb, thm)
    capx = v - (_clip_min(V[:, :, 0], V[:, :, 1], v) - PAD)
    V = TB.verts_np(Xlb, np.zeros(n), thm)
    capy = v - (_clip_min(V[:, :, 1], V[:, :, 0], v) - PAD)
    return dict(lo=lo, hi=hi, alive=alive, Xlb=Xlb, Ylb=Ylb, capx=capx, capy=capy,
                depth_ub=1.0 - f0, n=n)


def box_atoms(b, T):
    """-> (list of atoms, depth_ub_wall).  atom = (t0,t1 deg, x0,x1, y0,y1)."""
    per = max(1, int(round(ATOM_DEG / CELL_DEG)))
    ng = int(math.ceil(T['n'] / float(per)))
    if ng > NA_MAX:
        per = int(math.ceil(T['n'] / float(NA_MAX)))
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
        at.append((t0, t1, x0, x1, y0, y1))
    d = T['depth_ub'][T['alive']]
    return at, (float(d.max()) if d.size else None)


# ------------------------------------------------------------------ interval SAT
def imul(alo, ahi, blo, bhi):
    p = (alo * blo, alo * bhi, ahi * blo, ahi * bhi)
    return (np.minimum(np.minimum(p[0], p[1]), np.minimum(p[2], p[3])),
            np.maximum(np.maximum(p[0], p[1]), np.maximum(p[2], p[3])))


def _absub(lo, hi):
    return np.maximum(hi, -lo)


def gap_ub(Ai, Aj):
    """sound UPPER bound of the SAT gap over every placement pair in the two atom
    stacks.  Ai/Aj are dicts of (m, NA) arrays; result (m, NA, NA)."""
    ix0, ix1, iy0, iy1 = (Ai['x0'][:, :, None], Ai['x1'][:, :, None],
                          Ai['y0'][:, :, None], Ai['y1'][:, :, None])
    jx0, jx1, jy0, jy1 = (Aj['x0'][:, None, :], Aj['x1'][:, None, :],
                          Aj['y0'][:, None, :], Aj['y1'][:, None, :])
    dxl, dxh = jx0 - ix1, jx1 - ix0
    dyl, dyh = jy0 - iy1, jy1 - iy0
    best = None
    for S in (Ai, Aj):
        if S is Ai:
            cl, ch = S['cl'][:, :, None], S['ch'][:, :, None]
            sl, sh = S['sl'][:, :, None], S['sh'][:, :, None]
        else:
            cl, ch = S['cl'][:, None, :], S['ch'][:, None, :]
            sl, sh = S['sl'][:, None, :], S['sh'][:, None, :]
        xcl, xch = imul(dxl, dxh, cl, ch)
        xsl, xsh = imul(dxl, dxh, sl, sh)
        ycl, ych = imul(dyl, dyh, cl, ch)
        ysl, ysh = imul(dyl, dyh, sl, sh)
        e1 = _absub(xcl + ysl, xch + ysh)          # | dx cos + dy sin |
        e2 = _absub(-xsh + ycl, -xsl + ych)        # | -dx sin + dy cos |
        m = np.maximum(e1, e2)
        best = m if best is None else np.maximum(best, m)
    dl = Aj['t0'][:, None, :] - Ai['t1'][:, :, None]
    dh = Aj['t1'][:, None, :] - Ai['t0'][:, :, None]
    al, ah = np.abs(dl), np.abs(dh)
    u1 = np.maximum(al, ah)
    u0 = np.where((dl <= 0) & (dh >= 0), 0.0, np.minimum(al, ah))
    r_lb = 0.5 * np.minimum(np.cos(u0) + np.sin(u0), np.cos(u1) + np.sin(u1)) - 1e-15
    return best + PAD - 0.5 - r_lb


def stack(atoms, idx, NA):
    m = len(idx)
    Z = {k: np.zeros((m, NA)) for k in ('x0', 'x1', 'y0', 'y1', 'cl', 'ch', 'sl', 'sh',
                                        't0', 't1')}
    ok = np.zeros((m, NA), bool)
    for r, k in enumerate(idx):
        A = atoms[k]
        for a, (t0, t1, x0, x1, y0, y1) in enumerate(A):
            r0, r1 = math.radians(t0), math.radians(t1)
            Z['x0'][r, a], Z['x1'][r, a] = x0, x1
            Z['y0'][r, a], Z['y1'][r, a] = y0, y1
            Z['t0'][r, a], Z['t1'][r, a] = r0, r1
            Z['cl'][r, a], Z['ch'][r, a] = math.cos(r1) - 1e-15, math.cos(r0) + 1e-15
            Z['sl'][r, a], Z['sh'][r, a] = math.sin(r0) - 1e-15, math.sin(r1) + 1e-15
            ok[r, a] = True
    Z['ok'] = ok
    return Z


# ------------------------------------------------------------------ stage 1
def stage_boxes(verbose=True):
    R, V, rows, boxes = TB.load_boxes()
    n = len(boxes)
    wallcheck = max(b.x1 + C85.h_max_of(b) for b in boxes), \
        max(b.y1 + C85.h_max_of(b) for b in boxes)
    atoms, depth, alive = [], [], []
    t0 = time.time()
    for k, b in enumerate(boxes):
        T = cell_table(b)
        a, d = box_atoms(b, T)
        atoms.append(a)
        depth.append(d)
        alive.append(bool(a))
        if verbose and (k + 1) % 200 == 0:
            print('  boxes %d/%d  %.0fs' % (k + 1, n, time.time() - t0), flush=True)
    na = [len(a) for a in atoms]
    out = dict(n_boxes=n, n_realisable=int(sum(alive)),
               far_wall_max_x_extent=wallcheck[0], far_wall_max_y_extent=wallcheck[1],
               far_wall_binds_at_s_lo=bool(max(wallcheck) > S_LO),
               s_window=[S_LO, S0F], depth_min=DEPTH_MIN,
               cell_deg=CELL_DEG, atom_deg=ATOM_DEG,
               n_atoms_total=int(sum(na)), n_atoms_max=int(max(na)),
               dropped=[k for k in range(n) if not alive[k]],
               depth_ub_wall=[depth[k] for k in range(n)],
               secs=time.time() - t0)
    return boxes, atoms, depth, alive, out


# ------------------------------------------------------------------ stage 2
def stage_pairs(boxes, atoms, alive, verbose=True):
    ppath = os.path.join(RES, 'a85_pairs_BL.json')
    idx_ok, vi, vj = TB.verify_box_index(boxes, ppath)
    pairs = TB.stream_pairs(ppath)
    NA = max(1, max(len(a) for a in atoms))
    keep = np.zeros(len(pairs), bool)
    both_boxes = np.array([alive[i] and alive[j] for (i, j, _a, _b) in pairs])
    todo = np.flatnonzero(both_boxes)
    I = np.array([pairs[k][0] for k in todo])
    J = np.array([pairs[k][1] for k in todo])
    t0 = time.time()
    for s in range(0, len(todo), CHUNK):
        e = min(s + CHUNK, len(todo))
        Ai = stack(atoms, I[s:e], NA)
        Aj = stack(atoms, J[s:e], NA)
        g = gap_ub(Ai, Aj)
        m = Ai['ok'][:, :, None] & Aj['ok'][:, None, :]
        keep[todo[s:e]] = ((g >= 0.0) & m).any(axis=(1, 2))
        if verbose and (s // CHUNK) % 10 == 0:
            print('  pairs %d/%d kept %d  %.0fs'
                  % (e, len(todo), int(keep.sum()), time.time() - t0), flush=True)
    out = dict(box_index_check=idx_ok, first_pair=[vi, vj], n_pairs=len(pairs),
               n_pairs_both_boxes_realisable=int(both_boxes.sum()),
               n_pairs_surviving=int(keep.sum()), secs=time.time() - t0)
    return pairs, keep, out


# ------------------------------------------------------------------ canaries
def canary_axis_aligned(_):
    """two axis-aligned unit squares in the BL quadrant, both meeting the open slot:
    impossible (A89 fact).  Degenerate theta boxes over the whole cover rect."""
    b = Box(0.5, 1.75, 0.5, 1.75, 0.0, 0.0)
    T = cell_table(b)
    at, d = box_atoms(b, T)
    Z = stack([at, at], [0, 1], max(1, len(at)))
    g = gap_ub({k: v[0:1] for k, v in Z.items()}, {k: v[1:2] for k, v in Z.items()})
    m = Z['ok'][0:1][:, :, None] & Z['ok'][1:2][:, None, :]
    surv = bool(((g >= 0.0) & m).any())
    return dict(box_realisable=bool(at), n_atoms=len(at), depth_ub_wall=d,
                atom_x=[at[0][2], at[0][3]] if at else None,
                atom_y=[at[0][4], at[0][5]] if at else None,
                max_gap_ub=float(np.where(m, g, -np.inf).max()),
                pair_survives=surv, PASS=(bool(at) and not surv),
                claim='one axis-aligned blocker is realisable; a PAIR of them at one '
                      'corner is not (c_x, c_y in [1/2, 3/2) forces max|dC| < 1)')


def canary_trump(boxes, atoms, alive, pairs, keep):
    """Trump's TL 2-crowd (squares 4 and 6) mapped to the BL frame must be REALISABLE."""
    getcontext().prec = 300
    d = json.load(open(os.path.join(ATT, 'A03-upper-reconstruct', 'trump11_exact.json')))
    s = Decimal(d['s'])
    co, si = Decimal(d['cos_theta']), Decimal(d['sin_theta'])
    half = Decimal(1) / 2

    def quad(cx, cy, c, sn):
        return [(cx + c * u - sn * v, cy + sn * u + c * v)
                for (u, v) in ((-half, -half), (half, -half), (half, half), (-half, half))]

    def fmm_dec(Q):
        best = min(max(x, y) for x, y in Q)
        for k in range(4):
            px, py = Q[k]
            qx, qy = Q[(k + 1) % 4]
            dx, dy = qx - px, qy - py
            if dx == dy:
                continue
            t = (py - px) / (dx - dy)
            if 0 <= t <= 1:
                best = min(best, px + t * dx)
        return best

    rec = []
    P = []
    for i in (4, 6):
        sq = d['squares'][i]
        cx, cy = Decimal(sq['cx']), Decimal(sq['cy'])
        c, sn = (Decimal(1), Decimal(sq['theta'])) if i == 4 else (co, si)
        Q = quad(cx, cy, c, sn)
        QB = [(x, s - y) for (x, y) in Q]                 # TL -> BL frame (y -> s - y)
        f = fmm_dec(QB)
        thd = 0.0 if i == 4 else 90.0 - math.degrees(math.asin(float(si)))
        P.append((float(cx), float(s - cy), thd, QB))
        rec.append(dict(square=i, cx_BL=float(cx), cy_BL=float(s - cy), theta_BL_deg=thd,
                        f_minmax_exact=str(f)[:40], depth=float(1 - f),
                        min_x=float(min(x for x, _ in QB)),
                        min_y=float(min(y for _, y in QB)),
                        in_quadrant=bool(min(x for x, _ in QB) >= -1e-12
                                         and min(y for _, y in QB) >= -1e-12),
                        meets_open_slot_depth_gt_tol=bool(1 - f > Decimal(DEPTH_MIN))))
    # exact SAT gap between the two BL-frame squares
    A, B = P[0], P[1]
    gA = TB.sat_gap(np.array([A[0]]), np.array([A[1]]), np.array([math.radians(A[2])]),
                    np.array([B[0]]), np.array([B[1]]), np.array([math.radians(B[2])]))[0]
    # containing cover boxes + verdicts
    loc = []
    for (cx, cy, thd, _Q) in P:
        hit = [k for k, b in enumerate(boxes)
               if b.x0 - 1e-9 <= cx <= b.x1 + 1e-9 and b.y0 - 1e-9 <= cy <= b.y1 + 1e-9
               and b.th0 - 1e-7 <= thd <= b.th1 + 1e-7]
        loc.append(hit)
    pk = {(min(i, j), max(i, j)): k for k, (i, j, _a, _b) in enumerate(pairs)}
    pl = []
    for i in loc[0]:
        for j in loc[1]:
            if i == j:
                continue
            k = pk.get((min(i, j), max(i, j)))
            pl.append(dict(i=i, j=j, in_A85_census=(k is not None),
                           box_i_realisable=bool(alive[i]), box_j_realisable=bool(alive[j]),
                           pair_survives=(bool(keep[k]) if k is not None else None)))
    # tiny-box test on the poses themselves
    tiny = []
    for (cx, cy, thd, _Q) in P:
        b = Box(cx - 1e-9, cx + 1e-9, cy - 1e-9, cy + 1e-9, max(0.0, thd - 1e-7),
                min(90.0, thd + 1e-7))
        T = cell_table(b)
        at, du = box_atoms(b, T)
        tiny.append(dict(n_atoms=len(at), realisable=bool(at), depth_ub_wall=du))
    ok = all(r['in_quadrant'] and r['meets_open_slot_depth_gt_tol'] for r in rec) \
        and float(gA) >= 0.0 and all(t['realisable'] for t in tiny) \
        and all(p['box_i_realisable'] and p['box_j_realisable'] for p in pl) \
        and all(p['pair_survives'] for p in pl if p['in_A85_census'])
    return dict(squares=rec, sat_gap_BL_frame=float(gA), cover_boxes=loc,
                census_pairs=pl, tiny_box_test=tiny, PASS=bool(ok))


def canary_grid_witnesses(boxes, alive, pairs, keep):
    """every pair A89 grid-WITNESSED against the OPEN SLOT must survive (soundness)."""
    p = os.path.join(ATT, 'A89-tilt-floor', 'results', 't2b_pairs.jsonl')
    if not os.path.exists(p):
        return dict(available=False)
    pk = {(min(i, j), max(i, j)): k for k, (i, j, _a, _b) in enumerate(pairs)}
    n = nb = nk = miss = 0
    bad = []
    boxbad = set()
    for L in open(p):
        if not L.strip():
            continue
        r = json.loads(L)
        if r.get('witness_kind') != 'slot':
            continue
        ex = r.get('witness_exact', {})
        if not (ex.get('both_meet_slot_exact') and ex.get('disjoint_exact')
                and ex.get('in_quadrant_exact')):
            continue
        n += 1
        i, j = r['i'], r['j']
        if alive[i] and alive[j]:
            nb += 1
        else:
            boxbad.add((i, j))
        k = pk.get((min(i, j), max(i, j)))
        if k is None:
            miss += 1
            continue
        if keep[k]:
            nk += 1
        elif len(bad) < 10:
            bad.append([i, j])
    return dict(available=True, n_exact_slot_witnessed=n, n_with_both_boxes_kept=nb,
                n_pairs_kept=nk, n_not_in_census=miss,
                n_box_soundness_violations=len(boxbad),
                n_pair_soundness_violations=n - nk - miss, examples=bad,
                PASS=bool(n == nb and n - miss == nk))


# ------------------------------------------------------------------ stage 3: the gate
def stage_gate(boxes, pairs, keep, depth, n=1000, seed=SEED):
    W = alive84.load_witnesses('k0_00')
    keys = sorted(W)
    MASK = {c: [G85.drop_masks(G85.map_box(b, c), W) for b in boxes] for c in G85.CORNERS}
    CCORE = {c: [G85.map_box(b, c).core() for b in boxes] for c in G85.CORNERS}
    closed, permT = C85.sigma_closed_boxes(boxes)
    surv = [(pairs[k][0], pairs[k][1]) for k in np.flatnonzero(keep)]
    d2ub = [min(depth[i], depth[j]) for (i, j) in surv]
    surv_d2 = [p for p, v in zip(surv, d2ub) if v >= D2_DELTA]

    def sample(pl, N, sd):
        rnd = random.Random(sd)
        got = dict(attemptable=0, unkillable=0, contradictory=0)
        ncanon = 0
        orb = {}
        if not pl:
            return got, 0, orb
        for _ in range(N):
            node = {c: pl[rnd.randrange(len(pl))] for c in G85.CORNERS}
            bx = [(c, k) for c in G85.CORNERS for k in node[c]]
            contra = False
            for u in range(len(bx)):
                for v in range(u + 1, len(bx)):
                    (cu, iu), (cv, iv) = bx[u], bx[v]
                    if cu == cv:
                        continue
                    if cores_meet(CCORE[cu][iu], CCORE[cv][iv]):
                        contra = True
                        break
                if contra:
                    break
            nd = {c: tuple(sorted(node[c])) for c in G85.CORNERS}
            can, ismin = G85.d4_canonical(nd, permT)
            ncanon += 1 if ismin else 0
            if contra:
                got['contradictory'] += 1
                continue
            st, k, _per = G85.verdict([MASK[c][i] for (c, i) in bx], 3, keys)
            got[st] += 1
        return got, ncanon, orb

    gA, cA, _ = sample(surv, n, seed)
    gB, cB, _ = sample(surv_d2, n, seed + 1)
    return dict(n_surviving_pairs=len(surv), n_surviving_pairs_d2ge=len(surv_d2),
                d2_delta=D2_DELTA, budget=3, n_sampled=n, seed=seed,
                counts=gA, d4_canonical=cA, d4_canonical_fraction=cA / float(n),
                counts_d2=gB, d4_canonical_d2=cB,
                d2ub_stats=dict(min=(min(d2ub) if d2ub else None),
                                max=(max(d2ub) if d2ub else None),
                                median=(float(np.median(d2ub)) if d2ub else None)))


def price(npair, frac_att, tag):
    combos = npair ** 4 / 8.0
    front = combos * frac_att
    return {'tag': tag, 'n_pairs': npair, 'D4_canonical_4tuples': combos,
            'attemptable_fraction': frac_att, 'frontier_nodes': front,
            'CPU_h_at_0.47': front * CPU_H_LO, 'CPU_h_at_1.1': front * CPU_H_HI,
            'CPU_h_at_1700s_per_attempt': front * CPU_H_ATT,
            'ratio_to_3200_CPU_h': front * CPU_H_LO / 3200.0,
            'ratio_to_7000_CPU_h': front * CPU_H_HI / 7000.0}


def main(argv):
    t00 = time.time()
    fc, fp = free_commit_mb()
    print('free commit %.0f MB / avail phys %.0f MB' % (fc, fp), flush=True)
    assert fc > 6144, 'headroom below 6 GB'
    res = dict(attempt='A85 chore realise85: exact realisability of the k0 blocker-pair '
                       'census', s_window=[S_LO, S0F], depth_min=DEPTH_MIN,
               free_commit_mb_at_start=fc)
    print('[1] boxes ...', flush=True)
    boxes, atoms, depth, alive, ob = stage_boxes()
    res['part1_boxes'] = {k: v for k, v in ob.items() if k != 'depth_ub_wall'}
    json.dump(dict(dropped=ob['dropped'], depth_ub_wall=ob['depth_ub_wall'],
                   n_atoms=[len(a) for a in atoms]), open(OUT_BOX, 'w'))
    print(json.dumps(res['part1_boxes'], indent=1), flush=True)

    print('[2] pairs ...', flush=True)
    pairs, keep, op = stage_pairs(boxes, atoms, alive)
    res['part2_pairs'] = op
    json.dump(dict(surviving=[[pairs[k][0], pairs[k][1]]
                              for k in np.flatnonzero(keep).tolist()]),
              open(OUT_PAIR, 'w'))
    print(json.dumps(op, indent=1), flush=True)

    print('[canaries] ...', flush=True)
    res['canary_axis_aligned_pair'] = canary_axis_aligned(boxes)
    res['canary_trump_TL_2crowd'] = canary_trump(boxes, atoms, alive, pairs, keep)
    res['canary_A89_grid_witnesses'] = canary_grid_witnesses(boxes, alive, pairs, keep)
    for k in ('canary_axis_aligned_pair', 'canary_trump_TL_2crowd',
              'canary_A89_grid_witnesses'):
        print(' %-32s PASS=%s' % (k, res[k].get('PASS')), flush=True)

    print('[3] gate ...', flush=True)
    res['part3_gate'] = stage_gate(boxes, pairs, keep, depth)
    print(json.dumps({k: v for k, v in res['part3_gate'].items()}, indent=1), flush=True)

    g = res['part3_gate']
    fa = g['counts']['attemptable'] / float(g['n_sampled'])
    fb = (g['counts_d2']['attemptable'] / float(g['n_sampled'])
          if g['n_surviving_pairs_d2ge'] else 0.0)
    res['part4_price'] = dict(
        reference=dict(a85_pairs=33656, a85_attemptable_frac_4corner=0.179,
                       a85_frontier=33656 ** 4 * 0.179 / 8.0,
                       a85_interior_first_tree_CPU_h=[3200, 7000],
                       per_node_CPU_h=[CPU_H_LO, CPU_H_HI],
                       per_attempt_CPU_h=CPU_H_ATT),
        a85_baseline=price(33656, 0.179, 'A85 as published'),
        realisable=price(g['n_surviving_pairs'], fa, 'realisability-sound'),
        realisable_d2_hypothesis=price(g['n_surviving_pairs_d2ge'], fb,
                                       'realisable + d2 >= %g at all four corners'
                                       % D2_DELTA))
    res['secs'] = time.time() - t00
    res['free_commit_mb_at_end'] = free_commit_mb()[0]
    json.dump(res, open(OUT, 'w'), indent=1, default=str)
    print(json.dumps(res['part4_price'], indent=1, default=str), flush=True)
    print('-> %s  (%.1f s)' % (OUT, time.time() - t00), flush=True)


if __name__ == '__main__':
    main(sys.argv[1:])
