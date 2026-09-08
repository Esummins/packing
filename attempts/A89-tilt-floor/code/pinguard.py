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


def classify(box, pin_boxes, pin_slots, tol=1e-9, pin_full=None):
    """-> ('parent', pin) | ('contradictory', info) | ('ok', None)

    A84 edits (the ONLY changes to this file; with the defaults the behaviour is byte-identical
    to A57/A60's):

    `tol` widens the 'parent' test.  With SLACK pins the hypothesis is "a square sits SOMEWHERE
    in [slot +- delta]^2 at theta ~ 0", so a cover box containing any point of that dilated slot
    at theta = 0 or 90 can be realised by the pin square itself and must be booked 'parent'
    (UNSOUND-AT-REDUCED-BUDGET), not certified.  Callers pass tol = delta_pin + 1e-9.

    `pin_full` is LEMMA PD (pin drift), the repair for the delta_pin residue floor.  With slack
    cores (a = 1/2 - delta) a copy of an image square that penetrates a pin's SLOT SQUARE by
    e < delta meets no pin core, so it drops only one witness and the alive gate calls its box
    unkillable forever: the residue floor equals delta_pin (measured on k3_05: 2.199e-2 vs
    delta_pin = 2e-2, ladder scan `*_pre_PD.json`).

    The repair.  Over the transfer window the dilated family's pin p is the FULL unit square
    Sigma_p + d(lambda), d(lambda) = (lambda - 1) alpha_p per coordinate (Lemma B.0(c); the
    drift always points INTO the container), lambda in [1, lambda_max].  {d : K meets Sigma_p+d}
    = K - Sigma_p is CONVEX, so if core(B) meets Sigma_p at BOTH lambda = 1 and lambda =
    lambda_max it meets it for every lambda in between: every square realising B overlaps the
    pin square and is not it, so B's hypotheses are contradictory -- a free logic kill.

    `pin_full` is a list of (Core(Sigma_p), Core(Sigma_p + d_max)) pairs, both built from the
    FULL unit square (a = 1/2, tm = 0).  |d_max| is rounded OUTWARD, which is sound in both
    directions (it enlarges the covered segment and makes the test stricter)."""
    p = box_realizes_pin(box, pin_slots, tol)
    if p is not None:
        return "parent", list(p)
    cb = box.core()
    if cb is None:
        return "nocore", None
    for i, pb in enumerate(pin_boxes):
        if cores_meet(cb, pb.core()):
            return "contradictory", dict(pin=i, rule="slack-core")
    if pin_full:
        for i, (S_lo, S_hi) in enumerate(pin_full):
            if cores_meet(cb, S_lo) and cores_meet(cb, S_hi):
                return "contradictory", dict(pin=i, rule="PD", endpoints="both")
    return "ok", None
