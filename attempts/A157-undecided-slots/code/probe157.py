"""A157 -- rung-by-rung instrumentation of A141's LANE cover on one (node, slot) cell.

`lane_cover`'s `max_open` bounds only the OPEN frontier, not the number of DISCHARGED leaves, so
raising `depth0` costs memory exponentially.  This probe reports, per rung, the leaf count, the
open count, the wall time and the peak RSS, so the production ladder can be priced.

    python probe157.py --nid c0_Y0076 --slot "TL(0,0)" --rungs 20:1200,21:3000,22:8000
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
for _p in (os.path.join(ROOT, "attempts", "A141-polycore-lane", "code"),
           os.path.join(ROOT, "attempts", "A118-lane-count", "code")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import blas1  # noqa: F401,E402
import numpy as np  # noqa: E402

import polylane as P              # noqa: E402
import lane as LANE               # noqa: E402
from caselp import Box            # noqa: E402


def rss_mb():
    try:
        import ctypes
        import ctypes.wintypes as wt

        class PMC(ctypes.Structure):
            _fields_ = [("cb", wt.DWORD), ("PageFaultCount", wt.DWORD),
                        ("PeakWorkingSetSize", ctypes.c_size_t),
                        ("WorkingSetSize", ctypes.c_size_t),
                        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                        ("PagefileUsage", ctypes.c_size_t),
                        ("PeakPagefileUsage", ctypes.c_size_t)]
        c = PMC()
        c.cb = ctypes.sizeof(c)
        ctypes.windll.psapi.GetProcessMemoryInfo(
            ctypes.windll.kernel32.GetCurrentProcess(), ctypes.byref(c), c.cb)
        return round(c.WorkingSetSize / 1048576.0, 1)
    except Exception:                             # noqa: BLE001
        return None


def build(rec, slot):
    c, i, j = LANE.L.parse_cell(slot)
    pin_b, cond_b = LANE.cframe_boxes(rec, c, i, j)
    pins = P.build_cond([Box(b.x0, b.x1, b.y0, b.y1, b.th0, b.th1) for b in pin_b],
                        tighten=False)
    cond = P.build_cond([Box(b.x0, b.x1, b.y0, b.y1, b.th0, b.th1) for b in cond_b],
                        tighten=False)
    for k, cs in enumerate(cond):
        cs.idx = len(pins) + k
    return pins + cond, [cs.idx for cs in cond], (float(i), float(i) + 1.0,
                                                  float(j), float(j) + 1.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--recs", default=os.path.join(BASE, "results", "recs157.json"))
    ap.add_argument("--nid", required=True)
    ap.add_argument("--slot", required=True)
    ap.add_argument("--rungs", default="20:1200,21:3000,22:8000")
    ap.add_argument("--sample", type=int, default=20000)
    ap.add_argument("--rounds", type=int, default=8)
    a = ap.parse_args()

    recs = json.load(open(a.recs, encoding="utf-8"))
    rec = recs[a.nid]
    conds, meet, cell = build(rec, a.slot)
    rng = np.random.default_rng(1571)
    x0, x1, y0, y1 = P.centre_window(cell, P.S0)
    sm = P._sample_screen(cell, conds, P.S0, rng, a.sample)
    print("cell %s root [%.4f %.4f %.4f %.4f]  sample: lane_lb=%s  cond_lb=%s"
          % (a.slot, x0, x1, y0, y1, sm["lane_lb"],
             [(e["j"], e["can_meet"]) for e in sm.get("cond_lb", [])]), flush=True)
    print("  drawn=%s meeting=%s overlapping=%s free=%s"
          % (sm.get("drawn"), sm.get("meeting"), sm.get("overlapping_some_core"),
             sm.get("free")), flush=True)

    root = Box(x0, x1, y0, y1, 0.0, 90.0)
    for spec in a.rungs.split(","):
        d0, mo = (int(v) for v in spec.split(":"))
        t = time.time()
        cov = P.lane_cover(root, cell, conds, s=P.S0, depth0=d0, max_depth=max(34, d0 + 12),
                           max_open=mo, rounds=a.rounds)
        print("  depth0=%-3d max_open=%-7d lane=%-5s leaves=%-9d open=%-6d %7.1fs rss=%sMB %s"
              % (d0, mo, cov["lane"], len(cov["leaves"]), len(cov["open"]),
                 time.time() - t, rss_mb(), cov.get("reason", "")), flush=True)
        print("      hist=%s" % (cov["hist"],), flush=True)
        if cov["lane"] is not None:
            break


if __name__ == "__main__":
    main()
