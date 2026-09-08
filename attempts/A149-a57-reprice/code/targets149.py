"""A149 -- build the day's re-emission queue: the un-re-solved ALIVE nodes of A137's
`targets137.json`, in `frac_exact` DESCENDING order (A145's predictor; PAUSED.md v3 Sec.C.1 --
the top band is ~1.6x the rest, but the 0.30-0.45 band is 15 certified kills and stays in).

Read-only on A137: its targets file and its two result ledgers are read; nothing under A137 is
written.  A137's own claim files are IGNORED on purpose -- a claim with no recorded row is a node
whose worker was killed at the 06:45 stop, and it owes work like any other.

TWO CORRECTIONS A149 found, both of which remove duplicated work (`notes/dupwork.md`):

  (1) A137 ran TWO lanes over the same nodes.  Lane (a), the exact-core re-emission, re-solves an
      ALIVE node on its RECORDED box; lane (b), the fresh level-1 emission, re-solves the same
      node id on its T5'''-CLIPPED box.  **24 of the 141 un-re-solved targets were already solved
      last night in lane (b)** -- 8 of them PASS.  The clipped box is a subset of the recorded box
      (verified below, 60/60), so a lane-(b) verdict is at least as strong as a lane-(a) one:
      those nodes are dropped here rather than re-solved.

  (2) For the 60 targets that are still SITTING in lane (b)'s queue, the clipped box is available
      and is a strict subset in half the cases.  We solve the clipped box: same cost, strictly
      stronger, and the emission queue's job for that id is then redundant.

Both substitutions are checked for containment before they are made; a box that is not contained
is left as the target's own.
"""
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, ".."))
A137 = os.path.join(ROOT, "A137-night-shift-2")
OUT = os.path.join(BASE, "results", "targets149.json")


def main():
    T = json.load(open(os.path.join(A137, "results", "targets137.json")))
    done = set()
    for w in ("w0", "w1"):
        p = os.path.join(A137, "results", "exact_reemit_%s.jsonl" % w)
        if not os.path.exists(p):
            continue
        for ln in open(p, encoding="utf-8"):
            try:
                done.add(json.loads(ln)["id"])
            except Exception:
                pass
    # this attempt's own recorded rows, so the builder is idempotent across resumes
    for fn in os.listdir(os.path.join(BASE, "results")):
        if fn.startswith("exact_reemit_") and fn.endswith(".jsonl"):
            for ln in open(os.path.join(BASE, "results", fn), encoding="utf-8"):
                try:
                    done.add(json.loads(ln)["id"])
                except Exception:
                    pass
    # --- (1) ids lane (b) already decided last night, on a box contained in this one
    lane_b = {}
    for p in glob.glob(os.path.join(A137, "results", "emit_lp_*.jsonl")):
        for ln in open(p, encoding="utf-8"):
            try:
                r = json.loads(ln)
            except Exception:
                continue
            lane_b[r["id"]] = r.get("result")
    # --- (2) clipped boxes still queued in lane (b)
    lane_bq = {}
    for p in glob.glob(os.path.join(A137, "results", "emitq_*.json")):
        for j in json.load(open(p)):
            lane_bq[j["id"]] = j

    def contained(inner, outer):
        return (inner["x0"] >= outer["x0"] - 1e-9 and inner["x1"] <= outer["x1"] + 1e-9 and
                inner["y0"] >= outer["y0"] - 1e-9 and inner["y1"] <= outer["y1"] + 1e-9 and
                inner["th0"] >= outer["th0"] - 1e-9 and inner["th1"] <= outer["th1"] + 1e-9)

    rem, dropped, swapped = [], [], 0
    for t in T:
        if t["id"] in done:
            continue
        if t["id"] in lane_b:
            dropped.append((t["id"], lane_b[t["id"]]))
            continue
        j = lane_bq.get(t["id"])
        if j is not None and j.get("budget") == t.get("budget") and contained(j["box"], t["box"]):
            if j["box"] != t["box"]:
                swapped += 1
            t = dict(t, box=j["box"], box_source="A137 lane (b) T5'''-clipped box",
                     supersedes_emission_job=True)
        rem.append(t)
    rem.sort(key=lambda t: (-(t.get("frac_exact") or 0.0), t.get("level") or 9, t["id"]))
    json.dump(rem, open(OUT, "w"), indent=0)
    json.dump(dict(dropped_already_solved_in_lane_b=dropped, clipped_boxes_substituted=swapped),
              open(os.path.join(BASE, "results", "targets149_dedup.json"), "w"), indent=1)
    print("dropped %d already decided by A137's emission lane; %d clipped boxes substituted"
          % (len(dropped), swapped))
    bands = {">=0.60": 0, "0.45-0.60": 0, "0.30-0.45": 0, "<0.30": 0}
    for t in rem:
        f = t.get("frac_exact") or 0.0
        k = ">=0.60" if f >= 0.60 else "0.45-0.60" if f >= 0.45 else \
            "0.30-0.45" if f >= 0.30 else "<0.30"
        bands[k] += 1
    print("%d targets (of %d; %d already recorded) -> %s" % (len(rem), len(T), len(done), OUT))
    print("frac_exact bands: " + json.dumps(bands))


if __name__ == "__main__":
    main()
