# A211 progress -- 2026-09-16 16:22:47

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

## The k5 frontier (A57 census, deepest-first) (289 nodes)

| page | pad | stage reached | verdict | seconds |
|---|---|---|---|---|
| k5_11_interior_Y0186_D00_D00 | g1 | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD | 6 |
| k5_11_interior_Y0186_D00_D00 | zero | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 7 |
| k5_11_interior_Y0127_D04 | g1 | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD | 6 |
| k5_11_interior_Y0127_D04 | zero | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 7 |
| k5_11_interior_Y0036_D07 | g1 | 2 (tree: 28 nodes, depth 2, CC 2, exact 0, NS 0, pockets 0) | DEAD | 189 |
| k5_11_interior_Y0036_D07 | zero | 2 (tree: 26 nodes, depth 2, CC 2, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 142 |
| k5_11_interior_Y0105_D03 | g1 | 2 (tree: 40 nodes, depth 3, CC 1, exact 0, NS 0, pockets 5) | DEAD | 254 |
| k5_11_interior_Y0105_D03 | zero | 2 (tree: 35 nodes, depth 4, CC 1, exact 0, NS 0, pockets 3) | DEAD (s0-only, WINDOW-PENDING) | 186 |
| k5_11_interior_Y0186_D00 | g1 | 2 (tree: 169 nodes, depth 7, CC 3, exact 0, NS 6, pockets 36) | DEAD | 1420 |
| k5_11_interior_Y0186_D00 | zero | 2 (tree: 171 nodes, depth 7, CC 4, exact 0, NS 8, pockets 34) | DEAD (s0-only, WINDOW-PENDING) | 1321 |
| k5_11_interior_Y0186_D01 | g1 | 2 (tree: 72 nodes, depth 4, CC 3, exact 0, NS 0, pockets 13) | DEAD | 627 |
| k5_11_interior_Y0186_D01 | zero | 2 (tree: 71 nodes, depth 4, CC 2, exact 0, NS 0, pockets 13) | DEAD (s0-only, WINDOW-PENDING) | 625 |
| k5_11_interior_Y0217_D02 | g1 | 2 (tree: 41 nodes, depth 4, CC 3, exact 0, NS 0, pockets 4) | DEAD | 303 |
| k5_11_interior_Y0217_D02 | zero | 2 (tree: 36 nodes, depth 3, CC 3, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 224 |
| k5_11_interior_Y0217_D03 | g1 | 2 (tree: 43 nodes, depth 4, CC 2, exact 0, NS 0, pockets 2) | DEAD | 248 |
| k5_11_interior_Y0217_D03 | zero | 2 (tree: 40 nodes, depth 3, CC 4, exact 0, NS 2, pockets 1) | DEAD (s0-only, WINDOW-PENDING) | 202 |
| k5_11_interior_Y0217_D06 | g1 | 2 (tree: 62 nodes, depth 5, CC 3, exact 0, NS 7, pockets 6) | DEAD | 372 |
| k5_11_interior_Y0217_D06 | zero | 2 (tree: 58 nodes, depth 4, CC 6, exact 0, NS 4, pockets 2) | DEAD (s0-only, WINDOW-PENDING) | 316 |
| k5_11_interior_Y0217_D07 | g1 | 2 (tree: 59 nodes, depth 5, CC 3, exact 0, NS 4, pockets 7) | DEAD | 403 |
| k5_11_interior_Y0217_D07 | zero | 2 (tree: 35 nodes, depth 3, CC 2, exact 0, NS 0, pockets 2) | DEAD (s0-only, WINDOW-PENDING) | 197 |
| k5_11_interior_Y0256_D03 | g1 | 2 (tree: 55 nodes, depth 4, CC 1, exact 0, NS 4, pockets 6) | DEAD | 343 |
| k5_11_interior_Y0256_D03 | zero | 2 (tree: 37 nodes, depth 3, CC 2, exact 0, NS 0, pockets 2) | DEAD (s0-only, WINDOW-PENDING) | 194 |
| k5_11_interior_Y0256_D06 | g1 | 2 (tree: 65 nodes, depth 5, CC 4, exact 0, NS 5, pockets 4) | DEAD | 361 |
| k5_11_interior_Y0256_D06 | zero | 2 (tree: 59 nodes, depth 4, CC 5, exact 0, NS 5, pockets 3) | DEAD (s0-only, WINDOW-PENDING) | 304 |
| k5_11_interior_Y0256_D07 | g1 | 2 (tree: 54 nodes, depth 4, CC 4, exact 0, NS 0, pockets 6) | DEAD | 319 |
| k5_11_interior_Y0256_D07 | zero | 2 (tree: 49 nodes, depth 4, CC 5, exact 0, NS 4, pockets 2) | DEAD (s0-only, WINDOW-PENDING) | 273 |
| k5_11_interior_Y0376_D06 | g1 | 2 (tree: 15 nodes, depth 2, CC 0, exact 0, NS 0, pockets 0) | DEAD | 55 |
| k5_11_interior_Y0376_D06 | zero | 2 (tree: 19 nodes, depth 2, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 77 |
| k5_11_interior_Y0384_D00 | g1 | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD | 6 |
| k5_11_interior_Y0384_D00 | zero | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 6 |
| k5_11_interior_Y0636_D05 | g1 | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD | 6 |
| k5_11_interior_Y0636_D05 | zero | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 5 |
| k5_11_interior_Y0414_D03 | g1 | 2 (tree: 29 nodes, depth 4, CC 4, exact 0, NS 0, pockets 2) | DEAD | 125 |
| k5_11_interior_Y0414_D03 | zero | 2 (tree: 27 nodes, depth 3, CC 2, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 224 |
| k5_11_interior_Y0414_D07 | g1 | 2 (tree: 59 nodes, depth 6, CC 4, exact 0, NS 7, pockets 5) | DEAD | 345 |
| k5_11_interior_Y0414_D07 | zero | 2 (tree: 50 nodes, depth 4, CC 2, exact 0, NS 2, pockets 2) | DEAD (s0-only, WINDOW-PENDING) | 240 |
| k5_11_interior_Y0414_D06 | g1 | 2 (tree: 45 nodes, depth 4, CC 1, exact 0, NS 1, pockets 2) | DEAD | 227 |
| k5_11_interior_Y0414_D06 | zero | 2 (tree: 27 nodes, depth 2, CC 0, exact 0, NS 0, pockets 1) | DEAD (s0-only, WINDOW-PENDING) | 148 |
| k5_11_interior_Y0636_D06 | g1 | 2 (tree: 41 nodes, depth 3, CC 3, exact 0, NS 0, pockets 1) | DEAD | 246 |
| k5_11_interior_Y0636_D06 | zero | 2 (tree: 39 nodes, depth 3, CC 3, exact 0, NS 0, pockets 1) | DEAD (s0-only, WINDOW-PENDING) | 180 |
| k5_11_interior_Y0738_D00 | g1 | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD | 0 |
| k5_11_interior_Y0738_D00 | zero | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 1 |
| k5_11_interior_Y0738_D02 | g1 | 2 (tree: 38 nodes, depth 9, CC 2, exact 0, NS 7, pockets 1) | ALIVE (wall) | 1801 |
| k5_11_interior_Y0738_D02 | zero | 2 (tree: 41 nodes, depth 8, CC 2, exact 0, NS 7, pockets 1) | ALIVE (wall) | 1814 |
| k5_11_interior_Y0738_D01 | g1 | 2 (tree: 39 nodes, depth 9, CC 4, exact 0, NS 6, pockets 1) | ALIVE (wall) | 1802 |
| k5_11_interior_Y0738_D01 | zero | 2 (tree: 41 nodes, depth 7, CC 4, exact 0, NS 8, pockets 1) | ALIVE (wall) | 1859 |
| k5_11_interior_Y0738_D03 | g1 | 2 (tree: 42 nodes, depth 11, CC 5, exact 0, NS 5, pockets 1) | ALIVE (wall) | 1805 |
| k5_11_interior_Y0738_D03 | zero | 2 (tree: 37 nodes, depth 8, CC 5, exact 0, NS 8, pockets 1) | ALIVE (wall) | 1842 |
| k5_11_interior_Y0864_D07 | g1 | 2 (tree: 200 nodes, depth 7, CC 6, exact 0, NS 15, pockets 41) | DEAD | 1701 |
| k5_11_interior_Y0864_D07 | zero | 2 (tree: 176 nodes, depth 7, CC 2, exact 0, NS 8, pockets 33) | DEAD (s0-only, WINDOW-PENDING) | 1328 |
| k5_11_interior_Y0954_D00 | g1 | 2 (tree: 151 nodes, depth 8, CC 4, exact 0, NS 7, pockets 21) | DEAD | 1109 |
| k5_11_interior_Y0954_D00 | zero | 2 (tree: 141 nodes, depth 8, CC 5, exact 0, NS 7, pockets 21) | DEAD (s0-only, WINDOW-PENDING) | 987 |
| k5_11_interior_Y0954_D01 | g1 | 2 (tree: 168 nodes, depth 9, CC 2, exact 0, NS 11, pockets 25) | DEAD | 1301 |
| k5_11_interior_Y0954_D01 | zero | 2 (tree: 142 nodes, depth 8, CC 1, exact 0, NS 10, pockets 23) | DEAD (s0-only, WINDOW-PENDING) | 983 |
| k5_11_interior_Y0978_D04 | g1 | 2 (tree: 87 nodes, depth 7, CC 8, exact 0, NS 9, pockets 2) | DEAD | 1379 |
| k5_11_interior_Y0978_D04 | zero | 2 (tree: 82 nodes, depth 6, CC 3, exact 0, NS 5, pockets 2) | DEAD (s0-only, WINDOW-PENDING) | 829 |
| k5_11_interior_Y0954_D02 | g1 | 2 (tree: 139 nodes, depth 8, CC 3, exact 0, NS 6, pockets 28) | DEAD | 1046 |
| k5_11_interior_Y0954_D02 | zero | 2 (tree: 114 nodes, depth 8, CC 3, exact 0, NS 5, pockets 25) | DEAD (s0-only, WINDOW-PENDING) | 910 |
| k5_11_interior_Y0978_D07 | g1 | 2 (tree: 55 nodes, depth 6, CC 3, exact 0, NS 6, pockets 6) | DEAD | 344 |
| k5_11_interior_Y0978_D07 | zero | 2 (tree: 43 nodes, depth 4, CC 1, exact 0, NS 4, pockets 2) | DEAD (s0-only, WINDOW-PENDING) | 196 |
| k5_11_interior_Y1069_D06 | g1 | 2 (tree: 143 nodes, depth 7, CC 7, exact 0, NS 10, pockets 33) | DEAD | 1176 |
| k5_11_interior_Y1069_D06 | zero | 2 (tree: 145 nodes, depth 7, CC 7, exact 0, NS 10, pockets 35) | DEAD (s0-only, WINDOW-PENDING) | 1129 |
| k5_11_interior_Y1128_D06 | g1 | 2 (tree: 134 nodes, depth 4, CC 9, exact 0, NS 2, pockets 27) | DEAD | 1181 |
| k5_11_interior_Y1128_D06 | zero | 2 (tree: 133 nodes, depth 4, CC 9, exact 0, NS 2, pockets 29) | DEAD (s0-only, WINDOW-PENDING) | 1109 |
| k5_11_interior_Y1128_D07 | g1 | 2 (tree: 87 nodes, depth 4, CC 2, exact 0, NS 0, pockets 15) | DEAD | 705 |
| k5_11_interior_Y1128_D07 | zero | 2 (tree: 83 nodes, depth 4, CC 1, exact 0, NS 0, pockets 14) | DEAD (s0-only, WINDOW-PENDING) | 690 |
| k5_11_interior_Y1141_D00 | g1 | 2 (tree: 8 nodes, depth 1, CC 2, exact 0, NS 0, pockets 0) | DEAD | 26 |
| k5_11_interior_Y1141_D00 | zero | 2 (tree: 8 nodes, depth 1, CC 2, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 31 |
| k5_11_interior_Y1141_D01 | g1 | 2 (tree: 5 nodes, depth 1, CC 0, exact 0, NS 0, pockets 0) | DEAD | 4 |
| k5_11_interior_Y1141_D01 | zero | 2 (tree: 5 nodes, depth 1, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 7 |
| k5_11_interior_Y1141_D04 | g1 | 0 | DEAD | 30 |
| k5_11_interior_Y1141_D04 | zero | 0 | DEAD (s0-only, WINDOW-PENDING) | 27 |
| k5_11_interior_Y0033 | g1 | 2 (tree: 7 nodes, depth 1, CC 0, exact 0, NS 0, pockets 0) | DEAD | 37 |
| k5_11_interior_Y0033 | zero | 2 (tree: 145 nodes, depth 6, CC 2, exact 1, NS 1, pockets 11) | DEAD (s0-only, WINDOW-PENDING) | 1268 |
| k5_11_interior_Y0036 | g1 | 2 (tree: 73 nodes, depth 5, CC 1, exact 0, NS 2, pockets 3) | DEAD | 472 |
| k5_11_interior_Y0036 | zero | 2 (tree: 74 nodes, depth 5, CC 1, exact 0, NS 1, pockets 2) | DEAD (s0-only, WINDOW-PENDING) | 392 |
| k5_11_interior_Y0039 | g1 | 2 (tree: 87 nodes, depth 7, CC 0, exact 0, NS 10, pockets 11) | DEAD | 579 |
| k5_11_interior_Y0039 | zero | 2 (tree: 82 nodes, depth 7, CC 1, exact 0, NS 12, pockets 10) | DEAD (s0-only, WINDOW-PENDING) | 632 |
| k5_11_interior_Y0041 | g1 | 2 (tree: 161 nodes, depth 7, CC 4, exact 0, NS 1, pockets 13) | DEAD | 1575 |
| k5_11_interior_Y0041 | zero | 2 (tree: 144 nodes, depth 6, CC 3, exact 0, NS 1, pockets 12) | DEAD (s0-only, WINDOW-PENDING) | 1278 |
| k5_11_interior_Y0044 | g1 | 2 (tree: 75 nodes, depth 5, CC 2, exact 0, NS 0, pockets 5) | DEAD | 647 |
| k5_11_interior_Y0044 | zero | 2 (tree: 76 nodes, depth 5, CC 2, exact 0, NS 1, pockets 5) | DEAD (s0-only, WINDOW-PENDING) | 578 |
| k5_11_interior_Y0054 | g1 | 2 (tree: 66 nodes, depth 7, CC 4, exact 0, NS 4, pockets 8) | DEAD | 1104 |
| k5_11_interior_Y0054 | zero | 2 (tree: 62 nodes, depth 7, CC 3, exact 0, NS 3, pockets 6) | DEAD (s0-only, WINDOW-PENDING) | 744 |
| k5_11_interior_Y0069 | g1 | 2 (tree: 72 nodes, depth 7, CC 2, exact 0, NS 4, pockets 11) | DEAD | 1187 |
| k5_11_interior_Y0069 | zero | 2 (tree: 65 nodes, depth 7, CC 3, exact 0, NS 4, pockets 6) | DEAD (s0-only, WINDOW-PENDING) | 857 |
| k5_11_interior_Y0072 | g1 | 2 (tree: 25 nodes, depth 5, CC 0, exact 0, NS 3, pockets 2) | DEAD | 164 |
| k5_11_interior_Y0072 | zero | 2 (tree: 144 nodes, depth 6, CC 2, exact 0, NS 1, pockets 11) | DEAD (s0-only, WINDOW-PENDING) | 1338 |
| k5_11_interior_Y0084 | g1 | 2 (tree: 5 nodes, depth 0, CC 1, exact 0, NS 0, pockets 0) | DEAD | 89 |
| k5_11_interior_Y0084 | zero | 2 (tree: 20 nodes, depth 5, CC 0, exact 0, NS 1, pockets 2) | DEAD (s0-only, WINDOW-PENDING) | 146 |
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
| k5_11_interior_Y0127 | g1 | 2 (tree: 65 nodes, depth 7, CC 1, exact 0, NS 3, pockets 11) | DEAD | 504 |
| k5_11_interior_Y0127 | zero | 2 (tree: 59 nodes, depth 7, CC 1, exact 0, NS 3, pockets 8) | DEAD (s0-only, WINDOW-PENDING) | 406 |
| k5_11_interior_Y0133 | g1 | 2 (tree: 54 nodes, depth 3, CC 0, exact 0, NS 0, pockets 11) | DEAD | 470 |
| k5_11_interior_Y0133 | zero | 2 (tree: 45 nodes, depth 3, CC 0, exact 0, NS 0, pockets 9) | DEAD (s0-only, WINDOW-PENDING) | 409 |
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
| k5_11_interior_Y0321 | g1 | 2 (tree: 53 nodes, depth 7, CC 0, exact 0, NS 7, pockets 7) | DEAD | 386 |
| k5_11_interior_Y0321 | zero | 2 (tree: 3 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 44 |
| k5_11_interior_Y0355 | g1 | 2 (tree: 54 nodes, depth 7, CC 0, exact 0, NS 7, pockets 6) | DEAD | 391 |
| k5_11_interior_Y0355 | zero | 2 (tree: 11 nodes, depth 2, CC 0, exact 0, NS 0, pockets 1) | DEAD (s0-only, WINDOW-PENDING) | 106 |
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
| k5_11_interior_Y0384 | g1 | 2 (tree: 42 nodes, depth 3, CC 0, exact 0, NS 0, pockets 6) | DEAD | 374 |
| k5_11_interior_Y0384 | zero | 2 (tree: 281 nodes, depth 10, CC 13, exact 0, NS 8, pockets 41) | DEAD (s0-only, WINDOW-PENDING) | 1799 |
| k5_11_interior_Y0466 | g1 | 2 (tree: 160 nodes, depth 6, CC 2, exact 1, NS 1, pockets 11) | DEAD | 627 |
| k5_11_interior_Y0466 | zero | 2 (tree: 150 nodes, depth 6, CC 4, exact 0, NS 1, pockets 9) | DEAD (s0-only, WINDOW-PENDING) | 477 |
| k5_11_interior_Y0454 | g1 | 2 (tree: 159 nodes, depth 7, CC 4, exact 0, NS 5, pockets 32) | DEAD | 1206 |
| k5_11_interior_Y0454 | zero | 2 (tree: 155 nodes, depth 7, CC 3, exact 0, NS 4, pockets 30) | DEAD (s0-only, WINDOW-PENDING) | 1014 |
| k5_11_interior_Y0495 | g1 | 2 (tree: 6 nodes, depth 2, CC 2, exact 0, NS 0, pockets 2) | DEAD | 104 |
| k5_11_interior_Y0495 | zero | 2 (tree: 219 nodes, depth 9, CC 10, exact 1, NS 9, pockets 31) | DEAD (s0-only, WINDOW-PENDING) | 1346 |
| k5_11_interior_Y0513 | g1 | 2 (tree: 205 nodes, depth 10, CC 16, exact 0, NS 8, pockets 28) | DEAD | 1671 |
| k5_11_interior_Y0513 | zero | 2 (tree: 194 nodes, depth 9, CC 18, exact 0, NS 7, pockets 23) | DEAD (s0-only, WINDOW-PENDING) | 1166 |
| k5_11_interior_Y0570 | g1 | 2 (tree: 9 nodes, depth 2, CC 0, exact 0, NS 0, pockets 0) | DEAD | 8 |
| k5_11_interior_Y0570 | zero | 2 (tree: 8 nodes, depth 2, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 16 |
| k5_11_interior_Y0517 | g1 | 2 (tree: 177 nodes, depth 7, CC 2, exact 0, NS 33, pockets 24) | DEAD | 1350 |
| k5_11_interior_Y0517 | zero | 2 (tree: 109 nodes, depth 7, CC 0, exact 0, NS 7, pockets 17) | DEAD (s0-only, WINDOW-PENDING) | 746 |
| k5_11_interior_Y0574 | g1 | 2 (tree: 84 nodes, depth 4, CC 4, exact 0, NS 0, pockets 1) | DEAD | 288 |
| k5_11_interior_Y0574 | zero | 2 (tree: 79 nodes, depth 4, CC 6, exact 0, NS 0, pockets 1) | DEAD (s0-only, WINDOW-PENDING) | 228 |
| k5_11_interior_Y0579 | g1 | 2 (tree: 55 nodes, depth 7, CC 1, exact 0, NS 3, pockets 8) | DEAD | 293 |
| k5_11_interior_Y0579 | zero | 2 (tree: 45 nodes, depth 4, CC 1, exact 0, NS 0, pockets 4) | DEAD (s0-only, WINDOW-PENDING) | 216 |
| k5_11_interior_Y0588 | g1 | 2 (tree: 21 nodes, depth 2, CC 3, exact 0, NS 0, pockets 0) | DEAD | 41 |
| k5_11_interior_Y0588 | zero | 2 (tree: 19 nodes, depth 2, CC 3, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 36 |
| k5_11_interior_Y0559 | g1 | 2 (tree: 68 nodes, depth 4, CC 0, exact 0, NS 2, pockets 17) | DEAD | 634 |
| k5_11_interior_Y0559 | zero | 2 (tree: 7 nodes, depth 2, CC 0, exact 0, NS 0, pockets 1) | DEAD (s0-only, WINDOW-PENDING) | 46 |
| k5_11_interior_Y0597 | g1 | 2 (tree: 89 nodes, depth 8, CC 6, exact 0, NS 4, pockets 9) | DEAD | 472 |
| k5_11_interior_Y0597 | zero | 2 (tree: 91 nodes, depth 8, CC 6, exact 0, NS 5, pockets 10) | DEAD (s0-only, WINDOW-PENDING) | 442 |
| k5_11_interior_Y0636 | g1 | 2 (tree: 54 nodes, depth 3, CC 4, exact 0, NS 0, pockets 1) | DEAD | 232 |
| k5_11_interior_Y0636 | zero | 2 (tree: 79 nodes, depth 5, CC 4, exact 0, NS 0, pockets 2) | DEAD (s0-only, WINDOW-PENDING) | 225 |
| k5_11_interior_Y0628 | g1 | 2 (tree: 212 nodes, depth 7, CC 3, exact 0, NS 7, pockets 52) | DEAD | 1441 |
| k5_11_interior_Y0628 | zero | 2 (tree: 7 nodes, depth 1, CC 0, exact 0, NS 0, pockets 1) | DEAD (s0-only, WINDOW-PENDING) | 95 |
| k5_11_interior_Y0596 | g1 | 2 (tree: 261 nodes, depth 10, CC 18, exact 0, NS 8, pockets 39) | ALIVE (wall) | 1800 |
| k5_11_interior_Y0596 | zero | 2 (tree: 41 nodes, depth 3, CC 0, exact 0, NS 0, pockets 9) | DEAD (s0-only, WINDOW-PENDING) | 433 |
| k5_11_interior_Y0644 | g1 | 2 (tree: 85 nodes, depth 8, CC 5, exact 0, NS 6, pockets 9) | DEAD | 425 |
| k5_11_interior_Y0644 | zero | 2 (tree: 95 nodes, depth 8, CC 4, exact 0, NS 5, pockets 9) | DEAD (s0-only, WINDOW-PENDING) | 384 |
| k5_11_interior_Y0646 | g1 | 2 (tree: 29 nodes, depth 4, CC 0, exact 0, NS 0, pockets 3) | DEAD | 140 |
| k5_11_interior_Y0646 | zero | 2 (tree: 28 nodes, depth 4, CC 0, exact 0, NS 0, pockets 3) | DEAD (s0-only, WINDOW-PENDING) | 138 |
| k5_11_interior_Y0652 | g1 | 2 (tree: 54 nodes, depth 8, CC 4, exact 0, NS 1, pockets 4) | DEAD | 193 |
| k5_11_interior_Y0652 | zero | 2 (tree: 56 nodes, depth 8, CC 7, exact 0, NS 1, pockets 3) | DEAD (s0-only, WINDOW-PENDING) | 216 |
| k5_11_interior_Y0668 | g1 | 2 (tree: 72 nodes, depth 6, CC 5, exact 0, NS 4, pockets 8) | DEAD | 338 |
| k5_11_interior_Y0668 | zero | 2 (tree: 66 nodes, depth 6, CC 4, exact 0, NS 3, pockets 5) | DEAD (s0-only, WINDOW-PENDING) | 255 |
| k5_11_interior_Y0657 | g1 | 2 (tree: 127 nodes, depth 6, CC 3, exact 0, NS 1, pockets 23) | DEAD | 842 |
| k5_11_interior_Y0657 | zero | 2 (tree: 123 nodes, depth 7, CC 2, exact 0, NS 1, pockets 23) | DEAD (s0-only, WINDOW-PENDING) | 716 |
| k5_11_interior_Y0691 | g1 | 2 (tree: 54 nodes, depth 7, CC 1, exact 0, NS 4, pockets 4) | DEAD | 216 |
| k5_11_interior_Y0691 | zero | 2 (tree: 47 nodes, depth 7, CC 1, exact 0, NS 4, pockets 4) | DEAD (s0-only, WINDOW-PENDING) | 200 |
| k5_11_interior_Y0674 | g1 | 2 (tree: 195 nodes, depth 7, CC 6, exact 0, NS 7, pockets 39) | DEAD | 1418 |
| k5_11_interior_Y0674 | zero | 2 (tree: 193 nodes, depth 7, CC 6, exact 0, NS 7, pockets 37) | DEAD (s0-only, WINDOW-PENDING) | 1222 |
| k5_11_interior_Y0735 | g1 | 2 (tree: 27 nodes, depth 3, CC 0, exact 0, NS 0, pockets 2) | DEAD | 68 |
| k5_11_interior_Y0735 | zero | 2 (tree: 26 nodes, depth 3, CC 0, exact 0, NS 0, pockets 2) | DEAD (s0-only, WINDOW-PENDING) | 70 |
| k5_11_interior_Y0709 | g1 | 2 (tree: 94 nodes, depth 6, CC 1, exact 0, NS 1, pockets 4) | DEAD | 341 |
| k5_11_interior_Y0709 | zero | 2 (tree: 91 nodes, depth 5, CC 1, exact 0, NS 0, pockets 4) | DEAD (s0-only, WINDOW-PENDING) | 268 |
| k5_11_interior_Y0722 | g1 | 2 (tree: 87 nodes, depth 8, CC 5, exact 0, NS 4, pockets 8) | DEAD | 416 |
| k5_11_interior_Y0722 | zero | 2 (tree: 92 nodes, depth 8, CC 4, exact 0, NS 4, pockets 9) | DEAD (s0-only, WINDOW-PENDING) | 377 |
| k5_11_interior_Y0752 | g1 | 2 (tree: 46 nodes, depth 7, CC 1, exact 0, NS 3, pockets 4) | DEAD | 172 |
| k5_11_interior_Y0752 | zero | 2 (tree: 43 nodes, depth 7, CC 1, exact 0, NS 3, pockets 4) | DEAD (s0-only, WINDOW-PENDING) | 152 |
| k5_11_interior_Y0828 | g1 | 2 (tree: 3 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD | 3 |
| k5_11_interior_Y0828 | zero | 2 (tree: 3 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 6 |
| k5_11_interior_Y0791 | g1 | 2 (tree: 17 nodes, depth 4, CC 0, exact 0, NS 0, pockets 0) | DEAD | 28 |
| k5_11_interior_Y0791 | zero | 2 (tree: 15 nodes, depth 3, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 32 |
| k5_11_interior_Y0682 | g1 | 2 (tree: 221 nodes, depth 8, CC 1, exact 0, NS 5, pockets 46) | ALIVE (wall) | 1806 |
| k5_11_interior_Y0682 | zero | 2 (tree: 260 nodes, depth 8, CC 2, exact 0, NS 9, pockets 53) | DEAD (s0-only, WINDOW-PENDING) | 1692 |
| k5_11_interior_Y0839 | g1 | 2 (tree: 62 nodes, depth 5, CC 0, exact 0, NS 0, pockets 9) | DEAD | 366 |
| k5_11_interior_Y0839 | zero | 2 (tree: 61 nodes, depth 5, CC 0, exact 0, NS 0, pockets 9) | DEAD (s0-only, WINDOW-PENDING) | 354 |
| k5_11_interior_Y0854 | g1 | 2 (tree: 11 nodes, depth 1, CC 3, exact 0, NS 0, pockets 0) | DEAD | 24 |
| k5_11_interior_Y0854 | zero | 2 (tree: 10 nodes, depth 1, CC 3, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 26 |
| k5_11_interior_Y0842 | g1 | 2 (tree: 139 nodes, depth 9, CC 4, exact 0, NS 2, pockets 22) | DEAD | 932 |
| k5_11_interior_Y0842 | zero | 2 (tree: 129 nodes, depth 7, CC 4, exact 0, NS 3, pockets 21) | DEAD (s0-only, WINDOW-PENDING) | 861 |
| k5_11_interior_Y0848 | g1 | 2 (tree: 219 nodes, depth 9, CC 14, exact 0, NS 10, pockets 47) | DEAD | 1742 |
| k5_11_interior_Y0848 | zero | 2 (tree: 214 nodes, depth 7, CC 14, exact 0, NS 11, pockets 44) | DEAD (s0-only, WINDOW-PENDING) | 1448 |
| k5_11_interior_Y0866 | g1 | 2 (tree: 2 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD | 3 |
| k5_11_interior_Y0866 | zero | 2 (tree: 2 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 4 |
| k5_11_interior_Y0865 | g1 | 2 (tree: 200 nodes, depth 10, CC 12, exact 0, NS 8, pockets 25) | DEAD | 1390 |
| k5_11_interior_Y0865 | zero | 2 (tree: 191 nodes, depth 10, CC 10, exact 0, NS 6, pockets 23) | DEAD (s0-only, WINDOW-PENDING) | 1106 |
| k5_11_interior_Y0943 | g1 | 2 (tree: 23 nodes, depth 2, CC 4, exact 0, NS 0, pockets 0) | DEAD | 49 |
| k5_11_interior_Y0943 | zero | 2 (tree: 15 nodes, depth 2, CC 1, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 31 |
| k5_11_interior_Y0864 | g1 | 2 (tree: 208 nodes, depth 8, CC 6, exact 0, NS 7, pockets 41) | DEAD | 1526 |
| k5_11_interior_Y0864 | zero | 2 (tree: 211 nodes, depth 8, CC 5, exact 0, NS 7, pockets 40) | DEAD (s0-only, WINDOW-PENDING) | 1329 |
| k5_11_interior_Y0929 | g1 | 2 (tree: 260 nodes, depth 11, CC 25, exact 0, NS 9, pockets 31) | ALIVE (wall) | 1810 |
| k5_11_interior_Y0929 | zero | 2 (tree: 239 nodes, depth 10, CC 21, exact 0, NS 10, pockets 32) | DEAD (s0-only, WINDOW-PENDING) | 1379 |
| k5_11_interior_Y0977 | g1 | 2 (tree: 4 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD | 11 |
| k5_11_interior_Y0977 | zero | 2 (tree: 4 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 18 |
| k5_11_interior_Y0978 | g1 | 2 (tree: 80 nodes, depth 8, CC 5, exact 0, NS 4, pockets 8) | DEAD | 376 |
| k5_11_interior_Y0978 | zero | 2 (tree: 72 nodes, depth 8, CC 4, exact 0, NS 4, pockets 7) | DEAD (s0-only, WINDOW-PENDING) | 300 |
| k5_11_interior_Y0954 | g1 | 2 (tree: 221 nodes, depth 11, CC 13, exact 0, NS 9, pockets 39) | ALIVE (wall) | 1813 |
| k5_11_interior_Y0954 | zero | 2 (tree: 256 nodes, depth 10, CC 17, exact 0, NS 8, pockets 47) | ALIVE (wall) | 1806 |
| k5_11_interior_Y0976 | g1 | 2 (tree: 126 nodes, depth 7, CC 2, exact 0, NS 1, pockets 24) | DEAD | 856 |
| k5_11_interior_Y0976 | zero | 2 (tree: 113 nodes, depth 7, CC 2, exact 0, NS 1, pockets 23) | DEAD (s0-only, WINDOW-PENDING) | 751 |
| k5_11_interior_Y0988 | g1 | 2 (tree: 2 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD | 3 |
| k5_11_interior_Y0988 | zero | 2 (tree: 2 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 5 |
| k5_11_interior_Y0994 | g1 | 2 (tree: 35 nodes, depth 6, CC 2, exact 0, NS 3, pockets 4) | DEAD | 156 |
| k5_11_interior_Y0994 | zero | 2 (tree: 21 nodes, depth 3, CC 1, exact 0, NS 0, pockets 1) | DEAD (s0-only, WINDOW-PENDING) | 75 |
| k5_11_interior_Y0989 | g1 | 2 (tree: 211 nodes, depth 6, CC 3, exact 0, NS 2, pockets 41) | DEAD | 1463 |
| k5_11_interior_Y0989 | zero | 2 (tree: 195 nodes, depth 6, CC 2, exact 0, NS 2, pockets 38) | DEAD (s0-only, WINDOW-PENDING) | 1213 |
| k5_11_interior_Y0995 | g1 | 2 (tree: 21 nodes, depth 2, CC 0, exact 0, NS 0, pockets 0) | DEAD | 36 |
| k5_11_interior_Y0995 | zero | 2 (tree: 17 nodes, depth 1, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 41 |
| k5_11_interior_Y0982 | g1 | 2 (tree: 219 nodes, depth 9, CC 24, exact 0, NS 11, pockets 46) | ALIVE (wall) | 1803 |
| k5_11_interior_Y0982 | zero | 2 (tree: 252 nodes, depth 8, CC 24, exact 0, NS 12, pockets 52) | ALIVE (wall) | 1803 |
| k5_11_interior_Y1007 | g1 | 2 (tree: 40 nodes, depth 5, CC 2, exact 0, NS 0, pockets 3) | DEAD | 170 |
| k5_11_interior_Y1007 | zero | 2 (tree: 36 nodes, depth 5, CC 1, exact 0, NS 1, pockets 2) | DEAD (s0-only, WINDOW-PENDING) | 145 |
| k5_11_interior_Y0991 | g1 | 2 (tree: 174 nodes, depth 7, CC 5, exact 0, NS 6, pockets 29) | DEAD | 1233 |
| k5_11_interior_Y0991 | zero | 2 (tree: 170 nodes, depth 7, CC 6, exact 0, NS 5, pockets 26) | DEAD (s0-only, WINDOW-PENDING) | 1029 |
| k5_11_interior_Y1018 | g1 | 2 (tree: 18 nodes, depth 2, CC 1, exact 0, NS 0, pockets 0) | DEAD | 34 |
| k5_11_interior_Y1018 | zero | 2 (tree: 18 nodes, depth 2, CC 1, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 40 |
| k5_11_interior_Y1025 | g1 | 2 (tree: 3 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD | 3 |
| k5_11_interior_Y1025 | zero | 2 (tree: 3 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 8 |
| k5_11_interior_Y1051 | g1 | 2 (tree: 17 nodes, depth 3, CC 2, exact 0, NS 0, pockets 0) | DEAD | 69 |
| k5_11_interior_Y1051 | zero | 2 (tree: 29 nodes, depth 4, CC 1, exact 0, NS 0, pockets 2) | DEAD (s0-only, WINDOW-PENDING) | 152 |
| k5_11_interior_Y1031 | g1 | 2 (tree: 168 nodes, depth 7, CC 0, exact 0, NS 1, pockets 30) | DEAD | 1122 |
| k5_11_interior_Y1031 | zero | 2 (tree: 163 nodes, depth 7, CC 0, exact 0, NS 1, pockets 30) | DEAD (s0-only, WINDOW-PENDING) | 979 |
| k5_11_interior_Y1054 | g1 | 2 (tree: 23 nodes, depth 2, CC 4, exact 0, NS 0, pockets 0) | DEAD | 41 |
| k5_11_interior_Y1054 | zero | 2 (tree: 23 nodes, depth 2, CC 4, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 42 |
| k5_11_interior_Y1015 | g1 | 2 (tree: 240 nodes, depth 10, CC 8, exact 0, NS 13, pockets 41) | ALIVE (wall) | 1800 |
| k5_11_interior_Y1015 | zero | 2 (tree: 265 nodes, depth 10, CC 13, exact 0, NS 13, pockets 47) | ALIVE (wall) | 1804 |
| k5_11_interior_Y1061 | g1 | 2 (tree: 6 nodes, depth 1, CC 0, exact 0, NS 0, pockets 0) | DEAD | 15 |
| k5_11_interior_Y1061 | zero | 2 (tree: 4 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 21 |
| k5_11_interior_Y1097 | g1 | 2 (tree: 22 nodes, depth 2, CC 4, exact 0, NS 0, pockets 0) | DEAD | 49 |
| k5_11_interior_Y1097 | zero | 2 (tree: 21 nodes, depth 2, CC 4, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 45 |
| k5_11_interior_Y1056 | g1 | 2 (tree: 172 nodes, depth 8, CC 5, exact 0, NS 5, pockets 34) | DEAD | 1285 |
| k5_11_interior_Y1056 | zero | 2 (tree: 168 nodes, depth 8, CC 6, exact 0, NS 5, pockets 32) | DEAD (s0-only, WINDOW-PENDING) | 1092 |
| k5_11_interior_Y1069 | g1 | 2 (tree: 157 nodes, depth 8, CC 12, exact 0, NS 7, pockets 35) | DEAD | 1231 |
| k5_11_interior_Y1069 | zero | 2 (tree: 160 nodes, depth 8, CC 11, exact 0, NS 7, pockets 35) | DEAD (s0-only, WINDOW-PENDING) | 1113 |
| k5_11_interior_Y1057 | g1 | 2 (tree: 242 nodes, depth 10, CC 8, exact 0, NS 11, pockets 40) | ALIVE (wall) | 1802 |
| k5_11_interior_Y1057 | zero | 2 (tree: 274 nodes, depth 10, CC 6, exact 0, NS 12, pockets 48) | ALIVE (wall) | 1802 |
| k5_11_interior_Y1122 | g1 | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD | 1 |
| k5_11_interior_Y1122 | zero | 0 | DEAD (s0-only, WINDOW-PENDING) | 18 |
| k5_11_interior_Y1127 | g1 | 2 (tree: 14 nodes, depth 1, CC 0, exact 0, NS 0, pockets 0) | DEAD | 42 |
| k5_11_interior_Y1127 | zero | 2 (tree: 14 nodes, depth 1, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 42 |
| k5_11_interior_Y1103 | g1 | 2 (tree: 232 nodes, depth 11, CC 28, exact 0, NS 9, pockets 36) | ALIVE (wall) | 1801 |
| k5_11_interior_Y1103 | zero | 2 (tree: 264 nodes, depth 10, CC 21, exact 0, NS 10, pockets 48) | ALIVE (wall) | 1808 |
| k5_11_interior_Y1132 | g1 | 0 | DEAD | 19 |
| k5_11_interior_Y1132 | zero | 0 | DEAD (s0-only, WINDOW-PENDING) | 18 |
| k5_11_interior_Y1138 | g1 | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD | 0 |
| k5_11_interior_Y1138 | zero | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 1 |
| k5_11_interior_Y1141 | g1 | 2 (tree: 11 nodes, depth 2, CC 2, exact 0, NS 0, pockets 0) | DEAD | 32 |
| k5_11_interior_Y1141 | zero | 2 (tree: 11 nodes, depth 2, CC 2, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 37 |
| k5_11_interior_Y1144 | g1 | 2 (tree: 56 nodes, depth 8, CC 1, exact 0, NS 4, pockets 5) | DEAD | 211 |
| k5_11_interior_Y1144 | zero | 2 (tree: 49 nodes, depth 7, CC 3, exact 0, NS 4, pockets 4) | DEAD (s0-only, WINDOW-PENDING) | 176 |
| k5_11_interior_Y1128 | g1 | 2 (tree: 196 nodes, depth 7, CC 10, exact 0, NS 5, pockets 36) | DEAD | 1377 |
| k5_11_interior_Y1128 | zero | 2 (tree: 190 nodes, depth 7, CC 9, exact 0, NS 5, pockets 34) | DEAD (s0-only, WINDOW-PENDING) | 1217 |
| k5_11_interior_Y1150 | g1 | 2 (tree: 25 nodes, depth 2, CC 4, exact 0, NS 0, pockets 0) | DEAD | 49 |
| k5_11_interior_Y1150 | zero | 2 (tree: 20 nodes, depth 2, CC 3, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 41 |
| k5_11_interior_Y1108 | g1 | 2 (tree: 238 nodes, depth 10, CC 17, exact 0, NS 10, pockets 38) | ALIVE (wall) | 1808 |
| k5_11_interior_Y1108 | zero | 2 (tree: 277 nodes, depth 10, CC 17, exact 0, NS 7, pockets 47) | ALIVE (wall) | 1811 |
| k5_11_interior_Y0119_D06__L1 | g1 | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD | 0 |
| k5_11_interior_Y0119_D06__L1 | zero | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 1 |
| k5_11_interior_Y0036__L1 | g1 | 2 (tree: 64 nodes, depth 4, CC 1, exact 0, NS 0, pockets 1) | DEAD | 208 |
| k5_11_interior_Y0036__L1 | zero | 2 (tree: 64 nodes, depth 4, CC 1, exact 0, NS 0, pockets 1) | DEAD (s0-only, WINDOW-PENDING) | 185 |
| k5_11_interior_Y1145 | g1 | 2 (tree: 240 nodes, depth 9, CC 18, exact 0, NS 16, pockets 39) | ALIVE (wall) | 1808 |
| k5_11_interior_Y1145 | zero | 2 (tree: 275 nodes, depth 9, CC 21, exact 0, NS 18, pockets 49) | ALIVE (wall) | 1800 |
| k5_11_interior_Y0072__L1 | g1 | 2 (tree: 158 nodes, depth 6, CC 2, exact 0, NS 1, pockets 11) | DEAD | 575 |
| k5_11_interior_Y0072__L1 | zero | 2 (tree: 150 nodes, depth 6, CC 2, exact 0, NS 1, pockets 7) | DEAD (s0-only, WINDOW-PENDING) | 418 |
| k5_11_interior_Y0041__L1 | g1 | 2 (tree: 159 nodes, depth 6, CC 4, exact 0, NS 1, pockets 11) | DEAD | 578 |
| k5_11_interior_Y0041__L1 | zero | 2 (tree: 138 nodes, depth 6, CC 4, exact 0, NS 1, pockets 9) | DEAD (s0-only, WINDOW-PENDING) | 424 |
| k5_11_interior_Y1151 | g1 | 2 (tree: 251 nodes, depth 11, CC 22, exact 0, NS 17, pockets 34) | ALIVE (wall) | 1800 |
| k5_11_interior_Y1151 | zero | 2 (tree: 296 nodes, depth 10, CC 22, exact 0, NS 17, pockets 41) | ALIVE (wall) | 1805 |
| k5_11_interior_Y0084__L1 | g1 | 2 (tree: 100 nodes, depth 6, CC 1, exact 0, NS 3, pockets 18) | DEAD | 589 |
| k5_11_interior_Y0084__L1 | zero | 2 (tree: 99 nodes, depth 6, CC 0, exact 0, NS 3, pockets 18) | DEAD (s0-only, WINDOW-PENDING) | 539 |
| k5_11_interior_Y0119__L1 | g1 | 2 (tree: 61 nodes, depth 4, CC 0, exact 0, NS 0, pockets 1) | DEAD | 147 |
| k5_11_interior_Y0119__L1 | zero | 2 (tree: 58 nodes, depth 4, CC 1, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 124 |
| k5_11_interior_Y0108__L1 | g1 | 2 (tree: 57 nodes, depth 5, CC 2, exact 0, NS 1, pockets 7) | DEAD | 247 |
| k5_11_interior_Y0108__L1 | zero | 2 (tree: 55 nodes, depth 5, CC 4, exact 0, NS 0, pockets 6) | DEAD (s0-only, WINDOW-PENDING) | 225 |
| k5_11_interior_Y0149__L1 | g1 | 2 (tree: 5 nodes, depth 1, CC 0, exact 0, NS 0, pockets 0) | DEAD | 3 |
| k5_11_interior_Y0149__L1 | zero | 2 (tree: 5 nodes, depth 1, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 6 |
| k5_11_interior_Y0191__L1 | g1 | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD | 0 |
| k5_11_interior_Y0191__L1 | zero | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 1 |
| k5_11_interior_Y0402__L1 | g1 | 2 (tree: 70 nodes, depth 5, CC 2, exact 0, NS 0, pockets 3) | DEAD | 189 |
| k5_11_interior_Y0402__L1 | zero | 2 (tree: 72 nodes, depth 4, CC 1, exact 0, NS 0, pockets 1) | DEAD (s0-only, WINDOW-PENDING) | 137 |
| k5_11_interior_Y0414__L1 | g1 | 2 (tree: 72 nodes, depth 8, CC 6, exact 0, NS 4, pockets 7) | DEAD | 320 |
| k5_11_interior_Y0414__L1 | zero | 2 (tree: 62 nodes, depth 7, CC 6, exact 0, NS 4, pockets 5) | DEAD (s0-only, WINDOW-PENDING) | 248 |
| k5_11_interior_Y0486__L1 | g1 | 2 (tree: 3 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD | 3 |
| k5_11_interior_Y0486__L1 | zero | 2 (tree: 3 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 7 |
| k5_11_interior_Y0527__L1 | g1 | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD | 0 |
| k5_11_interior_Y0527__L1 | zero | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 0 |
| k5_16_interior_Y0143_D02 | g1 | 2 (tree: 11 nodes, depth 2, CC 0, exact 0, NS 0, pockets 0) | DEAD | 11 |
| k5_16_interior_Y0143_D02 | zero | 2 (tree: 11 nodes, depth 2, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 15 |
| k5_16_interior_Y0143_D03 | g1 | 2 (tree: 12 nodes, depth 2, CC 0, exact 0, NS 0, pockets 0) | DEAD | 13 |
| k5_16_interior_Y0143_D03 | zero | 2 (tree: 12 nodes, depth 2, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 17 |
| k5_16_interior_Y0003 | g1 | 2 (tree: 55 nodes, depth 3, CC 0, exact 0, NS 0, pockets 1) | DEAD | 87 |
| k5_16_interior_Y0003 | zero | 2 (tree: 7 nodes, depth 1, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 17 |
| k5_16_interior_Y0010 | g1 | 2 (tree: 36 nodes, depth 2, CC 0, exact 0, NS 0, pockets 0) | DEAD | 52 |
| k5_16_interior_Y0010 | zero | 2 (tree: 6 nodes, depth 1, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 16 |
| k5_11_interior_Y0186__L1 | g1 | 2 (tree: 203 nodes, depth 7, CC 4, exact 0, NS 8, pockets 42) | DEAD | 1564 |
| k5_11_interior_Y0186__L1 | zero | 2 (tree: 202 nodes, depth 7, CC 4, exact 0, NS 5, pockets 42) | DEAD (s0-only, WINDOW-PENDING) | 1409 |
| k5_16_interior_Y0036 | g1 | 2 (tree: 83 nodes, depth 5, CC 0, exact 0, NS 4, pockets 10) | DEAD | 414 |
| k5_16_interior_Y0036 | zero | 2 (tree: 80 nodes, depth 5, CC 0, exact 0, NS 4, pockets 11) | DEAD (s0-only, WINDOW-PENDING) | 430 |
| k5_16_interior_Y0033 | g1 | 2 (tree: 238 nodes, depth 4, CC 0, exact 0, NS 0, pockets 1) | DEAD | 739 |
| k5_16_interior_Y0033 | zero | 2 (tree: 208 nodes, depth 4, CC 0, exact 0, NS 0, pockets 3) | DEAD (s0-only, WINDOW-PENDING) | 540 |
| k5_11_interior_Y0461__L1 | g1 | 2 (tree: 199 nodes, depth 7, CC 0, exact 0, NS 2, pockets 41) | DEAD | 1398 |
| k5_11_interior_Y0461__L1 | zero | 2 (tree: 192 nodes, depth 7, CC 0, exact 0, NS 2, pockets 40) | DEAD (s0-only, WINDOW-PENDING) | 1210 |
| k5_11_interior_Y0384__L1 | g1 | 2 (tree: 262 nodes, depth 10, CC 11, exact 0, NS 9, pockets 36) | ALIVE (wall) | 1805 |
| k5_11_interior_Y0384__L1 | zero | 2 (tree: 281 nodes, depth 10, CC 13, exact 0, NS 8, pockets 41) | DEAD (s0-only, WINDOW-PENDING) | 1697 |
| k5_16_interior_Y0039 | g1 | 2 (tree: 152 nodes, depth 4, CC 0, exact 0, NS 0, pockets 4) | DEAD | 524 |
| k5_16_interior_Y0039 | zero | 2 (tree: 150 nodes, depth 4, CC 0, exact 0, NS 0, pockets 3) | DEAD (s0-only, WINDOW-PENDING) | 407 |
| k5_16_interior_Y0041 | g1 | 2 (tree: 204 nodes, depth 4, CC 0, exact 0, NS 0, pockets 3) | DEAD | 669 |
| k5_16_interior_Y0041 | zero | 2 (tree: 205 nodes, depth 4, CC 0, exact 0, NS 0, pockets 3) | DEAD (s0-only, WINDOW-PENDING) | 534 |
| k5_16_interior_Y0069 | g1 | 2 (tree: 84 nodes, depth 6, CC 0, exact 0, NS 14, pockets 10) | DEAD | 504 |
| k5_16_interior_Y0069 | zero | 2 (tree: 80 nodes, depth 6, CC 0, exact 0, NS 12, pockets 10) | DEAD (s0-only, WINDOW-PENDING) | 445 |
| k5_16_interior_Y0072 | g1 | 2 (tree: 202 nodes, depth 4, CC 0, exact 0, NS 1, pockets 0) | DEAD | 613 |
| k5_16_interior_Y0072 | zero | 2 (tree: 167 nodes, depth 4, CC 0, exact 0, NS 3, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 400 |
| k5_16_interior_Y0100 | g1 | 2 (tree: 46 nodes, depth 2, CC 0, exact 0, NS 0, pockets 0) | DEAD | 114 |
| k5_16_interior_Y0100 | zero | 2 (tree: 31 nodes, depth 2, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 137 |
| k5_16_interior_Y0084 | g1 | 2 (tree: 69 nodes, depth 4, CC 0, exact 0, NS 3, pockets 6) | DEAD | 255 |
| k5_16_interior_Y0084 | zero | 2 (tree: 69 nodes, depth 4, CC 0, exact 0, NS 1, pockets 6) | DEAD (s0-only, WINDOW-PENDING) | 234 |
| k5_16_interior_Y0101 | g1 | 2 (tree: 39 nodes, depth 3, CC 0, exact 0, NS 0, pockets 3) | DEAD | 138 |
| k5_16_interior_Y0101 | zero | 2 (tree: 33 nodes, depth 3, CC 0, exact 0, NS 0, pockets 3) | DEAD (s0-only, WINDOW-PENDING) | 178 |
| k5_16_interior_Y0103 | g1 | 2 (tree: 30 nodes, depth 3, CC 0, exact 0, NS 0, pockets 0) | DEAD | 38 |
| k5_16_interior_Y0103 | zero | 2 (tree: 10 nodes, depth 1, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 18 |
| k5_16_interior_Y0108 | g1 | 2 (tree: 20 nodes, depth 3, CC 0, exact 0, NS 0, pockets 0) | DEAD | 26 |
| k5_16_interior_Y0108 | zero | 2 (tree: 15 nodes, depth 3, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 24 |
| k5_16_interior_Y0119 | g1 | 2 (tree: 19 nodes, depth 2, CC 0, exact 0, NS 0, pockets 0) | DEAD | 43 |
| k5_16_interior_Y0119 | zero | 2 (tree: 19 nodes, depth 2, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 25 |
| k5_16_interior_Y0122 | g1 | 2 (tree: 23 nodes, depth 3, CC 0, exact 0, NS 0, pockets 0) | DEAD | 25 |
| k5_16_interior_Y0122 | zero | 2 (tree: 16 nodes, depth 2, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 23 |
| k5_16_interior_Y0105 | g1 | 2 (tree: 72 nodes, depth 6, CC 0, exact 0, NS 8, pockets 8) | DEAD | 374 |
| k5_16_interior_Y0105 | zero | 2 (tree: 68 nodes, depth 6, CC 0, exact 0, NS 7, pockets 8) | DEAD (s0-only, WINDOW-PENDING) | 340 |
| k5_16_interior_Y0124 | g1 | 2 (tree: 39 nodes, depth 5, CC 0, exact 0, NS 1, pockets 2) | DEAD | 214 |
| k5_16_interior_Y0124 | zero | 2 (tree: 38 nodes, depth 3, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 117 |
| k5_16_interior_Y0126 | g1 | 2 (tree: 34 nodes, depth 4, CC 0, exact 1, NS 0, pockets 4) | DEAD | 205 |
| k5_16_interior_Y0126 | zero | 2 (tree: 31 nodes, depth 5, CC 0, exact 0, NS 1, pockets 4) | DEAD (s0-only, WINDOW-PENDING) | 202 |
| k5_16_interior_Y0143 | g1 | 2 (tree: 21 nodes, depth 3, CC 0, exact 0, NS 0, pockets 0) | DEAD | 22 |
| k5_16_interior_Y0143 | zero | 2 (tree: 19 nodes, depth 2, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 29 |
| k5_16_interior_Y0145 | g1 | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD | 0 |
| k5_16_interior_Y0145 | zero | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 0 |
| k5_16_interior_Y0147 | g1 | 2 (tree: 2 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD | 2 |
| k5_16_interior_Y0147 | zero | 2 (tree: 2 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 3 |
| k5_16_interior_Y0149 | g1 | 2 (tree: 2 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD | 2 |
| k5_16_interior_Y0149 | zero | 2 (tree: 2 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 3 |
| k5_16_interior_Y0150 | g1 | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD | 2 |
| k5_16_interior_Y0150 | zero | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 3 |
| k5_16_interior_Y0170 | g1 | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD | 0 |
| k5_16_interior_Y0170 | zero | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 1 |
| k5_16_interior_Y0183 | g1 | 2 (tree: 19 nodes, depth 3, CC 0, exact 0, NS 0, pockets 2) | DEAD | 67 |
| k5_16_interior_Y0183 | zero | 2 (tree: 20 nodes, depth 3, CC 0, exact 0, NS 0, pockets 2) | DEAD (s0-only, WINDOW-PENDING) | 77 |
| k5_16_interior_Y0217 | g1 | 2 (tree: 50 nodes, depth 7, CC 0, exact 0, NS 7, pockets 4) | DEAD | 226 |
| k5_16_interior_Y0217 | zero | 2 (tree: 48 nodes, depth 6, CC 0, exact 0, NS 5, pockets 4) | DEAD (s0-only, WINDOW-PENDING) | 207 |
| k5_16_interior_Y0133 | g1 | 2 (tree: 200 nodes, depth 6, CC 0, exact 0, NS 3, pockets 19) | DEAD | 1238 |
| k5_16_interior_Y0133 | zero | 2 (tree: 204 nodes, depth 6, CC 0, exact 0, NS 2, pockets 19) | DEAD (s0-only, WINDOW-PENDING) | 1046 |
| k5_16_interior_Y0256 | g1 | 2 (tree: 40 nodes, depth 6, CC 0, exact 0, NS 6, pockets 4) | DEAD | 220 |
| k5_16_interior_Y0256 | zero | 2 (tree: 40 nodes, depth 6, CC 0, exact 0, NS 8, pockets 4) | DEAD (s0-only, WINDOW-PENDING) | 182 |
| k5_16_interior_Y0279 | g1 | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD | 1 |
| k5_16_interior_Y0279 | zero | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 2 |
| k5_16_interior_Y0127 | g1 | 2 (tree: 93 nodes, depth 8, CC 0, exact 0, NS 7, pockets 15) | ALIVE (wall) | 1807 |
| k5_16_interior_Y0127 | zero | 2 (tree: 119 nodes, depth 8, CC 0, exact 0, NS 7, pockets 18) | DEAD (s0-only, WINDOW-PENDING) | 1784 |
| k5_16_interior_Y0130 | g1 | 2 (tree: 23 nodes, depth 8, CC 0, exact 0, NS 2, pockets 4) | ALIVE (wall) | 1889 |
| k5_16_interior_Y0130 | zero | 2 (tree: 50 nodes, depth 8, CC 0, exact 0, NS 2, pockets 4) | ALIVE (wall) | 1801 |
| k5_16_interior_Y0186 | g1 | 2 (tree: 170 nodes, depth 5, CC 0, exact 0, NS 7, pockets 28) | ALIVE (wall) | 1821 |
| k5_16_interior_Y0186 | zero | 2 (tree: 165 nodes, depth 6, CC 0, exact 0, NS 6, pockets 28) | ALIVE (wall) | 1923 |
| k5_16_interior_Y0281 | g1 | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD | 2 |
| k5_16_interior_Y0281 | zero | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 3 |
| k5_16_interior_Y0290 | g1 | 2 (tree: 130 nodes, depth 5, CC 0, exact 0, NS 0, pockets 5) | DEAD | 355 |
| k5_16_interior_Y0290 | zero | 2 (tree: 112 nodes, depth 5, CC 0, exact 0, NS 0, pockets 4) | DEAD (s0-only, WINDOW-PENDING) | 299 |
| k5_16_interior_Y0308 | g1 | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD | 1 |
| k5_16_interior_Y0308 | zero | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 2 |
| k5_16_interior_Y0280 | g1 | 2 (tree: 43 nodes, depth 10, CC 0, exact 0, NS 3, pockets 2) | ALIVE (wall) | 1819 |
| k5_16_interior_Y0280 | zero | 2 (tree: 55 nodes, depth 9, CC 0, exact 0, NS 6, pockets 7) | ALIVE (wall) | 1811 |
| k5_16_interior_Y0358 | g1 | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD | 2 |
| k5_16_interior_Y0358 | zero | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 3 |
| k5_16_interior_Y0368 | g1 | 2 (tree: 36 nodes, depth 2, CC 0, exact 0, NS 0, pockets 0) | DEAD | 65 |
| k5_16_interior_Y0368 | zero | 2 (tree: 33 nodes, depth 2, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 64 |
| k5_16_interior_Y0321 | g1 | 2 (tree: 210 nodes, depth 6, CC 0, exact 0, NS 9, pockets 14) | DEAD | 895 |
| k5_16_interior_Y0321 | zero | 2 (tree: 192 nodes, depth 6, CC 0, exact 0, NS 8, pockets 14) | DEAD (s0-only, WINDOW-PENDING) | 648 |
| k5_16_interior_Y0355 | g1 | 2 (tree: 155 nodes, depth 6, CC 0, exact 0, NS 20, pockets 21) | ALIVE (wall) | 1814 |
| k5_16_interior_Y0355 | zero | 2 (tree: 160 nodes, depth 7, CC 0, exact 0, NS 17, pockets 26) | ALIVE (wall) | 1803 |
| k5_16_interior_Y0414 | g1 | 2 (tree: 58 nodes, depth 7, CC 0, exact 0, NS 8, pockets 4) | DEAD | 251 |
| k5_16_interior_Y0414 | zero | 2 (tree: 48 nodes, depth 6, CC 0, exact 0, NS 4, pockets 3) | DEAD (s0-only, WINDOW-PENDING) | 207 |
| k5_16_interior_Y0376 | g1 | 2 (tree: 198 nodes, depth 10, CC 0, exact 10, NS 17, pockets 14) | ALIVE (wall) | 1810 |
| k5_16_interior_Y0376 | zero | 2 (tree: 224 nodes, depth 10, CC 0, exact 9, NS 19, pockets 16) | DEAD (s0-only, WINDOW-PENDING) | 1702 |
| k5_16_interior_Y0384 | g1 | 2 (tree: 98 nodes, depth 8, CC 0, exact 0, NS 7, pockets 11) | ALIVE (wall) | 2050 |
| k5_16_interior_Y0384 | zero | 2 (tree: 235 nodes, depth 7, CC 0, exact 0, NS 16, pockets 25) | ALIVE (wall) | 1824 |
| k5_16_interior_Y0422 | g1 | 2 (tree: 58 nodes, depth 5, CC 0, exact 0, NS 1, pockets 5) | DEAD | 295 |
| k5_16_interior_Y0422 | zero | 2 (tree: 51 nodes, depth 4, CC 0, exact 0, NS 0, pockets 4) | DEAD (s0-only, WINDOW-PENDING) | 244 |
| k5_16_interior_Y0449 | g1 | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD | 0 |
| k5_16_interior_Y0449 | zero | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 1 |
| k5_16_interior_Y0391 | g1 | 2 (tree: 226 nodes, depth 8, CC 0, exact 0, NS 13, pockets 20) | ALIVE (wall) | 1926 |
| k5_16_interior_Y0391 | zero | 2 (tree: 223 nodes, depth 8, CC 0, exact 0, NS 14, pockets 20) | ALIVE (wall) | 1858 |
| k5_16_interior_Y0452 | g1 | 2 (tree: 82 nodes, depth 6, CC 0, exact 0, NS 7, pockets 10) | DEAD | 518 |
| k5_16_interior_Y0452 | zero | 2 (tree: 79 nodes, depth 6, CC 0, exact 0, NS 7, pockets 10) | DEAD (s0-only, WINDOW-PENDING) | 482 |
| k5_16_interior_Y0454 | g1 | 2 (tree: 45 nodes, depth 5, CC 0, exact 0, NS 3, pockets 9) | DEAD | 350 |
| k5_16_interior_Y0454 | zero | 2 (tree: 43 nodes, depth 5, CC 0, exact 0, NS 3, pockets 9) | DEAD (s0-only, WINDOW-PENDING) | 315 |
| k5_16_interior_Y0458 | g1 | 2 (tree: 30 nodes, depth 3, CC 0, exact 0, NS 0, pockets 0) | DEAD | 23 |
| k5_16_interior_Y0458 | zero | 2 (tree: 30 nodes, depth 3, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 38 |
| k5_16_interior_Y0466 | g1 | 2 (tree: 91 nodes, depth 4, CC 0, exact 0, NS 0, pockets 9) | DEAD | 331 |
| k5_16_interior_Y0466 | zero | 2 (tree: 83 nodes, depth 4, CC 0, exact 0, NS 0, pockets 9) | DEAD (s0-only, WINDOW-PENDING) | 292 |
| k5_16_interior_Y0486 | g1 | 2 (tree: 16 nodes, depth 2, CC 0, exact 0, NS 0, pockets 0) | DEAD | 25 |
| k5_16_interior_Y0486 | zero | 2 (tree: 15 nodes, depth 2, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 37 |
| k5_16_interior_Y0461 | g1 | 2 (tree: 230 nodes, depth 6, CC 0, exact 0, NS 5, pockets 13) | DEAD | 1030 |
| k5_16_interior_Y0461 | zero | 2 (tree: 218 nodes, depth 5, CC 0, exact 0, NS 3, pockets 12) | DEAD (s0-only, WINDOW-PENDING) | 749 |
| k5_16_interior_Y0489 | g1 | 2 (tree: 118 nodes, depth 7, CC 0, exact 0, NS 15, pockets 13) | DEAD | 942 |
| k5_16_interior_Y0489 | zero | 2 (tree: 106 nodes, depth 7, CC 0, exact 0, NS 15, pockets 11) | DEAD (s0-only, WINDOW-PENDING) | 706 |
| k5_16_interior_Y0531 | g1 | 2 (tree: 12 nodes, depth 2, CC 0, exact 0, NS 0, pockets 0) | DEAD | 15 |
| k5_16_interior_Y0531 | zero | 2 (tree: 12 nodes, depth 2, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 28 |
| k5_16_interior_Y0495 | g1 | 2 (tree: 130 nodes, depth 8, CC 0, exact 0, NS 13, pockets 11) | ALIVE (wall) | 1824 |
| k5_16_interior_Y0495 | zero | 2 (tree: 139 nodes, depth 8, CC 0, exact 0, NS 12, pockets 15) | ALIVE (wall) | 1909 |
| k5_16_interior_Y0513 | g1 | 2 (tree: 200 nodes, depth 10, CC 0, exact 28, NS 15, pockets 8) | ALIVE (wall) | 1801 |
| k5_16_interior_Y0513 | zero | 2 (tree: 233 nodes, depth 9, CC 0, exact 34, NS 15, pockets 10) | DEAD (s0-only, WINDOW-PENDING) | 1731 |
| k5_16_interior_Y0517 | g1 | 2 (tree: 246 nodes, depth 9, CC 0, exact 0, NS 18, pockets 22) | ALIVE (wall) | 1803 |
| k5_16_interior_Y0517 | zero | 2 (tree: 288 nodes, depth 9, CC 0, exact 0, NS 18, pockets 23) | ALIVE (wall) | 1804 |
| k5_16_interior_Y0559 | g1 | 2 (tree: 219 nodes, depth 7, CC 0, exact 0, NS 24, pockets 27) | DEAD | 1558 |
| k5_16_interior_Y0559 | zero | 2 (tree: 217 nodes, depth 7, CC 0, exact 0, NS 23, pockets 26) | DEAD (s0-only, WINDOW-PENDING) | 1330 |
| k5_16_interior_Y0540 | g1 | 2 (tree: 218 nodes, depth 5, CC 0, exact 0, NS 15, pockets 33) | ALIVE (wall) | 1804 |
| k5_16_interior_Y0540 | zero | 2 (tree: 242 nodes, depth 6, CC 0, exact 0, NS 17, pockets 39) | ALIVE (wall) | 1820 |
| k5_16_interior_Y0568 | g1 | 2 (tree: 55 nodes, depth 4, CC 0, exact 0, NS 3, pockets 2) | DEAD | 212 |
| k5_16_interior_Y0568 | zero | 2 (tree: 59 nodes, depth 4, CC 0, exact 0, NS 1, pockets 1) | DEAD (s0-only, WINDOW-PENDING) | 120 |
| k5_16_interior_Y0570 | g1 | 2 (tree: 22 nodes, depth 2, CC 0, exact 0, NS 0, pockets 0) | DEAD | 40 |
| k5_16_interior_Y0570 | zero | 2 (tree: 28 nodes, depth 2, CC 0, exact 0, NS 0, pockets 1) | DEAD (s0-only, WINDOW-PENDING) | 130 |
| k5_16_interior_Y0572 | g1 | 2 (tree: 66 nodes, depth 5, CC 0, exact 0, NS 2, pockets 6) | DEAD | 367 |
| k5_16_interior_Y0572 | zero | 2 (tree: 40 nodes, depth 4, CC 0, exact 0, NS 0, pockets 6) | DEAD (s0-only, WINDOW-PENDING) | 290 |
| k5_16_interior_Y0574 | g1 | 2 (tree: 30 nodes, depth 3, CC 0, exact 0, NS 0, pockets 0) | DEAD | 50 |
| k5_16_interior_Y0574 | zero | 2 (tree: 10 nodes, depth 1, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 22 |
| k5_16_interior_Y0579 | g1 | 2 (tree: 26 nodes, depth 3, CC 0, exact 0, NS 0, pockets 3) | DEAD | 154 |
| k5_16_interior_Y0579 | zero | 2 (tree: 26 nodes, depth 3, CC 0, exact 0, NS 0, pockets 3) | DEAD (s0-only, WINDOW-PENDING) | 148 |
| k5_16_interior_Y0588 | g1 | 2 (tree: 58 nodes, depth 5, CC 0, exact 0, NS 2, pockets 4) | DEAD | 218 |
| k5_16_interior_Y0588 | zero | 2 (tree: 40 nodes, depth 4, CC 0, exact 0, NS 1, pockets 2) | DEAD (s0-only, WINDOW-PENDING) | 125 |
| k5_16_interior_Y0592 | g1 | 2 (tree: 57 nodes, depth 3, CC 0, exact 0, NS 0, pockets 2) | DEAD | 168 |
| k5_16_interior_Y0592 | zero | 2 (tree: 51 nodes, depth 3, CC 0, exact 0, NS 0, pockets 1) | DEAD (s0-only, WINDOW-PENDING) | 123 |
| k5_16_interior_Y0635 | g1 | 2 (tree: 14 nodes, depth 2, CC 0, exact 0, NS 0, pockets 0) | DEAD | 7 |
| k5_16_interior_Y0635 | zero | 2 (tree: 14 nodes, depth 2, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 10 |
| k5_16_interior_Y0597 | g1 | 2 (tree: 71 nodes, depth 7, CC 0, exact 0, NS 7, pockets 5) | DEAD | 353 |
| k5_16_interior_Y0597 | zero | 2 (tree: 68 nodes, depth 6, CC 0, exact 1, NS 6, pockets 5) | DEAD (s0-only, WINDOW-PENDING) | 323 |
| k5_16_interior_Y0636 | g1 | 2 (tree: 26 nodes, depth 3, CC 0, exact 0, NS 0, pockets 2) | DEAD | 92 |
| k5_16_interior_Y0636 | zero | 2 (tree: 27 nodes, depth 3, CC 0, exact 0, NS 0, pockets 2) | DEAD (s0-only, WINDOW-PENDING) | 85 |
| k5_16_interior_Y0596 | g1 | 2 (tree: 145 nodes, depth 8, CC 0, exact 0, NS 15, pockets 12) | DEAD | 1032 |
| k5_16_interior_Y0596 | zero | 2 (tree: 128 nodes, depth 8, CC 0, exact 0, NS 13, pockets 10) | DEAD (s0-only, WINDOW-PENDING) | 741 |
| k5_16_interior_Y0646 | g1 | 2 (tree: 4 nodes, depth 1, CC 0, exact 0, NS 0, pockets 0) | DEAD | 9 |
| k5_16_interior_Y0646 | zero | 2 (tree: 4 nodes, depth 1, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 12 |
| k5_16_interior_Y0628 | g1 | 2 (tree: 206 nodes, depth 5, CC 0, exact 0, NS 4, pockets 13) | DEAD | 974 |
| k5_16_interior_Y0628 | zero | 2 (tree: 204 nodes, depth 5, CC 0, exact 0, NS 3, pockets 12) | DEAD (s0-only, WINDOW-PENDING) | 756 |
| k5_16_interior_Y0652a | g1 | 2 (tree: 13 nodes, depth 2, CC 0, exact 0, NS 0, pockets 0) | DEAD | 21 |
| k5_16_interior_Y0652a | zero | 2 (tree: 24 nodes, depth 2, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 54 |
| k5_16_interior_Y0644 | g1 | 2 (tree: 53 nodes, depth 6, CC 0, exact 0, NS 6, pockets 5) | DEAD | 293 |
| k5_16_interior_Y0644 | zero | 2 (tree: 49 nodes, depth 6, CC 0, exact 0, NS 6, pockets 2) | DEAD (s0-only, WINDOW-PENDING) | 214 |
| k5_16_interior_Y0663 | g1 | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD | 2 |
| k5_16_interior_Y0663 | zero | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 3 |
| k5_16_interior_Y0657 | g1 | 2 (tree: 115 nodes, depth 8, CC 0, exact 0, NS 5, pockets 19) | DEAD | 1504 |
| k5_16_interior_Y0657 | zero | 2 (tree: 85 nodes, depth 7, CC 0, exact 0, NS 3, pockets 16) | DEAD (s0-only, WINDOW-PENDING) | 581 |
| k5_16_interior_Y0665 | g1 | 2 (tree: 43 nodes, depth 4, CC 0, exact 0, NS 0, pockets 3) | DEAD | 247 |
| k5_16_interior_Y0665 | zero | 2 (tree: 47 nodes, depth 4, CC 0, exact 0, NS 1, pockets 3) | DEAD (s0-only, WINDOW-PENDING) | 221 |
| k5_16_interior_Y0642 | g1 | 2 (tree: 157 nodes, depth 6, CC 0, exact 0, NS 26, pockets 23) | ALIVE (wall) | 1801 |
| k5_16_interior_Y0642 | zero | 2 (tree: 154 nodes, depth 6, CC 0, exact 0, NS 23, pockets 22) | DEAD (s0-only, WINDOW-PENDING) | 1570 |
| k5_16_interior_Y0674 | g1 | 2 (tree: 62 nodes, depth 5, CC 0, exact 0, NS 6, pockets 9) | DEAD | 430 |
| k5_16_interior_Y0674 | zero | 2 (tree: 75 nodes, depth 5, CC 0, exact 0, NS 3, pockets 6) | DEAD (s0-only, WINDOW-PENDING) | 320 |
| k5_16_interior_Y0656 | g1 | 2 (tree: 207 nodes, depth 11, CC 0, exact 27, NS 16, pockets 13) | ALIVE (wall) | 1808 |
| k5_16_interior_Y0656 | zero | 2 (tree: 252 nodes, depth 11, CC 0, exact 27, NS 23, pockets 18) | DEAD (s0-only, WINDOW-PENDING) | 1732 |
| k5_16_interior_Y0672 | g1 | 2 (tree: 30 nodes, depth 9, CC 0, exact 0, NS 1, pockets 2) | ALIVE (wall) | 1877 |
| k5_16_interior_Y0672 | zero | 2 (tree: 36 nodes, depth 9, CC 0, exact 0, NS 2, pockets 5) | ALIVE (wall) | 1802 |
| k5_16_interior_Y0727 | g1 | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD | 0 |
| k5_16_interior_Y0727 | zero | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 1 |
| k5_16_interior_Y0687 | g1 | 2 (tree: 147 nodes, depth 11, CC 0, exact 3, NS 19, pockets 13) | ALIVE (wall) | 1879 |
| k5_16_interior_Y0687 | zero | 2 (tree: 148 nodes, depth 10, CC 0, exact 2, NS 19, pockets 13) | ALIVE (wall) | 1880 |
| k5_16_interior_Y0735 | g1 | 2 (tree: 84 nodes, depth 4, CC 0, exact 0, NS 0, pockets 5) | DEAD | 505 |
| k5_16_interior_Y0735 | zero | 2 (tree: 75 nodes, depth 4, CC 0, exact 0, NS 0, pockets 4) | DEAD (s0-only, WINDOW-PENDING) | 390 |
| k5_16_interior_Y0702 | g1 | 2 (tree: 178 nodes, depth 14, CC 0, exact 9, NS 16, pockets 12) | ALIVE (wall) | 1996 |
| k5_16_interior_Y0702 | zero | 2 (tree: 180 nodes, depth 15, CC 0, exact 7, NS 13, pockets 12) | ALIVE (wall) | 1947 |
| k5_16_interior_Y0713 | g1 | 2 (tree: 228 nodes, depth 13, CC 0, exact 12, NS 22, pockets 7) | ALIVE (wall) | 1800 |
| k5_16_interior_Y0713 | zero | 2 (tree: 257 nodes, depth 14, CC 0, exact 17, NS 19, pockets 7) | ALIVE (wall) | 1803 |
| k5_16_interior_Y0743 | g1 | 2 (tree: 120 nodes, depth 7, CC 0, exact 0, NS 5, pockets 11) | DEAD | 620 |
| k5_16_interior_Y0743 | zero | 2 (tree: 111 nodes, depth 7, CC 0, exact 0, NS 7, pockets 10) | DEAD (s0-only, WINDOW-PENDING) | 898 |
| k5_16_interior_Y0745 | g1 | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD | 2 |
| k5_16_interior_Y0745 | zero | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 2 |
| k5_16_interior_Y0752 | g1 | 2 (tree: 39 nodes, depth 6, CC 0, exact 0, NS 2, pockets 4) | DEAD | 156 |
| k5_16_interior_Y0752 | zero | 2 (tree: 33 nodes, depth 5, CC 0, exact 0, NS 2, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 88 |
| k5_16_interior_Y0738 | g1 | 2 (tree: 243 nodes, depth 13, CC 0, exact 2, NS 21, pockets 14) | ALIVE (wall) | 1802 |
| k5_16_interior_Y0738 | zero | 2 (tree: 362 nodes, depth 13, CC 0, exact 2, NS 18, pockets 18) | ALIVE (wall) | 1802 |
| k5_16_interior_Y0803 | g1 | 2 (tree: 81 nodes, depth 8, CC 0, exact 0, NS 11, pockets 6) | DEAD | 347 |
| k5_16_interior_Y0803 | zero | 2 (tree: 54 nodes, depth 6, CC 0, exact 0, NS 2, pockets 1) | DEAD (s0-only, WINDOW-PENDING) | 151 |
| k5_16_interior_Y0817 | g1 | 2 (tree: 59 nodes, depth 3, CC 0, exact 0, NS 0, pockets 0) | DEAD | 147 |
| k5_16_interior_Y0817 | zero | 2 (tree: 57 nodes, depth 3, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 166 |
| k5_16_interior_Y0828 | g1 | 2 (tree: 16 nodes, depth 3, CC 0, exact 0, NS 0, pockets 0) | DEAD | 14 |
| k5_16_interior_Y0828 | zero | 2 (tree: 16 nodes, depth 3, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 24 |
| k5_16_interior_Y0791 | g1 | 2 (tree: 93 nodes, depth 7, CC 0, exact 0, NS 13, pockets 11) | DEAD | 646 |
| k5_16_interior_Y0791 | zero | 2 (tree: 89 nodes, depth 7, CC 0, exact 0, NS 11, pockets 10) | DEAD (s0-only, WINDOW-PENDING) | 522 |
| k5_16_interior_Y0851 | g1 | 2 (tree: 74 nodes, depth 5, CC 0, exact 0, NS 7, pockets 0) | DEAD | 129 |
| k5_16_interior_Y0851 | zero | 2 (tree: 62 nodes, depth 5, CC 0, exact 0, NS 7, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 144 |
| k5_16_interior_Y0854 | g1 | 2 (tree: 15 nodes, depth 1, CC 0, exact 0, NS 0, pockets 0) | DEAD | 45 |
| k5_16_interior_Y0854 | zero | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 0 |
| k5_16_interior_Y0848 | g1 | 2 (tree: 80 nodes, depth 6, CC 0, exact 0, NS 6, pockets 11) | DEAD | 520 |
| k5_16_interior_Y0848 | zero | 2 (tree: 80 nodes, depth 6, CC 0, exact 0, NS 6, pockets 11) | DEAD (s0-only, WINDOW-PENDING) | 481 |
| k5_16_interior_Y0871 | g1 | 2 (tree: 29 nodes, depth 2, CC 0, exact 0, NS 0, pockets 0) | DEAD | 63 |
| k5_16_interior_Y0871 | zero | 2 (tree: 24 nodes, depth 2, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 62 |
| k5_16_interior_Y0878 | g1 | 2 (tree: 15 nodes, depth 3, CC 0, exact 0, NS 0, pockets 1) | DEAD | 52 |
| k5_16_interior_Y0878 | zero | 2 (tree: 15 nodes, depth 3, CC 0, exact 0, NS 0, pockets 1) | DEAD (s0-only, WINDOW-PENDING) | 62 |
| k5_16_interior_Y0864 | g1 | 2 (tree: 103 nodes, depth 5, CC 0, exact 0, NS 9, pockets 12) | DEAD | 724 |
| k5_16_interior_Y0864 | zero | 2 (tree: 100 nodes, depth 5, CC 0, exact 0, NS 9, pockets 11) | DEAD (s0-only, WINDOW-PENDING) | 598 |
| k5_16_interior_Y0954 | g1 | 2 (tree: 64 nodes, depth 7, CC 0, exact 0, NS 3, pockets 8) | DEAD | 389 |
| k5_16_interior_Y0954 | zero | 2 (tree: 58 nodes, depth 6, CC 0, exact 0, NS 5, pockets 6) | DEAD (s0-only, WINDOW-PENDING) | 323 |
| k5_16_interior_Y0943 | g1 | 2 (tree: 155 nodes, depth 9, CC 0, exact 0, NS 29, pockets 1) | DEAD | 671 |
| k5_16_interior_Y0943 | zero | 2 (tree: 146 nodes, depth 9, CC 0, exact 2, NS 27, pockets 1) | DEAD (s0-only, WINDOW-PENDING) | 531 |
| k5_16_interior_Y0959 | g1 | 2 (tree: 15 nodes, depth 2, CC 0, exact 0, NS 0, pockets 0) | DEAD | 53 |
| k5_16_interior_Y0959 | zero | 2 (tree: 15 nodes, depth 2, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 62 |
| k5_16_interior_Y0978 | g1 | 2 (tree: 65 nodes, depth 8, CC 0, exact 4, NS 4, pockets 4) | DEAD | 320 |
| k5_16_interior_Y0978 | zero | 2 (tree: 60 nodes, depth 7, CC 0, exact 4, NS 3, pockets 2) | DEAD (s0-only, WINDOW-PENDING) | 243 |
| k5_16_interior_Y0929 | g1 | 2 (tree: 257 nodes, depth 10, CC 0, exact 13, NS 27, pockets 8) | ALIVE (wall) | 1800 |
| k5_16_interior_Y0929 | zero | 2 (tree: 274 nodes, depth 11, CC 0, exact 11, NS 28, pockets 10) | DEAD (s0-only, WINDOW-PENDING) | 1479 |
| k5_16_interior_Y0992 | g1 | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD | 2 |
| k5_16_interior_Y0992 | zero | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 3 |
| k5_16_interior_Y0985 | g1 | 2 (tree: 138 nodes, depth 7, CC 0, exact 0, NS 15, pockets 0) | DEAD | 479 |
| k5_16_interior_Y0985 | zero | 2 (tree: 123 nodes, depth 7, CC 0, exact 0, NS 15, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 354 |
| k5_16_interior_Y0996 | g1 | 2 (tree: 37 nodes, depth 4, CC 0, exact 0, NS 1, pockets 5) | DEAD | 192 |
| k5_16_interior_Y0996 | zero | 2 (tree: 36 nodes, depth 4, CC 0, exact 0, NS 1, pockets 5) | DEAD (s0-only, WINDOW-PENDING) | 186 |
| k5_16_interior_Y1015 | g1 | 2 (tree: 88 nodes, depth 7, CC 0, exact 0, NS 8, pockets 6) | DEAD | 582 |
| k5_16_interior_Y1015 | zero | 2 (tree: 74 nodes, depth 6, CC 0, exact 0, NS 2, pockets 6) | DEAD (s0-only, WINDOW-PENDING) | 382 |
| k5_16_interior_Y1028 | g1 | 2 (tree: 33 nodes, depth 5, CC 0, exact 0, NS 6, pockets 0) | DEAD | 47 |
| k5_16_interior_Y1028 | zero | 2 (tree: 32 nodes, depth 5, CC 0, exact 0, NS 6, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 75 |
| k5_16_interior_Y0973 | g1 | 2 (tree: 214 nodes, depth 9, CC 0, exact 19, NS 18, pockets 15) | DEAD | 1629 |
| k5_16_interior_Y0973 | zero | 2 (tree: 196 nodes, depth 9, CC 0, exact 20, NS 21, pockets 11) | DEAD (s0-only, WINDOW-PENDING) | 1217 |
| k5_16_interior_Y1033 | g1 | 2 (tree: 15 nodes, depth 2, CC 0, exact 0, NS 0, pockets 0) | DEAD | 8 |
| k5_16_interior_Y1033 | zero | 2 (tree: 14 nodes, depth 2, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 11 |
| k5_16_interior_Y1038 | g1 | 2 (tree: 28 nodes, depth 3, CC 0, exact 0, NS 0, pockets 0) | DEAD | 68 |
| k5_16_interior_Y1038 | zero | 2 (tree: 27 nodes, depth 3, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 80 |
| k5_16_interior_Y1045 | g1 | 2 (tree: 63 nodes, depth 6, CC 0, exact 0, NS 10, pockets 0) | DEAD | 177 |
| k5_16_interior_Y1045 | zero | 2 (tree: 62 nodes, depth 6, CC 0, exact 0, NS 15, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 272 |
| k5_16_interior_Y1062 | g1 | 2 (tree: 9 nodes, depth 1, CC 0, exact 0, NS 0, pockets 0) | DEAD | 9 |
| k5_16_interior_Y1062 | zero | 2 (tree: 8 nodes, depth 1, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 16 |
| k5_16_interior_Y1057 | g1 | 2 (tree: 81 nodes, depth 7, CC 0, exact 0, NS 5, pockets 5) | DEAD | 482 |
| k5_16_interior_Y1057 | zero | 2 (tree: 80 nodes, depth 7, CC 0, exact 0, NS 5, pockets 5) | DEAD (s0-only, WINDOW-PENDING) | 401 |
| k5_16_interior_Y1058 | g1 | 2 (tree: 116 nodes, depth 8, CC 0, exact 8, NS 9, pockets 8) | DEAD | 667 |
| k5_16_interior_Y1058 | zero | 2 (tree: 112 nodes, depth 8, CC 0, exact 0, NS 9, pockets 8) | DEAD (s0-only, WINDOW-PENDING) | 529 |
| k5_16_interior_Y1069 | g1 | 2 (tree: 128 nodes, depth 6, CC 0, exact 0, NS 4, pockets 6) | DEAD | 432 |
| k5_16_interior_Y1069 | zero | 2 (tree: 115 nodes, depth 6, CC 0, exact 0, NS 4, pockets 6) | DEAD (s0-only, WINDOW-PENDING) | 383 |
| k5_16_interior_Y1122 | g1 | 2 (tree: 28 nodes, depth 3, CC 0, exact 0, NS 0, pockets 1) | DEAD | 99 |
| k5_16_interior_Y1122 | zero | 2 (tree: 27 nodes, depth 3, CC 0, exact 0, NS 0, pockets 1) | DEAD (s0-only, WINDOW-PENDING) | 99 |
| k5_16_interior_Y1124 | g1 | 2 (tree: 44 nodes, depth 5, CC 0, exact 0, NS 2, pockets 3) | DEAD | 189 |
| k5_16_interior_Y1124 | zero | 2 (tree: 33 nodes, depth 5, CC 0, exact 0, NS 2, pockets 5) | DEAD (s0-only, WINDOW-PENDING) | 179 |
| k5_16_interior_Y1106 | zero | 2 (tree: 134 nodes, depth 7, CC 0, exact 0, NS 12, pockets 10) | DEAD (s0-only, WINDOW-PENDING) | 613 |
| k5_16_interior_Y1104 | zero | 2 (tree: 248 nodes, depth 11, CC 0, exact 2, NS 45, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 1016 |
| k5_16_interior_Y1076 | zero | 2 (tree: 281 nodes, depth 11, CC 0, exact 16, NS 28, pockets 10) | DEAD (s0-only, WINDOW-PENDING) | 1448 |

CPU-h in this block: 87.59

## Price and projection

* gallery: 17 / 18 pages DEAD at the window pad, 8.84 CPU-h
* frontier: 289 nodes run (251 DEAD at the window pad), 87.59 CPU-h; the census has 49 alive nodes, 14 remaining
* PRICE over the first 20 frontier nodes: mean 537 s, median 444 s per node (both pads); PROJECTION for the remaining 14: 2.1 CPU-h (cap 200)

