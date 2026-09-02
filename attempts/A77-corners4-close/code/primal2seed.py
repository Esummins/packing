#!/usr/bin/env python
"""primal2seed.py -- convert a dumped covering primal (atoms px,py,qx,qy,w)
into the pair_dual points+rows format that pairlp413m --seed_dual consumes."""
import json, sys
from fractions import Fraction as Fr
src, dst = sys.argv[1], sys.argv[2]
p = json.load(open(src))
pts, rows = [], []
for a in p["atoms"]:
    i = len(pts)
    pts.append([float(Fr(a["px"])), float(Fr(a["py"]))])
    pts.append([float(Fr(a["qx"])), float(Fr(a["qy"]))])
    rows.append([i, i + 1, float(Fr(a["w"]))])
json.dump(dict(points=pts, rows=rows, source=src, n_nonzero=len(rows),
               sum_duals=sum(r[2] for r in rows)), open(dst, "w"))
print("wrote", dst, len(rows), "rows")
