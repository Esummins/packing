"""A50 T1 canaries C1-C4 (spec section 4).  All exact; no floats in certified values.

C1  phi = 45 reproduction of s* = 2 sqrt2 + 1   (arithmetic in Q + Q sqrt2)
C2  Trump x-/y-spine step-ledger residual        (exact rational, |res| < 1e-5)
C3  the 2.6e-6 margin: 5 cos theta_T vs 191/50   + theta_T's cell in the table
C4  theta* enclosure + "every multiset" audit    (exact)
"""

from fractions import Fraction as F
import json
import os

import span_table as ST
from span_table import S0, LO, F as _F   # noqa: F401  (same Fraction)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(ROOT))
RESULTS = os.path.join(ROOT, "results")


# ------------------------------------------------- exact ordered field Q[sqrt2]
class Q2:
    """p + q*sqrt(2) with p, q rational -- exact ordered field."""

    __slots__ = ("p", "q")

    def __init__(self, p, q=0):
        self.p, self.q = F(p), F(q)

    def __add__(self, o):
        o = o if isinstance(o, Q2) else Q2(o)
        return Q2(self.p + o.p, self.q + o.q)

    __radd__ = __add__

    def __sub__(self, o):
        o = o if isinstance(o, Q2) else Q2(o)
        return Q2(self.p - o.p, self.q - o.q)

    def __rsub__(self, o):
        return Q2(o) - self

    def __mul__(self, o):
        o = o if isinstance(o, Q2) else Q2(o)
        return Q2(self.p * o.p + 2 * self.q * o.q, self.p * o.q + self.q * o.p)

    __rmul__ = __mul__

    def sign(self):
        """Exact sign of p + q sqrt2 (no floats): compare p^2 with 2 q^2."""
        if self.q == 0:
            return (self.p > 0) - (self.p < 0)
        if self.p == 0:
            return (self.q > 0) - (self.q < 0)
        if (self.p > 0) == (self.q > 0):
            return 1 if self.p > 0 else -1
        # opposite signs: |p| vs sqrt2 |q|  <->  p^2 vs 2 q^2
        c = (self.p * self.p) - 2 * (self.q * self.q)
        big_p = c > 0                     # |p| > sqrt2 |q|
        return (1 if self.p > 0 else -1) if big_p else (1 if self.q > 0 else -1)

    def cmp_rat(self, r):
        return (self - Q2(r)).sign()

    def __repr__(self):
        return "%s + %s*sqrt2" % (self.p, self.q)


SQRT2 = Q2(0, 1)
HALF_SQRT2 = Q2(0, F(1, 2))          # cos 45 = sin 45 = sqrt2/2


# ----------------------------------------------------------------------- C1
def canary_C1():
    A6 = ST.index_set(6)
    hit = []
    for (a, b, c) in A6:
        f = HALF_SQRT2 * (a + b) + Q2(c)          # a cos45 + b sin45 + c
        if f.cmp_rat(LO) >= 0 and f.cmp_rat(S0) <= 0:
            hit.append((a, b, c))
    expected = sorted((a, b, c) for (a, b, c) in A6 if a + b == 4 and c == 1)
    ok_set = sorted(hit) == expected
    # s* = 2 sqrt2 + 1 in [lo, s0], proved by exact squaring comparisons
    sstar = Q2(1, 2)
    lo_gap = sstar.cmp_rat(LO)            # > 0 expected
    hi_gap = sstar.cmp_rat(S0)            # < 0 expected
    sq_lo = F(8) - (LO - 1) ** 2          # 8 - (141/50)^2 > 0  <=>  2sqrt2 > lo-1
    sq_hi = (S0 - 1) ** 2 - F(8)          # (s0-1)^2 - 8 > 0    <=>  2sqrt2 < s0-1
    return {
        "name": "C1 phi=45 s* reproduction",
        "pass": bool(ok_set and lo_gap > 0 and hi_gap < 0 and sq_lo > 0 and sq_hi > 0),
        "hitting_set": [list(t) for t in sorted(hit)],
        "hitting_set_size": len(hit),
        "expected_rule": "{(a,b,c) in A(6) : a+b=4, c=1}",
        "expected_size": len(expected),
        "hitting_set_equals_expected": ok_set,
        "span_at_45": "2*sqrt2 + 1",
        "exact_squaring_lo": {"claim": "8 - (191/50 - 1)^2 > 0",
                              "value_num": str(sq_lo.numerator),
                              "value_den": str(sq_lo.denominator)},
        "exact_squaring_hi": {"claim": "(s0 - 1)^2 - 8 > 0",
                              "value_num": str(sq_hi.numerator),
                              "value_den": str(sq_hi.denominator)},
    }


# ----------------------------------------------------------------------- C2
def _cert():
    path = os.path.join(REPO, "certs", "trump11_certificate.json")
    with open(path) as fh:
        return json.load(fh), path


def _h_of_t(t):
    """h(phi) = (cos phi + sin phi)/2 with t = tan(phi/2), exact."""
    return ((1 - t * t) + 2 * t) / (2 * (1 + t * t))


def _spine_residual(cert, idxs, axis):
    sq = cert["squares"]
    key = "cx" if axis == "x" else "cy"
    c_first = F(sq[idxs[0]][key])
    c_last = F(sq[idxs[-1]][key])
    t_first = F(sq[idxs[0]]["t"])
    t_last = F(sq[idxs[-1]]["t"])
    rhs = S0 - _h_of_t(t_first) - _h_of_t(t_last)
    res = (c_last - c_first) - rhs
    return res, c_first, c_last, t_first, t_last, rhs


def canary_C2():
    cert, path = _cert()
    assert F(cert["side"]) == S0, "certificate side != s0"
    out = {"name": "C2 Trump spine ledger", "certificate": os.path.relpath(path, REPO),
           "spines": {}, "pass": True}
    for axis, idxs in (("x", [0, 1, 8, 2]), ("y", [2, 8, 7, 9, 5])):
        res, c1, ck, t1, tk, rhs = _spine_residual(cert, idxs, axis)
        ok = abs(res) < F(1, 100000)
        out["spines"][axis] = {
            "squares": idxs, "k": len(idxs),
            "c_first": str(c1), "c_last": str(ck),
            "t_first": str(t1), "t_last": str(tk),
            "rhs_s0_minus_h_minus_h": str(rhs),
            "residual_exact": str(res),
            "_float_residual": float(res),
            "bound": "1/100000",
            "pass": bool(ok),
            "note": "flush links present (outside the flush-free P-chain class); "
                    "this canary tests the ledger arithmetic only",
        }
        out["pass"] = out["pass"] and ok
    return out


# ----------------------------------------------------------------------- C3
def canary_C3(table):
    tT = F(194075, 530594)
    cos = (1 - tT * tT) / (1 + tT * tT)
    diff = LO - 5 * cos                        # > 0  <=>  5 cos theta_T < 191/50
    degT = ST.deg_of_t(tT)
    cell = None
    for kind in ("excluded_intervals", "admitted_intervals"):
        for iv in table["columns"]["L6"][kind]:
            if iv["_float_deg_lo"] - 1e-9 <= degT <= iv["_float_deg_hi"] + 1e-9:
                cell = (kind, iv)
    # exact membership: which triples hit at theta_T
    hits = [t for t in ST.index_set(6) if LO <= ST.f_at(*t, tT) <= S0]
    adm = [iv for iv in table["columns"]["L6"]["admitted_intervals"]]
    nearest = None
    if cell is not None:
        nearest = {"cell_kind": cell[0],
                   "_float_deg_lo": cell[1]["_float_deg_lo"],
                   "_float_deg_hi": cell[1]["_float_deg_hi"]}
    neighbours = []
    for iv in adm:
        neighbours.append([iv["_float_deg_lo"], iv["_float_deg_hi"]])
    return {
        "name": "C3 the 2.6e-6 margin",
        "t_T": str(tT), "_float_theta_T_deg": degT,
        "cos_theta_T": str(cos),
        "claim": "5 cos theta_T < 191/50",
        "difference_191_50_minus_5cos": str(diff),
        "_float_difference": float(diff),
        "strictly_less": bool(diff > 0),
        "cell": nearest,
        "theta_T_admitted": bool(hits),
        "hitting_triples_at_theta_T": [list(t) for t in hits],
        "admitted_intervals_deg": neighbours,
        "pass": bool(diff > 0 and cell is not None),
    }


# ----------------------------------------------------------------------- C4
def canary_C4(table):
    ts, quad = ST.theta_star()
    below, above = ts.lo, ts.hi                 # rationals bracketing theta*
    fb = 4 * (ST.cos_t(below) - ST.sin_t(below))
    fa = 4 * (ST.cos_t(above) - ST.sin_t(above))
    a6 = table["near_flush_exclusion"]["audit_L6"]
    a8 = table["near_flush_exclusion"]["audit_L8"]
    full6 = len(a6["entries"]) == len(ST.multisets_cache(6, 0)) == a6["n_multisets"]
    full8 = len(a8["entries"]) == len(ST.multisets_cache(8, 0)) == a8["n_multisets"]
    return {
        "name": "C4 theta* enclosure + full multiset audit",
        "quadratic": {"A": str(quad[0]), "B": str(quad[1]), "C": str(quad[2]),
                      "root_index": ts.idx},
        "_float_theta_star_deg": ST.deg_of_t(float(ts)),
        "t_below": str(below), "four_cos_minus_sin_below": str(fb),
        "t_above": str(above), "four_cos_minus_sin_above": str(fa),
        "below_gt_s0": bool(fb > S0), "above_lt_s0": bool(fa < S0),
        "audit_L6_covers_all_multisets": bool(full6),
        "audit_L8_covers_all_multisets": bool(full8),
        "audit_L6_excluded": bool(a6["excluded"]),
        "audit_L8_excluded": bool(a8["excluded"]),
        "audit_L6_hits_window": a6["n_hits_window"],
        "pass": bool(fb > S0 and fa < S0 and full6 and full8
                     and a6["excluded"] and a8["excluded"]),
    }


def main():
    with open(os.path.join(RESULTS, "span_table.json")) as fh:
        table = json.load(fh)
    res = [canary_C1(), canary_C2(), canary_C3(table), canary_C4(table)]
    doc = {"canaries": res, "all_pass": all(r["pass"] for r in res)}
    path = os.path.join(RESULTS, "canaries_a50.json")
    with open(path, "w") as fh:
        json.dump(doc, fh, indent=1)
    for r in res:
        print("%-40s %s" % (r["name"], "PASS" if r["pass"] else "FAIL"))
    print("all_pass:", doc["all_pass"])
    if not doc["all_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
