"""A172 report -- the before/after table for the per-piece K' fix, on A168's S2 node.

    python report172.py            (writes results/report172.json, prints the table)

Three columns, all at nsub=4, refine=3, s = 3.877084:

  UNION      A171 as shipped: K' rebuilt from union_box(), the axis-box x tilt hull of the
             surviving pieces  (`normalise(..., kmode="union")`).
  SAME-PIECES  the exact intersection of the per-piece K' computed on EXACTLY the pieces the UNION
             fixed point leaves -- the like-for-like measurement of what the hull forgets.
  PIECES     A172 as shipped: the same fixed-point loop driven by the per-piece K' throughout
             (`normalise()`, kmode="pieces" being the default).
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
A171 = os.path.abspath(os.path.join(HERE, "..", "..", "A171-multibox-invariant", "code"))
sys.path.insert(0, A171)

import multibox as MB                                          # noqa: E402

ROLES = {                                                      # demo171.ROLES, verbatim
    "H":  (2.5674485, 2.67226625, 2.357813, 2.46263075, 45.0, 60.0),
    "B1": (3.127084, 3.1733821433529026, 1.5015011950128963, 1.5785397484754269, 45.0, 50.625),
    "D":  (3.223006893074939, 3.377084, 3.211365683498047, 3.377084, 0.0, 11.25),
}
SRC = ("attempts/A168-cascade-fable/results/v0_union_boxes/cascade168.jsonl -- cell l1_153, "
       "node BR139/TRH-25, step S2 (the ROLES of A171 code/demo171.py)")


def snap(nd, seconds):
    r = nd.assert_invariant(raise_on_fail=False)
    return dict(kept={k: v for k, v in r["kept"].items()},
                K_area={k: b.pc.area() for k, b in nd.boxes.items()},
                axis_a={k: float(b.core.a) for k, b in nd.boxes.items()},
                pieces={k: len(b.pieces) for k, b in nd.boxes.items()},
                k_source={k: b.k_source for k, b in nd.boxes.items()},
                k_info={k: b.k_info for k, b in nd.boxes.items()},
                passes=nd.stats["passes"], exact_calls=nd.stats["exact_calls"],
                invariant=r["ok"], checks={k: v["ok"] for k, v in r["checks"].items()},
                diagnostics=r["diagnostics"], seconds=round(seconds, 2))


def main():
    out = dict(source=SRC, s=str(MB.S_RAT), settings=dict(nsub=4, refine=3, n_grid=97, max_v=16))

    t = time.time()
    ndu = MB.Node(ROLES, name="A168 S2 union-hull K'")
    ndu.normalise(nsub=4, refine=3, kmode="union")
    out["union"] = snap(ndu, time.time() - t)

    t = time.time()
    same, cache = {}, {}
    for k, mb in ndu.boxes.items():
        V, info, boxes = MB.pieces_poly(mb.pieces, cache=cache)
        same[k] = dict(area=float(MB.poly_area_frac(V)), nv=len(V), n_pieces=len(mb.pieces),
                       uncertified=len(MB.certify_verts(V, boxes)), shrink=info["shrink"])
    out["same_pieces"] = dict(K_area={k: v["area"] for k, v in same.items()}, detail=same,
                              seconds=round(time.time() - t, 2))

    t = time.time()
    ndp = MB.Node(ROLES, name="A168 S2 per-piece K'")
    ndp.normalise(nsub=4, refine=3)
    out["pieces"] = snap(ndp, time.time() - t)

    hdr = f"{'':10s} " + " ".join(f"{k:>10s}" for k in ROLES)
    print(f"A168 BR139/TRH-25, nsub=4 refine=3\n{hdr}")
    for tag, key in (("K' area (union hull)", ("union", "K_area")),
                     ("K' area (same pieces, per-piece)", ("same_pieces", "K_area")),
                     ("K' area (A172 fixed point)", ("pieces", "K_area")),
                     ("kept (union)", ("union", "kept")),
                     ("kept (A172)", ("pieces", "kept")),
                     ("axis a (union)", ("union", "axis_a")),
                     ("axis a (A172)", ("pieces", "axis_a")),
                     ("pieces (union)", ("union", "pieces")),
                     ("pieces (A172)", ("pieces", "pieces"))):
        d = out[key[0]][key[1]]
        print(f"{tag:34s} " + " ".join(f"{d[k]:10.6f}" if isinstance(d[k], float)
                                       else f"{d[k]:10d}" for k in ROLES))
    for m in ("union", "pieces"):
        print(f"{m:34s} passes={out[m]['passes']} invariant={out[m]['invariant']} "
              f"exact_calls={out[m]['exact_calls']} {out[m]['seconds']} s")
    print("uncertified vertices (same pieces): "
          f"{sum(v['uncertified'] for v in same.values())}")
    p = os.path.join(HERE, "..", "results", "report172.json")
    with open(os.path.abspath(p), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    print("wrote", os.path.abspath(p))


if __name__ == "__main__":
    main()
