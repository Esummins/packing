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

