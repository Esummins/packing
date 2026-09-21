"""A258 EXACT geometry check [T-computed]: rational arithmetic (fractions.Fraction), no floats in any verdict.

Tilts are given by the half-angle tangent u = tan(phi/2) in Q:  cos = (1-u^2)/(1+u^2), sin = 2u/(1+u^2), so every
vertex of every row member is rational when a and s are.  Checked, exactly:
  containment in [0, s]^2;  pairwise interior-disjointness (SAT over the rational edge normals, separation >= 0);
  which squares MEET which of the 12 border cells (strict overlap on every axis);  the Hall minimum.
Witnesses:  W1  the TIGHT C4 normal ring + SEATED poker at s = 3877/1000, u = 1/8 (phi = 14.25 deg);
            W2  the MIXED-SENSE ring + + + - at s = 79/20 = 3.95, u = (1/8, 1/8, 1/8 | 2/21), LP offsets rounded to 1e-6.
Output results/exact258.json.
"""
import itertools
import json
import os
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, '..', 'results', 'exact258.json'))


def cs(u):
    return (1 - u * u) / (1 + u * u), 2 * u / (1 + u * u)


def to_xy(w, s, P):
    out = []
    for t, d in P:
        out.append([(t, d), (s - d, t), (s - t, s - d), (d, s - t)][w])
    return out


def member(u, p, sg):
    c, g = cs(u)
    if sg > 0:
        return [(p + g, Fr(0)), (p + c + g, g), (p + c, c + g), (p, c)]
    return [(p + c, Fr(0)), (p + c + g, c), (p + g, c + g), (p, g)]


def ring(s, a, u, sg):
    out = []
    for w in range(4):
        c, _ = cs(u[w])
        for k in range(2):
            out.append(to_xy(w, s, member(u[w], a[w] + k / c, sg[w])))
    return out


def seated(s, w, a, u):
    c, g = cs(u)
    p = (a + 1 / c, c)
    return to_xy(w, s, [p, (p[0] + c, p[1] + g), (p[0] + c - g, p[1] + c + g), (p[0] - g, p[1] + c)])


def axes(P):
    return [(P[(i + 1) % len(P)][1] - P[i][1], P[i][0] - P[(i + 1) % len(P)][0]) for i in range(len(P))]


def separated(A, B, strict=False):
    """exists an edge normal n with max_A(n.P) <= min_B(n.P) or the reverse (unnormalised: the sign is exact)."""
    for n in axes(A) + axes(B):
        pa = [n[0] * x + n[1] * y for x, y in A]
        pb = [n[0] * x + n[1] * y for x, y in B]
        if max(pa) <= min(pb) or max(pb) <= min(pa):
            return True
    return False


def cells(s):
    out = {}
    one = [(Fr(0), Fr(0)), (Fr(1), Fr(0)), (Fr(1), Fr(1)), (Fr(0), Fr(1))]
    for k in range(4):
        out['C%d' % k] = to_xy(k, s, one)
    for w in range(4):
        out['L%d' % w] = to_xy(w, s, [(Fr(1), Fr(0)), (Fr(2), Fr(0)), (Fr(2), Fr(1)), (Fr(1), Fr(1))])
        out['R%d' % w] = to_xy(w, s, [(s - 2, Fr(0)), (s - 1, Fr(0)), (s - 1, Fr(1)), (s - 2, Fr(1))])
    return out


def check(sq, s):
    inside = all(0 <= x <= s and 0 <= y <= s for Q in sq for x, y in Q)
    disjoint = all(separated(sq[i], sq[j]) for i in range(len(sq)) for j in range(i))
    cl = cells(s)
    meet = {k: [i for i, Q in enumerate(sq) if not separated(Q, R)] for k, R in cl.items()}
    best = None
    for kb in range(16):
        for ch in itertools.product('-LR', repeat=4):
            fam = ['C%d' % k for k in range(4) if kb >> k & 1] + [c + str(w) for w, c in enumerate(ch) if c != '-']
            if fam:
                v = len(set(i for k in fam for i in meet[k])) - len(fam)
                if best is None or v < best[0]:
                    best = (v, fam)
    return dict(inside=inside, disjoint=disjoint, packing=inside and disjoint,
                box_meeters=[len(meet['C%d' % k]) for k in range(4)],
                cells_met_by_fewer_than_two=[k for k, v in meet.items() if len(v) < 2],
                hall_min=best[0], hall_family=best[1])


def main():
    res = {}
    s, u = Fr(3877, 1000), Fr(1, 8)
    c, g = cs(u)
    K = s - 1 / c - c - g
    a = (K * c - 1) / (c - g)
    sq = ring(s, [a] * 4, [u] * 4, (1, 1, 1, 1))
    res['W1_tight_ring'] = dict(s=str(s), u=str(u), a=str(a), b=str(K - a), corner=str(a * g + (K - a) * c - 1),
                                **check(sq, s))
    res['W1_tight_ring_plus_seated_poker'] = check(sq + [seated(s, 0, a, u)], s)
    import dom258 as Dm
    import math
    s2, us, sg = Fr(79, 20), [Fr(1, 8), Fr(1, 8), Fr(1, 8), Fr(2, 21)], (1, 1, 1, -1)
    t, af = Dm.sup_margin(float(s2), [2 * math.atan(float(v)) for v in us], sg, (2, 2, 2, 2), False)
    a2 = [Fr(round(v * 10 ** 6), 10 ** 6) for v in af]
    res['W2_mixed_ring'] = dict(s=str(s2), u=[str(v) for v in us], senses=list(sg), a=[str(v) for v in a2],
                                lp_margin=t, **check(ring(s2, a2, us, sg), s2))
    json.dump(res, open(OUT, 'w', encoding='utf-8'), indent=1)
    for k, v in res.items():
        print(k, {kk: vv for kk, vv in v.items() if kk in ('packing', 'box_meeters', 'hall_min', 'corner',
                                                          'cells_met_by_fewer_than_two', 'lp_margin')})


if __name__ == '__main__':
    main()
