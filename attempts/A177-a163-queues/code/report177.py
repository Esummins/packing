"""A177 -- regenerate A136's board with this attempt's closures tagged honestly.

    python report177.py

`report136.py` is IMPORTED and its `main()` is what runs, so the closure schema, the Lean fragment
emission, the certificate re-hashing and the `nodes_*` discovery are byte-identical.  Two things are
wrapped:

  * `row()` -- a record this attempt wrote carries an `a177` stamp (`run177.restatus177`), so the
    closure row it produces is tagged `attempt: "A177"` with the certifier and entry rule that
    earned it, instead of the literal `"A136"`.  Rows from A136's own records are untouched.
  * the A96 ledger append -- `report136.main()` is called with `--no_ledger` and the append is done
    here from the rows it wrote, so each ledger row carries its OWN attempt tag.  The append is
    still append-only and still writes every current closure (A120's ledger reader takes the last
    row for each id), so nothing about how it is read changes.

READ-ONLY on A136's code.  PYTHONDONTWRITEBYTECODE=1.
"""
from __future__ import annotations

import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
A136C = os.path.join(ROOT, "attempts", "A136-a120-resume", "code")

os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.path.insert(0, A136C)

import a136lib as A6                                               # noqa: E402
import report136 as RP                                             # noqa: E402

_ROW = RP.row


def row177(rec, certdir=None):
    x = _ROW(rec, certdir)
    if x is not None and rec.get("a177"):
        x["attempt"] = "A177"
        x["a177"] = rec["a177"]
    return x


def main():
    RP.row = row177
    if "--no_ledger" not in sys.argv:
        sys.argv.append("--no_ledger")
    rc = RP.main()
    rows = []
    p = os.path.join(A6.RES, "closures136.jsonl")
    with open(p, encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if ln:
                rows.append(json.loads(ln))
    with open(RP.LEDGER, "a", encoding="utf-8") as f:
        for x in rows:
            f.write(json.dumps(dict(
                id=x["node"], cls=x["cls"], level=x["level"], status="CLOSED",
                attempt=x.get("attempt", "A136"), rev=3, s0=x["s0"], N=x["N"],
                yes="local certificate %s (%s, sha %s)" % (
                    x["N"], x["hD"]["certificate"]["format"],
                    x["hD"]["certificate"]["sha256"][:12]),
                no=[h["certificate"] for h in x["hno"]],
                zone_sub_box=True, fcover="fixed (A136)",
                note=("s0-only; supersedes A120's row for this id"
                      + ("; A177 re-run under the widest-citeable-N rule with A170's exact cores "
                         "inside the certification loop" if x.get("attempt") == "A177" else "")),
                generated=x["generated"])) + "\n")
    print("A177: appended %d rows to %s (%d tagged A177)"
          % (len(rows), RP.LEDGER, sum(1 for x in rows if x.get("attempt") == "A177")))
    return rc


if __name__ == "__main__":
    sys.exit(main())
