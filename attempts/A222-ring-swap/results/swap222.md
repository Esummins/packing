# A222 exchange searches on the four-crowd witnesses (26 of 193 HELD + CROWD four-crowds; `swap222.jsonl`)

Per witness (side = the witness's own, 4.00-4.47): CORNER-SWAP per corner (X = the two meeters, S_c settled, one square placed in U(X) \ int S_c); WALL-SWAP per wall (both corners settled, two squares placed); RING4 (X = the eight meeters, all four corners settled, four squares placed); RING1 (one corner settled, seven placed; implied by a successful corner swap); RING4X (X = the meeters + the non-meeters that meet a window-perimeter cell, all four settled).  Placement: exact c-space per tilt for one square, seeded greedy + penalty restarts otherwise; every placement exact-checked on the composed 11-square configuration (SAT gaps and wall rows >= -1e-9).  A "not found" is a heuristic verdict for k >= 2 squares; for one square it is exact up to the 1-degree tilt grid.

| search | witnesses where it succeeds | notes |
|---|---|---|
| CORNER-SWAP at >= 1 corner | 26 / 26 | corners swappable per witness: 4: 13, 3: 11, 2: 1, 1: 1, 0: 0 |
| CORNER-SWAP at all four corners | 13 / 26 | |
| WALL-SWAP at >= 1 wall | 25 / 26 | walls per witness: 4: 3, 3: 13, 2: 6, 1: 3, 0: 1 |
| RING4 (all four settled) | 12 / 26 | fails: 14 (band squares placed 3: 12, 2: 2, <= 1: 0) |
| RING1 (>= 1 corner settled, ring re-packed) | 26 / 26 | all four corners: 14 |
| RING4X (intruders moved too) | 23 / 26 | intruders per witness: 0: 0, 1: 9, 2: 17, >= 3: 0 |
| RING4 or RING4X | 23 / 26 | |
| any exchange with >= 1 settled corner | 26 / 26 | (corner, ring1, ring4, ring4x) |

Blocked corner swaps: 16 of 104 corners; non-X squares cutting the hull of the two meeters: {0: 1, 1: 15} (0 = the remainders themselves are too thin: the two meeters cover the box and their outer parts hold no unit square without the free space).

## The ring rand_0_0569|t20 (side 4.1099, 20 s)
* corner_BL: X = [4, 5], settled ['BL'], place 1: not found (0 placed) (greedy+12 restarts, 0.64 s; non-X squares in the hull of X: [0])
* corner_BR: X = [6, 7], settled ['BR'], place 1: FOUND (greedy(18 tilts)+polish, 0.02 s; non-X squares in the hull of X: [])
* corner_TR: X = [8, 10], settled ['TR'], place 1: FOUND (greedy(18 tilts)+polish, 0.03 s; non-X squares in the hull of X: [1])
* corner_TL: X = [2, 3], settled ['TL'], place 1: FOUND (greedy(18 tilts)+polish, 0.03 s; non-X squares in the hull of X: [])
* wall_BLBR: X = [4, 5, 6, 7], settled ['BL', 'BR'], place 2: not found (1 placed) (greedy+12 restarts, 1.35 s; non-X squares in the hull of X: [0, 2, 8])
* wall_BRTR: X = [6, 7, 8, 10], settled ['BR', 'TR'], place 2: FOUND (greedy(18 tilts)+polish, 0.08 s; non-X squares in the hull of X: [0, 1, 9])
* wall_TRTL: X = [2, 3, 8, 10], settled ['TR', 'TL'], place 2: FOUND (greedy(18 tilts)+polish, 0.06 s; non-X squares in the hull of X: [0, 1, 9])
* wall_TLBL: X = [2, 3, 4, 5], settled ['TL', 'BL'], place 2: FOUND (penalty restart 3, 0.58 s; non-X squares in the hull of X: [0, 1, 9])
* ring4: X = [2, 3, 4, 5, 6, 7, 8, 10], settled ['BL', 'BR', 'TR', 'TL'], place 4: FOUND (seed 0+polish, 0.15 s; non-X squares in the hull of X: [0, 1, 9])
* ring1_BL: X = [2, 3, 4, 5, 6, 7, 8, 10], settled ['BL'], place 7: FOUND (penalty restart 4, 10.56 s; non-X squares in the hull of X: [0, 1, 9])
* ring1_BR: X = [2, 3, 4, 5, 6, 7, 8, 10], settled ['BR'], place 7: FOUND (implied by corner_BR, 0.00 s; non-X squares in the hull of X: [])
* ring1_TR: X = [2, 3, 4, 5, 6, 7, 8, 10], settled ['TR'], place 7: FOUND (implied by corner_TR, 0.00 s; non-X squares in the hull of X: [1])
* ring1_TL: X = [2, 3, 4, 5, 6, 7, 8, 10], settled ['TL'], place 7: FOUND (implied by corner_TL, 0.00 s; non-X squares in the hull of X: [])
* ring4x: X = [0, 2, 3, 4, 5, 6, 7, 8, 9, 10], settled ['BL', 'BR', 'TR', 'TL'], place 6: FOUND (penalty restart 11, 6.83 s; non-X squares in the hull of X: [1])

Sides: 4.0014 - 4.1099; wall time 425 s total.
RAISE (Lemma CELLS on census cells): `raise222_kept.md` (486 kept witnesses) and `raise222.md` (every search row).
