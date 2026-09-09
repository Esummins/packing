"""A161 T7 -- the overlap: which A161 kills are DISTINCT NEW dead nodes.

The authority on "what is already dead" is the collector the PI's STATUS.md is built from,
`docs/shadows/status_gallery.py` (A162): it scans EVERY kill record in the repo (A57's own tree
jsonl, A137's clipkills, the supersession ledgers folding in A131/A135/A141/A142/A145, A149's and
A156's day-shift records, A136/A96 closures, A140's k0 arm, A141's lane kills, A161's own, and
every `*.clipkill.json`), applies its soundness filter and its tag rule.  This script imports it
READ-ONLY, builds that table, and subtracts A161's own rows.

    python overlap161.py
"""
import argparse
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "docs", "shadows"))

import status_gallery as SG  # noqa: E402  READ-ONLY


def a161_nodes():
    """(chord-lane kills, A141x kills) as {nid: [slots]}."""
    out = {}
    for tag, path in (("t3", os.path.join(BASE, "results", "t3_dedup.jsonl")),
                      ("t5", os.path.join(BASE, "results", "t5_retry.jsonl")),
                      ("t6", os.path.join(BASE, "results", "t6_a141x.jsonl"))):
        d = {}
        if os.path.exists(path):
            for ln in open(path, encoding="utf-8"):
                r = json.loads(ln)
                if r.get("verdict") == "KILL":
                    d.setdefault(r["nid"], []).append(r["slot"])
        out[tag] = d
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(BASE, "results", "overlap161.json"))
    a = ap.parse_args()
    corpus, tags_of = SG.load_a57_corpus()
    table = SG.Table(corpus, tags_of)
    SG.collect(table, corpus)
    print("kill table: %d rows, %d kills, from %d sources"
          % (len(table.rows), sum(1 for r in table.rows if r["dead"]), len(table.by_source)))

    # every node id recorded dead by a source that is NOT A161
    dead_other = collections.defaultdict(set)      # nid -> {attempt}
    for r in table.rows:
        if not r["dead"] or r["attempt"] == "A161":
            continue
        dead_other[r["id"]].add(r["attempt"])
    print("nodes recorded dead by non-A161 sources: %d" % len(dead_other))

    mine = a161_nodes()
    res = {"sources": {k: dict(v) for k, v in table.by_source.items()},
           "n_dead_other": len(dead_other)}
    allnew = set()
    for tag, d in mine.items():
        nids = set(d)
        pre = {n for n in nids if n in dead_other}
        new = sorted(nids - pre)
        allnew |= set(new)
        res[tag] = dict(kill_nodes=len(nids), kill_pairs=sum(len(v) for v in d.values()),
                        already_dead=len(pre), new=len(new), new_nodes=new,
                        prior_attempts=dict(collections.Counter(
                            a for n in pre for a in dead_other[n])))
        print("%-4s %4d kill nodes, %4d already dead elsewhere, **%4d NEW**   prior: %s"
              % (tag, len(nids), len(pre), len(new), res[tag]["prior_attempts"]))
    union = set().union(*[set(d) for d in mine.values()]) if mine else set()
    pre_u = {n for n in union if n in dead_other}
    res["union"] = dict(kill_nodes=len(union), already_dead=len(pre_u),
                        new=len(union - pre_u), new_nodes=sorted(union - pre_u))
    print("UNION %d kill nodes, %d already dead elsewhere, **%d distinct NEW dead nodes**"
          % (len(union), len(pre_u), len(union - pre_u)))
    json.dump(res, open(a.out, "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
