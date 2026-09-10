"""A197 driver: the forced-cell PAIR test at nsub 8 / refine 4 over the alive a57v4 pages.

    python run197.py [--only id,id] [--skip id,id] [--shard k/n] [--wall 900] [--redo]

Writes results/slotpair197.jsonl (one row per page, resumable) and certs/sp197_<nid>.json for every
DEAD page (the library's clip traces and EmptyBox reasons at the pair leaf).
<= 1 process per invocation; BelowNormal + affinity are set by the launcher.
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
sys.path.insert(0, os.path.join(ROOT, "attempts", "A178-gallery-geometry", "code"))

import geo178 as G                                              # noqa: E402  READ-ONLY (A178)
import pair197 as P                                             # noqa: E402

GALDIR = os.path.join(ROOT, "docs", "shadows", "a57v4")


def pages():
    out = []
    for r in csv.DictReader(open(os.path.join(GALDIR, "review_a57v4.csv"), encoding="utf-8")):
        if os.path.exists(os.path.join(GALDIR, "killed", r["file"])):
            continue
        out.append(dict(gallery="a57v4", nid=r["node"], camp=r["camp"], cls=r["cls"],
                        record=r["record"].replace("\\", "/"), file=r["file"]))
    return out


def done_ids(path):
    ids = set()
    if os.path.exists(path):
        for l in open(path, encoding="utf-8"):
            if l.strip():
                ids.add(json.loads(l)["nid"])
    return ids


def area(b):
    return max(0.0, b[1] - b[0]) * max(0.0, b[3] - b[2])


def run_page(p, a, log):
    t0 = time.time()
    deadline = t0 + a.wall - 25
    rec = G.load_record(p["record"])
    cls = G.class_of_record(rec)
    s = rec["s"]
    base = G.base_roles(rec)
    hnames = [k for k in base if k.startswith("H")]
    pinroles = {k: v for k, v in base.items() if k.startswith("P")}
    row = dict(nid=p["nid"], gallery=p["gallery"], camp=p["camp"], cls=cls, record=p["record"],
               budget=rec["budget"], n_pins=len(rec["pins"]), n_H=len(rec["H"]),
               nsub=a.nsub, refine=a.refine, base_nsub=a.base_nsub, base_refine=a.base_refine,
               of_nsub=a.of_nsub, of_refine=a.of_refine, side=P.SIDE, max_cells=a.max_cells,
               max_pairs=a.max_pairs, wall=a.wall, when=time.strftime("%Y-%m-%d %H:%M:%S"))

    nd0, info0 = G.run_node(base, nsub=a.base_nsub, refine=a.base_refine, label="base")
    row["base"] = dict(dead=info0.get("dead"), seconds=info0["seconds"], kept=info0.get("kept"))
    if info0["dead"]:
        row.update(verdict="DEAD", leaf="base node EmptyBox(%s) at nsub %d / refine %d"
                   % (info0["dead"], a.nsub, a.refine), kill_cell=None,
                   cert_detail=info0.get("cert"), seconds=round(time.time() - t0, 1))
        return row
    hull = {k: G.hull_of(nd0, k) for k in hnames}
    row["H_hull_base"] = hull
    items = G.forced_items(cls, rec)
    row["forced"] = [dict(cell=it["cell"], corner=it["is_corner"], extension=it.get("extension"),
                          wbox=list(it["wbox"]), window=list(it["window"])) for it in items]
    log("  %s (%s): %d forced cells, H hull %s" % (p["nid"], cls, len(items),
        " ".join("%s=[%.3f,%.3f]x[%.3f,%.3f]" % (k, v[0], v[1], v[2], v[3]) for k, v in hull.items())))

    # ---- phase 1: one free meeter at every forced cell (cheap, and a kill on its own)
    ones = []
    timed_out = False
    try:
        for it in items:
            nd, info, hb, tag = P.one_free(pinroles, hnames, hull, it, nsub=a.of_nsub,
                                           refine=a.of_refine, deadline=deadline, label=p["nid"])
            if info["dead"]:
                log("    %s one-free DEAD (%s)" % (it["cell"], info["dead"]))
                row.update(verdict="DEAD", kill_cell=it["cell"],
                           leaf="no FREE meeter of the widened box at %s: EmptyBox(%s)"
                                % (it["cell"], info["dead"]),
                           cert_detail=info.get("cert"),
                           subcases=[dict(cell=it["cell"], case="one-free", dead=info["dead"],
                                          seconds=info["seconds"])],
                           seconds=round(time.time() - t0, 1))
                return row
            ones.append((area(hb), it, hb, tag, info))
            log("    %s one-free alive: B hull %.3f x %.3f (kept %.4g)"
                % (it["cell"], hb[1] - hb[0], hb[3] - hb[2], info["kept"]["B_" + tag]))
    except P.Timeout as e:
        timed_out = True
        log("    WALL during one-free (%s)" % e)

    # ---- phase 2: the pair test, most squeezed cell first
    ones.sort(key=lambda z: z[0])
    tables = []
    if not timed_out:
        try:
            for (_, it, hb, tag, info) in ones:
                r = P.pair_test(pinroles, hnames, hull, it, info, hb, tag, s, nsub=a.nsub,
                                refine=a.refine, max_cells=a.max_cells, max_pairs=a.max_pairs,
                                deadline=deadline, log=log, label=p["nid"],
                                want_witness=not a.no_witness)
                tables.append(dict(cell=it["cell"], corner=it["is_corner"], alive=r["alive"],
                                   caps=r["caps"], subcases=r["subcases"], hull_B=r["hull_B"],
                                   witness=r["witness"], seconds=r["seconds"], leaf=r.get("leaf")))
                if not r["alive"]:
                    row.update(verdict="DEAD", kill_cell=it["cell"], leaf=r["leaf"],
                               subcases=tables, seconds=round(time.time() - t0, 1))
                    return row
        except P.Timeout as e:
            timed_out = True
            log("    WALL during pair test (%s)" % e)

    row.update(verdict="ALIVE", kill_cell=None,
               leaf=("wall %ds reached: pair test incomplete" % a.wall) if timed_out else None,
               timed_out=timed_out, subcases=tables,
               open_residue=[dict(cell=t["cell"], caps=t["caps"],
                                  witness=t["witness"], hull_B=t["hull_B"]) for t in tables],
               seconds=round(time.time() - t0, 1))
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--skip", default="k5_16_interior_Y0491")
    ap.add_argument("--nsub", type=int, default=8)          # the PAIR nodes: the ones that decide
    ap.add_argument("--refine", type=int, default=4)
    ap.add_argument("--base-nsub", dest="base_nsub", type=int, default=4)
    ap.add_argument("--base-refine", dest="base_refine", type=int, default=2)
    ap.add_argument("--of-nsub", dest="of_nsub", type=int, default=4)
    ap.add_argument("--of-refine", dest="of_refine", type=int, default=2)
    ap.add_argument("--max-cells", dest="max_cells", type=int, default=24)
    ap.add_argument("--max-pairs", dest="max_pairs", type=int, default=400)
    ap.add_argument("--wall", type=int, default=900)
    ap.add_argument("--shard", default="1/1")
    ap.add_argument("--redo", action="store_true")
    ap.add_argument("--no-witness", dest="no_witness", action="store_true")
    ap.add_argument("--out", default=os.path.join(RES, "slotpair197.jsonl"))
    a = ap.parse_args()
    os.makedirs(RES, exist_ok=True)
    os.makedirs(CERTS, exist_ok=True)
    k, n = (int(v) for v in a.shard.split("/"))
    only = set(v for v in a.only.split(",") if v)
    skip = set(v for v in a.skip.split(",") if v)
    P_ = [p for p in pages() if p["nid"] not in skip]
    if only:
        P_ = [p for p in P_ if p["nid"] in only]
    else:
        P_ = [p for i, p in enumerate(P_) if i % n == (k - 1)]
    done = set() if a.redo else done_ids(a.out)
    log = lambda s_: print(s_, flush=True)                       # noqa: E731
    for p in P_:
        if p["nid"] in done:
            continue
        print("== %s (%s)" % (p["nid"], p["cls"]), flush=True)
        try:
            row = run_page(p, a, log)
        except Exception as ex:                                  # noqa: BLE001
            import traceback
            traceback.print_exc()
            row = dict(nid=p["nid"], gallery=p["gallery"], camp=p["camp"], cls=p["cls"],
                       record=p["record"], verdict="ERROR", leaf=str(ex)[:300],
                       when=time.strftime("%Y-%m-%d %H:%M:%S"))
        if row.get("verdict") == "DEAD":
            cp = os.path.join(CERTS, "sp197_%s.json" % p["nid"])
            json.dump(dict(nid=p["nid"], cls=row.get("cls"), record=p["record"],
                           leaf=row.get("leaf"), kill_cell=row.get("kill_cell"),
                           theorem="docs/proofs/forced_corners.md Theorem FC + Corollaries "
                                   "FC-slot / FC-count; sideband.md Lemma A1",
                           library="attempts/A171-multibox-invariant/code/multibox.py",
                           settings=dict(nsub=row.get("nsub"), refine=row.get("refine"),
                                         side=P.SIDE, max_cells=row.get("max_cells"),
                                         max_pairs=row.get("max_pairs")),
                           note="[C: library geometry; the frozen verifier is not involved]",
                           base=row.get("base"), forced=row.get("forced"),
                           cert_detail=row.get("cert_detail"), subcases=row.get("subcases")),
                      open(cp, "w", encoding="utf-8"), indent=1)
            row["cert"] = os.path.relpath(cp, ROOT).replace("\\", "/")
        with open(a.out, "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
        print("== %s: %s %s (%.0f s)" % (p["nid"], row.get("verdict"), row.get("leaf") or "",
                                         row.get("seconds") or 0), flush=True)


if __name__ == "__main__":
    main()
