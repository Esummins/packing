"""A149 Task A -- re-price A57 in docs/budget.md's own model.

Same shape as A124's `schedule124.py` (an expected-cost-of-an-emitted-child recursion with a
per-level geometry kill rate and a per-level descent factor), but ABSOLUTE rather than relative:
A124 scaled a 13.3-wall-day baseline by E'/E because it had no measured node cost.  A137's night
measured one, so the recursion is evaluated in CPU-seconds against a counted frontier.

    E_L = (1 - g_L) * [ c + 8 * d_L * E_{L+1} ]     an EMITTED level-L child, screen not yet run
    F_L =              c + 8 * d_L * E_{L+1}        a child already past the geometry screen
    E_5 = 0                                          the tree terminates at level 4 (A124, docs/budget.md B)

  g_L  probability the geometry screen (T5 / T5' at the EXACT pin core / T5'' trim / T5''' pin-clip
       / T5'''' polygon) kills the child outright: no LP, no certificate, ~0 s.
  d_L  probability that a child which reaches the LP still owes a split afterwards
       (NO-KILL + LOST-KILL-ON-RESOLVE + TOO-TIGHT; a PASS is closed).
  c    CPU-seconds for one LP + s0 exact certificate + FROZEN verify_case.py.

Every input is measured and cited in `rates()`; `scenarios()` states the range.  The frontier is
counted, not modelled: `results/frontier149.json` (never-emitted level-1 children), A137's
queue/ledger files, and A57's own corpus.
"""
import collections
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, ".."))
A57 = os.path.join(ROOT, "A57-shadow-trees", "results")
A137 = os.path.join(ROOT, "A137-night-shift-2", "results")
OUT = os.path.join(BASE, "results", "reprice149.json")

WORKERS = 5.0          # docs/budget.md's "wall-days at 5"
HOURS_PER_DAY = 24.0


# ----------------------------------------------------------------- the recursion
def E(g, d, c, maxlevel=4):
    """expected CPU-s to resolve one EMITTED level-L child and everything under it, per level."""
    out = {maxlevel + 1: 0.0}
    for L in range(maxlevel, 0, -1):
        f = c + 8.0 * (d[L] if L < maxlevel else 0.0) * out[L + 1]
        out[L] = (1.0 - g[L]) * f
    return out


def F(g, d, c, maxlevel=4):
    """... for a child that has ALREADY passed the geometry screen (it is in the LP queue)."""
    e = E(g, d, c, maxlevel)
    return {L: c + 8.0 * (d[L] if L < maxlevel else 0.0) * e.get(L + 1, 0.0)
            for L in range(1, maxlevel + 1)}


# ----------------------------------------------------------------- the frontier, counted
def frontier():
    """`frontier149.py`'s id-level classification -- one entry point per node, no double count."""
    return json.load(open(os.path.join(BASE, "results", "frontier149.json")))


# ----------------------------------------------------------------- measured rates
def rates():
    """Everything here is a count from a file, with the file named."""
    return dict(
        # --- geometry screen, A137 lane (b)+(c), counted from emit_geo_*.jsonl + emitq_*.json
        g1_new=(62, 276),        # level-1 children never before recorded  -> 22.5 %
        g1_all=(245, 849),       # every level-1 child screened, incl. 573 re-screens -> 28.9 %
        g2=(464, 1869),          # level-2 (deepen of the surviving ALIVE) -> 24.8 %
        g3=(82, 256),            # level-3                                 -> 32.0 %
        g4=(7, 8),               # level-4                                 -> 87.5 %
        # --- LP outcome, A137 lane (b), emit_lp_*.jsonl; "owes a split" = NO-KILL + LOST-KILL +
        #     TOO-TIGHT (a PASS is closed; a WALL-CAP is not a verdict and is excluded)
        d1_new=(20, 85),         # on never-before-recorded ids            -> 23.5 %
        d1_all=(39, 188),        # on every decided level-1 node           -> 20.7 %
        # --- node cost, CPU-seconds (LP + s0 exact certificate + FROZEN verify_case.py)
        c_lane_b=14.85 * 3600 / 189.0,     # 283 s, 189 level-1 nodes, exact cores, cap 420 s
        c_lane_a=15.5 * 3600 / 163.0,      # 342 s, 163 exact-core re-solves of ALIVE nodes
        # --- descent below level 1: the only measurement is A96's level-2 descent of ALL emitted
        #     level-2 nodes (residue_map.md line 25), which A124 used as 8p = 0.91
        D2_a96=0.113,
        # --- the exact-core lever, A137 lane (a): 46 of 161 decided
        exactcore_kill=(46, 161),
        exactcore_band_030_045=(15, 63),
        # --- the four-side grid, lemmas.md T23 (2): post-C-check "ok" children per side
        grid_ok={"side1": 821 + 914, "side2": 816 + 907, "side3": 704 + 784, "side4": 695 + 777},
    )


def scen(name, g1, d1, c, D2, drop_orphans, grid_geo, note):
    return dict(name=name, g1=g1, d1=d1, c=c, D2=D2, drop_orphans=drop_orphans,
                grid_geo=grid_geo, note=note)


def price(s, R, FR):
    g = {1: s["g1"], 2: R["g2"][0] / R["g2"][1], 3: R["g3"][0] / R["g3"][1],
         4: R["g4"][0] / R["g4"][1]}
    d = {1: s["d1"], 2: s["D2"] / (1 - g[2]), 3: s["D2"] / (1 - g[3]), 4: 0.0}
    c = s["c"]
    e, f = E(g, d, c), F(g, d, c)
    C = FR["counts"]

    def by_level(k, cost):
        return sum(n * cost(int(L)) for L, n in C.get(k, {}).get("by_level", {}).items())

    # (i) cover children never screened: they pay the geometry screen first
    cost_new = by_level("NEW", lambda L: e[L])
    # (ii) screened, geometry passed, LP not run
    cost_queue = by_level("QUEUED", lambda L: f[L])
    # (iii) recorded ALIVE whose 8 children are ALREADY emitted (and counted in (ii)): the only
    #       work they still owe is the exact-core re-solve, where it has not been run
    cost_exactcore = FR["exactcore_targets_left"] * R["c_lane_a"]
    # (iv) recorded ALIVE whose children are NOT emitted: the LP is paid, the 8 children are not
    cost_alive_u = by_level("ALIVE_U", lambda L: 8.0 * e[min(L + 1, 4)])
    # (v) recorded FAIL: one more solve, then a split with probability d_L.  A FAIL whose children
    #     are already emitted owes only the re-solve.
    cost_failn = by_level("FAILN", lambda L: f[L])
    cost_faild = C.get("FAILD", {}).get("total", 0) * R["c_lane_a"]

    side1 = cost_new + cost_queue + cost_exactcore + cost_alive_u + cost_failn + cost_faild
    if not s["drop_orphans"]:
        side1 += FR.get("orphaned_queue", 330) * f[2]

    # (v) sides 2-4 of the delta = 1e-2 slack-core grid: full tree re-runs.  The C-check has
    #     already removed the free logic kills, so each "ok" child enters at F_1 -- unless the
    #     emission hooks are credited with their measured incremental geometry kill (grid_geo).
    ok234 = R["grid_ok"]["side2"] + R["grid_ok"]["side3"] + R["grid_ok"]["side4"]
    sides234 = ok234 * (e[1] / (1 - g[1]) * (1 - s["grid_geo"]) if s["grid_geo"] else f[1])

    tot = side1 + sides234
    return dict(scenario=s["name"], note=s["note"],
                inputs=dict(g={str(k): round(v, 4) for k, v in g.items()},
                            d={str(k): round(v, 4) for k, v in d.items()},
                            c_s=round(c, 1), D2=s["D2"], drop_orphans=s["drop_orphans"],
                            grid_geo=s["grid_geo"]),
                per_child_s=dict(E1=round(e[1], 1), E2=round(e[2], 1), E3=round(e[3], 1),
                                 F1=round(f[1], 1), F2=round(f[2], 1), F3=round(f[3], 1)),
                side1_cpu_h=dict(
                    new_cover_children=round(cost_new / 3600, 1),
                    lp_queue=round(cost_queue / 3600, 1),
                    exactcore_resolves=round(cost_exactcore / 3600, 1),
                    alive_not_deepened=round(cost_alive_u / 3600, 1),
                    open_fails=round((cost_failn + cost_faild) / 3600, 1),
                    total=round(side1 / 3600, 1)),
                sides234_cpu_h=round(sides234 / 3600, 1),
                total_cpu_h=round(tot / 3600, 1),
                walldays_at_5=round(tot / 3600 / WORKERS / HOURS_PER_DAY, 2))


def main():
    R = rates()
    FR = frontier()
    g1n = R["g1_new"][0] / R["g1_new"][1]
    g1a = R["g1_all"][0] / R["g1_all"][1]
    d1n = R["d1_new"][0] / R["d1_new"][1]
    d1a = R["d1_all"][0] / R["d1_all"][1]
    c = R["c_lane_b"]

    S = [
        scen("CENTRAL", g1n, d1n, c, R["D2_a96"], True, 0.0,
             "the night's rates on the population they were measured on: geometry at the "
             "NEW-id rate (22.5 %), descent at the NEW-id rate (23.5 %), node cost 283 s, "
             "A96's level-2 descent below, the 330 superseded queue jobs dropped, sides 2-4 "
             "credited with no geometry beyond the C-check"),
        scen("LOW", g1a, d1a, 240.0, R["D2_a96"], True, g1n,
             "optimistic and internally consistent: geometry at the all-ids rate (28.9 %), "
             "descent at the all-ids rate (20.7 %), node cost at the 240 s the campaign's LP "
             "cap implies, and the emission hooks credited on sides 2-4 at the measured 22.5 %"),
        scen("HIGH", g1n, d1n, 400.0, 0.16, False, 0.0,
             "pessimistic: node cost 400 s (the top of docs/budget.md B's LP band), descent "
             "below level 1 at docs/budget.md B's ALIVE share rather than A96's 11.3 %, and "
             "the 330 superseded queue jobs NOT dropped"),
        scen("control: budget.md B anatomy", 0.29, 0.19 / 0.71, 850.0, R["D2_a96"], True, 0.0,
             "the SAME frontier priced with docs/budget.md B's pre-night anatomy (29 % logic "
             "kills, ALIVE 19 % of all nodes = 26.8 % of those that reach the LP, ~850 s per "
             "node incl. the 4-D window verify): how much of the change is the rates and how "
             "much is the counted frontier"),
        scen("control: no geometry screen", 0.0, d1n, c, R["D2_a96"], True, 0.0,
             "the marginal value of the emission hooks on the part of the frontier that has NOT "
             "yet been screened (325 new cover children only -- the 1,432 queued jobs are past "
             "the screen already, so this is NOT the hooks' value on the campaign as a whole)"),
    ]
    # THE sensitivity that matters: D2, the fraction of emitted level-2 children that still owe a
    # split, is the ONE input with no measurement under the exact cores -- all 1,117 level-2 LP
    # jobs are queued and untouched.  A96's 0.113 is from the old tree.
    sens = []
    for D2 in (0.05, 0.08, 0.113, 0.15, 0.20, 0.25, 0.30):
        r = price(scen("D2=%.3f" % D2, g1n, d1n, c, D2, True, 0.0, "CENTRAL with D2 varied"),
                  R, FR)
        sens.append(dict(D2=D2, cpu_h=r["total_cpu_h"], walldays_at_5=r["walldays_at_5"],
                         children_per_emitted_L2=round(8 * D2, 3)))

    # where the change from the standing 768 CPU-h comes from.  That figure is lemmas.md T23's
    # grid estimate: 6,418 level-1 "ok" children at 431 s each and NO subtree.
    central = price(S[0], R, FR)
    f1 = central["per_child_s"]["F1"]
    decomp = dict(
        standing_estimate_cpu_h=round(6418 * 431.0 / 3600, 0),
        standing_per_child_s=431.0,
        measured_per_node_s=round(c, 1),
        same_count_at_measured_node_cost_cpu_h=round(6418 * c / 3600, 0),
        subtree_multiplier_F1_over_c=round(f1 / c, 2),
        note="the standing figure counted one LP per level-1 ok child and no descent.  The node "
             "itself got CHEAPER (431 -> 283 s, exact cores); what the estimate never carried is "
             "the subtree, and at the measured level-1 descent one ok child costs %.2f nodes."
             % (f1 / c))

    out = dict(when="2026-09-08", owner="A149", decomposition=decomp,
               model="E_L = (1-g_L)[c + 8 d_L E_{L+1}], E_5 = 0; F_L = E_L/(1-g_L)",
               workers=WORKERS, rates={k: v for k, v in R.items()},
               frontier=FR, scenarios=[price(s, R, FR) for s in S], D2_sensitivity=sens)
    json.dump(out, open(OUT, "w"), indent=1)
    print(json.dumps(dict(frontier=FR), indent=1))
    for r in out["scenarios"]:
        print("\n== %-18s  %8.0f CPU-h   %5.2f wall-days at 5" %
              (r["scenario"], r["total_cpu_h"], r["walldays_at_5"]))
        print("   per child: " + json.dumps(r["per_child_s"]))
        print("   side 1:    " + json.dumps(r["side1_cpu_h"]))
        print("   sides 2-4: %s CPU-h" % r["sides234_cpu_h"])
    print("\n== D2 sensitivity (CENTRAL, everything else fixed)")
    for x in sens:
        print("   D2 %.3f  (%.2f children per emitted L2 node)  %7.0f CPU-h  %6.2f wall-days"
              % (x["D2"], x["children_per_emitted_L2"], x["cpu_h"], x["walldays_at_5"]))
    print("\n-> " + OUT)


if __name__ == "__main__":
    main()
