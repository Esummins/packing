# Leaf WASTE — the uncoverable-area leaf, its Lean shape, and what the raster owes

A164, 2026-09-08.  Labels: [T] proved here, [S] routine given cited items, [M] measured,
[F] finding, [C] open.

## 1. The statement

**Node.**  A node N is a finite family of hypothesis boxes B_1, …, B_r, each a product
rect(B_j) × [t0_j, t1_j] of a closed centre rectangle and a closed tilt interval, together with a
**core** K_j with

  (K)  K_j ⊆ Q(c, θ)   for every (c, θ) ∈ B_j.

A135's exact axis core of a pin and A132's polygon core K′(B) of a conditioned square both
satisfy (K) — that is exactly what "core" means in those two attempts.  The node's **budget** is
b = 11 − r.

**Cover sets.**  At side m, for a fixed square side λ ≥ 1,

  Cov_j(λ)   = ⋃ { Q_λ(c, θ) : (c, θ) ∈ B_j }                             the j-th box's cover
  Adm        = { (c, θ) : Q_1(c, θ) ⊆ [0, m]²  and  int Q_1(c, θ) ∩ int K_j = ∅ ∀j }
  Cov_free(λ) = ⋃ { Q_λ(c, θ) : (c, θ) ∈ Adm }
  **U(N, m, λ) = [0, m]² \ ( Cov_free(λ) ∪ ⋃_j Cov_j(λ) )**

(λ = 1 is the plain statement; λ > 1 is the window transport of §4.)

**Lemma WASTE [T].**  Let P = (Q_1, …, Q_11) be an 11-packing at side m (closed unit squares,
pairwise interior-disjoint, inside [0, m]²) consistent with N — i.e. after re-indexing,
(c_j, θ_j) ∈ B_j for j ≤ r.  Then

  **|U(N, m, 1)| ≤ m² − 11.**

Hence **|U(N, m, 1)| > m² − 11 ⟹ no such packing exists: N is DEAD, with no LP.**

*Proof.*  For j ≤ r, Q_j ⊆ Cov_j by definition.  For i > r: Q_i ⊆ [0, m]², and for every j ≤ r,
int Q_i ∩ int Q_j = ∅ while K_j ⊆ Q_j by (K), so int Q_i ∩ int K_j = ∅; thus (c_i, θ_i) ∈ Adm and
Q_i ⊆ Cov_free.  Therefore ⋃_i Q_i ⊆ [0, m]² \ U, and since the eleven interiors are disjoint and
each square has area 1 with null boundary,

  11 = Σ_i |Q_i| = |⋃_i Q_i| ≤ | [0, m]² \ U | = m² − |U|.  ∎

The budget is A89's E(m) = m² − 11 (`docs/proofs/tilt_floor_k0.md` §7), bounded on the window by
B₀ = s₀² − 11 = 4.031780343056.

## 2. Lemma ID is the special case [T]

A89's Lemma ID takes the four corner unit boxes C_c.  Under the hypothesis DEPTH(c) < δ at all
four corners, no square interior meets (0, 1−δ)² in c's frame, so
⋃_c [0, 1−δ]²_c ⊆ [0, m]² \ ⋃_i int Q_i; the corner boxes are pairwise m − 2 > 1 apart hence
disjoint, and Lemma WASTE's measure step gives 4(1 − δ)² ≤ m² − 11.  Lemma ID therefore differs
from Leaf WASTE in ONE respect only: its uncoverable region is certified by a **hypothesis**
(shallowness, a NO-family in the node's case-LP certificate) instead of by **geometry**
(no admissible pose reaches the region).  Everything downstream — disjointness of the charged
regions, composition across corners, the exempt-box bookkeeping of §7's Lemma B transport — is
the same, and the region no longer has to be a corner box or even connected: it only has to be a
measurable subset of U, and areas of subsets of U simply add.

**Corollary [T] (the separated-region form, for the record).**  If W_1, …, W_k are pairwise
disjoint measurable sets and n_i is an upper bound on the number of the eleven squares that can
meet W_i, then Σ_i max(0, |W_i| − n_i · cap(W_i)) ≤ m² − 11, where cap(W) is any upper bound on
|Q ∩ W| for one square.  With n_i = 0 this is Leaf WASTE restricted to W_i; with W_i the corner
boxes and n_i = 0 it is Lemma ID.  **[F] On this population the refinement is empty**: n_i = 0 is
the only value that ever beats |U ∩ W_i| (see §5), because whenever a region is reachable at all
it is reachable by a square that covers essentially all of it.

## 3. What the raster owes [T]/[C]

The Lean statement quantifies over sets; the raster discharges exactly one existential.  Fix a
finite family R of closed axis-aligned cells of side p.  The raster's claim is

  **(RAS)  ∀ C ∈ R, ∀ (c, θ) ∈ Adm ∪ ⋃_j B_j :  Q_λ(c, θ) ∩ C = ∅**,

i.e. R ⊆ U(N, m, λ); then |U| ≥ |R| = |R| · p² by monotonicity of Lebesgue measure and the leaf
fires on the count of cells alone.  (RAS) is reduced to finitely many arithmetic inequalities by
two Lipschitz facts and nothing else:

* **[T] L-c.**  clearance(c, θ) := min( container clearance of the centre, min_j −depth(K_j,
  Q_1(c, θ)) ) is 1-Lipschitz in c.  (Each term is the signed distance from c to the complement of
  a convex set: for the walls, an affine function; for K_j, the signed distance to
  K_j ⊕ (−Q_1(0, θ)), which is convex.  A min of 1-Lipschitz functions.)
* **[T] L-θ.**  clearance is (√2/2)-Lipschitz in θ, because rotating a unit square about its centre
  by dθ moves every boundary point by ≤ (√2/2) dθ, and SAT depth between convex sets is
  1-Lipschitz in Hausdorff distance.  (A148 geo148.py states and uses both.)

Given those, with tilt bins of width dθ about θ_k, a rotated grid of pitch q in the θ_k frame,
m₁ = q√2/2 + (√2/2)(dθ/2) and H = λ/2 + λ(√2/2)(dθ/2) + q/2 + p√2/2, the certificate per cell is

  **∀k, max over the finitely many grid nodes n in the θ_k-frame box of half-width H about C's
  centre of clearance(n, θ_k)  <  −m₁**,

plus, for each hypothesis box, ∀ sampled tilt θ_i in its tilt range, the exact rect-vs-rotated-
square SAT gap between rect(B_j) and Q_λ(C's centre, θ_i) exceeds λ(√2/2)(dt/2) + p√2/2.  Every
one of those is a polynomial inequality in the rational data (A132 certifies K′'s vertices as
rationals; A135 certifies the pins' exact half-sides), so the obligation is decidable.

**Named obligations for Lean.**
* **W1 (measure).**  Eleven pairwise interior-disjoint closed unit squares inside [0, m]² have
  |⋃ Q_i| = 11.  `MeasureTheory` additivity plus "the boundary of a rotated unit square is null"
  and "its area is 1"; the second is the rotation-invariance of `volume`.  Routine [S].
* **W2 (core transfer).**  K_j ⊆ Q_j and int Q_i ∩ int Q_j = ∅ ⟹ int Q_i ∩ int K_j = ∅.  One line
  [T]; it is where (K) — and so A132/A135's certified cores — enters.
* **W3 (raster soundness).**  L-c, L-θ and the window/dilation bookkeeping above, i.e. (RAS) from
  the finite family of inequalities.  This is the ONLY analytic content and the only place the
  pitch, the tilt count and the margins appear.  **[C] not written**; it subsumes the Lipschitz
  lemmas A148 already relies on informally, so writing it pays for both attempts.
* **W4 (window transport).**  §4 below; the same bookkeeping as K0-WIDEN / Lemma B.

Shape:

    theorem waste_kill (N : Node) (m : ℝ) (R : Finset Cell)
        (hR  : ∀ C ∈ R, RasterCert N m C)          -- decidable, W3 turns it into R ⊆ U
        (hgt : (R.card : ℝ) * N.pitch ^ 2 > m ^ 2 - 11) :
        ∀ P : Packing 11 m, ¬ P.Consistent N

Axiom cost: **zero new axioms** if W1–W4 are proved; one axiom (W3) if the Lipschitz reduction is
assumed, which is the honest interim position and is the same axiom A148's pages already lean on.

## 4. The window [T]

A57 emits at s₀ and the node's boxes are the transported ones (Lemma B): a packing at
m′ ∈ [3.81794, s₀] dilates by λ = s₀/m′ ∈ [1, λ_max], λ_max = s₀/3.81794 = 1.015527…, to eleven
squares of side λ in [0, s₀]², whose uncovered area is s₀² − 11λ² ≤ s₀² − 11 = B₀.  A side-λ
square that is admissible (inside the container, interior-disjoint from the cores) contains the
CONCENTRIC unit square, which is then admissible too, and its own body is inside the concentric
λ_max square.  So keeping admissibility at side 1 and inflating only the COVER square to λ_max
gives U(N, s₀, λ_max) ⊆ U for every m′ in the slab, and

  **|U(N, s₀, λ_max)| > B₀  kills the node at every side in the slab.**

The λ = 1 number is the statement at side exactly s₀.  Both are reported per node; the λ_max
number is the smaller of the two, so B₀ — the LARGEST budget on the slab — is the right threshold
for it.  (Note the direction: the smallest side in the slab has the smallest budget but also the
least room, and the two effects do not compose monotonically; the transport above is what makes
the single s₀-frame raster cover the slab.)

## 5. [M] What it measures — and why it does not kill

See `results/summary164.txt` and `results/summary164.csv` (71 nodes: the 11 pin-free k0v4 cells and
the 60 a57v4 pages, raster pitch 0.01 × 36 tilt bins, 10⁵ sampled poses each).  Headline: **the
leaf is alive on every node, by a factor of at least 2.1 even on the best one.**

| | n | mean |U|/B₀ | max |
|---|---|---|---|
| k0v4 (0 pins, budget 10) | 11 | 3.18 % | 8.32 % (`l1_158`, 0.3353) |
| A57 (5 pins, budget 5) | 40 | 19.47 % | 35.97 % (`k5_11_interior_Y0202`, 1.4504) |
| A60 (5 pins, budget 4–5) | 20 | 21.20 % | 42.18 % (`f1_L10_0003`, 7 boxes, 1.7007) |

Distribution of |U| / B₀: min 0.000 %, q1 11.75 %, median 18.56 %, q3 23.48 %, max 42.18 %, mean
17.44 %; 0 nodes above 50 %, 0 above 100 %.  Refined on the two extremes at pitch 0.005 × 90 tilt
bins: `f1_L10_0003` 1.8969 (47.05 % of B₀; window-sound variant at λ_max 1.8084 = 44.85 %),
`k5_11_interior_Y0738` 1.4261 (35.37 %; window 1.3271 = 32.92 %), `l1_104` 0.1290 (3.20 %; window
0.1152 = 2.86 %).  Cross-checks: 7.1 M poses drawn over the population, 1 223 887 certified
admissible by an independent SAT pass, 976 134 carried through the containment test, **0 hits**;
and the independent checker `verify164.py` (its own SAT, its own dense sweep, no shared code with
the dilation) confirmed five masks — `l1_104`, `l1_158`, `l2_p114_001`, `k5_11_interior_Y0738`,
`f1_L10_0003` — cell by cell, 4.6–7.1 M meeting poses tested per node, **0 admissible meeters**.

The single-square notion is simply too generous: on a 3.877-side container with at most seven
small cores, almost every point is inside SOME admissible unit square, and the certified set
collapses to slivers against the walls and to the wedges between a core and a wall.

**[F] The corner column is ZERO on all 71 nodes.**  `U:corners` = 0.00000 everywhere: no corner
unit box is ever certified unreachable, so **Lemma ID's charged region is empty on the whole alive
population** — not "small", empty.  All the certified waste is in the four wall strips (64–100 %
of it, median ≈ 100 %) with the rest in the interior.  That is the sharpest thing A164 measured:
the shallow-corner
route of §7 has no consumer at this frontier, and the wastage that does exist is a WALL-STRIP
phenomenon.

**[F] Where the PI's reading is right and where it breaks.**  On `l1_104` every one of the
0.129 units of certified waste lies in the EAST wall strip — the wedge between K′(H) and the wall
x = s₀ that A148's page already flags as the node's one sub-unit pocket (H → wall x = s, 0.828).
The location is exactly the PI's.  What does not hold is the count: the PI's "only one square's
centre can sit near the right wall below H's reach" is false as an unconditional geometric
statement — the outer admissible-centre mask lets **seven** 1-separated centres into
x ≥ s₀ − 1/2 and **eight** into x ≥ s₀ − 1 (upper bounds; the disk bound and a 0.7-cell cover
bound agree to within one).  The "only one" can only come from a COUNTING hypothesis, and the
natural one — K0-FREE′, every corner box doubly met, so eight of the eleven squares are
corner-committed — is measured here too (`crowd` row) and is **vacuous on this geometry**: a
square that meets a corner box has its centre within √2/2 of it and covers √2/2 further, so the
four corner reach-envelopes already cover all but 0.0166 of the container at s₀ = 3.877 on
`l1_104` (max 0.248 over the eleven k0 cells), against the 2 + B₀ = 6.03 the row would need.  A
counted-wastage leaf therefore needs the LANE machinery (A141's per-cell meeter counts, A153's
cover number), not an area argument: the area budget B₀ = 4.03 out of 15.03 is simply too large a
fraction of the container for a 0.1–1.0 sliver to reach.

**[F] Scaling, and the one prediction worth testing.**  |U| grows with the number of hypothesis
boxes (mean 0.128 at 1 box / 0 pins (n = 11), 0.793 at 6 boxes / 5 pins (n = 59), 1.701 at 7
boxes (n = 1)) and with the
raster's resolution (`l1_104`: 0.0048 / 0.0407 / 0.0736 / 0.1290 at pitch 0.04 / 0.02 / 0.01 /
0.005 — at coarse pitch the MARGINS, not the geometry, dominate; the increments are halving, so
the pitch-0 limit is within ~15 % of the 0.005 value).  Read across the box count: 1 box → 0.13,
6 → 0.81, 7 → 1.90 at the fine raster.  Extrapolating the box-count trend rather than the pitch
trend, **the leaf would first fire at roughly 9–10 hypothesis boxes, i.e. a node with only 1–2
free squares left** — and at that depth the LP is cheap anyway, which is the honest reason the
leaf has no consumer.  The concrete thing to test, if anyone wants to: run it at emission on the
A57 level-3/4 nodes (7–8 boxes) where it costs 15 s and might catch a node the LP would have spent
850 s on.
