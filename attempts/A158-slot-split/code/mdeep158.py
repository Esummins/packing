"""A158b -- escalate the M-EXCLUSION cover on the clipped cores.

`lanedeep158.py` closed the hard half on `k5_11_interior_Y1110 TR(0,0)`: with `S` clamped to the
admissible strip and `H` clipped against `K'(S)`, `LANE_K'(C | S, H_clipped) = 0` is CERTIFIED
(36 leaves, 0 open, 36 s).  What is left is `M(C | S, H_clipped) = 0`, i.e. A141's
`cond_can_meet` -- "cover `H_clipped`'s own box and discharge every sub-box by container /
misses the cell / shares a rational point with a DIFFERENT core".  It came back `excluded = False`
at `lane_corner_generic`'s default budget while the 100,000-pose screen realised NO meeting pose
clear of the other cores, so the failure is a COVER BUDGET, not a refutation.

This calls `polylane.cond_can_meet` directly on a ladder and reports leaves / open / reason / RSS,
so the cost of the missing half is measured.  `ok = True` is the exclusion, and then
`1 + LANE + M = 1` and the YES child is dead by teleport.

    python mdeep158.py --jobs ../results/deep_jobs.jsonl --ladder 40:5000,40:40000,44:200000
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import slotlib158 as SL                                            # noqa: E402
import yeslp158 as YL                                              # noqa: E402
import clip158 as CL                                               # noqa: E402
import lanedeep158 as LD                                           # noqa: E402
import emit141 as EM141                                            # noqa: E402  READ-ONLY (A141)
import numpy as np                                                 # noqa: E402
from caselp import Box                                             # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", default=os.path.join(BASE, "results", "deep_jobs.jsonl"))
    ap.add_argument("--recs", default=os.path.join(BASE, "results", "recs158.json"))
    ap.add_argument("--r", type=float, default=0.10)
    ap.add_argument("--tt", type=float, default=10.0)
    ap.add_argument("--ladder", default="40:5000,40:40000,44:200000")
    ap.add_argument("--maxleaves", type=int, default=600000)
    ap.add_argument("--lane_depth0", type=int, default=22)
    ap.add_argument("--lane_open", type=int, default=8000)
    ap.add_argument("--wall", type=float, default=900.0)
    ap.add_argument("--nline", type=int, default=100000)
    ap.add_argument("--out", default=os.path.join(BASE, "results", "mdeep158.jsonl"))
    ap.add_argument("--certs", default=os.path.join(BASE, "certs"))
    ap.add_argument("--budget_s", type=float, default=4200.0)
    a = ap.parse_args()

    def log(*x):
        print(*x, flush=True)

    ladder = [tuple(int(v) for v in s.split(":")) for s in a.ladder.split(",")]
    recs = json.load(open(a.recs, encoding="utf-8"))
    jobs = [json.loads(l) for l in open(a.jobs, encoding="utf-8") if l.strip()]
    fh = open(a.out, "a", encoding="utf-8")
    t_start = time.time()
    for j in jobs:
        rec = recs[j["nid"]]
        node = json.load(open(os.path.join(ROOT, rec["path"]), encoding="utf-8"))
        cj = node["hyp"]["boxes"][rec["n_pin"]:]
        if len(cj) != 1:
            continue
        H = Box.from_json(cj[0])
        for piece, Sb in enumerate(YL.s_boxes_world(rec, j["slot"], a.r, a.tt)):
            if time.time() - t_start > a.budget_s:
                log("process budget reached"); fh.close(); return
            pcH0, pcS0 = CL.polycore(H), CL.polycore(Sb)
            aS = CL.axis_core_in(pcS0, 0.5 * (Sb.x0 + Sb.x1), 0.5 * (Sb.y0 + Sb.y1))
            aH = CL.axis_core_in(pcH0, 0.5 * (H.x0 + H.x1), 0.5 * (H.y0 + H.y1))
            cS = (0.5 * (Sb.x0 + Sb.x1), 0.5 * (Sb.y0 + Sb.y1))
            cH = (0.5 * (H.x0 + H.x1), 0.5 * (H.y0 + H.y1))
            clH = CL.clip_box(H, cS, aS, 1) if aS > 0 else None
            clS = CL.clip_box(Sb, cH, aH, 1) if aH > 0 else None
            Hc = H if (clH is None or clH["refused"] or clH["union_rect"] is None) \
                else CL.rect_to_box(clH["union_rect"], H.th0, H.th1)
            Sc = Sb if (clS is None or clS["refused"] or clS["union_rect"] is None) \
                else CL.rect_to_box(clS["union_rect"], Sb.th0, Sb.th1)
            conds, meet, cell, _ = CL.frame_conds(rec, j["slot"], Hc, Sc)
            hidx = meet[0]
            csH = next(x for x in conds if x.idx == hidx)
            rng = np.random.default_rng(1585 + piece)
            log("%s %s piece %d : M-cover ladder on H_clipped %s"
                % (j["nid"], j["slot"], piece, csH.box))
            steps, mres = [], None
            for (md, mo) in ladder:
                ap_, cp_ = YL.free_mb()
                if ap_ < 3072 or cp_ < 6144:
                    steps.append(dict(max_depth=md, max_open=mo, aborted="memory gate"))
                    log("   rung (%d, %d) SKIPPED: free phys %.0f MB" % (md, mo, ap_))
                    break
                t0 = time.time()
                r = SL.P.cond_can_meet(csH, cell, conds, max_leaves=a.maxleaves,
                                       max_depth=md, max_open=mo)
                dt = time.time() - t0
                steps.append(dict(max_depth=md, max_open=mo, ok=bool(r["ok"]),
                                  n_leaves=r["n_leaves"], open=len(r["open"]),
                                  depth=r["depth"], reason=r.get("reason"),
                                  secs=round(dt, 1), rss_mb=round(LD.rss_mb(), 1)))
                mres = r
                log("   rung (depth %d, open %6d): excluded=%-5s leaves %-7s open %-7s "
                    "depth %-3s %6.1fs RSS %.0f MB  %s"
                    % (md, mo, bool(r["ok"]), r["n_leaves"], len(r["open"]), r["depth"], dt,
                       steps[-1]["rss_mb"], r.get("reason") or ""))
                if r["ok"] or dt > a.wall:
                    break
            excluded = bool(mres and mres["ok"])
            # the lane half, re-certified alongside so the certificate is self-contained
            lres = SL.P.lane_corner_generic(cell, conds, meeters=meet, rng=rng, sample=20000,
                                            max_open=a.lane_open, max_depth=34,
                                            lane_depth0=a.lane_depth0, keep_cert=True,
                                            bound_when_dead=True)
            lane = lres.get("lane_ub")
            M = 0 if excluded else (lres.get("M") if lres.get("M") is not None else 1)
            kill = bool(lane == 0 and M == 0)
            row = dict(nid=j["nid"], slot=j["slot"], piece=piece, r=a.r, tt=a.tt,
                       H_box=H.to_json(), H_box_clipped=Hc.to_json(),
                       S_box=Sb.to_json(), S_box_clipped=Sc.to_json(),
                       clip_kept_H=(clH or {}).get("kept_union"),
                       clip_kept_S=(clS or {}).get("kept_union"),
                       lane_ub=lane, M=M, M_excluded_by_cover=excluded,
                       total_meeters=(None if lane is None else 1 + lane + M),
                       kill=kill, m_steps=steps,
                       h_sample_line=CL.h_sample_line(conds, hidx, cell, rng, a.nline))
            log("   -> LANE<=%s  M=%s  1+LANE+M=%s  %s ; H sample line %s"
                % (lane, M, row["total_meeters"],
                   "KILL BY TELEPORT" if kill else "no kill",
                   json.dumps(row["h_sample_line"])))
            if kill:
                d = EM141.cert_dict("polycore_slot_lane_clipped", j["nid"], j["slot"], conds,
                                    [x.box for x in conds], lres,
                                    extra=dict(cell_kind="usable_slot", cls=rec["cls"],
                                               attempt="A158b",
                                               extension=SL.CP.CLASSES[rec["cls"]]["usable"][j["slot"]],
                                               s_box=Sb.to_json(), s_box_clipped=Sc.to_json(),
                                               h_box=H.to_json(), h_box_clipped=Hc.to_json(),
                                               s_piece=piece, s_r=a.r, s_tt=a.tt,
                                               clip_axis_core_S=dict(a=aS, centre=list(cS)),
                                               clip_axis_core_H=dict(a=aH, centre=list(cH)),
                                               M_cover=mres["leaves"], M_ladder=steps,
                                               h_sample_line=row["h_sample_line"],
                                               kill_rule="1 + LANE_K'(C | S, H_clipped) + "
                                                         "M(C | S, H_clipped) <= 1"))
                p = os.path.join(a.certs, "yeslane_%s__%s__p%d.json"
                                 % (j["nid"], j["slot"].replace("(", "").replace(")", "")
                                    .replace(",", "_"), piece))
                row["cert"] = os.path.relpath(p, ROOT)
                row["sha256"] = EM141.write_cert(p, d)
                log("   cert %s" % row["cert"])
            fh.write(json.dumps(row) + "\n")
            fh.flush()
    fh.close()


if __name__ == "__main__":
    main()
