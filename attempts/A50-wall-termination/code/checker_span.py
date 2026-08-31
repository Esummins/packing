"""A50 T1 -- INDEPENDENT corruption-gated checker for results/span_table.json.

Re-verifies the table FROM THE JSON ALONE with a separately written algebra path:
its own index-set enumeration (by candidate (a,b,c) + realisability search, not by
multiset enumeration), its own quadratic root isolation (Cauchy-bound bracket +
halving), its own surd order, and its own arrangement of the domain.  Nothing is
imported from span_table.py.

Verification model (complete, not spot-check):
  * every sign change of f_{abc} - lo and f_{abc} - s0 happens at a root of the
    corresponding boundary quadratic, so the root set R of ALL boundary quadratics
    of ALL admissible triples cuts (0, t45] into cells on which the hit-set is
    constant;
  * every element of R that lies in the domain is an ADMITTED point (f equals lo
    or s0 there exactly, and lo < s0);
  * each open cell is labelled by exact evaluation at a rational witness;
  * the maximal runs of equal labels must reproduce the JSON's intervals exactly
    (endpoints as algebraic objects, closure flags, labels, per-triple sides).

Then the CORRUPTION GATE: 5 seeded corruptions, each of which must make this
checker FAIL.  Log: logs/checker_gate.log
"""

from fractions import Fraction as Q
from math import gcd, isqrt
import copy
import json
import os
import sys

LO_ = Q(191, 50)
S0_ = Q(969271, 250000)
MAX_ENCLOSURE_WIDTH = Q(1, 10 ** 15)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RESULTS = os.path.join(ROOT, "results")
LOGS = os.path.join(ROOT, "logs")


class CheckFail(Exception):
    pass


def need(cond, msg):
    if not cond:
        raise CheckFail(msg)


# ------------------------------------------------------------- own algebra
def primitive(A, B, C):
    """Rational coefficients -> primitive integer triple with A>0 (or A=0, B>0)."""
    co = [Q(A), Q(B), Q(C)]
    m = 1
    for x in co:
        m = m * x.denominator // gcd(m, x.denominator)
    v = [int(x * m) for x in co]
    g = 0
    for x in v:
        g = gcd(g, abs(x))
    if g:
        v = [x // g for x in v]
    if v[0] < 0 or (v[0] == 0 and v[1] < 0):
        v = [-x for x in v]
    return tuple(v)


class Surd:
    """Root #idx of the integer quadratic A x^2 + B x + C (A>0, disc>0 non-square)."""

    def __init__(self, A, B, C, idx):
        self.abc = (A, B, C)
        self.idx = idx
        D = B * B - 4 * A * C
        need(D > 0, "non-positive discriminant in Surd")
        need(isqrt(D) ** 2 != D, "square discriminant in Surd")
        # Cauchy-style bracket then halving
        M = Q(abs(A) + max(abs(B), abs(C)), abs(A))      # Cauchy bound
        vert = Q(-B, 2 * A)
        if idx == 1:
            self.a, self.b = vert, M
        else:
            self.a, self.b = -M, vert
        need(self.a < self.b, "empty root bracket")
        need(self.val(self.a) * self.val(self.b) < 0, "bad root bracket")
        self.tighten(MAX_ENCLOSURE_WIDTH / 10)

    def val(self, x):
        A, B, C = self.abc
        return (A * x + B) * x + C

    def tighten(self, width):
        A = self.abc[0]
        # on [a,b] the polynomial is monotone (a,b on one side of the vertex)
        sa = self.val(self.a)
        while self.b - self.a > width:
            m = (self.a + self.b) / 2
            sm = self.val(m)
            need(sm != 0, "rational root inside irreducible quadratic")
            if (sm > 0) == (sa > 0):
                self.a, sa = m, sm
            else:
                self.b = m

    def key(self):
        return (self.abc, self.idx)

    def __float__(self):
        return float((self.a + self.b) / 2)


def order(u, v):
    """Total order on Fractions and Surds."""
    su, sv = isinstance(u, Surd), isinstance(v, Surd)
    if not su and not sv:
        return (u > v) - (u < v)
    if su and not sv:
        return _surd_vs_rat(u, v)
    if sv and not su:
        return -_surd_vs_rat(v, u)
    if u.key() == v.key():
        return 0
    w = MAX_ENCLOSURE_WIDTH
    while True:
        if u.b <= v.a:
            return -1
        if v.b <= u.a:
            return 1
        w = w / 4096
        u.tighten(w)
        v.tighten(w)


def _surd_vs_rat(u, r):
    if r <= u.a:
        return 1
    if r >= u.b:
        return -1
    s = u.val(r)
    A, B, _ = u.abc
    if s < 0:
        return 1 if u.idx == 1 else -1
    return 1 if r < Q(-B, 2 * A) else -1


def roots_of(A, B, C):
    """Exact roots of the rational quadratic, ascending."""
    A, B, C = primitive(A, B, C)
    if A == 0:
        return [] if B == 0 else [Q(-C, B)]
    D = B * B - 4 * A * C
    if D < 0:
        return []
    s = isqrt(D)
    if s * s == D:
        return [Q(-B, 2 * A)] if D == 0 else [Q(-B - s, 2 * A), Q(-B + s, 2 * A)]
    return [Surd(A, B, C, 0), Surd(A, B, C, 1)]


def lower(x):
    return x.a if isinstance(x, Surd) else x


def upper(x):
    return x.b if isinstance(x, Surd) else x


def between(x, y):
    """A rational strictly between x < y."""
    w = MAX_ENCLOSURE_WIDTH
    for _ in range(200):
        a, b = upper(x), lower(y)
        if a < b:
            return (a + b) / 2
        w = w / 4096
        if isinstance(x, Surd):
            x.tighten(w)
        if isinstance(y, Surd):
            y.tighten(w)
    raise CheckFail("cannot separate breakpoints")


def f_value(a, b, c, t):
    """a cos + b sin + c at rational t = tan(phi/2), exact."""
    return (a * (1 - t * t) + 2 * b * t + c * (1 + t * t)) / (1 + t * t)


# --------------------------------------------------- Q[sqrt2] (phi = 45 point)
def sqrt2_sign(p, q):
    """sign of p + q sqrt2, p,q rational, exact."""
    if q == 0:
        return (p > 0) - (p < 0)
    if p == 0:
        return (q > 0) - (q < 0)
    if (p > 0) == (q > 0):
        return 1 if p > 0 else -1
    return (1 if p > 0 else -1) if p * p > 2 * q * q else (1 if q > 0 else -1)


def hits_at_45(a, b, c):
    """lo <= a cos45 + b sin45 + c <= s0, exact in Q[sqrt2]."""
    # (a+b) sqrt2/2 + c  vs w  <->  sign((c-w) + (a+b)/2 sqrt2)
    lo_ok = sqrt2_sign(Q(c) - LO_, Q(a + b, 2)) >= 0
    hi_ok = sqrt2_sign(Q(c) - S0_, Q(a + b, 2)) <= 0
    return lo_ok and hi_ok


# ------------------------------------------------ independent index sets
def realisable(a, b, c, Lmax):
    """(a,b,c) realisable: exists n1..n4 >= 0 with a=n1+n3+n4, b=n2+n3-n4,
    n1+n2+n3+n4 >= 2 and 3 <= n1+n2+n3+n4+c <= Lmax."""
    if c < 0 or a < 0 or c > Lmax:
        return False
    for n3 in range(0, a + 1):
        for n4 in range(0, a - n3 + 1):
            n1 = a - n3 - n4
            n2 = b - n3 + n4
            if n2 < 0:
                continue
            nt = n1 + n2 + n3 + n4
            if nt < 2:
                continue
            if 3 <= nt + c <= Lmax:
                return True
    return False


_IDX = {}


def index_set_indep(Lmax):
    if Lmax in _IDX:
        return _IDX[Lmax]
    out = []
    for a in range(0, Lmax + 1):
        for b in range(-Lmax, Lmax + 1):
            for c in range(0, Lmax + 1):
                if realisable(a, b, c, Lmax):
                    out.append((a, b, c))
    _IDX[Lmax] = sorted(out)
    return _IDX[Lmax]


def multisets_indep(Lmax, m=0):
    """(n1,n2,n3,n4,c), n1+..+n4 >= 2, L = sum + c + m in [3, Lmax]."""
    out = []
    cap = Lmax - m
    for n1 in range(cap + 1):
        for n2 in range(cap + 1):
            for n3 in range(cap + 1):
                for n4 in range(cap + 1):
                    nt = n1 + n2 + n3 + n4
                    if nt < 2 or nt > cap:
                        continue
                    for c in range(cap - nt + 1):
                        if 3 <= nt + c + m <= Lmax:
                            out.append((n1, n2, n3, n4, c))
    return out


# ------------------------------------------------------- JSON deserialisation
def parse_point(d):
    if d["kind"] == "rational":
        return Q(int(d["num"]), int(d["den"]))
    need(d["kind"] == "quadratic", "unknown endpoint kind")
    A, B, C, idx = int(d["A"]), int(d["B"]), int(d["C"]), d["root_index"]
    need(A > 0, "endpoint quadratic must have A > 0")
    need(idx in (0, 1), "bad root index")
    e = d["enclosure"]
    lo = Q(int(e["lo_num"]), int(e["lo_den"]))
    hi = Q(int(e["hi_num"]), int(e["hi_den"]))
    need(lo < hi, "empty enclosure")
    need(hi - lo < MAX_ENCLOSURE_WIDTH,
         "enclosure width %s not < 1e-15" % float(hi - lo))
    p = lambda x: (A * x + B) * x + C          # noqa: E731
    need(p(lo) * p(hi) < 0, "enclosure does not bracket a root of the stored quadratic")
    vert = Q(-B, 2 * A)
    if idx == 0:
        need(hi <= vert, "root index 0 but enclosure is right of the vertex")
    else:
        need(lo >= vert, "root index 1 but enclosure is left of the vertex")
    pa, pb, pc = primitive(A, B, C)
    s = Surd(pa, pb, pc, idx)
    need(order(s, lo) > 0 and order(s, hi) < 0, "stored enclosure inconsistent with root")
    return s


def parse_iv(d):
    return (parse_point(d["lo"]), bool(d["lo_closed"]),
            parse_point(d["hi"]), bool(d["hi_closed"]))


def parse_rat(d):
    return Q(int(d["num"]), int(d["den"]))


# ------------------------------------------------- independent column model
_MODEL = {}


def column_model(Lmax):
    """Independent reconstruction of the labelled interval decomposition of (0,t45]."""
    if Lmax in _MODEL:
        return _MODEL[Lmax]
    A = index_set_indep(Lmax)
    t45 = Surd(1, 2, -1, 1)
    zero = Q(0)
    pts = []
    for (a, b, c) in A:
        for w in (LO_, S0_):
            for r in roots_of(c - w - a, 2 * b, a + c - w):
                if order(r, zero) > 0 and order(r, t45) < 0:
                    pts.append(r)
    pts.sort(key=_Key)
    uniq = []
    for p in pts:
        if not uniq or order(uniq[-1], p) != 0:
            uniq.append(p)
    breaks = [zero] + uniq + [t45]
    # label each cell
    labels = []          # alternating: open cell, then the point at its right end
    for i in range(len(breaks) - 1):
        w = between(breaks[i], breaks[i + 1])
        hit = [j for j, (a, b, c) in enumerate(A) if LO_ <= f_value(a, b, c, w) <= S0_]
        labels.append(("open", i, bool(hit), w))
        if i + 1 < len(breaks) - 1:
            # interior breakpoint: it is a root of some boundary quadratic, so
            # f = lo or f = s0 there exactly => the POINT is admitted (lo < s0)
            labels.append(("pt", i + 1, True, None))
        else:
            adm45 = any(hits_at_45(a, b, c) for (a, b, c) in A)
            labels.append(("pt", i + 1, adm45, None))
    # merge into maximal runs
    runs = []
    for kind, i, adm, w in labels:
        if kind == "open":
            lo, lc, hi, hc = breaks[i], False, breaks[i + 1], False
        else:
            lo, lc, hi, hc = breaks[i], True, breaks[i], True
        if runs and runs[-1][0] == adm:
            runs[-1][3], runs[-1][4] = hi, hc
        else:
            runs.append([adm, lo, lc, hi, hc])
    _MODEL[Lmax] = (A, breaks, [tuple(r) for r in runs])
    return _MODEL[Lmax]


class _Key:
    __slots__ = ("v",)

    def __init__(self, v):
        self.v = v

    def __lt__(self, other):
        return order(self.v, other.v) < 0


# ----------------------------------------------------------- column verifier
def verify_column(col, Lmax, tag):
    A, breaks, runs = column_model(Lmax)
    stored = [tuple(x) for x in col["index_set"]]
    need(sorted(stored) == A, "%s: index set differs from independent enumeration "
                              "(stored %d, independent %d)" % (tag, len(stored), len(A)))
    need(col["index_set_size"] == len(A), "%s: index_set_size wrong" % tag)

    items = []
    for d in col["admitted_intervals"]:
        items.append((True, parse_iv(d), d))
    for d in col["excluded_intervals"]:
        items.append((False, parse_iv(d), d))
    items.sort(key=lambda it: _Key(it[1][0]))
    need(len(items) == len(runs),
         "%s: %d intervals stored, %d reconstructed" % (tag, len(items), len(runs)))

    for (adm, iv, d), run in zip(items, runs):
        radm, rlo, rlc, rhi, rhc = run
        need(adm == radm, "%s: label mismatch near %.6f deg (stored %s)"
             % (tag, d["_float_deg_lo"], "admitted" if adm else "excluded"))
        need(order(iv[0], rlo) == 0, "%s: lo endpoint mismatch at %.6f deg"
             % (tag, d["_float_deg_lo"]))
        need(order(iv[2], rhi) == 0, "%s: hi endpoint mismatch at %.6f deg"
             % (tag, d["_float_deg_hi"]))
        need(iv[1] == rlc and iv[3] == rhc,
             "%s: closure flags mismatch at %.6f deg" % (tag, d["_float_deg_lo"]))

        w = parse_rat(d["witness_t"]) if d.get("witness_t") else None
        need(w is not None, "%s: interval without rational witness" % tag)
        need(order(iv[0], w) < 0 and order(w, iv[2]) < 0,
             "%s: witness not strictly inside its interval" % tag)
        hit = [j for j, (a, b, c) in enumerate(A) if LO_ <= f_value(a, b, c, w) <= S0_]
        if adm:
            need(hit, "%s: admitted interval whose witness hits nothing" % tag)
            need(sorted(d.get("witness_hitting_triple_indices", [])) == hit,
                 "%s: witness hitting set mismatch" % tag)
            need(set(hit) <= set(d.get("hitting_triples_indices",
                                       d.get("hitting_triple_indices", []))),
                 "%s: hitting-triple list does not contain the witness hits" % tag)
        else:
            need(not hit, "%s: excluded interval whose witness IS admitted" % tag)
            sides = d.get("exclusion_sides")
            need(sides is not None, "%s: excluded interval without per-triple sides" % tag)
            below, above = [], []
            for j, (a, b, c) in enumerate(A):
                v = f_value(a, b, c, w)
                (below if v < LO_ else above).append(j)
            need(sorted(sides["below_lo"]) == below and sorted(sides["above_hi"]) == above,
                 "%s: per-triple exclusion sides mismatch" % tag)
            # no boundary-quadratic root strictly inside an excluded interval
            for p in breaks:
                need(not (order(iv[0], p) < 0 and order(p, iv[2]) < 0),
                     "%s: a boundary root lies inside an excluded interval" % tag)
    return len(items)


# -------------------------------------------------------- near-flush verifier
def verify_near_flush(doc):
    nf = doc["near_flush_exclusion"]
    q = nf["quadratic"]
    A, B, C = int(q["A"]), int(q["B"]), int(q["C"])
    need((A, B, C) == primitive(4 + S0_, 8, -(4 - S0_)),
         "near-flush: theta* quadratic is not the primitive form of (4+s0)t^2+8t-(4-s0)")
    ts = Surd(A, B, C, q["root_index"])
    need(order(ts, Q(0)) > 0, "near-flush: theta* root index selects a non-positive root")
    v = parse_rat(nf["v_rational_just_below"])
    need(order(ts, v) > 0 and v > 0, "near-flush: v is not strictly below theta*")
    cv = (1 - v * v) / (1 + v * v)
    sv = 2 * v / (1 + v * v)
    need(4 * (cv - sv) > S0_, "near-flush: 4(cos v - sin v) <= s0")
    for key, Lmax, m in (("audit_L6", 6, 0), ("audit_L8", 8, 0),
                         ("audit_L6_mixed_m1", 6, 1), ("audit_L6_mixed_m2", 6, 2)):
        au = nf[key]
        ms = multisets_indep(Lmax, m)
        need(au["n_multisets"] == len(ms),
             "near-flush %s: multiset count %d != %d" % (key, au["n_multisets"], len(ms)))
        stored = {tuple(e[:5]): e[5] for e in au["entries"]}
        need(len(stored) == len(ms), "near-flush %s: duplicate/missing entries" % key)
        for (n1, n2, n3, n4, c) in ms:
            lo = (n1 * cv + n3 * 1 + n4 * (cv - sv) + c + m * (cv - sv))
            hi = (n1 * 1 + n2 * sv + n3 * (cv + sv) + n4 * 1 + c + m * (cv + sv))
            if hi < LO_:
                lab = "max_below_lo"
            elif lo > S0_:
                lab = "min_above_hi"
            else:
                lab = "HITS_WINDOW"
            need(lab != "HITS_WINDOW",
                 "near-flush %s: multiset %s reaches the live window" % (key, (n1, n2, n3, n4, c)))
            need(stored.get((n1, n2, n3, n4, c)) == lab,
                 "near-flush %s: side label mismatch for %s" % (key, (n1, n2, n3, n4, c)))
        need(au["excluded"] is True, "near-flush %s: not flagged excluded" % key)


# ------------------------------------------------------------ V1 sweep gate
def verify_sweep(doc):
    """Re-verify every window-class sweep row exactly (own hull arithmetic)."""
    for key, blk in doc["v1_sweep"].items():
        Lmax = blk["Lmax"]
        ms = multisets_indep(Lmax, 0)
        need(blk["n_windows"] == len(blk["rows"]), "sweep %s: row count" % key)
        n_exc = 0
        for row in blk["rows"]:
            tu, tv = parse_rat(row["tu"]), parse_rat(row["tv"])
            need(0 <= tu <= tv, "sweep %s: bad window" % key)
            cu, su = (1 - tu * tu) / (1 + tu * tu), 2 * tu / (1 + tu * tu)
            cv, sv = (1 - tv * tv) / (1 + tv * tv), 2 * tv / (1 + tv * tv)
            hit = False
            for (n1, n2, n3, n4, c) in ms:
                lo = n1 * cv + n2 * su + n3 * (cu + su) + n4 * (cv - sv) + c
                hi = n1 * cu + n2 * sv + n3 * (cv + sv) + n4 * (cu - su) + c
                if not (hi < LO_ or lo > S0_):
                    hit = True
                    break
            status = "ADMITTED" if hit else "EXCLUDED"
            need(status == row["status"],
                 "sweep %s: window [%s, %s] deg is %s, stored %s"
                 % (key, row["_float_u_deg"], row["_float_v_deg"], status, row["status"]))
            n_exc += (status == "EXCLUDED")
        need(n_exc == blk["n_excluded"], "sweep %s: excluded count" % key)


# ------------------------------------------------------------- top verifier
def verify(doc):
    c = doc["constants"]
    need(parse_rat(c["s0"]) == S0_, "constant s0 differs from 969271/250000")
    need(parse_rat(c["lo"]) == LO_, "constant lo differs from 191/50")
    t45 = parse_point(c["t45"])
    need(t45.key() == ((1, 2, -1), 1), "t45 is not the positive root of t^2+2t-1")
    need(doc["index_set_sizes"]["A6"] == len(index_set_indep(6)) == 172,
         "|A(6)| != 172")
    need(doc["index_set_sizes"]["A8"] == len(index_set_indep(8)), "|A(8)| mismatch")
    n6 = verify_column(doc["columns"]["L6"], 6, "L6")
    n8 = verify_column(doc["columns"]["L8"], 8, "L8")
    verify_near_flush(doc)
    verify_sweep(doc)
    return {"L6_intervals": n6, "L8_intervals": n8}


# ------------------------------------------------------------ corruption gate
def corrupt_enclosure(d):
    e = d["columns"]["L6"]["excluded_intervals"][1]["hi"]["enclosure"]
    lo = Q(int(e["lo_num"]), int(e["lo_den"])) - Q(1, 10 ** 9)
    hi = Q(int(e["hi_num"]), int(e["hi_den"])) + Q(1, 10 ** 9)
    e["lo_num"], e["lo_den"] = str(lo.numerator), str(lo.denominator)
    e["hi_num"], e["hi_den"] = str(hi.numerator), str(hi.denominator)
    return "exclusion endpoint enclosure widened by 1e-9"


def corrupt_delete_triple(d):
    d["columns"]["L6"]["index_set"].pop(100)
    d["columns"]["L6"]["index_set_size"] -= 1
    d["index_set_sizes"]["A6"] -= 1
    return "triple #100 deleted from A(6)"


def corrupt_sign_flip(d):
    p = d["columns"]["L6"]["excluded_intervals"][1]["lo"]
    p["B"] = str(-int(p["B"]))
    return "sign flip of coefficient B in a stored endpoint quadratic"


def corrupt_s0(d):
    n = int(d["constants"]["s0"]["num"])
    d["constants"]["s0"]["num"] = str(n + 1)
    return "s0 numerator off by one"


def corrupt_relabel(d):
    iv = d["columns"]["L6"]["excluded_intervals"].pop(3)
    iv["hitting_triples"] = []
    iv["hitting_triple_indices"] = []
    iv["witness_hitting_triple_indices"] = []
    d["columns"]["L6"]["admitted_intervals"].append(iv)
    return "an excluded interval relabelled admitted"


CORRUPTIONS = [corrupt_enclosure, corrupt_delete_triple, corrupt_sign_flip,
               corrupt_s0, corrupt_relabel]


def main():
    os.makedirs(LOGS, exist_ok=True)
    path = os.path.join(RESULTS, "span_table.json")
    with open(path) as fh:
        doc = json.load(fh)
    lines = ["A50 T1 checker gate -- %s" % os.path.relpath(path, ROOT)]
    ok = True
    try:
        info = verify(doc)
        lines.append("PRISTINE: PASS  %s" % info)
        print("PRISTINE: PASS", info)
    except Exception as ex:                     # noqa: BLE001
        ok = False
        lines.append("PRISTINE: FAIL  %s: %s" % (type(ex).__name__, ex))
        print("PRISTINE: FAIL", ex)
    for i, corr in enumerate(CORRUPTIONS, 1):
        d = copy.deepcopy(doc)
        what = corr(d)
        try:
            verify(d)
            lines.append("CORRUPTION %d (%s): NOT DETECTED  <-- GATE FAILURE" % (i, what))
            print("CORRUPTION %d: NOT DETECTED" % i)
            ok = False
        except Exception as ex:                 # noqa: BLE001
            lines.append("CORRUPTION %d (%s): detected -- %s: %s"
                         % (i, what, type(ex).__name__, ex))
            print("CORRUPTION %d: detected (%s)" % (i, type(ex).__name__))
    lines.append("GATE: %s" % ("PASS" if ok else "FAIL"))
    with open(os.path.join(LOGS, "checker_gate.log"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("GATE:", "PASS" if ok else "FAIL")
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
