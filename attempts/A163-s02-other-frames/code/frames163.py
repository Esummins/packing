"""A163 T1 -- state the three frames explicitly and check the re-framing is exact.

Writes results/frames163.json: per class the pins (with their affine slot cells alpha + beta*s and
the delta-core half-width), the free boxes, the dropped squares, and -- the soundness check that the
re-framing is legitimate -- the worst deviation between the S02 shadow's own slot squares and the
pin cores of each class at the shadow's own side s* (a pin is only a valid clause of the hypothesis
if the shadow it is meant to cover actually satisfies it).

    python frames163.py

READ-ONLY on every campaign and prior attempt.
"""
from __future__ import annotations

import json, math, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib163 as L                      # noqa: E402
import a116lib as A                     # noqa: E402


def main():
    s_sh, P, slots, free = A.anchored(TAG := "S02", A.S0)
    s_star, Pstar, _, _ = A.shadow_poses("S02")
    out = dict(when=time.strftime("%Y-%m-%dT%H:%M:%S"), tag="S02", s_star=s_star, s0=float(A.S0),
               pin_slack=A.PIN_SLACK, slot_squares=list(L.SLOTS7), rattlers=list(L.RATTLERS),
               loadbearing=list(A.LOADBEARING["S02"]) + ["BR(0,1)"], frames={})
    for cls in ("k5_11",) + L.FRAMES:
        pins, boxes, dropped = L.frame(cls)
        rows, worst = [], 0.0
        for p in pins:
            ax, ay = A.slot_affine(p)
            cx, cy = ax[0] + ax[1] * s_star, ay[0] + ay[1] * s_star
            gx, gy, gt = Pstar[p]
            d = max(abs(gx - cx), abs(gy - cy))
            worst = max(worst, d)
            rows.append(dict(name=p, alpha=[ax[0], ay[0]], beta=[ax[1], ay[1]],
                             cell_at_s_star=[cx, cy], shadow_pose=[gx, gy, math.degrees(gt)],
                             dev=d, inside_core=bool(d <= A.PIN_SLACK)))
        out["frames"][cls] = dict(pins=rows, n_pins=len(pins), boxes=boxes, dropped=dropped,
                                  worst_pin_dev=worst,
                                  shadow_in_all_cores=bool(worst <= A.PIN_SLACK))
        print("%-7s pins %-58s boxes %-28s dropped %-20s worst pin dev %.2e  %s"
              % (cls, " ".join(pins), " ".join(boxes), " ".join(dropped), worst,
                 "OK" if worst <= A.PIN_SLACK else "PIN CORE VIOLATED"))

    # the re-framing itself: every A160 entry must map into both frames with identical boxes
    ents = L.entries()
    chk = []
    for cls in L.FRAMES:
        ok = 0
        for e in ents:
            bodies, nv, s_sh2, _ = L.bodies_in_frame(e, cls)
            src = L.entry_boxes(e)
            dev = 0.0
            for b in bodies:
                if b.kind != "free":
                    continue
                w = src[b.name]
                dev = max(dev, abs(b.x0 - w["x"][0]), abs(b.x1 - w["x"][1]),
                          abs(b.y0 - w["y"][0]), abs(b.y1 - w["y"][1]),
                          abs(b.t0 - w["t"][0]), abs(b.t1 - w["t"][1]))
            assert dev == 0.0, (e["id"], cls, dev)
            ok += 1
        chk.append(dict(cls=cls, entries=ok, box_deviation=0.0))
        print("%-7s re-framed %d of %d A160 box sets, box deviation 0.0 (geometry identical)"
              % (cls, ok, len(ents)))
    out["reframe_check"] = chk
    out["n_entries"] = len(ents)
    p = os.path.join(L.RES, "frames163.json")
    json.dump(out, open(p, "w", encoding="utf-8"), indent=1)
    print("wrote", p)


if __name__ == "__main__":
    main()
