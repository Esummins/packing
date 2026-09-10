"""A191 -- the S3 children of the S2 SURVIVORS at the COARSE setting (nsub 4 / refine 2, A184 E1), parent-seeded
by construction (the inherited roles ARE the parent's recorded fixed point; B = the child's cover box, A168's
`src` box: a sound superset of A168's clipped B pieces), the polygon + lonely clip to the fixed point
(polyclip175.make_node, 4/2 only -- no 8/3 pass), then the same leaf as S2 (node191: corner no-room, windows +
guard-line LP, v5).  Records results/run191_<cell>_S3coarse.jsonl (resumable), with the geometry seconds and the
LP seconds separately -- the S3 price is measured here.

    python s3_191.py --cell l1_104 [--parents auto|NODE,NODE] [--per-parent 2] [--shard k/n] [--cap 300]
"""
import argparse
import glob
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
RES = os.path.join(BASE, "results")
sys.path.insert(0, HERE)
import prio191                                                   # noqa: E402,F401
import node191 as ND                                             # noqa: E402
import run191 as RUN                                             # noqa: E402
import renorm181 as R8                                           # noqa: E402  (A181, read-only)
import roles168 as R                                             # noqa: E402  (A168, read-only)
import polyclip175 as PX                                         # noqa: E402  (A175, read-only)
import lp168 as L                                                # noqa: E402  (A168, read-only)
from caselp import Box                                           # noqa: E402  (A57, read-only)


def s3_boxes(cell):
    out = {}
    for f in sorted(glob.glob(os.path.join(RES, "s3_boxes_%s_s*of3.json" % cell))):
        out.update(json.load(open(f, encoding="utf-8")))
    return out


def s2_survivors(cell):
    """S2 nodes ALIVE in the A183 record and not killed by run191 so far (auto)."""
    alive = set(n for n, _ in RUN.alive_nodes(cell, "S2"))
    dead = set()
    for f in glob.glob(os.path.join(RES, "run191_%s_S2*.jsonl" % cell)):
        for ln in open(f, encoding="utf-8"):
            try:
                r = json.loads(ln)
            except Exception:                                    # noqa: BLE001
                continue
            if str(r.get("verdict", "")).startswith("DEAD"):
                dead.add(r.get("record_node"))
    return sorted(alive - dead)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", default="l1_104")
    ap.add_argument("--parents", default="auto")
    ap.add_argument("--per-parent", type=int, default=2)
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--cap", type=float, default=300.0)
    ap.add_argument("--wall", type=float, default=1500.0)
    ap.add_argument("--lines", type=int, default=8)
    ap.add_argument("--v1", type=int, default=1)
    ap.add_argument("--geo", type=int, default=1)
    ap.add_argument("--geo-cap", type=float, default=150.0)
    ap.add_argument("--cert", type=int, default=1)
    ap.add_argument("--rounds", type=int, default=2)
    ap.add_argument("--lp", type=int, default=1)
    ap.add_argument("--max-nodes", type=int, default=10 ** 6)
    a = ap.parse_args()
    k, n = (int(x) for x in a.shard.split("/"))
    out = os.path.join(RES, "run191_%s_S3coarse.jsonl" % a.cell)
    recs = R8.load_side(a.cell)
    boxes = s3_boxes(a.cell)
    parents = s2_survivors(a.cell) if a.parents == "auto" else [x.strip() for x in a.parents.split(",") if x.strip()]
    jobs = []
    for p in parents:
        kids = sorted((c for c, d in boxes.items() if d["parent"] == p and d.get("B_src")),
                      key=lambda c: int(c.rsplit("B", 1)[1]))
        # spread: the first, the middle, the last ... (A184 sampled evenly spaced boxes)
        if len(kids) > a.per_parent:
            step = max(1, len(kids) // a.per_parent)
            kids = kids[::step][:a.per_parent]
        jobs += [(p, c) for c in kids]
    jobs = [j for i, j in enumerate(jobs) if i % n == k]
    done = set()
    if os.path.exists(out):
        for ln in open(out, encoding="utf-8"):
            try:
                r = json.loads(ln)
                if not str(r.get("verdict", "")).startswith(("[P]", "ERROR")):
                    done.add(r["record_node"])
            except Exception:                                    # noqa: BLE001
                pass
    jobs = [j for j in jobs if j[1] not in done][:a.max_nodes]
    print("s3_191 %s shard %s: %d children under %d parents (%d done before)" % (a.cell, a.shard, len(jobs), len(parents), len(done)), flush=True)
    warm_cell = None
    for p, c in jobs:
        if os.path.exists(os.path.join(BASE, "PAUSE")):
            break
        t0 = time.time()
        par = recs[p]
        roles = R.roles_from_json(par["roles"])
        bsrc = boxes[c]["B_src"]
        roles.append(R.Role.from_box("B", Box(*bsrc), nsub=4))
        rec = dict(node=RUN.tag_of(a.cell, c), record_node=c, parent=p, cell=a.cell, step="S3", setting="nsub 4 / refine 2 (coarse only, parent-seeded)",
                   a168_verdict=boxes[c]["verdict"], a168_kept=boxes[c]["kept"], B_src=bsrc, when=time.strftime("%Y-%m-%d %H:%M"))
        try:
            rr, rep = PX.make_node(roles, refine=2, lonely=True)
        except Exception as e:                                   # noqa: BLE001
            rr, rep = None, dict(dead="ERROR %r" % (e,), leaf="ERROR")
        rec.update(clip_s=round(time.time() - t0, 1), kept=rep.get("kept"), n_pieces=rep.get("n_pieces"), passes=rep.get("passes"),
                   k_area=rep.get("k_area"))
        if rr is None:
            rec.update(verdict="DEAD(C, %s)" % str(rep.get("dead"))[:200], leaf=rep.get("leaf"), wall_s=round(time.time() - t0, 1))
            RUN.emit(out, rec)
            continue
        rec["roles_fixed"] = R.roles_json(rr)
        if not a.lp:
            rec.update(verdict="ALIVE(geometry, 4/2; LP not run)", wall_s=round(time.time() - t0, 1))
            RUN.emit(out, rec)
            continue
        if warm_cell is None:
            warm_cell = L.load_warm(a.cell)
        warm = dict(atoms=list(warm_cell["atoms"]), rows=list(warm_cell["rows"]))
        try:
            lrec = ND.run_node(rec["node"], a.cell, "S3", rr, warm, a, t0 + a.wall)
        except Exception as e:                                   # noqa: BLE001
            lrec = dict(error=repr(e)[:300], verdict="ERROR")
        lrec.pop("node", None)
        rec.update(lrec)
        rec["wall_s"] = round(time.time() - t0, 1)
        RUN.emit(out, rec)


if __name__ == "__main__":
    main()
