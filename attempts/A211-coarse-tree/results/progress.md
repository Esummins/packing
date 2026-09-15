# A211 progress -- 2026-09-14 19:17:46

The COARSE tree (notes/coarse_tree.md): A202 stage 0 + A203 CSP; coarse internal nodes (re-binned pieces <= 96 units, refine 1, no lonely clip, reach depth 2; ONE round; branch at once); at every fully named leaf: rule CC (Lemma CORNER-COVER) -> A208 no-room + pocket CN bound (pockets branched at k = 9) -> A207 basin clip -> A206 Rule NS (MAX_FRAC 0.5) -> the exact cascade + sharp round.  Pad 0 FIRST then the G1 window pad; wall 1800 s per pad per page; depth cap 6; node cap 600; every kill [C: closed-form / library clip trace + the leaf lemma], no verifier clause.

## The 19 alive k5 gallery pages (18 nodes)

| page | pad | stage reached | verdict | seconds |
|---|---|---|---|---|
| k5_11_interior_Y0202 | g1 | 2 (tree: 10 nodes, depth 1, CC 0, exact 0, NS 0, pockets 0) | DEAD | 94 |
| k5_11_interior_Y0202 | zero | 2 (tree: 27 nodes, depth 8, CC 0, exact 0, NS 3, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 1604 |
| k5_11_interior_Y0130 | g1 | 2 (tree: 5 nodes, depth 2, CC 0, exact 0, NS 1, pockets 1) | DEAD | 137 |
| k5_11_interior_Y0130 | zero | 2 (tree: 29 nodes, depth 4, CC 4, exact 0, NS 5, pockets 4) | DEAD (s0-only, WINDOW-PENDING) | 490 |
| k5_11_interior_Y0672 | g1 | 2 (tree: 43 nodes, depth 5, CC 5, exact 0, NS 10, pockets 8) | DEAD | 1005 |
| k5_11_interior_Y0672 | zero | 2 (tree: 99 nodes, depth 5, CC 15, exact 0, NS 14, pockets 13) | ALIVE (wall) | 1800 |
| k5_11_interior_Y0738 | g1 | 2 (tree: 79 nodes, depth 7, CC 4, exact 0, NS 21, pockets 15) | ALIVE (wall) | 1843 |
| k5_11_interior_Y0738 | zero | 2 (tree: 81 nodes, depth 7, CC 7, exact 0, NS 19, pockets 16) | ALIVE (wall) | 1805 |
| k5_16_interior_Y0044 | g1 | 2 (tree: 50 nodes, depth 4, CC 0, exact 0, NS 5, pockets 0) | DEAD | 923 |
| k5_16_interior_Y0044 | zero | 2 (tree: 15 nodes, depth 3, CC 0, exact 0, NS 3, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 527 |
| k5_16_interior_Y0099 | g1 | 2 (tree: 10 nodes, depth 1, CC 0, exact 0, NS 1, pockets 1) | DEAD | 169 |
| k5_16_interior_Y0099 | zero | 2 (tree: 8 nodes, depth 1, CC 0, exact 0, NS 0, pockets 1) | DEAD (s0-only, WINDOW-PENDING) | 78 |
| k5_16_interior_Y0249 | g1 | 2 (tree: 87 nodes, depth 4, CC 0, exact 0, NS 9, pockets 1) | DEAD | 1669 |
| k5_16_interior_Y0249 | zero | 2 (tree: 68 nodes, depth 4, CC 0, exact 0, NS 9, pockets 0) | ALIVE (wall) | 1842 |
| k5_16_interior_Y0402 | g1 | 2 (tree: 40 nodes, depth 6, CC 0, exact 0, NS 7, pockets 0) | ALIVE (wall) | 1847 |
| k5_16_interior_Y0402 | zero | 2 (tree: 43 nodes, depth 5, CC 0, exact 0, NS 9, pockets 0) | ALIVE (wall) | 1849 |
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
| k5_16_interior_Y0865 | g1 | 2 (tree: 186 nodes, depth 9, CC 0, exact 43, NS 16, pockets 2) | ALIVE (wall) | 1804 |
| k5_16_interior_Y0865 | zero | 2 (tree: 137 nodes, depth 8, CC 0, exact 31, NS 16, pockets 4) | ALIVE (wall) | 1802 |
| k5_16_interior_Y0991 | g1 | 2 (tree: 8 nodes, depth 2, CC 0, exact 0, NS 0, pockets 1) | DEAD | 229 |
| k5_16_interior_Y0991 | zero | 2 (tree: 30 nodes, depth 3, CC 0, exact 0, NS 0, pockets 3) | DEAD (s0-only, WINDOW-PENDING) | 762 |
| k5_16_interior_Y1117 | g1 | 2 (tree: 24 nodes, depth 3, CC 0, exact 0, NS 2, pockets 0) | ALIVE (wall) | 1823 |
| k5_16_interior_Y1117 | zero | 2 (tree: 0 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 0 |
| k5_16_interior_Y1022 | g1 | 2 (tree: 35 nodes, depth 3, CC 0, exact 0, NS 4, pockets 5) | DEAD | 710 |
| k5_16_interior_Y1022 | zero | 2 (tree: 33 nodes, depth 3, CC 0, exact 0, NS 2, pockets 6) | DEAD (s0-only, WINDOW-PENDING) | 926 |
| k5_16_interior_Y1056 | g1 | 2 (tree: 14 nodes, depth 4, CC 0, exact 0, NS 5, pockets 0) | ALIVE (wall) | 1895 |
| k5_16_interior_Y1056 | zero | 2 (tree: 25 nodes, depth 4, CC 0, exact 0, NS 4, pockets 3) | ALIVE (wall) | 2006 |

CPU-h in this block: 11.31

## The k5 frontier (A57 census, deepest-first) (40 nodes)

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
| k5_11_interior_Y0041 | zero | 2 (tree: 144 nodes, depth 6, CC 3, exact 0, NS 1, pockets 12) | DEAD (s0-only, WINDOW-PENDING) | 1278 |

CPU-h in this block: 30.92

## Price and projection

* gallery: 13 / 18 pages DEAD at the window pad, 11.31 CPU-h
* frontier: 40 nodes run (10 DEAD at the window pad), 30.92 CPU-h; the census has 297 alive nodes, 263 remaining
* PRICE over the first 20 frontier nodes: mean 2999 s, median 3677 s per node (both pads); PROJECTION for the remaining 263: 219.1 CPU-h (cap 200)

