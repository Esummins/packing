# A211 progress -- 2026-09-15 19:54:43

The COARSE tree (notes/coarse_tree.md): A202 stage 0 + A203 CSP; coarse internal nodes (re-binned pieces <= 96 units, refine 1, no lonely clip, reach depth 2; ONE round; branch at once); at every fully named leaf: rule CC (Lemma CORNER-COVER) -> A208 no-room + pocket CN bound (pockets branched at k = 9) -> A207 basin clip -> A206 Rule NS (MAX_FRAC 0.5) -> the exact cascade + sharp round.  Pad 0 FIRST then the G1 window pad; wall 1800 s per pad per page; depth cap 6; node cap 600; every kill [C: closed-form / library clip trace + the leaf lemma], no verifier clause.

## Where the alive k5 gallery pages stand (A225 PROGRESS: start nodes left / alive leaves / depth)

A *start node* is an alive leaf the run inherited from the previous run (Lemma INHERIT, notes/coarse_tree.md s.4) -- the top-level branches of the current run.  *Left* = alive at the wall + never reached.  *Alive leaves* = the start nodes of the NEXT run.  *Depth* = absolute (the start node's own path length + the depth the run added below it).

| page | pad | start nodes | dead this run | alive at wall | not reached | **left** | alive leaves | max depth | runs | wall (CPU-h) | estimate (CPU-h) | last run |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| k5_16_interior_Y1117 | g1 | 10 | 8 | 1 | 1 | **2** | 11 | 5 | 1 | 0.51 | 0.07 | 2026-09-12 23:28:01 |
| k5_16_interior_Y1117 | zero | 0 | 0 | 0 | 0 | **0** | 0 | 0 | 1 | 0.00 | 0.00 | 2026-09-12 22:57:37 (**this pad is now DEAD**) |

**TOTAL over the 1 alive k5 gallery pages (window pad):** 2 start nodes left, 11 alive leaves (the next runs' start nodes), deepest branch 5, 2 run(s) over both pads for 0.51 CPU-h spent; ESTIMATE (not a bound) 0.07 CPU-h to close the start nodes now open at the window pad -- an UNDER-estimate: the start nodes still alive are the ones that already survived a full wall, and each survivor splits into several new start nodes.

## The 19 alive k5 gallery pages (18 nodes)

| page | pad | stage reached | verdict | seconds |
|---|---|---|---|---|
| k5_11_interior_Y0202 | g1 | 2 (tree: 10 nodes, depth 1, CC 0, exact 0, NS 0, pockets 0) | DEAD | 94 |
| k5_11_interior_Y0202 | zero | 2 (tree: 27 nodes, depth 8, CC 0, exact 0, NS 3, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 1604 |
| k5_11_interior_Y0130 | g1 | 2 (tree: 5 nodes, depth 2, CC 0, exact 0, NS 1, pockets 1) | DEAD | 137 |
| k5_11_interior_Y0130 | zero | 2 (tree: 29 nodes, depth 4, CC 4, exact 0, NS 5, pockets 4) | DEAD (s0-only, WINDOW-PENDING) | 490 |
| k5_11_interior_Y0672 | g1 | 2 (tree: 43 nodes, depth 5, CC 5, exact 0, NS 10, pockets 8) | DEAD | 1005 |
| k5_11_interior_Y0672 | zero | 2 (tree: 99 nodes, depth 5, CC 15, exact 0, NS 14, pockets 13) | ALIVE (wall) | 1800 |
| k5_11_interior_Y0738 | g1 | 2 (tree: 155 nodes, depth 8, CC 2, exact 0, NS 13, pockets 36) | DEAD | 1287 |
| k5_11_interior_Y0738 | zero | 2 (tree: 119 nodes, depth 8, CC 2, exact 0, NS 13, pockets 24) | DEAD (s0-only, WINDOW-PENDING) | 970 |
| k5_16_interior_Y0044 | g1 | 2 (tree: 50 nodes, depth 4, CC 0, exact 0, NS 5, pockets 0) | DEAD | 923 |
| k5_16_interior_Y0044 | zero | 2 (tree: 15 nodes, depth 3, CC 0, exact 0, NS 3, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 527 |
| k5_16_interior_Y0099 | g1 | 2 (tree: 10 nodes, depth 1, CC 0, exact 0, NS 1, pockets 1) | DEAD | 169 |
| k5_16_interior_Y0099 | zero | 2 (tree: 8 nodes, depth 1, CC 0, exact 0, NS 0, pockets 1) | DEAD (s0-only, WINDOW-PENDING) | 78 |
| k5_16_interior_Y0249 | g1 | 2 (tree: 87 nodes, depth 4, CC 0, exact 0, NS 9, pockets 1) | DEAD | 1669 |
| k5_16_interior_Y0249 | zero | 2 (tree: 68 nodes, depth 4, CC 0, exact 0, NS 9, pockets 0) | ALIVE (wall) | 1842 |
| k5_16_interior_Y0402 | g1 | 2 (tree: 0 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD | 0 |
| k5_16_interior_Y0402 | zero | 2 (tree: 0 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 1 |
| k5_16_interior_Y0460 | g1 | 2 (tree: 43 nodes, depth 4, CC 0, exact 0, NS 5, pockets 7) | DEAD | 1297 |
| k5_16_interior_Y0460 | zero | 2 (tree: 47 nodes, depth 4, CC 0, exact 0, NS 6, pockets 8) | DEAD (s0-only, WINDOW-PENDING) | 1571 |
| k5_16_interior_Y0719 | g1 | 2 (tree: 9 nodes, depth 1, CC 0, exact 0, NS 0, pockets 0) | DEAD | 237 |
| k5_16_interior_Y0719 | zero | 2 (tree: 13 nodes, depth 1, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 558 |
| k5_16_interior_Y0500 | g1 | 2 (tree: 79 nodes, depth 4, CC 0, exact 0, NS 3, pockets 8) | DEAD | 1341 |
| k5_16_interior_Y0500 | zero | 2 (tree: 70 nodes, depth 4, CC 0, exact 0, NS 5, pockets 6) | DEAD (s0-only, WINDOW-PENDING) | 1130 |
| k5_16_interior_Y0660 | g1 | 2 (tree: 41 nodes, depth 4, CC 0, exact 0, NS 4, pockets 8) | DEAD | 1460 |
| k5_16_interior_Y0660 | zero | 2 (tree: 42 nodes, depth 4, CC 0, exact 0, NS 7, pockets 8) | DEAD (s0-only, WINDOW-PENDING) | 1474 |
| k5_16_interior_Y0881 | g1 | 2 (tree: 26 nodes, depth 2, CC 0, exact 0, NS 2, pockets 0) | DEAD | 879 |
| k5_16_interior_Y0881 | zero | 2 (tree: 34 nodes, depth 3, CC 0, exact 0, NS 2, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 1144 |
| k5_16_interior_Y0865 | g1 | 2 (tree: 163 nodes, depth 8, CC 0, exact 39, NS 15, pockets 4) | DEAD | 1762 |
| k5_16_interior_Y0865 | zero | 2 (tree: 94 nodes, depth 6, CC 0, exact 10, NS 11, pockets 4) | DEAD (s0-only, WINDOW-PENDING) | 1027 |
| k5_16_interior_Y0991 | g1 | 2 (tree: 8 nodes, depth 2, CC 0, exact 0, NS 0, pockets 1) | DEAD | 229 |
| k5_16_interior_Y0991 | zero | 2 (tree: 30 nodes, depth 3, CC 0, exact 0, NS 0, pockets 3) | DEAD (s0-only, WINDOW-PENDING) | 762 |
| k5_16_interior_Y1117 | g1 | 2 (tree: 24 nodes, depth 3, CC 0, exact 0, NS 2, pockets 0) | ALIVE (wall) | 1823 |
| k5_16_interior_Y1117 | zero | 2 (tree: 0 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 0 |
| k5_16_interior_Y1022 | g1 | 2 (tree: 35 nodes, depth 3, CC 0, exact 0, NS 4, pockets 5) | DEAD | 710 |
| k5_16_interior_Y1022 | zero | 2 (tree: 33 nodes, depth 3, CC 0, exact 0, NS 2, pockets 6) | DEAD (s0-only, WINDOW-PENDING) | 926 |
| k5_16_interior_Y1056 | g1 | 2 (tree: 80 nodes, depth 4, CC 0, exact 0, NS 0, pockets 4) | DEAD | 468 |
| k5_16_interior_Y1056 | zero | 2 (tree: 80 nodes, depth 4, CC 0, exact 0, NS 0, pockets 4) | DEAD (s0-only, WINDOW-PENDING) | 442 |

CPU-h in this block: 8.84

## The k5 frontier (A57 census, deepest-first) (84 nodes)

| page | pad | stage reached | verdict | seconds |
|---|---|---|---|---|
| k5_11_interior_Y0186_D00_D00 | g1 | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD | 6 |
| k5_11_interior_Y0186_D00_D00 | zero | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 7 |
| k5_11_interior_Y0127_D04 | g1 | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD | 6 |
| k5_11_interior_Y0127_D04 | zero | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 7 |
| k5_11_interior_Y0036_D07 | g1 | 2 (tree: 25 nodes, depth 6, CC 0, exact 0, NS 0, pockets 1) | ALIVE (wall) | 1831 |
| k5_11_interior_Y0036_D07 | zero | 2 (tree: 25 nodes, depth 5, CC 0, exact 1, NS 0, pockets 1) | ALIVE (wall) | 2012 |
| k5_11_interior_Y0105_D03 | g1 | 2 (tree: 19 nodes, depth 5, CC 2, exact 0, NS 2, pockets 1) | ALIVE (wall) | 1844 |
| k5_11_interior_Y0105_D03 | zero | 2 (tree: 21 nodes, depth 5, CC 4, exact 0, NS 2, pockets 0) | ALIVE (wall) | 1834 |
| k5_11_interior_Y0186_D00 | g1 | 2 (tree: 25 nodes, depth 7, CC 1, exact 1, NS 4, pockets 1) | ALIVE (wall) | 1897 |
| k5_11_interior_Y0186_D00 | zero | 2 (tree: 22 nodes, depth 6, CC 2, exact 1, NS 3, pockets 1) | ALIVE (wall) | 1915 |
| k5_11_interior_Y0186_D01 | g1 | 2 (tree: 47 nodes, depth 5, CC 3, exact 0, NS 1, pockets 1) | ALIVE (wall) | 1811 |
| k5_11_interior_Y0186_D01 | zero | 2 (tree: 44 nodes, depth 5, CC 2, exact 0, NS 1, pockets 0) | ALIVE (wall) | 1852 |
| k5_11_interior_Y0217_D02 | g1 | 2 (tree: 18 nodes, depth 6, CC 3, exact 0, NS 5, pockets 1) | ALIVE (wall) | 1836 |
| k5_11_interior_Y0217_D02 | zero | 2 (tree: 20 nodes, depth 7, CC 2, exact 0, NS 5, pockets 1) | ALIVE (wall) | 1853 |
| k5_11_interior_Y0217_D03 | g1 | 2 (tree: 18 nodes, depth 6, CC 4, exact 1, NS 3, pockets 0) | ALIVE (wall) | 1930 |
| k5_11_interior_Y0217_D03 | zero | 2 (tree: 20 nodes, depth 5, CC 4, exact 0, NS 5, pockets 1) | ALIVE (wall) | 1861 |
| k5_11_interior_Y0217_D06 | g1 | 2 (tree: 17 nodes, depth 5, CC 3, exact 0, NS 4, pockets 1) | ALIVE (wall) | 1847 |
| k5_11_interior_Y0217_D06 | zero | 2 (tree: 18 nodes, depth 6, CC 3, exact 0, NS 5, pockets 1) | ALIVE (wall) | 1816 |
| k5_11_interior_Y0217_D07 | g1 | 2 (tree: 19 nodes, depth 6, CC 3, exact 1, NS 3, pockets 0) | ALIVE (wall) | 1970 |
| k5_11_interior_Y0217_D07 | zero | 2 (tree: 25 nodes, depth 5, CC 5, exact 0, NS 4, pockets 0) | ALIVE (wall) | 1828 |
| k5_11_interior_Y0256_D03 | g1 | 2 (tree: 20 nodes, depth 6, CC 4, exact 1, NS 3, pockets 1) | ALIVE (wall) | 1939 |
| k5_11_interior_Y0256_D03 | zero | 2 (tree: 21 nodes, depth 5, CC 5, exact 0, NS 4, pockets 0) | ALIVE (wall) | 1871 |
| k5_11_interior_Y0256_D06 | g1 | 2 (tree: 19 nodes, depth 5, CC 4, exact 1, NS 4, pockets 1) | ALIVE (wall) | 1931 |
| k5_11_interior_Y0256_D06 | zero | 2 (tree: 17 nodes, depth 5, CC 3, exact 0, NS 4, pockets 1) | ALIVE (wall) | 1880 |
| k5_11_interior_Y0256_D07 | g1 | 2 (tree: 18 nodes, depth 5, CC 4, exact 0, NS 4, pockets 1) | ALIVE (wall) | 1829 |
| k5_11_interior_Y0256_D07 | zero | 2 (tree: 18 nodes, depth 5, CC 3, exact 1, NS 4, pockets 1) | ALIVE (wall) | 2034 |
| k5_11_interior_Y0376_D06 | g1 | 2 (tree: 31 nodes, depth 6, CC 0, exact 0, NS 0, pockets 1) | ALIVE (wall) | 1814 |
| k5_11_interior_Y0376_D06 | zero | 2 (tree: 28 nodes, depth 6, CC 0, exact 0, NS 0, pockets 1) | ALIVE (wall) | 1801 |
| k5_11_interior_Y0384_D00 | g1 | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD | 6 |
| k5_11_interior_Y0384_D00 | zero | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 6 |
| k5_11_interior_Y0636_D05 | g1 | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD | 6 |
| k5_11_interior_Y0636_D05 | zero | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 5 |
| k5_11_interior_Y0414_D03 | g1 | 2 (tree: 26 nodes, depth 6, CC 3, exact 0, NS 3, pockets 0) | ALIVE (wall) | 1826 |
| k5_11_interior_Y0414_D03 | zero | 2 (tree: 25 nodes, depth 8, CC 1, exact 0, NS 3, pockets 0) | ALIVE (wall) | 1820 |
| k5_11_interior_Y0414_D07 | g1 | 2 (tree: 21 nodes, depth 6, CC 4, exact 0, NS 5, pockets 1) | ALIVE (wall) | 1836 |
| k5_11_interior_Y0414_D07 | zero | 2 (tree: 20 nodes, depth 6, CC 4, exact 0, NS 5, pockets 1) | ALIVE (wall) | 1840 |
| k5_11_interior_Y0414_D06 | g1 | 2 (tree: 20 nodes, depth 6, CC 2, exact 1, NS 5, pockets 1) | ALIVE (wall) | 1879 |
| k5_11_interior_Y0414_D06 | zero | 2 (tree: 21 nodes, depth 6, CC 1, exact 1, NS 5, pockets 1) | ALIVE (wall) | 2075 |
| k5_11_interior_Y0636_D06 | g1 | 2 (tree: 26 nodes, depth 5, CC 0, exact 0, NS 1, pockets 2) | ALIVE (wall) | 1809 |
| k5_11_interior_Y0636_D06 | zero | 2 (tree: 28 nodes, depth 5, CC 0, exact 0, NS 1, pockets 1) | ALIVE (wall) | 1808 |
| k5_11_interior_Y0738_D00 | g1 | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD | 0 |
| k5_11_interior_Y0738_D00 | zero | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 1 |
| k5_11_interior_Y0738_D02 | g1 | 2 (tree: 38 nodes, depth 9, CC 2, exact 0, NS 7, pockets 1) | ALIVE (wall) | 1801 |
| k5_11_interior_Y0738_D02 | zero | 2 (tree: 41 nodes, depth 8, CC 2, exact 0, NS 7, pockets 1) | ALIVE (wall) | 1814 |
| k5_11_interior_Y0738_D01 | g1 | 2 (tree: 39 nodes, depth 9, CC 4, exact 0, NS 6, pockets 1) | ALIVE (wall) | 1802 |
| k5_11_interior_Y0738_D01 | zero | 2 (tree: 41 nodes, depth 7, CC 4, exact 0, NS 8, pockets 1) | ALIVE (wall) | 1859 |
| k5_11_interior_Y0738_D03 | g1 | 2 (tree: 42 nodes, depth 11, CC 5, exact 0, NS 5, pockets 1) | ALIVE (wall) | 1805 |
| k5_11_interior_Y0738_D03 | zero | 2 (tree: 37 nodes, depth 8, CC 5, exact 0, NS 8, pockets 1) | ALIVE (wall) | 1842 |
| k5_11_interior_Y0864_D07 | g1 | 2 (tree: 38 nodes, depth 8, CC 6, exact 0, NS 5, pockets 1) | ALIVE (wall) | 1837 |
| k5_11_interior_Y0864_D07 | zero | 2 (tree: 49 nodes, depth 8, CC 6, exact 0, NS 7, pockets 2) | ALIVE (wall) | 1802 |
| k5_11_interior_Y0954_D00 | g1 | 2 (tree: 40 nodes, depth 10, CC 5, exact 0, NS 2, pockets 1) | ALIVE (wall) | 1810 |
| k5_11_interior_Y0954_D00 | zero | 2 (tree: 43 nodes, depth 10, CC 6, exact 0, NS 2, pockets 1) | ALIVE (wall) | 1832 |
| k5_11_interior_Y0954_D01 | g1 | 2 (tree: 49 nodes, depth 9, CC 8, exact 0, NS 4, pockets 4) | ALIVE (wall) | 1841 |
| k5_11_interior_Y0954_D01 | zero | 2 (tree: 63 nodes, depth 9, CC 6, exact 0, NS 5, pockets 6) | ALIVE (wall) | 1801 |
| k5_11_interior_Y0978_D04 | g1 | 2 (tree: 87 nodes, depth 7, CC 8, exact 0, NS 9, pockets 2) | DEAD | 1379 |
| k5_11_interior_Y0978_D04 | zero | 2 (tree: 82 nodes, depth 6, CC 3, exact 0, NS 5, pockets 2) | DEAD (s0-only, WINDOW-PENDING) | 829 |
| k5_11_interior_Y0954_D02 | g1 | 2 (tree: 41 nodes, depth 9, CC 6, exact 0, NS 1, pockets 1) | ALIVE (wall) | 1831 |
| k5_11_interior_Y0954_D02 | zero | 2 (tree: 41 nodes, depth 9, CC 6, exact 0, NS 1, pockets 1) | ALIVE (wall) | 1840 |
| k5_11_interior_Y0978_D07 | g1 | 2 (tree: 43 nodes, depth 8, CC 3, exact 0, NS 4, pockets 0) | ALIVE (wall) | 1804 |
| k5_11_interior_Y0978_D07 | zero | 2 (tree: 47 nodes, depth 8, CC 1, exact 0, NS 5, pockets 1) | ALIVE (wall) | 1803 |
| k5_11_interior_Y1069_D06 | g1 | 2 (tree: 45 nodes, depth 12, CC 2, exact 0, NS 7, pockets 2) | ALIVE (wall) | 1810 |
| k5_11_interior_Y1069_D06 | zero | 2 (tree: 44 nodes, depth 12, CC 1, exact 0, NS 4, pockets 2) | ALIVE (wall) | 1818 |
| k5_11_interior_Y1128_D06 | g1 | 2 (tree: 63 nodes, depth 7, CC 4, exact 0, NS 8, pockets 1) | ALIVE (wall) | 1843 |
| k5_11_interior_Y1128_D06 | zero | 2 (tree: 77 nodes, depth 9, CC 5, exact 0, NS 10, pockets 2) | ALIVE (wall) | 1848 |
| k5_11_interior_Y1128_D07 | g1 | 2 (tree: 84 nodes, depth 7, CC 5, exact 0, NS 7, pockets 21) | ALIVE (wall) | 1850 |
| k5_11_interior_Y1128_D07 | zero | 2 (tree: 81 nodes, depth 7, CC 5, exact 0, NS 7, pockets 21) | ALIVE (wall) | 1832 |
| k5_11_interior_Y1141_D00 | g1 | 2 (tree: 8 nodes, depth 1, CC 2, exact 0, NS 0, pockets 0) | DEAD | 26 |
| k5_11_interior_Y1141_D00 | zero | 2 (tree: 8 nodes, depth 1, CC 2, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 31 |
| k5_11_interior_Y1141_D01 | g1 | 2 (tree: 5 nodes, depth 1, CC 0, exact 0, NS 0, pockets 0) | DEAD | 4 |
| k5_11_interior_Y1141_D01 | zero | 2 (tree: 5 nodes, depth 1, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 7 |
| k5_11_interior_Y1141_D04 | g1 | 0 | DEAD | 30 |
| k5_11_interior_Y1141_D04 | zero | 0 | DEAD (s0-only, WINDOW-PENDING) | 27 |
| k5_11_interior_Y0033 | g1 | 2 (tree: 147 nodes, depth 5, CC 2, exact 0, NS 0, pockets 13) | ALIVE (wall) | 1810 |
| k5_11_interior_Y0033 | zero | 2 (tree: 145 nodes, depth 6, CC 2, exact 1, NS 1, pockets 11) | DEAD (s0-only, WINDOW-PENDING) | 1268 |
| k5_11_interior_Y0036 | g1 | 2 (tree: 73 nodes, depth 5, CC 1, exact 0, NS 2, pockets 3) | DEAD | 472 |
| k5_11_interior_Y0036 | zero | 2 (tree: 74 nodes, depth 5, CC 1, exact 0, NS 1, pockets 2) | DEAD (s0-only, WINDOW-PENDING) | 392 |
| k5_11_interior_Y0039 | g1 | 2 (tree: 95 nodes, depth 6, CC 2, exact 0, NS 3, pockets 19) | ALIVE (wall) | 1859 |
| k5_11_interior_Y0039 | zero | 2 (tree: 94 nodes, depth 5, CC 2, exact 0, NS 2, pockets 20) | ALIVE (wall) | 1801 |
| k5_11_interior_Y0041 | g1 | 2 (tree: 161 nodes, depth 7, CC 4, exact 0, NS 1, pockets 13) | DEAD | 1575 |
| k5_11_interior_Y0041 | zero | 2 (tree: 144 nodes, depth 6, CC 3, exact 0, NS 1, pockets 12) | DEAD (s0-only, WINDOW-PENDING) | 1278 |
| k5_11_interior_Y0044 | g1 | 2 (tree: 75 nodes, depth 5, CC 2, exact 0, NS 0, pockets 5) | DEAD | 647 |
| k5_11_interior_Y0044 | zero | 2 (tree: 76 nodes, depth 5, CC 2, exact 0, NS 1, pockets 5) | DEAD (s0-only, WINDOW-PENDING) | 578 |
| k5_11_interior_Y0054 | g1 | 2 (tree: 66 nodes, depth 7, CC 4, exact 0, NS 4, pockets 8) | DEAD | 1104 |
| k5_11_interior_Y0054 | zero | 2 (tree: 62 nodes, depth 7, CC 3, exact 0, NS 3, pockets 6) | DEAD (s0-only, WINDOW-PENDING) | 744 |
| k5_11_interior_Y0069 | g1 | 2 (tree: 72 nodes, depth 7, CC 2, exact 0, NS 4, pockets 11) | DEAD | 1187 |
| k5_11_interior_Y0069 | zero | 2 (tree: 65 nodes, depth 7, CC 3, exact 0, NS 4, pockets 6) | DEAD (s0-only, WINDOW-PENDING) | 857 |
| k5_11_interior_Y0072 | g1 | 2 (tree: 135 nodes, depth 5, CC 2, exact 0, NS 0, pockets 10) | ALIVE (wall) | 1831 |
| k5_11_interior_Y0072 | zero | 2 (tree: 144 nodes, depth 6, CC 2, exact 0, NS 1, pockets 11) | DEAD (s0-only, WINDOW-PENDING) | 1338 |
| k5_11_interior_Y0084 | g1 | 2 (tree: 101 nodes, depth 6, CC 0, exact 0, NS 3, pockets 18) | ALIVE (wall) | 1841 |
| k5_11_interior_Y0084 | zero | 2 (tree: 88 nodes, depth 6, CC 0, exact 0, NS 3, pockets 18) | ALIVE (wall) | 1806 |
| k5_11_interior_Y0100 | g1 | 2 (tree: 9 nodes, depth 2, CC 2, exact 0, NS 0, pockets 0) | DEAD | 40 |
| k5_11_interior_Y0100 | zero | 2 (tree: 6 nodes, depth 1, CC 1, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 40 |
| k5_11_interior_Y0103 | g1 | 2 (tree: 72 nodes, depth 5, CC 5, exact 0, NS 0, pockets 3) | DEAD | 534 |
| k5_11_interior_Y0103 | zero | 2 (tree: 63 nodes, depth 4, CC 8, exact 0, NS 0, pockets 1) | DEAD (s0-only, WINDOW-PENDING) | 335 |
| k5_11_interior_Y0105 | g1 | 2 (tree: 66 nodes, depth 5, CC 3, exact 0, NS 2, pockets 11) | DEAD | 1245 |
| k5_11_interior_Y0105 | zero | 2 (tree: 60 nodes, depth 5, CC 2, exact 0, NS 2, pockets 8) | DEAD (s0-only, WINDOW-PENDING) | 979 |
| k5_11_interior_Y0108 | g1 | 2 (tree: 57 nodes, depth 5, CC 3, exact 0, NS 0, pockets 8) | DEAD | 934 |
| k5_11_interior_Y0108 | zero | 2 (tree: 59 nodes, depth 5, CC 4, exact 0, NS 1, pockets 8) | DEAD (s0-only, WINDOW-PENDING) | 914 |
| k5_11_interior_Y0119 | g1 | 2 (tree: 70 nodes, depth 4, CC 1, exact 0, NS 0, pockets 2) | DEAD | 298 |
| k5_11_interior_Y0119 | zero | 2 (tree: 60 nodes, depth 4, CC 2, exact 0, NS 0, pockets 2) | DEAD (s0-only, WINDOW-PENDING) | 277 |
| k5_11_interior_Y0124 | g1 | 2 (tree: 13 nodes, depth 2, CC 2, exact 0, NS 0, pockets 0) | DEAD | 19 |
| k5_11_interior_Y0124 | zero | 2 (tree: 15 nodes, depth 2, CC 2, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 44 |
| k5_11_interior_Y0122 | g1 | 2 (tree: 69 nodes, depth 7, CC 1, exact 0, NS 3, pockets 10) | DEAD | 958 |
| k5_11_interior_Y0122 | zero | 2 (tree: 48 nodes, depth 4, CC 3, exact 0, NS 0, pockets 7) | DEAD (s0-only, WINDOW-PENDING) | 864 |
| k5_11_interior_Y0127 | g1 | 2 (tree: 76 nodes, depth 8, CC 2, exact 0, NS 4, pockets 18) | ALIVE (wall) | 1805 |
| k5_11_interior_Y0127 | zero | 2 (tree: 76 nodes, depth 7, CC 1, exact 0, NS 5, pockets 16) | ALIVE (wall) | 1842 |
| k5_11_interior_Y0133 | g1 | 2 (tree: 109 nodes, depth 6, CC 1, exact 0, NS 2, pockets 16) | ALIVE (wall) | 1804 |
| k5_11_interior_Y0133 | zero | 2 (tree: 114 nodes, depth 6, CC 1, exact 0, NS 2, pockets 17) | ALIVE (wall) | 1801 |
| k5_11_interior_Y0149 | g1 | 2 (tree: 5 nodes, depth 1, CC 0, exact 0, NS 0, pockets 0) | DEAD | 4 |
| k5_11_interior_Y0149 | zero | 2 (tree: 5 nodes, depth 1, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 7 |
| k5_11_interior_Y0170 | g1 | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD | 0 |
| k5_11_interior_Y0170 | zero | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 1 |
| k5_11_interior_Y0183 | g1 | 2 (tree: 32 nodes, depth 3, CC 4, exact 0, NS 0, pockets 0) | DEAD | 83 |
| k5_11_interior_Y0183 | zero | 2 (tree: 28 nodes, depth 3, CC 3, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 71 |
| k5_11_interior_Y0143 | g1 | 2 (tree: 69 nodes, depth 4, CC 0, exact 0, NS 0, pockets 1) | DEAD | 202 |
| k5_11_interior_Y0143 | zero | 2 (tree: 62 nodes, depth 4, CC 2, exact 0, NS 0, pockets 1) | DEAD (s0-only, WINDOW-PENDING) | 175 |
| k5_11_interior_Y0217 | g1 | 2 (tree: 72 nodes, depth 8, CC 3, exact 0, NS 3, pockets 8) | DEAD | 371 |
| k5_11_interior_Y0217 | zero | 2 (tree: 67 nodes, depth 7, CC 5, exact 0, NS 4, pockets 5) | DEAD (s0-only, WINDOW-PENDING) | 272 |
| k5_11_interior_Y0274 | g1 | 2 (tree: 53 nodes, depth 4, CC 0, exact 0, NS 0, pockets 1) | DEAD | 139 |
| k5_11_interior_Y0274 | zero | 2 (tree: 55 nodes, depth 4, CC 0, exact 0, NS 0, pockets 1) | DEAD (s0-only, WINDOW-PENDING) | 119 |
| k5_11_interior_Y0256 | g1 | 2 (tree: 76 nodes, depth 8, CC 5, exact 0, NS 4, pockets 8) | DEAD | 387 |
| k5_11_interior_Y0256 | zero | 2 (tree: 70 nodes, depth 8, CC 5, exact 0, NS 4, pockets 5) | DEAD (s0-only, WINDOW-PENDING) | 311 |
| k5_11_interior_Y0303 | g1 | 2 (tree: 41 nodes, depth 5, CC 0, exact 0, NS 0, pockets 4) | DEAD | 194 |
| k5_11_interior_Y0303 | zero | 2 (tree: 40 nodes, depth 5, CC 1, exact 0, NS 0, pockets 4) | DEAD (s0-only, WINDOW-PENDING) | 190 |
| k5_11_interior_Y0290 | g1 | 2 (tree: 149 nodes, depth 7, CC 0, exact 0, NS 2, pockets 19) | DEAD | 944 |
| k5_11_interior_Y0290 | zero | 2 (tree: 140 nodes, depth 7, CC 0, exact 0, NS 2, pockets 19) | DEAD (s0-only, WINDOW-PENDING) | 780 |
| k5_11_interior_Y0186 | g1 | 2 (tree: 201 nodes, depth 7, CC 3, exact 0, NS 8, pockets 43) | DEAD | 1734 |
| k5_11_interior_Y0186 | zero | 2 (tree: 200 nodes, depth 7, CC 4, exact 0, NS 5, pockets 43) | DEAD (s0-only, WINDOW-PENDING) | 1494 |
| k5_11_interior_Y0280 | g1 | 2 (tree: 210 nodes, depth 10, CC 12, exact 0, NS 6, pockets 29) | DEAD | 1618 |
| k5_11_interior_Y0280 | zero | 2 (tree: 208 nodes, depth 9, CC 15, exact 0, NS 6, pockets 29) | DEAD (s0-only, WINDOW-PENDING) | 1385 |
| k5_11_interior_Y0376 | g1 | 2 (tree: 62 nodes, depth 4, CC 2, exact 0, NS 0, pockets 1) | DEAD | 189 |
| k5_11_interior_Y0376 | zero | 2 (tree: 59 nodes, depth 4, CC 0, exact 0, NS 0, pockets 1) | DEAD (s0-only, WINDOW-PENDING) | 161 |
| k5_11_interior_Y0321 | g1 | 2 (tree: 225 nodes, depth 9, CC 9, exact 0, NS 11, pockets 44) | ALIVE (wall) | 1804 |
| k5_11_interior_Y0321 | zero | 2 (tree: 242 nodes, depth 8, CC 7, exact 0, NS 12, pockets 49) | ALIVE (wall) | 1801 |
| k5_11_interior_Y0355 | g1 | 2 (tree: 222 nodes, depth 8, CC 8, exact 0, NS 10, pockets 44) | ALIVE (wall) | 1800 |
| k5_11_interior_Y0355 | zero | 2 (tree: 241 nodes, depth 7, CC 9, exact 0, NS 12, pockets 47) | ALIVE (wall) | 1804 |
| k5_11_interior_Y0380 | g1 | 2 (tree: 78 nodes, depth 8, CC 2, exact 0, NS 6, pockets 8) | DEAD | 396 |
| k5_11_interior_Y0380 | zero | 2 (tree: 70 nodes, depth 8, CC 3, exact 0, NS 4, pockets 7) | DEAD (s0-only, WINDOW-PENDING) | 343 |
| k5_11_interior_Y0414 | g1 | 2 (tree: 73 nodes, depth 8, CC 7, exact 0, NS 5, pockets 7) | DEAD | 333 |
| k5_11_interior_Y0414 | zero | 2 (tree: 70 nodes, depth 8, CC 5, exact 0, NS 4, pockets 6) | DEAD (s0-only, WINDOW-PENDING) | 278 |
| k5_11_interior_Y0391 | g1 | 2 (tree: 166 nodes, depth 6, CC 3, exact 0, NS 1, pockets 12) | DEAD | 629 |
| k5_11_interior_Y0391 | zero | 2 (tree: 150 nodes, depth 6, CC 4, exact 0, NS 1, pockets 8) | DEAD (s0-only, WINDOW-PENDING) | 462 |
| k5_11_interior_Y0422 | g1 | 2 (tree: 57 nodes, depth 7, CC 2, exact 0, NS 4, pockets 6) | DEAD | 270 |
| k5_11_interior_Y0422 | zero | 2 (tree: 44 nodes, depth 5, CC 0, exact 0, NS 1, pockets 3) | DEAD (s0-only, WINDOW-PENDING) | 184 |
| k5_11_interior_Y0452 | g1 | 2 (tree: 42 nodes, depth 5, CC 3, exact 0, NS 0, pockets 3) | DEAD | 144 |
| k5_11_interior_Y0452 | zero | 2 (tree: 32 nodes, depth 4, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 69 |
| k5_11_interior_Y0486 | g1 | 2 (tree: 3 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD | 4 |
| k5_11_interior_Y0486 | zero | 2 (tree: 3 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 8 |
| k5_11_interior_Y0460 | g1 | 2 (tree: 54 nodes, depth 7, CC 2, exact 0, NS 3, pockets 4) | DEAD | 259 |
| k5_11_interior_Y0460 | zero | 2 (tree: 47 nodes, depth 7, CC 1, exact 0, NS 3, pockets 4) | DEAD (s0-only, WINDOW-PENDING) | 202 |
| k5_11_interior_Y0489 | g1 | 2 (tree: 85 nodes, depth 5, CC 3, exact 0, NS 0, pockets 3) | DEAD | 288 |
| k5_11_interior_Y0489 | zero | 2 (tree: 78 nodes, depth 5, CC 0, exact 0, NS 0, pockets 3) | DEAD (s0-only, WINDOW-PENDING) | 245 |
| k5_11_interior_Y0384 | g1 | 2 (tree: 252 nodes, depth 10, CC 11, exact 0, NS 8, pockets 34) | ALIVE (wall) | 1823 |
| k5_11_interior_Y0384 | zero | 2 (tree: 281 nodes, depth 10, CC 13, exact 0, NS 8, pockets 41) | DEAD (s0-only, WINDOW-PENDING) | 1799 |
| k5_11_interior_Y0466 | g1 | 2 (tree: 160 nodes, depth 6, CC 2, exact 1, NS 1, pockets 11) | DEAD | 627 |
| k5_11_interior_Y0466 | zero | 2 (tree: 150 nodes, depth 6, CC 4, exact 0, NS 1, pockets 9) | DEAD (s0-only, WINDOW-PENDING) | 477 |
| k5_11_interior_Y0454 | g1 | 2 (tree: 159 nodes, depth 7, CC 4, exact 0, NS 5, pockets 32) | DEAD | 1206 |
| k5_11_interior_Y0454 | zero | 2 (tree: 155 nodes, depth 7, CC 3, exact 0, NS 4, pockets 30) | DEAD (s0-only, WINDOW-PENDING) | 1014 |
| k5_11_interior_Y0495 | zero | 2 (tree: 219 nodes, depth 9, CC 10, exact 1, NS 9, pockets 31) | DEAD (s0-only, WINDOW-PENDING) | 1346 |
| k5_11_interior_Y0513 | zero | 2 (tree: 194 nodes, depth 9, CC 18, exact 0, NS 7, pockets 23) | DEAD (s0-only, WINDOW-PENDING) | 1166 |
| k5_11_interior_Y0570 | g1 | 2 (tree: 9 nodes, depth 2, CC 0, exact 0, NS 0, pockets 0) | DEAD | 8 |
| k5_11_interior_Y0570 | zero | 2 (tree: 8 nodes, depth 2, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 16 |
| k5_11_interior_Y0517 | zero | 2 (tree: 257 nodes, depth 9, CC 25, exact 0, NS 18, pockets 39) | ALIVE (wall) | 1805 |
| k5_11_interior_Y0574 | g1 | 2 (tree: 84 nodes, depth 4, CC 4, exact 0, NS 0, pockets 1) | DEAD | 288 |
| k5_11_interior_Y0574 | zero | 2 (tree: 79 nodes, depth 4, CC 6, exact 0, NS 0, pockets 1) | DEAD (s0-only, WINDOW-PENDING) | 228 |

CPU-h in this block: 48.20

## Price and projection

* gallery: 17 / 18 pages DEAD at the window pad, 8.84 CPU-h
* frontier: 84 nodes run (45 DEAD at the window pad), 48.20 CPU-h; the census has 255 alive nodes, 219 remaining
* PRICE over the first 20 frontier nodes: mean 2999 s, median 3677 s per node (both pads); PROJECTION for the remaining 219: 182.4 CPU-h (cap 200)

