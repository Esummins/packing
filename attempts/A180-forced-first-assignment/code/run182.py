"""A182 driver: the resumable forced-first assignment search over gallery pages (successor of run180).

    python run182.py --only c0_Y1033 --capture --max-nodes 600 --deadline 7200 --lp 1
    python run182.py --gallery a57v4 --skip c0_Y1033 --max-nodes 150 --deadline 1200 --shard 1/2

Every multibox node goes to results/journal/<nid>.jsonl as it completes (journal182); a re-run of the
same page REPLAYS the journal and continues where the crash hit.  Per page one row is appended to
results/assign182.jsonl (the LAST row per nid is the verdict; UNDECIDED rows are re-run unless
--keep-undecided), results/trees/<nid>.json (tree + every node's record) and, with --capture, the
tree nodes' pieces for fig182.  ONE process per invocation; the LP's frozen verifier is its only child.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RES = os.path.abspath(os.path.join(HERE, "..", "results"))
sys.path.insert(0, HERE)
import assign182 as A2                                           # noqa: E402
import journal182 as J                                           # noqa: E402
import run180 as R                                               # noqa: E402  (A180: pages, summarise, kill_cert)
import geo178 as G                                               # noqa: E402  READ-ONLY (A178)


def last_rows(path):
    out = {}
    if os.path.exists(path):
        for l in open(path, encoding="utf-8"):
            if l.strip():
                try:
                    d = json.loads(l)
                except ValueError:
                    continue
                out[d["nid"]] = d
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--skip", default="")
    ap.add_argument("--gallery", default="a57v4")
    ap.add_argument("--nsub", type=int, default=4)
    ap.add_argument("--refine", type=int, default=2)
    ap.add_argument("--sharp", type=int, default=1)
    ap.add_argument("--chords", type=int, default=1)
    ap.add_argument("--lanes", type=int, default=1)
    ap.add_argument("--lane-s", type=float, default=30.0)
    ap.add_argument("--max-nodes", type=int, default=150)
    ap.add_argument("--deadline", type=float, default=1200.0)
    ap.add_argument("--wall", type=float, default=1500.0)
    ap.add_argument("--lp", type=int, default=1)
    ap.add_argument("--lp-cap", type=float, default=600.0)
    ap.add_argument("--max-lp", type=int, default=4)
    ap.add_argument("--shard", default="1/1")
    ap.add_argument("--redo", action="store_true")
    ap.add_argument("--keep-undecided", action="store_true")
    ap.add_argument("--capture", action="store_true")
    ap.add_argument("--refine-opts", type=int, default=1)
    ap.add_argument("--side", type=float, default=0.36)
    ap.add_argument("--max-combos", type=int, default=100)
    ap.add_argument("--commit", type=int, default=1)
    ap.add_argument("--out", default=os.path.join(RES, "assign182.jsonl"))
    a = ap.parse_args()
    os.makedirs(os.path.join(RES, "trees"), exist_ok=True)
    k, n = (int(v) for v in a.shard.split("/"))
    only = set(v for v in a.only.split(",") if v)
    skip = set(v for v in a.skip.split(",") if v)
    P = [p for i, p in enumerate(R.pages(a.gallery)) if i % n == (k - 1)]
    if only:
        P = [p for p in P if p["nid"] in only]
    done = {} if a.redo else last_rows(a.out)
    for p in P:
        prev = done.get(p["nid"])
        if p["nid"] in skip or (prev is not None and (a.keep_undecided or prev.get("verdict") in ("DEAD", "ALIVE"))):
            continue
        t0 = time.time()
        print("== %s (%s, %s)%s" % (p["nid"], p["gallery"], p["cls"], "  [resume: previous %s]" % prev["verdict"] if prev else ""), flush=True)
        rec = G.load_record(p["record"])
        cls = G.class_of_record(rec)
        G.CAPTURE = [] if a.capture else None
        leaf = None
        if a.lp:
            import lp180
            leaf = lp180.make_leaf(p["record"], cap=a.lp_cap, log=lambda s: print(s, flush=True), max_lp=a.max_lp)
        jn = J.Journal(p["nid"], wall=a.wall)
        print("   journal: %d nodes, %d subtrees, %d lanes on disk" % (len(jn.nodes), len(jn.subtrees), len(jn.lanes)), flush=True)
        S = A2.Search(rec, cls, jn, sharp=a.sharp, chords=a.chords, lanes=a.lanes, lane_s=a.lane_s,
                      commit_branches=a.commit, nsub=a.nsub, refine=a.refine, log=lambda s: print(s, flush=True),
                      max_nodes=a.max_nodes, deadline=a.deadline, leaf=leaf, refine_opts=a.refine_opts,
                      side=a.side, max_combos=a.max_combos)
        try:
            r = S.run()
        except Exception as ex:                                  # noqa: BLE001
            import traceback
            traceback.print_exc()
            r = dict(verdict="ERROR", leaf=str(ex)[:200], tree=None)
        jn.idle()
        row = dict(nid=p["nid"], gallery=p["gallery"], camp=p["camp"], cls=cls, record=p["record"],
                   budget=rec["budget"], n_pins=len(rec["pins"]), n_H=len(rec["H"]),
                   forced=[dict(cell=c, corner=it["is_corner"], extension=it.get("extension")) for c, it in S.items.items()],
                   verdict=r["verdict"], leaf=r.get("leaf"), n_nodes=S.n_nodes, n_fresh=S.n_fresh,
                   n_replayed=jn.n_replayed, compute_s=round(S.compute_s, 1), summary=R.summarise(r.get("tree")),
                   seconds=round(time.time() - t0, 1), nsub=a.nsub, refine=a.refine, sharp=a.sharp, chords=a.chords,
                   lanes=a.lanes, max_nodes=a.max_nodes, deadline=a.deadline, when=time.strftime("%Y-%m-%d %H:%M:%S"),
                   journal=os.path.relpath(jn.path, ROOT).replace("\\", "/"))
        row["cert"] = (R.kill_cert(r.get("tree"), p["nid"]).replace("trees/", "trees/") if r["verdict"] == "DEAD" else None)
        tp = os.path.join(RES, "trees", "%s.json" % p["nid"])
        json.dump(dict(row=row, tree=r.get("tree"), steps=S.steps), open(tp, "w", encoding="utf-8"), indent=0)
        if a.capture:
            json.dump(dict(nid=p["nid"], cls=cls, record=p["record"], pins=rec["pins"], H=rec["H"],
                           forced=row["forced"], nodes=G.CAPTURE, verdict=r["verdict"], leaf=r.get("leaf")),
                      open(os.path.join(RES, "capture182_%s.json" % p["nid"]), "w", encoding="utf-8"))
        with open(a.out, "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
        if a.commit:
            J.git_commit([a.out, tp, jn.path], "A182: %s %s (%d nodes, %d fresh, %.0f s)" % (
                p["nid"], r["verdict"], S.n_nodes, S.n_fresh, time.time() - t0))
        print("== %s: %s %s (%d nodes, %d fresh, %.0f s)" % (p["nid"], r["verdict"], r.get("leaf") or "", S.n_nodes,
                                                             S.n_fresh, time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
