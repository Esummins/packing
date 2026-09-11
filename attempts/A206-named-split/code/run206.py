"""A206 driver.  Two modes:
   python run206.py leaf <nid> --pad g1 --leaf R.2.3.1 [--src standard|extended --tag _w3600] [--wall 3600]
       the node loaded from A205's certificate (load206), one refresh cascade, then the tree with Rule NS from there;
   python run206.py tree <nid> --pad g1 [--wall 3600]
       the whole clip tree of the page under Rule NS (A205's tree with the split at every fully named node).
One certificate per page, certs/namedsplit206_<nid>.json, runs keyed <pad>_<leaf> / <pad>_tree; the page
docs/residue_map/campaigns/A206-namedsplit/namedsplit206_<nid>.svg redrawn after every closed node; one slim row per run
in results/namedsplit206.jsonl."""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CERTS = os.path.abspath(os.path.join(HERE, "..", "certs"))
RES = os.path.abspath(os.path.join(HERE, "..", "results", "namedsplit206.jsonl"))
sys.path.insert(0, HERE)
import poly204 as P                                            # noqa: E402
import tree206 as N6                                           # noqa: E402
import tree206b as NB                                          # noqa: E402
import load206                                                 # noqa: E402
import fig206                                                  # noqa: E402

FP, QP, MB = P.FP, P.QP, P.MB
VERIFIER = ("[C: library clip trace] A206 Rule NS on A205's clip tree: at a fully named node split a soft-named (slot, role) pair into "
            "[role meets slot] (the exact reach clip at the slot, A161) / [role misses slot] (its rows leave the option table, MISS-CLIP), "
            "A204's cascade + A205's clips at every node; DEAD iff every branch DEAD; no verifier clause")


def belownormal():
    try:
        import ctypes
        k = ctypes.windll.kernel32
        h = k.GetCurrentProcess()
        k.SetPriorityClass(h, 0x00004000)
        k.SetProcessAffinityMask(h, 0xFFFF)
    except Exception:
        pass


def save(doc, cert):
    os.makedirs(os.path.dirname(cert), exist_ok=True)
    tmp = cert + ".tmp"
    json.dump(doc, open(tmp, "w", encoding="utf-8"), indent=1, default=str)
    os.replace(tmp, cert)


def draw(doc):
    try:
        return fig206.render(doc)
    except Exception as e:                                        # noqa: BLE001
        import traceback
        traceback.print_exc()
        print("   fig206 failed: %r" % (e,), flush=True)


def row_of(doc, key, cert):
    d = doc["runs"][key]
    slim = dict(nid=doc["nid"], cls=doc.get("cls"), run=key, pad=d.get("pad"), mode=d.get("mode"), leaf_label=d.get("leaf_label"), source=d.get("source"),
                cfg=d.get("cfg"), lam=d.get("lam"), verdict=d.get("verdict"), leaf=d.get("leaf"), n_nodes=d.get("n_nodes"), n_records=d.get("n_records"),
                max_depth=d.get("max_depth"), alive_leaves=d.get("alive_leaves"), dead_leaves=d.get("dead_leaves"), ns_splits=d.get("ns_splits"),
                killing=d.get("killing"), undecided=d.get("undecided"), seconds=d.get("seconds"), root=d.get("root"), wall=d.get("wall"),
                window_pending=d.get("window_pending"), verifier=VERIFIER, cert=os.path.relpath(cert, ROOT).replace("\\", "/"),
                when=time.strftime("%Y-%m-%d %H:%M:%S"))
    os.makedirs(os.path.dirname(RES), exist_ok=True)
    with open(RES, "a", encoding="utf-8") as f:
        f.write(json.dumps(slim, default=str) + "\n")
    return slim


def page_doc(doc, pg):
    doc.setdefault("cells", [FP.rect_f(c["rect"]) for c in pg.cells])
    doc.setdefault("slots", list(pg.slots))
    doc.setdefault("wbox", {p: FP.rect_f(pg.item[p]["wb"]) for p in pg.slots})
    doc.setdefault("wbox_pad", {})[pg.pad] = {p: FP.rect_f(pg.item[p]["wb"]) for p in pg.slots}
    doc.setdefault("H_record", [round(v, 6) for v in pg.record_H])


def run_one(doc, a, cert, log=print):
    T = FP.Trace(wall=a.wall)
    if a.mode == "leaf":
        pg, meta = load206.load_node(a.nid, a.pad, a.leaf, T, src=a.src, tag=a.tag)
        key, root_label, start = "%s_%s" % (a.pad, a.leaf), a.leaf, meta["start"]
    else:
        start = P.load_start(a.nid, a.pad)
        rec, cls, row = FP.load_page(a.nid)
        pg = N6.TreePage206(rec, cls, a.nid, T, pad=a.pad, start=start)
        meta = dict(source=start.get("file"), start=start)
        key, root_label = "%s_tree" % a.pad, "R"
    doc["cls"] = pg.cls if hasattr(pg, "cls") else doc.get("cls")
    page_doc(doc, pg)
    d = doc["runs"][key] = dict(pad=a.pad, mode=a.mode, leaf_label=(a.leaf if a.mode == "leaf" else None), source=meta.get("source"), lam=float(pg.lam),
                                start=start, loaded=meta.get("loaded"), recorded=meta.get("recorded"), path=meta.get("path"), verdict="RUNNING", nodes=[],
                                verifier=VERIFIER, cfg=dict(rounds=a.rounds, depth_cap=a.depth, node_cap=a.nodes, wall=a.wall, nsub=4, refine=2, soft_all=N6.SOFT_ALL))
    log("== %s %s pad %s [%s]: start %s; H %s; forced H %s; roles %s (cells %s); %d slots; free squares %d" % (
        a.nid, a.mode, a.pad, root_label, meta.get("source"), [round(v, 3) for v in pg.roles[pg.H]], sorted(pg.forced_H),
        {k: list(v) for k, v in pg.role_slots.items()}, dict(pg.role_cell), len(pg.slots), pg.n_free))

    def on_node(tree):
        d["nodes"] = tree.nodes
        d.update(n_nodes=tree.n_nodes, max_depth=tree.max_depth, alive_leaves=tree.alive_leaves, dead_leaves=tree.dead_leaves, ns_splits=tree.ns_splits, seconds=round(T.now(), 1))
        save(doc, cert)
        draw(doc)

    tree = NB.Tree206(pg, rounds=a.rounds, depth_cap=a.depth, node_cap=a.nodes, on_node=on_node, log=log, root_label=root_label)
    out = tree.run()
    root = tree.nodes[0] if tree.nodes else {}
    out["root"] = dict(verdict=root.get("verdict"), clip=root.get("clip"), seconds=root.get("seconds"), n_rounds=root.get("n_rounds"), kept=root.get("kept"),
                       forced_H=root.get("forced_H"), role_slots=root.get("role_slots"), alive_cells=root.get("alive_cells"), branch_slot=root.get("branch_slot"),
                       branch_role=root.get("branch_role"), branch_rows=root.get("branch_rows"), ns_candidates=root.get("ns_candidates"))
    out["wall"] = T.out_of_time()
    out["window_pending"] = (a.pad == "zero") and out["verdict"] == "DEAD"
    out["leaf"] = None
    if out["verdict"] == "DEAD":
        out["leaf"] = "every branch DEAD under Rule NS: " + "; ".join("%s %s%s<-%s by %s r%s" % (
            k["label"], k.get("slot") or "root", ("[%s %s]" % (k.get("role"), "meets" if k.get("kind") == "ns-meets" else "misses")) if k.get("kind", "").startswith("ns-") else "",
            k.get("rows"), k["clip"], k["round"]) for k in out["killing"])
        if out["window_pending"]:
            out["leaf"] += " [pad 0: s0-only, WINDOW-PENDING]"
    out["tests"], out["steps"], out["seconds"] = T.tests[-4000:], T.steps[-2000:], round(T.now(), 1)
    d.update(out)
    d["nodes"] = tree.nodes
    save(doc, cert)
    draw(doc)
    log("   => %s (%s) in %.1f s: %d nodes, depth %d, %d NS splits, %d dead / %d alive leaves%s" % (
        out["verdict"], key, out["seconds"], out["n_nodes"], out["max_depth"], out["ns_splits"], out["dead_leaves"], out["alive_leaves"], " (WALL)" if out["wall"] else ""))
    return row_of(doc, key, cert)


if __name__ == "__main__":
    belownormal()
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("leaf", "tree"))
    ap.add_argument("nid")
    ap.add_argument("--pad", default="g1")
    ap.add_argument("--leaf", default=None)
    ap.add_argument("--src", default="standard", choices=("standard", "extended"))
    ap.add_argument("--tag", default="")
    ap.add_argument("--wall", type=float, default=3600)
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--depth", type=int, default=6)
    ap.add_argument("--nodes", type=int, default=200)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    if a.mode == "leaf" and not a.leaf:
        ap.error("leaf mode needs --leaf")
    cert = os.path.join(CERTS, "namedsplit206_%s.json" % a.nid)
    doc = dict(nid=a.nid, runs={})
    if os.path.exists(cert):
        try:
            doc = json.load(open(cert, encoding="utf-8"))
        except Exception:
            doc = dict(nid=a.nid, runs={})
    key = "%s_%s" % (a.pad, a.leaf) if a.mode == "leaf" else "%s_tree" % a.pad
    prev = doc["runs"].get(key)
    if prev and prev.get("verdict") in ("DEAD", "ALIVE") and not a.force:
        print("   %s: cached %s" % (key, prev["verdict"]), flush=True)
    else:
        run_one(doc, a, cert)
    try:
        print("   gallery: %s" % fig206.gallery(), flush=True)
    except Exception as e:                                        # noqa: BLE001
        print("   gallery failed: %r" % (e,), flush=True)
