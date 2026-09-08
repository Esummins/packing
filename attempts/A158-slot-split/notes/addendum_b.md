# A158b — the YES child as an LP node, and the mutual clip (coordinator's two corrections)

## 1. The YES child IS an LP node — and it lands exactly back on the knife edge

`SomeIn S` is an ordinary case-LP hypothesis, so the YES child is the node

    pins + H + the SLOT BOX S ,     budget = 11 - #cores = 4      (level-1 trump5 / k5, 5 pins)

`yeslp158.py`: A135 `ExactHyp(..., scope="exall")` on all 7 boxes, warm-started from the node's own
atoms and rows, frozen-verifier-compatible (`S` is an ordinary second core in the schema). Two LP
sub-cases per cell, one per tilt piece of `S`.

**Extra soundness gate.** A135's `ExactHyp` only checks `cores[:len(boxes)-1]` pairwise disjoint;
with `S` appended that leaves `K(S)` unchecked, and if `K(S)` met `K(H)` the two hypotheses could be
witnessed by the SAME square and the budget would be 5, not 4. `cores_pairwise_disjoint` is re-run
over **all 7** cores and a failure aborts. Min gap measured: 0.0000 (A60, exact pins — the pin cores
touch at `a = 1/2`, as they do in every A60 node) and 0.0141 (A57, `delta = 10^-2` slack pins).

**Result — 12 of 12 sub-cases, all converged: `tau = 4.000000 = budget`, `eta = 0`.**

| cell | `tau0` | YES budget | `tau` piece 0 | `tau` piece 1 |
|---|---|---|---|---|
| `c0_Y0076 TL(0,0)` | 5.000000 | 4 | 4.000000 | 4.000000 |
| `c0_Y0787 BR(0,1)` | 5.000000 | 4 | 4.000000 | 4.000000 |
| `c0_Y0959 TR(0,1)` | 5.000000 | 4 | 4.000000 | 4.000000 |
| `k5_11_interior_Y0130 TR(0,0)` | 5.500000 | 4 | 4.000000 | 4.000000 |
| `k5_11_interior_Y0147 TR(0,0)` | 5.000000 | 4 | 4.000000 | 4.000000 |
| `k5_11_interior_Y1110 TR(0,0)` | 5.000000 | 4 | 4.000000 | 4.000000 |

**This is the general obstruction, stated exactly.** Adding the slot square to the hypothesis
removes **exactly one** unit of dual packing *and* **exactly one** unit of budget, so the child lands
back at `tau = budget`. That is the same 1 the NO child removes from `tau` alone (`c0_Y0076`:
`5 -> 4` against budget 5). The dual weight in `S` is exactly 1 on **730 of the 1,238** selected
records, so on that whole sub-population the split is **structurally neutral**: whichever side you
take, the node returns to the knife edge. Nothing about compute changes that.

## 2. The mutual clip (A131 pin-clip with each box's own core in the pin's role)

`clip158.py`. `pinclip.Oct` needs an AXIS-ALIGNED core, and A132's `K'` is not axis-aligned, so the
core handed to A131 is the largest axis-aligned square inscribed in `K'(B)` about `B`'s midpoint
(strictly smaller than `K'(B)` ⇒ the clip removes LESS than the truth: sound, and A131's certified
machinery is imported unchanged). Measured at `S(0.10, 10°)`:

| cell | kept `H` (nsub 1 / 4) | kept `S` (nsub 1 / 4) | `K'(H)` before → after | `K'(S)` before → after |
|---|---|---|---|---|
| `c0_Y0076` | 0.8865 / 0.6209 | 1.0000 / 0.527–0.540 | 0.602072 → 0.618361 (×1.027) | 0.736355 → 0.736355 |
| `c0_Y0787` | **0.5003** / 0.4714 | 1.0000 / 0.690–0.700 | 0.590298 → **0.664416** (×1.126) | 0.646355 → 0.646355 |
| `c0_Y0959` | 0.9580 / 0.9526 | 0.7439 / 0.265 (2 empty bins) | 0.681579 → 0.686626 | 0.646355 → 0.666843 |
| `Y0130` | 1.0000 | 1.0000 | unchanged | unchanged |
| `Y0147` | 0.6273 / 0.4601 | 0.7265 / 0.249 (2 empty bins) | 0.681579 → 0.726393 (×1.066) | 0.732041 → 0.757183 |
| `Y1110` | 1.0000 | 1.0000 | unchanged | unchanged |

The PI's prediction is confirmed on the *clip*: `H`'s box loses up to **half** its area
(`c0_Y0787`), and `K'(H)` grows by up to 12.6 %; at `nsub = 4` two cells lose whole tilt sub-bins.

## 3. The lane test on the clipped cores — and where it stops

**The clamp is what mattered, not the clip.** The LP framing puts `S` in the world frame clamped to
`[1/2, s0-1/2]`, which for a corner slot halves the centre box (`c0_Y0076`: `0.2 × 0.2 → 0.1 × 0.1`)
and so makes `K'(S)` far fatter (0.566 → 0.736). With that `K'(S)`:

| cell | piece 0 `lane_lb / M_lb` | piece 1 `lane_lb / M_lb` | certified |
|---|---|---|---|
| `c0_Y0076` | **0 / 0** | 0 / **1** | LANE ≤ 1 at (22, 8k) → (24, 30k) → (26, 60k); open set **GROWS** 159 → 270 → 646 |
| `c0_Y0787` | 1 / 0 (clearance 4.37e-2) | 1 / 0 | refuted |
| `c0_Y0959` | 1 / 0 (clearance 1.23e-1) | 1 / 0 | refuted |
| `Y0130` | 1 / 1 | 1 / 1 | refuted |
| `Y0147` | 1 / 1 | 1 / 1 | refuted |
| **`Y1110`** | **0 / 0** | **0 / 0** | **`LANE_K'(C \| S, H_clipped) = 0` CERTIFIED, both pieces: 36 and 35 leaves, 0 open, 36 s and 37 s** |

So on `k5_11_interior_Y1110 TR(0,0)` the hard half of the conditional leaf **closes** — the first
time an empty conditional lane cover has been obtained. The kill then needs
`M(C | S, H_clipped) = 0`, and that is where it stops:

* the sampled screen finds **no** admissible pose of the clipped `H` box that meets `int C` and
  clears every other core (100,000 draws) — so `M = 0` is *believed*;
* `cond_can_meet`'s cover makes **zero** progress: `(max_depth 40, max_open 5,000)` → **0
  discharged leaves**, 5,001 open, 21.8 s; `(42, 40,000)` → **0** discharged, 40,001 open, 183.8 s.
  The reason is structural: `H_clipped` sits at frame `[1.374, 1.519]²` with `hmax ≈ 0.686`, so
  `box_misses_cell` needs `x0 ≥ 1 + hmax = 1.686` and can **never** fire, the container prune never
  fires on an interior box, and the shared-point discharge is not finding points — the DFS drives
  depth-first into one corner and fills the open budget without discharging anything. A third rung
  was stopped at 674 s rather than bought: a cover discharging 0 leaves does not close by scaling.

`c0_Y0076`'s YES child fails on the other half: its lane open set grows with depth (159 → 646),
and piece 1 has `M_lb = 1` outright, so **no amount of depth closes it**.

## 4. Net

* **`c0_Y0076` is NOT dead by the split, on either route** — YES-by-LP `tau = 4 = budget` on both
  pieces; YES-by-lane blocked (growing open set; `M_lb = 1` on piece 1). Its NO child stands
  certified (frozen `verify_case` PASS), so the closure record has one child certified and one alive;
  no `A136 closures` record is written, because there is no closure.
* The one cell whose YES child is one certified cover away is `k5_11_interior_Y1110 TR(0,0)` —
  and its NO child is alive (`tau = 5`), so even a closed `M` cover there gives YES-only, not a node
  kill.
* **Verdict on running the split over the 1,238-record population: no.** The YES-child LP costs
  4–80 s per sub-case, always returns `tau = budget`, and the reason is the exact-1 accounting of
  §1; the geometric route needs an `M` cover whose prune set is empty by construction on
  interior-`H` cells.
