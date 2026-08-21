#!/usr/bin/env python3
"""
rankcuts.py -- A26 bonus: are the band-counting lemmas VIOLATED by A19's exact
rational fractional packing of value 11 at s = 96/25?

Why it matters.  A07/A19 proved the pure coverage LP can never certify 3.84:
A19 exhibits an EXACT rational fractional packing of value 11 (file
attempts/A19-hybrid-kernel/lp_floor_384.json, verified by an exact cell B&B).
The band-counting lemma is a family of REGION-RANK cuts (idea I-L8):

    for every w:   sum_{p : R(p) >= w} y_p  <=  m(w),
    R(p) := dist(centre(p), nearest wall) - h(theta_p)   ("the largest band width
            this placement avoids"),   m(w) = max{n : s(n) <= s - 2w}.

If A19's y satisfies every such cut, then y stays feasible for the CUT-
STRENGTHENED LP, so the strengthened LP still has value >= 11 and STILL cannot
certify s(11) >= 3.84.  That is a decisive (negative) statement about the whole
region-rank-cut line, obtained for free.

Also tested: tilt-class cuts, band x tilt cuts, and the A21/A24 zone ranks.
"""
from __future__ import annotations

import json
import math
import os
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
S = F(96, 25)
SQRT2_LO = F(int(math.isqrt(2 * 10 ** 60)), 10 ** 30)
S5_LO = 2 + SQRT2_LO / 2            # < s(5) = 2 + 1/sqrt2
SN_LO = {1: F(1), 2: F(2), 3: F(2), 4: F(2), 5: S5_LO,
         6: F(3), 7: F(3), 8: F(3), 9: F(3)}


def m_of_w(w: F):
    """exact m(w) = max{n : s(n) <= s-2w}; None if it needs the unproven s(10)."""
    B = S - 2 * w
    if B < 1:
        return 0
    if SN_LO[9] <= B:
        return None
    n = 0
    for k in sorted(SN_LO):
        if SN_LO[k] <= B:
            n = k
    return n


def load():
    d = json.load(open(os.path.join(HERE, '..', 'A19-hybrid-kernel',
                                    'lp_floor_384.json')))
    assert F(d['s']) == S
    P = []
    for p in d['placements']:
        cx, cy, co, si, w = (F(p['cx']), F(p['cy']), F(p['cos']),
                             F(p['sin']), F(p['w']))
        h = (co + si) / 2
        D = min(cx, cy, S - cx, S - cy)
        th = math.degrees(math.atan2(float(si), float(co))) % 90.0
        tilt = min(th, 90.0 - th)          # distance from axis-parallel
        P.append(dict(cx=cx, cy=cy, co=co, si=si, w=w, h=h, D=D, R=D - h,
                      tilt=tilt))
    return P


def main():
    P = load()
    tot = sum(p['w'] for p in P)
    print('=' * 76)
    print('A26 / rankcuts -- band rank cuts vs A19\'s exact value-11 fractional packing')
    print('=' * 76)
    print(f'  s = {S} = {float(S)},  placements = {len(P)},  total weight = {tot}')

    # ---- band family: test at every breakpoint (the R values) ------------
    Rs = sorted(set(p['R'] for p in P), reverse=True)
    print('\n  BAND RANK CUTS   sum_{R(p) >= w} y_p  <=  m(w)')
    print('    w        m(w)   LHS(w)=weight with R>=w   slack')
    viol = []
    tight = []
    for R in Rs:
        for w in (R, R - F(1, 10 ** 6)):
            if w <= 0:
                continue
            m = m_of_w(w)
            lhs = sum(p['w'] for p in P if p['R'] >= w)
            if m is None:
                continue
            sl = m - lhs
            if sl < 0:
                viol.append((w, m, lhs))
            if sl == 0:
                tight.append((w, m, lhs))
        m = m_of_w(R)
        lhs = sum(p['w'] for p in P if p['R'] >= R)
        print(f'   {float(R):8.5f}  {str(m):>4}   {float(lhs):8.3f}'
              f'              {"n/a" if m is None else format(float(m-lhs), "+.3f")}')
    print(f'\n  VIOLATIONS: {len(viol)}   TIGHT cuts: {len(set(tight))}')
    for w, m, l in sorted(set(tight))[:6]:
        print(f'    tight at w={float(w):.6f}: m={m} = weight {float(l):.3f}')

    # the largest-w statements
    for w in (F(92, 100), F(93, 100), F(1), F(11, 10), F(14, 10)):
        m = m_of_w(w)
        lhs = sum(p['w'] for p in P if p['R'] >= w)
        print(f'    w={float(w):.2f}: m(w)={m}, LP weight with R>=w = {float(lhs):.3f}')

    # ---- tilt cuts ------------------------------------------------------
    print('\n  TILT CUTS   sum_{tilt(p) <= eps} y_p <= 9   (eps <= 3.326 deg proved)')
    for eps in (0.0, 1.0, 2.0, 3.326, 5.0, 10.0, 15.0):
        lhs = sum(p['w'] for p in P if p['tilt'] <= eps + 1e-12)
        print(f'    eps={eps:6.3f} deg: weight = {float(lhs):.3f}'
              f'   {"VIOLATION" if (eps <= 3.326 and lhs > 9) else "ok"}')

    # ---- band x tilt ----------------------------------------------------
    print('\n  BAND x TILT   near-upright squares avoiding the width-w band')
    print('    (they live in a B x B box with pairwise ||.||_inf >= 1/(cos e+sin e),')
    print('     so at most (floor((B-1)/rho)+1)^2 of them)')
    for w in (F(2, 10), F(42, 100), F(6, 10), F(8, 10)):
        B = S - 2 * w
        eps = 3.326
        rho = 1.0 / (math.cos(math.radians(eps)) + math.sin(math.radians(eps)))
        cap = (int(math.floor(float(B - 1) / rho)) + 1) ** 2
        lhs = sum(p['w'] for p in P if p['R'] >= w and p['tilt'] <= eps)
        print(f'    w={float(w):.2f} B={float(B):.3f}: cap={cap}, LP weight='
              f'{float(lhs):.3f}   {"VIOLATION" if lhs > cap else "ok"}')

    # ---- zone ranks (A21 corner/side zones) ------------------------------
    print('\n  ZONE RANK CUTS (A21 zones, rank by diameter/pigeonhole)')
    zones = [('corner [1/2,11/10]^2', F(1, 2), F(11, 10), F(1, 2), F(11, 10), 1),
             ('corner (3.84-)', S - F(11, 10), S - F(1, 2), S - F(11, 10), S - F(1, 2), 1),
             ('bottom side [11/10,137/50]x[1/2,11/10]', F(11, 10), F(137, 50),
              F(1, 2), F(11, 10), 3),
             ('interior [11/10,137/50]^2', F(11, 10), F(137, 50), F(11, 10), F(137, 50), None)]
    for name, x0, x1, y0, y1, rank in zones:
        lhs = sum(p['w'] for p in P if x0 <= p['cx'] <= x1 and y0 <= p['cy'] <= y1)
        dia2 = (x1 - x0) ** 2 + (y1 - y0) ** 2
        print(f'    {name}: diam^2={float(dia2):.3f}  rank<={rank}  LP weight='
              f'{float(lhs):.3f}   {"VIOLATION" if rank and lhs > rank else "ok"}')

    out = dict(n_violations=len(viol),
               tight=[(str(w), m, str(l)) for w, m, l in sorted(set(tight))],
               R_profile=[(str(p['R']), str(p['w']), p['tilt']) for p in
                          sorted(P, key=lambda q: -q['R'])])
    os.makedirs(os.path.join(HERE, 'results'), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, 'results', 'rankcuts.json'), 'w'), indent=1)
    print('\n  wrote results/rankcuts.json')
    print('\n  CONCLUSION: if 0 violations, A19\'s y is feasible for the cut-strengthened')
    print('  LP too, hence tau_cut(3.84) >= 11: the band/tilt/zone rank-cut family')
    print('  CANNOT break the pure-LP ceiling at 3.84.')


if __name__ == '__main__':
    main()
