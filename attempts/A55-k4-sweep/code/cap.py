"""
A55 leg 3: the post-sweep EMPTINESS MAP -- the exact statement of A53's L5 cap after k = 4.

Kill semantics (A53 L5): an exact certificate for pin-set S empties EVERY stratum whose skeleton
CONTAINS S (up to D4).  So the emptiness map is: a Young class C (any k) is certifiably empty iff
some certified pin-set is contained in C.

Inputs (read-only):
  A53  certs_wip/<name>.json.PASS        32 k=6 kills + 19 k=5 kills
  A54  certs/<name>.json.PASS            k6_23, k5_13
  A55  certs/<name>.json.PASS            this sweep's k=4 kills
Output: results/cap.json + a printed table of the census by k split into
  EMPTY (certified) / OPEN, with the witnessing minimal certified sub-pin-set for each empty class.
"""
import argparse, glob, json, os, sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
A53 = os.path.abspath(os.path.join(BASE, "..", "A53-simple-strata"))
A54 = os.path.abspath(os.path.join(BASE, "..", "A54-stragglers"))
sys.path.insert(0, HERE)
from skeletons import d4_images, canon, TRUMP


def certified_names():
    """{name: source} for every pin-set with a PASSing exact certificate"""
    got = {}
    for src, pat in (("A53", os.path.join(A53, "certs_wip", "*.json.PASS")),
                     ("A54", os.path.join(A54, "certs", "*.json.PASS")),
                     ("A55", os.path.join(BASE, "certs", "*.json.PASS"))):
        for p in glob.glob(pat):
            nm = os.path.basename(p).replace(".json.PASS", "")
            got.setdefault(nm, src)
    return got


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(BASE, "results", "cap.json"))
    a = ap.parse_args()

    d = json.load(open(os.path.join(A53, "results", "skeletons_young.json")))
    by_k = {}
    for cl in d["classes"]:
        by_k.setdefault(cl["k"], []).append(frozenset((Fr(x), Fr(y)) for x, y in cl["slots"]))
    trump = frozenset(TRUMP)
    trump_c = canon(trump)

    # name -> slot set, for every named node in A53 + A55
    slotname = {}
    for f, keys in ((os.path.join(A53, "results", "name_to_slots.json"), None),
                    (os.path.join(BASE, "results", "name_to_slots.json"), None)):
        for nm, sl in json.load(open(f)).items():
            slotname.setdefault(nm, [(round(x, 9), round(y, 9)) for x, y in sl])
    # index the classes by rounded-float canonical form so names <-> classes match
    def rf(S):
        return frozenset((round(float(x), 9), round(float(y), 9)) for x, y in S)
    cls_by_k_rf = {k: [rf(S) for S in v] for k, v in by_k.items()}

    def name_class_idx(nm):
        S = frozenset(slotname[nm])
        k = len(S)
        for j, C in enumerate(cls_by_k_rf[k]):
            if any(frozenset((round(float(x), 9), round(float(y), 9)) for x, y in img) == C
                   for img in d4_images(frozenset((Fr(x).limit_denominator(10**7), Fr(y).limit_denominator(10**7)) for x, y in S))):
                return j
        return None

    cert = certified_names()
    # certified pin-sets as EXACT class representatives (all D4 images, rounded-float)
    kill_imgs = []      # (name, k, [frozenset of rounded-float slot tuples] per D4 image)
    for nm, src in sorted(cert.items()):
        if nm not in slotname:
            continue
        S = frozenset((Fr(x).limit_denominator(10 ** 7), Fr(y).limit_denominator(10 ** 7))
                      for x, y in slotname[nm])
        imgs = [frozenset((round(float(x), 9), round(float(y), 9)) for x, y in img)
                for img in d4_images(S)]
        kill_imgs.append((nm, src, len(S), imgs))

    # A53 naming: at k=5 the campaign numbering SKIPS trump5, so class index != name index
    def label_of(k, j):
        if k != 5:
            return f"k{k}_{j:02d}"
        if canon(by_k[5][j]) == trump_c:
            return "trump5"
        return "k5_%02d" % sum(1 for jj in range(j) if canon(by_k[5][jj]) != trump_c)

    rows, detail = [], {}
    for k in sorted(by_k):
        empty, open_ = [], []
        for j, C in enumerate(cls_by_k_rf[k]):
            hits = [(nm, src, kk) for (nm, src, kk, imgs) in kill_imgs
                    if kk <= k and any(img <= C for img in imgs)]
            label = label_of(k, j)
            if hits:
                empty.append(label)
                hits.sort(key=lambda h: h[2])
                detail[label] = dict(status="EMPTY", witness=hits[0][0],
                                     witness_src=hits[0][1], witness_k=hits[0][2],
                                     n_witnesses=len(hits))
            else:
                open_.append(label)
                is_trump = (canon(by_k[k][j]) == trump_c)
                in_trump = any(img <= rf(trump) for img in
                               [frozenset((round(float(x), 9), round(float(y), 9)) for x, y in im)
                                for im in d4_images(by_k[k][j])])
                detail[label] = dict(status="OPEN", is_trump5=is_trump,
                                     subset_of_trump5=in_trump)
        rows.append(dict(k=k, n_classes=len(cls_by_k_rf[k]), n_empty=len(empty),
                         n_open=len(open_), open_classes=open_))

    print(f"certified pin-sets in the ledger: {len(kill_imgs)}  "
          f"({sum(1 for x in kill_imgs if x[2]==4)} at k=4, "
          f"{sum(1 for x in kill_imgs if x[2]==5)} at k=5, "
          f"{sum(1 for x in kill_imgs if x[2]==6)} at k=6)")
    print(f"{'k':>2s} {'classes':>8s} {'EMPTY':>6s} {'OPEN':>5s}   open classes")
    for r in rows:
        op = ", ".join(r["open_classes"])
        note = []
        for lb in r["open_classes"]:
            if detail[lb].get("is_trump5"):
                note.append(f"{lb}=trump5")
            elif detail[lb].get("subset_of_trump5"):
                note.append(f"{lb}<trump5")
        print(f"{r['k']:2d} {r['n_classes']:8d} {r['n_empty']:6d} {r['n_open']:5d}   {op}"
              + ("   [" + "; ".join(note) + "]" if note else ""))
    json.dump(dict(certified=[dict(name=n, src=s, k=kk) for (n, s, kk, _) in kill_imgs],
                   by_k=rows, classes=detail), open(a.out, "w"), indent=1)
    print("->", os.path.relpath(a.out, BASE))


if __name__ == "__main__":
    main()
