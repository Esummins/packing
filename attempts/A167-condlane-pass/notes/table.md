# A167 -- the conditional chord-limited lane, population pass

Population (built from the collector: 5742 records, 5258 kills, 46 sources, 3214 distinct dead node ids): **416 cells** over **258** alive A57/A60 nodes.

Cells RUN: **416** of 416.

| verdict | cells | meaning |
|---|---|---|
| `KILL` | 15 | every piece of `B_H` closed: `n(b) <= 1` everywhere, the node is DEAD |
| `NO-GO-witness` | 285 | some piece has NO viable guard offset -- a sampled free meeter forces the leaf's own counters to `>= 2` at every swept offset |
| `UNDECIDED-time` | 116 | the 60 s cell budget ran out with covers unresolved |

## By class x slot (population cells in the last column)

| class | slot | run | KILL | NO-GO | UNDEC | in population |
|---|---|---|---|---|---|---|
| trump5 | BR(0,1) | 66 | **10** | 36 | 20 | 66 |
| k5_16 | BL(1,0) | 54 | **4** | 18 | 32 | 54 |
| trump5 | TR(0,1) | 48 | **1** | 34 | 13 | 48 |
| k5_16 | BR(1,0) | 47 | **0** | 33 | 14 | 47 |
| k5_16 | BR(0,1) | 38 | **0** | 32 | 6 | 38 |
| trump5 | BL(0,2) | 36 | **0** | 28 | 8 | 36 |
| k5_16 | TR(0,1) | 35 | **0** | 25 | 10 | 35 |
| k5_16 | TL(1,0) | 31 | **0** | 30 | 1 | 31 |
| k5_16 | TR(1,0) | 29 | **0** | 26 | 3 | 29 |
| trump5 | TL(0,0) | 16 | **0** | 8 | 8 | 16 |
| k5_11 | BR(0,1) | 6 | **0** | 5 | 1 | 6 |
| trump5 | TR(1,0) | 6 | **0** | 6 | 0 | 6 |
| k5_11 | TL(1,0) | 4 | **0** | 4 | 0 | 4 |

## Overlap with the collector's dead set

| | nodes |
|---|---|
| kill nodes (distinct) | 15 |
| already dead per the collector | 0 |
| **distinct NEW dead nodes** | **15** |

NEW: `c0_Y0902, c0_Y0913, c0_Y0921, c0_Y0989, c0_Y0993, c0_Y0994, c0_Y0995, c0_Y0996, c0_Y0997, c0_Y1002, c0_Y1131, k5_16_interior_Y0191, k5_16_interior_Y0281, k5_16_interior_Y0635, k5_16_interior_Y0663`

## Exact two-crowd witnesses (`nogo_two_crowd_v1`)

60 NO-GO cells escalated, **49** carry an EXACT rational two-crowd witness (both squares inside the container, both meeting `int C`, interiors disjoint, clear of all five pins, one a legal `H` pose) -- those cells are RETIRED for the whole lane-leaf family; the rest are no-go only at the split depth reached.

## Re-checked against a FRESH collect (end of the attempt)

The population was built from a collector snapshot taken at the start; other campaigns write kills
while A167 runs, so the NEW claim is re-derived at the end (`code/recheck167.py`,
`results/recheck.json`).

FRESH collector: **5,800 records, 5,314 kills, 46 sources, 3,238 distinct dead node ids**.

| | nodes |
|---|---|
| A167 kill nodes | 15 |
| already dead when re-checked (all four killed by **A149** during this attempt) | 4 — `c0_Y0902`, `c0_Y0913`, `c0_Y0921`, `c0_Y0994` |
| **distinct NEW dead nodes** | **11** — 7 trump5 (A60), 4 k5_16 (A57), all level 1 |

NEW: `c0_Y0989, c0_Y0993, c0_Y0995, c0_Y0996, c0_Y0997, c0_Y1002, c0_Y1131,
k5_16_interior_Y0191, k5_16_interior_Y0281, k5_16_interior_Y0635, k5_16_interior_Y0663`

## Which lever did the work (piece accounting over the 15 certificates, 121 pieces)

| piece kind | pieces |
|---|---|
| `m = 1`, `beta = 1`, the BAND cover closed `LANE_band = 0` | 92 |
| `m = 1`, PER-PIECE `beta = 0`, no band cover needed at all | 29 |
| `m = 0` (piece misses the cell) | 0 |

Every kill piece has `m = 1` — the population is precisely the `NO-LINE`/`M = 1` cells where `H`
reaches the cell, so the unconditional form could never fire. The band cover (levers (i) + (iii))
carries 76 % of the pieces and the per-piece guard row (lever (ii)) the other 24 %; `c0_Y1131` is
killed by the per-piece `beta` alone on all nine of its pieces.
