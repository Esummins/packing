"""A167 T5 -- re-run the COLLECTOR fresh and re-check A167's kills against it.

The population was built from a collector snapshot taken at the start of the attempt; other
campaigns write kills while A167 runs, so the NEW-node claim is re-derived from a FRESH collect
before it is reported.

    python recheck167.py
"""
import argparse
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import pop167  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", default=os.path.join(BASE, "results", "table.json"))
    ap.add_argument("--cache", default=os.path.join(BASE, "results", "collector_final.json"))
    ap.add_argument("--out", default=os.path.join(BASE, "results", "recheck.json"))
    a = ap.parse_args()
    if os.path.exists(a.cache):
        os.remove(a.cache)                      # force a fresh collect
    dead, sources, stats = pop167.dead_set(a.cache)
    t = json.load(open(a.table, encoding="utf-8"))
    kills = t["kill_nodes"]
    pre = {n: dead[n] for n in kills if n in dead}
    new = sorted(set(kills) - set(pre))
    print("FRESH collector: %d records, %d kills, %d sources, %d distinct dead node ids"
          % (stats["rows"], stats["kills"], stats["sources"], stats["dead_ids"]))
    print("A167 kill nodes: %d;  already dead elsewhere: %d;  **NEW: %d**"
          % (len(kills), len(pre), len(new)))
    for n, v in sorted(pre.items()):
        print("   already dead: %-30s %s" % (n, v))
    print("NEW: %s" % ", ".join(new))
    by = collections.Counter(n.split("_")[0] for n in new)
    print("by source tag: %s" % dict(by))
    json.dump(dict(stats=stats, kill_nodes=sorted(kills), already_dead=pre, new_nodes=new),
              open(a.out, "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
