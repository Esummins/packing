# A149 — three places A57 is paying twice, all found while counting the frontier

None of these is a soundness problem. Every certificate involved is correct for the node it names.
They are all the same shape: **an id is looked up in one file when the corpus keeps it in
several.**

## 1. The shard index moved, so 573 of A137's 849 "fresh" level-1 children were re-screens

`emit137.py --mode l1` builds the whole level-1 cover, shards it `i % 6 == si`, and skips ids
already present in **`tree_<key>_s{si}.jsonl` — its own shard's file only**. The cover has been
re-built with different orderings over the campaign's life, so a child recorded months ago under
`s2` reappears under `s4` today, and the `done` check does not see it.

Measured on the night's own output:

| tree | A137 level-1 rows | of which ids already in the corpus |
|---|---|---|
| `k5_11_interior_G1` | 333 | **213** |
| `k5_16_interior_G1` | 100 | **73** |

397 ids carry more than one row across the six shard files (363 with an identical box, 34 with a
nested one — checked; **0 non-nested**, so a PASS on any row is a valid kill of the node and
"dead wins" is sound when the corpus is collapsed).

**Cost.** 104 of the night's 189 level-1 LP solves were on already-recorded ids, and **71 of those
were already PASS** — about **8 of the 14.85 CPU-h** of the level-1 emission lane went to
re-proving certified-dead nodes. It was not worthless: the re-screen closed 28 previously-open
nodes by geometry (18 ALIVE + 10 FAIL) and 15 more by the LP. But the yield per CPU-h is a third
of what the headline suggests.

**Effect on the published rates.** PAUSED v3's level-1 numbers are a mixture. On the 276 genuinely
new children the geometry rate is **22.5 %, not 27.4 %**, and PASS is **76.5 % of decided, not
78.8 %**. Both corrections move the schedule the *wrong* way, which is why `notes/reprice.md`
uses them.

**Fix (two lines).** `emit137.py`'s `done` set should glob `tree_<key>_s*.jsonl`, not `_s{si}`.

## 2. 563 of the 1,995 unsolved queued LP jobs are already dead

`mkqueue137.py` drops ids that are recorded or claimed. It does not test the id or its ancestors
against the night's own supersession ledgers
(`superseded_by_backlog_A137.jsonl`, `superseded_by_exactcore_A137.jsonl`, 538 ids).

| level | dead jobs still in the queue |
|---|---|
| 1 | 201 |
| 2 | 288 |
| 3 | 73 |
| 4 | 1 |
| **total** | **563 of 1,995 = 28 %** |

A worker started on `queue_bc.json` today spends better than a quarter of its wall on nodes that
are certified dead. Worth ≈ 90 CPU-h on the CENTRAL model.

**Fix (a few lines).** `mkqueue137.py` should carry `fold137.py`'s `anc_dead` test.

## 3. The two re-emission lanes overlap, and one of them is strictly weaker

A137 ran **lane (a)** (the exact-core re-emission: an ALIVE node re-solved on its **recorded**
box) and **lane (b)** (fresh emission: the same node id re-solved on its **T5‴-clipped** box) at
the same time, over overlapping id sets. The clipped box is contained in the recorded box
(checked: 60 of 60), so a lane-(b) verdict is at least as strong as a lane-(a) one.

Of the 141 un-re-solved lane-(a) targets this attempt inherited:

* **24 had already been decided by lane (b) last night** — 8 of them PASS. Re-solving them costs
  ~2.3 CPU-h and cannot produce a stronger verdict. **Dropped.**
* **60 more are still sitting in lane (b)'s queue** with a clipped box available, strictly smaller
  in 17 cases. **Substituted**: A149 solves the clipped box, same cost, strictly stronger, and
  lane (b)'s job for that id becomes redundant.

`code/targets149.py` does both, with a containment check before every substitution;
`results/targets149_dedup.json` records what was dropped and why. Queue 141 → **117**.
