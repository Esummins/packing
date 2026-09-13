"""A211 driver -- ONE runner for the COARSE tree on one node (a gallery page or an A57 tree record):
   python run211.py page <nid> [--wall 1800] [--pads zero,g1] [--depth 6] [--nodes 600] [--force]
Per pad, PAD 0 FIRST (a pad-0 kill is s0-only, WINDOW-PENDING; the window pad follows): stage 0 (A202 closed form +
A203 CSP, cached), then the coarse tree (tree211: cheap coarse internal nodes, the leaf rules at every fully named
leaf: rule CC -> no-room + pockets -> basin clip -> Rule NS -> the exact cascade last).  One certificate per node
certs/coarsetree211_<nid>.json (every node with its seconds), one slim row per (pad) run in
results/coarsetree211.jsonl, the page docs/residue_map/campaigns/A211-coarsetree/coarsetree211_<nid>.svg; the pad-0
verdict printed beside the window verdict.  Copied from A209's run209.py (the chain's driver) and changed here only."""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CERTS = os.path.abspath(os.path.join(HERE, "..", "certs"))
RES = os.path.abspath(os.path.join(HERE, "..", "results", "coarsetree211.jsonl"))
sys.path.insert(0, HERE)
import load211                                                 # noqa: E402
load211.install()
import stage209                                                # noqa: E402
import poly204 as P                                            # noqa: E402
import tree206 as N6                                           # noqa: E402
import clip207 as C                                            # noqa: E402
import coarse211 as C11                                        # noqa: E402
import tree211 as N11                                          # noqa: E402
import fig211                                                  # noqa: E402

C11.install()
FP, QP, MB = P.FP, P.QP, P.MB
A206CERTS = os.path.join(ROOT, "attempts", "A206-named-split", "certs")
VERIFIER = ("[C: closed-form / library clip trace + the leaf lemma (Lemma CORNER-COVER / A189 Lemma 1 / Lemma CN / Lemma BASIN)] A211 coarse tree "
            "(notes/coarse_tree.md): A202 stage 0 + A203 CSP; coarse internal nodes (re-binned pieces, refine 1, no lonely clip, shallow reach: supersets); "
            "at every fully named leaf rule CC (A210), A208 no-room + pocket CN bound (pockets branched at k = 9), A207 basin clip, A206 Rule NS (MAX_FRAC 0.5), "
            "then the exact A204/A205 cascade (nsub 4 / refine 2, lonely clip, sharp round); DEAD iff every branch DEAD (Lemma CT); no verifier clause")


def belownormal():
    """A210's WORKING fix: c_void_p(-1) + argtypes (the lab's old snippet silently no-ops)."""
    try:
        import ctypes
        k = ctypes.windll.kernel32
        k.SetPriorityClass.argtypes = [ctypes.c_void_p, ctypes.c_uint]
        k.SetProcessAffinityMask.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
        k.GetPriorityClass.argtypes = [ctypes.c_void_p]
        h = ctypes.c_void_p(-1)
        k.SetPriorityClass(h, 0x00004000)
        k.SetProcessAffinityMask(h, 0xFFFF)
        print("   priority class %d (16384 = BelowNormal), affinity 0xFFFF" % k.GetPriorityClass(h), flush=True)
    except Exception as e:                                        # noqa: BLE001
        print("   belownormal failed: %r" % (e,), flush=True)


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
        return fig211.render(doc)
    except Exception as e:                                        # noqa: BLE001
        import traceback
        traceback.print_exc()
        print("   fig211 failed: %r" % (e,), flush=True)


def closed_subtree(nodes, label):
    sub = [n for n in nodes if n["label"] == label or (n["label"].startswith(label) and n["label"][len(label)] in ".rusx")]
    return bool(sub) and all(n.get("verdict") != "ALIVE" for n in sub) and any(n.get("verdict") == "DEAD" for n in sub)


def a206_inherited(nid, pad, source):
    """(slot, rows) -> the A206 whole-tree run's closed depth-1 branch on the same page, pad and A203 start (A209's rule)."""
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


def brief_nodes(nodes):
    return [dict(label=n["label"], depth=n.get("depth"), verdict=n.get("verdict"), clip=n.get("clip"), kind=n.get("kind"), seconds=n.get("seconds"),
                 coarse=n.get("coarse"), n_roles=len(n.get("roles") or {}), reason=str(n.get("reason") or "")[:80]) for n in nodes]


def row_of(doc, key, cert):
    d = doc["runs"][key]
    slim = dict(nid=doc["nid"], cls=doc.get("cls"), record=doc.get("record"), tree=doc.get("tree"), applies_to_tags=[doc.get("tree")] if doc.get("tree") else [],
                run=key, pad=d.get("pad"), mode="page", source=d.get("source"), cfg=d.get("cfg"), lam=d.get("lam"), verdict=d.get("verdict"), leaf=d.get("leaf"),
                n_nodes=d.get("n_nodes"), n_records=d.get("n_records"), max_depth=d.get("max_depth"), alive_leaves=d.get("alive_leaves"), dead_leaves=d.get("dead_leaves"),
                ns_splits=d.get("ns_splits"), pocket_splits=d.get("pocket_splits"), cc_kills=d.get("cc_kills"), exact_rounds=d.get("exact_rounds"), basin_kills=d.get("basin_kills"),
                noroom=[dict(label=r["label"], k=r["k"], verdict=r["verdict"], clip=r["clip"], seconds=r["seconds"]) for r in (d.get("noroom_runs") or [])],
                inherited=d.get("inherited"), basins=d.get("basins"), killing=d.get("killing"), undecided=d.get("undecided"), seconds=d.get("seconds"), root=d.get("root"),
                wall=d.get("wall"), window_pending=d.get("window_pending"), stage0=doc.get("stage0"), verdicts=doc.get("verdicts"), stage_reached=doc.get("stage_reached"),
                nodes_brief=brief_nodes(d.get("nodes") or []), verifier=VERIFIER, cert=os.path.relpath(cert, ROOT).replace("\\", "/"), when=time.strftime("%Y-%m-%d %H:%M:%S"))
    os.makedirs(os.path.dirname(RES), exist_ok=True)
    with open(RES, "a", encoding="utf-8") as f:
        f.write(json.dumps(slim, default=str) + "\n")
    return slim


def run_tree(doc, a, pad, cert, log=print):
    T = FP.Trace(wall=a.wall)
    rec, cls, row = FP.load_page(a.nid)
    start = stage209.start_of(a.nid, pad)
    basins = C.load_basins(cls, pad, QP.PADS[pad]) if pad != "zero" else []
    pg = C11.CoarsePage(rec, cls, a.nid, T, pad=pad, start=start, basins=basins)
    inh = a206_inherited(a.nid, pad, start.get("file"))
    key = "%s_page" % pad
    page_doc(doc, pg)
    d = doc["runs"][key] = dict(pad=pad, mode="page", source=start.get("file"), lam=float(pg.lam), start=start, verdict="RUNNING", nodes=[], basins=[C.basin_json(b) for b in basins],
                                inherited_available={"%s<-%s" % k: v for k, v in inh.items()}, verifier=VERIFIER,
                                cfg=dict(rounds=a.rounds, depth_cap=a.depth, node_cap=a.nodes, wall=a.wall, coarse=dict(grid=[C11.NX, C11.NY, C11.NB], cap=C11.CAP, refine=C11.REFINE, max_iter=C11.MAX_ITER,
                                         nsub=C11.NSUB, depth=C11.DEPTH, jdepth=C11.JDEPTH, kmode=C11.KMODE), exact=C11.EXACT, exact_rounds=N11.EXACT_ROUNDS, noroom_cap=N11.NOROOM_CAP,
                                         soft_all=N6.SOFT_ALL, max_frac=N6.MAX_FRAC))
    log("== %s page pad %s: start %s; basins %s; inherited A206 kills %s; H %s; forced H %s; %d slots; free squares %d" % (
        a.nid, pad, start.get("file"), [(b["cell"], float(b["rc"])) for b in basins], list(d["inherited_available"]), [round(v, 3) for v in pg.roles[pg.H]], sorted(pg.forced_H), len(pg.slots), pg.n_free))

    def on_node(tree):
        d["nodes"] = tree.nodes
        d.update(n_nodes=tree.n_nodes, max_depth=tree.max_depth, alive_leaves=tree.alive_leaves, dead_leaves=tree.dead_leaves, ns_splits=tree.ns_splits,
                 pocket_splits=tree.pocket_splits, cc_kills=tree.cc_kills, exact_rounds=tree.exact_rounds, seconds=round(T.now(), 1), basin_clips=list(pg.basin_rep)[-40:])
        save(doc, cert)
        draw(doc)

    tree = N11.Tree211(pg, inherited=inh, rounds=a.rounds, depth_cap=a.depth, node_cap=a.nodes, on_node=on_node, log=log, root_label="R")
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
    log("   => %s (%s) in %.1f s: %d nodes, depth %d, %d CC kills, %d exact leaf cascades, %d NS splits, %d pocket splits, %d inherited, %d dead / %d alive leaves%s" % (
        out["verdict"], key, out["seconds"], out["n_nodes"], out["max_depth"], out["cc_kills"], out["exact_rounds"], out["ns_splits"], out["pocket_splits"], len(out["inherited"]),
        out["dead_leaves"], out["alive_leaves"], " (WALL)" if out["wall"] else ""))
    log("   per node: " + "; ".join("%s d%s %s%s %ss%s" % (n["label"], n.get("depth"), n.get("verdict"), (" " + n["clip"]) if n.get("clip") else "", n.get("seconds"), "" if n.get("coarse") else " [exact]")
                                    for n in tree.nodes))
    return key, out["verdict"]


def run_page(doc, a, cert, log=print):
    rec, cls, row = FP.load_page(a.nid)
    doc.update(cls=cls, record=(row.get("record") or "").replace("\\", "/"), tree=row.get("tree") or ("%s_interior_G1" % cls), level=row.get("level"))
    doc.setdefault("stage0", {})
    doc.setdefault("verdicts", {})
    for pad in a.pads.split(","):
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
        save(doc, cert)
        draw(doc)
        key, v = run_tree(doc, a, pad, cert, log=log)
        doc["verdicts"][pad] = v
        doc["stage_reached"] = "2 (tree)"
        save(doc, cert)
        draw(doc)
        row_of(doc, key, cert)
    log("== %s: g1 %s | pad0 %s   (pad-0 verdict beside the window verdict; a page is killed only by a DEAD g1)" % (a.nid, doc["verdicts"].get("g1"), doc["verdicts"].get("zero")))


if __name__ == "__main__":
    belownormal()
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("page",))
    ap.add_argument("nid")
    ap.add_argument("--pads", default="zero,g1")           # pad 0 FIRST
    ap.add_argument("--wall", type=float, default=1800)
    ap.add_argument("--rounds", type=int, default=1)       # the coarse node: ONE cascade round
    ap.add_argument("--depth", type=int, default=6)
    ap.add_argument("--nodes", type=int, default=600)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    cert = os.path.join(CERTS, "coarsetree211_%s.json" % a.nid)
    doc = dict(nid=a.nid, runs={})
    if os.path.exists(cert) and not a.force:
        try:
            doc = json.load(open(cert, encoding="utf-8"))
        except Exception:
            doc = dict(nid=a.nid, runs={})
    run_page(doc, a, cert)
    try:
        print("   gallery: %s" % fig211.gallery(), flush=True)
    except Exception as e:                                        # noqa: BLE001
        print("   gallery failed: %r" % (e,), flush=True)
