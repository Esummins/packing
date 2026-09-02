#!/usr/bin/env python
# -*- coding: ascii -*-
"""catalog81.py -- A81: dump the k4_08 U-row catalog (A80 rig, read-only import) as a
placement list for the mixed-depth emission LP (pairlp_u.py).

Columns: the two compatible Trump images' free-square poses at s0 (crowdfam k4_08 family
= the trump-sym4 image, exact to 1e-8; 'diag' = its diagonal reflection, k4_08's own
symmetry), +-d_in / +-d_out perturbation columns per zone centre (so the fractional dual
can trade in-zone against out-of-zone mass -- the A12/A80 dodge), and the A66 grid
enrichment.  Every column is exactly core-free and contained (build_catalog filters).

    python code\catalog81.py --r_z 1e-4 --out results\catalog_k4_08_u.json
"""
import os
for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse
import json
import sys
from fractions import Fraction as Fr

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
sys.path.insert(0, os.path.join(ATT, "A80-u-ladder", "code"))
import pairlp as pl                      # A80 copy of the A66 rig, imported read-only
from basinlp import perturbed
from ladderlp import reflect_diag


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cls", default="k4_08")
    ap.add_argument("--r_z", type=float, default=1e-4)
    ap.add_argument("--d_in", type=float, default=None)
    ap.add_argument("--d_out", type=float, default=None)
    ap.add_argument("--images", default="id,diag")
    ap.add_argument("--cap_total", type=int, default=300)
    ap.add_argument("--cap_m2", type=int, default=200)
    ap.add_argument("--cap_m1", type=int, default=60)
    ap.add_argument("--cap_coarse", type=int, default=40)
    ap.add_argument("--min_sep", type=float, default=0.35)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    if args.d_in is None:
        args.d_in = 0.3 * args.r_z
    if args.d_out is None:
        args.d_out = 3.0 * args.r_z
    fh = open(os.path.join(BASE, "logs", "catalog81.log"), "a")
    spec = json.load(open(pl.BOXSPEC))
    e = spec["classes"][args.cls]
    pins = np.array([[float(Fr(a)), float(Fr(b))] for a, b in e["pins"]])
    boxes = np.array([[float(Fr(b["slot"][0])), float(Fr(b["slot"][1]))] for b in e["boxes"]])
    ctrl = pl.control_family(args.cls, pins, boxes, fh)
    assert ctrl is not None
    images = {}
    for name in args.images.split(","):
        if name == "id":
            images[name] = [list(p) for p in ctrl["placements"]]
        elif name == "diag":
            images[name] = [list(p) for p in reflect_diag(ctrl["placements"])]
        else:
            raise SystemExit("unknown image " + name)
    extra = []
    for name, zones in images.items():
        extra += [tuple(z) for z in zones] + perturbed([tuple(z) for z in zones], pins,
                                                       args.d_in, args.d_out)
    cat = pl.build_catalog(pins, boxes, args, fh, extra=extra)
    pls = [[float(t), float(c[0]), float(c[1])] for t, c in zip(cat["t"], cat["C"])]
    # every image pose must be a column (exactly, up to the 1e-9 dedupe)
    for name, zones in images.items():
        for (t, cx, cy) in zones:
            d = min(max(abs(p[0] - t), abs(p[1] - cx), abs(p[2] - cy)) for p in pls)
            assert d < 1e-8, (name, t, cx, cy, d)
    out = dict(cls=args.cls, n=len(pls), placements=pls, images=images, r_z=args.r_z,
               d_in=args.d_in, d_out=args.d_out, control=dict(
                   sum_m2_unitboxes=ctrl["sum_m2"], min_sat_gap=ctrl["min_sat_gap"]),
               stats=cat["stats"], settings=vars(args),
               note="A81 catalog81.py: A80 rig build_catalog (A66 conventions) + both Trump "
                    "images' poses + perturbation columns at d_in/d_out; masks are NOT stored "
                    "(pairlp_u.py recomputes m2 against the WIDENED class boxes)")
    json.dump(out, open(args.out, "w"))
    pl.log("wrote %s: %d placements, images %s, stats %s" % (
        args.out, len(pls), list(images), json.dumps(cat["stats"])), fh)


if __name__ == "__main__":
    main()
