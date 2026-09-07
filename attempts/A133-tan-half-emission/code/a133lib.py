"""A133 -- the local certificate in t = tan(theta/2): exact rational geometry.

Everything in this module is EXACT rational arithmetic (`fractions.Fraction`).  There is no pi,
no Taylor series, no dyadic interval kernel and no float in any decision path: with

    cos theta = (1 - t^2)/(1 + t^2),      sin theta = 2 t/(1 + t^2)

the separating-axis geometry of `docs/proofs/local_certificate.md` is a RATIONAL function of the
tilt parameters, and every enclosure a local certificate needs is the exact range of a rational
function over a rational cell.

The pieces, in the order the certificate uses them:

  * `cosT`/`sinT`, `cos_range`/`sin_range` -- exact, by monotonicity on t in [0, 1]
    (theta in [0 deg, 90 deg], which is the fundamental domain a packed square is normalised to).
  * `wfun_u`/`w_range` -- w(Delta) = |cos Delta| + |sin Delta| as a function of u = tan(Delta/2),
    and its EXACT range over a u-interval (the interior maximum sqrt(2) at u = sqrt(2) - 1 is
    located by a rational comparison, and only its VALUE needs a rational upper bound of sqrt 2).
  * `u_of`, `u_range` -- u = tan((theta_w - theta_o)/2) = (t_w - t_o)/(1 + t_w t_o), monotone in
    each argument, so its range over a cell product is again the endpoint values.
  * `bern1`/`bern2` -- Bernstein coefficients of a polynomial on an interval / box.  All
    Bernstein coefficients >= 0 implies the polynomial is >= 0 there; the test is the certificate
    of every affine bound below, is decidable in exact rational arithmetic, and is sharpened by
    recursive subdivision (`poly_nonneg_1`, `poly_nonneg_2`).
  * `aff_lower_w` / `aff_upper_S` / `chord_h` -- the three affine envelopes Lemma RELAX needs,
    each returned with the exact rational coefficients and verified by the Bernstein test.

Finding E3 disappears here: a tilt cell that leaves [0 deg, 90 deg] is a LIST of t-intervals and
this module never needs a single interval to hold it (the generator keeps the part inside the
fundamental domain, which makes N smaller and `LocalDead` weaker -- the sound direction).
"""
from __future__ import annotations

from fractions import Fraction as Q

# ----------------------------------------------------------------- constants
# a rational UPPER bound of sqrt 2 (14142135623730951/10^16 squared is 2 + 2.4e-17 > 2)
SQRT2_HI = Q(14142135623730951, 10 ** 16)
assert SQRT2_HI * SQRT2_HI > 2
HALF = Q(1, 2)

# Bernstein subdivision depths of the two envelope families.  The SAME depths are used by the
# independent checker and by the Lean checker, so a bound emitted here is verified there by the
# identical decidable test.
DEPTH1 = 2          # univariate (h's chord, S's affine enclosure)
DEPTH2 = 1          # bivariate (w's affine lower bound)


def _chk(cond, msg):
    if not cond:
        raise AssertionError(msg)


# ----------------------------------------------------------------- intervals
class IQ:
    """A closed interval with exact rational endpoints."""
    __slots__ = ("lo", "hi")

    def __init__(self, lo, hi=None):
        if hi is None:
            hi = lo
        self.lo, self.hi = Q(lo), Q(hi)
        _chk(self.lo <= self.hi, "empty interval")

    def __repr__(self):
        return "[%s, %s]" % (float(self.lo), float(self.hi))

    def __add__(self, o):
        o = o if isinstance(o, IQ) else IQ(o)
        return IQ(self.lo + o.lo, self.hi + o.hi)

    def __sub__(self, o):
        o = o if isinstance(o, IQ) else IQ(o)
        return IQ(self.lo - o.hi, self.hi - o.lo)

    def __neg__(self):
        return IQ(-self.hi, -self.lo)

    def __mul__(self, o):
        o = o if isinstance(o, IQ) else IQ(o)
        p = (self.lo * o.lo, self.lo * o.hi, self.hi * o.lo, self.hi * o.hi)
        return IQ(min(p), max(p))

    __rmul__ = __mul__
    __radd__ = __add__

    def contains(self, x):
        return self.lo <= x <= self.hi

    def absmax(self):
        return max(abs(self.lo), abs(self.hi))


# ----------------------------------------------------------------- the t parametrisation
def cosT(t: Q) -> Q:
    t = Q(t)
    return (1 - t * t) / (1 + t * t)


def sinT(t: Q) -> Q:
    t = Q(t)
    return 2 * t / (1 + t * t)


def cos_range(a: Q, b: Q) -> IQ:
    """exact range of cos theta over t in [a, b] subset [0, 1] (cosT is decreasing there)."""
    _chk(0 <= a <= b <= 1, "cos_range outside the fundamental domain")
    return IQ(cosT(b), cosT(a))


def sin_range(a: Q, b: Q) -> IQ:
    """exact range of sin theta over t in [a, b] subset [0, 1] (sinT is increasing there)."""
    _chk(0 <= a <= b <= 1, "sin_range outside the fundamental domain")
    return IQ(sinT(a), sinT(b))


def axis_pt(t: Q, k: int):
    """the owner's axis a_k(theta) at the rational tilt parameter t -- exactly rational."""
    c, s = cosT(t), sinT(t)
    return (c, s) if k == 0 else (-s, c)


def axis_range(a: Q, b: Q, k: int):
    c, s = cos_range(a, b), sin_range(a, b)
    return (c, s) if k == 0 else (-s, c)


def u_of(tw: Q, to: Q) -> Q:
    """u = tan((theta_w - theta_o)/2) = (t_w - t_o)/(1 + t_w t_o)."""
    d = 1 + tw * to
    _chk(d > 0, "u_of: degenerate denominator")
    return (tw - to) / d


def u_range(aw: Q, bw: Q, ao: Q, bo: Q) -> IQ:
    """exact range of u over the cell product: u is increasing in t_w, decreasing in t_o."""
    return IQ(u_of(aw, bo), u_of(bw, ao))


def wfun_u(u: Q) -> Q:
    """w = |cos Delta| + |sin Delta| in terms of u = tan(Delta/2), for |Delta| <= 90 deg."""
    u = Q(u)
    return (1 - u * u + 2 * abs(u)) / (1 + u * u)


def w_range(iv: IQ) -> IQ:
    """EXACT range of w over a u-interval (|u| <= 1, i.e. |Delta| <= 90 deg).

    w is a function of |u| alone, increasing on [0, sqrt 2 - 1] and decreasing after, with the
    interior maximum sqrt 2.  The location test `alo <= sqrt2 - 1 <= ahi` is the rational
    comparison `(alo + 1)^2 <= 2 <= (ahi + 1)^2`; only the VALUE sqrt 2 needs a rational bound.
    """
    lo, hi = iv.lo, iv.hi
    _chk(-1 <= lo <= hi <= 1, "w_range: |u| > 1 (cell wider than 90 deg)")
    if lo <= 0 <= hi:
        alo, ahi = Q(0), max(-lo, hi)
    else:
        a1, a2 = abs(lo), abs(hi)
        alo, ahi = min(a1, a2), max(a1, a2)
    wlo = min(wfun_u(alo), wfun_u(ahi))
    if (alo + 1) ** 2 <= 2 <= (ahi + 1) ** 2:
        whi = SQRT2_HI
    else:
        whi = max(wfun_u(alo), wfun_u(ahi))
    return IQ(wlo, whi)


def w_range_cell(aw: Q, bw: Q, ao: Q, bo: Q) -> IQ:
    return w_range(u_range(aw, bw, ao, bo))


def half_width(t: Q) -> Q:
    """h(t) = (|cos theta| + |sin theta|)/2 for t in [0, 1]."""
    return wfun_u(t) / 2


# ----------------------------------------------------------------- polynomials, Bernstein
def p_mul(p, q):
    out = [Q(0)] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        if a:
            for j, b in enumerate(q):
                if b:
                    out[i + j] += a * b
    return out


def p_add(p, q):
    n = max(len(p), len(q))
    return [(p[i] if i < len(p) else Q(0)) + (q[i] if i < len(q) else Q(0)) for i in range(n)]


def p_scale(p, c):
    return [c * a for a in p]


def p_eval(p, x):
    r = Q(0)
    for a in reversed(p):
        r = r * x + a
    return r


_BINOM = {}


def binom(n, k):
    v = _BINOM.get((n, k))
    if v is None:
        v = 1
        for i in range(k):
            v = v * (n - i) // (i + 1)
        _BINOM[(n, k)] = v
    return v


def bern1(p, a: Q, b: Q):
    """Bernstein coefficients of the univariate polynomial `p` (monomial coefficient list,
    ascending) on [a, b].  If every coefficient is >= 0 then p >= 0 on [a, b], because the
    Bernstein basis functions are nonnegative there and sum to 1."""
    n = len(p) - 1
    if n < 0:
        return [Q(0)]
    # p(a + (b-a) x) in the monomial basis of x in [0, 1]
    h = b - a
    q = [Q(0)] * (n + 1)
    for c in reversed(p):                      # q <- q * (a + h x) + c, degree stays <= n
        new = [Q(0)] * (n + 1)
        for i in range(n + 1):
            if q[i]:
                new[i] += q[i] * a
                if i + 1 <= n:
                    new[i + 1] += q[i] * h
        new[0] += c
        q = new
    # monomial -> Bernstein on [0, 1]:  b_k = sum_{i<=k} C(k,i)/C(n,i) q_i
    out = []
    for k in range(n + 1):
        s = Q(0)
        for i in range(k + 1):
            s += Q(binom(k, i), binom(n, i)) * q[i]
        out.append(s)
    return out


def poly_nonneg_1(p, a: Q, b: Q, depth: int = DEPTH1) -> bool:
    """decide (sufficiently) that p >= 0 on [a, b] by Bernstein with recursive subdivision."""
    if a > b:
        return True
    bc = bern1(p, a, b)
    if all(c >= 0 for c in bc):
        return True
    if depth <= 0:
        return False
    m = (a + b) / 2
    return poly_nonneg_1(p, a, m, depth - 1) and poly_nonneg_1(p, m, b, depth - 1)


# -- bivariate: coefficient grid P[i][j] for t_w^i t_o^j
def p2_zero(nw, no):
    return [[Q(0)] * (no + 1) for _ in range(nw + 1)]


def p2_add(P, R):
    nw = max(len(P), len(R)) - 1
    no = max(max(len(r) for r in P), max(len(r) for r in R)) - 1
    out = p2_zero(nw, no)
    for G in (P, R):
        for i, row in enumerate(G):
            for j, c in enumerate(row):
                out[i][j] += c
    return out


def p2_mul(P, R):
    nw = len(P) + len(R) - 2
    no = max(len(r) for r in P) + max(len(r) for r in R) - 2
    out = p2_zero(nw, no)
    for i, row in enumerate(P):
        for j, c in enumerate(row):
            if not c:
                continue
            for k, row2 in enumerate(R):
                for l, d in enumerate(row2):
                    if d:
                        out[i + k][j + l] += c * d
    return out


def p2_scale(P, c):
    return [[c * a for a in row] for row in P]


def bern2(P, aw, bw, ao, bo):
    """Bernstein coefficients of a bivariate polynomial on the box (tensor product)."""
    nw = len(P) - 1
    no = max(len(r) for r in P) - 1
    G = [[(P[i][j] if j < len(P[i]) else Q(0)) for j in range(no + 1)] for i in range(nw + 1)]
    # transform in t_o for each fixed power of t_w
    G2 = [bern1(G[i], ao, bo) for i in range(nw + 1)]
    # ... but bern1 acts on a monomial list; the rows of G ARE monomial in t_o.  Now the columns
    # are still monomial in t_w, and the Bernstein transform is linear, so transform columns.
    cols = []
    for j in range(no + 1):
        col = [G2[i][j] for i in range(nw + 1)]
        cols.append(bern1(col, aw, bw))
    return [[cols[j][i] for j in range(no + 1)] for i in range(nw + 1)]


def poly_nonneg_2(P, aw, bw, ao, bo, depth: int = DEPTH2) -> bool:
    if aw > bw or ao > bo:
        return True
    bc = bern2(P, aw, bw, ao, bo)
    if all(c >= 0 for row in bc for c in row):
        return True
    if depth <= 0:
        return False
    mw, mo = (aw + bw) / 2, (ao + bo) / 2
    for (x0, x1) in ((aw, mw), (mw, bw)):
        for (y0, y1) in ((ao, mo), (mo, bo)):
            if not poly_nonneg_2(P, x0, x1, y0, y1, depth - 1):
                return False
    return True


# ----------------------------------------------------------------- the three affine envelopes
def chord_h(a: Q, b: Q):
    """(m, c) with h(t) >= m t + c on [a, b] subset [0, 1], h = (cos + sin)/2.

    h is CONCAVE on [0, 1] (h'' = (t^3 + 3t^2 - 3t - 1)/(1+t^2)^3 = (t-1)(t^2+4t+1)/(1+t^2)^3
    <= 0 there), so the chord through the two endpoint values -- both exact rationals -- lies
    below h.  Verified independently by the Bernstein test on
        p(t) = (1 + 2t - t^2) - 2 (m t + c) (1 + t^2)  >= 0.
    """
    _chk(0 <= a <= b <= 1, "chord_h outside [0, 1]")
    if a == b:
        return Q(0), half_width(a)
    fa, fb = half_width(a), half_width(b)
    m = (fb - fa) / (b - a)
    c = fa - m * a
    _chk(verify_h_lower(m, c, a, b), "chord_h: Bernstein test failed")
    return m, c


def verify_h_lower(m: Q, c: Q, a: Q, b: Q, depth: int = DEPTH1) -> bool:
    """h(t) >= m t + c on [a, b]?  (1 + 2t - t^2) - 2(m t + c)(1 + t^2) >= 0, 1 + t^2 > 0."""
    p = p_add([Q(1), Q(2), Q(-1)], p_scale(p_mul([c, m], [Q(1), Q(0), Q(1)]), Q(-2)))
    return poly_nonneg_1(p, a, b, depth)


def sinphi_poly(tm: Q):
    """S(t) = sin(theta(t) - theta(tm)) = N(t)/(1 + t^2) with N = 2 c_m t + s_m t^2 - s_m."""
    cm, sm = cosT(tm), sinT(tm)
    return [-sm, 2 * cm, sm]          # ascending coefficients of N


def sinphi(tm: Q, t: Q) -> Q:
    return p_eval(sinphi_poly(tm), t) / (1 + t * t)


def aff_bounds_S(tm: Q, a: Q, b: Q, tol_bits: int = 60):
    """(alpha, beta_up, beta_lo) with

        alpha t + beta_lo  <=  S(t)  <=  alpha t + beta_up      on [a, b],

    `alpha` the secant slope of S, the two offsets the exact rational extremes tightened by
    bisection against the Bernstein test.  Second order in the cell width, as the corresponding
    step of A119's relaxation is in the angle.
    """
    N = sinphi_poly(tm)
    if a == b:
        v = sinphi(tm, a)
        return Q(0), v, v
    alpha = (sinphi(tm, b) - sinphi(tm, a)) / (b - a)
    D = [Q(1), Q(0), Q(1)]                                   # 1 + t^2 > 0
    M = p_add(N, p_scale(p_mul([Q(0), alpha], D), Q(-1)))     # N - alpha t (1 + t^2)
    hi = bern_ratio_1(M, D, a, b, DEPTH1, True)
    lo = bern_ratio_1(M, D, a, b, DEPTH1, False)
    return alpha, hi, lo


def _pad2(P, nw, no):
    return [[(P[i][j] if i < len(P) and j < len(P[i]) else Q(0)) for j in range(no)]
            for i in range(nw)]


def bern_ratio_1(P, D, a: Q, b: Q, depth: int, want_max: bool):
    """over [a, b], subdivided `depth` times: the max (resp. min) of `bern(P)_i / bern(D)_i`.

    `D` must have strictly positive Bernstein coefficients on every subbox.  Taking `beta` = the
    MAX makes `beta D - P` Bernstein-nonnegative on every subbox, i.e. certifies `P <= beta D`;
    taking the MIN certifies `P >= beta D`.  This replaces a bisection by one linear pass and is
    exactly as sharp as the subdivided Bernstein test itself.
    """
    n = max(len(P), len(D))
    P = P + [Q(0)] * (n - len(P))       # degree elevation: the Bernstein form in the COMMON
    D = D + [Q(0)] * (n - len(D))       # degree, so the two coefficient lists are aligned
    best = None
    stack = [(a, b, depth)]
    while stack:
        x0, x1, d = stack.pop()
        bp, bd = bern1(P, x0, x1), bern1(D, x0, x1)
        for u, v in zip(bp, bd):
            _chk(v > 0, "bern_ratio_1: denominator not positive")
            r = u / v
            if best is None or (r > best if want_max else r < best):
                best = r
        if d > 0:
            m = (x0 + x1) / 2
            stack.append((x0, m, d - 1))
            stack.append((m, x1, d - 1))
    return best


def bern_ratio_2(P, D, aw: Q, bw: Q, ao: Q, bo: Q, depth: int, want_max: bool):
    """the bivariate form of `bern_ratio_1` on a box."""
    nw = max(len(P), len(D))
    no = max(max(len(r) for r in P), max(len(r) for r in D))
    P = _pad2(P, nw, no)
    D = _pad2(D, nw, no)
    best = None
    stack = [(aw, bw, ao, bo, depth)]
    while stack:
        x0, x1, y0, y1, d = stack.pop()
        bp, bd = bern2(P, x0, x1, y0, y1), bern2(D, x0, x1, y0, y1)
        for rp, rd in zip(bp, bd):
            for u, v in zip(rp, rd):
                _chk(v > 0, "bern_ratio_2: denominator not positive")
                r = u / v
                if best is None or (r > best if want_max else r < best):
                    best = r
        if d > 0:
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            for (p0, p1) in ((x0, mx), (mx, x1)):
                for (q0, q1) in ((y0, my), (my, y1)):
                    stack.append((p0, p1, q0, q1, d - 1))
    return best


def _tighten(ok, base: Q, direction: int, step: Q, rounds: int = 40):
    """smallest (direction +1) / largest (direction -1) offset beyond `base` that passes `ok`.

    `ok` is MONOTONE in the offset (moving further in `direction` only weakens the claim), so a
    doubling search followed by bisection converges to the tight value from the safe side; the
    value returned always passes `ok`.
    """
    if ok(base):
        return base
    bad, k = base, 0
    while True:
        good = base + direction * step * (1 << k)
        if ok(good):
            break
        bad, k = good, k + 1
        if k > 44:
            raise AssertionError("_tighten: no valid offset found")
    for _ in range(rounds):
        mid = (good + bad) / 2
        if ok(mid):
            good = mid
        else:
            bad = mid
    return good


def verify_S_upper(alpha: Q, beta: Q, a: Q, b: Q, N=None, depth: int = DEPTH1) -> bool:
    """S(t) <= alpha t + beta on [a, b]?  (alpha t + beta)(1 + t^2) - N(t) >= 0."""
    p = p_add(p_mul([beta, alpha], [Q(1), Q(0), Q(1)]), p_scale(N, Q(-1)))
    return poly_nonneg_1(p, a, b, depth)


def verify_S_lower(alpha: Q, beta: Q, a: Q, b: Q, N=None, depth: int = DEPTH1) -> bool:
    """S(t) >= alpha t + beta on [a, b]?  N(t) - (alpha t + beta)(1 + t^2) >= 0."""
    p = p_add(N, p_scale(p_mul([beta, alpha], [Q(1), Q(0), Q(1)]), Q(-1)))
    return poly_nonneg_1(p, a, b, depth)


# -- w's affine lower bounds over the cell product
def w_num_poly(eps: int):
    """the numerator of W_eps = cos Delta + eps sin Delta, as a bivariate polynomial in
    (t_w, t_o) over the common denominator (1 + t_w^2)(1 + t_o^2):

        (1 + t_w t_o)^2 - (t_w - t_o)^2 + 2 eps (t_w - t_o)(1 + t_w t_o).

    `w = |cos Delta| + |sin Delta| >= W_{+1}` and `>= W_{-1}` on the WHOLE cell (cos Delta >= 0
    for |Delta| <= 90 deg, and |sin| >= +-sin), and `max(W_{+1}, W_{-1}) = w`.  So the two
    numerators are the exact analogue of A119's two V-lines and need no kink location at all.
    """
    one_tt = [[Q(1), Q(0)], [Q(0), Q(1)]]                                      # 1 + t_w t_o
    diff = [[Q(0), Q(-1)], [Q(1), Q(0)]]                                       # t_w - t_o
    P = p2_add(p2_mul(one_tt, one_tt), p2_scale(p2_mul(diff, diff), Q(-1)))
    P = p2_add(P, p2_scale(p2_mul(diff, one_tt), Q(2 * eps)))
    return P


def den2_poly():
    """(1 + t_w^2)(1 + t_o^2)."""
    return [[Q(1), Q(0), Q(1)], [Q(0), Q(0), Q(0)], [Q(1), Q(0), Q(1)]]


def aff_lower_w(eps: int, aw: Q, bw: Q, ao: Q, bo: Q, depth: int = DEPTH2):
    """(mw, mo, c) with w(t_w, t_o) >= mw t_w + mo t_o + c on the cell product.

    The slopes are the secant slopes of W_eps in each variable through the box corners (exact
    rationals); the offset is tightened by bisection against the bivariate Bernstein test.
    """
    N = w_num_poly(eps)
    D = den2_poly()

    def W(tw, to):
        return (cosT(tw) * cosT(to) + sinT(tw) * sinT(to)) \
            + eps * (sinT(tw) * cosT(to) - cosT(tw) * sinT(to))

    mw = Q(0) if bw == aw else (W(bw, (ao + bo) / 2) - W(aw, (ao + bo) / 2)) / (bw - aw)
    mo = Q(0) if bo == ao else (W((aw + bw) / 2, bo) - W((aw + bw) / 2, ao)) / (bo - ao)
    L = [[Q(0), mo], [mw, Q(0)]]
    M = p2_add(N, p2_scale(p2_mul(L, D), Q(-1)))              # N - (mw t_w + mo t_o) D
    c = bern_ratio_2(M, D, aw, bw, ao, bo, depth, False)
    return mw, mo, c


def verify_w_lower(eps: int, mw: Q, mo: Q, c: Q, aw: Q, bw: Q, ao: Q, bo: Q, depth: int = DEPTH2) -> bool:
    """W_eps(t_w, t_o) >= mw t_w + mo t_o + c on the box?  N - (mw t_w + mo t_o + c) D >= 0."""
    N = w_num_poly(eps)
    D = den2_poly()
    L = [[c, mo], [mw, Q(0)]]
    P = p2_add(N, p2_scale(p2_mul(L, D), Q(-1)))
    return poly_nonneg_2(P, aw, bw, ao, bo, depth)
