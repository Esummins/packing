# A220 benchmark -- exact-first (flag A220_EXACT_FIRST) and the short no-room child cap (A220_NOROOM_INHERIT)

`off` = the same code with every A220 flag unset (the control); `ef` = exact-first at every role split;
`efs` = exact-first only when the role the split would bisect is positionally small (< 0.25); `nri` = `efs`
+ the short no-room child cap; `eqbase` / `eqoff` = the equivalence pair (pre-A220 code vs this code, flags
off, same page / pad / wall).  All runs: pad g1, one runner, BelowNormal, wall as shown.

| page | cfg | inh | verdict | s | ratio | nodes | dead | cc | rsplit | exact | ef run/kill/TO | nr runs | short | coarse s | noroom s | exact s | other s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| k5_11_interior_Y0672 | eqbase | n | ALIVE (wall) | 602 | 0.33 | 63 | 40 | 2 | 1 | 0 | 0/0/0 | 12 | None | 166.7 (28%) | 423.9 (70%) | 0.0 (0%) | 11.9 |
| k5_11_interior_Y0672 | eqoff | n | ALIVE (wall) | 601 | 0.33 | 61 | 39 | 2 | 0 | 0 | 0/0/0 | 10 | 0 | 190.5 (32%) | 397.3 (66%) | 0.0 (0%) | 13.0 |
| k5_11_interior_Y0672 | off | n | ALIVE (wall) | 1828 | 1.00 | 126 | 71 | 11 | 11 | 0 | 0/0/0 | 42 | 0 | 344.6 (19%) | 1436.1 (79%) | 0.0 (0%) | 47.0 |
| k5_11_interior_Y0672 | efs | n | ALIVE (wall) | 1820 | 1.00 | 126 | 71 | 11 | 11 | 0 | 0/0/0 | 42 | 0 | 337.9 (19%) | 1436.3 (79%) | 0.0 (0%) | 45.5 |
| k5_11_interior_Y0738 | off | y | ALIVE (wall) | 1808 | 1.00 | 74 | 56 | 1 | 7 | 0 | 0/0/0 | 36 | 0 | 547.4 (30%) | 780.7 (43%) | 0.0 (0%) | 479.5 |
| k5_11_interior_Y0738 | nri | y | ALIVE (wall) | 1813 | 1.00 | 93 | 68 | 1 | 7 | 0 | 0/0/0 | 41 | 0 | 428.7 (24%) | 1029.1 (57%) | 0.0 (0%) | 355.4 |
| k5_16_interior_Y0249 | off | n | ALIVE (wall) | 1852 | 1.00 | 103 | 68 | 0 | 0 | 0 | 0/0/0 | 37 | 0 | 296.6 (16%) | 1495.2 (81%) | 0.0 (0%) | 60.7 |
| k5_16_interior_Y0402 | off | y | ALIVE (wall) | 1803 | 1.00 | 72 | 46 | 0 | 9 | 0 | 0/0/0 | 32 | 0 | 1121.2 (62%) | 493.1 (27%) | 0.0 (0%) | 189.0 |
| k5_16_interior_Y0402 | nri | y | ALIVE (wall) | 1809 | 1.00 | 71 | 45 | 0 | 8 | 1 | 1/1/0 | 32 | 0 | 1137.7 (63%) | 491.8 (27%) | 3.0 (0%) | 176.5 |
| k5_16_interior_Y0460 | off | n | DEAD | 1449 | 1.00 | 64 | 32 | 0 | 0 | 0 | 0/0/0 | 24 | 0 | 267.2 (18%) | 1117.0 (77%) | 0.0 (0%) | 64.4 |
| k5_16_interior_Y0460 | efs | n | DEAD | 1453 | 1.00 | 64 | 32 | 0 | 0 | 0 | 0/0/0 | 24 | 0 | 265.9 (18%) | 1122.5 (77%) | 0.0 (0%) | 64.3 |
| k5_16_interior_Y0500 | off | n | ALIVE (wall) | 1850 | 1.00 | 158 | 109 | 0 | 1 | 0 | 0/0/0 | 28 | 0 | 358.8 (19%) | 1404.0 (76%) | 0.0 (0%) | 86.8 |
| k5_16_interior_Y0500 | efs | n | RUNNING | 1697 | 0.92 | 151 | None | None | None | None | 1/1/0 | 0 | None | 388.1 (23%) | 0 (0%) | 0.4 (0%) | 1308.5 |
| k5_16_interior_Y0865 | off | y | ALIVE (wall) | 1804 | 1.00 | 134 | 57 | 0 | 31 | 38 | 0/0/0 | 82 | 0 | 1196.0 (66%) | 127.1 (7%) | 345.3 (19%) | 135.1 |
| k5_16_interior_Y0865 | ef | y | ALIVE (wall) | 1801 | 1.00 | 89 | 42 | 0 | 14 | 22 | 28/5/0 | 52 | 0 | 807.1 (45%) | 313.5 (17%) | 599.5 (33%) | 80.8 |
| k5_16_interior_Y0865 | efs | y | ALIVE (wall) | 1809 | 1.00 | 95 | 44 | 0 | 22 | 26 | 18/4/0 | 60 | 0 | 1018.9 (56%) | 122.3 (7%) | 574.2 (32%) | 93.5 |
| k5_16_interior_Y0865 | nri | y | ALIVE (wall) | 1802 | 1.00 | 129 | 59 | 0 | 24 | 30 | 18/4/0 | 76 | 0 | 845.0 (47%) | 450.6 (25%) | 412.2 (23%) | 94.3 |
| k5_16_interior_Y0865 | smoke | y | RUNNING | 546 | 0.30 | 22 | None | None | None | None | 6/4/0 | 0 | None | 319.6 (59%) | 0 (0%) | 89.0 (16%) | 137.0 |

**ef**: geometric-mean ratio 0.999 over 1 page(s); no verdict regression.

**efs**: geometric-mean ratio 0.979 over 4 page(s); no verdict regression.

**nri**: geometric-mean ratio 1.002 over 3 page(s); no verdict regression.

**flag-off equivalence** (k5_11_interior_Y0672, pad g1, no inherit): pre-A220 code ALIVE in 602 s (63 nodes) vs this code ALIVE in 601 s (61 nodes) -- node list and verdicts DIFFER.
  first difference: R.3.1.2.p2.p2:INTERNAL:None vs R.3.1.2.p2.p2:ALIVE:None
