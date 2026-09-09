"""A163 T1 -- run A116's selection tree over every one of A160's 53 box sets, re-framed.

One process per frame.  Resumable: every finished box set is one jsonl line keyed by
`<index>|<A160 id>` (A160's ids are not unique -- the r_xy probe reuses one -- so the index is part
of the key) and `--skip-done` re-reads the file.

    python run163.py --cls k5_16  --out ../results/tree_k5_16.jsonl  --time-cap 240 --skip-done
    python run163.py --cls trump5 --out ../results/tree_trump5.jsonl --time-cap 240 --skip-done

Order: cheapest-first inside each family, families in decreasing consumer value (the slices at f1's
base box, then the chain, then the wide-f1 slices), so a budget stop always leaves the useful half
done.  `--budget-s` stops the process cleanly when its own accumulated tree wall passes the budget.

READ-ONLY on every campaign and prior attempt; writes only under attempts/A163-s02-other-frames/.
"""
from __future__ import annotations

import argparse, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib163 as L                     # noqa: E402

FAMORDER = {"slice": 0, "chain": 1, "other": 2}


def keyof(i, e):
    return "%03d|%s" % (i, e["id"])


def order(ents):
    rows = [(i, e) for i, e in enumerate(ents)]

    def k(t):
        i, e = t
        sec = (e.get("tree_verdict") or {}).get("seconds") or 0.0
        wide = 1 if "a151B" in e["id"] else 0            # the wide-f1 slices last (A160: expensive)
        return (FAMORDER.get(L.family(e["id"]), 3) + 2 * wide, sec, i)
    return sorted(rows, key=k)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cls", required=True, choices=list(L.FRAMES) + ["k5_11"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--time-cap", type=float, default=240.0)
    ap.add_argument("--samples", type=int, default=3000)
    ap.add_argument("--budget-s", type=float, default=5400.0)
    ap.add_argument("--only", default=None, help="substring filter on the A160 id")
    ap.add_argument("--skip-done", action="store_true")
    a = ap.parse_args()

    ents = L.entries()
    done = set()
    if a.skip_done and os.path.exists(a.out):
        for line in open(a.out, encoding="utf-8"):
            try:
                done.add(json.loads(line)["key"])
            except Exception:
                pass
    prog = os.path.join(L.PROG, "run163_%s.json" % a.cls)
    todo = [(i, e) for (i, e) in order(ents)
            if keyof(i, e) not in done and (a.only is None or a.only in e["id"])]
    print("frame %s: %d box sets, %d already done, %d to run, cap %.0f s each, budget %.0f s"
          % (a.cls, len(ents), len(done), len(todo), a.time_cap, a.budget_s), flush=True)
    spent, n_ok, n_bad = 0.0, 0, 0
    for n, (i, e) in enumerate(todo):
        if spent > a.budget_s:
            print("BUDGET STOP after %.0f s (%d of %d run)" % (spent, n, len(todo)), flush=True)
            break
        t0 = time.time()
        try:
            rec = L.run_tree(e, a.cls, time_cap=a.time_cap, samples=a.samples)
        except Exception as ex:                      # never lose the rest of the queue
            rec = dict(id=e["id"], cls=a.cls, dead=False, reason="ERROR", error=repr(ex),
                       seconds=round(time.time() - t0, 1))
        rec["key"] = keyof(i, e)
        rec["a160_index"] = i
        rec["family"] = L.family(e["id"])
        with open(a.out, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
        spent += rec["seconds"]
        n_ok += 1 if rec.get("dead") else 0
        n_bad += 0 if rec.get("dead") else 1
        cm = (rec.get("tree") or {}).get("certified_min")
        print("[%2d/%2d] %-62s %-10s min %-14s wit %s unres %s  %6.1f s  (total %.0f s)"
              % (n + 1, len(todo), e["id"][9:], rec.get("reason"),
                 ("%.7f" % cm) if isinstance(cm, float) else "-",
                 rec.get("n_witnesses"), rec.get("n_unresolved"), rec["seconds"], spent), flush=True)
        json.dump(dict(cls=a.cls, when=time.strftime("%Y-%m-%dT%H:%M:%S"), run=n + 1,
                       todo=len(todo), certified=n_ok, refused=n_bad, seconds=round(spent, 1)),
                  open(prog, "w", encoding="utf-8"), indent=1)
    print("frame %s DONE: %d certified, %d refused, %.0f s" % (a.cls, n_ok, n_bad, spent),
          flush=True)


if __name__ == "__main__":
    main()
