"""T5'' — tilt-bin trimming at emission.  PREPARED, wired behind TRIM; see notes/lemmas.md.

A pin contributes its guaranteed core K_P: an axis-aligned square of half-side a_P = 1/2 - delta,
inside the pinned square wherever that square sits in its slack core.  Q(c, theta) (the unit
square) OVERLAPS K_P iff c lies in an octagon about the slot -- the Minkowski sum K_P (+) -Q --
because two convex squares are disjoint iff one of four axes separates them:

    |d_x| <= A, |d_y| <= A, |d.u| <= B, |d.v| <= B
    A = w/2 + a_P,  B = 1/2 + a_P*w,  w = |cos theta| + |sin theta|,
    u = (cos theta, sin theta),  v = (-sin theta, cos theta),  d = c - slot.

A tilt sub-interval is DEAD when the whole centre box lies inside ONE pin's octagon for every
theta in it: every admissible square at those tilts then overlaps that pinned square and is not
it, which is exactly T5's contradiction restricted to a tilt range.

    node  ==  trimmed child(ren) on the surviving sub-intervals  +  k excluded tilt intervals

The trimmed child is a SUB-BOX, so its certificate is the ordinary one and nothing in the frozen
verifier chain changes.  Each excluded interval is one T5-with-range instance.

Only the DEAD side is certified; anything not provably dead stays in the surviving bin, so
trimming can only ever remove configurations that carry no packing.  MARGIN shrinks A and B
before comparison so float slop cannot manufacture an exclusion; a fully rational version rounds
|d.n| up and A, B down.

Control (A96, 2026-09-05): 618/618 existing T5/T5' kills come out fully dead, zero violations.
Yield at that snapshot: 159 boxes with an empty surviving bin, of which 89 are incremental over
T5' (L1 31, L2 54, L3 3, L4 1).
"""
import math

TRIM = True          # set False to restore pre-T5'' behaviour exactly
MARGIN = 1e-9
NSUB = 256           # tilt sub-intervals scanned per bin
DELTA = 1e-2         # pin slack; a_P = 1/2 - DELTA


def _w(x_deg):
    r = math.radians(x_deg)
    return abs(math.cos(r)) + abs(math.sin(r))


def _w_min(d0, d1):
    """min of |cos| + |sin| over [d0, d1] degrees (minima at multiples of 90)."""
    best = min(_w(d0), _w(d1))
    k = math.ceil(d0 / 90.0)
    while k * 90.0 <= d1 + 1e-12:
        best = min(best, _w(k * 90.0))
        k += 1
    return best


def _max_proj(dx, dy, d0, d1, off):
    """max over theta in [d0,d1] of |dx cos(theta+off) + dy sin(theta+off)| (degrees)."""
    r = math.hypot(dx, dy)
    if r == 0.0:
        return 0.0
    phi = math.degrees(math.atan2(dy, dx)) - off
    k = math.ceil((d0 - phi) / 180.0)
    if phi + k * 180.0 <= d1 + 1e-12:
        return r                                   # a critical angle lies inside the interval
    def v(x):
        a = math.radians(x + off)
        return abs(dx * math.cos(a) + dy * math.sin(a))
    return max(v(d0), v(d1))


def dead_by_pin(box, slot, d0, d1, a_pin=None):
    """True if EVERY centre in `box` overlaps this pin's core for EVERY tilt in [d0, d1]."""
    # A111 bug (ii): the |cos| + |sin| envelopes below are stated for tilts in [0, 90].  A
    # reflected or unnormalised bin silently breaks them, so refuse it.
    if not (0.0 <= d0 <= d1 <= 90.0):
        raise ValueError(f"dead_by_pin: tilt interval [{d0}, {d1}] outside [0, 90]")
    aP = (0.5 - DELTA) if a_pin is None else a_pin
    if not (0.0 < aP < 0.5):
        raise ValueError(f"dead_by_pin: pin core half-side {aP} outside (0, 1/2)")
    wm = _w_min(d0, d1)
    A = wm / 2.0 + aP - MARGIN
    B = 0.5 + aP * wm - MARGIN
    for cx in (box.x0, box.x1):
        for cy in (box.y0, box.y1):
            dx, dy = cx - slot[0], cy - slot[1]
            if abs(dx) > A or abs(dy) > A:
                return False
            if _max_proj(dx, dy, d0, d1, 0.0) > B:
                return False
            if _max_proj(dx, dy, d0, d1, 90.0) > B:
                return False
    return True


def split_bin(box, slots, nsub=NSUB):
    """-> (surviving intervals, excluded intervals-with-witness-pin).

    Each excluded entry is (lo, hi, pin_index): the T5-with-range instance to certify."""
    if not (0.0 <= box.th0 <= box.th1 <= 90.0):
        raise ValueError(f"split_bin: tilt interval [{box.th0}, {box.th1}] outside [0, 90]")
    lo, hi = box.th0, box.th1
    if not TRIM or hi <= lo:
        return [[lo, hi]], []
    step = (hi - lo) / nsub
    alive, dead = [], []
    for i in range(nsub):
        a0, a1 = lo + i * step, lo + (i + 1) * step
        j = next((k for k, s in enumerate(slots) if dead_by_pin(box, s, a0, a1)), None)
        if j is None:
            if alive and abs(alive[-1][1] - a0) < 1e-12:
                alive[-1][1] = a1
            else:
                alive.append([a0, a1])
        else:
            if dead and abs(dead[-1][1] - a0) < 1e-12 and dead[-1][2] == j:
                dead[-1][1] = a1
            else:
                dead.append([a0, a1, j])
    return alive, dead


def trim_box(box, slots, nsub=NSUB):
    """-> (list of trimmed sub-boxes, excluded intervals).  An empty list of sub-boxes means the
    whole bin is dead: a T5-style kill needing no LP and no certificate."""
    from caselp import Box
    alive, dead = split_bin(box, slots, nsub)
    subs = [Box(box.x0, box.x1, box.y0, box.y1, a, b) for a, b in alive if b > a]
    return subs, dead
