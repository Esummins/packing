# A87 H1 pilot report

Engine: `code/t3lib.py` (A30 verbatim, two data paths repointed) + `code/pilot87.py`.
`code/selftest30.py`: **ALL PASS, 7/7** (incl. 3 corruption gates + adversarial sampling) -- `logs/selftest.log`.  s0 = 969271/250000 = 3.877084; every cell s-box = [sigma_min(cell), s0].

## 1. Per-cell cost (measured, single process, BLAS pinned)

| stage | secs/cell | n | A30 reference |
|---|---|---|---|
| build_cell + clip_s only (verdict a-sigma) | 0.0147 | 1351 | -- |
| test_ab (a)+(b) | 0.1146 | 97 | 0.08 |
| build_menu | 0.6261 | 97 | 0.44 |
| union Farkas LP | 0.0591 | 97 | 0.037 |
| **cheap path total** (a/b/menu/c1-union) | **0.800** | 97 | 0.50 |
| per-selection Farkas (sweep) | 0.00248 | 69000 selections | 0.0019 |
| sweep cell total (cap 3000 selections) | 8.22 | 23 | -- |

Mean per-cell cost over the whole J2 survey (1380 cells, a-sigma-dominated): **0.0575 s**; over sigma-feasible cells only (74): **0.813 s**.

## 2. J1 -- discharge-scale ladder h*(Delta)  (`results/j1_ladder.jsonl`)

| cfg | description | sigma | Delta = sigma - s0 | contacts | h=0.05 | h=0.02 | h=0.01 | h=0.005 | h=0.002 | h=0.001 | h=0.0005 | h=0.0002 | h=0.0001 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| r1 | best k0 optimum | 3.887213268 | +1.0129e-02 | 13 | . | . | . | A-s | A-s | A-s | A-s | A-s | A-s |
| r2 | smallest-side optimum with n_axis_aligned=0 | 3.905653294 | +2.8569e-02 | 8 | . | . | A-s | A-s | A-s | A-s | A-s | A-s | A-s |
| r3 | s closest to 3.95 | 3.955959671 | +7.8876e-02 | 15 | A-s | A-s | A-s | A-s | A-s | A-s | A-s | A-s | A-s |
| r4 | s closest to 4.00 | 4.000000001 | +1.2292e-01 | 7 | A-s | A-s | A-s | A-s | A-s | A-s | A-s | A-s | A-s |
| r5 | s closest to 4.20 | 4.242640688 | +3.6556e-01 | 9 | A-s | A-s | A-s | A-s | A-s | A-s | A-s | A-s | A-s |
| r6 | Trump rotated by phi=0.001 | 3.880958735 | +3.8747e-03 | - | . | . | . | . | A-s | A-s | A-s | A-s | A-s |
| r7 | Trump rotated by phi=5e-08 | 3.877083785 | -2.1512e-07 | - | . | . | . | . | . | . | . | . | . |

Legend: `A-s` = a-sigma (sigma_min(cell) > s0), `A` = interval infeasible, `A-m` = empty selection menu, `B` = D2 slack, `C1u` = union Farkas, `C1s` = complete per-selection sweep 0-alive, `.` = alive.

r7 extension (Delta < 0, the rotational ghost):

| cfg | h=1e-05 | h=1e-06 | h=1e-07 | h=3e-08 | h=1e-08 |
|---|---|---|---|---|---|
| r7 | . | . | . | . | . |

| cfg | Delta | h* (largest h excluded) | by test | h*/Delta | sweep at largest alive h |
|---|---|---|---|---|---|
| r1 | +1.0129e-02 | 0.005 | a-sigma | 0.494 | h=0.05: 3000/2^30 tested, 3000 alive (capped) |
| r2 | +2.8569e-02 | 0.01 | a-sigma | 0.350 | h=0.05: 3000/2^28 tested, 3000 alive (capped) |
| r3 | +7.8876e-02 | 0.05 | a-sigma | 0.634 | -- |
| r4 | +1.2292e-01 | 0.05 | a-sigma | 0.407 | -- |
| r5 | +3.6556e-01 | 0.05 | a-sigma | 0.137 | -- |
| r6 | +3.8747e-03 | 0.002 | a-sigma | 0.516 | h=0.05: 3000/2^34 tested, 3000 alive (capped) |
| r7 | -2.1512e-07 | -- | -- | -- | h=0.05: 3000/2^34 tested, 3000 alive (capped) |

## 3. J2 -- near-feasible survey, 262 optima x 5 h (+14 offset cells) = 1380 cells
(`results/j2_survey.jsonl`, `results/j2_summary.json`)

### 3a. Verdict counts by h

| h | a | a-menu | a-sigma | b | c1-union | alive | total |
|---|---|---|---|---|---|---|---|
| 0.05 | 0 | 0 | 245 | 0 | 0 | 31 | 276 |
| 0.02 | 0 | 0 | 249 | 0 | 0 | 27 | 276 |
| 0.01 | 0 | 0 | 260 | 0 | 0 | 16 | 276 |
| 0.005 | 0 | 0 | 276 | 0 | 0 | 0 | 276 |
| 0.002 | 0 | 0 | 276 | 0 | 0 | 0 | 276 |

### 3b. Verdict counts by Delta-bin

| Delta bin | a | a-menu | a-sigma | b | c1-union | alive | total |
|---|---|---|---|---|---|---|---|
| [0.01,0.02) | 0 | 0 | 52 | 0 | 0 | 40 | 92 |
| [0.02,0.05) | 0 | 0 | 29 | 0 | 0 | 26 | 55 |
| [0.05,0.1) | 0 | 0 | 40 | 0 | 0 | 8 | 48 |
| [0.1,0.3) | 0 | 0 | 1060 | 0 | 0 | 0 | 1060 |
| [0.3,inf) | 0 | 0 | 125 | 0 | 0 | 0 | 125 |

### 3c. Key number -- "excluded with no FJ solve" rate

| quantity | value |
|---|---|
| cells with sigma_min(cell) <= s0 (NOT killed by a-sigma) | 74 / 1380 |
| of those, killed by (b) or (c1-union) | **0  (0.0%)** |
| of those, killed by (a) or (a-menu) | 0 |
| of those, alive after the whole cheap path | **74 (100%)** |

| h | sigma-feasible cells | killed by (b)/(c1-union) | rate |
|---|---|---|---|
| 0.05 | 31 | 0 | 0.0% |
| 0.02 | 27 | 0 | 0.0% |
| 0.01 | 16 | 0 | 0.0% |
| 0.005 | 0 | 0 | -- |
| 0.002 | 0 | 0 | -- |

### 3d. h* vs Delta (largest h at which the centred cell is excluded)

| Delta bin | n | h* median | h*/Delta median | h*/Delta min | h*/Delta max | reason |
|---|---|---|---|---|---|---|
| [0.01,0.02) | 12 | 0.005 | 0.478 | 0.431 | 0.494 | a-sigma |
| [0.02,0.05) | 5 | 0.01 | 0.420 | 0.350 | 0.496 | a-sigma |
| [0.05,0.1) | 8 | 0.05 | 0.557 | 0.502 | 0.634 | a-sigma |
| [0.1,0.3) | 212 | 0.05 | 0.407 | 0.272 | 0.473 | a-sigma |
| [0.3,1e+09) | 25 | 0.05 | 0.137 | 0.044 | 0.137 | a-sigma |

All 262: h*/Delta median 0.407, min 0.044, max 0.634; reason mix {'a-sigma': 262}.  245 of 262 are CENSORED at the ladder top (h* = 0.05 = largest h tested).
Uncensored subset (h* < 0.05, n = 17): h*/Delta median 0.465, min 0.350, max 0.496.

Offset cells (14 optima with s < 3.9, +-h/2 per coordinate, rng 87, n = 70): {'alive': 30, 'a-sigma': 40}.

## 4. J3 -- FJ degeneracy at the under-contacted k0 optima (`results/j3_degeneracy.json`)

| id | sigma | Delta | pair/wall contacts (cp85) | m active rows | grad rank | rank on 33 cfg coords | flat dim | rattlers | FJ multipliers feasible | lam0=0 branch | Krawczyk compl (h=1e-4, lam-rad 1e-3) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| o000 | 3.8872133 | 1.0129e-02 | 8/5 | 21 | 19 | 19 | 14 | 2 | False | False | FJ infeasible |
| o001 | 3.8872587 | 1.0175e-02 | 7/5 | 20 | 18 | 18 | 15 | 3 | False | False | FJ infeasible |
| o002 | 3.8872878 | 1.0204e-02 | 6/5 | 19 | 17 | 17 | 16 | 4 | False | False | FJ infeasible |
| o003 | 3.8874037 | 1.0320e-02 | 7/6 | 22 | 19 | 19 | 14 | 3 | False | False | FJ infeasible |
| o004 | 3.8874647 | 1.0381e-02 | 6/5 | 19 | 17 | 17 | 16 | 4 | False | False | FJ infeasible |
| o005 | 3.8875528 | 1.0469e-02 | 6/5 | 19 | 17 | 17 | 16 | 4 | False | False | FJ infeasible |
| o006 | 3.8878121 | 1.0728e-02 | 6/5 | 19 | 17 | 17 | 16 | 4 | False | False | FJ infeasible |
| o007 | 3.8878253 | 1.0741e-02 | 6/5 | 19 | 17 | 17 | 16 | 4 | False | False | FJ infeasible |
| o008 | 3.8878912 | 1.0807e-02 | 6/5 | 19 | 17 | 17 | 16 | 4 | False | False | FJ infeasible |
| o009 | 3.8880201 | 1.0936e-02 | 6/5 | 19 | 17 | 17 | 16 | 4 | False | False | FJ infeasible |
| o010 | 3.8882801 | 1.1196e-02 | 9/7 | 24 | 22 | 22 | 11 | 1 | False | False | FJ infeasible |
| o011 | 3.8886982 | 1.1614e-02 | 6/5 | 19 | 17 | 17 | 16 | 4 | False | False | FJ infeasible |
| o012 | 3.8972308 | 2.0147e-02 | 9/7 | 27 | 22 | 21 | 12 | 3 | True | True | a-sigma at h=1e-4 |
| o013 | 3.8988968 | 2.1813e-02 | 7/6 | 21 | 19 | 19 | 14 | 3 | False | False | FJ infeasible |
| r6 | 3.8809587 | 3.8747e-03 | -/- | 25 | 23 | 23 | 10 | 0 | False | False | FJ infeasible |

| id | h=1e-3 cell verdict | sweep class at h=1e-3 | smallest non-a-sigma h | verdict there | menu log2 | sweep (cap 3000) |
|---|---|---|---|---|---|---|
| o000 | a-sigma | n/a (a-sigma) | 0.01 | alive | 17.0 | 3000 tested / 2^17, 3000 alive (capped) |
| o001 | a-sigma | n/a (a-sigma) | 0.01 | alive | 16.0 | 3000 tested / 2^16, 3000 alive (capped) |
| o002 | a-sigma | n/a (a-sigma) | 0.01 | alive | 17.0 | 3000 tested / 2^17, 3000 alive (capped) |
| o003 | a-sigma | n/a (a-sigma) | 0.01 | alive | 16.0 | 3000 tested / 2^16, 3000 alive (capped) |
| o004 | a-sigma | n/a (a-sigma) | 0.01 | alive | 16.0 | 3000 tested / 2^16, 3000 alive (capped) |
| o005 | a-sigma | n/a (a-sigma) | 0.01 | alive | 17.0 | 3000 tested / 2^17, 3000 alive (capped) |
| o006 | a-sigma | n/a (a-sigma) | 0.01 | alive | 17.0 | 3000 tested / 2^17, 3000 alive (capped) |
| o007 | a-sigma | n/a (a-sigma) | 0.01 | alive | 16.0 | 3000 tested / 2^16, 3000 alive (capped) |
| o008 | a-sigma | n/a (a-sigma) | 0.01 | alive | 16.0 | 3000 tested / 2^16, 3000 alive (capped) |
| o009 | a-sigma | n/a (a-sigma) | 0.01 | alive | 17.0 | 3000 tested / 2^17, 3000 alive (capped) |
| o010 | a-sigma | n/a (a-sigma) | 0.01 | alive | 16.0 | 3000 tested / 2^16, 3000 alive (capped) |
| o011 | a-sigma | n/a (a-sigma) | 0.01 | alive | 17.0 | 3000 tested / 2^17, 3000 alive (capped) |
| o012 | a-sigma | n/a (a-sigma) | 0.02 | alive | 21.0 | 3000 tested / 2^21, 3000 alive (capped) |
| o013 | a-sigma | n/a (a-sigma) | 0.02 | alive | 27.0 | 3000 tested / 2^27, 3000 alive (capped) |
| r6 | a-sigma | n/a (a-sigma) | 0.005 | alive | 23.0 | 3000 tested / 2^23, 3000 alive (capped) |

## 5. J4 -- projections (computed from the measured costs; `results/j4_projection.json`)

Inputs: h*_median (J2) = 0.05 (censored: 245/262 optima sit at the ladder top); cheap-path cost = 0.813 s/cell on sigma-feasible cells, 0.0575 s/cell averaged over the survey; sweep cell = 8.22 s (cap 3000, 0.00248 s/selection); symmetry divisor 8*11! = 319334400.

### (i) uniform 33-dim cover of D0, centres in [0,s0]^2, theta in [0,pi/2), / 8*11!

| h | cells | A30 reference |
|---|---|---|
| 0.05 | 1e39.6 | -- |
| 0.01 | 1e62.7 | 1e63 |
| 0.001 | 1e95.7 | -- |

A30 (same model): h=0.1 -> 1e30, h=0.01 -> 1e63, h=5e-4 -> 1e106, h=1.75e-4 -> 1e121.

### (ii)/(iii) cells to cover one box, and CPU-h

| target | radius | h | cells | CPU-h cheap path | CPU-h with sweep | cell discharged by T3? |
|---|---|---|---|---|---|---|
| A85 landing box | 0.0016 | 0.05 | 1e0.0 | 1e-3.6 | 1e-2.6 | NO |
| A85 landing box | 0.0016 | 0.001 | 1e6.7 | 1e3.1 | 1e4.1 | NO |
| A85 landing box | 0.0016 | 0.000175 | 1e31.7 | 1e28.1 | 1e29.1 | NO |
| A85 landing box | 0.0016 | 0.0001 | 1e39.7 | 1e36.1 | 1e37.1 | NO |
| ghost drain box | 0.005 | 0.05 | 1e0.0 | 1e-3.6 | 1e-2.6 | NO |
| ghost drain box | 0.005 | 0.001 | 1e23.1 | 1e19.4 | 1e20.4 | NO |
| ghost drain box | 0.005 | 0.000175 | 1e48.0 | 1e44.4 | 1e45.4 | NO |
| ghost drain box | 0.005 | 0.0001 | 1e56.1 | 1e52.4 | 1e53.4 | NO |

At h = h*_median = 0.05 one cell covers either box, but that cell is NOT discharged by any T3 test (J1/J2: no sigma-feasible cell was ever killed), so the CPU-h entries at h=0.05 are the cost of a test that returns "alive".

### (v) cost ratio to A85

| quantity | value |
|---|---|
| A87 cheap-path cell (sigma-feasible) | 0.813 s |
| A85 measured LP node | 1700 s |
| ratio A87 cell / A85 LP node | **4.78e-04** (1 LP node = 2092 cheap cells) |
| A30 floor, cheap path only | 1.1e5 CPU-h |
| A30 floor, per-selection sweep | 4.9e7 CPU-h |

## 6. Findings (measured)

1. Every excluded cell in the pilot was excluded by **a-sigma** (sigma_min(cell) > s0): 1351 of 1448 cells; (b) D2-slack fired 0 times, (c1) union-Farkas 0 times, (a)/(a-menu) 0 times.  Of the 74 J2 cells with sigma_min <= s0, **0 (0.0%) were killed by (b) or (c1-union)** -- the "excluded with no FJ solve" rate is 0, not high.
2. h* is linear in Delta and is a pure s-clip effect: h*/Delta = 0.465 median (0.350-0.496) on the 17 optima whose h* is uncensored, i.e. h* ~ Delta/2.15; 245/262 optima are censored at the ladder top h = 0.05.  For Delta <= 0 (r7, the rotational ghost at sigma = s0 - 2.2e-7) NO h down to 1e-8 excludes the cell.
3. The per-selection Farkas sweep killed nothing: 114000 selections over 38 cells, 3000-alive-of-3000 in every case, with menu sizes 2^16 - 2^34, so no sweep can complete (cap 3000).
4. FJ degeneracy at the under-contacted optima: 14 of 15 points admit **no feasible FJ multiplier** at tol 1e-6 (grad s is outside the cone of the 19-27 active rows); rank on the 33 configuration coordinates is 17-23, so the flat dimension is 10-16, with 0-4 rattler squares.  Only o012 has FJ multipliers, and it also admits the lambda_0 = 0 branch.  Every h=1e-3 cell around these points is already a-sigma, so no Krawczyk/sweep verdict is reachable there.
5. Cost: 0.813 s per sigma-feasible cell (A30: 0.50 s), 0.0147 s for an a-sigma cell, 0.0025 s per swept selection; the cheap-path cell is 4.8e-4 of an A85 LP node (1 LP node = 2092 cells).  The uniform cover reproduces A30: 1e62.7 vs 1e63 at h = 0.01.

