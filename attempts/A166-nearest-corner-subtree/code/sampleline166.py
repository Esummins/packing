"""A166 -- the convention's drawn -> tested -> hits line for the headline claim, tested DIRECTLY on the
poses rather than through the box cover.

The claim, for a cell whose branch (a) is empty: *there is no configuration in which `H` has a pose in
`B_H` and TWO squares OTHER than `H` meet `int B_TR^w`.*  The box-level proof is in `notes/method.md`
sec 2; this is its sampled counterpart, and it does not use the cover at all:

    draw  h  uniformly in B_H, keep it if Q(h) is inside the container;
    draw  q1, q2  uniformly over the corner-meeting zone Z(w) x [0, 90) (the ONLY constraint the cover
          derives), keep each if Q is inside the container and meets int B_TR^w;
    a HIT is a triple with Q(h), Q(q1), Q(q2) pairwise interior-disjoint.

Its own from-scratch SAT (`check166.sat_depth`), its own sampling.  0 hits is EVIDENCE for the claim,
never a proof; a single hit would REFUTE the attempt's headline and is reported loudly.

The same line is run on a control cell whose branch (a) is NOT empty, so that a zero count is known not
to be an artefact of the sampler.

    python code/sampleline166.py --n 400000
"""
import argparse
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import check166 as K                                          # noqa: E402  (its own SAT)

RES = os.path.join(BASE, "results")
S0 = K.S0


def run(cell, pad, n, rng, log):
    a_w = 1.0 + (K.W_MAX if pad == "wmax" else 0.0)
    d = json.load(open(os.path.join(RES, "survivors166_%s_%s.json" % (pad, cell)),
                      encoding="utf-8"))
    corner = d["corner"]
    rect = K.corner_rect(corner, a_w)
    b = d["Hbox"]
    zlo, zhi = 0.5, a_w + math.sqrt(0.5)

    def draw_meeter():
        for _ in range(60):
            u = rng.uniform(zlo, zhi)
            v = rng.uniform(zlo, zhi)
            th = rng.uniform(0.0, 90.0)
            # local -> global (the inverse of check166.to_local)
            if corner == "BL":
                x, y = u, v
            elif corner == "BR":
                x, y = S0 - v, u
            elif corner == "TR":
                x, y = S0 - u, S0 - v
            else:
                x, y = v, S0 - u
            if not K.in_container(x, y, th):
                continue
            if K.sat_depth(K.verts(x, y, th), K.rect_poly(rect)) <= 0.0:
                continue
            return (x, y, th)
        return None

    drawn = kept_h = pairs = hits = 0
    hit = None
    for _ in range(n):
        drawn += 1
        h = (rng.uniform(b["x0"], b["x1"]), rng.uniform(b["y0"], b["y1"]),
             rng.uniform(b["th0"], b["th1"]))
        if not K.in_container(*h):
            continue
        kept_h += 1
        q1 = draw_meeter()
        if q1 is None:
            continue
        if K.sat_depth(K.verts(*h), K.verts(*q1)) > 0.0:
            continue
        q2 = draw_meeter()
        if q2 is None:
            continue
        pairs += 1
        if K.sat_depth(K.verts(*h), K.verts(*q2)) > 0.0:
            continue
        if K.sat_depth(K.verts(*q1), K.verts(*q2)) > 0.0:
            continue
        hits += 1
        if hit is None:
            hit = dict(h=h, q1=q1, q2=q2)
    log("%-12s pad %-4s drawn %d, H admissible %d, (H, q1, q2) triples tested %d, HITS %d%s"
        % (cell, pad, drawn, kept_h, pairs, hits, ("  <-- REFUTATION" if hits else "")))
    return dict(cell=cell, pad=pad, drawn=drawn, h_admissible=kept_h, triples=pairs, hits=hits,
                witness=hit, branch_a_survivors=d["n_survivors"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pad", default="wmax")
    ap.add_argument("--n", type=int, default=200000)
    ap.add_argument("--cells", default="l1_124,l1_153,l1_158,l1_159")
    ap.add_argument("--controls", default="l1_071,l2_p65_101")
    ap.add_argument("--seed", type=int, default=166166)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    out = []
    print("EMPTY-branch cells (0 hits expected):", flush=True)
    for c in a.cells.split(","):
        out.append(run(c, a.pad, a.n, rng, lambda s: print("  " + s, flush=True)))
    print("CONTROLS (branch (a) non-empty -- hits expected):", flush=True)
    for c in a.controls.split(","):
        out.append(run(c, a.pad, a.n, rng, lambda s: print("  " + s, flush=True)))
    bad = [r for r in out if r["branch_a_survivors"] == 0 and r["hits"] > 0]
    json.dump(dict(pad=a.pad, n=a.n, seed=a.seed, rows=out, REFUTED=bool(bad)),
              open(os.path.join(RES, "sampleline166_%s.json" % a.pad), "w"), indent=1)
    print("REFUTED =", bool(bad), flush=True)


if __name__ == "__main__":
    main()
