# The budget — the live estimate of remaining compute, and where it goes

**Rule.** This file is the one place the total lives. Every landed measurement that changes a number updates the row,
its provenance, and the date; nothing else in the repo quotes a total without pointing here. Lean replay is excluded
(the PI's convention). Machine: i7-12700K, 6 usable LP slots with BLAS pinned; "wall-days at 5" assumes five
workers.

Last updated: **2026-09-06 21:30**.

## A. The total

| layer | remaining | central | range | wall-days at 5 | provenance | levers not yet in the number |
|---|---|---|---|---|---|---|
| A57 window trees, k5_11 + k5_16 | ~1,400 open boxes across levels 1–4, tail measured to termination (level-4 descent 0 of 30) | **1,250 CPU-h** (≈ 52 CPU-days) | 1,150–1,600 | **10–11** (13.3 without trimming; 19.6 without the tight core; 27 at the 95% tail bound) | A96 `e68d8dbc` (trimming projection), `5fd0e287` (tail), `761513f5` (tight core) | LP-time re-check of unconverged "alive" nodes (28/46 were not alive); load-path branching (A111/A112); trimmed-bin LP strength (A96 re-solves running) |
| Window stragglers | k5_02, k5_03 (partial), k5_12, k5_13 (running); **k6 and up all full-window** | **15 CPU-h** | 8–25 | 0.15 | A114 `9ef80bfa` (k6_07, k6_23, k6_27 closed for 3 CPU-h; slab cost 340 s per 10⁻³ of side for k5_03), A61 pass 5 | slab sweeps running (cap 15 CPU-h) |
| Protected tier, 15 classes excl. k0_00 | conditioning trees per exact stratum; trump5's residual tree | **3,800 CPU-h** | 2,900–6,300 | 32 | A100 `a100_projection.json` (2026-09-05) | tight core + trimming untested here (same box/pin geometry, expect a similar fraction); η-gating already in the number |
| k0_00 | the frame residue; tree at 9,300–21,700 CPU-h, or one theorem | **theorem route: 0** / tree route **15,000 CPU-h** | 9,300–21,700 | 0 / 125 | A99 `99985b76`; LOCK-FREE⁺ evidence A104 `af6456e1`; A113 `6409396b` | LOCK-FREE⁺(< 4); dual-guided re-branching on the slot the support keeps occupying (A113: the un-killable cells' supports are 2–6-slot partial skeletons of near-critical shadows; the cell's own box distance to the manifold predicts nothing, the support does); the k0 tree has zero logic kills today |
| **Total, theorem route** | | **≈ 5,100 CPU-h** | 4,100–8,000 | **≈ 42** | | |
| **Total, tree route** | | **≈ 20,000 CPU-h** | 13,000–30,000 | **≈ 170** | | |
| PI target | | 400 CPU-h | | 3 | | |

The gap to the target is the protected tier and, on the tree route, k0_00. A57 is now under 1/3 of the theorem-route
total; the levers of this week (tight core −32%, trimming −20%) applied to the protected tier's trees would move that
row by a comparable fraction, but that is a projection, not a measurement.

## B. Where a tree's time goes — the anatomy of a node (A57, measured)

| outcome of a node | share of nodes (level 1 → 4) | what runs | cost per node |
|---|---|---|---|
| KILL-BY-LOGIC (box vs pin cores; now T5′ tight core, T5″ trimming) | 29% → 60% (rises with depth: smaller boxes clash with pins) | geometry only | **~0 s** |
| PASS (LP dead, certificate verified) | 45% → 20% | LP 240–400 s + exact verify 100 s at s0 + 4-D window verify 545 s at level 2 | **~800–900 s** |
| FAIL (LP dead, certificate has holes) → resolver | 7–10% | LP + verify + resolver 3–11 s (or ε_geo retries, up to minutes) | ~900 s |
| ALIVE-at-LP (τ = budget, η = 0) → split into 8 children | 19% → 10% | LP 240–300 s, no certificate, then 8 children | **300 s + 8 × (the row above)** |
| timeouts (verify cap; atom-heavy children) | ~5% | wasted verify wall, then resolver | up to the cap (1,500 s) |

Two readings of that table. **Roughly half of a non-logic node's wall is verification, not LP** (100 s exact at s0
plus 545 s over the window at level 2, against 240 s of LP); the parametric route already cut this from four fixed
sides to one 4-D run, and the resolver turns completed FAILs into kills in seconds, so timeouts are the waste to
watch. **The expensive object is the ALIVE node**, because it pays an LP and then buys eight more nodes; the alive
population is the S01/S02 families of `residue_ledger.md`, and A109 found 28 of 46 sampled "alive" nodes were
merely unconverged at the LP time cap.

## C. What the compute is being spent on, by structure (the families of `residue_ledger.md`)

| structure | share of alive nodes | why the LP cannot kill it | kills that work | kills that do not |
|---|---|---|---|---|
| S01 "room at side 4": a slot left empty or singly met | ~45% | the LP does not know the teleport lemma; crowd rows re-price rather than forbid (A109) | splitting until the box clashes with a pin (logic) | crowd rows at licensed depth (0 of 18) |
| S02 the k7 pinwheel (= Trump's load path in k5_11's skeleton) | ~25%, and 10 of 19 level-3, 4 of 9 level-4 | 0.0097 of slack invisible to cores at a ≤ 0.48; the tree conditions on the rattler's pocket, not the load path | trimming (12 of 14 level-4 boxes), tight core; load-path branching (A111 measuring) | basin balls (no open box contains the shadow), grain flood (circular) |
| S03–S06, S08–S53 | ~20% | as S01 by type | splitting | |
| fractional supports | ~25% (mostly level 1) | genuinely undecided | splitting | nothing structural known |
| near-flush / η = 0 pin-contact stratum (cert_failures E) | the FAIL population | certificates refuse at η = 0 exactly | resolver, ε_geo retries | SNAP leaf (0 flips) |

## D. Where to look for improvements, ranked by CPU-h at stake

1. **Geometric kills that skip both LP and verification.** Every node killed by logic saves ~850 s. The two in hand
   (tight core, trimming) took A57 from 19.6 to 10–11 wall-days. The next candidates, in order of likely yield:
   pair kills once a node carries two boxes (core–core overlap; Lemma TC between bins — free after re-conditioning);
   box–pin octagon tests at emission (already what trimming does); box-vs-forced-neighbour kills, which need a
   second conditioned square and are the reason A112 (load-path branching) exists.
   *A111 (`4c6ace6e`):* load-path branching ≈ +1 wall-day (35 kills projected, n = 3 certified); the free pair kill
   between a node's bin and a load-path box fires on 43–76% of S02 nodes by level; the chain kill only at level-4
   widths. A112 is measuring the region tree with three orderings.
2. **The alive population.** Re-run unconverged alive nodes with a longer LP cap before splitting them (A109's 28/46);
   branch on the load path instead of the rattler (A112); both are about not paying eight children for a node that
   was never alive or whose slack sits in squares it does not condition on.
   *Row-dropping by the all-poses test (2026-09-06, A96 `d016209b`):* the closed-form tilt-coherence screen alone
   removes a median 44% of a node's warm rows (13k of 30k); the exact all-poses test removes more. It is the
   strongest LP lever measured, and it is not free: it widens the frozen verifier's admissibility clause from
   "disjoint from every core" to "disjoint from some pose of the box", i.e. a new frozen verifier version with a Lean
   theorem parallel to T5. Kill yield at 900 s being measured; spec for the clause requested. *Caution banked with
   it:* trimmed-bin re-solves at the 240 s cap moved the LP without deciding it (29 solved, 2 converged, 19 on the
   knife edge) — no kill count from a re-solve counts before the 900 s re-check.
3. **Verification wall.** Atom-dependent verify caps (in), resolver over timeouts (in), σ ladder to level 2 (recorded,
   not deployed: −2 wall-days, needs a coverage reset), 4-D verify sharing across siblings (untested).
4. **The protected tier.** No lever of this week has been applied there; the same box/pin geometry suggests the same
   fractions, and trump5's alive nodes are the same S01/S07 families. Worth a pilot before the tier runs at all.
5. **k0_00.** Not a compute question: LOCK-FREE⁺(< 4) or the 15,000 CPU-h tree.

## E. The slab-width law (window certificates; A114's k6_07 log, 2026-09-06)

The 4-D verifier bisects tilt, position and side to a cap of 48 levels per path. Two constants belong to the
certificate and the class, not to the slab: the leaf s-cell width it needs, w_min (k6_07: 2.3·10⁻⁵, set by the
certificate's slack against the dilation sensitivity), and the pose depth it needs, d_pose (k6_07: ≈ 39). **A slab
passes iff log₂(width / w_min) + d_pose ≤ 48.** k6_07: passing 0.0029 slabs reached s-depth 7 and max depth 46 at
167–215 s each (rising gently toward s0 with the admissible area); the 0.0235 halves reached s-depth 10, hit the cap
with 8 undecided boxes and 0 holes, and cost 1,500 s each for nothing. Predictor: one narrow probe slab gives w_min
= width / 2^(max s-depth) and d_pose = max depth − max s-depth; width_max = w_min · 2^(48 − d_pose) (k6_07: 0.012, five
pieces would have done). Once slabs fit, total cost is ≈ linear in band width (k6_27 11 s, k6_07 65 s, k5_03 340 s
per 10⁻³ of side); over-splitting costs percent, under-splitting costs a failed slab.

**Near a solution the law stops being linear.** w_min and d_pose are set by the certificate's slack, and a class whose
boundary carries a shadow at side s* has slack ≈ (s* − s) at side s: k5_02's s0 certificate has margin 0.0006 and
k5_03's fails on bulk slabs near s0 while both pass cheaply at the bottom of the window — and both are classes the k7
pinwheel (s* = s0 + 0.0097, A107's S02 list) sits on. So the cost per unit of side is flat far below the shadow and
rises steeply as s approaches s* − (s* − s0), diverging only if a class contains an actual minimum (Trump's classes,
which is what the basin/tube machinery is for). Consequence for sweeps: anchor a fresh certificate at the top of each
slab (its slack is then s* − s_top, not s* − s0) rather than reusing the s0 certificate across the band.

What is *not* the cost driver: certificate-margin stragglers (hours each), exact endpoint certificates (seconds), the
Lean replay (excluded).
