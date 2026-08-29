#!/usr/bin/env python3
"""A43-H2 spine census core: type alphabet, certified per-link dx intervals,
tilt-class state machine, and the C0-C2 layered feasibility DP.

Everything is parametrised by the container side s (a float upper bound is used
in the SOUND direction: the span identity uses s as an interval).

--------------------------------------------------------------------------
TYPE ALPHABET (formalization.md Part 2)
   tau = (k; e_L, e_R; t_1..t_{k-1}) up to reversal,
   e in {F (wall-flush), C (wall-corner)},
   t in {FL, CEab (corner of q_i on edge of q_{i+1}), CEba, CC}.

TILT-CLASS STATE.  Gauge phi = theta mod 90 in [0, 90).  Classes are the maximal
runs of consecutive FL links.  A class is represented by one of

   ZS  -- the wall-flush zero class containing q_1      (only when e_L = F): phi = 0 exactly
   ZE  -- the wall-flush zero class containing q_k      (only when e_R = F): phi = 0 exactly
   0..NBIN-1 -- an ordinary class confined to tilt bin b = [BW*b, BW*(b+1)] deg

ZS and ZE are DIFFERENT classes that happen to carry the same value 0; keeping
them separate is what makes A31's "zero class has in-degree 0" rule checkable.
No CE/CC link may leave ZE (it is by definition the last run), and no CE/CC link
may enter ZS (it is by definition the first run) -- so the run structure of the
path is reproduced exactly by the state machine.

PER-LINK dx INTERVALS.  delta_i = c_{i+1} - c_i, dx_i = its x-component.  Each
link contributes a finite set of BRANCHES; a type is one printable label and the
branch set is an internal disjunction, so the census takes the UNION.

  FL, common tilt phi, shared-edge outward normal psi in {phi + 90m, m = 0..3}:
      delta = u(psi) + t u(psi+90), t in [-1, 1]
      dx    = cos psi - t sin psi in [cos psi - |sin psi|, cos psi + |sin psi|]
  CE, corner of a on edge of b, b's edge normal psi in {phi_b + 90m}:
      p   = c_b + (1/2) u(psi) + u u(psi+90),  u in [-1/2, 1/2]
      c_a = p + (sqrt2/2) u(th_d),  th_d = phi_a + 45 + 90j,  |th_d - psi| < 45
      (c_a - c_b)_x = (1/2)cos psi - u sin psi + (sqrt2/2) cos th_d
      The support condition forces n = (j - m) mod 4 = 3 when phi_a > phi_b and
      n = 0 when phi_a < phi_b, and is IMPOSSIBLE for n in {1, 2}; phi_a = phi_b
      is the flush degeneracy and is excluded.  n is the CE SIGN BRANCH.
  CC, both corners at the same point p:
      c_x = p + (sqrt2/2) u(th_x), th_x = phi_x + 45 + 90 j_x
      delta = (sqrt2/2)(u(th_b) - u(th_a)); NECESSARY certified relaxation of
      interior-disjointness: cos(th_a - th_b) <= 0  (equivalently |delta| >= 1).

ENDS.  x_1 = h(phi_1), x_k = s - h(phi_k), h(phi) = (cos phi + sin phi)/2.
Containment: x_i in [h(phi_i), s - h(phi_i)] (relaxed outward to the bin's h_lo).

CONSTRAINTS.
  C0 span + containment + consecutive distance (|dx| <= sqrt2 is the only part of
     |delta| in [1, sqrt2] that constrains x alone; y is free).
  C1 tilt-coupling feasibility -- encoded in the state machine (no strict edge
     inside a class; zero classes have in-degree 0; wall-corner end not in a zero
     class).  On a PATH the class digraph is a path, so an acyclic orientation
     with the zero class as a source always exists once those local rules hold;
     C1 therefore reduces exactly to the local rules.  (Recorded as a finding.)
  C2 tilt bins x span propagation (this module's DP) + the y-column capacity
     lemma (applied per anchor / per propagated window in census.py).

The DP is a forward reachability over cells: an EMPTY result is a certified kill;
a non-empty result is only a survival CANDIDATE (cells over-approximate x).
"""
from __future__ import annotations

import math
from ivl import I, cos_deg, sin_deg, h_deg, SQRT2, SQRT2H

# ----------------------------------------------------------------- alphabet
FL, CEAB, CEBA, CC = 0, 1, 2, 3
LINK_NAME = ['FL', 'CEab', 'CEba', 'CC']
END_F, END_C = 0, 1
END_NAME = ['F', 'C']
LINK_REV = [FL, CEBA, CEAB, CC]

BW = 3.0                       # tilt bin width, degrees
NBIN = int(round(90.0 / BW))   # 30 ordinary bins
ZS = NBIN                      # zero class containing q_1  (e_L = F)
ZE = NBIN + 1                  # zero class containing q_k  (e_R = F)
NST = NBIN + 2


def st_phi(st):
    """Certified phi-interval (degrees) of a class state."""
    if st >= NBIN:
        return (0.0, 0.0)
    return (BW * st, BW * (st + 1))


def st_is_zero(st):
    return st >= NBIN


_H_CACHE = {}


def st_h(st):
    """h(phi) enclosure for a class state."""
    v = _H_CACHE.get(st)
    if v is None:
        a, b = st_phi(st)
        v = h_deg(a, b)
        _H_CACHE[st] = v
    return v


# ------------------------------------------------------------- type coding
def type_id(k, eL, eR, links):
    v = eL * 2 + eR
    for t in links:
        v = v * 4 + t
    return v


def type_decode(k, tid):
    links = []
    for _ in range(k - 1):
        links.append(tid & 3)
        tid >>= 2
    links.reverse()
    eR = tid & 1
    eL = (tid >> 1) & 1
    return eL, eR, tuple(links)


def type_reverse(eL, eR, links):
    return eR, eL, tuple(LINK_REV[t] for t in reversed(links))


def type_canon(k, eL, eR, links):
    a = (eL, eR, tuple(links))
    b = type_reverse(eL, eR, links)
    ia = type_id(k, *a)
    ib = type_id(k, *b)
    return a if ia <= ib else b


def type_label(k, eL, eR, links):
    return '%s-%s-%s' % (END_NAME[eL], '.'.join(LINK_NAME[t] for t in links),
                         END_NAME[eR])


def all_types(k):
    """All canonical types of length k, as (eL, eR, links) tuples."""
    seen = set()
    out = []
    for eL in (END_F, END_C):
        for eR in (END_F, END_C):
            for v in range(4 ** (k - 1)):
                links = []
                w = v
                for _ in range(k - 1):
                    links.append(w & 3)
                    w >>= 2
                links = tuple(reversed(links))
                c = type_canon(k, eL, eR, links)
                cid = type_id(k, *c)
                if cid in seen:
                    continue
                seen.add(cid)
                out.append(c)
    return out


# --------------------------------------------------- per-link dx branch sets
def _fl_branches_p(P):
    """(branch_key, dx interval) for a flush link at common tilt window P."""
    a, b = P
    out = []
    for m in range(4):
        lo, hi = a + 90.0 * m, b + 90.0 * m
        C = cos_deg(lo, hi)
        S = sin_deg(lo, hi)
        w = S.maxabs()
        out.append((('FL', m), I(C.lo, C.hi) + I(-w, w)))
    return out


def _ce_spec_p(Pa, Pb, sgn, za=False, zb=False):
    """(branch_key, interval of (c_a - c_b)_x) for a CE contact, corner of a on
    edge of b.  sgn = +1 means phi_a > phi_b, -1 means phi_a < phi_b.
    za/zb flag a WALL-FLUSH-PINNED zero class (A31's zero class), which enables
    the in-degree-0 rule.  Returns [] if the sign branch is impossible."""
    # A31 zero-class rule: nothing sits below phi = 0.
    if za and zb:
        return []                       # strict edge between two zero classes
    if zb and sgn < 0:
        return []                       # phi_a < 0 impossible
    if za and sgn > 0:
        return []                       # phi_b < 0 impossible
    # bin compatibility of the strict sign (closed bins -> non-strict test)
    if sgn > 0 and not (Pa[1] >= Pb[0]):
        return []
    if sgn < 0 and not (Pa[0] <= Pb[1]):
        return []
    n = 3 if sgn > 0 else 0
    out = []
    for m in range(4):
        j = (m + n) % 4
        psi_lo, psi_hi = Pb[0] + 90.0 * m, Pb[1] + 90.0 * m
        thd_lo = Pa[0] + 45.0 + 90.0 * j
        thd_hi = Pa[1] + 45.0 + 90.0 * j
        # support condition |th_d - psi| < 45 (mod 360): must be satisfiable
        d_lo, d_hi = thd_lo - psi_hi, thd_hi - psi_lo
        if not _mod360_meets_open45(d_lo, d_hi):
            continue
        C = cos_deg(psi_lo, psi_hi)
        S = sin_deg(psi_lo, psi_hi)
        w = S.maxabs()
        Cd = cos_deg(thd_lo, thd_hi)
        dx = I(0.5, 0.5) * C + I(-0.5 * w, 0.5 * w) + SQRT2H * Cd
        out.append((('CE', sgn, m), dx))
    return out


def _mod360_meets_open45(lo, hi):
    """Does [lo, hi] meet (-45, 45) modulo 360?"""
    if hi - lo >= 360.0:
        return True
    n0 = math.floor((lo + 45.0) / 360.0)
    n1 = math.ceil((hi + 45.0) / 360.0)
    for n in range(int(n0) - 1, int(n1) + 2):
        a, b = -45.0 + 360.0 * n, 45.0 + 360.0 * n
        if lo < b and a < hi:
            return True
    return False


def _cc_branches_p(Pa, Pb):
    """(branch_key, dx = (c_b - c_a)_x) for a corner-corner link, a = q_i."""
    out = []
    for ja in range(4):
        tha_lo = Pa[0] + 45.0 + 90.0 * ja
        tha_hi = Pa[1] + 45.0 + 90.0 * ja
        for jb in range(4):
            thb_lo = Pb[0] + 45.0 + 90.0 * jb
            thb_hi = Pb[1] + 45.0 + 90.0 * jb
            # necessary disjointness relaxation: cos(th_a - th_b) <= 0
            d = cos_deg(tha_lo - thb_hi, tha_hi - thb_lo)
            if d.lo > 0.0:
                continue
            Ca = cos_deg(tha_lo, tha_hi)
            Cb = cos_deg(thb_lo, thb_hi)
            dx = SQRT2H * (I(Cb.lo, Cb.hi) - I(Ca.lo, Ca.hi))
            out.append((('CC', ja, jb), dx))
    return out


_BP_CACHE = {}


def branches_p(link, Pi, Pj, zi=False, zj=False):
    key = (link, Pi, Pj, zi, zj)
    v = _BP_CACHE.get(key)
    if v is None:
        v = _branches_p(link, Pi, Pj, zi, zj)
        if len(_BP_CACHE) < 200000:
            _BP_CACHE[key] = v
    return v


def _branches_p(link, Pi, Pj, zi=False, zj=False):
    """Certified (branch_key, dx = x_{i+1} - x_i) list for one link, given the
    tilt windows Pi (q_i) and Pj (q_{i+1}) in degrees and the wall-flush-zero
    flags.  This is the raw geometric layer used by BOTH the census (bins) and
    the realized-point canary check (degenerate windows)."""
    if link == FL:
        # flush forces phi_i = phi_{i+1}: the two windows must intersect, and the
        # certified common-tilt window is their hull (outward, hence sound).
        if Pi[1] < Pj[0] or Pj[1] < Pi[0]:
            v = []
        else:
            v = _fl_branches_p((min(Pi[0], Pj[0]), max(Pi[1], Pj[1])))
    elif link == CEAB:
        # a = q_i (corner), b = q_{i+1} (edge); dx_link = -(c_a - c_b)_x
        v = []
        for sgn in (1, -1):
            for bk, dxs in _ce_spec_p(Pi, Pj, sgn, zi, zj):
                v.append((('CEab',) + bk[1:], -dxs))
    elif link == CEBA:
        # a = q_{i+1} (corner), b = q_i (edge); dx_link = +(c_a - c_b)_x
        v = []
        for sgn in (1, -1):
            for bk, dxs in _ce_spec_p(Pj, Pi, sgn, zj, zi):
                v.append((('CEba',) + bk[1:], dxs))
    else:
        v = _cc_branches_p(Pi, Pj)
    # L5(a) redundant check: |dx| <= sqrt2 (the x-shadow of |delta| <= sqrt2)
    return [(bk, I(max(d.lo, -SQRT2.hi), min(d.hi, SQRT2.hi))) for bk, d in v
            if d.lo <= SQRT2.hi and d.hi >= -SQRT2.hi]


_BR_CACHE = {}


def link_branches(link, sa, sb):
    """Certified branch list for one link between class states sa (q_i) and
    sb (q_{i+1}).  For FL the two are the same class, so sa must equal sb."""
    key = (link, sa, sb)
    v = _BR_CACHE.get(key)
    if v is None:
        if link == FL and sa != sb:
            v = []
        else:
            v = branches_p(link, st_phi(sa), st_phi(sb),
                           st_is_zero(sa), st_is_zero(sb))
        _BR_CACHE[key] = v
    return v


def link_dx_union(link, sa, sb):
    """Hull of the branch union (None if the link is impossible)."""
    br = link_branches(link, sa, sb)
    if not br:
        return None
    lo = min(d.lo for _, d in br)
    hi = max(d.hi for _, d in br)
    return I(lo, hi)


# -------------------------------------------------- state-transition legality
def state_transition_ok(link, sa, sb):
    """Structural (class-graph) legality, independent of geometry."""
    if link == FL:
        return sa == sb
    # a CE/CC link starts a NEW class
    if sb == ZS:
        return False        # ZS is by definition the run containing q_1
    if sa == ZE:
        return False        # ZE is by definition the run containing q_k
    return True


# ------------------------------------------------------------------- the DP
class Geom:
    """Container-side dependent geometry: cells, per-state boxes, transitions."""

    def __init__(self, s, cell_w=1.0 / 8.0):
        self.s = float(s)
        self.S = I(self.s, self.s)
        self.cw = float(cell_w)
        n = int(math.ceil(self.s / self.cw))
        self.ncell = n
        self.cells = []
        for i in range(n):
            lo = i * self.cw
            hi = min((i + 1) * self.cw, self.s)
            self.cells.append(I(lo, hi))
        # per-state containment box [h_lo, s - h_lo] (outward relaxation)
        self.box = {}
        for st in range(NST):
            h = st_h(st)
            self.box[st] = I(h.lo, self.s - h.lo)
        # per-state end intervals
        self.xL = {st: I(st_h(st).lo, st_h(st).hi) for st in range(NST)}
        self.xR = {st: I(self.s - st_h(st).hi, self.s - st_h(st).lo)
                   for st in range(NST)}
        self._cellbox = {}
        self._cellarr_cache = {}
        self._T = {}
        self._M = {}

    def cellbox(self, st, ci):
        """cell ci intersected with the containment box of state st (or None)."""
        key = (st, ci)
        if key in self._cellbox:
            return self._cellbox[key]
        v = self.cells[ci].inter(self.box[st])
        self._cellbox[key] = v
        return v

    def nstate(self):
        return NST * self.ncell

    def _cellarr(self, st, pin=None):
        """(lo, hi, ok) arrays of the certified x-window of square in state st,
        cell-by-cell.  pin = 'L' applies the LEFT end identity x = h(phi),
        pin = 'R' the right one x = s - h(phi); None is plain containment."""
        import numpy as np
        key = (st, pin)
        v = self._cellarr_cache.get(key)
        if v is None:
            lo = np.zeros(self.ncell)
            hi = np.zeros(self.ncell)
            ok = np.zeros(self.ncell, dtype=bool)
            base = self.box[st] if pin is None else (
                self.xL[st] if pin == 'L' else self.xR[st])
            for ci in range(self.ncell):
                B = self.cells[ci].inter(base)
                if B is not None:
                    lo[ci], hi[ci], ok[ci] = B.lo, B.hi, True
            v = (lo, hi, ok)
            self._cellarr_cache[key] = v
        return v

    def _build(self, link, count, apin, bpin):
        """Boolean (count=False) or branch-multiplicity (count=True) matrix."""
        import numpy as np
        N = self.nstate()
        M = np.zeros((N, N), dtype=(np.float32 if count else bool))
        nc = self.ncell
        for sa in range(NST):
            Alo, Ahi, Aok = self._cellarr(sa, apin)
            for sb in range(NST):
                if not state_transition_ok(link, sa, sb):
                    continue
                br = link_branches(link, sa, sb)
                if not br:
                    continue
                Blo, Bhi, Bok = self._cellarr(sb, bpin)
                mask = Aok[:, None] & Bok[None, :]
                if not mask.any():
                    continue
                blk = np.zeros((nc, nc), dtype=(np.float32 if count else bool))
                items = br if count else [(None, link_dx_union(link, sa, sb))]
                for _, D in items:
                    c = ((D.lo <= (Bhi[None, :] - Alo[:, None])) &
                         ((Blo[None, :] - Ahi[:, None]) <= D.hi) & mask)
                    blk = blk + c if count else (blk | c)
                M[sa * nc:(sa + 1) * nc, sb * nc:(sb + 1) * nc] = blk
        return M

    def trans(self, link, apin=None, bpin=None):
        key = (link, apin, bpin)
        T = self._T.get(key)
        if T is None:
            T = self._build(link, False, apin, bpin)
            self._T[key] = T
        return T

    def mult(self, link, apin=None, bpin=None):
        """Branch-multiplicity matrix: entry = #geometric branches realising the
        (state, cell) -> (state, cell) step."""
        key = (link, apin, bpin)
        M = self._M.get(key)
        if M is None:
            M = self._build(link, True, apin, bpin)
            self._M[key] = M
        return M

    def _endvec(self, e, side):
        import numpy as np
        v = np.zeros(self.nstate(), dtype=bool)
        if side == 'L':
            states = [ZS] if e == END_F else list(range(NBIN))
        else:
            states = [ZS, ZE] if e == END_F else list(range(NBIN))
        for st in states:
            _, _, ok = self._cellarr(st, side)
            v[st * self.ncell:(st + 1) * self.ncell] = ok
        return v

    def start_vec(self, eL):
        return self._endvec(eL, 'L')

    def end_mask(self, eR):
        return self._endvec(eR, 'R')

    def pins(self, k):
        """(apin, bpin) per link for a spine of length k."""
        return [('L' if i == 0 else None, 'R' if i == k - 2 else None)
                for i in range(k - 1)]

    def step(self, v, link, apin=None, bpin=None):
        import numpy as np
        T = self.trans(link, apin, bpin)
        idx = np.flatnonzero(v)
        if idx.size == 0:
            return v
        return T[idx].any(axis=0)

    def alive(self, eL, eR, links):
        """C0-C2 (span/containment/tilt-coupling/bin-propagation) feasibility.
        False => CERTIFIED dead.  True => survival candidate."""
        k = len(links) + 1
        v = self.start_vec(eL)
        for t, (a, b) in zip(links, self.pins(k)):
            v = self.step(v, t, a, b)
            if not v.any():
                return False
        return bool((v & self.end_mask(eR)).any())
