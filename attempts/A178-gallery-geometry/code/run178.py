"""A178 driver: the geometry cascade over the alive a57v4 pages and the k0v4 pages.

    python run178.py [--only id,id] [--gallery a57v4|k0v4|all] [--nsub 4] [--refine 2] [--shard k/n]

Writes results/geopass178.jsonl (one line per page, resumable: pages already present are skipped
unless --redo) and certs/geo178_<id>.json for every DEAD page (the library's clip traces at the
pair leaf, per case).  <= 1 process per invocation; BelowNormal + affinity are set by the launcher.
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
CERTS = os.path.abspath(os.path.join(HERE, "..", "certs"))
sys.path.insert(0, HERE)
import geo178 as G                                              # noqa: E402

GAL = {"a57v4": os.path.join(ROOT, "docs", "shadows", "a57v4"),
       "k0v4": os.path.join(ROOT, "docs", "shadows", "k0v4")}


def pages(which):
    out = []
    for g, d in GAL.items():
        if which not in ("all", g):
            continue
        csvp = os.path.join(d, "review_%s.csv" % g)
        for r in csv.DictReader(open(csvp, encoding="utf-8")):
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--gallery", default="all")
    ap.add_argument("--nsub", type=int, default=4)
    ap.add_argument("--refine", type=int, default=2)
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--shard", default="1/1")
    ap.add_argument("--redo", action="store_true")
    ap.add_argument("--capture", action="store_true")
    ap.add_argument("--merge", action="store_true")
    ap.add_argument("--sharp", action="store_true")
    ap.add_argument("--out", default=os.path.join(RES, "geopass178.jsonl"))
    a = ap.parse_args()
    os.makedirs(RES, exist_ok=True)
    os.makedirs(CERTS, exist_ok=True)
    k, n = (int(v) for v in a.shard.split("/"))
    only = set(v for v in a.only.split(",") if v)
    P = pages(a.gallery)
    P = [p for i, p in enumerate(P) if i % n == (k - 1)]
    if only:
        P = [p for p in P if p["nid"] in only]
    done = set() if a.redo else done_ids(a.out)
    for p in P:
        if p["nid"] in done:
            continue
        t0 = time.time()
        print("== %s (%s, %s)" % (p["nid"], p["gallery"], p["cls"]), flush=True)
        rec = G.load_record(p["record"])
        cls = G.class_of_record(rec)
        G.CAPTURE = [] if a.capture else None
        try:
            r = G.cascade(rec, cls, nsub=a.nsub, refine=a.refine, max_rounds=a.rounds,
                          log=lambda s: print(s, flush=True), merge_cases=a.merge, sharp=a.sharp)
        except Exception as ex:                                  # noqa: BLE001
            import traceback
            traceback.print_exc()
            r = dict(verdict="ERROR", leaf=str(ex)[:200], steps=[])
        items = G.forced_items(cls, rec)
        row = dict(nid=p["nid"], gallery=p["gallery"], camp=p["camp"], cls=cls, record=p["record"],
                   budget=rec["budget"], n_pins=len(rec["pins"]), n_H=len(rec["H"]),
                   roles_base=list(G.base_roles(rec)),
                   forced=[dict(cell=it["cell"], corner=it["is_corner"], extension=it.get("extension"),
                                status=it.get("status"), H_misses=it.get("misses")) for it in items],
                   verdict=r["verdict"], leaf=r.get("leaf"),
                   n_steps=len(r["steps"]),
                   base=r["steps"][0]["info"] if r["steps"] else None,
                   cases_alive=r.get("cases_alive"),
                   steps=[dict(step=s.get("step"), case=s.get("case"), cell=s.get("cell"), cells=s.get("cells"),
                               added=s.get("added"), split=s.get("split"),
                               dead=s["info"].get("dead"), seconds=s["info"].get("seconds"),
                               kept=s["info"].get("kept"), k_area=s["info"].get("k_area"),
                               lonely_removed=s["info"].get("lonely_removed"),
                               invariant=s["info"].get("invariant"), passes=s["info"].get("passes"),
                               subcases=s["info"].get("subcases"), leaf=s["info"].get("leaf"))
                          for s in r["steps"]],
                   seconds=round(time.time() - t0, 1), nsub=a.nsub, refine=a.refine,
                   cert=None, when=time.strftime("%Y-%m-%d %H:%M:%S"))
        if r["verdict"] == "DEAD":
            cp = os.path.join(CERTS, "geo178_%s.json" % p["nid"])
            json.dump(dict(nid=p["nid"], cls=cls, record=p["record"], leaf=r["leaf"],
                           library="attempts/A171-multibox-invariant/code/multibox.py",
                           kills=r.get("cert"), steps=row["steps"]),
                      open(cp, "w", encoding="utf-8"), indent=1)
            row["cert"] = os.path.relpath(cp, ROOT).replace("\\", "/")
        if a.capture:
            json.dump(dict(nid=p["nid"], cls=cls, record=p["record"], pins=rec["pins"], H=rec["H"],
                           forced=row["forced"], nodes=G.CAPTURE, verdict=r["verdict"], leaf=r.get("leaf")),
                      open(os.path.join(RES, "capture_%s.json" % p["nid"]), "w", encoding="utf-8"))
        with open(a.out, "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
        print("== %s: %s %s (%.0f s)" % (p["nid"], r["verdict"], r.get("leaf") or "", time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
