"""A161 T4 -- the population table and the overlap analysis.

    python t4_table.py [--src ../results/t3.jsonl] [--md ../notes/t3_table.md]
"""
import argparse
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))

PRIOR = {
    "A141-lane": ["attempts/A141-polycore-lane/results/t4_slots.jsonl"],
    "A142-exactclip": ["attempts/A142-a57-review-gallery/results/exactclip_kills_a57.jsonl",
                       "attempts/A142-a57-review-gallery/results/exactclip_kills_a60.jsonl"],
    "A131-pinclip": ["attempts/A131-pin-clip/results/backlog_kills.jsonl"],
}


def prior_kills():
    out = {}
    for tag, files in PRIOR.items():
        ids = set()
        for f in files:
            p = os.path.join(ROOT, f)
            if not os.path.exists(p):
                continue
            for ln in open(p, encoding="utf-8"):
                try:
                    r = json.loads(ln)
                except Exception:
                    continue
                nid = r.get("nid") or r.get("id")
                if nid and (r.get("verdict") in (None, "KILL")
                            or str(r.get("new_verdict", "")).startswith("KILL")):
                    ids.add(nid)
        out[tag] = ids
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=os.path.join(BASE, "results", "t3.jsonl"))
    ap.add_argument("--md", default=os.path.join(BASE, "notes", "t3_table.md"))
    ap.add_argument("--out", default=os.path.join(BASE, "results", "t3_table.json"))
    a = ap.parse_args()
    rows = [json.loads(ln) for ln in open(a.src, encoding="utf-8")]
    pk = prior_kills()

    by_cs = collections.defaultdict(collections.Counter)      # (cls, slot) -> verdict counter
    by_cl = collections.defaultdict(collections.Counter)      # (cls, level) -> verdict counter
    kills = [r for r in rows if r["verdict"] == "KILL"]
    nm = [r for r in rows if r["verdict"] == "NEAR-MISS"]
    for r in rows:
        by_cs[(r["cls"], r["slot"])][r["verdict"]] += 1
        by_cl[(r["cls"], r["level"])][r["verdict"]] += 1

    kn = set(r["nid"] for r in kills)
    overlap = {t: len(kn & s) for t, s in pk.items()}
    allprior = set().union(*pk.values()) if pk else set()
    fresh = sorted(kn - allprior)

    verdicts = sorted({r["verdict"] for r in rows})
    short = {v: (v.split(" ")[0][:14]) for v in verdicts}

    L = []
    L.append("# A161 T3 — the chord-limited lane over the alive A57/A60 wall-adjacent usable slots")
    L.append("")
    L.append("Population: every alive A57/A60 node (A141's `t2_a5760` pass, nodes A141 already "
             "killed excluded) x every WALL-ADJACENT usable slot whose A141 verdict is UNDECIDED "
             "or NEAR-MISS with `lane_lb <= 1`.")
    L.append("")
    L.append("* pairs run: **%d** over **%d** distinct nodes" % (len(rows),
                                                                 len(set(r["nid"] for r in rows))))
    L.append("* KILLs: **%d** pairs over **%d** distinct nodes; NEAR-MISS (total = 2): %d"
             % (len(kills), len(kn), len(nm)))
    L.append("")
    L.append("## Verdict counts")
    L.append("")
    L.append("| verdict | pairs | what it means |")
    L.append("|---|---|---|")
    MEAN = {
        "KILL": "beta + LANE_out + M <= 1 — the node is DEAD (certificate emitted)",
        "NEAR-MISS": "beta + LANE_out + M = 2 — one unit short",
        "RETIRED-beta>=2": "the chord row leaves room for 2 band squares on every swept wall "
                           "line (the wall carries only ONE pin chord)",
        "NO-LINE (beta + M >= 2 on every swept offset)":
            "beta + M >= 2 on every swept offset: the conditioned square reaches the cell AND the "
            "band cap is 1",
        "RETIRED-outside-witness": "an exact free OUTSIDE pose meeting the cell exists, so "
                                   "LANE_out >= 1 (A159's witness rule)",
        "RETIRED-two-crowd-outside": "TWO interior-disjoint free OUTSIDE poses exist — A159's "
                                     "two-crowd witness retires the cell",
        "M>=2": "two conditioned squares can reach the cell",
        "UNDECIDED": "the outside lane cover did not close inside the budget",
        "CHORD-CONTRADICTION": "SUM minchord > s0 — A144's guard row alone kills the node",
        "ERROR": "run error (see results/t3.jsonl)",
    }
    tot = collections.Counter(r["verdict"] for r in rows)
    for v, c in tot.most_common():
        L.append("| `%s` | %d | %s |" % (v, c, MEAN.get(v, "")))
    L.append("")
    L.append("## By class x slot")
    L.append("")
    L.append("| class | slot | wall | pairs | KILL | NEAR-MISS | beta>=2 | outside-witness | "
             "no-line | undecided |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for (cls, slot) in sorted(by_cs):
        c = by_cs[(cls, slot)]
        ij = slot[3:-1]
        wall = "bottom (h)" if ij.endswith(",0") else "left (v)"
        if ij == "0,0":
            wall = "corner (h+v)"
        L.append("| %s | %s | %s | %d | **%d** | %d | %d | %d | %d | %d |"
                 % (cls, slot, wall, sum(c.values()), c["KILL"], c["NEAR-MISS"],
                    c["RETIRED-beta>=2"],
                    c["RETIRED-outside-witness"] + c["RETIRED-two-crowd-outside"],
                    c["NO-LINE (beta + M >= 2 on every swept offset)"], c["UNDECIDED"]))
    L.append("")
    L.append("## By class x level")
    L.append("")
    L.append("| class | level | pairs | KILL | distinct nodes killed |")
    L.append("|---|---|---|---|---|")
    for (cls, lvl) in sorted(by_cl, key=lambda z: (z[0], z[1] if z[1] is not None else -1)):
        c = by_cl[(cls, lvl)]
        nn = len(set(r["nid"] for r in kills if r["cls"] == cls and r["level"] == lvl))
        L.append("| %s | %s | %d | **%d** | %d |" % (cls, lvl, sum(c.values()), c["KILL"], nn))
    L.append("")
    L.append("## beta split of the kills (which half of the PI's sentence did the work)")
    L.append("")
    bc = collections.Counter((r.get("beta"), r.get("M"), r.get("lane_out")) for r in kills)
    L.append("| beta | M | LANE_out | kills | reading |")
    L.append("|---|---|---|---|---|")
    for (b, m, lo), c in sorted(bc.items(), key=lambda z: (-z[1],)):
        rd = ("the conditioned square IS the one band square (its chord > s0 - 3), nothing else "
              "crosses the wall line" if b == 0 else
              "one free band square is allowed and the conditioned square cannot reach the cell")
        L.append("| %s | %s | %s | %d | %s |" % (b, m, lo, c, rd))
    L.append("")
    L.append("## Overlap with the prior leaves")
    L.append("")
    L.append("| prior campaign | its killed node ids | also killed here | NEW here |")
    L.append("|---|---|---|---|")
    for t, s in sorted(pk.items()):
        L.append("| %s | %d | %d | — |" % (t, len(s), len(kn & s)))
    L.append("| **union of the three** | %d | %d | **%d distinct nodes A161 kills that none of "
             "them killed** |" % (len(allprior), len(kn & allprior), len(fresh)))
    L.append("")
    L.append("A161's kills are therefore **%d genuinely new dead nodes** out of %d killed."
             % (len(fresh), len(kn)))
    L.append("")
    if nm:
        L.append("## NEAR-MISS pairs (total = 2)")
        L.append("")
        L.append("| node | slot | beta | LANE_out | M |")
        L.append("|---|---|---|---|---|")
        for r in nm[:40]:
            L.append("| %s | %s | %s | %s | %s |" % (r["nid"], r["slot"], r.get("beta"),
                                                     r.get("lane_out"), r.get("M")))
        if len(nm) > 40:
            L.append("")
            L.append("(%d more in `results/t3.jsonl`.)" % (len(nm) - 40))
        L.append("")
    open(a.md, "w", encoding="utf-8").write("\n".join(L) + "\n")
    json.dump(dict(n_pairs=len(rows), n_nodes=len(set(r["nid"] for r in rows)),
                   verdicts=dict(tot), n_kill_pairs=len(kills), n_kill_nodes=len(kn),
                   kill_nodes=sorted(kn), new_nodes=fresh, overlap=overlap,
                   prior_sizes={t: len(s) for t, s in pk.items()},
                   beta_split={"%s/%s/%s" % k: v for k, v in bc.items()},
                   by_class_slot={"%s|%s" % k: dict(v) for k, v in by_cs.items()},
                   by_class_level={"%s|%s" % k: dict(v) for k, v in by_cl.items()}),
              open(a.out, "w", encoding="utf-8"), indent=1)
    print("%d pairs, %d KILL pairs / %d nodes, %d NEW nodes -> %s"
          % (len(rows), len(kills), len(kn), len(fresh), a.md))


if __name__ == "__main__":
    main()
