"""A258 tests [M]: the closed forms of geo258 against SAT.
  T1 row members are edge to edge (gap 0, contact length 1 - tan phi);
  T2 corner closed form: sat_gap(A-type, B-type) >= 0  <=>  max(E_A, E_B) >= 0 on a < 1, b < 1;
  T3 D  ==>  the eight squares are a packing in the container and every one of the 12 cells is met by >= 2;
  T4 the bare normal ring has Hall minimum 0 (it is NOT family-stuck alone), attained only by maximal families;
  T5 the tight C4 ring is in the closure of D where its formula says so.
"""
import math
import sys

import numpy as np

import geo258 as G

rng = np.random.default_rng(258)


def t1():
    worst = 0.0
    for _ in range(2000):
        phi, a, sg = rng.uniform(0.01, 0.78), rng.uniform(0, 1), rng.choice([-1, 1])
        q = G.row(0, 4.0, a, phi, sg, 2)
        worst = max(worst, abs(G.sat_gap(q[0], q[1])))
    return worst


def t2(N=200000):
    bad, n_other = 0, 0
    worst = 0.0
    for _ in range(N):
        al, be = rng.uniform(0.002, math.pi / 4), rng.uniform(0.002, math.pi / 4)
        a, b = rng.uniform(0, 1), rng.uniform(0, 1)
        A = np.array(G.member(al, a, 1))                                   # floor frame, corner BL
        c, g = math.cos(be), math.sin(be)
        B = np.array([(0, b + c), (g, b), (c + g, b + g), (c, b + c + g)])  # left-wall B-type, offset b
        sg = G.sat_gap(A, B)
        e = max(G.E_corner(a, al, b, be))
        if (sg >= 0) != (e >= 0):
            bad += 1
            worst = max(worst, abs(sg - e))
        if sg > e + 1e-12:
            n_other += 1
    return bad, n_other, worst


def sample_D(s, slots=True, tries=200000, common=False):
    out = []
    for _ in range(tries):
        if common:
            phi = [rng.uniform(0.01, 0.75)] * 4
        else:
            phi = list(rng.uniform(0.01, 0.75, 4))
        K = [s - 1 / math.cos(p) - math.cos(p) - math.sin(p) for p in phi]
        a = [rng.uniform(max(0, k - 1), min(1, k)) for k in K]
        if G.in_D(s, a, phi, slots) > 0:
            out.append((a, phi))
    return out


def t3(s):
    S = sample_D(s, True, 60000)
    worst_c, worst_p, under = 9, 9, 0
    for a, phi in S:
        sq = G.ring(s, a, phi)
        cm, pg = G.check_packing(sq, s)
        worst_c, worst_p = min(worst_c, cm), min(worst_p, pg)
        mt = G.meet_table(sq, s, 0.0)
        if min(len(v) for v in mt.values()) < 2:
            under += 1
    return len(S), worst_c, worst_p, under


def t4(s):
    S = sample_D(s, True, 20000)[:200]
    vals = {}
    for a, phi in S:
        v, fam = G.hall_min(G.ring(s, a, phi), s, 0.0)
        vals[(v, len(fam))] = vals.get((v, len(fam)), 0) + 1
    return vals


if __name__ == '__main__':
    print('T1 worst |gap| of row neighbours', t1())
    print('T2 (sign mismatches, other-axis-larger count, worst)', t2(int(sys.argv[1]) if len(sys.argv) > 1 else 200000))
    for s in (3.82, G.SHAT, 3.95, 3.99):
        print('T3 s=%.4f  (n in D, min containment, min pair gap, rings with an under-met cell)' % s, t3(s))
    print('T4 Hall minimum of the bare ring {(min, |family|): count}', t4(G.SHAT))
    for ph in (2, 8, 14.545, 25, 33):
        a, b = G.tight_ring(G.SHAT, ph * G.DEG)
        print('T5 tight ring at s-hat, phi=%5.2f: a=%.4f b=%.4f in_D=%.4f tooth=%s' % (
            ph, a, b, G.in_D(G.SHAT, [a] * 4, [ph * G.DEG] * 4), G.tooth_terms(G.SHAT, a, ph * G.DEG)))
