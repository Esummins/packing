# The budget — the live estimate of remaining compute, and where it goes

**Rule.** This file is the one place the total lives. Every landed measurement that changes a number updates the row,
its provenance, and the date; nothing else in the repo quotes a total without pointing here. Lean replay is excluded
(the PI's convention). Machine: i7-12700K, 6 usable LP slots with BLAS pinned; "wall-days at 5" assumes five
workers.

Last updated: **2026-09-07 16:15**.

## A. The total

| layer | remaining | central | range | wall-days at 5 | provenance | levers not yet in the number |
|---|---|---|---|---|---|---|
| A57 window trees, k5_11 + k5_16 | ~1,400 open boxes across levels 1–4, tail measured to termination (level-4 descent 0 of 30) | **1,300 CPU-h** (≈ 54 CPU-days) | 1,150–1,700 | **11–13** — the night shift (A123 `ad55f884`) measured T5″ LIVE: it touches 6.4% of children as projected but fully empties only 1.0% (3/296) against the 3.7% the 10–11 figure assumed, so trimming buys LP tractability, not kills; the honest figure until A124's touched-vs-emptied control lands is the 13.3 of the tight core alone, less what the re-check removes | A123 `ad55f884` (live), A96 `761513f5` (tight core), `5fd0e287` (tail) | **the 900 s re-check: 11 of 23 previously-alive nodes certified dead in 7.3 CPU-h (48%), 360 queued — the best per-budget item on the board, running (A124)**; the local certificate as YES leaf (A120: 4 of 9 closed); the Y0381 hang |
| Window stragglers | **k5_13 only** (A61 running); every other k5/k6 class full-window — A114 closed k5_02, k5_03, k5_12 overnight with the original s0 certificates (12.5 CPU-h) | **≤ 3 CPU-h** | 0–5 | 0.03 | A114 `ee0c18d5`; scoreboard 51/52 | none needed |
| Protected tier, 15 classes excl. k0_00 | conditioning trees per exact stratum; trump5's residual tree | **3,800 CPU-h** | 2,900–6,300 | 32 | A100 `a100_projection.json` (2026-09-05) | tight core + trimming untested here (same box/pin geometry, expect a similar fraction); η-gating already in the number |
| k0_00 | the frame residue; tree at 9,300–21,700 CPU-h, or one theorem — **warm re-solves complete over every reachable open cell (A115 T4+T5+T6 `0d4c79fd`, 2026-09-07): 22 of the 216 level-1 root cells certified dead plus 13 level-2, 2 level-3 and 10 A85/A99 nodes for 29.8 CPU-h, removing 1,023–2,372 CPU-h (34–80× return); 14 of 14 of the PI's `i` readings certified; 71 stage-A kill candidates still lack the 900 s continuation (5 of the last 27 closed that way); 12 cells are converged-alive (τ = budget, minmass 1) and need the two-meeter cover or A128's coupled moves** | **theorem route: 0** / tree route **12,000 CPU-h** (13,500 less A115's midpoint) | 7,000–18,900 | 0 / 100 | A99 `99985b76`; A115 `0d4c79fd`; LOCK-FREE⁺ evidence A104 `af6456e1`; A113 `6409396b` | LOCK-FREE⁺(< 4); dual-guided re-branching on the slot the support keeps occupying (A113: the un-killable cells' supports are 2–6-slot partial skeletons of near-critical shadows; the cell's own box distance to the manifold predicts nothing, the support does); the k0 tree has zero logic kills today |
| **Total, theorem route** | | **≈ 5,100 CPU-h** | 4,100–8,000 | **≈ 42** | | |
| **Total, tree route** | | **≈ 18,500 CPU-h** | 12,000–29,000 | **≈ 155** | | |
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
   *A111 (`4c6ace6e`), A112 (`e6690215`):* the region tree kills 3 of 11 non-trivial stalled S02 regions at 27–54×
   less wall than the old tree on those boxes (two certificates per kill), ordering is a tie-break, the free kills
   are all Lemma TC, the k0 cells do not move (η = 0 exactly). As a scheduler option for stalled nodes with
   fall-through it is worth of order a wall-day on A57. A117 (`6f160858`) delivered both prerequisites — verify_param_v2
   with NO-families (Lean-proved exemption clause) and TC as a leaf (170/170 fires, 1.7M samples) — but v2 buys
   validity, not wall (10× the four fixed sides), and YES-side boxes are refused as parametric cores, so
   certificate-based region-tree kills remain s0-only for now.
   *A116 (`74a34f96`):* the local certificate around a minimum is dead at (0.2, 10°) for S02 and (0.1, 40°) for S07
   — the YES leaf of the region tree at 20× A111's radius, covering the supports of 95 of the 252 S02-explained
   alive nodes. A119 (`71d18eba`) made the five neighbourhoods exact (independent rational checker, 53k leaves) and
   Lean-backed (0 sorries, one axiom: interior SAT); blocking boxes do not widen them; three of A116's larger cells
   are alive, not open. A120 (`9fa13dfe`) deployed it: 4 of the first 9 in-N nodes closed outright (≈ 0.05
   wall-days), the rest limited by certifier rounds at a 0.3% margin, not by the mathematics; 26 nodes continue.
   *A118 (`405b6522`):* the lane-count leaf is a 0.37 s/cell emission-time pre-screen worth ~1.7% of LPs (0.05
   wall-days) — deploy at resume; the two-meeter cover does not terminate (2–500 CPU-h per node); the octagon pair
   test supersedes Lemma TC as the pair leaf.
   *A131 (`PENDING`) — the PIN-CLIP (T5‴), measured, not deployed:* shrink the centre box, not just
   the tilt bin. For each tilt sub-bin, discard every centre at which the conditioned square meets
   a pin core at EVERY tilt of the bin — the exact intersection over tilts of the forbidden
   octagons, in rational arithmetic with no epsilon (tilts as `t = tan(θ/2)` make cos/sin rational).
   Controls: 674/674 existing logic kills clip to EMPTY, 1,140,000 drawn → 897,320 tested → 0 hits,
   and the predicate matches a direct SAT grid on 40,000 random cases with 0 unsound / 0 missed.
   **It strictly dominates T5″** (all 159 of T5″'s empties, plus 21 more) and touches 2.7× as many
   boxes (455 vs 166). On the 1,744-box corpus: 10.3% clip to EMPTY, 26.1% are narrowed and
   survive, median 0.71 free levels among those narrowed; L4 85.7% emptied. **The decision-relevant
   slice is the 607 recorded-UNCLOSED nodes (414 ALIVE + 193 FAIL): 132 (21.8%) clip to EMPTY and
   292 more (48.1%) narrow** — 112 of the 132 need only the trim already deployed, and they are
   open only because T5′/T5″ are pre-filters on newly emitted children. That backlog sweep is pure
   geometry (minutes) against the 900 s re-check's 27 kills for 8.11 CPU-h, and the two sets
   overlap in one node. At emission the incremental value over deployed T5′+T5″ is small — 1.2% new
   outright kills plus ~2.6% of modelled level-promotion, ≈ 0.4 wall-days of the A57 row — so the
   ranking is: **run the retrospective sweep first (`attempts/A131-pin-clip/results/backlog131.jsonl`),
   deploy at emission second.** In vitro (10 nodes, 2.85 CPU-h, two-stage 240/900 s through
   recheck96's node path): **5 of 10 go from η ≈ 0 to η = −0.5 or −1.0 on the clipped box and 2 are
   certified dead through the frozen verifier** (`Y0036_D02` L2 PASS 11 s, `Y0186_D00_D00` L3 PASS
   219 s, both previously ALIVE); 3 more reach η ≤ −0.5 but the certificate has real holes →
   resolver. On the other 5 only the columns move (support 107→5, 1041→5), and which of the two
   happens is **not** predicted by how much is clipped. List, notes and the deployment shape:
   `attempts/A131-pin-clip/notes/{measurement.md, lp_effect.md, deploy.md}`, lemmas.md T5‴.
2. **The alive population.** Re-run unconverged alive nodes with a longer LP cap before splitting them (A109's 28/46);
   branch on the load path instead of the rattler (A112); both are about not paying eight children for a node that
   was never alive or whose slack sits in squares it does not condition on.
   *Row-dropping by the all-poses test (2026-09-06, A96 `d016209b`):* the closed-form tilt-coherence screen alone
   removes a median 44% of a node's warm rows (13k of 30k); the exact all-poses test removes more. It is the
   strongest LP lever measured, and it is not free: it widens the frozen verifier's admissibility clause from
   "disjoint from every core" to "disjoint from some pose of the box", i.e. a new frozen verifier version with a Lean
   theorem parallel to T5. **Measured (A96 `37eae961`, three arms at 900 s): dropping a median 53% of rows produced
   zero additional kills** (arm C 3 kills vs arm B 4, none new); it buys convergence (7/26 vs 4/30) on nodes that
   land knife-edge or alive anyway. A speedup with no kill yield does not justify a soundness-relevant verifier
   change: row-dropping is shelved, spec on file. The 900 s cap stands on its own (2/29 converged at 240 s vs 4/30
   and 7/26 at 900 s). *Caution banked with
   it:* trimmed-bin re-solves at the 240 s cap moved the LP without deciding it (29 solved, 2 converged, 19 on the
   knife edge) — no kill count from a re-solve counts before the 900 s re-check.
3. **Verification wall.** Atom-dependent verify caps (in), resolver over timeouts (in), σ ladder to level 2 (recorded,
   not deployed: −2 wall-days, needs a coverage reset), 4-D verify sharing across siblings (untested).
4. **The protected tier.** No lever of this week has been applied there; the same box/pin geometry suggests the same
   fractions, and trump5's alive nodes are the same S01/S07 families. Worth a pilot before the tier runs at all.
5. **k0_00.** Not a compute question: LOCK-FREE⁺(< 4) or the 15,000 CPU-h tree. Corner-crowd rows at the node
   level are out (A115: the room supports have single deep meeters, nothing for a crowd row to charge; Trump realises
   nine incidences against a budget of eight at depth 0). What the k0 room needs is the teleport hypothesis itself as
   a node cut, i.e. re-branching on the singly-met corner (A112's k0 face), not a weighted row.

6. **The net-orientation verifier is a cross-check, not a lever — REJECTED as a replay verifier and as a
   certificate simplifier (A129 `[pending]`, 2026-09-07).** Burns–Massaccesi (Aug 2026, blog not arXiv) turns out
   to certify with *the same object we do* — an atomic measure with total weight < n — and to differ only in the
   verifier: a finite net of orientations, an "almost-unit" test square, and an exact per-orientation translation
   sweep. A129 built it sharply (`σ(δ) = 1/(cos δ + sin δ)` exactly, adaptive net, and — the change without which
   it replays nothing — the exemption clause decided for the *unit* square over the whole net cell rather than the
   shrunk one) plus an independent `Fraction`-only checker that imports the frozen exemption predicates.
   **As a replay verifier for A57's PASS leaves: no.** On 60 stratified PASS leaves it reproduced 26 inside a
   120 s budget at a **median 15× the frozen verifier's wall** (10.8× on the totals); an exact second pass on 12
   of the 34 that ran out of budget resolved 96 of 96 sampled tilt positions at levels 5–12 and put their cost at a
   **median 26.7× (up to 234×)**. It cannot replace any of the ~850 s: it multiplies the 100 s exact-verify half by
   10–30. **The failure mode is not the reviewer's predicted margin — 0 of 60 leaves lost the shrink.** The shrink
   consumed at the level that works is 6e−5 to 5e−2 in side and every certificate absorbed it, because a leaf
   certificate is a *measure*: the shrink comes out of its mass slack, not its side slack. What kills it is
   architectural — the frozen 3-D `(t, c_x, c_y)` tree discharges a whole band of orientations against the six
   cores with one `t`-box, while the net re-resolves the same exempt boundary at every one of a median 185 net
   orientations. Optimising the predicate moves this by ~2×, not by 10×.
   **As a certificate simplifier: no.** There are no Farkas vectors and no separating-axis selections to be had —
   the certificate stays the same atoms and weights, and the net certificate merely adds a tilt tiling (1,950 exact
   rationals for 3.82) and a σ per cell. The Lean shape is *worse* than A119's `leaf_*` lemmas, not better: it
   replaces one 3-D `native_decide` by one per net cell.
   **As a cross-check: yes, and it earns that outright.** Both whole-problem certificates were run to completion and
   both PASS: `s(11) ≥ 3.82` at 1,950 net orientations (deepest level 14, shrink 3.81e−3, 3.96e10 arrangement cells)
   in **2,148 s** against the frozen verifier's **587 s** (3.66×), and `s(12) ≥ 3.90` at 987 orientations in
   **802 s** against **232 s** (3.45×). Unconditional measure certificates are exactly where the method is cheap —
   no exemptions, so no bisection at all (the mass is constant on an arrangement cell, so the correct bisection
   depth is 0). That is a genuinely structurally independent decision procedure for the two headline theorems, for
   36 and 13 single-core minutes, sharing no code, no data structure and no search order with A07/A08; a fully
   exact `netcheck` replay of the same two would cost 19 h and 9.5 h (16 cells of each were run: both CHECKED).
   Take it for W7 and for the paper's "two verifiers" paragraph; do not schedule it against the A57 row.
   *Files:* `attempts/A129-net-verifier/{code,notes,results}`, notes `method.md` (Lemmas N1–N4) and `benchmark.md`.

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

**Measured cost profile along the side (A114 L7, 224 verifier runs):** seconds per 10⁻³ of side from the bottom of
the window to the slab ending at s0 — k6_07 53 → 91, k6_27 20 → 1,589, k5_02 89 → 502, k5_03 412 → 1,064, k5_12
129 → 4,181. The bulk trend is mild (+38% to +59% across the window); the blow-up is confined to the last 10⁻⁴ to
5·10⁻⁴ below s0, where w_min shrinks (k5_12: 1.7M boxes for a 5·10⁻⁴ slab at 3.8405 vs 12.7M at 3.877) and d_pose
climbs. That is the S02 shadow in the arithmetic, and it says the per-slab re-solve I proposed is unnecessary: the s0
certificate closes every class, including the top slabs, once the slab width is set by the law (every earlier bulk
FAIL was a slab over its width_max, k5_02's by 4×, never node hardness). Measured width_max: k6_27 0.014, k6_07
0.012, k5_02 0.0018, k5_03 0.0018 → 0.0010 at the top, k5_12 0.0010 → 0.0005 at the top.

**Near a solution the law stops being linear.** w_min and d_pose are set by the certificate's slack, and a class whose
boundary carries a shadow at side s* has slack ≈ (s* − s) at side s: k5_02's s0 certificate has margin 0.0006 and
k5_03's fails on bulk slabs near s0 while both pass cheaply at the bottom of the window — and both are classes the k7
pinwheel (s* = s0 + 0.0097, A107's S02 list) sits on. So the cost per unit of side is flat far below the shadow and
rises steeply as s approaches s* − (s* − s0), diverging only if a class contains an actual minimum (Trump's classes,
which is what the basin/tube machinery is for). Consequence for sweeps: anchor a fresh certificate at the top of each
slab (its slack is then s* − s_top, not s* − s0) rather than reusing the s0 certificate across the band.

What is *not* the cost driver: certificate-margin stragglers (hours each), exact endpoint certificates (seconds), the
Lean replay (excluded).
