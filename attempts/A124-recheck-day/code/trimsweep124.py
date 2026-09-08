"""A124 T1 addendum -- bank the ZERO-COST T5'' kills in the ALIVE queue, and persist their
excluded intervals.

The coordinator's observation, confirmed here: 57 of the 414 queued ALIVE rows have an EMPTY
surviving bin under the deployed `trim57.trim_box`.  `recheck96 --trimmed` (and this attempt's
`recheck124`) already record those as TRIM-KILL **before** any LP -- the `if not subs` branch
precedes `solve_node` and `continue`s, wall_s 0.0 -- so no LP time is being spent on them.  But
they are reached in queue order, i.e. only after every earlier node has paid its ~900-1500 s, so
54 free kills were sitting behind ~13 CPU-h of LP work.  This banks them immediately.

It also fixes, for these rows, the auditability gap of PAUSED.md v2 section 6: the excluded tilt
intervals are written out (`excluded_intervals`), not just counted, so the coverage claim
"original bin = surviving pieces + excluded intervals" is checkable from the results.

Zero LP, zero certificates, no A57 writes.  Appends to A96's recheck96.jsonl (its own schema,
plus the extra key) and to this attempt's ledger.

    python code/trimsweep124.py [--dry-run]
"""
import argparse, json, math, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
A96 = os.path.join(ATT, "A96-a57-parametric")
A57 = os.path.join(ATT, "A57-shadow-trees")
A53 = os.path.join(ATT, "A53-simple-strata")
sys.path.insert(0, os.path.join(A96, "code"))
sys.path.insert(0, os.path.join(A57, "code"))

import recheck96, trim57
from caselp import Box
from recheck124 import A96_RES, A124_RES, append, ledger


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    slots = json.load(open(os.path.join(A53, "results", "name_to_slots.json")))
    done = ledger()
    rem = [r for r in recheck96.alive_rows() if (r["_cls"], r["id"]) not in done]
    n = 0
    for r in rem:
        sl = [tuple(p) for p in slots[r["_name"]]]
        b = Box.from_json(r["box"])
        subs, excl = trim57.trim_box(b, sl)
        if subs:
            continue
        n += 1
        iv = [[float(x), float(y)] for (x, y) in
              ((getattr(e, "th0", e[0]), getattr(e, "th1", e[1])) for e in excl)]
        rec = dict(id=r["id"], cls=r["_cls"], verdict="TRIM-KILL", excluded=len(excl),
                   wall_s=0.0, excluded_intervals=iv,
                   original_bin=[float(b.th0), float(b.th1)],
                   source="A124 trimsweep124 (zero-LP sweep of the ALIVE queue)",
                   when=time.strftime("%Y-%m-%d %H:%M:%S"))
        print(f"{r['id']:38s} L{1+r['id'].count('_D')} TRIM-KILL  bin "
              f"[{b.th0:.4f},{b.th1:.4f}] excluded={len(excl)}", flush=True)
        if not a.dry_run:
            append(A96_RES, rec)
            append(A124_RES, dict(rec, shard="sweep", level=1 + r["id"].count("_D")))
    print(f"{'would record' if a.dry_run else 'recorded'} {n} zero-cost T5'' kills", flush=True)


if __name__ == "__main__":
    main()
