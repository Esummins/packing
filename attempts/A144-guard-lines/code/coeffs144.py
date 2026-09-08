"""A144 T1 -- the EXACT rational column coefficients |l n Q_p| for every column in a node's pool.

For the chosen guard line of a node: the exact Fraction coefficient of every placement in the
node's stored row pool (`rows_all`) and of every dual-support column, with the placement snapped to
the corpus's own grids (t = tan(theta/2) on 1/2^24, centres on 1/10^9 -- the grids `caselp.t_lo`,
`caselp.t_hi` and `caselp.q` already use), and the float-vs-exact discrepancy that the snapping
costs.  This is the object the v3 clause's verifier recomputes, so it has to be producible exactly
and cheaply for a whole pool.

    set PYTHONDONTWRITEBYTECODE=1 && python code/coeffs144.py --node k5_11_interior_Y0147
"""
import argparse
import json
import math
import os
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import guardline as G                                                   # noqa: E402
import offline144 as OFF                                                # noqa: E402
import polycore                                                         # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--node", default="k5_11_interior_Y0147")
    ap.add_argument("--tag", default="PI: 0.99 below the top")
    a = ap.parse_args()
    d, path = OFF.load_node(a.node)
    pins, hbox = G.node_boxes(d)
    pcv = polycore.build(hbox, max_v=16).verts
    _fam, rows, _ = OFF.measure(d, want_pi=True, max_lines=40)
    r = next((x for x in rows if x["line"]["tag"] == a.tag), rows[0])
    ln = G.Line(r["line"]["orient"], Fr(r["line"]["off"]), r["line"]["tag"])
    gr = G.guard_row(pins, hbox, ln, pc_verts=pcv)

    pool = [tuple(x) for x in (d.get("rows_all") or [])]
    t0 = time.time()
    ex = G.column_coefficients_exact(pool, ln)                 # LP half-side (shrunk)
    ex_full = G.column_coefficients_exact(pool, ln, a=G.HALF)  # full unit squares
    dt = time.time() - t0
    fl = [G.chord_float(float(G.HALF) - 1e-4, th, ln.offset_of(cx, cy)) for (cx, cy, th) in pool]
    err = max((abs(float(e) - f) for e, f in zip(ex, fl)), default=0.0)
    nz = sum(1 for e in ex if e > 0)

    sup = []
    for p in (d.get("packing") or []):
        e = G.column_coefficients_exact([(float(p["cx"]), float(p["cy"]), float(p["theta"]))],
                                        ln, a=G.HALF)[0]
        sup.append(dict(cx=float(p["cx"]), cy=float(p["cy"]),
                        theta_deg=math.degrees(float(p["theta"])), y=float(p["y"]),
                        chord_exact=str(e), chord_float=float(e),
                        chord_float_direct=G.chord_float(0.5, float(p["theta"]),
                                                         ln.offset_of(float(p["cx"]),
                                                                      float(p["cy"])))))
    lhs_exact = sum((Fr(round(s["y"] * 10 ** 9), 10 ** 9) * Fr(s["chord_exact"]) for s in sup),
                    Fr(0))
    out = dict(node=a.node, record=path, line=ln.to_json(),
               rhs_exact=str(gr["rhs"]), rhs_float=gr["rhs_float"],
               minchord_H_exact=str(gr["h"]), pins_exact=[str(x) for x in gr["pins"]],
               kprime_chord_exact=(str(gr["kprime"]) if gr["kprime"] is not None else None),
               pool_size=len(pool), pool_nonzero_coefficients=nz,
               pool_exact_seconds=round(dt, 2),
               max_abs_float_minus_exact=err,
               sum_exact_coefficients_full_half=float(sum(ex_full, Fr(0))),
               support=sup,
               lhs_exact=str(lhs_exact), lhs_exact_float=float(lhs_exact),
               violation_exact=str(lhs_exact - gr["rhs"]),
               violation_exact_float=float(lhs_exact - gr["rhs"]))
    p = os.path.join(BASE, "results", f"coeffs144_{a.node}.json")
    json.dump(out, open(p, "w", encoding="utf-8"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
