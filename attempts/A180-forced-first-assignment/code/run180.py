"""A180 driver: the forced-first assignment search over gallery pages.

    python run180.py --only c0_Y1033 --capture --max-nodes 400 --deadline 5400 --lp 1
    python run180.py --gallery a57v4 --max-nodes 80 --deadline 1200 --shard 1/1

Writes results/assign180.jsonl (one line per page; resumable: pages already present are skipped
unless --redo), results/trees/<nid>.json (the full search tree with every multibox node's record)
and results/capture180_<nid>.json (--capture: every node's pieces/K' for fig180).  ONE process per
invocation; the LP's frozen verifier is its only child.
"""
import argparse
import csv
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RES = os.path.abspath(os.path.join(HERE, "..", "results"))
sys.path.insert(0, HERE)
import assign180 as A                                            # noqa: E402
import geo178 as G                                               # noqa: E402  READ-ONLY (A178)

GAL = {"a57v4": os.path.join(ROOT, "docs", "shadows", "a57v4"), "k0v4": os.path.join(ROOT, "docs", "shadows", "k0v4")}
A178_JSONL = os.path.join(ROOT, "attempts", "A178-gallery-geometry", "results", "geopass178.jsonl")


def a178_killed():
    dead = set()
    if os.path.exists(A178_JSONL):
        for l in open(A178_JSONL, encoding="utf-8"):
            if l.strip():
                d = json.loads(l)
                if d.get("verdict") == "DEAD":
                    dead.add(d["nid"])
    return dead


def pages(which):
    out = []
    for g, d in GAL.items():
        if which not in ("all", g):
            continue
        for r in csv.DictReader(open(os.path.join(d, "review_%s.csv" % g), encoding="utf-8")):
            if os.path.exists(os.path.join(d, "killed", r["file"])):
                continue
            out.append(dict(gallery=g, nid=r["node"], camp=r["camp"], cls=r["cls"],
                            record=r["record"].replace("\\", "/"), budget=r.get("budget")))
    return out


def done_ids(path):
    ids = set()
    if os.path.exists(path):
        for l in open(path, encoding="utf-8"):
            if l.strip():
                ids.add(json.loads(l)["nid"])
    return ids


def summarise(tree):
    """count leaves by verdict and the forced/branched steps."""
    c = dict(dead=0, alive=0, undecided=0, branches=0, lp=0)

    def walk(t):
        if t is None:
            return
        if "children" in t:
            c["branches"] += 1
            for k in t["children"]:
                walk(k)
        else:
            v = t.get("verdict", "")
            c["dead" if v == "DEAD" else ("alive" if v.startswith("ALIVE") else "undecided")] += 1
            if t.get("lp"):
                c["lp"] += 1
    walk(tree)
    return c


def kill_cert(tree, nid):
    """the certificate of a DEAD page: the LP certificate(s) if any leaf was killed by the LP, else the
    search tree itself (every leaf a multibox pair leaf, with the library's clip traces)."""
    certs = []

    def walk(t):
        if t is None:
            return
        for k in t.get("children", []):
            walk(k)
        if (t.get("lp") or {}).get("cert") and t["lp"].get("certified") == "PASS":
            certs.append(t["lp"]["cert"])
    walk(tree)
    tp = "attempts/A180-forced-first-assignment/results/trees/%s.json" % nid
    return (";".join(certs) + ";" + tp) if certs else tp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--skip", default="")
    ap.add_argument("--gallery", default="a57v4")
    ap.add_argument("--nsub", type=int, default=4)
    ap.add_argument("--refine", type=int, default=2)
    ap.add_argument("--max-nodes", type=int, default=80)
    ap.add_argument("--deadline", type=float, default=1200.0)
    ap.add_argument("--lp", type=int, default=1)
    ap.add_argument("--lp-cap", type=float, default=600.0)
    ap.add_argument("--max-lp", type=int, default=4)
    ap.add_argument("--shard", default="1/1")
    ap.add_argument("--redo", action="store_true")
    ap.add_argument("--capture", action="store_true")
    ap.add_argument("--refine-opts", type=int, default=1)
    ap.add_argument("--side", type=float, default=0.36)
    ap.add_argument("--max-combos", type=int, default=100)
    ap.add_argument("--out", default=os.path.join(RES, "assign180.jsonl"))
    a = ap.parse_args()
    os.makedirs(os.path.join(RES, "trees"), exist_ok=True)
    k, n = (int(v) for v in a.shard.split("/"))
    only = set(v for v in a.only.split(",") if v)
    skip = set(v for v in a.skip.split(",") if v)
    P = [p for i, p in enumerate(pages(a.gallery)) if i % n == (k - 1)]
    if only:
        P = [p for p in P if p["nid"] in only]
    done = set() if a.redo else done_ids(a.out)
    dead178 = a178_killed()
    for p in P:
        if p["nid"] in done or p["nid"] in skip or (p["nid"] in dead178 and not only):
            continue
        t0 = time.time()
        print("== %s (%s, %s)" % (p["nid"], p["gallery"], p["cls"]), flush=True)
        rec = G.load_record(p["record"])
        cls = G.class_of_record(rec)
        G.CAPTURE = [] if a.capture else None
        leaf = None
        if a.lp:
            import lp180
            leaf = lp180.make_leaf(p["record"], cap=a.lp_cap, log=lambda s: print(s, flush=True), max_lp=a.max_lp)
        S = A.Search(rec, cls, nsub=a.nsub, refine=a.refine, log=lambda s: print(s, flush=True),
                     max_nodes=a.max_nodes, deadline=a.deadline, leaf=leaf, refine_opts=a.refine_opts,
                     side=a.side, max_combos=a.max_combos)
        try:
            r = S.run()
        except Exception as ex:                                  # noqa: BLE001
            import traceback
            traceback.print_exc()
            r = dict(verdict="ERROR", leaf=str(ex)[:200], tree=None)
        row = dict(nid=p["nid"], gallery=p["gallery"], camp=p["camp"], cls=cls, record=p["record"],
                   budget=rec["budget"], n_pins=len(rec["pins"]), n_H=len(rec["H"]),
                   forced=[dict(cell=c, corner=it["is_corner"], extension=it.get("extension")) for c, it in S.items.items()],
                   verdict=r["verdict"], leaf=r.get("leaf"), n_nodes=S.n_nodes, summary=summarise(r.get("tree")),
                   seconds=round(time.time() - t0, 1), nsub=a.nsub, refine=a.refine, max_nodes=a.max_nodes,
                   deadline=a.deadline, when=time.strftime("%Y-%m-%d %H:%M:%S"))
        row["cert"] = kill_cert(r.get("tree"), p["nid"]) if r["verdict"] == "DEAD" else None
        json.dump(dict(row=row, tree=r.get("tree"), steps=S.steps),
                  open(os.path.join(RES, "trees", "%s.json" % p["nid"]), "w", encoding="utf-8"), indent=0)
        if a.capture:
            json.dump(dict(nid=p["nid"], cls=cls, record=p["record"], pins=rec["pins"], H=rec["H"],
                           forced=row["forced"], nodes=G.CAPTURE, steps=S.steps, tree=r.get("tree"),
                           verdict=r["verdict"], leaf=r.get("leaf")),
                      open(os.path.join(RES, "capture180_%s.json" % p["nid"]), "w", encoding="utf-8"))
        with open(a.out, "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
        print("== %s: %s %s (%d nodes, %.0f s)" % (p["nid"], r["verdict"], r.get("leaf") or "", S.n_nodes,
                                                   time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
