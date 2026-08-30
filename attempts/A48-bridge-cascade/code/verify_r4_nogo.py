# A48 Theorem C6: grant-all ceiling of the certified tables vs B0, exact.
# Loads the actual certified tables (A46 w_WC, A47 corner + side), takes their
# EXACT maxima, adds the interior CE cap (29/4096, A46 pilot; robustness x2
# variant) over the maximal contact count, and compares with B0 = s0^2 - 11.
# Profile granted (upper accounting, overlaps ignored upward):
#   n_WC = 12 wall contacts at the w_WC max bin (N1 <= 12),
#   3k+2 - n_WC = 23 interior contacts at the CE cap,
#   + corner-zone max + side-zone max (both zone occupants granted).
import json, os
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(HERE, "..", "results", "r4_nogo.json")

S0 = F(969271, 250000)
B0 = S0 * S0 - 11

def wc_max():
    d = json.load(open(os.path.join(ROOT, "attempts", "A46-balanced-wedge",
                                    "results", "w_wc_table.json")))
    vals = [F(e["w_WC"]) for e in d["entries"]]
    assert len(vals) == 11
    return max(vals)

def corner_max():
    d = json.load(open(os.path.join(ROOT, "attempts", "A47-corner-majority",
                                    "results", "primitives_corner.json")))
    best = F(0)
    for tab in ("table_theta", "table_delta"):
        for e in d[tab]:
            v = F(e["area_exact"])
            if v > best:
                best = v
    return best

def side_max():
    d = json.load(open(os.path.join(ROOT, "attempts", "A47-corner-majority",
                                    "results", "primitives_side.json")))
    best = F(0)
    for k in ("table_refined", "table_coarse_brief_cells"):
        for e in d.get(k, []):
            v = e.get("area_exact")
            if v is not None and F(v) > best:
                best = F(v)
    return best

def main():
    wWC, wCor, wSide = wc_max(), corner_max(), side_max()
    CE_CAP = F(29, 4096)          # A46 w_ce_cc_pilot max_CE (float-provenance)
    CC_CAP = F(289, 4096)         # sharp-CC cap, for the fire-zone remark
    n_wc, n_int = 12, 35 - 12
    ceil1 = n_wc * wWC + n_int * CE_CAP + wCor + wSide
    ceil2 = n_wc * wWC + n_int * (2 * CE_CAP) + wCor + wSide   # robustness x2
    # all-sharp-CC variant (NOT forced by anything; needs >= 10 WC + >= 6 CC per A47)
    ceil_cc = n_wc * wWC + n_int * CC_CAP + wCor + wSide
    out = {"what": "A48 Theorem C6: exact grant-all ceiling vs B0",
           "B0": str(B0), "B0_float": float(B0),
           "w_WC_max": str(wWC), "corner_max": str(wCor), "side_max": str(wSide),
           "CE_cap": str(CE_CAP), "CC_cap": str(CC_CAP),
           "profile": {"n_WC": n_wc, "n_interior": n_int,
                       "zones": "corner + side maxima granted"},
           "ceiling_CE_interiors": str(ceil1), "ceiling_float": float(ceil1),
           "ratio_to_B0": float(ceil1 / B0),
           "shortfall": str(B0 - ceil1), "shortfall_float": float(B0 - ceil1),
           "ceiling_CE_cap_doubled": str(ceil2),
           "ceiling_CE_cap_doubled_lt_B0": ceil2 < B0,
           "ceiling_all_sharp_CC": str(ceil_cc),
           "ceiling_all_sharp_CC_float": float(ceil_cc),
           "note_cc": "sharp-CC variant exceeds B0 only in a fire zone needing "
                      ">= 10 WC AND >= 6 sharp-CC simultaneously (A47); the "
                      "cascade forces zero CC contacts (theory sect. 5).",
           "verdict_nogo": ceil1 < B0}
    assert ceil1 < B0 and ceil2 < B0, "no-go ceiling unexpectedly reaches B0"
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w"), indent=1)
    print("PASS r4_nogo: ceiling =", float(ceil1), "=", float(ceil1 / B0), "B0;",
          "doubled-CE variant", float(ceil2), "< B0:", ceil2 < B0,
          "; all-sharp-CC", float(ceil_cc))

if __name__ == "__main__":
    main()
