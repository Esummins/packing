"""A230 -- the OFFLINE re-scan of Rule EPS (A230: all candidates, smallest box first, the polygon taper, the
NS-at-wedge split) over every recorded node of an existing A211 certificate, exactly A227's replay harness with
epsns230.evaluate in place of eps227.evaluate.

    python epsscan230.py <nid> [<nid> ...] [--run g1_page] [--out ../results/eps230.jsonl] [--only-label L]

One jsonl row per node with at least one candidate: the candidates (with `only_new` marking the ones A224's
centre-and-every-piece filter did NOT return), the targets of (F, C) with a flag for the ones carrying an exact
polygon, the struck roles, the survivors with the targets they reach, the anonymous cells, the taper counters,
the verdict, and the NS-at-wedge split where one blocker survives.  Resumable: nodes already in --out are skipped.
"""
import argparse
import glob
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "attempts", "A224-snap-rule", "code"))
sys.path.insert(0, os.path.join(ROOT, "attempts", "A227-lemma-eps", "code"))
sys.path.insert(0, HERE)
import snapscan224 as SC                                       # noqa: E402  READ-ONLY (A224): the shim page + paths
import epsscan227 as SC7                                       # noqa: E402  READ-ONLY (A227): the shim Page subclass
import epsns230 as E                                           # noqa: E402


def scan_node(doc, node, pad):
    pg = SC7.Page(doc, node, pad)
    if not pg.roles or not pg.slots:
        return None
    t0 = time.time()
    r = E.evaluate(pg, node.get("label"))
    if r is None:
        return None
    r.update(nid=doc["nid"], pad=pad, depth=node.get("depth"), verdict_recorded=node.get("verdict"),
             clip_recorded=node.get("clip"), kind=node.get("kind"), role_cell=pg.role_cell, n_free=pg.n_free,
             seconds=round(time.time() - t0, 3))
    return r


def scan(nid, run, out, only=None, log=print):
    f = os.path.join(SC.CERTS, "coarsetree211_%s.json" % nid)
    if not os.path.exists(f):
        log("   %s: no certificate" % nid)
        return []
    doc = json.load(open(f, encoding="utf-8"))
    d = (doc.get("runs") or {}).get(run)
    if not d:
        log("   %s: no run %s" % (nid, run))
        return []
    pad = d.get("pad") or run.split("_")[0]
    seen = SC7.done_keys(out)
    rows, n, skipped = [], 0, 0
    for node in d.get("nodes") or []:
        if not node.get("snapshot") or (only and node.get("label") != only):
            continue
        n += 1
        if (nid, pad, node.get("label")) in seen:
            skipped += 1
            continue
        r = scan_node(doc, node, pad)
        if r:
            rows.append(r)
            if out:
                os.makedirs(os.path.dirname(out), exist_ok=True)
                with open(out, "a", encoding="utf-8") as fh:
                    fh.write(json.dumps(r, default=str) + "\n")
    kills = [r for r in rows if r.get("verdict") == "DEAD"]
    wns = [r for r in rows if r.get("wedge_ns")]
    log("   %s %s: %d snapshot node(s) (%d done), %d with a candidate (%d cand., %d added by A230), %d KILL(s), "
        "%d NS-at-wedge%s" % (nid, run, n, skipped, len(rows), sum(r["n_cands"] for r in rows),
                              sum(r["n_added"] for r in rows), len(kills), len(wns),
                              (" -- " + "; ".join("%s d%s %s@%s" % (r["label"], r["depth"], r["kill"]["role"], r["kill"]["slot"])
                                                  for r in kills[:6])) if kills else ""))
    return rows


if __name__ == "__main__":
    SC.belownormal()
    ap = argparse.ArgumentParser()
    ap.add_argument("nid", nargs="+", help="page ids, or ALL for every A211 certificate")
    ap.add_argument("--run", default="g1_page")
    ap.add_argument("--out", default=os.path.join(HERE, "..", "results", "eps230.jsonl"))
    ap.add_argument("--only-label", dest="only", default=None)
    a = ap.parse_args()
    nids = a.nid
    if nids == ["ALL"]:
        nids = sorted(os.path.basename(f)[len("coarsetree211_"):-len(".json")]
                      for f in glob.glob(os.path.join(SC.CERTS, "coarsetree211_*.json")))
    out = os.path.abspath(a.out) if a.out and a.out != "-" else None
    tot = []
    T0 = time.time()
    for nid in nids:
        tot += scan(nid, a.run, out, only=a.only)
    print("== %d node(s) with a candidate, %d FC+EPS kill(s), %d NS-at-wedge split(s) over %d page(s) in %.0f s" % (
        len(tot), sum(1 for r in tot if r.get("verdict") == "DEAD"), sum(1 for r in tot if r.get("wedge_ns")),
        len(nids), time.time() - T0), flush=True)
