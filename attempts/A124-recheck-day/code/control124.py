"""A124 T2 -- the offline trimming control, re-run with EMPTIED and TRIMMED kept apart.

A123 read the v1 control's "159 boxes gain an empty surviving bin" as boxes TOUCHED (6.62% of
2403) and compared it against a live 6.42% touch rate, which made the live full-kill rate of
1.01% look like a 3.7x shortfall.  This re-runs the same measurement over the same corpus and
reports three disjoint classes per level, against two different denominators, so nothing can be
conflated again:

    EMPTIED    surviving fraction == 0   -- a full T5'' kill, no LP is ever run
    TRIMMED    0 < fraction < 1          -- the bin narrows, the node still costs a full LP
    UNTOUCHED  fraction == 1

and cross-tabs each against whether the DEPLOYED T5' (pinguard.classify with TIGHT_CORE = True,
recomputed here rather than read from the stored cert) already kills the box.  "Incremental" =
EMPTIED and not killed by T5', which is the only class that changes the schedule.

Read-only on A96/A57: it imports trim96.rows/surviving and pinguard.classify unmodified.

    python code/control124.py [--nsub 256]
"""
import argparse, collections, json, math, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
A96 = os.path.join(ATT, "A96-a57-parametric")
A57 = os.path.join(ATT, "A57-shadow-trees")
A53 = os.path.join(ATT, "A53-simple-strata")
sys.path.insert(0, os.path.join(A96, "code"))
sys.path.insert(0, os.path.join(A57, "code"))

import trim96                                   # rows(), surviving(), same geometry
import pinguard
from caselp import Box

DELTA = trim96.DELTA


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nsub", type=int, default=256)
    ap.add_argument("--out", default=os.path.join(BASE, "results", "control124.json"))
    a = ap.parse_args()
    assert pinguard.TIGHT_CORE, "T5' must be on: the incremental count is defined against it"

    slots_all = json.load(open(os.path.join(A53, "results", "name_to_slots.json")))
    hh = DELTA / math.sqrt(2.0)
    P = {}
    for nm in ("k5_11", "k5_16"):
        sl = [tuple(p) for p in slots_all[nm]]
        P[nm] = ([Box(x - hh, x + hh, y - hh, y + hh, 0.0, 0.0) for (x, y) in sl], sl)

    R = trim96.rows()
    rows, t0 = [], time.time()
    for i, r in enumerate(R):
        b = Box.from_json(r["box"])
        pin_boxes, sl = P[r["_name"]]
        # T5' recomputed with the deployed tight core, not read off the stored cert: the corpus
        # contains rows emitted BEFORE the tight core landed, whose cert understates it.
        try:
            kind, _ = pinguard.classify(b, pin_boxes, sl)
        except Exception as e:
            kind = "error:" + type(e).__name__
        frac, alive = trim96.surviving(b, sl, a.nsub)
        cls = "EMPTIED" if frac == 0.0 else ("UNTOUCHED" if frac >= 1.0 else "TRIMMED")
        rows.append(dict(id=r["id"], level=r["_level"], name=r["_name"],
                         cert=str(r.get("cert") or "").split("(")[0].strip(),
                         t5prime=kind, surviving=round(frac, 6), n_intervals=len(alive),
                         klass=cls))
        if (i + 1) % 250 == 0:
            print(f"{i+1}/{len(R)}  {time.time()-t0:.0f}s", flush=True)

    # ---------------------------------------------------------------- tabulate
    def tab(sel):
        c = collections.Counter()
        for x in rows:
            if sel(x):
                c[(x["level"], x["klass"])] += 1
        lv = sorted({k[0] for k in c})
        out = {}
        for L in lv:
            n = sum(c[(L, k)] for k in ("EMPTIED", "TRIMMED", "UNTOUCHED"))
            out[str(L)] = dict(n=n, EMPTIED=c[(L, "EMPTIED")], TRIMMED=c[(L, "TRIMMED")],
                               UNTOUCHED=c[(L, "UNTOUCHED")],
                               emptied_pct=round(100.0 * c[(L, "EMPTIED")] / n, 2) if n else None,
                               trimmed_pct=round(100.0 * c[(L, "TRIMMED")] / n, 2) if n else None,
                               touched_pct=round(100.0 * (c[(L, "EMPTIED")] + c[(L, "TRIMMED")]) / n, 2) if n else None)
        tot = collections.Counter(x["klass"] for x in rows if sel(x))
        n = sum(tot.values())
        out["all"] = dict(n=n, EMPTIED=tot["EMPTIED"], TRIMMED=tot["TRIMMED"],
                          UNTOUCHED=tot["UNTOUCHED"],
                          emptied_pct=round(100.0 * tot["EMPTIED"] / n, 2) if n else None,
                          trimmed_pct=round(100.0 * tot["TRIMMED"] / n, 2) if n else None,
                          touched_pct=round(100.0 * (tot["EMPTIED"] + tot["TRIMMED"]) / n, 2) if n else None)
        return out

    is_kill = lambda x: x["t5prime"] in ("contradictory",)
    survives = lambda x: x["t5prime"] not in ("contradictory", "parent")
    control = dict(t5prime_kills=sum(1 for x in rows if is_kill(x)),
                   t5prime_kills_fully_emptied=sum(1 for x in rows if is_kill(x) and x["klass"] == "EMPTIED"),
                   stored_logic_kills=sum(1 for x in rows if x["cert"].startswith("KILL-BY-LOGIC")),
                   stored_logic_kills_fully_emptied=sum(
                       1 for x in rows if x["cert"].startswith("KILL-BY-LOGIC") and x["klass"] == "EMPTIED"))
    control["positive_control_clean"] = (control["t5prime_kills"] == control["t5prime_kills_fully_emptied"])

    summary = dict(
        corpus=len(rows), nsub=a.nsub,
        positive_control=control,
        all_boxes=tab(lambda x: True),
        excluding_stored_logic_kills=tab(lambda x: not x["cert"].startswith("KILL-BY-LOGIC")),
        incremental_over_T5prime=tab(survives),
        seconds=round(time.time() - t0, 1))
    json.dump(dict(summary=summary, rows=rows), open(a.out, "w"), indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
