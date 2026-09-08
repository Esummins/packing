"""A150 T1 -- the per-corner ADMISSIBLE BAND for a corner intruder.

A K0-BLOCKED packing has, at EVERY corner box, at least two meeters.  Condition on ONE of them at
each corner (the "first meeter"); its pose lies in one of A143's 216 level-1 cells of the corner
zone `[1/2, a_w + sqrt2/2]^2 x [0, 90)`, stated in that corner's own local frame.

Two necessary conditions on that cell -- both purely geometric, both cheap, both read off data that
already exists:

  (B1) SECOND-MEETER ROOM.  K0-BLOCKED demands a SECOND square meeting the same corner box,
       interior-disjoint from the first.  A143's pair geometry (`results/pairs143_geom.jsonl`)
       decided, for every unordered pair {A, B} of level-1 cells, whether ANY two interior-disjoint
       unit squares can realise it (P2 = max centre distance < 1, P1 = K'(A) meets K'(B),
       P1s = A131 per-sub-bin refinement of P1).  A cell A survives (B1) iff there EXISTS a cell B
       (B = A allowed) with verdict ALIVE-CORE.  If every partner is dead the corner cannot be
       doubly met with its first meeter in A, so the packing is K0-FREE at that corner -- a (T)
       leaf, i.e. the cell is dead on the K0-BLOCKED branch.

  (B2) L-SHAPED-REMAINDER ROOM (the disk bound, A148 `geo148.disk_bound`).  Every unit square
       contains the disk of radius 1/2 about its centre, and the centre of an admissible square
       lies in the feasible-centre region R = {c : SOME tilt puts Q(c,t) inside the container and
       interior-disjoint from the conditioned core}.  A148 certifies an OUTER approximation
       (GREEN u UNDECIDED) of R with margin, so

           budget  <=  area( (GREEN u UNDECIDED) (+) B(1/2)  n  [0,s0]^2 ) / (pi/4)  =:  n_max.

       (B2) is `n_max >= 10` with the ONE conditioned core removed (budget 10 = 11 - 1), and the
       four-corner form `n_max >= 7` is applied to the product in prod150.py.

The band is the set of cells passing (B1) and (B2).  Nothing here is an approximation in the unsafe
direction: (B1) and (B2) are both NECESSARY conditions on a K0-BLOCKED packing, so discarding a cell
that fails either is sound.

    python code/band150.py --stage b1
    python code/band150.py --stage b2 [--pitch 0.02]
    python code/band150.py --stage confirm
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
ROOT = os.path.abspath(os.path.join(ATT, ".."))
for _p in (os.path.join(ATT, "A143-corner-first-k0", "code"),
           os.path.join(ATT, "A148-gallery-v4", "code"),
           os.path.join(ATT, "A132-polygon-core", "code"),
           os.path.join(ATT, "A135-polycore-verifier", "code"),
           os.path.join(ATT, "A118-lane-count", "code"),
           os.path.join(ATT, "A57-shadow-trees", "code"),
           HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import blas1                                                    # noqa: F401,E402
import numpy as np                                              # noqa: E402
import cells143 as C                                            # noqa: E402
import pairs143 as P143                                         # noqa: E402
import polycore                                                 # noqa: E402
import geo148                                                   # noqa: E402

RES = os.path.join(BASE, "results")
A143_PAIRS = os.path.join(ATT, "A143-corner-first-k0", "results", "pairs143_geom.jsonl")
MAXV = 16
S0 = C.S0


# ------------------------------------------------------------------------------ (B1)
def load_pair_verdicts():
    V = {}
    with open(A143_PAIRS, encoding="utf-8") as fh:
        for ln in fh:
            r = json.loads(ln)
            a, b = tuple(r["pair"][0]), tuple(r["pair"][1])
            V[(a, b)] = r["verdict"]
    return V


def b1_stage(out):
    cells = [c for c in C.all_cells() if not c.empty]
    keys = [P143.cell_key(c) for c in cells]
    V = load_pair_verdicts()
    partners = {}
    for a in keys:
        alive = []
        for b in keys:
            v = V.get(P143.pair_canonical(a, b))
            if v == "ALIVE-CORE":
                alive.append(b)
        partners[a] = alive
    rows = [dict(cell=list(a), n_partners=len(partners[a]), b1=bool(partners[a]))
            for a in keys]
    n_ok = sum(1 for r in rows if r["b1"])
    stats = dict(n_cells=len(keys), b1_pass=n_ok, b1_fail=len(keys) - n_ok,
                 pair_rows=len(V),
                 min_partners=min(r["n_partners"] for r in rows),
                 max_partners=max(r["n_partners"] for r in rows),
                 median_partners=float(np.median([r["n_partners"] for r in rows])))
    json.dump(dict(stats=stats, rows=rows), open(out, "w"), indent=1)
    print(json.dumps(stats, indent=1), flush=True)
    return stats


# ------------------------------------------------------------------------------ (B2)
def b2_stage(out, pitch=0.02, ntilt=36, budget=10):
    """disk bound with the ONE conditioned polygon core removed."""
    cells = [c for c in C.all_cells() if not c.empty]
    rows = []
    t0 = time.time()
    for c in cells:
        pc = polycore.build(c.box, max_v=MAXV)
        reg = geo148.feasible_region(S0, [pc.P], pitch_target=pitch, ntilt=ntilt)
        db = geo148.disk_bound(reg)
        rows.append(dict(cell=[c.ix, c.iy, c.it], n_max=db["n_max"],
                         area_dilated=round(db["area_dilated"], 5),
                         area_open=round(db["area_open"], 5),
                         area_green=round(db["area_green"], 5),
                         core_area=float(pc.area()),
                         b2=bool(db["n_max"] >= budget)))
        print("%s n_max=%d open=%.4f core=%.4f" % (rows[-1]["cell"], db["n_max"],
                                                   db["area_open"], rows[-1]["core_area"]),
              flush=True)
    n_ok = sum(1 for r in rows if r["b2"])
    stats = dict(n_cells=len(rows), budget=budget, pitch=pitch, ntilt=ntilt,
                 b2_pass=n_ok, b2_fail=len(rows) - n_ok,
                 n_max_min=min(r["n_max"] for r in rows),
                 n_max_max=max(r["n_max"] for r in rows),
                 secs=round(time.time() - t0, 1))
    json.dump(dict(stats=stats, rows=rows), open(out, "w"), indent=1)
    print(json.dumps(stats, indent=1), flush=True)
    return stats


# ------------------------------------------------------------------------------ the band
def band_keys():
    d = json.load(open(os.path.join(RES, "band150_b1.json"), encoding="utf-8"))
    ok = {tuple(r["cell"]) for r in d["rows"] if r["b1"]}
    p2 = os.path.join(RES, "band150_b2.json")
    if os.path.exists(p2):
        d2 = json.load(open(p2, encoding="utf-8"))
        ok &= {tuple(r["cell"]) for r in d2["rows"] if r["b2"]}
    return sorted(ok)


def band_geometry(keys):
    """width of the band in centre distance from the corner and in tilt."""
    byk = {P143.cell_key(c): c for c in C.all_cells() if not c.empty}
    dmin, dmax, tmin, tmax = 9e9, -9e9, 9e9, -9e9
    for k in keys:
        b = byk[k].box
        dmin = min(dmin, math.hypot(b.x0, b.y0))
        dmax = max(dmax, math.hypot(b.x1, b.y1))
        tmin = min(tmin, b.th0)
        tmax = max(tmax, b.th1)
    return dict(n=len(keys), d_min=dmin, d_max=dmax, d_width=dmax - dmin,
                th_min=tmin, th_max=tmax, th_width=tmax - tmin,
                tilt_bins=sorted({k[2] for k in keys}),
                pos_cells=sorted({(k[0], k[1]) for k in keys}))


# ------------------------------------------------------------ drawn -> tested -> hits
def confirm_stage(out, n=20000, seed=150):
    """Draw admissible K0-BLOCKED BL 2-crowds (two interior-disjoint unit squares in the container,
    both meeting the widened BL box) and check that the FIRST meeter always lands in a band cell.
    Both members are first meeters, so both must land in the band -- that is the claim."""
    keys = set(band_keys())
    rng = np.random.default_rng(seed)
    drawn = hits = miss = 0
    bad = []
    a_w = C.A_W
    t0 = time.time()
    lo, hi = C.ZLO, C.ZHI
    boxpoly = [(0.0, 0.0), (a_w, 0.0), (a_w, a_w), (0.0, a_w)]
    w = (C.ZHI - C.ZLO) / C.NPOS
    n_exact_checked = 0

    def raw_cell(cx, cy, th):
        if not (C.ZLO - 1e-12 <= cx <= C.ZHI + 1e-12 and C.ZLO - 1e-12 <= cy <= C.ZHI + 1e-12):
            return None
        return (min(C.NPOS - 1, max(0, int((cx - C.ZLO) / w))),
                min(C.NPOS - 1, max(0, int((cy - C.ZLO) / w))),
                min(C.NTILT - 1, max(0, int((th % 90.0) / C.TILT_W))))

    while drawn < n and time.time() - t0 < 1200:
        m = 20000
        X = rng.uniform(lo, hi, (m, 2, 2))
        TH = rng.uniform(0.0, 90.0, (m, 2))
        hh = 0.5 * (np.cos(np.radians(TH)) + np.sin(np.radians(TH)))
        inside = ((X[:, :, 0] >= hh) & (X[:, :, 0] <= S0 - hh)
                  & (X[:, :, 1] >= hh) & (X[:, :, 1] <= S0 - hh)).all(1)
        for i in np.nonzero(inside)[0]:
            if drawn >= n:
                break
            P = [geo148.sqpoly(X[i, j, 0], X[i, j, 1], math.radians(TH[i, j])) for j in (0, 1)]
            if geo148.sat_gap(P[0], boxpoly) >= 0.0 or geo148.sat_gap(P[1], boxpoly) >= 0.0:
                continue                       # both must MEET the widened BL box
            if geo148.sat_gap(P[0], P[1]) <= 0.0:
                continue                       # and be interior-disjoint
            drawn += 1
            good = True
            for j in (0, 1):
                raw = raw_cell(X[i, j, 0], X[i, j, 1], TH[i, j])
                loc = C.locate(X[i, j, 0], X[i, j, 1], TH[i, j])
                if (raw is None) or (raw not in keys) or (loc not in keys):
                    good = False
                    if len(bad) < 8:
                        bad.append(dict(pose=[float(X[i, j, 0]), float(X[i, j, 1]),
                                              float(TH[i, j])], loc=loc, raw=raw))
            if drawn <= 200:                   # cross-check the float meet test against A143's
                for j in (0, 1):               # EXACT rational f_min_max on the first 200 draws
                    n_exact_checked += 1
                    if not C.meets_bl(X[i, j, 0], X[i, j, 1], TH[i, j], a_w=a_w):
                        bad.append(dict(pose=[float(X[i, j, 0]), float(X[i, j, 1]),
                                              float(TH[i, j])], why="EXACT-MEET-DISAGREES"))
                        good = False
            hits += int(good)
            miss += int(not good)
    res = dict(drawn=drawn, hits=hits, misses=miss, bad=bad, band_cells=len(keys),
               n_exact_cross_checked=n_exact_checked,
               claim="every member of a drawn realised BL 2-crowd lies in a band cell",
               secs=round(time.time() - t0, 1))
    json.dump(res, open(out, "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "bad"}, indent=1), flush=True)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=("b1", "b2", "confirm", "summary"))
    ap.add_argument("--pitch", type=float, default=0.02)
    ap.add_argument("--ntilt", type=int, default=36)
    ap.add_argument("--n", type=int, default=20000)
    a = ap.parse_args()
    os.makedirs(RES, exist_ok=True)
    if a.stage == "b1":
        b1_stage(os.path.join(RES, "band150_b1.json"))
    elif a.stage == "b2":
        b2_stage(os.path.join(RES, "band150_b2.json"), pitch=a.pitch, ntilt=a.ntilt)
    elif a.stage == "confirm":
        confirm_stage(os.path.join(RES, "band150_confirm.json"), n=a.n)
    else:
        keys = band_keys()
        g = band_geometry(keys)
        json.dump(dict(band=[list(k) for k in keys], geometry=g),
                  open(os.path.join(RES, "band150.json"), "w"), indent=1)
        print(json.dumps(g, indent=1), flush=True)


if __name__ == "__main__":
    main()
