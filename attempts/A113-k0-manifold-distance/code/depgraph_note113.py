"""Append A113's one-line note to the depgraph K0.TREE node (owner field untouched).
Usage: python depgraph_note113.py   (edits lean/depgraph.json in place, utf-8, nothing else)."""
import io, json, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
P = os.path.join(ROOT, "lean", "depgraph.json")
NOTE = ("A113 (2026-09-06, geometry only): the k0 tree's cost is NOT concentrated near the k>=1 "
        "manifold -- only 1.4/4.6/17.6 percent of A99's 9,341-21,661 CPU-h lies within eta = "
        "0.05/0.1/0.2 of a simple placement (eta = max(L-inf distance to the 36 corner-lattice "
        "cell centres, sqrt2 sin(tilt-gap/2))), and all five alive(LP) level-1 cells are FAR "
        "(eta 0.229-0.366), because the tree conditions on an INTERIOR square and every near-shat "
        "minimum has its interior squares tilted (Trump 40.2/49.8 deg, so the three Trump-image "
        "cells sit at eta 0.366 while the images themselves have 5 simple squares each). The "
        "POSITION term alone does guide: 0 of 26 processed cells with d_pos <= 0.05 was ever "
        "LP-killed vs 45 percent at d_pos >= 0.2 (Spearman -0.44, stable in every tilt bin), and "
        "the six most resistant cells (tau up to 10.500 > budget) are at d_pos <= 0.02; those 36 "
        "root cells carry 16.7 percent of the cost and no kill. LP wall is flat in eta, so cost "
        "is un-killability, not per-node price. The real signal is the DUAL SUPPORT: 3.40 simple "
        "placements per ALIVE support vs 0.81 per LP-killed one, the killed ones matching A107's "
        "S01 'room' shadow at s* = 4.000000 and the survivors partial skeletons of near-critical "
        "shadows (l1_100 an exact match to S38 @ 3.928915, s1int_l1_043 Jaccard 0.83 to S07 @ "
        "3.885618) -- a re-branching rule, not a pre-branching one. Also: zero logic kills exist "
        "in this tree (nofams = [] in all 264 node jsons; Lemma ID needs a shallow corner).")

g = json.load(io.open(P, encoding="utf-8"))
byid = {n["id"]: n for n in g["nodes"]}
if "K0.TREE" not in byid:
    print("K0.TREE node absent -- nothing done")
    sys.exit(1)
if NOTE[:60] in (byid["K0.TREE"].get("note") or ""):
    print("note already present")
    sys.exit(0)
byid["K0.TREE"]["note"] = (byid["K0.TREE"].get("note", "") + " || " + NOTE)
json.dump(g, io.open(P, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("depgraph K0.TREE note appended (A113); owner field unchanged: %r"
      % byid["K0.TREE"].get("owner"))
