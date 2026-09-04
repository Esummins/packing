# A87 exchange87 -- corner exchange at fixed side

PI question: can every K0-BLOCKED packing be converted to a k >= 1 packing at the SAME side by a non-rigid exchange?

## Headline

- (packing, corner) cases run: **33**
- exchanges that SUCCEED at the same side (unit square fits and is verified exactly): **21**
- slot blocked by a third square: 0
- CANARY (Trump TL, s-hat = 3.877083590022814): fit_failed, largest inscribable square side found = **0.982345553** (< 1, as required)

## Per packing: does SOME corner work?

| packing | side m | corners tried | corners where the exchange succeeds | verdict |
|---|---|---|---|---|
| record_s0115 | 3.985483725 | 4 | TR, TL | CONVERTIBLE |
| polish12_s0380 | 4.000000118 | 4 | BL, BR | CONVERTIBLE |
| polish15_s0076 | 4.000004058 | 4 | BL, BR | CONVERTIBLE |
| polish21_s0380 | 4.000007451 | 4 | BL, BR, TR, TL | CONVERTIBLE |
| polish24_s0259 | 4.000011860 | 4 | BR, TR, TL | CONVERTIBLE |
| TRUMP_canary | 3.877083590 | 1 | - | no corner works |
| anchored0_p140 | 4.107107415 | 4 | BL, TR | CONVERTIBLE |
| anchored1_p094 | 4.083735460 | 4 | BL, TR, TL | CONVERTIBLE |
| anchored2_p094 | 4.083735886 | 4 | BL, TR, TL | CONVERTIBLE |

## Per (packing, corner)

| packing | side m | corner | intruders removed | slot | relax moves | moved squares | best stage | largest inscribable side | exchange |
|---|---|---|---|---|---|---|---|---|---|
| record_s0115 | 3.985483725 | BL | [1, 0] | ok | 10 | 6,7,8 | before_relax | 0.985272815 | fail |
| record_s0115 | 3.985483725 | BR | [2, 3] | ok | 1 | 4 | before_relax | 0.985483622 | fail |
| record_s0115 | 3.985483725 | TR | [7, 6] | ok | 1 | 6 | before_relax (refined) | 1.000000016 | SUCCESS |
| record_s0115 | 3.985483725 | TL | [5, 4] | ok | 0 | - | before_relax (refined) | 1.000174100 | SUCCESS |
| polish12_s0380 | 4.000000118 | BL | [0, 1] | ok | 1 | 7 | before_relax (refined) | 1.000000019 | SUCCESS |
| polish12_s0380 | 4.000000118 | BR | [3, 2] | ok | 12 | 6,7,8 | before_relax (refined) | 1.000000056 | SUCCESS |
| polish12_s0380 | 4.000000118 | TR | [6, 7] | ok | 0 | - | before_relax (refined) | 0.999648474 | fail |
| polish12_s0380 | 4.000000118 | TL | [5, 4] | ok | 0 | - | before_relax (refined) | 0.999999940 | fail |
| polish15_s0076 | 4.000004058 | BL | [0, 1] | ok | 0 | - | before_relax (refined) | 1.000296575 | SUCCESS |
| polish15_s0076 | 4.000004058 | BR | [2, 3] | ok | 11 | 0,1,2,4,5,6,7,8 | before_relax (refined) | 1.000001844 | SUCCESS |
| polish15_s0076 | 4.000004058 | TR | [6, 7] | ok | 5 | 4,8 | before_relax (refined) | 0.999943858 | fail |
| polish15_s0076 | 4.000004058 | TL | [4, 5] | ok | 12 | 0,1,3,4,5,6,7,8 | before_relax | 0.998910367 | fail |
| polish21_s0380 | 4.000007451 | BL | [0, 1] | ok | 6 | 1,7 | before_relax (refined) | 1.000006130 | SUCCESS |
| polish21_s0380 | 4.000007451 | BR | [3, 2] | ok | 5 | 6,7,8 | before_relax (refined) | 1.000002317 | SUCCESS |
| polish21_s0380 | 4.000007451 | TR | [6, 7] | ok | 0 | - | before_relax (refined) | 1.000358477 | SUCCESS |
| polish21_s0380 | 4.000007451 | TL | [4, 5] | ok | 8 | 1,2,3,6,7,8 | before_relax (refined) | 1.000000046 | SUCCESS |
| polish24_s0259 | 4.000011860 | BL | [0, 1] | ok | 2 | 6 | before_relax (refined) | 0.999751623 | fail |
| polish24_s0259 | 4.000011860 | BR | [3, 2] | ok | 12 | 0,1,6,7,8 | before_relax (refined) | 1.000055519 | SUCCESS |
| polish24_s0259 | 4.000011860 | TR | [7, 6] | ok | 0 | - | before_relax | 1.000005448 | SUCCESS |
| polish24_s0259 | 4.000011860 | TL | [4, 5] | ok | 0 | - | before_relax (refined) | 1.000004044 | SUCCESS |
| TRUMP_canary | 3.877083590 | TL | [6, 4] | ok | 0 | - | before_relax | 0.982345553 | fail |
| anchored0_p140 | 4.107107415 | BL | [0, 1] | ok | 0 | - | before_relax | 1.106962173 | SUCCESS |
| anchored0_p140 | 4.107107415 | BR | [3, 2] | ok | 8 | 0,1,5,6 | before_relax | 0.999923658 | fail |
| anchored0_p140 | 4.107107415 | TR | [6, 7] | ok | 0 | - | before_relax (refined) | 1.050430215 | SUCCESS |
| anchored0_p140 | 4.107107415 | TL | [4, 5] | ok | 0 | - | before_relax (refined) | 0.991169250 | fail |
| anchored1_p094 | 4.083735460 | BL | [0, 1] | ok | 0 | - | before_relax (refined) | 1.083596377 | SUCCESS |
| anchored1_p094 | 4.083735460 | BR | [2, 3] | ok | 0 | - | before_relax | 0.941370666 | fail |
| anchored1_p094 | 4.083735460 | TR | [6, 7] | ok | 0 | - | before_relax (refined) | 1.058818330 | SUCCESS |
| anchored1_p094 | 4.083735460 | TL | [5, 4] | ok | 0 | - | before_relax (refined) | 1.000037680 | SUCCESS |
| anchored2_p094 | 4.083735886 | BL | [0, 1] | ok | 0 | - | before_relax (refined) | 1.083595926 | SUCCESS |
| anchored2_p094 | 4.083735886 | BR | [2, 3] | ok | 0 | - | before_relax | 0.941370133 | fail |
| anchored2_p094 | 4.083735886 | TR | [6, 7] | ok | 0 | - | before_relax (refined) | 1.058818282 | SUCCESS |
| anchored2_p094 | 4.083735886 | TL | [5, 4] | ok | 0 | - | before_relax (refined) | 1.000037849 | SUCCESS |

## Stage detail (lambda_max = largest square side that fits)

| packing | corner | before relax | after relax | best on trajectory |
|---|---|---|---|---|
| record_s0115 | BL | 0.985272815 | 0.909030349 | 0.919882961 |
| record_s0115 | BR | 0.985483622 | 0.940843839 | - |
| record_s0115 | TR | 0.999999854 | 0.999999854 | - |
| record_s0115 | TL | 1.000172597 | - | - |
| polish12_s0380 | BL | 0.997821065 | 0.997821065 | - |
| polish12_s0380 | BR | 0.995824293 | 0.999647573 | 0.999647573 |
| polish12_s0380 | TR | 0.999648344 | - | - |
| polish12_s0380 | TL | 0.999999385 | - | - |
| polish15_s0076 | BL | 1.000280877 | - | - |
| polish15_s0076 | BR | 0.997830781 | 0.975019893 | 0.997825360 |
| polish15_s0076 | TR | 0.999943324 | 0.999943324 | 0.999943324 |
| polish15_s0076 | TL | 0.998910367 | 0.975919811 | 0.998910367 |
| polish21_s0380 | BL | 0.997777130 | 0.995882640 | 0.997777130 |
| polish21_s0380 | BR | 0.996471939 | 0.996390066 | 0.996471939 |
| polish21_s0380 | TR | 1.000356124 | - | - |
| polish21_s0380 | TL | 0.999997360 | 0.998194729 | 0.998194729 |
| polish24_s0259 | BL | 0.999279925 | 0.999279925 | 0.999279925 |
| polish24_s0259 | BR | 0.999601647 | 0.942639234 | 0.942639234 |
| polish24_s0259 | TR | 1.000005448 | - | - |
| polish24_s0259 | TL | 1.000001007 | - | - |
| TRUMP_canary | TL | 0.982345553 | - | - |
| anchored0_p140 | BL | 1.106962173 | - | - |
| anchored0_p140 | BR | 0.999923658 | 0.924178153 | 0.940588148 |
| anchored0_p140 | TR | 1.050429794 | - | - |
| anchored0_p140 | TL | 0.991167930 | - | - |
| anchored1_p094 | BL | 1.083593495 | - | - |
| anchored1_p094 | BR | 0.941370666 | - | - |
| anchored1_p094 | TR | 1.058818050 | - | - |
| anchored1_p094 | TL | 1.000037175 | - | - |
| anchored2_p094 | BL | 1.083593495 | - | - |
| anchored2_p094 | BR | 0.941370133 | - | - |
| anchored2_p094 | TR | 1.058815278 | - | - |
| anchored2_p094 | TL | 1.000037672 | - | - |

## Verified successful placements

- **record_s0115 / TR**: unit square at theta = 6.828e-10 rad, centre (3.485199883291, 2.485483718617); interval SAT min gap to the 10 squares >= 7.990e-09, container clearance >= 2.838e-04; the 10-square host config certifies min pair gap 2.680e-10, min clearance 0.000e+00 (disjoint True, contained True)
- **record_s0115 / TL**: unit square at theta = 1.571e+00 rad, centre (1.503810885026, 3.485396676845); interval SAT min gap to the 10 squares >= 8.705e-05, container clearance >= 8.705e-05; the 10-square host config certifies min pair gap 2.680e-10, min clearance 0.000e+00 (disjoint True, contained True)
- **polish12_s0380 / BL**: unit square at theta = -1.332e-07 rad, centre (0.500002784729, 1.500000076294); interval SAT min gap to the 10 squares >= 9.715e-09, container clearance >= 2.718e-06; the 10-square host config certifies min pair gap 1.000e-11, min clearance 0.000e+00 (disjoint True, contained True)
- **polish12_s0380 / BR**: unit square at theta = -1.100e-07 rad, centre (3.500000036593, 1.500000083059); interval SAT min gap to the 10 squares >= 2.807e-08, container clearance >= 2.807e-08; the 10-square host config certifies min pair gap 1.000e-11, min clearance 0.000e+00 (disjoint True, contained True)
- **polish15_s0076 / BL**: unit square at theta = 2.700e-05 rad, centre (0.511856074830, 1.500161790040); interval SAT min gap to the 10 squares >= 1.483e-04, container clearance >= 1.184e-02; the 10-square host config certifies min pair gap 1.000e-11, min clearance 0.000e+00 (disjoint True, contained True)
- **polish15_s0076 / BR**: unit square at theta = 0.000e+00 rad, centre (2.500003138371, 0.500000922047); interval SAT min gap to the 10 squares >= 9.221e-07, container clearance >= 9.220e-07; the 10-square host config certifies min pair gap 1.370e-11, min clearance 0.000e+00 (disjoint True, contained True)
- **polish21_s0380 / BL**: unit square at theta = -8.522e-06 rad, centre (0.500195312500, 1.500007324219); interval SAT min gap to the 10 squares >= 3.065e-06, container clearance >= 1.911e-04; the 10-square host config certifies min pair gap 1.002e-11, min clearance 0.000e+00 (disjoint True, contained True)
- **polish21_s0380 / BR**: unit square at theta = -9.015e-07 rad, centre (3.500005844097, 1.500001609398); interval SAT min gap to the 10 squares >= 1.159e-06, container clearance >= 1.159e-06; the 10-square host config certifies min pair gap 1.000e-11, min clearance 0.000e+00 (disjoint True, contained True)
- **polish21_s0380 / TR**: unit square at theta = -4.302e-05 rad, centre (2.499806695624, 3.497942817384); interval SAT min gap to the 10 squares >= 1.792e-04, container clearance >= 2.043e-03; the 10-square host config certifies min pair gap 1.000e-11, min clearance 0.000e+00 (disjoint True, contained True)
- **polish21_s0380 / TL**: unit square at theta = 2.008e-12 rad, centre (0.500000027328, 2.500007430245); interval SAT min gap to the 10 squares >= 2.325e-08, container clearance >= 2.733e-08; the 10-square host config certifies min pair gap 1.002e-11, min clearance 0.000e+00 (disjoint True, contained True)
- **polish24_s0259 / BR**: unit square at theta = 1.559e+00 rad, centre (3.494120502084, 1.505891359746); interval SAT min gap to the 10 squares >= 2.808e-05, container clearance >= 2.808e-05; the 10-square host config certifies min pair gap 5.837e-10, min clearance 0.000e+00 (disjoint True, contained True)
- **polish24_s0259 / TR**: unit square at theta = 6.818e-05 rad, centre (2.499980468750, 3.458437500000); interval SAT min gap to the 10 squares >= 1.379e-07, container clearance >= 4.154e-02; the 10-square host config certifies min pair gap 5.837e-10, min clearance 0.000e+00 (disjoint True, contained True)
- **polish24_s0259 / TL**: unit square at theta = -1.704e-05 rad, centre (1.500012207031, 3.499890136719); interval SAT min gap to the 10 squares >= 2.022e-06, container clearance >= 1.132e-04; the 10-square host config certifies min pair gap 5.837e-10, min clearance 0.000e+00 (disjoint True, contained True)
- **anchored0_p140 / BL**: unit square at theta = 3.409e-05 rad, centre (1.553496093750, 0.554238281250); interval SAT min gap to the 10 squares >= 5.348e-02, container clearance >= 5.422e-02; the 10-square host config certifies min pair gap 4.725e-10, min clearance 0.000e+00 (disjoint True, contained True)
- **anchored0_p140 / TR**: unit square at theta = 1.571e+00 rad, centre (3.581892308265, 2.581892308265); interval SAT min gap to the 10 squares >= 2.522e-02, container clearance >= 2.522e-02; the 10-square host config certifies min pair gap 4.725e-10, min clearance 0.000e+00 (disjoint True, contained True)
- **anchored1_p094 / BL**: unit square at theta = -1.704e-05 rad, centre (0.805014648438, 1.541801757813); interval SAT min gap to the 10 squares >= 4.180e-02, container clearance >= 3.050e-01; the 10-square host config certifies min pair gap 4.038e-09, min clearance 0.000e+00 (disjoint True, contained True)
- **anchored1_p094 / TR**: unit square at theta = 0.000e+00 rad, centre (2.554326296982, 3.554326296982); interval SAT min gap to the 10 squares >= 2.941e-02, container clearance >= 2.941e-02; the 10-square host config certifies min pair gap 3.990e-09, min clearance 0.000e+00 (disjoint True, contained True)
- **anchored1_p094 / TL**: unit square at theta = 0.000e+00 rad, centre (0.500022009630, 2.583716621803); interval SAT min gap to the 10 squares >= 1.884e-05, container clearance >= 2.201e-05; the 10-square host config certifies min pair gap 3.990e-09, min clearance 0.000e+00 (disjoint True, contained True)
- **anchored2_p094 / BL**: unit square at theta = -1.704e-05 rad, centre (0.805014648438, 1.541801757813); interval SAT min gap to the 10 squares >= 4.180e-02, container clearance >= 3.050e-01; the 10-square host config certifies min pair gap 2.769e-10, min clearance 0.000e+00 (disjoint True, contained True)
- **anchored2_p094 / TR**: unit square at theta = 0.000e+00 rad, centre (2.554326746493, 3.554326746493); interval SAT min gap to the 10 squares >= 2.941e-02, container clearance >= 2.941e-02; the 10-square host config certifies min pair gap 2.769e-10, min clearance 0.000e+00 (disjoint True, contained True)
- **anchored2_p094 / TL**: unit square at theta = 6.939e-18 rad, centre (0.500022961780, 2.583716962631); interval SAT min gap to the 10 squares >= 1.892e-05, container clearance >= 2.296e-05; the 10-square host config certifies min pair gap 2.769e-10, min clearance 0.000e+00 (disjoint True, contained True)

## Findings

1. **The exchange succeeds on every K0-BLOCKED packing tested.** Each of the 8 K0-BLOCKED configurations (the 5 exact ones of dataset (a) and the 3 anchored ones of dataset (b)) has at least one corner at which removing the two intruders, inserting the corner slot square, and refitting an 11th unit square works at the SAME side -- 21 of the 33 (packing, corner) cases.
2. **No corner was ever blocked by a third square.** In all 33 cases the two deepest intruders were the ONLY squares meeting the open unit slot (every packing had exactly n_block = 2 per corner), and the slot square was interval-SAT disjoint from the remaining 9 with a strictly positive gap.
3. **The relaxation is not what makes it work.** All 21 successes are already realised by the PRE-relaxation configuration: removing A and B and dropping in the slot square by itself leaves room for the 11th square.  Of the 14 cases where the greedy void-maximising relaxation moved anything (94 moves in total), it improved the largest inscribable square in 1, made it WORSE in 6 and left it unchanged in 7.  Maximising the void AREA spreads the free region into slivers; it is not the same objective as maximising the inscribed square.
4. **Canary behaves.** Trump at s-hat is rigid in the strong sense that NO single remaining square has any feasible rigid motion after the TL intruders sq6/sq4 are removed (0 moves in the relaxation), and the largest square that fits in the freed region is 0.982345553 < 1.  No second packing at s-hat is produced.
5. The margins of the successes vary hugely: the anchored candidates at side ~4.08-4.11 clear the unit square by 5-30% (lambda up to 1.107), whereas several successes at side ~4.0000001 clear it only in the 8th decimal (lambda - 1 ~ 1e-8), and 7 of the 12 failures also sit within 1e-3 of 1.  The near ties were re-decided by the high-resolution pass (results/exchange87.refine.json), not by the 1 deg / 1/200 scan.

## Method notes

- Intruders at a corner = squares with A90 corner depth > 1e-9 (they meet the OPEN unit slot); the two DEEPEST are removed.
- Slot square = exact axis-aligned unit square in the corner; disjointness from the remaining 9 is checked by interval SAT on the exact rational configuration.
- Relaxation maximises V = area of the largest connected free component (1/400 raster) meeting the zone vacated by A and B, by greedy single-square rigid motions (16 translation directions with step halving; +/- rotations about the centre and about contact points) that do not degrade any of the moved square's own constraint rows.
- Fit test: for each tilt (1 deg grid) and each centre on a 1/200 grid the code evaluates in closed form the LARGEST lambda whose lambda-square at that pose is interior-disjoint from all 10 squares and inside the container (lambda_j = max over the 4 SAT axes of (|n.(p-c_j)|-r_j)/r_S), then refines locally.  Success iff lambda >= 1; the reported shortfall is max lambda.
- Because a larger void is not the same thing as a larger inscribable square, the fit test is run on the pre-relaxation configuration, on the post-relaxation configuration, and on the best point of the relaxation trajectory; the best of the three is reported.
- Every case within 1e-2 of lambda = 1 was re-decided at high resolution (exchange87_refine.py: per-tilt best centre, then a pattern search in (cx, cy, theta) down to ~1e-15 steps) on the pre-relaxation configuration, which is reproducible exactly from (packing, corner).  That pass turned 9 apparent failures into verified successes and left the rest below 1.

## Data provenance / caveats

- Dataset (a): results/k0dir87.json record_K0_BLOCKED_packing (s0115, 3.98548) plus the 4 rows of results/k0dir87.polish.jsonl with exact_K0_BLOCKED true and non-null z_polished (indices 12, 15, 21, 24).  All exact rationals.
- Dataset (b): the ANCHORED candidates are NOT in results/d2front87.jsonl -- that file stores only per-node scalars (cap/s/side/d1/d2/n_block/score/steps) and carries no configuration vector.  They are in results/d2front87.json under own_side_anchored.candidates and per_cap_anchored[*].candidates, as EXACT rationals with their own certificate; 3 distinct ones exist (p140 at 4.10711, p094 at 4.08374 and 4.08374), all with K0_BLOCKED_certified true and n_block [2,2,2,2].  They were used as given, and re-verified here (disjoint_certified true).
- The relaxation accepts a single-square rigid motion only if it does not degrade any of that square's own rows below min(current value, 1e-10), with a 1e-13 float tolerance on rows that are already contacts.  Cumulative degradation over a run is therefore bounded by ~1e-12, well under the input packings' own certified gaps; but the exactly-verified claims in this report all rest on PRE-relaxation configurations, whose 10 squares carry the input packing's own certificate plus an exactly rational slot square.
- The container rows of an exactly axis-aligned rational square (the slot square) are evaluated in exact rational arithmetic; routing them through interval mpf(num)/mpf(den) rounds the two sides independently and reports a spurious -1e-41 clearance for a square that is flush by construction.
