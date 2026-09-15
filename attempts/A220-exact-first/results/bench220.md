# A220 benchmark -- exact-first (flag A220_EXACT_FIRST) and the short no-room child cap (A220_NOROOM_INHERIT)

`off` = the same code with every A220 flag unset (the control); `ef` = exact-first at every role split;
`efs` = exact-first only when the role the split would bisect is positionally small (< 0.25); `nri` = `efs`
+ the short no-room child cap; `eqbase` / `eqoff` = the equivalence pair (pre-A220 code vs this code, flags
off, same page / pad / wall).  All runs: pad g1, one runner, BelowNormal, wall as shown.

| page | cfg | inh | verdict | s | ratio | nodes | dead | cc | rsplit | exact | ef run/kill/TO | nr runs | short | coarse s | noroom s | exact s | other s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| k5_11_interior_Y0672 | eqbase | n | ALIVE (wall) | 602 | - | 63 | 40 | 2 | 1 | 0 | 0/0/0 | 12 | None | 166.7 (28%) | 423.9 (70%) | 0.0 (0%) | 11.9 |
| k5_11_interior_Y0672 | eqoff | n | ALIVE (wall) | 601 | - | 61 | 39 | 2 | 0 | 0 | 0/0/0 | 10 | 0 | 190.5 (32%) | 397.3 (66%) | 0.0 (0%) | 13.0 |
| k5_11_interior_Y0738 | off | y | ALIVE (wall) | 1808 | 1.00 | 74 | 56 | 1 | 7 | 0 | 0/0/0 | 36 | 0 | 547.4 (30%) | 780.7 (43%) | 0.0 (0%) | 479.5 |
| k5_16_interior_Y0402 | off | y | ALIVE (wall) | 1803 | 1.00 | 72 | 46 | 0 | 9 | 0 | 0/0/0 | 32 | 0 | 1121.2 (62%) | 493.1 (27%) | 0.0 (0%) | 189.0 |
| k5_16_interior_Y0402 | nri | y | ALIVE (wall) | 1809 | 1.00 | 71 | 45 | 0 | 8 | 1 | 1/1/0 | 32 | 0 | 1137.7 (63%) | 491.8 (27%) | 3.0 (0%) | 176.5 |
| k5_16_interior_Y0865 | off | y | ALIVE (wall) | 1804 | 1.00 | 134 | 57 | 0 | 31 | 38 | 0/0/0 | 82 | 0 | 1196.0 (66%) | 127.1 (7%) | 345.3 (19%) | 135.1 |
| k5_16_interior_Y0865 | ef | y | RUNNING | 735 | 0.41 | 28 | None | None | None | None | 7/4/0 | 0 | None | 459.0 (62%) | 0 (0%) | 133.6 (18%) | 142.1 |
| k5_16_interior_Y0865 | efs | y | ALIVE (wall) | 1809 | 1.00 | 95 | 44 | 0 | 22 | 26 | 18/4/0 | 60 | 0 | 1018.9 (56%) | 122.3 (7%) | 574.2 (32%) | 93.5 |
| k5_16_interior_Y0865 | smoke | y | RUNNING | 546 | 0.30 | 22 | None | None | None | None | 6/4/0 | 0 | None | 319.6 (59%) | 0 (0%) | 89.0 (16%) | 137.0 |

**ef**: geometric-mean ratio 0.407 over 1 page(s); no verdict regression.

**efs**: geometric-mean ratio 1.003 over 1 page(s); no verdict regression.

**nri**: geometric-mean ratio 1.003 over 1 page(s); no verdict regression.

**flag-off equivalence** (k5_11_interior_Y0672, pad g1, no inherit): pre-A220 code ALIVE in 602 s (63 nodes) vs this code ALIVE in 601 s (61 nodes) -- node list and verdicts DIFFER.
  first difference: R.3.1.2.p2.p2:INTERNAL:None vs R.3.1.2.p2.p2:ALIVE:None
