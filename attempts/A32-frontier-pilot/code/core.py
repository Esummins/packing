"""A32 core: partial-structure node semantics, monotone kill cascade, canonical forms.

NODE.  A node is a PARTIAL structure with a target core size K:
    * k squares already introduced (0..k-1),
    * for the introduced squares every square-square pair and every square-wall
      contact is DECIDED (present / absent),
    * K - k squares are still to come, and every introduced square may still gain
      square-square edges to those future squares.
A node therefore represents ALL completions to a K-square loaded core.

SOUNDNESS SPLIT (docs/proofs/structure_lemmas.md ledger governs).
  MONOTONE kills  -- valid at any node because the constraint set only accumulates
  under extension.  Used here:
      M1 L5(b)  wall-degree <= 2 and the two walls adjacent   (ALLOWED is downward
                closed, so a partial wall mask outside it can never be repaired)
      M2 per-wall <= 3 (A31's certified tightening of L5(c); PROMOTED to hard per
                the A32 brief -- the along-wall spacing proof is in A31's report)
      M3 L5(d)  square-square degree <= 12
      M4 L4(a)  Euler |E| <= 3K + 2   (final |E| >= current |E|)
      M5 L5(a)  metric interval feasibility, STRENGTHENED (see metric.py)
      M6 L4(b)  planarity of the committed H + the wall 4-cycle
                (a subgraph of a planar graph is planar)
  EXTENSIBILITY prunes -- sound because NO completion inside the remaining budget
  can satisfy the structural requirement:
      X1 L1  a square of total degree d < 2 must gain 2-d edges, and it can only
             gain them from the K-k squares not yet introduced (all pairs among the
             introduced squares are already decided).  Kill if 2-d > available.
      X2 Euler budget: a future edge retires at most 2 units of deficiency, so
             final |E| >= |E| + ceil(sum_i deficiency_i / 2); kill if > 3K+2.
  STRUCTURAL checks -- NOT monotone, fired only when the node CLOSES (k == K):
      L1 (all degrees >= 2), L3 (no floating component; self-stress branch split),
      L6 (a component joins two opposite walls; lambda0=0 branch split), L7.

Every monotone kill is compatible with duplicate-free generation: if a node dies,
every superset dies, so no live leaf is lost by pruning it.
"""
import os
import sys
import math
import itertools

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_A31 = os.path.normpath(os.path.join(_HERE, '..', '..', 'A31-structure-count', 'code'))
if _A31 not in sys.path:
    sys.path.insert(0, _A31)
import lib0 as L                                              # noqa: E402

SQRT2 = L.SQRT2
ALLOWED = L.ALLOWED
ALLOWED_SET = L.ALLOWED_SET
POP = L.POP
# certified (A31): at most 3 squares touch any one wall.  A32_WALLCAP=11 disables
# the cap, which reproduces A31's MAIN column exactly (validation mode).
WALLCAP = int(os.environ.get('A32_WALLCAP', '3'))
KISS = 12              # L5(d)

STAGES = ['M1_wallmask', 'M2_wallcap3', 'M3_kiss', 'M4_euler', 'X1_L1ext',
          'X2_eulerbudget', 'M5_metric', 'M5b_triangle', 'M6_planar']

# ABLATION: A32_DISABLE=M6_planar,M5b_triangle turns individual stages off.
OFF = set(x for x in os.environ.get('A32_DISABLE', '').split(',') if x)


# ------------------------------------------------------------------ contexts
class Ctx:
    """Slot layout and group action for structures on k squares."""

    def __init__(self, k):
        self.k = k
        self.pidx = L.pair_index(k)
        self.nss = len(self.pidx)
        self.ns = self.nss + 4 * k
        self.slot_ss = [None] * self.ns
        for (i, j), e in self.pidx.items():
            self.slot_ss[e] = (i, j)
        perms = list(itertools.permutations(range(k)))
        ng = len(perms) * 8
        GM = np.empty((ng, self.ns), dtype=np.int64)
        t = 0
        for p in perms:
            for d in range(8):
                dp = L.D4[d]
                for (i, j), e in self.pidx.items():
                    a, b = p[i], p[j]
                    if a > b:
                        a, b = b, a
                    GM[t, e] = self.pidx[(a, b)]
                for i in range(k):
                    for b in range(4):
                        GM[t, self.nss + 4 * i + b] = self.nss + 4 * p[i] + dp[b]
                t += 1
        # PW[e] = the |G|-vector of 2**(image of slot e), one CONTIGUOUS row per
        # slot: canonicalising a d-slot set is then d in-place vector adds
        # (~7x faster than fancy-indexing the (|G|, ns) matrix).
        self.PW = np.ascontiguousarray((np.int64(1) << GM).T)
        self.ng = ng

    def canon(self, bitlist):
        """Canonical (minimum) encoding of the slot set `bitlist` under S_k x D4."""
        if not bitlist:
            return 0
        P = self.PW
        acc = P[bitlist[0]].copy()
        for b in bitlist[1:]:
            acc += P[b]
        return int(acc.min())


_CTX = {}


def ctx(k):
    c = _CTX.get(k)
    if c is None:
        c = _CTX[k] = Ctx(k)
    return c


def decode(k, mask):
    """(adj list of bitmasks, wall masks) from a canonical slot mask."""
    c = ctx(k)
    adj = [0] * k
    wm = [0] * k
    m = mask
    while m:
        b = m & -m
        e = b.bit_length() - 1
        m ^= b
        if e < c.nss:
            i, j = c.slot_ss[e]
            adj[i] |= 1 << j
            adj[j] |= 1 << i
        else:
            t = e - c.nss
            wm[t >> 2] |= 1 << (t & 3)
    return adj, wm


def encode(k, adj, wm):
    c = ctx(k)
    bits = []
    for (i, j), e in c.pidx.items():
        if (adj[i] >> j) & 1:
            bits.append(e)
    for i in range(k):
        for b in range(4):
            if (wm[i] >> b) & 1:
                bits.append(c.nss + 4 * i + b)
    return bits


# --------------------------------------------------------------- metric part
# Certified centre boxes per wall mask (lib0._box is sound for any container side
# in [S_LO, S_HI]).
BOX = [L._box(m) for m in range(16)]


def _boxdist(m1, m2):
    return L._rect_range(BOX[m1], BOX[m2])


_DLO = np.zeros((16, 16))
_DHI = np.zeros((16, 16))
for _a in range(16):
    for _b in range(16):
        _lo, _hi = _boxdist(_a, _b)
        _DLO[_a, _b] = max(1.0, _lo)
        _DHI[_a, _b] = _hi


def metric_l5a(k, adj, wm, D):
    """A31's L5(a) broad phase: box-distance range vs sqrt2 * hop distance.
    SOUND at a partial node: future edges can only DECREASE hop distance, so the
    bound used here is a relaxation of every completion's bound."""
    for i in range(k):
        wi = wm[i]
        for j in range(i + 1, k):
            if not L.OKTAB[D[i][j]][wi * 16 + wm[j]]:
                return False
    return True


_DLOL = [[_DLO[a, b] for b in range(16)] for a in range(16)]
_DHIL = [[_DHI[a, b] for b in range(16)] for a in range(16)]
BIG = 1e9


def metric_triangle(k, adj, wm, D):
    """STRENGTHENING of L5(a): close the interval distance system under the
    triangle inequality before testing lo > hi.

      U[i][j] = min( sqrt2 * hop(i,j) , box-diameter bound )   (upper)
      L[i][j] = max( 1 , box-separation bound )                (lower)
    then    U[i][j] <- min_m U[i][m] + U[m][j]      (path shortening)
            L[i][j] <- max_m L[i][m] - U[m][j]      (reverse triangle)
    Both are true metric facts about the centre points, so the test is sound; and
    every ingredient only tightens under extension, so it is monotone."""
    U = [[0.0] * k for _ in range(k)]
    Lo = [[0.0] * k for _ in range(k)]
    for i in range(k):
        Ui, Li, wi = U[i], Lo[i], wm[i]
        dhi, dlo = _DHIL[wi], _DLOL[wi]
        Di = D[i]
        for j in range(k):
            if i == j:
                continue
            d = Di[j]
            u = SQRT2 * d if d < 90 else BIG
            wj = wm[j]
            h = dhi[wj]
            Ui[j] = u if u < h else h
            Li[j] = dlo[wj]
    for m in range(k):                       # Floyd on the upper bounds
        Um = U[m]
        for i in range(k):
            Ui = U[i]
            uim = Ui[m]
            if uim >= BIG:
                continue
            for j in range(k):
                v = uim + Um[j]
                if v < Ui[j]:
                    Ui[j] = v
    for m in range(k):                       # reverse triangle on the lower bounds
        Um = U[m]
        for i in range(k):
            Li, Ui = Lo[i], U[i]
            lim = Li[m]
            for j in range(k):
                if i == j:
                    continue
                v = lim - Um[j]
                if v > Li[j]:
                    Li[j] = v
    for i in range(k):
        Li, Ui = Lo[i], U[i]
        for j in range(k):
            if i != j and Li[j] > Ui[j] + 1e-12:
                return False
    return True


# ------------------------------------------------------------- kill cascade
class Counters:
    def __init__(self):
        self.visited = 0
        self.killed = {s: 0 for s in STAGES}
        self.survived = 0
        self.time = {s: 0.0 for s in STAGES}


def wallcounts(k, wm):
    c = [0, 0, 0, 0]
    for i in range(k):
        m = wm[i]
        for b in range(4):
            if (m >> b) & 1:
                c[b] += 1
    return c


def monotone_kill(k, adj, wm, K, avail, cnt=None, planar=True, D=None,
                  triangle=True, force_planar=False):
    """Run the monotone + extensibility cascade on a node with k introduced
    squares (all their mutual slots decided except those listed in `avail`).

    avail[i] = number of further square-square edges square i may still gain.
    Returns None if the node survives, else the stage name that killed it."""
    if cnt is not None:
        cnt.visited += 1
    # M1 wall mask admissible (L5(b)); ALLOWED is downward closed
    for i in range(k):
        if wm[i] not in ALLOWED_SET:
            if cnt: cnt.killed['M1_wallmask'] += 1
            return 'M1_wallmask'
    # M2 per-wall cap 3
    wc = wallcounts(k, wm)
    if 'M2_wallcap3' not in OFF and max(wc) > WALLCAP:
        if cnt: cnt.killed['M2_wallcap3'] += 1
        return 'M2_wallcap3'
    deg = [bin(adj[i]).count('1') for i in range(k)]
    # M3 kissing
    if 'M3_kiss' not in OFF and max(deg) > KISS:
        if cnt: cnt.killed['M3_kiss'] += 1
        return 'M3_kiss'
    E = sum(deg) // 2 + sum(POP[m] for m in wm)
    # M4 Euler
    if 'M4_euler' not in OFF and E > 3 * K + 2:
        if cnt: cnt.killed['M4_euler'] += 1
        return 'M4_euler'
    # X1 L1 extensibility
    defs = 0
    x1off = 'X1_L1ext' in OFF
    for i in range(k):
        d = deg[i] + POP[wm[i]]
        if d < 2:
            need = 2 - d
            if need > avail[i] and not x1off:
                if cnt: cnt.killed['X1_L1ext'] += 1
                return 'X1_L1ext'
            defs += need
    # X2 Euler budget.  A future edge has at most TWO deficient endpoints (one
    # introduced square and one future square), so it can retire at most 2 units
    # of deficiency: final |E| >= |E| + ceil(sum_i deficiency_i / 2).
    if 'X2_eulerbudget' not in OFF and E + (defs + 1) // 2 > 3 * K + 2:
        if cnt: cnt.killed['X2_eulerbudget'] += 1
        return 'X2_eulerbudget'
    if D is None:
        D = L.hop_matrix(adj, k)
    # M5 metric broad phase
    if 'M5_metric' not in OFF and not metric_l5a(k, adj, wm, D):
        if cnt: cnt.killed['M5_metric'] += 1
        return 'M5_metric'
    # M5b triangle closure
    if triangle and 'M5b_triangle' not in OFF and not metric_triangle(k, adj, wm, D):
        if cnt: cnt.killed['M5b_triangle'] += 1
        return 'M5b_triangle'
    # M6 planarity.  The parent (squares 0..k-2 plus the wall cycle) was already
    # certified planar when it entered the frontier, and attaching a new vertex of
    # TOTAL degree <= 1 cannot destroy planarity, so that case is skipped.
    if planar and 'M6_planar' not in OFF and (force_planar or deg[k - 1] + POP[wm[k - 1]] >= 2):
        edges = []
        for i in range(k):
            for j in range(i + 1, k):
                if (adj[i] >> j) & 1:
                    edges.append((i, j))
        if not L.is_planar(k, tuple(edges), tuple(wm), True):
            if cnt: cnt.killed['M6_planar'] += 1
            return 'M6_planar'
    if cnt is not None:
        cnt.survived += 1
    return None


# --------------------------------------------------------- structural checks
def close_checks(k, adj, wm):
    """Non-monotone structural requirements, fired only when the node CLOSES.
    Returns a dict of booleans + the branch classification."""
    deg = [bin(adj[i]).count('1') for i in range(k)]
    tot = [deg[i] + POP[wm[i]] for i in range(k)]
    l1 = all(t >= 2 for t in tot)
    comps = L.components(adj, k)
    cw = []
    for vs in comps:
        m = 0
        for v in vs:
            m |= wm[v]
        cw.append(m)
    changed = True
    while changed:                     # join components that share a wall node
        changed = False
        for a in range(len(cw)):
            for b in range(a + 1, len(cw)):
                if cw[a] & cw[b] and cw[a] != cw[b]:
                    cw[a] = cw[b] = cw[a] | cw[b]
                    changed = True
    nofloat = all(c != 0 for c in cw)
    span = any((c & 5) == 5 or (c & 10) == 10 for c in cw)
    allw = 0
    for m in wm:
        allw |= m
    l7 = (allw & 5) == 5 or (allw & 10) == 10
    thin = any(t == 2 for t in tot)
    E = sum(deg) // 2 + sum(POP[m] for m in wm)
    return dict(L1=l1, L3_nofloat=nofloat, L6_span=span, L7=l7, thin=thin, E=E,
                main=(l1 and nofloat and span),
                selfstress=(l1 and not nofloat),
                lam0=(l1 and nofloat and not span))
