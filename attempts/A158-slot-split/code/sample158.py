"""A158 -- a uniform random sample of the selected population, for the population-level YES screen.

The top-20 is ranked, so it is not evidence about the other 1,218 cells.  This draws a uniform
sample (fixed seed) of the (node, best slot) cells with w >= 0.5, excluding the ones already run.
"""
import argparse
import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
R = os.path.join(BASE, "results")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=120)
    ap.add_argument("--seed", type=int, default=158)
    ap.add_argument("--out", default=os.path.join(R, "sample158.jsonl"))
    a = ap.parse_args()

    rows = [json.loads(l) for l in open(os.path.join(R, "pop158.jsonl"), encoding="utf-8")
            if l.strip()]
    rows = [r for r in rows if r["w_max"] >= 0.5]
    already = set()
    p = os.path.join(R, "top158.jsonl")
    if os.path.exists(p):
        for ln in open(p, encoding="utf-8"):
            if ln.strip():
                d = json.loads(ln)
                already.add((d["nid"], d["slot"]))
    cells = []
    for r in rows:
        e = max((x for x in r["slots"] if x["w"] >= 0.5), key=lambda x: x["w"], default=None)
        if e is None or (r["nid"], e["slot"]) in already:
            continue
        cells.append(dict(nid=r["nid"], slot=e["slot"], cls=r["cls"], src=r["src"],
                          level=r["level"], w=e["w"], ext=e["ext"], tau=r["tau"], eta=r["eta"]))
    random.Random(a.seed).shuffle(cells)
    cells = cells[:a.n]
    with open(a.out, "w", encoding="utf-8") as fh:
        for c in cells:
            fh.write(json.dumps(c) + "\n")
    print("population with w >= 0.5: %d cells; sampled %d (seed %d) -> %s"
          % (len(rows), len(cells), a.seed, a.out))


if __name__ == "__main__":
    main()
