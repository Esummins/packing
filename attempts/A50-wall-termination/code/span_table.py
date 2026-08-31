"""A50 T1 -- span-semigroup tilt-exclusion table (EXACT arithmetic).

Spec: attempts/A50-wall-termination/notes/span_semigroup.md
      (Theorem S2 index sets, Theorem S3 window gap, variants V1 / V2 / E1).

Every certified quantity is exact: fractions.Fraction, or an integer-coefficient
quadratic (A t^2 + B t + C) plus a root index plus a rational enclosure refined by
exact-sign bisection.  Floats occur ONLY in fields whose key contains "_float".

Parametrisation: phi in (0,45] <-> t = tan(phi/2) in (0, sqrt2-1],
cos phi = (1-t^2)/(1+t^2), sin phi = 2t/(1+t^2).
Boundary of f_{abc}(phi) = a cos + b sin + c = w is the rational quadratic
      (c - w - a) t^2 + 2 b t + (a + c - w) = 0.
"""

from fractions import Fraction as F
from math import gcd, isqrt, atan, pi
import json
import os
import itertools

# ---------------------------------------------------------------- constants
S0 = F(969271, 250000)          # 3.877084  certified upper bound
LO = F(191, 50)                 # 3.82      certified lower bound
TOL = F(1, 10 ** 16)            # enclosure width target (< 1e-15)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RESULTS = os.path.join(ROOT, "results")


def deg_of_t(t):
    """float degrees phi = 2 atan(t) * 180/pi  -- READABILITY ONLY."""
    return 2.0 * atan(float(t)) * 180.0 / pi


# --------------------------------------------------- exact algebraic numbers
def norm_quad(A, B, C):
    """Rational (A,B,C) -> (primitive int A,B,C, flipped) with A>0, or A==0 and B>=0.

    `flipped` is True when the triple was negated (callers holding an inequality
    must then flip its sense)."""
    A, B, C = F(A), F(B), F(C)
    den = 1
    for x in (A, B, C):
        den = den * x.denominator // gcd(den, x.denominator)
    ai, bi, ci = int(A * den), int(B * den), int(C * den)
    g = gcd(gcd(abs(ai), abs(bi)), abs(ci))
    if g:
        ai, bi, ci = ai // g, bi // g, ci // g
    flipped = ai < 0 or (ai == 0 and bi < 0)
    if flipped:
        ai, bi, ci = -ai, -bi, -ci
    return ai, bi, ci, flipped


class Alg:
    """Root #idx (0 = smaller, 1 = larger) of the irreducible integer quadratic
    A t^2 + B t + C with A > 0 and non-square discriminant."""

    __slots__ = ("A", "B", "C", "idx", "lo", "hi")

    def __init__(self, A, B, C, idx):
        self.A, self.B, self.C, self.idx = A, B, C, idx
        D = B * B - 4 * A * C
        r = isqrt(D)                      # r <= sqrt(D) < r+1  (D not a square)
        v = F(-B, 2 * A)
        if idx == 1:
            self.lo, self.hi = v + F(r, 2 * A), v + F(r + 1, 2 * A)
        else:
            self.lo, self.hi = v - F(r + 1, 2 * A), v - F(r, 2 * A)
        self.refine(TOL)

    def key(self):
        return (self.A, self.B, self.C, self.idx)

    def p(self, t):
        return (self.A * t + self.B) * t + self.C

    def refine(self, eps):
        """Exact-sign bisection until hi - lo < eps."""
        while self.hi - self.lo >= eps:
            m = (self.lo + self.hi) / 2
            s = self.p(m)
            if s == 0:                     # impossible (irreducible) -- defensive
                raise AssertionError("rational root in irreducible quadratic")
            if self.idx == 1:
                if s < 0:
                    self.lo = m
                else:
                    self.hi = m
            else:
                if s > 0:
                    self.lo = m
                else:
                    self.hi = m

    def cmp_rat(self, q):
        """-1 if self < q, +1 if self > q  (never 0: self is irrational)."""
        if q <= self.lo:
            return 1
        if q >= self.hi:
            return -1
        s = self.p(q)
        if s < 0:                          # q strictly between the two roots
            return 1 if self.idx == 1 else -1
        v = F(-self.B, 2 * self.A)
        return 1 if q < v else -1

    def __float__(self):
        return float((self.lo + self.hi) / 2)

    def __repr__(self):
        return "Alg(%d,%d,%d;%d)~%.12f" % (self.A, self.B, self.C, self.idx, float(self))


class _Inf:
    __slots__ = ("s",)

    def __init__(self, s):
        self.s = s

    def __repr__(self):
        return "+inf" if self.s > 0 else "-inf"


NEG, POS = _Inf(-1), _Inf(1)


def cmp(x, y):
    """Total order on {Fraction} u {Alg} u {NEG, POS}."""
    if x is y:
        return 0
    if isinstance(x, _Inf) or isinstance(y, _Inf):
        xs = x.s if isinstance(x, _Inf) else 0
        ys = y.s if isinstance(y, _Inf) else 0
        return -1 if xs < ys else (1 if xs > ys else 0)
    if isinstance(x, F) and isinstance(y, F):
        return -1 if x < y else (1 if x > y else 0)
    if isinstance(x, Alg) and isinstance(y, F):
        return x.cmp_rat(y)
    if isinstance(x, F) and isinstance(y, Alg):
        return -y.cmp_rat(x)
    # Alg vs Alg: equal iff identical minimal polynomial and root index
    if x.key() == y.key():
        return 0
    eps = TOL
    while True:
        if x.hi <= y.lo:
            return -1
        if y.hi <= x.lo:
            return 1
        eps = eps / 1024
        x.refine(eps)
        y.refine(eps)


def rat_lb(x):
    return x.lo if isinstance(x, Alg) else x


def rat_ub(x):
    return x.hi if isinstance(x, Alg) else x


def quad_roots(A, B, C):
    """Exact real roots of rational A t^2 + B t + C, ascending (Fractions / Algs)."""
    A, B, C, _ = norm_quad(A, B, C)
    if A == 0:
        if B == 0:
            return []
        return [F(-C, B)]
    D = B * B - 4 * A * C
    if D < 0:
        return []
    r = isqrt(D)
    if r * r == D:
        if D == 0:
            return [F(-B, 2 * A)]
        return [F(-B - r, 2 * A), F(-B + r, 2 * A)]
    return [Alg(A, B, C, 0), Alg(A, B, C, 1)]


# ------------------------------------------------------------------ intervals
# interval = (lo, lo_closed, hi, hi_closed)
FULL = (NEG, False, POS, False)


def solve_ineq(A, B, C, sense):
    """Exact solution set of  A t^2 + B t + C  >= 0 ('ge')  or  <= 0 ('le')."""
    A, B, C, flipped = norm_quad(A, B, C)
    if flipped:
        sense = "le" if sense == "ge" else "ge"
    if A == 0:
        if B == 0:
            ok = (C >= 0) if sense == "ge" else (C <= 0)
            return [FULL] if ok else []
        r = F(-C, B)                        # B > 0 after normalisation
        return [(r, True, POS, False)] if sense == "ge" else [(NEG, False, r, True)]
    D = B * B - 4 * A * C
    if D < 0:                               # p > 0 everywhere
        return [FULL] if sense == "ge" else []
    if D == 0:
        r = F(-B, 2 * A)
        return [FULL] if sense == "ge" else [(r, True, r, True)]
    rts = quad_roots(A, B, C)
    r0, r1 = rts[0], rts[1]
    if sense == "le":
        return [(r0, True, r1, True)]
    return [(NEG, False, r0, True), (r1, True, POS, False)]


def _lo_max(a, b):
    """max of two lower ends ((point, closed)) -- closed loses ties."""
    c = cmp(a[0], b[0])
    if c > 0:
        return a
    if c < 0:
        return b
    return (a[0], a[1] and b[1])


def _hi_min(a, b):
    c = cmp(a[0], b[0])
    if c < 0:
        return a
    if c > 0:
        return b
    return (a[0], a[1] and b[1])


def _nonempty(lo, lc, hi, hc):
    c = cmp(lo, hi)
    if c < 0:
        return True
    if c > 0:
        return False
    return lc and hc


def inter2(xs, ys):
    """Intersect two interval lists (each sorted, disjoint)."""
    out = []
    for (al, alc, ah, ahc) in xs:
        for (bl, blc, bh, bhc) in ys:
            lo, lc = _lo_max((al, alc), (bl, blc))
            hi, hc = _hi_min((ah, ahc), (bh, bhc))
            if _nonempty(lo, lc, hi, hc):
                out.append((lo, lc, hi, hc))
    out.sort(key=_sort_key)
    return out


def _sort_key(iv):
    return _CmpKey(iv[0])


class _CmpKey:
    __slots__ = ("v",)

    def __init__(self, v):
        self.v = v

    def __lt__(self, other):
        return cmp(self.v, other.v) < 0


def interval_len_float(iv):
    lo, hi = iv[0], iv[2]
    return float(rat_ub(hi)) - float(rat_lb(lo))


# ---------------------------------------------------- Theorem S2 index sets
def multisets(Lmax):
    """(n1,n2,n3,n4,c) with n1+..+n4 >= 2 and L = n1+..+n4+c in [3, Lmax]."""
    out = []
    for n1 in range(Lmax + 1):
        for n2 in range(Lmax + 1 - n1):
            for n3 in range(Lmax + 1 - n1 - n2):
                for n4 in range(Lmax + 1 - n1 - n2 - n3):
                    nt = n1 + n2 + n3 + n4
                    if nt < 2:
                        continue
                    for c in range(Lmax + 1 - nt):
                        L = nt + c
                        if 3 <= L <= Lmax:
                            out.append((n1, n2, n3, n4, c))
    return out


def index_set(Lmax):
    """A(Lmax) = { (a,b,c) } with a = n1+n3+n4, b = n2+n3-n4."""
    s = set()
    for (n1, n2, n3, n4, c) in multisets(Lmax):
        s.add((n1 + n3 + n4, n2 + n3 - n4, c))
    return sorted(s)


# ------------------------------------- per-triple admitted set in t-space
T45 = Alg(1, 2, -1, 1)                      # sqrt2 - 1 = tan(45/2)
DOMAIN = [(F(0), False, T45, True)]         # phi in (0, 45]


def f_at(a, b, c, t):
    """Exact f_{abc}(t) = a cos + b sin + c at rational t."""
    return (a * (1 - t * t) + 2 * b * t + c * (1 + t * t)) / (1 + t * t)


def triple_set(a, b, c, lo=LO, hi=S0):
    """{ t in (0, t45] : lo <= f_{abc}(t) <= hi }, exact interval list."""
    ge = solve_ineq(c - lo - a, 2 * b, a + c - lo, "ge")     # f >= lo
    le = solve_ineq(c - hi - a, 2 * b, a + c - hi, "le")     # f <= hi
    return inter2(inter2(ge, le), DOMAIN)


# ------------------------------------------------------------- arrangement
def _idx_of(uniq, p):
    """Index of p in the sorted unique breakpoint list (binary search, exact cmp)."""
    lo, hi = 0, len(uniq) - 1
    while lo <= hi:
        m = (lo + hi) // 2
        c = cmp(uniq[m], p)
        if c == 0:
            return m
        if c < 0:
            lo = m + 1
        else:
            hi = m - 1
    raise AssertionError("breakpoint not found")


def arrangement(sets):
    """sets: list of (label, interval-list).  Atomic cell decomposition of the
    domain (0, t45] with, per cell, the labels covering it.
    Cells alternate: open (p_i, p_{i+1}), point {p_{i+1}}, ..."""
    pts = [F(0), T45]
    for _, ivs in sets:
        for (l, _, h, _) in ivs:
            pts.append(l)
            pts.append(h)
    pts.sort(key=_CmpKey)
    uniq = []
    for p in pts:
        if not uniq or cmp(uniq[-1], p) != 0:
            uniq.append(p)
    n = len(uniq)
    # integer-indexed intervals per label
    idx_sets = []
    for lab, ivs in sets:
        idx_sets.append((lab, [(_idx_of(uniq, l), lc, _idx_of(uniq, h), hc)
                               for (l, lc, h, hc) in ivs]))
    cells, hits = [], []
    for i in range(n - 1):
        cells.append(((uniq[i], False, uniq[i + 1], False), ("open", i)))
        cells.append(((uniq[i + 1], True, uniq[i + 1], True), ("pt", i + 1)))
    out = []
    for cell, tag in cells:
        kind, i = tag
        hit = []
        for lab, ivs in idx_sets:
            for (li, lc, hi_, hc) in ivs:
                if kind == "open":
                    if li <= i and hi_ >= i + 1:
                        hit.append(lab)
                        break
                else:
                    if (li < i or (li == i and lc)) and (hi_ > i or (hi_ == i and hc)):
                        hit.append(lab)
                        break
        out.append((cell, hit))
    return out


def union_merge(ivs):
    """Union of a list of intervals (closed ends merge when touching)."""
    if not ivs:
        return []
    ivs = sorted(ivs, key=_sort_key)
    out = [list(ivs[0])]
    for (l, lc, h, hc) in ivs[1:]:
        cl, clc, ch, chc = out[-1]
        c = cmp(l, ch)
        if c < 0 or (c == 0 and (lc or chc)):
            c2 = cmp(h, ch)
            if c2 > 0:
                out[-1][2], out[-1][3] = h, hc
            elif c2 == 0:
                out[-1][3] = chc or hc
        else:
            out.append([l, lc, h, hc])
    return [tuple(x) for x in out]


def measure_float(ivs):
    return sum(interval_len_float(iv) for iv in ivs)


def measure_deg_float(ivs):
    return sum(deg_of_t(float(rat_ub(iv[2]))) - deg_of_t(float(rat_lb(iv[0])))
               for iv in ivs)


def merge_cells(cells):
    """Merge consecutive cells with the same admitted/excluded status."""
    runs = []
    for cell, hit in cells:
        adm = bool(hit)
        if runs and runs[-1][0] == adm:
            runs[-1][1].append((cell, hit))
        else:
            runs.append((adm, [(cell, hit)]))
    out = []
    for adm, group in runs:
        lo, lc = group[0][0][0], group[0][0][1]
        hi, hc = group[-1][0][2], group[-1][0][3]
        hits = set()
        for cell, hit in group:
            hits.update(hit)
        out.append((adm, (lo, lc, hi, hc), sorted(hits)))
    return out


def witness(iv):
    """A rational strictly inside iv (or the point itself if iv is a rational point)."""
    lo, lc, hi, hc = iv
    if cmp(lo, hi) == 0:
        return lo if isinstance(lo, F) else None
    for _ in range(60):
        a, b = rat_ub(lo), rat_lb(hi)
        if a < b:
            return (a + b) / 2
        eps = (TOL if not isinstance(lo, Alg) else (lo.hi - lo.lo)) / 1024
        if isinstance(lo, Alg):
            lo.refine(eps)
        if isinstance(hi, Alg):
            hi.refine(max(eps, F(1, 10 ** 40)))
    return None


# ------------------------------------------------------------ serialisation
def ser_point(x):
    if isinstance(x, F):
        return {"kind": "rational", "num": str(x.numerator), "den": str(x.denominator),
                "_float_t": float(x), "_float_deg": deg_of_t(x)}
    return {"kind": "quadratic", "A": str(x.A), "B": str(x.B), "C": str(x.C),
            "root_index": x.idx,
            "enclosure": {"lo_num": str(x.lo.numerator), "lo_den": str(x.lo.denominator),
                          "hi_num": str(x.hi.numerator), "hi_den": str(x.hi.denominator)},
            "_float_t": float(x), "_float_deg": deg_of_t(float(x))}


def ser_rat(x):
    return {"num": str(x.numerator), "den": str(x.denominator), "_float": float(x)}


def ser_iv(iv, extra=None):
    d = {"lo": ser_point(iv[0]), "lo_closed": iv[1],
         "hi": ser_point(iv[2]), "hi_closed": iv[3],
         "_float_deg_lo": deg_of_t(float(rat_lb(iv[0]))),
         "_float_deg_hi": deg_of_t(float(rat_ub(iv[2])))}
    d["_float_deg_width"] = d["_float_deg_hi"] - d["_float_deg_lo"]
    if extra:
        d.update(extra)
    return d


# ======================================================= equal-class columns
def build_column(Lmax):
    """Equal-class MONOTONE table on (0,45], chain-length cap Lmax."""
    A = index_set(Lmax)
    sets = [(trip, triple_set(*trip)) for trip in A]
    cells = arrangement(sets)
    merged = merge_cells(cells)
    admitted, excluded = [], []
    idx_of_trip = {t: i for i, t in enumerate(A)}
    for adm, iv, hits in merged:
        w = witness(iv)
        extra = {"witness_t": ser_rat(w) if w is not None else None}
        if adm:
            extra["hitting_triples"] = [list(t) for t in hits]
            extra["hitting_triple_indices"] = sorted(idx_of_trip[t] for t in hits)
            if w is not None:
                wt = [i for i, t in enumerate(A) if LO <= f_at(*t, w) <= S0]
                extra["witness_hitting_triple_indices"] = wt
                assert wt, "admitted cell with no witness hit"
            admitted.append(ser_iv(iv, extra))
        else:
            below, above = [], []
            assert w is not None, "excluded interval without rational witness"
            for i, t in enumerate(A):
                v = f_at(*t, w)
                if v < LO:
                    below.append(i)
                elif v > S0:
                    above.append(i)
                else:
                    raise AssertionError("triple hits window inside excluded cell")
            extra["exclusion_sides"] = {"below_lo": below, "above_hi": above}
            excluded.append(ser_iv(iv, extra))
    adm_ivs = [(x, y, z, u) for (a, (x, y, z, u), h) in merged if a]
    exc_ivs = [(x, y, z, u) for (a, (x, y, z, u), h) in merged if not a]
    return {
        "index_set": [list(t) for t in A],
        "index_set_size": len(A),
        "admitted_intervals": admitted,
        "excluded_intervals": excluded,
        "_float_admitted_measure_t": measure_float(adm_ivs),
        "_float_excluded_measure_t": measure_float(exc_ivs),
        "_float_admitted_measure_deg": measure_deg_float(adm_ivs),
        "_float_excluded_measure_deg": measure_deg_float(exc_ivs),
    }


# ============================================================ V1 window class
def cos_t(t):
    return (1 - t * t) / (1 + t * t)


def sin_t(t):
    return 2 * t / (1 + t * t)


def hulls(tu, tv):
    """Per-step hulls over the tilt window t in [tu, tv] (0 <= tu <= tv).
    cos decreasing, sin increasing, cos+sin increasing, cos-sin decreasing in phi."""
    cu, su = cos_t(tu), sin_t(tu)
    cv, sv = cos_t(tv), sin_t(tv)
    return {
        "cos": (cv, cu),
        "sin": (su, sv),
        "cps": (cu + su, cv + sv),
        "cms": (cv - sv, cu - su),
        "one": (F(1), F(1)),
        "mix": (cv - sv, cv + sv),      # mixed-normal link hull (E1)
    }


def window_span_interval(ms, H, m=0):
    """Reachable span interval of multiset ms=(n1,n2,n3,n4,c) with m mixed links."""
    n1, n2, n3, n4, c = ms
    lo = (n1 * H["cos"][0] + n2 * H["sin"][0] + n3 * H["cps"][0]
          + n4 * H["cms"][0] + c + m * H["mix"][0])
    hi = (n1 * H["cos"][1] + n2 * H["sin"][1] + n3 * H["cps"][1]
          + n4 * H["cms"][1] + c + m * H["mix"][1])
    return lo, hi


def window_excluded(tu, tv, Lmax, m=0):
    """True iff EVERY multiset's reachable span interval misses [LO, S0]."""
    H = hulls(tu, tv)
    for ms in multisets_cache(Lmax, m):
        lo, hi = window_span_interval(ms, H, m)
        if not (hi < LO or lo > S0):
            return False, ms
    return True, None


_MSC = {}


def multisets_cache(Lmax, m=0):
    """(n1,n2,n3,n4,c) with n1+..+n4 >= 2 and L = n1+..+n4+c+m in [3, Lmax];
    m mixed-normal links occupy m further chain slots (E1)."""
    key = (Lmax, m)
    if key in _MSC:
        return _MSC[key]
    cap = Lmax - m
    out = []
    for n1 in range(cap + 1):
        for n2 in range(cap + 1 - n1):
            for n3 in range(cap + 1 - n1 - n2):
                for n4 in range(cap + 1 - n1 - n2 - n3):
                    nt = n1 + n2 + n3 + n4
                    if nt < 2:
                        continue
                    for c in range(cap + 1 - nt):
                        if 3 <= nt + c + m <= Lmax:
                            out.append((n1, n2, n3, n4, c))
    _MSC[key] = out
    return out


def band_set(a1, b1, c1, a2, b2, c2):
    """{ t in (0,t45] : f_{a1b1c1} >= LO  and  f_{a2b2c2} <= S0 }."""
    ge = solve_ineq(c1 - LO - a1, 2 * b1, a1 + c1 - LO, "ge")
    le = solve_ineq(c2 - S0 - a2, 2 * b2, a2 + c2 - S0, "le")
    return inter2(inter2(ge, le), DOMAIN)


# ------------------------------------------------- V1 near-flush corollary
def theta_star():
    """Root in (0,45) of 4(cos - sin) = s0, i.e. (4+s0) t^2 + 8 t - (4-s0) = 0."""
    A, B, C, _ = norm_quad(4 + S0, 8, -(4 - S0))
    rts = quad_roots(A, B, C)
    pos = [r for r in rts if cmp(r, F(0)) > 0]
    assert len(pos) == 1, pos
    return pos[0], (A, B, C)


def near_flush_audit(v, Lmax, m=0):
    """Every multiset's reachable span over the window class [0, v] misses [LO,S0]?"""
    H = hulls(F(0), v)
    entries, below, above = [], 0, 0
    tight_below = tight_above = None
    for ms in multisets_cache(Lmax, m):
        lo, hi = window_span_interval(ms, H, m)
        if hi < LO:
            entries.append([*ms, "max_below_lo"])
            below += 1
            if tight_below is None or hi > tight_below[1]:
                tight_below = (ms, hi)
        elif lo > S0:
            entries.append([*ms, "min_above_hi"])
            above += 1
            if tight_above is None or lo < tight_above[1]:
                tight_above = (ms, lo)
        else:
            entries.append([*ms, "HITS_WINDOW"])
    return {
        "n_multisets": len(entries),
        "n_max_below_lo": below,
        "n_min_above_hi": above,
        "n_hits_window": len(entries) - below - above,
        "excluded": below + above == len(entries),
        "tightest_below_lo": ({"multiset": list(tight_below[0]),
                               "max_span": ser_rat(tight_below[1])}
                              if tight_below else None),
        "tightest_above_hi": ({"multiset": list(tight_above[0]),
                               "min_span": ser_rat(tight_above[1])}
                              if tight_above else None),
        "entries": entries,
    }


# ------------------------------------------------------------- V1 sweep
def t_mark(deg):
    """Exact rational t whose float degree is within 1e-6 of `deg`."""
    from math import tan
    if deg <= 0:
        return F(0)
    t = F(tan(deg * pi / 360.0)).limit_denominator(10 ** 9)
    assert abs(deg_of_t(t) - deg) < 1e-6, (deg, deg_of_t(t))
    return t


def v1_sweep(Lmax=6, widths=(F(1, 2), F(1), F(2)), step=F(1, 4), top=45):
    out = {}
    for w in widths:
        rows = []
        u = step
        while u < top:
            v = min(u + w, F(top))
            tu, tv = t_mark(float(u)), t_mark(float(v))
            exc, wit = window_excluded(tu, tv, Lmax)
            rows.append({"_float_u_deg": float(u), "_float_v_deg": float(v),
                         "tu": ser_rat(tu), "tv": ser_rat(tv),
                         "status": "EXCLUDED" if exc else "ADMITTED"})
            u += step
        out["w=%s" % w] = {
            "width_deg": str(w),
            "Lmax": Lmax,
            "n_windows": len(rows),
            "n_excluded": sum(1 for r in rows if r["status"] == "EXCLUDED"),
            "excluded_windows": [[r["_float_u_deg"], r["_float_v_deg"]]
                                 for r in rows if r["status"] == "EXCLUDED"],
            "rows": rows,
        }
    return out


# ---------------------------------------------------------- V2 signed variant
def signed_index_set(Lmax):
    steps = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
    res = set()
    cur = {(0, 0)}
    reach = {0: {(0, 0)}}
    for k in range(1, Lmax + 1):
        cur = {(a + d[0], b + d[1]) for (a, b) in cur for d in steps}
        reach[k] = cur
    for nt in range(2, Lmax + 1):
        for c0 in range(0, Lmax - nt + 1):
            if nt + c0 < 3:
                continue
            cvals = list(range(-c0, c0 + 1, 2)) if c0 > 0 else [0]
            for (a, b) in reach[nt]:
                for c in cvals:
                    res.add((a, b, c))
    return sorted(res)


def union_over_triples(triples, mixed=0):
    ivs = []
    for (a, b, c) in triples:
        if mixed:
            s = band_set(a + mixed, b + mixed, c, a + mixed, b - mixed, c)
        else:
            s = triple_set(a, b, c)
        ivs.extend(s)
    return union_merge(ivs)


def e1_index_set(Lmax, m):
    s = set()
    for (n1, n2, n3, n4, c) in multisets_cache(Lmax, m):
        s.add((n1 + n3 + n4, n2 + n3 - n4, c))
    return sorted(s)


# --------------------------------------------------------------------- main
def main():
    os.makedirs(RESULTS, exist_ok=True)
    A6, A8 = index_set(6), index_set(8)
    print("|A(6)| =", len(A6), " |A(8)| =", len(A8))
    assert len(A6) == 172, "A(6) size %d != 172 (spec Theorem S2)" % len(A6)

    col6 = build_column(6)
    print("L<=6: excluded intervals:", len(col6["excluded_intervals"]),
          " excluded deg:", round(col6["_float_excluded_measure_deg"], 6))
    col8 = build_column(8)
    print("L<=8: excluded intervals:", len(col8["excluded_intervals"]),
          " excluded deg:", round(col8["_float_excluded_measure_deg"], 6))

    ts, tsq = theta_star()
    ts_deg = deg_of_t(float(ts))
    print("theta* = %.6f deg" % ts_deg)
    assert 1.73 < ts_deg < 1.74, "theta* out of expected range: %r" % ts_deg
    v = ts.lo if isinstance(ts, Alg) else ts        # rational just below theta*
    assert cmp(ts, v) > 0
    nf = {
        "definition": "root in (0,45) of 4(cos phi - sin phi) = s0",
        "quadratic": {"A": str(tsq[0]), "B": str(tsq[1]), "C": str(tsq[2]),
                      "root_index": ts.idx if isinstance(ts, Alg) else None},
        "theta_star_t": ser_point(ts),
        "_float_theta_star_deg": ts_deg,
        "v_rational_just_below": ser_rat(v),
        "_float_v_deg": deg_of_t(v),
        "cos_v": ser_rat(cos_t(v)), "sin_v": ser_rat(sin_t(v)),
        "four_cos_minus_sin_at_v": ser_rat(4 * (cos_t(v) - sin_t(v))),
        "audit_L6": near_flush_audit(v, 6),
        "audit_L8": near_flush_audit(v, 8),
        "audit_L6_mixed_m1": near_flush_audit(v, 6, m=1),
        "audit_L6_mixed_m2": near_flush_audit(v, 6, m=2),
    }
    for k in ("audit_L6", "audit_L8", "audit_L6_mixed_m1", "audit_L6_mixed_m2"):
        assert nf[k]["excluded"], "near-flush exclusion FAILED for " + k
    print("near-flush exclusion OK (L6/L8/E1 m=1,2)")

    sweep = v1_sweep()
    for k, vv in sweep.items():
        print("V1 sweep %s: %d/%d windows excluded" % (k, vv["n_excluded"], vv["n_windows"]))

    sg = signed_index_set(6)
    sg_adm = union_over_triples(sg)
    v2 = {"index_set_size": len(sg),
          "_float_admitted_measure_t": measure_float(sg_adm),
          "_float_admitted_measure_deg": measure_deg_float(sg_adm),
          "_float_domain_measure_t": float(T45.hi),
          "_float_domain_measure_deg": 45.0,
          "admitted_intervals": [ser_iv(iv) for iv in sg_adm]}
    print("V2 signed: %d triples, admitted %.6f of 45 deg"
          % (len(sg), v2["_float_admitted_measure_deg"]))

    e1 = {}
    all_ivs = []
    base = union_over_triples(A6)
    all_ivs.extend(base)
    for m in (1, 2):
        tr = e1_index_set(6, m)
        u = union_over_triples(tr, mixed=m)
        all_ivs.extend(u)
        e1["m=%d" % m] = {"index_set_size": len(tr),
                          "_float_admitted_measure_deg": measure_deg_float(u),
                          "admitted_intervals": [ser_iv(iv) for iv in u]}
        print("E1 m=%d: %d triples, admitted %.6f deg" % (m, len(tr),
              e1["m=%d" % m]["_float_admitted_measure_deg"]))
    tot = union_merge(all_ivs)
    e1["union_m_0_1_2"] = {"_float_admitted_measure_deg": measure_deg_float(tot),
                           "admitted_intervals": [ser_iv(iv) for iv in tot]}
    e1["near_flush_survives"] = {
        "m=1": nf["audit_L6_mixed_m1"]["excluded"],
        "m=2": nf["audit_L6_mixed_m2"]["excluded"]}
    print("E1 union m in {0,1,2}: admitted %.6f deg"
          % e1["union_m_0_1_2"]["_float_admitted_measure_deg"])

    doc = {
        "spec": "attempts/A50-wall-termination/notes/span_semigroup.md",
        "constants": {"s0": ser_rat(S0), "lo": ser_rat(LO),
                      "t45": ser_point(T45),
                      "enclosure_width_target": ser_rat(TOL),
                      "parametrisation": "t = tan(phi/2); cos=(1-t^2)/(1+t^2), sin=2t/(1+t^2)",
                      "boundary_quadratic": "(c-w-a) t^2 + 2 b t + (a+c-w) = 0"},
        "index_set_sizes": {"A6": len(A6), "A8": len(A8),
                            "multisets_L6": len(multisets(6)),
                            "multisets_L8": len(multisets(8))},
        "columns": {"L6": col6, "L8": col8},
        "near_flush_exclusion": nf,
        "v1_sweep": sweep,
        "v2_signed": v2,
        "e1_mixed": e1,
    }
    path = os.path.join(RESULTS, "span_table.json")
    with open(path, "w") as fh:
        json.dump(doc, fh, indent=1)
    print("wrote", path, os.path.getsize(path), "bytes")


if __name__ == "__main__":
    main()
