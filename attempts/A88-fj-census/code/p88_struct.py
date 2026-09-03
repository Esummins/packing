"""struct88.py -- A88 T3 COST-PILOT: contact-STRUCTURE vocabulary + core box.

A "structure" H is (rows, tilt-class decoration, wall masks).  Rows use the
t3lib row vocabulary:
    {'kind':'wall','i','corner','wall'}
    {'kind':'sep' ,'o','e','p','k'}          (kstar stored under 'k')
    {'kind':'dom' ,'o','e','p','k','m'}
The certificate attached to H is LOCAL TO THE LOADED CORE: only squares that
appear in some row of H are variables; unloaded squares are dropped (their
feasibility is discarded -- a sound weakening, since dropping constraints can
only enlarge the FJ-point set).

Core variable layout (per structure), length D:
    [cx_i, cy_i for each loaded square i (in sorted order)]  -> 2*k_H
    [tilt of tilt-class c for each NON-pinned class]         -> n_free
    [s]                                                      -> 1
Pinned (class 0) squares have theta == 0 exactly.

NOTHING here emits a certificate.  Interval arithmetic is float-based with an
outward pad (see fastiv.py); this is a COST measurement, not a verdict.
"""
from __future__ import annotations

import math
from fractions import Fraction

import t3lib as T

S_LO = 3.82
S_HAT_HI = 3.877084
SQRT2H = math.sqrt(2.0) / 2.0
HALFPI = math.pi / 2.0

HALF = [(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)]
NHAT = [(0.0, -1.0), (1.0, 0.0), (0.0, 1.0), (-1.0, 0.0)]

WALL_BIT = {'x=0': 1, 'y=0': 2, 'x=s': 4, 'y=s': 8}


# --------------------------------------------------------------- structure

def squares_of_row(r):
    if r['kind'] == 'wall':
        return (r['i'],)
    return (r['o'], r['p'])


def loaded_squares(rows):
    s = set()
    for r in rows:
        s.update(squares_of_row(r))
    return sorted(s)


def wall_masks(rows, loaded):
    mask = {i: 0 for i in loaded}
    for r in rows:
        if r['kind'] == 'wall':
            mask[r['i']] |= WALL_BIT[r['wall']]
    return mask


def norm_theta(t):
    """Clamp a tilt into the working range [0, pi/2].

    NOTE: no folding mod pi/2 is done.  Folding a theta of pi/2 down to 0 would
    ROTATE the corner and edge labels of that square, which would silently
    change every row of H that mentions it.  A square recorded at theta = pi/2
    is therefore kept as its own (pinned) tilt class, distinct from theta = 0.
    """
    t = float(t)
    if abs(t) < 1e-12:
        return 0.0
    if abs(t - HALFPI) < 1e-9:
        return HALFPI
    return min(max(t, 0.0), HALFPI)


def tilt_classes(thetas, loaded, tol=1e-7):
    """Group loaded squares by equal tilt (the flush/parallel decoration).

    Returns (cls, reps, pinned, order) where
      cls[i]  = class index of square i
      reps[c] = representative tilt of class c (mean of the group)
      pinned  = {class index: pinned value} for axis-aligned classes
                (rep == 0 or rep == pi/2 -- theta is then fixed EXACTLY)
      order   = [(a, b), ...] meaning tilt(a) < tilt(b) strictly
    Classes are numbered in increasing tilt, so `order` is the total order
    0 < 1 < ... < n-1.
    """
    vals = sorted(norm_theta(thetas[i]) for i in loaded)
    groups = [[vals[0]]]
    for v in vals[1:]:
        if v - groups[-1][-1] <= tol:
            groups[-1].append(v)
        else:
            groups.append([v])
    reps = [sum(g) / len(g) for g in groups]
    cls = {}
    for i in loaded:
        t = norm_theta(thetas[i])
        cls[i] = min(range(len(reps)), key=lambda c: abs(reps[c] - t))
    pinned = {}
    for c, v in enumerate(reps):
        if v <= 1e-9:
            pinned[c] = 0.0
        elif abs(v - HALFPI) <= 1e-9:
            pinned[c] = HALFPI
    order = [(c, c + 1) for c in range(len(reps) - 1)]
    return cls, reps, pinned, order


class Structure:
    """Support structure H + its core box parametrisation."""

    def __init__(self, tag, rows, cls, reps, pinned, order, extra=None,
                 ineq=None):
        self.tag = tag
        self.rows = list(rows)
        # rows imposed as INEQUALITIES g >= 0 rather than equalities.  The
        # census emits only the sep/wall EQUALITY rows; the t3lib DOMINANCE
        # rows that make a sep row equal true SAT separation are side
        # conditions, so they are rebuilt here and carried separately.
        self.ineq = list(ineq or [])
        self.loaded = loaded_squares(rows)
        self.k_H = len(self.loaded)
        self.m = len(rows)
        self.chi = self.m - (3 * self.k_H + 1)
        self.cls = cls
        self.reps = reps
        # pinned: {class index -> exact pinned tilt value}
        self.pinned = dict(pinned) if isinstance(pinned, dict) \
            else {c: 0.0 for c in pinned}
        self.order = list(order)
        self.masks = wall_masks(rows, self.loaded)
        self.extra = extra or {}
        self.free_cls = [c for c in range(len(reps)) if c not in self.pinned]
        # core variable index maps
        self.ix = {}
        n = 0
        for i in self.loaded:
            self.ix[('cx', i)] = n; n += 1
            self.ix[('cy', i)] = n; n += 1
        for c in self.free_cls:
            self.ix[('th', c)] = n; n += 1
        self.ix[('s',)] = n; n += 1
        self.D = n
        self.n_cls = len(reps)

    # ---- boxes -----------------------------------------------------------
    def centre_range(self, i, s_hi, s_lo=S_LO):
        """Wall-tightened centre box (A31 lib0._box, generalised to [s_lo,s_hi])."""
        m = self.masks[i]
        if m & 1:
            x = (0.5, SQRT2H)
        elif m & 4:
            x = (s_lo - SQRT2H, s_hi - 0.5)
        else:
            x = (0.5, s_hi - 0.5)
        if m & 2:
            y = (0.5, SQRT2H)
        elif m & 8:
            y = (s_lo - SQRT2H, s_hi - 0.5)
        else:
            y = (0.5, s_hi - 0.5)
        return x, y

    def core_box(self, s_lo=S_LO, s_hi=S_HAT_HI):
        """Initial core box as a list of D (lo, hi) float pairs."""
        b = [None] * self.D
        for i in self.loaded:
            x, y = self.centre_range(i, s_hi, s_lo)
            b[self.ix[('cx', i)]] = x
            b[self.ix[('cy', i)]] = y
        for c in self.free_cls:
            b[self.ix[('th', c)]] = (0.0, HALFPI)
        b[self.ix[('s',)]] = (s_lo, s_hi)
        return b

    def theta_bin(self, box, i):
        """(lo, hi) tilt interval of loaded square i under core box `box`."""
        c = self.cls[i]
        if c in self.pinned:
            v = self.pinned[c]
            return (v, v)
        return box[self.ix[('th', c)]]

    def cls_bin(self, box, c):
        if c in self.pinned:
            v = self.pinned[c]
            return (v, v)
        return box[self.ix[('th', c)]]

    def order_consistent(self, box, eps=0.0):
        """False if the strict class order is impossible on this box."""
        for a, b in self.order:
            la = self.cls_bin(box, a)
            lb = self.cls_bin(box, b)
            if la[0] >= lb[1] - eps and not (la == lb and la[0] == la[1]):
                return False
        return True

    # ---- 34-vector view for t3lib ---------------------------------------
    def to34(self, box):
        """Embed the core box into a 34-slot (lo, hi) list; unloaded squares
        get their full generic ranges (never touched by rows of H)."""
        s = box[self.ix[('s',)]]
        out = [(0.5, s[1] - 0.5)] * 34
        out = list(out)
        for i in range(11):
            out[3 * i] = (0.5, s[1] - 0.5)
            out[3 * i + 1] = (0.5, s[1] - 0.5)
            out[3 * i + 2] = (0.0, HALFPI)
        for i in self.loaded:
            out[3 * i] = box[self.ix[('cx', i)]]
            out[3 * i + 1] = box[self.ix[('cy', i)]]
            out[3 * i + 2] = self.theta_bin(box, i)
        out[33] = s
        return out

    def summary(self):
        rk = self.extra.get('rank')
        d_H = (3 * self.k_H + 1 - rk) if rk is not None else None
        return {
            'tag': self.tag, 'k_H': self.k_H, 'm': self.m, 'chi': self.chi,
            'D_core': self.D, 'n_cls': self.n_cls, 'n_free_cls': len(self.free_cls),
            'pinned0': (0 in self.pinned),
            'n_pinned_cls': len(self.pinned), 'rank': rk, 'd_H': d_H,
            'rattlers': self.extra.get('rattlers'),
            'rigid_possible': self.chi >= 0,
            'rigid_possible_core': (self.m >= self.D),
            'n_wall_rows': sum(1 for r in self.rows if r['kind'] == 'wall'),
            'n_sep_rows': sum(1 for r in self.rows if r['kind'] == 'sep'),
            'n_dom_rows': sum(1 for r in self.rows if r['kind'] == 'dom'),
            'n_ineq_rows': len(self.ineq),
            'masks': {str(i): self.masks[i] for i in self.loaded},
        }


# ------------------------------------------------------- serialise / load

def rows_to_json(rows):
    out = []
    for r in rows:
        d = {k: v for k, v in r.items() if k != 'vars'}
        out.append(d)
    return out


def rows_from_json(js):
    rows = []
    for d in js:
        if d['kind'] == 'wall':
            rows.append(T.wall_row(d['i'], d['corner'], d['wall']))
        elif d['kind'] == 'sep':
            rows.append(T.sep_row(d['o'], d['e'], d['p'], d.get('k', d.get('kstar'))))
        elif d['kind'] == 'dom':
            rows.append(T.dom_row(d['o'], d['e'], d['p'],
                                  d.get('k', d.get('kstar')), d['m']))
        else:
            raise ValueError(d['kind'])
    return rows


def struct_to_json(st):
    return {'tag': st.tag, 'rows': rows_to_json(st.rows),
            'ineq': rows_to_json(st.ineq),
            'cls': {str(k): v for k, v in st.cls.items()},
            'reps': st.reps,
            'pinned': {str(k): v for k, v in st.pinned.items()},
            'order': [list(o) for o in st.order], 'extra': st.extra}


def struct_from_json(d):
    rows = rows_from_json(d['rows'])
    cls = {int(k): v for k, v in d['cls'].items()}
    p = d['pinned']
    pinned = ({int(k): float(v) for k, v in p.items()} if isinstance(p, dict)
              else {int(c): 0.0 for c in p})
    return Structure(d['tag'], rows, cls, d['reps'], pinned,
                     [tuple(o) for o in d['order']], d.get('extra'),
                     ineq=rows_from_json(d.get('ineq') or []))
