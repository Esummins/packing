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

## 3. A57 - the top 40 by subtree cost

| # | node | class | L | subtree cost | family | tau/budget | K'-only support (cols / weight) | impossible cols (pins) | LANE<=1 corners | narrowest pocket | what to look for |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [`k5_11_interior_Y1104`](k5_11_interior_Y1104.svg) | k5_11 | 1 | 11.59 CPU-h | S10 | 5.000000/5 | 2 / 2.0 | 3 (0) | - | wall x=s 0.802 | 2 pocket(s) < 1: wall x=s 0.802, wall y=s 0.942; 3 impossible column(s) |
| 2 | [`k5_11_interior_Y0672`](k5_11_interior_Y0672.svg) | k5_11 | 1 | 4.53 CPU-h | S53 | 5.333333/5 | 9 / 3.0 | 11 (1) | - | P3 1.011 | 11 impossible column(s), 1 of them the PINS' |
| 3 | [`k5_16_interior_Y0083`](k5_16_interior_Y0083.svg) | k5_16 | 1 | 4.53 CPU-h | S02 | 4.500000/5 | 1 / 1.0 | 13 (4) | BL(1,0) | P1 0.439 | LANE<=1 at BL(1,0) (a second meeter is the cover); 4 pocket(s) < 1: P1 0.439, P0 0.491, P3 0.660; 13 impossible column(s), 4 of them the PINS' |
| 4 | [`k5_11_interior_Y0738`](k5_11_interior_Y0738.svg) | k5_11 | 1 | 3.76 CPU-h | S02 | 5.000000/5 | 2 / 0.6818 | 7 (0) | - | P1 0.123 | 6 pocket(s) < 1: P1 0.123, P2 0.153, wall x=0 0.802; 7 impossible column(s); pin-clip keeps only 0.924 of the box |
| 5 | [`k5_11_interior_Y1110`](k5_11_interior_Y1110.svg) | k5_11 | 1 | 2.88 CPU-h | S36 | 5.000000/5 | 5 / 5.0 | 5 (0) | TR(0,0) | wall x=s 0.933 | LANE<=1 at TR(0,0) (a second meeter is the cover); 2 pocket(s) < 1: wall x=s 0.933, wall y=s 0.933; 5 impossible column(s) |
| 6 | [`k5_11_interior_Y0286`](k5_11_interior_Y0286.svg) | k5_11 | 1 | 2.88 CPU-h | S01 | 5.500000/5 | 8 / 4.0 | 8 (2) | - | P1 0.980 | 4 pocket(s) < 1: P1 0.980, P4 0.983, wall x=s 0.985; 8 impossible column(s), 2 of them the PINS' |
| 7 | [`k5_11_interior_Y0609`](k5_11_interior_Y0609.svg) | k5_11 | 1 | 2.88 CPU-h | - | 5.000000/5 | 4 / 4.0 | 4 (0) | - | wall x=s 0.957 | 4 pocket(s) < 1: wall x=s 0.957, wall y=s 0.957, P1 0.968; 4 impossible column(s) |
| 8 | [`k5_11_interior_Y0626`](k5_11_interior_Y0626.svg) | k5_11 | 1 | 2.88 CPU-h | - | 5.000000/5 | 5 / 4.0 | 5 (2) | TL(1,0) | wall y=s 0.817 | LANE<=1 at TL(1,0) (a second meeter is the cover); 3 pocket(s) < 1: wall y=s 0.817, P1 0.881, P2 0.919; 5 impossible column(s), 2 of them the PINS' |
| 9 | [`k5_11_interior_Y0662`](k5_11_interior_Y0662.svg) | k5_11 | 1 | 2.88 CPU-h | - | 5.000000/5 | 4 / 4.0 | 4 (0) | - | wall y=s 0.817 | 2 pocket(s) < 1: wall y=s 0.817, wall x=s 0.957; 4 impossible column(s) |
| 10 | [`k5_16_interior_Y0058`](k5_16_interior_Y0058.svg) | k5_16 | 1 | 2.88 CPU-h | S05 | 5.000000/5 | 4 / 4.0 | 4 (0) | - | P4 0.369 | 2 pocket(s) < 1: P4 0.369, P3 0.731; 4 impossible column(s) |
| 11 | [`k5_16_interior_Y0626`](k5_16_interior_Y0626.svg) | k5_16 | 1 | 2.88 CPU-h | S05 | 5.000000/5 | 4 / 4.0 | 4 (2) | TL(1,0) | P4 0.147 | LANE<=1 at TL(1,0) (a second meeter is the cover); 4 pocket(s) < 1: P4 0.147, wall y=s 0.817, P1 0.881; 4 impossible column(s), 2 of them the PINS' |
| 12 | [`k5_11_interior_Y0130`](k5_11_interior_Y0130.svg) | k5_11 | 1 | 2.88 CPU-h | S01 | 5.500000/5 | 7 / 3.5 | 7 (2) | - | P1 1.007 | 7 impossible column(s), 2 of them the PINS' |
| 13 | [`k5_16_interior_Y0206`](k5_16_interior_Y0206.svg) | k5_16 | 1 | 2.88 CPU-h | S03 | 5.000000/5 | 27 / 3.1667 | 27 (4) | - | P4 0.421 | 4 pocket(s) < 1: P4 0.421, P3 0.709, P1 0.970; 27 impossible column(s), 4 of them the PINS' |
| 14 | [`k5_11_interior_Y0241`](k5_11_interior_Y0241.svg) | k5_11 | 1 | 2.88 CPU-h | S01 | 5.000000/5 | 3 / 3.0 | 4 (0) | - | P4 0.831 | 3 pocket(s) < 1: P4 0.831, wall x=s 0.845, P3 0.991; 4 impossible column(s) |
| 15 | [`k5_11_interior_Y0249`](k5_11_interior_Y0249.svg) | k5_11 | 1 | 2.88 CPU-h | S01 | 5.000000/5 | 3 / 3.0 | 3 (0) | - | P4 0.846 | 4 pocket(s) < 1: P4 0.846, P3 0.952, P1 0.970; 3 impossible column(s) |
| 16 | [`k5_11_interior_Y0275`](k5_11_interior_Y0275.svg) | k5_11 | 1 | 2.88 CPU-h | - | 5.000000/5 | 3 / 3.0 | 3 (0) | - | P1 0.842 | 3 pocket(s) < 1: P1 0.842, P2 0.958, wall y=s 0.985; 3 impossible column(s) |
| 17 | [`k5_11_interior_Y0308`](k5_11_interior_Y0308.svg) | k5_11 | 1 | 2.88 CPU-h | S01 | 5.000000/5 | 4 / 3.0 | 4 (0) | - | wall y=s 0.845 | 2 pocket(s) < 1: wall y=s 0.845, wall x=s 0.985; 4 impossible column(s) |
| 18 | [`k5_11_interior_Y0500`](k5_11_interior_Y0500.svg) | k5_11 | 1 | 2.88 CPU-h | S02 | 5.000000/5 | 7 / 3.0 | 8 (2) | - | P4 0.839 | 4 pocket(s) < 1: P4 0.839, P1 0.946, P3 0.955; 8 impossible column(s), 2 of them the PINS' |
| 19 | [`k5_11_interior_Y0985`](k5_11_interior_Y0985.svg) | k5_11 | 1 | 2.88 CPU-h | S01 | 5.000000/5 | 131 / 3.0 | 188 (27) | - | wall x=s 0.830 | 2 pocket(s) < 1: wall x=s 0.830, wall y=s 0.969; 188 impossible column(s), 27 of them the PINS' |
| 20 | [`k5_11_interior_Y1117`](k5_11_interior_Y1117.svg) | k5_11 | 1 | 2.88 CPU-h | S44 | 5.000000/5 | 13 / 3.0 | 14 (0) | TR(0,0) | wall x=s 0.942 | LANE<=1 at TR(0,0) (a second meeter is the cover); 4 pocket(s) < 1: wall x=s 0.942, wall y=s 0.942, P3 0.989; 14 impossible column(s) |

## 5. How to read a page

* **Panel 1** is the LP's own dual support at s0. A red-dashed column is a placement the LP is charging weight to that **cannot exist** under this node's hypothesis - it overlaps the conditioned square H, or one of the five pins, at every one of 7^3 sampled poses of that square's box. Each is labelled with which core it clears and which it meets, so `clears K(a) stock, clears K exact, meets K'` is a column only the polygon core reaches, and `clears K(a) stock, meets K exact` is one the exact pin core alone reaches - the slop A132's attribution found.
* **Panel 2** is the near-packing, and its names are the names to label from.
* **Panel 3** is the hypothesis alone: the three cores of H captioned with `a_stock / a_exact / area K'`, the pin-clipped centre box per tilt sub-bin, the A118 LANE<=1 corner cells, and the measured pockets.
* **The line under each page** names the corners whose lane count is 1 (a second meeter is what a two-meeter cover needs) and the pockets between K'(B) and the nearest pin narrower than 1 - nothing fits there, so any square the LP puts in that region is a column the geometry forbids.

Lane counts are **A118's stored AXIS-CORE verdicts** (K(a), not K'). A141's K' lane run had not landed when these pages were drawn, so a corner marked UNDECIDED here may still become LANE<=1 under K' - that is exactly the s3_far effect the PI read on A140's page.

**Geometry check** (`code/verify142.py`, a second implementation using edge-crossing and strict point-in-polygon, no separating axis anywhere): 326 red-dashed columns re-verified over 98102 poses, 0 failures; 283 non-flagged columns each shown disjoint at some pose of every box, 0 failures; 100 exact pin cores contained in their pin square at every pose, 0 failures; 800 K'(B) vertices contained at every pose, 0 failures; 160 clipped rects inside the original box, 0 failures.

Files: 20 A57 pages + 0 A60 pages, `review_a57v3.csv` (the review sheet, PI columns empty), and the machine-readable record in `attempts/A142-a57-review-gallery/results/`.
