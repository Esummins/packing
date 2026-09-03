"""A88 exact orbit counting under S_k x D4 for the FACTORABLE Level-0 subset.

Method = A59 code/count_exact.py generalised from S_6 to S_11 x D4.

Object counted: (simple graph on k labelled squares, wall-mask tuple) with a
FACTORABLE admissibility predicate:
    every pair    -> N(a,b)   (coexistence: max centre-box distance >= 1)
    every EDGE    -> T(a,b)   (touching window: min centre-box distance <= sqrt2)
so the pair weight is w(a,b) = [N] * (1 + [T]) in {0,1,2}: 0 = the pair is
impossible, 1 = the pair may only be a non-edge, 2 = either.  Every F0 structure
satisfies this, so the orbit count is a rigorous UPPER BOUND on the F0 census.

Group action.  g = (pi, delta) in S_k x D4 fixes (m, E) iff m_{pi(i)} = delta(m_i)
and E is pi-invariant.  On a cycle of length l the mask is m_{pi^r(b)} = delta^r(a)
with a in Fix(delta^l); pair orbits between cycles u, v of lengths l_u, l_v have
representatives (b_u, pi^r(b_v)) for r = 0..gcd(l_u,l_v)-1 (masks (a_u, delta^r a_v)),
and within one cycle of length l they are (b, pi^d b), d = 1..floor(l/2).
All weights are 0 or a power of two, so every Z is accumulated EXACTLY as
sum over exponents of (integer multiplicity) * 2^exponent.
"""
import os
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')
import itertools
import math
import sys
import time
from collections import defaultdict

import numpy as np

import a88lib as A


# ---------------------------------------------------------------- partitions
def partitions(n, maxp=None):
    if maxp is None:
        maxp = n
    if n == 0:
        yield ()
        return
    for p in range(min(n, maxp), 0, -1):
        for rest in partitions(n - p, p):
            yield (p,) + rest


def class_size(k, lam):
    mult = defaultdict(int)
    for p in lam:
        mult[p] += 1
    d = 1
    for j, mj in mult.items():
        d *= (j ** mj) * math.factorial(mj)
    return math.factorial(k) // d


def multiset_vectors(n, ns):
    """All count vectors of length ns summing to n, with multinomial weights."""
    out = []

    def rec(pos, rem, cur):
        if pos == ns - 1:
            cur.append(rem)
            c = tuple(cur)
            m = math.factorial(n)
            for x in c:
                m //= math.factorial(x)
            out.append((c, m))
            cur.pop()
            return
        for v in range(rem + 1):
            cur.append(v)
            rec(pos + 1, rem - v, cur)
            cur.pop()
    rec(0, n, [])
    return out


# ---------------------------------------------------------------- the counter
class Model:
    """masks: list of raw mask ints; d4tab[d][a] = index of delta_d(mask a);
    wok[a][b] bool, wexp[a][b] int  (weight = wok ? 2**wexp : 0)."""

    def __init__(self, masks, d4tab, wok, wexp):
        self.masks = list(masks)
        self.n = len(masks)
        self.d4 = np.asarray(d4tab, dtype=np.int64)
        self.wok = np.asarray(wok, dtype=bool)
        self.wexp = np.asarray(wexp, dtype=np.int64)

    def dpow(self, d, r, a):
        for _ in range(r):
            a = int(self.d4[d, a])
        return a


def build_from_tables(masks, allowed_idx, edge_ok, coex_ok):
    pass


def _fix_domain(model, d, l):
    return [a for a in range(model.n) if model.dpow(d, l, a) == a]


def _group_data(model, d, lengths):
    """Per distinct cycle length: domain, within-cycle weight; per length pair:
    the cross matrix.  Returns (doms, Vok, Vexp, Sok, Sexp, Cok, Cexp)."""
    L = sorted(set(lengths))
    doms = {l: _fix_domain(model, d, l) for l in L}
    Vok, Vexp, Sok, Sexp = {}, {}, {}, {}
    for l in L:
        dom = doms[l]
        nd = len(dom)
        vok = np.ones(nd, dtype=bool)
        vex = np.zeros(nd, dtype=np.int64)
        for t, a in enumerate(dom):
            for q in range(1, l // 2 + 1):
                b = model.dpow(d, q, a)
                if not model.wok[a, b]:
                    vok[t] = False
                vex[t] += model.wexp[a, b]
        Vok[l], Vexp[l] = vok, vex
        sok = np.ones((nd, nd), dtype=bool)
        sex = np.zeros((nd, nd), dtype=np.int64)
        for t, a in enumerate(dom):
            for u, bb in enumerate(dom):
                for r in range(l):                     # gcd(l,l) = l orbits
                    b2 = model.dpow(d, r, bb)
                    if not model.wok[a, b2]:
                        sok[t, u] = False
                    sex[t, u] += model.wexp[a, b2]
        Sok[l], Sexp[l] = sok, sex
    Cok, Cexp = {}, {}
    for i, l1 in enumerate(L):
        for l2 in L[i + 1:]:
            g = math.gcd(l1, l2)
            d1, d2 = doms[l1], doms[l2]
            cok = np.ones((len(d1), len(d2)), dtype=bool)
            cex = np.zeros((len(d1), len(d2)), dtype=np.int64)
            for t, a in enumerate(d1):
                for u, bb in enumerate(d2):
                    for r in range(g):
                        b2 = model.dpow(d, r, bb)
                        if not model.wok[a, b2]:
                            cok[t, u] = False
                        cex[t, u] += model.wexp[a, b2]
            Cok[(l1, l2)], Cexp[(l1, l2)] = cok, cex
    return doms, Vok, Vexp, Sok, Sexp, Cok, Cexp


def z_for(model, d, lam):
    """Exact sum over (delta_d, pi of cycle type lam)-fixed structures, returned
    as a dict exponent -> integer multiplicity (value = sum mult * 2**exp)."""
    lengths = list(lam)
    mult_by_len = defaultdict(int)
    for l in lengths:
        mult_by_len[l] += 1
    L = sorted(mult_by_len)
    doms, Vok, Vexp, Sok, Sexp, Cok, Cexp = _group_data(model, d, lengths)
    # per-group enumeration
    groups = []
    for l in L:
        n = mult_by_len[l]
        nd = len(doms[l])
        if nd == 0:
            return {}
        rows = []
        for c, mlt in multiset_vectors(n, nd):
            ok = True
            e = 0
            for a in range(nd):
                if c[a] == 0:
                    continue
                if not Vok[l][a]:
                    ok = False
                    break
                e += c[a] * int(Vexp[l][a])
                if c[a] >= 2:
                    if not Sok[l][a, a]:
                        ok = False
                        break
                    e += (c[a] * (c[a] - 1) // 2) * int(Sexp[l][a, a])
            if ok:
                for a in range(nd):
                    if c[a] == 0:
                        continue
                    for b in range(a + 1, nd):
                        if c[b] == 0:
                            continue
                        if not Sok[l][a, b]:
                            ok = False
                            break
                        e += c[a] * c[b] * int(Sexp[l][a, b])
                    if not ok:
                        break
            if ok:
                rows.append((c, mlt, e))
        if not rows:
            return {}
        C = np.array([r[0] for r in rows], dtype=np.int64)
        M = np.array([r[1] for r in rows], dtype=object)
        E = np.array([r[2] for r in rows], dtype=np.int64)
        groups.append(dict(l=l, C=C, M=M, E=E, nd=nd))
    out = defaultdict(int)
    ng = len(groups)

    def rec(gi, mult, exp, fields, bads):
        g = groups[gi]
        C, M, E = g['C'], g['M'], g['E']
        ex = E + C.dot(fields[gi])
        bad = bads[gi]
        good = (C[:, bad] == 0).all(1) if bad.any() else np.ones(len(C), bool)
        idx = np.nonzero(good)[0]
        if gi == ng - 1:
            for t in idx:
                out[exp + int(ex[t])] += mult * int(M[t])
            return
        for t in idx:
            c = C[t]
            nz = c > 0
            nf = list(fields)
            nb = list(bads)
            for gj in range(gi + 1, ng):
                l1, l2 = g['l'], groups[gj]['l']
                key = (min(l1, l2), max(l1, l2))
                cok, cex = Cok[key], Cexp[key]
                if l1 > l2:
                    cok, cex = cok.T, cex.T
                nf[gj] = fields[gj] + c.dot(cex)
                nb[gj] = bads[gj] | (~cok[nz]).any(0)
            rec(gi + 1, mult * int(M[t]), exp + int(ex[t]), nf, nb)

    f0 = [np.zeros(g['nd'], dtype=np.int64) for g in groups]
    b0 = [np.zeros(g['nd'], dtype=bool) for g in groups]
    rec(0, 1, 0, f0, b0)
    return dict(out)


def burnside(model, k, verbose=False):
    tot = 0
    detail = {}
    t0 = time.time()
    for lam in partitions(k):
        cs = class_size(k, lam)
        sub = 0
        for d in range(8):
            z = z_for(model, d, lam)
            sub += sum(m * (1 << e) for e, m in z.items())
        tot += cs * sub
        detail[str(lam)] = dict(class_size=cs, Zsum=sub)
        if verbose:
            print('  lam=%-22s size %-9d Zsum=%d  (%.1fs)'
                  % (str(lam), cs, sub, time.time() - t0), flush=True)
    g = math.factorial(k) * 8
    assert tot % g == 0, 'Burnside sum not divisible by k!*8: %d' % (tot % g)
    return tot // g, detail, tot


# --------------------------------------------------------------- models
def model_all16(uniform_edges=True):
    """A31 row R0: all 16 masks, no filter (every pair may be edge or non-edge)."""
    masks = list(range(16))
    d4 = [[int(A.MT[d][m]) for m in masks] for d in range(8)]
    wok = np.ones((16, 16), bool)
    wexp = np.ones((16, 16), dtype=np.int64)
    return Model(masks, d4, wok, wexp)


def model_allowed9(uniform_edges=True):
    """A31 row R2: the 9 L5(b)-admissible masks, no further filter."""
    masks = list(A.ALLOWED)
    d4 = A.MTD.tolist()
    wok = np.ones((9, 9), bool)
    wexp = np.ones((9, 9), dtype=np.int64)
    return Model(masks, d4, wok, wexp)


def model_factorable():
    """The A88 factorable subset: masks in ALLOWED, pairwise coexistence, and the
    touching window on edges."""
    masks = list(A.ALLOWED)
    d4 = A.MTD.tolist()
    wok = A.COEX.copy()
    wexp = A.TOUCH.astype(np.int64)
    return Model(masks, d4, wok, wexp)


def model_coex_only():
    masks = list(A.ALLOWED)
    d4 = A.MTD.tolist()
    wok = A.COEX.copy()
    wexp = np.ones((9, 9), dtype=np.int64)
    return Model(masks, d4, wok, wexp)


# --------------------------------------------------------------- brute force
def brute_orbits(model, k):
    """Independent brute-force orbit count (small k only)."""
    n = model.n
    pairs = [(i, j) for i in range(k) for j in range(i + 1, k)]
    perms = list(itertools.permutations(range(k)))
    seen = set()
    cnt = 0
    for m in itertools.product(range(n), repeat=k):
        if not all(model.wok[m[i], m[j]] for i, j in pairs):
            continue
        allowed = [q for q, (i, j) in enumerate(pairs)
                   if model.wexp[m[i], m[j]] > 0]
        for sub in range(1 << len(allowed)):
            E = frozenset(pairs[allowed[t]] for t in range(len(allowed))
                          if (sub >> t) & 1)
            key = (m, E)
            if key in seen:
                continue
            cnt += 1
            for p in perms:
                for d in range(8):
                    m2 = [0] * k
                    for i in range(k):
                        m2[p[i]] = int(model.d4[d, m[i]])
                    E2 = frozenset((min(p[a], p[b]), max(p[a], p[b]))
                                   for a, b in E)
                    seen.add((tuple(m2), E2))
    return cnt


def main():
    import json
    out = {}
    print('--- validation: A31 rows R0 / R2 by Burnside ---', flush=True)
    for k in (3, 4):
        r0, _, _ = burnside(model_all16(), k)
        r2, _, _ = burnside(model_allowed9(), k)
        print('k=%d  R0=%d (A31 %s)   R2=%d (A31 %s)'
              % (k, r0, {3: 1072, 4: 28796}[k], r2, {3: 192, 4: 2979}[k]),
              flush=True)
        out['R0_k%d' % k] = r0
        out['R2_k%d' % k] = r2
    out['R0_R2_match_A31'] = (out['R0_k3'] == 1072 and out['R2_k3'] == 192
                              and out['R0_k4'] == 28796 and out['R2_k4'] == 2979)
    print('--- validation: weighted Burnside vs brute force ---', flush=True)
    mf = model_factorable()
    for k in (3, 4):
        bo, _, _ = burnside(mf, k)
        bf = brute_orbits(mf, k)
        print('k=%d factorable: burnside=%d brute=%d  %s'
              % (k, bo, bf, 'OK' if bo == bf else 'MISMATCH'), flush=True)
        out['fact_k%d_burnside' % k] = bo
        out['fact_k%d_brute' % k] = bf
    out['brute_match'] = all(out['fact_k%d_burnside' % k] == out['fact_k%d_brute' % k]
                             for k in (3, 4))
    print('--- k = 11 factorable Burnside (exact UPPER bound) ---', flush=True)
    t0 = time.time()
    ub, detail, tot = burnside(mf, 11, verbose=True)
    print('k=11 factorable orbits (EXACT UB) = %d   (%.1f s)'
          % (ub, time.time() - t0), flush=True)
    out['k11_factorable_orbits_UB'] = ub
    out['k11_burnside_raw_sum'] = str(tot)
    out['k11_seconds'] = round(time.time() - t0, 1)
    # cumulative ablation of the factorable filters at k=11
    print('--- exact cumulative ablation of the factorable filters (k=11) ---',
          flush=True)
    ab = {}
    for name, mdl in [('F1 mask admissibility (L5b)', model_allowed9()),
                      ('F2 + pairwise coexistence', model_coex_only()),
                      ('F3 + touching window on edges', mf)]:
        v, _, _ = burnside(mdl, 11)
        ab[name] = v
        print('  %-34s -> %d' % (name, v), flush=True)
    out['k11_ablation_exact'] = ab
    # labelled partition function (identity term) for the MC normalisation
    zid = z_for(mf, 0, tuple([1] * 11))
    Z = sum(m * (1 << e) for e, m in zid.items())
    out['k11_labelled_Z'] = str(Z)
    print('labelled factorable structures Z = %d  (%.4e)' % (Z, float(Z)))
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, '..', 'results', 'burnside88.json'), 'w') as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps({a: b for a, b in out.items() if a != 'k11_ablation_exact'},
                     indent=1))


if __name__ == '__main__':
    main()
