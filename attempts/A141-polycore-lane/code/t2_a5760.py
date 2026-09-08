"""A141 T2 (second half) -- the COUNT-ONLY pass of the K' lane test over A57/A60 alive nodes.

The brief asks for a count only, no certificates: a different campaign's fold-in.  The pinned
classes' leaf lives at the USABLE SLOTS, not at the corners, and the frame is A118's: the count
runs on the ORIGINAL packing at side m, in the cell's corner frame, with every hypothesis box
pulled back and hulled over m in [m_lo, s0] (`lane.cframe_boxes`, imported READ-ONLY).  A141
changes exactly one thing: the obstacle of a box B is its POLYGON core K'(B) rather than A96's
axis-aligned tight core -- and for a PIN (zero tilt width, a degenerate or near-degenerate centre
box) K'(B) is A135's EXACT pin core, the unit square itself less the box's own width, rather than
pinguard's `a = 0.48999997`.

Lemma CONT is DROPPED here (it is a real constraint for pinned classes, so dropping it only
ENLARGES R'(C): the LANE upper bound stays sound, just weaker than A118's).  a_w = 1, the closed
cell, exactly as A118's `run_cell`.

    python t2_a5760.py [--out ../results/t2_a5760.jsonl] [--shard k/n]
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
import lane as LANE               # noqa: E402  READ-ONLY import of A118's driver
import corpus as CP               # noqa: E402  READ-ONLY
from caselp import Box            # noqa: E402


def cell_rect(i, j):
    """The closed unit cell [i, i+1] x [j, j+1] of the corner frame."""
    return (float(i), float(i) + 1.0, float(j), float(j) + 1.0)


def run_node(rec, sample, maxopen):
    cells = list(CP.CLASSES[rec["cls"]]["usable"].keys())
    rows = []
    rng = np.random.default_rng(1410 + (abs(hash(rec["nid"])) % 100000))
    for cn in cells:
        c, i, j = LANE.L.parse_cell(cn)
        pin_b, cond_b = LANE.cframe_boxes(rec, c, i, j)
        try:
            pins = P.build_cond([Box(b.x0, b.x1, b.y0, b.y1, b.th0, b.th1) for b in pin_b],
                                tighten=False)
            cond = P.build_cond([Box(b.x0, b.x1, b.y0, b.y1, b.th0, b.th1) for b in cond_b],
                                tighten=False)
        except Exception as e:                                   # noqa: BLE001
            rows.append(dict(cell=cn, verdict="ERROR", error=repr(e)[:120]))
            continue
        for k, cs in enumerate(cond):
            cs.idx = len(pins) + k
        conds = pins + cond
        cell = cell_rect(i, j)
        # LANE: pins AND conditioned cores are obstacles; only the CONDITIONED ones are meeters
        res = P.lane_corner_generic(cell, conds, meeters=[c.idx for c in cond], rng=rng,
                                    sample=sample, max_open=maxopen, keep_cert=False,
                                    bound_when_dead=False)
        res["cell"] = cn
        rows.append(res)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(BASE, "results", "t2_a5760.jsonl"))
    ap.add_argument("--progress", default=os.path.join(BASE, "progress", "t2_a5760.json"))
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--sample", type=int, default=8000)
    ap.add_argument("--maxopen", type=int, default=1200)
    a = ap.parse_args()

    recs = CP.load_nodes()
    known = set(r["nid"] for r in recs)
    boxes, missing = CP.load_open_boxes(known)
    recs = recs + [b for b in boxes if not b.get("covered_by_node")]
    recs = [r for r in recs if r["cls"] != "k0_00" and r.get("alive")]
    recs.sort(key=lambda r: (r["src"], r["nid"]))
    k, n = (int(v) for v in a.shard.split("/"))
    if n > 1:
        recs = [r for idx, r in enumerate(recs) if idx % n == k]
    done = set()
    if os.path.exists(a.out):
        for ln in open(a.out, encoding="utf-8"):
            try:
                done.add(json.loads(ln)["key"])
            except Exception:
                pass
    print("A57/A60 alive: %d nodes (%d done)" % (len(recs), len(done)), flush=True)

    fh = open(a.out, "a", encoding="utf-8")
    t0 = time.time()
    nrun = 0
    for r in recs:
        key = r["src"] + "/" + str(r.get("shard")) + "/" + r["nid"]
        if key in done:
            continue
        try:
            rows = run_node(r, a.sample, a.maxopen)
        except Exception as e:                                   # noqa: BLE001
            rows = [dict(cell="*", verdict="ERROR", error=repr(e)[:160])]
        kill = [x for x in rows if x.get("verdict") == "KILL"]
        fh.write(json.dumps(dict(key=key, src=r["src"], nid=r["nid"], cls=r["cls"],
                                 level=r["level"], alive=r.get("alive"),
                                 cells=[{kk: vv for kk, vv in x.items()
                                         if kk not in ("cover_cert", "cover_open_cert",
                                                       "M_cert", "sample")} for x in rows],
                                 kill=bool(kill),
                                 kill_cells=[x["cell"] for x in kill])) + "\n")
        nrun += 1
        if nrun % 25 == 0:
            fh.flush()
            json.dump(dict(done=nrun, elapsed=round(time.time() - t0, 1)),
                      open(a.progress, "w", encoding="utf-8"))
            print("  %d nodes, %.0f s" % (nrun, time.time() - t0), flush=True)
        if a.limit and nrun >= a.limit:
            break
    fh.close()
    json.dump(dict(done=nrun, elapsed=round(time.time() - t0, 1), finished=True),
              open(a.progress, "w", encoding="utf-8"))
    print("done %d nodes in %.0f s" % (nrun, time.time() - t0))


if __name__ == "__main__":
    main()
