# A141 T2 — the K′ lane test on every open k0 cell

173 distinct open k0 cells (A140's twelve + A115's open pool), four corners each. `ub` = certified LANE_K′ upper bound, `M` = conditioned squares that can meet the widened corner box, `A118` = the stored axis-core verdict.

## The twelve converged-alive cells

| cell | boxes | BL | BR | TR | TL | pair | verdict |
|---|---|---|---|---|---|---|---|
| `l1_071` | 1 | open L≤- M=0+ | open L≤- M=0+ | open L≤- M=0+ | open L≤- M=0+ | - | alive |
| `l1_104` | 1 | open L≤- M=0+ | open L≤- M=0+ | open L≤- M=0+ | open L≤- M=0+ | - | alive |
| `l1_124` | 1 | open L≤- M=0+ | open L≤- M=0+ | near L≤1 M=1+ | open L≤- M=0+ | - | alive |
| `l1_148` | 1 | open L≤- M=0+ | open L≤- M=0+ | und. L≤- M=1 | open L≤- M=0+ | - | alive |
| `l1_153` | 1 | open L≤- M=0+ | open L≤- M=0+ | near L≤1 M=1+ | open L≤- M=0+ | - | alive |
| `l1_158` | 1 | open L≤- M=0+ | open L≤- M=0+ | near L≤1 M=1 | open L≤- M=0+ | - | alive |
| `l1_159` | 1 | open L≤- M=0+ | open L≤- M=0+ | near L≤1 M=1 | open L≤- M=0+ | - | alive |
| `l2_p114_001` | 1 | open L≤- M=0+ | open L≤- M=0+ | near L≤1 M=1+ | open L≤- M=0+ | - | alive |
| `l2_p65_101` | 1 | open L≤- M=0+ | open L≤- M=0+ | open L≤- M=0+ | open L≤- M=0+ | - | alive |
| `l2_p65_111` | 1 | open L≤- M=0+ | open L≤- M=0+ | open L≤- M=0+ | open L≤- M=0+ | - | alive |
| `l2_p74_001` | 1 | open L≤- M=0+ | open L≤- M=0+ | open L≤- M=0+ | open L≤- M=0+ | - | alive |
| `s3_far_BL389484_TR018470` | 4 | **KILL** L≤1 M=0 | und. L≤- M=0 | near L≤0 M=2+ | open L≤- M=0+ | 0~1,1~0 | DEAD (pair) |

## Kills in the wider open pool

| cell | corner | LANE_K′ | M | meeter | A118 said |
|---|---|---|---|---|---|
| `l1_203_plain_warm` | TR | 0 | 1 | [0] | LANE<=1 (M=1) |
| `l1_203_sh3_warm` | TR | 0 | 1 | [0] | LANE<=1 (M=1) |
| `l1_214_plain_warm` | TR | 0 | 1 | [0] | LANE<=1 (M=1) |
| `l1_214_sh1_warm` | TR | 0 | 1 | [0] | LANE<=1 (M=1) |
| `l1_214_sh2adj_warm` | TR | 0 | 1 | [0] | LANE<=1 (M=1) |
| `l1_214_sh2dia_warm` | TR | 0 | 1 | [0] | LANE<=1 (M=1) |
| `l1_214_sh3_warm` | TR | 0 | 1 | [0] | LANE<=1 (M=1) |
| `l2_p114_010` | TR | 0 | 1 | [0] | UNDECIDED (M=1) |
| `l2_p210_000` | TR | 0 | 1 | [0] | LANE<=0 (M=1) |
| `l2_p210_001` | TR | 0 | 1 | [0] | LANE<=0 (M=1) |
| `l2_p210_010` | TR | 0 | 1 | [0] | LANE<=0 (M=1) |
| `l2_p210_011` | TR | 0 | 1 | [0] | LANE<=0 (M=1) |
| `l2_p215_000` | TR | 0 | 1 | [0] | LANE<=0 (M=1) |
| `l2_p215_001` | TR | 0 | 1 | [0] | LANE<=0 (M=1) |
| `l2_p215_010` | TR | 0 | 1 | [0] | LANE<=0 (M=1) |
| `l2_p215_011` | TR | 0 | 1 | [0] | LANE<=0 (M=1) |
| `l3_pp215_000_000` | TR | 0 | 1 | [0] | LANE<=0 (M=1) |
| `l3_pp215_000_001` | TR | 0 | 1 | [0] | LANE<=0 (M=1) |
| `l3_pp215_000_011` | TR | 0 | 1 | [0] | LANE<=0 (M=1) |
| `node_156` | TR | 0 | 1 | [0] | — |
| `node_157` | TR | 0 | 1 | [0] | — |
| `node_162` | TR | 0 | 1 | [0] | — |
| `node_163` | TR | 0 | 1 | [0] | — |
| `node_164` | TR | 0 | 1 | [0] | — |
| `node_165` | TR | 0 | 1 | [0] | — |
| `node_166` | TR | 0 | 1 | [0] | — |
| `node_167` | TR | 0 | 1 | [0] | — |
| `node_198` | TR | 0 | 1 | [0] | — |
| `node_199` | TR | 0 | 1 | [0] | — |
| `node_200` | TR | 0 | 1 | [0] | — |
| `node_201` | TR | 0 | 1 | [0] | — |
| `node_202` | TR | 0 | 1 | [0] | — |
| `node_203` | TR | 0 | 1 | [0] | — |
| `node_204` | TR | 0 | 1 | [0] | — |
| `node_205` | TR | 0 | 1 | [0] | — |
| `node_206` | TR | 0 | 1 | [0] | — |
| `node_207` | TR | 0 | 1 | [0] | — |
| `node_208` | TR | 0 | 1 | [0] | — |
| `node_209` | TR | 0 | 1 | [0] | — |
| `node_210` | TR | 0 | 1 | [0] | — |
| `node_211` | TR | 0 | 1 | [0] | — |
| `node_212` | TR | 0 | 1 | [0] | — |
| `node_213` | TR | 0 | 1 | [0] | — |
| `node_214` | TR | 0 | 1 | [0] | — |
| `node_215` | TR | 0 | 1 | [0] | — |
| `s3_far_BL389484_TR018470` | BL | 1 | 0 | [] | LANE<=1 (M=2) |

## Near-misses (LANE_K′ + M = 2): which two squares

| cell | corner | LANE_K′ | M | the two |
|---|---|---|---|---|
| `l1_115_plain_warm` | TR | None | 1 | conditioned [0] |
| `l1_115_sh3_warm` | TR | None | 1 | conditioned [0] |
| `l1_124` | TR | 1 | 1 | one free square + conditioned [0] |
| `l1_153` | TR | 1 | 1 | one free square + conditioned [0] |
| `l1_158` | TR | 1 | 1 | one free square + conditioned [0] |
| `l1_159` | TR | 1 | 1 | one free square + conditioned [0] |
| `l1_159_plain_warm` | TR | 1 | 1 | one free square + conditioned [0] |
| `l1_159_sh3_warm` | TR | 1 | 1 | one free square + conditioned [0] |
| `l1_192_plain_warm` | TR | None | 1 | conditioned [0] |
| `l1_192_sh3_warm` | TR | None | 1 | conditioned [0] |
| `l2_p114_000` | TR | None | 1 | conditioned [0] |
| `l2_p114_001` | TR | 1 | 1 | one free square + conditioned [0] |
| `l2_p114_011` | TR | 1 | 1 | one free square + conditioned [0] |
| `l3_pp114_001_000` | TR | 1 | 1 | one free square + conditioned [0] |
| `l3_pp114_001_011` | TR | 1 | 1 | one free square + conditioned [0] |
| `node_116` | TR | None | 1 | conditioned [0] |
| `node_117` | TR | None | 1 | conditioned [0] |
| `node_118` | TR | None | 1 | conditioned [0] |
| `node_119` | TR | None | 1 | conditioned [0] |
| `node_120` | TR | 1 | 1 | one free square + conditioned [0] |
| `node_121` | TR | 1 | 1 | one free square + conditioned [0] |
| `node_122` | TR | 1 | 1 | one free square + conditioned [0] |
| `node_123` | TR | 1 | 1 | one free square + conditioned [0] |
| `node_124` | TR | 1 | 1 | one free square + conditioned [0] |
| `node_125` | TR | 1 | 1 | one free square + conditioned [0] |
| `node_150` | TR | None | 1 | conditioned [0] |
| `node_151` | TR | 1 | 1 | one free square + conditioned [0] |
| `node_152` | TR | 1 | 1 | one free square + conditioned [0] |
| `node_153` | TR | 1 | 1 | one free square + conditioned [0] |
| `node_154` | TR | None | 1 | conditioned [0] |
| `node_155` | TR | None | 1 | conditioned [0] |
| `node_158` | TR | 1 | 1 | one free square + conditioned [0] |
| `node_159` | TR | 1 | 1 | one free square + conditioned [0] |
| `node_160` | TR | 1 | 1 | one free square + conditioned [0] |
| `node_161` | TR | 1 | 1 | one free square + conditioned [0] |
| `node_187` | TR | None | 1 | conditioned [0] |
| `node_192` | TR | None | 1 | conditioned [0] |
| `node_193` | TR | 1 | 1 | one free square + conditioned [0] |
| `node_194` | TR | None | 1 | conditioned [0] |
| `node_195` | TR | None | 1 | conditioned [0] |
| `node_196` | TR | 1 | 1 | one free square + conditioned [0] |
| `node_197` | TR | None | 1 | conditioned [0] |
| `s2_near_046_619` | BL | 1 | 2 | one free square + conditioned [0, 1] |
| `s3_far_BL389484_TR018470` | TR | 0 | 2 | conditioned [2, 3] |
