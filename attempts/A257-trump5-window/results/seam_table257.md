# A257 -- the seam pilot's SIBLING TABLE (results/pilot257.jsonl)

Page `synth257_d001_h002_t2`, pad `g1`, delta_pin 1e-2.  Spine: **14 aligned cut(s)**, 1 TUBE-KILL, 18 gate hit(s), 19 node(s), 108.7 s.  Each sibling below is run on its own with A211's ORDINARY rules (the gate is false there), the spine replayed first.

| # | sibling | cut | excess x r | verdict | rule | subtree s | nodes | run s |
|---|---|---|---|---|---|---|---|---|
| 1 | `R.2` | F3 y >= 2.534157 | 527.0995 | **not run** | - | None | None | None |
| 2 | `R.1.1` | F3 t <= 89.8797 | 475.1915 | **not run** | - | None | None | None |
| 3 | `R.1.2.1` | F1 t <= 40.0616 | 173.6092 | **not run** | - | None | None | None |
| 4 | `R.1.2.2.2` | F1 x >= 1.537886 | 8.5978 | **not run** | - | None | None | None |
| 5 | `R.1.2.2.1.2` | F1 t >= 40.3023 | 3.8285 | **not run** | - | None | None | None |
| 6 | `R.1.2.2.1.1.1.2` | F2 t >= 40.3023 | 1.9683 | **not run** | - | None | None | None |
| 7 | `R.1.2.2.1.1.1.1.1` | F2 t <= 40.0616 | 1.0831 | **not run** | - | None | None | None |
| 8 | `R.1.2.2.1.1.1.1.2.2` | F4 t >= 40.3023 | 1.0383 | **not run** | - | None | None | None |
| 9 | `R.1.2.2.1.1.1.1.2.1.2` | F2 y >= 1.938074 | 0.6463 | **not run** | - | None | None | None |
| 10 | `R.1.2.2.1.1.1.1.2.1.1.1` | H1 t <= 40.0616 | 0.4039 | **not run** | - | None | None | None |
| 11 | `R.1.2.2.1.1.1.1.2.1.1.2.1` | F1 x <= 1.534688 | 0.2805 | **not run** | - | None | None | None |
| 12 | `R.1.2.2.1.1.1.1.2.1.1.2.2.2` | F4 y >= 1.273853 | 0.202 | **not run** | - | None | None | None |
| 13 | `R.1.2.2.1.1.1.1.2.1.1.2.2.1.1` | F4 t <= 40.0616 | 0.1531 | **not run** | - | None | None | None |
| 14 | `R.1.2.2.1.1.1.1.2.1.1.2.2.1.2.2` | F3 x >= 0.501599 | 0.043 | **not run** | - | None | None | None |

Rules: `EmptyBox` = the multibox cascade emptied a role; `CC` = Lemma CORNER-COVER; `NOROOM*` = A189 Lemma 1 / Lemma CN; `REACH`, `S-PAIR`, `RSPLIT-EMPTY`, `SNAP`, `FC+EPS` as in A211 notes/coarse_tree.md.
