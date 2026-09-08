"""A151 T3 -- what the asymmetric N would close, and whether it beats the exact-core re-solve.

Joins: the S02-family nodes ALIVE now (results/alive_s02.json), A120/A136's in-N board
(attempts/A96-a57-parametric/results/a120_closures.jsonl, last row per id), the exact-core
re-solve outcomes per node (results/family_rates.json), and the consumer counts of the symmetric
and asymmetric N (results/consumer151.json).

READ-ONLY on every campaign.
"""
from __future__ import annotations
import json, os, collections, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
RES = os.path.join(BASE, "results")
A96 = os.path.join(ROOT, "attempts", "A96-a57-parametric", "results")

alive = json.load(open(os.path.join(RES, "alive_s02.json"), encoding="utf-8"))
alive_ids = {e["nid"] for e in alive["s02_alive"]}
fr = json.load(open(os.path.join(RES, "family_rates.json"), encoding="utf-8"))
L1 = fr["L1_rows"]

board = {}
for ln in open(os.path.join(A96, "a120_closures.jsonl"), encoding="utf-8"):
    if ln.strip():
        r = json.loads(ln)
        board[r["id"]] = r
status = collections.Counter(r["status"] for r in board.values())

cons = json.load(open(os.path.join(RES, "consumer151.json"), encoding="utf-8"))
base = cons[0]
# "best" = the largest CERTIFIED asymmetric N (the combined spec is a conjecture and is excluded)
best = max((c for c in cons if "certified" in c["label"]), key=lambda c: c["inside"])
conj = max((c for c in cons if "CONJECTURE" in c["label"]), key=lambda c: c["inside"], default=None)


def cset(c):
    return {r["nid"] for r in c["rows"] if r["inside"]}


S_base, S_best = cset(base), cset(best)
new = S_best - S_base
new_alive = new & alive_ids
base_alive = S_base & alive_ids
board_of = {i: board[i]["status"] for i in board}
out_board = dict(
    n_targets=len(board),
    base_inN=len(S_base), base_inN_alive=len(base_alive),
    base_inN_alive_on_board=collections.Counter(board_of.get(i, "not-a-target") for i in base_alive),
    best_inN=len(S_best), best_inN_alive=len(S_best & alive_ids),
)

# what the exact-core re-solve already did to the alive S02 population
resolved = {nid: L1[nid]["result"] for nid in alive_ids if nid in L1}
res_counts = collections.Counter(resolved.values())
not_resolved = sorted(alive_ids - set(resolved))

# A136 costs (notes/results136.md, measured)
COST_PER_CLOSURE = 2932.0          # s, mean over the 9 new closures
COST_PER_TARGET = 45102.0 / 13.0   # s, 13 new targets attempted
CLOSE_RATE = 9.0 / 13.0
# exact-core re-solve (A151 T1, S02 family)
S02 = fr["L1"]["S02"]
S02_dec = S02["_n"] - S02.get("WALL-CAP", 0)
S02_RATE = S02["PASS"] / S02_dec
S02_WALL = 513.0                   # median s

out = dict(
    alive_s02=len(alive_ids),
    in_N_board=dict(status),
    board_detail=dict(out_board, base_inN_alive_on_board=dict(out_board["base_inN_alive_on_board"])),
    consumer_base=dict(label=base["label"], inside=base["inside"], inside_alive=base["inside_alive"]),
    consumer_best=dict(label=best["label"], inside=best["inside"], inside_alive=best["inside_alive"]),
    consumer_conjecture=(None if conj is None else
                         dict(label=conj["label"], inside=conj["inside"],
                              inside_alive=conj["inside_alive"])),
    new_consumers=len(new), new_consumers_alive=len(new_alive),
    new_consumer_ids=sorted(new_alive),
    alive_already_resolved=dict(res_counts), n_never_resolved=len(not_resolved),
    a136=dict(cost_per_closure_s=COST_PER_CLOSURE, cost_per_target_s=round(COST_PER_TARGET, 1),
              close_rate=round(CLOSE_RATE, 3)),
    exactcore_s02=dict(rate=round(S02_RATE, 4), median_wall_s=S02_WALL,
                       cost_per_kill_s=round(S02_WALL / S02_RATE, 0)),
)
# the forward comparison, on the SAME nodes: the alive S02 nodes that are new consumers
n_new_alive = len(new_alive)
already = sum(1 for nid in new_alive if nid in resolved)
out["forward"] = dict(
    yes_no_expected_closures=round(CLOSE_RATE * n_new_alive, 1),
    yes_no_cost_h=round(COST_PER_TARGET * n_new_alive / 3600.0, 1),
    yes_no_cost_per_closure_h=round(COST_PER_TARGET / CLOSE_RATE / 3600.0, 2),
    exactcore_expected_kills_on_same=round(S02_RATE * (n_new_alive - already), 1),
    exactcore_already_failed_on=already,
    exactcore_cost_h=round(S02_WALL * (n_new_alive - already) / 3600.0, 2),
    exactcore_cost_per_kill_h=round(S02_WALL / S02_RATE / 3600.0, 2),
)
json.dump(out, open(os.path.join(RES, "t3_consequence.json"), "w", encoding="utf-8"), indent=1)
print(json.dumps(out, indent=1))
