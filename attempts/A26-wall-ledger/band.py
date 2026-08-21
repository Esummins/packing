#!/usr/bin/env python3
"""
band.py -- A26 task 1: the BAND-COUNTING LEMMA, in exact rational arithmetic.

Setting.  Container [0,s]^2, s rational.  A placement is a closed unit square
Q(c,theta); its half-width is h(theta) = (cos theta + sin theta)/2 in [1/2, sqrt2/2].

DEFINITION.  Q *avoids the width-w boundary band* iff Q \subseteq [w, s-w]^2.
Since Q(c,theta) \subseteq [a,b]^2 iff c in [a+h, b-h]^2, this is
        c in [w + h(theta), s - w - h(theta)]^2 .

  ==> the band-avoiding squares of a packing are EXACTLY a packing of unit
      squares in the concentric square of side  B = s - 2w.
  ==> m(w) := max # band-avoiding squares = max{ n : s(n) <= B },
      where s(n) is the square-packing constant.  (Lemma B0.)

This file provides three independent tiers of bound on m(w):

  TIER E (elementary, exact, SELF-CONTAINED -- proved and machine-checked here):
    E1  separating-axis two-square lemma:  (2B-1)^2 < 8  ==>  m <= 1.
        (equivalently B < 1/2 + sqrt2 = 1.914213...; this re-proves s(2) >= 1.9142)
    E2  Euclidean pigeonhole: band-avoiding centres lie in a square of side
        a = B - 1 (h >= 1/2) and are pairwise >= 1 apart (disjoint incircles of
        radius 1/2), so a p x q grid with a^2 (p^2+q^2) < p^2 q^2 gives m <= p q.

  TIER P (CITED, not re-verified here): proven optimal point-spreading constants
    d_n = max-min distance of n points in a unit square (n <= 9, classical):
    n points pairwise >= 1 fit in [0,a]^2 only if a >= 1/d_n.

  TIER S (CITED, not re-verified here): proven square-packing constants s(n),
    n <= 9:  s(1)=1, s(2)=s(3)=s(4)=2, s(5)=2+1/sqrt2, s(6)=..=s(9)=3.
    This tier is EXACT for m(w) by Lemma B0 (upper AND lower bound).

Also here: the quantitative TILT-FORCING lemma (task 3(ii)) and the Trump
sanity check.

Run:  python band.py            (prints everything, writes results/band.json)
"""
from __future__ import annotations

import json
import math
import os
from fractions import Fraction as F

S384 = F(96, 25)
SP = F(3877084, 10 ** 6)

# ---------------------------------------------------------------- exact helpers


def sqrt2_bounds(prec=60):
    """rational lo < sqrt2 < hi"""
    lo = F(int(math.isqrt(2 * 10 ** (2 * prec))), 10 ** prec)
    hi = lo + F(1, 10 ** prec)
    return lo, hi


SQRT2_LO, SQRT2_HI = sqrt2_bounds()


# ---------------------------------------------------------------- TIER E


def E1_at_most_one(B: F):
    """(2B-1)^2 < 8  ==>  at most ONE unit square fits in a square of side B.

    PROOF (elementary, complete).  Let Q1,Q2 be interior-disjoint unit squares
    inside [0,B]^2, tilts th1,th2, h_i = h(th_i) in [1/2, sqrt2/2].
    (a) Q_i subseteq [0,B]^2  <=>  c_i in [h_i, B-h_i]^2, so
        |c1x-c2x| <= B-h1-h2 =: D  and  |c1y-c2y| <= D.
    (b) SAT: interior-disjoint convex polygons are separated by an edge normal u
        of one of them, and then |u.(c1-c2)| >= hw1(u)+hw2(u).  If u is an edge
        normal of Q1 then hw1 = 1/2 and hw2 = (|cos psi|+|sin psi|)/2 >= 1/2
        (psi = th1-th2), so |u.(c1-c2)| >= 1.
    (c) u = (cos a, sin a) with a = th1 (mod 90), so |cos a|+|sin a| = 2 h1, and
        |u.(c1-c2)| <= D (|cos a|+|sin a|) = 2 h1 D.
    (b)+(c):  1 <= 2 h1 (B - h1 - h2) <= 2 h1 (B - 1/2 - h1) <= (B-1/2)^2/2,
    the last step being the unconstrained max over h1 in R.  Hence (2B-1)^2 >= 8.
    Contrapositive gives the claim.  (Same with 1<->2.)  QED
    """
    return (2 * B - 1) ** 2 < 8


def E2_grid_bound(a: F, pmax=6):
    """min p*q over grids with a^2(p^2+q^2) < p^2 q^2  (cell diameter < 1)."""
    if a <= 0:
        return 1
    best = None
    for p in range(1, pmax + 1):
        for q in range(1, pmax + 1):
            if a * a * (p * p + q * q) < p * p * q * q:
                if best is None or p * q < best:
                    best = p * q
    return best  # None => no grid certificate


# ---------------------------------------------------------------- TIER P / S

# d_n = max-min pairwise distance of n points in the UNIT square (proven n<=9).
# stored as exact algebraic values -> rational lower bounds on 1/d_n.
# 1/d_n = smallest side a of a square that can hold n points pairwise >= 1.
_ONE_OVER_D = {
    2: ('sqrt2/2', lambda: SQRT2_LO / 2),                      # 1/d2 = 1/sqrt2
    3: ('(sqrt6+sqrt2)/4', lambda: F(96592, 10 ** 5)),         # 0.965925...
    4: ('1', lambda: F(1)),
    5: ('sqrt2', lambda: SQRT2_LO),                            # 1.414213...
    6: ('6/sqrt13', lambda: F(166410, 10 ** 5)),               # 1.664100...
    7: ('(2+sqrt3)/2', lambda: F(186602, 10 ** 5)),            # 1.866025...
    8: ('(sqrt6+sqrt2)/2', lambda: F(193185, 10 ** 5)),        # 1.931851...
    9: ('2', lambda: F(2)),
}
# s(n) = side of the smallest square holding n unit squares (proven n<=9).
_SN = {
    1: ('1', F(1)),
    2: ('2', F(2)), 3: ('2', F(2)), 4: ('2', F(2)),
    5: ('2+1/sqrt2', None),      # 2.7071067811... -> rational LOWER bound below
    6: ('3', F(3)), 7: ('3', F(3)), 8: ('3', F(3)), 9: ('3', F(3)),
}
S5_LO = 2 + SQRT2_LO / 2          # < s(5), safe lower bound
_SN_LO = {n: (v[1] if v[1] is not None else S5_LO) for n, v in _SN.items()}


def P_bound(a: F):
    """max n with 1/d_n <= a   (n points pairwise >=1 fit in [0,a]^2 only if
    a >= 1/d_n).  Returns (bound, valid) -- bound None if a is beyond n=9."""
    n = 1
    for k in sorted(_ONE_OVER_D):
        if _ONE_OVER_D[k][1]() <= a:
            n = k
    if _ONE_OVER_D[9][1]() <= a:
        return None
    return n


def S_bound(B: F):
    """m(w) EXACTLY = max{n : s(n) <= B}, from the proven s(n), n <= 9."""
    if B < 1:
        return 0
    n = 0
    for k in sorted(_SN_LO):
        if _SN_LO[k] <= B:
            n = k
    if _SN_LO[9] <= B:      # B >= 3 : need s(10), not proven
        return None
    return n


# ---------------------------------------------------------------- the table


def m_table(s: F, ws):
    rows = []
    for w in ws:
        B = s - 2 * w
        a = B - 1
        e1 = E1_at_most_one(B)
        e2 = E2_grid_bound(a) if a > 0 else 1
        eE = 1 if e1 else (e2 if e2 is not None else None)
        if e1 and e2 is not None:
            eE = min(1, e2)
        eP = P_bound(a) if a > 0 else 0
        eS = S_bound(B)
        rows.append(dict(w=str(w), w_f=float(w), B=str(B), B_f=float(B),
                         a=str(a), a_f=float(a),
                         E1_at_most_1=bool(e1), E2_grid=e2, tierE=eE,
                         tierP=eP, tierS=eS,
                         m_exact=eS))
    return rows


# ---------------------------------------------------------------- tilt forcing


def tilt_forcing(s: F, N=3):
    """Largest eps such that AT MOST N^2 squares can have tilt within eps of
    axis-parallel (tilt mod 90 in [0,eps] u [90-eps,90)).

    PROOF.  Let Q_i, Q_j be two such squares.  By SAT there is an edge normal u
    of one of them with |u.(c_i-c_j)| >= 1 (as in E1).  u makes an angle
    delta <= eps with an axis, so |cos|+|sin| = cos delta + sin delta <=
    cos eps + sin eps, whence
          ||c_i-c_j||_inf >= 1/(cos eps + sin eps) =: rho .
    All centres lie in [1/2, s-1/2]^2 (h >= 1/2), a square of side L = s-1.
    Partition it into N x N half-open cells of side L/N; if L/N < rho each cell
    holds at most one centre, so there are at most N^2 such squares.
    Condition:  (s-1)(cos eps + sin eps) < N.                                QED
    """
    L = float(s) - 1.0
    # cos e + sin e = sqrt2 sin(e+45deg) < N/L
    r = (N / L) / math.sqrt(2.0)
    if r >= 1.0:
        return None
    eps = math.degrees(math.asin(r)) - 45.0
    return eps


def tilt_forcing_exact(s: F, N, eps_deg):
    """exact check of (s-1)(cos eps + sin eps) < N with OUTWARD rounding."""
    e = math.radians(eps_deg)
    c, sn = math.cos(e), math.sin(e)
    up = F(int((c + sn) * 10 ** 12) + 1, 10 ** 12)     # > cos+sin
    return (s - 1) * up < N, str(up)


# ---------------------------------------------------------------- Trump check


def trump_check(path='../../certs/trump11_certificate.json'):
    d = json.load(open(path))
    s = F(d['container_side'])
    out = []
    for q in d['squares']:
        cx, cy, t = F(q['cx']), F(q['cy']), F(q['t'])
        # cos = (1-t^2)/(1+t^2), sin = 2t/(1+t^2)  (exact rationals)
        den = 1 + t * t
        co, si = (1 - t * t) / den, 2 * t / den
        h = (co + si) / 2
        D = min(cx, cy, s - cx, s - cy)          # centre distance to nearest wall
        out.append(dict(cx=float(cx), cy=float(cy),
                        theta=math.degrees(2 * math.atan(float(t))),
                        h=float(h), D=float(D), w_avoid=float(D - h)))
    return s, out


# ---------------------------------------------------------------- main
def main():
    here = os.path.dirname(os.path.abspath(__file__))
    os.chdir(here)
    res = {}
    print('=' * 78)
    print('A26 task 1 -- BAND-COUNTING LEMMA (exact rationals)')
    print('=' * 78)

    for tag, s in (('3.84', S384), ("s'", SP)):
        print(f'\n--- s = {s} = {float(s):.6f} ---')
        B = s - 2
        print(f'w = 1:  B = s-2 = {B} = {float(B):.6f}')
        print(f'  PI pigeonhole:  a = B-1 = {B-1} = {float(B-1):.4f}, '
              f'5a^2/4 = {F(5,4)*(B-1)**2} = {float(F(5,4)*(B-1)**2):.6f} '
              f'{"< 1  ==> m(1) <= 2  OK" if F(5,4)*(B-1)**2 < 1 else "FAIL"}')
        ok = E1_at_most_one(B)
        print(f'  E1 (SAT lemma): (2B-1)^2 = {(2*B-1)**2} = {float((2*B-1)**2):.6f}'
              f' {"< 8  ==> m(1) = 1  (STRONGER)" if ok else ">= 8 (no)"}')
        assert ok
        print(f'  ==> at least 10 of the 11 squares MEET the width-1 band at s={float(s):.6f}')

    ws84 = [F(k, 100) for k in (0, 10, 20, 30, 40, 42, 45, 50, 55, 57, 60, 64,
                                70, 75, 80, 85, 90, 92, 95, 100, 110)]
    for tag, s in (('3.84', S384), ("3.877084", SP)):
        rows = m_table(s, ws84)
        res[f'm_table_{tag}'] = rows
        print(f'\n--- m(w) table, s = {float(s):.6f}  (B = s-2w, a = B-1) ---')
        print('   w      B       a     | E1 | E2grid | TierE | TierP | TierS=m(w) | >= this many MEET the band')
        for r in rows:
            mm = r['m_exact']
            meets = '' if mm is None else str(11 - mm)
            print(f"  {r['w_f']:.2f}  {r['B_f']:.4f}  {r['a_f']:.4f} | "
                  f"{'Y' if r['E1_at_most_1'] else '.':^2} | "
                  f"{str(r['E2_grid']):^6} | {str(r['tierE']):^5} | "
                  f"{str(r['tierP']):^5} | {str(mm):^10} | {meets}")

    print('\n  TierS is EXACT (Lemma B0 + proven s(n), n<=9): m(w) = max{n : s(n) <= B}.')
    print('  "None" = B >= 3, needs s(10) which is NOT proven -> only m <= 9 from TierP/E.')

    # the charge band
    print('\n--- the CHARGE band (w chosen so band-meeting => centre within 1.35 of a wall) ---')
    w = F(16, 25)                      # 0.64;  0.64 + sqrt2/2 = 1.34710678 < 1.35
    for tag, s in (('3.84', S384), ("3.877084", SP)):
        B = s - 2 * w
        a = B - 1
        print(f'  s={float(s):.6f}  w={float(w)}  B={float(B):.4f}  a={float(a):.4f}: '
              f'TierE m<={E2_grid_bound(a)}  TierP m<={P_bound(a)}  TierS m={S_bound(B)}'
              f'   => at least {11-S_bound(B)} squares have centre within '
              f'{float(w)+float(SQRT2_HI)/2:.4f} of a wall')
    res['charge_band'] = dict(w=str(w), reach=float(w) + float(SQRT2_HI) / 2)

    # tilt forcing
    print('\n--- QUANTITATIVE TILT FORCING (the weak link) ---')
    tf = {}
    for tag, s in (('3.84', S384), ("3.877084", SP)):
        for N, cap in ((3, 9), (4, 16)):
            e = tilt_forcing(s, N)
            if e is None:
                continue
            e_safe = math.floor(e * 1000) / 1000.0
            ok, up = tilt_forcing_exact(s, N, e_safe)
            print(f'  s={float(s):.6f}: at most {cap} squares have tilt within '
                  f'{e_safe:.3f} deg of axis-parallel   (exact check: {ok})')
            tf[f'{tag}_N{N}'] = dict(cap=cap, eps_deg=e_safe, exact_ok=bool(ok))
    res['tilt_forcing'] = tf
    print('  (For eps above this threshold the elementary pigeonhole jumps from 9 to 16')
    print('   and gives NOTHING.  Closing the gap between 3.3 deg and the true threshold')
    print('   is a genuine 30-dimensional packing question -- see notes.md sect.5.)')

    # Trump sanity check
    print('\n--- TRUMP SANITY CHECK ---')
    s_t, sq = trump_check()
    sq.sort(key=lambda r: -r['w_avoid'])
    print(f'  container side {float(s_t):.7f};  per square: D = dist(centre, nearest wall),')
    print('  h = half-width, w_avoid = D - h = the largest band width this square avoids')
    for r in sq:
        print(f'   theta={r["theta"]:6.2f}  centre=({r["cx"]:.4f},{r["cy"]:.4f})  '
              f'D={r["D"]:.4f}  h={r["h"]:.4f}  w_avoid={r["w_avoid"]:+.4f}')
    best = sq[0]['w_avoid']
    print(f'  max w_avoid over Trump squares = {best:.4f}  ==> ZERO Trump squares avoid the')
    print(f'  width-1 band (need w_avoid >= 1); consistent with m(1) = 1 (which allows one).')
    res['trump'] = dict(s=str(s_t), squares=sq, max_w_avoid=best)

    os.makedirs('results', exist_ok=True)
    with open('results/band.json', 'w') as f:
        json.dump(res, f, indent=1)
    print('\nwrote results/band.json')


if __name__ == '__main__':
    main()
