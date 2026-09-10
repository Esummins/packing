# A187 — the basin containment map of the alive residue

Generated 2026-09-09T20:23:04 by `attempts/A187-basin-map/code/basin187.py` + `report187.py`; data `results/basin_map187.json`; map `docs/residue_map/basin_map.svg`.  Read-only on every other attempt.

## 0. The headline

| | pages | of 63 |
|---|---|---|
| ALIVE gallery pages (52 `a57v4` + 11 `k0v4`) | 63 | 100 % |
| in a class frame that has **any** certified basin | 52 | 83 % |
| whose **own** nearest minimiser has a basin **in that frame** | 7 | 11 % |
| whose conditioned box is **inside** a certified basin box | 8 | 13 % |
| within a **2x growth** of a certified basin box | 32 | 51 % |
| whose A107 representative configuration is inside a certified N (A116/A151/A160/A163 consumer) | 7 | 11 % |

**[M] The residue is not basin-shaped.**  All 52 A57/A60 pages live in a frame (`k5_11`, `k5_16`, `trump5`) that owns the S02 pinwheel basin, but only 7 of the 63 pages minimise to a configuration that has a certified basin in their own frame at all — the other 56 cluster on a minimiser with no local certificate there.  Where a page's box does fit a certified box it is usually the WRONG minimiser's basin (a coincidence of position, not of family), so the honest measure of how much of the residue is basin-shaped is the consumer column: **7 of 63 pages = 11 %**.  All seven sit inside the S02 pinwheel basin and all seven are `k5_11` / `k5_16` pages; only three of them are S02 pages themselves (`k5_16` Y0054, Y0380, Y1110), the other four minimise to S10, S36 and S01 and land in S02's basin anyway.

## 1. Pages ranked by the growth the nearest certified basin would need

`growth` = max over (centre x, centre y, tilt) and over the two SIDES of the minimiser's own pose of (the reach the basin box would need) / (the reach it has) -- per side, because the certified windows are asymmetric -- minimised over every certified box of every entry in the page's frame.  `growth <= 1` = already contained.  `gap` = how far the page's box sticks out, per coordinate.  `own?` = is the matched basin the basin of the page's OWN nearest packing.  `cons` = the A116 consumer verdict on the page's A107 representative configuration.  `sup` = fraction of LP support weight inside the matched basin's boxes.

| # | page | class | family | s\* | basin matched | growth | gap x | gap y | gap tilt (deg) | own? | cons | sup |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `c0_Y0171` | `trump5_j0` | `S01` | 4.000000 | `S02` / `trump5` (S02_trump5_A163slice_a151B_f2+00.0…) | **0.29** | 0.000 | 0.000 | 0.0 | no | no | 0.40 |
| 2 | `c0_Y0076` | `trump5_j0` | `S02` | 3.886746 | `S02` / `trump5` (S02_trump5_A163slice_a151B_f2+00.0…) | **0.41** | 0.000 | 0.000 | 0.0 | yes | no | 0.20 |
| 3 | `k5_11_interior_Y0738` | `k5_11` | `S02` | 3.886746 | `S02` / `k5_11` (S02_k5_11_A160slice_a151B_f2-20.0_…) | **0.51** | 0.000 | 0.000 | 0.0 | yes | no | 0.29 |
| 4 | `c0_Y0258` | `trump5_j0` | `S01` | 4.000000 | `S02` / `trump5` (S02_trump5_A163slice_a151B_f2+00.0…) | **0.83** | 0.000 | 0.000 | 0.0 | no | no | 0.20 |
| 5 | `c0_Y0169` | `trump5_j0` | `S38` | 3.928915 | `S02` / `trump5` (S02_trump5_A163slice_a151B_f2+00.0…) | **0.85** | 0.000 | 0.000 | 0.0 | no | no | 0.20 |
| 6 | `c0_Y0257` | `trump5_j0` | `S08` | 3.914214 | `S02` / `trump5` (S02_trump5_A163slice_a151B_f2+00.0…) | **0.85** | 0.000 | 0.000 | 0.0 | no | no | 0.30 |
| 7 | `k5_11_interior_Y0662` | `k5_11` | `none` | 3.877084 | `S02` / `k5_11` (S02_k5_11_A160chain_BOTH_base_r0.2…) | **0.97** | 0.000 | 0.000 | 0.0 | no | no | 0.00 |
| 8 | `k5_16_interior_Y1056` | `k5_16` | `S08` | 3.914214 | `S02` / `k5_16` (S02_k5_16_A163slice_a151B_f2-20.0_…) | **0.99** | 0.000 | 0.000 | 0.0 | no | no | 0.40 |
| 9 | `c0_Y0175` | `trump5_j0` | `S01` | 4.000000 | `S02` / `trump5` (S02_trump5_A163slice_a151B_f2+00.0…) | 1.04 | 0.000 | 0.000 | 1.6 | no | no | 0.40 |
| 10 | `k5_16_interior_Y0500` | `k5_16` | `S01` | 4.000000 | `S02` / `k5_16` (S02_k5_16_A163chain_BOTH_base_r0.2…) | 1.17 | 0.000 | 0.033 | 0.0 | no | no | 0.01 |
| 11 | `slack0.02_c0_Y0272` | `trump5_j0` | `S01` | 4.000000 | `S02` / `trump5` (S02_trump5_A163slice_a151B_f2+00.0…) | 1.21 | 0.000 | 0.000 | 8.4 | no | no | 0.00 |
| 12 | `k5_11_interior_Y1104` | `k5_11` | `S10` | 3.902674 | `S02` / `k5_11` (S02_k5_11_A160chain_BOTH_base_r0.2…) | 1.27 | 0.000 | 0.000 | 2.7 | no | YES | 0.00 |
| 13 | `k5_16_interior_Y1117` | `k5_16` | `S01` | 4.000000 | `S02` / `k5_16` (S02_k5_16_A163chain_BOTH_base_r0.2…) | 1.27 | 0.034 | 0.000 | 2.7 | no | YES | 0.35 |
| 14 | `k5_11_interior_Y1110` | `k5_11` | `S36` | 3.924003 | `S02` / `k5_11` (S02_k5_11_r0.20_rho10…) | 1.28 | 0.057 | 0.000 | 0.0 | no | YES | 0.40 |
| 15 | `k5_11_interior_Y0130` | `k5_11` | `S01` | 4.000000 | `S02` / `k5_11` (S02_k5_11_A160slice_a151B_f2+00.0_…) | 1.28 | 0.057 | 0.000 | 0.0 | no | no | 0.18 |
| 16 | `k5_11_interior_Y0672` | `k5_11` | `S53` | 4.000261 | `S02` / `k5_11` (S02_k5_11_A160slice_a151B_f2+00.0_…) | 1.28 | 0.057 | 0.000 | 2.7 | no | no | 0.19 |
| 17 | `k5_16_interior_Y0099` | `k5_16` | `S03` | 3.942809 | `S02` / `k5_16` (S02_k5_16_A163slice_f1base_f2-20.0…) | 1.28 | 0.057 | 0.030 | 0.0 | no | no | 0.00 |
| 18 | `k5_16_interior_Y1110` | `k5_16` | `S02` | 3.886746 | `S02` / `k5_16` (S02_k5_16_A163slice_f1base_f2-20.0…) | 1.28 | 0.057 | 0.000 | 0.0 | yes | YES | 0.40 |
| 19 | `c0_Y0787` | `trump5_j0` | `S01` | 4.000000 | `S07` / `trump5` (S07_trump5_r0.20_rho10…) | 1.29 | 0.019 | 0.058 | 0.5 | no | no | 0.00 |
| 20 | `c0_Y0959` | `trump5_j0` | `S01` | 4.000000 | `S07` / `trump5` (S07_trump5_r0.10_rho40…) | 1.33 | 0.000 | 0.033 | 5.0 | no | no | 0.20 |
| 21 | `c0_Y0255` | `trump5_j0` | `S03` | 3.942809 | `S02` / `trump5` (S02_trump5_A163slice_a151B_f2+00.0…) | 1.39 | 0.000 | 0.098 | 1.6 | no | no | 0.20 |
| 22 | `k5_11_interior_Y0308` | `k5_11` | `S01` | 4.000000 | `S02` / `k5_11` (S02_k5_11_A160chain_BOTH_base_r0.2…) | 1.39 | 0.000 | 0.000 | 3.9 | no | no | 0.00 |
| 23 | `k5_16_interior_Y0249` | `k5_16` | `S03` | 3.942809 | `S02` / `k5_16` (S02_k5_16_A163chain_BOTH_base_r0.2…) | 1.39 | 0.000 | 0.033 | 3.9 | no | no | 0.00 |
| 24 | `c0_Y1033` | `trump5_j0` | `S01` | 4.000000 | `S02` / `trump5` (S02_trump5_A163slice_f1base_f2+20.…) | 1.42 | 0.000 | 0.000 | 4.2 | no | no | 0.20 |
| 25 | `k5_11_interior_Y0985` | `k5_11` | `S01` | 4.000000 | `S02` / `k5_11` (S02_k5_11_A160slice_a151B_f2+00.0_…) | 1.42 | 0.000 | 0.000 | 4.2 | no | no | 0.23 |
| 26 | `f1_L10_0003` | `trump5_j0` | `S07` | 3.885618 | `S07` / `trump5` (S07_trump5_r0.10_rho40…) | 1.61 | 0.000 | 0.000 | 2.1 | yes | no | 0.00 |
| 27 | `c0_Y0952` | `trump5_j0` | `S01` | 4.000000 | `S02` / `trump5` (S02_trump5_A163slice_f1base_f2-20.…) | 1.65 | 0.057 | 0.129 | 5.8 | no | no | 0.00 |
| 28 | `k5_11_interior_Y0147` | `k5_11` | `S01` | 4.000000 | `S02` / `k5_11` (S02_k5_11_A160slice_a151B_f2+00.0_…) | 1.65 | 0.057 | 0.129 | 0.0 | no | no | 0.00 |
| 29 | `k5_16_interior_Y0436` | `k5_16` | `none` | 3.877084 | `S02` / `k5_16` (S02_k5_16_A163slice_f1base_f2-20.0…) | 1.85 | 0.057 | 0.170 | 5.8 | no | no | 0.00 |
| 30 | `k5_16_interior_Y0719` | `k5_16` | `S01` | 4.000000 | `S02` / `k5_16` (S02_k5_16_A163slice_f1base_f2-20.0…) | 1.85 | 0.057 | 0.170 | 5.3 | no | no | 0.40 |
| 31 | `k5_16_interior_Y0881` | `k5_16` | `S01` | 4.000000 | `S02` / `k5_16` (S02_k5_16_A163slice_f1base_f2-20.0…) | 1.85 | 0.057 | 0.170 | 0.0 | no | no | 0.20 |
| 32 | `c0_Y0788` | `trump5_j0` | `S03` | 3.942809 | `S07` / `trump5` (S07_trump5_r0.20_rho10…) | 1.90 | 0.019 | 0.058 | 9.0 | no | no | 0.00 |
| 33 | `k5_16_interior_Y0325` | `k5_16` | `S01` | 4.000000 | `S02` / `k5_16` (S02_k5_16_A163slice_f1base_f2-20.0…) | 2.55 | 0.057 | 0.309 | 5.8 | no | no | 0.00 |
| 34 | `k5_16_interior_Y0491` | `k5_16` | `S01` | 4.000000 | `S02` / `k5_16` (S02_k5_16_A163chain_RXY_probe_-10.…) | 2.93 | 0.580 | 0.000 | 16.0 | no | no | 0.00 |
| 35 | `k5_16_interior_Y0565` | `k5_16` | `S01` | 4.000000 | `S02` / `k5_16` (S02_k5_16_A163chain_BOTH_base_r0.2…) | 2.94 | 0.034 | 0.389 | 4.2 | no | no | 0.00 |
| 36 | `k5_16_interior_Y0027` | `k5_16` | `S01` | 4.000000 | `S02` / `k5_16` (S02_k5_16_A163slice_a151B_f2-20.0_…) | 3.09 | 0.835 | 0.378 | 1.6 | no | no | 0.20 |
| 37 | `c0_Y0695` | `trump5_j0` | `S02` | 3.886746 | `S07` / `trump5` (S07_trump5_r0.10_rho40…) | 3.59 | 0.259 | 0.158 | 5.0 | no | no | 0.00 |
| 38 | `c0_Y0223` | `trump5_j0` | `S03` | 3.942809 | `S02` / `trump5` (S02_trump5_A163slice_a151B_f2+00.0…) | 3.63 | 0.000 | 0.657 | 1.6 | no | no | 0.00 |
| 39 | `k5_11_interior_Y0202` | `k5_11` | `S05` | 3.912232 | `S02` / `k5_11` (S02_k5_11_A160slice_a151B_f2-20.0_…) | 3.63 | 0.416 | 0.657 | 0.0 | no | no | 0.60 |
| 40 | `k5_16_interior_Y0054` | `k5_16` | `S02` | 3.886746 | `S02` / `k5_16` (S02_k5_16_A163slice_a151B_f2-20.0_…) | 3.63 | 0.416 | 0.657 | 1.6 | yes | YES | 0.60 |
| 41 | `k5_16_interior_Y0230` | `k5_16` | `S01` | 4.000000 | `S02` / `k5_16` (S02_k5_16_A163slice_a151B_f2-20.0_…) | 3.63 | 0.276 | 0.657 | 0.0 | no | YES | 0.60 |
| 42 | `k5_16_interior_Y0380` | `k5_16` | `S02` | 3.886746 | `S02` / `k5_16` (S02_k5_16_A163slice_a151B_f2-20.0_…) | 3.63 | 0.416 | 0.657 | 0.0 | yes | YES | 0.60 |
| 43 | `k5_16_interior_Y0839` | `k5_16` | `S01` | 4.000000 | `S02` / `k5_16` (S02_k5_16_A163slice_a151B_f2-20.0_…) | 3.63 | 0.975 | 0.657 | 0.0 | no | no | 0.20 |
| 44 | `k5_16_interior_Y1022` | `k5_16` | `S03` | 3.942809 | `S02` / `k5_16` (S02_k5_16_A163chain_RXY_probe_-10.…) | 3.69 | 0.719 | 0.000 | 26.9 | no | no | 0.00 |
| 45 | `k5_16_interior_Y0660` | `k5_16` | `S03` | 3.942809 | `S02` / `k5_16` (S02_k5_16_A163chain_RXY_probe_-10.…) | 3.86 | 0.859 | 0.000 | 4.3 | no | no | 0.20 |
| 46 | `k5_16_interior_Y0991` | `k5_16` | `S03` | 3.942809 | `S02` / `k5_16` (S02_k5_16_A163chain_RXY_probe_-10.…) | 3.86 | 0.859 | 0.000 | 18.1 | no | no | 0.00 |
| 47 | `c0_Y0215` | `trump5_j0` | `S11` | 3.976620 | `S02` / `trump5` (S02_trump5_A163slice_a151B_f2+00.0…) | 4.19 | 0.000 | 0.797 | 1.6 | no | no | 0.25 |
| 48 | `k5_16_interior_Y0044` | `k5_16` | `S01` | 4.000000 | `S02` / `k5_16` (S02_k5_16_A163slice_a151B_f2-20.0_…) | 4.19 | 0.136 | 0.797 | 1.6 | no | no | 0.34 |
| 49 | `k5_16_interior_Y0191` | `k5_16` | `S03` | 3.942809 | `S02` / `k5_16` (S02_k5_16_A163slice_a151B_f2-20.0_…) | 4.19 | 0.136 | 0.797 | 0.0 | no | no | 0.40 |
| 50 | `k5_16_interior_Y0402` | `k5_16` | `S03` | 3.942809 | `S02` / `k5_16` (S02_k5_16_A163slice_a151B_f2-20.0_…) | 4.19 | 0.136 | 0.797 | 8.4 | no | no | 0.40 |
| 51 | `k5_16_interior_Y0460` | `k5_16` | `none` | 3.877084 | `S02` / `k5_16` (S02_k5_16_A163slice_a151B_f2-20.0_…) | 4.19 | 0.416 | 0.797 | 8.4 | no | no | 0.33 |
| 52 | `k5_16_interior_Y0865` | `k5_16` | `S03` | 3.942809 | `S02` / `k5_16` (S02_k5_16_A163slice_a151B_f2-20.0_…) | 4.19 | 0.556 | 0.797 | 0.0 | no | no | 0.20 |
| 53 | `l1_071` | `k0_00` | `K01` | 4.000000 | — none in frame | — | 0.000 | 0.000 | 0.0 | no | no | — |
| 54 | `l1_104` | `k0_00` | `K04` | 3.914214 | — none in frame | — | 0.000 | 0.000 | 0.0 | no | no | — |
| 55 | `l1_124` | `k0_00` | `none` | 3.942810 | — none in frame | — | 0.000 | 0.000 | 0.0 | no | no | — |
| 56 | `l1_148` | `k0_00` | `K01` | 4.000000 | — none in frame | — | 0.000 | 0.000 | 0.0 | no | no | — |
| 57 | `l1_153` | `k0_00` | `none` | 3.877084 | — none in frame | — | 0.000 | 0.000 | 0.0 | no | no | — |
| 58 | `l1_158` | `k0_00` | `none` | 3.902674 | — none in frame | — | 0.000 | 0.000 | 0.0 | no | no | — |
| 59 | `l1_159` | `k0_00` | `K06` | 3.886745 | — none in frame | — | 0.000 | 0.000 | 0.0 | no | no | — |
| 60 | `l2_p114_001` | `k0_00` | `K20` | 3.924402 | — none in frame | — | 0.000 | 0.000 | 0.0 | no | no | — |
| 61 | `l2_p65_101` | `k0_00` | `K01` | 4.000000 | — none in frame | — | 0.000 | 0.000 | 0.0 | no | no | — |
| 62 | `l2_p65_111` | `k0_00` | `K03` | 3.925149 | — none in frame | — | 0.000 | 0.000 | 0.0 | no | no | — |
| 63 | `l2_p74_001` | `k0_00` | `K05` | 3.912232 | — none in frame | — | 0.000 | 0.000 | 0.0 | no | no | — |

## 2. Minimisers ranked by how many alive pages cluster on them

| minimiser | s\* | ALIVE pages | frames those pages live in | certified basin? |
|---|---|---|---|---|
| `S01` | 4.000000 | 23 | `k5_11`, `k5_16`, `trump5` | **none** |
| `S03` | 3.942809 | 11 | `k5_16`, `trump5` | **none** |
| `none` | — | 6 | `k0_00`, `k5_11`, `k5_16` | **none** |
| `S02` | 3.886746 | 6 | `k5_11`, `k5_16`, `trump5` | **yes** — k5_11, k5_16, trump5 |
| `K01` | 4.000000 | 3 | `k0_00` | **none** |
| `S08` | 3.914214 | 2 | `k5_16`, `trump5` | **none** |
| `K04` | 3.914214 | 1 | `k0_00` | **none** |
| `K06` | 3.886745 | 1 | `k0_00` | **none** |
| `K20` | 3.924402 | 1 | `k0_00` | **none** |
| `K03` | 3.925149 | 1 | `k0_00` | **none** |
| `K05` | 3.912232 | 1 | `k0_00` | **none** |
| `S38` | 3.928915 | 1 | `trump5` | **yes** — k6_21  *(but not in any frame an alive page lives in)* |
| `S11` | 3.976620 | 1 | `trump5` | **none** |
| `S07` | 3.885618 | 1 | `trump5` | **yes** — trump5 |
| `S05` | 3.912232 | 1 | `k5_11` | **none** |
| `S53` | 4.000261 | 1 | `k5_11` | **none** |
| `S10` | 3.902674 | 1 | `k5_11` | **none** |
| `S36` | 3.924003 | 1 | `k5_11` | **none** |

## 3. Pages with no nearby minimiser at all — the drain-census route

**[M] 56 of 63 pages** minimise to a configuration that has no certified basin in their class frame; **11** of those (the whole `k0_00` lane) sit in a frame with no basin of any minimiser, so containment cannot even be tested there — `k0_00` has no pins, so no local certificate of the `CLASS_PINS` form applies to it at all.  These are the census candidates.

| page | class | family (nearest packing) | s\* | why no basin |
|---|---|---|---|---|
| `l1_071` | `k0_00` | `K01` | 4.000000 | no basin in the `k0_00` frame (no class pins) |
| `l1_148` | `k0_00` | `K01` | 4.000000 | no basin in the `k0_00` frame (no class pins) |
| `l2_p65_101` | `k0_00` | `K01` | 4.000000 | no basin in the `k0_00` frame (no class pins) |
| `l2_p65_111` | `k0_00` | `K03` | 3.925149 | no basin in the `k0_00` frame (no class pins) |
| `l1_104` | `k0_00` | `K04` | 3.914214 | no basin in the `k0_00` frame (no class pins) |
| `l2_p74_001` | `k0_00` | `K05` | 3.912232 | no basin in the `k0_00` frame (no class pins) |
| `l1_159` | `k0_00` | `K06` | 3.886745 | no basin in the `k0_00` frame (no class pins) |
| `l2_p114_001` | `k0_00` | `K20` | 3.924402 | no basin in the `k0_00` frame (no class pins) |
| `l1_124` | `k0_00` | `none` | 3.942810 | no basin in the `k0_00` frame (no class pins) |
| `l1_153` | `k0_00` | `none` | 3.877084 | no basin in the `k0_00` frame (no class pins) |
| `l1_158` | `k0_00` | `none` | 3.902674 | no basin in the `k0_00` frame (no class pins) |
| `k5_11_interior_Y0130` | `k5_11` | `S01` | 4.000000 | `S01` has no local certificate anywhere |
| `k5_11_interior_Y0147` | `k5_11` | `S01` | 4.000000 | `S01` has no local certificate anywhere |
| `k5_11_interior_Y0308` | `k5_11` | `S01` | 4.000000 | `S01` has no local certificate anywhere |
| `k5_11_interior_Y0985` | `k5_11` | `S01` | 4.000000 | `S01` has no local certificate anywhere |
| `k5_11_interior_Y0202` | `k5_11` | `S05` | 3.912232 | `S05` has no local certificate anywhere |
| `k5_11_interior_Y1104` | `k5_11` | `S10` | 3.902674 | `S10` has no local certificate anywhere |
| `k5_11_interior_Y1110` | `k5_11` | `S36` | 3.924003 | `S36` has no local certificate anywhere |
| `k5_11_interior_Y0672` | `k5_11` | `S53` | 4.000261 | `S53` has no local certificate anywhere |
| `k5_11_interior_Y0662` | `k5_11` | `none` | 3.877084 | `none` has no local certificate anywhere |
| `k5_16_interior_Y0027` | `k5_16` | `S01` | 4.000000 | `S01` has no local certificate anywhere |
| `k5_16_interior_Y0044` | `k5_16` | `S01` | 4.000000 | `S01` has no local certificate anywhere |
| `k5_16_interior_Y0230` | `k5_16` | `S01` | 4.000000 | `S01` has no local certificate anywhere |
| `k5_16_interior_Y0325` | `k5_16` | `S01` | 4.000000 | `S01` has no local certificate anywhere |
| `k5_16_interior_Y0491` | `k5_16` | `S01` | 4.000000 | `S01` has no local certificate anywhere |
| `k5_16_interior_Y0500` | `k5_16` | `S01` | 4.000000 | `S01` has no local certificate anywhere |
| `k5_16_interior_Y0565` | `k5_16` | `S01` | 4.000000 | `S01` has no local certificate anywhere |
| `k5_16_interior_Y0719` | `k5_16` | `S01` | 4.000000 | `S01` has no local certificate anywhere |
| `k5_16_interior_Y0839` | `k5_16` | `S01` | 4.000000 | `S01` has no local certificate anywhere |
| `k5_16_interior_Y0881` | `k5_16` | `S01` | 4.000000 | `S01` has no local certificate anywhere |
| `k5_16_interior_Y1117` | `k5_16` | `S01` | 4.000000 | `S01` has no local certificate anywhere |
| `k5_16_interior_Y0099` | `k5_16` | `S03` | 3.942809 | `S03` has no local certificate anywhere |
| `k5_16_interior_Y0191` | `k5_16` | `S03` | 3.942809 | `S03` has no local certificate anywhere |
| `k5_16_interior_Y0249` | `k5_16` | `S03` | 3.942809 | `S03` has no local certificate anywhere |
| `k5_16_interior_Y0402` | `k5_16` | `S03` | 3.942809 | `S03` has no local certificate anywhere |
| `k5_16_interior_Y0660` | `k5_16` | `S03` | 3.942809 | `S03` has no local certificate anywhere |
| `k5_16_interior_Y0865` | `k5_16` | `S03` | 3.942809 | `S03` has no local certificate anywhere |
| `k5_16_interior_Y0991` | `k5_16` | `S03` | 3.942809 | `S03` has no local certificate anywhere |
| `k5_16_interior_Y1022` | `k5_16` | `S03` | 3.942809 | `S03` has no local certificate anywhere |
| `k5_16_interior_Y1056` | `k5_16` | `S08` | 3.914214 | `S08` has no local certificate anywhere |
| `k5_16_interior_Y0436` | `k5_16` | `none` | 3.877084 | `none` has no local certificate anywhere |
| `k5_16_interior_Y0460` | `k5_16` | `none` | 3.877084 | `none` has no local certificate anywhere |
| `c0_Y0171` | `trump5_j0` | `S01` | 4.000000 | `S01` has no local certificate anywhere |
| `c0_Y0175` | `trump5_j0` | `S01` | 4.000000 | `S01` has no local certificate anywhere |
| `c0_Y0258` | `trump5_j0` | `S01` | 4.000000 | `S01` has no local certificate anywhere |
| `c0_Y0787` | `trump5_j0` | `S01` | 4.000000 | `S01` has no local certificate anywhere |
| `c0_Y0952` | `trump5_j0` | `S01` | 4.000000 | `S01` has no local certificate anywhere |
| `c0_Y0959` | `trump5_j0` | `S01` | 4.000000 | `S01` has no local certificate anywhere |
| `c0_Y1033` | `trump5_j0` | `S01` | 4.000000 | `S01` has no local certificate anywhere |
| `slack0.02_c0_Y0272` | `trump5_j0` | `S01` | 4.000000 | `S01` has no local certificate anywhere |
| `c0_Y0223` | `trump5_j0` | `S03` | 3.942809 | `S03` has no local certificate anywhere |
| `c0_Y0255` | `trump5_j0` | `S03` | 3.942809 | `S03` has no local certificate anywhere |
| `c0_Y0788` | `trump5_j0` | `S03` | 3.942809 | `S03` has no local certificate anywhere |
| `c0_Y0257` | `trump5_j0` | `S08` | 3.914214 | `S08` has no local certificate anywhere |
| `c0_Y0215` | `trump5_j0` | `S11` | 3.976620 | `S11` has no local certificate anywhere |
| `c0_Y0169` | `trump5_j0` | `S38` | 3.928915 | `S38` has a basin only in `k6_21` |

## 4. What would have to grow, and by how much

* **`S02` / `k5_11`** — 57 certified box sets (A119, A160); 10 alive pages match it; growth needed: min 0.51x, median 1.28x, max 3.63x; 2 already contained, 7 within 2x.
* **`S02` / `k5_16`** — 52 certified box sets (A163); 25 alive pages match it; growth needed: min 0.99x, median 3.09x, max 4.19x; 1 already contained, 8 within 2x.
* **`S02` / `trump5`** — 42 certified box sets (A163); 12 alive pages match it; growth needed: min 0.29x, median 1.21x, max 4.19x; 5 already contained, 5 within 2x.
* **`S07` / `trump5`** — 2 certified box sets (A119); 5 alive pages match it; growth needed: min 1.29x, median 1.61x, max 3.59x; 0 already contained, 4 within 2x.
* **`S33` / `k6_07`** — 6 certified box sets; **no alive page sits in this frame**.
* **`S38` / `k6_21`** — 1 certified box sets; **no alive page sits in this frame**.

## 5. Soundness

**[S] Box containment is NECESSARY, not sufficient.**  A certified N asks for a square in *each* of its boxes (plus the class pins in their slack cores); an alive page conditions *one* square (62 of the 63 pages have exactly one conditioned box; `f1_L10_0003` has two).  A page whose box lies inside a basin box is therefore a page the LocalCompose YES leaf *can* cover once the other boxes are supplied by the NO children (A120/A136) — not a page that is already dead.  The kill that follows from containment alone is the consumer column (`cons`), which is A116/A151/A160/A163's own test and is reproduced here byte-for-byte on the shared cases.

**[M] Control.**  `k5_16_interior_Y1110` reproduces A163's consumer slack 0.01311 exactly, and `k5_16_interior_Y0054` / `Y0380` / `Y0230` reproduce A163's greedy-cover membership.

