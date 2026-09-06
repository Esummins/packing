"""A96 / A110 follow-up: TILT-BIN TRIMMING -- which tilts in a cover box are dead by logic.

MEASUREMENT ONLY.  Campaign paused; nothing here writes into A57 or deploys anything.

THE GEOMETRY.  A pin contributes its guaranteed core K_P: an axis-aligned square of half-side
a_P = 1/2 - delta (delta = 1e-2), centred at the slot, contained in the pinned square wherever
that square actually sits inside its slack core.  A candidate square Q(c, theta) is the unit
square (half-side 1/2) at tilt theta.  By the separating-axis theorem for two convex squares,
Q and K_P are DISJOINT iff one of four axes separates them: alpha in {0, 90, theta, theta+90}.
Writing d = c - s and w(theta) = |cos theta| + |sin theta|, they OVERLAP iff all four hold:

    |d_x| <= A,   |d_y| <= A,   |d . u| <= B,   |d . v| <= B
    A = w(theta)/2 + a_P,   B = 1/2 + a_P * w(theta),   u = (cos, sin),  v = (-sin, cos)

i.e. c lies in an OCTAGON about the slot (the Minkowski sum K_P (+) -Q(theta)).

A tilt sub-interval is CERTIFIED DEAD when, for some single pin, the whole centre box lies
inside that pin's octagon for every theta in the sub-interval -- then every admissible square at
those tilts overlaps that pinned square, which is exactly T5's contradiction, so the tilts carry
no configuration.  The test is run on all four box corners (the octagon is convex) with the
worst case over the sub-interval: the LARGEST |d . n| against the SMALLEST A, B.

  d . u = r cos(theta - phi) and d . v = r cos(theta - phi + 90), r = |d| -- so the max of each
  over a theta-interval is r when the critical angle falls inside, else the larger endpoint.
  w(theta) = |cos| + |sin| has its minima at multiples of 90 and maxima at 45 mod 90, so min A
  and min B come from min w over the interval, which is at an endpoint unless a multiple of 90
  is interior.

SOUNDNESS DIRECTION.  Only the DEAD side is certified; a sub-interval that is not provably dead
is left in the surviving bin.  So the trimmed fraction reported here is a LOWER bound on what a
deployed rule would remove, and the surviving bin is an UPPER bound on what survives.  Two
deliberate conservatisms: (a) only SINGLE-pin domination is tested -- a box covered by the UNION
of two pins' octagons but by neither alone is not trimmed here, and (b) float arithmetic with a
safety margin (a deployed version must use rational endpoints and round the |d.n| bounds UP and
A, B DOWN).

POSITIVE CONTROL.  A T5' kill has K_B meeting a pin core; K_B is inside every Q, so every c in
the box already overlaps that pin -- the box is inside the octagon at every tilt.  So every
existing T5' kill MUST come out fully dead here, and that is checked.
"""
import argparse, glob, json, math, os, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
A57 = os.path.abspath(os.path.join(BASE, "..", "A57-shadow-trees"))
A53 = os.path.abspath(os.path.join(BASE, "..", "A53-simple-strata"))
sys.path.insert(0, os.path.join(A57, "code"))
import pinguard
from caselp import Box

DELTA = 1e-2
A_PIN = 0.5 - DELTA            # half-side of the pin's guaranteed core
MARGIN = 1e-9                  # float safety: shrink A, B before comparing


def w_min(d0, d1):
    """min of |cos| + |sin| over [d0, d1] degrees (minima at multiples of 90)."""
    def w(x):
        r = math.radians(x)
        return abs(math.cos(r)) + abs(math.sin(r))
    best = min(w(d0), w(d1))
    k = math.ceil(d0 / 90.0)
    while k * 90.0 <= d1 + 1e-12:
        best = min(best, w(k * 90.0))
        k += 1
    return best


def max_proj(dx, dy, d0, d1, off):
    """max over theta in [d0,d1] of |dx cos(theta+off) + dy sin(theta+off)|, degrees."""
    r = math.hypot(dx, dy)
    if r == 0.0:
        return 0.0
    phi = math.degrees(math.atan2(dy, dx)) - off      # extremum where theta = phi mod 180
    lo, hi = d0, d1
    k = math.ceil((lo - phi) / 180.0)
    while phi + k * 180.0 <= hi + 1e-12:
        return r                                      # a critical angle is inside: full r
    def v(x):
        a = math.radians(x + off)
        return abs(dx * math.cos(a) + dy * math.sin(a))
    return max(v(lo), v(hi))


def dead_by_pin(b, slot, d0, d1):
    """Is every centre in the box inside this pin's octagon for every tilt in [d0,d1]?"""
    wm = w_min(d0, d1)
    A = wm / 2.0 + A_PIN - MARGIN
    B = 0.5 + A_PIN * wm - MARGIN
    for cx in (b.x0, b.x1):
        for cy in (b.y0, b.y1):
            dx, dy = cx - slot[0], cy - slot[1]
            if abs(dx) > A or abs(dy) > A:
                return False
            if max_proj(dx, dy, d0, d1, 0.0) > B:
                return False
            if max_proj(dx, dy, d0, d1, 90.0) > B:
                return False
    return True


def surviving(b, slots, nsub=256):
    """-> (surviving fraction, list of surviving [lo,hi] tilt sub-intervals)."""
    lo, hi = b.th0, b.th1
    if hi <= lo:
        return 1.0, [[lo, hi]]
    step = (hi - lo) / nsub
    alive = []
    for i in range(nsub):
        a0, a1 = lo + i * step, lo + (i + 1) * step
        if not any(dead_by_pin(b, s, a0, a1) for s in slots):
            if alive and abs(alive[-1][1] - a0) < 1e-12:
                alive[-1][1] = a1
            else:
                alive.append([a0, a1])
    frac = sum(y - x for x, y in alive) / (hi - lo)
    return frac, alive


def rows():
    out, seen = [], set()
    pats = ["tree_k5_1*_interior_G1_s*.jsonl", "tree_k5_1*_interior_G1_D2*.jsonl"]
    for pat in pats:
        for f in sorted(glob.glob(os.path.join(A57, "results", pat))):
            if "_s0.jsonl" in f and "_D2" in f:
                continue                              # probe INPUT files, not results
            for ln in open(f):
                ln = ln.strip()
                if not ln:
                    continue
                try:
                    r = json.loads(ln)
                except Exception:
                    continue
                if not r.get("box") or r["id"] in seen:
                    continue
                seen.add(r["id"])
                r["_name"] = "k5_11" if r["id"].startswith("k5_11") else "k5_16"
                r["_level"] = 1 + r["id"].count("_D")
                out.append(r)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nsub", type=int, default=256)
    ap.add_argument("--out", default=os.path.join(BASE, "results", "trim96.json"))
    a = ap.parse_args()
    slots_all = json.load(open(os.path.join(A53, "results", "name_to_slots.json")))
    hh = DELTA / math.sqrt(2.0)
    P = {nm: ([Box(x - hh, x + hh, y - hh, y + hh, 0.0, 0.0) for (x, y) in map(tuple, slots_all[nm])],
              [tuple(p) for p in slots_all[nm]]) for nm in ("k5_11", "k5_16")}

    R = rows()
    per_level = collections.defaultdict(list)
    empty = collections.Counter()
    control = dict(t5_kills=0, fully_dead=0, bad=[])
    gain = []
    recs = []
    for r in R:
        b = Box.from_json(r["box"])
        pins, sl = P[r["_name"]]
        frac, alive = surviving(b, sl, a.nsub)
        cert = str(r.get("cert") or "")
        is_kill = cert.startswith("KILL-BY-LOGIC")
        if is_kill:
            control["t5_kills"] += 1
            if frac == 0.0:
                control["fully_dead"] += 1
            else:
                control["bad"].append(dict(id=r["id"], surviving=round(frac, 6)))
            continue
        per_level[r["_level"]].append(frac)
        if frac == 0.0:
            empty[r["_level"]] += 1
        # a_tight on the trimmed bin: the widest surviving sub-interval is the child that
        # actually gets solved, so the core is recomputed on THAT range.
        c0 = b.core()
        if c0 is not None and alive:
            a_old = pinguard.tight_a(b, math.degrees(2.0 * math.atan(float(c0.tm))))
            wid = max(alive, key=lambda s: s[1] - s[0])
            tb = Box(b.x0, b.x1, b.y0, b.y1, wid[0], wid[1])
            tc = tb.core()
            if tc is not None:
                a_new = pinguard.tight_a(tb, math.degrees(2.0 * math.atan(float(tc.tm))))
                if a_old > 0:
                    gain.append(a_new / a_old)
        recs.append(dict(id=r["id"], level=r["_level"], cls=r["_name"],
                         verdict=cert.split("(")[0].strip(), surviving=round(frac, 6),
                         n_intervals=len(alive)))
    gain.sort()
    def q(v, p):
        return round(v[int(p * (len(v) - 1))], 4) if v else None
    summary = dict(
        boxes=len(R), nsub=a.nsub,
        positive_control=dict(t5_kills=control["t5_kills"], fully_dead=control["fully_dead"],
                              violations=control["bad"],
                              clean=(control["fully_dead"] == control["t5_kills"])),
        surviving_by_level={
            str(L): dict(n=len(v), mean=round(sum(v) / len(v), 4),
                         min=round(min(v), 4), p25=q(sorted(v), 0.25),
                         median=q(sorted(v), 0.5), max=round(max(v), 4),
                         fully_dead=empty.get(L, 0),
                         trimmed_at_all=sum(1 for x in v if x < 1.0))
            for L, v in sorted(per_level.items())},
        new_kills_by_level=dict(empty), new_kills_total=sum(empty.values()),
        a_tight_gain_on_trimmed_bin=dict(n=len(gain), min=q(gain, 0.0), median=q(gain, 0.5),
                                         p90=q(gain, 0.9), max=q(gain, 1.0)))
    json.dump(dict(summary=summary, rows=recs), open(a.out, "w"), indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
