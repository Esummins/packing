# Drain lemma and the T3 exclusion specification (advisor draft v1, 2026-08-22)

Setting. Configurations z = (c_i, t_i)_{i=1..11}, t_i = tan(θ_i/2) ∈ [0,1]; all constraints polynomial
in (c, t) after clearing (1+t²) denominators. D₀ = {z : squares pairwise interior-disjoint, normalised
min corner at the origin, contained in [0,4]²} — closed, bounded, SEMI-ALGEBRAIC (SAT gives the
polynomial description of interior-disjointness). σ(z) = side of the minimal enclosing axis-aligned
square = max of finitely many polynomial coordinate functions; continuous, piecewise-polynomial.

## Lemma D1 (attainment) — PROVED
If some z ∈ D₀ has σ(z) ≤ s₀ ≤ 4, then m := min{σ(z) : z ∈ D₀} ≤ s₀ is ATTAINED. Proof: {σ ≤ s₀} ∩ D₀
is closed (σ continuous, D₀ closed) and bounded, hence compact; σ continuous. ∎
Consequently s(11) = m, and "no minimiser of σ with value ≤ s₀ exists" ⟹ s(11) > s₀.

## Lemma D2 (gap-squeeze; slack cells are free) — PROVED
If z ∈ D₀ has every pairwise SAT-gap and every bounding-box clearance ≥ δ > 0, then σ can be strictly
decreased: the affine map c_i ↦ c_i·(σ−δ/3)/σ keeps interior-disjointness (relative centre displacement
≤ 2δ/3 · (diam/σ) < δ) and shrinks the bounding box. Hence NO minimiser has all gaps ≥ δ. Per-cell form:
if interval arithmetic certifies min-gap ≥ δ(C) > 0 uniformly on a cell C, then C contains no minimiser.
(This is the certified version of "slack configurations drain"; constant 1/3 is slack, any c < 1/2 works.)

## Lemma D3 (per-selection KKT necessity) — PROVED modulo CQ bookkeeping
At any minimiser ẑ, fix ANY "selection" S consistent with ẑ: for each pair, one SAT axis achieving
separation; for the box, the extremal corners; for containment, the touching walls. The region R_S
defined by S's smooth polynomial inequalities satisfies ẑ ∈ D₀ ∩ R_S ⊆ D₀, so ẑ also minimises σ over
D₀ ∩ R_S, a SMOOTH NLP; under the selection's constraint qualification (LICQ/MFCQ), the standard KKT
conditions for that NLP hold at ẑ. This holds for EVERY consistent selection simultaneously.
Care points, quarantined as their own (finitely many) degenerate branches: selections where CQ fails
(corner-corner ties, flush contacts — handled in A22 by centre-distance surrogate rows), and rattler
directions (zero multipliers; excluded by first parking rattlers: a square with a strict free
neighbourhood contributes no active rows and its cell needs only D2).

## T3 specification (sound by D1–D3)
A cell C (product of centre boxes and t-intervals for the 11 squares, mod symmetry) is EXCLUDED if:
 (a) C ∩ D₀ = ∅ (infeasible; interval SAT), or (b) D2 fires (uniform slack), or
 (c) for EVERY selection S in C's finite consistent menu (only geometrically possible contacts within
 C's ranges — small menus for small cells), interval-Krawczyk excludes all solutions of KKT(S) with
 value ≤ s₀ in C, degenerate branches included.
If every cell of a cover of D₀/symmetry is excluded, then no minimiser with σ ≤ s₀ exists, so
s(11) > s₀ by D1. — Implementation: A22's machinery per branch; menus enumerated per cell.

## Status
D1, D2 complete. D3 complete for CQ-selections; the degenerate-branch enumeration is specified but its
completeness argument (every CQ-failing point lies in one of the listed branches) is to be written out
with the exact contact taxonomy (corner-edge / corner-corner / flush / wall variants) — next draft.
The stress lemma (critical ⇒ wall-to-wall loaded structure) is NOT needed for T3 soundness; it is an
OPTIMISATION (prunes the selection menus) and stays on the I-L11 track separately.
