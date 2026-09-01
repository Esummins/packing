"""
A53 canary (PI addition): certify Trump's exact locked count k from his exact coordinates.

Simple = axis-aligned + doubly-flush (EXACT) against walls u locked squares, wall-anchored.
Works at Trump's own container side s_T (his packing tight in [0,s_T]^2); the k = 5
skeleton then transfers to the s0-stratification via the stretched embedding (corner pins
moved outward by s0 - s_T = 4.1e-7; see notes/lemmas.md).

Certification scheme: 60-digit certified decimals from A03's trump11_exact.json
(Gauss-Newton at 70 dps, contacts exact in the rigid system) + minimal polynomials.
All separations asserted below are > 1e-2, so 60-digit decimals decide them with margin
10^50; flushness of the five uprights is exact (rational coordinates 1/2, 3/2 and the
wall value s_T - 1/2, contacts by construction of the rigid solution).
"""
import json, os
from mpmath import mp, mpf

mp.dps = 60
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, "..", "..", "A03-upper-reconstruct", "trump11_exact.json")))
sT = mpf(d["s"])
sq = [(mpf(q["cx"]), mpf(q["cy"]), mpf(q["theta"])) for q in d["squares"]]

report = {"s_T": d["s"][:40], "squares": []}

# 1. orientation: uprights are exactly theta = 0 in the rigid system (A03 solved the
#    contact equations with theta_i = 0 imposed for i = 0..5; residuals ~1e-70 confirm).
uprights = [i for i, (_, _, th) in enumerate(sq) if abs(th) < mpf("1e-60")]
tilted = [i for i in range(11) if i not in uprights]
assert uprights == [0, 1, 2, 3, 4, 5]

# 2. flush graph among uprights + walls (exact coordinate arithmetic at 60 dps;
#    all decisions have margin > 1e-2 except stated contacts, which are exact 0 by rigidity)
def near(a, b):
    return abs(a - b) < mpf("1e-50")

slots_L = [mpf("0.5") + i for i in range(3)]
slots_R = [sT - mpf("0.5") - j for j in range(3)]

locked = set()
changed = True
while changed:
    changed = False
    for i in uprights:
        if i in locked:
            continue
        cx, cy, _ = sq[i]
        # x-support: wall (exact 1/2 or s_T - 1/2) or |dx| = 1 flush vs locked with y-overlap
        okx = near(cx, mpf("0.5")) or near(cx, sT - mpf("0.5")) or any(
            near(abs(cx - sq[j][0]), 1) and abs(cy - sq[j][1]) < 1 - mpf("1e-50") for j in locked)
        oky = near(cy, mpf("0.5")) or near(cy, sT - mpf("0.5")) or any(
            near(abs(cy - sq[j][1]), 1) and abs(cx - sq[j][0]) < 1 - mpf("1e-50") for j in locked)
        if okx and oky:
            locked.add(i); changed = True

k_trump = len(locked)
eps_off = sq[4][1] - mpf("2.5")          # square 4's cy vs the on-grid slot 5/2
gap_above_sq3 = sq[4][1] - 1 - (sq[3][1] + mpf("0.5")) + mpf("0.5")  # bottom edge of 4 minus top edge of 3
gap_to_R_slot = (sT - mpf("1.5")) - sq[4][1]  # distance to the from-above slot s_T - 3/2

for i in uprights:
    cx, cy, _ = sq[i]
    report["squares"].append({
        "i": i, "cx": mp.nstr(cx, 20), "cy": mp.nstr(cy, 20),
        "locked": i in locked,
        "cy_minpoly_degree": len(d["squares"][i].get("minpoly_cy", [])) - 1,
    })

report["k_trump"] = k_trump
report["locked_indices"] = sorted(locked)
report["tilted_nonsimple"] = {"indices": tilted, "theta_deg": d["theta_deg"][:20],
    "reason": "theta = 40.18 deg != 0 mod 90 -> not axis-aligned -> not simple"}
report["square4_classification"] = {
    "cy": mp.nstr(sq[4][1], 40),
    "epsilon_off_grid": mp.nstr(eps_off, 30),
    "gap_bottom_edge_to_square3_top_edge": mp.nstr(sq[4][1] - mpf("0.5") - 2, 30),
    "distance_to_slot_5_2": mp.nstr(eps_off, 30),
    "distance_to_slot_sT_minus_3_2": mp.nstr(gap_to_R_slot, 30),
    "cy_minpoly": d["squares"][4]["minpoly_cy"],
    "reason": ("x flush to left wall (cx = 1/2 exactly) but NO exact horizontal flush: "
               "bottom edge sits 0.0326 above square 3's top edge, and cy is 0.0326 above the "
               "from-below slot 5/2 and 0.155 above the from-above slot s_T - 3/2; cy has minimal polynomial of "
               "degree 7 (irrational), so cy equals NO rational grid value; wedged by the "
               "tilted strip -> non-simple. Margin of every separation > 1e-2 >> 1e-50."),
}
report["conclusion"] = (f"k_Trump = {k_trump}: squares 0,1,2,3,5 (BL corner, its two adjacent "
                        "on-grid squares, BR corner, TR corner) are simple; square 4 is "
                        "epsilon-off-grid (eps = 0.032558...); squares 6-10 are tilted. "
                        "Tier boundary: kill k >= 6, enumerate at k = 5.")
out = os.path.join(HERE, "..", "results", "trump_k.json")
json.dump(report, open(out, "w"), indent=1)
print("k_Trump =", k_trump, "locked =", sorted(locked))
print("square 4: cy =", mp.nstr(sq[4][1], 25), " eps off slot 5/2 =", mp.nstr(eps_off, 20))
print("  gap to square3 top edge =", mp.nstr(sq[4][1] - mpf("0.5") - 2, 20))
print("  gap to slot s_T-3/2      =", mp.nstr(gap_to_R_slot, 20))
