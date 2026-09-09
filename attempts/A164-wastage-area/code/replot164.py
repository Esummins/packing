"""A164 -- redraw a U figure from the STORED mask and result row, without recomputing.

    set PYTHONDONTWRITEBYTECODE=1 && python replot164.py --id f1_L10_0003 --tag fine_max
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
for _p in (os.path.join(ATT, "A148-gallery-v4", "code"),
           os.path.join(ATT, "A132-polygon-core", "code"),
           os.path.join(ATT, "A135-polycore-verifier", "code"),
           os.path.join(ATT, "A57-shadow-trees", "code"), HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import geo164 as G                                                    # noqa: E402
import fig164                                                         # noqa: E402
from caselp import Box                                                # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--id", required=True)
ap.add_argument("--tag", required=True)
a = ap.parse_args()

z = np.load(os.path.join(BASE, "results", f"mask_{a.id}.npz"), allow_pickle=True)
spec = json.loads(str(z["spec"][0]))
res = None
for ln in open(os.path.join(BASE, "results", f"u164_{a.tag}.jsonl"), encoding="utf-8"):
    r = json.loads(ln)
    if r["id"] == a.id:
        res = r
assert res is not None, a.id
assert abs(res["pitch"] - spec["pitch"]) < 1e-12 and abs(res["lam"] - spec["lam"]) < 1e-12, \
    "the stored mask and the stored row are from different runs"
obs, names, kinds, _ = G.obstacles_of(spec["boxes"])
bx = [Box.from_json(b) for b in spec["boxes"]]
out = fig164.page(dict(id=a.id, record=res.get("record")), res, z["U"], z["xs"], z["ys"],
                  obs, names, kinds, bx, os.path.join(BASE, "figs", f"{a.id}_U.svg"))
print("wrote", out)
