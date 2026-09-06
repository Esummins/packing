# A106 — the shadows in A57's alive nodes (read-only measurement, 2026-09-06)

Everything here is measured on **A106's own snapshot** of A57/A96 state
(`results/snapshot/`, sha256 manifest in `results/snapshot/MANIFEST.sha256.json`, taken
2026-09-06). No file under `attempts/A57-shadow-trees/`, `attempts/A96-a57-parametric/` or
`lean/` was written, and no A57/A96 process was started, stopped or re-niced. One BLAS-pinned
Python process at a time.

## 0. Conventions

* **s0** = 969271/250000 = 3.877084 (the G1 grid side A57 certifies at); **ŝ** = 3.877083590
  (Trump's optimum).
* **Level**: level 1 = `<cls>_interior_Y####` (children of the class root), level 2 =
  `..._Y####_D##`, level 3 = `..._D##_D##`, level 4 = `..._D##_D##_D##`. `deepen.py` bisects a
  node's box once in each of x, y and t, so a level has 8 children and each coordinate halves.
* **Open** = the last record for the id is neither `PASS` nor `KILL-BY-LOGIC` — i.e. `ALIVE-at-LP`
  (τ ≥ budget) or a certification `FAIL`. Both are still the tree's obligation; A57's own
  `board.py` counts them together as `open`.
* **Box**: A57's node hypothesis is 5 class pins + one *pose box* B = [x0,x1]×[y0,y1]×[θ0,θ1]
  asserting "some square has (centre, tilt) in B". The other five squares are unconstrained.
  Major diameter in pose space = max(Δx, Δy, Δθ in radians); Euclidean diameter =
  √(Δx² + Δy² + Δθ²).
* **The pins are not points.** The live A57 emission uses δ = 1e-2 *slack cores*: each pin box is
  the slot ± 0.01/√2 = ±0.0070710678 per axis at θ = 0 exactly (visible in every node json's
  `hyp.boxes[0..4]`). A106's minimiser therefore lets the five pinned squares slide inside those
  boxes; that is the hypothesis A57's certificates actually have to exclude, and it is materially
  weaker than exact slots (see §2).

## 1. T1 — the boxes (`results/t1_boxes.json`, `results/t1_levels.json`)

145 open nodes at levels 2–4: **k5_11** 122 (L2) + 10 (L3) + 4 (L4), **k5_16** 9 (L2).
Every one of them has its LP json (copied into `results/nodes/`).

| class | level | children | open | killed | med d_max (all) | med d_max (open) | max d_max (open) | med d_euc (open) | med Δx | med Δθ° | med a | med η (open) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| k5_11 | 1 | 720 | 158 | 562 | 0.169804 | 0.169804 | 0.169804 | — | 0.139757 | 9.7290 | 0.3566 | −0.0000 |
| k5_11 | 2 | 492 | 122 | 370 | 0.094952 | 0.099914 | 0.124355 | 0.144101 | 0.069878 | 5.4403 | 0.4242 | −0.0000 |
| k5_11 | 3 | 42 | 10 | 32 | 0.034939 | 0.034939 | 0.037664 | 0.059576 | 0.034939 | 1.9070 | 0.4607 | −0.0270 |
| k5_11 | 4 | 19 | 4 | 15 | 0.017470 | 0.017470 | 0.017470 | 0.029788 | 0.017470 | 0.9535 | 0.4800 | −0.9000 |
| k5_16 | 1 | 824 | 213 | 611 | 0.189903 | 0.189903 | 0.189903 | — | 0.139757 | 10.8807 | 0.3566 | 0.0000 |
| k5_16 | 2 | 51 | 9 | 42 | 0.069878 | 0.069878 | 0.069879 | 0.119153 | 0.069878 | 3.8141 | 0.4249 | −0.3333 |

**Shrink factor per level (median d_max over all children):** k5_11 L1→L2 1.79×, L2→L3 2.72×,
L3→L4 2.00×; k5_16 L1→L2 2.72×. The factor is 2 in each coordinate; it reads as 1.8–2.7 in
d_max only because which coordinate is the maximum changes with depth — the tilt width dominates
at levels 1–2 (Δθ = 5.4°–10.9° ⇒ 0.095–0.190 rad) and the centre width from level 3 down.

**Side window.** Every node in the table is a G1 node, certified/attempted at the *fixed* side
s0 = 969271/250000. A96's parametric pass re-emits the same certificates over the whole window
[191/50, s0]; where a node appears in `param96*.jsonl` its verdict and covered sub-window are
carried in `t1_boxes.json` (`side_window`, `param_verdict`, `param_coverage`).

**τ and η are integral, not converging.** Every open node sits at τ = budget exactly
(η = τ − budget within 2e-11 of 0); every killed node sits a whole unit or more below
(τ = 4.000000, η = −1.000000, or 4.2/4.33/4.5). The LP verdict flips; it does not drift. So no
"η → 0" extrapolation of the closing depth is available — the descent is a per-level *event
rate*, which is what A96 measured (11.3% at level 2, 9.5% at level 3, clustered).

## 2. T2 — the shadows

Engine: `code/shadow11.py` — A04 `pack11.py`'s geometry and penalty→SLSQP pipeline, reduced to
the class variety by a constant 34×n map (pins ride their slot lines c(s) = α + βs, β ∈ {0,1},
with the δ-slack offsets as variables scaled to [−1,1]; without that scaling the |u| ≤ 7e-3 block
against s ≈ 4 stalls the continuation and every landing is infeasible by exactly the pin
half-width — an hour lost to it). Validation: seeded from a perturbed Trump packing under
trump5's own pins it returns ŝ = 3.8770835866 (3.4e-9 from the true ŝ) in 1.7 s and the exact
interval endpoint certificate passes at ε = 1e-8.

### 2.1 The class shadow spectrum (`results/t2a_census.json`)

Multistart (Trump transports ×6, node-LP fractional packings, uniform random, basin hops) plus
one seed from the PI's k7 pinwheel (`docs/residue_map/pinwheel_k7_result.json`, read-only).
93 feasible landings; grouped by s*:

| s* | slack over s0 | k5_11 poses | k5_16 poses | exact endpoint |
|---|---|---|---|---|
| **3.886746** | **+0.009662** | 10 | 8 | ε = 1e-8 / 1e-7 |
| 3.902674 | +0.025590 | 2 | 2 | ε = 1e-9 |
| 3.911481 | +0.034397 | 1 | — | |
| 3.912232 | +0.035148 | 1 | 1 | |
| 3.914214 | +0.037130 | 1 | 1 | |
| 3.924003 | +0.046919 | 5 | 6 | |
| 3.942809 | +0.065725 | 1 | 1 | |
| 4.000000 | +0.122916 | 22 | 24 | |

The floor **s\* = 3.886746** is the PI's k7 pinwheel shadow (4 free squares at 48.435°, seven
squares on slots) — both classes' pin sets are subsets of its seven fixed squares, so it is a
configuration of each, and A106's independent minimiser reproduces it to 7 digits (3.886746029)
from the pi_k7 seed and to the same value from Trump transports and random starts. The whole
spectrum agrees with the PI's own 301-start k7 list. Several *pose*-distinct landings share one
s*: with δ-slack pins the minimum is attained on a manifold (pins slide inside their cores
without moving s), so a shadow is a value of s*, not a point.

### 2.2 Per open node (`results/t2_shadows.jsonl`, 145 nodes, 4 seeds each)

For each node the conditioned square is held in B by bounds and the side is minimised over
everything else; then B is released and the landing is followed to its free local minimum.

| | k5_11 L2 | k5_11 L3 | k5_11 L4 | k5_16 L2 | total |
|---|---|---|---|---|---|
| **EMPTY by box-vs-pin** | 51 | 6 | 4 | 3 | **64** |
| landed (box minimum found) | 53 | 3 | 0 | 6 | 62 |
| no feasible landing (clash ∈ [−0.93, −5e-4]) | 18 | 1 | 0 | 0 | 19 |

* **64 of the 145 open nodes are EMPTY on geometry alone** (22 of the 59 `ALIVE-at-LP`, 42 of
  the 86 cert-`FAIL`): no pose in B can be separated from one of the five pins, for any pin
  position in its δ-core, at any side. Clash depth median 0.0145, max 0.0506; 61 of the 64 have
  clash > 1e-3 (robust), 3 are within grid noise and would need an exact check. The clashing pin
  is #3 = (3/2, 1/2) 27×, #1 = (1/2, 3/2) 23×, #2 and #4 7× each, never the corner pin #0.
  A57's `pinguard` misses these because it tests the rational *inscribed cores*
  (a = 0.36–0.48) rather than the true unit squares.
* **Zero of the 62 landed nodes contains a shadow.** `free_in_box = 0` and `interior = 0` for
  every one: the box-constrained minimum always sits on the box boundary, and when B is released
  the configuration flows *out* of B to a class shadow (18 → 3.886746, 13 → 3.902674, 8 →
  3.925149, 7 → 3.912232, 7 → 4.0, …). Median ∞-gap from the box to the nearest square of the
  released shadow: **0.3166** — an order of magnitude larger than any box.
* **The alive boxes are not near-feasible.** The best side attainable with a square in an alive
  box: min +0.012987, q1 +0.0443, median **+0.0612**, q3 +0.1054, max +0.656 over s0 — i.e.
  1.3×–68× the shadow's own slack of 0.0097. (These are local minima, so upper bounds on the box
  minimum; the direction of the bound is the one that matters here.)
* One free-release landing came back below s0 (3.851577) and is flagged `free_feasible = False`
  — an infeasible penalty artefact, not a packing; it is excluded.

## 3. T3 — the switch (`results/t3_switch.json`)

**Basin radius.** Around a strict local minimum of side s*, A36's Taylor chain on the weighted
row sum W gives side ≥ s* − H̄x² on the box of radius x, so the ball where the side provably
stays above s0 has r_basin = √(slack/H̄). With A36/A70/A79's certified H̄ = 7.9079
(`docs/proofs/contraction_tube.md` §1.5):

| shadow | slack | r_basin (H̄ = 7.9079) | band H̄ ∈ [4, 16] |
|---|---|---|---|
| 3.886746 | 0.009662 | **0.034955** | 0.02457 – 0.04915 |
| 3.902674 | 0.025590 | 0.056887 | 0.03999 – 0.07998 |
| 3.912232 | 0.035148 | 0.066666 | 0.04687 – 0.09374 |

**Box radius vs basin radius** (half of the median major diameter):

| | half d_max | ÷ r_basin(3.886746) |
|---|---|---|
| k5_11 L1 | 0.084902 | 2.43 |
| k5_11 L2 | 0.047476 | 1.36 |
| k5_11 L3 | 0.017470 | 0.50 |
| k5_11 L4 | 0.008735 | 0.25 |
| k5_16 L1 | 0.094952 | 2.72 |
| k5_16 L2 | 0.034939 | 1.00 |

So *on size alone* the live boxes are at basin scale from level 2–3 down: one further bisection
takes a level-2 box inside r_basin, and level-3/4 boxes are already 2–4× inside it. **But size is
not the binding constraint**, because no live box is anywhere near a shadow (median gap 0.3166,
≈ 9 r_basin) and the boxes are further from feasibility than the shadows are. A ball around a
shadow would cover configurations no live box contains.

**The switch is therefore not available and not needed for these two classes.** The mechanism the
brief posits — branch-and-bound closing in on a shadow, taking smaller and smaller bites — is not
what the data show: the alive boxes do not contain shadows, τ is integral (5.000000 alive vs
4.000000 killed, never drifting), and 44% of them contain no admissible placement at all.

