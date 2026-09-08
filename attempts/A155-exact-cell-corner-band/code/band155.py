"""A155 T1 -- the per-corner band (B1) as a function of the K0-WIDEN pad.

(B1), verbatim from A150 but with the pad a parameter: a first-meeter cell A survives iff there
EXISTS a cell B (B = A allowed) such that some pose in A and some pose in B can be two distinct
interior-disjoint unit squares both meeting the corner box interior-to-interior.  The test is the
sound over-approximation A143 used:

    (P0)  container + reach clip of each cell                          -> the cell is empty
    (P2)  max centre distance over the two clipped boxes < 1           -> the pair is (C)
    (P1)  K'(A) meets K'(B)  (A132 exact polygon cores)                -> the pair is (C)
    (P1s) A131 per-tilt-sub-bin refinement of (P1) on both members     -> the pair is (C)

A cell with no surviving partner cannot be the first meeter of a 2-crowd, so the corner is met by
<= 1 square and Lemma K0-FREE teleports the packing into a k >= 1 class: the cell is a (T) leaf.

Stages:
    pairs   the pair census + the band, per pad                (results/band155_pairs_<tag>.json)
    confirm drawn -> tested -> hits, per pad                   (results/band155_confirm_<tag>.json)
    occ     per-cell POSE-LEVEL occupancy (diagnostic: how slim is the second-meeter space inside
            a surviving cell, i.e. what a finer cover could still win)  (band155_occ_<tag>.json)
    selftest float geometry vs A148's sat_gap and A143's exact rational meet test
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
           os.path.join(ATT, "A57-shadow-trees", "code"),
           HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import blas1                                                    # noqa: F401,E402
import numpy as np                                              # noqa: E402
import polycore                                                 # noqa: E402
import cells155 as C                                            # noqa: E402
import geom155 as G                                             # noqa: E402
from caselp import Box                                          # noqa: E402

RES = os.path.join(BASE, "results")
MAXV = 16
NSUB_PAIR = 4
S0 = C.S0


def pad_by_tag(tag):
    for t, w, why in C.PADS:
        if t == tag:
            return w, why
    raise SystemExit("unknown pad tag " + tag)


def max_centre_dist(b1, b2):
    dx = max(abs(b1.x1 - b2.x0), abs(b2.x1 - b1.x0))
    dy = max(abs(b1.y1 - b2.y0), abs(b2.y1 - b1.y0))
    return math.hypot(dx, dy)


def build_cores(cells, a_w):
    K, KS = {}, {}
    for c in cells:
        if c.empty:
            continue
        K[c.key] = polycore.build(c.box, max_v=MAXV)
        subs = []
        for (a, b, cl) in C.subbin_clip(*c.raw, a_w=a_w, nsub=NSUB_PAIR):
            bx = Box(cl[0], cl[1], cl[2], cl[3], a, b)
            try:
                subs.append(polycore.build(bx, max_v=MAXV))
            except Exception:                                   # noqa: BLE001
                subs.append(None)
        KS[c.key] = subs
    return K, KS


def pairs_stage(tag, log=print):
    w, why = pad_by_tag(tag)
    a_w = 1.0 + w
    cells = [c for c in C.all_cells(a_w) if not c.empty]
    byk = {c.key: c for c in cells}
    keys = sorted(byk)
    t0 = time.time()
    K, KS = build_cores(cells, a_w)
    log("%s: %d live cells, cores in %.0f s" % (tag, len(keys), time.time() - t0))
    seen = set()
    stats = dict(P2=0, P1=0, P1s=0, alive=0, canonical=0)
    partners = {k: 0 for k in keys}
    alive_pairs = []
    for i, k1 in enumerate(keys):
        for k2 in keys[i:]:
            cc = C.pair_canonical(k1, k2)
            if cc in seen:
                continue
            seen.add(cc)
            stats["canonical"] += 1
            a, b = cc
            if max_centre_dist(byk[a].box, byk[b].box) < 1.0:
                stats["P2"] += 1
                continue
            if polycore.poly_poly_depth(K[a].P, K[b].P) > 0.0:
                stats["P1"] += 1
                continue
            nsub_alive = 0
            for p1 in KS[a]:
                for p2 in KS[b]:
                    if p1 is None or p2 is None:
                        nsub_alive += 1
                    elif polycore.poly_poly_depth(p1.P, p2.P) <= 0.0:
                        nsub_alive += 1
            if nsub_alive == 0:
                stats["P1s"] += 1
                continue
            stats["alive"] += 1
            alive_pairs.append((a, b))
            # the verdict is canonical; credit BOTH members and both transposes
            for (u, v) in ((a, b), (C.transpose_key(a), C.transpose_key(b))):
                partners[u] = partners.get(u, 0) + 1
                if v != u:
                    partners[v] = partners.get(v, 0) + 1
    band = sorted(k for k in keys if partners.get(k, 0) > 0)
    geo = band_geometry(band, byk)
    out = dict(tag=tag, pad=w, why=why, a_w=a_w, slab=C.slab_of_pad(w),
               n_cells=len(C.all_cells(a_w)), n_live=len(keys),
               pair_stats=stats, band=len(band), band_cells=[list(k) for k in band],
               dead_cells=[list(k) for k in keys if partners.get(k, 0) == 0],
               partners={"%d%d%d" % k: partners.get(k, 0) for k in keys},
               geometry=geo, secs=round(time.time() - t0, 1))
    json.dump(out, open(os.path.join(RES, "band155_pairs_%s.json" % tag), "w"), indent=1)
    log("%s: pad %.7f  band %d/%d  pairs %s  %.0f s"
        % (tag, w, len(band), len(C.all_cells(a_w)), json.dumps(stats), time.time() - t0))
    return out


def refine_stage(tag, npos, ntilt, log=print):
    """(B1) on a REFINED cover (npos x npos positions x ntilt tilt windows).  Only the BAND is
    computed, not the full pair census: for each cell A the partners B are tried in order of
    decreasing max centre distance (the most likely to be alive first) and the loop stops at the
    first ALIVE-CORE partner, so a surviving cell costs O(1) tests and only a dying cell costs the
    full row.  The verdict per pair is A143's exact (P2)/(P1)/(P1s) chain, unchanged."""
    w, why = pad_by_tag(tag)
    a_w = 1.0 + w
    cells = [c for c in C.all_cells(a_w, npos, ntilt) if not c.empty]
    keys = sorted(c.key for c in cells)
    byk = {c.key: c for c in cells}
    t0 = time.time()
    K, KS = {}, {}

    def core(k):
        if k not in K:
            K[k] = polycore.build(byk[k].box, max_v=MAXV)
        return K[k]

    def subcores(k):
        if k not in KS:
            subs = []
            for (a, b, cl) in C.subbin_clip(*byk[k].raw, a_w=a_w, nsub=NSUB_PAIR):
                bx = Box(cl[0], cl[1], cl[2], cl[3], a, b)
                try:
                    subs.append(polycore.build(bx, max_v=MAXV))
                except Exception:                               # noqa: BLE001
                    subs.append(None)
            KS[k] = subs
        return KS[k]

    def alive_pair(a, b):
        if max_centre_dist(byk[a].box, byk[b].box) < 1.0:
            return False
        if polycore.poly_poly_depth(core(a).P, core(b).P) > 0.0:
            return False
        for p1 in subcores(a):
            for p2 in subcores(b):
                if p1 is None or p2 is None:
                    return True
                if polycore.poly_poly_depth(p1.P, p2.P) <= 0.0:
                    return True
        return False

    band, dead, ntests = [], [], 0
    for i, a in enumerate(keys):
        ba = byk[a].box
        order = sorted(keys, key=lambda b: -max_centre_dist(ba, byk[b].box))
        hit = None
        for b in order:
            ntests += 1
            if alive_pair(a, b):
                hit = b
                break
        (band if hit else dead).append(a)
        if (i + 1) % 100 == 0:
            log("  %s p%dt%d: %d/%d cells, band %d, %d pair tests, %.0f s"
                % (tag, npos, ntilt, i + 1, len(keys), len(band), ntests, time.time() - t0))
    geo = band_geometry(band, byk)
    out = dict(tag=tag, pad=w, why=why, a_w=a_w, npos=npos, ntilt=ntilt,
               n_cells=npos * npos * ntilt, n_live=len(keys), band=len(band),
               band_cells=[list(k) for k in band], dead_cells=[list(k) for k in dead],
               n_pair_tests=ntests, geometry=geo, secs=round(time.time() - t0, 1))
    json.dump(out, open(os.path.join(RES, "band155_refine_%s_p%dt%d.json"
                                     % (tag, npos, ntilt)), "w"), indent=1)
    log("%s p%dt%d: band %d/%d (live %d), %d pair tests, %.0f s"
        % (tag, npos, ntilt, len(band), npos * npos * ntilt, len(keys), ntests,
           time.time() - t0))
    return out


def band_geometry(keys, byk):
    if not keys:
        return dict(n=0)
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
                n_pos_cells=len({(k[0], k[1]) for k in keys}))


# --------------------------------------------------------------- drawn -> tested -> hits
def draw_crowds(rng, a_w, n, block=200000, tlim=600.0):
    """draw realised BL 2-crowds at pad w: two interior-disjoint unit squares inside [0, s0]^2,
    both meeting the OPEN box [0, a_w)^2.  Returns (cx, cy, th) arrays of shape (n, 2)."""
    zlo, zhi = C.zone(a_w)
    got = [[], [], []]
    ndrawn = 0
    t0 = time.time()
    while ndrawn < n and time.time() - t0 < tlim:
        X = rng.uniform(zlo, zhi, (block, 2, 2))
        TH = rng.uniform(0.0, 90.0, (block, 2))
        ok = G.in_container(X[:, :, 0], X[:, :, 1], TH, S0).all(1)
        ok &= (G.fmm(X[:, :, 0], X[:, :, 1], TH) < a_w).all(1)
        ok &= G.sat_gap(X[:, 0], TH[:, 0], X[:, 1], TH[:, 1]) > 0.0
        idx = np.nonzero(ok)[0]
        if len(idx) == 0:
            continue
        idx = idx[:max(0, n - ndrawn)]
        got[0].append(X[idx, :, 0]); got[1].append(X[idx, :, 1]); got[2].append(TH[idx])
        ndrawn += len(idx)
    return (np.concatenate(got[0]) if got[0] else np.zeros((0, 2)),
            np.concatenate(got[1]) if got[1] else np.zeros((0, 2)),
            np.concatenate(got[2]) if got[2] else np.zeros((0, 2)))


def confirm_stage(tag, n=8000, seed=155, nexact=200, log=print):
    w, _why = pad_by_tag(tag)
    a_w = 1.0 + w
    d = json.load(open(os.path.join(RES, "band155_pairs_%s.json" % tag), encoding="utf-8"))
    band = {tuple(k) for k in d["band_cells"]}
    rng = np.random.default_rng(seed)
    t0 = time.time()
    CX, CY, TH = draw_crowds(rng, a_w, n)
    hits = miss = 0
    bad = []
    for i in range(len(CX)):
        good = True
        for j in (0, 1):
            loc = C.locate(CX[i, j], CY[i, j], TH[i, j], a_w)
            if loc is None or loc not in band:
                good = False
                if len(bad) < 8:
                    bad.append(dict(pose=[float(CX[i, j]), float(CY[i, j]), float(TH[i, j])],
                                    loc=loc))
        hits += int(good)
        miss += int(not good)
    nx = 0
    for i in range(min(nexact, len(CX))):
        for j in (0, 1):
            nx += 1
            if not C.meets_bl_exact(CX[i, j], CY[i, j], TH[i, j], a_w):
                bad.append(dict(pose=[float(CX[i, j]), float(CY[i, j]), float(TH[i, j])],
                                why="EXACT-MEET-DISAGREES"))
    res = dict(tag=tag, pad=w, drawn=int(len(CX)), hits=hits, misses=miss,
               band_cells=len(band), n_exact_cross_checked=nx, bad=bad,
               claim="every member of a drawn realised BL 2-crowd at this pad lies in a band cell",
               secs=round(time.time() - t0, 1))
    json.dump(res, open(os.path.join(RES, "band155_confirm_%s.json" % tag), "w"), indent=1)
    log("%s: confirm drawn %d hits %d misses %d exact-xchecks %d (%.0f s)"
        % (tag, res["drawn"], hits, miss, nx, res["secs"]))
    return res


# ------------------------------------------------- per-cell POSE-LEVEL occupancy (diagnostic)
def occ_stage(tag, nfirst=200, npool=6000, seed=1551, log=print):
    """For each cell: sample first-meeter poses IN the cell (container + reach filtered) and, for
    each, ask whether ANY pose from a common pool of realised meeters is interior-disjoint from it.
    p_cell = fraction of sampled first meeters with a witnessed partner.

    p_cell = 0 over the sample does NOT kill the cell (it is a sampling statement, not a proof),
    but p_cell = 1 does show the cell is UNKILLABLE by any refinement of (B1): a positive-measure
    set of genuine 2-crowds has its first meeter there."""
    w, _why = pad_by_tag(tag)
    a_w = 1.0 + w
    zlo, zhi = C.zone(a_w)
    rng = np.random.default_rng(seed)
    # common pool of realised meeters
    pool = [[], [], []]
    while len(pool[0]) < 1 or sum(len(x) for x in pool[0:1]) < npool:
        X = rng.uniform(zlo, zhi, (4 * npool, 2))
        T = rng.uniform(0.0, 90.0, 4 * npool)
        ok = G.in_container(X[:, 0], X[:, 1], T, S0) & (G.fmm(X[:, 0], X[:, 1], T) < a_w)
        pool[0].append(X[ok, 0]); pool[1].append(X[ok, 1]); pool[2].append(T[ok])
        if sum(len(a) for a in pool[0]) >= npool:
            break
    PX = np.concatenate(pool[0])[:npool]
    PY = np.concatenate(pool[1])[:npool]
    PT = np.concatenate(pool[2])[:npool]
    PC = np.stack([PX, PY], -1)
    cells = [c for c in C.all_cells(a_w) if not c.empty]
    t0 = time.time()
    rows = []
    for c in cells:
        b = c.box
        # sample first meeters inside the clipped cell box
        fx = fy = ft = None
        tries = 0
        keepx, keepy, keept = [], [], []
        while sum(len(a) for a in keepx) < nfirst and tries < 40:
            tries += 1
            X = rng.uniform([b.x0, b.y0], [b.x1, b.y1], (8 * nfirst, 2))
            T = rng.uniform(b.th0, b.th1, 8 * nfirst)
            ok = G.in_container(X[:, 0], X[:, 1], T, S0) & (G.fmm(X[:, 0], X[:, 1], T) < a_w)
            keepx.append(X[ok, 0]); keepy.append(X[ok, 1]); keept.append(T[ok])
        fx = np.concatenate(keepx)[:nfirst]
        fy = np.concatenate(keepy)[:nfirst]
        ft = np.concatenate(keept)[:nfirst]
        if len(fx) == 0:
            rows.append(dict(cell=list(c.key), n_first=0, p=None, note="no realised meeter sampled"))
            continue
        FC = np.stack([fx, fy], -1)
        npart = np.zeros(len(fx), np.int64)
        for s in range(0, len(PX), 1000):                       # chunked: keep temporaries small
            e = min(s + 1000, len(PX))
            gaps = G.sat_gap(FC[:, None, :], ft[:, None], PC[None, s:e, :], PT[None, s:e])
            npart += (gaps > 0.0).sum(1)
        rows.append(dict(cell=list(c.key), n_first=int(len(fx)),
                         p=float((npart > 0).mean()),
                         mean_partners=float(npart.mean() / len(PX)),
                         min_partners=int(npart.min()), max_partners=int(npart.max())))
    ps = [r["p"] for r in rows if r["p"] is not None]
    out = dict(tag=tag, pad=w, npool=len(PX), nfirst=nfirst, n_cells=len(rows),
               n_p_zero=sum(1 for p in ps if p == 0.0),
               n_p_one=sum(1 for p in ps if p == 1.0),
               n_p_lt_01=sum(1 for p in ps if p < 0.1),
               p_min=min(ps) if ps else None, p_median=float(np.median(ps)) if ps else None,
               n_no_meeter=sum(1 for r in rows if r["p"] is None),
               rows=rows, secs=round(time.time() - t0, 1))
    json.dump(out, open(os.path.join(RES, "band155_occ_%s.json" % tag), "w"), indent=1)
    log("%s: occupancy p_min=%s p_med=%s  cells with p=0: %d, p=1: %d, p<0.1: %d (%.0f s)"
        % (tag, out["p_min"], out["p_median"], out["n_p_zero"], out["n_p_one"],
           out["n_p_lt_01"], out["secs"]))
    return out


# ------------------------------------------------------------------------------- selftest
def selftest(log=print):
    import geo148                                               # noqa: E402
    import cells143 as C143                                     # noqa: E402  (read-only)
    rng = np.random.default_rng(7)
    N = 400
    X = rng.uniform(0.4, 2.2, (N, 2, 2))
    T = rng.uniform(0.0, 90.0, (N, 2))
    g_mine = G.sat_gap(X[:, 0], T[:, 0], X[:, 1], T[:, 1])
    g_148 = np.array([geo148.sat_gap(geo148.sqpoly(X[i, 0, 0], X[i, 0, 1], math.radians(T[i, 0])),
                                     geo148.sqpoly(X[i, 1, 0], X[i, 1, 1], math.radians(T[i, 1])))
                      for i in range(N)])
    dsat = float(np.abs(g_mine - g_148).max())
    # fmm vs A143's exact rational f_min_max, and vs A143's meets_bl at the full pad
    f_mine = G.fmm(X[:, 0, 0], X[:, 0, 1], T[:, 0])
    dis = 0
    for i in range(120):
        if bool(f_mine[i] < C143.A_W) != C143.meets_bl(X[i, 0, 0], X[i, 0, 1], T[i, 0]):
            dis += 1
    # cells155 at the full pad must reproduce cells143 exactly
    a = [c.to_json() for c in C.all_cells(C143.A_W)]
    b = [c.to_json() for c in C143.all_cells()]
    same = all(x["raw"] == y["raw"] and x["empty"] == y["empty"] and
               ((x["box"] is None and y["box"] is None) or x["box"] == y["box"])
               for x, y in zip(a, b))
    out = dict(sat_max_abs_diff_vs_geo148=dsat, meet_test_disagreements=dis,
               cells155_matches_cells143_at_full_pad=bool(same), n=N)
    json.dump(out, open(os.path.join(RES, "band155_selftest.json"), "w"), indent=1)
    log(json.dumps(out, indent=1))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True,
                    choices=("pairs", "confirm", "occ", "refine", "selftest", "summary"))
    ap.add_argument("--npos", type=int, default=12)
    ap.add_argument("--ntilt", type=int, default=6)
    ap.add_argument("--pads", default="all")
    ap.add_argument("--n", type=int, default=8000)
    ap.add_argument("--nfirst", type=int, default=200)
    ap.add_argument("--npool", type=int, default=6000)
    a = ap.parse_args()
    os.makedirs(RES, exist_ok=True)
    tags = [t for t, _w, _y in C.PADS] if a.pads == "all" else a.pads.split(",")
    if a.stage == "selftest":
        selftest()
        return
    if a.stage == "summary":
        rows = []
        for t in tags:
            d = json.load(open(os.path.join(RES, "band155_pairs_%s.json" % t), encoding="utf-8"))
            cf = os.path.join(RES, "band155_confirm_%s.json" % t)
            oc = os.path.join(RES, "band155_occ_%s.json" % t)
            r = dict(tag=t, pad=d["pad"], slab=d["slab"], band=d["band"],
                     n_cells=d["n_cells"], pair_stats=d["pair_stats"], geometry=d["geometry"])
            if os.path.exists(cf):
                c = json.load(open(cf, encoding="utf-8"))
                r["confirm"] = dict(drawn=c["drawn"], hits=c["hits"], misses=c["misses"],
                                    exact=c["n_exact_cross_checked"])
            if os.path.exists(oc):
                o = json.load(open(oc, encoding="utf-8"))
                r["occ"] = {k: o[k] for k in ("p_min", "p_median", "n_p_zero", "n_p_one",
                                              "n_p_lt_01", "nfirst", "npool")}
            rows.append(r)
        json.dump(rows, open(os.path.join(RES, "band155_summary.json"), "w"), indent=1)
        for r in rows:
            print("%-8s pad %.7f slab %.5f  band %3d/%d  alive-pairs %6d  %s"
                  % (r["tag"], r["pad"], r["slab"], r["band"], r["n_cells"],
                     r["pair_stats"]["alive"], r.get("confirm", "")))
        return
    for t in tags:
        if a.stage == "pairs":
            pairs_stage(t)
        elif a.stage == "confirm":
            confirm_stage(t, n=a.n)
        elif a.stage == "refine":
            refine_stage(t, a.npos, a.ntilt)
        else:
            occ_stage(t, nfirst=a.nfirst, npool=a.npool)


if __name__ == "__main__":
    main()
