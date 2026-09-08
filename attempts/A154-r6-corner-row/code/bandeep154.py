"""A154 addendum -- how much of A150's band survives "the root corner is the DEEPEST corner".

Lemma ID's certified corollary (A89-O3 R1 PASS, docs/proofs/tilt_floor_k0.md sec 8.6"): every
11-packing at every side m in [3.82, s0] has a corner with DEPTH >= 0.3.  By the container's D4
a corner-first tree may name its root corner to be a DEEPEST one, so the root corner's meeter can
be taken with DEPTH >= 0.3, i.e. (transported to s0 by K0-WIDEN / Lemma B-YES) with

    mu_c(Q) <= a_w(0.3) = 72103/100000 = 0.72103.

A150's band cell (ix, iy, it) is the raw A143 cell [ZLO+ix*w, ZLO+(ix+1)*w]^2 x [15 it, 15(it+1)).
mu is nondecreasing in each of u, v, so min over the cell = min over the tilt bin at (u0, v0).

Read-only on A143/A150.  Writes results/bandeep154.json.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a154lib as L  # noqa: E402
from corner85 import f_min_max  # noqa: E402

ZLO = 0.5
A_W = 1.0 + (969271.0 / 250000.0 / 3.82 - 1.0) * (1.0 + math.sqrt(2.0) / 2.0)
NPOS, NTILT = 6, 6
TILT_W = 90.0 / NTILT


def min_mu(ix, iy, it, nth=301):
    w = (A_W + math.sqrt(2.0) / 2.0 - ZLO) / NPOS
    u0, v0 = ZLO + ix * w, ZLO + iy * w
    best = 1e9
    for k in range(nth):
        th = (it + k / (nth - 1.0)) * TILT_W
        m = float(f_min_max(u0, v0, math.tan(math.radians(th) / 2.0)))
        best = min(best, m)
    return best


def main():
    aw03 = float(L.get_fam(0.3, log=lambda *a: None)["a"])
    band = json.load(open(os.path.join(L.ROOT, "attempts", "A150-four-corner-product",
                                       "results", "band150.json"), encoding="utf-8"))
    cells = {tuple(c) for c in band["band"]}
    allc = [(ix, iy, it) for ix in range(NPOS) for iy in range(NPOS) for it in range(NTILT)]
    mm = {c: min_mu(*c) for c in allc}
    deep_all = [c for c in allc if mm[c] <= aw03 + 1e-12]
    deep_band = [c for c in sorted(cells) if mm[c] <= aw03 + 1e-12]
    # also the strict-window reading mu <= 0.7 (the statement at side m, before transport)
    deep_band_07 = [c for c in sorted(cells) if mm[c] <= 0.7 + 1e-12]
    out = dict(a_w_ID=aw03, ZHI=A_W + math.sqrt(2.0) / 2.0, n_all=len(allc), n_band=len(cells),
               n_deep_all=len(deep_all), n_deep_band=len(deep_band),
               n_deep_band_mu_le_0p7=len(deep_band_07),
               deep_band=[list(c) for c in deep_band],
               pos_cells_deep=sorted({(c[0], c[1]) for c in deep_band}),
               min_mu={str(list(c)): round(mm[c], 6) for c in allc})
    json.dump(out, open(os.path.join(L.RES, "bandeep154.json"), "w"), indent=1)
    print("a_w(0.3) = %.5f ; band 206 -> DEEP(0.3) cells = %d (of 216 raw: %d); "
          "at the untransported mu <= 0.7: %d" %
          (aw03, len(deep_band), len(deep_all), len(deep_band_07)))
    print("distinct position cells carrying a deep tilt bin: %d of 36" %
          len({(c[0], c[1]) for c in deep_band}))
    print("per position cell (ix,iy): #deep tilt bins")
    for ix in range(NPOS):
        print("  " + " ".join("%d" % len([c for c in deep_band if c[0] == ix and c[1] == iy])
                              for iy in range(NPOS)))


if __name__ == "__main__":
    main()
