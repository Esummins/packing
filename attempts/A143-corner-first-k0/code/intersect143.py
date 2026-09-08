"""A143 T2 -- intersect the two covers.

The corner-first tree is an INDEPENDENT cover of k0_00: a packing must survive BOTH it and the
interior-first tree, so a cell of one tree whose surviving geometry forces the other tree's DEAD
cell is itself dead.  Concretely, for each of A115 T6's twelve converged-alive interior cells:
locate the BL intruder(s) of its LP support -- the support placements that meet the widened BL box
-- and report which corner-first level-1 cells they occupy and what those cells' verdicts are.

    python code/intersect143.py
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
A140 = os.path.join(ROOT, "attempts", "A140-k0-residue-gallery", "code")
_A57 = os.path.join(ROOT, "attempts", "A57-shadow-trees", "code")
for _p in (A140, _A57, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import blas1                                                    # noqa: F401,E402
import cells143 as C                                            # noqa: E402
import pairs143 as P                                            # noqa: E402
import cells140 as C140                                         # noqa: E402


def locate_raw(x, y, th):
    w = (C.ZHI - C.ZLO) / C.NPOS
    th = th % 90.0
    if not (C.ZLO - 1e-9 <= x <= C.ZHI + 1e-9 and C.ZLO - 1e-9 <= y <= C.ZHI + 1e-9):
        return None
    return (min(C.NPOS - 1, max(0, int((x - C.ZLO) / w))),
            min(C.NPOS - 1, max(0, int((y - C.ZLO) / w))),
            min(C.NTILT - 1, max(0, int(th / C.TILT_W))))


def main():
    geo = {}
    for ln in open(os.path.join(BASE, "results", "geom143.dedup.jsonl"), encoding="utf-8"):
        r = json.loads(ln)
        geo[(r["ix"], r["iy"], r["it"])] = r["verdict"]
    pg = {}
    for ln in open(os.path.join(BASE, "results", "pairs143_geom.jsonl"), encoding="utf-8"):
        r = json.loads(ln)
        pg[(tuple(r["pair"][0]), tuple(r["pair"][1]))] = r["verdict"]

    out = {}
    for (name, lvl, src, fn, lanekey, alias) in C140.CELLS:
        meta, d = C140.load_cell(name)
        pk = d.get("packing") or []
        meeters = []
        for p in pk:
            cx, cy, th = float(p["cx"]), float(p["cy"]), float(p["theta"])
            thd = math.degrees(th) % 90.0
            if not C.meets_bl(cx, cy, thd, a_w=C.A_W):
                continue
            k = locate_raw(cx, cy, thd)
            meeters.append(dict(pose=[round(cx, 5), round(cy, 5), round(thd, 4)],
                                w=float(p.get("y", 0.0)),
                                cell_raw=(list(k) if k else None),
                                cell_canon=(list(C.locate(cx, cy, thd))
                                            if C.locate(cx, cy, thd) else None),
                                verdict=(geo.get(C.locate(cx, cy, thd)) if k else None),
                                unwidened=C.meets_bl(cx, cy, thd, a_w=1.0)))
        pairs = []
        for i in range(len(meeters)):
            for j in range(i + 1, len(meeters)):
                if not (meeters[i]["cell_raw"] and meeters[j]["cell_raw"]):
                    continue
                cc = P.pair_canonical(tuple(meeters[i]["cell_raw"]),
                                      tuple(meeters[j]["cell_raw"]))
                pairs.append(dict(pair=[list(cc[0]), list(cc[1])], verdict=pg.get(cc)))
        out[name] = dict(level=lvl, n_support=len(pk), n_bl_meeters=len(meeters),
                         n_bl_meeters_unwidened=sum(1 for m in meeters if m["unwidened"]),
                         meeters=meeters, pairs=pairs,
                         any_dead_single=any(m["verdict"] not in (None, "ALIVE-GEOM")
                                             for m in meeters),
                         any_dead_pair=any(p["verdict"] not in (None, "ALIVE-CORE")
                                           for p in pairs))
        print(f"{name:26s} support {len(pk):3d}  BL meeters {len(meeters):2d} "
              f"({out[name]['n_bl_meeters_unwidened']} unwidened)  "
              f"cells {sorted({tuple(m['cell_canon']) for m in meeters if m['cell_canon']})}  "
              f"dead_single={out[name]['any_dead_single']} "
              f"dead_pair={out[name]['any_dead_pair']}", flush=True)
    p = os.path.join(BASE, "results", "intersect143.json")
    json.dump(out, open(p, "w"), indent=1)
    print("wrote", p, flush=True)


if __name__ == "__main__":
    main()
