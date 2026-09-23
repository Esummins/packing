# A268 -- terminal leaves: benchmark and launch (2026-09-23)

Notes: `notes/terminal268.md`.  Page: `docs/residue_map/campaigns/A268-terminal-leaves/terminal268.svg`.
Benchmark runs were TEST runs (scratch cert dirs, not certificates); the launched loop below writes the real ones.
Flags always on: A220_NOROOM_INHERIT A221_LANE A224_SNAP (the passes' own); "on" = A268_COUNT=1 (+ A268_FORCE=1 on
the seam).  Walls: 480-540 s in the benchmark (foreground), 1800 s in the launch.

## 1. Where the wall went (A268_TIMING / the certificates' step records)

| representative | run | wall used | in CAPPED counts | what decides it |
|---|---|---|---|---|
| k5_16_interior_Y0384 g1 R.2.1.5.p2.p2.2.2.2 | 31 pass rows, n_nodes 1 | 2,808-5,000 s | 99.8 % (root 757 of 762 s; anon_needed ~2,045 s) | JOINT COUNT infeasible (hidden by the 200k cap) |
| trump5 c0_Y0886 zero R.3.3.2.p1.p1.2.2.2.2.2.2 | 5 nodes, 2 NS | 2,217 s | 99.4 % (14 capped counts 862 s + anon_needed ~1,340 s) | (now inherited DEAD, A256 pass 12) |
| seam synth257 g1 R.1.2.1 / R.1.1 | 6 / 46 nodes | 179 / 576 s | 0 % (counts feasible, ms) | fixed point: ROLE-SPLIT's WIDE gate |

## 2. Off / on

| node | OFF (chain as is) | ON (A268) |
|---|---|---|
| k5 Y0384 g1 R.2.1.5.p2.p2.2.2.2 | ALIVE x 31 passes, 2,808-5,000 s each | **DEAD by JOINT COUNT in 10.2 s** (1 count call, 3.7 s; verify268 VERIFIED, 1,212,429 nodes, 8.7 s) |
| seam R.1.2.1 (A257 far sibling) | ALIVE 179 s (fixed point) | **DEAD in 286 s** (2 forced splits: F1 x, F2 t -> EmptyBox; EPS) |
| seam R.1.1 (A257 far sibling) | ALIVE 576 s, 3 alive leaves | its fixed-point leaf DEAD (3 forced splits); wall 480 s hit in another branch -> launched at 1800 s |
| trump5 g1 c0_Y0169 (root) | DEAD 279 s (count 84 s + anon_needed 43 s) | DEAD 194 s (count 4 s), same tree (75 nodes) |
| trump5 g1 c0_Y0170 (root) | DEAD 302 s (count 113 s + anon 49 s) | DEAD 195 s, same tree (79 nodes) |
| trump5 g1 c0_Y0304 (root) | -- | DEAD 489 s (125 nodes, 12 pocket splits) |
| trump5 g1 c0_Y0970 (root) | -- | DEAD 488 s (122 nodes) |
| trump5 g1 c0_Y0691 (root) | -- | ALIVE at the 540 s wall (127 nodes, depth 8) |
| trump5 g1 c0_Y0880 (root) | -- | ALIVE at the 540 s wall (113 nodes) |

COUNT268 kills: 23 INFEASIBLE counts over the benchmark, 23 VERIFIED by verify268; 100 feasible dumps -> 100 FAILED
(the self-test).  No count268 call was capped anywhere in the benchmark (max 1.2M nodes, the k5 node).

## 3. The residue, recounted

* k5: the A229 loop's "70 start nodes" = ONE live start node (Y0384 g1) + 69 queue lines of 5 pages fold211 reports
  closed; ON kills the one in 10 s.
* trump5: pad 0 has NO start node left (A256 loop, pass 12, 09-22 15:42); the "87" is progress256's count of
  historical ALIVE shard rows.  The trump5 remainder is the g1 window pad: 84 pages, never run.  4 of 6 benchmarked
  roots die inside 540 s (195-490 s), 2 need more wall.
* seam: 2 far siblings, one DEAD by the forced split inside 286 s, the other part-closed.

## 4. Price and launch

Pass 1 = 87 lines (1 k5 + 2 seam + 84 trump5 g1 roots) at 1800 s, 4 workers: <= 43.6 CPU-h upper bound (measured
median of the 6 roots ~490 s -> ~12 CPU-h expected), later passes on the ALIVE roots' children.  Priced well inside
100 CPU-h: LAUNCHED detached (`code/loop268.sh 4 1800`, log `logs/loop268.log`), the STALLED invariant on
(`results/stalled268.txt`), a commit per shard, rows `results/terminal268.jsonl`, verifier rows
`results/verify268.jsonl`.
STOP: `touch attempts/A268-terminal-leaves/logs/STOP_LOOP` (after the pass) or `.../logs/STOP` (after each shard).
RESUME: remove both, relaunch the same line (the pass number continues from `results/ran268.txt`).

## 5. Follow-up (coordinator, 2026-09-23 ~13:00): the k5 fold

* The loop was STOPPED by the coordinator (trump5 g1 ran on A60's delta_pin 3e-8 records: those verdicts are s0-only
  per A256 O1; A269 re-emits the records).  Not relaunched.
* The readers: fold211 folds the LAST `mode=page, pad=g1, verdict=DEAD` row per nid of A211 `results/coarsetree211.jsonl`
  into `superseded_by_coarsetree_A211.jsonl`; load211.census / progress211 read that ledger.  Y0384's shard row
  (12:25:45) was already DEAD; one supplementary row re-emits it with the COUNT268 clause appended to `verifier`
  (`a268_supplement`, `a268_dump` = certs/count268_k5_16_interior_Y0384_bfecebcd18d63407.json, VERIFIED).
* The census's 14 alive nodes = Y0384 + 13 roots whose g1 start nodes were ALL closed by per-start-node shards
  (Lemma INHERIT (c) + PAR: 0 start nodes left in inherit211.merge) but which never had a page-level DEAD row (every
  shard row is ALIVE with its siblings "SKIPPED (filter)").  A plain run211 merge run (`--pads g1 --cert-suffix
  g1_merge268`, no start node to run) wrote each page's DEAD row, citing every inherited kill's certificate:
  Y0954 (k5_11), Y1103, Y1108, and k5_16 Y0127, Y0130, Y0186, Y0280, Y0517, Y0540, Y0687, Y0702, Y0713, Y0738.
* After fold211 + progress211: census 0 alive; frontier 300/303 DEAD rows (the 3 others are Y0738_D01-D03, closed
  by the ancestor Y0738's kill); gallery 17/18 with Y1117 closed by docs/shadows/a57v4/killed.
* rowcascade241 does NOT read A211 at all: its only row sources are (A) parametric window certificates and (B) the
  Lemma K1 climb.  So k5_11 / k5_16 stay [OPEN] there until a source "(C) the A57 class tree closed at the g1
  window pad" is admitted with its own soundness clause -- not added here.
