"""A124 T2 -- re-derive the A57 schedule counting ONLY full T5'' kills.

A trimmed-but-alive node pays the same LP as before (its bin is narrower, not empty), so the
only nodes trimming removes from the budget are the EMPTIED ones -- and each of those also
removes its expected subtree, which is where most of the saving is.

MODEL (all inputs measured, all cited):
  * expansion factor 8p = 0.91 per level (level-2 descent 11.3% into 8 children; residue_map.md
    line 25, A96 2026-09-05), measured on the deployed tree, i.e. already net of T5';
  * the tree terminates at level 4 (level-4 descent 0 of 30, docs/budget.md A);
  * node cost is treated as level-independent (level-2 LP settled at 1.11x, verify 545 s vs
    ~800-900 s per node -- inside the noise of a 13.3 +- 2 wall-day figure);
  * f_L = the INCREMENTAL full-kill rate of T5'' at level L, i.e. emptied AND not already killed
    by T5', measured by control124.py.

    E_L  = expected cost of one emitted level-L node and its subtree
         = g_L * (c + 0.91 * E_{L+1}),   g_L = 1 - f_L,   E_5 = 0, and no descent below 4.

  schedule = 13.3 wall-days * E'_1 / E_1   (E with the rates, E' the T5''-free baseline g == 1)

The 13.3 is the tight-core-only figure (docs/residue_ledger.md line 41; 19.6 without T5').
"""
import json, os

BASELINE_WALLDAYS = 13.3
EXPANSION = 0.91           # 8 * level-2 descent 11.3%
MAXLEVEL = 4


def E(f, expansion=EXPANSION, maxlevel=MAXLEVEL):
    """expected cost of an emitted level-1 node + subtree, in units of one node's cost."""
    nxt = 0.0
    for L in range(maxlevel, 0, -1):
        nxt = (1.0 - f.get(L, 0.0)) * (1.0 + expansion * nxt)
    return nxt


def walldays(f):
    return BASELINE_WALLDAYS * E(f) / E({})


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    base = os.path.abspath(os.path.join(here, ".."))
    c = json.load(open(os.path.join(base, "results", "control124.json")))["summary"]
    inc = c["incremental_over_T5prime"]
    offline = {int(L): inc[str(L)]["EMPTIED"] / inc[str(L)]["n"] for L in (1, 2, 3, 4)}

    # live, A123's night shift: 296 level-1 children, 90 killed by T5' first, so the
    # T5''-eligible population is 206, of which 3 were emptied and 16 merely trimmed.
    live_L1 = 3.0 / 206.0
    ratio = live_L1 / offline[1]

    scen = {}
    scen["no_T5pp (full kills count for nothing)"] = dict(f={}, note="the 13.3 baseline")
    scen["offline rates, all levels"] = dict(f=offline, note="control124, incremental over T5'")
    mixed = dict(offline)
    mixed[1] = live_L1
    scen["live L1, offline L2-L4"] = dict(f=mixed,
                                          note="the only level with live data replaced")
    scen["live L1, L2-L4 discounted by the same ratio"] = dict(
        f={L: (live_L1 if L == 1 else offline[L] * ratio) for L in (1, 2, 3, 4)},
        note=f"pessimistic: every level short by the live/offline factor {ratio:.3f}")

    out = dict(baseline_walldays=BASELINE_WALLDAYS, expansion=EXPANSION,
               offline_rates={str(k): round(v, 5) for k, v in offline.items()},
               live_L1_rate=round(live_L1, 5), live_over_offline_L1=round(ratio, 3),
               scenarios={})
    for k, v in scen.items():
        out["scenarios"][k] = dict(
            walldays=round(walldays(v["f"]), 2),
            cut_pct=round(100.0 * (1.0 - walldays(v["f"]) / BASELINE_WALLDAYS), 1),
            rates={str(a): round(b, 5) for a, b in sorted(v["f"].items())}, note=v["note"])
    json.dump(out, open(os.path.join(base, "results", "schedule124.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
