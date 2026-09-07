"""A131 -- the RETROSPECTIVE list: recorded-open A57 nodes that the pin-clip empties by logic.

T5' and T5'' are pre-filters on NEWLY EMITTED children (lemmas.md T5': "existing verdicts are not
recomputed or overwritten"), so nodes emitted before those rules landed keep their ALIVE / FAIL
verdicts even when the geometry now kills them.  This driver produces the list, with the witness
pins, so a re-classification pass can be run by the campaign's owner.

IT WRITES NOTHING INTO A57 OR A96.  Output: results/backlog131.jsonl (+ .json summary).
The verdicts here SUPERSEDE nothing until someone lands them in the campaign's own ledger, and
that landing must keep the prior verdict, as A96's superseded_by_tight_core.jsonl does.

    python code/backlog131.py
"""
import json, os, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(BASE, "..", "A57-shadow-trees", "code")))

import pinclip
from t1_check import corpus, SLOTS
from caselp import Box


def witnesses(b, slots, nsub):
    """which pins do the emptying?  single-pin first, else the smallest prefix that empties."""
    for i, sl in enumerate(slots):
        if pinclip.clip_node(b, [sl], nsub=nsub)["empty"]:
            return [i], "single"
    for k in range(2, len(slots) + 1):
        for sub in _combos(range(len(slots)), k):
            if pinclip.clip_node(b, [slots[i] for i in sub], nsub=nsub)["empty"]:
                return list(sub), f"joint-{k}"
    return list(range(len(slots))), "all"


def _combos(it, k):
    import itertools
    return itertools.combinations(list(it), k)


def main():
    nsub = 8
    rows = {json.loads(l)["id"]: json.loads(l) for l in
            open(os.path.join(BASE, "results", "corpus131.jsonl"))}
    C = {r["id"]: r for r in corpus()}
    out = []
    for nid, rec in rows.items():
        v = rec["verdict"]
        if v == "PASS" or not rec[f"emptied{nsub}"]:
            continue
        r = C[nid]
        b = Box.from_json(r["box"])
        w, kind = witnesses(b, SLOTS[rec["cls"]], nsub)
        out.append(dict(id=nid, cls=rec["cls"], level=rec["level"], prior_verdict=v,
                        prior_tau=r.get("tau"), prior_eta=r.get("eta"),
                        box=r["box"], nsub=nsub,
                        t5pp_surviving=rec["t5pp_surviving"],
                        t5pp_alone_empties=rec["t5pp_emptied"],
                        witness_pins=w, witness_kind=kind,
                        witness_slots=[list(SLOTS[rec["cls"]][i]) for i in w],
                        new_verdict="KILL-BY-LOGIC (pin-clip, T5''')"))
    out.sort(key=lambda r: (r["cls"], r["level"], r["id"]))
    p = os.path.join(BASE, "results", "backlog131.jsonl")
    with open(p, "w") as fh:
        for r in out:
            fh.write(json.dumps(r) + "\n")
    summ = dict(n=len(out),
                by_prior=dict(collections.Counter(r["prior_verdict"] for r in out)),
                by_level=dict(collections.Counter(r["level"] for r in out)),
                by_class=dict(collections.Counter(r["cls"] for r in out)),
                by_witness_kind=dict(collections.Counter(r["witness_kind"] for r in out)),
                needs_clip_not_just_trim=sum(1 for r in out if not r["t5pp_alone_empties"]),
                note=("recorded-open (ALIVE/FAIL) A57 nodes the pin-clip empties by logic; "
                      "SUPERSEDES NOTHING until landed in the campaign ledger with the prior "
                      "verdict retained"))
    json.dump(summ, open(os.path.join(BASE, "results", "backlog131.json"), "w"), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
