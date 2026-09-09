"""A173 -- MEASURE the lonely clip on A168's trees (READ-ONLY on A168).

For every ALIVE S1 node (roles H + D; D is the first TR meeter) and every ALIVE S2 node
(roles H, D, S) of `tree_l1_104.json` / `tree_l1_153.json`, build an A171 `Node` from the roles'
piece hulls and normalise it TWICE:

    base    node.normalise(...)                       -- A171/A172 as it stands
    lonely  node.normalise(..., corners={"D": ("TR", c)})   -- with A173's lonely clip on D

and report, per node: D kept fraction and K'(D) area before/after, H kept before/after, passes,
the invariant verdict, and any `EmptyBox` (a KILL that A168's whole-role R3 test could not see).

The starting box of each role is the role's `box` field = the axis x tilt hull of the pieces A168's
own normalise left alive; that hull contains every surviving pose, so it is a sound (and tighter
than `src`) hypothesis, and it is the SAME starting point for both runs.
"""
import argparse
import json
import os
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, "..", ".."))
RES = os.path.abspath(os.path.join(HERE, "..", "results"))
sys.path.insert(0, os.path.join(ATT, "A171-multibox-invariant", "code"))

import multibox as MB                                          # noqa: E402
from caselp import Box                                         # noqa: E402

A168_RES = os.path.join(ATT, "A168-cascade-fable", "results")
CORNER_OF = {"S1": ("D", "TR"), "S2": ("D", "TR")}


def alive_nodes(cell, step):
    T = json.load(open(os.path.join(A168_RES, "tree_%s.json" % cell), encoding="utf-8"))
    out = []
    for path, nd in T["nodes"].items():
        if nd.get("step") != step:
            continue
        if not str(nd.get("verdict", "")).startswith("ALIVE"):
            continue
        roles = nd.get("roles") or {}
        if not roles or any(r.get("box") is None for r in roles.values()):
            continue
        out.append((path, {k: Box(*r["box"]) for k, r in roles.items()},
                    {k: r.get("kept") for k, r in roles.items()}))
    return out


def run_one(boxes, corners, nsub, refine, max_iter, lonely_refine):
    t0 = time.time()
    nd = MB.Node({k: v for k, v in boxes.items()}, name="A173")
    try:
        nd.normalise(nsub=nsub, refine=refine, max_iter=max_iter, corners=corners,
                     lonely_refine=lonely_refine)
    except MB.EmptyBox as e:
        return dict(kill=True, kill_box=e.name, kill_detail=e.detail,
                    seconds=round(time.time() - t0, 2))
    rep = nd.assert_invariant(raise_on_fail=False, sample=1500)
    out = dict(kill=False, seconds=round(time.time() - t0, 2),
               passes=nd.stats.get("passes", 0), invariant=bool(rep["ok"]),
               kept={k: round(v, 6) for k, v in nd.kept().items()},
               k_area={k: round(b.pc.area(), 6) for k, b in nd.boxes.items()},
               axis_a={k: (round(float(b.core.a), 6) if b.core is not None else None)
                       for k, b in nd.boxes.items()},
               n_pieces={k: len(b.pieces) for k, b in nd.boxes.items()},
               failures=[f["check"] for f in rep["failures"]])
    if corners:
        out["lonely_removed"] = {k: round(float(getattr(b, "lonely_removed", 0.0)), 8)
                                 for k, b in nd.boxes.items()}
        out["lonely"] = {k: [dict(stage=r["stage"], removed=round(r["removed"], 8),
                                  dropped=r["dropped_pieces"], slabs=r["stats"]["slabs"])
                             for r in v if r["removed"] > 0 or r["dropped_pieces"]]
                         for k, v in nd.lonely.items()}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", default="l1_104,l1_153")
    ap.add_argument("--steps", default="S1,S2")
    ap.add_argument("--nsub", type=int, default=4)
    ap.add_argument("--refine", type=int, default=1)
    ap.add_argument("--max-iter", type=int, default=6)
    ap.add_argument("--lonely-refine", type=int, default=1)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--shard", default="0/1", help="k/n -- take every n-th node starting at k")
    ap.add_argument("--reverse", action="store_true",
                    help="walk the node list backwards (a second, concurrent process)")
    ap.add_argument("--out", default=os.path.join(RES, "measure173.jsonl"))
    a = ap.parse_args()
    os.makedirs(RES, exist_ok=True)
    sk, sn = (int(v) for v in a.shard.split("/"))

    def scan_done():
        """every (cell, step, path) already written by ANY shard.  Re-read BEFORE EVERY NODE so two
        concurrent processes cannot repeat each other's work: a node costs ~30 s, this costs ~1 ms,
        and a node is written (and flushed) the moment it finishes."""
        d = set()
        for fn in sorted(os.listdir(RES)):
            if not (fn.startswith("measure173") and fn.endswith(".jsonl")):
                continue
            for line in open(os.path.join(RES, fn), encoding="utf-8"):
                if line.strip():
                    r = json.loads(line)
                    d.add((r["cell"], r["step"], r["path"]))
        return d

    fh = open(a.out, "a", encoding="utf-8")
    t00 = time.time()
    n = 0
    for cell in a.cells.split(","):
        for step in a.steps.split(","):
            todo = list(enumerate(alive_nodes(cell, step)))
            if a.reverse:
                todo.reverse()
            for i, (path, boxes, a168_kept) in todo:
                if i % sn != sk:
                    continue
                if (cell, step, path) in scan_done():
                    continue
                if a.limit and n >= a.limit:
                    break
                name, corner = CORNER_OF[step]
                if name not in boxes:
                    continue
                rec = dict(cell=cell, step=step, path=path, a168_kept=a168_kept,
                           boxes={k: [v.x0, v.x1, v.y0, v.y1, v.th0, v.th1]
                                  for k, v in boxes.items()},
                           corner=corner, c=float(MB.C_WIDEN))
                for tag, cs in (("base", None), ("lonely", {name: (corner, MB.C_WIDEN)})):
                    try:
                        rec[tag] = run_one(boxes, cs, a.nsub, a.refine, a.max_iter,
                                           a.lonely_refine)
                    except Exception as e:                       # noqa: BLE001
                        rec[tag] = dict(error=repr(e), tb=traceback.format_exc()[-800:])
                fh.write(json.dumps(rec) + "\n")
                fh.flush()
                n += 1
                b, l = rec.get("base", {}), rec.get("lonely", {})
                print(f"{cell} {step} {path}: base D={b.get('kept', {}).get('D')} "
                      f"-> lonely D={l.get('kept', {}).get('D')} "
                      f"kill={l.get('kill')} ({b.get('seconds')}+{l.get('seconds')} s)",
                      flush=True)
    fh.close()
    print(f"{n} nodes in {time.time() - t00:.0f} s -> {a.out}", flush=True)


if __name__ == "__main__":
    main()
