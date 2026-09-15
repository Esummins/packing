# A224 -- Rule SNAP: the benchmark

Flag `A224_SNAP=1` (default OFF).  Rule SNAP is leaf rule (0) at a fully named leaf and a cheap test after
the coarse round at every internal node; the rule, its soundness chain and its certificate are
`docs/proofs/snap_rule.md` and `attempts/A224-snap-rule/code/snap224.py`.

## 1. The offline scan -- Rule SNAP over every recorded A211 node (`results/snapscan224.jsonl`)

`snapscan224.py ALL --run g1_page` replays the rule on the pose set each node actually had (its recorded
snapshot, padded outward), so it measures where SNAP WOULD fire without spending any search.

| measure | value |
|---|---|
| pages with a candidate | 17 |
| nodes with a SNAP candidate | 294 |
| SNAP / SNAP-DIAG kills | **0** |
| hand-offs (snapped into an open stratum) | 0 |

Most frequent (role, slot) candidates: H@BL(1,1) x171, F2@BR(0,1) x56, F1@BL(1,0) x46, F1@BR(1,0) x14, F1@BR(0,1) x14, F4@BR(0,1) x10, F1@TR(0,0) x4, F3@TR(0,0) x2.

Why a candidate does not fire (blocker set, `(clause b)` = an anonymous square could still meet the cell):

| blocking roles | candidates |
|---|---|
| (clause b) | 149 |
| F3, H | 55 |
| H | 52 |
| F1, F2 | 16 |
| F1, F4 | 12 |
| F2, H | 11 |
| F1 | 7 |
| F5, H | 7 |
| F2 | 3 |
| F4, H | 3 |

## 2. The live A/B -- run211 with the flag ON and OFF (`results/bench224.jsonl`)

Same wall, same pads (g1), same inheritance, isolated cert dirs, `--no-fig`.  With `A224_SNAP` unset the
engine is byte-for-byte the pass-5 engine; the OFF column is the control.

| page | flag | verdict | nodes | dead leaves | alive | SNAP eval / cand / kill / hand-off / partial | SNAP s | first SNAP kill | run s |
|---|---|---|---|---|---|---|---|---|---|
| k5_16_interior_Y0865 | ON | ALIVE | 45 | 24 | 4 | 60 / 60 / **0** / 0 / 0 | 0.17 | None | 422.4 |

**Verdict agreement:** every paired run agrees.

