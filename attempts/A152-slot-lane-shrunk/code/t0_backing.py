"""A152 T0b -- the BACKING canary (notes/soundness.md sec 4).

Proposition.  A *completable* slot of a Young down-set class has both predecessor cells
(i-1, j) and (i, j-1) occupied -- by a container WALL (the index is negative) or by a PIN of the
class.  Consequence: the admissible translate set of the snapped sixth pin is contained in
[0, h]^2 in the cell's corner frame, so the tolerance can only be spent moving the slot square
AWAY from its two backed sides -- towards the two OPEN faces, which is where the grazers are.

This script checks the proposition on all 16 usable (class, slot) pairs of the corpus and records
which axes are wall-backed (translate 0 admissible) and which are pin-backed (translate >= h
forced when the pins carry slack).

    python t0_backing.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import lane152 as L152                                # noqa: E402

S0 = L152.P.S0


def main():
    out = {"proposition": "every predecessor cell of a completable slot is a WALL or a PIN",
           "classes": {}, "violations": []}
    for cls, d in L152.CP.CLASSES.items():
        if cls == "k0_00":
            continue
        rows = []
        for slot in d["usable"]:
            c, i, j = L152.LANE.L.parse_cell(slot)
            fx = (lambda v: S0 - v) if c in ("BR", "TR") else (lambda v: v)
            fy = (lambda v: S0 - v) if c in ("TL", "TR") else (lambda v: v)
            occ = set()
            for (px, py) in d["pins"]:
                a, b = fx(px) - 0.5, fy(py) - 0.5
                if abs(a - round(a)) < 1e-6 and abs(b - round(b)) < 1e-6 and a > -0.5 and b > -0.5:
                    occ.add((int(round(a)), int(round(b))))
            back = {}
            for (di, dj), ax in (((-1, 0), "-u"), ((0, -1), "-v")):
                ni, nj = i + di, j + dj
                back[ax] = ("WALL" if (ni < 0 or nj < 0) else
                            "PIN" if (ni, nj) in occ else "OPEN")
                if back[ax] == "OPEN":
                    out["violations"].append("%s %s axis %s" % (cls, slot, ax))
            rows.append(dict(slot=slot, i=i, j=j, backing=back,
                             pin_cells=sorted(occ),
                             exact_snap_admissible_in_slack_family=(back["-u"] == "WALL"
                                                                    and back["-v"] == "WALL")))
        out["classes"][cls] = rows
    out["n_slots"] = sum(len(v) for v in out["classes"].values())
    out["n_both_axes_wall_backed"] = sum(
        1 for v in out["classes"].values() for r in v
        if r["exact_snap_admissible_in_slack_family"])
    out["verdict"] = ("PROPOSITION HOLDS on all %d usable slots; %d of them are wall-backed on "
                      "BOTH axes (so A141's exact snap t = 0 survives a slack pin family there); "
                      "the other %d have at least one PIN backing, where t = 0 is INADMISSIBLE "
                      "once the pins carry the delta = 1e-2 slack"
                      % (out["n_slots"], out["n_both_axes_wall_backed"],
                         out["n_slots"] - out["n_both_axes_wall_backed"])) \
        if not out["violations"] else "VIOLATED: " + "; ".join(out["violations"])
    p = os.path.join(BASE, "results", "t0_backing.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(out, open(p, "w", encoding="utf-8"), indent=1)
    for cls, rows in out["classes"].items():
        for r in rows:
            print("%-7s %-9s (%d,%d)  -u=%-4s -v=%-4s  t=0 admissible in slack family: %s"
                  % (cls, r["slot"], r["i"], r["j"], r["backing"]["-u"], r["backing"]["-v"],
                     r["exact_snap_admissible_in_slack_family"]))
    print(out["verdict"])
    print("wrote", p)


if __name__ == "__main__":
    main()
