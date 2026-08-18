"""max total weight of a 3-clique of pairwise-overlapping placement squares with empty common
intersection (pinwheel) in the dual packing; > 1 means the pointwise-coverage LP relaxation is
exploited beyond what clique (odd-cycle) cuts would allow. usage: python pinwheel_check.py result.json"""
import json, math, sys, itertools
from analyze2 import square_poly
from lp_measure2 import d4_placement_images
res = json.load(open(sys.argv[1])); s = res["s"]
pl = []
for p in res["packing"]:
    for (a, b, t) in d4_placement_images(p["cx"], p["cy"], p["theta"], s):
        pl.append((a, b, t, p["y"] / 8))
WMIN = float(sys.argv[2]) if len(sys.argv) > 2 else 0.02
pl = [q for q in pl if q[3] > WMIN]
polys = [square_poly(a, b, t) for (a, b, t, w) in pl]
n = len(polys); print(f"s={s} images with weight>{WMIN}: {n}, weight {sum(q[3] for q in pl):.3f} of {res['nu']:.3f}")
inter = {}
for i in range(n):
    for j in range(i + 1, n):
        if polys[i].intersects(polys[j]):
            I = polys[i].intersection(polys[j])
            if I.area > 1e-9: inter[(i, j)] = I
best = (0, None); cnt = 0; over = 0
for (i, j), I in inter.items():
    for k in range(j + 1, n):
        if (i, k) in inter and (j, k) in inter and I.intersection(polys[k]).area < 1e-9:
            cnt += 1; sw = pl[i][3] + pl[j][3] + pl[k][3]
            if sw > 1 + 1e-9: over += 1
            if sw > best[0]: best = (sw, (i, j, k))
print(f"pinwheel triples: {cnt}, with weight sum > 1: {over}; max weight sum = {best[0]:.4f}")
if best[1]:
    for q in best[1]:
        print("   ", tuple(round(v, 4) for v in pl[q][:2]), round(math.degrees(pl[q][2]), 2), "w=", round(pl[q][3], 4))
# heaviest pairwise-overlapping pairs
pairs = sorted(((pl[i][3] + pl[j][3], i, j) for (i, j) in inter), reverse=True)[:5]
print("heaviest overlapping pairs (weight sums):", [round(p[0], 3) for p in pairs])
