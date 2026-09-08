"""A143 T1 -- the COVER PROOF and its sampled confirmation.

Interval part (exact, in the docstring of cells143 and notes/composition.md):
  every admissible pose (c, th) that meets the widened BL box [0, a_w]^2 has, for each coordinate,
  h(th) <= c_i <= min(s0 - h(th), a_w + h(th)), hence c_i in [1/2, a_w + sqrt(2)/2] = [ZLO, ZHI];
  th in [0, 90) after the theta ~ theta + 90 glue.  The 6 x 6 x 6 grid of closed cells covers
  [ZLO, ZHI]^2 x [0, 90) exactly, and the BL stabiliser {id, transpose} lets us take x >= y.

Sampled confirmation (this module):
  (1) SINGLE cover: draw admissible poses that meet the widened box; every one must land in a
      non-empty cell whose CLIPPED box contains it.  A miss would mean the clip discards an
      admissible pose (unsound) or the zone is too small.
  (2) PAIR cover: draw pairs of such poses that are INTERIOR-DISJOINT (a realisable BL 2-crowd);
      every one must land in a pair cell that geometry did NOT kill.  A hit on a P2 / P1 / P1s
      cell would be a soundness violation of the pair prunes.

    python code/cover143.py --hits 20000
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
_A57 = os.path.join(ROOT, "attempts", "A57-shadow-trees", "code")
_A132 = os.path.join(ROOT, "attempts", "A132-polygon-core", "code")
for _p in (_A57, _A132, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import blas1                                                    # noqa: F401,E402
import numpy as np                                              # noqa: E402
import cells143 as C                                            # noqa: E402
import pairs143 as P                                            # noqa: E402


def locate_raw(x, y, th):
    w = (C.ZHI - C.ZLO) / C.NPOS
    th = th % 90.0
    if not (C.ZLO - 1e-12 <= x <= C.ZHI + 1e-12 and C.ZLO - 1e-12 <= y <= C.ZHI + 1e-12):
        return None
    return (min(C.NPOS - 1, max(0, int((x - C.ZLO) / w))),
            min(C.NPOS - 1, max(0, int((y - C.ZLO) / w))),
            min(C.NTILT - 1, max(0, int(th / C.TILT_W))))


def sat_gap(c1, t1, c2, t2):
    """SAT gap between two unit squares (vectorised over rows); > 0 iff interior-disjoint."""
    d = c2 - c1
    g = np.full(len(d), -np.inf)
    for tt in (t1, t2):
        for (ax, ay) in ((np.cos(tt), np.sin(tt)), (-np.sin(tt), np.cos(tt))):
            p = np.abs(d[:, 0] * ax + d[:, 1] * ay)
            h1 = 0.5 * (np.abs(ax * np.cos(t1) + ay * np.sin(t1))
                        + np.abs(-ax * np.sin(t1) + ay * np.cos(t1)))
            h2 = 0.5 * (np.abs(ax * np.cos(t2) + ay * np.sin(t2))
                        + np.abs(-ax * np.sin(t2) + ay * np.cos(t2)))
            g = np.maximum(g, p - h1 - h2)
    return g


def meets_bl_vec(Cc, TH, a_w=C.A_W):
    """float over-approximation-free test: min over Q of max(x, y) < a_w, computed on the four
    vertices and the diagonal crossings (the float twin of cells143.f_min_max)."""
    ct, st = np.cos(TH), np.sin(TH)
    e1 = np.stack([0.5 * ct, 0.5 * st], 1)
    e2 = np.stack([-0.5 * st, 0.5 * ct], 1)
    V = [Cc + su * e1 + sv * e2 for su, sv in ((1, 1), (1, -1), (-1, -1), (-1, 1))]
    best = np.full(len(Cc), np.inf)
    for v in V:
        best = np.minimum(best, np.maximum(v[:, 0], v[:, 1]))
    for i in range(4):
        p, q = V[i], V[(i + 1) % 4]
        dx, dy = q[:, 0] - p[:, 0], q[:, 1] - p[:, 1]
        den = dx - dy
        ok = np.abs(den) > 1e-15
        s = np.zeros(len(Cc))
        s[ok] = (p[ok, 1] - p[ok, 0]) / den[ok]
        good = ok & (s >= 0) & (s <= 1)
        cand = p[:, 0] + s * dx
        best = np.where(good, np.minimum(best, cand), best)
    return best < a_w


def draw_poses(rng, n, s=C.S0, a_w=C.A_W):
    Cc = rng.uniform(C.ZLO - 0.02, C.ZHI + 0.02, size=(n, 2))
    TH = rng.uniform(0.0, math.pi / 2, size=n)
    h = 0.5 * (np.cos(TH) + np.sin(TH))
    ok = (Cc[:, 0] >= h) & (Cc[:, 1] >= h) & (Cc[:, 0] <= s - h) & (Cc[:, 1] <= s - h)
    ok &= meets_bl_vec(Cc, TH, a_w)
    return Cc[ok], TH[ok]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hits", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=14300)
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)
    cells = {P.cell_key(c): c for c in C.all_cells()}
    geom = {}
    gp = os.path.join(BASE, "results", "pairs143_geom.jsonl")
    for ln in open(gp, encoding="utf-8"):
        r = json.loads(ln)
        geom[(tuple(r["pair"][0]), tuple(r["pair"][1]))] = r["verdict"]

    # ---------------- single cover
    hits = miss = 0
    drawn = 0
    bad = []
    seen_cells = set()
    while hits < a.hits:
        Cc, TH = draw_poses(rng, 40000)
        drawn += 40000
        for k in range(len(Cc)):
            x, y, th = Cc[k, 0], Cc[k, 1], math.degrees(TH[k])
            key = C.locate(x, y, th)          # with the D4_BL canonicalisation
            xx, yy, tt = (x, y, th) if x >= y else (y, x, (90.0 - th) % 90.0)
            ok = False
            if key is not None and key in cells and not cells[key].empty:
                b = cells[key].box
                ok = (b.x0 - 1e-9 <= xx <= b.x1 + 1e-9 and b.y0 - 1e-9 <= yy <= b.y1 + 1e-9
                      and b.th0 - 1e-9 <= tt <= b.th1 + 1e-9)
                seen_cells.add(key)
            if ok:
                hits += 1
            else:
                miss += 1
                if len(bad) < 5:
                    bad.append([x, y, th, list(key) if key else None])
        if drawn > 4000000:
            break
    single = dict(drawn=drawn, hits=hits, misses=miss, bad=bad,
                  distinct_cells_hit=len(seen_cells))
    print("SINGLE cover:", json.dumps(single)[:400], flush=True)

    # ---------------- pair cover
    phits = pviol = 0
    pdrawn = 0
    viol = []
    vcount = {}
    seen_pairs = set()
    while phits < a.hits:
        Cc, TH = draw_poses(rng, 60000)
        pdrawn += 60000
        n = len(Cc) // 2
        if n < 2:
            continue
        A, TA = Cc[:n], TH[:n]
        B, TB = Cc[n:2 * n], TH[n:2 * n]
        g = sat_gap(A, TA, B, TB)
        sel = np.flatnonzero(g > 0.0)
        for k in sel:
            k1 = locate_raw(A[k, 0], A[k, 1], math.degrees(TA[k]))
            k2 = locate_raw(B[k, 0], B[k, 1], math.degrees(TB[k]))
            if k1 is None or k2 is None:
                pviol += 1
                continue
            cc = P.pair_canonical(k1, k2)
            seen_pairs.add(cc)
            v = geom.get(cc, "MISSING")
            vcount[v] = vcount.get(v, 0) + 1
            if v == "ALIVE-CORE":
                phits += 1
            else:
                pviol += 1
                if len(viol) < 5:
                    viol.append(dict(verdict=v, pair=[list(cc[0]), list(cc[1])],
                                     gap=float(g[k]),
                                     p1=[float(A[k, 0]), float(A[k, 1]),
                                         float(math.degrees(TA[k]))],
                                     p2=[float(B[k, 0]), float(B[k, 1]),
                                         float(math.degrees(TB[k]))]))
            if phits >= a.hits:
                break
        if pdrawn > 30000000:
            break
    pair = dict(drawn=pdrawn, realised_2crowds=phits + pviol, hits_alive=phits,
                violations=pviol, verdict_counts=vcount, examples=viol,
                distinct_pair_cells_hit=len(seen_pairs))
    print("PAIR cover:", json.dumps({k: v for k, v in pair.items() if k != "examples"})[:500],
          flush=True)
    if viol:
        print("VIOLATIONS:", json.dumps(viol, indent=1)[:1200], flush=True)
    out = os.path.join(BASE, "results", "cover143.json")
    json.dump(dict(single=single, pair=pair), open(out, "w"), indent=1)
    print("wrote", out, flush=True)


if __name__ == "__main__":
    main()
