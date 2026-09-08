"""A134 T1 -- the polynomial layer of `LocalCertT.lean` / `LocalCertT2.lean`, mirrored EXACTLY.

Every function here is a line-by-line transcription of the Lean definition of the same name in
`lean/PackingCertMathlib/PackingCertMathlib/LocalCertT.lean` (sec. 3) and `LocalCertT2.lean`
(sec. 1-2), including the LIST SHAPES: Lean's `posCheck` compares `posAux a b c (c.length - 1)`
with the target polynomial by `List` equality (`==`), so a certificate that reproduces the
polynomial only up to trailing zeros would be REJECTED by the kernel.  This module therefore
reproduces `padd` / `pscale` / `pmul` / `ppow` / `posAux` (and their bivariate twins) with the
same recursion and the same truncated `Nat` subtraction, so that what the generator writes into a
`.tcert` is byte-for-byte what Lean's `decide` will accept.

Univariate certificate (Lean `posCheck p c a b`):

    p(X)  =  sum_k c_k (X - a)^k (b - X)^(n - k),   n = len(c) - 1,   all c_k >= 0

so `p >= 0` on `[a, b]`.  From the Bernstein coefficients `beta_k` of `p` on `[a, b]`,

    c_k = beta_k * C(n, k) / (b - a)^n.

Bivariate certificate (Lean `posCheck2 P C a b c d`), `P : List Poly` with `P[i]` the coefficient
list in `Y` of `X^i`:

    P(X, Y)  =  sum_i (X - a)^i (b - X)^(m - i) * Q_i(Y),
    Q_i(Y)   =  sum_j C[i][j] (Y - c)^j (d - Y)^(n - j),   all C[i][j] >= 0

with `C[i][j] = beta_ij * C(m, i) C(n, j) / ((b - a)^m (d - c)^n)`.  The check is again exact list
equality, and the outer sum is assembled by the SAME `posAux` recursion with polynomial (rather
than rational) coefficients, which is why no new soundness argument is needed for the second
variable.
"""
from __future__ import annotations

from fractions import Fraction as Q

# --------------------------------------------------------------- univariate, Lean's shapes
def padd(p, q):
    if not p:
        return list(q)
    if not q:
        return list(p)
    return [p[0] + q[0]] + padd(p[1:], q[1:])


def pscale(c, p):
    return [c * a for a in p]


def pmul(p, q):
    if not p:
        return []
    return padd(pscale(p[0], q), [Q(0)] + pmul(p[1:], q))


def ppow(p, n):
    if n == 0:
        return [Q(1)]
    return pmul(p, ppow(p, n - 1))


def linA(a):
    return [-a, Q(1)]


def linB(b):
    return [b, Q(-1)]


def posAux(a, b, c, m):
    """Lean `posAux`; `m - 1` is Nat truncated subtraction."""
    if not c:
        return []
    return padd(pscale(c[0], ppow(linB(b), m)),
                pmul(linA(a), posAux(a, b, c[1:], m - 1 if m > 0 else 0)))


def peval(p, x):
    r = Q(0)
    for a in reversed(p):
        r = r * x + a
    return r


# --------------------------------------------------------------- bivariate, Lean's shapes
def padd2(P, R):
    if not P:
        return [list(r) for r in R]
    if not R:
        return [list(p) for p in P]
    return [padd(P[0], R[0])] + padd2(P[1:], R[1:])


def pscale2(c, P):
    return [pscale(c, p) for p in P]


def pmul2(P, R):
    if not P:
        return []
    return padd2([pmul(P[0], r) for r in R], [[]] + pmul2(P[1:], R))


def posAuxP(a, b, qs, m):
    """Lean `posAuxP`: the outer `posAux` with POLYNOMIAL coefficients `qs : List Poly`."""
    if not qs:
        return []
    head = [pscale(e, qs[0]) for e in ppow(linB(b), m)]
    rest = posAuxP(a, b, qs[1:], m - 1 if m > 0 else 0)
    # (X - a) * rest  =  padd2 (map (pscale (-a)) rest) ([] :: rest)
    tail = padd2([pscale(-a, r) for r in rest], [[]] + rest)
    return padd2(head, tail)


def posAux2(a, b, c, d, C):
    """Lean `posAux2 a b c d C = posAuxP a b (C.map (fun cs => posAux c d cs (cs.length-1))) (C.length-1)`."""
    qs = [posAux(c, d, cs, len(cs) - 1 if cs else 0) for cs in C]
    return posAuxP(a, b, qs, len(C) - 1 if C else 0)


def peval2(P, x, y):
    r = Q(0)
    for p in reversed(P):
        r = r * x + peval(p, y)
    return r


# --------------------------------------------------------------- zero padding
# `pmul p []` is NOT `[]` in Lean's definition (only the FIRST argument's `[]` short-circuits),
# so `posAux a b c (c.length - 1)` carries exactly ONE trailing zero beyond the degree, and
# `posAux2`'s inner polynomials carry one each.  `posCheck` compares LISTS, so every envelope
# polynomial is defined in Lean through `padZ` / `padZ2` to the shape `posAux` produces.
def zpad(n):
    return [Q(0)] * n


def padZ(n, p):
    return padd(p, zpad(n))


def padZ2(n, P):
    return [padZ(n, p) for p in P]


# --------------------------------------------------------------- Bernstein -> certificate
_BINOM = {}


def binom(n, k):
    v = _BINOM.get((n, k))
    if v is None:
        v = 1
        for i in range(k):
            v = v * (n - i) // (i + 1)
        _BINOM[(n, k)] = v
    return v


def bern1(p, a, b):
    """Bernstein coefficients of `p` (ascending monomial list) on [a, b], degree len(p)-1."""
    n = len(p) - 1
    if n < 0:
        return [Q(0)]
    h = b - a
    q = [Q(0)] * (n + 1)
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
            s += Q(binom(k, i), binom(n, i)) * q[i]
        out.append(s)
    return out


def cert1(p, a, b):
    """the `posCheck` certificate of `p` on [a, b], or None if a Bernstein coefficient is < 0.

    `p` is the PADDED Lean shape (one trailing zero, see `padZ`), so the honest degree is
    `len(p) - 2` and `posAux a b c (len(c) - 1)` then has length `len(p)` exactly."""
    if not p or p[-1] != 0:
        raise AssertionError("cert1: expected a padZ-shaped polynomial")
    q = p[:-1]
    n = len(q) - 1
    if n < 0:
        return None
    beta = bern1(q, a, b)
    h = (b - a) ** n
    c = [beta[k] * binom(n, k) / h for k in range(n + 1)]
    if any(v < 0 for v in c):
        return None
    if posAux(a, b, c, n) != p:
        raise AssertionError("cert1: posAux does not reproduce the polynomial exactly")
    return c


def chain1(p, a, b, max_depth=6):
    """the SUBDIVIDED certificate: the coarsest uniform chain of [a, b] on which every piece has
    a `posCheck` certificate.  Returns (pieces, depth) with pieces = [(a_i, b_i, c_i), ...] laid
    end to end from a to b, or (None, None)."""
    for d in range(max_depth + 1):
        n = 1 << d
        step = (b - a) / n
        out = []
        ok = True
        for i in range(n):
            ai = a + step * i
            bi = b if i == n - 1 else a + step * (i + 1)
            c = cert1(p, ai, bi)
            if c is None:
                ok = False
                break
            out.append((ai, bi, c))
        if ok:
            return out, d
    return None, None


def bern2(P, aw, bw, ao, bo, nw, no):
    """Bernstein coefficients of the bivariate `P` (P[i] = coeff list in Y of X^i) on the box,
    in the bi-degree (nw, no)."""
    G = [[(P[i][j] if i < len(P) and j < len(P[i]) else Q(0)) for j in range(no + 1)]
         for i in range(nw + 1)]
    G2 = [bern1(G[i], ao, bo) for i in range(nw + 1)]
    cols = []
    for j in range(no + 1):
        cols.append(bern1([G2[i][j] for i in range(nw + 1)], aw, bw))
    return [[cols[j][i] for j in range(no + 1)] for i in range(nw + 1)]


def cert2(P, aw, bw, ao, bo):
    """the `posCheck2` certificate of `P` on the box, or None.

    `P` is the `padZ2`-shaped Lean list: `len(P) = nw + 1` (no padding in X, `posAuxP` adds none)
    and every entry carries one trailing zero, so `no = len(P[i]) - 2`."""
    nw = len(P) - 1
    no = max((len(p) for p in P), default=2) - 2
    if nw < 0 or no < 0:
        return None
    beta = bern2(P, aw, bw, ao, bo, nw, no)
    hw = (bw - aw) ** nw
    ho = (bo - ao) ** no
    C = [[beta[i][j] * binom(nw, i) * binom(no, j) / (hw * ho) for j in range(no + 1)]
         for i in range(nw + 1)]
    if any(v < 0 for row in C for v in row):
        return None
    if posAux2(aw, bw, ao, bo, C) != P:
        raise AssertionError("cert2: posAux2 does not reproduce the polynomial exactly")
    return C


def chain2(P, aw, bw, ao, bo, max_depth=4):
    """the SUBDIVIDED bivariate certificate: an x-chain of [aw, bw], each x-piece carrying a
    y-chain of [ao, bo].  Uniform depth in both variables.  Returns (pieces, depth)."""
    for d in range(max_depth + 1):
        n = 1 << d
        sw = (bw - aw) / n
        so = (bo - ao) / n
        out = []
        ok = True
        for i in range(n):
            ai = aw + sw * i
            bi = bw if i == n - 1 else aw + sw * (i + 1)
            ys = []
            for j in range(n):
                cj = ao + so * j
                dj = bo if j == n - 1 else ao + so * (j + 1)
                C = cert2(P, ai, bi, cj, dj)
                if C is None:
                    ok = False
                    break
                ys.append((cj, dj, C))
            if not ok:
                break
            out.append((ai, bi, ys))
        if ok:
            return out, d
    return None, None


# --------------------------------------------------------------- the three envelope polynomials
# Each is built with the SAME `padd`/`pscale`/`pmul` calls as the Lean definition of the same
# name, so the emitted certificate's list shape matches Lean's `posCheck` target exactly.

def hPoly(m, c):
    """Lean `hPoly m c` = (1 + 2X - X^2) - 2 (m X + c)(1 + X^2);  h(t) >= m t + c on the cell
    iff this is >= 0 there (2 h(t) = (1 + 2t - t^2)/(1 + t^2), and 1 + t^2 > 0)."""
    return padZ(5, padd([Q(1), Q(2), Q(-1)], pscale(Q(-2), pmul([c, m], [Q(1), Q(0), Q(1)]))))


def sNum(cm, sm):
    """Lean `sNum cm sm` = -sm + 2 cm X + sm X^2, the numerator of S(t) = sin(theta(t)-theta(tm))."""
    return [-sm, 2 * cm, sm]


def sUpPoly(cm, sm, alpha, beta):
    """Lean `sUpPoly`: (alpha X + beta)(1 + X^2) - N(X) >= 0  iff  S <= alpha t + beta."""
    return padZ(5, padd(pmul([beta, alpha], [Q(1), Q(0), Q(1)]), pscale(Q(-1), sNum(cm, sm))))


def sLoPoly(cm, sm, alpha, beta):
    """Lean `sLoPoly`: N(X) - (alpha X + beta)(1 + X^2) >= 0  iff  S >= alpha t + beta."""
    return padZ(5, padd(sNum(cm, sm), pscale(Q(-1), pmul([beta, alpha], [Q(1), Q(0), Q(1)]))))


ONE_TT = [[Q(1)], [Q(0), Q(1)]]                       # 1 + X Y
DIFF_T = [[Q(0), Q(-1)], [Q(1)]]                      # X - Y
DEN_T = [[Q(1), Q(0), Q(1)], [], [Q(1), Q(0), Q(1)]]  # (1 + X^2)(1 + Y^2)


def wNumT(eps):
    """Lean `wNumT eps` = (1 + XY)^2 - (X - Y)^2 + 2 eps (X - Y)(1 + XY),
    the numerator of W_eps = cos D - eps sin D over (1 + X^2)(1 + Y^2)."""
    return padd2(padd2(pmul2(ONE_TT, ONE_TT), pscale2(Q(-1), pmul2(DIFF_T, DIFF_T))),
                 pscale2(Q(2) * eps, pmul2(DIFF_T, ONE_TT)))


def wPolyT(eps, mw, mo, c):
    """Lean `wPolyT eps mw mo c` = wNumT eps - (mw X + mo Y + c) * DEN_T;  >= 0 on the cell
    product iff W_eps >= mw t_w + mo t_o + c there."""
    return padZ2(5, padd2(wNumT(eps), pscale2(Q(-1), pmul2([[c, mo], [mw]], DEN_T))))


def cPoly(cm, sm, K):
    """Lean `cPoly cm sm K` = (K - 1)(1 + X^2) + cm (1 - X^2) + 2 sm X;  >= 0 on the cell iff
    1 - cos(theta(t) - theta(tm)) <= K there (the correction term of Lemma RELAX)."""
    return padZ(5, padd(pscale(K - Q(1), [Q(1), Q(0), Q(1)]),
                        padd(pscale(cm, [Q(1), Q(0), Q(-1)]), [Q(0), Q(2) * sm])))
