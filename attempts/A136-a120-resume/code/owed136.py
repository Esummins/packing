"""A136 -- the owed-consumer board: for every queue, what happened to every id, and why.

The four (now five) queues under `results/queue_*.json` are the consumers this attempt owes a
verdict to.  A node can end up in one of six states, and the point of this script is that the
DIFFERENCE between them is the whole answer to "what is still owed and why":

  CLOSED         every NO child certified dead AND the YES leaf cites a checked certificate
  OPEN           at least one NO child survives the LP -- the cover does not prove this node
  SKIP-UNSOUND   a soundness assertion (A120 A1-A7 / per-box A4) refused the node before any LP
  A149-KILL      already certified dead on exact cores by A149; a kill it holds is not re-bought
  NOT-RUN        still owed: never started, or started and stopped at a cap / reboot / kill
  (a node may appear under TWO leaves -- see `--out_suffix` -- and is reported under both)

    python owed136.py            # writes results/owed136.json, prints the table

Read-only apart from `results/owed136.json`.
"""
from __future__ import annotations

import glob, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a136lib as A6                                               # noqa: E402

A149R = os.path.join(A6.ROOT, "attempts", "A149-a57-reprice", "results")


def a149_kills():
    out = {}
    for p in sorted(glob.glob(os.path.join(A149R, "exact_reemit_w*.jsonl"))):
        with open(p, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                if d.get("result") == "PASS" and d.get("id"):
                    out[d["id"]] = os.path.basename(p)
    return out


def records():
    """id -> [(subtree, status), ...] over every results/nodes* subtree."""
    out = {}
    for nd in [A6.NODES] + sorted(glob.glob(os.path.join(A6.RES, "nodes_*"))):
        if not os.path.isdir(nd):
            continue
        suf = os.path.basename(nd)[len("nodes"):] or "(base)"
        for p in sorted(glob.glob(os.path.join(nd, "rec__*.json"))):
            try:
                r = json.load(open(p, encoding="utf-8"))
            except Exception:
                continue
            if r.get("id"):
                out.setdefault(r["id"], []).append(
                    (suf, r.get("status"), r.get("child_status")))
    return out


def main():
    kills, recs = a149_kills(), records()
    board, tally = {}, {}
    for qp in sorted(glob.glob(os.path.join(A6.RES, "queue_*.json"))):
        q = json.load(open(qp, encoding="utf-8"))
        name = os.path.basename(qp)
        rows = []
        for x in q["ids"]:
            x = x if isinstance(x, dict) else dict(id=x)
            nid = x["id"]
            got = recs.get(nid) or []
            best = None
            for suf, st, cs in got:
                if st == "CLOSED":
                    best = ("CLOSED", suf, cs)
                    break
            if best is None and got:
                suf, st, cs = got[0]
                best = (st or "NOT-RUN", suf, cs)
            if best is None:
                best = ("A149-KILL" if nid in kills else "NOT-RUN",
                        kills.get(nid, ""), None)
            rows.append(dict(id=nid, state=best[0], subtree=best[1], child_status=best[2],
                             entry=x.get("entry"), link=x.get("link"),
                             alive_gallery_page=x.get("alive_gallery_page"),
                             all_records=[dict(subtree=s, status=t) for s, t, _ in got]))
            tally[best[0]] = tally.get(best[0], 0) + 1
        board[name] = dict(name=q.get("name", "")[:400], n=len(rows), rows=rows,
                           by_state={s: sum(1 for r in rows if r["state"] == s)
                                     for s in sorted({r["state"] for r in rows})})
    out = dict(generated=A6.now() if hasattr(A6, "now") else "", queues=board, tally=tally)
    A6.jdump(os.path.join(A6.RES, "owed136.json"), out)
    for name, b in board.items():
        print("%-28s n=%-3d %s" % (name, b["n"], json.dumps(b["by_state"])))
        for r in b["rows"]:
            if r["state"] not in ("CLOSED",):
                print("      %-28s %-14s %s%s" % (r["id"], r["state"], r["subtree"] or "",
                                                  "   [ALIVE PAGE]" if r.get("alive_gallery_page") else ""))
    print("\nTOTAL", json.dumps(tally))
    print("->", os.path.join(A6.RES, "owed136.json"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
