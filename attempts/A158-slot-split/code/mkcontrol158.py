"""A158 -- build the control job list: every cell where the NO child reported a kill, plus the six
PI cells.  The control is the SAME A135 exact-core re-solve with no NoFam at all."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.abspath(os.path.join(HERE, "..", "results"))

PI = [("c0_Y0076", "TL(0,0)"), ("c0_Y0787", "BR(0,1)"), ("c0_Y0959", "TR(0,1)"),
      ("k5_11_interior_Y0130", "TR(0,0)"), ("k5_11_interior_Y0147", "TR(0,0)"),
      ("k5_11_interior_Y1110", "TR(0,0)")]


def main():
    cells, seen = [], set()
    for (nid, slot) in PI:
        seen.add((nid, slot))
        cells.append(dict(nid=nid, slot=slot, why="PI cell"))
    p = os.path.join(R, "no158.jsonl")
    if os.path.exists(p):
        for ln in open(p, encoding="utf-8"):
            ln = ln.strip()
            if not ln:
                continue
            d = json.loads(ln)
            if not d.get("kill") or d.get("control"):
                continue
            k = (d["nid"], d["slot"])
            if k in seen:
                continue
            seen.add(k)
            cells.append(dict(nid=d["nid"], slot=d["slot"], why="NO-child kill at r=%s tt=%s"
                              % (d.get("r"), d.get("tt"))))
    out = os.path.join(R, "control_jobs.jsonl")
    with open(out, "w", encoding="utf-8") as fh:
        for c in cells:
            fh.write(json.dumps(c) + "\n")
    print("control jobs: %d -> %s" % (len(cells), out))
    for c in cells:
        print("  %-32s %-9s %s" % (c["nid"], c["slot"], c["why"]))


if __name__ == "__main__":
    main()
