"""A158 -- the YES child, certifying: A141's `lane_corner_generic` with K'(S) as an extra
obstacle, and a `polycore_slot_lane_v1` certificate with ONE new field.

The certificate is A141's `emit141.cert_dict(kind="polycore_slot_lane", ...)` verbatim, plus

    extra["s_box"]      the pose box S of the YES hypothesis (corner frame), and its tilt piece
    extra["s_index"]    the index of K'(S) in the certificate's core list
    extra["kill_rule"]  "1 + LANE_K'(C | S) + M(C | S) <= 1", i.e. LANE = M = 0

so a checker only has to (a) replay the cover exactly as A141's `check141.py` does, the extra core
being one more entry in the list, and (b) read the kill rule off `lane_ub + M + 1 <= 1` instead of
`lane_ub + M <= 1`.  Nothing else about the format changes.

This is run only on cells the fast screen (`yesscreen158.py`) does NOT refute — on the corpus
measured here that is the empty set, so no certificate was emitted; the driver exists so the leaf
is deployable the moment a cell survives the screen.

    python yescert158.py --jobs ../results/yes_candidates.jsonl --r 0.10 --tt 10
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
A141 = os.path.join(ROOT, "attempts", "A141-polycore-lane", "code")
for _p in (HERE, A141):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import slotlib158 as SL  # noqa: E402
import emit141 as EM     # noqa: E402  READ-ONLY (A141)
import numpy as np       # noqa: E402

LADDER = [(20, 1200, 34), (22, 8000, 34), (25, 40000, 36)]


def slot_tag(slot):
    return slot.replace("(", "").replace(")", "").replace(",", "_")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", default=os.path.join(BASE, "results", "yes_candidates.jsonl"))
    ap.add_argument("--recs", default=os.path.join(BASE, "results", "recs158.json"))
    ap.add_argument("--r", type=float, default=0.10)
    ap.add_argument("--tt", type=float, default=10.0)
    ap.add_argument("--sample", type=int, default=20000)
    ap.add_argument("--wall", type=float, default=300.0)
    ap.add_argument("--out", default=os.path.join(BASE, "results", "yescert158.jsonl"))
    ap.add_argument("--certs", default=os.path.join(BASE, "certs"))
    a = ap.parse_args()

    if not os.path.exists(a.jobs):
        print("no candidate file %s -- nothing to certify" % a.jobs)
        return
    recs = json.load(open(a.recs, encoding="utf-8"))
    jobs = [json.loads(l) for l in open(a.jobs, encoding="utf-8") if l.strip()]
    rng = np.random.default_rng(15802)
    fh = open(a.out, "a", encoding="utf-8")
    for j in jobs:
        rec = recs[j["nid"]]
        conds, meet, cell, (c, i, jj) = SL.build_node(rec, j["slot"])
        for piece in (0, 1):
            cs, sq = SL.add_s(conds, i, jj, a.r, a.tt, piece)
            t0 = time.time()
            res = None
            for (d0, mo, md) in LADDER:
                res = SL.P.lane_corner_generic(cell, cs, meeters=meet, rng=rng,
                                               sample=a.sample, max_open=mo, max_depth=md,
                                               lane_depth0=d0, keep_cert=True,
                                               bound_when_dead=True)
                if res.get("lane_ub") is not None or time.time() - t0 > a.wall:
                    break
            lane, M = res.get("lane_ub"), res.get("M")
            kill = bool(lane == 0 and M == 0)
            row = dict(nid=j["nid"], slot=j["slot"], r=a.r, tt=a.tt, piece=piece,
                       lane_ub=lane, lane_lb=res.get("lane_lb"), M=M,
                       M_exact=res.get("M_exact"), verdict=res.get("verdict"),
                       total_meeters=(None if lane is None or M is None else 1 + lane + M),
                       kill=kill, secs=round(time.time() - t0, 1))
            if kill:
                d = EM.cert_dict("polycore_slot_lane", j["nid"], j["slot"], cs,
                                 [x.box for x in cs], res,
                                 extra=dict(cell_kind="usable_slot", cls=rec["cls"],
                                            extension=SL.CP.CLASSES[rec["cls"]]["usable"][j["slot"]],
                                            attempt="A158",
                                            s_box=SL.P.box_json(sq.box), s_index=sq.idx,
                                            s_piece=piece, s_r=a.r, s_tt=a.tt,
                                            kill_rule="YES child of the A158 slot split: "
                                                      "1 + LANE_K'(C | S) + M(C | S) <= 1, i.e. "
                                                      "LANE_K'(C | S) = 0 and M(C | S) = 0; the "
                                                      "discharge against K'(S) IDENTIFIES the "
                                                      "pose with the S-square "
                                                      "(PolyCoreT5.shared_point_same_square)",
                                            provenance="A158 conditional lane test"))
                p = os.path.join(a.certs, "yes_%s__%s__p%d.json"
                                 % (j["nid"], slot_tag(j["slot"]), piece))
                row["cert"] = os.path.relpath(p, ROOT)
                row["sha256"] = EM.write_cert(p, d)
            fh.write(json.dumps(row) + "\n")
            fh.flush()
            print("%-32s %-9s p%d LANE<=%s M=%s -> %s %s"
                  % (j["nid"], j["slot"], piece, lane, M,
                     "KILL" if kill else res.get("verdict"), row.get("cert", "")), flush=True)
    fh.close()


if __name__ == "__main__":
    main()
