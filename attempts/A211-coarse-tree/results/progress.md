# A211 progress -- 2026-09-12 18:42:26

The COARSE tree (notes/coarse_tree.md): A202 stage 0 + A203 CSP; coarse internal nodes (re-binned pieces <= 96 units, refine 1, no lonely clip, reach depth 2; ONE round; branch at once); at every fully named leaf: rule CC (Lemma CORNER-COVER) -> A208 no-room + pocket CN bound (pockets branched at k = 9) -> A207 basin clip -> A206 Rule NS (MAX_FRAC 0.5) -> the exact cascade + sharp round.  Pad 0 FIRST then the G1 window pad; wall 1800 s per pad per page; depth cap 6; node cap 600; every kill [C: closed-form / library clip trace + the leaf lemma], no verifier clause.

## The 19 alive k5 gallery pages (0 nodes)

| page | pad | stage reached | verdict | seconds |
|---|---|---|---|---|

CPU-h in this block: 0.00

## The k5 frontier (A57 census, deepest-first) (0 nodes)

| page | pad | stage reached | verdict | seconds |
|---|---|---|---|---|

CPU-h in this block: 0.00

## Price and projection

* gallery: 0 / 0 pages DEAD at the window pad, 0.00 CPU-h
* frontier: not started; the census has 321 alive nodes ({'k5_11_interior_G1_D2_D2': 1, 'k5_11_interior_G1_D2': 35, 'k5_11_interior_G1': 116, 'k5_11_interior_L1_D2': 1, 'k5_11_interior_L1': 15, 'k5_16_interior_G1_D2': 2, 'k5_16_interior_G1': 144, 'k5_16_interior_L1': 7})

