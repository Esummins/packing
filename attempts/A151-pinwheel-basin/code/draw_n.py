"""A151 -- draw the neighbourhood N (its boxes) over the S02 shadow, dilated to s0.

    python draw_n.py [--spec results/spec_A.json ...] [--out results/N_s02.svg]

READ-ONLY on every campaign.
"""
from __future__ import annotations
import argparse, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "attempts", "A116-local-selection-tree", "code"))
sys.path.insert(0, HERE)
import a116lib as A     # noqa: E402
import a151grow as G    # noqa: E402
import draw151 as D     # noqa: E402

RES = os.path.join(BASE, "results")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", default=None)
    ap.add_argument("--out", default=os.path.join(RES, "N_s02.svg"))
    ap.add_argument("--title", default="A151: S02's neighbourhood N over the pinwheel, at s0")
    a = ap.parse_args()
    spec = G.base_spec()
    if a.spec:
        spec.update(json.load(open(a.spec, encoding="utf-8")))
    bodies, nv, s_sh, P = G.bodies_for(spec)
    _, Pe, slots, free = A.anchored("S02", A.S0)
    cfg = {n: [x, y, math.degrees(t)] for n, (x, y, t) in Pe.items()}
    boxes = G.boxlist(spec)
    sub = ("s* = %.6f, s0 = %.6f, slack %.4f. Dashed = N's centre boxes for %s; "
           "tilt window printed per box. " % (s_sh, A.S0, s_sh - A.S0,
                                              ", ".join(b["name"] for b in boxes if b["kind"] == "free"))
           + "spec " + json.dumps({k: {kk: round(vv, 4) for kk, vv in v.items()} for k, v in spec.items()}))
    D.svg(cfg, A.S0, a.title, sub, a.out, boxes=boxes)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
