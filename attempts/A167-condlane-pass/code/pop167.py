"""A167 T1 -- the population, built FROM THE COLLECTOR (not from a campaign snapshot).

A161's own lesson (notes/t3_table.md, T7): its population came from A141's `t2_a5760` snapshot, so
62 of its 96 "kills" were nodes A149/A156 had already marked dead in A57's tree jsonl.  The
authority on "what is still alive" is the collector `docs/shadows/status_gallery.py` (A162), which
scans EVERY kill record in the repo, applies its soundness filter and its tree-tag rule.  This
script imports it READ-ONLY.

Population = { (nid, slot) : nid ALIVE per the collector, the A161 T3 verdict is `NO-LINE ...` or
`UNDECIDED`, `M = 1` (exactly one conditioned square, and it can reach the cell) } -- these are
precisely the cells the CONDITIONAL leaf was designed for: `beta + M >= 2` only because the band
square and `H` are counted separately.

Ordering: A161's cost order -- trump5 BR(0,1), k5_16 BL(1,0), k5_16 BR(1,0), k5_16 TL(1,0), then
the rest (by class/slot cell count, descending).

    python pop167.py --collector ../results/collector.json --out ../results/pop.json
"""
import argparse
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
A161 = os.path.join(ROOT, "attempts", "A161-chord-lane")
sys.path.insert(0, os.path.join(ROOT, "docs", "shadows"))

import status_gallery as SG  # noqa: E402  READ-ONLY

COST_ORDER = [("trump5", "BR(0,1)"), ("k5_16", "BL(1,0)"), ("k5_16", "BR(1,0)"),
              ("k5_16", "TL(1,0)")]


def dead_set(cache=None):
    """{nid: sorted[attempt]} for every node id the collector records DEAD, and the source table."""
    if cache and os.path.exists(cache):
        d = json.load(open(cache, encoding="utf-8"))
        return {k: v for k, v in d["dead"].items()}, d["sources"], d["stats"]
    corpus, tags_of = SG.load_a57_corpus()
    table = SG.Table(corpus, tags_of)
    SG.collect(table, corpus)
    dead = collections.defaultdict(set)
    for r in table.rows:
        if r["dead"]:
            dead[r["id"]].add(r["attempt"])
    stats = dict(rows=len(table.rows), kills=sum(1 for r in table.rows if r["dead"]),
                 sources=len(table.by_source), dead_ids=len(dead))
    out = {k: sorted(v) for k, v in dead.items()}
    if cache:
        json.dump(dict(dead=out, sources={k: dict(v) for k, v in table.by_source.items()},
                       stats=stats), open(cache, "w", encoding="utf-8"), indent=1)
    return out, {k: dict(v) for k, v in table.by_source.items()}, stats


def t3_rows():
    """A161's T3 rows, deduplicated (t3_dedup.jsonl wins over t3.jsonl on a repeated pair)."""
    rows = {}
    for f in ("t3.jsonl", "t3_dedup.jsonl", "t5_retry.jsonl"):
        p = os.path.join(A161, "results", f)
        if not os.path.exists(p):
            continue
        for ln in open(p, encoding="utf-8"):
            try:
                r = json.loads(ln)
            except Exception:                                        # noqa: BLE001
                continue
            r["_src_file"] = f
            rows[(r["nid"], r["slot"])] = r
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--collector", default=os.path.join(BASE, "results", "collector.json"))
    ap.add_argument("--out", default=os.path.join(BASE, "results", "pop.json"))
    a = ap.parse_args()
    dead, sources, stats = dead_set(a.collector)
    print("collector: %d records, %d kills, %d sources, %d distinct dead node ids"
          % (stats["rows"], stats["kills"], stats["sources"], stats["dead_ids"]))

    rows = t3_rows()
    keep, drop = [], collections.Counter()
    for (nid, slot), r in rows.items():
        v = r.get("verdict") or ""
        if nid in dead:
            drop["node already dead (collector)"] += 1
            continue
        if not (v.startswith("NO-LINE") or v == "UNDECIDED"):
            drop["verdict %s" % v.split(" ")[0]] += 1
            continue
        if r.get("M") != 1:
            drop["M != 1 (%r)" % r.get("M")] += 1
            continue
        if r.get("n_cond") != 1:
            drop["n_cond != 1"] += 1
            continue
        keep.append(dict(nid=nid, slot=slot, src=r["src"], cls=r["cls"], level=r["level"],
                         a161_verdict=v, beta_min=r.get("beta_min"), beta=r.get("beta"),
                         a141_verdict=r.get("a141_verdict"), from_file=r["_src_file"]))
    by = collections.Counter((k["cls"], k["slot"]) for k in keep)
    rank = {cs: i for i, cs in enumerate(COST_ORDER)}
    rest = sorted([cs for cs in by if cs not in rank], key=lambda cs: (-by[cs], cs))
    for i, cs in enumerate(rest):
        rank[cs] = len(COST_ORDER) + i
    keep.sort(key=lambda k: (rank[(k["cls"], k["slot"])], k["nid"]))
    print("A161 T3 pairs read: %d;  population: %d cells over %d distinct alive nodes"
          % (len(rows), len(keep), len({k["nid"] for k in keep})))
    for cs in sorted(by, key=lambda c: rank[c]):
        print("   %-8s %-9s %4d" % (cs[0], cs[1], by[cs]))
    print("dropped:")
    for k, v in drop.most_common():
        print("   %-40s %5d" % (k, v))
    json.dump(dict(stats=stats, n_pop=len(keep), by_class_slot={"%s|%s" % k: v
                                                               for k, v in by.items()},
                   dropped=dict(drop), pop=keep),
              open(a.out, "w", encoding="utf-8"), indent=1)
    print("wrote %s" % a.out)


if __name__ == "__main__":
    main()
