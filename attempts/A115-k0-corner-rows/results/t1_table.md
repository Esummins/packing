# A115 T1 -- the K01 room: which corner cell the support leaves empty or singly met

`closed` = meets [0,1]^2 (mu_c <= 1, the s0 convention); `wide` = meets the K0-WIDEN box [0, 1.025520]^2.  84 K01 cells.

## corner-cell occupancy of the shadow (11 placements), by corner

| corner | 0 meeters | 1 meeter | 2 meeters | >=3 |
|---|---|---|---|---|
| BL | 0 | 57 | 21 | 6 |
| BR | 0 | 35 | 38 | 11 |
| TL | 0 | 70 | 11 | 3 |
| TR | 0 | 50 | 28 | 6 |

## which corners are 'room' (met by <= 1), as a set

| room set (closed) | cells | room set (widened) | cells |
|---|---|---|---|
| BL+TL | 16 | BL | 20 |
| BL+BR+TL+TR | 14 | (none) | 18 |
| BL+TL+TR | 12 | TL | 11 |
| TL+TR | 10 | TR | 10 |
| BL+BR+TL | 7 | TL+TR | 7 |
| BR+TL+TR | 6 | BL+TL | 6 |
| TR | 4 | BR+TR | 3 |
| BR+TL | 3 | BR | 3 |
| BL+BR | 3 | BL+BR | 2 |
| BL+TR | 3 | BL+TR | 2 |
| BL | 2 | BR+TL+TR | 2 |
| TL | 2 |  |  |
| BR+TR | 1 |  |  |
| BR | 1 |  |  |

## depth of the meeters that ARE there, by corner (shadow placements with mu_c <= 1)

| corner | 0 (touch/none) | (0,0.05) | [0.05,0.10) | [0.10,0.155) | [0.155,0.30) | >=0.30 | total |
|---|---|---|---|---|---|---|---|
| BL | 0 | 25 | 2 | 2 | 9 | 79 | 117 |
| BR | 0 | 36 | 0 | 16 | 20 | 72 | 144 |
| TL | 0 | 11 | 0 | 2 | 6 | 82 | 101 |
| TR | 0 | 16 | 4 | 14 | 27 | 63 | 124 |

## the SECOND meeter's depth d2 (the quantity Lemma CW conditions on), by corner

| corner | no 2nd meeter | d2 = 0 | d2 in (0,.05) | [.05,.10) | [.10,.155) | [.155,.30) | >= .30 |
|---|---|---|---|---|---|---|---|
| BL | 57 | 0 | 19 | 1 | 2 | 5 | 0 |
| BR | 35 | 0 | 28 | 0 | 11 | 10 | 0 |
| TL | 70 | 0 | 10 | 0 | 1 | 3 | 0 |
| TR | 50 | 0 | 14 | 3 | 10 | 7 | 0 |

## fractional crowd weight of the LP dual support (what the rows charge)

| level | cells | mean budget | mean total LP weight | mean weight in U_c F_c(widened) | mean weight per corner |
|---|---|---|---|---|---|
| 1 | 65 | 9.92 | 9.597 | 7.315 | BL 1.70 / BR 2.06 / TL 1.75 / TR 1.80 |
| 2 | 15 | 10.00 | 9.016 | 6.588 | BL 1.78 / BR 2.01 / TL 1.73 / TR 1.07 |
| 3 | 4 | 10.00 | 8.676 | 5.962 | BL 1.69 / BR 1.88 / TL 1.89 / TR 0.50 |

