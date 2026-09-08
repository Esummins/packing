"""A158b -- escalate the CONDITIONAL LANE cover on the clipped cores until it empties (or breaks).

`clip158.py` found the one live route: with `S` clamped to the admissible strip (so `K'(S)` is fat)
and `H` clipped against `K'(S)`, the 400,000-pose screen realises NO free meeter of the slot cell
(`lane_lb = 0`) and the `M` cover certifies `M(C | S, H_clipped) = 0`.  What is missing is the
EMPTY lane cover: `lane_corner_generic` at `(depth0 = 22, max_open = 8,000)` certified only
`LANE_K' <= 1`.  `1 + LANE + M <= 1` needs `LANE = 0`, i.e. every box of a complete cover of the
pose window discharged.

This walks the budget ladder on that one cover, reporting leaves / open / RSS / seconds per rung so
the cost is measured rather than guessed (A157 measured that `depth0 >= 24` with
`max_open >= 40,000` can reach GB-scale in `lane_cover`'s leaf list -- RSS is printed every rung and
the ladder stops on the memory gate).

    python lanedeep158.py --jobs ../results/y0076_job.jsonl --ladder 24:30000:36,26:60000:38
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
for _p in (HERE,):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import slotlib158 as SL                                            # noqa: E402
import yeslp158 as YL                                              # noqa: E402
import clip158 as CL                                               # noqa: E402
import emit141 as EM141                                            # noqa: E402  READ-ONLY (A141)
import numpy as np                                                 # noqa: E402
from caselp import Box                                             # noqa: E402


def rss_mb():
    try:
        import ctypes
        from ctypes import wintypes

        class PMC(ctypes.Structure):
            _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                        ("PeakWorkingSetSize", ctypes.c_size_t),
                        ("WorkingSetSize", ctypes.c_size_t),
                        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                        ("PagefileUsage", ctypes.c_size_t),
                        ("PeakPagefileUsage", ctypes.c_size_t)]
        c = PMC()
        c.cb = ctypes.sizeof(PMC)
        ctypes.windll.psapi.GetProcessMemoryInfo(
            ctypes.windll.kernel32.GetCurrentProcess(), ctypes.byref(c), c.cb)
        return c.WorkingSetSize / 2 ** 20
    except Exception:                                              # noqa: BLE001
        return -1.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", default=os.path.join(BASE, "results", "y0076_job.jsonl"))
    ap.add_argument("--recs", default=os.path.join(BASE, "results", "recs158.json"))
    ap.add_argument("--r", type=float, default=0.10)
    ap.add_argument("--tt", type=float, default=10.0)
    ap.add_argument("--ladder", default="24:30000:36,26:60000:38,28:120000:40")
    ap.add_argument("--wall", type=float, default=900.0)
    ap.add_argument("--sample", type=int, default=20000)
    ap.add_argument("--nline", type=int, default=20000)
    ap.add_argument("--out", default=os.path.join(BASE, "results", "lanedeep158.jsonl"))
    ap.add_argument("--certs", default=os.path.join(BASE, "certs"))
    ap.add_argument("--budget_s", type=float, default=4800.0)
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
        conds_json = node["hyp"]["boxes"][rec["n_pin"]:]
        if len(conds_json) != 1:
            log("%s: %d conditioned boxes, skipped" % (j["nid"], len(conds_json)))
            continue
        H = Box.from_json(conds_json[0])
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
            rng = np.random.default_rng(1584 + piece)
            log("%s %s piece %d : S=%s  H_clipped=%s" % (j["nid"], j["slot"], piece, Sc, Hc))
            steps, res = [], None
            for (d0, mo, md) in ladder:
                ap_, cp_ = YL.free_mb()
                if ap_ < 3072 or cp_ < 6144:
                    steps.append(dict(depth0=d0, max_open=mo, aborted="memory gate"))
                    log("   rung (%d, %d) SKIPPED: free phys %.0f MB" % (d0, mo, ap_))
                    break
                t0 = time.time()
                r = SL.P.lane_corner_generic(cell, conds, meeters=meet, rng=rng,
                                             sample=a.sample, max_open=mo, max_depth=md,
                                             lane_depth0=d0, keep_cert=True,
                                             bound_when_dead=True)
                dt = time.time() - t0
                steps.append(dict(depth0=d0, max_open=mo, max_depth=md,
                                  lane_ub=r.get("lane_ub"), lane_lb=r.get("lane_lb"),
                                  M=r.get("M"), leaves=r.get("cover_leaves"),
                                  open=r.get("cover_open"), hist=r.get("cover_hist"),
                                  verdict=r.get("verdict"), secs=round(dt, 1),
                                  rss_mb=round(rss_mb(), 1)))
                res = r
                log("   rung (%d, %6d): LANE<=%-4s M=%-3s leaves %-7s open %-7s %6.1fs "
                    "RSS %.0f MB" % (d0, mo, r.get("lane_ub"), r.get("M"),
                                     r.get("cover_leaves"), r.get("cover_open"), dt,
                                     steps[-1]["rss_mb"]))
                if r.get("lane_ub") == 0:
                    break
                if time.time() - t0 > a.wall:
                    log("   per-rung wall %.0fs exceeded; stopping the ladder" % a.wall)
                    break
            lane = res.get("lane_ub") if res else None
            M = res.get("M") if res else None
            kill = bool(lane == 0 and M == 0)
            row = dict(nid=j["nid"], slot=j["slot"], piece=piece, r=a.r, tt=a.tt,
                       S_box=Sb.to_json(), S_box_clipped=Sc.to_json(),
                       H_box=H.to_json(), H_box_clipped=Hc.to_json(),
                       KH_before=float(pcH0.area()), KS_before=float(pcS0.area()),
                       KH_after=float(CL.polycore(Hc).area()),
                       KS_after=float(CL.polycore(Sc).area()),
                       clip_kept_H=(clH or {}).get("kept_union"),
                       clip_kept_S=(clS or {}).get("kept_union"),
                       lane_ub=lane, M=M, total_meeters=(None if lane is None or M is None
                                                         else 1 + lane + M),
                       kill=kill, steps=steps,
                       h_sample_line=CL.h_sample_line(conds, meet[0], cell, rng, a.nline))
            if kill:
                d = EM141.cert_dict("polycore_slot_lane_clipped", j["nid"], j["slot"], conds,
                                    [x.box for x in conds], res,
                                    extra=dict(cell_kind="usable_slot", cls=rec["cls"],
                                               attempt="A158b",
                                               extension=SL.CP.CLASSES[rec["cls"]]["usable"][j["slot"]],
                                               s_box=Sb.to_json(), s_box_clipped=Sc.to_json(),
                                               h_box=H.to_json(), h_box_clipped=Hc.to_json(),
                                               s_piece=piece, s_r=a.r, s_tt=a.tt,
                                               clip_axis_core_S=dict(a=aS, centre=list(cS)),
                                               clip_axis_core_H=dict(a=aH, centre=list(cH)),
                                               h_sample_line=row["h_sample_line"],
                                               ladder=steps,
                                               kill_rule="1 + LANE_K'(C | S, H_clipped) + "
                                                         "M(C | S, H_clipped) <= 1"))
                p = os.path.join(a.certs, "yeslane_%s__%s__p%d.json"
                                 % (j["nid"], j["slot"].replace("(", "").replace(")", "")
                                    .replace(",", "_"), piece))
                row["cert"] = os.path.relpath(p, ROOT)
                row["sha256"] = EM141.write_cert(p, d)
                log("   KILL BY TELEPORT -> %s" % row["cert"])
            else:
                log("   no kill: 1 + LANE + M = %s" % row["total_meeters"])
            fh.write(json.dumps(row) + "\n")
            fh.flush()
    fh.close()


if __name__ == "__main__":
    main()
