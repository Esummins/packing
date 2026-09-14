"""A212 driver -- the TRUMP5 TREE on one trump5 node (a gallery page or an A60 frontier record), PAD 0 ONLY:
   python run212.py page <nid> [--wall 1800] [--depth 6] [--nodes 600] [--force]
stage 0 (A202 closed form + A203 CSP, computed here for the trump5 pages: certs/csp209_<nid>_zero_s0.json), then Tree212
(tree212: A211's coarse tree + the Trump-containment gate + the tube leaf + the aligned split; notes/trump5_tree.md).
Verdict DEAD / TRUMP-TUBE / ALIVE (s0-only, lam = 1; no window-pending label).  One certificate per node
certs/trump5tree212_<nid>.json, one row per run in results/trump5tree212.jsonl, the page
docs/residue_map/campaigns/A212-trump5tree/trump5tree212_<nid>.svg.  run211.py adapted; the gate decision is recorded on
every node record (`trump_gate`) and on the page row (`gate_root`, `gate_hits`, `gated_nodes`)."""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import load212                                                 # noqa: E402
load212.install()
import stage209                                                # noqa: E402
import poly204 as P                                            # noqa: E402
import tree206 as N6                                           # noqa: E402
import clip207 as C                                            # noqa: E402
import coarse211 as C11                                        # noqa: E402
import tree211 as N11                                          # noqa: E402
import tree212 as N12                                          # noqa: E402
import inherit211 as INH                                       # noqa: E402
import startload211 as SL                                      # noqa: E402
import trump212 as TR                                          # noqa: E402
import rows212 as RW                                           # noqa: E402

C11.install()
FP, QP = P.FP, P.QP
CERTS, VERIFIER = RW.CERTS, RW.VERIFIER


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


def verdict_of(runs_out):
    v = [r["verdict"] for r in runs_out]
    if any(x == "ALIVE" for x in v):
        return "ALIVE"
    return "TRUMP-TUBE" if any(x == "TRUMP-TUBE" for x in v) else "DEAD"


def run_tree(doc, a, pad, cert, log=print):
    T = FP.Trace(wall=a.wall)
    rec, cls, row = FP.load_page(a.nid)
    start = stage209.start_of(a.nid, pad)
    basins = C.load_basins(cls, pad, QP.PADS[pad]) if pad != "zero" else []
    key = "%s_page" % pad
    M = None if a.no_inherit else INH.merge(a.nid, pad, start.get("file"), log=log)
    base = C11.CoarsePage(rec, cls, a.nid, T, pad=pad, start=start, basins=basins)
    RW.page_doc(doc, base, FP)
    g0 = TR.gate(base)
    rows = RW.inherited_rows(M) if M else []
    starts = list((M or {}).get("starts") or [])
    dead_paths = (M or {}).get("dead_paths") or {}
    d = doc["runs"][key] = dict(pad=pad, mode="page", source=start.get("file"), lam=float(base.lam), start=start, verdict="RUNNING", nodes=list(rows),
                                basins=[C.basin_json(b) for b in basins], verifier=VERIFIER, inherit=(M["info"] if M else None),
                                gate_root=dict(contains=g0["contains"], g=g0["g"], assignment=g0["assignment"], pins=g0["pins"], seconds=g0["seconds"]),
                                inherited_dead=len(rows), inherited_alive=len(starts), start_nodes=[dict(s, steps=len(s["steps"])) for s in starts],
                                cfg=dict(rounds=a.rounds, depth_cap=a.depth, node_cap=a.nodes, wall=a.wall, inherit=not a.no_inherit, pads="zero", lam=1,
                                         trump_split_cap=N12.TRUMP_SPLIT_CAP, tube_cert=TR.radii()["cert"], r_c_eff=float(TR.radii()["r_c_eff"]), r_theta=float(TR.radii()["r_theta"]),
                                         coarse=dict(grid=[C11.NX, C11.NY, C11.NB], cap=C11.CAP, refine=C11.REFINE, max_iter=C11.MAX_ITER, nsub=C11.NSUB, depth=C11.DEPTH, jdepth=C11.JDEPTH, kmode=C11.KMODE),
                                         exact=C11.EXACT, exact_rounds=N11.EXACT_ROUNDS, noroom_cap=N11.NOROOM_CAP, soft_all=N6.SOFT_ALL, max_frac=N6.MAX_FRAC))
    log("== %s pad %s (lam = 1, s0-only): start %s; GATE at the root: %s%s; INHERIT %d dead + %d start nodes; H %s; forced H %s; %d slots; free %d" % (
        a.nid, pad, start.get("file"), "CONTAINS %s %s" % (g0["g"], g0["assignment"]) if g0["contains"] else "no image", "", len(rows), len(starts),
        [round(v, 3) for v in base.roles[base.H]], sorted(base.forced_H), len(base.slots), base.n_free))
    agg = run_starts(doc, d, a, pad, cert, T, rec, cls, start, basins, rows, starts, dead_paths, M is not None, log=log)
    agg["wall"] = T.out_of_time()
    agg["leaf"] = None
    if agg["verdict"] == "DEAD":
        agg["leaf"] = "every branch DEAD (%d inherited + %d proved here; s0-only, lam = 1): " % (len(rows), len(agg["killing"]) - len(rows)) + "; ".join(
            "%s %s<-%s by %s" % (k["label"], k.get("slot") or "root", k.get("rows"), k["clip"]) for k in agg["killing"][:40])
    elif agg["verdict"] == "TRUMP-TUBE":
        agg["leaf"] = "every branch DEAD or a TRUMP-TUBE leaf (%d tube leaves at aligned depths %s; %d kills): the residue of this node at s0 is the Trump image's basin (Lemma TUBE-LEAF)" % (
            agg["tube_leaves"], agg["tube_depths"], len(agg["killing"]))
    agg["kills_by_rule"] = RW.kills_by_rule(d["nodes"])
    agg["tests"], agg["steps"], agg["seconds"] = T.tests[-4000:], T.steps[-2000:], round(T.now(), 1)
    d.update(agg)
    log("   => %s (%s) in %.1f s: %d nodes, depth %d, gate hits %d (conflicts %d), tube leaves %d (depths %s), %d aligned cuts, kills by rule %s, %d NS, %d pockets, %d role splits, %d dead / %d alive leaves%s" % (
        agg["verdict"], key, agg["seconds"], agg["n_nodes"], agg["max_depth"], agg["gate_hits"], agg["gate_conflicts"], agg["tube_leaves"], agg["tube_depths"], agg["aligned_cuts"],
        agg["kills_by_rule"], agg["ns_splits"], agg["pocket_splits"], agg["rsplits"], agg["dead_leaves"], agg["alive_leaves"], " (WALL)" if agg["wall"] else ""))
    log("   per node: " + "; ".join("%s d%s %s%s%s %ss" % (n["label"], n.get("depth"), n.get("verdict"), (" " + n["clip"]) if n.get("clip") else "",
                                                          " [GATE]" if (n.get("trump_gate") or {}).get("contains") else "", n.get("seconds")) for n in d["nodes"]))
    return key, agg["verdict"]


def run_starts(doc, d, a, pad, cert, T, rec, cls, start, basins, rows, starts, dead_paths, have_merge, log=print):
    keys = ("n_nodes", "n_records", "alive_leaves", "dead_leaves", "ns_splits", "pocket_splits", "cc_kills", "exact_rounds", "basin_kills", "rsplits", "rsplit_kills",
            "n_inherited", "gate_hits", "gate_conflicts", "tube_leaves", "aligned_cuts")
    agg = dict({k: 0 for k in keys}, n_records=len(rows), dead_leaves=len(rows), n_inherited=len(rows), max_depth=0, tube_depths=[], tube_nodes=[],
               killing=[dict(label=r["label"], slot=r["slot"], rows=r["rows"], clip="INHERIT", round=None, seconds=0.0, cert=r["source_cert"]) for r in rows],
               undecided=[], noroom_runs=[], inherited={}, runs=[], root=None, basin_clips=[], gate_log=[])
    done, outs = [], []
    for sn in (starts if have_merge else [None]):
        lab = (sn or {}).get("label", "R")
        if T.out_of_time():
            agg["undecided"].append(dict(label=lab, reason="undecided: the wall ran out before this start node ran"))
            outs.append(dict(verdict="ALIVE"))
            continue
        try:
            pg, meta = (SL.load(sn, rec, cls, a.nid, T, pad, start, basins, rounds=a.rounds, log=log) if sn else
                        (C11.CoarsePage(rec, cls, a.nid, T, pad=pad, start=start, basins=basins), dict(label="R", path=[], steps=[], applied=[])))
        except Exception as e:                                    # noqa: BLE001
            agg["undecided"].append(dict(label=lab, reason="undecided: the start node could not be loaded soundly (%r)" % (e,)))
            outs.append(dict(verdict="ALIVE"))
            continue

        def on_node(tree):
            d["nodes"] = rows + done + tree.nodes
            d.update(n_nodes=agg["n_nodes"] + tree.n_nodes, seconds=round(T.now(), 1))
            RW.save(doc, cert)
            RW.draw(doc)

        tree = N12.Tree212(pg, dead_paths=dead_paths, path0=INH.path_tuple(sn) if sn else (), rounds=a.rounds, depth_cap=a.depth, node_cap=a.nodes, on_node=on_node, log=log, root_label=lab)
        out = tree.run()
        for n in tree.nodes[:1]:
            n.update(start_node=lab, start_cert=(sn or {}).get("cert"), start_camp=(sn or {}).get("camp"), start_meta=meta, path_key=(sn or {}).get("key") or [])
        done += tree.nodes
        outs.append(out)
        agg["runs"].append(dict(label=lab, verdict=out["verdict"], n_nodes=out["n_nodes"], seconds=round(T.now(), 1), cert=(sn or {}).get("cert"), applied=meta.get("applied"), wall=T.out_of_time()))
        if agg["root"] is None:
            r0 = tree.nodes[0] if tree.nodes else {}
            agg["root"] = dict(verdict=r0.get("verdict"), clip=r0.get("clip"), seconds=r0.get("seconds"), n_rounds=r0.get("n_rounds"), kept=r0.get("kept"),
                               forced_H=r0.get("forced_H"), role_slots=r0.get("role_slots"), alive_cells=r0.get("alive_cells"), gate=(r0.get("trump_gate") or {}).get("contains"))
        for k in keys:
            agg[k] = agg.get(k, 0) + (out.get(k) or 0)
        agg["max_depth"] = max(agg["max_depth"], out.get("max_depth") or 0)
        for k in ("killing", "undecided", "noroom_runs", "tube_depths", "tube_nodes", "gate_log"):
            agg[k] += out.get(k) or []
        agg["inherited"].update(out.get("inherited") or {})
        agg["basin_clips"] += list(pg.basin_rep)[-20:]
        log("   start %-12s => %s (%d nodes; t = %.0f s of %s)" % (lab, out["verdict"], out["n_nodes"], T.now(), a.wall))
    agg["verdict"] = verdict_of(outs) if (outs or not have_merge) else "DEAD"
    d["nodes"] = rows + done
    agg["n_records"] = len(d["nodes"])
    return agg


def run_page(doc, a, cert, log=print):
    rec, cls, row = FP.load_page(a.nid)
    doc.update(cls=cls, record=(row.get("record") or "").replace("\\", "/"), tree=row.get("tree") or "trump5_j0", level=row.get("level"), camp=row.get("camp"))
    doc.setdefault("stage0", {})
    doc.setdefault("verdicts", {})
    for pad in a.pads.split(","):
        if pad in doc["verdicts"] and not a.force and doc["verdicts"][pad] != "ALIVE":      # a cached ALIVE (a shorter wall) is re-run; DEAD / TRUMP-TUBE stay
            log("   pad %s: cached %s" % (pad, doc["verdicts"][pad]))
            continue
        s0 = stage209.stage0(a.nid, pad, log=log)
        doc["stage0"][pad] = s0
        doc["stage_reached"] = "0"
        if s0["verdict"] == "DEAD":
            doc["verdicts"][pad] = "DEAD (stage 0)"
            doc["runs"].setdefault("%s_page" % pad, dict(pad=pad, mode="page", source=s0["file"], verdict="DEAD", leaf="stage 0: %s" % s0.get("leaf"), n_nodes=0, seconds=s0.get("seconds"),
                                                            verifier=s0["verifier"], stage0_kill=True, nodes=[], gate_root=None))
            RW.save(doc, cert)
            RW.draw(doc)
            RW.row_of(doc, "%s_page" % pad, cert, RES)
            continue
        RW.save(doc, cert)
        key, v = run_tree(doc, a, pad, cert, log=log)
        doc["verdicts"][pad] = v
        doc["stage_reached"] = "2 (tree)"
        RW.save(doc, cert)
        RW.draw(doc)
        RW.row_of(doc, key, cert, RES)
    log("== %s: pad0 %s   (s0-only, lam = 1; DEAD = killed at s0, TRUMP-TUBE = the Trump basin, ALIVE = undecided)" % (a.nid, doc["verdicts"].get("zero")))


if __name__ == "__main__":
    belownormal()
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("page",))
    ap.add_argument("nid")
    ap.add_argument("--pads", default="zero")
    ap.add_argument("--wall", type=float, default=1800)
    ap.add_argument("--rounds", type=int, default=1)
    ap.add_argument("--depth", type=int, default=6)
    ap.add_argument("--nodes", type=int, default=600)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--no-inherit", dest="no_inherit", action="store_true")
    ap.add_argument("--cert-dir", dest="cert_dir", default=CERTS)
    ap.add_argument("--results", default=RW.RES)
    ap.add_argument("--no-fig", dest="no_fig", action="store_true")
    a = ap.parse_args()
    RES, RW.NOFIG[0] = os.path.abspath(a.results), bool(a.no_fig)
    cert = os.path.join(os.path.abspath(a.cert_dir), "trump5tree212_%s.json" % a.nid)
    doc = dict(nid=a.nid, runs={})
    if os.path.exists(cert) and not a.force:
        try:
            doc = json.load(open(cert, encoding="utf-8"))
        except Exception:
            doc = dict(nid=a.nid, runs={})
    run_page(doc, a, cert)
    if not RW.NOFIG[0]:
        try:
            import fig212
            print("   gallery: %s" % fig212.gallery(), flush=True)
        except Exception as e:                                    # noqa: BLE001
            print("   gallery failed: %r" % (e,), flush=True)
