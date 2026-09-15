"""A229 -- the MULTI-FILE merge test: a page run WHOLE must load back exactly like the same page run as several
`--start` SHARDS whose certificates are merged (notes/parallel229.md; Lemma INHERIT applied file-wise).

Two modes.

  python test_inherit_multi229.py [NID ...] [--pad g1] [--shards 2]
      SPLIT mode (fast, no geometry, the default).  Take the page's REAL A211 certificate, cut the run's node list
      into `--shards` shard certificates the way `run211.py --start ... --cert-suffix TAG` would have written them
      (each shard keeps the inherited rows, its own start nodes' subtrees, and records the other start nodes as
      SKIPPED (filter)), write them to a scratch directory, and check that inherit211's merge over the SHARDS ALONE
      gives the SAME dead path set and the SAME start nodes as the merge over the whole-page certificate.
      That is exactly the claim of notes/parallel229.md: the union of the shards is the page.

  python test_inherit_multi229.py --compare DIR_WHOLE DIR_SHARDS --nid NID --pad g1
      COMPARE mode: the same check between two directories of certificates produced by REAL runs (code/verify229.sh).

Exit 0 iff every check passed.
"""
import argparse
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
A211 = os.path.join(ROOT, "attempts", "A211-coarse-tree", "code")
CERTS = os.path.join(ROOT, "attempts", "A211-coarse-tree", "certs")
sys.path.insert(0, A211)


def quiet(*_a, **_k):
    pass


def merge_in(cert_dir, nid, pad):
    """inherit211's merge with the A211 certificates read from `cert_dir` -> (dead path set, start path set, info).

    A229_CERT_DIR is read at import time, so the module is re-imported per directory (the campaign certificates of
    A205 / A206 / A209 and the leaf ledgers are unchanged and shared: only the A211 sources move)."""
    os.environ["A229_CERT_DIR"] = os.path.abspath(cert_dir)
    for m in ("inherit211", "startload211"):
        sys.modules.pop(m, None)
    import load211
    load211.install()
    import stage209
    import inherit211 as INH
    s0 = stage209.start_of(nid, pad)
    M = INH.merge(nid, pad, s0.get("file"), log=quiet)
    dead = set(tuple(str(s) for s in p) for p in M["dead_paths"])
    starts = set(tuple(str(INH.norm(s)) for s in (x.get("key") or ())) for x in M["starts"])
    return dead, starts, M["info"]


def key_of(node_labels, start_label):
    """does `label` lie in the subtree grown under the start node `start_label` (pstats211._owns)?"""
    return [l for l in node_labels if l == start_label or l.startswith(start_label + ".") or l.startswith(start_label + "r")]


def owns(label, start):
    return label == start or label.startswith(start + ".") or label.startswith(start + "r")


def split_doc(doc, pad, shards):
    """-> [shard doc], the certificates `run211.py --start ... --cert-suffix` would have written for this run."""
    key = "%s_page" % pad
    d = (doc.get("runs") or {}).get(key)
    if not d:
        raise SystemExit("   the certificate has no run %s" % key)
    starts = [s.get("label") for s in (d.get("start_nodes") or []) if s.get("label")]
    if len(starts) < shards:
        raise SystemExit("   this run has only %d start node(s): nothing to shard into %d" % (len(starts), shards))
    groups = [starts[i::shards] for i in range(shards)]            # round robin: every shard gets work
    nodes = d.get("nodes") or []
    inh = [n for n in nodes if n.get("kind") == "inherited"]        # the inherited rows belong to EVERY shard
    out = []
    for g in groups:
        mine, gs = [], set(g)
        for n in nodes:
            if n.get("kind") == "inherited":
                continue
            lab = str(n.get("label") or "")
            if any(owns(lab, s) for s in gs):
                mine.append(n)
        runs = [r for r in (d.get("runs") or []) if r.get("label") in gs]
        skipped = [dict(label=s, reason="undecided: SKIPPED (filter) -- this run is the shard --start %s of the page; "
                                        "this start node belongs to a sibling shard of the same pass" % ",".join(sorted(gs)))
                   for s in starts if s not in gs]
        dd = dict(d)
        dd.update(nodes=inh + mine, runs=runs, verdict="ALIVE" if skipped else d.get("verdict"),
                  start_filter=sorted(gs), undecided=[u for u in (d.get("undecided") or []) if u.get("label") in gs] + skipped)
        out.append(dict(doc, runs=dict(doc.get("runs") or {}, **{key: dd})))
    return out


def write_shards(nid, pad, docs, out_dir):
    if os.path.isdir(out_dir):
        for f in os.listdir(out_dir):
            if f.startswith("coarsetree211_%s" % nid):
                os.remove(os.path.join(out_dir, f))
    os.makedirs(out_dir, exist_ok=True)
    for i, doc in enumerate(docs):
        p = os.path.join(out_dir, "coarsetree211_%s__t%d.json" % (nid, i + 1))
        with open(p, "w", encoding="utf-8") as f:
            json.dump(doc, f, indent=1, default=str)


def report(nid, pad, aw, bw, what_a, what_b):
    (da, sa, ia), (db, sb, ib) = aw, bw
    ok = True
    for name, A, B in (("DEAD path set", da, db), ("START node set", sa, sb)):
        if A == B:
            print("   OK   %-15s %-4s %-14s: %d == %d" % (nid, pad, name, len(A), len(B)))
            continue
        ok = False
        print("   FAIL %-15s %-4s %-14s: %s has %d, %s has %d" % (nid, pad, name, what_a, len(A), what_b, len(B)))
        for p in sorted(A - B)[:6]:
            print("        only in %s: %s" % (what_a, list(p)))
        for p in sorted(B - A)[:6]:
            print("        only in %s: %s" % (what_b, list(p)))
    print("        %s: %d trees, %d paths | %s: %d trees, %d paths"
          % (what_a, ia["n_trees"], ia["n_paths"], what_b, ib["n_trees"], ib["n_paths"]))
    return ok


def split_mode(nids, pad, shards, scratch):
    ok = True
    for nid in nids:
        src = os.path.join(CERTS, "coarsetree211_%s.json" % nid)
        if not os.path.exists(src):
            print("   SKIP %s: no A211 certificate" % nid)
            continue
        doc = json.load(open(src, encoding="utf-8"))
        try:
            docs = split_doc(doc, pad, shards)
        except SystemExit as e:
            print("   SKIP %s %s: %s" % (nid, pad, e))
            continue
        d = os.path.join(scratch, nid)
        shutil.rmtree(d, ignore_errors=True)
        write_shards(nid, pad, docs, d)
        whole = merge_in(CERTS, nid, pad)
        parts = merge_in(d, nid, pad)
        print("   %s %s: %d start node(s) of the recorded run, cut into %d shard certificate(s)"
              % (nid, pad, len(doc["runs"]["%s_page" % pad].get("start_nodes") or []), shards))
        ok = report(nid, pad, whole, parts, "whole", "shards") and ok
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("nids", nargs="*")
    ap.add_argument("--pad", default="g1")
    ap.add_argument("--shards", type=int, default=2)
    ap.add_argument("--compare", nargs=2, default=None, metavar=("DIR_WHOLE", "DIR_SHARDS"))
    ap.add_argument("--nid", default=None)
    ap.add_argument("--scratch", default=os.path.join(HERE, "..", "certs", "split_test"))
    a = ap.parse_args()
    if a.compare:
        nid = a.nid or (a.nids[0] if a.nids else None)
        if not nid:
            ap.error("--compare needs --nid")
        ok = report(nid, a.pad, merge_in(a.compare[0], nid, a.pad), merge_in(a.compare[1], nid, a.pad), "whole", "shards")
    else:
        nids = a.nids or ["k5_16_interior_Y0500", "k5_16_interior_Y0660", "k5_16_interior_Y0460", "k5_16_interior_Y0865"]
        ok = split_mode(nids, a.pad, a.shards, os.path.abspath(a.scratch))
    print("A229 multi-file merge test: %s" % ("PASS" if ok else "FAIL"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
