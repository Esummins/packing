# A152 T2 — Y1117, and the sweep

## 1. What was run

| stage | driver | what |
|---|---|---|
| T0 | `code/t0_counterexample.py` | the exact-rational refutation of the shrunk-cell step |
| T0b | `code/t0_backing.py` | the BACKING canary on all 16 usable (class, slot) pairs |
| T1 | `code/t1_y1117.py` | `k5_16_interior_Y1117`, all six usable slots, both pin regimes, all cell variants |
| T2 | `code/t2_sweep.py` | the population sweep (2 BelowNormal shards, resumable, wall-budgeted) |
| T4 | `code/t4_a141cells.py` | the targeted pass over A141's own 244 slot-lane kill cells |
| T6 | `code/t6_candidates.py` | deep covers on the screen-level NEW candidates and the canary cells |
| T3/T5 | `code/t3_fold.py`, `code/t5_manifest.py` | the tables, the overlap, the certificate manifest |
| check | `code/check152.py` | the independent checker for `polycore_slot_lane_shrunk_v1` |

Every cell is run in **the node's own pin regime** — A57 / A57box carry the G1 `δ = 10⁻²` slack
pin boxes, so their pin obstacles are the `K′` cores of the *m*-hulled slot boxes fattened by
`h = δ/√2 = 7.0711e-3`; A60's pins are exact, so nothing changes there — plus an
`exact cell / exact pins` baseline screen per cell, which is A141's own configuration and serves
as the control.

The cell variants per (node, slot) are the SHRUNK cell `C_h` (diagnostic only — the leaf built on
it is unsound, `notes/soundness.md` §3) and `C + t` for every admissible translate `t`
(`lane152.admissible_translates`, the corner points of `A` on the `{−h, 0, h}²` grid).  Number of
admissible translates per cell over the sweep: **1** on 593 cells, **2** on 3 610, **4** on 1 967.

Total ≈ **2.8 CPU-h** in ≤ 2 BelowNormal processes, `PYTHONDONTWRITEBYTECODE=1`, no LP, nothing
outside `attempts/A152-slot-lane-shrunk/**` written except the three named appends.

## 2. `k5_16_interior_Y1117` — the PI's example

The node is the right one: hypothesis box `x, y ∈ [2.357813, 2.49757]`, tilt `28.0725°–41.1121°`,
pins = corners4 + BL(0,1) at their `δ = 10⁻²` boxes (half-width 7.0711e-3), `τ = 5.000000` at
`budget = 5`, `dead: false` — alive, level 1, shard `k5_16_interior_G1`
(`results/t1_y1117.json`, `results/t1_y1117_all.json`).

**BR(0,1) is not singly met, and no variant makes it so.**  With 16 000 sampled poses `BR(0,1)`
yields ~390 free poses (free of every pin core AND of the hypothesis square's `K′`) and a realised
interior-disjoint pair with gap **0.24–0.33** — two full-width free squares, not one square and a
grazer.  The pair the coordinator sampled (`A` at depth 0.853 and `B` entering by 0.003, gap
0.024) exists, but it is nowhere near the binding witness: `B` pokes in at the cell's
`(u, v) = (1, 1)` corner in the corner frame, and the translate that sheds that strip still leaves
`lane_lb = 2`.

| slot | exact `C` | shrunk `C_h` | best admissible translate |
|---|---|---|---|
| BL(1,0) | LANE ≥ 2 (gap 0.067) | LANE ≥ 2 | LANE ≥ 2 (gap 0.105) |
| BR(0,1) | LANE ≥ 2 (gap 0.256) | LANE ≥ 2 | LANE ≥ 2 (gap 0.291) |
| BR(1,0) | LANE ≥ 2 (gap 0.768) | LANE ≥ 2 | LANE ≥ 2 (gap 0.810) |
| TR(0,1) | near-miss | near-miss | near-miss |
| TR(1,0) | near-miss | near-miss | near-miss |
| TL(1,0) | near-miss | UNDECIDED (`M = 1`, LANE not certified) | near-miss |

(slack-pin regime; the exact-pin regime gives the same picture.)

Two structural facts are visible in the run's own translate lists.  In the **exact**-pin regime
`Y1117`'s admissible set is `{(h,h), (0,h), (h,0), (0,0)}` — four points including A141's `t = 0`;
in the node's **real** slack regime it shrinks to `{(h,h), (0,h)}` (BR(0,1)) or `{(h,h), (h,0)}`
(the other five) — **`t = 0` is gone**, because a pin displaced by `+h` towards the slot overlaps
the exact cell.

## 3. The sweep

**Coverage.**  1 226 of the 1 713 alive records (**71.6 %**) and 6 170 of the 8 694 (node, slot)
cells (**71.0 %**) — 593 `k5_11`, 404 `k5_16`, 229 `trump5` records.  The record order is a
deterministic SHA-256 shuffle of `(src, shard, nid)`, so the covered part is a uniform sample
across all three classes and both campaigns, not a prefix of one shard.  The cover budget (2 × 1
200 s) was exhausted at ≈ record 225 of each shard; after that the screen alone runs, which still
detects every kill CANDIDATE (§3.3) — it just does not certify it.

### 3.1 Verdicts

| variant | LANE ≥ 2 | near-miss-or-worse | near-miss | undecided | screen-only | **KILL** |
|---|---|---|---|---|---|---|
| translated `C + t` (sound) | 9 750 | 2 891 | 96 | 109 | 2 590 | **245** |
| shrunk `C_h` (diagnostic) | 3 403 | 1 285 | 37 | 50 | 1 299 | **96** |

The 245 translated kills are **90 distinct (node, slot) cells on 90 distinct nodes** (one cell
each), every one of them `LANE_K′ = 0, M = 1` — the same and only form A141's 244 take.  Several
translates of the same cell can each certify the kill, which is why 245 > 90.

| by class / slot | count (cells) | by level | | by campaign | |
|---|---|---|---|---|---|
| k5_11 TR(0,0) | 52 | level 1 | 80 | A57 | 70 |
| k5_11 TL(1,0) | 34 | level 2 | 10 | A60 | 20 |
| k5_11 BR(0,1) | 32 | | | | |
| k5_16 BL(1,0) | 24 | | | | |
| k5_16 TL(1,0) | 24 | | | | |
| trump5 BR(0,1) | 52 | | | | |
| trump5 TL(0,0) | 27 | | | | |

(the left column counts certified (cell, translate) pairs; the 90 distinct cells are 46 `k5_11`,
24 `k5_16`, 20 `trump5`.)  Translates used: `(h,h)` 90, `(h,0)` 74, `(0,h)` 48, `(0,0)` 33 — the
last only at the two wall-backed slots `k5_11 TR(0,0)` and `trump5 TL(0,0)`, as `t0_backing.py`
predicts.

### 3.2 Overlap with A141 — ZERO new

**All 90 A152 kill cells are also A141 kill cells** (`overlap_with_a141`: `both = 90`,
`n_new_in_a152 = 0`).  Not one kill in the swept 71 % of the population is new.

### 3.3 The screen-level comparison (independent of the cover budget)

A cell is a *kill candidate* when the sampler realises no free pose meeting it and at most one
conditioned meeter (`lane_lb = 0, M_lb ≤ 1`); every certified kill is a candidate, so counting
candidates measures the refinement's reach even where the cover was not bought.

| | candidates |
|---|---|
| exact cell + exact pins (A141's configuration) | 428 |
| some admissible translate (the sound refinement) | 437 |
| the shrunk cell (the PI's proposal) | 444 |
| **translate but NOT baseline** (the refinement's only possible upside) | **36** |
| **baseline but NOT any translate** (what the refinement costs) | **27** |
| shrunk but not any translate | 36 |

T6 ran deep covers (sample 10 000, `max_open = 1 500`) on **27 of the 36** upside candidates
inside its wall: **0 translate KILLs and 0 shrunk KILLs** — every one lands on NEAR-MISS,
NEAR-MISS-OR-WORSE, UNDECIDED or LANE ≥ 2 (`results/t6_candidates.jsonl`).  The screen-level
upside does not convert.

### 3.4 What the refinement COSTS (T4)

A141's 244 kill cells, re-run in the node's real pin regime at an admissible translate (152 of
them inside the 700 s wall; `results/t4_a141cells.json`):

| | |
|---|---|
| A141 kill cells re-run | 152 |
| baseline control (exact cell + exact pins) reproduces `lane_lb = 0` | **152 / 152** |
| still KILL at some admissible translate | **143** |
| drop to NEAR-MISS | 8 |
| drop to UNDECIDED | 1 |

So **9 of 152 (5.9 %) of A141's kills do not survive** the honest slack-pin treatment — the pin
obstacle shrinks from the full unit square (or the near-degenerate `K′`) to half-side `½ − h`, and
the translate cannot make that back.  The refinement is **net negative**: zero gained, ~6 % lost.

## 4. The unsoundness, realised in the corpus

`notes/soundness.md` §3 refutes the shrunk-cell step abstractly (and
`results/t0_counterexample.json` machine-checks the four-grazer configuration in exact rationals).
The sweep exhibits the same failure on real nodes: **6 cells** where the leaf built on `C_h`
returns **KILL** while **no** admissible translate does better than NEAR-MISS —

| cell | slot | translate verdicts |
|---|---|---|
| `k5_11_interior_Y0030` | TL(1,0) | NEAR-MISS, NEAR-MISS |
| `k5_11_interior_Y0445` | BR(0,1) | NEAR-MISS, NEAR-MISS |
| `k5_16_interior_Y0157` | BL(1,0) | NEAR-MISS, NEAR-MISS |
| `k5_16_interior_Y0328` | TL(1,0) | NEAR-MISS, NEAR-MISS |
| `k5_16_interior_Y0428` | BL(1,0) | NEAR-MISS, NEAR-MISS |
| `k5_16_interior_Y0281_D07` | BL(1,0) | NEAR-MISS, NEAR-MISS |

On each of these the PI's rule would book a kill for which no admissible placement of the sixth
pin exists.  (T6 re-ran the canary list with a generous cover budget; it did not get past the
36 upside candidates inside its wall, so the six are recorded from the sweep's own covers, which
are sound in the direction that matters — a `KILL` verdict on `C_h` is a genuine
`LANE_K′(C_h) = 0, M(C_h) = 1`.)

## 5. Certificates

**90 `polycore_slot_lane_shrunk_v1` certificates** (`certs/slotshr_<shard>__<nid>__<slot>.json`),
all **PASS `code/check152.py`** (`results/check152.json`: checked 90, failed 0), which runs the
whole of A141's `check141.check_lane_cert` (complete-prefix-code cover, every leaf discharge
re-decided, the witness point exact via A132 `vertex_ok`, the M covers, `LANE + M ≤ 1`) and then
the four A152-specific clauses:

* **C7** `cell_rect` is the unit slot cell translated by the stored `t`, and `|t|_∞ ≤ h = δ/√2`;
* **C8** the translated cell is inside the container;
* **C9** the translated cell is interior-disjoint from every admissible position of every pin;
* **C10** the pin obstacle boxes are at least as wide as the node's pin slack, **and** the
  certificate declares itself `conditional` with a `prerequisite` field.  A certificate that
  claims an unconditional kill is REJECTED.

Sample line per kill, in the certificate: e.g. `k5_11_interior_Y1080_D00 TR(0,0)` —
80 000 poses drawn, 46 315 meeting the translated cell, **0 free**, all 46 315 met by the
conditioned square.  SHA-256 manifest: `results/cert_manifest.json`.

## 6. What A152 does NOT claim

* **No certificate here is a kill.**  Every one is conditional on the slack-form kill of its
  extension class, which does not exist (`notes/prereq.md`).
* The sweep covered 71 % of the population; the remaining 29 % is not evidence of anything, and
  the resume is one `python t2_sweep.py --shard k/2` away (the progress files carry the done set).
* Cells reading `lane_lb = 1, M_lb = 0` are recorded `SCREEN-ONLY`: a kill there would need a
  certified `LANE_K′ = 1` (every pair of open cover boxes always-overlapping) with `M = 0`, a form
  that has never fired in A118, A141 or A152.  Those covers were not bought.
* `LANE_K′` covers are capped at `max_depth = 30`, `max_open = 500` in the sweep (`1 500` in T6);
  a cover that does not close inside that is UNDECIDED, never a kill.
