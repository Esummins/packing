"""A157 -- cache the corpus records the job list needs.

`corpus.load_nodes()` globs and json-loads the whole A57/A60/k0 corpus (~2 min on a busy box) and
is re-paid by every worker.  `lane.cframe_boxes` only reads `src`, `cls` and `cond`, so cache
exactly those for the nids in the job list.  READ-ONLY on every campaign.

    python mkrecs157.py
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
A118 = os.path.join(ROOT, "attempts", "A118-lane-count", "code")
if A118 not in sys.path:
    sys.path.insert(0, A118)

import corpus as CP  # noqa: E402  READ-ONLY


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", default=os.path.join(BASE, "results", "undecided_cells.jsonl"))
    ap.add_argument("--out", default=os.path.join(BASE, "results", "recs157.json"))
    a = ap.parse_args()

    want = set()
    with open(a.jobs, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln:
                want.add(json.loads(ln)["nid"])

    recs = {r["nid"]: r for r in CP.load_nodes()}
    known = set(recs)
    boxes, _ = CP.load_open_boxes(known)
    for b in boxes:
        if not b.get("covered_by_node"):
            recs.setdefault(b["nid"], b)

    out = {}
    for nid in sorted(want):
        r = recs[nid]
        out[nid] = dict(src=r["src"], nid=nid, cls=r["cls"], level=r.get("level"),
                        shard=r.get("shard"), path=r.get("path"), alive=r.get("alive"),
                        cond=[{k: float(v) for k, v in bd.items()
                               if k in ("x0", "x1", "y0", "y1", "th0", "th1")}
                              for bd in r["cond"]])
    json.dump(out, open(a.out, "w", encoding="utf-8"))
    print("cached %d of %d nids -> %s" % (len(out), len(want), a.out))


if __name__ == "__main__":
    main()
