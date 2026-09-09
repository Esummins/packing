"""A166 T4 -- the PRICE: the cheap half of A166's geometry run over the WHOLE remaining open k0_00
pool, so the cost of the sub-tree is projected from data rather than from the eleven alone.

For every cell A115 left open (A140 `cells140.open_pool`, 166 records) minus the 47 that A141's `K'`
lane leaf killed (`polycore_lane_kills.jsonl`, `cls = k0_00`) -- **119 remaining open k0_00 cells** --
we compute the two quantities that decide A166's verdict, both cheap:

    d          = |z_H - p_TR|, the nearest-corner distance (the metric of notes/method.md sec 1);
    can_meet   = A161 `box_misses_cell_exact(B_H, B_TR^w)` negated: can H itself meet the widened
                 corner box?  `can_meet = False` is what makes the budget-8 cover COMPLETE, so that
                 an empty pair cover is an outright (C) leaf.

and, for a sample, the full cell stage (the 216 cover-cell verdicts and the surviving pair count),
which is the number the LP price is proportional to.

    python code/price166.py --pad wmax --sample 24
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
for _p in (os.path.join(ATT, "A140-k0-residue-gallery", "code"), HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import geo166 as G                                              # noqa: E402
import cells166 as C                                            # noqa: E402
import cells140 as C140                                         # noqa: E402  READ-ONLY (A140)
from caselp import Box                                          # noqa: E402  READ-ONLY (A57)

RES = os.path.join(BASE, "results")
PADS = {"w0": 0.0, "wmax": C.W_MAX}
A141 = os.path.join(ATT, "A141-polycore-lane", "results", "polycore_lane_kills.jsonl")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pad", default="wmax", choices=sorted(PADS))
    ap.add_argument("--sample", type=int, default=0,
                    help="also run the full 216-cell stage on this many cells (uniformly spaced "
                         "in the d ordering)")
    ap.add_argument("--nids", default="", help="comma-separated nids to stage as well (always)")
    a = ap.parse_args()
    a_w = 1.0 + PADS[a.pad]
    killed = {json.loads(l)["nid"] for l in open(A141, encoding="utf-8")
              if l.strip() and json.loads(l).get("cls") == "k0_00"}
    pool = C140.open_pool()
    rows = []
    t0 = time.time()
    for (nid, verdict, lp, rec) in pool:
        if nid in killed:
            continue
        d = json.load(open(lp, encoding="utf-8"))
        boxes = d.get("hyp", {}).get("boxes") or []
        if not boxes:
            rows.append(dict(nid=nid, verdict=verdict, n_boxes=0, skip="no hypothesis box"))
            continue
        bs = [Box(**{k: b[k] for k in ("x0", "x1", "y0", "y1", "th0", "th1")}) for b in boxes]
        # the nearest corner is decided by the box nearest ANY corner (the sub-tree hangs on the
        # conditioned square nearest a corner; with more than one box we take that one)
        best = None
        for i, b in enumerate(bs):
            c, dd = C.nearest_corner(b)
            if best is None or dd[c] < best[2]:
                best = (i, c, dd[c], dd)
        i, corner, dist, dd = best
        rect = C.corner_rect(corner, a_w)
        can, det = G.cell_can_meet(bs[i], rect)
        rows.append(dict(nid=nid, verdict=verdict, n_boxes=len(bs), which=i, corner=corner,
                         dist=round(dist, 6),
                         dists={k: round(v, 6) for k, v in dd.items()},
                         H_can_meet_corner=bool(can), budget=d.get("budget"),
                         tau=d.get("tau"), box=bs[i].to_json(),
                         all_corners_TR=bool(corner == "TR")))
    ok = [r for r in rows if "skip" not in r]
    print("remaining open k0_00 cells: %d (pool %d minus %d A141 lane kills); %d with a hypothesis "
          "box; %.0f s" % (len(rows), len(pool), len(killed), len(ok), time.time() - t0), flush=True)
    from collections import Counter
    print("nearest corner:", Counter(r["corner"] for r in ok).most_common())
    print("H can meet the widened corner box:", Counter(r["H_can_meet_corner"] for r in ok))
    print("n_boxes:", Counter(r["n_boxes"] for r in ok).most_common())
    ds = sorted(r["dist"] for r in ok)
    if ds:
        q = lambda f: ds[min(len(ds) - 1, int(f * len(ds)))]                      # noqa: E731
        print("d(z_H, corner): min %.4f  Q1 %.4f  med %.4f  Q3 %.4f  max %.4f"
              % (ds[0], q(.25), q(.5), q(.75), ds[-1]))
        for thr in (1.90, 2.00, 2.10, 2.20):
            print("   d < %.2f : %d of %d (%.0f %%)"
                  % (thr, sum(1 for x in ds if x < thr), len(ds),
                     100.0 * sum(1 for x in ds if x < thr) / len(ds)))
    out = dict(pad=a.pad, a_w=a_w, n_pool=len(pool), n_a141_killed=len(killed),
               n_remaining=len(rows), rows=rows)

    if a.sample or a.nids:
        want = set(x for x in a.nids.split(",") if x)
        srt = sorted(ok, key=lambda r: r["dist"])
        sel = []
        if a.sample:
            step = max(1, len(srt) // a.sample)
            sel = srt[::step][:a.sample]
        have = {r["nid"] for r in sel}
        sel += [r for r in srt if r["nid"] in want and r["nid"] not in have]
        cens = json.load(open(os.path.join(RES, "paircensus166_%s.json" % a.pad), encoding="utf-8"))
        alive = {(tuple(x), tuple(y)) for x, y in cens["alive_pairs"]}
        samp = []
        for r in sel:
            bH = Box(**r["box"])
            t1 = time.time()
            meta = dict(cell=r["nid"], level=None, family=None)
            try:
                res = _stage(meta, bH, a_w, alive, r["corner"])
            except Exception as e:                              # noqa: BLE001
                print("  %s FAILED %r" % (r["nid"], e), flush=True)
                continue
            res.update(nid=r["nid"], dist=r["dist"], H_can_meet_corner=r["H_can_meet_corner"],
                       secs=round(time.time() - t1, 1))
            samp.append(res)
            print("  %-26s d=%.4f can_meet=%-5s ALIVE cells %3d  survivors %4d  %.0f s"
                  % (r["nid"], r["dist"], r["H_can_meet_corner"], res["n_alive_cells"],
                     res["n_survivors"], res["secs"]), flush=True)
        out["sample"] = samp
        sv = sorted(s["n_survivors"] for s in samp)
        if sv:
            print("survivors over the sample: min %d med %d max %d, zero on %d of %d"
                  % (sv[0], sv[len(sv) // 2], sv[-1], sum(1 for x in sv if x == 0), len(sv)))
    p = os.path.join(RES, "price166_%s.json" % a.pad)
    json.dump(out, open(p, "w"), indent=0)
    print("wrote", p, flush=True)


def _stage(meta, bH, a_w, alive_pairs, corner):
    """the cell stage, reduced to the two counts the price needs (no per-cell file written)."""
    import cells155 as C155
    import polycore as PC
    rect = C.corner_rect(corner, a_w)
    KH = G.kprime(bH)
    cH = G.exact_core(bH)
    aH = G.axis_core_in(KH, float(cH.kx), float(cH.ky))
    surv, degen, dead = [], 0, 0
    boxes = {}
    for cl in C155.all_cells(a_w):
        if cl.empty:
            continue
        Gb = C.global_box(corner, cl)
        can, _d = G.cell_can_meet(Gb, rect)
        if not can:
            dead += 1
            continue
        inter = G.boxes_intersect(Gb, bH)
        if G.max_centre_dist(bH, Gb) < 1.0:
            degen += 1 if inter else 0
            dead += 0 if inter else 1
            continue
        if PC.poly_poly_depth(KH.P, G.kprime(Gb).P) > 0.0:
            degen += 1 if inter else 0
            dead += 0 if inter else 1
            continue
        cr = G.clip_against_core(Gb, float(cH.kx), float(cH.ky), aH)
        if cr.get("empty"):
            degen += 1 if inter else 0
            dead += 0 if inter else 1
            continue
        ur = cr.get("union_rect")
        Gc = G.rect_to_box(ur, Gb.th0, Gb.th1) if ur is not None else Gb
        can2, _d2 = G.cell_can_meet(Gc, rect)
        if not can2:
            dead += 1
            continue
        surv.append(cl.key)
        boxes[cl.key] = Gc
    n = 0
    for i, k1 in enumerate(surv):
        for k2 in surv[i:]:
            key = (k1, k2) if k1 <= k2 else (k2, k1)
            if key not in alive_pairs:
                continue
            b1, b2 = boxes[k1], boxes[k2]
            if G.max_centre_dist(b1, b2) < 1.0:
                continue
            import polycore as PC2
            if PC2.poly_poly_depth(G.kprime(b1).P, G.kprime(b2).P) > 0.0:
                continue
            n += 1
    return dict(n_alive_cells=len(surv), n_degenerate=degen, n_dead=dead, n_survivors=n)


if __name__ == "__main__":
    main()
