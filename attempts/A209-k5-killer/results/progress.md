# A209 progress -- 2026-09-12 04:48:09

Chain: A202 stage 0 + A203 CSP -> A204 cascade -> A205 clip tree (Lemma CT, bar-anon, sharp round) + A206 Rule NS (MAX_FRAC 0.5) + A207 basin clip (k5_16 TR(1,0) r_c 0.03; k5_11 BL(1,1) r_c 0.06) -> A208 no-room with the pocket CN bound at every leaf with >= 9 roles, pocket branching at k = 9.  Wall 3600 s per pad per page; depth cap 5; node cap 300; every kill [C: library clip trace (+ A189 Lemma 1 / Lemma CN / Lemma BASIN)], no verifier clause.

## The 22 alive k5 gallery pages (9 nodes)

| page | pad | stage reached | verdict | seconds |
|---|---|---|---|---|
| k5_11_interior_Y0202 | g1 | 2 (tree: 11 nodes, depth 5, NS 2, pockets 0) | ALIVE (wall) | 3663 |
| k5_11_interior_Y0202 | zero | 2 (tree: 13 nodes, depth 4, NS 2, pockets 0) | ALIVE (wall) | 3718 |
| k5_11_interior_Y0130 | g1 | 2 (tree: 12 nodes, depth 5, NS 1, pockets 1) | ALIVE (wall) | 3857 |
| k5_11_interior_Y0130 | zero | 2 (tree: 21 nodes, depth 4, NS 0, pockets 1) | ALIVE (wall) | 3665 |
| k5_11_interior_Y0672 | g1 | 2 (tree: 14 nodes, depth 5, NS 2, pockets 1) | ALIVE (wall) | 3728 |
| k5_11_interior_Y0672 | zero | 2 (tree: 20 nodes, depth 4, NS 0, pockets 1) | ALIVE (wall) | 3760 |
| k5_11_interior_Y0738 | g1 | 2 (tree: 15 nodes, depth 5, NS 3, pockets 0) | ALIVE (wall) | 3730 |
| k5_11_interior_Y0738 | zero | 2 (tree: 14 nodes, depth 5, NS 2, pockets 0) | ALIVE (wall) | 3691 |
| k5_16_interior_Y0325 | g1 | 2 (tree: 4 nodes, depth 1, NS 0, pockets 0) | DEAD | 414 |
| k5_16_interior_Y0044 | g1 | 2 (tree: 13 nodes, depth 5, NS 4, pockets 0) | ALIVE (wall) | 3646 |
| k5_16_interior_Y0044 | zero | 2 (tree: 24 nodes, depth 3, NS 3, pockets 0) | ALIVE (wall) | 3630 |
| k5_16_interior_Y0099 | g1 | 2 (tree: 29 nodes, depth 3, NS 0, pockets 0) | ALIVE (wall) | 3694 |
| k5_16_interior_Y0249 | g1 | 2 (tree: 18 nodes, depth 3, NS 0, pockets 0) | ALIVE (wall) | 3670 |
| k5_16_interior_Y0380 | g1 | 2 (tree: 14 nodes, depth 4, NS 3, pockets 0) | DEAD | 3536 |

CPU-h in this block: 13.45

## The k5 frontier (A57 census, deepest-first) (0 nodes)

| page | pad | stage reached | verdict | seconds |
|---|---|---|---|---|

CPU-h in this block: 0.00

## Price and projection

* gallery: 2 / 9 pages DEAD at the window pad, 13.45 CPU-h
* frontier: not started; the census has 323 alive nodes ({'k5_11_interior_G1_D2_D2': 1, 'k5_11_interior_G1_D2': 35, 'k5_11_interior_G1': 116, 'k5_11_interior_L1_D2': 1, 'k5_11_interior_L1': 15, 'k5_16_interior_G1_D2': 2, 'k5_16_interior_G1': 146, 'k5_16_interior_L1': 7})

