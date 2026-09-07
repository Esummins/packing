"""A126 T1 control -- read the EMITTED Lean data file, decode it the way `LocalCert.parseLeaf`
does, and check that (a) every leaf still passes and (b) small mutations make leaves FAIL.

    python control126.py [S07|S02]

(a) closes the loop on the generator: the numbers that reach the Lean kernel are read back out
of the `.lean` file itself, not out of the JSON they were written from.  (b) is the negative
control the check needs to be worth anything -- a checker that accepts everything proves
nothing.  Three mutations, each applied to ONE leaf at a time:

    drop-row     delete the last row (and its multiplier) of the Farkas combination
    negate-y     flip the sign of one multiplier (the checker must also reject `y < 0`)
    widen-box    widen the leaf's box by 1 in the first tilt coordinate

For each we report how many of the leaves the mutation makes fail.  A mutation that leaves
every leaf passing would mean the check is not looking at that part of the certificate.
"""
from __future__ import annotations

import os, re, sys
from fractions import Fraction as Q

HERE = os.path.dirname(os.path.abspath(__file__))
LEAN = os.path.abspath(os.path.join(HERE, "..", "..", "..", "lean", "PackingCertMathlib",
                                    "PackingCertMathlib"))
S0 = Q(969271, 250000)


def parse_leaf(s, nv, D):
    """the Python mirror of `LocalCert.parseLeaf`."""
    f, lo, hi, rows = s.split(";")
    box = list(zip([Q(int(t), D) for t in lo.split(" ")],
                   [Q(int(t), D) for t in hi.split(" ")]))
    out = []
    for rs in rows.split("|"):
        toks = rs.split(" ")
        k, y = Q(int(toks[0]), D), Q(int(toks[1]), D)
        co = [Q(0)] * nv
        for t in toks[2:]:
            i, c = t.split(":")
            co[int(i)] += Q(int(c), D)
        out.append([co, k, y])
    return (f == "1"), box, out


def check_leaf(infeas, box, rows, nv):
    """the Python mirror of `LocalCert.checkLeaf`."""
    if any(y < 0 for _, _, y in rows):
        return False
    acc = [Q(0)] * nv
    if not infeas:
        acc[0] = Q(1)
    kacc = Q(0)
    for co, k, y in rows:
        for j in range(nv):
            if co[j]:
                acc[j] += y * co[j]
        kacc += y * k
    lb = kacc
    for j in range(nv):
        if acc[j]:
            lb += min(acc[j] * box[j][0], acc[j] * box[j][1])
    return lb > (Q(0) if infeas else S0)


def main(tag="S07"):
    path = os.path.join(LEAN, "LocalCert%sData.lean" % tag)
    txt = open(path, encoding="utf-8").read()
    nv = int(re.search(r"parseLeaf (\d+) ", txt).group(1))
    D = int(re.search(r"parseLeaf \d+ \((\d+) : ℚ\)", txt).group(1))
    chunks = re.findall(r'^"([^"]*)",?$', txt, re.M)
    print("%s: %d leaf records read back out of %s, nv = %d, denominator %d"
          % (tag, len(chunks), os.path.basename(path), nv, D))

    leaves = [parse_leaf(c, nv, D) for c in chunks]
    bad = [i for i, (inf, box, rows) in enumerate(leaves) if not check_leaf(inf, box, rows, nv)]
    print("  (a) as emitted: %d of %d leaves pass  -> %s"
          % (len(leaves) - len(bad), len(leaves), "OK" if not bad else "FAIL %s" % bad[:5]))
    if bad:
        return 1

    for name in ("zero-y", "halve-y", "drop-row", "negate-y", "widen-box"):
        fails = 0
        for inf, box, rows in leaves:
            b2 = [list(p) for p in box]
            r2 = [[list(co), k, y] for co, k, y in rows]
            if name == "zero-y":
                for r in r2:
                    r[2] = Q(0)
            elif name == "halve-y":
                for r in r2:
                    r[2] = r[2] / 2
            elif name == "drop-row":
                if len(r2) < 2:
                    continue
                r2 = r2[:-1]
            elif name == "negate-y":
                r2[0][2] = -r2[0][2]
            else:
                b2[nv - 1][0] -= 1
                b2[nv - 1][1] += 1
            if not check_leaf(inf, [tuple(p) for p in b2], r2, nv):
                fails += 1
        print("  (b) mutation %-10s -> %d of %d leaves now FAIL" % (name, fails, len(leaves)))

    # (c) a Monte-Carlo smoke test of the COVER half (part C1 of `CertCover`): the leaves'
    # boxes differ only in the TILT coordinates -- every other coordinate is the global box --
    # so the cover question is whether the leaf CELLS cover the root tilt box.  A necessary
    # condition, checked on the emitted data; the sufficient version is Lemma COVER.
    import random
    varying = [j for j in range(nv)
               if len({(box[j][0], box[j][1]) for _, box, _ in leaves}) > 1]
    root = [(min(box[j][0] for _, box, _ in leaves),
             max(box[j][1] for _, box, _ in leaves)) for j in varying]
    print("  (c) %d of %d coordinates vary across leaves (the tilt cells); root box %s"
          % (len(varying), nv, ", ".join("[%.6f, %.6f]" % (float(a), float(b)) for a, b in root)))
    random.seed(20260907)
    miss, NS = 0, 20000
    cells = [tuple(box[j] for j in varying) for _, box, _ in leaves]
    for _ in range(NS):
        pt = [Q(random.randrange(int(a * 10 ** 9), int(b * 10 ** 9) + 1), 10 ** 9)
              for a, b in root]
        if not any(all(c[k][0] <= pt[k] <= c[k][1] for k in range(len(varying))) for c in cells):
            miss += 1
    print("      %d random points of the root tilt box, %d in NO leaf cell -> %s"
          % (NS, miss, "cover OK" if miss == 0 else "GAP"))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
