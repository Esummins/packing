"""A149 -- the A60 (trump5) exact-core re-emission queue.

Population: the alive trump5 nodes of A107's gallery (`shadow_nodes.json`, `src = A60`), minus
every node already certified dead:

  * A142's exact-clip kills          `attempts/A142-a57-review-gallery/results/exactclip_kills_a60.jsonl`
  * A141's slot-lane kills           `attempts/A141-polycore-lane/results/polycore_lane_kills.jsonl`, cls = trump5
  * A137's fold-in into A60          `attempts/A60-trump5-campaign/results/superseded_by_backlog_A137.jsonl`
    (which is the union of the two above as folded on 2026-09-08)
  * anything this attempt has already certified

Order: the coordinator's named start `c0_Y0215` first (the BL(1,1) near-simple square at tilt
82-90 deg, stored tau 5.5 against budget 5, grazer columns within a few hundredths of K'(H)), then
by |tau - budget| ascending -- on A60 there is no `frac_exact` measurement, so the closest analogue
of A145's predictor is how far the stored LP is from the budget.  A node with no stored box or no
node file is skipped and reported, never silently dropped.

Read-only on A60, A107, A141, A142: only `results/targets_a60.json` under THIS attempt is written.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, ".."))
A60 = os.path.join(ROOT, "A60-trump5-campaign")
A107 = os.path.join(ROOT, "A107-shadow-gallery", "results", "shadow_nodes.json")
A141 = os.path.join(ROOT, "A141-polycore-lane", "results", "polycore_lane_kills.jsonl")
A142 = os.path.join(ROOT, "A142-a57-review-gallery", "results", "exactclip_kills_a60.jsonl")
OUT = os.path.join(BASE, "results", "targets_a60.json")
FIRST = "c0_Y0215"


def jl(p):
    out = []
    if os.path.exists(p):
        for ln in open(p, encoding="utf-8"):
            ln = ln.strip()
            if ln:
                try:
                    out.append(json.loads(ln))
                except Exception:
                    pass
    return out


def main():
    gal = json.load(open(A107))
    alive = {}
    for fam, rows in gal.items():
        for r in rows:
            if r.get("src") == "A60":
                alive.setdefault(r["nid"], dict(r, families=[]))["families"].append(fam)

    dead = set()
    for r in jl(A142):
        dead.add(r.get("id"))
    for r in jl(A141):
        if r.get("cls") == "trump5":
            dead.add(r.get("nid"))
    for r in jl(os.path.join(A60, "results", "superseded_by_backlog_A137.jsonl")):
        dead.add(r.get("id"))
    for f in ("superseded_by_exactcore_a60_A149.jsonl", "superseded_by_exactcore_a60_v3_A149.jsonl"):
        for r in jl(os.path.join(BASE, "results", f)):
            dead.add(r.get("id"))
    dead.discard(None)

    done = set()
    for f in os.listdir(os.path.join(BASE, "results")):
        if f.startswith("a60_reemit_") and f.endswith(".jsonl"):
            for r in jl(os.path.join(BASE, "results", f)):
                done.add(r.get("id"))

    T, skipped = [], []
    for nid, r in alive.items():
        if nid in dead or nid in done:
            continue
        p = os.path.join(A60, "results", "nodes", nid + ".json")
        if not os.path.exists(p):
            skipped.append(dict(id=nid, why="no node json under A60 results/nodes"))
            continue
        T.append(dict(id=nid, node=p, budget=r.get("budget", 5), scope="exH",
                      level=r.get("level"), tau=r.get("tau"), families=r["families"],
                      cls="trump5"))

    def key(t):
        tau, b = t.get("tau"), t.get("budget") or 5
        gap = abs((tau if tau is not None else b) - b)
        return (0 if t["id"] == FIRST else 1, gap, t["id"])
    T.sort(key=key)
    json.dump(T, open(OUT, "w"), indent=0)
    json.dump(skipped, open(os.path.join(BASE, "results", "targets_a60_skipped.json"), "w"),
              indent=1)
    print("A60 alive in the gallery: %d; already dead: %d; already run here: %d; "
          "no node file: %d" % (len(alive), sum(1 for n in alive if n in dead),
                                sum(1 for n in alive if n in done), len(skipped)))
    print("%d targets -> %s" % (len(T), OUT))
    print("first five: " + ", ".join("%s (tau %s)" % (t["id"], t.get("tau")) for t in T[:5]))


if __name__ == "__main__":
    main()
