"""A132 -- POSITIVE CONTROL for the T5-polygon rule, in A96's discipline.

The polygon core K'(B) CONTAINS every square inscribed in all poses of B, in particular the
tight core K(a_tight) the deployed T5' rule uses, so no logic kill can be lost -- mathematically.
The computed polygon is shrunk by 1e-6 and simplified before certification, so this runs the
actual code over every recorded KILL-BY-LOGIC box and checks the rule still fires.

    python code/control132.py
"""
import glob
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, ".."))
A57 = os.path.join(ROOT, "A57-shadow-trees")
A53 = os.path.join(ROOT, "A53-simple-strata")
for p in (os.path.join(A57, "code"), os.path.join(ROOT, "A96-a57-parametric", "code"), HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

import polycore                                               # noqa: E402
from caselp import Box                                        # noqa: E402
import pinguard                                               # noqa: E402

DELTA = 1e-2


def main():
    slots_all = json.load(open(os.path.join(A53, "results", "name_to_slots.json")))
    hh = DELTA / math.sqrt(2.0)
    pinsets = {}
    n = kept = lost = err = 0
    lost_ids = []
    for f in sorted(glob.glob(os.path.join(A57, "results", "tree_*.jsonl"))):
        for ln in open(f):
            ln = ln.strip()
            if not ln:
                continue
            try:
                r = json.loads(ln)
            except Exception:
                continue
            if not str(r.get("cert") or "").startswith("KILL-BY-LOGIC") or not r.get("box"):
                continue
            nm = "k5_11" if r["id"].startswith("k5_11") else "k5_16"
            if nm not in pinsets:
                pinsets[nm] = [Box(x - hh, x + hh, y - hh, y + hh, 0.0, 0.0)
                               for (x, y) in slots_all[nm]]
            pins = pinsets[nm]
            b = Box.from_json(r["box"])
            n += 1
            try:
                pb = polycore.build(b)
                pp = [polycore.build(p) for p in pins]
                fires = any(polycore.poly_poly_depth(pb.P, q.P) > 0.0 for q in pp)
            except Exception as e:
                err += 1
                fires = False
                if err < 4:
                    print("  error", r["id"], repr(e)[:120])
            if fires:
                kept += 1
            else:
                lost += 1
                if len(lost_ids) < 25:
                    lost_ids.append(r["id"])
    print(f"positive control: {kept}/{n} recorded KILL-BY-LOGIC boxes still killed by the polygon "
          f"rule; lost {lost}; build errors {err}")
    if lost_ids:
        print("  lost:", lost_ids)
    json.dump(dict(boxes=n, kept=kept, lost=lost, errors=err, lost_ids=lost_ids,
                   clean=(lost == 0 and err == 0)),
              open(os.path.join(BASE, "results", "control132.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
