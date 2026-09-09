"""A165 -- the CASCADE case tree driver.

Stages (each writes to results/, each resumable, every sentinel honoured):

  cover    the four widened-corner meeter covers of the cell, + where the canary's real meeters sit
  pairs    the TR (or any corner) meeter PAIRS after the two sound pair prunes
  geom     the LP-free leaf battery on each pair: chord row, uncoverable area, disk bound
  lp3      the three-box case-LP  {H, D, S}  at budget 11 - 3 = 8
  lp5      the five-box case-LP   {H, D, S, TL_a, TL_b}  at budget 11 - 5 = 6

    python code/cascade165.py cover --cell l1_104 --depth 8
    python code/cascade165.py pairs --cell l1_104 --depth 8
    python code/cascade165.py geom  --cell l1_104 --depth 8
    python code/cascade165.py lp3   --cell l1_104 --depth 8 --sample 40 --cap 150
"""
import argparse
import itertools
import json
import math
import os
import random
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cas165 as K                                               # noqa: E402
import numpy as np                                               # noqa: E402
import polylane as PL                                            # noqa: E402
import guardline as GL                                           # noqa: E402
from caselp import Box                                           # noqa: E402

RES = os.path.join(K.BASE, "results")
CERTS = os.path.join(K.BASE, "certs")
LOGS = os.path.join(K.BASE, "logs")
for _d in (RES, CERTS, LOGS):
    os.makedirs(_d, exist_ok=True)

B0 = K.S0 * K.S0 - 11.0                     # A89 Lemma ID wastage budget at s0


# ===================================================================== helpers
def tag(cell, depth):
    return "%s_d%d" % (cell, depth)


def cover_path(cell, depth):
    return os.path.join(RES, "cover_%s.json" % tag(cell, depth))


def pairs_path(cell, depth, corner):
    return os.path.join(RES, "pairs_%s_%s.json" % (tag(cell, depth), corner))


def geom_path(cell, depth, corner):
    return os.path.join(RES, "geom_%s_%s.jsonl" % (tag(cell, depth), corner))


def line_family(orient, lo, hi, n, den=100000):
    """n exact rational lines with offsets strictly inside (lo, hi)."""
    out = []
    for i in range(1, n + 1):
        v = lo + (hi - lo) * i / (n + 1.0)
        off = Fr(int(round(v * den)), den)
        out.append(GL.Line(orient, off))
    return out


TOP_LINES = None
RIGHT_LINES = None


def wall_lines(n=24):
    """The wall-row lines the cascade uses: the TOP strip (y in (s0-1-w, s0)) and the RIGHT strip
    (x in (s0-1-w, s0)), plus the mirror pair at the bottom/left."""
    lo = K.S0 - 1.0 - K.W0
    return dict(top=line_family("h", lo, K.S0, n),
                right=line_family("v", lo, K.S0, n),
                bottom=line_family("h", 0.0, 1.0 + K.W0, n),
                left=line_family("v", 0.0, 1.0 + K.W0, n))


def row_scan(boxes, lines):
    """min over `lines` of rhs(l) = s0 - SUM_j minchord(B_j, l).  rhs < 0 is a (C) leaf: the
    chords of an interior-disjoint family on an axis line cannot exceed the side (A144 LINE-1)."""
    best = None
    for l in lines:
        r = K.chord_row(boxes, l)
        if best is None or r["rhs_f"] < best["rhs_f"]:
            best = r
    return best


# ===================================================================== stage: cover
def stage_cover(a):
    meta, rec, boxes = K.load_node(a.cell)
    conds = PL.build_cond(boxes, verbose=False)
    out = dict(cell=a.cell, depth0=a.depth, s0=K.S0, w=K.W0, a_w=K.AW, r6_gap=K.r6_gap(),
               boxes=[K.bx_json(b) for b in boxes], budget=rec["budget"], tau=rec["tau"],
               covers={}, canary=None)
    for corner in K.CORNERS:
        t0 = time.time()
        cov = K.meeter_cover(corner, conds, depth0=a.depth, max_open=a.max_open)
        out["covers"][corner] = dict(
            cell=K.corner_cell(corner), complete=cov.get("complete"), lane=cov.get("lane"),
            n_leaves=len(cov.get("leaves", [])), n_open=len(cov.get("open", [])),
            open=[o["box"] for o in cov.get("open", [])],
            open_paths=[o["path"] for o in cov.get("open", [])],
            leaves=[dict(path=lf["path"], why=lf["why"], j=lf.get("j"), w=lf.get("w"))
                    for lf in cov.get("leaves", [])],
            wall_s=round(time.time() - t0, 1))
        print("%-8s %-3s leaves=%4d open=%4d %5.1fs" % (
            a.cell, corner, out["covers"][corner]["n_leaves"],
            out["covers"][corner]["n_open"], out["covers"][corner]["wall_s"]), flush=True)

    # M(c): can the conditioned square meet the widened corner cell?  (A141's exclusion cover)
    out["M"] = {}
    for corner in K.CORNERS:
        cell = K.corner_cell(corner)
        r = PL.cond_can_meet(conds[0], cell, conds, s=K.S0, max_open=400)
        out["M"][corner] = dict(excluded=bool(r["ok"]), n_leaves=r["n_leaves"],
                                n_open=len(r.get("open", [])))
    # the exact A161 primitive as an independent second opinion on M
    out["M_exact"] = {}
    for c in K.CORNERS:
        ok, det = K.box_misses_cell_exact(boxes[0], K.corner_cell(c))
        out["M_exact"][c] = dict(misses=ok, detail=det)
    print("M (A141 cover):", {c: out["M"][c]["excluded"] for c in K.CORNERS},
          " M_exact (A161 SAT):", {c: out["M_exact"][c]["misses"] for c in K.CORNERS}, flush=True)

    # the canary: where do the real Trump meeters sit in the covers?
    import trump165 as T
    IM, s_trump, lam = T.images()
    hits = []
    for k, Z in IM:
        rep = T.image_report(Z, boxes)
        if not rep["hyp_hits"]:
            continue
        hyp_sq = {hh["sq"] for hh in rep["hyp_hits"]}
        loc = {}
        for corner in K.CORNERS:
            obs = [Box(*b) for b in out["covers"][corner]["open"]]
            ms = []
            for m in rep["corners"][corner]["meeters"]:
                p = m["pose"]
                ms.append(dict(sq=m["sq"], pose=p, is_H=bool(m["sq"] in hyp_sq),
                               box=K.box_of_pose(p[0], p[1], p[2], obs)))
            loc[corner] = dict(n_widened=rep["corners"][corner]["n_widened"],
                               n_plain=rep["corners"][corner]["n_plain"], meeters=ms,
                               n_free=sum(1 for m in ms if not m["is_H"]),
                               n_H=sum(1 for m in ms if m["is_H"]))
        hits.append(dict(image="g%d" % k, hyp_hits=rep["hyp_hits"], corners=loc,
                         poses=[[round(v, 9) for v in p] for p in Z]))
    out["canary"] = dict(s_trump=s_trump, lam=lam, images=hits)
    K.jdump(out, cover_path(a.cell, a.depth))
    print("wrote", cover_path(a.cell, a.depth), flush=True)
    if hits:
        for h in hits:
            for c in K.CORNERS:
                ms = h["corners"][c]["meeters"]
                miss = [m for m in ms if m["box"] is None and not m["is_H"]]
                print("CANARY %s %s: %d widened meeters (%d free, %d = H), free unlocated %d %s"
                      % (h["image"], c, h["corners"][c]["n_widened"], h["corners"][c]["n_free"],
                         h["corners"][c]["n_H"], len(miss),
                         "*** COVER MISSES A REAL MEETER ***" if miss else "OK"), flush=True)


# ===================================================================== stage: pairs
def stage_pairs(a):
    cov = json.load(open(cover_path(a.cell, a.depth), encoding="utf-8"))
    corner = a.corner
    obs = [Box(*b) for b in cov["covers"][corner]["open"]]
    n = len(obs)
    t0 = time.time()
    OV = K.pair_matrix(obs)
    # the vectorised screen is COARSE; A118's sharp per-normal test rescues survivors
    ii, jj = np.nonzero(np.triu(~OV, 0))
    cand = list(zip(ii.tolist(), jj.tolist()))
    sharp = []
    for (u, v) in cand:
        if K.pair_always_overlap(obs[u], obs[v]):
            continue
        sharp.append((u, v))
    print("%s %s: %d open boxes, %d/%d unordered pairs survive OVL (%.1fs)" % (
        a.cell, corner, n, len(sharp), n * (n + 1) // 2, time.time() - t0), flush=True)

    # (PAIR) a rational point in every pose of both boxes -> the SAME square -> impossible
    same, alive = [], []
    for (u, v) in sharp:
        w = K.pair_same_square(obs[u], obs[v]) if u != v else None
        if w is not None:
            same.append(dict(i=u, j=v, w=w))
        else:
            alive.append((u, v))
    out = dict(cell=a.cell, depth0=a.depth, corner=corner, n_open=n,
               n_pairs_raw=n * (n + 1) // 2, n_after_ovl=len(sharp),
               n_same_square=len(same), n_alive=len(alive),
               same_square=same[:400], pairs=alive, wall_s=round(time.time() - t0, 1))
    # the case FAMILY at this corner.  M(c) = 0 (certified by A161's exact SAT) forces both meeters
    # to be FREE squares -- the pair cases below.  M(c) >= 1 adds the mixed case {H, one free}.
    M_exact = cov["M_exact"][corner]["misses"] if isinstance(cov["M_exact"][corner], dict) \
        else bool(cov["M_exact"][corner])
    out["M_exact_misses"] = bool(M_exact)
    out["case_family"] = ("pair-only (M=0, certified by A161 box_misses_cell_exact)"
                          if M_exact else "pair OR mixed {H, one free} (M >= 1)")
    out["mixed_cases"] = ([] if M_exact else [[i] for i in range(n)])

    # locate the canary's real crowd
    for h in cov.get("canary", {}).get("images", []):
        ms = h["corners"][corner]["meeters"]
        free_boxes = sorted({m["box"] for m in ms if not m["is_H"] and m["box"] is not None})
        n_H = sum(1 for m in ms if m["is_H"])
        if n_H:
            cp = [[i] for i in free_boxes]                       # mixed cases {H, free box i}
            aliveset = {tuple(c) for c in out["mixed_cases"]}
        else:
            cp = [list(p) for p in itertools.combinations_with_replacement(free_boxes, 2)]
            aliveset = set(alive)
        out.setdefault("canary_pairs", []).append(
            dict(image=h["image"], boxes=free_boxes, n_H=n_H, kind=("mixed" if n_H else "pair"),
                 pairs=cp, alive=[p for p in cp if tuple(p) in aliveset],
                 unlocated=[m["sq"] for m in ms if m["box"] is None and not m["is_H"]]))
    K.jdump(out, pairs_path(a.cell, a.depth, corner))
    print("  same-square prune %d, ALIVE %d -> %s" % (len(same), len(alive),
                                                      pairs_path(a.cell, a.depth, corner)),
          flush=True)
    if "canary_pairs" in out:
        for cpv in out["canary_pairs"]:
            print("  CANARY %s boxes %s: %d pairs, %d alive" % (
                cpv["image"], cpv["boxes"], len(cpv["pairs"]), len(cpv["alive"])), flush=True)


# ===================================================================== stage: geom
def stage_geom(a):
    sys.path.insert(0, os.path.join(K.ATT, "A164-wastage-area", "code"))
    import geo164 as G                                            # noqa: E402
    cov = json.load(open(cover_path(a.cell, a.depth), encoding="utf-8"))
    pr = json.load(open(pairs_path(a.cell, a.depth, a.corner), encoding="utf-8"))
    H = Box(*cov["boxes"][0])
    obs = [Box(*b) for b in cov["covers"][a.corner]["open"]]
    LN = wall_lines(a.nlines)
    out = geom_path(a.cell, a.depth, a.corner)
    done = set()
    if os.path.exists(out):
        for ln in open(out, encoding="utf-8"):
            try:
                done.add(tuple(json.loads(ln)["pair"]))
            except Exception:                                     # noqa: BLE001
                pass
    pairs = [tuple(p) for p in pr["pairs"]]
    if a.limit:
        pairs = pairs[:a.limit]
    t00 = time.time()
    with open(out, "a", encoding="utf-8") as fh:
        for (u, v) in pairs:
            if (u, v) in done:
                continue
            sp = K.sentinel()
            if sp:
                print("sentinel", sp, "-- stopping cleanly", flush=True)
                break
            bs = [H, obs[u], obs[v]]
            rec = dict(pair=[u, v], cell=a.cell, corner=a.corner, depth0=a.depth,
                       boxes=[K.bx_json(b) for b in bs], budget=11 - len(bs))
            rows = {}
            for nm, lines in LN.items():
                rows[nm] = row_scan(bs, lines)
            rec["rows"] = rows
            rec["row_min_rhs"] = min(r["rhs_f"] for r in rows.values())
            rec["row_kill"] = bool(rec["row_min_rhs"] < 0.0)
            if a.area:
                bj = [b.to_json() for b in bs]
                O, names, kinds, _ = G.obstacles_of(bj)
                Um, xs, ys, res = G.uncoverable(K.S0, O, bs, lam=1.0, pitch=a.pitch,
                                                ntilt=a.ntilt, want_extra=False)
                rec["area_U"] = res["area_U"]
                rec["B0"] = B0
                rec["area_kill"] = bool(res["area_U"] > B0)
            fh.write(json.dumps(rec) + "\n")
            fh.flush()
    print("geom done in %.1fs -> %s" % (time.time() - t00, out), flush=True)


# ===================================================================== stage: LP
def stage_lp(a):
    sys.path.insert(0, os.path.join(K.ATT, "A150-four-corner-product", "code"))
    sys.path.insert(0, os.path.join(K.ATT, "A143-corner-first-k0", "code"))
    import lp150 as LP                                            # noqa: E402
    # A150's `certify` writes into `lp150.BASE/certs`; redirect it into THIS attempt so that
    # nothing is ever written under a prior attempt (the read-only rule).
    LP.BASE = K.BASE
    LP.OWN_PAUSE = os.path.join(K.BASE, "PAUSE")
    LP.GLOBAL_SENTINELS = [os.path.join(K.ROOT, "PAUSE"), os.path.join(K.ROOT, "STOP"),
                           os.path.join(K.BASE, "STOP")]
    cov = json.load(open(cover_path(a.cell, a.depth), encoding="utf-8"))
    pr = json.load(open(pairs_path(a.cell, a.depth, a.corner), encoding="utf-8"))
    H = Box(*cov["boxes"][0])
    obs = [Box(*b) for b in cov["covers"][a.corner]["open"]]
    pairs = [tuple(p) for p in pr["pairs"]]
    mixed = [tuple(m) for m in pr.get("mixed_cases", [])]
    canary = []
    for cpv in pr.get("canary_pairs", []):
        canary += [tuple(p) for p in cpv["alive"]]
    rng = random.Random(a.seed)
    pool = {"pair": pairs, "mixed": mixed, "both": pairs + mixed}[a.family]
    pick = list(dict.fromkeys(canary + rng.sample(pool, min(a.sample, len(pool)))))
    if a.only:
        pick = [tuple(int(v) for v in s.split("-")) for s in a.only.split(",")]
    out = os.path.join(RES, "lp3_%s_%s.jsonl" % (tag(a.cell, a.depth), a.corner))
    done = set()
    if os.path.exists(out):
        for ln in open(out, encoding="utf-8"):
            try:
                done.add(tuple(json.loads(ln)["pair"]))
            except Exception:                                     # noqa: BLE001
                pass
    warm = LP.load_warm()
    t00 = time.time()
    with open(out, "a", encoding="utf-8") as fh:
        for case in pick:
            if tuple(case) in done:
                continue
            sp = K.sentinel()
            if sp:
                print("sentinel", sp, "-- stopping cleanly", flush=True)
                break
            if a.deadline and time.time() - t00 > a.deadline:
                print("deadline reached; stopping cleanly", flush=True)
                break
            bs = [H] + [obs[i] for i in case]
            nm = "%s_%s_%s" % (a.cell, a.corner, "-".join(str(i) for i in case))
            rec, _ = LP.solve_one(nm, bs, 11 - len(bs), a.cap, warm, do_cert=bool(a.cert),
                                  cert_time=a.cert_time)
            rec["pair"] = list(case)
            rec["n_boxes"] = len(bs)
            rec["cell"] = a.cell
            rec["corner"] = a.corner
            rec["is_canary"] = bool(tuple(case) in set(canary))
            fh.write(json.dumps(rec) + "\n")
            fh.flush()
            print("%-28s tau=%s eta=%s conv=%s kill=%s cert=%s %ss%s" % (
                nm, rec.get("tau"), rec.get("eta"), rec.get("converged"),
                rec.get("kills_converged"), rec.get("certified"), rec.get("wall_s"),
                "  [CANARY]" if rec["is_canary"] else ""), flush=True)
    print("lp3 done -> %s" % out, flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=("cover", "pairs", "geom", "lp3"))
    ap.add_argument("--cell", default="l1_104")
    ap.add_argument("--depth", type=int, default=8)
    ap.add_argument("--corner", default="TR")
    ap.add_argument("--max_open", type=int, default=6000)
    ap.add_argument("--nlines", type=int, default=24)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--area", type=int, default=1)
    ap.add_argument("--pitch", type=float, default=0.02)
    ap.add_argument("--ntilt", type=int, default=30)
    ap.add_argument("--sample", type=int, default=24)
    ap.add_argument("--seed", type=int, default=165)
    ap.add_argument("--cap", type=float, default=150.0)
    ap.add_argument("--cert", type=int, default=1)
    ap.add_argument("--cert_time", type=float, default=90.0)
    ap.add_argument("--deadline", type=float, default=0.0)
    ap.add_argument("--only", default=None)
    ap.add_argument("--family", default="pair", choices=("pair", "mixed", "both"))
    a = ap.parse_args()
    {"cover": stage_cover, "pairs": stage_pairs, "geom": stage_geom, "lp3": stage_lp}[a.stage](a)


if __name__ == "__main__":
    main()
