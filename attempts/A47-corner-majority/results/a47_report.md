# A47 — corner primitives + majority composition: the THIN BRANCH of flush-mandatory
# is CLOSED COMPLETELY (theorem T1 + exact s* certificate); the non-thin packing-level
# composition DOES NOT FIRE (forced sum exactly 0) — mechanism named, route refined (I-L19)
(Fable lead + two Opus certification agents, 2026-08-29)

Constants: s0 = 969271/250000 = 3.877084, B0 = s0^2 - 11 = 4.031780343056, both exact.

## 1. Question and verdict

I-L18-expanded asked: (a) close the flush-free THIN branch via A46's designed rectangle
lemmas; (b) certify corner/wall-zone charge primitives at s0; (c) compose the PI's
majority route on the non-thin branch against B0.

**Verdict (four lines).**
1. **Leg (a) closes STRONGER than designed: the thin branch of flush-mandatory is a
   finished THEOREM over the whole window.** Theorem T1 (span quantization): a
   flush-free thin chain has wall-to-wall span EXACTLY o*sqrt2 + r (o >= 2 diamonds,
   r >= 0 uprights); the only such value in [3.82, s0] is s* = 2 sqrt2 + 1 = 3.8284271,
   and the s*-exception structure [45,0,45] is killed by an exact certificate (50/50
   parameter boxes, margin 0.159, independently re-verified): **no flush-free critical
   structure at any s in [3.82, s0] contains a thin wall-to-wall chain.** A46's G3
   rectangle lemmas were VACUOUS as posed (its [45,0,0,45] anchor has span
   4.828 > s0 and cannot exist; W1.6(f) corrected).
2. **Leg (b) delivered the strongest positional charge table in the lab — and its
   load-bearing entry is an exact ZERO.** 54-entry corner table (max 3491/4096 = 0.8523,
   all exact, 0 tile failures) with a proved feasibility law (near-corner cells force
   near-upright tilt: tilt > 40 deg cannot sit within 0.7 of a wall); but the near-flush
   cell ([0,1] deg x [0.49,0.7]^2) certifies EXACTLY 0 — an epsilon-tilted square parked
   epsilon off the corner strands nothing. Side table essentially inert (5/63 entries
   nonzero, max 0.125); pair primitive vacuous at A21-zone hypothesis width.
3. **Leg (c): the majority composition does not fire — the FORCED sum is exactly 0 for
   every profile.** Flush-freeness does NOT activate the corner primitive: the adversary
   parks the zone occupant in the zero cell (rattlers are unconstrained by criticality).
   Even GRANTING every contact and both zone occupants their maximal bins, the honest
   minimal profiles reach 1.77-2.99 = x1.35-2.27 short of B0. The PACKING-level
   flush-mandatory composition does NOT fire; census factor from (c): none. The
   criticality-aware statement is untouched — refined into I-L19 (sect. 6b).
4. **Canaries all pass, twice over:** the composition is provably vacuous on Trump + all
   12 atlas families (each has 12-17 flush contacts), and the primitive tables price
   Trump's three wall-flush corner squares at exactly 0 (consistent — the zero is real
   geometry, not resolution).

## 2. Leg (a): Theorem T1 and the s* exception (notes/theory.md; results/t1_span_check.json)

**T1 (span quantization).** In a flush-free configuration, every square of a thin
(degree-2) wall-to-wall load chain has its two contact points at equal height and at
x-distance exactly 1 (tilt exactly class 0) or exactly sqrt2 (tilt exactly 45) — the
proof runs W1.6(a)-(e) plus three new dismissals (mixed interior-edge/own-corner squares
are impossible; coincident contact points force either unbalance or an FL flush between
the neighbours; CC-CC squares also quantize to 0/45). The span telescopes:
span = o*sqrt2 + r with o >= 2 (both ends are 45-diamonds), r >= 0 integers.
**Corollary: o*sqrt2 + r meets [3.82, s0] only at (o,r) = (2,1)** — verified in exact
rationals (results/t1_span_check.json, PASS). So:
- At s0 (and at every other s in the certified window): **flush-free thin critical
  structures do not exist. Standalone theorem, no computation needed.**
- At s* = 2 sqrt2 + 1 exactly: the unique candidate is the 3-chain [45, 0, 45]
  (two wall-corner diamonds + one upright receiver; 2 free parameters y0, b).
- **Correction banked:** A46 W1.6(f)'s "minimal thin structure [45,0,0,45] at s0" cannot
  span (2 + 2 sqrt2 = 4.828 > s0); gap G3's designed rectangle lemmas were aimed at a
  nonexistent structure. W1.6(a)-(e) are untouched (T1 is built on them).

**The s* exception certificate (leg-a compute): PROVED over the full declared parameter
domain** (results/sstar_lemma.json, sstar_report.md). Statement: for every (y0, b) with
y0 in [sqrt2/2, sqrt2 + 1/2] (up-down symmetry half) and b in [max(0, y0-1), y0], no 8
unit squares with pairwise disjoint interiors fit in [0, s*]^2 avoiding the interiors of
the chain C(y0, b) — so the [45,0,45] structure admits no 11-packing completion. Method:
monotone rational relaxation (container [0, 383/100]^2; rational obstacle C_shr proved
exactly to lie inside lambda*C for every parameter in the box, lambda = 10001/10000,
slack >= 1/256) + A08-style exact measure certificates with an obstacle-exemption rule
(exempt placement boxes exhibit an exact witness point inside both the obstacle and
every placement) — the audited A08 branch-and-bound core imported verbatim, two new
links each machine-checked. 50/50 parameter boxes PASS, exact coverage audit of the
parameter domain: 0 gaps; worst mass margin 8 - 7.8412 = 0.1588 (at the genuine corner
of the domain, relaxation-limited); all 50 certificates re-verified in fresh processes
plus an independent random-placement negative control.

**Composed consequence — the attempt's headline positive: THE THIN BRANCH OF
FLUSH-MANDATORY IS CLOSED, COMPLETELY.** T1 (theory, exact-checked) + the s* certificate
(exact, 50/50) give: at EVERY s in the certified window [3.82, s0], no flush-free
critical structure contains a thin wall-to-wall load chain — with NO exceptions and no
delta_0-style hypothesis. This is the first fully closed branch of the flush-mandatory
conjecture.

## 3. Leg (b): the primitive tables (results/primitives_report.md — full tables there)

- **Corner table (i):** 54 entries over [49/100,11/10]^2 x 6 tilt bins (position boxes
  enlarged to cover the s0/(97/25) scale-back of A21's normalized zones), PlacedBox
  bin-uniform, every shipped tile exact (7049 tiles, 0 failures), shipped in BOTH theta
  and delta indexings + radial profiles. Range 0 to 0.8523 (delta-indexed max, far-corner
  cell [0.9,1.1]^2 near-upright). Cross-checks A23-4b (0.34-0.61) at the corner-touching
  cells (0.405 at (30,40]).
- **Feasibility law (positional fact, banked):** tilt in (40,45] is INFEASIBLE within
  0.7 of a wall (w(40)/2 = 0.7047); near-corner cells force near-upright tilt.
- **The load-bearing zero:** C_x0_x0_b0_1 ([0,1] deg, [0.49,0.7]^2) = exactly 0, zero
  tiles at every radius. Confirmed by Trump: his three corner-zone squares land exactly
  there and strand nothing.
- **Side table (ii) inert at zone width:** min over cy = 0 for all (cx, tilt) pairs;
  only 5/63 entries nonzero, all at extreme cy cells (window-corner artefacts), max 0.125.
- **Pair pilot (iii):** float 0.0098 at the smallest provably-disjoint offset — the pair
  primitive pays only at core boxes ~10-20x tighter than A21 zones (consistent with
  A23-4c's 1.38 at +-0.01 cores).

## 4. Leg (c): the composition (results/composition_a47.json; notes/theory.md sect. 2)

Accounting per honest minimal profile (A46 sect. 5a counts; thin profiles deleted by T1):

| profile (n_WC, n_int) | FORCED sum | GRANT-ALL sum | vs B0 |
|---|---|---|---|
| non-thin k_H=3, 1 axis (3,3) | **0** | 1.8528 | x2.18 short |
| non-thin k_H=4 (2,5) | **0** | 1.7727 | x2.27 short |
| non-thin k_H=5 (2,7) | **0** | 1.9138 | x2.11 short |
| non-thin k_H=3, 2 axes (4,3) | **0** | 2.0740 | x1.94 short |
| non-thin k_H=11 all-loaded (4,16) | **0** | 2.9912 | x1.35 short |

FORCED = what the hypotheses actually force: WC tilt has no lower bound (A46: no
delta_0) -> w_WC min bin = 0; interiors small-angle -> 0; A21 corner/side occupants'
bins unforced -> table min = 0 (the near-flush parking cell). **The composition's honest
value is zero — not small, zero.** Explicit evasion witness: a flush-free structure
whose wall contacts are at tilt <= 1 deg, interiors near-flush, zone occupants
epsilon-tilted uprights parked epsilon off the walls, charges nothing in any table.
(Scope: a PACKING-level evasion — this witness is NOT a critical point, it drains; see
the scope paragraph below and sect. 6b.)
GRANT-ALL = every contact at its maximal bin + both zone primitives at their maxima
(upper accounting, overlaps ignored in the overstating direction) — still x1.35-2.27
short at the forced counts.

Supporting facts:
- **P1 (population vacuity, notes/theory.md):** the A46 bridge instantiates independently
  per contact; no toolkit statement couples distinct contacts' mismatches, so the honest
  small-angle population bound is trivial. And it is MOOT: interior caps are
  angle-independent and tiny (CE <= 0.00708 at every mismatch, sharp-CC <= 0.070557), so
  even an all-large-angle interior population contributes <= 1.62 = 0.40 B0.
- **A26 tilt-forcing ingredient (assessed):** >= 2 squares are mid-tilt in any 11-packing
  (at most 9 within 2.503 deg of axis-parallel — universal, exact). This bounds the
  near-upright population but forces neither zone membership nor wall contact for the
  mid-tilt pair: adds 0 to FORCED. It becomes usable only jointly with a positional
  lemma pinning a mid-tilt square to a corner — which A21 measured to be beyond LP reach
  (per-corner occupancy unprovable at 3.88).
- **Ceilings:** CE-only interiors + 12 max wall contacts + BOTH zone maxima =
  3.7947 = 0.941 B0 — the A45/A46 Ceiling-2 law SURVIVES the zone enrichment (barely:
  the corner primitive moved the ceiling from 0.699 B0 to 0.941 B0, the largest single
  jump any enrichment has bought, and still short). With sharp-CC interiors the fire
  zone is 84 count-lattice points, all needing n_WC >= 10 AND >= 6 sharp-wedge CCs —
  atlas max is 3 WC + 1 aligned CC (worth 0). Nothing real is within reach.

**The mechanism, named (sixth face of the enumeration-certificate mismatch law) — with
its SCOPE stated precisely (PI framing).** What A46/A47's budget compositions price is
flush-free PACKINGS — a strictly stronger statement than flush-mandatory needs, which is
about flush-free CRITICAL POINTS. At the packing level the failure law is: (i)
unconditional POSITION theorems (A21) activate only the min-over-zone charge, and the
zone min is pinned to exactly 0 by flush-ADJACENT parking positions — the flush-free
class is open, its closure meets the flush stratum, and every continuous dead-area
certificate vanishes there (the A46 no-delta_0 phenomenon one level up: positions
instead of angles, rattlers instead of loaded contacts); (ii) even with activation
granted, the budget is DIFFUSE: certified capture on genuine structures maxes at ~14%
(A46 12.0%, A47 13.8%) — the missing 86% is far-field slack no local hypothesis
(contact, interface, junction, zone) has ever captured. Activation cleverness cannot
beat diffuseness at the packing level. BUT the escape witness is an escape for the
over-strong statement only: the epsilon-parked corner square is NOT critical — it
drains (the wedge-closing relaxation is unblocked for it). The measured 1-degree loaded
contacts (A37-NEW-0, fam 31) all sit inside flush-RICH structures; no flush-free
critical structure has ever been observed; and A46's bridge is a LOCAL balance
certificate that has never been embedded globally. The criticality-aware statement is
untouched by this failure (which never used criticality) and by A44's closure (which
was first/second-order FJ + counting only).

## 5. Canaries — ALL PASS (results/composition_canary_vacuity.json, primitive_canaries.json)

- **Vacuity of the composition** (required: genuine structures must be UNTOUCHED): every
  genuine atlas family + Trump has >= 12 flush contacts (WF+FL 12-17); the flush-free
  hypothesis excludes them all — composition provably vacuous on every known structure.
- **Primitive-table canaries:** Trump exact — 8 zone instances fire, every one prices 0,
  sum 0 <= B0; his corner squares are wall-flush uprights in the zero cell (independent
  confirmation the zero is real). 12 atlas families (float): sums 0-0.58 vs budgets
  4.03-4.50, max capture 13.8%. No violation anywhere.

## 6. Census factor

The composition does not fire, so no A43-H1 measurement was run (pre-registered
condition not met). Leg (a) contributes a hard prune: every flush-free thin branch
(L2-flagged degree-2 chains) dies at ALL s in the window — the s* exception included —
a branch-class deletion for every future census node, though the class was already
codimension-flagged and measure-tiny, so the count factor is ~1.

## 6b. The refined open problem (PI; recorded as I-L19)

The budget compositions of A45/A46/A47 all price flush-free PACKINGS and never use
criticality; A44's closure was first/second-order FJ + counting only. The
criticality-aware route between them is virgin: **"every flush-free configuration admits
an unblocked descent — sustaining all-near-flush balance requires bridge structures whose
own mid-tilt support requirements are globally self-defeating."** Concretely (the attack
surface, from A46 w1_theory par. 5 + W1.4): a loaded near-flush contact at mismatch d
needs a blocker whose support edge slopes g > d (strictly MORE tilted, itself loaded,
hence needing its own load path and possibly its own bridge — a recursion), a presser
loaded from above, and no wall shortcuts (wall levers die as 1/sin d). Target: the
support-slope recursion either terminates (an unblocked wedge-closing descent —
contradiction with criticality) or forms finite self-supporting mid-tilt structures that
are separately excludable. The A47 feasibility law (mid-tilt cannot hide within 0.7 of a
wall) and the atlas canaries (all genuine CPs flush-rich) are ready ingredients. Recorded
as I-L19 on the ideas board with I-L18 closed into it.

## 7. Keepers (banked)

1. **Theorem T1** — thin-branch span quantization; flush-free thin structures dead at s0
   unconditionally; the full window reduced to the single point s* with an explicit
   2-parameter structure; A46 W1.6(f)/G3 corrected. First fully-closed branch of the
   flush-mandatory conjecture.
2. **The corner primitive table** — 54 exact entries, both indexings, radial profiles;
   max 0.8523 (4x the best wall-wedge charge); the strongest positional charge table in
   the lab. Future use: case-tree NODE KILLERS — any context that pins a corner square's
   box + tilt (A29/A14-style nodes) can now charge 0.18-0.85 per node; useless only for
   hypothesis-free composition.
3. **The feasibility law** — tilt (40,45] infeasible within 0.7 of a wall; near-corner
   forces near-upright. Free structural fact for all future corner analyses.
4. **P1 + the sixth face** — the definitive statement of why occupancy-activated local
   charging cannot reach B0 at n = 11: activation is zeroed by flush-adjacent parking;
   diffuseness caps capture at ~14% even when activated.
5. **The s* certificate machinery** — obstacle-aware exact coverage certification at a
   rational relaxation: A08 verifier core verbatim + two new machine-checked links
   (parameter-uniform rational obstacle containment; lambda-scaling disjointness), LP
   producer strictly weaker than the verifier so nothing undischargeable is emitted,
   50 certificates re-verified from scratch + negative control. Reusable wherever a
   pinned partial structure must be shown incompletable (case-tree node kills, future
   exception points, irrational-parameter structures via rational relaxation).

## 8. Gap list

- **A47-G1** (leg a): NONE — the s* lemma is proved over the full declared parameter
  domain (50/50 boxes, exact coverage audit 0 gaps). Engineering lesson worth keeping:
  the producer's robust-row patch lattice must be ALIGNED with the verifier's dyadic box
  tree, else a failing placement box straddles two patch cells and the produce-verify
  loop thrashes (cost: several wasted LP iterations before the fix).
- **A47-G2**: T1 covers the certified window [3.82, s0]; below 3.82 (vacuous — packings
  cannot exist there by the certified lower bound) nothing is claimed.
- **A47-G3** (= GAP-A47b-1): the side table's nonzero entries sit at the window edge
  (13/8) — window-limited, not converged; irrelevant to the verdict (side is inert).
- **A47-G4** (= GAP-A47b-2): corner/side/w_WC region overlaps were not disjointified
  (needed only for a firing composition; all uses here are upper-accounting or zero).
- **A47-G5**: the near-flush corner zero is at 1/64 resolution; the TRUE dead area of an
  eps-tilted eps-off-corner square is O(eps) > 0 but vanishes in the limit — no finer
  resolution changes the composition verdict (the infimum is genuinely 0).
- **Float-only scope:** pair pilot; atlas canary rows (radians in the atlas); everything
  load-bearing (T1 check, both tables, Trump canary, composition) is exact Fractions.
- Inherited: A46-G1/G2/G4 (pencil tower, bridge global realizability, neighbourhood
  form), the lambda_0 = 0 self-stress branch (composition vacuous there, as in A46),
  N1 <= 12 and 3k+2 = 35 quoted not re-derived.

## 9. Files

notes/theory.md (T1 + P1 + composition frame), code/ (t1_span_check.py, compose_c.py,
leg-a producer/verifier, leg-b harness copies), results/ (t1_span_check.json,
sstar_lemma.json, sstar_report.md, primitives_{corner,side}.json, pair_pilot.json,
primitive_canaries.json, composition_canary_vacuity.json, composition_a47.json,
primitives_report.md, this report), work/ checkpoints, LOG.md. A29 untouched; no prior
attempt modified.
