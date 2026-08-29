"""A47 leg (c): majority composition for flush-free NON-thin critical structures at s <= s0.

Thin branch is EMPTY by Theorem T1 (notes/theory.md) at every s in [3.82, s0] except
s* = 2 sqrt2 + 1 (handled by the leg-a s* lemma). This script prices the non-thin branch.

Two accountings, both exact Fractions where inputs are exact:
  FORCED  : every charge at the minimum its hypothesis actually forces
            (WC tilt unbounded below -> min bin; zone occupants' bins unforced -> table min
             over feasible entries; interiors -> 0). The honest composition value.
  GRANTALL: every contact at its maximal bin, both zone primitives at table max,
            interiors at the sharp-CC max — the fantasy ceiling (upper accounting, so
            region-overlap/double-count concerns only overstate, which is the sound
            direction for a "cannot fire" verdict).

Profiles: A46 composition_report sect 5a honest minima (L1/L6/L7/L11 + planarity):
  (name, n_WC, n_int): NONTHIN k_H=3 (3,3); k_H=4 (2,5); k_H=5 (2,7);
  k_H=3 2axes (4,3); k_H=11 all-loaded (4,16). Caps: N1 <= 12, n_contacts <= 35.
"""
import json, sys, os
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
A46R = os.path.join(ROOT, "attempts", "A46-balanced-wedge", "results")
A47R = os.path.join(ROOT, "attempts", "A47-corner-majority", "results")

S0 = F(969271, 250000)
B0 = S0 * S0 - 11
W_WC_MAX = F(453, 2048)      # A46 exact, bin (40,45]
W_WC_MIN = F(0)              # bin (0.5,1] certifies 0; tilt not bounded below
CE_MAX = F(29, 4096)         # A46 exact
CC_SHARP_MAX = F(289, 4096)  # A46 exact
INT_MAX = CC_SHARP_MAX       # generous interior price (upper accounting)
INT_MIN = F(0)

def load_table(path):
    """Return (min, max) over shipped feasible entries; entries carry exact 'area' Fractions."""
    if not os.path.exists(path):
        return None, None, None
    d = json.load(open(path))
    vals = []
    ent = (d.get("table_delta") or d.get("table") or d.get("table_refined")
           or d.get("entries") or [])
    if isinstance(ent, dict):
        ent = list(ent.values())
    for e in ent:
        if isinstance(e, dict):
            if e.get("status", "").upper().startswith("INF"):
                continue
            a = e.get("area_exact", e.get("area"))
            if a is None:
                continue
            vals.append(F(a) if isinstance(a, str) else F(a).limit_denominator(10**12))
    if not vals:
        return None, None, d
    return min(vals), max(vals), d

def main():
    cmin, cmax, _ = load_table(os.path.join(A47R, "primitives_corner.json"))
    smin, smax, _ = load_table(os.path.join(A47R, "primitives_side.json"))
    have = cmin is not None
    profiles = [
        ("NONTHIN kH=3 1axis", 3, 3),
        ("NONTHIN kH=4 1axis", 2, 5),
        ("NONTHIN kH=5 1axis", 2, 7),
        ("NONTHIN kH=3 2axes", 4, 3),
        ("NONTHIN kH=11 all-loaded", 4, 16),
    ]
    out = {"what": "A47 leg (c) majority composition, flush-free non-thin branch, s <= s0",
           "B0": str(B0), "B0_float": float(B0),
           "corner_table": {"min": str(cmin) if have else None, "max": str(cmax) if have else None},
           "side_table": {"min": str(smin) if smin is not None else None,
                           "max": str(smax) if smax is not None else None},
           "profiles": []}
    csm = cmin if have else F(0); cbg = cmax if have else F(0)
    ssm = smin if smin is not None else F(0); sbg = smax if smax is not None else F(0)
    for name, nwc, nint in profiles:
        forced = nwc * W_WC_MIN + nint * INT_MIN + csm + ssm
        grantall = nwc * W_WC_MAX + nint * INT_MAX + cbg + sbg
        out["profiles"].append({
            "profile": name, "n_WC": nwc, "n_int": nint,
            "forced_sum": str(forced), "forced_float": float(forced),
            "forced_fires": forced > B0,
            "grantall_sum": str(grantall), "grantall_float": float(grantall),
            "grantall_fires": grantall > B0,
            "grantall_shortfall_factor": float(B0 / grantall) if grantall > 0 else None,
        })
    # absolute ceiling: N1<=12 walls at max, 23 interiors at max, both zones at max
    ceil_all = 12 * W_WC_MAX + 23 * INT_MAX + cbg + sbg
    ceil_ce = 12 * W_WC_MAX + 23 * CE_MAX + cbg + sbg
    out["absolute_ceiling"] = {
        "walls12_int23_sharpCC_plus_zones": {"sum": str(ceil_all), "float": float(ceil_all),
                                             "fires": ceil_all > B0},
        "walls12_int23_CEonly_plus_zones": {"sum": str(ceil_ce), "float": float(ceil_ce),
                                            "fires": ceil_ce > B0},
    }
    # enlarged fire zone: which (n_WC, n_int) count-lattice points could conceivably fire
    # even after granting both zone primitives at their table maxima
    fire = []
    for nwc in range(0, 13):
        for nint in range(0, 36 - nwc):
            if nwc * W_WC_MAX + nint * CC_SHARP_MAX + cbg + sbg > B0:
                fire.append([nwc, nint])
    fire_min = sorted(fire, key=lambda p: p[0] + p[1])[:8]
    out["fire_zone"] = {
        "n_points": len(fire),
        "min_total_contact_points": fire_min,
        "note": ("counts needing nwc*maxWC + nint*maxSharpCC + cornerMax + sideMax > B0; "
                 "A46's zone-free fire zone was 5 points; atlas max is 3 WC + 1 aligned CC "
                 "(charge 0) — still nothing real within reach"),
    }
    out["a26_population_note"] = (
        "A26 (universal, exact): at most 9 squares within 2.503 deg of axis-parallel, so every "
        "11-packing has >= 2 mid-tilt squares. This bounds the near-upright POPULATION but "
        "forces neither zone membership nor wall contact for the mid-tilt squares, so it adds "
        "0 to the FORCED sum; it would matter only jointly with a (nonexistent) positional "
        "lemma pinning a mid-tilt square to a corner zone.")
    out["note_ownership"] = ("GRANTALL/ceiling are upper accountings (overlaps only overstate). "
                             "FORCED uses table minima; zone occupant bins are not forced by any "
                             "known lemma (rattler evasion), WC tilts not bounded below (A46: no delta_0).")
    dst = os.path.join(A47R, "composition_a47.json")
    json.dump(out, open(dst, "w"), indent=1)
    print("written", dst, "| tables loaded:", have, smin is not None)
    for p in out["profiles"]:
        print(f"{p['profile']:28s} forced {p['forced_float']:.4f} fires={p['forced_fires']}"
              f" | grantall {p['grantall_float']:.4f} fires={p['grantall_fires']}"
              f" (x{p['grantall_shortfall_factor'] and round(p['grantall_shortfall_factor'],2)} short)")
    ca = out["absolute_ceiling"]
    print("ceiling sharpCC:", ca["walls12_int23_sharpCC_plus_zones"]["float"],
          "fires=", ca["walls12_int23_sharpCC_plus_zones"]["fires"])
    print("ceiling CEonly :", ca["walls12_int23_CEonly_plus_zones"]["float"],
          "fires=", ca["walls12_int23_CEonly_plus_zones"]["fires"])

if __name__ == "__main__":
    main()
