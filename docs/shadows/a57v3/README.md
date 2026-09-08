# The A57 / A60 review gallery, v3 (A142)

One page per surviving alive node, in the format the PI reviewed on 2026-09-07 (A140's `docs/shadows/k0v3/`), with the three objects the A57 figures had never shown: the **exact pin cores** (A135, half-side 1/2 - delta/sqrt2, certified), the **polygon core** K'(B) (A132, certified vertices) and the **pin-clipped centre box** (A131, exact rationals per tilt sub-bin). Every conditioned H carries all THREE of its cores in distinct styles - solid black = the stock axis core K(a) the LP pruned against, solid teal = A135's exact axis core, filled purple = K' - and every pin carries both its stock and its exact core. Schematic objects (centre boxes, clipped boxes, lane cells) are thin dashed outlines with no fill: they are regions of centres, not square bodies.

## 1. The population: which alive nodes survive today's kills

Start from A131's corpus (`attempts/A131-pin-clip/results/corpus131.jsonl`): of A96's 2418 boxes, 1744 are open and **607 are work-owing = 414 ALIVE + 193 FAIL**. Then remove today's kills, and every descendant of a killed node (monotonicity: a child's centre box is a sub-box and its tilt bin a sub-interval, so a geometric exclusion is inherited - A124 `notes/trim_empty_alive.md` section 4).

| step | list | hits the work-owing set | NEW removals | running total removed |
|---|---|---|---|---|
| A131 pin-clip kills (`backlog_kills.jsonl`) | 132 | 132 | 132 | 132 |
| A135 polygon (T5-poly) kills (`polycore_kills.jsonl`) | 64 | 54 | 6 | 138 |
| A135 LP kills certified through the verifier | 3 | 3 | 2 | 140 |
| A124 trim-empty ALIVE nodes (zero-LP sweep) | 54 | 54 | 0 | 140 |
| descendants of anything killed (monotonicity) | 824 | 2 | 2 | 142 |
| **surviving** | | | | **607 - 142 = 465** |

**465 nodes survive: 330 ALIVE + 135 FAIL**, by level L1 366, L2 95, L3 4, by class k5_11 243, k5_16 222. The four kill lists overlap heavily - the 54 A124 trim-empty nodes are ALL already inside the 132 pin-clip kills, and 54 of the 64 polygon kills are too, which is why 253 list entries remove only 142 nodes.

A60's alive population is the **283 nodes with an LP support** in A107's `shadow_nodes.json`; they are all at depth j = 0 (level 1) and none has emitted a child.

## 2. The subtree-cost ranking

From `docs/budget.md` section B: KILL-BY-LOGIC ~0 s, PASS ~850 s (LP 240-400 + exact verify 100 at s0 + 4-D window verify 545 at level 2), FAIL ~900 s, ALIVE-at-LP 300 s of LP **and then eight children**. With p_K(L), p_L(L), p_A(L) the measured per-level verdict shares of A57's own 2,418-box corpus,

```
C(L) = p_K(L)*0 + p_L(L)*850 + p_A(L)*(300 + 8*C(L+1)),    C(5) = 0

subtree(n) = residual(n) + SUM over still-open emitted descendants d of residual(d)
residual(ALIVE at L with no still-open emitted child) = 8*C(L+1) * kept8(n)
residual(ALIVE at L that already has such children)   = 0
residual(FAIL)                                        = 900 s
```

`kept8(n)` is A131's measured pin-clip kept VOLUME at 8 tilt sub-bins - the per-node alive fraction that multiplies the crude 8^(levels remaining); a node clipped to 12% of its box carries 12% of the modelled subtree. C(5) = 0 because the tree terminates at level 4 (budget.md section A: level-4 descent 0 of 30).

| level | corpus rows | logic | leaf (PASS+FAIL) | alive | C(L) |
|---|---|---|---|---|---|
| 1 | 1719 | 26.4% | 53.2% | 20.4% | 2632 s |
| 2 | 625 | 32.0% | 58.6% | 9.4% | 1297 s |
| 3 | 42 | 7.1% | 83.3% | 9.5% | 1020 s |
| 4 | 32 | 56.2% | 43.8% | 0.0% | 372 s |

The model cannot see inside an un-descended box, so every level-1 ALIVE node with kept8 = 1 and no emitted child gets the SAME subtree cost (2.88 CPU-h). Ties are broken by the polygon core's measured bite on that node's own dual support (A132 `measure132.jsonl`, `w_poly_only`): among equally expensive nodes, the ones where K' already excludes the most dual weight are the ones a geometric reading is most likely to close. That is the order below.

## 2b. A free kill found while drawing: the pin-clip at the EXACT pin core

A131 deployed the clip with the STOCK pin core half-side `A_PIN = 1/2 - delta = 0.49`. A135 certified the pin's guaranteed core to be the larger square of half-side `1/2 - delta/sqrt2 = 0.492928902`, and that the frozen verifiers take the half-side VERBATIM. Enlarging `a_pin` in the clip is sound for the same reason it is sound in the verifier: the conditioned square is interior-disjoint from the pin square, and the pin square CONTAINS K'(P) at every pose of the pin box. So the clip re-run at `a_pin = a_exact` is a strictly stronger geometric test at the same cost - and it is the composition of the day's two levers that nobody had run.

* **A57**: over all 465 surviving nodes the deployed stock-core clip empties **0** (the correct control - the 132 stock-clip kills were already removed from this population), and the exact-core clip empties **17**. Those **17 are NEW T5''' logic kills**, free, geometry only: `k5_11_interior_Y1002`, `k5_11_interior_Y0041_D02`, `k5_11_interior_Y0414_D02`, `k5_11_interior_Y0930`, `k5_11_interior_Y0978_D05`, `k5_11_interior_Y1002_D05`, `k5_11_interior_Y1134_D06`, `k5_11_interior_Y1134_D07`, `k5_16_interior_Y0930`, `k5_16_interior_Y0997`, `k5_16_interior_Y1002`, `k5_16_interior_Y0449`, `k5_16_interior_Y0648`, `k5_16_interior_Y0809`, `k5_11_interior_Y0997`, `k5_11_interior_Y1099`, `k5_16_interior_Y1099`.
* **A60 has never been clipped at all.** Its pins are EXACT placements (box `x0 = x1`), so the guaranteed pin core is the whole unit square, `a_pin = 1/2`. Of the 283 A60 nodes with an LP support, **34 clip to EMPTY** - dead by pin geometry, no LP, no certificate change. 143 more are narrowed (mean kept volume 0.54392).
* Across A57 the exact core also narrows **272 of 465** boxes strictly further than the stock core does (mean kept volume 0.60161 -> 0.58448).

Independent control (`results/clipsweep142.json`, sampling, not the same code path): 4,000 uniform poses drawn in the box of each EMPTY node give **zero** pin-free poses, while non-empty controls give 75-2,126. Every page below draws BOTH clips - pale orange dotted = stock, heavy orange dashed = exact - so the difference is visible on the node.

## 3. A57 - the top 40 by subtree cost

| # | node | class | L | subtree cost | family | tau/budget | K'-only support (cols / weight) | impossible cols (pins) | clip kept (exact core) | LANE<=1 corners | narrowest pocket | what to look for |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [`k5_11_interior_Y1104`](k5_11_interior_Y1104.svg) | k5_11 | 1 | 11.59 CPU-h | S10 | 5.000000/5 | 2 / 2.0 | 3 (0) | 1.000 | - | wall x=s 0.802 | 2 pocket(s) < 1: wall x=s 0.802, wall y=s 0.942; 3 impossible column(s) |
| 2 | [`k5_11_interior_Y0672`](k5_11_interior_Y0672.svg) | k5_11 | 1 | 4.53 CPU-h | S53 | 5.333333/5 | 9 / 3.0 | 11 (1) | 1.000 | - | P3 1.011 | 11 impossible column(s), 1 of them the PINS' |
| 3 | [`k5_16_interior_Y0083`](k5_16_interior_Y0083.svg) | k5_16 | 1 | 4.53 CPU-h | S02 | 4.500000/5 | 1 / 1.0 | 13 (4) | 1.000 | BL(1,0) | P1 0.439 | LANE<=1 at BL(1,0) (a second meeter is the cover); 4 pocket(s) < 1: P1 0.439, P0 0.491, P3 0.660; 13 impossible column(s), 4 of them the PINS' |
| 4 | [`k5_11_interior_Y0738`](k5_11_interior_Y0738.svg) | k5_11 | 1 | 3.76 CPU-h | S02 | 5.000000/5 | 2 / 0.6818 | 7 (0) | 0.904 | - | P1 0.123 | 6 pocket(s) < 1: P1 0.123, P2 0.153, wall x=0 0.802; 7 impossible column(s); pin-clip keeps only 0.904 of the box |
| 5 | [`k5_11_interior_Y1110`](k5_11_interior_Y1110.svg) | k5_11 | 1 | 2.88 CPU-h | S36 | 5.000000/5 | 5 / 5.0 | 5 (0) | 1.000 | TR(0,0) | wall x=s 0.933 | LANE<=1 at TR(0,0) (a second meeter is the cover); 2 pocket(s) < 1: wall x=s 0.933, wall y=s 0.933; 5 impossible column(s) |
| 6 | [`k5_11_interior_Y0286`](k5_11_interior_Y0286.svg) | k5_11 | 1 | 2.88 CPU-h | S01 | 5.500000/5 | 8 / 4.0 | 8 (2) | 1.000 | - | P1 0.980 | 4 pocket(s) < 1: P1 0.980, P4 0.983, wall x=s 0.985; 8 impossible column(s), 2 of them the PINS' |
| 7 | [`k5_11_interior_Y0609`](k5_11_interior_Y0609.svg) | k5_11 | 1 | 2.88 CPU-h | - | 5.000000/5 | 4 / 4.0 | 4 (0) | 1.000 | - | wall x=s 0.957 | 4 pocket(s) < 1: wall x=s 0.957, wall y=s 0.957, P1 0.968; 4 impossible column(s) |
| 8 | [`k5_11_interior_Y0626`](k5_11_interior_Y0626.svg) | k5_11 | 1 | 2.88 CPU-h | - | 5.000000/5 | 5 / 4.0 | 5 (2) | 1.000 | TL(1,0) | wall y=s 0.817 | LANE<=1 at TL(1,0) (a second meeter is the cover); 3 pocket(s) < 1: wall y=s 0.817, P1 0.881, P2 0.919; 5 impossible column(s), 2 of them the PINS' |
| 9 | [`k5_11_interior_Y0662`](k5_11_interior_Y0662.svg) | k5_11 | 1 | 2.88 CPU-h | - | 5.000000/5 | 4 / 4.0 | 4 (0) | 1.000 | - | wall y=s 0.817 | 2 pocket(s) < 1: wall y=s 0.817, wall x=s 0.957; 4 impossible column(s) |
| 10 | [`k5_16_interior_Y0058`](k5_16_interior_Y0058.svg) | k5_16 | 1 | 2.88 CPU-h | S05 | 5.000000/5 | 4 / 4.0 | 4 (0) | 1.000 | - | P4 0.369 | 2 pocket(s) < 1: P4 0.369, P3 0.731; 4 impossible column(s) |
| 11 | [`k5_16_interior_Y0626`](k5_16_interior_Y0626.svg) | k5_16 | 1 | 2.88 CPU-h | S05 | 5.000000/5 | 4 / 4.0 | 4 (2) | 1.000 | TL(1,0) | P4 0.147 | LANE<=1 at TL(1,0) (a second meeter is the cover); 4 pocket(s) < 1: P4 0.147, wall y=s 0.817, P1 0.881; 4 impossible column(s), 2 of them the PINS' |
| 12 | [`k5_11_interior_Y0130`](k5_11_interior_Y0130.svg) | k5_11 | 1 | 2.88 CPU-h | S01 | 5.500000/5 | 7 / 3.5 | 7 (2) | 1.000 | - | P1 1.007 | 7 impossible column(s), 2 of them the PINS' |
| 13 | [`k5_16_interior_Y0206`](k5_16_interior_Y0206.svg) | k5_16 | 1 | 2.88 CPU-h | S03 | 5.000000/5 | 27 / 3.1667 | 27 (4) | 1.000 | - | P4 0.421 | 4 pocket(s) < 1: P4 0.421, P3 0.709, P1 0.970; 27 impossible column(s), 4 of them the PINS' |
| 14 | [`k5_11_interior_Y0241`](k5_11_interior_Y0241.svg) | k5_11 | 1 | 2.88 CPU-h | S01 | 5.000000/5 | 3 / 3.0 | 4 (0) | 1.000 | - | P4 0.831 | 3 pocket(s) < 1: P4 0.831, wall x=s 0.845, P3 0.991; 4 impossible column(s) |
| 15 | [`k5_11_interior_Y0249`](k5_11_interior_Y0249.svg) | k5_11 | 1 | 2.88 CPU-h | S01 | 5.000000/5 | 3 / 3.0 | 3 (0) | 1.000 | - | P4 0.846 | 4 pocket(s) < 1: P4 0.846, P3 0.952, P1 0.970; 3 impossible column(s) |
| 16 | [`k5_11_interior_Y0275`](k5_11_interior_Y0275.svg) | k5_11 | 1 | 2.88 CPU-h | - | 5.000000/5 | 3 / 3.0 | 3 (0) | 1.000 | - | P1 0.842 | 3 pocket(s) < 1: P1 0.842, P2 0.958, wall y=s 0.985; 3 impossible column(s) |
| 17 | [`k5_11_interior_Y0308`](k5_11_interior_Y0308.svg) | k5_11 | 1 | 2.88 CPU-h | S01 | 5.000000/5 | 4 / 3.0 | 4 (0) | 1.000 | - | wall y=s 0.845 | 2 pocket(s) < 1: wall y=s 0.845, wall x=s 0.985; 4 impossible column(s) |
| 18 | [`k5_11_interior_Y0500`](k5_11_interior_Y0500.svg) | k5_11 | 1 | 2.88 CPU-h | S02 | 5.000000/5 | 7 / 3.0 | 8 (2) | 1.000 | - | P4 0.839 | 4 pocket(s) < 1: P4 0.839, P1 0.946, P3 0.955; 8 impossible column(s), 2 of them the PINS' |
| 19 | [`k5_11_interior_Y0985`](k5_11_interior_Y0985.svg) | k5_11 | 1 | 2.88 CPU-h | S01 | 5.000000/5 | 131 / 3.0 | 188 (27) | 1.000 | - | wall x=s 0.830 | 2 pocket(s) < 1: wall x=s 0.830, wall y=s 0.969; 188 impossible column(s), 27 of them the PINS' |
| 20 | [`k5_11_interior_Y1117`](k5_11_interior_Y1117.svg) | k5_11 | 1 | 2.88 CPU-h | S44 | 5.000000/5 | 13 / 3.0 | 14 (0) | 1.000 | TR(0,0) | wall x=s 0.942 | LANE<=1 at TR(0,0) (a second meeter is the cover); 4 pocket(s) < 1: wall x=s 0.942, wall y=s 0.942, P3 0.989; 14 impossible column(s) |
| 21 | [`k5_16_interior_Y0027`](k5_16_interior_Y0027.svg) | k5_16 | 1 | 2.88 CPU-h | S01 | 5.000000/5 | 3 / 3.0 | 4 (1) | 1.000 | - | P3 0.454 | 2 pocket(s) < 1: P3 0.454, P4 0.646; 4 impossible column(s), 1 of them the PINS' |
| 22 | [`k5_16_interior_Y0191`](k5_16_interior_Y0191.svg) | k5_16 | 1 | 2.88 CPU-h | S03 | 5.000000/5 | 87 / 3.0 | 103 (0) | 1.000 | BL(1,0) | P1 0.271 | LANE<=1 at BL(1,0) (a second meeter is the cover); 4 pocket(s) < 1: P1 0.271, P0 0.316, P3 0.823; 103 impossible column(s) |
| 23 | [`k5_16_interior_Y0260`](k5_16_interior_Y0260.svg) | k5_16 | 1 | 2.88 CPU-h | S01 | 5.000000/5 | 3 / 3.0 | 3 (0) | 1.000 | - | P3 0.208 | 4 pocket(s) < 1: P3 0.208, P4 0.958, P1 0.970; 3 impossible column(s) |
| 24 | [`k5_16_interior_Y0275`](k5_16_interior_Y0275.svg) | k5_16 | 1 | 2.88 CPU-h | S11 | 5.000000/5 | 125 / 3.0 | 131 (24) | 1.000 | - | P4 0.208 | 4 pocket(s) < 1: P4 0.208, P1 0.842, P2 0.958; 131 impossible column(s), 24 of them the PINS' |
| 25 | [`k5_16_interior_Y0823`](k5_16_interior_Y0823.svg) | k5_16 | 1 | 2.88 CPU-h | S01 | 5.000000/5 | 3 / 3.0 | 4 (1) | 1.000 | - | P4 0.433 | 3 pocket(s) < 1: P4 0.433, P1 0.804, P3 0.918; 4 impossible column(s), 1 of them the PINS' |
| 26 | [`k5_16_interior_Y0839`](k5_16_interior_Y0839.svg) | k5_16 | 1 | 2.88 CPU-h | S01 | 5.000000/5 | 3 / 3.0 | 4 (1) | 1.000 | - | P3 0.209 | 3 pocket(s) < 1: P3 0.209, wall x=s 0.799, P4 0.896; 4 impossible column(s), 1 of them the PINS' |
| 27 | [`k5_16_interior_Y0842`](k5_16_interior_Y0842.svg) | k5_16 | 1 | 2.88 CPU-h | S02 | 5.000000/5 | 4 / 3.0 | 5 (0) | 1.000 | - | P3 0.433 | 3 pocket(s) < 1: P3 0.433, P1 0.784, P0 0.918; 5 impossible column(s) |
| 28 | [`k5_16_interior_Y0881`](k5_16_interior_Y0881.svg) | k5_16 | 1 | 2.88 CPU-h | S01 | 5.000000/5 | 136 / 3.0 | 174 (56) | 1.000 | - | P4 0.460 | 4 pocket(s) < 1: P4 0.460, P3 0.774, P1 0.928; 174 impossible column(s), 56 of them the PINS' |
| 29 | [`k5_16_interior_Y0941`](k5_16_interior_Y0941.svg) | k5_16 | 1 | 2.88 CPU-h | S02 | 5.000000/5 | 3 / 3.0 | 3 (1) | 1.000 | - | P1 0.396 | 3 pocket(s) < 1: P1 0.396, P0 0.714, P3 0.755; 3 impossible column(s), 1 of them the PINS' |
| 30 | [`k5_16_interior_Y0968`](k5_16_interior_Y0968.svg) | k5_16 | 1 | 2.88 CPU-h | S39 | 5.000000/5 | 5 / 3.0 | 5 (0) | 1.000 | - | P4 0.237 | 5 pocket(s) < 1: P4 0.237, wall x=s 0.939, wall y=s 0.939; 5 impossible column(s) |
| 31 | [`k5_16_interior_Y1056`](k5_16_interior_Y1056.svg) | k5_16 | 1 | 2.88 CPU-h | S08 | 5.000000/5 | 6 / 3.0 | 7 (1) | 1.000 | - | P1 0.260 | 3 pocket(s) < 1: P1 0.260, P2 0.440, P0 0.936; 7 impossible column(s), 1 of them the PINS' |
| 32 | [`k5_16_interior_Y0460`](k5_16_interior_Y0460.svg) | k5_16 | 1 | 2.88 CPU-h | - | 5.000000/5 | 20 / 2.5833 | 24 (0) | 1.000 | - | P3 0.466 | 3 pocket(s) < 1: P3 0.466, P1 0.585, P0 0.682; 24 impossible column(s) |
| 33 | [`k5_16_interior_Y0249`](k5_16_interior_Y0249.svg) | k5_16 | 1 | 2.88 CPU-h | S03 | 5.000000/5 | 3 / 2.5 | 4 (0) | 1.000 | - | P4 0.287 | 4 pocket(s) < 1: P4 0.287, P3 0.846, P1 0.970; 4 impossible column(s) |
| 34 | [`k5_11_interior_Y0250`](k5_11_interior_Y0250.svg) | k5_11 | 1 | 2.88 CPU-h | S01 | 5.000000/5 | 28 / 2.4317 | 34 (7) | 1.000 | - | wall x=s 0.705 | 3 pocket(s) < 1: wall x=s 0.705, P4 0.970, wall y=s 0.985; 34 impossible column(s), 7 of them the PINS' |
| 35 | [`k5_16_interior_Y0402`](k5_16_interior_Y0402.svg) | k5_16 | 1 | 2.88 CPU-h | S03 | 5.000000/5 | 9 / 2.3333 | 9 (0) | 1.000 | - | P1 0.306 | 3 pocket(s) < 1: P1 0.306, P0 0.411, P3 0.738; 9 impossible column(s) |
| 36 | [`k5_16_interior_Y1117`](k5_16_interior_Y1117.svg) | k5_16 | 1 | 2.88 CPU-h | S01 | 5.000000/5 | 7 / 2.25 | 8 (3) | 1.000 | - | P4 0.243 | 4 pocket(s) < 1: P4 0.243, wall x=s 0.942, wall y=s 0.942; 8 impossible column(s), 3 of them the PINS' |
| 37 | [`k5_16_interior_Y0500`](k5_16_interior_Y0500.svg) | k5_16 | 1 | 2.88 CPU-h | S01 | 5.000000/5 | 84 / 2.1462 | 105 (24) | 1.000 | - | P4 0.329 | 4 pocket(s) < 1: P4 0.329, P3 0.839, P1 0.946; 105 impossible column(s), 24 of them the PINS' |
| 38 | [`k5_16_interior_Y0044`](k5_16_interior_Y0044.svg) | k5_16 | 1 | 2.88 CPU-h | S01 | 5.000000/5 | 37 / 2.0782 | 41 (4) | 1.000 | BL(1,0) | P1 0.306 | LANE<=1 at BL(1,0) (a second meeter is the cover); 3 pocket(s) < 1: P1 0.306, P0 0.318, P3 0.784; 41 impossible column(s), 4 of them the PINS' |
| 39 | [`k5_11_interior_Y0147`](k5_11_interior_Y0147.svg) | k5_11 | 1 | 2.88 CPU-h | S01 | 5.000000/5 | 2 / 2.0 | 2 (0) | 1.000 | - | wall y=s 0.740 | 1 pocket(s) < 1: wall y=s 0.740; 2 impossible column(s) |
| 40 | [`k5_11_interior_Y0202`](k5_11_interior_Y0202.svg) | k5_11 | 1 | 2.88 CPU-h | S05 | 5.000000/5 | 2 / 2.0 | 2 (0) | 1.000 | - | P3 0.172 | 4 pocket(s) < 1: P3 0.172, P1 0.551, P4 0.594; 2 impossible column(s) |

## 4. A60 - the top 20 by subtree cost

| # | node | class | L | subtree cost | family | tau/budget | K'-only support (cols / weight) | impossible cols (pins) | clip kept (exact core) | LANE<=1 corners | narrowest pocket | what to look for |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [`slack0.02_c0_Y0272`](slack0.02_c0_Y0272.svg) | trump5_j0 | 1 | 2.88 CPU-h | S01 | 5.000000/5 | 8 / 4.5 | 8 (3) | 1.000 | TL(0,0) | P2 0.209 | LANE<=1 at TL(0,0) (a second meeter is the cover); 2 pocket(s) < 1: P2 0.209, wall y=s 0.880; 8 impossible column(s), 3 of them the PINS' |
| 2 | [`c0_Y0254`](c0_Y0254.svg) | trump5_j0 | 1 | 2.88 CPU-h | S01 | 5.000000/5 | 6 / 3.0 | 7 (0) | **EMPTY - dead** | - | P2 0.000 | **DEAD**: the pin-clip at the EXACT pin core empties the box at all 8 tilt sub-bins; 4 pocket(s) < 1: P2 0.000, P1 0.683, P0 0.815; 7 impossible column(s); pin-clip keeps only 0.000 of the box |
| 3 | [`c0_Y0258`](c0_Y0258.svg) | trump5_j0 | 1 | 2.88 CPU-h | S01 | 5.000000/5 | 3 / 3.0 | 3 (0) | 1.000 | - | P2 0.131 | 4 pocket(s) < 1: P2 0.131, P1 0.780, P0 0.859; 3 impossible column(s) |
| 4 | [`c0_Y0787`](c0_Y0787.svg) | trump5_j0 | 1 | 2.88 CPU-h | S01 | 5.000000/5 | 3 / 3.0 | 3 (0) | 1.000 | - | P1 0.130 | 5 pocket(s) < 1: P1 0.130, P3 0.339, P2 0.771; 3 impossible column(s) |
| 5 | [`c0_Y0939`](c0_Y0939.svg) | trump5_j0 | 1 | 2.88 CPU-h | S01 | 5.000000/5 | 3 / 3.0 | 3 (0) | 1.000 | - | P4 0.234 | 4 pocket(s) < 1: P4 0.234, wall x=s 0.933, wall y=s 0.933; 3 impossible column(s) |
| 6 | [`c0_Y0942`](c0_Y0942.svg) | trump5_j0 | 1 | 2.88 CPU-h | S01 | 5.000000/5 | 3 / 3.0 | 3 (0) | 0.856 | - | P4 0.144 | 5 pocket(s) < 1: P4 0.144, P2 0.972, P3 0.975; 3 impossible column(s); pin-clip keeps only 0.856 of the box |
| 7 | [`c0_Y0959`](c0_Y0959.svg) | trump5_j0 | 1 | 2.88 CPU-h | S01 | 5.000000/5 | 5 / 3.0 | 7 (2) | 0.031 | - | P4 0.019 | 2 pocket(s) < 1: P4 0.019, wall y=s 0.740; 7 impossible column(s), 2 of them the PINS'; pin-clip keeps only 0.031 of the box |
| 8 | [`c0_Y1033`](c0_Y1033.svg) | trump5_j0 | 1 | 2.88 CPU-h | S01 | 5.000000/5 | 3 / 3.0 | 3 (0) | 0.323 | - | P4 0.079 | 3 pocket(s) < 1: P4 0.079, wall x=s 0.830, wall y=s 0.969; 3 impossible column(s); pin-clip keeps only 0.323 of the box |
| 9 | [`c0_Y1038`](c0_Y1038.svg) | trump5_j0 | 1 | 2.88 CPU-h | S01 | 5.000000/5 | 3 / 3.0 | 3 (0) | 0.647 | - | P4 0.105 | 4 pocket(s) < 1: P4 0.105, wall x=s 0.845, P3 0.963; 3 impossible column(s); pin-clip keeps only 0.647 of the box |
| 10 | [`f1_L10_0003`](f1_L10_0003.svg) | trump5_j0 | 1 | 2.88 CPU-h | S07 | 4.000000/4 | 3 / 3.0 | 4 (2) | 1.000 | TR(1,0) | P4 0.012 | LANE<=1 at TR(1,0) (a second meeter is the cover); 3 pocket(s) < 1: P4 0.012, wall y=s 0.558, wall x=s 0.767; 4 impossible column(s), 2 of them the PINS' |
| 11 | [`c0_Y0952`](c0_Y0952.svg) | trump5_j0 | 1 | 2.88 CPU-h | S01 | 5.000000/5 | 5 / 2.5 | 7 (2) | 0.336 | - | P4 0.062 | 2 pocket(s) < 1: P4 0.062, wall y=s 0.740; 7 impossible column(s), 2 of them the PINS'; pin-clip keeps only 0.336 of the box |
| 12 | [`c0_Y0788`](c0_Y0788.svg) | trump5_j0 | 1 | 2.88 CPU-h | S03 | 5.000000/5 | 15 / 2.375 | 19 (1) | 1.000 | - | P1 0.131 | 5 pocket(s) < 1: P1 0.131, P3 0.339, P2 0.777; 19 impossible column(s), 1 of them the PINS' |
| 13 | [`c0_Y0257`](c0_Y0257.svg) | trump5_j0 | 1 | 2.88 CPU-h | S08 | 5.000000/5 | 5 / 2.3333 | 5 (0) | 0.883 | - | P2 0.127 | 4 pocket(s) < 1: P2 0.127, P1 0.808, P0 0.845; 5 impossible column(s); pin-clip keeps only 0.883 of the box |
| 14 | [`c0_Y0878`](c0_Y0878.svg) | trump5_j0 | 1 | 2.88 CPU-h | S01 | 5.076923/5 | 73 / 2.2367 | 100 (22) | **EMPTY - dead** | - | P1 0.004 | **DEAD**: the pin-clip at the EXACT pin core empties the box at all 8 tilt sub-bins; 6 pocket(s) < 1: P1 0.004, P3 0.105, wall y=0 0.845; 100 impossible column(s), 22 of them the PINS'; pin-clip keeps only 0.000 of the box |
| 15 | [`c0_Y0695`](c0_Y0695.svg) | trump5_j0 | 1 | 2.88 CPU-h | S02 | 5.000000/5 | 37 / 2.2017 | 41 (4) | 0.241 | - | P1 0.044 | 4 pocket(s) < 1: P1 0.044, P3 0.361, P2 0.718; 41 impossible column(s), 4 of them the PINS'; pin-clip keeps only 0.241 of the box |
| 16 | [`c0_Y0255`](c0_Y0255.svg) | trump5_j0 | 1 | 2.88 CPU-h | S03 | 5.000000/5 | 11 / 2.2 | 13 (2) | 0.031 | - | P2 0.019 | 3 pocket(s) < 1: P2 0.019, P1 0.718, P0 0.776; 13 impossible column(s), 2 of them the PINS'; pin-clip keeps only 0.031 of the box |
| 17 | [`c0_Y0076`](c0_Y0076.svg) | trump5_j0 | 1 | 2.88 CPU-h | S02 | 5.000000/5 | 2 / 2.0 | 3 (1) | 0.291 | - | P2 0.052 | 5 pocket(s) < 1: P2 0.052, wall x=0 0.659, P1 0.917; 3 impossible column(s), 1 of them the PINS'; pin-clip keeps only 0.291 of the box |
| 18 | [`c0_Y0168`](c0_Y0168.svg) | trump5_j0 | 1 | 2.88 CPU-h | S01 | 5.000000/5 | 2 / 2.0 | 4 (1) | **EMPTY - dead** | - | P2 0.000 | **DEAD**: the pin-clip at the EXACT pin core empties the box at all 8 tilt sub-bins; 4 pocket(s) < 1: P2 0.000, wall x=0 0.880, P0 0.998; 4 impossible column(s), 1 of them the PINS'; pin-clip keeps only 0.000 of the box |
| 19 | [`c0_Y0169`](c0_Y0169.svg) | trump5_j0 | 1 | 2.88 CPU-h | S38 | 5.000000/5 | 2 / 2.0 | 3 (1) | 0.248 | TL(0,0) | P2 0.069 | LANE<=1 at TL(0,0) (a second meeter is the cover); 5 pocket(s) < 1: P2 0.069, wall x=0 0.830, P1 0.948; 3 impossible column(s), 1 of them the PINS'; pin-clip keeps only 0.248 of the box |
| 20 | [`c0_Y0171`](c0_Y0171.svg) | trump5_j0 | 1 | 2.88 CPU-h | S01 | 5.000000/5 | 2 / 2.0 | 3 (1) | 1.000 | BL(0,2), TL(0,0) | P2 0.126 | LANE<=1 at BL(0,2), TL(0,0) (a second meeter is the cover); 5 pocket(s) < 1: P2 0.126, wall x=0 0.793, P1 0.911; 3 impossible column(s), 1 of them the PINS' |

## 5. How to read a page

* **Panel 1** is the LP's own dual support at s0. A red-dashed column is a placement the LP is charging weight to that **cannot exist** under this node's hypothesis - it overlaps the conditioned square H, or one of the five pins, at every one of 7^3 sampled poses of that square's box. Each is labelled with which core it clears and which it meets, so `clears K(a) stock, clears K exact, meets K'` is a column only the polygon core reaches, and `clears K(a) stock, meets K exact` is one the exact pin core alone reaches - the slop A132's attribution found.
* **Panel 2** is the near-packing, and its names are the names to label from.
* **Panel 3** is the hypothesis alone: the three cores of H captioned with `a_stock / a_exact / area K'`, the pin-clipped centre box per tilt sub-bin, the A118 LANE<=1 corner cells, and the measured pockets.
* **The line under each page** names the corners whose lane count is 1 (a second meeter is what a two-meeter cover needs) and the pockets between K'(B) and the nearest pin narrower than 1 - nothing fits there, so any square the LP puts in that region is a column the geometry forbids.

Lane counts are **A118's stored AXIS-CORE verdicts** (K(a), not K'). A141's K' lane run had not landed when these pages were drawn, so a corner marked UNDECIDED here may still become LANE<=1 under K' - that is exactly the s3_far effect the PI read on A140's page.

**Geometry check** (`code/verify142.py`, a second implementation using edge-crossing and strict point-in-polygon, no separating axis anywhere): 1240 red-dashed columns re-verified over 361906 poses, 0 failures; 2088 non-flagged columns each shown disjoint at some pose of every box, 0 failures; 300 exact pin cores contained in their pin square at every pose, 0 failures; 2384 K'(B) vertices contained at every pose, 0 failures; 446 clipped rects inside the original box, 0 failures.

Files: 40 A57 pages + 20 A60 pages, `review_a57v3.csv` (the review sheet, PI columns empty), and the machine-readable record in `attempts/A142-a57-review-gallery/results/`.
