# A113 T3 -- where the k0_00 projection sits relative to the k >= 1 manifold

Model: A85 s.8.3 / A99 projection99 (f2 = 2/3, c = 0.47-1.1 CPU-h/node, window x1.05, +150 CPU-h for (D)/(D')).  Weighted node total = 18624 (A99's 18,624).

| level | boxes | model weight | share |
|---|---|---|---|
| 2 | 1728 | 1728 | 9.3% |
| 3 | 13824 | 4608 | 24.7% |
| 4 | 110592 | 12288 | 66.0% |

## the split (combined eta = max(position, tilt-as-displacement) -- the brief's measure)

| eta | weight within | share of frontier cost | CPU-h within | CPU-h beyond |
|---|---|---|---|---|
| 0.05 | 257 | **1.38%** | 127-296 | 9214-21364 |
| 0.10 | 851 | **4.57%** | 420-983 | 8921-20678 |
| 0.20 | 3271 | **17.57%** | 1614-3778 | 7727-17882 |

## the same split on POSITION distance alone (d_pos; the tilt term dropped)

| d_pos | weight within | share of frontier cost |
|---|---|---|
| 0.05 | 1804 | 9.69% |
| 0.10 | 3663 | 19.67% |
| 0.20 | 8209 | 44.08% |

## by level (combined eta)

| eta | level 2 | level 3 | level 4 |
|---|---|---|---|
| 0.05 | 1.97% | 1.97% | 1.07% |
| 0.10 | 7.18% | 5.38% | 3.90% |
| 0.20 | 24.65% | 18.74% | 16.13% |

## measured-cost variant (each level-1 subtree weighted by its measured level-1 LP wall;
the 82 notrun cells carry the median 498 s)

| eta | share of measured-cost-weighted frontier |
|---|---|
| 0.05 | 1.54% |
| 0.10 | 5.14% |
| 0.20 | 18.89% |

## by PARENT level-1 cell (what a guided tree would actually branch on: the cost that
descends from the 216 root cells inside the near-manifold set)

| threshold | level-1 cells within (of 216) | share of projected cost | LP kills there | kill rate there |
|---|---|---|---|---|
| eta(cell) <= 0.05 | 12 | 5.6% | 0/9 | 0% |
| eta(cell) <= 0.10 | 20 | 9.3% | 0/9 | 0% |
| eta(cell) <= 0.20 | 84 | 38.9% | 7/38 | 18% |
| d_pos(cell) <= 0.05 | 36 | 16.7% | 0/26 | 0% |
| d_pos(cell) <= 0.10 | 60 | 27.8% | 0/26 | 0% |
| d_pos(cell) <= 0.20 | 126 | 58.3% | 9/56 | 16% |

Total frontier cost in the model: 9191-21511 CPU-h (+150 (D)/(D')) = 9341-21661 CPU-h, A99's 9,341-21,661.

