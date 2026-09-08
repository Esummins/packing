"""A157 T3 -- the fold-in: A141's `polycore_lane_kills.jsonl` record format, in a NEW file.

A141's own ledger is READ-ONLY (the brief forbids appending to it), so the kills land in
`attempts/A157-undecided-slots/results/slot_kills157.jsonl` with the identical schema, plus an
`origin` field naming the A141 row this cell came from.

    python fold157.py
"""
import argparse
import collections
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))

LEAF = ("LANE_K' + M <= 1 at a USABLE SLOT (SLOT-CROWD: >= 2 non-pin meeters impossible; "
        "teleport into the certified-dead extension class)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", default=",".join(
        [os.path.join(BASE, "results", "t157_cells.jsonl"),
         os.path.join(BASE, "results", "t157_cells_s1.jsonl"),
         os.path.join(BASE, "results", "t157_deep.jsonl")]))
    ap.add_argument("--recs", default=os.path.join(BASE, "results", "recs157.json"))
    ap.add_argument("--out", default=os.path.join(BASE, "results", "slot_kills157.jsonl"))
    ap.add_argument("--summary", default=os.path.join(BASE, "results", "summary157.json"))
    a = ap.parse_args()

    recs = json.load(open(a.recs, encoding="utf-8"))
    RANK = {"KILL": 0, "NEAR-MISS": 1, "NEAR-MISS-OR-WORSE": 2, "LANE>=2": 3,
            "UNDECIDED": 4, "ERROR": 5}
    best = {}
    for p in [x for x in a.cells.split(",") if x and os.path.exists(x)]:
        with open(p, encoding="utf-8") as fh:
            for ln in fh:
                ln = ln.strip()
                if not ln:
                    continue
                d = json.loads(ln)
                k = (d["nid"], d["slot"])
                cur = best.get(k)
                if cur is None or RANK.get(d.get("verdict"), 9) < RANK.get(cur.get("verdict"), 9):
                    best[k] = d
    rows = list(best.values())

    kills = [r for r in rows if r.get("verdict") == "KILL"]
    with open(a.out, "w", encoding="utf-8") as fh:
        for r in sorted(kills, key=lambda r: (r["src"], r["cls"], r["nid"], r["slot"])):
            fh.write(json.dumps(dict(
                src="A157", nid=r["nid"], path=recs.get(r["nid"], {}).get("path"),
                cls=r["cls"], level=r["level"], corner=r["slot"],
                lane=r["lane_ub"], M=r["M"], meeters=r["meeters"], leaf=LEAF,
                cert=dict(kind="polycore_slot_lane_v1",
                          path=r["cert"].replace("/", os.sep), sha256=r["sha256"],
                          checker="attempts/A141-polycore-lane/code/check141.py"),
                origin=dict(attempt="A141", file="results/t2_a5760_s{0,1}.jsonl",
                            key=r.get("key"), verdict="UNDECIDED",
                            lane_lb=r.get("a141_lane_lb"), M=r.get("a141_M"),
                            why="LANE cover exhausted its open budget at "
                                "max_open=1200, depth0=20"),
                caveat="exact-pin form, class-S composition, A118-O1 stands",
                verdict="DEAD BY POLYCORE SLOT LANE")) + "\n")

    def tally(pred):
        return collections.Counter((r["cls"], r["slot"]) for r in rows if pred(r))

    # ---- the screen population (task 2's cheap half)
    import glob
    scr = []
    for p in sorted(glob.glob(os.path.join(BASE, "results", "screen157*.jsonl"))):
        with open(p, encoding="utf-8") as fh:
            for ln in fh:
                ln = ln.strip()
                if ln:
                    scr.append(json.loads(ln))
    retired = [r for r in scr if r["lane_lb"] + r["a141_M"] >= 2]
    cand = [r for r in scr if r["lane_lb"] + r["a141_M"] <= 1]
    ran = set((r["nid"], r["slot"]) for r in rows)
    screen_summ = dict(
        n_screened=len(scr), sample_per_cell=(scr[0]["sample"]["drawn"] if scr else None),
        retired_by_realised_free_pose=len(retired),
        retired_with_disjoint_pair=sum(1 for r in retired if r["lane_lb"] == 2),
        retired_by_class_slot={"%s %s" % k: v for k, v in collections.Counter(
            (r["cls"], r["slot"]) for r in retired).most_common()},
        retired_by_class_level={"%s L%s" % k: v for k, v in collections.Counter(
            (r["cls"], r["level"]) for r in retired).most_common()},
        retired_clearance_below_1e4=sum(1 for r in retired if r["best_margin"] < 1e-4),
        kill_possible=len(cand),
        kill_possible_by_lb_M={"lb%d/M%d" % k: v for k, v in collections.Counter(
            (r["lane_lb"], r["a141_M"]) for r in cand).most_common()},
        kill_possible_by_class_slot={"%s %s" % k: v for k, v in collections.Counter(
            (r["cls"], r["slot"]) for r in cand).most_common()},
        kill_possible_nodes=len(set(r["nid"] for r in cand)),
        covers_run=len(ran & set((r["nid"], r["slot"]) for r in cand)),
        covers_not_run=len([r for r in cand if (r["nid"], r["slot"]) not in ran]),
        not_run_cells=[dict(nid=r["nid"], slot=r["slot"], cls=r["cls"], level=r["level"],
                            M=r["a141_M"], clearance=r["best_margin"])
                       for r in cand if (r["nid"], r["slot"]) not in ran],
    )

    summ = dict(
        screen=screen_summ,
        n_cells_run=len(rows),
        by_verdict={k: v for k, v in collections.Counter(
            r.get("verdict") for r in rows).most_common()},
        kills=len(kills),
        kills_by_class={k: v for k, v in collections.Counter(
            r["cls"] for r in kills).most_common()},
        kills_by_class_slot={"%s %s" % k: v for k, v in tally(
            lambda r: r.get("verdict") == "KILL").most_common()},
        kills_by_class_level={"%s L%s" % (r0, l0): c for (r0, l0), c in collections.Counter(
            (r["cls"], r["level"]) for r in kills).most_common()},
        kills_by_src={k: v for k, v in collections.Counter(
            r["src"] for r in kills).most_common()},
        kill_nodes=len(set(r["nid"] for r in kills)),
        near_miss=[dict(nid=r["nid"], slot=r["slot"], cls=r["cls"], level=r["level"],
                        lane_ub=r["lane_ub"], M=r["M"])
                   for r in rows if r.get("verdict") == "NEAR-MISS"],
        not_closed=[dict(nid=r["nid"], slot=r["slot"], cls=r["cls"], level=r["level"],
                         lane_ub=r["lane_ub"], lane_lb=r["lane_lb"], M=r["M"],
                         depth_reached=max((s["depth0"] for s in r.get("steps") or []),
                                           default=None),
                         max_open=max((s["max_open"] for s in r.get("steps") or []),
                                      default=None),
                         leaves=(r.get("steps") or [{}])[-1].get("leaves"),
                         open_leaves=(r.get("steps") or [{}])[-1].get("open"),
                         hist=(r.get("steps") or [{}])[-1].get("hist"),
                         secs=r.get("secs"))
                    for r in rows if r.get("verdict") not in ("KILL", "NEAR-MISS")],
    )
    json.dump(summ, open(a.summary, "w", encoding="utf-8"), indent=1)
    show = {k: v for k, v in summ.items() if k not in ("near_miss", "not_closed")}
    show["screen"] = {k: v for k, v in show["screen"].items() if k != "not_run_cells"}
    print(json.dumps(show, indent=1))
    print("near-miss %d, not-closed %d -> %s"
          % (len(summ["near_miss"]), len(summ["not_closed"]), a.summary))
    print("wrote %d kill rows -> %s" % (len(kills), a.out))


if __name__ == "__main__":
    main()
