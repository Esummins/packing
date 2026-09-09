"""A166 T1 -- the geometric stages of the nearest-corner sub-tree, per cell and per pad.

    python code/subtree166.py --pad wmax           # the window pad (K0-WIDEN, w = 0.0255101)
    python code/subtree166.py --pad w0             # the exact unit corner box (s0-only)

Stage 0 (once per pad, shared by every cell because the local cover and the pair verdicts are
frame-independent -- each corner frame is a ROTATION of the BL frame and the tests are isometry
invariant): A143's pair chain (P2, P1, P1s) over ALL 216*217/2 = 23 436 unordered pairs of the
216-cell cover.  The transpose quotient of A143/A150 is NOT applied (see cells166's docstring).

Stage 1..n (per cell): the reach test, the H-vs-cell tests, the H clip, the pair chain on the
clipped boxes, the mutual clip, and the exact-core distinctness gate.  Writes one record per cell to
`results/subtree166_<pad>.jsonl` and the surviving pair cells to
`results/survivors166_<pad>_<cell>.json`.
"""
import argparse
import json
import math
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import geo166 as G                                          # noqa: E402
import cells166 as C                                        # noqa: E402
import polycore as PC                                       # noqa: E402  READ-ONLY (A132)
import cells155 as C155                                     # noqa: E402  READ-ONLY (A155)
from caselp import Box                                      # noqa: E402  READ-ONLY (A57)

RES = os.path.join(BASE, "results")
LOGD = os.path.join(BASE, "logs")
PADS = {"w0": 0.0, "wmax": C.W_MAX}


def log_open(tag):
    os.makedirs(LOGD, exist_ok=True)
    fh = open(os.path.join(LOGD, "subtree166_%s.log" % tag), "a", encoding="utf-8")

    def log(*a):
        s = " ".join(str(x) for x in a)
        print(s, flush=True)
        fh.write(s + "\n")
        fh.flush()
    return log


# ===================================================================== stage 0: the pair census
def pair_census(a_w, tag, log):
    """A143's (P2)/(P1)/(P1s) over every unordered pair of the LOCAL cover.  Cached."""
    p = os.path.join(RES, "paircensus166_%s.json" % tag)
    if os.path.exists(p):
        d = json.load(open(p, encoding="utf-8"))
        log("pair census %s: cached, %d alive of %d" % (tag, d["alive"], d["n_pairs"]))
        return {(tuple(a), tuple(b)) for a, b in d["alive_pairs"]}, d
    t0 = time.time()
    cells = C155.all_cells(a_w)
    live = [c for c in cells if not c.empty]
    byk = {c.key: c for c in live}
    keys = sorted(byk)
    K = {k: PC.build(byk[k].box, max_v=G.MAXV) for k in keys}
    KS = {}
    for k in keys:
        subs = []
        for (a, b, cl) in C155.subbin_clip(*byk[k].raw, a_w=a_w, nsub=G.NSUB_PAIR):
            try:
                subs.append(PC.build(Box(cl[0], cl[1], cl[2], cl[3], a, b), max_v=G.MAXV))
            except Exception:                               # noqa: BLE001
                subs.append(None)
        KS[k] = subs
    log("pair census %s: %d live cells, cores in %.0f s" % (tag, len(keys), time.time() - t0))
    stats = dict(P2=0, P1=0, P1s=0, alive=0, n_pairs=0)
    alive = set()
    for i, k1 in enumerate(keys):
        for k2 in keys[i:]:
            stats["n_pairs"] += 1
            if G.max_centre_dist(byk[k1].box, byk[k2].box) < 1.0:
                stats["P2"] += 1
                continue
            if PC.poly_poly_depth(K[k1].P, K[k2].P) > 0.0:
                stats["P1"] += 1
                continue
            ok = False
            for p1 in KS[k1]:
                for p2 in KS[k2]:
                    if p1 is None or p2 is None or PC.poly_poly_depth(p1.P, p2.P) <= 0.0:
                        ok = True
                        break
                if ok:
                    break
            if not ok:
                stats["P1s"] += 1
                continue
            stats["alive"] += 1
            alive.add((k1, k2))
    d = dict(tag=tag, a_w=a_w, n_cells=len(cells), n_live=len(live), secs=round(time.time() - t0, 1),
             alive_pairs=[[list(a), list(b)] for a, b in sorted(alive)], **stats)
    json.dump(d, open(p, "w"), indent=0)
    log("pair census %s: %s  %.0f s" % (tag, json.dumps({k: stats[k] for k in
        ("n_pairs", "P2", "P1", "P1s", "alive")}), time.time() - t0))
    return alive, d


# ===================================================================== stage 1: per cell
def _q(v, f):
    v = sorted(v)
    return round(v[min(len(v) - 1, int(f * len(v)))], 6) if v else None


def _kept_summary(cl):
    """kept fraction of each cover box under the K'(H) clip: n, min, Q1, median, max, and how many
    boxes the clip emptied."""
    kv = [c["kept_union"] for c in cl if c.get("kept_union") is not None]
    return dict(n=len(kv), min=_q(kv, 0.0), q1=_q(kv, 0.25), median=_q(kv, 0.5), max=_q(kv, 0.999),
                n_emptied=sum(1 for c in cl if c.get("empty")),
                n_lost_subbins=sum(1 for c in cl if (c.get("n_empty") or 0) > 0))


def _kept_summary_mut(kf):
    """kept fraction of each PAIR box under the mutual clip, over both members of every pair."""
    kv = [x for r in kf for x in r["kept_union"] if x is not None]
    return dict(n=len(kv), min=_q(kv, 0.0), q1=_q(kv, 0.25), median=_q(kv, 0.5), max=_q(kv, 0.999),
                n_below_1=sum(1 for x in kv if x < 0.999999),
                n_lost_subbins=sum(1 for r in kf for x in r["n_empty_subbins"] if (x or 0) > 0))


def cell_stages(meta, bH, a_w, tag, alive_pairs, log, nsub_clip=1, mutual=True):
    t0 = time.time()
    name = meta["cell"]
    corner, dists = C.nearest_corner(bH)
    rect = C.corner_rect(corner, a_w)
    KH = G.kprime(bH)
    cH = G.exact_core(bH)
    kxH, kyH = float(cH.kx), float(cH.ky)
    aH_axis = G.axis_core_in(KH, kxH, kyH)
    log("%-12s corner %s d=%.5f  K'(H) area %.6f  inscribed axis core a=%.6f  K(H) a_exact=%.6f"
        % (name, corner, dists[corner], KH.area(), aH_axis, float(cH.a)))

    cover = C155.all_cells(a_w)
    live = [c for c in cover if not c.empty]
    per = {}
    st = dict(n_cover=len(cover), n_live=len(live), dead_R=0, dead_H2=0, dead_H1=0,
              dead_clip=0, degenerate=0, survive=0)
    for cl in live:
        k = cl.key
        Gb = C.global_box(corner, cl)
        rec = dict(key=list(k), gbox=Gb.to_json())
        # --- R: A161 exact reach
        can, det = G.cell_can_meet(Gb, rect)
        if not can:
            rec.update(verdict="DEAD_R", detail=det)
            st["dead_R"] += 1
            per[k] = rec
            continue
        inter = G.boxes_intersect(Gb, bH)
        rec["meets_Hbox"] = bool(inter)
        # --- H2: centre distance H vs the cell
        md = G.max_centre_dist(bH, Gb)
        rec["maxdist_H"] = md
        if md < 1.0:
            if not inter:
                rec.update(verdict="DEAD_H2", maxdist_H=md)
                st["dead_H2"] += 1
                per[k] = rec
                continue
            rec.update(verdict="DEGENERATE_H2")
            st["degenerate"] += 1
            per[k] = rec
            continue
        # --- H1: K'(H) vs K'(cell)
        KA = G.kprime(Gb)
        d1 = PC.poly_poly_depth(KH.P, KA.P)
        rec["kprime_depth_H"] = float(d1)
        if d1 > 0.0:
            if not inter:
                rec.update(verdict="DEAD_H1")
                st["dead_H1"] += 1
                per[k] = rec
                continue
            rec.update(verdict="DEGENERATE_H1")
            st["degenerate"] += 1
            per[k] = rec
            continue
        # --- CLIP against K'(H) (A131 + A158's rule)
        cl_res = G.clip_against_core(Gb, kxH, kyH, aH_axis, nsub=nsub_clip)
        rec["clip"] = dict(kept_union=cl_res.get("kept_union"), kept_vol=cl_res.get("kept_vol"),
                           empty=bool(cl_res.get("empty")), refused=bool(cl_res.get("refused")),
                           n_empty=cl_res.get("n_empty"))
        if cl_res.get("empty"):
            if not inter:
                rec.update(verdict="DEAD_CLIP")
                st["dead_clip"] += 1
                per[k] = rec
                continue
            rec.update(verdict="DEGENERATE_CLIP")
            st["degenerate"] += 1
            per[k] = rec
            continue
        ur = cl_res.get("union_rect")
        Gc = (G.rect_to_box(ur, Gb.th0, Gb.th1) if ur is not None else Gb)
        # the clip can only shrink; re-run the reach test on the clipped box (strictly stronger)
        can2, det2 = G.cell_can_meet(Gc, rect)
        if not can2:
            rec.update(verdict="DEAD_R2", detail=det2, cbox=Gc.to_json())
            st["dead_R"] += 1
            per[k] = rec
            continue
        rec.update(verdict="ALIVE", cbox=Gc.to_json(),
                   kprime_area=float(G.kprime(Gc).area()))
        st["survive"] += 1
        per[k] = rec

    surv = sorted(k for k, r in per.items() if r["verdict"] == "ALIVE")

    def _subcores(b):
        subs = []
        n = G.NSUB_PAIR
        for i in range(n):
            a0 = b.th0 + (b.th1 - b.th0) * i / n
            a1 = b.th0 + (b.th1 - b.th0) * (i + 1) / n
            try:
                subs.append(PC.build(Box(b.x0, b.x1, b.y0, b.y1, a0, a1), max_v=G.MAXV))
            except Exception:                               # noqa: BLE001
                subs.append(None)
        return subs

    KC = {k: G.kprime(Box(**per[k]["cbox"])) for k in surv}
    KCS = {k: _subcores(Box(**per[k]["cbox"])) for k in surv}

    # --- the pair stage on the CLIPPED boxes.  ORDER (the coordinator's reinforcement, 2026-09-08):
    # the MUTUAL clip (A158, per tilt sub-bin) runs FIRST -- before the pair leaf, before any
    # chord/lane test, before the figure and before the LP -- because every later test is stronger on
    # the smaller boxes.  A box all of whose poses meet the other's core is EMPTY and the case dies.
    pst = dict(raw=0, raw_alive_a143=0, both_alive=0, MUT=0, P2=0, P1=0, P1s=0, DIST=0, alive=0)
    survivors = []
    kept_frac = []
    for i, k1 in enumerate(surv):
        for k2 in surv[i:]:
            pst["both_alive"] += 1
            key = (k1, k2) if k1 <= k2 else (k2, k1)
            if key not in alive_pairs:
                continue                      # already dead in A143's own (unclipped) census
            pst["raw_alive_a143"] += 1
            b1, b2 = Box(**per[k1]["cbox"]), Box(**per[k2]["cbox"])
            K1, K2 = KC[k1], KC[k2]
            KS1, KS2 = KCS[k1], KCS[k2]
            kf = None
            if mutual:
                a1 = G.axis_core_in(K1, 0.5 * (b1.x0 + b1.x1), 0.5 * (b1.y0 + b1.y1))
                a2 = G.axis_core_in(K2, 0.5 * (b2.x0 + b2.x1), 0.5 * (b2.y0 + b2.y1))
                r1 = G.clip_against_core(b1, 0.5 * (b2.x0 + b2.x1), 0.5 * (b2.y0 + b2.y1), a2,
                                         nsub=nsub_clip)
                r2 = G.clip_against_core(b2, 0.5 * (b1.x0 + b1.x1), 0.5 * (b1.y0 + b1.y1), a1,
                                         nsub=nsub_clip)
                if r1.get("empty") or r2.get("empty"):
                    pst["MUT"] += 1
                    continue
                u1, u2 = r1.get("union_rect"), r2.get("union_rect")
                if u1 is not None:
                    b1 = G.rect_to_box(u1, b1.th0, b1.th1)
                if u2 is not None:
                    b2 = G.rect_to_box(u2, b2.th0, b2.th1)
                c1, _d1 = G.cell_can_meet(b1, rect)
                c2, _d2 = G.cell_can_meet(b2, rect)
                if not (c1 and c2):
                    pst["MUT"] += 1
                    continue
                kf = dict(a=list(k1), b=list(k2),
                          kept_union=[r1.get("kept_union"), r2.get("kept_union")],
                          kept_vol=[r1.get("kept_vol"), r2.get("kept_vol")],
                          n_empty_subbins=[r1.get("n_empty"), r2.get("n_empty")])
                # every later test uses the MUTUALLY CLIPPED boxes and their rebuilt K'
                K1, K2 = G.kprime(b1), G.kprime(b2)
                KS1, KS2 = _subcores(b1), _subcores(b2)
            if G.max_centre_dist(b1, b2) < 1.0:
                pst["P2"] += 1
                continue
            if PC.poly_poly_depth(K1.P, K2.P) > 0.0:
                pst["P1"] += 1
                continue
            ok = False
            for p1 in KS1:
                for p2 in KS2:
                    if p1 is None or p2 is None or PC.poly_poly_depth(p1.P, p2.P) <= 0.0:
                        ok = True
                        break
                if ok:
                    break
            if not ok:
                pst["P1s"] += 1
                continue
            if kf is not None:
                kept_frac.append(kf)
            # --- DIST: the three exact cores pairwise interior-disjoint (budget 8)
            try:
                e1 = G.exact_core(b1)
                e2 = G.exact_core(b2)
            except Exception as ex:                          # noqa: BLE001
                pst["DIST"] += 1
                continue
            okd = True
            gaps = []
            for (u, v) in ((cH, e1), (cH, e2), (e1, e2)):
                o, g = G.cores_disjoint_exact(u, v)
                gaps.append(float(g))
                okd = okd and o
            if not okd:
                pst["DIST"] += 1
                continue
            pst["alive"] += 1
            survivors.append(dict(a=list(k1), b=list(k2),
                                  boxes=[bH.to_json(), b1.to_json(), b2.to_json()],
                                  core_gaps=[round(x, 9) for x in gaps],
                                  a_exact=[float(cH.a), float(e1.a), float(e2.a)]))
    pst["raw"] = len(live) * (len(live) + 1) // 2
    out = dict(cell=name, level=meta["level"], family=meta["family"], pad=tag, a_w=a_w,
               corner=corner, dist_to_corner=dists[corner],
               dists={k: round(v, 6) for k, v in dists.items()},
               Hbox=bH.to_json(), kprime_H_area=float(KH.area()), a_axis_H=aH_axis,
               a_exact_H=float(cH.a), cell_stats=st, pair_stats=pst,
               n_survivors=len(survivors), nsub_clip=nsub_clip, mutual_first=bool(mutual),
               kept_H_clip=_kept_summary([per[k].get("clip") for k in per
                                          if isinstance(per[k].get("clip"), dict)]),
               kept_mutual=_kept_summary_mut(kept_frac),
               secs=round(time.time() - t0, 1))
    json.dump(dict(out, survivors=survivors, kept_frac=kept_frac,
                   per_cell={"%d%d%d" % k: per[k] for k in per}),
              open(os.path.join(RES, "survivors166_%s_%s.json" % (tag, name)), "w"), indent=0)
    log("%-12s cells %s | pairs %s | survivors %d | %.0f s"
        % (name, json.dumps(st), json.dumps(pst), len(survivors), time.time() - t0))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pad", default="wmax", choices=sorted(PADS))
    ap.add_argument("--cells", default="")
    ap.add_argument("--nsub_clip", type=int, default=1)
    ap.add_argument("--no_mutual", action="store_true")
    a = ap.parse_args()
    tag = a.pad
    a_w = 1.0 + PADS[tag]
    log = log_open(tag)
    log("=== A166 subtree166 pad=%s a_w=%.9f  %s" % (tag, a_w, time.strftime("%Y-%m-%d %H:%M:%S")))
    alive, cens = pair_census(a_w, tag, log)
    want = set(a.cells.split(",")) if a.cells else None
    out = os.path.join(RES, "subtree166_%s.jsonl" % tag)
    done = set()
    if os.path.exists(out):
        for ln in open(out, encoding="utf-8"):
            try:
                done.add(json.loads(ln)["cell"])
            except Exception:                               # noqa: BLE001
                pass
    for (meta, bH, _rec) in C.load_eleven():
        if want and meta["cell"] not in want:
            continue
        if meta["cell"] in done:
            log("%s already done" % meta["cell"])
            continue
        r = cell_stages(meta, bH, a_w, tag, alive, log, nsub_clip=a.nsub_clip,
                        mutual=not a.no_mutual)
        r["census"] = {k: cens[k] for k in ("n_pairs", "P2", "P1", "P1s", "alive")}
        with open(out, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(r) + "\n")
    log("subtree166 pad %s done" % tag)


if __name__ == "__main__":
    main()
