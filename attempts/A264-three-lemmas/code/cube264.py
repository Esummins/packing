"""A264 Lemma 3 -- NEAR-FLAT CUBE: the mixed-sense rings of pairs with all tilts in [0, eps0] are infeasible
below side 4 - lam - nu (three_lemmas.md s.3).  This file (1) evaluates the lemma's constants in interval
arithmetic (mpmath, 60 digits, outward rounded) and checks the three closing inequalities; (2) tests the two
corner lemmas MC(+,-), MC(-,+), PC(+,+) on random near-flat corners against the exact SAT forms of corner264;
(3) as an independent sanity check solves, at random tilt vectors of the cube and every choice of axes, the
LP  max t  s.t.  a_w, b_w <= 1 - t, a_w + b_w = s - sec - cos - sin, corner forms >= 0  and reports max t
(the hand lemma says max t < 0 -- no STRICT ring; the closed relaxation t = 0 is the domino pinwheel).
    python cube264.py            -> results/cube264.json
"""
import json
import math
import os
import random
import sys

import mpmath as mp
import numpy as np
from scipy.optimize import linprog

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import corner264 as C                                                    # noqa: E402

mp.mp.dps = 60
EPS0 = mp.pi / 256                    # 0.703125 deg = 45 deg / 64, A261's TMIN
SHAT = mp.mpf('3.877083590022814')
SMAX = mp.mpf('3.8771')


def constants(eps0=EPS0):
    """lam: MC(+,-) forces a, b > 1 - lam;  mu: MC(-,+) forces a > 1 - mu or b > 1 - mu;
    nu(A): PC(+,+) forces b > 1 - nu(A) when a <= A.  All upper bounds (monotone in eps0)."""
    e = mp.mpf(eps0)
    lam = e / 2 + e * e / 2
    mu = e * e / 2 + mp.tan(e) * (1 + mp.sin(e))
    return lam, mu, (lambda A: e * e / 2 + mp.mpf(A) * mp.tan(e))


def chains(s=SMAX, eps0=EPS0):
    """The three patterns: returns the side threshold below which each is infeasible, and the margin at s."""
    lam, mu, nu = constants(eps0)
    S3 = s - 3                                            # a_w <= s - 3 + (1 - b_w) whenever b_w known
    out = {}
    # + + + -: corner 0 (+,-) -> a0, b3 >= 1 - lam; wall 3 -> a3 <= S3 + lam; corner 3 (-,+) -> b2 >= 1 - mu
    # (a3 >= 1 - mu impossible); wall 2 -> a2 <= S3 + mu; corner 2 (+,+) -> b1 >= 1 - nu(a2); wall 1 ->
    # a1 <= S3 + nu(a2); corner 1 (+,+) -> b0 >= 1 - nu(a1); wall 0 -> a0 <= S3 + nu(a1) < 1 - lam.
    n2 = nu(S3 + mu)
    n1 = nu(S3 + n2)
    out['pppm'] = dict(threshold=float(4 - lam - n1), margin=float((1 - lam) - (S3 + n1)),
                       also=float((1 - mu) - (S3 + lam)))
    # + - + -: corners 0, 2 (+,-) -> a0, b3, a2, b1 >= 1 - lam; wall 1 -> a1 <= S3 + lam; corner 1 (-,+) with
    # A = wall 1, B = wall 0: a1 >= 1 - mu impossible, so b0 >= 1 - mu; wall 0 -> a0 <= S3 + mu < 1 - lam.
    out['pmpm'] = dict(threshold=float(4 - lam - mu), margin=float((1 - lam) - (S3 + mu)))
    # + + - -: corner 0 (+,-) -> a0 >= 1 - lam; wall 0 -> b0 <= S3 + lam; corner 1 (+,+) -> b0 >= 1 - nu(1).
    out['ppmm'] = dict(threshold=float(4 - lam - nu(1)), margin=float((1 - nu(1)) - (S3 + lam)))
    out['constants'] = dict(eps0_rad=float(eps0), eps0_deg=float(eps0 * 180 / mp.pi), lam=float(lam),
                            mu=float(mu), nu_1=float(nu(1)), s=float(s))
    return out


def test_corner_lemmas(n=20000, seed=5, eps0=float(EPS0)):
    """Random corners with a, b in [0,1), tilts in [0, eps0]: whenever SAT says disjoint, the lemma's bound holds."""
    rng = random.Random(seed)
    lam, mu, nu = constants(eps0)
    lam, mu = float(lam), float(mu)
    viol = dict(pm=0, mp=0, pp=0)
    worst = dict(pm=1.0, mp=1.0, pp=1.0)
    for _ in range(n):
        al, be = rng.uniform(0, eps0), rng.uniform(0, eps0)
        a, b = 1 - rng.uniform(0, 0.03), 1 - rng.uniform(0, 0.03)
        if rng.random() < 0.3:
            a, b = rng.uniform(0, 1), rng.uniform(0, 1)
        for tag, sA, sB in (('pm', 1, -1), ('mp', -1, 1), ('pp', 1, 1)):
            if C.sat_gap(C.vertsA(a, al, sA), C.vertsB(b, be, sB)) < 0:
                continue
            if tag == 'pm':
                m = min(a, b) - (1 - lam)
            elif tag == 'mp':
                m = max(a, b) - (1 - mu)
            else:
                m = b - (1 - float(nu(a)))
            worst[tag] = min(worst[tag], m)
            if m < -1e-12:
                viol[tag] += 1
    return dict(n=n, violations=viol, least_slack=worst)


def lp_max_t(senses, phi, s):
    """max t over all 16 axis choices: a_w, b_w <= 1 - t, a_w, b_w >= 0, wall identity, corner forms."""
    best = -1.0
    kap = [1 / math.cos(p) + math.cos(p) + math.sin(p) for p in phi]
    for ch in range(16):
        A, bvec = [], []
        for w in range(4):                    # a_w + t <= 1;  b_w + t <= 1  (b_w = s - kap_w - a_w)
            r = [0.0] * 5; r[w] = 1; r[4] = 1; A.append(r); bvec.append(1.0)
            r = [0.0] * 5; r[w] = -1; r[4] = 1; A.append(r); bvec.append(1.0 - (s - kap[w]))
            r = [0.0] * 5; r[w] = 1; A.append(r); bvec.append(s - kap[w])           # b_w >= 0
        for k in range(4):
            p = (k - 1) % 4
            which = (ch >> k) & 1
            ca, cb, c0 = C.a261_form(which, senses[k], senses[p], phi[k], phi[p])
            # ca*a_k + cb*(s - kap_p - a_p) + c0 >= 0  ->  -ca*a_k + cb*a_p <= cb*(s - kap_p) + c0
            r = [0.0] * 5; r[k] -= ca; r[p] += cb; A.append(r); bvec.append(cb * (s - kap[p]) + c0)
        res = linprog([0, 0, 0, 0, -1.0], A_ub=A, b_ub=bvec, bounds=[(0, 1)] * 4 + [(-1, 1)], method='highs')
        if res.status == 0:
            best = max(best, -res.fun)
    return best


def lp_scan(n=200, seed=7, eps0=float(EPS0), s=float(SMAX)):
    rng = random.Random(seed)
    out = {}
    for name, sg in (('pppm', (1, 1, 1, -1)), ('pmpm', (1, -1, 1, -1)), ('ppmm', (1, 1, -1, -1))):
        worst = -1.0
        for i in range(n):
            phi = [rng.uniform(0, eps0) for _ in range(4)]
            if i % 4 == 0:
                phi = [rng.choice((0.0, eps0)) for _ in range(4)]
            worst = max(worst, lp_max_t(sg, phi, s))
        out[name] = worst
    return out


if __name__ == '__main__':
    res = dict(chains=chains(), chains_at_4=chains(s=mp.mpf(4)), corners=test_corner_lemmas(),
               lp_max_t=lp_scan(), forms_check=C.check_forms(n=20000, tmax=float(EPS0) * 3, seed=11))
    os.makedirs(os.path.join(HERE, '..', 'results'), exist_ok=True)
    with open(os.path.join(HERE, '..', 'results', 'cube264.json'), 'w') as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))
