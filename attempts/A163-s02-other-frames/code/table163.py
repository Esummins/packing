"""A163 -- the per-box-set / per-frame verdict table, as markdown (results/table163.md).

Columns: the A160 object, its k5_11-frame verdict (A160's own record, for comparison), then per frame
the verdict (CERTIFIED / WALL_CAP / WITNESS / SAMPLE_HIT / not run), the certified minimum, the number
of LIVE-LOW witnesses, and the wall seconds.

    python table163.py

READ-ONLY on every campaign and prior attempt.
"""
from __future__ import annotations

import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib163 as L                 # noqa: E402


def load(cls):
    p = os.path.join(L.RES, "tree_%s.jsonl" % cls)
    out = {}
    if os.path.exists(p):
        for line in open(p, encoding="utf-8"):
            r = json.loads(line)
            out[r.get("key")] = r
    return out


def main():
    ents = L.entries()
    runs = {c: load(c) for c in L.FRAMES}
    tc = {}
    p = os.path.join(L.RES, "tcerts163.json")
    if os.path.exists(p):
        for r in json.load(open(p, encoding="utf-8"))["runs"]:
            tc[(r.get("cls"), r.get("key"))] = r
    lines = ["# A163 — the 53 A160 box sets, re-framed and re-run\n",
             "`CERTIFIED` = A116's selection tree closed every leaf inside the cap AND the sampling",
             "survivor rule (drawn → tested → hits) found 0 hits.  `WALL_CAP` = cap reached with",
             "unresolved cells and NO witness (a compute limit).  `WITNESS` = a LIVE-LOW leaf, i.e. a",
             "real partial packing of `L ∪ P` at side ≤ s₀ (a geometry limit).  `tcert` = an exact",
             "t = tan(θ/2) certificate emitted by A133's `gen_local_t.py` and verified by A133's",
             "independent `check_local_t.py` (sha256 in `results/tcerts163.json`).\n",
             "| # | A160 object | family | k5_11 (A160) | k5_16 | min | s | trump5 | min | s | tcert |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    tot = {c: dict(cert=0, wall=0, wit=0, other=0, sec=0.0, n=0) for c in L.FRAMES}
    for i, e in enumerate(ents):
        key = "%03d|%s" % (i, e["id"])
        row = ["%d" % i, "`%s`" % e["id"].replace("S02_k5_11_A160", ""), L.family(e["id"]),
               "CERT %.7f" % (e["tree_verdict"]["certified_min"] or 0.0)]
        marks = []
        for c in L.FRAMES:
            r = runs[c].get(key)
            if r is None:
                row += ["—", "—", "—"]
                continue
            cm = (r.get("tree") or {}).get("certified_min")
            row += [r.get("reason"), ("%.7f" % cm) if isinstance(cm, float) else "-",
                    "%.0f" % r["seconds"]]
            t = tot[c]
            t["n"] += 1
            t["sec"] += r["seconds"]
            t["cert"] += 1 if r.get("dead") else 0
            t["wall"] += 1 if r.get("reason") == "WALL_CAP" else 0
            t["wit"] += 1 if r.get("reason") == "WITNESS" else 0
            t["other"] += 1 if (not r.get("dead") and r.get("reason") not in
                                ("WALL_CAP", "WITNESS")) else 0
            x = tc.get((c, key))
            if x:
                marks.append("%s %s" % (c, "VALID" if x.get("checker_ok") else
                                        ("dead" if x.get("dead") else "not dead")))
        row.append(", ".join(marks) if marks else "")
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")
    for c in L.FRAMES:
        t = tot[c]
        lines.append("* **%s**: %d of %d box sets run, **%d CERTIFIED**, %d wall cap, %d witness, "
                     "%d other; %.0f s of tree (%.2f CPU-h)."
                     % (c, t["n"], len(ents), t["cert"], t["wall"], t["wit"], t["other"],
                        t["sec"], t["sec"] / 3600.0))
    p = os.path.join(L.RES, "table163.md")
    open(p, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines[-3:]))
    print("wrote", p)


if __name__ == "__main__":
    main()
