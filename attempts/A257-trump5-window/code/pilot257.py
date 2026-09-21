"""A257 -- the SEAM PILOT (BRIEF.md task 2): what does it cost to hand the near-Trump siblings to the tube?

Two phases over ONE synthetic Trump-containing trump5 page at slack pins (code/synth257.py), at a WINDOW pad:

  SPINE   Tree257 with `spine=True`: at every gated fully named node the aligned split (A212 s.3, ported in
          tree257.py) cuts at the tube wall and ONLY the child that holds the image is expanded; the other child --
          the NEAR-TRUMP SIBLING, a node just outside the tube radii -- is recorded and left for phase B.  Measures:
          how many aligned cuts reach the tube, and whether Lemma TUBE-KILL then closes the image child.
  SIBLING for each sibling, a fresh run of the SAME page with `only = <sibling label>`: the spine is replayed (its
          cascades are re-run, which is the honest cost) and then the sibling's subtree gets the wall, with A211's
          ORDINARY rules -- the gate is false there, so every kill rule applies.  Measures: dies / does not, by
          which rule, in how long.  The siblings that do not die are the SEAM GAP (delta_LP vs delta_basin).

LAUNCH-AND-EXIT: one python process, a STOP file (logs/STOP), a journal after every phase (results/pilot257.jsonl)
and resume = re-run the same command line (rows already in the journal are skipped)."""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ATT = os.path.abspath(os.path.join(HERE, ".."))
CERTS, RESULTS, LOGS = os.path.join(ATT, "certs"), os.path.join(ATT, "results"), os.path.join(ATT, "logs")
JOURNAL, STOP = os.path.join(RESULTS, "pilot257.jsonl"), os.path.join(LOGS, "STOP")
A256 = os.path.join(ROOT, "attempts", "A256-trump5-passes", "code")
A211 = os.path.join(ROOT, "attempts", "A211-coarse-tree", "code")


def setup():
    """A256's shadow install (run256.install_shadows: A211's chain with A256's load211/poly204/stage209/inherit211),
    then A257's code dir in front and A257's own certificate directory -- A256's and A211's are never written."""
    os.environ["A229_CERT_DIR"] = CERTS
    os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    for p in (A211, A256, HERE):
        while p in sys.path:
            sys.path.remove(p)
    sys.path[:0] = [HERE, A256, A211]
    import run256                                              # noqa: E402  READ-ONLY (A256)
    run256.install_shadows()
    sys.path.insert(0, HERE)
    import stage209                                            # noqa: E402
    stage209.CERTS = CERTS
    stage209.READ_DIRS = [CERTS] + list(stage209.READ_DIRS)
    import load257                                             # noqa: E402
    load257.install()
    import coarse211 as C11                                    # noqa: E402
    C11.install()
    return stage209


def belownormal():
    try:
        import ctypes
        k = ctypes.windll.kernel32
        k.SetPriorityClass.argtypes = [ctypes.c_void_p, ctypes.c_uint]
        k.SetProcessAffinityMask.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
        h = ctypes.c_void_p(-1)
        k.SetPriorityClass(h, 0x00004000)
        k.SetProcessAffinityMask(h, 0xFFFF)
    except Exception as e:                                     # noqa: BLE001
        print("   belownormal failed: %r" % (e,), flush=True)


def journal(row):
    os.makedirs(RESULTS, exist_ok=True)
    with open(JOURNAL, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, default=str) + "\n")


def done_rows(nid, pad):
    out = {}
    if os.path.exists(JOURNAL):
        for ln in open(JOURNAL, encoding="utf-8"):
            ln = ln.strip()
            if not ln:
                continue
            try:
                r = json.loads(ln)
            except Exception:
                continue
            if r.get("nid") == nid and r.get("pad") == pad:
                out[(r.get("phase"), r.get("only"))] = r
    return out


def save(doc, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, default=str)
    os.replace(tmp, path)


def one_run(S9, nid, pad, wall, only=None, spine=False, tag="spine", depth=8, nodes=600, log=print):
    """ONE Tree257 over the page (A211's run211.run_tree without Lemma INHERIT: the pilot is a measurement, so it
    always starts from the page's own A203 stage-0 root and never merges or writes a campaign certificate)."""
    import poly204 as P
    import clip207 as C
    import coarse211 as C11
    import tree257 as N57
    FP, QP = P.FP, P.QP
    s0 = S9.stage0(nid, pad, log=log)
    if s0["verdict"] == "DEAD":
        return dict(verdict="DEAD (stage 0)", leaf=s0.get("leaf"), n_nodes=0, seconds=s0.get("seconds"), stage0=s0)
    T = FP.Trace(wall=wall)
    rec, cls, row = FP.load_page(nid)
    start = S9.start_of(nid, pad)
    basins = C.load_basins(cls, pad, QP.PADS[pad]) if pad != "zero" else []
    pg = C11.CoarsePage(rec, cls, nid, T, pad=pad, start=start, basins=basins)
    log("== %s pad %s [%s]: lam %s, H %s, %d slots, %d free squares, delta_pin %s; wall %.0f s%s" % (
        nid, pad, tag, float(pg.lam), [round(v, 4) for v in pg.roles[pg.H]], len(pg.slots), pg.n_free,
        sorted({round(p["dpin"], 8) for p in rec["pins"]}), wall, (" only=%s" % only) if only else ""))
    tree = N57.Tree257(pg, spine=spine, rounds=1, depth_cap=depth, node_cap=nodes, log=log, root_label="R", only=only)
    out = tree.run()
    out["nodes_brief"] = [dict(label=n["label"], depth=n.get("depth"), verdict=n.get("verdict"), clip=n.get("clip"),
                               kind=n.get("kind"), seconds=n.get("seconds"), gate=bool((n.get("trump_gate") or {}).get("contains")),
                               n_anon=n.get("n_anon"), reason=str(n.get("reason") or "")[:200],
                               leaf=str(n.get("leaf") or "")[:300]) for n in tree.nodes]
    out["tube_nodes"] = [n for n in tree.nodes if n.get("verdict") in ("TUBE-KILL", "TRUMP-TUBE")]
    out["seconds"], out["cls"], out["record"] = round(T.now(), 1), cls, row.get("record")
    out["wall_hit"] = bool(T.out_of_time())
    out["tests"] = T.tests[-1500:]
    return out


def sibling_verdict(out, sib):
    """the subtree under `sib`: DEAD (and by which rule, at what time) or ALIVE / undecided."""
    sub = [n for n in out.get("nodes_brief") or [] if n["label"] == sib or
           (n["label"].startswith(sib) and n["label"][len(sib):][:1] in ".rusx")]
    alive = [n for n in sub if n.get("verdict") == "ALIVE"]
    dead = [n for n in sub if n.get("verdict") == "DEAD"]
    secs = round(sum(float(n.get("seconds") or 0.0) for n in sub), 1)
    root = next((n for n in sub if n["label"] == sib), None)
    closed = bool(sub) and not alive and bool(dead)
    return dict(sibling=sib, n_nodes=len(sub), seconds=secs, closed=closed,
                verdict=("DEAD" if closed else ("ALIVE" if alive else ("NOT REACHED" if not sub else "UNDECIDED"))),
                rules=sorted({n["clip"] for n in dead if n.get("clip")}),
                first_kill=next((dict(label=n["label"], clip=n.get("clip"), seconds=n.get("seconds"),
                                      leaf=n.get("leaf")) for n in sub if n.get("verdict") == "DEAD"), None),
                alive_leaves=[dict(label=n["label"], reason=n.get("reason")) for n in alive][:8],
                root=dict(verdict=(root or {}).get("verdict"), clip=(root or {}).get("clip"),
                          seconds=(root or {}).get("seconds")) if root else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nid", default=None, help="default: build / reuse the synthetic page at --dpin")
    ap.add_argument("--pad", default="g1")
    ap.add_argument("--dpin", type=float, default=0.01)
    ap.add_argument("--wall-spine", dest="wall_spine", type=float, default=5400.0)
    ap.add_argument("--wall-sib", dest="wall_sib", type=float, default=1800.0)
    ap.add_argument("--depth", type=int, default=8)
    ap.add_argument("--nodes", type=int, default=600)
    ap.add_argument("--max-siblings", dest="max_sib", type=int, default=40)
    ap.add_argument("--phase", default="all", choices=("spine", "siblings", "all"))
    ap.add_argument("--journal", default=None, help="a SMOKE run points the journal / certificates elsewhere")
    ap.add_argument("--only-sibling", dest="only_sib", default=None,
                    help="run exactly ONE near-Trump sibling (the launcher's shard: one process, one commit)")
    ap.add_argument("--list-siblings", dest="list_sib", action="store_true",
                    help="print the spine's sibling labels from the journal and exit (no chain import)")
    a = ap.parse_args()
    if a.journal:
        global JOURNAL, CERTS
        JOURNAL = os.path.abspath(a.journal)
        CERTS = os.path.dirname(JOURNAL)
    if a.list_sib:
        nid = a.nid or "synth257_d%s_h002_t2" % ("%g" % a.dpin).replace(".", "")
        sp = (done_rows(nid, a.pad).get(("spine", None)) or {})
        for s in (sp.get("siblings") or []):
            print(s["sibling"])
        return
    belownormal()
    S9 = setup()
    import synth257
    nid = a.nid or synth257.build(a.dpin)[0]
    if not a.nid:
        synth257.build(a.dpin)
    have = done_rows(nid, a.pad)
    print("== A257 seam pilot: %s pad %s (journal has %d row(s))" % (nid, a.pad, len(have)), flush=True)

    spine = (have.get(("spine", None)) or {}).get("out")
    if a.phase in ("spine", "all") and spine is None:
        t0 = time.time()
        out = one_run(S9, nid, a.pad, a.wall_spine, only=None, spine=True, tag="spine", depth=a.depth, nodes=a.nodes)
        save(dict(nid=nid, pad=a.pad, phase="spine", out=out,
                  runs={"%s_spine" % a.pad: dict(pad=a.pad, mode="pilot-spine", nodes=out.get("tube_nodes") or [],
                                                 verifier="[V: certs/verify_tubekill257.py]")}),
             os.path.join(CERTS, "pilot257_%s_%s_spine.json" % (nid, a.pad)))
        row = dict(nid=nid, pad=a.pad, phase="spine", only=None, verdict=out.get("verdict"),
                   aligned_cuts=out.get("aligned_cuts"), tube_kills=out.get("tube_kills"), gate_hits=out.get("gate_hits"),
                   gate_conflicts=out.get("gate_conflicts"), n_nodes=out.get("n_nodes"), seconds=out.get("seconds"),
                   wall_hit=out.get("wall_hit"), siblings=out.get("sibling_rows"), tube_tries=out.get("tube_tries"),
                   when=time.strftime("%Y-%m-%d %H:%M:%S"), wall=a.wall_spine,
                   elapsed=round(time.time() - t0, 1), out=out)
        journal(row)
        spine = out
        print("   SPINE: %s -- %d aligned cut(s), %d TUBE-KILL(s), %d gate hit(s), %d node(s), %.0f s%s" % (
            out.get("verdict"), out.get("aligned_cuts") or 0, out.get("tube_kills") or 0, out.get("gate_hits") or 0,
            out.get("n_nodes") or 0, out.get("seconds") or 0, " (WALL)" if out.get("wall_hit") else ""), flush=True)

    if a.phase == "spine" or spine is None:
        return
    sibs = [s["sibling"] for s in (spine.get("sibling_rows") or [])][:a.max_sib]
    if a.only_sib:
        sibs = [s for s in sibs if s == a.only_sib] or [a.only_sib]
    print("   %d near-Trump sibling(s) to run: %s" % (len(sibs), sibs), flush=True)
    for sib in sibs:
        if os.path.exists(STOP):
            print("   STOP present: exiting before sibling %s" % sib, flush=True)
            return
        if ("sibling", sib) in have:
            print("   sibling %s: already in the journal (%s)" % (sib, have[("sibling", sib)].get("verdict")), flush=True)
            continue
        t0 = time.time()
        out = one_run(S9, nid, a.pad, a.wall_sib, only=sib, spine=False, tag="sibling %s" % sib,
                      depth=a.depth, nodes=a.nodes)
        v = sibling_verdict(out, sib)
        save(dict(nid=nid, pad=a.pad, phase="sibling", sibling=sib, verdict=v, out=out),
             os.path.join(CERTS, "pilot257_%s_%s_sib_%s.json" % (nid, a.pad, sib.replace(".", "_"))))
        journal(dict(nid=nid, pad=a.pad, phase="sibling", only=sib, verdict=v["verdict"], rules=v["rules"],
                     seconds=v["seconds"], n_nodes=v["n_nodes"], first_kill=v["first_kill"],
                     alive_leaves=v["alive_leaves"], run_seconds=out.get("seconds"), wall=a.wall_sib,
                     wall_hit=out.get("wall_hit"), elapsed=round(time.time() - t0, 1),
                     when=time.strftime("%Y-%m-%d %H:%M:%S"), out=out))
        print("   SIBLING %-12s %-9s by %s in %.0f s (subtree %d node(s); run %.0f s%s)" % (
            sib, v["verdict"], ",".join(v["rules"]) or "-", v["seconds"], v["n_nodes"], out.get("seconds") or 0,
            " WALL" if out.get("wall_hit") else ""), flush=True)
    print("== A257 seam pilot: done", flush=True)


if __name__ == "__main__":
    main()
