"""A144 T1 -- the sampled confirmation of the two claims the guard row rests on.

  (C1) minchord is a LOWER bound.  Per node, for three lines of its family (the maximum-violation
       line and two others), 10^4 poses of the conditioned square drawn uniformly in its box and
       10^4 poses of every pin drawn in its own box: the TRUE chord must be >= minchord in every
       draw.  Reported as drawn -> tested -> hits (a hit = a violation of the bound).

  (C2) LINE-1.  10^4 random interior-disjoint square sets in [0,s0]^2, each tested on a random
       axis-parallel line: SUM of chords <= s0.  The lemma is trivial; the line is on the record.

    set PYTHONDONTWRITEBYTECODE=1 && python code/confirm144.py
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import guardline as G                                                   # noqa: E402
import offline144 as OFF                                                # noqa: E402
from fractions import Fraction as Fr                                    # noqa: E402

RES = os.path.join(BASE, "results")


def main():
    pop, _ = OFF.population()
    off = {}
    for ln in open(os.path.join(RES, "offline144.jsonl"), encoding="utf-8"):
        if ln.strip():
            r = json.loads(ln)
            off[r["id"]] = r
    rng = np.random.default_rng(7)
    drawn = tested = hits = 0
    worst = 9e9
    n_nodes = n_lines = 0
    t0 = time.time()
    per_node = []
    for r in pop:
        o = off.get(r["id"])
        if not o or o.get("max_viol") is None:
            continue
        got = OFF.load_node(r["id"])
        if got is None:
            continue
        d, _p = got
        pins, hbox = G.node_boxes(d)
        fam = G.line_family(pins, hbox, max_lines=40)
        picks = [G.Line(o["max_viol_line"]["orient"], Fr(o["max_viol_line"]["off"]), "maxviol")]
        for k in rng.choice(len(fam), size=min(2, len(fam)), replace=False):
            picks.append(fam[int(k)])
        nh = 0
        for L in picks:
            n_lines += 1
            for b in ([hbox] + pins):
                s = G.sample_confirm(b, L, a=0.5, n=10000, seed=int(rng.integers(1 << 30)))
                drawn += s["n"]
                tested += s["n"]
                hits += s["hits"]
                nh += s["hits"]
                if s["minchord"] > 0:
                    worst = min(worst, s["slack"])
        n_nodes += 1
        per_node.append(dict(id=r["id"], hits=nh))
    pk = G.sample_packings(s=G.S0, n_trial=10000, k=11, seed=11)
    out = dict(generated=time.strftime("%Y-%m-%dT%H:%M:%S"), seconds=round(time.time() - t0, 1),
               C1=dict(nodes=n_nodes, lines=n_lines, drawn=drawn, tested=tested, hits=hits,
                       min_slack_over_all_positive_bounds=(None if worst > 8e9 else worst),
                       nodes_with_hits=[x for x in per_node if x["hits"]]),
               C2=pk)
    json.dump(out, open(os.path.join(RES, "confirm144.json"), "w", encoding="utf-8"), indent=1)
    print(json.dumps({k: v for k, v in out.items()}, indent=1)[:2500])


if __name__ == "__main__":
    main()
