"""A205 driver: per page, the CLIP TREE at the g1 pad (the page's window), then -- if ALIVE -- at pad 0 (s0-only,
WINDOW-PENDING); wall 900 s per pad, depth cap 4, node cap 200, coarse settings (nsub 4 / refine 2); the page
docs/residue_map/campaigns/A205-cliptree/cliptree205_<nid>.svg redrawn after the root cascade and after every closed
branch; certificate certs/cliptree205_<nid>.json (every node: branch, verdict, clip, round, seconds, last snapshot);
one slim row per (nid, pad) in results/cliptree205.jsonl.       python run205.py <nid> [--wall 900] [--pads g1,zero]
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CERTS = os.path.abspath(os.path.join(HERE, "..", "certs"))
RES = os.path.abspath(os.path.join(HERE, "..", "results", "cliptree205.jsonl"))
sys.path.insert(0, HERE)
import poly204 as P                                            # noqa: E402
import tree205 as T5                                           # noqa: E402
import tree205b as TB                                          # noqa: E402
import fig205                                                  # noqa: E402

FP, QP, MB = P.FP, P.QP, P.MB
VERIFIER = ("[C: library clip trace] A205 clip tree: branch on a forced slot's remaining meeter rows (Theorem FC), instantiate, "
            "A171/A172/A173 polygon + lonely clip + A203 rule-S clip to a fixed point, A161 exact miss, A198/A200 caps + FC + count with "
            "A203's pair table and Lemma HC rows; start = A203's closed-form trace; no verifier clause")


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
        return fig205.render(doc)
    except Exception as e:                                        # noqa: BLE001
        import traceback
        traceback.print_exc()
        print("   fig205 failed: %r" % (e,), flush=True)


def row_of(doc, pad, cert):
    d = doc["pads"][pad]
    slim = dict(nid=doc["nid"], cls=doc["cls"], pad=pad, lam=d.get("lam"), verdict=d.get("verdict"), leaf=d.get("leaf"),
                n_nodes=d.get("n_nodes"), n_records=d.get("n_records"), max_depth=d.get("max_depth"), alive_leaves=d.get("alive_leaves"),
                dead_leaves=d.get("dead_leaves"), killing=d.get("killing"), undecided=d.get("undecided"), seconds=d.get("seconds"),
                root=d.get("root"), wall=d.get("wall"), window_pending=d.get("window_pending"), verifier=VERIFIER, start=d.get("start"),
                cert=os.path.relpath(cert, ROOT).replace("\\", "/"), prior_tau=doc.get("prior_tau"), record=doc.get("record"),
                row=doc.get("row"), when=time.strftime("%Y-%m-%d %H:%M:%S"))
    os.makedirs(os.path.dirname(RES), exist_ok=True)
    with open(RES, "a", encoding="utf-8") as f:
        f.write(json.dumps(slim, default=str) + "\n")
    return slim


def run_pad(doc, nid, pad, wall, cert, rounds=3, depth_cap=4, node_cap=200, log=print):
    start = P.load_start(nid, pad)
    T = FP.Trace(wall=wall)
    rec, cls, row = FP.load_page(nid)
    doc["cls"], doc["row"] = cls, dict(family=row.get("family"), camp=row.get("camp"), tau=row.get("tau"))
    doc["record"] = (row.get("record") or "").replace(chr(92), "/")
    try:
        doc["prior_tau"] = float(row.get("tau"))
    except (TypeError, ValueError):
        doc["prior_tau"] = None
    pg = T5.TreePage(rec, cls, nid, T, pad=pad, start=start)
    doc.setdefault("cells", [FP.rect_f(c["rect"]) for c in pg.cells])
    doc.setdefault("slots", list(pg.slots))
    doc.setdefault("wbox", {p: FP.rect_f(pg.item[p]["wb"]) for p in pg.slots})
    doc.setdefault("wbox_pad", {})[pad] = {p: FP.rect_f(pg.item[p]["wb"]) for p in pg.slots}
    doc.setdefault("H_record", [round(v, 6) for v in pg.record_H])
    d = doc["pads"][pad] = dict(pad=pad, lam=float(pg.lam), start=start, verdict="RUNNING", nodes=[], verifier=VERIFIER,
                                cfg=dict(rounds=rounds, depth_cap=depth_cap, node_cap=node_cap, wall=wall, nsub=4, refine=2))
    log("== %s (%s) at the %s pad: start %s, H %s, forced H %s, H units %s/%s; %d slots; free squares %d" % (
        nid, cls, pad, start.get("source"), [round(v, 3) for v in pg.roles[pg.H]], sorted(pg.forced_H), start.get("n_units_alive"),
        start.get("n_units"), len(pg.slots), pg.n_free))

    def on_node(tree):
        d["nodes"] = tree.nodes
        d.update(n_nodes=tree.n_nodes, max_depth=tree.max_depth, alive_leaves=tree.alive_leaves, dead_leaves=tree.dead_leaves, seconds=round(T.now(), 1))
        save(doc, cert)
        draw(doc)

    tree = TB.Tree(pg, rounds=rounds, depth_cap=depth_cap, node_cap=node_cap, on_node=on_node, log=log)
    out = tree.run()
    root = tree.nodes[0] if tree.nodes else {}
    out["root"] = dict(verdict=root.get("verdict"), clip=root.get("clip"), seconds=root.get("seconds"), n_rounds=root.get("n_rounds"),
                       kept=root.get("kept"), forced_H=root.get("forced_H"), role_slots=root.get("role_slots"), alive_cells=root.get("alive_cells"),
                       branch_slot=root.get("branch_slot"), branch_rows=root.get("branch_rows"))
    out["wall"] = T.out_of_time()
    out["window_pending"] = (pad == "zero") and out["verdict"] == "DEAD"
    out["leaf"] = None
    if out["verdict"] == "DEAD":
        out["leaf"] = "every branch of the clip tree DEAD: " + "; ".join("%s %s<-%s by %s r%s" % (k["label"], k.get("slot") or "root", k.get("rows"), k["clip"], k["round"]) for k in out["killing"])
        if out["window_pending"]:
            out["leaf"] += " [pad 0: s0-only, WINDOW-PENDING]"
    out["tests"], out["steps"], out["seconds"] = T.tests[-4000:], T.steps[-2000:], round(T.now(), 1)
    d.update(out)
    d["nodes"] = tree.nodes
    save(doc, cert)
    draw(doc)
    log("   => %s at the %s pad in %.1f s: %d nodes, depth %d, %d dead / %d alive leaves%s" % (
        out["verdict"], pad, out["seconds"], out["n_nodes"], out["max_depth"], out["dead_leaves"], out["alive_leaves"], " (WALL)" if out["wall"] else ""))
    return row_of(doc, pad, cert)


if __name__ == "__main__":
    belownormal()
    ap = argparse.ArgumentParser()
    ap.add_argument("nid")
    ap.add_argument("--wall", type=float, default=900)
    ap.add_argument("--pads", default="g1,zero")
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--depth", type=int, default=4)
    ap.add_argument("--nodes", type=int, default=200)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    cert = os.path.join(CERTS, "cliptree205_%s.json" % a.nid)
    doc = dict(nid=a.nid, pads={})
    if os.path.exists(cert) and not a.force:
        try:
            doc = json.load(open(cert, encoding="utf-8"))
        except Exception:
            doc = dict(nid=a.nid, pads={})
    for pad in a.pads.split(","):
        prev = doc["pads"].get(pad)
        if prev and prev.get("verdict") in ("DEAD", "ALIVE") and not a.force:
            print("   %s pad: cached %s" % (pad, prev["verdict"]), flush=True)
            if prev["verdict"] == "DEAD":
                break
            continue
        r = run_pad(doc, a.nid, pad, a.wall, cert, rounds=a.rounds, depth_cap=a.depth, node_cap=a.nodes)
        if r["verdict"] == "DEAD":
            break
    try:
        print("   gallery: %s" % fig205.gallery(), flush=True)
    except Exception as e:                                        # noqa: BLE001
        print("   gallery failed: %r" % (e,), flush=True)
