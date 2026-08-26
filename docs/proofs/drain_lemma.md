# Drain lemma and the T3 exclusion specification (advisor draft v2, 2026-08-26)

v2: D3 (KKT under constraint qualification, with a to-be-written degenerate taxonomy) is REPLACED by
D3′ (Fritz John, CQ-free). The taxonomy obligation is DISCHARGED: FJ needs no constraint
qualification, so corner-corner ties, flush contacts and every other CQ failure are covered by the
same statement. T3 updated accordingly. v1's D3 kept below for the record.

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

## Lemma D3′ (per-selection FRITZ JOHN necessity) — PROVED, no CQ needed

Smooth selection NLP. Epigraph variables (z, s). Constraints, all polynomial after clearing (1+t²):
 (i) containment: every corner coordinate of every square lies in [0, s] — already smooth, NO
     selection needed (a conjunction of 88 polynomial inequalities plus the epigraph coupling);
 (ii) pairwise separation, selected: for each pair (i,j) a selection S picks an owner square, one of
     its two edge normals u (a rational function of the owner's t), a sign, and a dominant corner k*
     of the other square, and imposes  (c_j − c_i)·u ≥ h_i + (corner_{k*} − c_j)·u  together with the
     three DOMINANCE rows  (corner_{k*} − corner_m)·u ≥ 0.  Dominance makes the selected row equal to
     true SAT separation, so S-FEASIBLE ⇒ INTERIOR-DISJOINT (soundness of the smooth surrogate), and
     for convex polygons a separating axis always exists among edge normals, so every z ∈ D₀ is
     S-feasible for AT LEAST ONE selection of the finite menu (completeness). Ties (corner-corner
     contacts, flush = parallel edges) are consistent with SEVERAL selections and are covered by each.

Statement. Let ẑ minimise σ over D₀ with value m (exists by D1). Then for EVERY selection S
consistent with ẑ, the point (ẑ, m) is a global minimiser of s over the S-feasible set (S-feasible ⊆
D₀ and ẑ ∈ S-feasible), a smooth polynomial NLP; hence the FRITZ JOHN conditions hold: there exist
λ₀ ≥ 0 and λ ≥ 0, (λ₀, λ) ≠ 0 (normalise λ₀ + Σλ = 1), with λ₀∇s + Σ λ_k ∇g_k = 0 and λ_k g_k = 0.
Proof: FJ is necessary at any local minimum of a smooth NLP with NO constraint qualification
(F. John 1948; standard). ∎

Remark (cost, not soundness). FJ admits spurious solutions with λ₀ = 0 (positively dependent
constraint gradients with no descent content). A cell whose FJ system is solvable only with λ₀ = 0
is not certified by (c); split it, or exclude the λ₀ = 0 branch by a separate argument. This is the
only trace left of the old degenerate taxonomy, and it is an efficiency question.

## Lemma D3 (v1: per-selection KKT necessity) — superseded by D3′, kept for the record
At any minimiser ẑ, fix ANY "selection" S consistent with ẑ: for each pair, one SAT axis achieving
separation; for the box, the extremal corners; for containment, the touching walls. The region R_S
defined by S's smooth polynomial inequalities satisfies ẑ ∈ D₀ ∩ R_S ⊆ D₀, so ẑ also minimises σ over
D₀ ∩ R_S, a SMOOTH NLP; under the selection's constraint qualification (LICQ/MFCQ), the standard KKT
conditions for that NLP hold at ẑ. This holds for EVERY consistent selection simultaneously.
Care points, quarantined as their own (finitely many) degenerate branches: selections where CQ fails
(corner-corner ties, flush contacts — handled in A22 by centre-distance surrogate rows), and rattler
directions (zero multipliers; excluded by first parking rattlers: a square with a strict free
neighbourhood contributes no active rows and its cell needs only D2).

## T3 specification (sound by D1, D2, D3′)
A cell C (product of centre boxes and t-intervals for the 11 squares, mod symmetry) is EXCLUDED if:
 (a) C ∩ D₀ = ∅ (infeasible; interval SAT), or (b) D2 fires (uniform slack), or
 (c) for EVERY selection S in C's finite consistent menu (only rows whose interval evaluation on C
 straddles activity — small menus for small cells; menu must include tie selections, which are the
 SAME smooth systems), interval-Krawczyk (or any sound interval test) excludes all solutions of the
 FJ(S) system with value ≤ s₀ and λ₀ ≥ 0, λ ≥ 0, λ₀ + Σλ = 1 in C. Active-set sub-branching within a
 selection is an implementation choice (complementarity rows λ_k g_k = 0 kept polynomial, or subsets
 enumerated with interval pruning); either is sound.
If every cell of a cover of D₀/symmetry is excluded, then no minimiser with σ ≤ s₀ exists, so
s(11) > s₀ by D1. — Implementation: A22's machinery per branch; menus enumerated per cell.

## Status
D1, D2, D3′ complete — T3 is SOUND as specified, with no outstanding taxonomy obligation. Remaining
questions are entirely about COST: menu sizes after interval pruning, per-selection Krawczyk time,
the λ₀ = 0 branch, and how many cells a full cover needs (pilot: A30). The stress lemma (critical ⇒
wall-to-wall loaded structure) remains an OPTIMISATION (prunes menus), on the I-L11 track separately.
