# A150 — tables

## 1. The band (per corner)

| step | cells in | killed | cells out |
|---|---|---|---|
| A143 level-1 cells (6 x 6 positions x 6 tilt windows of 15 deg) | 216 | 0 | 216 |
| (B1) no partner cell survives A143's pair geometry | 216 | 10 | 206 |
| (B2) disk bound n_max >= 10 with the one core removed | 206 | 0 | 206 |

band = **206** cells; centre distance from the corner spans [0.7071, 2.4503] (width 1.7432), tilt spans [0, 90) deg (the full range); 35 of 36 position cells present; disk bound over all 216 cells n_max in [15, 18] against budget 10.

cover confirmation: **20000 drawn / 20000 hits / 0 misses** (realised interior-disjoint BL 2-crowds, both members located); 400 exact-rational cross-checks of the meet test, 0 disagreements.

## 2. The product cover, stage by stage

| stage | surviving 4-tuples | D4 orbits | cut so far |
|---|---|---|---|
| 0 raw band product | 1800814096 | 225117727 | 0.00 % |
| 1 +Q2 adjacent centre distance | 1692641440 | 211592473 | 6.01 % |
| 2 +Q1 adjacent K'-vs-K' | 1561731694 | 195228403 | 13.28 % |
| 3 +Q1s adjacent per-sub-bin | 1519799378 | 189986576 | 15.60 % |
| 4 +Q2/Q1/Q1s on the two diagonals | 1519380658 | 189934236 | 15.63 % |

per adjacent corner pair, of 206^2 = 42 436: (Q2) 648, (Q1) 816, (Q1s) 266 -> 1730 killed (4.08 %); per diagonal pair: (Q2) 0, (Q1) 6, (Q1s) 2 -> 8 (0.019 %).  Vertical-mirror consistency of the adjacency matrix: True.

## 3. The kills that fire on nothing

| leaf | measured on | result | kills |
|---|---|---|---|
| (QG) A144 guard lines, 776 axis lines at pitch 0.01 | 3000 sampled survivors | rhs_min 1.3773, median 1.7224 (needs < 0) | 0 |
| (QD) A148 disk bound, all four cores, budget 7 | 40 random survivors | n_max in [10, 14], median 12 | 0 |
| (QS) separation bound, side 0.70 partition | the same 40 survivors | n_max in [9, 16], median 13 — WORSE than the disk bound | 0 |

**Trump canary**: 192 4-tuples over the eight D4 images, 192 in band, **192 survive every geometric kill** — verdict CANARY-PASS.

## 4. The LP with four conditioned squares (budget 7 = 11 - 4)

A143's ONE-corner numbers at the same 240 s cap, for comparison: budget 10, eta = -0.0442 / -0.6328 / -0.0000, **0 converged kills**; budget 9 with TWO squares at the SAME corner, eta = -0.0826 / -0.0769, **0 converged kills**.

### 4a. the FINE band cover (206 cells/corner, a ~ 0.31-0.36)

| node | kind | cells (BL,BR,TR,TL) | a_exact | tau | eta | conv | kill | cert | rows | wall s |
|---|---|---|---|---|---|---|---|---|---|---|
| `q_110_x4` | A143-repeat | 11 t0 11 t0 11 t0 11 t0 | 0.334 | 6.0000 | -1.0000 | False | False | - | 10175 | 271.0 |
| `q_321_x4` | A143-repeat | 32 t1 32 t1 32 t1 32 t1 | 0.321 | 1.0000 | -6.0000 | True | True | PASS | 420 | 9.4 |
| `q_402_x4` | A143-repeat | 40 t2 40 t2 40 t2 40 t2 | 0.361 | 5.0000 | -2.0000 | True | True | FAIL | 3537 | 92.4 |
| `q_000_x4` | band-extreme | 00 t0 00 t0 00 t0 00 t0 | 0.334 | 7.8763 | +0.8763 | False | False | - | 9263 | 253.6 |
| `q_rand_020_143_043_144` | random-survivor | 02 t0 14 t3 04 t3 14 t4 | 0.315 | 6.4643 | -0.5357 | False | False | - | 10379 | 258.0 |
| `q_rand_103_443_145_152` | random-survivor | 10 t3 44 t3 14 t5 15 t2 | 0.315 | 7.0000 | +0.0000 | True | False | - | 3085 | 65.5 |
| `q_rand_301_000_321_533` | random-survivor | 30 t1 00 t0 32 t1 53 t3 | 0.315 | 6.0000 | -1.0000 | True | True | FAIL | 1785 | 71.4 |
| `q_rand_311_530_133_430` | random-survivor | 31 t1 53 t0 13 t3 43 t0 | 0.315 | 6.0000 | -1.0000 | True | True | PASS | 273 | 26.9 |
| `q_rand_423_411_123_424` | random-survivor | 42 t3 41 t1 12 t3 42 t4 | 0.315 | 6.0000 | -1.0000 | True | True | PASS | 1158 | 43.3 |
| `r_000_550_140_400` | random-survivor-r3 | 00 t0 55 t0 14 t0 40 t0 | 0.334 | 7.6000 | +0.6000 | True | False | - | 3788 | 207.9 |
| `r_055_035_044_453` | random-survivor-r3 | 05 t5 03 t5 04 t4 45 t3 | 0.315 | 6.0000 | -1.0000 | True | True | FAIL | 1349 | 13.2 |
| `r_232_145_253_415` | random-survivor-r3 | 23 t2 14 t5 25 t3 41 t5 | 0.315 | 5.0000 | -2.0000 | True | True | PASS | 389 | 8.7 |
| `q_trump_g0` | trump-canary | 00 t0 00 t0 00 t0 40 t0 | 0.334 | 8.0787 | +1.0787 | False | False | - | 7927 | 257.9 |

13 nodes: **7 converged kills** (4 certified PASS through the frozen verifier), 2 unconverged kill candidates (tau < 7), 4 alive.

### 4b. the COARSE covers (the pricing question)

| node | kind | cells (BL,BR,TR,TL) | a_exact | tau | eta | conv | kill | cert | rows | wall s |
|---|---|---|---|---|---|---|---|---|---|---|
| `cnp3_nt3_000_000_000_000` | coarse-np3_nt3 | 00 t0 00 t0 00 t0 00 t0 | 0.180 | 8.8840 | +1.8840 | False | False | - | 9382 | 269.6 |
| `cnp3_nt3_001_001_001_001` | coarse-np3_nt3 | 00 t1 00 t1 00 t1 00 t1 | 0.279 | 6.4398 | -0.5602 | False | False | - | 9691 | 267.9 |
| `cnp3_nt3_002_002_002_002` | coarse-np3_nt3 | 00 t2 00 t2 00 t2 00 t2 | 0.176 | 8.9604 | +1.9604 | False | False | - | 8890 | 251.4 |
| `cnp3_nt3_010_010_010_010` | coarse-np3_nt3 | 01 t0 01 t0 01 t0 01 t0 | 0.180 | 7.2113 | +0.2113 | False | False | - | 8900 | 261.9 |
| `cnp3_nt3_012_220_110_122` | coarse-np3_nt3 | 01 t2 22 t0 11 t0 12 t2 | 0.176 | 7.0000 | -0.0000 | True | False | - | 6144 | 249.2 |

5 nodes: **0 converged kills** (0 certified PASS through the frozen verifier), 1 unconverged kill candidates (tau < 7), 4 alive.

### 4c. re-certification of the two FAILed kills at scale cap 1.30 (A143 used 1.03)

| node | tau | eta | conv | cert | wall s |
|---|---|---|---|---|---|
| `q_402_x4_recert` | 5.0000 | -2.0000 | True | FAIL | 116.2 |
| `q_rand_301_000_321_533_recert` | 6.0000 | -1.0000 | True | FAIL | 90.9 |

Same tau, same FAIL: the certificate failure is NOT a margin problem.  Both stay **LP-dead, certificate pending** (they need the A13/A14 separation loop with more rounds than A150's cert budget allowed).

total LP + certification CPU: **3307 s = 0.92 CPU-h** over 20 node solves.

## 5. The coarseness ladder

`area_open` is A148's certified-non-blocked feasible-centre area with all four cores removed (6 random states per row, `results/ladder150.json`); on the fine cover the LP decides below `area_open ~ 2` and is alive above ~ 3.3, so it is a 1-second proxy for the 240 s LP.

| cover (positions x tilt windows) | cells/corner | core a (median) | D4 orbits | area_open min/med/max | cost at 100 s/node |
|---|---|---|---|---|---|
| 2 x 2 x 2 of 45.0 deg | 8 | 0.0482 | 538 | 5.09 / 5.42 / 5.60 | 14 CPU-h |
| 2 x 2 x 3 of 30.0 deg | 12 | 0.0617 | 2661 | 4.46 / 4.73 / 4.88 | 73 CPU-h |
| 3 x 3 x 3 of 30.0 deg | 27 | 0.1771 | 66771 | 2.90 / 3.08 / 4.35 | 1,854 CPU-h |
| 3 x 3 x 4 of 22.5 deg | 36 | 0.1788 | 210447 | 2.62 / 3.19 / 3.80 | 5,845 CPU-h |
| 4 x 4 x 4 of 22.5 deg | 64 | 0.2461 | 2067939 | 1.49 / 2.42 / 3.96 | 57,442 CPU-h |
| 6 x 6 x 3 of 30.0 deg | 108 | 0.2913 | 15266858 | 1.55 / 1.86 / 2.68 | 424,079 CPU-h |
| 6 x 6 x 6 of 15.0 deg | 206 | 0.3192 | 189934236 | 1.34 / 2.00 / 2.57 | 5,275,951 CPU-h |
