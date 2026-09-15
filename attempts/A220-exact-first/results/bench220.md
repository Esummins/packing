# A220 benchmark -- exact-first (flag A220_EXACT_FIRST) and the short no-room child cap (A220_NOROOM_INHERIT)

`off` = the same code with every A220 flag unset (the control); `ef` = exact-first at every role split;
`efs` = exact-first only when the role the split would bisect is positionally small (< 0.25); `nri` = `efs`
+ the short no-room child cap; `eqbase` / `eqoff` = the equivalence pair (pre-A220 code vs this code, flags
off, same page / pad / wall).  All runs: pad g1, one runner, BelowNormal, wall as shown.

| page | cfg | inh | verdict | s | ratio | nodes | dead | cc | rsplit | exact | ef run/kill/TO | nr runs | short | coarse s | noroom s | exact s | other s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| k5_11_interior_Y0672 | eqbase | n | ALIVE (wall) | 602 | - | 63 | 40 | 2 | 1 | 0 | 0/0/0 | 12 | None | 166.7 (28%) | 423.9 (70%) | 0.0 (0%) | 11.9 |
| k5_11_interior_Y0672 | eqoff | n | RUNNING | 46 | - | 30 | None | None | None | None | 0/0/0 | 0 | None | 44.0 (96%) | 0 (0%) | 0.0 (0%) | 1.9 |
| k5_16_interior_Y0865 | smoke | y | RUNNING | 546 | - | 22 | None | None | None | None | 6/4/0 | 0 | None | 319.6 (59%) | 0 (0%) | 89.0 (16%) | 137.0 |

**flag-off equivalence** (k5_11_interior_Y0672, pad g1, no inherit): pre-A220 code ALIVE in 602 s (63 nodes) vs this code RUNNING in 46 s (30 nodes) -- node list and verdicts DIFFER.
  first difference: length 72 vs 30
