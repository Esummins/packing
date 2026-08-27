"""A34 independent exact verifier for rounded SOS certificates (Fable, advisor-side).

Certifies: min of objective over the semialgebraic set >= lambda_certified, where
  objective - lambda = sigma_0 + sum_k sigma_k * g_k + sum_l phi_l * h_l + r,
sigma SOS (rational Gram PSD, checked by exact LDL^T), g_k >= 0 / h_l = 0 the constraints,
and the residual r is bounded exactly on the variable box:  lambda_certified = lambda - bound(|r|).

JSON schema:
{
 "lambda": "num/den",
 "vars": ["x1", ...],
 "box": {"x1": ["lo", "hi"], ...},                 # every var MUST have finite rational bounds
 "objective": {"<mono>": "coef", ...},             # mono: "1" or "x1^2*x3"
 "constraints": [{"name": "...", "type": "ineq"|"eq", "poly": {...}}, ...],
 "sos": [{"constraint": -1 | k, "basis": ["<mono>", ...], "gram": [["coef",...],...]}, ...],
   # constraint -1 = sigma_0; k must index an "ineq"
 "eqmult": [{"constraint": l, "poly": {...}}, ...]  # l must index an "eq"
}
All numbers rational strings. Usage: python verify_sos.py cert.json
Exit 0 + prints CERTIFIED lambda' iff everything checks in exact arithmetic.
"""
import json, sys
from fractions import Fraction as F


def parse_mono(s):
    if s.strip() in ("1", ""):
        return ()
    out = []
    for f in s.split("*"):
        if "^" in f:
            v, e = f.split("^"); out.append((v.strip(), int(e)))
        else:
            out.append((f.strip(), 1))
    out.sort()
    # merge repeated vars
    merged = {}
    for v, e in out:
        merged[v] = merged.get(v, 0) + e
    return tuple(sorted(merged.items()))


def parse_poly(d):
    p = {}
    for m, c in d.items():
        k = parse_mono(m)
        p[k] = p.get(k, F(0)) + F(c)
    return {k: v for k, v in p.items() if v != 0}


def mono_mul(a, b):
    d = dict(a)
    for v, e in b:
        d[v] = d.get(v, 0) + e
    return tuple(sorted(d.items()))


def poly_mul(p, q):
    r = {}
    for ma, ca in p.items():
        for mb, cb in q.items():
            m = mono_mul(ma, mb)
            r[m] = r.get(m, F(0)) + ca * cb
    return {k: v for k, v in r.items() if v != 0}


def poly_add(p, q, sc=F(1)):
    r = dict(p)
    for m, c in q.items():
        r[m] = r.get(m, F(0)) + sc * c
    return {k: v for k, v in r.items() if v != 0}


def psd_ldl(G):
    """Exact PSD check by pivoted outer-product elimination. Returns True iff G is PSD."""
    n = len(G)
    A = [[F(G[i][j]) for j in range(n)] for i in range(n)]
    # symmetry
    for i in range(n):
        for j in range(i):
            if A[i][j] != A[j][i]:
                return False, "not symmetric"
    active = list(range(n))
    while active:
        # pick max diagonal pivot
        piv = max(active, key=lambda i: A[i][i])
        if A[piv][piv] < 0:
            return False, "negative diagonal"
        if A[piv][piv] == 0:
            # all remaining diagonals <= 0 -> must all be 0 with zero rows
            for i in active:
                if A[i][i] != 0:
                    return False, "negative diagonal"
                for j in active:
                    if A[i][j] != 0:
                        return False, "zero diagonal, nonzero row"
            return True, "ok"
        d = A[piv][piv]
        active.remove(piv)
        col = {i: A[i][piv] for i in active}
        for i in active:
            if col[i] == 0:
                continue
            ci = col[i] / d
            for j in active:
                A[i][j] -= ci * col[j]
    return True, "ok"


def mono_bound(mono, box):
    """sup |mono| over the box, exact rational."""
    b = F(1)
    for v, e in mono:
        lo, hi = box[v]
        b *= max(abs(lo), abs(hi)) ** e
    return b


def main(path):
    cert = json.load(open(path))
    lam = F(cert["lambda"])
    box = {v: (F(lo), F(hi)) for v, (lo, hi) in cert["box"].items()}
    obj = parse_poly(cert["objective"])
    cons = [(c["name"], c["type"], parse_poly(c["poly"])) for c in cert["constraints"]]

    # every variable used anywhere must have a box bound
    def vars_of(p):
        return {v for m in p for v, _ in m}
    used = vars_of(obj)
    for _, _, p in cons:
        used |= vars_of(p)

    # assemble sum
    acc = {}
    n_sos = 0
    for blk in cert["sos"]:
        k = blk["constraint"]
        G = blk["gram"]
        ok, why = psd_ldl(G)
        if not ok:
            print(f"FAIL: Gram (constraint {k}) not PSD: {why}"); return 1
        basis = [parse_mono(m) for m in blk["basis"]]
        for m in blk["basis"]:
            used |= vars_of({parse_mono(m): F(1)})
        sos_poly = {}
        n = len(basis)
        for i in range(n):
            for j in range(n):
                m = mono_mul(basis[i], basis[j])
                sos_poly[m] = sos_poly.get(m, F(0)) + F(G[i][j])
        if k == -1:
            acc = poly_add(acc, sos_poly)
        else:
            name, typ, g = cons[k]
            if typ != "ineq":
                print(f"FAIL: SOS multiplier on non-ineq constraint {k} ({name})"); return 1
            acc = poly_add(acc, poly_mul(sos_poly, g))
        n_sos += 1
    for em in cert.get("eqmult", []):
        l = em["constraint"]
        name, typ, h = cons[l]
        if typ != "eq":
            print(f"FAIL: eq multiplier on non-eq constraint {l} ({name})"); return 1
        phi = parse_poly(em["poly"])
        used |= vars_of(phi)
        acc = poly_add(acc, poly_mul(phi, h))

    missing = [v for v in used if v not in box]
    if missing:
        print(f"FAIL: no box bounds for vars {missing}"); return 1

    # residual r = objective - lambda - acc
    r = poly_add(obj, {(): -lam})
    r = poly_add(r, acc, sc=F(-1))
    rbound = sum(abs(c) * mono_bound(m, box) for m, c in r.items())
    lam_cert = lam - rbound
    print(f"PSD blocks: {n_sos} OK; residual terms: {len(r)}; |r| <= {float(rbound):.3e}")
    print(f"CERTIFIED: objective >= {lam_cert} = {float(lam_cert):.12f} on the constrained box")
    print(f"(claimed lambda {float(lam):.12f}, margin lost to rounding {float(rbound):.3e})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
