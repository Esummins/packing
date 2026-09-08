"""A158b -- the MUTUAL CLIP of the two conditioned boxes of the YES child, then the LP again.

Inside the YES child the hypothesis carries TWO conditioned squares: the node's `H` and the square
in the slot box `S`.  They are distinct squares of the same packing, so each must be
interior-disjoint from the OTHER's guaranteed core.  That is exactly A131's PIN-CLIP with the other
box's core in the pin's role:

    D(t0, t1) := { d : Q(centre + d, theta) meets the other core's interior at EVERY theta in the
                       sub-bin }                                      (convex, A131's octagon)

    a centre in D admits no tilt in the sub-bin, so it carries no packing and is DISCARDED.

`pinclip.Oct(t0, t1, a)` builds that octagon for an AXIS-ALIGNED core of half-side `a` centred at
the "slot".  A132's polygon core `K'(B)` is not axis-aligned, so the core handed to A131 here is
the largest AXIS-ALIGNED square inscribed in `K'(B)` about `B`'s own midpoint — strictly smaller
than `K'(B)`, hence the clip removes LESS than the truth: sound, and it lets A131's certified
machinery be imported unchanged rather than re-derived.

Both clips are applied, then `K'` is rebuilt on each clipped box (A132), then the YES-child LP is
re-solved with the clipped boxes and A135 exact cores.  Reported per cell:

  * kept fraction of each box (`kept_union` at nsub = 1, the single-child form the LP consumes, and
    `kept_vol` at nsub = 4, the per-sub-bin figure);
  * `K'` area before and after, for both boxes;
  * the YES-child LP's tau/eta with and without the clip.

    python clip158.py --jobs ../results/y0076_job.jsonl --r 0.10 --tt 10
"""
import argparse
import json
import math
import os
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
A131 = os.path.join(ROOT, "attempts", "A131-pin-clip", "code")
A135 = os.path.join(ROOT, "attempts", "A135-polycore-verifier", "code")
for _p in (HERE, A131, A135):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import slotlib158 as SL                                            # noqa: E402
import yeslp158 as YL                                              # noqa: E402
import pinclip as PCLIP                                            # noqa: E402  READ-ONLY (A131)
import emit135 as EM                                               # noqa: E402  READ-ONLY (A135)
import exactcore as EC                                             # noqa: E402  READ-ONLY (A135)
from caselp import Box, solve_node                                 # noqa: E402  READ-ONLY
import numpy as np                                                 # noqa: E402

S0 = SL.S0
PC = SL.PC


def polycore(box):
    """A132 K'(box) with its vertex array and area (no container tightening)."""
    cs = SL.P.build_cond([box], tighten=False)[0]
    return cs.pc


def inside_poly(P, x, y, eps=0.0):
    """point strictly inside the convex polygon P (CCW), by the edge cross products A132 uses."""
    E = np.roll(P, -1, axis=0) - P
    return bool(np.all(E[:, 0] * (y - P[:, 1]) - E[:, 1] * (x - P[:, 0]) >= eps))


def axis_core_in(pc, kx, ky, hi=0.5, iters=40):
    """largest a with the axis-aligned square [kx +- a] x [ky +- a] inside K'; 0 if the midpoint
    itself is outside.  Monotone in a, so a plain bisection is exact to 2^-iters."""
    P = pc.P
    if not inside_poly(P, kx, ky):
        return 0.0
    lo, hi_ = 0.0, hi
    for _ in range(iters):
        mid = 0.5 * (lo + hi_)
        ok = all(inside_poly(P, kx + sx * mid, ky + sy * mid)
                 for sx in (-1.0, 1.0) for sy in (-1.0, 1.0))
        if ok:
            lo = mid
        else:
            hi_ = mid
    return lo


def clip_box(box, core_centre, a_core, nsub, traces=None):
    """A131 clip_node with ONE 'pin' = the other box's inscribed axis core."""
    return PCLIP.clip_node(box, [core_centre], nsub=nsub, s_rat=PCLIP.S_RAT,
                           a_pin=Fr(str(a_core)), traces=traces)


def rect_to_box(rect, th0, th1):
    return Box(float(rect[0]), float(rect[1]), float(rect[2]), float(rect[3]), th0, th1)


def frame_conds(rec, slot, Hc, Sc):
    """The clipped boxes pulled into the cell's CORNER FRAME, with the class pins, exactly as
    A141/A157 do (`lane.cframe_boxes` on a record whose `cond` list is the two clipped boxes).

    Returns (conds, [H index], cell rect, (corner, i, j)).  Only the H index is a MEETER: the
    S-square is the +1 of `1 + LANE + M`, not part of `M`."""
    c, i, j = SL.LANE.L.parse_cell(slot)
    rec2 = dict(rec)
    rec2["cond"] = [Hc.to_json(), Sc.to_json()]
    pin_b, cond_b = SL.LANE.cframe_boxes(rec2, c, i, j)
    pins = SL.P.build_cond([Box(b.x0, b.x1, b.y0, b.y1, b.th0, b.th1) for b in pin_b],
                           tighten=False)
    cond = SL.P.build_cond([Box(b.x0, b.x1, b.y0, b.y1, b.th0, b.th1) for b in cond_b],
                           tighten=False)
    for k, cs in enumerate(cond):
        cs.idx = len(pins) + k
    return pins + cond, [cond[0].idx], (float(i), float(i) + 1.0,
                                        float(j), float(j) + 1.0), (c, i, j)


def h_sample_line(conds, hidx, cell, rng, n):
    """The PI's sample line: >= n poses of the CLIPPED H box that meet int C and clear every other
    core (K'(S_clipped) included).  `free = 0` is the sampled corroboration of `M = 0`."""
    cs = next(x for x in conds if x.idx == hidx)
    b = cs.box
    C = np.column_stack([rng.uniform(b.x0, b.x1, n), rng.uniform(b.y0, b.y1, n)])
    T = np.radians(rng.uniform(b.th0, b.th1, n))
    h = 0.5 * (np.abs(np.cos(T)) + np.abs(np.sin(T)))
    adm = ((C[:, 0] >= h) & (C[:, 0] <= S0 - h) & (C[:, 1] >= h) & (C[:, 1] <= S0 - h))
    meet = adm & SL.P.rect_square_meets(cell, C, T)
    ok = meet.copy()
    for o in conds:
        if o.idx == hidx or not ok.any():
            continue
        ok &= (PC.poly_square_depth(o.pc.P, C, T) <= 0.0)
    return dict(drawn=n, admissible=int(adm.sum()), meeting_cell=int(meet.sum()),
                free_of_other_cores=int(ok.sum()))


def lp(node, boxes, budget, cap, log):
    hyp = EM.ExactHyp(boxes, [], scope="exall")
    ok, pair, gap = EC.cores_pairwise_disjoint(hyp.cores)
    if not ok:
        return dict(error="cores not pairwise disjoint (pair %s gap %s)" % (pair, gap))
    ap_, cp_ = YL.free_mb()
    if ap_ < 3072 or cp_ < 6144:
        return dict(error="memory gate %.0f/%.0f" % (ap_, cp_))
    warm = dict(atoms=[(x, y) for (x, y, w) in node["atoms_all"]],
                rows=[tuple(t) for t in node["rows_all"]])
    t0 = time.time()
    res = solve_node(S0, hyp, budget, sym_kind="C1", warm=warm, time_limit=cap, max_iter=900,
                     out=None, log=lambda *x: None, prune=0, prune_cols=3,
                     col_stop_iter=10 ** 6, col_stop_cov=1.002, max_cols_add=400,
                     max_rows_add=2000, fine_slack=99.0, alternate=True, fine=True)
    return dict(res=res, hyp=hyp, secs=round(time.time() - t0, 1),
                core_gap=float(gap) if gap is not None else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", default=os.path.join(BASE, "results", "y0076_job.jsonl"))
    ap.add_argument("--recs", default=os.path.join(BASE, "results", "recs158.json"))
    ap.add_argument("--r", type=float, default=0.10)
    ap.add_argument("--tt", type=float, default=10.0)
    ap.add_argument("--nsub", type=int, default=4)
    ap.add_argument("--nscreen", type=int, default=400000)
    ap.add_argument("--nline", type=int, default=20000, help="poses of the clipped H box for the "
                                                             "sample line (the PI asked >= 1e4)")
    ap.add_argument("--cap", type=float, default=240.0)
    ap.add_argument("--out", default=os.path.join(BASE, "results", "clip158.jsonl"))
    ap.add_argument("--budget_s", type=float, default=4200.0)
    a = ap.parse_args()

    def log(*x):
        print(*x, flush=True)

    recs = json.load(open(a.recs, encoding="utf-8"))
    jobs = [json.loads(l) for l in open(a.jobs, encoding="utf-8") if l.strip()]
    fh = open(a.out, "a", encoding="utf-8")
    t_start = time.time()
    for j in jobs:
        rec = recs[j["nid"]]
        node = json.load(open(os.path.join(ROOT, rec["path"]), encoding="utf-8"))
        pins = [Box.from_json(b) for b in node["hyp"]["boxes"][:rec["n_pin"]]]
        conds = [Box.from_json(b) for b in node["hyp"]["boxes"][rec["n_pin"]:]]
        if len(conds) != 1:
            log("%s: %d conditioned boxes, the mutual clip is written for exactly one"
                % (j["nid"], len(conds)))
            continue
        H = conds[0]
        budget = node["budget"] - 1
        pieces = YL.s_boxes_world(rec, j["slot"], a.r, a.tt)
        log("%s %s (%s %s L%s) budget %s -> YES budget %s"
            % (j["nid"], j["slot"], rec["src"], rec["cls"], rec["level"], node["budget"], budget))
        for piece, Sb in enumerate(pieces):
            if time.time() - t_start > a.budget_s:
                log("process budget reached"); fh.close(); return
            pcH0, pcS0 = polycore(H), polycore(Sb)
            aH = axis_core_in(pcH0, 0.5 * (H.x0 + H.x1), 0.5 * (H.y0 + H.y1))
            aS = axis_core_in(pcS0, 0.5 * (Sb.x0 + Sb.x1), 0.5 * (Sb.y0 + Sb.y1))
            cH = (0.5 * (H.x0 + H.x1), 0.5 * (H.y0 + H.y1))
            cS = (0.5 * (Sb.x0 + Sb.x1), 0.5 * (Sb.y0 + Sb.y1))
            log("   piece %d  S=%s" % (piece, Sb))
            log("      K'(H) area %.6f verts %d ; inscribed axis core a=%.6f at (%.6f, %.6f)"
                % (pcH0.area(), len(pcH0.verts), aH, cH[0], cH[1]))
            log("      K'(S) area %.6f verts %d ; inscribed axis core a=%.6f at (%.6f, %.6f)"
                % (pcS0.area(), len(pcS0.verts), aS, cS[0], cS[1]))
            row = dict(nid=j["nid"], slot=j["slot"], src=rec["src"], cls=rec["cls"],
                       level=rec["level"], piece=piece, r=a.r, tt=a.tt, nsub=a.nsub,
                       H_box=H.to_json(), S_box=Sb.to_json(), budget=budget,
                       tau0=node["tau"], node_budget=node["budget"],
                       aH=aH, aS=aS,
                       KH_area_before=float(pcH0.area()), KS_area_before=float(pcS0.area()))
            # --- the two clips
            trH, trS = [], []
            clipH = clip_box(H, cS, aS, 1, trH) if aS > 0 else None
            clipS = clip_box(Sb, cH, aH, 1, trS) if aH > 0 else None
            row["clip_traces"] = dict(H=trH, S=trS)
            clipH_n = clip_box(H, cS, aS, a.nsub) if aS > 0 else None
            clipS_n = clip_box(Sb, cH, aH, a.nsub) if aH > 0 else None
            for tag, cl, cln in (("H", clipH, clipH_n), ("S", clipS, clipS_n)):
                row["clip_" + tag] = None if cl is None else dict(
                    kept_union=cl["kept_union"], kept_vol=cl["kept_vol"], empty=cl["empty"],
                    refused=cl["refused"], reason=cl["reason"],
                    union_rect=(None if cl["union_rect"] is None
                                else [str(v) for v in cl["union_rect"]]))
                row["clip_%s_nsub%d" % (tag, a.nsub)] = None if cln is None else dict(
                    kept_union=cln["kept_union"], kept_vol=cln["kept_vol"],
                    n_empty=cln["n_empty"], empty=cln["empty"])
            log("      clip H: kept_union %.6f (nsub=%d kept_vol %.6f, %s empty bins) ; "
                "clip S: kept_union %.6f (nsub=%d kept_vol %.6f, %s empty bins)"
                % ((clipH["kept_union"] if clipH else 1.0), a.nsub,
                   (clipH_n["kept_vol"] if clipH_n else 1.0),
                   (clipH_n["n_empty"] if clipH_n else 0),
                   (clipS["kept_union"] if clipS else 1.0), a.nsub,
                   (clipS_n["kept_vol"] if clipS_n else 1.0),
                   (clipS_n["n_empty"] if clipS_n else 0)))
            # --- rebuild K' on the clipped boxes
            Hc = H if (clipH is None or clipH["refused"] or clipH["union_rect"] is None) \
                else rect_to_box(clipH["union_rect"], H.th0, H.th1)
            Sc = Sb if (clipS is None or clipS["refused"] or clipS["union_rect"] is None) \
                else rect_to_box(clipS["union_rect"], Sb.th0, Sb.th1)
            if clipH is not None and clipH["empty"]:
                row["verdict"] = "H-BOX EMPTY under the clip: the YES child is dead by geometry"
                log("      H box EMPTIED by the clip -- YES child dead by geometry")
                fh.write(json.dumps(row) + "\n"); fh.flush(); continue
            if clipS is not None and clipS["empty"]:
                row["verdict"] = "S-BOX EMPTY under the clip: no square can sit in S"
                log("      S box EMPTIED by the clip -- SomeIn(S) impossible")
                fh.write(json.dumps(row) + "\n"); fh.flush(); continue
            pcHc, pcSc = polycore(Hc), polycore(Sc)
            row.update(H_box_clipped=Hc.to_json(), S_box_clipped=Sc.to_json(),
                       KH_area_after=float(pcHc.area()), KS_area_after=float(pcSc.area()))
            log("      K'(H) area %.6f -> %.6f (x%.4f) ; K'(S) area %.6f -> %.6f (x%.4f)"
                % (pcH0.area(), pcHc.area(), pcHc.area() / max(pcH0.area(), 1e-18),
                   pcS0.area(), pcSc.area(), pcSc.area() / max(pcS0.area(), 1e-18)))

            # --- THE LANE TEST ON THE CLIPPED CORES, before any LP (the PI's order)
            rng = np.random.default_rng(1583 + piece)
            conds, meet, cell, _ = frame_conds(rec, j["slot"], Hc, Sc)
            sc = SL.screen_conditional(conds, cell, rng, a.nscreen)
            sm = SL.screen_cond_meet(conds, meet, cell, rng, max(2000, a.nscreen // 4))
            row["lane_screen"] = dict(lane_lb=sc["lane_lb"], free=sc.get("free"),
                                      meeting=sc.get("meeting"), M_lb=sm["M_lb"],
                                      clearance=sc.get("clearance"),
                                      free_pose=sc.get("free_pose"))
            log("      LANE screen on the CLIPPED cores: %d/%d meeting poses free "
                "(lane_lb %d), M_lb %d%s"
                % (sc.get("free", 0), sc.get("meeting", 0), sc["lane_lb"], sm["M_lb"],
                   ("  clearance %.4e" % sc["clearance"]) if sc.get("clearance") else ""))
            if sc["lane_lb"] == 0 and sm["M_lb"] == 0:
                lres = SL.P.lane_corner_generic(cell, conds, meeters=meet, rng=rng,
                                                sample=20000, max_open=8000, max_depth=34,
                                                lane_depth0=22, keep_cert=True,
                                                bound_when_dead=True)
                lane, M = lres.get("lane_ub"), lres.get("M")
                tot = None if (lane is None or M is None) else 1 + lane + M
                row["lane_cover"] = dict(lane_ub=lane, M=M, M_exact=lres.get("M_exact"),
                                         total_meeters=tot, a141_verdict=lres.get("verdict"),
                                         leaves=lres.get("cover_leaves"),
                                         open=lres.get("cover_open"),
                                         kill=bool(lane == 0 and M == 0))
                row["h_sample_line"] = h_sample_line(conds, meet[0], cell, rng, a.nline)
                log("      LANE cover: LANE_K'<=%s  M=%s  ->  1+LANE+M = %s  %s ; H sample line %s"
                    % (lane, M, tot, "KILL BY TELEPORT" if row["lane_cover"]["kill"] else "no kill",
                       json.dumps(row["h_sample_line"])))
                if row["lane_cover"]["kill"]:
                    try:
                        import emit141 as EM141
                        d = EM141.cert_dict("polycore_slot_lane_clipped", j["nid"], j["slot"],
                                            conds, [x.box for x in conds], lres,
                                            extra=dict(
                                                cell_kind="usable_slot", cls=rec["cls"],
                                                attempt="A158b",
                                                extension=SL.CP.CLASSES[rec["cls"]]["usable"][j["slot"]],
                                                s_box=Sb.to_json(), s_box_clipped=Sc.to_json(),
                                                h_box=H.to_json(), h_box_clipped=Hc.to_json(),
                                                s_piece=piece, s_r=a.r, s_tt=a.tt,
                                                clip_axis_core_H=dict(a=aH, centre=list(cH)),
                                                clip_axis_core_S=dict(a=aS, centre=list(cS)),
                                                clip_kept=dict(H=row.get("clip_H"),
                                                               S=row.get("clip_S")),
                                                clip_traces=row.get("clip_traces"),
                                                h_sample_line=row["h_sample_line"],
                                                kill_rule="YES child of the A158 slot split with "
                                                          "the MUTUAL CLIP: 1 + LANE_K'(C | S, "
                                                          "H_clipped) + M(C | S, H_clipped) <= 1"))
                        p = os.path.join(BASE, "certs", "yeslane_%s__%s__p%d.json"
                                         % (j["nid"], j["slot"].replace("(", "").replace(")", "")
                                            .replace(",", "_"), piece))
                        row["cert"] = os.path.relpath(p, ROOT)
                        row["sha256"] = EM141.write_cert(p, d)
                        log("      cert %s" % row["cert"])
                    except Exception as e:                          # noqa: BLE001
                        row["cert_error"] = repr(e)[:200]
                        log("      CERT ERROR %r" % (e,))
                    fh.write(json.dumps(row) + "\n"); fh.flush()
                    continue                                        # dead by teleport: no LP
            else:
                row["lane_cover"] = dict(skipped="refuted by the screen",
                                         lane_lb=sc["lane_lb"], M_lb=sm["M_lb"])
                log("      LANE >= 1 (or M >= 1) on the clipped cores -> falling back to the LP")

            # --- the LP fallback, unclipped then clipped
            for tag, bxs in (("unclipped", pins + [H, Sb]), ("clipped", pins + [Hc, Sc])):
                o = lp(node, bxs, budget, a.cap, log)
                if "res" not in o:
                    row["lp_" + tag] = dict(error=o["error"])
                    log("      LP %-9s ERROR %s" % (tag, o["error"]))
                    continue
                tau = o["res"].get("tau")
                row["lp_" + tag] = dict(tau=tau,
                                        eta=(None if tau is None else round(budget - tau, 12)),
                                        converged=o["res"].get("converged"),
                                        n_dual=len(o["res"].get("packing") or []),
                                        core_gap=o["core_gap"], secs=o["secs"],
                                        kill=bool(tau is not None and tau < budget - 1e-9))
                log("      LP %-9s tau %.12g  eta %.6g  conv=%s  (%.1f s)  %s"
                    % (tag, tau if tau is not None else float("nan"),
                       row["lp_" + tag]["eta"], row["lp_" + tag]["converged"], o["secs"],
                       "KILL" if row["lp_" + tag]["kill"] else "NO-KILL"))
            fh.write(json.dumps(row) + "\n")
            fh.flush()
    fh.close()


if __name__ == "__main__":
    main()
