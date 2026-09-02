#!/usr/bin/env python3
"""A72 — exact diff of the clean-room census (A72) against A53's implementation.

Run ONLY after ../results/sha256s is frozen.  Reads A53's code read-only (imports
skeletons.py's predicates and replays skeletons2.py's enumeration in-process; A53's own
result files and directories are never written).  Writes ../results/diff_report.json.

Diff levels
  D1 slot-set level (convention-free): the 1110 sets of exact rational plane points.
  D2 orbit partition (representative-free): the induced partition into D4 classes.
  D3 the D4 groups themselves: A72's 8 plane maps vs A53's `d4_images`, as maps on slots.
  D4 canonical representatives: A72's L4c convention vs A53's `canon`.
  D5 A53's 163 stored class records in results/skeletons_young.json.
  D6 Trump canary.
"""
import itertools
import json
import os
import sys
from fractions import Fraction as Q

HERE = os.path.dirname(os.path.abspath(__file__))
A72 = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(A72, "..", ".."))
A53 = os.path.join(REPO, "attempts", "A53-simple-strata")

sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(A53, "code"))

import enum_census as A72M                                    # noqa: E402
from skeletons import S0, HALF, overlap, d4_images, canon, TRUMP   # noqa: E402  (A53)

assert S0 == A72M.S0, "side mismatch"

# ---------------------------------------------------------------------------------------
# Replay of A53 skeletons2.py's enumeration, in-process, writing nothing.
# (verbatim logic from that file; the heavy recursive-BFS cross-check is NOT invoked)
# ---------------------------------------------------------------------------------------
PARTS = [tuple(l) for l in itertools.product(range(4), repeat=3) if l[0] >= l[1] >= l[2]]
CORNERS53 = {"BL": (HALF, HALF, 1, 1), "BR": (S0 - HALF, HALF, -1, 1),
             "TR": (S0 - HALF, S0 - HALF, -1, -1), "TL": (HALF, S0 - HALF, 1, -1)}
ORDER = ["BL", "BR", "TR", "TL"]


def cells53(lam):
    return [(i, j) for j, lj in enumerate(lam) for i in range(lj)]


def slots53(corner, lam):
    x0, y0, sx, sy = CORNERS53[corner]
    return [(x0 + sx * i, y0 + sy * j) for (i, j) in cells53(lam)]


def a53_enumerate():
    slotmap = {c: {lam: slots53(c, lam) for lam in PARTS} for c in CORNERS53}

    def compatible(A, B):
        return all(not overlap(p, q) for p in A for q in B)

    tuples = []
    for lBL in PARTS:
        A = slotmap["BL"][lBL]
        for lBR in PARTS:
            B = slotmap["BR"][lBR]
            if not compatible(A, B):
                continue
            for lTR in PARTS:
                C = slotmap["TR"][lTR]
                if not (compatible(A, C) and compatible(B, C)):
                    continue
                for lTL in PARTS:
                    D = slotmap["TL"][lTL]
                    if not (compatible(A, D) and compatible(B, D) and compatible(C, D)):
                        continue
                    tuples.append((lBL, lBR, lTR, lTL))
    sets = {}
    for tp in tuples:
        S = frozenset(s for c, lam in zip(ORDER, tp) for s in slotmap[c][lam])
        sets.setdefault(S, []).append(tp)
    classes = {}
    for S in sets:
        classes.setdefault(canon(S), set()).add(S)
    return tuples, sets, classes


# ---------------------------------------------------------------------------------------
# A72 side: decode the frozen census file into plane slot-sets.
# ---------------------------------------------------------------------------------------
def a72_load():
    with open(os.path.join(A72, "results", "census_cleanroom.json"), encoding="utf-8") as f:
        d = json.load(f)

    def decode(enc):
        pts = []
        for ci, part in enumerate(enc.split("|")):
            for t in range(0, len(part), 2):
                i, j = int(part[t]), int(part[t + 1])
                pts.append(A72M.slot_point(ci, i, j))
        return frozenset(pts)

    sets = {}
    for enc in d["tuples"]:
        S = decode(enc)
        sets.setdefault(S, []).append(enc)
    classes = {}
    for rep, members in d["classes"].items():
        classes[rep] = frozenset(decode(m) for m in members)
    return d, sets, classes, decode


def main():
    d72, sets72, classes72, decode = a72_load()
    tup53, sets53, classes53 = a53_enumerate()

    R = {"a72_sha256": d72["sha256"], "a72_file_frozen_before_diff": True}

    # ---- D1 slot-set level -------------------------------------------------------------
    only72 = sorted(str(sorted(map(str, S))) for S in set(sets72) - set(sets53))
    only53 = sorted(str(sorted(map(str, S))) for S in set(sets53) - set(sets72))
    R["D1_slot_sets"] = {
        "a72_n_tuples": len(d72["tuples"]),
        "a53_n_tuples": len(tup53),
        "a72_n_distinct_slot_sets": len(sets72),
        "a53_n_distinct_slot_sets": len(sets53),
        "a72_tuple_to_set_injective": all(len(v) == 1 for v in sets72.values()),
        "a53_tuple_to_set_injective": all(len(v) == 1 for v in sets53.values()),
        "only_in_a72": only72,
        "only_in_a53": only53,
        "MATCH": (not only72) and (not only53) and len(sets72) == len(sets53),
    }
    R["D1_census_by_k"] = {
        "a72": d72["census_by_k"],
        "a53": {str(k): sum(1 for t in tup53 if sum(sum(l) for l in t) == k)
                for k in sorted({sum(sum(l) for l in t) for t in tup53})},
    }
    R["D1_census_by_k"]["MATCH"] = R["D1_census_by_k"]["a72"] == R["D1_census_by_k"]["a53"]

    # ---- D2 orbit partition (representative-free) --------------------------------------
    part72 = {frozenset(v) for v in classes72.values()}
    part53 = {frozenset(v) for v in classes53.values()}
    R["D2_orbit_partition"] = {
        "a72_n_classes": len(part72),
        "a53_n_classes": len(part53),
        "orbits_only_in_a72": len(part72 - part53),
        "orbits_only_in_a53": len(part53 - part72),
        "MATCH": part72 == part53,
    }
    R["D2_classes_by_k"] = {
        "a72": d72["classes_by_k"],
        "a53": {str(k): sum(1 for c in classes53 if len(c) == k)
                for k in sorted({len(c) for c in classes53})},
    }
    R["D2_classes_by_k"]["MATCH"] = R["D2_classes_by_k"]["a72"] == R["D2_classes_by_k"]["a53"]
    R["D2_orbit_size_histogram"] = {
        "a72": d72["orbit_size_histogram"],
        "a53": {str(n): sum(1 for o in part53 if len(o) == n)
                for n in sorted({len(o) for o in part53})},
    }
    R["D2_orbit_size_histogram"]["MATCH"] = (
        R["D2_orbit_size_histogram"]["a72"] == R["D2_orbit_size_histogram"]["a53"])

    # ---- D3 the two D4 groups, as maps on the slot lattice -----------------------------
    allslots = frozenset(p for S in sets72 for p in S)
    g72 = {frozenset((str(p), str(A72M.apply_g(M, p))) for p in allslots)
           for M in A72M.d4_matrices()}
    # A53's `d4_images` returns images of a SET, which loses the per-point pairing; rebuild the
    # same 8 maps element-wise from that function's own body (rot/refl loop, verbatim), and
    # cross-check the set-level result against it below.
    g53 = set()
    for rot in range(4):
        for refl in (False, True):
            pairs = []
            for (x, y) in allslots:
                a, b = x, y
                for _ in range(rot):
                    a, b = b, S0 - a
                if refl:
                    a = S0 - a
                pairs.append((str((x, y)), str((a, b))))
            g53.add(frozenset(pairs))
    # cross-check the element-wise rebuild against A53's own set-level d4_images
    imgs53_setlevel = set(d4_images(allslots))
    imgs53_rebuilt = {frozenset(eval(b, {"Fraction": Q}) for _, b in m) for m in g53}  # noqa: S307
    R["D3_rebuild_matches_a53_d4_images"] = (imgs53_setlevel == imgs53_rebuilt)
    R["D3_d4_group"] = {
        "n_slots_in_lattice": len(allslots),
        "a72_n_distinct_maps": len(g72),
        "a53_n_distinct_maps": len(g53),
        "MATCH": g72 == g53,
        "note": "the two groups are compared as sets of graphs of maps on the slot lattice",
    }

    # ---- D4 canonical representatives ---------------------------------------------------
    # A72 rep (L4c: lex-min of the corner-major cell encoding) vs A53 rep (lex-min of the
    # sorted plane-coordinate tuple).  Convention differs; check same-orbit agreement.
    rep_same, rep_diff = 0, []
    set_to_orbit53 = {}
    for cn, members in classes53.items():
        for S in members:
            set_to_orbit53[S] = cn
    for rep72enc, members72 in classes72.items():
        S72 = decode(rep72enc)
        cn53 = set_to_orbit53[S72]
        rep53 = frozenset(cn53)
        if rep53 == S72:
            rep_same += 1
        else:
            rep_diff.append({"a72_rep": rep72enc,
                             "a53_rep": [[str(x), str(y)] for (x, y) in sorted(cn53)]})
        assert rep53 in members72, "A53 rep left A72's orbit"
    R["D4_representatives"] = {
        "n_classes": len(classes72),
        "identical_representative": rep_same,
        "different_representative_same_orbit": len(rep_diff),
        "a53_rep_always_inside_a72_orbit": True,
        "MATCH_canonicalisation": (len(part72 - part53) == 0 and len(part53 - part72) == 0),
        "note": ("representative choice is convention (A72 notes/ambiguities.md L4c) and is NOT "
                 "a correctness criterion; the invariant D2 partition is."),
        "sample_differences": rep_diff[:5],
    }

    # ---- D5 A53's stored class records ---------------------------------------------------
    with open(os.path.join(A53, "results", "skeletons_young.json"), encoding="utf-8") as f:
        y = json.load(f)
    stored = [frozenset((Q(a), Q(b)) for a, b in c["slots"]) for c in y["classes"]]
    orbit_of72 = {}
    for rep72enc, members in classes72.items():
        for S in members:
            orbit_of72[S] = rep72enc
    hit = [orbit_of72.get(S) for S in stored]
    R["D5_stored_file"] = {
        "file": "attempts/A53-simple-strata/results/skeletons_young.json",
        "n_tuples_raw": y["n_tuples_raw"], "n_sets_raw": y["n_sets_raw"],
        "n_classes_d4": y["n_classes_d4"],
        "census_raw_by_k_matches_a72": y["census_raw_by_k"] == d72["census_by_k"],
        "census_d4_by_k_matches_a72": y["census_d4_by_k"] == d72["classes_by_k"],
        "n_stored_reps": len(stored),
        "stored_reps_all_in_a72_census": all(S in sets72 for S in stored),
        "stored_reps_hit_distinct_a72_orbits": len(set(hit)) == len(stored) and None not in hit,
        "stored_reps_cover_all_a72_orbits": set(hit) == set(classes72),
        "MATCH": (y["n_tuples_raw"] == len(d72["tuples"])
                  and y["n_classes_d4"] == len(classes72)
                  and y["census_raw_by_k"] == d72["census_by_k"]
                  and y["census_d4_by_k"] == d72["classes_by_k"]
                  and all(S in sets72 for S in stored)
                  and set(hit) == set(classes72)),
    }

    # ---- D6 Trump canary ------------------------------------------------------------------
    trump72 = [decode(e) for e in d72["trump"]["matched_tuples"]]
    R["D6_trump"] = {
        "a72_matched_tuples": len(trump72),
        "a72_k": d72["checks"]["trump_k"],
        "a53_TRUMP_set": [[str(x), str(y)] for (x, y) in sorted(TRUMP)],
        "a72_trump_in_census": all(S in sets72 for S in trump72),
        "a53_TRUMP_in_a72_census": TRUMP in sets72,
        "same_orbit": (len(trump72) == 1 and orbit_of72[trump72[0]] == orbit_of72[TRUMP]),
        "a53_stored_trump_rep_in_same_orbit": any(
            c["is_trump"] and orbit_of72[frozenset((Q(a), Q(b)) for a, b in c["slots"])]
            == orbit_of72[TRUMP] for c in y["classes"]),
        "lambda_convention_note": ("A53 indexes lambda by ROW (cells53: row j has lam[j] cells); "
                                   "A72 by COLUMN (ambiguities.md L1c/L2c). The two lambda "
                                   "labellings are transposes; the slot sets are identical."),
    }
    R["D6_trump"]["MATCH"] = (R["D6_trump"]["a53_TRUMP_in_a72_census"]
                              and R["D6_trump"]["same_orbit"]
                              and R["D6_trump"]["a53_stored_trump_rep_in_same_orbit"])

    R["VERDICT"] = ("MATCH" if all(R[k]["MATCH"] for k in
                                   ["D1_slot_sets", "D1_census_by_k", "D2_orbit_partition",
                                    "D2_classes_by_k", "D2_orbit_size_histogram",
                                    "D3_d4_group", "D5_stored_file", "D6_trump"])
                    else "MISMATCH")

    outp = os.path.join(A72, "results", "diff_report.json")
    with open(outp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(R, f, indent=1)
        f.write("\n")

    print("VERDICT:", R["VERDICT"])
    for k in sorted(R):
        if isinstance(R[k], dict) and "MATCH" in R[k]:
            print("  %-28s %s" % (k, R[k]["MATCH"]))
    print("  D4 representatives identical: %d / %d (convention, not correctness)"
          % (R["D4_representatives"]["identical_representative"], len(classes72)))
    print("  ->", outp)
    return 0


if __name__ == "__main__":
    sys.exit(main())
