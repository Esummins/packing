"""A141 T4 (the PI's extension) -- the K' lane leaf at the USABLE SLOTS of the A57/A60 alive
population, with certificates.

THE SLOT RULE (A118 method.md sec 3, from `attempts/A56-sparametric/results/scoreboard.json`,
A56 + A61 + A114).  A cell `p` of class `S` is USABLE iff it is an unclipped COMPLETABLE slot
whose EXTENSION class `T = S u {p}` is certified dead on a window CONTAINING the node's side
range.  Every extension of every slot below is FULL on the CLOSED window [191/50, 969271/250000]:

    k5_11: BL(1,1)->k6_18, BR(0,1)->k6_20, TL(1,0)->k6_20, TR(0,0)->k6_23
    k5_16: BL(1,0)->k6_23, BR(0,1)->k6_29, BR(1,0)->k6_27, TR(0,1)->k6_30, TR(1,0)->k6_28,
           TL(1,0)->k6_27
    trump5: BL(0,2)->k6_07, BL(1,1)->k6_19, BR(0,1)->k6_21, TR(0,1)->k6_22, TR(1,0)->k6_24,
           TL(0,0)->k6_23

THE LEAF.  Lemma SLOT-CROWD gives >= 2 NON-PIN squares meeting the slot cell of any class-S
packing at any side of the node's range.  If LANE_K'(p) + M(p) <= 1 -- LANE over free squares
that avoid the pin cores AND the conditioned K', M over the conditioned squares that can reach
the cell -- that is impossible, so the node is DEAD.  (Equivalently, in the PI's phrasing: a
singly-met usable slot lets the meeter be snapped into the exact slot, landing the packing in
the dead extension class T.)

The cores: for a PIN, K'(B) with B the pin's own (m-hulled, zero-tilt) box -- A135's EXACT pin
core, the unit square less the box's width, not pinguard's a = 0.48999997; for the conditioned
square, K'(B) of its m-hulled box.  Frame: A118's, the ORIGINAL packing at side m in the cell's
corner frame, every box hulled over m in [m_lo, s0] by `lane.cframe_boxes` (imported READ-ONLY).
Lemma CONT is dropped -- it only ENLARGES R'(C), so the LANE upper bound stays sound.

    python t4_slots.py --nodes k5_16_interior_Y0460 --slots "BR(0,1)"
    python t4_slots.py --from ../results/t2_a5760_s0.jsonl,../results/t2_a5760_s1.jsonl
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
A118 = os.path.join(ROOT, "attempts", "A118-lane-count", "code")
for _p in (HERE, A118):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import blas1  # noqa: F401,E402
import numpy as np  # noqa: E402

import polylane as P              # noqa: E402
import polycore as PC             # noqa: E402
import emit141 as EM              # noqa: E402
import lane as LANE               # noqa: E402  READ-ONLY
import corpus as CP               # noqa: E402  READ-ONLY
from caselp import Box            # noqa: E402


def build(rec, slot):
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


def run(rec, slot, rng, sample, maxopen, keep_cert=True):
    conds, meet, cell = build(rec, slot)
    res = P.lane_corner_generic(cell, conds, meeters=meet, rng=rng, sample=sample,
                                max_open=maxopen, keep_cert=keep_cert)
    res["slot"] = slot
    res["n_pins"] = len(conds) - len(meet)
    return res, conds, cell


def sample_line(conds, cell, rng, n):
    C, T = P.sample_meeting(cell, P.S0, n, rng)
    hit = np.zeros(len(C), bool)
    per = {}
    for cs in conds:
        h = PC.poly_square_depth(cs.pc.P, C, T) > 0.0
        per[cs.idx] = int(h.sum())
        hit |= h
    return dict(drawn=n, meeting=int(len(C)), overlapping_some_core=int(hit.sum()),
                per_core=per, free=int((~hit).sum()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nodes", default="")
    ap.add_argument("--slots", default="")
    ap.add_argument("--from", dest="src", default="")
    ap.add_argument("--out", default=os.path.join(BASE, "results", "t4_slots.jsonl"))
    ap.add_argument("--sample", type=int, default=200000)
    ap.add_argument("--maxopen", type=int, default=2500)
    a = ap.parse_args()

    recs = {r["nid"]: r for r in CP.load_nodes()}
    known = set(recs)
    boxes, _ = CP.load_open_boxes(known)
    for b in boxes:
        if not b.get("covered_by_node"):
            recs.setdefault(b["nid"], b)

    jobs = []
    if a.nodes:
        for nid in a.nodes.split(","):
            for slot in (a.slots.split(";") if a.slots
                         else list(CP.CLASSES[recs[nid]["cls"]]["usable"].keys())):
                jobs.append((nid, slot))
    for f in [x for x in a.src.split(",") if x]:
        for ln in open(f, encoding="utf-8"):
            r = json.loads(ln)
            for slot in r.get("kill_cells", []):
                if (r["nid"], slot) not in jobs and r["nid"] in recs:
                    jobs.append((r["nid"], slot))
    print("%d (node, slot) jobs" % len(jobs), flush=True)

    fh = open(a.out, "a", encoding="utf-8")
    rng = np.random.default_rng(1441)
    n_kill = 0
    t0 = time.time()
    for (nid, slot) in jobs:
        rec = recs[nid]
        res, conds, cell = run(rec, slot, rng, a.sample // 10, a.maxopen)
        row = dict(nid=nid, src=rec["src"], cls=rec["cls"], level=rec["level"],
                   slot=slot, lane_ub=res["lane_ub"], lane_lb=res["lane_lb"],
                   M=res["M"], M_exact=res.get("M_exact"), meeters=res["meeters"],
                   verdict=res["verdict"], n_pins=res["n_pins"])
        if res["verdict"] == "KILL":
            row["sample_line"] = sample_line(conds, cell, rng, a.sample)
            d = EM.cert_dict("polycore_slot_lane", nid, slot, conds,
                             [c.box for c in conds], res,
                             extra=dict(cell_kind="usable_slot", cls=rec["cls"],
                                        extension=CP.CLASSES[rec["cls"]]["usable"][slot],
                                        extension_window="[191/50, 969271/250000] FULL "
                                                         "(A56/A61/A114 scoreboard)",
                                        n_pins=res["n_pins"],
                                        sample_line=row["sample_line"]))
            p = os.path.join(BASE, "certs", "slot_%s__%s.json"
                             % (nid, slot.replace("(", "").replace(")", "").replace(",", "_")))
            row["cert"] = os.path.relpath(p, ROOT)
            row["sha256"] = EM.write_cert(p, d)
            n_kill += 1
        fh.write(json.dumps(row) + "\n")
        fh.flush()
        print("%-34s %-9s LANE<=%s M=%s %s %s" % (nid, slot, res["lane_ub"], res["M"],
                                                  res["verdict"],
                                                  row.get("cert", "")), flush=True)
    fh.close()
    print("done %d jobs, %d kills, %.0f s" % (len(jobs), n_kill, time.time() - t0))


if __name__ == "__main__":
    main()
