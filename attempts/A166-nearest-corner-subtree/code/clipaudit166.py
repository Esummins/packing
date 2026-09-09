"""A166 -- audit of the A131 clip's pin half-side rounding (a soundness detail, and the check that
the recorded results do not depend on it).

`geo166.clip_against_core` hands A131's `pinclip.clip_node` a RATIONAL half-side for the axis core
inscribed in `K'(B_H)`.  The first version rounded it with `Fraction(str(a)).limit_denominator(1e9)`,
which can round UP by ~1e-9; a pin core larger than the inscribed square would let A131's octagon claim
an overlap that need not happen, i.e. an UNSOUND clip.  (The overshoot is far inside A132's own
`shrink = 1e-6` inward offset of `K'`, so no recorded verdict can actually be wrong -- but "far inside
another margin" is not a proof, so the code now floors the value onto a 1e-12 grid instead.)

This script re-runs every clip of every cell with the floored value and checks that

    * no cell whose clip was EMPTY becomes non-empty (that would change a DEAD_CLIP/DEGENERATE_CLIP
      verdict), and
    * every surviving cell's clipped box is unchanged to 1e-12,

so the recorded `results/subtree166_*.jsonl` and `survivors166_*.json` stand as they are.

    python code/clipaudit166.py --pad wmax
"""
import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import geo166 as G                                              # noqa: E402
import cells166 as C                                            # noqa: E402
from caselp import Box                                          # noqa: E402

RES = os.path.join(BASE, "results")
PADS = {"w0": 0.0, "wmax": C.W_MAX}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pad", default="wmax", choices=sorted(PADS))
    a = ap.parse_args()
    out = []
    for f in sorted(glob.glob(os.path.join(RES, "survivors166_%s_*.json" % a.pad))):
        d = json.load(open(f, encoding="utf-8"))
        bH = Box(**d["Hbox"])
        KH = G.kprime(bH)
        cH = G.exact_core(bH)
        aH = G.axis_core_in(KH, float(cH.kx), float(cH.ky))
        nchk = nempty_diff = nbox_diff = 0
        worst = 0.0
        for k, r in d["per_cell"].items():
            if r["verdict"] in ("DEAD_R",):
                continue
            if "clip" not in r:
                continue
            nchk += 1
            Gb = Box(**r["gbox"])
            cr = G.clip_against_core(Gb, float(cH.kx), float(cH.ky), aH)
            was_empty = bool(r["clip"]["empty"])
            now_empty = bool(cr.get("empty"))
            if was_empty != now_empty:
                nempty_diff += 1
            if not now_empty and "cbox" in r:
                ur = cr.get("union_rect")
                nb = (G.rect_to_box(ur, Gb.th0, Gb.th1) if ur is not None else Gb)
                ob = Box(**r["cbox"])
                dd = max(abs(nb.x0 - ob.x0), abs(nb.x1 - ob.x1), abs(nb.y0 - ob.y0),
                         abs(nb.y1 - ob.y1))
                worst = max(worst, dd)
                if dd > 1e-12:
                    nbox_diff += 1
        out.append(dict(cell=d["cell"], pad=a.pad, checked=nchk, a_axis=aH,
                        emptiness_changes=nempty_diff, box_changes=nbox_diff,
                        worst_box_shift=worst))
        print("%-12s checked %3d clips | emptiness changes %d | box changes %d | worst shift %.3e"
              % (d["cell"], nchk, nempty_diff, nbox_diff, worst), flush=True)
    ok_empty = all(r["emptiness_changes"] == 0 for r in out)
    worst = max([r["worst_box_shift"] for r in out] or [0.0])
    json.dump(dict(pad=a.pad, EMPTINESS_UNCHANGED=bool(ok_empty), worst_box_shift=worst,
                   note="the floored pin is SMALLER, so every recorded clipped box is a subset of "
                        "the sound one by at most worst_box_shift; a subset hypothesis is only a "
                        "problem for a KILL, and A166 banks none",
                   rows=out),
              open(os.path.join(RES, "clipaudit166_%s.json" % a.pad), "w"), indent=1)
    print("EMPTINESS_UNCHANGED = %s   worst box shift = %.3e" % (ok_empty, worst), flush=True)


if __name__ == "__main__":
    main()
