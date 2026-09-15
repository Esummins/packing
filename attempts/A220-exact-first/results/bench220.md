# A220 benchmark -- exact-first (flag A220_EXACT_FIRST) and the short no-room child cap (A220_NOROOM_INHERIT)

`off` = the same code with every A220 flag unset (the control); `ef` = exact-first at every role split;
`efs` = exact-first only when the role the split would bisect is positionally small (< 0.25); `nri` = `efs`
+ the short no-room child cap; `eqbase` / `eqoff` = the equivalence pair (pre-A220 code vs this code, flags
off, same page / pad / wall).  All runs: pad g1, one runner, BelowNormal, wall as shown.

| page | cfg | inh | verdict | s | ratio | nodes | dead | cc | rsplit | exact | ef run/kill/TO | nr runs | short | coarse s | noroom s | exact s | other s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
