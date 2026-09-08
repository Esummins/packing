"""A141 T3 -- the fold-in: the kill ledger, the T2 table, and the A118 comparison.

Writes (new files only):
  results/polycore_lane_kills.jsonl   -- A115/A99's node-record shape, one line per kill
  results/t2_table.json               -- cell x corner -> (LANE_K' ub, M, verdict)
  results/t2_vs_a118.json             -- what flips against A118's stored k0 verdicts
  notes/t2_table.md                   -- the same table, readable

    python t3_fold.py
"""
import collections
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
sys.path.insert(0, HERE)

CORNERS = ("BL", "BR", "TR", "TL")
TWELVE = ["l1_071", "l1_104", "l1_124", "l1_148", "l1_153", "l1_158", "l1_159",
          "l2_p114_001", "l2_p65_101", "l2_p65_111", "l2_p74_001",
          "s3_far_BL389484_TR018470"]


def load():
    rows, seen = [], set()
    for f in sorted(glob.glob(os.path.join(BASE, "results", "t2_cells_s*.jsonl"))):
        for ln in open(f, encoding="utf-8"):
            r = json.loads(ln)
            key = (r["cell"], r.get("group"))
            if key in seen:
                continue
            seen.add(key)
            rows.append(r)
    # the same cell can appear both in A140's `twelve` and in its `pool`: keep the twelve's row
    best = {}
    for r in rows:
        c = r["cell"]
        if c not in best or (r.get("group") == "twelve"):
            best[c] = r
    return [best[c] for c in sorted(best)]


def a118_verdict(r, corner):
    a = r.get("a118") or {}
    v = a.get(corner + "(0,0)")
    return v


def main():
    rows = load()
    kills, near = [], []
    for r in rows:
        for c in CORNERS:
            v = r["corners"][c]
            if v["verdict"] == "KILL":
                kills.append((r, c, v))
            elif v["verdict"].startswith("NEAR-MISS"):
                near.append((r, c, v))

    # ---------------------------------------------------------------- the kill ledger
    p = os.path.join(BASE, "results", "polycore_lane_kills.jsonl")
    with open(p, "w", encoding="utf-8") as fh:
        for (r, c, v) in kills:
            fh.write(json.dumps(dict(
                src="A141", nid=r["cell"], path=r.get("record"),
                cls="k0_00", level=r.get("level"), corner=c + "(0,0)",
                tau=r.get("tau"), budget=r.get("budget"), converged=r.get("converged"),
                lane=v["lane_ub"], M=v["M"], meeters=v["meeters"],
                leaf="LANE_K' + M <= 1  (K0-FREE / teleport_packing, conditional on k1_00)",
                cert=dict(kind="polycore_lane_v1",
                          path=r["certs"][c]["path"], sha256=r["certs"][c]["sha256"],
                          checker="attempts/A141-polycore-lane/code/check141.py"),
                verdict="DEAD BY POLYCORE LANE (pending k1_00)")) + "\n")
        for r in rows:
            for pr in r.get("pairs", []):
                fh.write(json.dumps(dict(
                    src="A141", nid=r["cell"], path=r.get("record"), cls="k0_00",
                    level=r.get("level"), corner=None,
                    tau=r.get("tau"), budget=r.get("budget"), converged=r.get("converged"),
                    lane=None, M=None, meeters=[pr["i"], pr["j"]],
                    leaf="conditioned squares %d and %d share a certified rational point "
                         "(shared_point_same_square) -- the hypothesis is contradictory"
                         % (pr["i"], pr["j"]),
                    cert=dict(kind="polycore_pair_v1", path=pr["cert"], sha256=pr["sha256"],
                              checker="attempts/A141-polycore-lane/code/check141.py"),
                    verdict="DEAD BY POLYCORE PAIR (unconditional)")) + "\n")
        # the deep-cover kills (T5b) and the A57/A60 usable-slot kills (T4)
        q = os.path.join(BASE, "results", "t5_deep.jsonl")
        if os.path.exists(q):
            for ln in open(q, encoding="utf-8"):
                z = json.loads(ln)
                if not z.get("kill"):
                    continue
                fh.write(json.dumps(dict(
                    src="A141", nid=z["cell"],
                    path=next((x.get("record") for x in rows if x["cell"] == z["cell"]), None),
                    cls="k0_00", level=None, corner=z["corner"] + "(0,0)",
                    lane=z["lane_ub"], M=z["M"], meeters=None,
                    leaf="LANE_K' + M <= 1 (deep cover; K0-FREE / teleport_packing, "
                         "conditional on k1_00)",
                    cert=dict(kind="polycore_lane_v1", path=z["cert"], sha256=z["sha256"],
                              checker="attempts/A141-polycore-lane/code/check141.py"),
                    verdict="DEAD BY POLYCORE LANE (pending k1_00)")) + "\n")
        q = os.path.join(BASE, "results", "t4_slots.jsonl")
        if os.path.exists(q):
            seen_slot = set()
            for ln in open(q, encoding="utf-8"):
                z = json.loads(ln)
                if z.get("verdict") != "KILL" or (z["nid"], z["slot"]) in seen_slot:
                    continue
                seen_slot.add((z["nid"], z["slot"]))
                fh.write(json.dumps(dict(
                    src="A141", nid=z["nid"], path=None, cls=z["cls"], level=z["level"],
                    corner=z["slot"], lane=z["lane_ub"], M=z["M"], meeters=z["meeters"],
                    leaf="LANE_K' + M <= 1 at a USABLE SLOT (SLOT-CROWD: >= 2 non-pin meeters "
                         "impossible; teleport into the certified-dead extension class)",
                    cert=dict(kind="polycore_slot_lane_v1", path=z["cert"],
                              sha256=z["sha256"],
                              checker="attempts/A141-polycore-lane/code/check141.py"),
                    verdict="DEAD BY POLYCORE SLOT LANE")) + "\n")
    print("wrote", p)

    # ---------------------------------------------------------------- the table
    table = {}
    for r in rows:
        table[r["cell"]] = dict(
            group=r.get("group"), level=r.get("level"), n_boxes=r["n_boxes"],
            converged=r.get("converged"), tau=r.get("tau"), budget=r.get("budget"),
            corners={c: dict(lane_ub=r["corners"][c]["lane_ub"],
                             lane_lb=r["corners"][c]["lane_lb"],
                             M=r["corners"][c]["M"],
                             M_exact=r["corners"][c].get("M_exact"),
                             verdict=r["corners"][c]["verdict"],
                             meeters=r["corners"][c]["meeters"],
                             a118=a118_verdict(r, c)) for c in CORNERS},
            pair_kills=[(pp["i"], pp["j"]) for pp in r.get("pairs", [])],
            kill_corners=sorted(r.get("certs", {})))
    json.dump(dict(cells=len(rows), kills=len(kills), near_misses=len(near), table=table),
              open(os.path.join(BASE, "results", "t2_table.json"), "w", encoding="utf-8"),
              indent=1)

    # ---------------------------------------------------------------- vs A118
    flips = []
    for r in rows:
        for c in CORNERS:
            old = a118_verdict(r, c)
            v = r["corners"][c]
            if old is None:
                continue
            old_kill = (old.get("lane_ub") is not None
                        and old["lane_ub"] + (old.get("ncond_pot") or 0) <= 1)
            new_kill = v["verdict"] == "KILL"
            if old_kill != new_kill or (old.get("lane_ub") != v["lane_ub"]):
                flips.append(dict(cell=r["cell"], corner=c,
                                  a118=dict(verdict=old["verdict"], lane_ub=old.get("lane_ub"),
                                            M=old.get("ncond_pot"), kill=old_kill),
                                  a141=dict(verdict=v["verdict"], lane_ub=v["lane_ub"],
                                            M=v["M"], kill=new_kill)))
    new_kills = [f for f in flips if f["a141"]["kill"] and not f["a118"]["kill"]]
    no_a118 = [(r["cell"], c) for r in rows for c in CORNERS
               if a118_verdict(r, c) is None and r["corners"][c]["verdict"] == "KILL"]
    json.dump(dict(flips=flips, new_kills=new_kills, kills_without_an_a118_row=no_a118),
              open(os.path.join(BASE, "results", "t2_vs_a118.json"), "w", encoding="utf-8"),
              indent=1)

    # ---------------------------------------------------------------- markdown
    lines = ["# A141 T2 — the K′ lane test on every open k0 cell",
             "",
             f"{len(rows)} distinct open k0 cells (A140's twelve + A115's open pool), four corners "
             f"each. `ub` = certified LANE_K′ upper bound, `M` = conditioned squares that can meet "
             f"the widened corner box, `A118` = the stored axis-core verdict.",
             "", "## The twelve converged-alive cells", "",
             "| cell | boxes | " + " | ".join(CORNERS) + " | pair | verdict |",
             "|---|---|" + "---|" * (len(CORNERS) + 2)]

    def fmt(v):
        ub = "-" if v["lane_ub"] is None else str(v["lane_ub"])
        m = "?" if v["M"] is None else (str(v["M"]) + ("" if v.get("M_exact") else "+"))
        tag = {"KILL": "**KILL**", "NEAR-MISS": "near", "NEAR-MISS-OR-WORSE": "near?",
               "LANE>=2": "open", "UNDECIDED": "und."}.get(v["verdict"], v["verdict"])
        return f"{tag} L≤{ub} M={m}"

    for n in TWELVE:
        r = next((x for x in rows if x["cell"] == n), None)
        if r is None:
            continue
        pk = ",".join(f"{i}~{j}" for (i, j) in
                      [(pp["i"], pp["j"]) for pp in r.get("pairs", [])]) or "-"
        verdict = ("DEAD (pair)" if r.get("pairs") else
                   "DEAD (lane)" if r.get("certs") else "alive")
        lines.append("| `%s` | %d | %s | %s | %s |" %
                     (n, r["n_boxes"],
                      " | ".join(fmt(r["corners"][c]) for c in CORNERS), pk, verdict))

    lines += ["", "## Kills in the wider open pool", "",
              "| cell | corner | LANE_K′ | M | meeter | A118 said |", "|---|---|---|---|---|---|"]
    for (r, c, v) in sorted(kills, key=lambda z: z[0]["cell"]):
        old = a118_verdict(r, c)
        lines.append("| `%s` | %s | %s | %s | %s | %s |" %
                     (r["cell"], c, v["lane_ub"], v["M"], v["meeters"],
                      "—" if old is None else
                      f"{old['verdict']} (M={old.get('ncond_pot')})"))
    lines += ["", "## Near-misses (LANE_K′ + M = 2): which two squares", "",
              "| cell | corner | LANE_K′ | M | the two |", "|---|---|---|---|---|"]
    for (r, c, v) in sorted(near, key=lambda z: z[0]["cell"]):
        who = ("one free square + conditioned %s" % v["meeters"]) if (v["lane_ub"] or 0) >= 1 \
            else ("conditioned %s" % v["meeters"])
        lines.append("| `%s` | %s | %s | %s | %s |" %
                     (r["cell"], c, v["lane_ub"], v["M"], who))
    open(os.path.join(BASE, "notes", "t2_table.md"), "w", encoding="utf-8").write(
        "\n".join(lines) + "\n")
    print("cells %d  kills %d  near-misses %d  new-vs-A118 %d  kills with no A118 row %d"
          % (len(rows), len(kills), len(near), len(new_kills), len(no_a118)))
    print(collections.Counter(v["verdict"] for r in rows for v in r["corners"].values()))


if __name__ == "__main__":
    main()
