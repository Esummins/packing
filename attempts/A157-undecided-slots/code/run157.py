"""A157 T2 -- run A141's CERTIFYING cover on the UNDECIDED usable-slot cells.

Identical machinery to `A141/code/t4_slots.py` (imported READ-ONLY): the same corner frame
(`lane.cframe_boxes`), the same EXACT pin cores and conditioned `K'(H)` (`polylane.build_cond`,
`tighten=False`), the same leaf `polylane.lane_corner_generic`, the same `M` exclusion by the
interval cover, the same `emit141.cert_dict` -> `polycore_slot_lane_v1` certificate and the same
`check141.py`.  The ONLY change is the cover BUDGET: A141's sweep ran `max_open = 1200`,
`lane_depth0 = 20`, which exhausted the open budget on these cells and returned `lane = None`
(verdict UNDECIDED).  A157 walks a budget LADDER until the cover closes.

    python run157.py --jobs ../results/undecided_cells.jsonl --shard 0/2
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
A118 = os.path.join(ROOT, "attempts", "A118-lane-count", "code")
for _p in (A141, A118):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import blas1  # noqa: F401,E402   (A141's single-thread BLAS pin, imported before numpy)
import numpy as np  # noqa: E402

import polylane as P              # noqa: E402  READ-ONLY
import polycore as PC             # noqa: E402  READ-ONLY
import emit141 as EM              # noqa: E402  READ-ONLY
import lane as LANE               # noqa: E402  READ-ONLY
import corpus as CP               # noqa: E402  READ-ONLY
from caselp import Box            # noqa: E402  READ-ONLY

# (lane_depth0, max_open, rounds-worth max_depth) ladder
LADDER = [(20, 1200, 34), (22, 8000, 34), (25, 40000, 36), (28, 160000, 40)]


def build(rec, slot):
    """A141 t4_slots.build, verbatim."""
    c, i, j = LANE.L.parse_cell(slot)
    pin_b, cond_b = LANE.cframe_boxes(rec, c, i, j)
    pins = P.build_cond([Box(b.x0, b.x1, b.y0, b.y1, b.th0, b.th1) for b in pin_b],
                        tighten=False)
    cond = P.build_cond([Box(b.x0, b.x1, b.y0, b.y1, b.th0, b.th1) for b in cond_b],
                        tighten=False)
    for k, cs in enumerate(cond):
        cs.idx = len(pins) + k
    return pins + cond, [cs.idx for cs in cond], (float(i), float(i) + 1.0,
                                                  float(j), float(j) + 1.0)


def sample_line(conds, cell, rng, n):
    """A141 t4_slots.sample_line, verbatim: drawn -> meeting -> free."""
    C, T = P.sample_meeting(cell, P.S0, n, rng)
    hit = np.zeros(len(C), bool)
    per = {}
    for cs in conds:
        h = PC.poly_square_depth(cs.pc.P, C, T) > 0.0
        per[cs.idx] = int(h.sum())
        hit |= h
    return dict(drawn=n, meeting=int(len(C)), overlapping_some_core=int(hit.sum()),
                per_core=per, free=int((~hit).sum()))


def slot_tag(slot):
    return slot.replace("(", "").replace(")", "").replace(",", "_")


def run_cell(job, recs, rng, sample, wall, ladder):
    nid, slot = job["nid"], job["slot"]
    rec = recs[nid]
    conds, meet, cell = build(rec, slot)
    steps = []
    res = None
    t0 = time.time()
    for (d0, mo, md) in ladder:
        r = P.lane_corner_generic(cell, conds, meeters=meet, rng=rng, sample=sample,
                                  max_open=mo, max_depth=md, lane_depth0=d0,
                                  keep_cert=True, bound_when_dead=True)
        steps.append(dict(depth0=d0, max_open=mo, max_depth=md, lane_ub=r.get("lane_ub"),
                          lane_lb=r.get("lane_lb"), M=r.get("M"),
                          leaves=r.get("cover_leaves"), open=r.get("cover_open"),
                          hist=r.get("cover_hist"), verdict=r.get("verdict"),
                          secs=round(time.time() - t0, 1)))
        res = r
        if r.get("verdict") == "KILL" or r.get("lane_ub") is not None:
            break
        if time.time() - t0 > wall:
            break
    return res, conds, cell, meet, steps, round(time.time() - t0, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", default=os.path.join(BASE, "results", "undecided_cells.jsonl"))
    ap.add_argument("--recs", default=os.path.join(BASE, "results", "recs157.json"))
    ap.add_argument("--out", default=os.path.join(BASE, "results", "t157_cells.jsonl"))
    ap.add_argument("--progress", default=os.path.join(BASE, "progress", "t157.json"))
    ap.add_argument("--certs", default=os.path.join(BASE, "certs"))
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--only", default="", help="comma list of nid or nid:slot")
    ap.add_argument("--sample", type=int, default=20000)
    ap.add_argument("--sample_line", type=int, default=200000)
    ap.add_argument("--wall", type=float, default=150.0, help="per-cell seconds before the "
                                                             "ladder stops escalating")
    ap.add_argument("--budget", type=float, default=5000.0, help="process wall budget, seconds")
    ap.add_argument("--maxstep", type=int, default=4, help="ladder rungs to use")
    ap.add_argument("--ladder", default="", help="depth0:max_open:max_depth, comma separated")
    a = ap.parse_args()

    if os.path.exists(a.recs):
        recs = json.load(open(a.recs, encoding="utf-8"))
    else:                                          # fall back to the live corpus (slow)
        recs = {r["nid"]: r for r in CP.load_nodes()}
        known = set(recs)
        boxes, _ = CP.load_open_boxes(known)
        for b in boxes:
            if not b.get("covered_by_node"):
                recs.setdefault(b["nid"], b)

    jobs, seen = [], set()
    with open(a.jobs, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln:
                continue
            j = json.loads(ln)
            k = (j["nid"], j["slot"])
            if k in seen:                     # the same node can sit in two A57 shard trees
                continue
            seen.add(k)
            jobs.append(j)
    if a.only:
        want = set(a.only.split(","))
        jobs = [j for j in jobs if j["nid"] in want or (j["nid"] + ":" + j["slot"]) in want]
    k, n = (int(v) for v in a.shard.split("/"))
    if n > 1:
        jobs = [j for i, j in enumerate(jobs) if i % n == k]

    done = set()
    if os.path.exists(a.out):
        with open(a.out, encoding="utf-8") as fh:
            for ln in fh:
                try:
                    d = json.loads(ln)
                    done.add((d["nid"], d["slot"]))
                except Exception:             # noqa: BLE001
                    pass
    print("A157: %d (node, slot) cells (%d already done)" % (len(jobs), len(done)), flush=True)

    if a.ladder:
        ladder = [tuple(int(v) for v in spec.split(":")) for spec in a.ladder.split(",")]
    else:
        ladder = LADDER[:a.maxstep]
    print("ladder %s" % (ladder,), flush=True)
    fh = open(a.out, "a", encoding="utf-8")
    rng = np.random.default_rng(1570 + k)
    t0 = time.time()
    n_kill = n_near = n_open = 0
    for idx, j in enumerate(jobs):
        if (j["nid"], j["slot"]) in done:
            continue
        if time.time() - t0 > a.budget:
            print("budget reached, stopping", flush=True)
            break
        try:
            res, conds, cell, meet, steps, secs = run_cell(j, recs, rng, a.sample, a.wall,
                                                           ladder)
        except Exception as e:                # noqa: BLE001
            fh.write(json.dumps(dict(nid=j["nid"], slot=j["slot"], src=j["src"], cls=j["cls"],
                                     level=j["level"], verdict="ERROR",
                                     error=repr(e)[:200])) + "\n")
            fh.flush()
            print("ERROR %-34s %-9s %s" % (j["nid"], j["slot"], repr(e)[:90]), flush=True)
            continue
        row = dict(nid=j["nid"], slot=j["slot"], src=j["src"], key=j["key"], cls=j["cls"],
                   level=j["level"], lane_ub=res.get("lane_ub"), lane_lb=res.get("lane_lb"),
                   M=res.get("M"), M_exact=res.get("M_exact"), meeters=res.get("meeters"),
                   verdict=res.get("verdict"), n_pins=len(conds) - len(meet),
                   a141_M=j["M"], a141_lane_lb=j["lane_lb"], steps=steps, secs=secs)
        if res.get("verdict") == "KILL":
            row["sample_line"] = sample_line(conds, cell, rng, a.sample_line)
            d = EM.cert_dict("polycore_slot_lane", j["nid"], j["slot"], conds,
                             [c.box for c in conds], res,
                             extra=dict(cell_kind="usable_slot", cls=j["cls"],
                                        extension=CP.CLASSES[j["cls"]]["usable"][j["slot"]],
                                        extension_window="[191/50, 969271/250000] FULL "
                                                         "(A56/A61/A114 scoreboard)",
                                        n_pins=len(conds) - len(meet), attempt="A157",
                                        provenance="A141 t2_a5760 UNDECIDED "
                                                   "(lane_lb=0, M<=1); re-covered at "
                                                   "depth0=%d, max_open=%d"
                                                   % (steps[-1]["depth0"], steps[-1]["max_open"]),
                                        sample_line=row["sample_line"]))
            p = os.path.join(a.certs, "slot_%s__%s.json" % (j["nid"], slot_tag(j["slot"])))
            row["cert"] = os.path.relpath(p, ROOT)
            row["sha256"] = EM.write_cert(p, d)
            n_kill += 1
        elif res.get("verdict") == "NEAR-MISS":
            n_near += 1
        else:
            n_open += 1
        fh.write(json.dumps(row) + "\n")
        fh.flush()
        json.dump(dict(done=idx + 1, of=len(jobs), kills=n_kill, near=n_near, open=n_open,
                       elapsed=round(time.time() - t0, 1)),
                  open(a.progress, "w", encoding="utf-8"))
        print("%-34s %-9s LANE<=%-4s M=%-3s %-12s %6.1fs %s"
              % (j["nid"], j["slot"], res.get("lane_ub"), res.get("M"), res.get("verdict"),
                 secs, row.get("cert", "")), flush=True)
    fh.close()
    print("A157 done: %d kills, %d near-miss, %d open, %.0f s"
          % (n_kill, n_near, n_open, time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
