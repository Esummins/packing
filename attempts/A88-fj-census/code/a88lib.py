"""A88 T2 census core library.

Object: the SUPPORT structure H of a k0 FJ point on a loaded core of k_H squares
plus the 4 wall nodes (L,B,R,T in cycle order), counted up to S_k x D4.

LEVEL 0 = (simple graph on k squares, wall mask per square).
LEVEL 1 = + a DECORATION: per square-square edge one of the gauge-fixed 20 types
          (4 flush + 16 corner-on-edge), per square-wall edge one of 2
          (wall-flush / corner-on-wall); tilt-class system must be tilt-feasible.

Filters reused verbatim in logic from attempts/A31-structure-count/code/lib0.py
(Fact 0, L1, L3, L4, L5(a) broad phase, L5(b), L5(d), L6, L7) and A43's N1
(per-wall <= 3, EXACT).  The ONLY change vs A31 is the certified window:
      S_LO = 3.82 = 191/50   (A88 window; A31 used 3.80)
      S_HI = 3.877084        (Trump)

Nothing under attempts/A31, A43, A44, A57, A59, A60, A61, A85, A86, A87, certs/,
lean/ or docs/ is written or modified.
"""
import math
import itertools

import numpy as np
import networkx as nx

SQRT2 = math.sqrt(2.0)
HALF = SQRT2 / 2.0

# ---- the CERTIFIED WINDOW used by A88 (differs from A31's 3.80 lower end) ----
S_LO, S_HI = 3.82, 3.877084

# wall bits: 0=L 1=B 2=R 3=T  (cycle order L-B-R-T)
WALL_NAMES = ['L', 'B', 'R', 'T']
WALL_EXPR = ['x=0', 'y=0', 'x=s', 'y=s']
ALLOWED = [0, 1, 2, 4, 8, 3, 6, 12, 9]          # L5(b): wall-deg <= 2, adjacent
ALLOWED_SET = set(ALLOWED)
CORNER_MASKS = (3, 6, 12, 9)                    # LB, BR, RT, TL
POP = [bin(m).count("1") for m in range(16)]
NM = len(ALLOWED)                               # 9
MIDX = {m: i for i, m in enumerate(ALLOWED)}    # mask -> dense index
INF_D = 99


# ------------------------------------------------------------------ D4
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


MT = [_mask_tab(p) for p in D4]
# dense (9-index) version
MTD = np.zeros((8, NM), dtype=np.int64)
for _d in range(8):
    for _i, _m in enumerate(ALLOWED):
        MTD[_d, _i] = MIDX[int(MT[_d][_m])]


# --------------------------------------------------- certified centre boxes
def box(m):
    """Certified centre box of a square with wall mask m, sound for any container
    side in [S_LO, S_HI].  Half-width of a unit square in any direction in
    [1/2, sqrt2/2]."""
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


def rect_range(b1, b2):
    (x1, X1), (y1, Y1) = b1
    (x2, X2), (y2, Y2) = b2
    dxmin = max(0.0, max(x1 - X2, x2 - X1))
    dymin = max(0.0, max(y1 - Y2, y2 - Y1))
    dxmax = max(X1 - x2, X2 - x1)
    dymax = max(Y1 - y2, Y2 - y1)
    return math.hypot(dxmin, dymin), math.hypot(dxmax, dymax)


def build_tables():
    """COEX (N): the two boxes can hold two interior-disjoint unit squares
                 (max centre distance >= 1).
       TOUCH (T): the two boxes admit an active contact (min distance <= sqrt2).
       DREQ:      minimum hop distance forced by |c_i-c_j| <= sqrt2 * hops."""
    COEX = np.zeros((NM, NM), dtype=bool)
    TOUCH = np.zeros((NM, NM), dtype=bool)
    DREQ = np.zeros((NM, NM), dtype=np.int64)
    MIND = np.zeros((NM, NM))
    for i, a in enumerate(ALLOWED):
        for j, b in enumerate(ALLOWED):
            lo, hi = rect_range(box(a), box(b))
            lo = max(1.0, lo)          # two interior-disjoint unit squares: >= 1
            MIND[i, j] = lo
            if lo > hi + 1e-12:
                COEX[i, j] = False
                DREQ[i, j] = 250
            else:
                COEX[i, j] = True
                DREQ[i, j] = int(math.ceil(lo / SQRT2 - 1e-12))
            TOUCH[i, j] = COEX[i, j] and DREQ[i, j] <= 1
    return COEX, TOUCH, DREQ, MIND


COEX, TOUCH, DREQ, MIND = build_tables()
# pair weight of the FACTORABLE model: number of admissible edge statuses
W_PAIR = COEX.astype(np.int64) * (1 + TOUCH.astype(np.int64))    # 0,1,2
# 16-index versions (for filters that carry raw masks)
COEX16 = np.zeros((16, 16), dtype=bool)
DREQ16 = np.full((16, 16), 250, dtype=np.int64)
for i, a in enumerate(ALLOWED):
    for j, b in enumerate(ALLOWED):
        COEX16[a, b] = COEX[i, j]
        DREQ16[a, b] = DREQ[i, j]


def check_d4_equivariance():
    """COEX / TOUCH must be invariant under the D4 relabelling of masks, else the
    Burnside pair-orbit weights are not well defined."""
    bad = []
    for d in range(8):
        t = MTD[d]
        if not (COEX[np.ix_(t, t)] == COEX).all():
            bad.append(('COEX', d))
        if not (TOUCH[np.ix_(t, t)] == TOUCH).all():
            bad.append(('TOUCH', d))
        if not (DREQ[np.ix_(t, t)] == DREQ).all():
            bad.append(('DREQ', d))
    return bad


def check_structural_facts():
    """The two facts that make the labelled partition function a closed-form sum
    over mask COUNT vectors:
      (F-a) COEX(a,b) is false exactly when a == b is a corner mask;
      (F-b) TOUCH(a,b) is false exactly when a|b contains two OPPOSITE walls."""
    out = {'coex_ok': True, 'touch_ok': True, 'coex_fail_pairs': [],
           'touch_fail_pairs': []}
    for i, a in enumerate(ALLOWED):
        for j, b in enumerate(ALLOWED):
            want_coex = not (a == b and a in CORNER_MASKS)
            if bool(COEX[i, j]) != want_coex:
                out['coex_ok'] = False
                out['coex_fail_pairs'].append((a, b, bool(COEX[i, j])))
            ab = a | b
            want_touch = want_coex and not ((ab & 5) == 5 or (ab & 10) == 10)
            if bool(TOUCH[i, j]) != want_touch:
                out['touch_ok'] = False
                out['touch_fail_pairs'].append((a, b, bool(TOUCH[i, j])))
    return out


# ------------------------------------------------------------------ graphs
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


def adj_from_edges(k, edges):
    adj = [0] * k
    for i, j in edges:
        adj[i] |= 1 << j
        adj[j] |= 1 << i
    return adj


def is_planar_struct(k, edges, wm, with_wall_cycle=True):
    G = nx.Graph()
    G.add_nodes_from(range(k + 4))
    G.add_edges_from(edges)
    for i, m in enumerate(wm):
        for b in range(4):
            if (m >> b) & 1:
                G.add_edge(i, k + b)
    if with_wall_cycle:
        for b in range(4):
            G.add_edge(k + b, k + (b + 1) % 4)
    return nx.check_planarity(G, counterexample=False)[0]


# ------------------------------------------------------------ the F0 filter
F0_NAMES = ['L5b_masks', 'L1_deg2', 'L5d_deg12', 'L4a_euler', 'L5a_metric',
            'L3_nofloat', 'L6_span', 'L4b_planar', 'L7', 'N1_wallcap3']


def f0_flags(k, edges, wm, skip_planar=False, s_hi=None):
    """Returns a dict name -> bool for every Level-0 hard filter of F0.
    `s_hi` (optional) widens the metric window for the A87 certified-point audit."""
    adj = adj_from_edges(k, edges)
    deg = [bin(a).count('1') for a in adj]
    Esw = sum(POP[m] for m in wm)
    E = len(edges) + Esw
    r = {}
    r['L5b_masks'] = all(m in ALLOWED_SET for m in wm)
    r['L1_deg2'] = all(deg[i] + POP[wm[i]] >= 2 for i in range(k))
    r['L5d_deg12'] = max(deg) <= 12 if k else True
    r['L4a_euler'] = E <= 3 * k + 2
    D = hop_matrix(adj, k)
    ok = True
    if r['L5b_masks']:
        if s_hi is None:
            for i in range(k):
                for j in range(i + 1, k):
                    a, b = wm[i], wm[j]
                    if (not COEX16[a, b]) or DREQ16[a, b] > min(D[i][j], 250):
                        ok = False
        else:
            ok = _l5a_wide(k, wm, D, s_hi)
    else:
        ok = False
    r['L5a_metric'] = ok
    comps = components(adj, k)
    cw = []
    for vs in comps:
        m = 0
        for v in vs:
            m |= wm[v]
        cw.append(m)
    changed = True
    while changed:
        changed = False
        for a in range(len(cw)):
            for b in range(a + 1, len(cw)):
                if cw[a] & cw[b] and cw[a] != cw[b]:
                    cw[a] = cw[b] = cw[a] | cw[b]
                    changed = True
    r['L3_nofloat'] = all(c != 0 for c in cw)
    r['L6_span'] = any((c & 5) == 5 or (c & 10) == 10 for c in cw)
    allw = 0
    for m in wm:
        allw |= m
    r['L7'] = ((allw & 5) == 5) or ((allw & 10) == 10)
    r['N1_wallcap3'] = all(sum(1 for m in wm if (m >> b) & 1) <= 3
                           for b in range(4))
    r['L4b_planar'] = True if skip_planar else is_planar_struct(k, edges, wm)
    return r


def _l5a_wide(k, wm, D, s_hi):
    """L5(a) with the container window widened to [S_LO, s_hi] (A87 audit only)."""
    def bx(m):
        if m & 1:
            x = (0.5, HALF)
        elif m & 4:
            x = (S_LO - HALF, s_hi - 0.5)
        else:
            x = (0.5, s_hi - 0.5)
        if m & 2:
            y = (0.5, HALF)
        elif m & 8:
            y = (S_LO - HALF, s_hi - 0.5)
        else:
            y = (0.5, s_hi - 0.5)
        return x, y
    for i in range(k):
        for j in range(i + 1, k):
            lo, hi = rect_range(bx(wm[i]), bx(wm[j]))
            lo = max(1.0, lo)
            if lo > hi + 1e-12:
                return False
            if math.ceil(lo / SQRT2 - 1e-12) > min(D[i][j], 250):
                return False
    return True


def f0_pass(k, edges, wm):
    f = f0_flags(k, edges, wm)
    return all(f.values()), f


# ================================================================= LEVEL 1
# Gauge (A31 code/level1.py docstring, reproduced):
#   phi_i = theta_i mod 90 in [0,90) fixes each square's corner/edge labels.
#   flush(i,j)      : 4 types  = which edge e of the OWNER (we take the larger
#                     index as owner); the partner's edge is e+2 (mod 4).
#   corner-on-edge  : 8 types  = (owner in {i,j}) x (edge e of the owner);
#                     the touching corner of the partner is then forced by the
#                     sign of the class inequality:
#                        (e - c) mod 4 = 3 if phi_partner > phi_owner
#                        (e - c) mod 4 = 2 if phi_partner < phi_owner
#                     -> 8 x 2 signs = 16 gauge-fixed types.
#   square-wall     : wall-flush (pins phi = 0) or corner-on-wall (phi != 0) = 2.
# t3lib conventions (attempts/A30-t3-pilot/t3lib.py):
#   HALF[k] = corner offsets [(-.5,-.5),(.5,-.5),(.5,.5),(-.5,.5)]
#   NHAT[e] = outward normal of edge e: [(0,-1),(1,0),(0,1),(-1,0)]
#   => edge e joins corners e and (e+1) mod 4.
# Wall dictionary in the gauge (phi in [0,90)):
#   wall bit b -> touching EDGE (b+3) mod 4, touching CORNER (b+3) mod 4.
WALL_EDGE = [(b + 3) % 4 for b in range(4)]      # L->3, B->0, R->1, T->2
WALL_CORNER = [(b + 3) % 4 for b in range(4)]    # same index


def acyclic_orientations(n, edges, _cache={}):
    if n == 0:
        return 1
    key = (n, tuple(sorted(edges)))
    v = _cache.get(key)
    if v is not None:
        return v
    adj = [0] * n
    for a, b in edges:
        adj[a] |= 1 << b
        adj[b] |= 1 << a
    full = (1 << n) - 1
    memo = {0: 1}

    def a(S):
        if S in memo:
            return memo[S]
        tot = 0
        sub = S
        while True:
            if sub:
                ok = True
                t = sub
                while t:
                    b = t & -t
                    i = b.bit_length() - 1
                    t ^= b
                    if adj[i] & sub:
                        ok = False
                        break
                if ok:
                    sgn = -1 if (bin(sub).count('1') % 2 == 0) else 1
                    tot += sgn * a(S & ~sub)
            if sub == 0:
                break
            sub = (sub - 1) & S
        memo[S] = tot
        return tot

    v = a(full)
    _cache[key] = v
    return v


class Decoration:
    """A Level-1 decoration of a Level-0 structure.

    ss_type[e] for the e-th square-square edge (i,j), i<j:
        ('F', eo)          flush, eo = edge of the owner (= j) touched
        ('C', owner, eo)   corner-on-edge: corner of the partner on edge eo of owner
    sw_type[(i,b)] in {'WF','CW'}                     wall-flush / corner-on-wall
    """

    def __init__(self, k, ss_edges, wm, ss_type, sw_type):
        self.k = k
        self.ss_edges = list(ss_edges)
        self.wm = list(wm)
        self.ss_type = list(ss_type)
        self.sw_type = dict(sw_type)
        self.wedges = [(i, b) for i in range(k) for b in range(4)
                       if (wm[i] >> b) & 1]

    # ------------------------------------------------------- tilt system
    def tilt_system(self):
        """Union-find on flush ties + wall-flush pinning; then the strict digraph.
        Returns dict(feasible, cls (per-square class id), zero_class (or None),
        strict (list of (lower, upper) class pairs))."""
        k = self.k
        parent = list(range(k))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        for e, (i, j) in enumerate(self.ss_edges):
            if self.ss_type[e][0] == 'F':
                a, b = find(i), find(j)
                if a != b:
                    parent[a] = b
        pinned = set()
        corner_wall = set()
        for (i, b) in self.wedges:
            if self.sw_type[(i, b)] == 'WF':
                pinned.add(find(i))
            else:
                corner_wall.add(find(i))
        if pinned & corner_wall:
            return dict(feasible=False, reason='wall-flush and corner-on-wall in '
                        'one class')
        roots = sorted(set(find(i) for i in range(k)))
        # merge all pinned roots into a single zero class
        cid = {}
        nxt = 0
        zpos = None
        if pinned:
            for r in roots:
                if r in pinned:
                    continue
                cid[r] = nxt
                nxt += 1
            zpos = nxt
            for r in pinned:
                cid[r] = zpos
            ncls = nxt + 1
        else:
            for r in roots:
                cid[r] = nxt
                nxt += 1
            ncls = nxt
        cls = [cid[find(i)] for i in range(k)]
        strict = []
        for e, (i, j) in enumerate(self.ss_edges):
            t = self.ss_type[e]
            if t[0] == 'F':
                continue
            owner = t[1]
            partner = j if owner == i else i
            u, v = cls[owner], cls[partner]
            if u == v:
                return dict(feasible=False, reason='strict edge inside a class')
            # direction: t[3] is the sign flag, True <=> phi_partner > phi_owner
            if t[3]:
                strict.append((u, v))        # owner class < partner class
            else:
                strict.append((v, u))
        # acyclicity (Kahn) + zero class has in-degree 0
        succ = [[] for _ in range(ncls)]
        indeg = [0] * ncls
        for u, v in set(strict):
            succ[u].append(v)
            indeg[v] += 1
        if zpos is not None and indeg[zpos] > 0:
            return dict(feasible=False, reason='class below the zero class')
        stack = [u for u in range(ncls) if indeg[u] == 0]
        seen = 0
        while stack:
            u = stack.pop()
            seen += 1
            for v in succ[u]:
                indeg[v] -= 1
                if indeg[v] == 0:
                    stack.append(v)
        if seen != ncls:
            return dict(feasible=False, reason='cyclic strict digraph')
        return dict(feasible=True, cls=cls, ncls=ncls, zero_class=zpos,
                    strict=sorted(set(strict)))

    # ------------------------------------------------------ K0-1 / K0-3
    def k0_1(self):
        """slot exclusion: no square carries TWO wall-flush contacts."""
        for i in range(self.k):
            nwf = sum(1 for b in range(4) if (self.wm[i] >> b) & 1
                      and self.sw_type[(i, b)] == 'WF')
            if nwf >= 2:
                return False
        return True

    def slot_squares(self):
        out = []
        for i in range(self.k):
            nwf = sum(1 for b in range(4) if (self.wm[i] >> b) & 1
                      and self.sw_type[(i, b)] == 'WF')
            if nwf >= 2:
                out.append(i)
        return out

    def k0_3(self, ts=None, s_hi=None):
        """A45 Lemma R (flush-ruler cap) in its exact per-axis component form.

        Squares joined by a flush contact share a tilt class phi.  A flush link
        with owner edge e pins ONE class-frame coordinate exactly and leaves the
        transverse offset free:
            e in {1,3} (normal +-u):  u_partner - u_owner = +-1, v free in (-1,1)
            e in {0,2} (normal +-v):  v_partner - v_owner = +-1, u free
        So each normal family a in {u, v} carries its own graph G_a of pinned
        links; on each connected component of G_a the coordinate is determined up
        to translation with INTEGER differences.  Two exact kills:
          (M2) a cycle of G_a whose +-1 sum does not close  -> infeasible;
          (R)  extent = max - min over a component obeys Lemma R
                    extent <= s(|cos psi| + |sin psi|) - 1
               = 2 for the zero class (|cos|+|sin| = 1, so rulers of >= 4 upright
                 squares die) and 4 otherwise (rulers of >= 6 squares die).
        Returns (ok, info)."""
        if ts is None:
            ts = self.tilt_system()
        if not ts['feasible']:
            return False, dict(reason='tilt-infeasible')
        k = self.k
        sh = S_HI if s_hi is None else s_hi
        # Lemma R's cap is WINDOW-DEPENDENT: extent <= s(|cos psi|+|sin psi|) - 1
        cap_zero = int(math.floor(sh * 1.0 - 1.0 + 1e-12))          # = 2 at S_HI
        cap_free = int(math.floor(sh * SQRT2 - 1.0 + 1e-12))        # = 4 at S_HI
        NH = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        worst = 0
        for ax in (0, 1):                       # 0 = u (e in {1,3}), 1 = v
            parent = list(range(k))
            pot = [0] * k

            def find(x):
                path = []
                while parent[x] != x:
                    path.append(x)
                    x = parent[x]
                for y in reversed(path):
                    pot[y] += pot[parent[y]]
                    parent[y] = x
                return x

            for e, (i, j) in enumerate(self.ss_edges):
                t = self.ss_type[e]
                if t[0] != 'F':
                    continue
                eo = t[1]
                if (eo % 2) != (1 - ax):        # e in {1,3} pins u, {0,2} pins v
                    continue
                d = NH[eo][0] if ax == 0 else NH[eo][1]
                owner, partner = j, i           # owner = larger index (gauge)
                ro, rp = find(owner), find(partner)
                if ro == rp:
                    if pot[partner] - pot[owner] != d:
                        return False, dict(
                            reason='flush cycle inconsistent (Lemma R / M2)',
                            axis=ax, edge=[i, j])
                else:
                    shift = pot[owner] + d - pot[partner]
                    parent[rp] = ro
                    pot[rp] += shift
            comps = {}
            for i in range(k):
                comps.setdefault(find(i), []).append(i)
            for r, vs in comps.items():
                if len(vs) < 2:
                    continue
                zero = (ts['zero_class'] is not None
                        and ts['cls'][vs[0]] == ts['zero_class'])
                cap = cap_zero if zero else cap_free
                us = [pot[v] for v in vs]
                ext = max(us) - min(us)
                worst = max(worst, ext)
                if ext > cap:
                    return False, dict(reason='ruler too long', extent=ext,
                                       cap=cap, zero=zero, axis=ax,
                                       component=sorted(vs))
        return True, dict(max_extent=worst)

    # ------------------------------------------------------ t3lib rows
    def rows(self, ts=None):
        """Row set in the A30 t3lib vocabulary (see notes/sample_format.md)."""
        if ts is None:
            ts = self.tilt_system()
        out = []
        for (i, b) in self.wedges:
            if self.sw_type[(i, b)] == 'WF':
                e = WALL_EDGE[b]
                out.append({'kind': 'wall', 'i': i, 'corner': e,
                            'wall': WALL_EXPR[b]})
                out.append({'kind': 'wall', 'i': i, 'corner': (e + 1) % 4,
                            'wall': WALL_EXPR[b]})
            else:
                out.append({'kind': 'wall', 'i': i, 'corner': WALL_CORNER[b],
                            'wall': WALL_EXPR[b]})
        for e, (i, j) in enumerate(self.ss_edges):
            t = self.ss_type[e]
            if t[0] == 'F':
                eo = t[1]
                o, p = j, i                      # owner = larger index
                ks = (eo + 2) % 4                # partner's touching edge = eo+2
                out.append({'kind': 'sep', 'o': o, 'e': eo, 'p': p,
                            'kstar': ks})
                out.append({'kind': 'sep', 'o': o, 'e': eo, 'p': p,
                            'kstar': (ks + 1) % 4})
            else:
                _, owner, eo, hi = t
                p = j if owner == i else i
                # (e - c) mod 4 = 3 if phi_p > phi_o else 2
                c = (eo - 3) % 4 if hi else (eo - 2) % 4
                out.append({'kind': 'sep', 'o': owner, 'e': eo, 'p': p,
                            'kstar': c})
        return out

    def counts(self):
        Ess = len(self.ss_edges)
        Esw = len(self.wedges)
        nf = sum(1 for t in self.ss_type if t[0] == 'F')
        nwf = sum(1 for v in self.sw_type.values() if v == 'WF')
        E = Ess + Esw
        F = nf + nwf
        m = E + F
        return dict(Ess=Ess, Esw=Esw, E=E, F=F, m=m, nf=nf, nwf=nwf,
                    chi=m - (3 * self.k + 1))


def random_decoration(k, ss_edges, wm, rng):
    """Uniform draw from the RAW gauge-fixed menu 20^Ess * 2^Esw."""
    ss = []
    for _ in ss_edges:
        t = int(rng.integers(0, 20))
        if t < 4:
            ss.append(('F', t))
        else:
            t -= 4                       # 0..15 = owner(2) x edge(4) x sign(2)
            owner_bit = t & 1
            eo = (t >> 1) & 3
            hi = bool((t >> 3) & 1)
            ss.append(('C', owner_bit, eo, hi))
    # resolve owner_bit -> actual vertex
    ss2 = []
    for q, (i, j) in enumerate(ss_edges):
        t = ss[q]
        if t[0] == 'F':
            ss2.append(t)
        else:
            ss2.append(('C', j if t[1] else i, t[2], t[3]))
    sw = {}
    for i in range(k):
        for b in range(4):
            if (wm[i] >> b) & 1:
                sw[(i, b)] = 'WF' if rng.integers(0, 2) else 'CW'
    return Decoration(k, ss_edges, wm, ss2, sw)


# --------------------------------------------------------- K0-2 crowding
ZBOX = (0.5, 1.0 + HALF)          # centre coordinate range in the corner frame


def zone_box(c):
    """Centre box of a square meeting corner box c (0=LB,1=BR,2=RT,3=TL)."""
    lo, hi = ZBOX
    xs = (lo, hi) if c in (0, 3) else (S_LO - hi, S_HI - lo)
    ys = (lo, hi) if c in (0, 1) else (S_LO - hi, S_HI - lo)
    return xs, ys


ZONE_WALLS = [3, 6, 12, 9]        # zone c may only carry walls of corner c


def _isect(b1, b2):
    (x1, X1), (y1, Y1) = b1
    (x2, X2), (y2, Y2) = b2
    x, X = max(x1, x2), min(X1, X2)
    y, Y = max(y1, y2), min(Y1, Y2)
    if x > X or y > Y:
        return None
    return (x, X), (y, Y)


def k0_2(k, edges, wm, general=False, slots=()):
    """A58 crowding as an EXISTENTIAL zone-assignment CSP.

    Does there exist an assignment of squares to the 4 corner zones, >= 2 per
    zone, consistent with each square's wall mask and with the zone-shrunk
    centre boxes (coexistence on all pairs, touching window on edges)?
    `general=True` (A58-general): a corner holding a SLOT square counts filled.
    """
    need = [2, 2, 2, 2]
    if general:
        for i in slots:
            m = wm[i]
            for c in range(4):
                if m == ZONE_WALLS[c]:
                    need[c] = 0
    if all(n == 0 for n in need):
        return True, dict(assign=None, note='all corners hold slot squares')
    boxes = {}
    cand = [[] for _ in range(4)]
    for i in range(k):
        for c in range(4):
            if need[c] == 0:
                continue
            if wm[i] & ~ZONE_WALLS[c]:
                continue                     # zone-c square cannot carry other walls
            bb = _isect(box(wm[i]), zone_box(c))
            if bb is None:
                continue
            boxes[(i, c)] = bb
            cand[c].append(i)
    for c in range(4):
        if len(cand[c]) < need[c]:
            return False, dict(reason='zone %d has %d candidates < %d'
                               % (c, len(cand[c]), need[c]))
    eset = set((min(a, b), max(a, b)) for a, b in edges)

    def compat(i, ci, j, cj):
        bi = boxes[(i, ci)] if ci is not None else box(wm[i])
        bj = boxes[(j, cj)] if cj is not None else box(wm[j])
        lo, hi = rect_range(bi, bj)
        lo = max(1.0, lo)
        if lo > hi + 1e-12:
            return False
        if (min(i, j), max(i, j)) in eset and lo > SQRT2 + 1e-12:
            return False
        return True

    order = [c for c in range(4) if need[c]]
    assign = {}

    def rec(t, used):
        if t == len(order):
            return True
        c = order[t]
        pool = [i for i in cand[c] if i not in used]
        for combo in itertools.combinations(pool, need[c]):
            ok = True
            for a in range(len(combo)):
                for b in range(a + 1, len(combo)):
                    if not compat(combo[a], c, combo[b], c):
                        ok = False
                        break
                if not ok:
                    break
            if not ok:
                continue
            for i in combo:
                for j, cj in assign.items():
                    if not compat(i, c, j, cj):
                        ok = False
                        break
                if not ok:
                    break
            if not ok:
                continue
            # zone squares vs unassigned squares: their (possibly unshrunk) boxes
            # are already covered by the Level-0 L5(a) test, so nothing more here.
            for i in combo:
                assign[i] = c
            if rec(t + 1, used | set(combo)):
                return True
            for i in combo:
                del assign[i]
        return False

    ok = rec(0, set())
    return ok, dict(assign=dict(assign) if ok else None, need=need)
