"""A144 T1 -- unit tests of the two exact primitives, against brute force.

  (T1a) `chord_float` against a direct numerical measurement of |l n Q| (dense sampling of the
        line, no formula shared with (CH)).
  (T1b) `minchord_box` against a dense grid minimum over the box, on RANDOM boxes covering the
        regimes that matter: V < a, V = a, V > a; zero-width and wide tilt bins; bins that
        straddle 0, 45 and 90 degrees.  The exact bound must never exceed the grid minimum, and
        must not be loose by more than the grid's own resolution.

    set PYTHONDONTWRITEBYTECODE=1 && python code/t1_test.py
"""
import json
import math
import os
import sys
from fractions import Fraction as Fr

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import guardline as G                                                   # noqa: E402
from caselp import Box                                                  # noqa: E402


def measured_chord(a, cx, cy, th, line, n=400001):
    """|l n Q| by direct sampling of the line -- shares no algebra with (CH)."""
    lo, hi = -3.0, 3.0
    u = np.linspace(lo, hi, n)
    if line.orient == "h":
        px, py = cx + u, np.full(n, line.foff)
    else:
        px, py = np.full(n, line.foff), cy + u
    dx, dy = px - cx, py - cy
    c, s = math.cos(th), math.sin(th)
    inside = (np.abs(dx * c + dy * s) <= a) & (np.abs(-dx * s + dy * c) <= a)
    return float(inside.sum()) * (hi - lo) / (n - 1)


def main():
    rng = np.random.default_rng(3)
    # ---------------------------------------------------------------- (T1a)
    worst_a, n_a = 0.0, 0
    for _ in range(400):
        th = rng.uniform(0, math.pi / 2)
        cy = rng.uniform(0.5, 3.4)
        off = cy + rng.uniform(-0.85, 0.85)
        L = G.Line("h", Fr(round(off * G.LDEN), G.LDEN), "test")
        f = G.chord_float(0.5, th, L.foff - cy)
        m = measured_chord(0.5, 1.9, cy, th, L)
        worst_a = max(worst_a, abs(f - m))
        n_a += 1
    # vertical lines too
    for _ in range(200):
        th = rng.uniform(0, math.pi / 2)
        cx = rng.uniform(0.5, 3.4)
        off = cx + rng.uniform(-0.85, 0.85)
        L = G.Line("v", Fr(round(off * G.LDEN), G.LDEN), "test")
        f = G.chord_float(0.5, th, L.foff - cx)
        m = measured_chord(0.5, cx, 1.9, th, L)
        worst_a = max(worst_a, abs(f - m))
        n_a += 1

    # ---------------------------------------------------------------- (T1b)
    regimes = [(0.0, 0.0), (0.0, 90.0), (0.0, 12.0), (78.0, 90.0), (30.0, 60.0),
               (40.0, 50.0), (44.9, 45.1), (0.0, 45.0), (45.0, 90.0), (82.37, 90.0),
               (10.0, 11.0), (60.0, 61.0)]
    worst_over, worst_slack, n_b, fails = 0.0, 0.0, 0, []
    for (th0, th1) in regimes:
        for _ in range(40):
            cx = rng.uniform(0.8, 3.0)
            cy = rng.uniform(0.8, 3.0)
            wx = rng.choice([0.0, 0.01, 0.07, 0.14])
            wy = rng.choice([0.0, 0.01, 0.07, 0.14])
            b = Box(cx, cx + wx, cy, cy + wy, th0, th1)
            off = cy + rng.uniform(-1.0, 1.0)
            L = G.Line("h", Fr(round(off * G.LDEN), G.LDEN), "test")
            mc = G.minchord_box(b, L, a=G.HALF)
            # dense grid minimum of the TRUE chord over the box
            ny = 41 if wy > 0 else 1
            nt = 121 if th1 > th0 else 1
            YS = np.linspace(b.y0, b.y1, ny)
            TS = np.radians(np.linspace(b.th0, b.th1, nt))
            Y, T = np.meshgrid(YS, TS, indexing="ij")
            ch = G.chord_many(0.5, T.ravel(), L.foff - Y.ravel())
            gmin = float(ch.min())
            over = mc["lo_float"] - gmin              # must be <= 0 (up to grid resolution)
            worst_over = max(worst_over, over)
            worst_slack = max(worst_slack, gmin - mc["lo_float"])
            n_b += 1
            if over > 1e-9:
                fails.append(dict(box=b.to_json(), off=L.foff, exact=mc["lo_float"],
                                  grid_min=gmin, over=over, terms=mc["terms"]))
    out = dict(T1a=dict(cases=n_a, worst_abs_error_vs_measured=worst_a,
                        ok=bool(worst_a < 2e-5)),
               T1b=dict(cases=n_b, worst_exceedance_over_grid_min=worst_over,
                        worst_slack_below_grid_min=worst_slack,
                        ok=bool(worst_over <= 1e-9), failures=fails[:5]))
    out["all_ok"] = bool(out["T1a"]["ok"] and out["T1b"]["ok"])
    json.dump(out, open(os.path.join(BASE, "results", "t1_test144.json"), "w",
                        encoding="utf-8"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
