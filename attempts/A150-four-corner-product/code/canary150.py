"""A150 -- the TRUMP CANARY for the four-corner product.

Every D4 image of Trump's family, dilated to s0, is a genuine 11-square configuration that
satisfies K0-BLOCKED on the WIDENED corner boxes (A143 sec 4: at a_w = 1.0255 every corner of every
image has >= 2 meeters).  So for every image and every choice of one meeter per corner, the
resulting 4-tuple of band cells MUST survive every geometric kill in prod150.  If it does not, a
kill is unsound.

Frames are frames150's ROTATIONAL ones (global -> local):
    BL: (x, y)        BR: (y, s-x)        TR: (s-x, s-y)        TL: (s-y, x)
each a rotation, so the local tilt is always theta mod 90.

    python code/canary150.py
"""
import itertools
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
for _p in (os.path.join(ATT, "A99-k0-tree-v2", "code"),
           os.path.join(ATT, "A143-corner-first-k0", "code"),
           os.path.join(ATT, "A57-shadow-trees", "code"),
           HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import blas1                                                    # noqa: F401,E402
import numpy as np                                              # noqa: E402
import class84 as K84                                           # noqa: E402
import cells143 as C                                            # noqa: E402
import frames150 as F                                           # noqa: E402

RES = os.path.join(BASE, "results")
S0 = C.S0
AW = C.A_W


def to_local(cx, cy, th_deg, corner, s=S0):
    if corner == "BL":
        u, v = cx, cy
    elif corner == "BR":
        u, v = cy, s - cx
    elif corner == "TR":
        u, v = s - cx, s - cy
    elif corner == "TL":
        u, v = s - cy, cx
    else:
        raise ValueError(corner)
    return u, v, th_deg % 90.0


def raw_cell(u, v, th):
    """the RAW (un-transposed) cell index; the product cover is over raw cells, not A143's
    D4_BL-canonical ones."""
    w = (C.ZHI - C.ZLO) / C.NPOS
    if not (C.ZLO - 1e-9 <= u <= C.ZHI + 1e-9 and C.ZLO - 1e-9 <= v <= C.ZHI + 1e-9):
        return None
    return (min(C.NPOS - 1, max(0, int((u - C.ZLO) / w))),
            min(C.NPOS - 1, max(0, int((v - C.ZLO) / w))),
            min(C.NTILT - 1, max(0, int((th % 90.0) / C.TILT_W))))


def main():
    band = [tuple(k) for k in json.load(open(os.path.join(RES, "band150.json"),
                                             encoding="utf-8"))["band"]]
    idx = {k: i for i, k in enumerate(band)}
    A = np.load(os.path.join(RES, "prod150_A.npy"))
    D = np.load(os.path.join(RES, "prod150_D.npy"))
    Y0, s_trump, lam = K84.trump_scaled()
    out = dict(s_trump=s_trump, lam=lam, s0=S0, a_w=AW, images={},
               n_tuples=0, n_in_band=0, n_survive=0, failures=[])
    for k in range(8):
        Z = K84.symmetry(Y0, k)
        per = {}
        for corner in F.CORNERS:
            ms = []
            for i, (x, y, th) in enumerate(Z):
                u, v, t = to_local(x, y, math.degrees(th), corner)
                if not C.meets_bl(u, v, t, a_w=AW):
                    continue
                ms.append(dict(sq=i, u=round(u, 6), v=round(v, 6), th=round(t, 6),
                               cell=raw_cell(u, v, t)))
            per[corner] = ms
        img = dict(counts={c: len(per[c]) for c in F.CORNERS},
                   cells={c: [m["cell"] for m in per[c]] for c in F.CORNERS},
                   n_tuples=0, n_in_band=0, n_survive=0)
        for combo in itertools.product(*[per[c] for c in F.CORNERS]):
            t = tuple(m["cell"] for m in combo)
            img["n_tuples"] += 1
            out["n_tuples"] += 1
            if any(x is None or x not in idx for x in t):
                out["failures"].append(dict(image="g%d" % k, tuple=[list(x) if x else None
                                                                   for x in t],
                                            why="NOT-IN-BAND"))
                continue
            img["n_in_band"] += 1
            out["n_in_band"] += 1
            a = [idx[x] for x in t]
            ok = bool(A[a[0], a[1]] and A[a[1], a[2]] and A[a[2], a[3]] and A[a[3], a[0]]
                      and D[a[0], a[2]] and D[a[1], a[3]])
            if ok:
                img["n_survive"] += 1
                out["n_survive"] += 1
            else:
                out["failures"].append(dict(image="g%d" % k, tuple=[list(x) for x in t],
                                            why="KILLED-BY-GEOMETRY",
                                            edges=[int(A[a[0], a[1]]), int(A[a[1], a[2]]),
                                                   int(A[a[2], a[3]]), int(A[a[3], a[0]]),
                                                   int(D[a[0], a[2]]), int(D[a[1], a[3]])]))
        out["images"]["g%d" % k] = img
        print("g%d  %s  tuples=%d in_band=%d survive=%d"
              % (k, img["counts"], img["n_tuples"], img["n_in_band"], img["n_survive"]),
              flush=True)
    out["verdict"] = ("CANARY-PASS" if not out["failures"] else "CANARY-FAIL")
    json.dump(out, open(os.path.join(RES, "canary150.json"), "w"), indent=1)
    print(json.dumps(dict(n_tuples=out["n_tuples"], n_in_band=out["n_in_band"],
                          n_survive=out["n_survive"], verdict=out["verdict"],
                          n_failures=len(out["failures"])), indent=1), flush=True)


if __name__ == "__main__":
    main()
