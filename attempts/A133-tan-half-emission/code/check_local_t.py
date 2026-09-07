"""A133 T1 -- the INDEPENDENT checker of a t = tan(theta/2) local certificate.

    python check_local_t.py ../certs/<id>.tcert.json.gz [more...]

This program shares NO code with the generator: it does not import `a133lib`, `gen_local_t`,
`a116lib`, `a119lib`, `numpy`, `scipy` or any LP solver.  It re-implements the geometry of
`docs/proofs/local_certificate.md` in the tan-half parametrisation, in exact rational arithmetic
(`fractions.Fraction`), and decides whether the certificate PROVES

    Dead_{L u P}(N, s0):  no interior-disjoint configuration of the |L| + |P| bodies of N, with
    every body in its box / slack core and the side s in [s_lo, s_hi], has s <= s0.

Two deliberate differences from the generator, which is what makes the check independent:

  * the certificate's affine envelopes (Lemma RELAX's three families: the chord of the wall
    half-width `h`, the two-sided affine enclosure of `sin(theta(t) - theta(t*))`, and the two
    affine lower bounds of `w = |cos D| + |sin D|`) are not re-derived but VERIFIED, each by a
    decision procedure of this file's own: the two univariate families EXACTLY, by Sturm's
    theorem on the square-free part, and the bivariate one by a subdivided Bernstein test written
    here from the definition and subdivided deeper than the generator's;
  * the emitted row is never trusted: for every row a Farkas multiplier names, the checker builds
    its OWN row out of the verified envelopes and requires `min over the leaf's box of
    (own - emitted) >= 0`, i.e. that the emitted row is IMPLIED by a row this program derived
    itself.  Only then is the emitted row used in the Farkas bound.

NO EARLY RETURN anywhere (A126's finding E2 is impossible to reproduce here by construction, and
this program is written so that it could not hide one either): every node of the tree is walked,
every leaf is checked, every failure is recorded and counted, and the verdict is the conjunction
at the end.  Exit code 0 iff every certificate passes.
"""
from __future__ import annotations

import gzip, hashlib, json, os, sys, time
from fractions import Fraction as Q

S0 = Q(969271, 250000)
SELS8 = [(o, k, e) for o in (0, 1) for k in (0, 1) for e in (1, -1)]
SUBDIV = 32          # interval-arithmetic subdivisions used to verify an affine envelope
SQRT2_HI = Q(14142135623730951, 10 ** 16)


# ---------------------------------------------------------------- exact intervals
class I:
    __slots__ = ("lo", "hi")

    def __init__(self, lo, hi=None):
        self.lo = Q(lo)
        self.hi = Q(lo if hi is None else hi)

    def __add__(self, o):
        o = o if isinstance(o, I) else I(o)
        return I(self.lo + o.lo, self.hi + o.hi)

    def __sub__(self, o):
        o = o if isinstance(o, I) else I(o)
        return I(self.lo - o.hi, self.hi - o.lo)

    def __mul__(self, o):
        o = o if isinstance(o, I) else I(o)
        p = (self.lo * o.lo, self.lo * o.hi, self.hi * o.lo, self.hi * o.hi)
        return I(min(p), max(p))

    __rmul__ = __mul__

    def __truediv__(self, o):
        if o.lo <= 0 <= o.hi:
            raise ZeroDivisionError("interval division through zero")
        return self * I(1 / o.hi, 1 / o.lo)

    def __repr__(self):
        return "[%s,%s]" % (float(self.lo), float(self.hi))


def ev_poly_iv(p, iv: I) -> I:
    """centred (mean-value) evaluation of a monomial polynomial over an interval -- second order
    in the interval width, and a different algorithm from the generator's Bernstein form."""
    m = (iv.lo + iv.hi) / 2
    r = I(iv.lo - m, iv.hi - m)
    # Taylor coefficients about m by repeated synthetic division
    c, work = [], list(p)
    while work:
        acc = Q(0)
        for i in range(len(work) - 1, -1, -1):
            acc = acc * m + work[i]
        c.append(acc)
        # divide by (x - m)
        nw = [Q(0)] * (len(work) - 1)
        carry = Q(0)
        for i in range(len(work) - 1, 0, -1):
            carry = work[i] + carry * m if i < len(work) - 1 else work[i]
            nw[i - 1] = carry
        work = nw
    out = I(c[0])
    pw = I(1)
    for k in range(1, len(c)):
        pw = pw * r
        out = out + I(c[k]) * pw
    return out


def poly_range_1(p, a: Q, b: Q, n: int = SUBDIV) -> I:
    lo = hi = None
    h = (b - a) / n
    for i in range(n):
        iv = ev_poly_iv(p, I(a + i * h, a + (i + 1) * h))
        lo = iv.lo if lo is None else min(lo, iv.lo)
        hi = iv.hi if hi is None else max(hi, iv.hi)
    return I(lo, hi)


def poly_range_2(P, aw: Q, bw: Q, ao: Q, bo: Q, n: int = 8) -> I:
    """range of a bivariate monomial grid over a box, by subdivided centred evaluation in t_o of
    the univariate polynomials obtained by centred evaluation in t_w."""
    lo = hi = None
    hw, ho = (bw - aw) / n, (bo - ao) / n
    for i in range(n):
        ivw = I(aw + i * hw, aw + (i + 1) * hw)
        # collapse t_w: coefficients of t_o^j become intervals
        no = max(len(r) for r in P)
        cw = []
        for j in range(no):
            col = [(P[i2][j] if j < len(P[i2]) else Q(0)) for i2 in range(len(P))]
            cw.append(ev_poly_iv(col, ivw))
        for j in range(n):
            ivo = I(ao + j * ho, ao + (j + 1) * ho)
            acc = I(0)
            pw = I(1)
            for t in range(no):
                acc = acc + cw[t] * pw
                pw = pw * ivo
            lo = acc.lo if lo is None else min(lo, acc.lo)
            hi = acc.hi if hi is None else max(hi, acc.hi)
    return I(lo, hi)


# ---------------------------------------------------------------- the t geometry
def cT(t: Q) -> Q:
    return (1 - t * t) / (1 + t * t)


def sT(t: Q) -> Q:
    return 2 * t / (1 + t * t)


def wfun(u: Q) -> Q:
    return (1 - u * u + 2 * abs(u)) / (1 + u * u)


def hw_of(t: Q) -> Q:
    return wfun(t) / 2


def cos_iv(a: Q, b: Q) -> I:
    assert 0 <= a <= b <= 1
    return I(cT(b), cT(a))


def sin_iv(a: Q, b: Q) -> I:
    assert 0 <= a <= b <= 1
    return I(sT(a), sT(b))


def axis_iv(a: Q, b: Q, k: int):
    c, s = cos_iv(a, b), sin_iv(a, b)
    return (c, s) if k == 0 else (I(-s.hi, -s.lo), c)


def axis_pt(t: Q, k: int):
    c, s = cT(t), sT(t)
    return (c, s) if k == 0 else (-s, c)


def uu(tw: Q, to: Q) -> Q:
    return (tw - to) / (1 + tw * to)


def w_iv(aw: Q, bw: Q, ao: Q, bo: Q) -> I:
    ul, uh = uu(aw, bo), uu(bw, ao)
    assert -1 <= ul <= uh <= 1
    if ul <= 0 <= uh:
        alo, ahi = Q(0), max(-ul, uh)
    else:
        alo, ahi = min(abs(ul), abs(uh)), max(abs(ul), abs(uh))
    lo = min(wfun(alo), wfun(ahi))
    hi = SQRT2_HI if (alo + 1) ** 2 <= 2 <= (ahi + 1) ** 2 else max(wfun(alo), wfun(ahi))
    return I(lo, hi)


# ---------------------------------------------------------------- affine forms
class Aff:
    __slots__ = ("co", "k")

    def __init__(self, co=None, k=Q(0)):
        self.co = dict(co or {})
        self.k = Q(k)

    def __add__(self, o):
        c = dict(self.co)
        for v, a in o.co.items():
            c[v] = c.get(v, Q(0)) + a
        return Aff(c, self.k + o.k)

    def __sub__(self, o):
        c = dict(self.co)
        for v, a in o.co.items():
            c[v] = c.get(v, Q(0)) - a
        return Aff(c, self.k - o.k)

    def scale(self, f):
        f = Q(f)
        return Aff({v: a * f for v, a in self.co.items()}, self.k * f) if f else Aff()

    def rng(self, box) -> I:
        lo = hi = self.k
        for v, a in self.co.items():
            bl, bh = box[v]
            if a >= 0:
                lo += a * bl; hi += a * bh
            else:
                lo += a * bh; hi += a * bl
        return I(lo, hi)


def V(v):
    return Aff({v: Q(1)})


def C(x):
    return Aff({}, Q(x))


# ---------------------------------------------------------------- exact univariate positivity
def p_trim(p):
    q = list(p)
    while q and q[-1] == 0:
        q.pop()
    return q


def p_ev(p, x: Q) -> Q:
    r = Q(0)
    for a in reversed(p):
        r = r * x + a
    return r


def p_der(p):
    return p_trim([i * p[i] for i in range(1, len(p))])


def p_rem(a, b):
    a, b = p_trim(a), p_trim(b)
    db = len(b) - 1
    while a and len(a) - 1 >= db:
        f = a[-1] / b[-1]
        sh = len(a) - 1 - db
        for i in range(len(b)):
            a[i + sh] -= f * b[i]
        a = p_trim(a)
    return a


def p_gcd(a, b):
    a, b = p_trim(a), p_trim(b)
    while b:
        a, b = b, p_rem(a, b)
    return a


def p_div(a, b):
    a, b = p_trim(a), p_trim(b)
    db = len(b) - 1
    q = [Q(0)] * max(1, len(a) - db)
    while a and len(a) - 1 >= db:
        f = a[-1] / b[-1]
        sh = len(a) - 1 - db
        q[sh] = f
        for i in range(len(b)):
            a[i + sh] -= f * b[i]
        a = p_trim(a)
    return p_trim(q)


def _sturm_chain(p):
    ch = [p_trim(p)]
    d = p_der(p)
    if not d:
        return ch
    ch.append(d)
    while True:
        r = p_rem(ch[-2], ch[-1])
        if not r:
            break
        ch.append([-c for c in r])
    return ch


def _sturm_V(ch, x: Q):
    s, v = 0, 0
    for f in ch:
        val = p_ev(f, x)
        if val == 0:
            continue
        sg = 1 if val > 0 else -1
        if s and sg != s:
            v += 1
        s = sg
    return v


def sturm_nonneg(p, a: Q, b: Q) -> bool:
    """EXACT decision of `p(t) >= 0 for every t in [a, b]`, by Sturm's theorem on the square-free
    part.  A different algorithm from the generator's Bernstein test, and a COMPLETE one: a valid
    envelope is always confirmed and an invalid one is always caught.

    The interval is bisected until each piece holds at most one distinct root of `p`; on such a
    piece the sign of `p` on either side of the root is its sign at the adjacent endpoint, so
    testing `p` at the endpoints and the midpoints of the pieces decides the question.
    """
    p = p_trim(p)
    if not p:
        return True
    g = p_gcd(p, p_der(p))
    q = p_div(p, g) if len(g) > 1 else p
    ch = _sturm_chain(q)
    if len(ch) == 1:
        return p_ev(p, a) >= 0 and p_ev(p, b) >= 0 and p_ev(p, (a + b) / 2) >= 0
    stack = [(a, b)]
    pts = {a, b}
    guard = 0
    while stack:
        u, v = stack.pop()
        guard += 1
        if guard > 100000:
            return False
        n = _sturm_V(ch, u) - _sturm_V(ch, v)
        if n <= 1:
            pts.add(u); pts.add(v)
            continue
        m = (u + v) / 2
        stack.append((u, m)); stack.append((m, v))
    ptl = sorted(pts)
    for x in ptl:
        if p_ev(p, x) < 0:
            return False
    for i in range(len(ptl) - 1):
        if p_ev(p, (ptl[i] + ptl[i + 1]) / 2) < 0:
            return False
    return True


# ---------------------------------------------------------------- Bernstein, this file's own
_BC = {}


def _binom(n, k):
    v = _BC.get((n, k))
    if v is None:
        v = 1
        for i in range(k):
            v = v * (n - i) // (i + 1)
        _BC[(n, k)] = v
    return v


def _bern1(p, a: Q, b: Q):
    n = len(p) - 1
    q = [Q(0)] * (n + 1)
    h = b - a
    for c in reversed(p):
        new = [Q(0)] * (n + 1)
        for i in range(n + 1):
            if q[i]:
                new[i] += q[i] * a
                if i + 1 <= n:
                    new[i + 1] += q[i] * h
        new[0] += c
        q = new
    out = []
    for k in range(n + 1):
        s = Q(0)
        for i in range(k + 1):
            s += Q(_binom(k, i), _binom(n, i)) * q[i]
        out.append(s)
    return out


def bern_nonneg_2(P, aw, bw, ao, bo, depth=3) -> bool:
    """`P >= 0` on the box, by subdivided tensor-product Bernstein: all Bernstein coefficients
    nonnegative on a sub-box implies `P >= 0` there, and the sub-boxes cover.  Written here from
    the definition and subdivided DEEPER than the generator's own test; subdivision only sharpens
    the bound, so a bound the generator certified is certified here too."""
    nw = len(P) - 1
    no = max(len(r) for r in P) - 1
    G = [[(P[i][j] if j < len(P[i]) else Q(0)) for j in range(no + 1)] for i in range(nw + 1)]
    stack = [(aw, bw, ao, bo, depth)]
    while stack:
        x0, x1, y0, y1, d = stack.pop()
        rows = [_bern1(G[i], y0, y1) for i in range(nw + 1)]
        ok = True
        for j in range(no + 1):
            col = _bern1([rows[i][j] for i in range(nw + 1)], x0, x1)
            if any(c < 0 for c in col):
                ok = False
                break
        if ok:
            continue
        if d <= 0:
            return False
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        for (p0, p1) in ((x0, mx), (mx, x1)):
            for (q0, q1) in ((y0, my), (my, y1)):
                stack.append((p0, p1, q0, q1, d - 1))
    return True


# ---------------------------------------------------------------- the three envelopes, VERIFIED
def _grid_mul(P, R):
    nw = len(P) + len(R) - 1
    no = max(len(r) for r in P) + max(len(r) for r in R) - 1
    out = [[Q(0)] * no for _ in range(nw)]
    for i, row in enumerate(P):
        for j, c in enumerate(row):
            if not c:
                continue
            for k, row2 in enumerate(R):
                for l, d in enumerate(row2):
                    if d:
                        out[i + k][j + l] += c * d
    return out


def _w_num(eps: int):
    """(1 + tw to)^2 - (tw - to)^2 + 2 eps (tw - to)(1 + tw to): the numerator of
    W_eps = cos D + eps sin D over the common denominator (1 + tw^2)(1 + to^2).  Both branches
    are lower bounds of w = |cos D| + |sin D| on the whole cell, and their maximum IS w."""
    P = [[Q(0)] * 3 for _ in range(3)]

    def add(i, j, c):
        P[i][j] += Q(c)
    add(0, 0, 1); add(1, 1, 2); add(2, 2, 1)
    add(2, 0, -1); add(1, 1, 2); add(0, 2, -1)
    add(1, 0, 2 * eps); add(2, 1, 2 * eps); add(0, 1, -2 * eps); add(1, 2, -2 * eps)
    return P


def _w_den():
    P = [[Q(0)] * 3 for _ in range(3)]
    P[0][0] = P[0][2] = P[2][0] = P[2][2] = Q(1)
    return P


def verify_h(m: Q, c: Q, a: Q, b: Q) -> bool:
    """h(t) = (1 + 2t - t^2)/(2(1 + t^2)) >= m t + c on [a, b]?  Exactly, by Sturm."""
    return sturm_nonneg([Q(1) - 2 * c, Q(2) - 2 * m, Q(-1) - 2 * c, -2 * m], a, b)


def verify_S(alpha: Q, bup: Q, blo: Q, a: Q, b: Q) -> bool:
    """alpha t + blo <= sin(theta(t) - theta(tm)) <= alpha t + bup on [a, b], with tm the cell
    midpoint?  Exactly, by Sturm on the two cubics."""
    tm = (a + b) / 2
    cm, sm = cT(tm), sT(tm)
    N = [-sm, 2 * cm, sm]
    up = [bup - N[0], alpha - N[1], bup - N[2], alpha]             # (alpha t + bup)(1+t^2) - N
    dn = [N[0] - blo, N[1] - alpha, N[2] - blo, -alpha]            # N - (alpha t + blo)(1+t^2)
    return sturm_nonneg(up, a, b) and sturm_nonneg(dn, a, b)


def verify_w(eps: int, mw: Q, mo: Q, c: Q, aw: Q, bw: Q, ao: Q, bo: Q) -> bool:
    """W_eps(tw, to) >= mw tw + mo to + c on the cell product?  N - (mw tw + mo to + c) D >= 0,
    decided by this file's own subdivided Bernstein test."""
    N, D = _w_num(eps), _w_den()
    Lp = [[c, mo], [mw, Q(0)]]
    M = _grid_mul(Lp, D)
    nw = max(len(M), len(N))
    no = max(max(len(r) for r in M), max(len(r) for r in N))
    P = [[(N[i][j] if i < len(N) and j < len(N[i]) else Q(0))
          - (M[i][j] if i < len(M) and j < len(M[i]) else Q(0))
          for j in range(no)] for i in range(nw)]
    return bern_nonneg_2(P, aw, bw, ao, bo)

# ---------------------------------------------------------------- bodies
class Body:
    def __init__(self, d):
        self.name, self.kind, self.vi = d["name"], d["kind"], d["vi"]
        if self.kind == "free":
            self.ti = d["ti"]
            self.x0, self.x1 = Q(d["x0"]), Q(d["x1"])
            self.y0, self.y1 = Q(d["y0"]), Q(d["y1"])
            self.t0, self.t1 = Q(d["t0"]), Q(d["t1"])
        else:
            self.ti = None
            self.ax = (Q(d["ax"][0]), Q(d["ax"][1]))
            self.ay = (Q(d["ay"][0]), Q(d["ay"][1]))
            self.hh = Q(d["hh"])

    def centre(self):
        if self.kind == "pin":
            return (Aff({0: self.ax[1], self.vi: Q(1)}, self.ax[0]),
                    Aff({0: self.ay[1], self.vi + 1: Q(1)}, self.ay[0]))
        return V(self.vi), V(self.vi + 1)

    def cell(self, cells):
        return (Q(0), Q(0)) if self.kind == "pin" else cells[self.name]

    def taff(self):
        return Aff() if self.kind == "pin" else V(self.ti)

    def xy(self, s_lo, s_hi):
        if self.kind == "pin":
            return ((self.ax[0] + self.ax[1] * s_lo - self.hh, self.ax[0] + self.ax[1] * s_hi + self.hh),
                    (self.ay[0] + self.ay[1] * s_lo - self.hh, self.ay[0] + self.ay[1] * s_hi + self.hh))
        return ((self.x0, self.x1), (self.y0, self.y1))


# ---------------------------------------------------------------- the checker
class Checker:
    def __init__(self, cert, only_leaf=None):
        # `only_leaf` restricts the (expensive) row rebuild to ONE leaf; the tree walk, the
        # envelope verification and the leaf-reference bookkeeping are unaffected.  It exists
        # for `control133.py`, which re-checks thousands of one-leaf mutants; a full run never
        # sets it.
        self.only_leaf = only_leaf
        self.c = cert
        self.m = cert["meta"]
        self.bodies = [Body(d) for d in self.m["bodies"]]
        self.by = {b.name: b for b in self.bodies}
        self.idx = {b.name: i for i, b in enumerate(self.bodies)}
        self.nv = self.m["nv"]
        self.s_lo, self.s_hi = Q(self.m["s_lo"]), Q(self.m["s_hi"])
        self.box0 = {0: (self.s_lo, self.s_hi)}
        for b in self.bodies:
            if b.kind == "free":
                self.box0[b.vi] = (b.x0, b.x1)
                self.box0[b.vi + 1] = (b.y0, b.y1)
            else:
                self.box0[b.vi] = (-b.hh, b.hh)
                self.box0[b.vi + 1] = (-b.hh, b.hh)
        self.xyr = {b.name: b.xy(self.s_lo, self.s_hi) for b in self.bodies}
        self.leaves = cert["leaves"]
        self.seen = [0] * len(self.leaves)
        self.n = dict(nodes=0, bisect=0, branch=0, imp=0, imp_sel=0, dead=0, infeas=0,
                      excluded=0, forced=0, rows=0, mult=0, rows_implied=0)
        self.errors = []
        self.min_bound = None
        self._gc = {}
        env = cert.get("env") or {}
        self.envh = {k: tuple(Q(x) for x in v) for k, v in (env.get("h") or {}).items()}
        self.envS = {k: tuple(Q(x) for x in v) for k, v in (env.get("S") or {}).items()}
        self.envw = {k: tuple(Q(x) for x in v) for k, v in (env.get("w") or {}).items()}
        self.n["env_h"] = self.n["env_S"] = self.n["env_w"] = 0

    def fail(self, msg):
        self.errors.append(msg)

    # -- the certificate's affine envelopes, each VERIFIED here before it is used
    def verify_env(self):
        """decide every entry of the certificate's envelope table.  `h` and `S` are decided
        EXACTLY (Sturm); `w` by this file's own subdivided Bernstein test."""
        for key, (m, c) in self.envh.items():
            a, b = (Q(x) for x in key.split("|"))
            self.n["env_h"] += 1
            if not verify_h(m, c, a, b):
                self.fail("env h[%s]: h is not above %s t + %s on the cell" % (key, m, c))
        for key, (al, bu, bl) in self.envS.items():
            a, b = (Q(x) for x in key.split("|"))
            self.n["env_S"] += 1
            if not verify_S(al, bu, bl, a, b):
                self.fail("env S[%s]: sin(theta(t) - theta(tm)) is not enclosed" % key)
        for key, (mw, mo, c) in self.envw.items():
            p = key.split("|")
            eps = int(p[0])
            aw, bw, ao, bo = (Q(x) for x in p[1:])
            self.n["env_w"] += 1
            if not verify_w(eps, mw, mo, c, aw, bw, ao, bo):
                self.fail("env w[%s]: w is not above the recorded plane on the cell product" % key)

    def h_env(self, a, b):
        v = self.envh.get("%s|%s" % (a, b))
        if v is None:
            self.fail("no h envelope recorded for the cell [%s, %s]" % (a, b))
            return Q(0), Q(0)
        return v

    def S_env(self, a, b):
        v = self.envS.get("%s|%s" % (a, b))
        if v is None:
            self.fail("no S envelope recorded for the cell [%s, %s]" % (a, b))
            return Q(0), Q(0), Q(0)
        return v

    def W_env(self, eps, aw, bw, ao, bo):
        v = self.envw.get("%d|%s|%s|%s|%s" % (eps, aw, bw, ao, bo))
        if v is None:
            self.fail("no w envelope recorded for eps=%d on [%s,%s]x[%s,%s]"
                      % (eps, aw, bw, ao, bo))
            return Q(0), Q(0), Q(0)
        return v

    def cellbox(self, cells):
        bx = dict(self.box0)
        for b in self.bodies:
            if b.kind == "free":
                bx[b.ti] = cells[b.name]
        return bx

    def root_cells(self):
        return {b.name: (b.t0, b.t1) for b in self.bodies if b.kind == "free"}

    # -- the selection gap enclosure
    def gap(self, bw, bo, k, eps, cells):
        key = (bw.name, bo.name, k, eps,
               cells.get(bw.name), cells.get(bo.name))
        v = self._gc.get(key)
        if v is not None:
            return v
        twl, twh = bw.cell(cells)
        tol, toh = bo.cell(cells)
        ax, ay = axis_iv(twl, twh, k)
        (xwl, xwh), (ywl, ywh) = self.xyr[bw.name]
        (xol, xoh), (yol, yoh) = self.xyr[bo.name]
        DX = I(xol - xwh, xoh - xwl)
        DY = I(yol - ywh, yoh - ywl)
        w = w_iv(twl, twh, tol, toh)
        g = I(eps) * (DX * ax + DY * ay) - I(Q(1, 2)) - I(Q(1, 2)) * w
        self._gc[key] = g
        return g

    def excluded_ok(self, cells, nm1, nm2, keep):
        b1, b2 = self.by[nm1], self.by[nm2]
        bad = []
        for (o, k, e) in SELS8:
            if (o, k, e) in keep:
                continue
            if b1.kind == "pin" and b2.kind == "pin" and o == 1:
                continue
            bw, bo = (b1, b2) if o == 0 else (b2, b1)
            g = self.gap(bw, bo, k, e, cells)
            self.n["excluded"] += 1
            if g.hi >= 0:
                bad.append(((o, k, e), g.hi))
        return bad

    # -- Lemma RELAX, this program's own implementation
    def rows_of(self, cells, sel_by_pair, want):
        """rebuild exactly the rows named in `want` (a set of key tuples)."""
        out = {}
        box = self.cellbox(cells)
        for b in self.bodies:
            cx, cy = b.centre()
            if b.kind == "pin":
                m, c = Q(0), Q(1, 2)
            else:
                a, bb = cells[b.name]
                m, c = self.h_env(a, bb)
            hb = b.taff().scale(m) + C(c)
            for (cc, nm) in ((cx, "x"), (cy, "y")):
                out[("w", b.name, nm, "lo")] = C(0) - cc + hb
                out[("w", b.name, nm, "hi")] = cc - V(0) + hb
        for kp, sel in sel_by_pair.items():
            nm1, nm2 = kp.split("|")
            o, k, eps = sel
            b1, b2 = self.by[nm1], self.by[nm2]
            bw, bo = (b1, b2) if o == 0 else (b2, b1)
            cxw, cyw = bw.centre(); cxo, cyo = bo.centre()
            dcx, dcy = cxo - cxw, cyo - cyw
            aw, bwid = bw.cell(cells)
            ao, boh = bo.cell(cells)
            tm = (aw + bwid) / 2
            Ax, Ay = axis_pt(tm, k)
            P = (dcx.scale(Ax) + dcy.scale(Ay)).scale(eps)
            QQ = (dcx.scale(-Ay) + dcy.scale(Ax)).scale(eps)
            pr, qr = P.rng(box), QQ.rng(box)
            if bw.kind == "pin" or aw == bwid:
                corr = Q(0)
                Us = [(Aff(), "A")]
            else:
                ul, uh = uu(aw, tm), uu(bwid, tm)
                U = max(abs(ul), abs(uh))
                corr = max(Q(0), -pr.lo) * (2 * U * U / (1 + U * U))
                Slo, Shi = sT(ul), sT(uh)
                Slo, Shi = min(Slo, Shi), max(Slo, Shi)
                Sabs = max(abs(Slo), abs(Shi))
                alpha, bup, blo = self.S_env(aw, bwid)
                Sup = V(bw.ti).scale(alpha) + C(bup)
                Sdn = V(bw.ti).scale(alpha) + C(blo)
                qlo, qhi = qr.lo, qr.hi
                if qlo >= 0:
                    mq, cq = Q(1), Q(0)
                elif qhi <= 0:
                    mq, cq = Q(-1), Q(0)
                else:
                    mq = (qhi + qlo) / (qhi - qlo)
                    cq = -2 * qlo * qhi / (qhi - qlo)
                Us = [((QQ.scale(mq) + C(cq)).scale(Sabs), "A"),
                      ((Sup if qhi >= 0 else Sdn).scale(qhi) + QQ.scale(Slo) + C(-qhi * Slo), "B1"),
                      ((Sup if qlo >= 0 else Sdn).scale(qlo) + QQ.scale(Shi) + C(-qlo * Shi), "B2")]
            if bw.kind == "pin" and bo.kind == "pin":
                wbs = [(Q(0), Q(0), Q(1), 0)]
            else:
                wbs = []
                for (w_i, we) in ((0, 1), (1, -1)):
                    mw_, mo_, c_ = self.W_env(we, aw, bwid, ao, boh)
                    wbs.append((mw_, mo_, c_, w_i))
            for (mw, mo, c, widx) in wbs:
                Wlb = bw.taff().scale(mw) + bo.taff().scale(mo) + C(c)
                base = Wlb.scale(Q(1, 2)) + C(Q(1, 2) - corr) - P
                for (Uf, nmU) in Us:
                    out[("s", bw.name, bo.name, k, eps, widx, nmU)] = base - Uf
        return out, box

    # -- the walk (NO early return: every branch of the tree is visited)
    def walk(self, node, cells, fixed):
        self.n["nodes"] += 1
        k = node.get("k")
        if k == "bisect":
            self.n["bisect"] += 1
            nm = node["body"]
            lo, hi = cells[nm]
            rlo, rmid, rhi = Q(node["lo"]), Q(node["mid"]), Q(node["hi"])
            if (rlo, rhi) != (lo, hi) or not (lo <= rmid <= hi):
                self.fail("bisect cell mismatch at %s" % nm)
            for idx, (a, b) in enumerate(((rlo, rmid), (rmid, rhi))):
                c2 = dict(cells); c2[nm] = (a, b)
                self.walk(node["ch"][idx], c2, fixed)
        elif k == "branch":
            self.n["branch"] += 1
            nm1, nm2 = node["pair"]
            keep = {tuple(s) for s in node["sels"]}
            bad = self.excluded_ok(cells, nm1, nm2, keep)
            if bad:
                self.fail("branch %s|%s omits a possible selection %s (sup g = %s)"
                          % (nm1, nm2, bad[0][0], float(bad[0][1])))
            for idx, s in enumerate(node["sels"]):
                f2 = dict(fixed); f2["%s|%s" % (nm1, nm2)] = tuple(s)
                self.walk(node["ch"][idx], cells, f2)
        elif k == "imp":
            self.n["imp"] += 1
            nm1, nm2 = node["pair"]
            bad = self.excluded_ok(cells, nm1, nm2, set())
            if bad:
                self.fail("imp node %s|%s: selection %s is possible" % (nm1, nm2, bad[0][0]))
        elif k == "imp_sel":
            self.n["imp_sel"] += 1
            nm1, nm2 = node["pair"]
            s = tuple(node["sel"])
            bad = self.excluded_ok(cells, nm1, nm2, set(SELS8) - {s})
            if bad:
                self.fail("imp_sel %s of %s|%s is not impossible" % (s, nm1, nm2))
        elif k == "dead":
            self.dead(node, cells, fixed)
        else:
            self.fail("unclosed leaf of kind %r" % k)

    def dead(self, node, cells, fixed):
        self.n["dead"] += 1
        li = node["leaf"]
        if not (0 <= li < len(self.leaves)):
            self.fail("dead node names leaf %r out of range" % li)
            return
        self.seen[li] += 1
        if self.only_leaf is not None and li != self.only_leaf:
            return
        rec = self.leaves[li]
        sel = {kp: tuple(v) for kp, v in node.get("sel", {}).items()}
        forced = set(node.get("forced", []))
        for kp, s in sel.items():
            if kp in fixed:
                if fixed[kp] != s:
                    self.fail("leaf %d uses a selection the branch did not fix" % li)
                continue
            if kp not in forced:
                self.fail("leaf %d uses an unjustified selection %s %s" % (li, kp, s))
                continue
            nm1, nm2 = kp.split("|")
            bad = self.excluded_ok(cells, nm1, nm2, {s})
            self.n["forced"] += 1
            if bad:
                self.fail("leaf %d: selection %s of %s is not forced (rival %s)"
                          % (li, s, kp, bad[0][0]))
        box = self.cellbox(cells)
        for v in range(self.nv):
            got = (Q(rec["box"][v][0]), Q(rec["box"][v][1]))
            if got != box[v]:
                self.fail("leaf %d: emitted box coordinate %d is not the cell box" % (li, v))
        want = set()
        for r in rec["rows"]:
            want.add(parse_key(r["key"]))
        mine, _ = self.rows_of(cells, sel, want)
        acc = Aff() if rec["infeas"] else V(0)
        for r in rec["rows"]:
            key = parse_key(r["key"])
            y = Q(r["y"])
            if y < 0:
                self.fail("leaf %d: negative Farkas multiplier" % li)
            emitted = Aff({int(v): Q(a) for v, a in r["co"].items()}, Q(r["k"]))
            own = mine.get(key)
            self.n["rows"] += 1
            if own is None:
                self.fail("leaf %d: row %s could not be rebuilt" % (li, r["key"]))
                continue
            if (own - emitted).rng(box).lo < 0:
                self.fail("leaf %d: emitted row %s is NOT implied by the rebuilt row (slack %s)"
                          % (li, r["key"], float((own - emitted).rng(box).lo)))
            else:
                self.n["rows_implied"] += 1
            acc = acc + emitted.scale(y)
            self.n["mult"] += 1
        lb = acc.rng(box).lo
        if rec["infeas"]:
            self.n["infeas"] += 1
            if lb <= 0:
                self.fail("leaf %d: infeasibility ray gives %s <= 0" % (li, float(lb)))
        else:
            if self.min_bound is None or lb < self.min_bound:
                self.min_bound = lb
            if lb <= S0:
                self.fail("leaf %d: Farkas bound %s <= s0" % (li, float(lb)))

    def run(self):
        cells = self.root_cells()
        meta_cells = {b["name"]: (Q(b["t0"]), Q(b["t1"])) for b in self.m["bodies"]
                      if b["kind"] == "free"}
        if cells != meta_cells:
            self.fail("root cells do not match the declared neighbourhood")
        sys.setrecursionlimit(200000)
        self.verify_env()
        self.walk(self.c["root"], cells, {})
        for i, c in enumerate(self.seen):
            if c != 1:
                self.fail("leaf %d is referenced %d times by the tree" % (i, c))
        return not self.errors


def parse_key(s):
    p = s.split("|")
    if p[0] == "w":
        return ("w", p[1], p[2], p[3])
    if p[0] == "s":
        return ("s", p[1], p[2], int(p[3]), int(p[4]), int(p[5]), p[6])
    raise ValueError("unknown row key %r" % s)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main(paths):
    ok_all = True
    out = []
    for p in paths:
        t0 = time.time()
        with gzip.open(p, "rt", encoding="utf-8") as f:
            cert = json.load(f)
        C_ = Checker(cert)
        ok = C_.run()
        wall = time.time() - t0
        rec = dict(file=os.path.basename(p), id=cert["meta"]["id"], ok=bool(ok),
                   sha256=sha256_of(p), seconds=round(wall, 1), bytes=os.path.getsize(p),
                   counts=dict(C_.n), n_leaves=len(C_.leaves),
                   certified_min=(None if C_.min_bound is None else str(C_.min_bound)),
                   certified_min_float=(None if C_.min_bound is None else float(C_.min_bound)),
                   s0=float(S0), n_errors=len(C_.errors), errors=C_.errors[:5])
        out.append(rec)
        print("%-28s %s  nodes %-7d bisect %-6d branch %-4d leaves %-6d rows %-7d "
              "implied %-7d  min %s  %.1f s"
              % (rec["id"], "VALID  " if ok else "INVALID(%d)" % len(C_.errors),
                 C_.n["nodes"], C_.n["bisect"], C_.n["branch"], len(C_.leaves), C_.n["rows"],
                 C_.n["rows_implied"],
                 ("%.9f" % rec["certified_min_float"]) if C_.min_bound is not None else "-", wall))
        for e in C_.errors[:5]:
            print("    !", e)
        ok_all = ok_all and ok
    res = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results",
                       "check_local_t.json")
    prev = []
    if os.path.exists(res):
        try:
            prev = json.load(open(res, encoding="utf-8")).get("runs", [])
        except Exception:
            prev = []
    with open(res, "w", encoding="utf-8") as f:
        json.dump(dict(when=time.strftime("%Y-%m-%dT%H:%M:%S"), runs=out, previous=prev[:20]),
                  f, indent=1)
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
