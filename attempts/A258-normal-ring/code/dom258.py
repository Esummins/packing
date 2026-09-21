"""A258: the PINWHEEL OF ROWS as a linear problem in the offsets.

For FIXED side s, tilts phi_w, senses sg_w and row lengths l_w the ring conditions are LINEAR in the four start
offsets a_w (b_w = K_w - a_w, K_w = s - (l_w - 1) sec phi_w - w(phi_w)):
    boxes met:     a_w <= 1 - t,  b_w <= 1 - t,  a_w >= 0, b_w >= 0   (HARD containment: the row is in the container
                   iff a_w, b_w >= 0 -- there is no containment penalty anywhere in A258)
    slots (l = 2): a_w + sec <= 2 - t,  b_w + sec <= 2 - t            (optional: 'slots')
    corner k:      sep_i(a_k, b_{k-1}) >= t for ONE SAT axis i of the pair (END of wall k-1, START of wall k);
                   each sep_i is linear in (a, b) for fixed tilts (a translation moves a projection linearly).
sup_margin() maximises t by one LP per choice of axis at each corner (axes that cannot reach sep >= 0 on the
offset box are dropped first), then RE-CHECKS the optimum with the full geometry (all 28 pairs, containment,
cells) -- `verify`.  The LP optimum is exact for its tilt vector; the scan over tilts is a grid: [M].
"""
import itertools
import math

import numpy as np
from scipy.optimize import linprog

import geo258 as G


def corner_forms(sgA, alpha, lA, sgB, beta, lB, s_ref=10.0):
    """linear forms sep = ca * a + cb * b + c0 for the corner pair in the BL frame: START member of the floor row
    (offset a) against the END member of the left-wall row (end offset b).  Only forms with max over the box
    [0,1]^2 >= 0 are returned."""
    A0 = np.array(G.member(alpha, 0.0, sgA))                     # floor frame = xy at BL, offset 0
    # END member of the left-wall row with END offset b = 0: build the row on wall 3 of a big container and shift
    secB = 1.0 / math.cos(beta)
    a3 = s_ref - (lB - 1) * secB - math.cos(beta) - math.sin(beta)   # start offset giving end offset 0
    B0 = G.row(3, s_ref, a3, beta, sgB, lB)[-1]
    out = []
    for P in (A0, B0):
        e = np.roll(P, -1, 0) - P
        nrm = np.stack([e[:, 1], -e[:, 0]], 1)
        nrm = nrm / np.linalg.norm(nrm, axis=1, keepdims=True)
        for n in nrm:
            for sign in (1.0, -1.0):
                m = sign * n
                # B beyond A in direction m:  min_B(m.P) - max_A(m.P) ; A moves by a*(1,0), B by b*(0,1)
                c0 = float((B0 @ m).min() - (A0 @ m).max())
                ca, cb = -float(m[0]), float(m[1])
                if c0 + max(0.0, ca) + max(0.0, cb) >= 0:
                    out.append((ca, cb, c0))
    ded = {}
    for f in out:                                  # the same axis arrives once per parallel edge: keep one
        ded[tuple(round(v, 12) for v in f)] = f
    return list(ded.values())


def sup_margin(s, phi, sg=(1, 1, 1, 1), l=(2, 2, 2, 2), slots=True):
    """(t*, a*) maximising the least margin over the offsets; t* < 0: no ring for these tilts."""
    K = [s - (l[w] - 1) / math.cos(phi[w]) - math.cos(phi[w]) - math.sin(phi[w]) for w in range(4)]
    if min(K) < 0:
        return min(K), None
    if max(K) >= 2:                    # a + b = K with a, b <= 1 - t  =>  t <= (2 - K) / 2
        return (2 - max(K)) / 2, None
    Aub, bub = [], []

    def add(coefs, const):            # sum coefs[w]*a_w + const >= t   ->   -coefs.a + t <= const
        Aub.append([-c for c in coefs] + [1.0])
        bub.append(const)
    for w in range(4):
        e = [0.0] * 4
        e[w] = 1.0
        me = [-v for v in e]
        add(me, 1.0)                  # 1 - a >= t
        add(e, 1.0 - K[w])            # 1 - b = 1 - K + a >= t
        if slots and l[w] == 2:
            sec = 1.0 / math.cos(phi[w])
            add(me, 2.0 - sec)
            add(e, 2.0 - sec - K[w])
    forms = [corner_forms(sg[k], phi[k], l[k], sg[k - 1], phi[k - 1], l[k - 1]) for k in range(4)]
    if any(len(f) == 0 for f in forms):
        return -1.0, None
    best = (-9.0, None)
    bounds = [(0.0, K[w]) for w in range(4)] + [(-5.0, 5.0)]
    for ch in itertools.product(*forms):
        A2, b2 = list(Aub), list(bub)
        for k, (ca, cb, c0) in enumerate(ch):
            co = [0.0] * 4
            co[k] += ca
            co[(k - 1) % 4] -= cb
            A2.append([-c for c in co] + [1.0])
            b2.append(c0 + cb * K[(k - 1) % 4])
        r = linprog([0, 0, 0, 0, -1.0], A_ub=A2, b_ub=b2, bounds=bounds, method='highs')
        if r.status == 0 and -r.fun > best[0]:
            best = (float(-r.fun), [float(v) for v in r.x[:4]])
    return best


def min_side(phi, sg=(1, 1, 1, 1), l=(2, 2, 2, 2), slots=False, t0=0.0):
    """the LEAST side at which a pinwheel of rows with these tilts / senses / lengths exists (closed conditions,
    margin t0): everything is linear in (a_0..a_3, s) too, since K_w = s - kappa_w.  Returns (s_min, a) or (inf, None)."""
    kap = [(l[w] - 1) / math.cos(phi[w]) + math.cos(phi[w]) + math.sin(phi[w]) for w in range(4)]
    Aub, bub = [], []
    for w in range(4):
        e = [0.0] * 5
        e[w] = 1.0
        Aub.append(list(e)); bub.append(1.0 - t0)                          # a <= 1 - t0
        r = [0.0] * 5; r[w] = -1.0; r[4] = 1.0
        Aub.append(list(r)); bub.append(1.0 - t0 + kap[w])                   # b = s - kap - a <= 1 - t0
        Aub.append([-v for v in r]); bub.append(-kap[w])                     # b >= 0
        if slots and l[w] == 2:
            sec = 1.0 / math.cos(phi[w])
            Aub.append(list(e)); bub.append(2.0 - sec - t0)
            Aub.append(list(r)); bub.append(2.0 - sec - t0 + kap[w])
    forms = [corner_forms(sg[k], phi[k], l[k], sg[k - 1], phi[k - 1], l[k - 1]) for k in range(4)]
    if any(len(f) == 0 for f in forms):
        return float('inf'), None
    best = (float('inf'), None)
    bounds = [(0.0, 1.0)] * 4 + [(2.0, 8.0)]
    for ch in itertools.product(*forms):
        A2, b2 = list(Aub), list(bub)
        for k, (ca, cb, c0) in enumerate(ch):                                # ca a_k + cb (s - kap' - a') + c0 >= t0
            co = [0.0] * 5
            co[k] -= ca
            co[(k - 1) % 4] += cb
            co[4] -= cb
            A2.append(co); b2.append(c0 - cb * kap[(k - 1) % 4] - t0)
        r = linprog([0, 0, 0, 0, 1.0], A_ub=A2, b_ub=b2, bounds=bounds, method='highs')
        if r.status == 0 and r.fun < best[0]:
            best = (float(r.fun), [float(v) for v in r.x[:4]])
    return best


def verify(s, a, phi, sg=(1, 1, 1, 1), l=(2, 2, 2, 2)):
    """full geometry re-check of a ring: containment, all pairs, every box met by >= 2, cells met by >= 2."""
    sq = G.ring(s, a, phi, sg, l)
    cm, pg = G.check_packing(sq, s)
    mt = G.meet_table(sq, s, 1e-9)
    boxes = min(len(mt[('C', k)]) for k in range(4))
    allc = min(len(v) for v in mt.values())
    return dict(contain=cm, pair_gap=pg, min_box_meeters=boxes, min_cell_meeters=allc,
                hall_min=G.hall_min(sq, s, 1e-9)[0], n=len(sq))


if __name__ == '__main__':
    for s in (3.82, G.SHAT, 3.95, 3.99):
        for deg in (2, 8, 14.545, 25, 30):
            t, a = sup_margin(s, [deg * G.DEG] * 4)
            print('s=%.4f phi=%6.3f  t*=%+.5f' % (s, deg, t), None if a is None else [round(v, 4) for v in a],
                  verify(s, a, [deg * G.DEG] * 4) if a and t > 0 else '')
    for sgp in ((1, 1, 1, -1), (1, 1, -1, -1), (1, -1, 1, -1)):
        t, a = sup_margin(G.SHAT, [14.545 * G.DEG] * 4, sgp)
        print('mixed', sgp, 't*=%+.5f' % t, a)
