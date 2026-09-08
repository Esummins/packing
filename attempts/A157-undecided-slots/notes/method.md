# A157 — what the UNDECIDED usable-slot cells of A141 actually are

## 0. Discipline

READ-ONLY on every campaign and on A118/A132/A141 (`lanelib.py`, `polycore.py`, `polylane.py`,
`emit141.py`, `check141.py`, `lane.py`, `corpus.py`, `caselp.py` are imported, never written).
Every A157 file is new, under `attempts/A157-undecided-slots/**`, plus the three named appends
(`attempts/A57-shadow-trees/PAUSED.md`, `attempts/A60-trump5-campaign/notes/ledger.md`,
`docs/residue_ledger.md` §1). `PYTHONDONTWRITEBYTECODE=1`; <= 2 python processes at BelowNormal
with affinity `0xFFFF`; no recursive deletes.

The leaf, the frame, the cores, the certificate format and the checker are A141's, unchanged —
`polycore_slot_lane_v1`, `check141.py`, `lane.cframe_boxes`, `polylane.build_cond(tighten=False)`,
A135 exact pin cores. **Caveat A118-O1 stands**: exact-pin form, class-`S` composition
(`attempts/A118-lane-count/notes/method.md` §2), never the `delta = 10^-2` slack family.

## 1. Correction to the premise

The brief's premise was that A141 recorded those cells UNDECIDED "because the certifying cover was
skipped for speed (`skipped_covers`)". **It did not.** Over the two sweep files (1 693 alive
records, 6 859 cells):

| verdict | count | `skipped_covers` |
|---|---|---|
| `LANE>=2` | 4 750 | true |
| `NEAR-MISS-OR-WORSE` | 1 790 | true |
| `UNDECIDED` | 1 655 | **false** |
| `KILL` | 256 | false |
| `NEAR-MISS` | 163 | false |

`skipped_covers` is set only on the early-exit branch of `polylane.lane_corner_generic`
(`lane_lb + M_lb >= 2`, where a kill is impossible anyway). Every UNDECIDED row carries
`M_exact = true`: the `M` exclusion covers ran and closed. What failed is the **LANE** cover.
With `t2_a5760.py`'s budget (`max_open = 1200`, `lane_depth0 = 20`, `rounds = 8`)
`polylane.lane_cover` returned `lane = None, reason = "open budget exhausted"`, and that branch
also returns `open = []` — which is why 188 of the 196 target rows report the misleading
`cover_open = 0`. A157 is therefore a **budget** job, not a "run the skipped cover" job.

## 2. The target population (task 1, recomputed)

Alive-node cells with `verdict = UNDECIDED`, `lane_lb = 0`, `M <= 1`: **196 cells** on **174
distinct nodes** (`results/undecided_cells.jsonl`, `results/enum157.json`). 17 (nid, slot) pairs
occur twice because the same A57 node sits in two shard trees (e.g.
`k5_11_interior_L1` and `..._G1`), so **179 distinct (node, slot) cells** are actually run.
`M = 0` on 19 of the 196 rows, `M = 1` on 177.

By class and slot (196 rows):

| class | slot | n |  | class | slot | n |
|---|---|---|---|---|---|---|
| k5_16 | BL(1,0) | 40 |  | trump5 | BR(0,1) | 22 |
| k5_16 | TL(1,0) | 27 |  | trump5 | TR(0,1) | 12 |
| k5_16 | BR(0,1) | 16 |  | trump5 | BL(0,2) | 7 |
| k5_16 | TR(0,1) | 11 |  | trump5 | BL(1,1) | 6 |
| k5_16 | TR(1,0) | 10 |  | trump5 | TL(0,0) | 1 |
| k5_16 | BR(1,0) | 9 |  | k5_11 | BL(1,1) | 23 |
|  |  |  |  | k5_11 | BR(0,1) | 8 |
|  |  |  |  | k5_11 | TL(1,0) | 3 |
|  |  |  |  | k5_11 | TR(0,0) | 1 |

By class and level: k5_16 L1 103 / L2 10; trump5 L1 48; k5_11 L1 23 / L2 7 / L3 5.

## 3. The cheap thing first: a 50x bigger sample screen (`code/screen157.py`)

A141 screened with **8 000** poses. `lane_lb = 0` there means *no free pose was drawn*, which is
not evidence that none exists. A157 re-screens every one of the 179 cells with **400 000** poses
(~2 s/cell, 179 cells in ~6 min on two workers) and records `drawn / meeting / free`, the best
core clearance `max over meeting poses of min over cores of (-depth)`, a free-pose witness with
its per-core depths, and a realised interior-disjoint pair when one exists.

Result (`results/screen157.jsonl`, `results/screen157_s1.jsonl`):

| screen `lane_lb` | `M = 0` | `M = 1` | total |
|---|---|---|---|
| 0 | 11 | 77 | 88 |
| 1 | 5 | 75 | 80 |
| 2 | 0 | 11 | 11 |

**91 of the 179 cells realise `LANE_K' >= 1` at the bigger draw**, and for the 75 of those with
`M = 1` (and the 11 with `lane_lb = 2`) that is a *proof that no kill is available by this leaf* —
`LANE + M >= 2` — obtained for 2 s of sampling each rather than a cover. A kill remains possible on
`lane_lb + M <= 1`: **93 cells** (77 at `(0, 1)`, 11 at `(0, 0)`, 5 at `(1, 0)`).

## 4. The certifying covers (`code/run157.py`)

`polylane.lane_corner_generic` with `keep_cert=True` on a budget ladder; rung 1 reproduces A141's
`(depth0 = 20, max_open = 1200)`, rung 2 escalates to `(21, 4000)`, with a per-cell wall between
rungs. Kills are emitted with `emit141.cert_dict(kind="polycore_slot_lane", …)`, i.e. exactly
A141's `polycore_slot_lane_v1`, with the provenance of the A141 row and the sample line
(drawn -> meeting -> free) attached, and checked with A141's own `check141.py`.

Note the asymmetry the numbers force:

* a cell with `M = 0` needs only `LANE_K' <= 1`, which `lane_cover` certifies with a NON-EMPTY
  open set (all open pairs always-overlapping) — cheap;
* a cell with `M = 1` needs `LANE_K' = 0`, i.e. an **empty** open set — every box of a complete
  cover of the pose window discharged by container / misses-cell / a shared rational point. On
  these cells the frontier does not empty: the depth-20 -> depth-21 refinement roughly doubles it.

`code/probe157.py` prices the rungs on a single cell (leaf count, open count, seconds, RSS); it is
what showed that `depth0 >= 24` with `max_open >= 40 000` runs into GB-scale memory in
`lane_cover`'s leaf list (`max_open` bounds only the frontier, not the discharged leaves).

## 5. What the covers returned

**25 cells covered, 0 kills, 1 near-miss, 24 not closed** (`results/t157_cells.jsonl`,
`t157_cells_s1.jsonl`, `t157_deep.jsonl`; tables in `results/summary157.json`). The 25 include
**all 16** of the kill-possible cells with `M = 0` — the only sub-population where a kill was
structurally reachable at this budget, because `M = 0` needs only `LANE_K' <= 1`, which
`lane_cover` certifies with a NON-EMPTY open set. None of the 16 closed. The 68 cells left
unrun are all `M = 1`; they need `LANE_K' = 0`, i.e. an **empty** cover, which no measured cell
came close to.

Where the cover stops, measured at `(depth0 = 21, max_open = 4 000)`:

* **21 of 25 never finish the DFS phase**: the undischarged frontier at depth 20-21 passes 4 000
  before the subdivision is complete (322-4 560 discharged leaves at the cut). The probe ladder on
  the best candidate, `k5_16_interior_Y0410 BL(1,0)` (clearance 1.36e-1, the largest in the
  corpus), gives `depth0 = 20 -> 324` leaves and `depth0 = 21 -> 799` leaves, both budget-cut:
  the frontier roughly doubles per level, so the discharge is not converging.
* **4 reach the refinement phase and the open set still grows**: `k5_16_interior_Y0149_D02
  TR(1,0)` goes `43 -> 38 -> 55 -> 80 -> 122 -> 203 -> 306 -> 497 -> 873` over the 8 rounds
  (`..._D00` `51 -> ... -> 506`), i.e. the always-overlap screen keeps finding open pairs that are
  genuinely far apart — `LANE_K' <= 1` is not merely unproved there, the 2-crowd hypothesis is not
  being squeezed.
* **1 closes**: `k5_16_interior_Y0254 BL(1,0)` certifies `LANE_K' <= 1` on 2 296 always-overlapping
  open boxes, and with `M = 1` that is `NEAR-MISS`, not a kill.
* A single cell at `(21, 30 000)` (`k5_16_interior_Y0383 BL(1,0)`, `M = 0`, clearance 6.2e-2) had
  not completed after 125 CPU-s and was stopped; RSS stayed at 43 MB, so the wall, not memory, is
  the binding constraint at that rung.

**No `polycore_slot_lane_v1` certificate was emitted, because no cell reached `LANE_K' + M <= 1`.**
`results/slot_kills157.jsonl` is therefore empty by construction, not by omission. The checker
was exercised as a control: `check141.py` PASSes A141's `slot_slack0.02_c0_Y0281__TL0_0.json` in
this environment, so the emit/check path is live and would have produced certificates had a cell
closed.

## 6. The PI's example, answered

`c0_Y0076` (A60 trump5, level 1, alive) has exactly two non-`LANE>=2` cells in A141's sweep, and
both are the PI's: `TL(0,0)` and `BL(0,2)`, each `UNDECIDED, lane_lb = 0, M = 1`. At 400 000 poses
**both realise a free pose**, so `LANE_K' >= 1` and, with `M = 1`, no kill by this leaf:

| cell | drawn | meeting | free | clearance from every core |
|---|---|---|---|---|
| `TL(0,0)` | 400 000 | 231 041 | 14 | **1.1026e-2** at `c = (1.6807459, 0.6862003)`, `theta = 29.4420 deg` |
| `BL(0,2)` | 400 000 | 270 606 | 3 | **5.2398e-3** at `c = (1.6636782, 3.1947477)`, `theta = 61.0252 deg` |

In both witnesses the binding core is the conditioned square's (index 5, depth `-1.10e-2` /
`-5.24e-3`); every pin core is between 0.5 and 1.75 away. The clearances are ten orders of
magnitude above the float64 geometry noise, and the free pose lies in the container and meets the
closed slot cell, so it is in `R'(C)` by definition. The PI's reading — that a second meeter of
`TL(0,0)` would have to be a corner intrusion that does not fit — is not what the pose window says:
a free square tilted 29.44 deg does reach the cell while clearing the hypothesis square's core by
1.1e-2.

## 7. Cost and disposition

~0.7 CPU-h of the 3 CPU-h cap (the box carried 14 other lab python processes throughout, so the
two A157 workers held ~10 % of a core each and WALL, not CPU, was the binding limit). Two
processes, BelowNormal, affinity `0xFFFF`, throughout. The 68 unrun cells are listed in
`results/summary157.json -> screen.not_run_cells` and are resumable from
`results/cover_jobs_rem.jsonl`; on the measured evidence they are not worth buying.
