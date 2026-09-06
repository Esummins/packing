r"""trumplocal103.py -- A103: numerical check of Lemma TRUMP-LOCAL (docs/proofs/noroom.md s.4).

Claim checked (BR corner of Trump, the TR corner is the D4 mirror): in a container of side
m = s-hat + eps, a square Q2 within eta of Trump's BR slot square (centre within eta in L_inf, tilt
within eta radians) and a square Q8 within eta of Trump's square 8 (the 40.18-degree square whose
edge rests on the slot square's top-left corner), interior-disjoint, NEVER both meet the open BR
cell (m-1, m) x (0, 1).  Two tests:
  (1) the cover claim: every admissible Q2 (inside the container, meeting the cell) contains the
      points (m-1+xi, 1-xi') for small xi, xi' > 0 -- the cell's top-left corner region is covered;
  (2) the pair claim: random (Q2, Q8) pairs near Trump's, valid (disjoint, inside), and the count of
      BR meeters among them.
Pure geometry, one process, seconds.  Writes results/trumplocal103.json.
"""
from __future__ import annotations

import json
import math
import os
import random
from decimal import Decimal
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
A103 = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(A103))
RES = os.path.join(A103, 'results')

import lock103 as L  # noqa: E402  (geometry, same conventions)

t = json.load(open(os.path.join(ROOT, 'attempts', 'A03-upper-reconstruct', 'trump11_exact.json')))
SHAT = float(Fraction(Decimal(t['s'])))
TRUMP = [(float(Fraction(Decimal(q['cx']))), float(Fraction(Decimal(q['cy']))),
          float(Fraction(Decimal(q['theta'])))) for q in t['squares']]


def inside(poly, m):
    return all(-1e-12 <= x <= m + 1e-12 and -1e-12 <= y <= m + 1e-12 for x, y in poly)


def point_in_square(p, sq):
    cx, cy, th = sq
    c, s_ = math.cos(th), math.sin(th)
    dx, dy = p[0] - cx, p[1] - cy
    u = dx * c + dy * s_
    v = -dx * s_ + dy * c
    return max(abs(u), abs(v)) <= 0.5 + 1e-12


def run(seed=103, n1=200000, n2=200000):
    rng = random.Random(seed)
    out = {'shat': SHAT}
    # (1) cover claim
    cover = {}
    for eps in (0.0, 0.01, 0.03, 0.06):
        m = SHAT + eps
        for eta in (0.02, 0.05, 0.1):
            worst = None
            tested = 0
            fails = 0
            for _ in range(n1 // 12):
                cx = m - 0.5 + rng.uniform(-eta, eta)
                cy = 0.5 + rng.uniform(-eta, eta)
                th = rng.uniform(-eta, eta)
                sq = (cx, cy, th)
                poly = L.verts(*sq)
                if not inside(poly, m):
                    continue
                if L.corner_depth(sq, 'BR', m) <= 1e-9:
                    continue
                tested += 1
                for xi in (0.002, 0.01, 0.03):
                    for xi2 in (0.002, 0.01, 0.03):
                        p = (m - 1.0 + xi, 1.0 - xi2)
                        if not point_in_square(p, sq):
                            fails += 1
                            if worst is None:
                                worst = {'sq': sq, 'p': p}
            cover['eps=%g eta=%g' % (eps, eta)] = {'tested': tested, 'fails': fails, 'worst': worst}
    out['cover'] = cover
    # (2) pair claim
    pair = {}
    sq2, sq8 = TRUMP[2], TRUMP[8]
    for eps in (0.0, 0.01, 0.03, 0.06, 0.1):
        m = SHAT + eps
        for eta in (0.02, 0.05, 0.1):
            valid = 0
            both = 0
            d2max = 0.0
            ex = None
            for _ in range(n2 // 15):
                q2 = (sq2[0] + rng.uniform(-eta, eta), sq2[1] + rng.uniform(-eta, eta),
                      sq2[2] + rng.uniform(-eta, eta))
                q8 = (sq8[0] + rng.uniform(-eta, eta), sq8[1] + rng.uniform(-eta, eta),
                      sq8[2] + rng.uniform(-eta, eta))
                p2, p8 = L.verts(*q2), L.verts(*q8)
                if not (inside(p2, m) and inside(p8, m)) or L.sep(p2, p8) < 0:
                    continue
                valid += 1
                a, b = L.corner_depth(q2, 'BR', m), L.corner_depth(q8, 'BR', m)
                if a > 1e-9 and b > 1e-9:
                    both += 1
                    if min(a, b) > d2max:
                        d2max = min(a, b)
                        ex = {'q2': q2, 'q8': q8, 'd2': a, 'd8': b}
            pair['eps=%g eta=%g' % (eps, eta)] = {'valid_pairs': valid, 'both_meet': both,
                                                   'max_second_depth': d2max, 'example': ex}
    out['pair'] = pair
    json.dump(out, open(os.path.join(RES, 'trumplocal103.json'), 'w'), indent=1)
    for k, v in cover.items():
        print('cover', k, 'tested', v['tested'], 'fails', v['fails'])
    for k, v in pair.items():
        print('pair ', k, 'valid', v['valid_pairs'], 'both_meet', v['both_meet'],
              'max d2 %.3e' % v['max_second_depth'])


if __name__ == '__main__':
    run()
