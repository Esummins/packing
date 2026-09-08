"""A158 -- pick the top-N (node, slot) cells of the population and write the two job files.

Rank: the PI's selector is "dual support weight >= 0.5 in some usable slot's S box".  730 of the
1,238 selected nodes sit at exactly w = 1 (one whole dual square in the slot box), so the weight
alone does not order them.  The tiebreak is stated, not invented at read time:

    key = ( -w  (the PI's weight),
            -sum of w over ALL usable slots of the node   (how much of the dual sits in slots),
            |budget - tau|                                (knife-edge nodes first: the NO child
                                                           only has to move tau at all),
            nid )

The three PI-named cells are pinned at the head in the order the PI named them.

    python mktop158.py --n 20
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))

PINNED = [("c0_Y0076", "TL(0,0)"), ("c0_Y0787", "BR(0,1)"), ("c0_Y0959", "TR(0,1)"),
          ("k5_11_interior_Y0130", "TR(0,0)"), ("k5_11_interior_Y0147", "TR(0,0)")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pop", default=os.path.join(BASE, "results", "pop158.jsonl"))
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--out", default=os.path.join(BASE, "results", "top158.jsonl"))
    a = ap.parse_args()

    rows = [json.loads(l) for l in open(a.pop, encoding="utf-8") if l.strip()]
    rows = [r for r in rows if r["w_max"] >= 0.5]

    def key(r):
        eta = abs(r["eta"]) if r["eta"] is not None else 9.9
        return (-r["w_max"], -sum(e["w"] for e in r["slots"]), eta, r["nid"])

    rows.sort(key=key)
    byid = {r["nid"]: r for r in rows}
    out, seen = [], set()
    recs = json.load(open(os.path.join(BASE, "results", "recs158.json"), encoding="utf-8"))
    for (nid, slot) in PINNED:
        r = byid.get(nid)
        if r is None:                     # PI-named but NOT selected by the weight (w = 0)
            q = recs[nid]
            out.append(dict(nid=nid, slot=slot, cls=q["cls"], src=q["src"], level=q["level"],
                            w=0.0, ext=None, tau=q.get("tau"),
                            eta=(None if q.get("tau") is None else
                                 round(q["budget"] - q["tau"], 12)),
                            pinned=True, not_in_population=True))
            seen.add((nid, slot))
            continue
        e = next((x for x in r["slots"] if x["slot"] == slot), None)
        out.append(dict(nid=nid, slot=slot, cls=r["cls"], src=r["src"], level=r["level"],
                        w=(e or {}).get("w", 0.0) or 0.0, ext=(e or {}).get("ext"),
                        tau=r["tau"], eta=r["eta"], pinned=True,
                        w_max_slot=r["slots"][0]["slot"] if r["slots"] else None,
                        w_max=r["w_max"]))
        seen.add((nid, slot))
    for r in rows:
        if len(out) >= a.n:
            break
        e = max((x for x in r["slots"] if x["w"] >= 0.5), key=lambda x: x["w"], default=None)
        if e is None or (r["nid"], e["slot"]) in seen:
            continue
        seen.add((r["nid"], e["slot"]))
        out.append(dict(nid=r["nid"], slot=e["slot"], cls=r["cls"], src=r["src"],
                        level=r["level"], w=e["w"], ext=e["ext"], tau=r["tau"], eta=r["eta"],
                        pinned=False))
    with open(a.out, "w", encoding="utf-8") as fh:
        for j in out:
            fh.write(json.dumps(j) + "\n")
    for j in out:
        print("%-34s %-9s %-7s L%-2s w=%.3f ext=%-6s eta=%.3g%s"
              % (j["nid"], j["slot"], j["cls"], j["level"], j["w"] or 0.0, j["ext"] or "-",
                 j["eta"] if j["eta"] is not None else float("nan"),
                 "  [PI]" if j["pinned"] else ""))
    print("wrote %s (%d cells)" % (a.out, len(out)))


if __name__ == "__main__":
    main()
