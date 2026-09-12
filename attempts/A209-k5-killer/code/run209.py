"""A209 driver -- ONE runner for the whole chain on one node (a gallery page or an A57 tree record):
   python run209.py page <nid> [--wall 3600] [--pads g1,zero] [--depth 5] [--nodes 300] [--rounds 3] [--force]
Per pad (g1 = the page's window first, pad 0 second): stage 0 (A202 closed form + A203 CSP, cached from A203 / A202 /
A209's certs), the page drawn; if alive the composed tree (A204 cascade + A205 clip tree + A206 Rule NS + A207 basin
clip + A208 no-room / pocket branching), the page redrawn after every closed node.  The pad-0 tree is skipped when the
g1 tree is DEAD (the page is killed; pad 0 is s0-only).  One certificate per node certs/k5killer209_<nid>.json, one slim
row per (pad) run in results/k5killer209.jsonl, the page docs/residue_map/campaigns/A209-k5killer/k5killer209_<nid>.svg."""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CERTS = os.path.abspath(os.path.join(HERE, "..", "certs"))
RES = os.path.abspath(os.path.join(HERE, "..", "results", "k5killer209.jsonl"))
sys.path.insert(0, HERE)
import load209                                                 # noqa: E402
load209.install()
import stage209                                                # noqa: E402
import poly204 as P                                            # noqa: E402
import tree206 as N6                                           # noqa: E402
import tree207 as N7                                           # noqa: E402
import tree209 as N9                                           # noqa: E402
import clip207 as C                                            # noqa: E402
import fig209                                                  # noqa: E402

FP, QP, MB = P.FP, P.QP, P.MB
A206CERTS = os.path.join(ROOT, "attempts", "A206-named-split", "certs")
VERIFIER = ("[C: library clip trace (+ A189 Lemma 1 / Lemma CN / Lemma BASIN)] A209 composed chain: A202 stage 0 + A203 CSP, A204 polygon-clip cascade, "
            "A205 clip tree (Lemma CT, fresh-table proviso, bar-anon, sharp round), A206 Rule NS (MAX_FRAC 0.5), A207 basin clip where a certified basin covers the "
            "window, A208 no-room with the pocket CN bound at every leaf with >= 9 roles and pocket branching at k = 9; DEAD iff every branch DEAD; no verifier clause")


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
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, default=str)
    for k in range(8):
        try:
            os.replace(tmp, cert)
            return
        except PermissionError:
            time.sleep(2 + 3 * k)
    with open(cert, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, default=str)


def draw(doc):
    try:
        return fig209.render(doc)
    except Exception as e:                                        # noqa: BLE001
        import traceback
        traceback.print_exc()
        print("   fig209 failed: %r" % (e,), flush=True)


def closed_subtree(nodes, label):
    """A206's record: the subtree under `label` is closed iff it has a DEAD node and no ALIVE node."""
    sub = [n for n in nodes if n["label"] == label or (n["label"].startswith(label) and n["label"][len(label)] in ".rus")]
    return bool(sub) and all(n.get("verdict") != "ALIVE" for n in sub) and any(n.get("verdict") == "DEAD" for n in sub)


def a206_inherited(nid, pad, source):
    """(slot, rows) -> the A206 whole-tree run's closed depth-1 branch on the same page, pad and A203 start."""
    f = os.path.join(A206CERTS, "namedsplit206_%s.json" % nid)
    out = {}
    if not os.path.exists(f):
        return out
    try:
        doc = json.load(open(f, encoding="utf-8"))
    except Exception:
        return out
    for key, d in (doc.get("runs") or {}).items():
        if d.get("mode") != "tree" or d.get("pad") != pad or d.get("source") != source:
            continue
        nodes = d.get("nodes") or []
        for n in nodes:
            if n.get("depth") != 1 or n.get("rows") is None or str(n.get("kind") or "").startswith("ns-") or n.get("kind") in ("refresh", "sharp") or "." not in n["label"]:
                continue
            if closed_subtree(nodes, n["label"]):
                out[(n.get("slot"), tuple(n["rows"]))] = dict(run=key, label=n["label"], cert=os.path.relpath(f, ROOT).replace("\\", "/"), leaf=n.get("leaf") or n.get("reason"))
    return out


def page_doc(doc, pg):
    doc.setdefault("cells", [FP.rect_f(c["rect"]) for c in pg.cells])
    doc.setdefault("slots", list(pg.slots))
    doc.setdefault("wbox", {p: FP.rect_f(pg.item[p]["wb"]) for p in pg.slots})
    doc.setdefault("wbox_pad", {})[pg.pad] = {p: FP.rect_f(pg.item[p]["wb"]) for p in pg.slots}
    doc.setdefault("H_record", [round(v, 6) for v in pg.record_H])


def row_of(doc, key, cert):
    d = doc["runs"][key]
    slim = dict(nid=doc["nid"], cls=doc.get("cls"), record=doc.get("record"), tree=doc.get("tree"), applies_to_tags=[doc.get("tree")] if doc.get("tree") else [],
                run=key, pad=d.get("pad"), mode="page", source=d.get("source"), cfg=d.get("cfg"), lam=d.get("lam"), verdict=d.get("verdict"), leaf=d.get("leaf"),
                n_nodes=d.get("n_nodes"), n_records=d.get("n_records"), max_depth=d.get("max_depth"), alive_leaves=d.get("alive_leaves"), dead_leaves=d.get("dead_leaves"),
                ns_splits=d.get("ns_splits"), pocket_splits=d.get("pocket_splits"), noroom=[dict(label=r["label"], k=r["k"], verdict=r["verdict"], clip=r["clip"], seconds=r["seconds"]) for r in (d.get("noroom_runs") or [])],
                inherited=d.get("inherited"), basins=d.get("basins"), killing=d.get("killing"), undecided=d.get("undecided"), seconds=d.get("seconds"), root=d.get("root"),
                wall=d.get("wall"), window_pending=d.get("window_pending"), stage0=doc.get("stage0"), verdicts=doc.get("verdicts"), stage_reached=doc.get("stage_reached"),
                verifier=VERIFIER, cert=os.path.relpath(cert, ROOT).replace("\\", "/"), when=time.strftime("%Y-%m-%d %H:%M:%S"))
    os.makedirs(os.path.dirname(RES), exist_ok=True)
    with open(RES, "a", encoding="utf-8") as f:
        f.write(json.dumps(slim, default=str) + "\n")
    return slim


def run_tree(doc, a, pad, cert, log=print):
    T = FP.Trace(wall=a.wall)
    rec, cls, row = FP.load_page(a.nid)
    start = stage209.start_of(a.nid, pad)
    basins = C.load_basins(cls, pad, QP.PADS[pad]) if pad != "zero" else []
    pg = N7.TreePage207(rec, cls, a.nid, T, pad=pad, start=start, basins=basins)
    inh = a206_inherited(a.nid, pad, start.get("file"))
    key = "%s_page" % pad
    page_doc(doc, pg)
    d = doc["runs"][key] = dict(pad=pad, mode="page", source=start.get("file"), lam=float(pg.lam), start=start, verdict="RUNNING", nodes=[], basins=[C.basin_json(b) for b in basins],
                                inherited_available={"%s<-%s" % k: v for k, v in inh.items()}, verifier=VERIFIER,
                                cfg=dict(rounds=a.rounds, depth_cap=a.depth, node_cap=a.nodes, wall=a.wall, nsub=4, refine=2, soft_all=N6.SOFT_ALL, max_frac=N6.MAX_FRAC))
    log("== %s page pad %s: start %s; basins %s; inherited A206 kills %s; H %s; forced H %s; %d slots; free squares %d" % (
        a.nid, pad, start.get("file"), [(b["cell"], float(b["rc"])) for b in basins], list(d["inherited_available"]), [round(v, 3) for v in pg.roles[pg.H]], sorted(pg.forced_H), len(pg.slots), pg.n_free))

    def on_node(tree):
        d["nodes"] = tree.nodes
        d.update(n_nodes=tree.n_nodes, max_depth=tree.max_depth, alive_leaves=tree.alive_leaves, dead_leaves=tree.dead_leaves, ns_splits=tree.ns_splits,
                 pocket_splits=tree.pocket_splits, seconds=round(T.now(), 1), basin_clips=list(pg.basin_rep)[-40:])
        save(doc, cert)
        draw(doc)

    tree = N9.Tree209(pg, inherited=inh, rounds=a.rounds, depth_cap=a.depth, node_cap=a.nodes, on_node=on_node, log=log, root_label="R")
    out = tree.run()
    root = tree.nodes[0] if tree.nodes else {}
    out["root"] = dict(verdict=root.get("verdict"), clip=root.get("clip"), seconds=root.get("seconds"), n_rounds=root.get("n_rounds"), kept=root.get("kept"),
                       forced_H=root.get("forced_H"), role_slots=root.get("role_slots"), alive_cells=root.get("alive_cells"))
    out["wall"] = T.out_of_time()
    out["window_pending"] = (pad == "zero") and out["verdict"] == "DEAD"
    out["leaf"] = None
    if out["verdict"] == "DEAD":
        out["leaf"] = "every branch DEAD: " + "; ".join("%s %s%s<-%s by %s r%s" % (
            k["label"], k.get("slot") or "root", ("[%s %s]" % (k.get("role"), "meets" if k.get("kind") == "ns-meets" else "misses")) if str(k.get("kind") or "").startswith("ns-") else "",
            k.get("rows"), k["clip"], k["round"]) for k in out["killing"])
        if out["window_pending"]:
            out["leaf"] += " [pad 0: s0-only, WINDOW-PENDING]"
    out["tests"], out["steps"], out["seconds"] = T.tests[-4000:], T.steps[-2000:], round(T.now(), 1)
    out["basin_clips"] = list(pg.basin_rep)[-60:]
    d.update(out)
    d["nodes"] = tree.nodes
    log("   => %s (%s) in %.1f s: %d nodes, depth %d, %d NS splits, %d pocket splits, %d inherited, %d dead / %d alive leaves%s" % (
        out["verdict"], key, out["seconds"], out["n_nodes"], out["max_depth"], out["ns_splits"], out["pocket_splits"], len(out["inherited"]), out["dead_leaves"], out["alive_leaves"], " (WALL)" if out["wall"] else ""))
    return key, out["verdict"]


def run_page(doc, a, cert, log=print):
    rec, cls, row = FP.load_page(a.nid)
    doc.update(cls=cls, record=(row.get("record") or "").replace("\\", "/"), tree=row.get("tree") or ("%s_interior_G1" % cls), level=row.get("level"))
    doc.setdefault("stage0", {})
    doc.setdefault("verdicts", {})
    pads = a.pads.split(",")
    for pad in pads:
        if pad in doc["verdicts"] and not a.force:
            log("   pad %s: cached %s" % (pad, doc["verdicts"][pad]))
            continue
        s0 = stage209.stage0(a.nid, pad, log=log)
        doc["stage0"][pad] = s0
        doc["stage_reached"] = "0"
        if s0["verdict"] == "DEAD":
            doc["verdicts"][pad] = "DEAD (stage 0)"
            save(doc, cert)
            draw(doc)
            doc["runs"].setdefault("%s_page" % pad, dict(pad=pad, mode="page", source=s0["file"], verdict="DEAD", leaf="stage 0: %s" % s0.get("leaf"), n_nodes=0, seconds=s0.get("seconds"),
                                                            window_pending=(pad == "zero"), verifier=s0["verifier"], stage0_kill=True, nodes=[]))
            row_of(doc, "%s_page" % pad, cert)
            continue
        if pad == "zero" and doc["verdicts"].get("g1", "").startswith("DEAD"):
            doc["verdicts"][pad] = "not run (g1 DEAD; stage 0 %s)" % s0["verdict"]
            save(doc, cert)
            draw(doc)
            continue
        save(doc, cert)
        draw(doc)
        key, v = run_tree(doc, a, pad, cert, log=log)
        doc["verdicts"][pad] = v
        doc["stage_reached"] = "2 (tree)"
        save(doc, cert)
        draw(doc)
        row_of(doc, key, cert)
    log("== %s: g1 %s | pad0 %s" % (a.nid, doc["verdicts"].get("g1"), doc["verdicts"].get("zero")))


if __name__ == "__main__":
    belownormal()
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("page",))
    ap.add_argument("nid")
    ap.add_argument("--pads", default="zero,g1")   # PI 2026-09-12: pad 0 FIRST (instant kills of pad ghosts), the window second
    ap.add_argument("--wall", type=float, default=3600)
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--depth", type=int, default=5)
    ap.add_argument("--nodes", type=int, default=300)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    cert = os.path.join(CERTS, "k5killer209_%s.json" % a.nid)
    doc = dict(nid=a.nid, runs={})
    if os.path.exists(cert) and not a.force:
        try:
            doc = json.load(open(cert, encoding="utf-8"))
        except Exception:
            doc = dict(nid=a.nid, runs={})
    run_page(doc, a, cert)
    try:
        print("   gallery: %s" % fig209.gallery(), flush=True)
    except Exception as e:                                        # noqa: BLE001
        print("   gallery failed: %r" % (e,), flush=True)
