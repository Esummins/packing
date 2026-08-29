"""A45-B  m_ub(theta) crude guard  [EXACT, cheap]  --  notes/charging_lemma.md Sec 6.4.

m(theta) = max number of unit squares at EXACTLY common tilt theta inside [0,s]^2, s <= s0.
Certified crude upper bound, per 3-degree theta bin of [0,45] (the D4 fundamental domain: theta
and 90-theta give congruent configurations, so [45,90] is covered by reflection).

GEOMETRY (exact).  Squares of common tilt theta are pairwise interior-disjoint iff their centres
are >= 1 apart in the THETA-ROTATED sup-norm.  A tilted unit square fits in [0,s]^2 iff its
centre lies in [h, s-h]^2 with h = (cos+sin)/2 (the axis support half-width).  Rotating into the
theta-frame: the centres lie in a square of side  A(theta) = s - (cos+sin), rotated by -theta,
and are pairwise >= 1 apart in the STANDARD sup-norm.  Using s = s0 is sound (the region only
grows with s).  NOTE (deviation from the brief's wording): the eroded region is a rotated SQUARE
(4 edges), not an octagon -- the Minkowski erosion of a square by a square is a square.  The
count below is done on that exact region.

COUNTING (the certified bound).  Partition the region's bounding box (side B = A*(cos+sin)) into
columns of width < 1.  Two centres in one column have |dx| < 1, hence must differ by >= 1 in y.
A column meeting the region in a y-interval of length Y therefore holds at most 1 + floor(Y)
centres.  m_ub = sum over columns.  This is sharper than counting cells and it reproduces the
required sanity value: bin [0,3) -> 9.

INTERVAL TREATMENT OVER A BIN.  cos and sin are enclosed by exact rationals from tan-half
endpoints (float tan widened by 1e-9 outward, the A43-G4 convention).  The dependence
B = w*(s0-w), w = cos+sin, is evaluated as a monotone function of w (NOT as a+b with independent
intervals) -- using independent intervals would inflate B enough to lose the [0,3) -> 9 sanity
check.  Every per-column bound is taken in the direction that can only INCREASE the count.
"""
from fractions import Fraction as F
import math, json, os

S0 = F(969271, 250000)
EPS = F(1, 10 ** 9)


def tanhalf(deg, up):
    """Rational bracket of tan(deg/2): widened outward by 1e-9 (A43-G4 float convention)."""
    if deg == 0:
        return F(0)
    v = F(math.tan(math.radians(deg) / 2))
    return v + EPS if up else max(F(0), v - EPS)


def cs_from_t(t):
    """(cos, sin) as exact rationals from the tan-half value t."""
    d = 1 + t * t
    return (1 - t * t) / d, 2 * t / d


def floorF(x):
    return x.numerator // x.denominator


def count_partition(bounds, a_lo, a_hi, b_lo, b_hi, B_hi):
    """bounds: increasing list of column boundaries over [0, B_hi], every width < 1.
    Region (bbox-local): vertices (0,b), (a,0), (B,B-b), (b,B); a+b = B.
      lower(x) = b(1-x/a) on [0,a], (x-a)a/b on [a,B]
      upper(x) = b + xa/b on [0,b],  B - (b/a)(x-b) on [b,B]
    Per column we bound  max upper  above and  min lower  below, over every theta in the bin."""
    tot = 0
    per = []
    for j in range(len(bounds) - 1):
        xl, xr = bounds[j], bounds[j + 1]
        if xl >= B_hi:
            per.append(0)
            continue
        UP = B_hi
        if xl >= b_hi and a_hi > 0:
            UP = min(UP, B_hi - (b_lo / a_hi) * (xl - b_hi))
        LO = F(0)
        if xr <= a_lo and a_lo > 0:
            LO = max(LO, b_lo * (1 - xr / a_lo))
        Y = UP - LO
        if Y < 0:
            per.append(0)
            continue
        c = 1 + floorF(Y)
        per.append(c)
        tot += c
    return tot, per


def partitions(B_hi):
    """Candidate column partitions of [0, B_hi], every width < 1.  Uniform for n = n_min..n_min+2
    plus a symmetric outer-width family for n_min (the corner-trimming one)."""
    n_min = floorF(B_hi) + 1
    out = []
    for n in (n_min, n_min + 1, n_min + 2):
        w = B_hi / n
        if w >= 1:
            continue
        out.append(('uniform_n%d' % n, [w * t for t in range(n + 1)]))
    n = n_min
    if n >= 3:
        for num, den in ((3, 4), (4, 5), (17, 20), (9, 10), (19, 20)):
            wo = F(num, den)
            rest = B_hi - 2 * wo
            if rest <= 0 or n - 2 <= 0:
                continue
            wi = rest / (n - 2)
            if wi >= 1 or wo >= 1 or wi <= 0:
                continue
            b = [F(0), wo] + [wo + wi * t for t in range(1, n - 1)] + [B_hi]
            out.append(('outer%s/%s_n%d' % (num, den, n), b))
    return out


def bin_bound(a_deg, b_deg, nsub=12):
    """m_ub for the bin = MAX over a sub-partition of the bin of the per-sub-bin certified bound.
    Sub-binning is sound (every theta lies in some sub-bin) and strictly tightens the interval
    arithmetic; nsub = 1 reproduces the single-interval evaluation."""
    subs = [_sub_bound(a_deg + (b_deg - a_deg) * F(t, nsub),
                       a_deg + (b_deg - a_deg) * F(t + 1, nsub)) for t in range(nsub)]
    best = max(subs, key=lambda r: r['m_ub'])
    best = dict(best)
    best['bin'] = [a_deg, b_deg]
    best['nsub'] = nsub
    best['per_sub_m_ub'] = [r['m_ub'] for r in subs]
    best['single_grain_residue_dies'] = best['m_ub'] <= 10
    return best


def _sub_bound(a_deg, b_deg):
    tlo, thi = tanhalf(a_deg, up=False), tanhalf(b_deg, up=True)
    c_hi, s_lo = cs_from_t(tlo)          # cos decreasing, sin increasing in theta
    c_lo, s_hi = cs_from_t(thi)
    w_lo, w_hi = c_lo + s_lo, c_hi + s_hi
    # w(theta) = cos+sin is increasing on [0,45]; evaluate at the endpoints
    w_lo = min(w_lo, cs_from_t(tlo)[0] + cs_from_t(tlo)[1])
    w_hi = max(w_hi, cs_from_t(thi)[0] + cs_from_t(thi)[1])
    A_lo, A_hi = S0 - w_hi, S0 - w_lo
    B_lo, B_hi = w_lo * (S0 - w_lo), w_hi * (S0 - w_hi)   # B = w(s0-w), increasing on [1,sqrt2]
    if B_hi < B_lo:
        B_lo, B_hi = B_hi, B_lo
    a_lo, a_hi = A_lo * c_lo, A_hi * c_hi
    b_lo, b_hi = A_lo * s_lo, A_hi * s_hi
    best = None
    for tag, bnds in partitions(B_hi):
        for (al, ah, bl, bh, t2) in ((a_lo, a_hi, b_lo, b_hi, tag),
                                     (b_lo, b_hi, a_lo, a_hi, tag + '_swap')):
            tot, per = count_partition(bnds, al, ah, bl, bh, B_hi)
            if best is None or tot < best[0]:
                best = (tot, t2, per)
    return dict(bin=[a_deg, b_deg], m_ub=best[0], partition=best[1], per_column=best[2],
                w_lo=str(w_lo), w_hi=str(w_hi), A_lo=str(A_lo), A_hi=str(A_hi),
                B_lo=str(B_lo), B_hi=str(B_hi), B_hi_float=float(B_hi),
                a=[float(a_lo), float(a_hi)], b=[float(b_lo), float(b_hi)],
                single_grain_residue_dies=(best[0] <= 10))


def table():
    rows = [bin_bound(3 * j, 3 * (j + 1)) for j in range(15)]
    return rows


if __name__ == '__main__':
    rows = table()
    for r in rows:
        print('[%2d,%2d) m_ub=%2d  %-16s cols=%s  %s'
              % (r['bin'][0], r['bin'][1], r['m_ub'], r['partition'], r['per_column'],
                 'DIES' if r['single_grain_residue_dies'] else 'GAP-A45-Z1 stands'))
    assert rows[0]['m_ub'] == 9, 'SANITY FAIL: bin [0,3) must give 9'
    print('sanity bin[0,3) = 9 OK')
