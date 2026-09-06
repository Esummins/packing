"""A96 route (B): a TIGHT common-inscribed-square core for A57's existing KILL-BY-LOGIC leaf.

MEASUREMENT ONLY -- this script does not write into A57 and does not change any verdict.

THE LEAF IS UNCHANGED.  A57's rule is: K_B is contained in every unit square whose (centre,
tilt) lies in B; K_P is contained in the pinned square; if K_B meets K_P the hypotheses are
contradictory and the box is empty by logic (T5, Lean `core_meet_same_square`).  Only the
computation of K_B's half-side changes, so no new leaf kind, no new Lean, and nothing in the
frozen verifier chain is touched.

THE OLD BOUND (caselp.Box.core):

    a_old = (1/2 - hd) / (1 + (t1 - t0)),   hd = half-DIAGONAL of the centre box

is conservative twice over.  Write the core as the square centred at the box-centre k with tilt
theta_m and half-side a; K subset Q(c, theta) for every (c, theta) in B iff every corner of K
lies in Q, i.e. for all d = k - c and all phi = theta_m - theta,

    | R(-theta) d + a R(phi) s |_inf <= 1/2   for the four sign vectors s.

Bounding the two terms separately and taking worst cases:

    a_tight = (1/2 - h * M_c) / M_t
      h   = half-WIDTH of the (square) centre box
      M_c = max over theta in [theta0, theta1] of (|cos theta| + |sin theta|)
      M_t = max over phi in [theta0 - theta_m, theta1 - theta_m] of (|cos phi| + |sin phi|)

Both factors improve on the old bound:
  * the old numerator uses hd = h*sqrt(2), which is M_c = sqrt(2) -- attained ONLY when 45 deg
    lies in the box's tilt range; away from 45 deg, M_c is as low as 1;
  * the old denominator 1 + (t1 - t0) over-states M_t, because a t-width w corresponds to a
    theta-half-width of at most w radians and cos(x) + sin(x) <= 1 + x.

Since (kx, ky, theta_m) are UNCHANGED and a_tight >= a_old, the new core CONTAINS the old one.
That is what makes the positive control hold by construction: any box the old rule killed, the
new rule also kills.  The control is still run, because a construction argument that is not
executed is a claim, not a check.

Float is used for the yield sweep.  A deployed version must recompute a_tight with outward
rational rounding (Fraction, round M_c and M_t UP, round the numerator DOWN) so the emitted core
is never larger than the true common inscribed square; the sweep applies --margin to stay clear
of the boundary so the counts here are not inflated by float slop.
"""
import argparse, glob, json, math, os, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
A57 = os.path.abspath(os.path.join(BASE, "..", "A57-shadow-trees"))
A53 = os.path.abspath(os.path.join(BASE, "..", "A53-simple-strata"))
sys.path.insert(0, os.path.join(A57, "code"))
import caselp
from caselp import Box, Core
from pinguard import classify
PIN_DELTA = 1e-2


def _cs(deg):
    r = math.radians(deg)
    return abs(math.cos(r)) + abs(math.sin(r))


def max_cs(d0, d1):
    """max of |cos| + |sin| over [d0, d1] degrees (both endpoints and 45 deg mod 90)."""
    best = max(_cs(d0), _cs(d1))
    k = math.floor(d0 / 90.0)
    while k * 90.0 + 45.0 <= d1 + 1e-12:
        c = k * 90.0 + 45.0
        if c >= d0 - 1e-12:
            best = max(best, _cs(c))
        k += 1
    return best


def tight_a(b, theta_m_deg):
    """The tight common-inscribed half-side for box b with core tilt theta_m."""
    hx = 0.5 * (b.x1 - b.x0)
    hy = 0.5 * (b.y1 - b.y0)
    h = max(hx, hy)                       # the centre box is square in this cover
    Mc = max_cs(b.th0, b.th1)
    phi0, phi1 = b.th0 - theta_m_deg, b.th1 - theta_m_deg
    lo, hi = min(phi0, phi1), max(phi0, phi1)
    Mt = max(_cs(lo), _cs(hi))
    if lo <= 0.0 <= hi:
        Mt = max(Mt, 1.0)
    return (0.5 - h * Mc) / Mt


class TightBox(Box):
    """The same box with the same core CENTRE and TILT, only a larger half-side."""

    def __init__(self, b, margin=0.0):
        Box.__init__(self, b.x0, b.x1, b.y0, b.y1, b.th0, b.th1)
        self._base = b.core()
        self._margin = margin

    def core(self):
        c = self._base
        if c is None:
            return None
        tm_deg = math.degrees(2.0 * math.atan(float(c.tm)))
        a = tight_a(self, tm_deg) - self._margin
        if a <= 0:
            return None
        from fractions import Fraction as F
        return Core(c.kx, c.ky, c.tm, F(int(a * 10 ** 9), 10 ** 9), self)


def rows():
    out, seen = [], set()
    pats = ["tree_k5_1*_interior_G1_s*.jsonl", "tree_k5_1*_interior_G1_D2*.jsonl"]
    for pat in pats:
        for f in sorted(glob.glob(os.path.join(A57, "results", pat))):
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
    ap.add_argument("--margin", type=float, default=1e-9,
                    help="shrink a_tight by this before testing, so float slop cannot create a kill")
    a = ap.parse_args()
    slots_all = json.load(open(os.path.join(A53, "results", "name_to_slots.json")))
    hh = PIN_DELTA / math.sqrt(2.0)
    pinsets = {}
    for nm in ("k5_11", "k5_16"):
        sl = [tuple(p) for p in slots_all[nm]]
        pinsets[nm] = ([Box(x - hh, x + hh, y - hh, y + hh, 0.0, 0.0) for (x, y) in sl], sl)

    R = rows()
    control = dict(total=0, still_killed=0, lost=[])
    gained = collections.Counter()
    open_by_lvl = collections.Counter()
    ratio = []
    newkills = []
    for r in R:
        b = Box.from_json(r["box"])
        pins, sl = pinsets[r["_name"]]
        old = classify(b, pins, sl)[0]
        tb = TightBox(b, a.margin)
        c0, c1 = b.core(), tb.core()
        if c0 is not None and c1 is not None:
            ratio.append(float(c1.a) / float(c0.a))
        new = classify(tb, pins, sl)[0]
        cert = str(r.get("cert") or "")
        if cert.startswith("KILL-BY-LOGIC"):
            control["total"] += 1
            if new == "contradictory":
                control["still_killed"] += 1
            else:
                control["lost"].append(dict(id=r["id"], old=old, new=new))
        else:
            open_by_lvl[r["_level"]] += 1
            if new == "contradictory" and old != "contradictory":
                gained[r["_level"]] += 1
                newkills.append(dict(id=r["id"], level=r["_level"], cls=r["_name"],
                                     status=cert.split("(")[0].strip(),
                                     a_old=float(c0.a) if c0 else None,
                                     a_new=float(c1.a) if c1 else None))
    ratio.sort()
    out = dict(
        boxes=len(R),
        positive_control=dict(known_logic_kills=control["total"],
                              still_killed=control["still_killed"],
                              lost=control["lost"],
                              clean=(control["still_killed"] == control["total"])),
        a_ratio_new_over_old=dict(min=round(ratio[0], 4), median=round(ratio[len(ratio) // 2], 4),
                                  max=round(ratio[-1], 4),
                                  below_1=sum(1 for x in ratio if x < 1.0)),
        open_boxes_by_level=dict(open_by_lvl),
        new_kills_by_level=dict(gained),
        new_kills_total=sum(gained.values()),
        new_kills=newkills)
    json.dump(out, open(os.path.join(BASE, "results", "core96.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "new_kills"}, indent=1))


if __name__ == "__main__":
    main()
