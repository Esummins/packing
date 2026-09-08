"""A144 -- the distribution numbers for the report, from results/offline144.jsonl."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
RES = os.path.join(BASE, "results")

rows = [json.loads(l) for l in open(os.path.join(RES, "offline144.jsonl"), encoding="utf-8")
        if l.strip()]
ok = [r for r in rows if r.get("max_viol") is not None]
viol = sorted([r for r in ok if r["max_viol"] > 1e-9], key=lambda r: -r["max_viol"])

bins = [(1e-9, 0.01), (0.01, 0.05), (0.05, 0.10), (0.10, 0.15), (0.15, 0.25), (0.25, 1e9)]
dist = {f"({a:g},{b:g}]": sum(1 for r in viol if a < r["max_viol"] <= b) for a, b in bins}

ch = {}
for r in ok:
    k = r["max_chords_ge1"]
    ch[k] = ch.get(k, 0) + 1

# the honest "how many chords of length >= 1 sit on the argmax line": hypothesis chords counted
# one each, LP columns counted with their DUAL WEIGHT (a fractional support has many columns of
# tiny weight, so an unweighted count over-reads).
wch = {}
for r in ok:
    t = r["top_rows"][0] if r["top_rows"] else None
    if not t:
        continue
    n = t["n_pin_chords_full"] + (1 if t["minchord_H"] >= 1 - 1e-12 else 0)
    n += sum(c["y"] for c in t["cols"] if c["chord"] >= 1 - 1e-12)
    k = round(n, 3)
    wch[k] = wch.get(k, 0) + 1
w_ge4 = sum(v for k, v in wch.items() if k >= 4 - 1e-9)
w_ge4_viol = 0
for r in viol:
    t = r["top_rows"][0]
    n = t["n_pin_chords_full"] + (1 if t["minchord_H"] >= 1 - 1e-12 else 0) \
        + sum(c["y"] for c in t["cols"] if c["chord"] >= 1 - 1e-12)
    w_ge4_viol += int(n >= 4 - 1e-9)

lines_hist = {}
for r in viol:
    k = r["n_lines_violated"]
    lines_hist[k] = lines_hist.get(k, 0) + 1

orient = {"h": 0, "v": 0}
tags = {}
for r in viol:
    orient[r["max_viol_line"]["orient"]] += 1
    t = r["max_viol_line"]["tag"]
    tags[t] = tags.get(t, 0) + 1

uses = {}
for r in ok:
    for t in r["top_rows"][:1]:
        uses[t["uses"]] = uses.get(t["uses"], 0) + 1

out = dict(
    n_measured=len(ok), n_violating=len(viol),
    pct_violating=round(100.0 * len(viol) / len(ok), 2),
    depth_distribution=dist,
    median_violation=(sorted(r["max_viol"] for r in viol)[len(viol) // 2] if viol else None),
    max_violation=(viol[0]["max_viol"] if viol else None),
    max_violation_node=(viol[0]["id"] if viol else None),
    n_lines_violated_hist=dict(sorted(lines_hist.items())),
    chords_ge1_hist=dict(sorted(ch.items())),
    n_with_ge4_chords=sum(1 for r in ok if r["max_chords_ge1"] >= 4),
    violating_with_ge4_chords=sum(1 for r in viol if r["max_chords_ge1"] >= 4),
    weighted_chords_ge1_on_argmax_line_hist=dict(sorted(wch.items())),
    n_with_weighted_ge4=w_ge4, violating_with_weighted_ge4=w_ge4_viol,
    argmax_line_orientation=orient, argmax_line_tag=tags,
    rhs_source_on_best_line=uses,
    by_class={c: [sum(1 for r in viol if r["cls"] == c), sum(1 for r in ok if r["cls"] == c)]
              for c in ("k5_11", "k5_16")},
    by_level={str(l): [sum(1 for r in viol if r["level"] == l),
                       sum(1 for r in ok if r["level"] == l)] for l in (1, 2, 3)},
    violating_in_top40_by_subtree_cost=sum(1 for r in viol if r["rank"] <= 40),
    n_top40=sum(1 for r in ok if r["rank"] <= 40),
    top20=[dict(id=r["id"], viol=round(r["max_viol"], 6), rank=r["rank"],
                level=r["level"], chords_ge1=r["max_chords_ge1"],
                line=f"{r['max_viol_line']['orient']}={r['max_viol_line']['off_float']:.6f} "
                     f"({r['max_viol_line']['tag']})") for r in viol[:20]],
)
json.dump(out, open(os.path.join(RES, "analyse144.json"), "w", encoding="utf-8"), indent=1)
print(json.dumps(out, indent=1))
