# A143 tables

### T2 — single-intruder root, budget 10, cap 240 s, exact cores

| node | kind | cell(s) | tau | eta | conv | minmass | maxcov | kill | certified | K' extra cols | wall s |
|---|---|---|---|---|---|---|---|---|---|---|---|
| s_c1_11_t0 | sample | c1_11_t0 | 9.95580 | -0.0442 | False | 0.6303 | 1.4993 | False | — | 262 of 6000 | 276.5 |
| s_c1_32_t1 | sample | c1_32_t1 | 9.36721 | -0.6328 | False | 0.4721 | 1.3231 | False | — | 527 of 6000 | 282.7 |
| s_c1_40_t2 | sample | c1_40_t2 | 10.00000 | -0.0000 | False | 0.7260 | 1.3507 | False | — | 273 of 6000 | 273.6 |

n = 3, eta in [-0.6328, -0.0000], median -0.0442; converged kills 0; certified 0.

### T2b — doubly-met pair root, budget 9, cap 240 s, exact cores

| node | kind | cell(s) | tau | eta | conv | minmass | maxcov | kill | certified | K' extra cols | wall s |
|---|---|---|---|---|---|---|---|---|---|---|---|
| p_001__510 | sample | ((0, 0, 1), (5, 1, 0)) | 8.91736 | -0.0826 | False | 0.7610 | 1.2920 | False | — | 723 of 6000 | 254.6 |
| p_014__552 | sample | ((0, 1, 4), (5, 5, 2)) | 8.92308 | -0.0769 | False | 0.5405 | 1.4595 | False | — | 833 of 6000 | 270.3 |

n = 2, eta in [-0.0826, -0.0769], median -0.0769; converged kills 0; certified 0.

### T1 — geometry on the single-intruder cover (216 cells)

| verdict | cells |
|---|---|
| ALIVE-GEOM | 216 |

| corner | LANE>=2 | LANE<=1 | LANE<=0 | UNDECIDED |
|---|---|---|---|---|
| BL(0,0) | 39 | 20 | 0 | 157 |
| BR(0,0) | 214 | 0 | 0 | 2 |
| TR(0,0) | 216 | 0 | 0 | 0 |
| TL(0,0) | 212 | 0 | 0 | 4 |

### T1b — geometry on the pair cover

unordered pairs 23436, D4_BL-canonical 11772; P2 7919, P1 1313, P1s 406, alive 2134 (81.9 % killed by geometry)

lane test on 1322 of 2134 survivors: 0 kills

| corner | LANE>=2 | LANE<=1 | LANE<=0 | UNDECIDED |
|---|---|---|---|---|
| BL(0,0) | 20 | 991 | 98 | 213 |
| BR(0,0) | 1279 | 0 | 0 | 43 |
| TR(0,0) | 1322 | 0 | 0 | 0 |
| TL(0,0) | 1309 | 0 | 0 | 13 |

### T2 — intersection with the twelve converged-alive interior cells

| interior cell | support | BL meeters (unwidened) | corner-first cells | support pairs alive / dead | Rule III fires |
|---|---|---|---|---|---|
| l1_071 | 68 | 12 (7) | 8 | 33 / 33 | no |
| l1_104 | 17 | 4 (4) | 4 | 4 / 2 | no |
| l1_124 | 17 | 4 (3) | 4 | 3 / 3 | no |
| l1_148 | 10 | 3 (1) | 3 | 3 / 0 | no |
| l1_153 | 10 | 2 (2) | 2 | 1 / 0 | no |
| l1_158 | 16 | 3 (2) | 3 | 2 / 1 | no |
| l1_159 | 15 | 4 (4) | 4 | 4 / 2 | no |
| l2_p114_001 | 10 | 2 (2) | 2 | 1 / 0 | no |
| l2_p65_101 | 83 | 20 (5) | 7 | 36 / 154 | no |
| l2_p65_111 | 60 | 15 (6) | 6 | 44 / 61 | no |
| l2_p74_001 | 10 | 1 (1) | 1 | 0 / 0 | YES |
| s3_far_BL389484_TR018470 | 14 | 2 (1) | 1 | 0 / 1 | YES |

### T1 — sampled cover confirmation

single: 40000 drawn, 22078 admissible BL-meeting poses, 0 misses, 113 distinct cells hit
pair: 13320000 drawn, 12000 realised interior-disjoint BL 2-crowds, 0 violations, 422 distinct pair cells hit

### the Trump lineage, descended (geometry only)

image g2, BL meeters [[0.5000000528718522, 1.3445254178482875, 0.0], [1.5362873427647126, 0.7046082443696386, 49.81806270967018]], cells [[0, 4, 0], [5, 0, 3]]

| depth | P1 | P2 | BL | BR | TR | TL | any kill |
|---|---|---|---|---|---|---|---|
| 0 | False | False | UNDECIDED M=2 | LANE>=2 M=0 | LANE>=2 M=0 | LANE>=2 M=0 | False |
| 1 | False | False | LANE<=1 M=2 | UNDECIDED M=0 | LANE>=2 M=0 | LANE>=2 M=0 | False |
| 2 | False | False | LANE<=1 M=2 | LANE>=2 M=0 | LANE>=2 M=0 | LANE>=2 M=0 | False |
| 3 | False | False | LANE<=0 M=2 | LANE>=2 M=0 | LANE>=2 M=0 | LANE>=2 M=0 | False |

### T1 — the K′ lane leaf with A141's POLYGON cores (`polylane.lane_corner`, read-only)

27 of the 216 single cells (the `ix = 0` prefix — the run was stopped at the CPU cap), all four
corners, exact rational shared-point discharge: **0 kills**.  BL: 7 `LANE ≥ 2`, 16
`NEAR-MISS-OR-WORSE` (a second BL meeter is realised by an explicit sampled witness, so
`LANE_K′(BL) ≥ 1` and with `M = 1` the K0-FREE threshold `LANE + M ≤ 1` is missed), 4 UNDECIDED.
BR / TR / TL: 27 / 27 / 27 `LANE ≥ 2`.  Upgrading A118's axis cores to A132's polygon cores — the
upgrade that killed 26 level-1 cells of the INTERIOR tree (A141) — kills nothing here, because on
the corner-first root the conditioned square is itself a BL meeter and the leaf needs the corner to
be met by ≤ 1 square in total.
