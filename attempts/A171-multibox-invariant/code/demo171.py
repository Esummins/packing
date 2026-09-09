"""A171 demo -- the whole rule on A168's failing S2 node BR139/TRH-25, end to end.

    python demo171.py            (writes results/demo171.json and figs/A168_BR139_TRH-25_*.svg)

Shows, in the order every cascade must use them:  build cores -> assert_invariant (FAILS) ->
normalise -> assert_invariant (PASSES) -> figure -> chord_rows -> misses_cell -> lane.
"""
import json
import os
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BASE = os.path.abspath(os.path.join(HERE, ".."))

import multibox as MB                                          # noqa: E402
import guardline as GL                                         # noqa: E402  READ-ONLY (A144)

SRC = ("attempts/A168-cascade-fable/results/v0_union_boxes/cascade168.jsonl "
       "-- cell l1_153, node BR139/TRH-25, step S2, verdict ALIVE(geometry), budget 8")
ROLES = {
    "H":  (2.5674485, 2.67226625, 2.357813, 2.46263075, 45.0, 60.0),
    "B1": (3.127084, 3.1733821433529026, 1.5015011950128963, 1.5785397484754269, 45.0, 50.625),
    "D":  (3.223006893074939, 3.377084, 3.211365683498047, 3.377084, 0.0, 11.25),
}
TR_CELL = (2.877084, 3.877084, 2.877084, 3.877084)             # the container's top-right unit cell
LINES = [GL.Line("h", Fr(1487939, 500000), tag="top"),         # A168's own recorded rows
         GL.Line("v", Fr(1503477, 500000), tag="right")]


def main():
    t0 = time.time()
    out = dict(source=SRC, roles={k: list(v) for k, v in ROLES.items()}, s=str(MB.S_RAT))

    nd0 = MB.Node(ROLES, name="A168 BR139/TRH-25 as recorded")
    nd0.build_cores()
    r0 = nd0.assert_invariant(raise_on_fail=False)
    out["before"] = dict(ok=r0["ok"], checks={k: v["ok"] for k, v in r0["checks"].items()},
                         failures=r0["failures"], diagnostics=r0["diagnostics"])
    nd0.figure(os.path.join(BASE, "figs", "A168_BR139_TRH-25_before.svg"),
               title="A168 BR139/TRH-25 -- as recorded (unclipped)")
    print(f"BEFORE  ok={r0['ok']}  failures={len(r0['failures'])}")
    for f in r0["failures"]:
        print(f"   {f['check']:24s} [{f['what']}] {f['detail']}")

    nd = MB.Node(ROLES, name="A168 BR139/TRH-25 normalised")
    nd.normalise(nsub=4, refine=3, verbose=True)
    r1 = nd.assert_invariant()
    out["after"] = dict(ok=r1["ok"], checks={k: v["ok"] for k, v in r1["checks"].items()},
                        kept=r1["kept"], sliver_area=r1["sliver_area"],
                        diagnostics=r1["diagnostics"],
                        pieces={k: len(b.pieces) for k, b in nd.boxes.items()},
                        axis_a={k: float(b.core.a) for k, b in nd.boxes.items()},
                        poly_area={k: b.pc.area() for k, b in nd.boxes.items()},
                        stats=nd.stats)
    print(f"AFTER   ok={r1['ok']}  kept=" +
          " ".join(f"{k}={v:.6f}" for k, v in r1["kept"].items()))
    nd.figure(os.path.join(BASE, "figs", "A168_BR139_TRH-25_after.svg"),
              title="A168 BR139/TRH-25 -- after normalise (A171)")

    out["chord_rows"] = nd.chord_rows(LINES)
    out["chord_rows_recorded_by_A168"] = dict(top=dict(beta=2), right=dict(beta=1))
    print("chord rows: " + " ".join(f"{r['orient']}@{r['off_float']:.6f} beta={r['beta']}"
                                    for r in out["chord_rows"]))
    out["misses_cell_TR"] = {k: v["misses"] for k, v in nd.misses_cell(TR_CELL).items()}
    t = time.time()
    lane = nd.lane(TR_CELL, line=None, max_depth=24, max_open=600,
                   deadline=time.time() + 120.0)
    out["lane_TR"] = dict(lane=lane["lane"], leaves=len(lane["leaves"]),
                          open=len(lane["open"]), depth=lane["depth"],
                          reason=lane.get("reason"), seconds=round(time.time() - t, 2))
    print(f"lane(TR cell) = {lane['lane']}  ({len(lane['leaves'])} discharged leaves, "
          f"{len(lane['open'])} open)")
    out["node"] = nd.to_json()
    out["seconds"] = round(time.time() - t0, 2)
    p = os.path.join(BASE, "results", "demo171.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    print(f"wrote {p}  ({out['seconds']} s)")


if __name__ == "__main__":
    main()
