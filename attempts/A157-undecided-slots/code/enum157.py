"""A157 T1 -- enumerate the UNDECIDED usable-slot cells of A141's A57/A60 sweep.

Target population: alive-node cells of `t2_a5760_s{0,1}.jsonl` with

    verdict == "UNDECIDED"  and  lane_lb == 0  and  M <= 1

i.e. the 8k-pose sample found NO free pose meeting the slot cell and the (exactly certified)
count of conditioned meeters is at most one.  Those are the probable `LANE_K' = 0, M <= 1` kills.

Writes `results/undecided_cells.jsonl` (the job list) and `results/enum157.json` (the tables).
READ-ONLY on A141.

    python enum157.py
"""
import argparse
import collections
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
A141 = os.path.join(ROOT, "attempts", "A141-polycore-lane", "results")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(BASE, "results", "undecided_cells.jsonl"))
    ap.add_argument("--table", default=os.path.join(BASE, "results", "enum157.json"))
    a = ap.parse_args()

    recs = []
    for f in ("t2_a5760_s0.jsonl", "t2_a5760_s1.jsonl"):
        p = os.path.join(A141, f)
        with open(p, encoding="utf-8") as fh:
            for ln in fh:
                ln = ln.strip()
                if ln:
                    recs.append((f, json.loads(ln)))

    tot = collections.Counter()
    jobs = []
    for f, r in recs:
        for c in r["cells"]:
            tot[(bool(r.get("alive")), c.get("verdict"))] += 1
            if not r.get("alive"):
                continue
            if c.get("verdict") != "UNDECIDED":
                continue
            if c.get("lane_lb") != 0:
                continue
            M = c.get("M")
            if M is None or M > 1:
                continue
            jobs.append(dict(shard=f, key=r["key"], src=r["src"], nid=r["nid"], cls=r["cls"],
                             level=r["level"], slot=c["cell"], lane_lb=c.get("lane_lb"),
                             M=M, M_exact=c.get("M_exact"), meeters=c.get("meeters"),
                             a141_cover_leaves=c.get("cover_leaves"),
                             a141_cover_open=c.get("cover_open"),
                             a141_cover_hist=c.get("cover_hist"),
                             a141_lane_ub=c.get("lane_ub")))

    # c0_Y0076 first, then A60 before A57, then by class / slot / nid
    def keyf(j):
        return (0 if j["nid"] == "c0_Y0076" else 1, 0 if j["src"] == "A60" else 1,
                j["cls"], j["slot"], j["nid"])
    jobs.sort(key=keyf)

    by_cls = collections.Counter(j["cls"] for j in jobs)
    by_slot = collections.Counter((j["cls"], j["slot"]) for j in jobs)
    by_lvl = collections.Counter((j["cls"], j["level"]) for j in jobs)
    by_M = collections.Counter(j["M"] for j in jobs)
    with open(a.out, "w", encoding="utf-8") as fh:
        for j in jobs:
            fh.write(json.dumps(j) + "\n")
    tbl = dict(n_records=len(recs), n_cells=sum(tot.values()),
               verdicts={"%s/%s" % (k[0], k[1]): v for k, v in sorted(tot.items())},
               n_target=len(jobs), n_target_nodes=len(set(j["nid"] for j in jobs)),
               by_class={k: v for k, v in by_cls.most_common()},
               by_class_slot={"%s %s" % k: v for k, v in by_slot.most_common()},
               by_class_level={"%s L%s" % k: v for k, v in by_lvl.most_common()},
               by_M={str(k): v for k, v in sorted(by_M.items())},
               a141_open_leaves_nonzero=sorted(
                   (j["nid"], j["slot"], j["a141_cover_open"]) for j in jobs
                   if j["a141_cover_open"]))
    json.dump(tbl, open(a.table, "w", encoding="utf-8"), indent=1)
    print(json.dumps(tbl, indent=1))


if __name__ == "__main__":
    main()
