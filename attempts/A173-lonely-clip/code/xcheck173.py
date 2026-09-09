"""A173 -- cross-check the multibox port of A169's Theorem B against A168's `resume168.lonely_box`.

500 random corner-meeter boxes per run (all four corners, tilt sub-bins of the widths A168 uses).
The two implementations must return IDENTICAL verdicts.  A168 is imported READ-ONLY and only here
and in the test; `multibox.lonely_local` never imports it at runtime.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ATT, "A171-multibox-invariant", "code"))

import multibox as MB                                          # noqa: E402
import numpy as np                                             # noqa: E402
from caselp import Box                                         # noqa: E402


def a168():
    """import A168's resume168 (READ-ONLY) for the cross-check only."""
    for p in (os.path.join(ATT, "A168-cascade-fable", "code"),):
        if p not in sys.path:
            sys.path.insert(0, p)
    import resume168 as R168                                    # noqa: E402
    return R168


def random_boxes(n, seed=173):
    """boxes that a corner meeter cover actually produces: a centre rect of width 0.02-0.25 inside
    the corner reach window, and a tilt sub-bin of width 0-11.25 deg."""
    rng = np.random.default_rng(seed)
    s = float(MB.S_RAT)
    reach = 1.0 + float(MB.W0_RAT) + 1.0 / np.sqrt(2.0)
    out = []
    for _ in range(n):
        corner = MB.CORNERS[rng.integers(4)]
        wx = float(rng.uniform(0.005, 0.25))
        wy = float(rng.uniform(0.005, 0.25))
        lx = float(rng.uniform(0.4, reach))
        ly = float(rng.uniform(0.4, reach))
        x0, x1 = lx, lx + wx
        y0, y1 = ly, ly + wy
        if corner in ("BR", "TR"):
            x0, x1 = s - x1, s - x0
        if corner in ("TL", "TR"):
            y0, y1 = s - y1, s - y0
        th0 = float(rng.uniform(0.0, 88.0))
        th1 = th0 + float(rng.choice([0.0, 1.40625, 2.8125, 5.625, 11.25]))
        out.append((Box(x0, x1, y0, y1, th0, min(th1, 90.0)), corner))
    return out


def run(n=500, seed=173):
    R168 = a168()
    boxes = random_boxes(n, seed)
    t0 = time.time()
    bad, ntrue = [], 0
    for i, (b, corner) in enumerate(boxes):
        a, da = R168.lonely_box(b, corner)
        m, dm = MB.lonely_box(b, corner)
        ntrue += int(a)
        if a != m or {k: da[k] for k in ("W", "S", "NE")} != {k: dm[k] for k in ("W", "S", "NE")}:
            bad.append(dict(i=i, corner=corner, box=[b.x0, b.x1, b.y0, b.y1, b.th0, b.th1],
                            a168=[a, da], multibox=[m, dm]))
    dt = time.time() - t0
    return dict(n=n, seed=seed, identical=(not bad), n_lonely=ntrue, mismatches=bad[:10],
                n_mismatch=len(bad), seconds=round(dt, 2),
                c_widen_a168=str(R168.C_RAT), c_widen_multibox=str(MB.C_WIDEN),
                c_equal=(R168.C_RAT == MB.C_WIDEN))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=500)
    ap.add_argument("--seed", type=int, default=173)
    ap.add_argument("--json", default=os.path.join(HERE, "..", "results", "xcheck173.json"))
    a = ap.parse_args()
    r = run(a.n, a.seed)
    print(json.dumps({k: v for k, v in r.items() if k != "mismatches"}, indent=1))
    for m in r["mismatches"]:
        print("  MISMATCH", m)
    os.makedirs(os.path.dirname(os.path.abspath(a.json)), exist_ok=True)
    with open(os.path.abspath(a.json), "w", encoding="utf-8") as fh:
        json.dump(r, fh, indent=1)
    sys.exit(0 if r["identical"] and r["c_equal"] else 1)
