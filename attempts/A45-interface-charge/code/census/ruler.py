"""A45-B  RULER filter  [EXACT]  -- Lemma R (flush-ruler cap) + Lemma Q (quantization kill),
notes/charging_lemma.md Sec 6.3, applied to a census DECORATION.

OBJECT.  A decoration fixes, for every square-square contact, whether it is FLUSH (FL) or a
corner type, and for every square-wall contact, whether it is WALL-FLUSH (WF) or wall-corner
(WC).  It does NOT fix the realization data that Lemma R quantizes: per FL link the shared edge
normal psi (4 choices = 2 normal FAMILIES x 2 SIGNS -- exactly A31's factor 4 per flush edge)
and the slide t in [-1,1].  This module decides, per FLUSH COMPONENT (connected component of the
FL-edge graph, one merged tilt class by Sec 6.2), whether ANY (family, sign, slide) assignment is
consistent with the certified interval constraints.

CONSTRAINTS IMPLEMENTED (exactly the ones stated in Sec 6.3; nothing stronger)
  per FL link (a,b), family f in {u, v}, sign sg in {+1,-1}:
      proj_f(c_b) - proj_f(c_a) = sg          (Lemma R: support along an edge normal is
                                               exactly 1/2 for BOTH squares)
      proj_g(c_b) - proj_g(c_a) in [-1, 1]    (g = the other family; the slide)
  extent, both families:  max proj - min proj <= s0*(cos phi + sin phi) - 1
  zero-pinned components (component carries a WF contact => phi = 0 exactly, Sec 6.2):
      u = x-axis, v = y-axis, and containment is ABSOLUTE:
          proj in [1/2, s - 1/2],  s in [19/5, s0]      (s is a shared unknown: one extra node)
      WF on the left/bottom wall pins that coordinate to exactly 1/2;
      WF on the right/top wall pins it to exactly s - 1/2   (Lemma Q's anchors).
  s ranges over [3.80, s0]: caps use the WEAKEST value s0, the wall anchors use the interval
  (this is the census form of Lemma Q -- there is no integer s in the range, and the filter
  finds that fact by itself through the difference-constraint system).

SOUNDNESS.  Everything is a system of DIFFERENCE CONSTRAINTS over the exact rationals (scaled to
integers over the common denominator 500000; the only rounding is on s0*(cos+sin), rounded UP,
which only WEAKENS the extent cap).  Feasibility is decided exactly by negative-cycle detection.
A decoration is KILLED only when EVERY (family, sign) assignment is infeasible, so the filter is
one-sided: it over-accepts, never over-kills.  Documented over-acceptances:
  (OA1) slides are relaxed to their interval hull (the true slide is determined by the geometry);
  (OA2) no interior-disjointness between squares of a component is imposed (Sec 6.3 does not
        license it and the brief forbids going beyond);
  (OA3) tilt windows: a non-zero-pinned component uses cos+sin <= sqrt2 (the widest window the
        H1 decoration carries), so its extent cap is the weakest possible;
  (OA4) components with more than CAP_M FL links are not enumerated; the kill test falls back to
        the PATH RELAXATION (a sub-system of the full system, hence infeasibility still implies
        infeasibility) and the assignment count falls back to the full 4^m.
"""
from fractions import Fraction as F
import itertools, math

DEN = 500000                       # common denominator; all quantities are ints of 1/DEN
ONE = DEN                          # 1
HALF = DEN // 2                    # 1/2
S0_N = 1938542                     # s0 = 969271/250000 = 3.877084
S_LO_N = 1900000                   # 3.80 (certified lower bound on s(11))
SQRT2_UP = F(707107, 500000)       # > sqrt2, outward
CAP_M = 12                         # max FL links per component for exact enumeration

assert F(S0_N, DEN) == F(969271, 250000)
assert SQRT2_UP ** 2 > 2


def extent_cap(cs_max):
    """L = s0*(cos+sin) - 1 in 1/DEN units, rounded UP (weaker constraint => sound)."""
    v = F(S0_N) * F(cs_max)
    return -(-v.numerator // v.denominator) - ONE


L_ZERO = extent_cap(1)             # 1438542  = 2.877084 = s0 - 1
L_FREE = extent_cap(SQRT2_UP)      # phi unknown in (0,90): weakest cap


# ------------------------------------------------------------------ difference-constraint core
def feasible(nv, cons):
    """cons: list of (a, b, w) meaning  x_b - x_a <= w   (ints).  Feasible iff no neg cycle.
    Bellman-Ford from a virtual source connected to every node with weight 0."""
    d = [0] * nv
    for _ in range(nv):
        changed = False
        for a, b, w in cons:
            nd = d[a] + w
            if nd < d[b]:
                d[b] = nd
                changed = True
        if not changed:
            return True
    for a, b, w in cons:
        if d[a] + w < d[b]:
            return False
    return True


def _axis_cons(n, links, fams, sgs, axis, pins, zero, L):
    """Constraints for ONE projection axis of one flush component.
    links: list of (a,b) local indices; fams[i] in {0,1} (0 = this axis is the link's normal
    family); sgs[i] in {+1,-1}; axis is only used for pin selection by the caller.
    Nodes: 0..n-1 = the projections; n = Z (origin), n+1 = S (container side)."""
    nv = n + 2 if zero else n
    Z, S = n, n + 1
    cons = []
    for t, (a, b) in enumerate(links):
        if fams[t] == 0:                      # normal along this axis: exact +-1
            w = sgs[t] * ONE
            cons.append((a, b, w))            # x_b - x_a <= w
            cons.append((b, a, -w))           # x_b - x_a >= w
        else:                                 # the slide: free in [-1, 1]
            cons.append((a, b, ONE))
            cons.append((b, a, ONE))
    if zero:
        cons.append((Z, S, S0_N))             # S - Z <= s0
        cons.append((S, Z, -S_LO_N))          # S - Z >= 3.80
        for i in range(n):
            cons.append((i, Z, -HALF))        # Z - x_i <= -1/2   (x_i >= 1/2)
            cons.append((S, i, -HALF))        # x_i - S <= -1/2   (x_i <= S - 1/2)
        for i, kind in pins:
            if kind == 'LO':                  # x_i = 1/2
                cons.append((Z, i, HALF))
                cons.append((i, Z, -HALF))
            else:                             # x_i = S - 1/2
                cons.append((i, S, HALF))
                cons.append((S, i, -HALF))
    else:
        for i in range(n):                    # extent: max - min <= L
            for j in range(n):
                if i != j:
                    cons.append((i, j, L))
    return nv, cons


_sign_cache = {}


def _count_signs(n, links, fams, axis_family, pins, zero, L):
    """Number of sign assignments (on the links whose normal family IS this axis) for which the
    axis system is feasible.  Memoized on the exact system signature."""
    idx = [t for t in range(len(links)) if fams[t] == axis_family]
    key = (n, tuple(links), tuple(fams), axis_family, tuple(sorted(pins)), zero, L)
    v = _sign_cache.get(key)
    if v is not None:
        return v
    tot = 0
    fam_flag = [0 if fams[t] == axis_family else 1 for t in range(len(links))]
    for bits in range(1 << len(idx)):
        sgs = [0] * len(links)
        for r, t in enumerate(idx):
            sgs[t] = 1 if (bits >> r) & 1 else -1
        nv, cons = _axis_cons(n, links, fam_flag, sgs, axis_family, pins, zero, L)
        if feasible(nv, cons):
            tot += 1
    _sign_cache[key] = tot
    return tot


def component_count(n, links, pinsU, pinsV, zero, cs_max=None):
    """Number of FEASIBLE (family, sign) assignments of the component's FL links, out of 4^m.
    Returns (count, exact_flag).  count == 0  <=>  the component is DEAD (kill).
    exact_flag False means the enumeration cap was hit and count = 4^m was returned unrefined."""
    m = len(links)
    L = L_ZERO if zero else (extent_cap(cs_max) if cs_max is not None else L_FREE)
    if m == 0:
        # a lone square: only the pins can conflict, and a wall mask never holds two opposite
        # walls (L5(b)); still check, it is free.
        nvU, cU = _axis_cons(n, [], [], [], 0, pinsU, zero, L)
        nvV, cV = _axis_cons(n, [], [], [], 1, pinsV, zero, L)
        return (1 if (feasible(nvU, cU) and feasible(nvV, cV)) else 0), True
    if m > CAP_M:
        return 4 ** m, False
    tot = 0
    for fb in range(1 << m):
        fams = [(fb >> t) & 1 for t in range(m)]
        cu = _count_signs(n, links, fams, 0, pinsU, zero, L)
        if cu == 0:
            continue
        cv = _count_signs(n, links, fams, 1, pinsV, zero, L)
        tot += cu * cv
    return tot, True


# ------------------------------------------------------------------ path relaxation (fallback)
def _dist(n, links, src):
    D = [None] * n
    D[src] = 0
    adj = [[] for _ in range(n)]
    for a, b in links:
        adj[a].append(b)
        adj[b].append(a)
    fr = [src]
    d = 0
    while fr:
        d += 1
        nx = []
        for u in fr:
            for v in adj[u]:
                if D[v] is None:
                    D[v] = d
                    nx.append(v)
        fr = nx
    return D


def path_relaxation_kill(n, links, pins):
    """Lemma-Q path form, valid for any component size: if a LO pin and a HI pin of the SAME
    family sit at FL-graph distance m, then that axis's difference must equal s - 1 in
    [2.80, 2.877084], while the path can realize at most |m| (each link contributes at most 1 to
    that projection).  m <= 2 is therefore infeasible.  Sub-system of the full system => sound."""
    lo = [i for i, t in pins if t == 'LO']
    hi = [i for i, t in pins if t == 'HI']
    for a in lo:
        D = _dist(n, links, a)
        for b in hi:
            if D[b] is not None and D[b] <= 2:
                return True
    return False


# ------------------------------------------------------------------ decoration-level driver
_comp_cache = {}
KILLED = {}   # audit: component signatures that the CSP proved dead, with hit counts
WALL_FAMILY = {0: 0, 2: 0, 1: 1, 3: 1}          # L,R -> u(x);  B,T -> v(y)
WALL_KIND = {0: 'LO', 1: 'LO', 2: 'HI', 3: 'HI'}


def analyse(k, fl_edges, wf_edges, cs_max=None):
    """fl_edges: list of (i,j) square-square FLUSH contacts.
       wf_edges: list of (i,b) square-wall FLUSH (WF) contacts, b in 0=L 1=B 2=R 3=T.
    Returns dict with:
       kill        True iff some flush component admits NO (family,sign) assignment
       gauge_full  4^(#FL edges)                      -- A31's flush gauge multiplicity
       gauge_ok    number of feasible assignments     -- the REFINED (still exact) multiplicity
       exact       False if any component hit the enumeration cap (gauge_ok then over-counts)
       n_comp_zero number of zero-pinned flush components
       capped      number of components that hit the cap
    """
    par = list(range(k))

    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x
    for i, j in fl_edges:
        a, b = find(i), find(j)
        if a != b:
            par[a] = b
    comps = {}
    for i in range(k):
        comps.setdefault(find(i), []).append(i)
    pin = {}
    zeroc = set()
    for i, b in wf_edges:
        pin.setdefault(i, []).append(b)
        zeroc.add(find(i))
    kill = False
    gfull = 1
    gok = 1
    exact = True
    capped = 0
    for root, vs in comps.items():
        loc = {v: t for t, v in enumerate(vs)}
        links = [(loc[i], loc[j]) for i, j in fl_edges if find(i) == root]
        if not links and not any(v in pin for v in vs):
            continue                                    # bare square, nothing to say
        pu = [(loc[v], WALL_KIND[b]) for v in vs for b in pin.get(v, []) if WALL_FAMILY[b] == 0]
        pv = [(loc[v], WALL_KIND[b]) for v in vs for b in pin.get(v, []) if WALL_FAMILY[b] == 1]
        zero = root in zeroc
        key = (len(vs), tuple(sorted(links)), tuple(sorted(pu)), tuple(sorted(pv)), zero,
               cs_max if cs_max is not None else 'free')
        got = _comp_cache.get(key)
        if got is None:
            if len(links) > CAP_M:
                kl = path_relaxation_kill(len(vs), links, pu) or \
                     path_relaxation_kill(len(vs), links, pv)
                got = (0 if kl else 4 ** len(links), False)
            else:
                got = component_count(len(vs), links, pu, pv, zero, cs_max)
            _comp_cache[key] = got
        cnt, ex = got
        if cnt == 0:
            KILLED[key] = KILLED.get(key, 0) + 1
        gfull *= 4 ** len(links)
        gok *= cnt
        if not ex:
            exact = False
            capped += 1
        if cnt == 0:
            kill = True
    return dict(kill=kill, gauge_full=gfull, gauge_ok=gok, exact=exact,
                n_comp_zero=len(zeroc), capped=capped)


def self_test():
    """Lemma R / Lemma Q sanity, plus the Trump 5-strip margin."""
    out = {}
    # (1) Lemma R at phi = 0: a 4-square upright ruler is dead, a 3-square one is not.
    #     Modelled as a path of FL links in a zero-pinned component (one WF anchor).
    for nsq in (3, 4, 5):
        links = [(t, t + 1) for t in range(nsq - 1)]
        c, ex = component_count(nsq, links, [(0, 'LO')], [], True)
        # count the assignments that are pure "same family, same sign" rulers
        out['zero_chain_%d_feasible_assignments' % nsq] = c
        out['zero_chain_%d_of' % nsq] = 4 ** (nsq - 1)
    # (2) Lemma Q: opposite-wall WF anchors at FL distance 1, 2, 3.
    for m in (1, 2, 3):
        links = [(t, t + 1) for t in range(m)]
        c, ex = component_count(m + 1, links, [(0, 'LO'), (m, 'HI')], [], True)
        out['opposite_anchor_dist_%d_feasible' % m] = c
    # (3) Lemma R cap arithmetic at s0.
    out['L_zero_exact'] = str(F(L_ZERO, DEN))
    out['L_free_exact'] = str(F(L_FREE, DEN))
    out['ruler_cap_k_at_phi0'] = math.floor(F(S0_N, DEN))
    cs = math.cos(math.radians(40.18)) + math.sin(math.radians(40.18))
    out['trump_strip_capacity_s0_times_cos_plus_sin_at_40.18deg'] = float(F(S0_N, DEN)) * cs
    out['trump_strip_k'] = 5
    out['trump_strip_margin'] = float(F(S0_N, DEN)) * cs - 5
    return out


if __name__ == '__main__':
    import json
    print(json.dumps(self_test(), indent=1))
