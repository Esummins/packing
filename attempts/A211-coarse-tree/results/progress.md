# A211 progress -- 2026-09-13 03:52:57

The COARSE tree (notes/coarse_tree.md): A202 stage 0 + A203 CSP; coarse internal nodes (re-binned pieces <= 96 units, refine 1, no lonely clip, reach depth 2; ONE round; branch at once); at every fully named leaf: rule CC (Lemma CORNER-COVER) -> A208 no-room + pocket CN bound (pockets branched at k = 9) -> A207 basin clip -> A206 Rule NS (MAX_FRAC 0.5) -> the exact cascade + sharp round.  Pad 0 FIRST then the G1 window pad; wall 1800 s per pad per page; depth cap 6; node cap 600; every kill [C: closed-form / library clip trace + the leaf lemma], no verifier clause.

## The 19 alive k5 gallery pages (18 nodes)

| page | pad | stage reached | verdict | seconds |
|---|---|---|---|---|
| k5_11_interior_Y0202 | g1 | 2 (tree: 1 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | ALIVE | 92 |
| k5_11_interior_Y0202 | zero | 2 (tree: 13 nodes, depth 2, CC 0, exact 2, NS 4, pockets 0) | ALIVE (wall) | 945 |
| k5_11_interior_Y0130 | g1 | 2 (tree: 28 nodes, depth 2, CC 3, exact 1, NS 0, pockets 1) | ALIVE | 1224 |
| k5_11_interior_Y0130 | zero | 2 (tree: 17 nodes, depth 3, CC 2, exact 3, NS 2, pockets 2) | ALIVE (wall) | 1853 |
| k5_11_interior_Y0672 | g1 | 2 (tree: 9 nodes, depth 1, CC 0, exact 3, NS 0, pockets 1) | ALIVE (wall) | 1922 |
| k5_11_interior_Y0672 | zero | 2 (tree: 12 nodes, depth 1, CC 0, exact 4, NS 2, pockets 0) | ALIVE (wall) | 1823 |
| k5_11_interior_Y0738 | g1 | 2 (tree: 13 nodes, depth 2, CC 2, exact 2, NS 2, pockets 0) | ALIVE (wall) | 1811 |
| k5_11_interior_Y0738 | zero | 2 (tree: 17 nodes, depth 4, CC 2, exact 1, NS 6, pockets 1) | ALIVE (wall) | 1819 |
| k5_16_interior_Y0044 | g1 | 2 (tree: 31 nodes, depth 5, CC 0, exact 2, NS 9, pockets 1) | ALIVE (wall) | 1848 |
| k5_16_interior_Y0044 | zero | 2 (tree: 23 nodes, depth 5, CC 0, exact 5, NS 6, pockets 0) | ALIVE (wall) | 1807 |
| k5_16_interior_Y0099 | g1 | 2 (tree: 59 nodes, depth 3, CC 0, exact 0, NS 1, pockets 1) | ALIVE (wall) | 1822 |
| k5_16_interior_Y0099 | zero | 2 (tree: 64 nodes, depth 3, CC 0, exact 0, NS 3, pockets 1) | ALIVE (wall) | 1842 |
| k5_16_interior_Y0249 | g1 | 2 (tree: 24 nodes, depth 2, CC 0, exact 2, NS 1, pockets 0) | ALIVE (wall) | 1810 |
| k5_16_interior_Y0249 | zero | 2 (tree: 24 nodes, depth 3, CC 0, exact 2, NS 8, pockets 0) | ALIVE (wall) | 1808 |
| k5_16_interior_Y0402 | g1 | 2 (tree: 13 nodes, depth 3, CC 0, exact 3, NS 4, pockets 0) | ALIVE (wall) | 1919 |
| k5_16_interior_Y0402 | zero | 2 (tree: 10 nodes, depth 3, CC 0, exact 2, NS 2, pockets 0) | ALIVE (wall) | 1826 |
| k5_16_interior_Y0460 | g1 | 2 (tree: 15 nodes, depth 3, CC 0, exact 0, NS 5, pockets 0) | ALIVE (wall) | 1857 |
| k5_16_interior_Y0460 | zero | 2 (tree: 15 nodes, depth 3, CC 0, exact 0, NS 5, pockets 0) | ALIVE (wall) | 1860 |
| k5_16_interior_Y0719 | g1 | 2 (tree: 9 nodes, depth 1, CC 0, exact 0, NS 0, pockets 0) | DEAD | 237 |
| k5_16_interior_Y0719 | zero | 2 (tree: 13 nodes, depth 1, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 558 |
| k5_16_interior_Y0500 | g1 | 2 (tree: 29 nodes, depth 2, CC 0, exact 0, NS 2, pockets 0) | ALIVE (wall) | 1827 |
| k5_16_interior_Y0500 | zero | 2 (tree: 32 nodes, depth 2, CC 0, exact 0, NS 2, pockets 0) | ALIVE (wall) | 1814 |
| k5_16_interior_Y0660 | g1 | 2 (tree: 13 nodes, depth 5, CC 0, exact 1, NS 7, pockets 0) | ALIVE (wall) | 2026 |
| k5_16_interior_Y0660 | zero | 2 (tree: 19 nodes, depth 6, CC 0, exact 1, NS 6, pockets 0) | ALIVE (wall) | 2009 |
| k5_16_interior_Y0881 | g1 | 2 (tree: 26 nodes, depth 2, CC 0, exact 0, NS 2, pockets 0) | DEAD | 879 |
| k5_16_interior_Y0881 | zero | 2 (tree: 34 nodes, depth 3, CC 0, exact 0, NS 2, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 1144 |
| k5_16_interior_Y0865 | g1 | 2 (tree: 17 nodes, depth 6, CC 0, exact 0, NS 4, pockets 0) | ALIVE (wall) | 1841 |
| k5_16_interior_Y0865 | zero | 2 (tree: 15 nodes, depth 4, CC 0, exact 2, NS 3, pockets 0) | ALIVE (wall) | 1891 |
| k5_16_interior_Y0991 | g1 | 2 (tree: 21 nodes, depth 2, CC 0, exact 0, NS 1, pockets 0) | ALIVE (wall) | 1852 |
| k5_16_interior_Y0991 | zero | 2 (tree: 11 nodes, depth 7, CC 0, exact 0, NS 1, pockets 0) | ALIVE (wall) | 1812 |
| k5_16_interior_Y1117 | g1 | 2 (tree: 24 nodes, depth 3, CC 0, exact 0, NS 2, pockets 0) | ALIVE (wall) | 1823 |
| k5_16_interior_Y1117 | zero | 2 (tree: 0 nodes, depth 0, CC 0, exact 0, NS 0, pockets 0) | DEAD (s0-only, WINDOW-PENDING) | 0 |
| k5_16_interior_Y1022 | g1 | 2 (tree: 17 nodes, depth 4, CC 0, exact 1, NS 3, pockets 0) | ALIVE (wall) | 1932 |
| k5_16_interior_Y1022 | zero | 2 (tree: 10 nodes, depth 4, CC 0, exact 0, NS 2, pockets 0) | ALIVE (wall) | 1832 |
| k5_16_interior_Y1056 | g1 | 2 (tree: 14 nodes, depth 4, CC 0, exact 0, NS 5, pockets 0) | ALIVE (wall) | 1895 |
| k5_16_interior_Y1056 | zero | 2 (tree: 12 nodes, depth 2, CC 0, exact 0, NS 4, pockets 0) | ALIVE (wall) | 1846 |

CPU-h in this block: 15.86

## The k5 frontier (A57 census, deepest-first) (20 nodes)

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
| k5_11_interior_Y0414_D06 | zero | 2 (tree: 21 nodes, depth 6, CC 1, exact 1, NS 5, pockets 1) | ALIVE (wall) | 2075 |
| k5_11_interior_Y0636_D06 | zero | 2 (tree: 28 nodes, depth 5, CC 0, exact 0, NS 1, pockets 1) | ALIVE (wall) | 1808 |

CPU-h in this block: 15.64

## Price and projection

* gallery: 2 / 18 pages DEAD at the window pad, 15.86 CPU-h
* frontier: 20 nodes run (4 DEAD at the window pad), 15.64 CPU-h; the census has 314 alive nodes, 283 remaining
* PRICE over the first 20 frontier nodes: mean 2814 s, median 3670 s per node (both pads); PROJECTION for the remaining 283: 221.2 CPU-h (cap 200)
* **STOP: the projection exceeds the cap -- the workers exit after their current node**

