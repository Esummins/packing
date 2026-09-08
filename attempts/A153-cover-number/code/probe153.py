"""A153 -- the tilt-bin probe for Lemma TC.

The per-tilt TC cover number is only a *conditional-at-a-point* statement.  A sound tilt-coherent
leaf has to hold on a whole tilt bin: on a bin of half-width delta the piece side must satisfy
d(1 + delta) < 1, so the pieces shrink as the bin widens.  This asks, for a node where the
single-tilt number reached a kill, HOW FINE the tilt branch would have to be for the kill to be
sound -- i.e. the largest delta at which the window-robust cover is still below the budget, and how
much of the node's tilt window that bin covers.

Writes results/probe153_<node>.json.  READ-ONLY on every campaign.
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
for _p in (HERE, os.path.join(os.path.abspath(os.path.join(BASE, "..")),
                              "A142-a57-review-gallery", "code")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import cover153 as C                                                  # noqa: E402
import run153 as R                                                    # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--node", required=True)
    ap.add_argument("--camp", default="A57")
    ap.add_argument("--budget", type=int, default=5)
    ap.add_argument("--centre-deg", type=float, default=None)
    ap.add_argument("--deltas-deg", default="0,0.25,0.5,1,2,4")
    ap.add_argument("--nsweep", type=int, default=19)
    a = ap.parse_args()
    import gallery142 as G142
    d, path = G142.load_node(a.camp, a.node)
    boxes = d["hyp"]["boxes"]
    reg, obst, onames, kinds = C.region_of(boxes)
    mask = ~reg.blocked
    frames, win = R.tc_frames(boxes)
    lo, hi = win
    out = dict(node=a.node, camp=a.camp, record=path, budget=a.budget,
               tilt_window_deg=[math.degrees(lo), math.degrees(hi)],
               area_open=reg.area_open(), area_green=reg.area_green(), sweep=[], bins=[])
    for k in range(a.nsweep):
        th = lo + (hi - lo) * k / (a.nsweep - 1.0)
        r = C.tc_cover(reg, mask, th, 0.0, exact_limit=a.budget + 3)
        r["floor_tc"] = len(C.separated_floor_tc(reg, mask, th))
        r["floor_tc_green"] = len(C.separated_floor_tc(reg, reg.green, th))
        out["sweep"].append({k2: v for k2, v in r.items() if k2 != "pieces"})
        print(f"  t={math.degrees(th):8.4f} deg  K={r['K']} side={r['side']:.4f} "
              f"cover={r.get('exact') or r['ub']} floor={r['floor_tc']} "
              f"floor_green={r['floor_tc_green']}", flush=True)
    c0 = math.radians(a.centre_deg) if a.centre_deg is not None else hi
    for dd in [float(x) for x in a.deltas_deg.split(",")]:
        dl = math.radians(dd)
        r = C.tc_cover(reg, mask, c0, dl, exact_limit=a.budget + 3)
        cov = r.get("exact") or r["ub"]
        out["bins"].append(dict(centre_deg=math.degrees(c0), delta_deg=dd, K=r["K"],
                                side=r["side"], cover=cov, lb=r["lb_indep"],
                                kills=bool(cov < a.budget)))
        print(f"  bin +-{dd:5.2f} deg about {math.degrees(c0):.3f}: K={r['K']} "
              f"side={r['side']:.4f} cover={cov} "
              f"{'KILL (conditional, tilt-coherent)' if cov < a.budget else ''}", flush=True)
    p = os.path.join(BASE, "results", f"probe153_{a.node}.json")
    json.dump(out, open(p, "w", encoding="utf-8"), indent=1)
    print("wrote", p)


if __name__ == "__main__":
    main()
