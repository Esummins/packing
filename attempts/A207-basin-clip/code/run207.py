"""A207 driver (A206's run206 with the basin clip).  Modes:
   python run207.py leaf <nid> --pad g1 --leaf R.2.3s.1.1.1s --src a206 --tag g1_R.2.3s [--wall 3600]
       the node loaded from an A206 / A205 certificate (load207), the basin clip + A206's tree with Rule NS from there;
   python run207.py tree <nid> --pad g1 [--wall 3600]
       the whole clip tree of the page with the basin clip at every node.
One certificate per page, certs/basinclip207_<nid>.json (runs keyed <pad>_<tag>_<leaf> / <pad>_tree, the basins used under
"basins"); the page docs/residue_map/campaigns/A207-basinclip/basinclip207_<nid>.svg; one slim row per run in
results/basinclip207.jsonl (page, pad, leaf, verdict, which basin, seconds)."""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CERTS = os.path.abspath(os.path.join(HERE, "..", "certs"))
RES = os.path.abspath(os.path.join(HERE, "..", "results", "basinclip207.jsonl"))
sys.path.insert(0, HERE)
import poly204 as P                                            # noqa: E402
import tree206 as N6                                           # noqa: E402
import tree206b as NB                                          # noqa: E402
import tree207 as N7                                           # noqa: E402
import clip207 as C                                            # noqa: E402
import load207                                                 # noqa: E402
import fig207                                                  # noqa: E402
import run206 as R6                                            # noqa: E402  (the copy: save / belownormal / page_doc)

FP, QP, MB = P.FP, P.QP, P.MB
VERIFIER = ("[C: extension certificate + Lemma BASIN + library clip trace] A207 basin clip on A206's clip tree with Rule NS: every non-pin role's "
            "pieces and every anonymous option row minus the basin B_F(p) of each FULL slot p (Lemma BASIN, notes/basin.md; the basin certificate "
            "= the extension class re-solved with the boxed slot square, verified by the frozen A53 / A56 verifiers), then A204's cascade + A205's "
            "clips + Rule NS at every node; DEAD iff every branch DEAD; no verifier clause on the clip tree itself")
N7.install()


def row_of(doc, key, cert):
    d = doc["runs"][key]
    slim = dict(nid=doc["nid"], cls=doc.get("cls"), run=key, pad=d.get("pad"), mode=d.get("mode"), leaf_label=d.get("leaf_label"), source=d.get("source"),
                cfg=d.get("cfg"), lam=d.get("lam"), verdict=d.get("verdict"), leaf=d.get("leaf"), n_nodes=d.get("n_nodes"), n_records=d.get("n_records"),
                max_depth=d.get("max_depth"), alive_leaves=d.get("alive_leaves"), dead_leaves=d.get("dead_leaves"), ns_splits=d.get("ns_splits"),
                killing=d.get("killing"), undecided=d.get("undecided"), seconds=d.get("seconds"), root=d.get("root"), wall=d.get("wall"),
                window_pending=d.get("window_pending"), basins=d.get("basins"), basin_clips=d.get("basin_clips"), verifier=VERIFIER,
                cert=os.path.relpath(cert, ROOT).replace("\\", "/"), when=time.strftime("%Y-%m-%d %H:%M:%S"))
    os.makedirs(os.path.dirname(RES), exist_ok=True)
    with open(RES, "a", encoding="utf-8") as f:
        f.write(json.dumps(slim, default=str) + "\n")
    return slim


def run_one(doc, a, cert, log=print):
    T = FP.Trace(wall=a.wall)
    rec, cls, row = FP.load_page(a.nid)
    basins = C.load_basins(cls, a.pad, QP.PADS[a.pad])
    if not basins:
        raise SystemExit("no certified basin covers the %s window of a %s page (results/basin207.jsonl)" % (a.pad, cls))
    if a.mode == "leaf":
        pg, meta = load207.load_node(a.nid, a.pad, a.leaf, T, src=a.src, tag=a.tag, basins=basins)
        key, root_label, start = "%s_%s%s_%s" % (a.pad, a.src, ("_" + a.tag) if a.tag else "", a.leaf), a.leaf, meta["start"]
    else:
        start = P.load_start(a.nid, a.pad)
        pg = N7.TreePage207(rec, cls, a.nid, T, pad=a.pad, start=start, basins=basins)
        meta = dict(source=start.get("file"), start=start)
        key, root_label = ("%s_tree_%s" % (a.pad, a.only)) if a.only else "%s_tree" % a.pad, "R"
    doc["cls"] = cls
    R6.page_doc(doc, pg)
    doc.setdefault("basins", {})[a.pad] = [C.basin_json(b) for b in basins]
    d = doc["runs"][key] = dict(pad=a.pad, mode=a.mode, leaf_label=(a.leaf if a.mode == "leaf" else None), source=meta.get("source"), lam=float(pg.lam),
                                start=start, loaded=meta.get("loaded"), recorded=meta.get("recorded"), path=meta.get("path"), verdict="RUNNING", nodes=[],
                                basins=[C.basin_json(b) for b in basins], verifier=VERIFIER,
                                cfg=dict(rounds=a.rounds, depth_cap=a.depth, node_cap=a.nodes, wall=a.wall, nsub=4, refine=2, soft_all=N6.SOFT_ALL, max_frac=N6.MAX_FRAC, only=a.only))
    log("== %s %s pad %s [%s]: start %s; basins %s; H %s; forced H %s; roles %s; %d slots" % (
        a.nid, a.mode, a.pad, root_label, meta.get("source"), [(b["cell"], float(b["rc"]), round(float(b.get("r_t_deg") or 0), 2)) for b in basins],
        [round(v, 3) for v in pg.roles[pg.H]], sorted(pg.forced_H), {k: list(v) for k, v in pg.role_slots.items()}, len(pg.slots)))

    def on_node(tree):
        d["nodes"] = tree.nodes
        d.update(n_nodes=tree.n_nodes, max_depth=tree.max_depth, alive_leaves=tree.alive_leaves, dead_leaves=tree.dead_leaves, ns_splits=tree.ns_splits,
                 seconds=round(T.now(), 1), basin_clips=list(pg.basin_rep)[-40:])
        R6.save(doc, cert)
        fig207.render(doc)

    tree = NB.Tree206(pg, rounds=a.rounds, depth_cap=a.depth, node_cap=a.nodes, on_node=on_node, log=log, root_label=root_label, only=a.only)
    out = tree.run()
    root = tree.nodes[0] if tree.nodes else {}
    out["root"] = dict(verdict=root.get("verdict"), clip=root.get("clip"), seconds=root.get("seconds"), n_rounds=root.get("n_rounds"), kept=root.get("kept"),
                       forced_H=root.get("forced_H"), role_slots=root.get("role_slots"), alive_cells=root.get("alive_cells"), branch_slot=root.get("branch_slot"),
                       branch_role=root.get("branch_role"), branch_rows=root.get("branch_rows"), ns_candidates=root.get("ns_candidates"))
    out["wall"] = T.out_of_time()
    out["window_pending"] = (a.pad == "zero") and out["verdict"] == "DEAD"
    out["leaf"] = None
    if out["verdict"] == "DEAD":
        out["leaf"] = "every branch DEAD under the basin clip + Rule NS: " + "; ".join("%s %s%s<-%s by %s r%s" % (
            k["label"], k.get("slot") or "root", ("[%s %s]" % (k.get("role"), "meets" if k.get("kind") == "ns-meets" else "misses")) if str(k.get("kind") or "").startswith("ns-") else "",
            k.get("rows"), k["clip"], k["round"]) for k in out["killing"])
        if out["window_pending"]:
            out["leaf"] += " [pad 0: s0-only, WINDOW-PENDING]"
    out["tests"], out["steps"], out["seconds"] = T.tests[-4000:], T.steps[-2000:], round(T.now(), 1)
    out["basin_clips"] = list(pg.basin_rep)[-60:]
    d.update(out)
    d["nodes"] = tree.nodes
    R6.save(doc, cert)
    fig207.render(doc)
    log("   => %s (%s) in %.1f s: %d nodes, depth %d, %d NS splits, %d dead / %d alive leaves%s" % (
        out["verdict"], key, out["seconds"], out["n_nodes"], out["max_depth"], out["ns_splits"], out["dead_leaves"], out["alive_leaves"], " (WALL)" if out["wall"] else ""))
    return row_of(doc, key, cert)


if __name__ == "__main__":
    R6.belownormal()
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("leaf", "tree"))
    ap.add_argument("nid")
    ap.add_argument("--pad", default="g1")
    ap.add_argument("--leaf", default=None)
    ap.add_argument("--src", default="a206", choices=("standard", "extended", "a206"))
    ap.add_argument("--tag", default="")
    ap.add_argument("--wall", type=float, default=3600)
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--depth", type=int, default=6)
    ap.add_argument("--nodes", type=int, default=200)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    a.only = None
    if "+" in a.pad:
        a.pad, a.only = a.pad.split("+", 1)
    if a.mode == "leaf" and not a.leaf:
        ap.error("leaf mode needs --leaf")
    cert = os.path.join(CERTS, "basinclip207_%s.json" % a.nid)
    doc = dict(nid=a.nid, runs={})
    if os.path.exists(cert):
        try:
            doc = json.load(open(cert, encoding="utf-8"))
        except Exception:
            doc = dict(nid=a.nid, runs={})
    key = ("%s_%s%s_%s" % (a.pad, a.src, ("_" + a.tag) if a.tag else "", a.leaf)) if a.mode == "leaf" else (("%s_tree_%s" % (a.pad, a.only)) if a.only else "%s_tree" % a.pad)
    prev = doc["runs"].get(key)
    if prev and prev.get("verdict") in ("DEAD", "ALIVE") and not a.force:
        print("   %s: cached %s" % (key, prev["verdict"]), flush=True)
    else:
        run_one(doc, a, cert)
    try:
        print("   gallery: %s" % fig207.gallery(), flush=True)
    except Exception as e:                                        # noqa: BLE001
        print("   gallery failed: %r" % (e,), flush=True)
