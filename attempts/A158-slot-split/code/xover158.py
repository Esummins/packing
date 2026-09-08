"""A158 -- the CROSSOVER radius of the slot split, measured, not guessed.

For a (node, slot) the YES child can only close if EVERY free meeter of the cell and EVERY
conditioned meeter is forced to overlap K'(S_r).  K'(S_r) SHRINKS as r grows, so there is a
threshold

    r_lane := sup { r : every sampled free meeter of int C overlaps K'(S_r) }
    r_M    := sup { r : every conditioned meeter is blocked by K'(S_r) }
    r_yes  := min(r_lane, r_M)

and for r > r_yes the YES kill is REFUTED by a realised pose (sound, no cover needed).  r_yes is
an UPPER bound on the closable radius: it is computed from a finite sample of free poses, so the
true threshold can only be smaller.

The NO child pulls the other way: the bigger the zone S_r, the more LP rows it exempts.  This
script measures the geometry half; `no158.py` measures the LP half.

    python xover158.py --jobs ../results/xover_jobs.jsonl --n 400000
"""
import argparse
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import slotlib158 as SL  # noqa: E402
import numpy as np  # noqa: E402


def s_core(i, j, r, tt, piece):
    b = SL.s_boxes_frame(i, j, r, tt)[piece]
    return SL.P.build_cond([b], tighten=False)[0]


def overlaps_all(cs, C, T):
    """boolean: the pose's square overlaps K'(S) (positive SAT depth)."""
    return SL.PC.poly_square_depth(cs.pc.P, C, T) > 0.0


def r_threshold_lane(i, j, tt, piece, C, T, rlo=0.0, rhi=0.25, iters=22):
    """largest r with EVERY pose of (C, T) overlapping K'(S_r); poses are the sampled free
    meeters.  Monotone: K'(S_r) shrinks in r, so the predicate is monotone decreasing."""
    if not len(C):
        return rhi, None                       # nothing to block
    def ok(r):
        cs = s_core(i, j, r, tt, piece)
        return bool(overlaps_all(cs, C, T).all())
    if not ok(rlo):
        return -1.0, None
    if ok(rhi):
        return rhi, None
    for _ in range(iters):
        mid = 0.5 * (rlo + rhi)
        if ok(mid):
            rlo = mid
        else:
            rhi = mid
    cs = s_core(i, j, rhi, tt, piece)
    m = ~overlaps_all(cs, C, T)
    k = int(np.nonzero(m)[0][0])
    return rlo, [float(C[k, 0]), float(C[k, 1]), math.degrees(float(T[k]))]


def r_threshold_M(conds, meet, cell, i, j, tt, piece, rng, n, rlo=0.0, rhi=0.25, iters=16):
    """largest r at which NO conditioned meeter can meet int C clear of K'(S_r)."""
    def ok(r):
        cs = s_core(i, j, r, tt, piece)
        cs.idx = max(c.idx for c in conds) + 1
        return SL.screen_cond_meet(conds + [cs], meet, cell, rng, n)["M_lb"] == 0
    if not ok(rlo):
        return -1.0
    if ok(rhi):
        return rhi
    for _ in range(iters):
        mid = 0.5 * (rlo + rhi)
        if ok(mid):
            rlo = mid
        else:
            rhi = mid
    return rlo


def free_meeters(conds, cell, rng, n, cap=4000):
    """sampled poses in R'(C): meet int C, in the container, clear of every node core."""
    C, T = SL.P.sample_meeting(cell, SL.S0, n, rng)
    if not len(C):
        return C, T, 0
    hit = np.zeros(len(C), bool)
    for cs in conds:
        hit |= (SL.PC.poly_square_depth(cs.pc.P, C, T) > 0.0)
    return C[~hit][:cap], T[~hit][:cap], int(len(C))


def run(rec, slot, rng, n, nm, tilts):
    conds, meet, cell, (c, i, j) = SL.build_node(rec, slot)
    C, T, nmeet = free_meeters(conds, cell, rng, n)
    out = dict(nid=rec["nid"], src=rec["src"], cls=rec["cls"], level=rec.get("level"), slot=slot,
               n_drawn=n, n_meeting=nmeet, n_free=int(len(C)), n_pins=len(conds) - len(meet),
               rows=[])
    for tt in tilts:
        row = dict(tt=tt)
        for piece in (0, 1):
            rl, wit = r_threshold_lane(i, j, tt, piece, C, T)
            rm = r_threshold_M(conds, meet, cell, i, j, tt, piece, rng, nm)
            row["piece%d" % piece] = dict(r_lane=rl, r_M=rm, r_yes=min(rl, rm), witness=wit)
        row["r_yes"] = min(row["piece0"]["r_yes"], row["piece1"]["r_yes"])
        out["rows"].append(row)
    out["r_yes_best"] = max(r["r_yes"] for r in out["rows"]) if out["rows"] else None
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", default="")
    ap.add_argument("--nid", default="c0_Y0076")
    ap.add_argument("--slot", default="TL(0,0)")
    ap.add_argument("--recs", default=os.path.join(BASE, "results", "recs158.json"))
    ap.add_argument("--n", type=int, default=400000)
    ap.add_argument("--nm", type=int, default=120000)
    ap.add_argument("--tilts", default="0,10,15")
    ap.add_argument("--out", default=os.path.join(BASE, "results", "xover158.jsonl"))
    ap.add_argument("--budget", type=float, default=3000.0)
    a = ap.parse_args()

    recs = json.load(open(a.recs, encoding="utf-8")) if os.path.exists(a.recs) else {}
    if not recs:
        recs = {r["nid"]: r for r in SL.CP.load_nodes()}
    jobs = []
    if a.jobs:
        for ln in open(a.jobs, encoding="utf-8"):
            ln = ln.strip()
            if ln:
                jobs.append(json.loads(ln))
    else:
        jobs = [dict(nid=a.nid, slot=a.slot)]
    tilts = [float(v) for v in a.tilts.split(",")]
    done = set()
    if os.path.exists(a.out):
        for ln in open(a.out, encoding="utf-8"):
            try:
                d = json.loads(ln)
                done.add((d["nid"], d["slot"]))
            except Exception:                      # noqa: BLE001
                pass
    rng = np.random.default_rng(1580)
    fh = open(a.out, "a", encoding="utf-8")
    t0 = time.time()
    for j in jobs:
        if (j["nid"], j["slot"]) in done:
            continue
        if time.time() - t0 > a.budget:
            print("budget reached", flush=True)
            break
        try:
            r = run(recs[j["nid"]], j["slot"], rng, a.n, a.nm, tilts)
            r.update({k: v for k, v in j.items() if k not in r})
        except Exception as e:                     # noqa: BLE001
            r = dict(nid=j["nid"], slot=j["slot"], error=repr(e)[:200])
        fh.write(json.dumps(r) + "\n")
        fh.flush()
        print("%-30s %-9s free %-5s r_yes %s  %s"
              % (j["nid"], j["slot"], r.get("n_free"), r.get("r_yes_best"),
                 json.dumps([{"tt": x["tt"], "r": x["r_yes"]} for x in r.get("rows", [])])),
              flush=True)
    fh.close()


if __name__ == "__main__":
    main()
