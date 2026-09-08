"""A150 -- independent re-checks of every structural claim, by a different route from the one
that produced the number.  Nothing here imports prod150's counting code.

  V1  D4 is a group of order 8 acting on 4-tuples: the eight maps of frames150 are pairwise
      distinct as FUNCTIONS on random states, closed under composition, and `canonical` is
      constant on orbits.
  V2  (R6): no unit square meets two widened corner boxes.  Exact: the gap between B_BL^w and
      B_BR^w is s0 - 2 a_w = 1.8262 > sqrt2.  Confirmed by drawing poses that meet one box and
      testing the others.
  V3  the transfer-matrix survivor count and the Burnside orbit count, against BRUTE-FORCE
      enumeration of the whole product on a random SUB-COVER of 12 cells (12^4 = 20 736 states).
  V4  the band (B1) recomputed from A143's file by a different loop (ordered raw pairs, no
      canonicalisation cache).
  V5  the frames: the global box of a cell at each corner really is the image of the BL box under
      the corresponding quarter turn, checked on the box corners.

    python code/verify150.py
"""
import itertools
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
for _p in (os.path.join(ATT, "A143-corner-first-k0", "code"),
           os.path.join(ATT, "A148-gallery-v4", "code"),
           os.path.join(ATT, "A57-shadow-trees", "code"),
           HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import blas1                                                        # noqa: F401,E402
import numpy as np                                                  # noqa: E402
import cells143 as C                                                # noqa: E402
import geo148 as G                                                  # noqa: E402
import frames150 as F                                               # noqa: E402

RES = os.path.join(BASE, "results")
S0 = C.S0
A_W = C.A_W


def v1(rng):
    states = [tuple(tuple(int(x) for x in rng.integers([0, 0, 0], [6, 6, 6])) for _ in range(4))
              for _ in range(400)]
    names = [n for n, _g in F.D4]
    maps = [g for _n, g in F.D4]
    distinct = all(any(g1(s) != g2(s) for s in states)
                   for i, g1 in enumerate(maps) for g2 in maps[i + 1:])
    closed = True
    for g1 in maps:
        for g2 in maps:
            if not all(any(g1(g2(s)) == g3(s) for g3 in maps) for s in states[:60]):
                closed = False
    orbit_ok = all(len({F.canonical(g(s)) for _n, g in F.D4}) == 1 for s in states)
    return dict(n_elements=len(maps), names=names, pairwise_distinct=bool(distinct),
                closed_under_composition=bool(closed),
                canonical_constant_on_orbits=bool(orbit_ok))


def v2(rng, n=200000):
    """no unit square meets two widened corner boxes."""
    gap = S0 - 2.0 * A_W
    boxes = {c: F.to_global(c, 0.0, A_W, 0.0, A_W) for c in F.CORNERS}

    def poly(b):
        return [(b[0], b[2]), (b[1], b[2]), (b[1], b[3]), (b[0], b[3])]

    P = {c: poly(b) for c, b in boxes.items()}
    worst = 0
    for _ in range(n // 1000):
        cx = rng.uniform(0.0, S0, 1000)
        cy = rng.uniform(0.0, S0, 1000)
        th = rng.uniform(0.0, math.pi / 2, 1000)
        for i in range(1000):
            q = G.sqpoly(cx[i], cy[i], th[i])
            k = sum(1 for c in F.CORNERS if G.sat_gap(q, P[c]) < 0.0)
            worst = max(worst, k)
    return dict(gap_between_adjacent_corner_boxes=gap, diam_unit_square=math.sqrt(2.0),
                gap_exceeds_diameter=bool(gap > math.sqrt(2.0)),
                drawn=n, max_corner_boxes_met_by_one_square=worst,
                claim_ok=bool(worst <= 1))


def v3(rng):
    keys = [tuple(k) for k in json.load(open(os.path.join(RES, "band150.json"),
                                             encoding="utf-8"))["band"]]
    A = np.load(os.path.join(RES, "prod150_A.npy"))
    D = np.load(os.path.join(RES, "prod150_D.npy"))
    idx = {k: i for i, k in enumerate(keys)}
    # a TRANSPOSE-CLOSED sub-cover, so whole D4 orbits live inside it and the Burnside count
    # can be compared with explicit orbit enumeration
    sub = []
    while len(sub) < 12:
        k = keys[int(rng.integers(0, len(keys)))]
        for x in (k, F.T(k)):
            if x in idx and x not in sub and len(sub) < 12:
                sub.append(x)
    sub = sorted(set(sub))
    pick = [idx[k] for k in sub]
    subset = set(sub)
    Asub = A[np.ix_(pick, pick)]
    Dsub = D[np.ix_(pick, pick)]
    # brute force over 12^4 states of the sub-cover
    alive = []
    for t in itertools.product(range(12), repeat=4):
        if (Asub[t[0], t[1]] and Asub[t[1], t[2]] and Asub[t[2], t[3]] and Asub[t[3], t[0]]
                and Dsub[t[0], t[2]] and Dsub[t[1], t[3]]):
            alive.append(t)
    # orbits by explicit canonicalisation, restricted to the sub-cover (an orbit may leave it;
    # count only orbits entirely inside, and compare with Burnside restricted the same way)
    orbits = set()
    closed_orbits = 0
    for t in alive:
        st = tuple(sub[i] for i in t)
        imgs = [g(st) for _n, g in F.D4]
        if all(all(x in subset for x in im) for im in imgs):
            closed_orbits += 1
            orbits.add(min(imgs))
    # Burnside on the sub-cover
    n = 12
    tp = np.array([pick.index(idx[F.T(k)]) if F.T(k) in idx and idx[F.T(k)] in pick else -1
                   for k in sub])

    def ok(t):
        if min(t) < 0:
            return False
        return bool(Asub[t[0], t[1]] and Asub[t[1], t[2]] and Asub[t[2], t[3]]
                    and Asub[t[3], t[0]] and Dsub[t[0], t[2]] and Dsub[t[1], t[3]])

    A64 = Asub.astype(np.int64)
    if Dsub.all():
        M2 = A64 @ A64
        total_tm = int(np.einsum("ij,ji->", M2, M2))
    else:
        total_tm = 0
        for a0 in range(n):
            m1, m3, m2 = A64[a0] > 0, A64[:, a0] > 0, Dsub[a0] > 0
            s1, s3 = A64[np.ix_(m1, m2)], A64[np.ix_(m2, m3)]
            Dm = Dsub[np.ix_(m1, m3)]
            total_tm += int(((s1 @ s3) * Dm).sum()) if Dm.size else 0
    # Burnside over the sub-cover (valid because the sub-cover is transpose-closed, so D4 maps
    # sub-cover states to sub-cover states)
    tfix = [a for a in range(n) if tp[a] == a]
    fix = dict(e=total_tm, r=sum(1 for a in range(n) if ok((a, a, a, a))))
    fix["r3"] = fix["r"]
    fix["r2"] = sum(1 for a in range(n) for b in range(n) if ok((a, b, a, b)))
    fix["m_diag"] = sum(1 for a in tfix for c in tfix for b in range(n)
                        if ok((a, b, c, int(tp[b]))))
    fix["m_anti"] = sum(1 for b in tfix for d in tfix for a in range(n)
                        if ok((a, b, int(tp[a]), d)))
    fix["m_horiz"] = sum(1 for a in range(n) for b in range(n)
                         if ok((a, b, int(tp[b]), int(tp[a]))))
    fix["m_vert"] = sum(1 for a in range(n) for b in range(n)
                        if ok((a, int(tp[a]), int(tp[b]), b)))
    burnside = sum(fix.values()) / 8.0
    return dict(sub_cover=[list(k) for k in sub],
                sub_cover_transpose_closed=bool(all(F.T(k) in set(sub) for k in sub)),
                brute_force_states=len(alive), transfer_matrix_states=total_tm,
                agree=bool(len(alive) == total_tm),
                orbits_by_explicit_canonicalisation=len(orbits),
                states_in_those_orbits=closed_orbits,
                orbits_by_burnside=burnside,
                orbits_agree=bool(abs(burnside - len(orbits)) < 1e-9))


def v4():
    """recompute (B1) by a different loop and compare with band150_b1.json."""
    V = {}
    with open(os.path.join(ATT, "A143-corner-first-k0", "results",
                           "pairs143_geom.jsonl"), encoding="utf-8") as fh:
        for ln in fh:
            r = json.loads(ln)
            V[(tuple(r["pair"][0]), tuple(r["pair"][1]))] = r["verdict"]

    def canon(a, b):
        def T(k):
            return (k[1], k[0], 5 - k[2])
        return min(tuple(sorted((a, b))), tuple(sorted((T(a), T(b)))))

    cells = [(i, jj, t) for i in range(6) for jj in range(6) for t in range(6)]
    ok = set()
    for a in cells:
        for b in cells:
            if V.get(canon(a, b)) == "ALIVE-CORE":
                ok.add(a)
                break
    band = {tuple(k) for k in json.load(open(os.path.join(RES, "band150.json"),
                                             encoding="utf-8"))["band"]}
    return dict(recomputed=len(ok), on_file=len(band), agree=bool(ok == band),
                dead=sorted(list(map(list, set(cells) - ok))))


def v5():
    """the global box of a cell is the quarter-turn image of its BL box."""
    cell = [c for c in C.all_cells() if (c.ix, c.iy, c.it) == (2, 4, 3)][0]
    b = cell.box
    corners = [(b.x0, b.y0), (b.x1, b.y0), (b.x1, b.y1), (b.x0, b.y1)]
    rot = {"BL": lambda p: p,
           "BR": lambda p: (S0 - p[1], p[0]),
           "TR": lambda p: (S0 - p[0], S0 - p[1]),
           "TL": lambda p: (p[1], S0 - p[0])}
    out = {}
    for c in F.CORNERS:
        gb = F.global_box(c, cell)
        want = [rot[c](p) for p in corners]
        got = {(round(gb.x0, 9), round(gb.y0, 9)), (round(gb.x1, 9), round(gb.y0, 9)),
               (round(gb.x1, 9), round(gb.y1, 9)), (round(gb.x0, 9), round(gb.y1, 9))}
        out[c] = bool({(round(x, 9), round(y, 9)) for x, y in want} == got
                      and gb.th0 == b.th0 and gb.th1 == b.th1)
    return dict(cell=[cell.ix, cell.iy, cell.it], per_corner=out, all_ok=all(out.values()))


def main():
    rng = np.random.default_rng(1500)
    res = dict(V1_d4_group=v1(rng), V2_corner_disjointness=v2(rng),
               V3_counting=v3(rng), V4_band_b1=v4(), V5_frames=v5())
    res["ALL_OK"] = bool(res["V1_d4_group"]["pairwise_distinct"]
                         and res["V1_d4_group"]["closed_under_composition"]
                         and res["V1_d4_group"]["canonical_constant_on_orbits"]
                         and res["V2_corner_disjointness"]["claim_ok"]
                         and res["V2_corner_disjointness"]["gap_exceeds_diameter"]
                         and res["V3_counting"]["agree"]
                         and res["V3_counting"]["orbits_agree"]
                         and res["V4_band_b1"]["agree"]
                         and res["V5_frames"]["all_ok"])
    json.dump(res, open(os.path.join(RES, "verify150.json"), "w"), indent=1)
    print(json.dumps({k: (v if not isinstance(v, dict) else
                          {kk: vv for kk, vv in v.items()
                           if kk not in ("sub_cover", "dead", "names")})
                      for k, v in res.items()}, indent=1))


if __name__ == "__main__":
    main()
