"""A117 T1 -- assemble results/equivalence.json.

The main equivalence run (logs/equiv_main28.log) completed 28 of 30 certificates and was then
stopped: certificate 29 of the selection, `A95 .../k5_11_interior_Y0048.param.json`, has no stored
report in A95 (it was never verified there) and ran unbounded past 30 minutes per verifier.  Its
28 finished rows are recovered from the run's own per-certificate log lines -- the runner prints
`IDENTICAL` only when the verdict AND every one of v1's statistics matched, and prints the full
diff list otherwise, so the log carries the whole claim.  The last two certificates were then
re-run (logs/equiv_tail.log -> results/equivalence_tail.json) with `Y0048` swapped for A95's
`Y0049` (which has a stored report, 567 s / 10.2 M boxes) and with a DETERMINISTIC `--box-cap`,
which stops both verifiers at the same box and so preserves the comparison exactly.

Writes results/equivalence.json.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys

os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
RES = os.path.normpath(os.path.join(HERE, "..", "results"))
LOGS = os.path.normpath(os.path.join(HERE, "..", "logs"))

LINE = re.compile(r"^\[(\d+)/(\d+)\] (\S+)\s+(IDENTICAL|DIFFERS .*?)\s+(PASS|FAIL|CAP|\?)\s+"
                  r"boxes=(\d+|\?)\s*$")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    tags = {e["cert"]: e.get("tag", "") for e in
            json.load(open(os.path.join(RES, "selection.json")))}
    rows = []
    for ln in open(os.path.join(LOGS, "equiv_main28.log")):
        m = LINE.match(ln.rstrip("\n"))
        if not m:
            continue
        _, _, cert, verdict, res, boxes = m.groups()
        rows.append(dict(cert=cert, tag=tags.get(cert, ""),
                         identical=(verdict == "IDENTICAL"),
                         diffs=([] if verdict == "IDENTICAL" else [verdict]),
                         result=res, boxes=int(boxes) if boxes.isdigit() else None,
                         source="logs/equiv_main28.log"))
    tail = json.load(open(os.path.join(RES, "equivalence_tail.json")))
    for r in tail["rows"]:
        rows.append(dict(cert=r["cert"], tag=r.get("tag", ""), identical=r["identical"],
                         diffs=r["diffs"], result=r.get("v1", {}).get("result"),
                         boxes=r.get("v1", {}).get("boxes"),
                         v1=r.get("v1"), v2=r.get("v2"),
                         source="results/equivalence_tail.json"))
    n_ok = sum(1 for r in rows if r["identical"])
    doc = dict(n=len(rows), identical=n_ok, differing=len(rows) - n_ok,
               v1_sha256=sha(os.path.join(ROOT, "attempts", "A96-a57-parametric", "code",
                                          "verify_param.py")),
               v2_sha256=sha(os.path.join(ROOT, "attempts", "A96-a57-parametric", "code",
                                          "verify_param_v2.py")),
               contract=("verdict AND every statistic v1 reports (boxes, covered, vacuous, "
                         "exempt, split, s_splits, exact_atom_checks, float_rejects, max_depth, "
                         "max_s_depth, s_cells, s_cells_built, depth_hist_covered, witnesses); "
                         "v2's only extra keys must be exempt_core/exempt_nofam, their sum must "
                         "equal exempt, and exempt_nofam must be 0"),
               excluded=[dict(cert="attempts/A95-a57-shortcuts/results/param/"
                                   "k5_11_interior_Y0048.param.json",
                              reason="no stored A95 report; unbounded (> 30 min per verifier); "
                                     "swapped for A95 k5_11_interior_Y0049")],
               rows=rows)
    json.dump(doc, open(os.path.join(RES, "equivalence.json"), "w"), indent=1)
    print("%d/%d byte-identical" % (n_ok, len(rows)))
    for r in rows:
        print("  %-46s %-11s %-5s %10s  %s" % (r["tag"][:46], "IDENTICAL" if r["identical"]
                                               else "DIFFERS", r["result"], r["boxes"],
                                               os.path.basename(r["cert"])))


if __name__ == "__main__":
    main()
