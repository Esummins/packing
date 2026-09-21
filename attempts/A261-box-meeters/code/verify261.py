"""A261 O3 -- the VERIFIER (trusted kernel) of the box-valid LP certificates: "no pinwheel of rows of the given senses
and lengths at side s in [S_LO, S0], for ANY per-wall tilts in the job's tilt domain".  Standalone: numpy + ivl261.py (the interval / mean-value arithmetic).

THE CLAIM PER JOB.  Walls w = 0..3 (A258's frames), row of length l_w, sense sg_w, tilt phi_w = t_w * 45 deg,
t_w in the job's dyadic t-interval; start offset a_w in [0, 1], end offset b_w = s - kappa_w - a_w in [0, 1],
kappa = (l - 1) sec + cos + sin; s in [S_LO, S0].  At corner k the START square of wall k (offset a_k, tilt alpha =
phi_k) and the END square of wall k-1 (offset b_{k-1}, tilt beta = phi_{k-1}) both meet the open corner box, so
[T: SAT + Lemma PUSH (k0_count.md)] if they are interior-disjoint they are separated along an EDGE NORMAL m of one of
them pointing into the OPEN second quadrant (m_u < 0 < m_v): at most ONE normal per square -- form 0 (the START
square's) or form 1 (the END square's):   sep = ca a + cb b + c0 >= 0   (closed forms below).
A LEAF certificate for a tilt box is a list of (pattern, y): pattern in {0, 1, 2}^4 (2 = any form at that corner,
then y gives that corner zero weight), y >= 0 twelve multipliers (b <= 1 x4, b >= 0 x4, corner x4).  For every
feasible point  S(x, phi) := sum_i y_i row_i(x, phi) <= 0;  the verifier bounds  min S over x in [0,1]^4 x [S_LO, S0]
and phi in the box from BELOW with outward-rounded interval arithmetic and demands it > 0, for patterns covering all
16 choices.  The tilt boxes come from a bisection TREE in preorder (tokens 0..3 = split that dimension, 4 = leaf),
so they tile the job's domain by construction.

    python verify261.py certs/<job>          -> PASS / FAIL, leaf count   (needs <job>.json, .tree, .leaves)
"""
import json
import struct
import sys

import os

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ivl261 import (INF, PI4, angle, const, dn, up, lower, qabs, qadd, qcos, qmul, qneg, qscale, qsin, qsub,  # noqa: E402
                    wall)

S0 = 3.8771
S_LO = 3.0
VERT = np.array([[(v >> w) & 1 for w in range(4)] + [S_LO if (v >> 4) & 1 else S0] for v in range(32)], float)


def form(which, sA, sB, WA, WB):
    """(ca, cb, c0) of the separation form along the START square's normal (which = 0) or the END square's
    (which = 1):  c0 = P (w_beta - w_alpha)/2 - [1 + cos(arg) + |sin(arg)|]/2,  arg = alpha -+ beta."""
    own, sg = (WA, sA) if which == 0 else (WB, sB)
    if sg > 0:
        ca, cb, P = own['sin'], own['cos'], own['d']
    else:
        ca, cb, P = own['cos'], own['sin'], qneg(own['d'])
    arg = qsub(WA['var'], WB['var']) if sA * sB > 0 else qadd(WA['var'], WB['var'])
    wr = qadd(qcos(arg), qabs(qsin(arg)))
    c0 = qsub(qscale(0.5, qmul(P, qsub(WB['w'], WA['w']))), qscale(0.5, qadd(const(1.0), wr)))
    return ca, cb, c0


def lower_bound(job, tbox, pats, ys):
    """min of S over x in [0,1]^4 x [S_LO, S0] and the tilt box, from below, for M certificates at once.
    S is linear in x, so the minimum is at one of the 32 vertices; per vertex the better of the natural and the
    mean-value enclosure.  tbox: 4 x (tlo, thi); pats: (M, 4); ys: (M, 12) >= 0.  Returns an (M,) array."""
    sg, l = job['senses'], job['lengths']
    pats = np.asarray(pats, int).reshape(-1, 4)
    ys = np.asarray(ys, float).reshape(-1, 12)
    M = len(ys)
    if (ys < 0).any() or not np.isfinite(ys).all():
        return np.full(M, -INF)
    phi = [angle(tbox[w][0], tbox[w][1]) for w in range(4)]
    mid = [0.5 * (p[0] + p[1]) for p in phi]
    r = [up(max(p[1] - m, m - p[0])) for p, m in zip(phi, mid)]
    W = [wall(w, phi[w], mid[w], l[w]) for w in range(4)]
    y1, y2, y3 = ys[:, 0:4], ys[:, 4:8], ys[:, 8:12]
    bad = ((pats == 2) & (y3 != 0)).any(1)
    yq = lambda v: ((v, v), (v, v), [None] * 4)
    A = [qsub(yq(y2[:, w]), yq(y1[:, w])) for w in range(4)]      # coefficient of a_w
    Kc = list(A)                                                  # coefficient of kappa_w, GROUPED (it nearly cancels)
    Sg = const(np.zeros(M))                                       # coefficient of s
    C = const(np.zeros(M))
    for w in range(4):
        Sg = qadd(Sg, qsub(yq(y1[:, w]), yq(y2[:, w])))
        C = qsub(C, yq(y1[:, w]))
    for k in range(4):
        p = (k - 1) % 4
        for q in (0, 1):
            yk = np.where(pats[:, k] == q, y3[:, k], 0.0)
            if not yk.any():
                continue
            ca, cb, c0 = form(q, sg[k], sg[p], W[k], W[p])
            A[k] = qsub(A[k], qscale(yk, ca))
            A[p] = qadd(A[p], qscale(yk, cb))
            Kc[p] = qadd(Kc[p], qscale(yk, cb))
            Sg = qsub(Sg, qscale(yk, cb))
            C = qsub(C, qscale(yk, c0))
    for w in range(4):
        C = qadd(C, qmul(Kc[w], W[w]['kap']))
    Sv = qadd(C, qscale(VERT[:, 4:5], Sg))                        # all 32 vertices at once: shape (32, M)
    for w in range(4):
        Sv = qadd(Sv, qscale(VERT[:, w:w + 1], A[w]))
    L = lower(Sv, r).min(0)
    return np.where(bad, -INF, L)


def admissible(job):
    """the form choices that must be refuted: at corner k form 0 is owned by wall k's START square, form 1 by wall
    k-1's END square; a square of an exactly FLAT wall (tdomain [0, 0]) owns no admissible form [T: PUSH]."""
    flat = [w for w in range(4) if job['tdomain'][w][1] == 0.0]
    out = []
    for ch in range(16):
        c = [(ch >> k) & 1 for k in range(4)]
        if all(not ((c[k] == 0 and k in flat) or (c[k] == 1 and (k - 1) % 4 in flat)) for k in range(4)):
            out.append(tuple(c))
    return out


def covers(pats, need):
    return all(any(all(p[k] == 2 or p[k] == c[k] for k in range(4)) for p in pats) for c in need)


REC = struct.Struct('<4b12f')


def read_leaves(fh):
    while True:
        h = fh.read(1)
        if not h:
            return
        n = h[0]
        rows = [REC.unpack(fh.read(REC.size)) for _ in range(n)]
        yield [r[:4] for r in rows], [r[4:] for r in rows]


def walk(job, tree, leaves):
    """rebuild the boxes from the preorder token stream and check every leaf.  Returns (n_leaves, n_bad, complete)."""
    stack = [tuple((float(a), float(b)) for a, b in job['tdomain'])]
    it = read_leaves(leaves)
    n = bad = 0
    worst = INF
    need = admissible(job)
    for tok in tree:
        if not stack:
            return n, bad + 1, False, worst
        box = stack.pop()
        if tok < 4:
            lo, hi = box[tok]
            mid = 0.5 * (lo + hi)                                 # dyadic: exact in binary floating point
            if not (lo < mid < hi):
                return n, bad + 1, False, worst
            stack.append(box[:tok] + ((mid, hi),) + box[tok + 1:])
            stack.append(box[:tok] + ((lo, mid),) + box[tok + 1:])
        else:
            pats, ys = next(it)
            L = lower_bound(job, box, pats, ys) if len(ys) else np.array([-INF])
            n += 1
            worst = min(worst, float(L.min()))
            if not (covers(pats, need) and (L > 0).all()):
                bad += 1
    return n, bad, (not stack), worst


def main():
    base = sys.argv[1]
    job = json.load(open(base + '.json'))
    assert job['S0'] == S0 and job['S_LO'] == S_LO
    tree = open(base + '.tree', 'rb').read()
    with open(base + '.leaves', 'rb') as fh:
        n, bad, complete, worst = walk(job, tree, fh)
    ok = complete and bad == 0
    print('%s  leaves=%d bad=%d complete=%s least_bound=%.3e  %s' % (job['name'], n, bad, complete, worst,
                                                                     'PASS' if ok else 'FAIL'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
