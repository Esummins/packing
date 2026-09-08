"""S_k graph representatives with automorphism groups (A31 lib0 pattern, copied
into A59 so this attempt is self-contained)."""
import itertools
import numpy as np

INF_D = 99


def pair_index(k):
    idx = {}
    e = 0
    for i in range(k):
        for j in range(i + 1, k):
            idx[(i, j)] = e
            e += 1
    return idx


def _perm_edge_maps(k):
    idx = pair_index(k)
    ne = len(idx)
    perms = list(itertools.permutations(range(k)))
    M = np.zeros((len(perms), ne), dtype=np.int64)
    for pi, p in enumerate(perms):
        for (i, j), e in idx.items():
            a, b = p[i], p[j]
            if a > b:
                a, b = b, a
            M[pi, idx[(a, b)]] = e
    return perms, M


def canon_and_aut(mask, k, perms, M, pw):
    ne = M.shape[1]
    bits = ((mask >> np.arange(ne)) & 1).astype(np.int64)
    img = bits[M]
    vals = img @ pw
    mn = int(vals.min())
    aut = [perms[t] for t in np.nonzero(vals == mask)[0]] if mn == mask else None
    return mn, aut


_cache = {}


def graph_reps(k):
    if k in _cache:
        return _cache[k]
    perms, M = _perm_edge_maps(k)
    ne = M.shape[1]
    pw = (1 << np.arange(ne)).astype(np.int64)
    if k <= 1:
        reps = [(0, [tuple(range(k))])]
        _cache[k] = reps
        return reps
    prev = graph_reps(k - 1)
    idx = pair_index(k)
    pidx = pair_index(k - 1)
    seen = {}
    for pm, _ in prev:
        base = 0
        for (i, j), e in pidx.items():
            if (pm >> e) & 1:
                base |= 1 << idx[(i, j)]
        for nb in range(1 << (k - 1)):
            g = base
            for i in range(k - 1):
                if (nb >> i) & 1:
                    g |= 1 << idx[(i, k - 1)]
            c, aut = canon_and_aut(g, k, perms, M, pw)
            if c not in seen:
                if aut is None:
                    _, aut = canon_and_aut(c, k, perms, M, pw)
                seen[c] = aut
    reps = sorted(seen.items())
    _cache[k] = reps
    return reps


def mask_to_adj(mask, k):
    idx = pair_index(k)
    adj = [0] * k
    edges = []
    for (i, j), e in idx.items():
        if (mask >> e) & 1:
            adj[i] |= 1 << j
            adj[j] |= 1 << i
            edges.append((i, j))
    return adj, sorted(edges)


def hop_matrix(adj, k):
    D = [[INF_D] * k for _ in range(k)]
    for s in range(k):
        D[s][s] = 0
        frontier = [s]
        d = 0
        while frontier:
            d += 1
            nxt = []
            for u in frontier:
                m = adj[u]
                while m:
                    b = m & -m
                    v = b.bit_length() - 1
                    m ^= b
                    if D[s][v] > d:
                        D[s][v] = d
                        nxt.append(v)
            frontier = nxt
    return D


def edges_of(mask, k):
    return mask_to_adj(mask, k)[1]
