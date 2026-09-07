# N as per-square boxes — what A96 must quantify over, and why "a square in each box" is enough

`results/N_boxes.json` (generator `code/export_boxes119.py`, read-only on A116).

## 1. The two objects A116 states, and which one A96 can consume

A116 states **two** box-shaped objects and they are not the same:

* **Lemma STAB's pair boxes** (`a116lib.pair_box`, `forced_test`): for ONE pair (i, j) a
  6-dimensional box of *pair* poses, carrying a *forced selection* σ*.  This is the PI's
  single-leaf route (`docs/proofs/local_certificate.md` §3.2).  It is not a hypothesis on a
  configuration: it names a pair and a separating axis, quantities that do not occur in A96's
  node LP at all.  **A96 cannot consume it.**
* **The certificate's hypothesis N** (`a116lib.build_bodies`): a PRODUCT of per-square
  axis-aligned boxes — one (centre box) × (tilt interval) per free body ℓ ∈ L, one slack core
  per class pin p ∈ P, all in the class frame at side s0.  **This is what Theorem LOCAL kills
  and what A96 quantifies over.**  It is what `N_boxes.json` exports.

The export is a transcription, not a re-derivation: `boxes[l].cx = [c_x − r, c_x + r]`,
`cy = [c_y − r, c_y + r]`, `theta_deg = [θ_ℓ − ρ, θ_ℓ + ρ] ∩ cut`, with the anchor
c_ℓ = z*'s pose dilated to s0 (`c · s0/s*`) for a tilted square and the slot position at s0 for
a load-bearing slot square that is not a pin (S02's `BR(0,1)`).  `pins[p]` is
(α_p, β_p, h): centre in α_p + β_p·s + [−h, h]², tilt exactly 0, h = δ/√2, δ = 10⁻².

## 2. The hypothesis, in the form A96's caselp / NO-family machinery reads

For a node of class `cls` whose support has been carried into the class frame by A107's
`struct_op` (a D4 element, listed per class in `N_boxes.json.frame_ops`; the action at s0 is in
`d4_ops`):

> **YES(N).**  s ∈ [3.82, s0 + 0.02]; for each p ∈ P a square with tilt 0 and centre in
> α_p + β_p s + [−h, h]²; for each ℓ ∈ L a **distinct other** square with centre in ℓ's box and
> tilt (mod 90°) in ℓ's interval; and, where a cut is present, θ_ℓ (mod 90°) ≥ cut for every
> **tilted** ℓ.  Conclusion: no such configuration of the n squares is a packing at side ≤ s0.

Only |P| + |L| squares are named; the remaining n − |P| − |L| are unconstrained.  The cut is a
single scalar inequality on the common tilt variable of the tilted squares of L, exported as
`cut.inequality`.

## 3. The DROP/COVER step: "a square in each box" + pins ⟹ inside N ⟹ dead

Three separate facts compose; none of them is about pair boxes.

**(a) DROP** (`local_certificate.md` §1, Reduction DROP [T]).  If a packing of n squares at side
s satisfies YES(N), the |P| + |L| named squares are themselves a packing of |P| + |L| squares at
side s satisfying YES(N) — pairwise interior-disjointness and containment in [0, s]² are
inherited by any subfamily.  So `Dead_{L∪P}(N, s0) ⟹ Dead(N, s0)`, with **no** hypothesis on the
dropped squares.  This is the only place the other squares are used, and they are used by being
forgotten.

**(b) COVER** (§2, Lemma COVER [T]) is where "the union of the boxes covers every configuration"
actually lives, and it is a statement about SELECTIONS, not about pair boxes.  Fix a tilt cell K
of the finite cover 𝒦 of the product of the tilt intervals.  Let z be any configuration of
L ∪ P inside the boxes, at side s, with all pairs interior-disjoint and tilts in K.  For each
near pair, Lemma SAT gives a signed selection σ with g_σ(z) ≥ 0; σ is *possible* on K because the
interval enclosure [g_σ]_K contains g_σ(z) ≥ 0.  Hence z ∈ P_λ(θ) for the leaf λ that assigns
those selections.  The pins' and boxes' own rows hold at z by hypothesis; far pairs impose no
row.  So

  {configurations of L ∪ P inside the boxes, interior-disjoint, side s}  ⊆  ⋃_{K ∈ 𝒦} ⋃_{λ possible on K} P_λ(θ),

a finite union indexed by (cell, leaf).  **The covering family is the family of leaf polyhedra of
the per-square boxes**, and the pair boxes of Lemma STAB play no part in it: STAB only says when
a pair needs NO case split (one leaf suffices), i.e. it prunes the union, never defines it.

**(c) LEAF** (§2, Lemma LEAF [T]) + Theorem LOCAL: on every (K, λ) the LP value exceeds s0, so no
point of any P_λ(θ) has s ≤ s0.  Composing (b) and (c): no interior-disjoint configuration of
L ∪ P inside the boxes has side ≤ s0.  Composing with (a): no packing of n squares satisfying
YES(N) has side ≤ s0.  ∎

So the implication A96 needs — *a square in each box, plus the pins, plus the cut ⟹ inside N ⟹
side > s0* — is exactly (b) ∘ (c) ∘ (a), and the only object it quantifies over is the product of
per-square boxes exported here.

## 4. The sampled check (`sample_check` per N in `N_boxes.json`)

12 000 configurations per N drawn uniformly from **these boxes** (free poses uniform in
(cx, cy, θ), pin offsets uniform in [−h, h]²), each tested at 30 sides spanning [3.82, s0]: a hit
would be a packing of L ∪ P at side ≤ s0 inside the exported boxes, i.e. a counterexample to
Theorem LOCAL's verdict AND to this transcription.  Result, all five N: **0 hits**
(free-pair-disjoint survivors 19 – 1 812; every survivor fails the wall/pin/side test at all 30
sides).  The rejects overlap by up to 0.7, which is why the survivor counts are small: the boxes
are wide, and almost every draw already has two of the L squares overlapping.

| N | L | r | ρ | cut | samples | free-pairs-disjoint | hits |
|---|---|---|---|---|---|---|---|
| S02 k5_11 (0.2, 10°) | f1 f2 f3 BR(0,1) | 0.2 | 10° | — | 12 000 | 420 | **0** |
| S02 k5_11 (0.05, 20°) | f1 f2 f3 BR(0,1) | 0.05 | 20° | — | 12 000 | 19 | **0** |
| S02 k5_11 (0.1, 10°) | f1 f2 f3 BR(0,1) | 0.1 | 10° | — | 12 000 | 174 | **0** |
| S07 trump5 (0.1, 40°) | f0 f2 f4 | 0.1 | 40° | θ ≥ 41.565° | 12 000 | 119 | **0** |
| S07 trump5 (0.2, 10°) | f0 f2 f4 | 0.2 | 10° | θ ≥ 41.565° | 12 000 | 1 812 | **0** |
| S02 k5_11 (0.1, 5°), blocking boxes | f1 f2 f3 f0 TR(0,0) BR(0,1) | 0.1 | 5° | — | 12 000 | 22 | **0** |

(A116 ran 10⁴ of its own on each; these 12 000 are independent draws with a different seed.  The
last row is A119's own T3 neighbourhood — the only one of the blocking-box grid that closes; it
carries SIX boxes, which is why so few uniform draws survive the free-pair test.)
