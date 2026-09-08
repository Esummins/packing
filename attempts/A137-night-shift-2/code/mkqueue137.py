"""A137 -- rebuild ONE combined LP queue for the emission lanes, in the coordinator's priority
order: (b) fresh level-1 children of the shards first, then (c) the level-2 deepen children.

Jobs already recorded or already claimed by a live worker are dropped, so a worker launched later
never starts on an exhausted queue (three scaler slots were wasted at 02:16-02:36 doing exactly
that: the scaler counted a queue's REMAINING rows from its out-file, not from the claims).

Prints the number of jobs written; the scaler uses that to decide whether to launch at all.
"""
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(BASE, "results", "queue_bc.json")


def main():
    done = set()
    for p in glob.glob(os.path.join(BASE, "results", "emit_lp_*.jsonl")):
        for ln in open(p, encoding="utf-8"):
            try:
                done.add(json.loads(ln)["id"])
            except Exception:
                pass
    claimed = {os.path.basename(p)[:-6] for p in
               glob.glob(os.path.join(BASE, "progress", "claims", "*.claim"))}
    files = sorted(glob.glob(os.path.join(BASE, "results", "emitq_*.json")),
                   key=lambda p: (1 if p.endswith("_D2.json") else 0, p))
    jobs, seen = [], set()
    for p in files:
        for j in json.load(open(p)):
            if j["id"] in done or j["id"] in claimed or j["id"] in seen:
                continue
            seen.add(j["id"])
            jobs.append(j)
    json.dump(jobs, open(OUT, "w"), indent=0)
    print(len(jobs))


if __name__ == "__main__":
    main()
