"""A254: the border-cell system for general m = ceil(sqrt n), s in (m-1, m), eps = m - s; the C4 pinwheel ring of
4(m-2) tilted wall touchers; incidences; the Hall / FAMILY-STUCK check (min over admissible families of
|M(Pi)| - |Pi|) for the bare ring and for ring + one abstract poker.

Cells (8m - 20 of them): four corner boxes; per wall, in the wall coordinate t in [0, s], the LEFT chain
L_j = [j, j+1] and the RIGHT chain R_j = [s-j-1, s-j], j = 1 .. m-3 (depth [0,1] off the wall).  m = 4 gives
A244/A250's twelve cells.  L_j meets R_j' iff j + j' = m-2 (ribbon of width eps) or m-1 (width 1-eps).
    python cells254.py --m 3,4,5,6        -> results/cells254.json
"""
import argparse
import itertools
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))


def rot(P, s, k):
    """C4: (x, y) -> (s - y, x), k times (left wall -> floor -> right wall -> ceiling)."""
    P = np.array(P, float)
    for _ in range(k % 4):
        P = np.stack([s - P[:, 1], P[:, 0]], 1)
    return P


def cells(m, s):
    """[(name, 4x2 rect)]: corners C0..C3 (C0 = BL, then C4 images), wall w cells wL{j}, wR{j}."""
    out = []
    for w in range(4):
        out.append(('C%d' % w, rot([(0, 0), (1, 0), (1, 1), (0, 1)], s, w)))
    for w in range(4):
        for j in range(1, m - 2):
            out.append(('%dL%d' % (w, j), rot([(0, j), (1, j), (1, j + 1), (0, j + 1)], s, w)))
            out.append(('%dR%d' % (w, j), rot([(0, s - j - 1), (1, s - j - 1), (1, s - j), (0, s - j)], s, w)))
    return out


def sat_gap(A, B):
    """max over edge normals of the separation (> 0 disjoint, < 0 interiors overlap by that depth)."""
    best = -math.inf
    for P in (A, B):
        for i in range(len(P)):
            e = P[(i + 1) % len(P)] - P[i]
            n = np.array([e[1], -e[0]]) / math.hypot(*e)
            a, b = A @ n, B @ n
            best = max(best, max(a.min() - b.max(), b.min() - a.max()))
    return best


def conflicts(cl):
    return {(i, j) for i in range(len(cl)) for j in range(i + 1, len(cl)) if sat_gap(cl[i][1], cl[j][1]) < -1e-9}


def toucher(p, tau, hand):
    """left-wall toucher, lowest extent p along the wall, tilt tau; hand +1: lowest vertex at (sin, p) (theta = tau
    in A249's frame), hand -1: the mirror (theta = 90 - tau)."""
    c, d = math.cos(tau), math.sin(tau)
    if hand > 0:
        return np.array([(d, p), (d + c, p + d), (c, p + c + d), (0, p + c)])
    return np.array([(c, p), (c + d, p + c), (d, p + c + d), (0, p + d)])


def ring(m, s, tau, a, hand, extra=0.0):
    """C4 pinwheel ring: per wall m-2 touchers, first at offset a, pitch 1/cos(tau) + extra; returns squares, b."""
    pitch = 1 / math.cos(tau) + extra
    w = math.cos(tau) + math.sin(tau)
    ps = [a + i * pitch for i in range(m - 2)]
    b = s - (ps[-1] + w)
    sq = [rot(toucher(p, tau, hand), s, k) for k in range(4) for p in ps]
    return sq, b


def ring_margin(sq, s):
    """min SAT gap over the pairs that are not stack neighbours (those touch by construction: gap 0), or -1 if a
    stack pair overlaps / a square leaves the container."""
    q = len(sq) // 4
    g, ok = math.inf, True
    for i in range(len(sq)):
        for j in range(i + 1, len(sq)):
            v = sat_gap(sq[i], sq[j])
            if i // q == j // q and j == i + 1:
                ok = ok and v > -1e-9
            else:
                g = min(g, v)
    ok = ok and min(min(P.min(), s - P.max()) for P in sq) > -1e-9
    return g if ok else -1.0


def best_ring(m, s, tau):
    best = None
    for hand in (1, -1):
        for a in np.linspace(0.02, 0.999, 120):
            sq, b = ring(m, s, tau, a, hand)
            # ADJ pattern: toucher i starts below i (it meets L_{i-1} and R_{m-1-i}), last one meets its corner box
            if not (0.03 < b < 0.97) or a > 0.97 or a + (m - 3) / math.cos(tau) > m - 2 - 0.01:
                continue
            mg = ring_margin(sq, s)
            if best is None or mg > best[0]:
                best = (mg, hand, float(a), float(b), sq)
    return best


def incid(sq, cl, tol=1e-7):
    """meeters[i] = bitmask of the squares whose interior meets cell i (SAT depth > tol)."""
    return [sum(1 << q for q, S in enumerate(sq) if sat_gap(S, C) < -tol) for _, C in cl]


def hall(cl, conf, meet, m):
    """min over admissible families of |M(Pi)| - |Pi| (and one minimiser); walls are independent given the
    conflict graph (conflicts live inside one wall), so enumerate per wall and combine."""
    names = [c[0] for c in cl]
    groups = [[i for i, nm in enumerate(names) if nm.startswith('%d' % w) and nm[0] != 'C'] for w in range(4)]
    per = []
    for g in groups:
        L = []
        for r in range(len(g) + 1):
            for sub in itertools.combinations(g, r):
                if all((x, y) not in conf for x, y in itertools.combinations(sub, 2)):
                    mk = 0
                    for x in sub:
                        mk |= meet[x]
                    L.append((len(sub), mk, sub))
        per.append(L)
    corners = [i for i, nm in enumerate(names) if nm[0] == 'C']
    cs = []
    for r in range(5):
        for sub in itertools.combinations(corners, r):
            mk = 0
            for x in sub:
                mk |= meet[x]
            cs.append((r, mk, sub))
    best, nfam = (10 ** 9, None), 0
    for c0 in cs:
        for a in per[0]:
            for b in per[1]:
                k1, m1 = c0[0] + a[0] + b[0], c0[1] | a[1] | b[1]
                for c in per[2]:
                    for d in per[3]:
                        k = k1 + c[0] + d[0]
                        nfam += 1
                        if k == 0:
                            continue
                        v = bin(m1 | c[1] | d[1]).count('1') - k
                        if v < best[0]:
                            best = (v, [names[i] for i in c0[2] + a[2] + b[2] + c[2] + d[2]])
    return best[0], best[1], nfam - 1


def analyse(m, s, tau):
    cl = cells(m, s)
    conf = conflicts(cl)
    names = [c[0] for c in cl]
    exp = set()
    for w in range(4):
        for j in range(1, m - 2):
            for jj in range(1, m - 2):
                if j + jj in (m - 2, m - 1):
                    exp.add(tuple(sorted((names.index('%dL%d' % (w, j)), names.index('%dR%d' % (w, jj))))))
    r = best_ring(m, s, tau)
    out = dict(m=m, s=s, eps=m - s, tau_deg=math.degrees(tau), n_cells=len(cl), n_conflicts=len(conf),
               conflicts_as_predicted=(conf == exp), ring_size=4 * (m - 2))
    if r is None or r[0] <= 0:
        out['ring'] = None if r is None else dict(margin=r[0], hand=r[1], a=r[2], b=r[3])
        return out
    mg, hand, a, b, sq = r
    meet = incid(sq, cl)
    cnt = {nm: bin(v).count('1') for nm, v in zip(names, meet)}
    h0 = hall(cl, conf, meet, m)
    out.update(ring=dict(margin=mg, hand=hand, a=a, b=b), min_meeters=min(cnt.values()),
               singly_met=[nm for nm, v in cnt.items() if v < 2], hall_bare=h0[0], hall_bare_family=h0[1],
               n_families=h0[2], max_family=4 * (m - 2))
    pk = {}
    P = 1 << len(sq)                                   # the abstract poker: one more square
    if m == 3:
        mp = list(meet)
        mp[names.index('C0')] |= P
        pk['corner C0'] = hall(cl, conf, mp, m)[0]
    for k in range(2, m - 1):                          # narrow ribbon [k - eps, k] on wall 0: cells L_{k-1}, R_{m-1-k}
        mp = list(meet)
        mp[names.index('0L%d' % (k - 1))] |= P
        mp[names.index('0R%d' % (m - 1 - k))] |= P
        pk['narrow k=%d' % k] = hall(cl, conf, mp, m)[0]
    for j in range(2, m - 2):                          # wide overlap only: L_j and R_{m-1-j}
        mp = list(meet)
        mp[names.index('0L%d' % j)] |= P
        mp[names.index('0R%d' % (m - 1 - j))] |= P
        pk['wide j=%d' % j] = hall(cl, conf, mp, m)[0]
    out['hall_with_poker'] = pk
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--m', default='3,4,5,6')
    ap.add_argument('--tau', type=float, default=6.0)
    a = ap.parse_args()
    side = {3: 2.70, 4: 3.877084, 5: 4.70, 6: 5.70, 7: 6.70}
    res = [analyse(m, side[m], math.radians(a.tau)) for m in [int(t) for t in a.m.split(',')]]
    json.dump(res, open(os.path.join(ATT, 'results', 'cells254.json'), 'w'), indent=1)
    for r in res:
        print(json.dumps({k: v for k, v in r.items() if k != 'hall_bare_family'}))


if __name__ == '__main__':
    main()
