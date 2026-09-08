"""A150 -- the coarseness ladder measured as a GEOMETRIC quantity, so the LP verdict can be
predicted without paying for it.

On the fine cover the LP verdict tracks `area_open` = the area of the certified-non-blocked
feasible-centre set with all four polygon cores removed (A148's outer approximation of the region
a further square's centre may occupy): the ten fine nodes solved in T3 split at roughly
`area_open ~ 2` (below: converged kill; well above: alive).  `area_open` is a pure geometry
computation costing ~1 s, so it can be evaluated all along the coarseness ladder and says WHY the
coarse covers stop deciding: a coarse cell has a smaller exact core, the cores block less, and the
free region grows.

    python code/ladder150.py --per 6
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
for _p in (os.path.join(ATT, "A143-corner-first-k0", "code"),
           os.path.join(ATT, "A148-gallery-v4", "code"),
           os.path.join(ATT, "A132-polygon-core", "code"),
           os.path.join(ATT, "A135-polycore-verifier", "code"),
           os.path.join(ATT, "A57-shadow-trees", "code"),
           HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import blas1                                                        # noqa: F401,E402
import numpy as np                                                  # noqa: E402
import polycore                                                     # noqa: E402
import exactcore                                                    # noqa: E402
import geo148 as G                                                  # noqa: E402
import cells143 as C                                                # noqa: E402
import frames150 as F                                               # noqa: E402
import coarse150 as K                                               # noqa: E402

RES = os.path.join(BASE, "results")
S0 = C.S0
LADDER = [(2, 2), (2, 3), (3, 3), (3, 4), (4, 4), (6, 3), (6, 6)]


def measure(cells, keys, npos, ntilt, per, rng):
    rows = []
    for _ in range(per):
        t = [keys[int(rng.integers(0, len(keys)))] for _ in range(4)]
        byk = {c.key if hasattr(c, "key") else (c.ix, c.iy, c.it): c for c in cells}
        boxes = [K.gbox(c, byk[k]) if hasattr(byk[k], "key") else F.global_box(c, byk[k])
                 for c, k in zip(F.CORNERS, t)]
        obs = [polycore.build(b, max_v=16).P for b in boxes]
        reg = G.feasible_region(S0, obs, pitch_target=0.02, ntilt=36)
        aex = []
        for b in boxes:
            a, _a0, ok = exactcore.exact_a(b)
            aex.append(float(a) if ok else 0.0)
        rows.append(dict(tuple=[list(x) for x in t], area_open=reg.area_open(),
                         area_green=reg.area_green(), a_exact_min=min(aex)))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per", type=int, default=6)
    a = ap.parse_args()
    rng = np.random.default_rng(1520)
    out = []
    for (npos, ntilt) in LADDER:
        if (npos, ntilt) == (6, 6):
            keys = [tuple(k) for k in json.load(open(os.path.join(RES, "band150.json"),
                                                     encoding="utf-8"))["band"]]
            cells = [c for c in C.all_cells() if (c.ix, c.iy, c.it) in set(keys)]
        else:
            cells = K.all_coarse(npos, ntilt)
            keys = [c.key for c in cells]
        rows = measure(cells, keys, npos, ntilt, a.per, rng)
        ao = np.array([r["area_open"] for r in rows])
        am = np.array([r["a_exact_min"] for r in rows])
        rec = dict(npos=npos, ntilt=ntilt, cells=len(keys),
                   orbits=(len(keys) ** 4) // 8,
                   a_exact_min=float(am.min()), a_exact_median=float(np.median(am)),
                   area_open_min=float(ao.min()), area_open_median=float(np.median(ao)),
                   area_open_max=float(ao.max()), n=len(rows), rows=rows)
        out.append(rec)
        print("np%d nt%d  cells %3d  a_exact med %.4f  area_open %.3f / %.3f / %.3f"
              % (npos, ntilt, len(keys), rec["a_exact_median"], ao.min(),
                 np.median(ao), ao.max()), flush=True)
    json.dump(out, open(os.path.join(RES, "ladder150.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
