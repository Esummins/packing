"""Exact orbit counting for the A59 Level-0 grain census.

KEY OBSERVATION.  Every hard filter except the per-element capacity caps and full
planarity is a condition on a PAIR of free squares, and which condition applies
depends only on whether that pair is an edge of E:

    non-edge (i,j):  masks must merely coexist   -> predicate  N(a,b)
    edge     (i,j):  masks must also be able to touch -> predicate  T(a,b) <= N

(the hop bound |c_i-c_j| <= sqrt2*hops is vacuous for hops >= 2 on R(s), see the
report), and T(a,b) implies N(a,b).  Therefore the number of LABELLED structures
(graph on 6 labelled vertices + mask tuple) is

    Z = sum over mask tuples m of  prod_{i<j} w(m_i, m_j),
    w(a,b) = [N(a,b)] + [T(a,b)]  in {0,1,2}

and the number of S6-ORBITS is Burnside over S6.  For a permutation p with
cycles C_1..C_c, a fixed pair (G,m) has m constant on cycles and G constant on
p-orbits of vertex pairs; all pairs in one orbit join the same two cycles, so

    Z_p = sum over a in M^c of prod over pair-orbits O of w(a_u(O), a_v(O)).

All intermediate quantities are integers < 2^53, so float64 arithmetic (BLAS) is
EXACT here; the outer accumulation is done in Python ints.
"""
import itertools
import math
import numpy as np


def orbit_structure(p):
    """(c, K) for a permutation p of range(k): c cycles, K[u][v] = number of
    p-orbits of unordered vertex pairs joining cycle u and cycle v."""
    k = len(p)
    seen = [False] * k
    cyc_of = [-1] * k
    c = 0
    for s in range(k):
        if seen[s]:
            continue
        x = s
        while not seen[x]:
            seen[x] = True
            cyc_of[x] = c
            x = p[x]
        c += 1
    K = [[0] * c for _ in range(c)]
    done = set()
    for i in range(k):
        for j in range(i + 1, k):
            if (i, j) in done:
                continue
            a, b = i, j
            while True:
                done.add((min(a, b), max(a, b)))
                a, b = p[a], p[b]
                if (min(a, b), max(a, b)) == (i, j):
                    break
            u, v = cyc_of[i], cyc_of[j]
            if u > v:
                u, v = v, u
            K[u][v] += 1
    clen = [0] * c
    for i in range(k):
        clen[cyc_of[i]] += 1
    return c, K, clen


def _mpow(W, e, n):
    if e == 0:
        return np.ones((n, n))
    if e == 1:
        return W
    return W ** e


def _z3(s0, s1, s2, M01, M02, M12):
    """sum_{a,b,c} s0[a]s1[b]s2[c] M01[a,b] M02[a,c] M12[b,c]."""
    U = s1[None, :] * M01              # U[a] = s1 * M01[a]
    V = s2[None, :] * M02              # V[a] = s2 * M02[a]
    R = U @ M12                        # R[a] = U[a] @ M12
    inner = np.einsum('ij,ij->i', R, V)
    return float(np.dot(s0, inner))


def z_general(W, c, K, vw=None, clen=None):
    """sum over a in M^c of prod_u diag(W)[a_u]^K[u][u] * vw[a_u]^clen[u]
       * prod_{u<v} W^K[u][v][a_u,a_v]."""
    n = W.shape[0]
    dg = np.diag(W).copy()
    sv = [dg ** K[u][u] if K[u][u] else np.ones(n) for u in range(c)]
    if vw is not None:
        sv = [sv[u] * (vw ** (clen[u] if clen else 1)) for u in range(c)]
    Wk = [[None] * c for _ in range(c)]
    for u in range(c):
        for v in range(u + 1, c):
            Wk[u][v] = _mpow(W, K[u][v], n)
    if c == 1:
        return int(round(float(sv[0].sum())))
    if c == 2:
        return int(round(float(sv[0] @ (Wk[0][1] @ sv[1]))))
    if c == 3:
        return int(round(_z3(sv[0], sv[1], sv[2], Wk[0][1], Wk[0][2], Wk[1][2])))
    # c >= 4 : fix the first c-3 indices, reduce to the 3-index kernel
    fixed = c - 3
    tot = 0
    idx = list(range(fixed, c))
    for pref in itertools.product(range(n), repeat=fixed):
        coef = 1.0
        for u in range(fixed):
            coef *= sv[u][pref[u]]
            for v in range(u + 1, fixed):
                coef *= Wk[u][v][pref[u], pref[v]]
        if coef == 0.0:
            continue
        s = []
        for t, v in enumerate(idx):
            vec = sv[v].copy()
            for u in range(fixed):
                vec = vec * Wk[u][v][pref[u]]
            s.append(vec)
        v3 = _z3(s[0], s[1], s[2],
                 Wk[idx[0]][idx[1]], Wk[idx[0]][idx[2]], Wk[idx[1]][idx[2]])
        assert abs(v3) < 2.0 ** 53 and abs(coef) < 2.0 ** 53
        tot += int(round(coef)) * int(round(v3))
    return int(tot)


def z_identity6(W, vw=None):
    """Fast exact path for p = identity on 6 vertices (all K[u][v] = 1).
    The summand is symmetric in all six indices, so sum over sorted triples
    (a0<=a1<=a2) with multinomial multiplicities.  vw = optional vertex weight."""
    n = W.shape[0]
    one = np.ones(n) if vw is None else vw
    tot = 0
    for a0 in range(n):
        W0 = W[a0]
        for a1 in range(a0, n):
            w01 = W0[a1]
            if w01 == 0:
                continue
            r = W0 * W[a1]
            for a2 in range(a1, n):
                pre = w01 * W0[a2] * W[a1, a2] * one[a0] * one[a1] * one[a2]
                if pre == 0:
                    continue
                mult = 1 if (a0 == a1 == a2) else (3 if (a0 == a1 or a1 == a2) else 6)
                q = r * W[a2] * one
                U = q[None, :] * W          # U[a3] = q * W[a3]
                R = U @ W
                inner = np.einsum('ij,ij->i', U, R)
                val = float(np.dot(q, inner))
                assert val < 2.0 ** 53
                tot += mult * int(round(float(pre))) * int(round(val))
    return int(tot)


CYCLE_TYPES = {}


def _cycle_type_reps(k=6):
    if k in CYCLE_TYPES:
        return CYCLE_TYPES[k]
    reps = {}
    for p in itertools.permutations(range(k)):
        seen = [False] * k
        ct = []
        for s in range(k):
            if seen[s]:
                continue
            L = 0
            x = s
            while not seen[x]:
                seen[x] = True
                x = p[x]
                L += 1
            ct.append(L)
        key = tuple(sorted(ct, reverse=True))
        if key not in reps:
            reps[key] = [p, 0]
        reps[key][1] += 1
    CYCLE_TYPES[k] = reps
    return reps


def burnside(W, verbose=False, log=None, k=6, vw=None):
    """Exact number of S_k-orbits of (graph, mask-tuple) pairs weighted by W,
    with optional per-vertex mask weight vw."""
    reps = _cycle_type_reps(k)
    tot = 0
    detail = {}
    for key, (p, size) in sorted(reps.items()):
        c, K, clen = orbit_structure(p)
        if k == 6 and key == (1, 1, 1, 1, 1, 1):
            z = z_identity6(W, vw)
        else:
            z = z_general(W, c, K, vw, clen)
        detail[str(key)] = dict(size=size, cycles=c, Z=z)
        tot += size * z
        if verbose:
            msg = '  cycle type %-18s size %3d  c=%d  Z=%d' % (str(key), size, c, z)
            print(msg, flush=True)
            if log:
                log(msg)
    g = math.factorial(k)
    assert tot % g == 0, 'Burnside sum not divisible by |S_k|'
    return tot // g, detail


def prefix_counts(W):
    """Exact number of LABELLED valid k-prefixes (mask tuples m_0..m_{k-1} with all
    pairs among them allowed, weighted by the number of admissible edge statuses)
    for k = 1..6.  This is the per-prefix growth curve of the DFS."""
    n = W.shape[0]
    out = [n]
    ones = np.ones(n)
    out.append(int(round(float(ones @ W @ ones))))                     # k=2
    out.append(int(round(_z3(ones, ones, ones, W, W, W))))             # k=3
    for k in (4, 5, 6):
        c = k
        K = [[0] * c for _ in range(c)]
        for u in range(c):
            for v in range(u + 1, c):
                K[u][v] = 1
        if k == 6:
            # symmetric fast path, but the prefix count is the labelled Z_id
            out.append(z_identity6(W))
        else:
            out.append(z_general(W, c, K))
    return out
