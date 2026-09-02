"""
A57 slack-core grid (A63 route (b), hybrid backbone).

rho(C) = 1/2 - a*(cos th + sin th) at the PINS (they bind; the interior cover box has rho ~ 0.127).
With pin core half-side a = 1/2 - delta and the library's tm, rho = delta - tm + O(tm^2).
A63 B' transfers a PASS at side s" to every packing side m with (s"/m - 1)*A < rho, A = 5/2, so
one certified side covers the half-open slab  ( s"/(1 + rho/A),  s" ].

This module emits the grid of sides covering [3.82, s0] and, per side, re-runs the pinguard
C-check: the cover box and the pins BOTH move with s, so which children are contradictory
(free logic kills) is an s-dependent fact and must be recomputed once per side.  Pure geometry,
no LP.
"""
import argparse, json, math, os, sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from caselp import Box, Hyp
from pinguard import classify
from tree57 import cover, ghost_placements, ghost_dist

S0 = F(969271, 250000)
S_LO = F(191, 50)              # 3.82
A_MAX = F(5, 2)
TM = F(1, 33554432)            # the library's core tilt
A53 = os.path.abspath(os.path.join(HERE, "..", "..", "A53-simple-strata"))


def rho_of(delta):
    """exact rho for a pin core of half-side 1/2 - delta at tilt tm."""
    a = F(1, 2) - F(delta)
    c = (1 - TM * TM) / (1 + TM * TM)
    s = 2 * TM / (1 + TM * TM)
    return F(1, 2) - a * (c + s)


def grid_sides(delta, safety=F(95, 100)):
    """sides s_1 = s0 > s_2 > ... covering (.., s0] down past S_LO.
    Step uses `safety` * rho/A so consecutive slabs OVERLAP rather than abut."""
    rho = rho_of(delta)
    step = rho / A_MAX * safety
    sides, s = [], S0
    while True:
        lo = s / (1 + rho / A_MAX)          # the slab this side actually covers
        sides.append((s, lo))
        if lo <= S_LO:
            break
        s = s / (1 + step)
        s = F(math.floor(float(s) * 250000), 250000)   # keep sides on the 1/250000 grid
        if len(sides) > 500:
            raise RuntimeError("grid did not terminate")
    return rho, sides


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--delta", default="1e-2")
    ap.add_argument("--name", default="k5_11")
    ap.add_argument("--w", type=float, default=0.15)
    ap.add_argument("--nth", type=int, default=8)
    ap.add_argument("--cw", type=float, default=0.6)
    ap.add_argument("--ccheck", action="store_true", help="re-run the pinguard C-check per side")
    a = ap.parse_args()

    delta = F(a.delta) if "/" in a.delta else F(str(float(a.delta)))
    rho, sides = grid_sides(delta)
    out = dict(delta=str(delta), rho=str(rho), rho_float=float(rho),
               slab_rel_width=float(rho / A_MAX), n_sides=len(sides),
               window=[str(S_LO), str(S0)],
               sides=[dict(s=str(s), s_float=float(s), covers_lo=float(lo)) for s, lo in sides])
    lo_min = min(float(lo) for _, lo in sides)
    out["covers_down_to"] = lo_min
    out["window_covered"] = lo_min <= float(S_LO)
    print(json.dumps({k: v for k, v in out.items() if k != "sides"}, indent=1))
    for i, (s, lo) in enumerate(sides, 1):
        print("  side %d: s = %-22s (%.9f)  covers (%.9f, %.9f]" %
              (i, str(s), float(s), float(lo), float(s)))

    if a.ccheck:
        slots0 = [tuple(p) for p in json.load(open(os.path.join(A53, "results", "name_to_slots.json")))[a.name]]
        h = float(delta) / math.sqrt(2.0)
        G = ghost_placements()
        out["ccheck"] = []
        for i, (s, lo) in enumerate(sides, 1):
            sf = float(s)
            # slots are affine in s: alpha + beta*s with beta = 1 for the R-anchored ones
            sl = [(x if x < 1.0 else (x - float(S0) + sf) if x > 2.0 else x,
                   y if y < 1.0 else (y - float(S0) + sf) if y > 2.0 else y) for (x, y) in slots0]
            pins = [Box(x - h, x + h, y - h, y + h, 0.0, 0.0) for (x, y) in sl]
            c0 = 0.5 + a.cw
            rect = (c0, sf - c0, c0, sf - c0)
            boxes, bad, grid = cover(rect, sf, a.w, a.nth, 0.34)
            cls = [classify(b, pins, sl)[0] for b in boxes]
            rec = dict(side=str(s), cover=len(boxes), uncoverable=len(bad),
                       contradictory=cls.count("contradictory"), ok=cls.count("ok"),
                       parent=cls.count("parent"))
            out["ccheck"].append(rec)
            print("  C-check side %d: cover=%d  free(logic)=%d  ok=%d  parent=%d  uncoverable=%d"
                  % (i, rec["cover"], rec["contradictory"], rec["ok"], rec["parent"], rec["uncoverable"]))
    json.dump(out, open(os.path.join(HERE, "..", "results", f"grid_{a.name}_d{a.delta}.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
