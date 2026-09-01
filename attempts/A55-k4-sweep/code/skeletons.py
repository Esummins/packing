"""
A53 leg (a): exact enumeration of simple-square skeletons at s0 = 969271/250000.

Definitions (I-L20, docs/ideas.md; formalized in notes/lemmas.md):
  A square of a packing is SIMPLE (grid-locked) iff it is axis-aligned and belongs to some
  recursively-locked set: each member has an x-support (left/right edge on a wall, or a
  positive-length vertical edge contact with an earlier member at |dx| = 1) AND a y-support
  (bottom/top edge on a wall, or a positive-length horizontal edge contact at |dy| = 1).
  Simp(P) = union of all recursively-locked subsets of P (closed under union => well-defined).

  Consequence (exact grid): both centre coordinates of a simple square lie in
      X = ({1/2 + i} u {s0 - 1/2 - j}) n [1/2, s0 - 1/2],  i, j in Z>=0,
  because wall contact pins a coordinate to 1/2 or s0-1/2 and each locked-locked flush step
  moves it by exactly +-1, and cross-family steps of exactly 1 do not exist at s0
  (s0 - m - n is never an integer for the relevant small m, n; verified below).

  A SKELETON is any possible value of Simp(P): a set of pairwise interior-disjoint slot
  squares that is recursively locked. This script enumerates ALL of them exactly (Fractions),
  reduces by D4, and identifies Trump's k = 5 skeleton.

Output: results/skeletons.json (census + all D4 classes with exact coordinates).
"""
import json, sys, itertools
from fractions import Fraction as Fr

S0 = Fr(969271, 250000)
HALF = Fr(1, 2)

def slot_values():
    L, R = [], []
    v = HALF
    while v <= S0 - HALF:
        L.append(v); v += 1
    v = S0 - HALF
    while v >= HALF:
        R.append(v); v -= 1
    vals = sorted(set(L + R))
    return vals, L, R

VALS, LFAM, RFAM = slot_values()

def check_no_cross_step():
    """no two slot values differ by exactly 1 across families (so the slot set is closed
    under flush steps) -- and record which pairs differ by exactly 1 (within-family)."""
    ones, cross = [], []
    for a, b in itertools.combinations(VALS, 2):
        d = abs(a - b)
        if d == 1:
            ones.append((a, b))
            if (a in LFAM) != (b in LFAM):
                cross.append((a, b))
    return ones, cross

def overlap(p, q):
    """open interiors intersect (touching allowed)"""
    return abs(p[0] - q[0]) < 1 and abs(p[1] - q[1]) < 1

def supported(p, placed):
    """is slot p doubly supported by walls u placed (exact)?"""
    okx = p[0] == HALF or p[0] == S0 - HALF or any(
        abs(p[0] - q[0]) == 1 and abs(p[1] - q[1]) < 1 for q in placed)
    oky = p[1] == HALF or p[1] == S0 - HALF or any(
        abs(p[1] - q[1]) == 1 and abs(p[0] - q[0]) < 1 for q in placed)
    return okx and oky

SLOTS = [(x, y) for x in VALS for y in VALS]

def enumerate_skeletons():
    """BFS over recursively-locked sets (frozensets of slots)."""
    seen = {frozenset()}
    frontier = [frozenset()]
    while frontier:
        nxt = []
        for A in frontier:
            for p in SLOTS:
                if p in A:
                    continue
                if any(overlap(p, q) for q in A):
                    continue
                if not supported(p, A):
                    continue
                B = A | {p}
                if B not in seen:
                    seen.add(B); nxt.append(B)
        frontier = nxt
    return seen

def d4_images(A):
    out = []
    for rot in range(4):
        for refl in (False, True):
            B = []
            for (x, y) in A:
                a, b = x, y
                for _ in range(rot):
                    a, b = b, S0 - a
                if refl:
                    a = S0 - a
                B.append((a, b))
            out.append(frozenset(B))
    return out

def canon(A):
    return min((tuple(sorted(im)) for im in d4_images(A)))

TRUMP = frozenset({(HALF, HALF), (Fr(3, 2), HALF), (HALF, Fr(3, 2)),
                   (S0 - HALF, HALF), (S0 - HALF, S0 - HALF)})

def main():
    ones, cross = check_no_cross_step()
    assert not cross, f"cross-family exact-1 steps exist: {cross}"
    all_sets = enumerate_skeletons()
    classes = {}
    for A in all_sets:
        c = canon(A)
        classes.setdefault(c, 0)
        classes[c] += 1
    census_raw, census_d4 = {}, {}
    for A in all_sets:
        census_raw[len(A)] = census_raw.get(len(A), 0) + 1
    for c in classes:
        census_d4[len(c)] = census_d4.get(len(c), 0) + 1
    trump_canon = canon(TRUMP)
    assert trump_canon in classes, "Trump skeleton missing!"
    out = {
        "s0": str(S0), "slot_values": [str(v) for v in VALS],
        "slot_families": {"L": [str(v) for v in LFAM], "R": [str(v) for v in RFAM]},
        "within_family_unit_steps": [[str(a), str(b)] for a, b in ones],
        "cross_family_unit_steps": [],
        "n_locked_sets_raw": len(all_sets),
        "n_classes_d4": len(classes),
        "census_raw_by_k": {str(k): v for k, v in sorted(census_raw.items())},
        "census_d4_by_k": {str(k): v for k, v in sorted(census_d4.items())},
        "trump_canonical": [[str(x), str(y)] for (x, y) in trump_canon],
        "classes": [
            {"k": len(c), "slots": [[str(x), str(y)] for (x, y) in c],
             "slots_float": [[float(Fr(x)), float(Fr(y))] for (x, y) in c],
             "is_trump": c == trump_canon}
            for c in sorted(classes, key=lambda c: (len(c), c))
        ],
    }
    with open(sys.argv[1] if len(sys.argv) > 1 else "results/skeletons.json", "w") as f:
        json.dump(out, f, indent=1)
    print("locked sets (raw):", len(all_sets))
    print("D4 classes:", len(classes))
    print("census raw by k:", dict(sorted(census_raw.items())))
    print("census D4  by k:", dict(sorted(census_d4.items())))
    print("Trump canonical:", [(float(x), float(y)) for x, y in trump_canon])

if __name__ == "__main__":
    main()
