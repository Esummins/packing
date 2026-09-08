"""A156 -- rebuild ONE combined LP queue for the day shift, in PAUSED.md v3 §E's priority order.

Sources, in order:
  * A137's `results/emitq_*.json` -- the night's screened-and-clipped children (level 1 first, then
    the level-2/3 deepen children: level-1 children that reach the LP died at 78.8 % of decided);
  * A156's own `results/emitq_*.json` -- anything this attempt's deepen lane emits today.

Dropped: ids already **recorded** anywhere (A137's `emit_lp_*.jsonl`, A156's `lp156_*.jsonl`) and
ids **claimed by a live A156 worker** (A156's own claims dir), so a worker launched later never
starts on an exhausted queue -- A137 §D.6's wasted-slot bug.

A137's *stale* claims are deliberately NOT dropped: 196 ids were claimed by night workers that
stopped at the sentinel before recording a row, and re-solving them is idempotent (the certificate
is written under A156's own certs dir).  A WALL-CAP releases its claim, so a capped node returns to
the queue on the next rebuild rather than being lost.

Prints the number of jobs written; the scaler uses that to decide whether to launch at all.
"""
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, ".."))
A137 = os.path.join(ROOT, "A137-night-shift-2")
OUT = os.path.join(BASE, "results", "queue156.json")


def _ids(pattern):
    s = set()
    for p in glob.glob(pattern):
        try:
            for ln in open(p, encoding="utf-8"):
                try:
                    s.add(json.loads(ln)["id"])
                except Exception:
                    pass
        except OSError:
            pass
    return s


def main():
    done = _ids(os.path.join(A137, "results", "emit_lp_*.jsonl"))
    done |= _ids(os.path.join(BASE, "results", "lp156_*.jsonl"))
    claimed = {os.path.basename(p)[:-6] for p in
               glob.glob(os.path.join(BASE, "progress", "claims", "*.claim"))}
    files = sorted(glob.glob(os.path.join(A137, "results", "emitq_*.json")),
                   key=lambda p: (1 if p.endswith("_D2.json") else 0, p))
    files += sorted(glob.glob(os.path.join(BASE, "results", "emitq_*.json")))
    jobs, seen = [], set()
    for p in files:
        try:
            rows = json.load(open(p))
        except Exception:
            continue
        for j in rows:
            if j["id"] in done or j["id"] in claimed or j["id"] in seen:
                continue
            seen.add(j["id"])
            jobs.append(j)
    jobs.sort(key=lambda j: (j.get("level") or 9))          # level 1 first: 78.8 % of decided die
    json.dump(jobs, open(OUT, "w"), indent=0)
    print(len(jobs))


if __name__ == "__main__":
    main()
