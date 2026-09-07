"""A121 canaries.  READ-ONLY; pure geometry; writes only results/canary121.json.

C1  FRAME DIRECTION.  For every node of every K-entry: applying the stored `struct_op` to the
    node's own `cfg` and re-running A107's snap-based split must reproduce the node's stored
    canonical `struct` (slot set, nfree).  This pins the direction of the map: the SHADOW frame
    is  f(node frame),  so a shadow cell pulls back to the node frame through f^{-1}.
C2  CELL PERMUTATION.  cell_map is an action of D4 on names: cell_map(cell_map(c, g), g^-1) == c
    for all 8 ops and every named cell, and it permutes the four corner cells.
C3  PRIMARY STRUCTURE.  The entry's drawn packing is the minimum of the structure with most
    nodes; its slot set must equal the entry's `slots`.
C4  OCCUPANCY vs A107.  Every pair the entry's own contact analysis books at gap < 1e-7 is
    reproduced by this module's SAT gap to within 1e-9 (the geometry agrees with A107's).
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import validate121 as V  # noqa: E402  (imports blas1 before numpy)
import lanelib as L  # noqa: E402
import numpy as np  # noqa: E402


def snap_name(x, y, t, s, dtol=0.05, atol=3.0):
    """A107 shadowlib.snap, verbatim in effect."""
    a = math.degrees(t - (math.pi / 2) * math.floor(t / (math.pi / 2)))
    if min(a, 90.0 - a) > atol:
        return None
    best, bd = None, 1e9
    for nm, (px, py) in V.slot_cells(s).items():
        d = math.hypot(x - px, y - py)
        if d < bd:
            best, bd = nm, d
    return best if bd <= dtol else None


def structure(cfg, s):
    slots, free = [], []
    for q in cfg:
        nm = snap_name(q[0], q[1], q[2], s)
        (slots.append(nm) if nm else free.append(q))
    return tuple(sorted(set(slots))), len(free)


def main():
    ent = V.load_entries()
    nodes_of = V.load_nodes_of_entry()
    sops, nidx = V.load_struct_ops()
    S0 = V.S0
    out = {}

    # ---- C1
    n, bad = 0, []
    for sid, ns in nodes_of.items():
        if not sid.startswith("K"):
            continue
        for nd in ns:
            rec = sops.get((nd["src"], nd["nid"]))
            if not rec or "cfg" not in rec:
                continue
            f = V.d4_ops(S0)[rec["struct_op"]]
            im = [f(q[0], q[1], q[2]) for q in rec["cfg"]]
            got = structure(im, S0)
            want = (tuple(rec["struct"][0]), rec["struct"][1])
            n += 1
            if got != want:
                bad.append(dict(src=nd["src"], nid=nd["nid"], op=rec["struct_op"],
                                got=[list(got[0]), got[1]], want=[list(want[0]), want[1]]))
    out["C1_frame_direction"] = dict(checked=n, mismatches=len(bad), examples=bad[:5],
                                     PASS=(n > 0 and not bad))

    # ---- C2
    ok, ncheck = True, 0
    corners = {"BL(0,0)", "BR(0,0)", "TR(0,0)", "TL(0,0)"}
    for g, gi in V.D4_INV.items():
        img = set()
        for c in corners:
            m = V.cell_map(c, g)
            img.add(m)
            ncheck += 1
            if V.cell_map(m, gi) != c:
                ok = False
        if img != corners:
            ok = False
        for c in ("BL(1,0)", "BR(0,1)", "TR(1,0)", "TL(1,1)", "BL(0,2)"):
            ncheck += 1
            if V.cell_map(V.cell_map(c, g), gi) != c:
                ok = False
    out["C2_cell_permutation"] = dict(checked=ncheck, PASS=ok)

    # ---- C3
    bad3 = []
    for sid, e in sorted(ent.items()):
        if not sid.startswith("K") or not e.get("structs"):
            continue
        prim = max(e["structs"], key=lambda d: d["nnodes"])
        if list(prim["slots"]) != list(e["slots"]) or prim["nfree"] != e["nfree"]:
            bad3.append(dict(entry=sid, prim=prim["slots"], entry_slots=e["slots"]))
    out["C3_primary_structure"] = dict(entries=len([k for k in ent if k.startswith("K")]),
                                       mismatches=len(bad3), examples=bad3[:5],
                                       PASS=not bad3)

    # ---- C4
    worst, ncc = 0.0, 0
    for sid, e in sorted(ent.items()):
        if not sid.startswith("K"):
            continue
        s, P = V.packing_of(e)
        D = {nm: (x, y, t) for nm, x, y, t in P}
        for c in (e.get("analysis") or {}).get("contacts", []):
            if c["a"] not in D or c["b"] not in D:
                continue
            ax, ay, at = D[c["a"]]
            bx, by, bt = D[c["b"]]
            g = L.sq_gap(L.Sq(ax, ay, at, 0.5), L.Sq(bx, by, bt, 0.5))
            worst = max(worst, abs(g - c["gap"]))
            ncc += 1
    out["C4_contacts_vs_A107"] = dict(contacts=ncc, max_abs_diff=worst,
                                      PASS=bool(ncc > 0 and worst < 1e-9))

    out["ALL_PASS"] = all(v["PASS"] for v in out.values() if isinstance(v, dict))
    p = os.path.join(V.RES, "canary121.json")
    os.makedirs(V.RES, exist_ok=True)
    json.dump(out, open(p, "w"), indent=1)
    print(json.dumps(out, indent=1)[:3000])


if __name__ == "__main__":
    main()
