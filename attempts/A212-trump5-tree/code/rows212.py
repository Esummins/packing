"""A212 -- the certificate / row / page helpers of run212 (run211's save / draw / row_of / inherited_rows, re-pathed)."""
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CERTS = os.path.abspath(os.path.join(HERE, "..", "certs"))
RES = os.path.abspath(os.path.join(HERE, "..", "results", "trump5tree212.jsonl"))
VERIFIER = ("[C: closed-form / library clip trace + the leaf lemma (Lemma CORNER-COVER / A189 Lemma 1 / Lemma CN / Lemma BASIN) + Lemma INHERIT; a TRUMP-TUBE leaf: exact containment "
            "of the pieces in the tube box + Theorem T1 (certs/verify_tube.py)] A212 trump5 tree (notes/trump5_tree.md): A211's coarse tree at PAD 0 ONLY (lam = 1, s0-only) with the "
            "Trump-containment GATE (a node holding a D4 image of z-hat embedded at s0 is never submitted to a kill rule: branched at once), the TUBE LEAF (all 11 named, pieces inside "
            "the certified tube radii: uniqueness, not a kill) and the ALIGNED split (Lemma ROLE-SPLIT cut at the tube wall); DEAD iff every branch DEAD (Lemma CT); no verifier clause")
NOFIG = [False]


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
    if NOFIG[0]:
        return
    try:
        import fig212
        return fig212.render(doc)
    except Exception as e:                                        # noqa: BLE001
        import traceback
        traceback.print_exc()
        print("   fig212 failed: %r" % (e,), flush=True)


def page_doc(doc, pg, FP):
    doc.setdefault("cells", [FP.rect_f(c["rect"]) for c in pg.cells])
    doc.setdefault("slots", list(pg.slots))
    doc.setdefault("wbox", {p: FP.rect_f(pg.item[p]["wb"]) for p in pg.slots})
    doc.setdefault("wbox_pad", {})[pg.pad] = {p: FP.rect_f(pg.item[p]["wb"]) for p in pg.slots}
    doc.setdefault("H_record", [round(v, 6) for v in pg.record_H])


def brief_nodes(nodes):
    return [dict(label=n["label"], depth=n.get("depth"), verdict=n.get("verdict"), clip=n.get("clip"), kind=n.get("kind"), seconds=n.get("seconds"),
                 coarse=n.get("coarse"), n_roles=len(n.get("roles") or {}), gate=bool((n.get("trump_gate") or {}).get("contains")),
                 g=(n.get("trump_gate") or {}).get("g"), tube_depth=n.get("tube_depth"), reason=str(n.get("reason") or "")[:80]) for n in nodes]


def row_of(doc, key, cert, res=None):
    d = doc["runs"][key]
    gated = [n for n in (d.get("nodes") or []) if (n.get("trump_gate") or {}).get("contains")]
    slim = dict(nid=doc["nid"], cls=doc.get("cls"), record=doc.get("record"), tree=doc.get("tree"), applies_to_tags=[doc.get("tree")] if doc.get("tree") else [],
                run=key, pad=d.get("pad"), mode="page", source=d.get("source"), cfg=d.get("cfg"), lam=d.get("lam"), verdict=d.get("verdict"), leaf=d.get("leaf"),
                n_nodes=d.get("n_nodes"), n_records=d.get("n_records"), max_depth=d.get("max_depth"), alive_leaves=d.get("alive_leaves"), dead_leaves=d.get("dead_leaves"),
                tube_leaves=d.get("tube_leaves"), tube_depth=(min(d.get("tube_depths") or [None]) if d.get("tube_depths") else None), tube_depths=d.get("tube_depths"),
                tube_nodes=d.get("tube_nodes"), gate_hits=d.get("gate_hits"), gate_conflicts=d.get("gate_conflicts"), gate_root=d.get("gate_root"), aligned_cuts=d.get("aligned_cuts"),
                gated_nodes=[dict(label=n["label"], depth=n.get("depth"), g=n["trump_gate"].get("g"), verdict=n.get("verdict")) for n in gated][:60],
                ns_splits=d.get("ns_splits"), pocket_splits=d.get("pocket_splits"), cc_kills=d.get("cc_kills"), exact_rounds=d.get("exact_rounds"), basin_kills=d.get("basin_kills"),
                rsplits=d.get("rsplits"), rsplit_kills=d.get("rsplit_kills"),
                kills_by_rule=d.get("kills_by_rule"),
                noroom=[dict(label=r["label"], k=r["k"], verdict=r["verdict"], clip=r["clip"], seconds=r["seconds"], gated=r.get("gated")) for r in (d.get("noroom_runs") or [])],
                inherited_dead=d.get("inherited_dead"), inherited_alive=d.get("inherited_alive"), n_inherited=d.get("n_inherited"),
                inherit_sources=[dict(camp=e.get("camp"), label=e.get("label"), rule=e.get("rule"), cert=e.get("cert"), ledger=e.get("ledger"))
                                 for e in ((d.get("inherit") or {}).get("inherited_dead") or [])],
                start_nodes=d.get("start_nodes"), start_runs=d.get("runs"), killing=d.get("killing"), undecided=d.get("undecided"), seconds=d.get("seconds"), root=d.get("root"),
                wall=d.get("wall"), s0_only=True, window_pending=None, stage0=doc.get("stage0"), verdicts=doc.get("verdicts"), stage_reached=doc.get("stage_reached"),
                nodes_brief=brief_nodes(d.get("nodes") or []), verifier=VERIFIER, cert=os.path.relpath(cert, ROOT).replace("\\", "/"), when=time.strftime("%Y-%m-%d %H:%M:%S"))
    res = res or RES
    os.makedirs(os.path.dirname(res), exist_ok=True)
    with open(res, "a", encoding="utf-8") as f:
        f.write(json.dumps(slim, default=str) + "\n")
    return slim


def inherited_rows(M):
    rows = []
    for e in M["info"]["inherited_dead"]:
        p = e["path"]
        rows.append(dict(label=e["label"], depth=e["n_steps"], slot=(p[-1][1] if p else None), kind="inherited", rows=(p[-1][2] if p else None),
                         named=None, verdict="DEAD", clip="INHERIT", killed_round=None, seconds=0.0, t=0.0, n_rounds=0, snapshot=None,
                         source_cert=e["cert"], source_label=e["label"], source_camp=e["camp"], source_rule=e["rule"], source_ledger=e.get("ledger"),
                         source_path=["%s<-%s" % (s[1], s[2]) for s in p], path_key=e.get("key"),
                         reason="inherited DEAD (final) from %s %s" % (e["camp"], e["cert"]),
                         leaf="Lemma INHERIT (A211 notes/coarse_tree.md s.4): the hypothesis %s is refuted by %s [%s] -- %s" % (
                             "; ".join("%s<-%s" % (s[1], s[2]) for s in p), e["camp"], e["rule"], e["cert"]),
                         verifier="[C: library clip trace] inherited (Lemma INHERIT): %s" % e["cert"]))
    return rows


def kills_by_rule(nodes):
    out = {}
    for n in nodes:
        if n.get("verdict") == "DEAD":
            out[n.get("clip") or "?"] = out.get(n.get("clip") or "?", 0) + 1
    return out
