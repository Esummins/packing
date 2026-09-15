# A220 benchmark -- exact-first (flag A220_EXACT_FIRST) and the short no-room child cap (A220_NOROOM_INHERIT)

`off` = the same code with every A220 flag unset (the control); `ef` = exact-first at every role split;
`efs` = exact-first only when the role the split would bisect is positionally small (< 0.25); `nri` = `efs`
+ the short no-room child cap; `eqbase` / `eqoff` = the equivalence pair (pre-A220 code vs this code, flags
off, same page / pad / wall).  All runs: pad g1, one runner, BelowNormal, wall as shown.

| page | cfg | inh | verdict | s | ratio | nodes | dead | cc | rsplit | exact | ef run/kill/TO | nr runs | short | coarse s | noroom s | exact s | other s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| k5_11_interior_Y0672 | eqbase | n | ALIVE (wall) | 602 | - | 63 | 40 | 2 | 1 | 0 | 0/0/0 | 12 | None | 166.7 (28%) | 423.9 (70%) | 0.0 (0%) | 11.9 |
| k5_11_interior_Y0672 | eqoff | n | ALIVE (wall) | 601 | - | 61 | 39 | 2 | 0 | 0 | 0/0/0 | 10 | 0 | 190.5 (32%) | 397.3 (66%) | 0.0 (0%) | 13.0 |
| k5_16_interior_Y0402 | off | y | ALIVE (wall) | 1803 | 1.00 | 72 | 46 | 0 | 9 | 0 | 0/0/0 | 32 | 0 | 1121.2 (62%) | 493.1 (27%) | 0.0 (0%) | 189.0 |
| k5_16_interior_Y0865 | off | y | RUNNING | 773 | 1.00 | 49 | None | None | None | None | 0/0/0 | 0 | None | 566.6 (73%) | 0 (0%) | 59.3 (8%) | 146.8 |
| k5_16_interior_Y0865 | smoke | y | RUNNING | 546 | 0.71 | 22 | None | None | None | None | 6/4/0 | 0 | None | 319.6 (59%) | 0 (0%) | 89.0 (16%) | 137.0 |

**flag-off equivalence** (k5_11_interior_Y0672, pad g1, no inherit): pre-A220 code ALIVE in 602 s (63 nodes) vs this code ALIVE in 601 s (61 nodes) -- node list and verdicts DIFFER.
  first difference: R.3.1.2.p2.p2:INTERNAL:None vs R.3.1.2.p2.p2:ALIVE:None
