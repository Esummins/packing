"""
A55 leg 0: the 14 k = 4 Young classes, their names, and the containment lattice.

Reads A53's results/skeletons_young.json (never writes it).  Emits, into A55/results/:
  name_to_slots.json      k4_00..k4_13 (+ trump5, corners4 aliases) -> float slot lists
  k4_lattice.json         for each k4 class: which k=5 / k=6 classes contain it (up to D4),
                          whether it is contained in trump5 (=> PROVABLY ALIVE, never kill),
                          and which of A53/A54's certified kills already cover its supersets.

Containment is tested up to the container's D4 symmetry: class A (slot set) is "contained in"
class B iff some D4 image of A is a subset of some D4 image of B (equivalently: some D4 image
of A is a subset of B, since D4 is a group).
"""
import json, os, sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
A53 = os.path.abspath(os.path.join(BASE, "..", "A53-simple-strata"))
sys.path.insert(0, HERE)
from skeletons import S0, d4_images, canon, TRUMP


def frs(pairs):
    return frozenset((Fr(x), Fr(y)) for (x, y) in pairs)


def contained(A, B):
    """some D4 image of A is a subset of B (A, B frozensets of exact slot points)"""
    for img in d4_images(A):
        if img <= B:
            return True
    return False


def main():
    d = json.load(open(os.path.join(A53, "results", "skeletons_young.json")))
    by_k = {}
    for cl in d["classes"]:
        by_k.setdefault(cl["k"], []).append(
            frozenset((Fr(x), Fr(y)) for x, y in cl["slots"]))
    trump = frozenset(TRUMP)
    trump_c = canon(trump)

    n2s_a53 = json.load(open(os.path.join(A53, "results", "name_to_slots.json")))
    # A53's name_to_slots stores floats; compare on rounded floats, not exact Fractions
    corners4_f = set((round(x, 9), round(y, 9)) for x, y in n2s_a53["corners4"])

    k4 = by_k[4]
    names, name_to_slots, lattice = [], {}, {}
    for i, S in enumerate(k4):
        nm = f"k4_{i:02d}"
        names.append(nm)
        name_to_slots[nm] = [[float(x), float(y)] for (x, y) in sorted(S)]
        in_trump = contained(S, trump)
        is_corners4 = any(set((round(float(x), 9), round(float(y), 9)) for (x, y) in img) == corners4_f
                          for img in d4_images(S))
        sup5 = [j for j, T in enumerate(by_k[5]) if contained(S, T)]
        sup6 = [j for j, T in enumerate(by_k[6]) if contained(S, T)]
        lattice[nm] = dict(
            slots=[[str(x), str(y)] for (x, y) in sorted(S)],
            slots_float=name_to_slots[nm],
            in_trump5=in_trump, is_corners4=is_corners4,
            n_sup_k5=len(sup5), n_sup_k6=len(sup6),
            sup_k5_idx=sup5, sup_k6_idx=sup6,
        )
    # k5 class index -> A53 name (trump excluded from the k5_XX numbering, as in campaign53)
    k5_names, i5 = {}, 0
    for j, T in enumerate(by_k[5]):
        if canon(T) == trump_c:
            k5_names[j] = "trump5"
        else:
            k5_names[j] = f"k5_{i5:02d}"; i5 += 1
    for nm in names:
        lattice[nm]["sup_k5"] = sorted(k5_names[j] for j in lattice[nm]["sup_k5_idx"])
        lattice[nm]["sup_k6"] = [f"k6_{j:02d}" for j in lattice[nm]["sup_k6_idx"]]
        assert ("trump5" in lattice[nm]["sup_k5"]) == lattice[nm]["in_trump5"]

    name_to_slots["corners4"] = n2s_a53["corners4"]
    name_to_slots["trump5"] = n2s_a53["trump5"]
    os.makedirs(os.path.join(BASE, "results"), exist_ok=True)
    json.dump(name_to_slots, open(os.path.join(BASE, "results", "name_to_slots.json"), "w"), indent=1)
    json.dump(dict(k5_index_to_name=k5_names, classes=lattice),
              open(os.path.join(BASE, "results", "k4_lattice.json"), "w"), indent=1, default=str)

    print(f"{len(names)} k=4 classes")
    for nm in names:
        L = lattice[nm]
        tag = []
        if L["in_trump5"]:
            tag.append("SUBSET-OF-TRUMP5 (provably alive, NEVER KILL)")
        if L["is_corners4"]:
            tag.append("corners4 (A14/A16 baseline)")
        print(f"  {nm} {[[round(x,4), round(y,4)] for x,y in L['slots_float']]}"
              f"  sup: {L['n_sup_k5']} k5 / {L['n_sup_k6']} k6   {'; '.join(tag)}")


if __name__ == "__main__":
    main()
