# A257 -- the seam pilot's SIBLING TABLE (results/pilot257.jsonl)

Page `synth257_d001_h002_t2`, pad `g1`, delta_pin 1e-2.  Spine: **14 aligned cut(s)**, 1 TUBE-KILL, 18 gate hit(s), 19 node(s), 108.7 s.  Each sibling below is run on its own with A211's ORDINARY rules (the gate is false there), the spine replayed first.

| # | sibling | cut | excess x r | verdict | rule | subtree s | nodes | run s |
|---|---|---|---|---|---|---|---|---|
| 1 | `R.2` | F3 y >= 2.534157 | 527.0995 | **DEAD** | EmptyBox,FC+EPS | 132.8 | 9 | 154.4 |
| 2 | `R.1.1` | F3 t <= 89.8797 | 475.1915 | **ALIVE** | EmptyBox,FC+EPS | 543.6 | 46 | 576.0 |
| 3 | `R.1.2.1` | F1 t <= 40.0616 | 173.6092 | **ALIVE** | FC+EPS | 144.4 | 6 | 178.8 |
| 4 | `R.1.2.2.2` | F1 x >= 1.537886 | 8.5978 | **DEAD** | EmptyBox,FC+EPS | 18.0 | 4 | 56.6 |
| 5 | `R.1.2.2.1.2` | F1 t >= 40.3023 | 3.8285 | **DEAD** | EmptyBox,FC+EPS | 48.0 | 4 | 107.2 |
| 6 | `R.1.2.2.1.1.1.2` | F2 t >= 40.3023 | 1.9683 | **DEAD** | EmptyBox | 46.8 | 2 | 104.2 |
| 7 | `R.1.2.2.1.1.1.1.1` | F2 t <= 40.0616 | 1.0831 | **DEAD** | EmptyBox | 37.4 | 2 | 90.3 |
| 8 | `R.1.2.2.1.1.1.1.2.2` | F4 t >= 40.3023 | 1.0383 | **DEAD** | EmptyBox | 23.0 | 2 | 78.6 |
| 9 | `R.1.2.2.1.1.1.1.2.1.2` | F2 y >= 1.938074 | 0.6463 | **DEAD** | EmptyBox | 3.6 | 1 | 63.8 |
| 10 | `R.1.2.2.1.1.1.1.2.1.1.1` | H1 t <= 40.0616 | 0.4039 | **DEAD** | EmptyBox | 11.5 | 2 | 78.5 |
| 11 | `R.1.2.2.1.1.1.1.2.1.1.2.1` | F1 x <= 1.534688 | 0.2805 | **DEAD** | EmptyBox | 6.8 | 2 | 80.0 |
| 12 | `R.1.2.2.1.1.1.1.2.1.1.2.2.2` | F4 y >= 1.273853 | 0.202 | **DEAD** | EmptyBox | 1.4 | 1 | 79.2 |
| 13 | `R.1.2.2.1.1.1.1.2.1.1.2.2.1.1` | F4 t <= 40.0616 | 0.1531 | **DEAD** | FC | 7.3 | 1 | 94.9 |
| 14 | `R.1.2.2.1.1.1.1.2.1.1.2.2.1.2.2` | F3 x >= 0.501599 | 0.043 | **DEAD** | EmptyBox | 0.2 | 1 | 114.1 |

Rules: `EmptyBox` = the multibox cascade emptied a role; `CC` = Lemma CORNER-COVER; `NOROOM*` = A189 Lemma 1 / Lemma CN; `REACH`, `S-PAIR`, `RSPLIT-EMPTY`, `SNAP`, `FC+EPS` as in A211 notes/coarse_tree.md.
