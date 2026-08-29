"""A31 Level-0 core: enumeration of pruned contact/support structures.

Object enumerated: the SUPPORT graph H on a loaded core of k squares plus the 4 wall
nodes (L,B,R,T in cycle order), up to  S_k (relabel squares) x D4 (symmetries of the
wall 4-cycle).  Edges: square-square and square-wall only (no wall-wall contact edges;
the wall 4-cycle is an artefact used only in the L4 planarity drawing).

All filters are the ones of docs/proofs/structure_lemmas.md.  Every HARD filter used
here is a PROVED NECESSARY condition, so it can only remove structures that cannot
occur (never a realizable one).  SOFT filters are computed but reported separately.
"""
import math, itertools, json, os
import numpy as np

SQRT2 = math.sqrt(2.0)
HALF = SQRT2 / 2.0
# container side of a minimiser: s(11) in [S_LO, S_HI].  S_LO = 3.80 is the certified
# lower bound (A06/A07/A08); S_HI = 3.8771 > Trump 3.8770835900228 is the target.
S_LO, S_HI = 3.80, 3.8771

# wall bits: 0=L 1=B 2=R 3=T  (cycle order L-B-R-T)
OPP = [(0, 2), (1, 3)]
# L5(b): wall-degree <= 2 and the two walls adjacent  => 9 admissible wall masks
ALLOWED = [0, 1, 2, 4, 8, 3, 6, 12, 9]
ALLOWED_SET = set(ALLOWED)
POP = [bin(m).count("1") for m in range(16)]


# ---------------------------------------------------------------- D4 on the walls
def d4_perms():
    P = [tuple((i + j) % 4 for i in range(4)) for j in range(4)]       # rotations
    P += [tuple((j - i) % 4 for i in range(4)) for j in range(4)]      # reflections
    return P


D4 = d4_perms()


def _mask_tab(p):
    t = np.zeros(16, dtype=np.uint8)
    for m in range(16):
        n = 0
        for b in range(4):
            if (m >> b) & 1:
                n |= 1 << p[b]
        t[m] = n
    return t


MT = [_mask_tab(p) for p in D4]          # 8 mask-relabelling tables


# ---------------------------------------------------------------- L5(a) broad phase
def _box(m):
    """Certified centre box of a square with wall-contact mask m (sound for any
    container side in [S_LO, S_HI]).  Half-width of a unit square in any direction is
    in [1/2, sqrt2/2]."""
    if m & 1:
        x = (0.5, HALF)
    elif m & 4:
        x = (S_LO - HALF, S_HI - 0.5)
    else:
        x = (0.5, S_HI - 0.5)
    if m & 2:
        y = (0.5, HALF)
    elif m & 8:
        y = (S_LO - HALF, S_HI - 0.5)
    else:
        y = (0.5, S_HI - 0.5)
    return x, y


def _rect_range(b1, b2):
    (x1, X1), (y1, Y1) = b1
    (x2, X2), (y2, Y2) = b2
    dxmin = max(0.0, max(x1 - X2, x2 - X1))
    dymin = max(0.0, max(y1 - Y2, y2 - Y1))
    dxmax = max(X1 - x2, X2 - x1)
    dymax = max(Y1 - y2, Y2 - y1)
    return math.hypot(dxmin, dymin), math.hypot(dxmax, dymax)


def build_l5a_tables():
    """BAD[m1*16+m2]  : the two centre boxes cannot hold two interior-disjoint unit
                        squares at all (lower bound 1 exceeds the box diameter).
       DREQ[m1*16+m2] : minimum square-square hop distance forced by
                        |c_i-c_j| <= sqrt2 * d  (chain of contacts)."""
    BAD = np.zeros(256, dtype=bool)
    DREQ = np.zeros(256, dtype=np.uint8)
    for m1 in ALLOWED:
        for m2 in ALLOWED:
            lo, hi = _rect_range(_box(m1), _box(m2))
            lo = max(1.0, lo)          # two interior-disjoint unit squares: >= 1
            idx = m1 * 16 + m2
            if lo > hi + 1e-12:
                BAD[idx] = True
                DREQ[idx] = 250
            else:
                DREQ[idx] = int(math.ceil(lo / SQRT2 - 1e-12))
    return BAD, DREQ


BAD, DREQ = build_l5a_tables()
INF_D = 99


def ok_table(d):
    """256-entry boolean table: pair with hop distance d is L5a-consistent."""
    return (~BAD) & (DREQ <= min(d, 250))


OKTAB = {d: ok_table(d) for d in list(range(0, 20)) + [INF_D]}


# ---------------------------------------------------------------- graph reps (S_k)
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
            M[pi, idx[(a, b)]] = e     # bit e of g goes to bit idx[(a,b)] of p(g)
    return perms, M


def canon_and_aut(mask, k, perms, M, pw):
    """mask: int bitmask over edge slots. Returns (canonical mask, automorphism list)."""
    ne = M.shape[1]
    bits = ((mask >> np.arange(ne)) & 1).astype(np.int64)
    img = bits[M]                       # (nperm, ne): permuted bit vectors
    vals = img @ pw
    mn = int(vals.min())
    aut = [perms[t] for t in np.nonzero(vals == mask)[0]] if mn == mask else None
    return mn, aut


def graph_reps(k, cache={}):
    """All simple graphs on k unlabelled vertices, one canonical rep each, with Aut."""
    if k in cache:
        return cache[k]
    perms, M = _perm_edge_maps(k)
    ne = M.shape[1]
    pw = (1 << np.arange(ne)).astype(np.int64)
    if k <= 1:
        reps = [(0, [tuple(range(k))])]
        cache[k] = reps
        return reps
    prev = graph_reps(k - 1)
    idx = pair_index(k)
    seen = {}
    for pm, _ in prev:
        # embed the (k-1)-graph on vertices 0..k-2 (edge slots keep their meaning)
        base = 0
        pidx = pair_index(k - 1)
        for (i, j), e in pidx.items():
            if (pm >> e) & 1:
                base |= 1 << idx[(i, j)]
        for nb in range(1 << (k - 1)):
            g = base
            for i in range(k - 1):
                if (nb >> i) & 1:
                    g |= 1 << idx[(i, k - 1)]
            if g in seen:
                continue
            c, aut = canon_and_aut(g, k, perms, M, pw)
            if c not in seen:
                if aut is None:
                    _, aut = canon_and_aut(c, k, perms, M, pw)
                seen[c] = aut
    reps = sorted(seen.items())
    cache[k] = reps
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
    return adj, edges


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


def components(adj, k):
    seen = [False] * k
    comps = []
    for s in range(k):
        if seen[s]:
            continue
        stack, cur = [s], []
        seen[s] = True
        while stack:
            u = stack.pop()
            cur.append(u)
            m = adj[u]
            while m:
                b = m & -m
                v = b.bit_length() - 1
                m ^= b
                if not seen[v]:
                    seen[v] = True
                    stack.append(v)
        comps.append(sorted(cur))
    return comps


# ---------------------------------------------------------------- planarity
_planar_cache = {}


def is_planar(k, edges, wmasks, with_wall_cycle=True):
    key = (k, edges, tuple(wmasks), with_wall_cycle)
    v = _planar_cache.get(key)
    if v is not None:
        return v
    import networkx as nx
    G = nx.Graph()
    G.add_nodes_from(range(k + 4))
    G.add_edges_from(edges)
    for i, m in enumerate(wmasks):
        for b in range(4):
            if (m >> b) & 1:
                G.add_edge(i, k + b)
    if with_wall_cycle:
        for b in range(4):
            G.add_edge(k + b, k + (b + 1) % 4)
    v = nx.check_planarity(G, counterexample=False)[0]
    if len(_planar_cache) < 400000:
        _planar_cache[key] = v
    return v


def planar_graph(mask, k):
    import networkx as nx
    adj, edges = mask_to_adj(mask, k)
    G = nx.Graph()
    G.add_nodes_from(range(k))
    G.add_edges_from(edges)
    return nx.check_planarity(G, counterexample=False)[0]


# ---------------------------------------------------------------- Burnside rows
def burnside_rows(k):
    """Exact orbit counts under S_k x D4 for the two rows that are NOT restricted by
    L1 (so the per-A-rep enumeration cannot supply them):
        R0 : all simple graphs (squares + 4 walls, no wall-wall edges)
        R2 : + L5(b)  (wall mask of every square in ALLOWED)
    Uses Burnside; for g=(pi,delta) the square-square part and the square-wall part
    factor, and the wall part is a product over the cycles of pi."""
    perms, M = _perm_edge_maps(k)
    ne = M.shape[1]
    # number of orbits of pi on edge slots
    orb_counts = []
    for pi in range(len(perms)):
        row = M[pi]
        seen = [False] * ne
        c = 0
        for e in range(ne):
            if seen[e]:
                continue
            c += 1
            x = e
            while not seen[x]:
                seen[x] = True
                x = int(row[x])   # orbits of a permutation = orbits of its inverse
        orb_counts.append(c)
    # fixed masks of delta^l
    fixcnt = {}
    for di, p in enumerate(D4):
        for l in range(1, k + 1):
            t = np.arange(16, dtype=np.uint8)
            for _ in range(l):
                t = MT[di][t]
            fixcnt[(di, l, 'all')] = int(np.sum(t == np.arange(16)))
            fixcnt[(di, l, 'allowed')] = int(sum(1 for m in ALLOWED if t[m] == m))
    tot_all = 0
    tot_allowed = 0
    for pi, p in enumerate(perms):
        # cycle lengths of p
        seen = [False] * k
        cyc = []
        for s in range(k):
            if seen[s]:
                continue
            l = 0
            x = s
            while not seen[x]:
                seen[x] = True
                x = p[x]
                l += 1
            cyc.append(l)
        ss = 1 << orb_counts[pi]
        for di in range(8):
            wa = 1
            wb = 1
            for l in cyc:
                wa *= fixcnt[(di, l, 'all')]
                wb *= fixcnt[(di, l, 'allowed')]
            tot_all += ss * wa
            tot_allowed += ss * wb
    g = math.factorial(k) * 8
    assert tot_all % g == 0 and tot_allowed % g == 0
    return tot_all // g, tot_allowed // g
