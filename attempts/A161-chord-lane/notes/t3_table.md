# A161 T3 — the chord-limited lane over the alive A57/A60 wall-adjacent usable slots

Population: every alive A57/A60 node (A141's `t2_a5760` pass, nodes A141 already killed excluded) x every WALL-ADJACENT usable slot whose A141 verdict is UNDECIDED or NEAR-MISS with `lane_lb <= 1`.

* pairs run: **2377** over **1223** distinct nodes
* KILLs: **98** pairs over **96** distinct nodes; NEAR-MISS (total = 2): 1

## Verdict counts

| verdict | pairs | what it means |
|---|---|---|
| `RETIRED-outside-witness` | 845 | an exact free OUTSIDE pose meeting the cell exists, so LANE_out >= 1 (A159's witness rule) |
| `NO-LINE (beta + M >= 2 on every swept offset)` | 769 | beta + M >= 2 on every swept offset: the conditioned square reaches the cell AND the band cap is 1 |
| `RETIRED-beta>=2` | 485 | the chord row leaves room for 2 band squares on every swept wall line (the wall carries only ONE pin chord) |
| `UNDECIDED` | 126 | the outside lane cover did not close inside the budget |
| `KILL` | 98 | beta + LANE_out + M <= 1 — the node is DEAD (certificate emitted) |
| `RETIRED-two-crowd-outside` | 53 | TWO interior-disjoint free OUTSIDE poses exist — A159's two-crowd witness retires the cell |
| `NEAR-MISS` | 1 | beta + LANE_out + M = 2 — one unit short |

## By class x slot

| class | slot | wall | pairs | KILL | NEAR-MISS | beta>=2 | outside-witness | no-line | undecided |
|---|---|---|---|---|---|---|---|---|---|
| k5_11 | BR(0,1) | left (v) | 270 | **0** | 0 | 212 | 11 | 47 | 0 |
| k5_11 | TL(1,0) | bottom (h) | 270 | **0** | 0 | 225 | 6 | 39 | 0 |
| k5_16 | BL(1,0) | bottom (h) | 310 | **45** | 1 | 0 | 144 | 94 | 26 |
| k5_16 | BR(0,1) | left (v) | 226 | **0** | 0 | 0 | 148 | 70 | 8 |
| k5_16 | BR(1,0) | bottom (h) | 198 | **1** | 0 | 0 | 92 | 84 | 21 |
| k5_16 | TL(1,0) | bottom (h) | 240 | **26** | 0 | 0 | 114 | 81 | 19 |
| k5_16 | TR(0,1) | left (v) | 186 | **0** | 0 | 0 | 110 | 68 | 8 |
| k5_16 | TR(1,0) | bottom (h) | 188 | **0** | 0 | 0 | 106 | 70 | 12 |
| trump5 | BL(0,2) | left (v) | 72 | **1** | 0 | 0 | 17 | 46 | 8 |
| trump5 | BR(0,1) | left (v) | 187 | **23** | 0 | 0 | 74 | 82 | 8 |
| trump5 | TL(0,0) | corner (h+v) | 55 | **2** | 0 | 0 | 30 | 15 | 8 |
| trump5 | TR(0,1) | left (v) | 110 | **0** | 0 | 0 | 42 | 60 | 8 |
| trump5 | TR(1,0) | bottom (h) | 65 | **0** | 0 | 48 | 4 | 13 | 0 |

## By class x level

| class | level | pairs | KILL | distinct nodes killed |
|---|---|---|---|---|
| k5_11 | 1 | 314 | **0** | 0 |
| k5_11 | 2 | 201 | **0** | 0 |
| k5_11 | 3 | 17 | **0** | 0 |
| k5_11 | 4 | 8 | **0** | 0 |
| k5_16 | 1 | 1264 | **71** | 69 |
| k5_16 | 2 | 84 | **1** | 1 |
| trump5 | 1 | 489 | **26** | 26 |

## beta split of the kills (which half of the PI's sentence did the work)

| beta | M | LANE_out | kills | reading |
|---|---|---|---|---|
| 0 | 1 | 0 | 65 | the conditioned square IS the one band square (its chord > s0 - 3), nothing else crosses the wall line |
| 1 | 0 | 0 | 30 | one free band square is allowed and the conditioned square cannot reach the cell |
| 0 | 0 | 0 | 3 | the conditioned square IS the one band square (its chord > s0 - 3), nothing else crosses the wall line |

## Overlap with the prior leaves

| prior campaign | its killed node ids | also killed here | NEW here |
|---|---|---|---|
| A131-pinclip | 132 | 3 | — |
| A141-lane | 244 | 0 | — |
| A142-exactclip | 51 | 3 | — |
| **union of the three** | 426 | 6 | **90 distinct nodes A161 kills that none of them killed** |

A161's kills are therefore **90 genuinely new dead nodes** out of 96 killed.

## NEAR-MISS pairs (total = 2)

| node | slot | beta | LANE_out | M |
|---|---|---|---|---|
| k5_16_interior_Y0143_D01 | BL(1,0) | 1 | 1 | 0 |


---

# A161 continuation (2026-09-08, +3 CPU-h): the retry, A141's own leaf, and the CORRECTED overlap

## T5 — the 126 UNDECIDED pairs at 60 s/pair

Two findings, in order of importance.

1. **A longer budget alone buys nothing.** The first retry (60 s/pair, 30,000-box budget, single
   guard line) re-ran 12 pairs and every one ended `time budget exhausted` with `lane_out = None`.
   The covers do not converge; they grind.
2. **WHICH guard line is tried matters far more than how long.** On Y0842 the cover blows a
   40,000-box budget at `y_L = 0.9167` and closes in 163 leaves at `y_L = 0.7917`. `run_slot` now
   tries the top `--nlines_try` ranked offsets, each with its own slice of the pair budget.
   With `--nlines_try 6`: **127 of the 136 pairs re-run, 13 new KILLs**, 22 decisively RETIRED (a
   free OUTSIDE pose exists on every viable offset, so `LANE_out >= 1` is realised — these are now
   closed as no-go, not merely unfinished), 92 still UNDECIDED, 9 not reached (wall cap).

Also landed in `chordlane.cover`: budget exhaustion no longer discards the cover. The remaining
stack is folded into the open set — `leaves + open` still TILES the root — so the pairwise
always-overlap test can still certify `LANE <= 1`. (It certifies nothing on these particular cells:
the open sets are 600-800 boxes and spread across the window.)

## T6 — A141's OWN leaf (`LANE_K' + M <= 1`) with the exact separating-axis test

Population: every A141 `t2_a5760` cell (ALL usable slots, not only wall-adjacent) whose verdict is
UNDECIDED / NEAR-MISS / NEAR-MISS-OR-WORSE with `lane_lb <= 1`, on a node A141 did not kill — 3,103
pairs. `run141x.py` re-decides them with `box_misses_cell_exact` in both covers and **no chord row
and no band prune**, so a kill there would be a kill under A141's leaf exactly as A141 states it.

| stage | result |
|---|---|
| exact `M` over 3,048 of the 3,103 pairs (0.24 s/pair) | `M = 0` on **1,169**, `M = 1` on 1,879 |
| **`M` flips** (A141 recorded `M >= 1`, the exact SAT test gives `M = 0`) | **105** |
| LANE cover on 220 of the 1,169 `M = 0` pairs (4.5 s/pair) | **0 kills** — every one `lane_ub = None`, open sets 600-800 boxes |

**The conclusion is a clean negative and it is the useful part.** The exact separating-axis test is
necessary but not sufficient: it fixes the `M` side (105 flips, and it is what made Y0842 close),
but on its own it produces **zero** new kills under A141's leaf, because the LANE side never closes
without the chord row. Without the `band` prune the entire wall row of poses is free and spread, so
`LANE >= 2` is not excludable by any cover. **The chord row is doing the essential work in every
A161 kill, not the SAT fix.** `certs141x/` is therefore empty; `check141x.py` (A141's own
`check_lane_cert` with `leaf_misses` widened to accept the exact-SAT `axis` reason code) is
validated end-to-end against two of A141's own certificates (2/2 PASS).

## T7 — the CORRECTED overlap (and a correction to this attempt's first report)

The authority is the collector `docs/shadows/status_gallery.py` builds STATUS.md from: **44 sources,
5,474 records, 4,994 kills, 3,173 distinct node ids recorded dead by non-A161 sources.** The first
A161 report compared against only three prior campaigns (A131, A141, A142) and claimed 90 new dead
nodes. **That number was wrong.** Against the full dead set:

| A161 pass | kill nodes | already dead elsewhere | **NEW** | prior sources |
|---|---|---|---|---|
| T3 chord lane | 96 | 72 | **24** | A57 tree 62, A137 9, A156 4, A131 3, A142 3, A149 3 |
| T5 retry | 10 | 6 | **4** | A137 5, A131 2, A57 tree 2, A142 1, A156 1 |
| T6 A141x | 0 | 0 | **0** | — |
| **union** | **105** | **78** | **27** | |

The dominant prior is `A57 tree` (62 nodes): A161's population was built from A141's `t2_a5760`
snapshot, and A149's and A156's re-solves have since marked many of those nodes dead in A57's own
tree jsonl. The lesson for the next pass is to build the population from the collector, not from a
campaign snapshot.

**The 27 distinct new dead nodes** — 23 trump5 (A60) and 4 k5_16 (A57), all level 1:

`c0_Y0075, c0_Y0174, c0_Y0475, c0_Y0984, c0_Y0990, c0_Y0991, c0_Y0992, c0_Y1080, c0_Y1083,
c0_Y1084, c0_Y1085, c0_Y1087, c0_Y1088, c0_Y1091, c0_Y1092, c0_Y1093, c0_Y1094, c0_Y1095,
c0_Y1097, c0_Y1098, c0_Y1099, c0_Y1100, f1_L23_0030, k5_16_interior_Y0150,
k5_16_interior_Y0727, k5_16_interior_Y0842, k5_16_interior_Y1146`

by slot: BR(0,1) 20, BL(1,0) 3, TL(0,0) 2, BR(1,0) 1, BL(0,2) 1. **The PI's node
`k5_16_interior_Y0842` is among them.** 109/109 certificates PASS `checkcl.py`.
