"""A140 -- the A118 LANE COUNT for the twelve converged-alive k0 cells, on the four corner cells.

A118's lane verdict depends only on the node's HYPOTHESIS BOXES and the container, never on the LP
support, so a stored A118 record transfers between two records of the same cell (verified: the
A99 alias and the A115 converged record of l1_148 / l1_159 / l1_071 / l1_104 carry identical
boxes).  Three of the twelve (l1_124, l1_153, l1_158) were never in A118's corpus -- A38 has no
node json for them -- so their verdicts are computed here with A118's own `lane.run_cell`,
unchanged and read-only.

    python code/lane140.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
A118 = os.path.join(ROOT, "attempts", "A118-lane-count", "code")
for p in (A118, HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

import numpy as np                                          # noqa: E402
import lane as LANE                                         # noqa: E402
import cells140 as C140                                     # noqa: E402

CORNERS = ["BL(0,0)", "BR(0,0)", "TR(0,0)", "TL(0,0)"]


def main():
    out = {}
    for (name, lvl, src, fn, lanekey, alias) in C140.CELLS:
        meta, d = C140.load_cell(name)
        stored = C140.a118_lane(lanekey) if lanekey else None
        rec = dict(src="A38", nid=name, cls="k0_00", level=lvl,
                   cond=[dict(x0=b["x0"], x1=b["x1"], y0=b["y0"], y1=b["y1"],
                              th0=b["th0"], th1=b["th1"]) for b in d["hyp"]["boxes"]])
        rng = np.random.default_rng(140)
        fresh = {}
        for c in CORNERS:
            try:
                fresh[c] = LANE.run_cell(rec, c, rng, rigorous=True)
            except Exception as e:                            # noqa: BLE001
                fresh[c] = dict(cell=c, verdict="ERROR", error=repr(e)[:200])
        out[name] = dict(
            a118_key=lanekey,
            a118_stored={cc["cell"]: dict(verdict=cc["verdict"], lane_ub=cc.get("lane_ub"),
                                          lane_lb=cc.get("lane_lb"), ncond_pot=cc.get("ncond_pot"))
                         for cc in (stored or {}).get("cells", [])},
            a118_min_lane_ub=(stored or {}).get("min_lane_ub"),
            fresh={c: dict(verdict=v["verdict"], lane_ub=v.get("lane_ub"),
                           lane_lb=v.get("lane_lb"), ncond_pot=v.get("ncond_pot"),
                           kill=v.get("kill"), secs=v.get("secs")) for c, v in fresh.items()})
        print(f"{name:26s} stored " +
              ", ".join(f"{k}={v['verdict']}" for k, v in out[name]["a118_stored"].items())
              + "  ||  fresh " +
              ", ".join(f"{k}={v['verdict']}" for k, v in out[name]["fresh"].items()), flush=True)
    p = os.path.join(BASE, "results", "lane140.json")
    json.dump(out, open(p, "w", encoding="utf-8"), indent=1)
    print("wrote", p)


if __name__ == "__main__":
    main()
