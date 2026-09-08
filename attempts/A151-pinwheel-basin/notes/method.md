# A151 — method: what was computed, from what, and what each number is NOT

Owner A151 (Opus engineer), 2026-09-08. READ-ONLY on every campaign and prior attempt; every file
written by this attempt is under `attempts/A151-pinwheel-basin/` except the two doc lines the brief
names.

## 1. The three lanes of "the night's kill records" are NOT one lane

A137's rows all carry `lane: "exact-core re-emission"`, including the rows that are the **first**
LP of a child emitted that night. The file a row sits in is what distinguishes them, and mixing
them inflates the S02 kill rate from 36.8 % to 43.6 %. `code/family_join.py` keeps three lanes:

| lane | what it is | source files | n |
|---|---|---|---|
| **L1** | exact-pin-core **RE-SOLVE** of the pre-existing ALIVE population (A135's named chore) | A137 `exact_reemit_w{0,1}.jsonl` (163) + A149 `exact_reemit_w{0..3}.jsonl` (59) | 222 |
| **L2** | **first** LP of a child emitted that night, already with exact cores | A137 `emit_lp_combined.jsonl` (142) + `emit_lp_k5_11_interior_G1_s0.jsonl` (47) | 189 |
| **L3** | geometric leaves at emission (T5′ at the exact pin core, T5‴ clip, T5⁗ polygon) | A137 `emit_geo_*.jsonl` (798 kills) against the screened set (kills ∪ `queue_bc.json` ∪ L2) | 2,940 |

L1's totals reproduce PAUSED.md v3 §C.1 (163 re-solved, 46 PASS) and L2+L3 reproduce §C.2
(3,034 screened → 798 dead by geometry, 189 solved with 149 PASS) up to the 94 level-4/deepen rows
that never entered a queue file (2,940 vs 3,034 screened).

## 2. The family join

Family = A107's shadow attribution (`shadow_nodes.json`) of the node itself, or of its nearest
ancestor the gallery classifies (`Y0217_D06` → `Y0217`; a trailing `a`/`b` variant falls back to
its base id). A node with no classified ancestor but present in `extract.json` is `fractional` when
its LP minimiser is non-integral and `unexplained-integral` otherwise. A node with **no** gallery
entry at any ancestor is `post-A107`: A107's gallery covers 1,566 of today's 3,160 corpus rows, so
every child emitted after it was built lands there. **`post-A107` is a provenance bucket, not a
geometric one** — no claim is made that those nodes are or are not pinwheels.

## 3. The alive population

`code/alive_s02.py` re-derives A57's open rows exactly as A137's `state137.py` does (verdict from
the `cert` prefix; ALIVE/FAIL = open; a node is dead if it or any `_Dnn` ancestor carries a
supersession row), and adds on top: A149's `superseded_by_exactcore_A149.jsonl`, A137's emission
geometry kills and A137's fresh-emission LP PASSes. **A120/A136's YES/NO closures are deliberately
NOT folded in** — A120's runner.md §2 says the YES kill is a prose+numeric certificate and is never
counted with the frozen-verifier kills — so 6 of A136's 15 CLOSED nodes still read ALIVE/FAIL here.
That is stated wherever the number is used.

## 4. The consumer test for an ASYMMETRIC N

`code/consumer151.py` is A116's `consumer116.inside` with the symmetric predicate
(`dmax ≤ r and tmax ≤ ρ`) replaced by per-coordinate box containment, over the same objects: the
node's A107 representative support canonicalised into the shadow frame by A107's `struct_op`, an
injection of the **tilted** load-path boxes `f1, f2, f3` into distinct support squares (A116's
convention — `BR(0,1)` is a slot square and is not matched). Control: on A116's symmetric
`(0.2, 10°)` it returns **72 of 184** k5_11-frame S02 nodes, identical to A116's own
`t3_consumer.json`.

## 5. The growth (T2)

`code/a151grow.py` imports A116's `a116lib` read-only and overrides each free body's six box
bounds. Knobs are `(square, axis)` with axis ∈ {x, y, θ} — twelve knobs — grown one at a time along
`x, y ∈ {0.25, 0.30, 0.40, 0.55}` and `θ ∈ {14°, 20°, 28°, 40°}` from the certified symmetric base
`(0.2, 10°)`. Growth order is A116's per-pair forced radii (`notes/stability_table.md`, S02
κ = 100): the square whose tightest pair is most stable first — `f2` (0.215), `BR(0,1)` (0.083),
`f1` (0.019), `f3` (0.019). Two processes, disjoint square sets (A: `f2`, `BR(0,1)`; B: `f1`, `f3`),
then a combined verification run, because widening two knobs at once is not implied by widening
each alone — **the combined run is the certificate, the per-knob runs are the search**.

A step is ACCEPTED only if the tree returns `dead` with `capped = False` **and** the sampling check
returns 0 hits. A step that returns `capped = True` is recorded as **CAPPED, not as a failure**:
it is a wall-clock limit (A116's own grid has the same rows at ρ ≥ 20°), and no geometric claim is
made from it. A step refused with LIVE-LOW witnesses is a genuine geometric limit and its first
valid witness — a real partial packing of L ∪ P at side ≤ s₀ — is drawn by `code/draw151.py`.

Base control (this attempt, `results/grow_smoke.jsonl`): the symmetric `(0.2, 10°)` N is DEAD with
32,570 leaves, certified minimum 3.8770840979, 1,000 samples → 0 hits, Trump outside, in 205 s with
phase 2 off. The leaf count matches A126's control for S02 exactly.
