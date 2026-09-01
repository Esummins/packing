"""
A60 / G-A60-2: the OUTER three squares.  Census + residue ladder for the side zones at
conditioning depth 3 (the interior triple located), exact arithmetic only -- no LP.
Writes one json per zone so a partial run is never lost.
"""
import json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import blas1  # A57 T18: pin BLAS to 1 thread BEFORE numpy loads
import tree60 as T
from tree60 import census, ladder_scan, gate, RES
from caselp import Box


def interior_triple():
    """re-derive the three located interior boxes (one chain, deterministic)."""
    loc = [Box.from_json(d) for d in json.load(open(os.path.join(RES, "a60_located_sq1.json")))]

    def hug(b, cond=(), names=(), budget=5):
        g = gate(b, list(cond), [], budget, list(names))
        h = g["hugs"]
        return h if isinstance(h, str) else (h[0] if h else None)

    byh = {}
    for b in loc:
        byh.setdefault(hug(b), []).append(b)
    B1 = byh["sq7"][0]
    r1, _ = ladder_scan(["sq7"], 26, cond_boxes=[B1])
    L1 = [Box.from_json(d) for d in r1["final_residue"]]
    h1 = {}
    for b in L1:
        h1.setdefault(hug(b, [B1], ["sq7"], 4), []).append(b)
    nm2 = sorted(h1)[0]
    B2 = h1[nm2][0]
    r2, _ = ladder_scan(["sq7", nm2], 26, cond_boxes=[B1, B2])
    L2 = [Box.from_json(d) for d in r2["final_residue"]]
    h2 = {}
    for b in L2:
        h2.setdefault(hug(b, [B1, B2], ["sq7", nm2], 3), []).append(b)
    nm3 = sorted(h2)[0]
    B3 = h2[nm3][0]
    return [B1, B2, B3], ["sq7", nm2, nm3]


def main():
    levels = int(sys.argv[1]) if len(sys.argv) > 1 else 26
    zs = sys.argv[2].split(",") if len(sys.argv) > 2 else ["side_R", "side_L", "side_T"]
    cond, names = interior_triple()
    print("conditioned interior triple:", names, flush=True)
    for z in zs:
        t0 = time.time()
        cen = census(names, cond_boxes=cond, zone=z)
        r, _ = ladder_scan(names, levels, cond_boxes=cond, zone=z)
        L = r["levels"][-1]
        q = sum(x.get("kill_queue", 0) for x in r["levels"])
        out = dict(zone=z, cond=names, counts=cen["counts"], queue=q,
                   levels=[{k: v for k, v in x.items() if k != "queue"} for x in r["levels"]],
                   final_residue=r["final_residue"], seconds=round(time.time() - t0, 1))
        json.dump(out, open(os.path.join(RES, "a60_sidezone_%s_j3.json" % z), "w"), indent=1)
        print("%-8s cover=%d free=%d parent=%d att=%d unk0=%d | terminal L%d boxes=%d "
              "contain=%.3e all_inside=%s queue=%d  (%.0f s)"
              % (z, cen["counts"]["cover"], cen["counts"]["contradictory"],
                 cen["counts"]["parent"], cen["counts"]["attemptable"],
                 r["levels"][0]["boxes"], L["level"], L["boxes"], L["max_containment"] or 0,
                 L["all_inside"], q, time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
