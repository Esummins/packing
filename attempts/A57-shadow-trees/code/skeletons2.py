"""
A53 leg (a), PRIMARY (PI's authoritative definition, 2026-08-31):

A square of a packing is SIMPLE iff it sits at integer distance from two perpendicular
container sides and is connected to both by gap-free flush support chains -- i.e., it is
part of a tiling grown in from a corner. Structural form (definitional here, see
notes/lemmas.md L1): the simple set of any packing is a 4-tuple of corner-anchored
Young diagrams (staircases): for corner c, cell (i,j) occupied => all (i',j') <= (i,j)
occupied. At s0 = 969271/250000 < 4 each diagram fits in 3x3 (offset 3 exceeds the
admissible band), and cross-corner compatibility = exact pairwise non-overlap of the
slot squares (this subsumes the shared-wall width constraint w + w' <= 3).

Enumerates all 4-tuples (lambda_BL, lambda_BR, lambda_TR, lambda_TL) of Young diagrams
in 3x3 whose slot-square union is pairwise interior-disjoint (exact Fractions),
D4-reduces, cross-checks against the recursive-BFS census (skeletons.py: the PI
definition is strictly stronger; every Young union is recursively locked, not conversely).

Output: results/skeletons_young.json
"""
import json, sys, os, itertools
from fractions import Fraction as Fr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skeletons import S0, HALF, overlap, d4_images, canon, TRUMP, enumerate_skeletons

# Young diagrams inside 3x3: partitions lambda1 >= lambda2 >= lambda3, 0 <= li <= 3
PARTS = [tuple(l) for l in itertools.product(range(4), repeat=3) if l[0] >= l[1] >= l[2]]

CORNERS = {
    "BL": (HALF, HALF, 1, 1),
    "BR": (S0 - HALF, HALF, -1, 1),
    "TR": (S0 - HALF, S0 - HALF, -1, -1),
    "TL": (HALF, S0 - HALF, 1, -1),
}

def cells(lam):
    """Young diagram cells (col i, row j): row j has lam[j] cells."""
    return [(i, j) for j, lj in enumerate(lam) for i in range(lj)]

def slots_of(corner, lam):
    x0, y0, sx, sy = CORNERS[corner]
    return [(x0 + sx * i, y0 + sy * j) for (i, j) in cells(lam)]

def main():
    tuples = []
    # precompute slot lists per (corner, partition)
    slotmap = {c: {lam: slots_of(c, lam) for lam in PARTS} for c in CORNERS}
    order = ["BL", "BR", "TR", "TL"]
    def compatible(A, B):
        return all(not overlap(p, q) for p in A for q in B)
    # incremental enumeration with pairwise pruning
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
    # canonicalize by geometry (D4 acts on the union of slots)
    classes = {}
    for tp in tuples:
        S = frozenset(s for c, lam in zip(order, tp) for s in slotmap[c][lam])
        cn = canon(S)
        classes.setdefault(cn, []).append(tp)
    census_raw, census_d4 = {}, {}
    for tp in tuples:
        k = sum(sum(l) for l in tp)
        census_raw[k] = census_raw.get(k, 0) + 1
    for cn in classes:
        census_d4[len(cn)] = census_d4.get(len(cn), 0) + 1
    trump_canon = canon(TRUMP)
    assert trump_canon in classes, "Trump skeleton missing from Young enumeration!"
    trump_shapes = classes[trump_canon][0]
    # cross-check: every Young union is recursively locked (PI def strictly stronger)
    bfs = enumerate_skeletons()
    young_sets = set()
    for tp in tuples:
        young_sets.add(frozenset(s for c, lam in zip(order, tp) for s in slotmap[c][lam]))
    not_in_bfs = [S for S in young_sets if S not in bfs]
    extra_bfs = len(bfs) - len(young_sets)
    out = {
        "s0": str(S0),
        "n_tuples_raw": len(tuples), "n_sets_raw": len(young_sets),
        "n_classes_d4": len(classes),
        "census_raw_by_k": {str(k): v for k, v in sorted(census_raw.items())},
        "census_d4_by_k": {str(k): v for k, v in sorted(census_d4.items())},
        "young_subset_of_bfs": len(not_in_bfs) == 0,
        "bfs_sets_not_young (recursive def strictly weaker)": extra_bfs,
        "trump_canonical": [[str(x), str(y)] for (x, y) in trump_canon],
        "trump_shapes_BL_BR_TR_TL": [list(l) for l in trump_shapes],
        "classes": [
            {"k": len(cn), "slots": [[str(x), str(y)] for (x, y) in cn],
             "slots_float": [[float(Fr(x)), float(Fr(y))] for (x, y) in cn],
             "is_trump": cn == trump_canon}
            for cn in sorted(classes, key=lambda c: (len(c), c))
        ],
    }
    with open("results/skeletons_young.json", "w") as f:
        json.dump(out, f, indent=1)
    print("tuples raw:", len(tuples), " distinct slot-sets:", len(young_sets))
    print("D4 classes:", len(classes))
    print("census raw:", dict(sorted(census_raw.items())))
    print("census D4 :", dict(sorted(census_d4.items())))
    print("Young subset of BFS:", len(not_in_bfs) == 0, "; BFS extras:", extra_bfs)
    print("Trump shapes (BL,BR,TR,TL):", trump_shapes)

if __name__ == "__main__":
    main()
