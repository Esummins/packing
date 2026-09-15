# A229 -- verification: one page run WHOLE vs the same page run as three `--start` SHARDS, merged

Page `k5_16_interior_Y0500`, pad `g1`, isolated certificate directories under `attempts/A229-start-parallel/certs/verify/`,
isolated results jsonl `results/verify229.jsonl`, `--no-fig`; the pass-6 workers and their pages untouched.
Driver `code/verify229.sh` (resumable), comparison `code/test_inherit_multi229.py --compare`.

## The shared prior state (phase `base`)

A short wall in an EMPTY certificate directory, so the A211 sources are only what this run wrote:
verdict **ALIVE** at the WALL, 603 s, 43 nodes, 8 inherited dead, 5 start node(s) offered.

Its 5 start node(s), longest-first (`queue229.py`): `R.2.3`, `R.2.1.8`, `R.2.2`, `R.2.4`, `R.3`.

## The two ways of running it

| run | wall | verdict | s | nodes | dead leaves | alive leaves | start nodes run | skipped (filter) |
|---|---|---|---|---|---|---|---|---|
| whole (1 process) | 1586 | DEAD | 1580 | 106 | 81 | 0 | 5 | 0 |
| shard s1 `--start R.2.3,R.2.4` | 486 | ALIVE | 482 | 35 | 32 | 0 | 2 | 3 |
| shard s2 `--start R.2.1.8,R.3` | 1028 | ALIVE | 1024 | 54 | 43 | 0 | 2 | 3 |
| shard s3 `--start R.2.2` | 56 | ALIVE | 54 | 17 | 22 | 0 | 1 | 4 |

Sequential total of the three shards **1570 s**; the longest shard **1028 s** -- that is the wall the three would
have taken RUN IN PARALLEL, against **1586 s** for the whole page in one process (speed-up x1.54).  The shards were
run one after another here so that at most one test python of this campaign ran at a time beside the live pass-6
workers; each had its own certificate directory holding only the shared `base` certificate, so none of them saw a
sibling's work -- exactly the state three simultaneous processes would have had.

## The check (`--compare whole merge`)

`certs/verify/merge/` = the `base` certificate + the three shard certificates `coarsetree211_k5_16_interior_Y0500__s{1,2,3}.json`.
`inherit211.merge` is run over that directory and over `certs/verify/whole/`; the two must agree on

* the set of **DEAD path keys** (every branch closed, whichever file closed it -- Lemma INHERIT (a), file-wise), and
* the set of **next START nodes** (what the following pass would run).

```
2026-09-15 09:22:19 the shared state has 5 start node(s) at pad g1: R.2.3 R.2.1.8 R.2.2 R.2.4 R.3
2026-09-15 10:15:00 merge dir: coarsetree211_k5_16_interior_Y0500.json coarsetree211_k5_16_interior_Y0500__s1.json coarsetree211_k5_16_interior_Y0500__s2.json coarsetree211_k5_16_interior_Y0500__s3.json
   OK   k5_16_interior_Y0500 g1   DEAD path set : 13 == 13
   OK   k5_16_interior_Y0500 g1   START node set: 0 == 0
2026-09-15 10:15:01 verify229: comparison rc=0
```

Proof that this is the right check: `notes/parallel229.md` Lemma PAR and its corollary.
