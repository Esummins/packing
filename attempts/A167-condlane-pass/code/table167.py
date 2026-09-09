"""A167 T4 -- the table: verdicts by class/slot, and the overlap with the COLLECTOR's dead set.

The authority on "already dead" is `docs/shadows/status_gallery.py` (imported READ-ONLY by
`pop167.py`, whose cached table `results/collector.json` this reuses).  A kill here counts as NEW
only if the collector records NO kill for that node id from any source.

    python table167.py --rows ../results/pass_s0.jsonl ../results/pass_s1.jsonl ...
"""
import argparse
import collections
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))

ORDER = ["KILL", "NO-GO-witness", "UNDECIDED-time", "UNDECIDED", "ERROR", "NO-RECORD",
         "NOT-SINGLE-CONDITIONED", "NOT-WALL-ADJACENT"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", nargs="*", default=[os.path.join(BASE, "results", f) for f in
                                                  ("pass_s0.jsonl", "pass_s1.jsonl",
                                                   "y0169.jsonl")])
    ap.add_argument("--pop", default=os.path.join(BASE, "results", "pop.json"))
    ap.add_argument("--collector", default=os.path.join(BASE, "results", "collector.json"))
    ap.add_argument("--nogo", default=os.path.join(BASE, "results", "nogo.jsonl"))
    ap.add_argument("--out", default=os.path.join(BASE, "results", "table.json"))
    ap.add_argument("--md", default=os.path.join(BASE, "notes", "table.md"))
    a = ap.parse_args()

    rows = {}
    for f in a.rows:
        if not os.path.exists(f):
            continue
        for ln in open(f, encoding="utf-8"):
            r = json.loads(ln)
            key = (r["nid"], r["slot"])
            # a KILL always wins over a weaker verdict for the same cell
            if key not in rows or (r.get("verdict") == "KILL"):
                rows[key] = r
    pop = json.load(open(a.pop, encoding="utf-8"))
    coll = json.load(open(a.collector, encoding="utf-8"))
    dead = coll["dead"]
    npop = len(pop["pop"])

    tally = collections.Counter(r["verdict"] for r in rows.values())
    per = collections.defaultdict(collections.Counter)
    for r in rows.values():
        per[(r["cls"], r["slot"])][r["verdict"]] += 1
    popper = collections.Counter((p["cls"], p["slot"]) for p in pop["pop"])

    kills = collections.defaultdict(list)
    for r in rows.values():
        if r["verdict"] == "KILL":
            kills[r["nid"]].append(r["slot"])
    pre = {n for n in kills if n in dead}
    new = sorted(set(kills) - pre)
    prior = collections.Counter(a2 for n in pre for a2 in dead[n])

    nogo = {}
    if os.path.exists(a.nogo):
        for ln in open(a.nogo, encoding="utf-8"):
            q = json.loads(ln)
            nogo[(q["nid"], q["slot"])] = q

    L = []
    L.append("# A167 -- the conditional chord-limited lane, population pass")
    L.append("")
    L.append("Population (built from the collector: %d records, %d kills, %d sources, %d distinct "
             "dead node ids): **%d cells** over **%d** alive A57/A60 nodes."
             % (coll["stats"]["rows"], coll["stats"]["kills"], coll["stats"]["sources"],
                coll["stats"]["dead_ids"], npop, len({p["nid"] for p in pop["pop"]})))
    L.append("")
    L.append("Cells RUN: **%d** of %d." % (len(rows), npop))
    L.append("")
    L.append("| verdict | cells | meaning |")
    L.append("|---|---|---|")
    MEAN = {
        "KILL": "every piece of `B_H` closed: `n(b) <= 1` everywhere, the node is DEAD",
        "NO-GO-witness": "some piece has NO viable guard offset -- a sampled free meeter forces "
                         "the leaf's own counters to `>= 2` at every swept offset",
        "UNDECIDED-time": "the 60 s cell budget ran out with covers unresolved",
        "UNDECIDED": "no offset closed on some piece inside its slices",
        "ERROR": "exception (see the row)",
    }
    for v in ORDER + [v for v in tally if v not in ORDER]:
        if tally.get(v):
            L.append("| `%s` | %d | %s |" % (v, tally[v], MEAN.get(v, "")))
    L.append("")
    L.append("## By class x slot (population cells in the last column)")
    L.append("")
    L.append("| class | slot | run | KILL | NO-GO | UNDEC | in population |")
    L.append("|---|---|---|---|---|---|---|")
    for cs in sorted(per, key=lambda c: (-popper[c], c)):
        t = per[cs]
        L.append("| %s | %s | %d | **%d** | %d | %d | %d |"
                 % (cs[0], cs[1], sum(t.values()), t["KILL"], t["NO-GO-witness"],
                    t["UNDECIDED-time"] + t["UNDECIDED"], popper[cs]))
    L.append("")
    L.append("## Overlap with the collector's dead set")
    L.append("")
    L.append("| | nodes |")
    L.append("|---|---|")
    L.append("| kill nodes (distinct) | %d |" % len(kills))
    L.append("| already dead per the collector | %d |" % len(pre))
    L.append("| **distinct NEW dead nodes** | **%d** |" % len(new))
    if prior:
        L.append("")
        L.append("prior sources on the overlapping ones: %s"
                 % ", ".join("%s %d" % kv for kv in prior.most_common()))
    if new:
        L.append("")
        L.append("NEW: `%s`" % ", ".join(new))
    if nogo:
        ok = sum(1 for q in nogo.values() if q.get("ok"))
        L.append("")
        L.append("## Exact two-crowd witnesses (`nogo_two_crowd_v1`)")
        L.append("")
        L.append("%d NO-GO cells escalated, **%d** carry an EXACT rational two-crowd witness "
                 "(both squares inside the container, both meeting `int C`, interiors disjoint, "
                 "clear of all five pins, one a legal `H` pose) -- those cells are RETIRED for the "
                 "whole lane-leaf family; the rest are no-go only at the split depth reached."
                 % (len(nogo), ok))
    md = "\n".join(L) + "\n"
    print(md)
    open(a.md, "w", encoding="utf-8").write(md)
    json.dump(dict(n_run=len(rows), n_pop=npop, tally=dict(tally),
                   per_class_slot={"%s|%s" % k: dict(v) for k, v in per.items()},
                   kill_nodes={k: v for k, v in kills.items()},
                   already_dead=sorted(pre), new_nodes=new,
                   prior_sources=dict(prior),
                   nogo_exact=sum(1 for q in nogo.values() if q.get("ok")),
                   nogo_rows=len(nogo)),
              open(a.out, "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
