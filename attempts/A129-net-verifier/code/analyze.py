#!/usr/bin/env python3
"""analyze.py -- A129 T2.  Turn bench60.jsonl into the report table."""
import json
import sys
import statistics as st
import collections

rows = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
print(f"leaves benchmarked: {len(rows)}\n")


def fmt(xs, f="{:.1f}"):
    xs = [x for x in xs if x is not None]
    if not xs:
        return "-"
    return f.format(st.median(xs))


def block(name, sel):
    sub = [r for r in rows if sel(r)]
    if not sub:
        return None
    st_ = collections.Counter(r["net"]["status"] for r in sub)
    ok = [r for r in sub if r["net"]["status"] == "PASS"]
    return {
        "stratum": name, "n": len(sub),
        "reproduced": len(ok), "frac": len(ok) / len(sub),
        "blowup": st_.get("BLOWUP", 0), "margin": st_.get("MARGIN", 0),
        "med_atoms": fmt([r["n_atoms"] for r in sub], "{:.0f}"),
        "med_level_pass": fmt([r["net"]["deepest_level"] for r in ok], "{:.0f}"),
        "med_netleaves_pass": fmt([r["net"]["net_leaves"] for r in ok], "{:.0f}"),
        "med_shrink_pass": fmt([r["net"]["shrink"] for r in ok], "{:.2e}"),
        "med_margin_side_pass": fmt([r["net"]["margin_consumed_side"] for r in ok], "{:.2e}"),
        "med_eta": fmt([abs(r["eta"]) for r in sub if r.get("eta") is not None], "{:.3f}"),
        "med_frozen_s": fmt([r["frozen_wall_s"] for r in sub], "{:.1f}"),
        "med_net_s_pass": fmt([r["net"]["wall_s"] for r in ok], "{:.1f}"),
        "med_ratio_pass": fmt([r["net"].get("wall_ratio_vs_frozen") for r in ok], "{:.0f}"),
        "med_grid_cells": fmt([r["net"]["grid_cells"] for r in sub], "{:.0f}"),
        "med_exempt_tests": fmt([r["net"]["exempt"] for r in sub], "{:.0f}"),
        "med_frozen_boxes": fmt([r["frozen_boxes"] for r in sub], "{:.0f}"),
    }


strata = [("ALL", lambda r: True),
          ("level 1", lambda r: r["level"] == 1),
          ("level 2", lambda r: r["level"] == 2),
          ("A: atoms <= 5", lambda r: r["stratum"] == "A_few_atoms"),
          ("B: atoms 6-30", lambda r: r["stratum"] == "B_mid"),
          ("C: atoms > 30", lambda r: r["stratum"] == "C_many"),
          ("L2 (deep)", lambda r: r["stratum"] == "L2"),
          ("param sub-cells (s_cells>1)", lambda r: (r.get("p96_scells") or 0) > 1),
          ("no param record", lambda r: not r.get("p96_scells")),
          ]
out = []
hdr = ["stratum", "n", "repro", "frac", "MARGIN", "BLOWUP", "atoms", "L*", "netcells",
       "shrink", "d_side", "|eta|", "frozen_s", "net_s", "ratio", "gridcells", "exempt", "frozenboxes"]
print("| " + " | ".join(hdr) + " |")
print("|" + "---|" * len(hdr))
for name, sel in strata:
    b = block(name, sel)
    if not b:
        continue
    out.append(b)
    print("| " + " | ".join(str(x) for x in [
        b["stratum"], b["n"], b["reproduced"], f"{b['frac']:.0%}", b["margin"], b["blowup"],
        b["med_atoms"], b["med_level_pass"], b["med_netleaves_pass"], b["med_shrink_pass"],
        b["med_margin_side_pass"], b["med_eta"], b["med_frozen_s"], b["med_net_s_pass"],
        b["med_ratio_pass"], b["med_grid_cells"], b["med_exempt_tests"], b["med_frozen_boxes"]]) + " |")

print()
allok = [r for r in rows if r["net"]["status"] == "PASS"]
if allok:
    print(f"PASS leaves: net wall total {sum(r['net']['wall_s'] for r in allok):.0f}s vs frozen "
          f"{sum(r['frozen_wall_s'] for r in allok):.0f}s "
          f"(ratio of totals {sum(r['net']['wall_s'] for r in allok)/sum(r['frozen_wall_s'] for r in allok):.1f}x)")
    print(f"  wall ratio per leaf: min {min(r['net']['wall_ratio_vs_frozen'] for r in allok):.1f} "
          f"median {st.median([r['net']['wall_ratio_vs_frozen'] for r in allok]):.1f} "
          f"max {max(r['net']['wall_ratio_vs_frozen'] for r in allok):.1f}")
    print(f"  exempt tests (net) vs boxes (frozen), totals: "
          f"{sum(r['net']['exempt'] for r in allok)} vs {sum(r['frozen_boxes'] for r in allok)}")
fails = [r for r in rows if r["net"]["status"] != "PASS"]
if fails:
    print(f"\nfailures: {len(fails)}")
    for r in sorted(fails, key=lambda r: -r["n_atoms"])[:12]:
        n = r["net"]
        print(f"  {r['id']:30s} atoms={r['n_atoms']:4d} cores={r['n_cores']} {n['status']:7s} "
              f"leaves={n['net_leaves']:5d} L={n['deepest_level']} shrink={n['shrink']:.2e} "
              f"livemin={n['live_min_mass']} frozen={r['frozen_wall_s']:.1f}s")
json.dump(out, open(sys.argv[1].replace(".jsonl", "_table.json"), "w"), indent=1)
