"""A132 -- attribute the K'-only columns to the CONDITIONED box vs the PIN boxes.

`measure132.py` tests a placement against every core of the hypothesis (the pins and the node's own
box).  The pins are boxes too, so they also have a polygon core -- for a pin box (th0 = th1 = 0,
centre half-width hh = 1e-2/sqrt(2)) K'(P) is the axis square of half-side 1/2 - hh = 0.49293
against K(a) = 0.48999..., a 0.6% enlargement that still bites because pinned squares nearly touch.
This splits the count so the conditioned box's own contribution -- the PI's observation -- is
separate from the pins'.
"""
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, ".."))
A57 = os.path.join(ROOT, "A57-shadow-trees")
A60 = os.path.join(ROOT, "A60-trump5-campaign")
for p in (os.path.join(A57, "code"), os.path.join(ROOT, "A96-a57-parametric", "code"), HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

import polycore                                               # noqa: E402
from caselp import Box, EPS_CORE                              # noqa: E402
import measure132                                             # noqa: E402


def main():
    nodes = measure132.a57_alive() + measure132.a60_alive()
    out = []
    for meta, d in nodes:
        boxes = [Box.from_json(b) for b in d["hyp"]["boxes"]]
        cores = [b.core() for b in boxes]
        pcs = [measure132.polycore_for(b) for b in boxes]
        rec = dict(meta)
        for nm, arr in (("support",
                         np.array([[q["cx"], q["cy"], q["theta"], q["y"]]
                                   for q in d.get("packing", [])], float).reshape(-1, 4)),
                        ("pool",
                         np.hstack([np.array(d.get("rows_all") or [], float).reshape(-1, 3),
                                    np.zeros((len(d.get("rows_all") or []), 1))])
                         if d.get("rows_all") else np.zeros((0, 4)))):
            if not len(arr):
                rec[nm] = dict(n=0)
                continue
            C, TH, Wt = arr[:, :2], arr[:, 2], arr[:, 3]
            hit_core = np.zeros(len(arr), bool)
            hit_node = np.zeros(len(arr), bool)
            hit_pin = np.zeros(len(arr), bool)
            for j, (c, pc) in enumerate(zip(cores, pcs)):
                hit_core |= polycore.core_depth_fast(c, C, TH) > EPS_CORE
                h = polycore.poly_square_depth(pc.P, C, TH) > EPS_CORE
                if j == len(cores) - 1:
                    hit_node |= h
                else:
                    hit_pin |= h
            only_node = hit_node & ~hit_core
            only_pin = hit_pin & ~hit_core & ~hit_node
            rec[nm] = dict(n=int(len(arr)), only_node=int(only_node.sum()),
                           only_pin=int(only_pin.sum()),
                           w_only_node=float(Wt[only_node].sum()),
                           w_only_pin=float(Wt[only_pin].sum()), w=float(Wt.sum()))
        out.append(rec)
    with open(os.path.join(BASE, "results", "split132.jsonl"), "w") as fh:
        for r in out:
            fh.write(json.dumps(r) + "\n")

    for cls in ("A57", "A60"):
        S = [r for r in out if r["camp"] == cls]
        for nm in ("support", "pool"):
            n = sum(r[nm].get("n", 0) for r in S)
            a = sum(r[nm].get("only_node", 0) for r in S)
            b = sum(r[nm].get("only_pin", 0) for r in S)
            wa = sum(r[nm].get("w_only_node", 0.0) for r in S)
            wb = sum(r[nm].get("w_only_pin", 0.0) for r in S)
            print(f"{cls} {nm:8s} n={n:8d}  K'-only from the CONDITIONED box {a:7d} "
                  f"({100.0 * a / max(n, 1):5.2f}%, weight {wa:8.2f})  from the PINS {b:7d} "
                  f"({100.0 * b / max(n, 1):5.2f}%, weight {wb:8.2f})")


if __name__ == "__main__":
    main()
