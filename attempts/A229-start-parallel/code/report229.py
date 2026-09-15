"""A229 -- write results/verify229.md from what code/verify229.sh left in certs/verify (stdlib only, no runs).

    python report229.py [NID] [PAD]   > attempts/A229-start-parallel/results/verify229.md
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
A229 = os.path.abspath(os.path.join(HERE, ".."))
V = os.path.join(A229, "certs", "verify")


def stamp(name):
    p = os.path.join(V, "%s.done" % name)
    if not os.path.exists(p):
        return None, None
    txt = open(p, encoding="utf-8").read().strip()
    rc = sec = None
    for tok in txt.split():
        if tok.startswith("rc="):
            rc = tok[3:]
        if tok.startswith("seconds="):
            sec = float(tok[8:])
    return rc, sec


def cert(d, nid, tag=""):
    p = os.path.join(V, d, "coarsetree211_%s%s.json" % (nid, tag))
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:                                             # noqa: BLE001
        return None


def run_of(doc, pad):
    return ((doc or {}).get("runs") or {}).get("%s_page" % pad) or {}


def line(doc, pad):
    d = run_of(doc, pad)
    sk = [u for u in (d.get("undecided") or []) if "SKIPPED (filter)" in str(u.get("reason") or "")]
    return dict(verdict=d.get("verdict"), seconds=d.get("seconds"), n_nodes=d.get("n_nodes"),
                dead_leaves=d.get("dead_leaves"), alive_leaves=d.get("alive_leaves"),
                inherited_dead=d.get("inherited_dead"), n_starts=len(d.get("start_nodes") or []),
                ran=[r.get("label") for r in (d.get("runs") or [])], skipped=len(sk), wall=bool(d.get("wall")),
                filt=d.get("start_filter"))


def main():
    nid = sys.argv[1] if len(sys.argv) > 1 else "k5_16_interior_Y0500"
    pad = sys.argv[2] if len(sys.argv) > 2 else "g1"
    starts = []
    if os.path.exists(os.path.join(V, "starts.txt")):
        starts = [x.strip() for x in open(os.path.join(V, "starts.txt"), encoding="utf-8") if x.strip()]
    out = []
    w = out.append
    w("# A229 -- verification: one page run WHOLE vs the same page run as three `--start` SHARDS, merged")
    w("")
    w("Page `%s`, pad `%s`, isolated certificate directories under `attempts/A229-start-parallel/certs/verify/`," % (nid, pad))
    w("isolated results jsonl `results/verify229.jsonl`, `--no-fig`; the pass-6 workers and their pages untouched.")
    w("Driver `code/verify229.sh` (resumable), comparison `code/test_inherit_multi229.py --compare`.")
    w("")
    w("## The shared prior state (phase `base`)")
    rc, sec = stamp("base")
    b = line(cert("base", nid), pad)
    w("")
    w("A short wall in an EMPTY certificate directory, so the A211 sources are only what this run wrote:")
    w("verdict **%s**%s, %.0f s, %d nodes, %d inherited dead, %d start node(s) offered."
      % (b["verdict"], " at the WALL" if b["wall"] else "", sec or 0.0, b["n_nodes"] or 0, b["inherited_dead"] or 0, b["n_starts"]))
    w("")
    w("Its %d start node(s), longest-first (`queue229.py`): `%s`." % (len(starts), "`, `".join(starts) or "-"))
    w("")
    w("## The two ways of running it")
    w("")
    w("| run | wall | verdict | s | nodes | dead leaves | alive leaves | start nodes run | skipped (filter) |")
    w("|---|---|---|---|---|---|---|---|---|")
    rcw, secw = stamp("whole")
    ww = line(cert("whole", nid), pad)
    w("| whole (1 process) | %.0f | %s%s | %d | %d | %s | %s | %d | %d |"
      % (secw or 0.0, ww["verdict"], " (WALL)" if ww["wall"] else "", ww["seconds"] or 0, ww["n_nodes"] or 0,
         ww["dead_leaves"], ww["alive_leaves"], len(ww["ran"]), ww["skipped"]))
    tot = 0.0
    mx = 0.0
    for k in (1, 2, 3):
        rck, seck = stamp("s%d" % k)
        s = line(cert("s%d" % k, nid, "__s%d" % k), pad)
        tot += seck or 0.0
        mx = max(mx, seck or 0.0)
        w("| shard s%d `--start %s` | %.0f | %s%s | %d | %d | %s | %s | %d | %d |"
          % (k, ",".join(s["filt"] or []), seck or 0.0, s["verdict"], " (WALL)" if s["wall"] else "",
             s["seconds"] or 0, s["n_nodes"] or 0, s["dead_leaves"], s["alive_leaves"], len(s["ran"]), s["skipped"]))
    w("")
    w("Sequential total of the three shards **%.0f s**; the longest shard **%.0f s** -- that is the wall the three would" % (tot, mx))
    w("have taken RUN IN PARALLEL, against **%.0f s** for the whole page in one process (speed-up x%.2f).  The shards were" % (secw or 0.0, (secw or 0.0) / mx if mx else 0.0))
    w("run one after another here so that at most one test python of this campaign ran at a time beside the live pass-6")
    w("workers; each had its own certificate directory holding only the shared `base` certificate, so none of them saw a")
    w("sibling's work -- exactly the state three simultaneous processes would have had.")
    w("")
    w("## The check (`--compare whole merge`)")
    w("")
    w("`certs/verify/merge/` = the `base` certificate + the three shard certificates `coarsetree211_%s__s{1,2,3}.json`." % nid)
    w("`inherit211.merge` is run over that directory and over `certs/verify/whole/`; the two must agree on")
    w("")
    w("* the set of **DEAD path keys** (every branch closed, whichever file closed it -- Lemma INHERIT (a), file-wise), and")
    w("* the set of **next START nodes** (what the following pass would run).")
    w("")
    w("```")
    lg = os.path.join(A229, "logs", "verify229.log")
    if os.path.exists(lg):
        keep = [x.rstrip() for x in open(lg, encoding="utf-8") if (" OK " in x or " FAIL " in x or "comparison rc=" in x
                                                                   or "merge dir:" in x or "start node(s) at pad" in x)]
        out.extend(keep[-14:])
    w("```")
    w("")
    w("Proof that this is the right check: `notes/parallel229.md` Lemma PAR and its corollary.")
    sys.stdout.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
