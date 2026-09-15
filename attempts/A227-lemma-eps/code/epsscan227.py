"""A227 -- the OFFLINE replay of Rule EPS over every recorded node of an existing A211 certificate (its snapshots,
padded outward exactly as snapscan224 does, so a superset of each node's hypothesis).

    python epsscan227.py <nid> [<nid> ...] [--run g1_page] [--out ../results/eps227.jsonl] [--only-label L]

One jsonl row per node with at least one near-simple candidate: the candidates, per candidate the targets of
(F, C), the struck roles, the survivors with the target they reach, the anonymous cells kept, and the verdict.
Resumable: nodes already in --out (same nid, run, label) are skipped.
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
sys.path.insert(0, HERE)
import snapscan224 as SC                                       # noqa: E402  READ-ONLY (A224): the shim page + paths
import eps227 as E                                             # noqa: E402


class Page(SC.ShimPage):
    def __init__(self, doc, node, pad):
        SC.ShimPage.__init__(self, doc, node, pad)
        self.cells = [dict(rect=list(r)) for r in (doc.get("cells") or [])]


def scan_node(doc, node, pad):
    pg = Page(doc, node, pad)
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


def done_keys(out):
    keys = set()
    if out and os.path.exists(out):
        for ln in open(out, encoding="utf-8"):
            try:
                d = json.loads(ln)
                keys.add((d.get("nid"), d.get("pad"), d.get("label")))
            except Exception:                                  # noqa: BLE001
                pass
    return keys


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
    seen = done_keys(out)
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
    lost = [r for r in rows if any(c["struck"] for c in r["cands"])]
    log("   %s %s: %d snapshot node(s) (%d already done), %d with a candidate, %d lost a meeter, %d KILL(s) by FC+EPS%s" % (
        nid, run, n, skipped, len(rows), len(lost), len(kills),
        (" -- " + "; ".join("%s d%s (recorded %s) %s@%s" % (r["label"], r["depth"], r["verdict_recorded"], r["kill"]["role"], r["kill"]["slot"])
                            for r in kills[:6])) if kills else ""))
    return rows


if __name__ == "__main__":
    SC.belownormal()
    ap = argparse.ArgumentParser()
    ap.add_argument("nid", nargs="+", help="page ids, or ALL for every A211 certificate")
    ap.add_argument("--run", default="g1_page")
    ap.add_argument("--out", default=os.path.join(HERE, "..", "results", "eps227.jsonl"))
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
    print("== %d node(s) with a candidate, %d FC+EPS kill(s) over %d page(s) in %.0f s" % (
        len(tot), sum(1 for r in tot if r.get("verdict") == "DEAD"), len(nids), time.time() - T0))
