"""A150 T2b -- the COARSE four-corner product.

The fine product (A143's 6 x 6 x 6 cells per corner) has 1.9e8 D4-orbits: no LP rate can pay for
that.  But a large |eta| at level 1 buys COARSENESS -- a node whose LP kills with eta = -6 can
afford a hypothesis box several times wider.  This module builds the coarse covers

    NP x NP positions on [1/2, a_w + sqrt2/2]^2   x   NT tilt windows of 90/NT degrees

(the fine cover is NP = NT = 6), applies the same (Q2)/(Q1)/(Q1s) adjacent- and diagonal-corner
kills, counts the D4-reduced product exactly by the same transfer-matrix / Burnside route, and
emits an LP node list.  A coarse cell is a UNION of fine cells, so the coarse cover is a cover
whenever the fine one is: nothing is lost by coarsening except core size.

    python code/coarse150.py --np 3 --nt 3 --stage all
"""
import argparse
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
for _p in (os.path.join(ATT, "A143-corner-first-k0", "code"),
           os.path.join(ATT, "A132-polygon-core", "code"),
           os.path.join(ATT, "A135-polycore-verifier", "code"),
           os.path.join(ATT, "A57-shadow-trees", "code"),
           HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import blas1                                                        # noqa: F401,E402
import numpy as np                                                  # noqa: E402
import polycore                                                     # noqa: E402
import exactcore                                                    # noqa: E402
import cells143 as C                                                # noqa: E402
import frames150 as F                                               # noqa: E402
from caselp import Box                                              # noqa: E402

RES = os.path.join(BASE, "results")
S0 = C.S0
MAXV = 16
NSUB = 4


class Coarse:
    def __init__(self, ix, iy, it, npos, ntilt):
        self.ix, self.iy, self.it = ix, iy, it
        self.npos, self.ntilt = npos, ntilt
        w = (C.ZHI - C.ZLO) / npos
        tw = 90.0 / ntilt
        self.raw = (C.ZLO + ix * w, C.ZLO + (ix + 1) * w,
                    C.ZLO + iy * w, C.ZLO + (iy + 1) * w,
                    it * tw, (it + 1) * tw)
        c = C.clip_box(*self.raw)
        self.subbins = C.subbin_clip(*self.raw, nsub=NSUB)
        self.empty = (c is None) or (not self.subbins)
        self.box = None if self.empty else Box(c[0], c[1], c[2], c[3], self.raw[4], self.raw[5])

    @property
    def key(self):
        return (self.ix, self.iy, self.it)


def all_coarse(npos, ntilt):
    return [c for c in (Coarse(i, j, t, npos, ntilt)
                        for i in range(npos) for j in range(npos) for t in range(ntilt))
            if not c.empty]


def gbox(corner, cell):
    b = cell.box
    X0, X1, Y0, Y1 = F.to_global(corner, b.x0, b.x1, b.y0, b.y1)
    return Box(X0, X1, Y0, Y1, b.th0, b.th1)


def gsub(corner, cell):
    out = []
    for (a, b, cl) in cell.subbins:
        X0, X1, Y0, Y1 = F.to_global(corner, cl[0], cl[1], cl[2], cl[3])
        out.append(Box(X0, X1, Y0, Y1, a, b))
    return out


def max_centre_dist(b1, b2):
    dx = max(abs(b1.x1 - b2.x0), abs(b2.x1 - b1.x0))
    dy = max(abs(b1.y1 - b2.y0), abs(b2.y1 - b1.y0))
    return math.hypot(dx, dy)


def pair_matrix(cells, c1, c2, log=print):
    n = len(cells)
    G1 = [gbox(c1, c) for c in cells]
    G2 = [gbox(c2, c) for c in cells]
    K1 = [polycore.build(b, max_v=MAXV) for b in G1]
    K2 = [polycore.build(b, max_v=MAXV) for b in G2]
    S1 = [[polycore.build(b, max_v=MAXV) for b in gsub(c1, c)] for c in cells]
    S2 = [[polycore.build(b, max_v=MAXV) for b in gsub(c2, c)] for c in cells]
    M = np.ones((n, n), np.uint8)
    kills = dict(Q2=0, Q1=0, Q1s=0)
    for i in range(n):
        for j in range(n):
            if max_centre_dist(G1[i], G2[j]) < 1.0:
                M[i, j] = 0
                kills["Q2"] += 1
                continue
            if polycore.poly_poly_depth(K1[i].P, K2[j].P) > 0.0:
                M[i, j] = 0
                kills["Q1"] += 1
                continue
            if max_centre_dist(G1[i], G2[j]) < 2.9:
                if not any(polycore.poly_poly_depth(p.P, q.P) <= 0.0
                           for p in S1[i] for q in S2[j]):
                    M[i, j] = 0
                    kills["Q1s"] += 1
    kills["alive"] = int(M.sum())
    kills["total"] = n * n
    log("%s-%s %s" % (c1, c2, json.dumps(kills)))
    return M, kills


def count(A, D, keys, npos, ntilt):
    n = len(keys)
    idx = {k: i for i, k in enumerate(keys)}

    def T(k):
        return (k[1], k[0], ntilt - 1 - k[2])

    tp = np.array([idx.get(T(k), -1) for k in keys])
    A64 = A.astype(np.int64)
    if D.all():
        M2 = A64 @ A64
        total = int(np.einsum("ij,ji->", M2, M2))
    else:
        total = 0
        for a0 in range(n):
            m1, m3, m2 = A64[a0] > 0, A64[:, a0] > 0, D[a0] > 0
            sub, sub3 = A64[np.ix_(m1, m2)], A64[np.ix_(m2, m3)]
            Dm = D[np.ix_(m1, m3)]
            total += int(((sub @ sub3) * Dm).sum()) if Dm.size else 0

    def alive(t):
        if min(t) < 0:
            return False
        return bool(A[t[0], t[1]] and A[t[1], t[2]] and A[t[2], t[3]] and A[t[3], t[0]]
                    and D[t[0], t[2]] and D[t[1], t[3]])

    tfix = [a for a in range(n) if tp[a] == a]
    fix = dict(e=total,
               r=sum(1 for a in range(n) if alive((a, a, a, a))))
    fix["r3"] = fix["r"]
    fix["r2"] = sum(1 for a in range(n) for b in range(n) if alive((a, b, a, b)))
    fix["m_diag"] = sum(1 for a in tfix for c in tfix for b in range(n)
                        if alive((a, b, c, int(tp[b]))))
    fix["m_anti"] = sum(1 for b in tfix for d in tfix for a in range(n)
                        if alive((a, b, int(tp[a]), d)))
    fix["m_horiz"] = sum(1 for a in range(n) for b in range(n)
                         if alive((a, b, int(tp[b]), int(tp[a]))))
    fix["m_vert"] = sum(1 for a in range(n) for b in range(n)
                        if alive((a, int(tp[a]), int(tp[b]), b)))
    return dict(npos=npos, ntilt=ntilt, cells=n, raw=n ** 4, total=total,
                orbits=sum(fix.values()) / 8.0, fix=fix,
                adj_alive_frac=float(A.mean()), diag_alive_frac=float(D.mean()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--np", type=int, default=3)
    ap.add_argument("--nt", type=int, default=3)
    ap.add_argument("--nodes", type=int, default=8)
    ap.add_argument("--seed", type=int, default=1503)
    a = ap.parse_args()
    tag = "np%d_nt%d" % (a.np, a.nt)
    cells = all_coarse(a.np, a.nt)
    keys = [c.key for c in cells]
    t0 = time.time()
    A, kA = pair_matrix(cells, "BL", "BR")
    D, kD = pair_matrix(cells, "BL", "TR")
    cnt = count(A, D, keys, a.np, a.nt)
    cnt["kills_adj"] = kA
    cnt["kills_diag"] = kD
    # core half-sides available at this coarseness
    aex = []
    for c in cells[:min(len(cells), 40)]:
        try:
            x, _x0, ok = exactcore.exact_a(gbox("BL", c))
            aex.append(float(x) if ok else None)
        except Exception:                                           # noqa: BLE001
            aex.append(None)
    good = [x for x in aex if x]
    cnt["a_exact_min"] = min(good) if good else None
    cnt["a_exact_max"] = max(good) if good else None
    cnt["a_exact_fail"] = sum(1 for x in aex if not x)
    cnt["secs"] = round(time.time() - t0, 1)
    json.dump(cnt, open(os.path.join(RES, "coarse150_%s.json" % tag), "w"), indent=1)
    print(json.dumps({k: v for k, v in cnt.items() if k != "fix"}, indent=1), flush=True)

    idx = {k: i for i, k in enumerate(keys)}
    byk = {c.key: c for c in cells}

    def alive(t):
        try:
            u = [idx[x] for x in t]
        except KeyError:
            return False
        return bool(A[u[0], u[1]] and A[u[1], u[2]] and A[u[2], u[3]] and A[u[3], u[0]]
                    and D[u[0], u[2]] and D[u[1], u[3]])

    rng = np.random.default_rng(a.seed)
    picks = []
    seen = set()
    # the diagonal tuples first (a, a, a, a) -- the D4-symmetric spine of the product
    for k in keys:
        if len(picks) >= a.nodes // 2:
            break
        if alive((k, k, k, k)):
            picks.append((k, k, k, k))
            seen.add((k, k, k, k))
    tries = 0
    while len(picks) < a.nodes and tries < 20000:
        tries += 1
        t = tuple(keys[i] for i in rng.integers(0, len(keys), 4))
        if t in seen or not alive(t):
            continue
        seen.add(t)
        picks.append(t)
    nodes = []
    for t in picks:
        nid = "c%s_%s" % (tag, "_".join("%d%d%d" % k for k in t))
        nodes.append(dict(node=nid, kind="coarse-%s" % tag, budget=7,
                          tuple=[list(k) for k in t],
                          boxes=[gbox(c, byk[k]).to_json()
                                 for c, k in zip(F.CORNERS, t)],
                          note="coarse cover %d x %d positions x %d tilt windows of %.1f deg"
                               % (a.np, a.np, a.nt, 90.0 / a.nt)))
    json.dump(nodes, open(os.path.join(RES, "nodes150_%s.json" % tag), "w"), indent=1)
    for n in nodes:
        print(n["node"], n["tuple"], flush=True)
    print("wrote %d coarse nodes" % len(nodes), flush=True)


if __name__ == "__main__":
    main()
