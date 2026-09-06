"""A108 T1 - the EXACT S07 configuration and its endpoint certificate.

The all-eleven-free polish (polish.py) lands on s = 3.885618083164..., every tilted square at
45.000 deg to 4e-5 deg, every coordinate recognisable in Q(sqrt 2).  Reading the active contact
chain off that landing gives a closed 9-equation system whose solution is exact:

    s* = 2 + 4*sqrt(2)/3 = (6 + 4*sqrt 2)/3 = 3.88561808316412...

    the s-determining cycle:  top wall - f1 - BL(0,2) corner - [BL column of three] - bottom wall
                              and       f1 - f0 - f4 - BR(0,0) corner,
                              anchored in x by  f0 - BL(0,1) right edge (x = 1, BL(0,1) on the left
                              wall).

Unlike s-hat (an algebraic number of degree 8), s* lies in the quadratic field Q(sqrt 2), which is
what makes the certificate below EXACT rather than interval: every centre is a + b*sqrt(2) with
a, b rational, every tilt is 0 or 45 deg, so every SAT gap and every containment gap is an element
of Q(sqrt 2) and its sign is decided by rational arithmetic alone.  The mpmath interval endpoint
certificate of A106 (`certify_endpoint`) is run as well, on the numerically polished landing, so
the two methods can be compared.

Outputs results/exact.json.
"""
from __future__ import annotations

import json
import math
import os
from fractions import Fraction as F

import numpy as np

import a108lib as A
from a108lib import S11, L
import polish as P


# ------------------------------------------------------------------ exact arithmetic in Q(sqrt 2)
class Q2:
    """a + b*sqrt(2) with a, b rational.  Exact ordered field arithmetic."""
    __slots__ = ('a', 'b')

    def __init__(self, a=0, b=0):
        self.a = F(a)
        self.b = F(b)

    def __add__(self, o):
        o = q2(o)
        return Q2(self.a + o.a, self.b + o.b)

    __radd__ = __add__

    def __neg__(self):
        return Q2(-self.a, -self.b)

    def __sub__(self, o):
        return self + (-q2(o))

    def __rsub__(self, o):
        return q2(o) + (-self)

    def __mul__(self, o):
        o = q2(o)
        return Q2(self.a * o.a + 2 * self.b * o.b, self.a * o.b + self.b * o.a)

    __rmul__ = __mul__

    def __truediv__(self, o):
        o = q2(o)
        d = o.a * o.a - 2 * o.b * o.b
        return self * Q2(o.a / d, -o.b / d)

    def sign(self):
        """Exact sign of a + b*sqrt2 (no floating point anywhere)."""
        a, b = self.a, self.b
        if a == 0 and b == 0:
            return 0
        if a == 0:
            return 1 if b > 0 else -1
        if b == 0:
            return 1 if a > 0 else -1
        if a > 0 and b > 0:
            return 1
        if a < 0 and b < 0:
            return -1
        # opposite signs: compare a^2 with 2 b^2
        c = a * a - 2 * b * b            # a^2 - 2b^2; sign of (a+b*r2) = sign(a) * sign(c)
        sa = 1 if a > 0 else -1
        sc = 0 if c == 0 else (1 if c > 0 else -1)
        return sa * sc

    def __lt__(self, o):
        return (self - q2(o)).sign() < 0

    def __le__(self, o):
        return (self - q2(o)).sign() <= 0

    def __eq__(self, o):
        return (self - q2(o)).sign() == 0

    def __hash__(self):
        return hash((self.a, self.b))

    def __abs__(self):
        return self if self.sign() >= 0 else -self

    def __float__(self):
        return float(self.a) + float(self.b) * math.sqrt(2.0)

    def __repr__(self):
        return f'({self.a})+({self.b})sqrt2'


def q2(x):
    if isinstance(x, Q2):
        return x
    return Q2(x, 0)


R2 = Q2(0, 1)                      # sqrt 2
HALF_R2 = Q2(0, F(1, 2))           # sqrt(2)/2 = cos 45 = sin 45


# ------------------------------------------------------------------ the exact configuration
S_STAR = Q2(2, F(4, 3))            # 2 + 4 sqrt2 / 3

# tilt is coded as the pair (cos, sin): (1, 0) for an upright, (r2/2, r2/2) for a 45 deg square
UP = (Q2(1), Q2(0))
D45 = (HALF_R2, HALF_R2)

EXACT = [
    ('f0',      Q2(1, F(1, 2)),   Q2(1, F(2, 3)),   D45),
    ('f1',      Q2(2, F(-1, 3)),  Q2(2, F(5, 6)),   D45),
    ('f2',      Q2(1, F(1, 1)),   Q2(1, F(7, 6)),   D45),
    ('f3',      Q2(F(19, 6), 0),  Q2(F(3, 2), F(1, 3)), D45),      # rattler: pocket centre
    ('f4',      Q2(F(3, 2), F(2, 3)), Q2(F(3, 2), F(-1, 6)), D45),
    ('BL(0,0)', Q2(F(1, 2), 0),   Q2(F(1, 2), 0),   UP),
    ('BL(0,1)', Q2(F(1, 2), 0),   Q2(F(3, 2), 0),   UP),
    ('BL(0,2)', Q2(F(1, 2), 0),   Q2(F(5, 2), 0),   UP),
    ('BL(1,0)', Q2(F(3, 2), 0),   Q2(F(1, 2), 0),   UP),
    ('BR(0,0)', S_STAR - Q2(F(1, 2)), Q2(F(1, 2), 0), UP),
    ('TR(0,0)', S_STAR - Q2(F(1, 2)), S_STAR - Q2(F(1, 2)), UP),
]


def exact_float():
    ang = {UP: 0.0, D45: math.pi / 4}
    return float(S_STAR), [(float(x), float(y), ang[t]) for _, x, y, t in EXACT]


# ------------------------------------------------------------------ exact gaps
def sat_gap_exact(p, q):
    """SAT gap of two unit squares in Q(sqrt 2): max over the four body axes of
    |d . n| - 1/2 - (support of the other square along n)/2.  >= 0 <=> interiors disjoint."""
    _, x1, y1, (c1, s1) = p
    _, x2, y2, (c2, s2) = q
    dx, dy = x2 - x1, y2 - y1
    best = None
    for (ca, sa, cb, sb) in ((c1, s1, c2, s2), (c2, s2, c1, s1)):
        for (nx, ny) in ((ca, sa), (-sa, ca)):
            proj = abs(dx * nx + dy * ny)
            sup = abs(nx * cb + ny * sb) + abs(-nx * sb + ny * cb)
            g = proj - Q2(F(1, 2)) - sup * Q2(F(1, 2))
            if best is None or best < g:
                best = g
    return best


def wall_gaps_exact(p, s):
    _, x, y, (c, sn) = p
    w = (abs(c) + abs(sn)) * Q2(F(1, 2))
    return dict(left=x - w, right=s - w - x, bottom=y - w, top=s - w - y)


def verify_exact(cfg=EXACT, s=S_STAR):
    """Exact proof obligation: every pairwise SAT gap >= 0 and every containment gap >= 0."""
    pairs, walls = [], []
    for i in range(len(cfg)):
        for j in range(i + 1, len(cfg)):
            g = sat_gap_exact(cfg[i], cfg[j])
            pairs.append((cfg[i][0], cfg[j][0], g))
        for k, v in wall_gaps_exact(cfg[i], s).items():
            walls.append((cfg[i][0], k, v))
    bad = [t for t in pairs if t[2].sign() < 0] + [t for t in walls if t[2].sign() < 0]
    tight = ([t for t in pairs if t[2].sign() == 0], [t for t in walls if t[2].sign() == 0])
    return pairs, walls, bad, tight


def main():
    out = {}
    s_f, cfg_f = exact_float()
    out['s_exact'] = dict(expr='2 + 4*sqrt(2)/3', a=str(S_STAR.a), b=str(S_STAR.b),
                          float=s_f, minus_shat=s_f - A.SHAT, minus_s0=s_f - A.S0)
    out['configuration'] = [dict(name=n, cx=str(x), cy=str(y),
                                 cx_float=float(x), cy_float=float(y),
                                 tilt_deg=(45.0 if t is D45 else 0.0)) for n, x, y, t in EXACT]
    print('s* =', S_STAR, '=', s_f)
    print('   s* - s-hat =', s_f - A.SHAT, '   s* - s0 =', s_f - A.S0)

    pairs, walls, bad, tight = verify_exact()
    out['exact_verification'] = dict(
        n_pairs=len(pairs), n_walls=len(walls), n_violations=len(bad),
        tight_pairs=[[a, b] for a, b, _ in tight[0]],
        tight_walls=[[a, w] for a, w, _ in tight[1]],
        min_pair_gap=str(min(pairs, key=lambda t: float(t[2]))[2]),
        min_wall_gap=str(min(walls, key=lambda t: float(t[2]))[2]),
        slack_pairs=sorted([[a, b, float(g)] for a, b, g in pairs if g.sign() > 0],
                           key=lambda t: t[2])[:12],
        verdict=('EXACT PACKING at s = 2 + 4 sqrt2 / 3' if not bad else 'VIOLATIONS'))
    print(f"exact check: {len(pairs)} pairs + {len(walls)} containment rows, "
          f"{len(bad)} violations, {len(tight[0])} pair contacts, {len(tight[1])} wall contacts")
    print('  contacts:', ', '.join(f'{a}-{b}' for a, b, _ in tight[0]))
    print('  walls   :', ', '.join(f'{a}-{w}' for a, w, _ in tight[1]))
    assert not bad, bad

    # cross-check in floating point with the lab's own SAT routine
    out['float_crosscheck'] = dict(zip(('worst_pair_gap', 'worst_wall_gap'),
                                       A.worst_gaps(s_f, cfg_f)))
    out['float_crosscheck']['sigma'] = A.sigma(*A.normalise(s_f, cfg_f))
    print('float cross-check:', out['float_crosscheck'])

    # ---------------- A106's interval endpoint certificate on the numerically polished landing
    d = json.load(open(os.path.join(A.RES, 'polish.json'), encoding='utf-8'))
    z = A.to106(d['penalty_polish']['s'], [tuple(c) for c in d['penalty_polish']['cfg']])
    R = P.R_all()
    eps, rep = S11.certify_endpoint(R, z, bounds=P.bounds_all(R))
    out['a106_interval_certificate'] = dict(eps=eps, **{k: (str(v) if not isinstance(v, (int, float, type(None))) else v)
                                                        for k, v in rep.items()})
    print('A106 interval endpoint certificate: eps =', eps, rep)

    # and the same, seeded from the EXACT configuration
    z2 = A.to106(s_f, cfg_f)
    eps2, rep2 = S11.certify_endpoint(R, z2, bounds=P.bounds_all(R))
    out['a106_interval_certificate_from_exact'] = dict(
        eps=eps2, **{k: (str(v) if not isinstance(v, (int, float, type(None))) else v)
                     for k, v in rep2.items()})
    print('   from the exact configuration: eps =', eps2, rep2)

    json.dump(out, open(os.path.join(A.RES, 'exact.json'), 'w', encoding='utf-8'), indent=1)
    print('wrote results/exact.json')


if __name__ == '__main__':
    main()
