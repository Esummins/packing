"""A150 -- choose the 4-tuples that go to the LP and to the drawings.

The ten LP nodes are chosen to make the comparison with A143 direct, not to be a random sample:

  * three tuples repeat A143's THREE single-corner LP cells at all four corners, so the marginal
    effect of adding three more corner cores to the SAME hypothesis is read straight off the eta
    column (A143 single: eta = -0.0442 at (1,1,t0), -0.6328 at (3,2,t1), -0.0000 at (4,0,t2));
  * one is a TRUMP tuple -- a node a real 11-family reaches, so its LP must NOT kill;
  * two are the extremes of the band (all four intruders hugging their corners; all four as far
    from their corners as the band allows);
  * four are drawn uniformly from the survivors with a fixed seed.

    python code/pick150.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
for _p in (os.path.join(ATT, "A143-corner-first-k0", "code"),
           os.path.join(ATT, "A57-shadow-trees", "code"), HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import blas1                                                        # noqa: F401,E402
import numpy as np                                                  # noqa: E402
import cells143 as C                                                # noqa: E402
import frames150 as F                                               # noqa: E402

RES = os.path.join(BASE, "results")


def alive_fn(A, D, idx):
    def alive(t):
        try:
            a = [idx[x] for x in t]
        except KeyError:
            return False
        return bool(A[a[0], a[1]] and A[a[1], a[2]] and A[a[2], a[3]] and A[a[3], a[0]]
                    and D[a[0], a[2]] and D[a[1], a[3]])
    return alive


def main():
    band = [tuple(k) for k in json.load(open(os.path.join(RES, "band150.json"),
                                             encoding="utf-8"))["band"]]
    idx = {k: i for i, k in enumerate(band)}
    A = np.load(os.path.join(RES, "prod150_A.npy"))
    D = np.load(os.path.join(RES, "prod150_D.npy"))
    alive = alive_fn(A, D, idx)
    byk = {(c.ix, c.iy, c.it): c for c in C.all_cells() if not c.empty}

    picks = []

    def add(tag, tup, kind, note=""):
        if not alive(tup):
            print("SKIP (geometry-dead)", tag, tup, flush=True)
            return
        if any(p["tuple"] == [list(k) for k in tup] for p in picks):
            return
        picks.append(dict(node=tag, kind=kind, note=note, budget=7,
                          tuple=[list(k) for k in tup],
                          boxes=[F.global_box(c, byk[k]).to_json()
                                 for c, k in zip(F.CORNERS, tup)]))

    for k, lab in (((1, 1, 0), "A143 s_c1_11_t0 eta -0.0442"),
                   ((3, 2, 1), "A143 s_c1_32_t1 eta -0.6328"),
                   ((4, 0, 2), "A143 s_c1_40_t2 eta -0.0000")):
        add("q_%d%d%d_x4" % k, (k, k, k, k), "A143-repeat", lab)

    can = os.path.join(RES, "canary150.json")
    if os.path.exists(can):
        cj = json.load(open(can, encoding="utf-8"))
        for g, img in cj["images"].items():
            cells = img["cells"]
            t = tuple(tuple(cells[c][0]) for c in F.CORNERS)
            if alive(t):
                add("q_trump_%s" % g, t, "trump-canary",
                    "a Trump image reaches this node: the LP must NOT kill it")
                break

    add("q_000_x4", ((0, 0, 0),) * 4, "band-extreme", "all four intruders hug their corners")
    far = max((k for k in band if k[0] == 5 and k[1] == 5), key=lambda k: k[2])
    add("q_far_x4", (far,) * 4, "band-extreme", "all four as far from their corners as the band allows")

    rng = np.random.default_rng(150)
    tries = 0
    while len(picks) < 10 and tries < 20000:
        tries += 1
        t = tuple(band[i] for i in rng.integers(0, len(band), 4))
        if alive(t):
            add("q_rand_%s" % "_".join("%d%d%d" % k for k in t), t, "random-survivor", "")
    json.dump(picks, open(os.path.join(RES, "nodes150.json"), "w"), indent=1)
    for p in picks:
        print(p["node"], p["kind"], p["tuple"], flush=True)
    print("wrote %d nodes" % len(picks), flush=True)


if __name__ == "__main__":
    main()
