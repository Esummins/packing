"""A106 T3 — the switch: continued branching versus a bottom-up basin certificate per shadow.

Inputs (all A106's own):
  results/t1_boxes.json     open nodes at levels 2-4 with their boxes, tau, eta
  results/t2_shadows.jsonl  per node: box-vs-pin emptiness, the box-constrained side minimum,
                            and the free (box-released) landing
  results/t2a_census.json   the class shadow catalogue

Constants, cited where used:
  * per-child cost 292 s and the level expansion factors 1.44 / 0.91 / 0.76 with decay
    rho = 0.63-0.86 -> 5-9 further levels, 23-26 wall-days at 5 workers: docs/residue_map.md
    section 7 (A96, 2026-09-06).
  * Hbar = 7.9079: the second-order constant A36/A70/A79 certify for the 11-square weighted row
    sum W on Trump's universal box (docs/proofs/contraction_tube.md section 1.5).  Around a
    strict local minimum with side s*, W's Taylor chain gives side >= s* - Hbar*x^2 on the
    box of radius x, so the ball on which the side provably stays above s0 has
    r_basin = sqrt((s* - s0) / Hbar).  Reported with a band Hbar in [4, 16].
"""
from __future__ import annotations
import json, math, os, statistics, collections

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
RES = os.path.join(BASE, "results")

S0 = 969271 / 250000.0
HBAR = 7.9079
HBAR_BAND = (4.0, 16.0)
COST_PER_CHILD_S = 292.0
FANOUT = 8


def med(v):
    return statistics.median(v) if v else float("nan")


def pose_dist_to_box(pose, b):
    """L-inf-ish distance from a square pose (x, y, theta deg) to the box, tilt in radians."""
    dx = max(b["x0"] - pose[0], 0.0, pose[0] - b["x1"])
    dy = max(b["y0"] - pose[1], 0.0, pose[1] - b["y1"])
    dt = math.radians(max(b["th0"] - pose[2], 0.0, pose[2] - b["th1"]))
    return max(dx, dy, dt), math.sqrt(dx * dx + dy * dy + dt * dt)


def main():
    rows = [json.loads(l) for l in open(os.path.join(RES, "t2_shadows.jsonl")) if l.strip()]
    census = json.load(open(os.path.join(RES, "t2a_census.json")))
    lv = json.load(open(os.path.join(RES, "t1_levels.json")))

    out = {"s0": S0, "Hbar": HBAR, "cost_per_child_s": COST_PER_CHILD_S}

    # ------------------------------------------------------------- shadow spectrum per class
    spec = {}
    for cls, d in census.items():
        g = collections.OrderedDict()
        for sh in d["shadows"]:
            k = round(sh["s"], 6)
            e = g.setdefault(k, dict(s=sh["s"], slack=sh["s"] - S0, n_poses=0, hits=0,
                                     endpoint_eps=None, conf=sh["conf"],
                                     tilts=sorted(round(p[2], 3) for p in sh["conf"][5:])))
            e["n_poses"] += 1
            e["hits"] += sh["hits"]
            if sh.get("endpoint_eps") is not None and e["endpoint_eps"] is None:
                e["endpoint_eps"] = sh["endpoint_eps"]
        spec[cls] = list(g.values())
    out["shadow_spectrum"] = {c: [{k: v for k, v in e.items() if k != "conf"} for e in s[:10]]
                              for c, s in spec.items()}

    # ------------------------------------------------------------- per-node
    tbl = []
    for r in rows:
        rec = dict(id=r["id"], cls=r["cls"], level=r["level"], status=r["status"],
                   dmax=r["dmax"], deuc=r.get("deuc"), tau=r.get("tau"), eta=r.get("eta"),
                   pin_empty=bool(r.get("pin_empty")),
                   pin_clash=r.get("pin_clash_worst"))
        sh = r.get("shadow")
        if sh:
            rec.update(s_box=sh["s_box"], slack_box=sh["slack_box"], interior=sh["interior"],
                       free_s=sh["free_s"], free_in_box=sh["free_in_box"])
            # how far is the nearest square of the released shadow from the node's box?
            best = (1e9, 1e9)
            for p in sh["free_conf"]:
                d = pose_dist_to_box(p, r["box"])
                if d[0] < best[0]:
                    best = d
            rec["shadow_gap_inf"], rec["shadow_gap_euc"] = best
        elif r.get("infeasible"):
            rec["resid"] = r["infeasible"]["resid"]
        tbl.append(rec)
    out["nodes"] = tbl

    empty = [r for r in tbl if r["pin_empty"]]
    land = [r for r in tbl if r.get("s_box") is not None]
    nolan = [r for r in tbl if not r["pin_empty"] and r.get("s_box") is None]

    out["counts"] = dict(open_nodes=len(tbl), empty_by_pin=len(empty),
                         landed=len(land), no_landing=len(nolan),
                         landed_with_shadow_in_box=sum(1 for r in land if r["free_in_box"]),
                         landed_interior_min=sum(1 for r in land if r["interior"]))
    per = collections.Counter()
    for r in tbl:
        per[(r["cls"], r["level"], "empty" if r["pin_empty"]
             else ("landed" if r.get("s_box") is not None else "no_landing"))] += 1
    out["counts_by_cell"] = {"/".join(map(str, k)): v for k, v in sorted(per.items())}

    if land:
        sl = sorted(r["slack_box"] for r in land)
        out["box_minimum_slack"] = dict(
            n=len(sl), min=sl[0], q1=sl[len(sl) // 4], median=med(sl),
            q3=sl[3 * len(sl) // 4], max=sl[-1])
        out["shadow_gap"] = dict(
            median_inf=med([r["shadow_gap_inf"] for r in land]),
            min_inf=min(r["shadow_gap_inf"] for r in land),
            median_euc=med([r["shadow_gap_euc"] for r in land]))
        fs = collections.Counter(round(r["free_s"], 6) for r in land)
        out["free_release_landings"] = dict(sorted(fs.items()))

    # ------------------------------------------------------------- the switch, per shadow
    per_shadow = []
    for cls, sp in spec.items():
        for e in sp[:5]:
            slack = e["slack"]
            if slack <= 0:
                continue
            r_b = math.sqrt(slack / HBAR)
            holders = [r for r in land if r["cls"] == cls
                       and abs(r["free_s"] - e["s"]) < 1e-5]
            per_shadow.append(dict(
                cls=cls, s=e["s"], slack=slack, endpoint_eps=e["endpoint_eps"],
                tilts=e["tilts"], n_poses=e["n_poses"],
                r_basin=r_b, r_band=[math.sqrt(slack / HBAR_BAND[1]),
                                     math.sqrt(slack / HBAR_BAND[0])],
                n_open_boxes_flowing_here=len(holders),
                n_open_boxes_containing_it=sum(1 for r in holders if r["free_in_box"]),
                med_box_dmax=med([r["dmax"] for r in holders]),
                med_box_half_dmax=med([r["dmax"] / 2 for r in holders]),
                med_shadow_gap_inf=med([r["shadow_gap_inf"] for r in holders]),
                levels_for_box_radius_to_reach_r_basin=(
                    max(0.0, math.log2(med([r["dmax"] / 2 for r in holders]) / r_b))
                    if holders else None)))
    out["per_shadow_switch"] = per_shadow

    # ------------------------------------------------------------- level geometry vs basin
    r_b = math.sqrt(min(e["slack"] for c in spec.values() for e in c[:1]) / HBAR)
    out["r_basin_lowest_shadow"] = r_b
    out["level_geometry"] = {k: dict(med_dmax=v["med_dmax_all"],
                                     med_half_dmax=v["med_dmax_all"] / 2,
                                     half_over_rbasin=v["med_dmax_all"] / 2 / r_b)
                             for k, v in lv.items()}

    json.dump(out, open(os.path.join(RES, "t3_switch.json"), "w"), indent=1)

    # ------------------------------------------------------------- print
    print("SHADOW SPECTRUM (delta = 1e-2 slack pins, side minimum on the class variety)")
    for cls, s in out["shadow_spectrum"].items():
        print(f"  {cls}: " + ", ".join(f"{e['s']:.6f}(+{e['slack']:.6f})" for e in s[:8]))
    print()
    print("OPEN NODES:", json.dumps(out["counts"]))
    for k, v in out["counts_by_cell"].items():
        print(f"   {k:24s} {v}")
    print()
    if land:
        print("box-constrained side minimum, slack over s0:", json.dumps(out["box_minimum_slack"]))
        print("gap from the box to the nearest square of the released shadow:",
              json.dumps(out["shadow_gap"]))
        print("free-release landings:", out["free_release_landings"])
    print()
    print(f"r_basin (lowest shadow, Hbar = {HBAR}) = {r_b:.6f}")
    for k, v in out["level_geometry"].items():
        print(f"   {k}: med d_max {v['med_dmax']:.6f}, half {v['med_half_dmax']:.6f}, "
              f"half/r_basin {v['half_over_rbasin']:.3f}")
    print()
    for p in per_shadow:
        print(f"  {p['cls']} s*={p['s']:.6f} slack={p['slack']:.6f} r_basin={p['r_basin']:.5f} "
              f"[{p['r_band'][0]:.5f},{p['r_band'][1]:.5f}]  boxes flowing here "
              f"{p['n_open_boxes_flowing_here']}, containing it "
              f"{p['n_open_boxes_containing_it']}, med gap {p['med_shadow_gap_inf']}")


if __name__ == "__main__":
    main()
