"""A119 finding F1, the consequence probe.

A119's tree finds a CHECKED witness packing of L u P at S07 (0.2, 20 deg) in 2 s; A116 reports
CAP there after 900 s and 12 703 q-range splits.  This probe runs the SAME cell three ways:

  a116        A116's own tree (imported read-only), phase 1 only, 900 s;
  a119_qkeep  A119's tree with the q-range CARRY-OVER of A116 restored (qdrop=False);
  a119        A119's tree as shipped (a q-range is dropped when its owner's cell is bisected).

If only the third finds the witness, finding F1 has a consequence: the carried-over q-range rows
are not implied on the bisected cell, and they close leaves that contain a real packing.

Usage: python f1probe.py [tag cls r rho cut]
"""
from __future__ import annotations
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a119lib as L
import a116lib as A


def main():
    tag, cls, r, rho, cut = "S07", "trump5", 0.2, 20.0, 41.565
    if len(sys.argv) > 5:
        tag, cls, r, rho = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
        cut = None if sys.argv[5] == "None" else float(sys.argv[5])
    bodies, nv, s_sh, P = A.build_bodies(tag, cls, r, rho, tilt_floor_deg=cut)
    _, Pe, _, _ = A.anchored(tag, s_sh)
    ss = A.shadow_selections(bodies, Pe)
    out = []
    for name in ("a119", "a119_qkeep", "a116"):
        t0 = time.time()
        if name == "a116":
            T = A.Tree(bodies, nv, contact_pairs=list(ss), min_cell_deg=0.05, node_cap=4000000,
                       time_cap=900.0, target=A.S0, tighten_cap=0)
            v = T.run()
            wit = [w for w in T.witnesses if w.get("witness_valid")]
            st = v["stats"]
            qs = st["qsplit"]
        else:
            T = L.RecTree(bodies, nv, contact_pairs=list(ss), min_cell_deg=0.05,
                          node_cap=4000000, time_cap=900.0, qdrop=(name == "a119"))
            v = T.run()
            wit = [w for w in T.witnesses if w.get("witness_valid")]
            st = v["stats"]
            qs = st["qsplit"]
        rec = dict(variant=name, tag=tag, cls=cls, r=r, rho=rho, cut=cut,
                   dead=v["dead"], capped=v["capped"], nodes=st["nodes"], qsplit=qs,
                   qdrop=st.get("qdrop"), n_valid_witnesses=len(wit),
                   witness_side=(wit[0]["witness_side"] if wit else None),
                   witness_cfg=(wit[0].get("witness_cfg") if wit else None),
                   seconds=round(time.time() - t0, 1))
        out.append(rec)
        print("%-11s dead=%-5s cap=%-5s nodes=%-7d qsplit=%-6d valid witnesses=%d  side=%s  (%.0fs)"
              % (name, rec["dead"], rec["capped"], rec["nodes"], rec["qsplit"],
                 rec["n_valid_witnesses"],
                 ("%.6f" % rec["witness_side"]) if rec["witness_side"] else "-", rec["seconds"]),
              flush=True)
    with open(os.path.join(L.RES, "f1_probe.json"), "w", encoding="utf-8") as f:
        json.dump(dict(runs=out), f, indent=1)


if __name__ == "__main__":
    main()
