"""
A57 soundness guard for YES children (a gap in A54's `substrat.py`, harmless there, fatal here).

A YES child adds a core box B to the pins and drops the budget from 11-k to 11-k-1.  That is
sound only if the square witnessing B is a DIFFERENT square from every pinned one -- the node
semantics "budget = n - #cores" silently assumes the cores are realised by distinct squares.
Three cases, decided from B and the pins alone:

  * "parent"        -- some pin's placement (px, py, 0deg) lies IN B (remember theta = 90 is the
                       SAME square as theta = 0, so a box touching 90 realises an upright pin).
                       Then B may be witnessed by that pin itself, only k squares are accounted
                       for, and the child is just the parent with a redundant core.  Certifying
                       it at budget 11-k-1 would certify a FALSE statement.  A57 marks such a
                       child UNSOUND-AT-REDUCED-BUDGET and never certifies it; it must instead be
                       carried at the parent's budget (i.e. it makes no progress).
  * "contradictory" -- B's rational core meets some pin's core, and no pin placement lies in B.
                       Every square with (centre, theta) in B then overlaps that pinned square
                       and is not it, so the hypotheses are contradictory and the child is EMPTY
                       by logic -- a kill that needs no LP and no certificate.
  * "ok"            -- neither; the ordinary case.

A54's one rung-3 probe (k6_23 / side_T, boxes from x = 1.1 outward) happened to avoid both
degenerate cases, which is why the gap never fired there.  It fires immediately on any corner or
side zone that contains a pin.
"""
import math

import numpy as np


def _core_quad(c):
    """the four corners of a Core as floats."""
    cx, cy, a = float(c.kx), float(c.ky), float(c.a)
    co, si = float(c.cm), float(c.sm)
    u = (co * a, si * a)
    v = (-si * a, co * a)
    return [(cx + su * u[0] + sv * v[0], cy + su * u[1] + sv * v[1])
            for su, sv in ((1, 1), (1, -1), (-1, -1), (-1, 1))]


def cores_meet(c1, c2, eps=1e-12):
    """separating-axis test on two Cores (rotated squares); True if they overlap."""
    for (a, b) in ((c1, c2), (c2, c1)):
        co, si = float(a.cm), float(a.sm)
        for ax in ((co, si), (-si, co)):
            p1 = [ax[0] * x + ax[1] * y for (x, y) in _core_quad(a)]
            p2 = [ax[0] * x + ax[1] * y for (x, y) in _core_quad(b)]
            if min(p1) > max(p2) + eps or min(p2) > max(p1) + eps:
                return False
    return True


def box_realizes_pin(box, pins, tol=1e-9):
    """a pin placement (px, py, 0 deg) inside the box; theta 90 == theta 0 for a square."""
    th_ok = (box.th0 - 1e-9 <= 0.0 <= box.th1 + 1e-9) or (box.th0 - 1e-9 <= 90.0 <= box.th1 + 1e-9)
    if not th_ok:
        return None
    for (px, py) in pins:
        if box.x0 - tol <= px <= box.x1 + tol and box.y0 - tol <= py <= box.y1 + tol:
            return (px, py)
    return None


class _TightCore:
    """Duck-typed stand-in for caselp.Core carrying only what cores_meet reads.  Deliberately not
    a real Core and deliberately not returned by Box.core(): see tight_a()."""

    __slots__ = ("kx", "ky", "a", "cm", "sm")

    def __init__(self, kx, ky, a, cm, sm):
        self.kx, self.ky, self.a, self.cm, self.sm = kx, ky, a, cm, sm


def _cs(deg):
    r = math.radians(deg)
    return abs(math.cos(r)) + abs(math.sin(r))


def _max_cs(d0, d1):
    """max of |cos| + |sin| over [d0, d1] degrees; the interior maxima are at 45 deg mod 90."""
    best = max(_cs(d0), _cs(d1))
    k = math.floor(d0 / 90.0)
    while k * 90.0 + 45.0 <= d1 + 1e-12:
        c = k * 90.0 + 45.0
        if c >= d0 - 1e-12:
            best = max(best, _cs(c))
        k += 1
    return best


def tight_a(box, tm_deg):
    """A96 (2026-09-05).  The TIGHT half-side of the common inscribed square of every unit square
    whose (centre, tilt) lies in `box`, for a core at the box centre with tilt tm_deg:

        a = (1/2 - h * M_c) / M_t,   h   = centre-box half-WIDTH,
                                     M_c = max(|cos|+|sin|) over the box's tilt range,
                                     M_t = max(|cos|+|sin|) over the tilt range about tm.

    K subset Q(c, theta) iff every corner of K lies in Q, i.e. |R(-theta) d + a R(phi) s|_inf
    <= 1/2 for d = k - c, phi = tm - theta and the four sign vectors s; bounding the two terms
    separately gives the formula.  caselp.Box.core()'s (1/2 - hd)/(1 + (t1-t0)) is the same bound
    with hd = h*sqrt(2) (i.e. assuming 45 deg is always in the tilt range) and with
    1 + (t1-t0) >= M_t; it is sound but loose, by 0.7-11% on the deployed cover.

    THIS IS USED ONLY BY classify(), i.e. only for the KILL-BY-LOGIC decision.  It is NOT wired
    into Box.core(), because that core is the LP's hypothesis and appears in every emitted
    certificate: changing it would change the certificate corpus.  The kill certificate itself is
    UNCHANGED (T5, Lean core_meet_same_square); only the half-side of the core the rule is
    applied to has grown, and since the centre and tilt are untouched the new core CONTAINS the
    old one, so no previously-valid kill can be lost.  Control: 583/583 known logic-kill boxes
    still killed (attempts/A96-a57-parametric/results/core96.json).
    """
    h = max(0.5 * (box.x1 - box.x0), 0.5 * (box.y1 - box.y0))
    Mc = _max_cs(box.th0, box.th1)
    phi0, phi1 = box.th0 - tm_deg, box.th1 - tm_deg
    lo, hi = min(phi0, phi1), max(phi0, phi1)
    Mt = max(_cs(lo), _cs(hi), 1.0 if lo <= 0.0 <= hi else 0.0)
    return (0.5 - h * Mc) / Mt


TIGHT_CORE = True          # set False to fall back to caselp.Box.core() exactly
TIGHT_EPS = 1e-9           # shrink before use, so float slop can never manufacture a kill


def kill_core(box):
    """The core the logic-kill rule is applied to: the box's own core, enlarged to the tight
    common inscribed square when that is bigger.  Never smaller than box.core()."""
    cb = box.core()
    if cb is None or not TIGHT_CORE:
        return cb
    try:
        tm_deg = math.degrees(2.0 * math.atan(float(cb.tm)))
        a = tight_a(box, tm_deg) - TIGHT_EPS
    except Exception:
        return cb
    if a <= float(cb.a):
        return cb
    return _TightCore(cb.kx, cb.ky, a, cb.cm, cb.sm)


def classify(box, pin_boxes, pin_slots):
    """-> ('parent', pin) | ('contradictory', i) | ('ok', None)"""
    p = box_realizes_pin(box, pin_slots)
    if p is not None:
        return "parent", list(p)
    cb = kill_core(box)
    if cb is None:
        return "nocore", None
    for i, pb in enumerate(pin_boxes):
        if cores_meet(cb, pb.core()):
            return "contradictory", i
    return "ok", None
