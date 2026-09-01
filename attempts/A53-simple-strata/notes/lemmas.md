# A53 — simple-square stratification: definitions, lemmas, honest gaps (Fable, 2026-08-31)

Container side s0 = 969271/250000 = 3.877084 (rational, s0 ∉ Z, frac(s0) = 0.877084 ∈ (3/4, 1)).
Everything below is stated for a packing P of 11 pairwise interior-disjoint closed unit squares
in [0,s0]²; "axis-aligned" means orientation ≡ 0 (mod 90°). Branch labels: [T] = proved theorem,
[S] = proved selection/soundness statement, [C] = conjecture / named gap.

## L1 [T] — Definition (PI, authoritative) and its three readings

For a corner c of the container let (e_c, f_c) be the inward unit axes at c and define the
**corner grid** G_c = { c + (i+1/2) e_c + (j+1/2) f_c : i, j ∈ Z≥0 } (slot (i,j) of corner c).

**Definition (simple square, Young form — adopted as primary).** For a packing P and corner c,
let S_c(P) be the largest set of squares of P such that each is axis-aligned, centred EXACTLY at
a slot of G_c, and the occupied slots form a **Young diagram**: (i,j) occupied ⇒ every (i',j') with
i' ≤ i, j' ≤ j occupied (by squares of P). Simp(P) = ∪_c S_c(P); k(P) = |Simp(P)|;
the **skeleton** of P is the 4-tuple (S_BL, S_BR, S_TR, S_TL) (equivalently the slot-set union,
by L2(ii) below).

*Well-definedness*: if two subsets of P both have the Young property at c, so does their union
(a slot is occupied by at most one square of P, by disjointness of interiors and unit size; the
union of two Young diagrams is a Young diagram). Hence a unique largest S_c(P) exists. ∎

**Reading 1 (PI's phrasing).** "Integer distance from two perpendicular sides + gap-free flush
support chains to both = part of a tiling grown in from a corner." The Young form is the precise
content of "tiling grown in from a corner": the diagram IS the corner-anchored partial tiling.
CAUTION: the literal chain phrasing, with chains allowed to pass through partially-overlapping
flush contacts, is STRICTLY WEAKER. Witness (exact, at s0): P ⊇ {(½,½), (½,s0−½), (3/2,s0−½),
(3/2,s0−5/2)} with the last square's remaining neighbours free. The square Q at (3/2, s0−5/2) =
(1.5, 1.377084) is at integer distance 1 from the left side and 2 from the top side; a gap-free
flush chain to the top exists through the aligned stack (3/2, s0−3/2)... (when present), and a
flush chain to the LEFT side exists through the single PARTIAL contact with the corner square
(½,½) (shared edge segment x = 1, y ∈ [0.877084, 1], length 0.122916 > 0). Literal reading:
simple. Young form: NOT simple (TL-diagram cell (1,2) requires cell (0,2) = (½, 1.377084),
absent). We adopt the Young form; the enumeration and all LP semantics use it.

**Reading 2 (the brief's recursive doubly-flush definition)** — "doubly-flush against
{walls} ∪ {already-locked}, wall-anchored" with positive-length flush contacts — is also strictly
weaker than the Young form, for the same reason (partial-overlap cross-family supports). Measured:
at s0 the recursive definition admits 7204 locked sets (944 D4 classes; code/skeletons.py), the
Young definition 1110 (163 D4 classes; code/skeletons2.py), and every Young union is recursively
locked (verified exactly), with 6094 recursively-locked sets NOT of Young form. The three readings
agree on every set consisting of full corner blocks (in particular on Trump's skeleton).

**Edge cases the definition settles** (PI list, now theorems of the Young form):
(i) integer-offset floating squares (no support path): non-simple — a slot square with an
unoccupied predecessor slot violates the diagram closure; (ii) interior flush clusters (flush
pairs/chains not reaching a wall): non-simple — every diagram cell chains to the corner;
(iii) simultaneous integer distance from two OPPOSITE sides is impossible: it would force
a + 1 + b = s0 with a, b ∈ Z≥0, contradicting s0 ∉ Z. Hence:

## L2 [T] — Anchor uniqueness and the exact slot grid

(i) Each simple square lies in exactly one S_c(P) — its x-coordinate anchors to exactly one of
{left, right} and its y-coordinate to exactly one of {bottom, top} (L1(iii)); so the 4-tuple is a
partition of Simp(P) and |Simp| = Σ_c |S_c|.
(ii) The slot coordinates take exactly 6 values per axis at s0: L-family {1/2, 3/2, 5/2} and
R-family {s0−1/2, s0−3/2, s0−5/2} (offset 3 leaves the admissible band [1/2, s0−1/2] since
1/2 + 3 > s0 − 1/2 ⟺ s0 < 4). No two slot values differ by exactly 1 across families
(s0 ∉ Z; verified exactly), so flush unit steps never leave a family.
(iii) Two slot squares from different corner diagrams at column offsets i (from left) and j (from
right) conflict in x iff |s0 − 1 − (i+j)| < 1 iff i + j ∈ {2, 3} (frac(s0) ∈ (3/4,1)); this is the
PI's shared-wall constraint (widths w + w' ≤ 3) and is subsumed by the exact pairwise-disjointness
filter used in the enumeration.
(iv) **Census stability in s**: statements (i)–(iii) and hence the whole combinatorial census
depend only on s ∈ (3.82, 3.9) ⊃ [certified lower bound, s_T]: all comparisons used are of the
form s ≶ integer or s − (i+j) ≶ 1 ± ..., constant on that window. The slot POSITIONS of the
R-family move continuously with s; the combinatorics do not.

## L3 [T] — Partition exhaustiveness (census theorem)

Every packing P of 11 unit squares in [0,s0]² has exactly one skeleton Simp(P), and Simp(P) is
one of the 1110 4-tuples of Young diagrams inside 3×3 with pairwise interior-disjoint slot
squares, enumerated exactly (rational arithmetic) in code/skeletons2.py — 163 classes up to the
D4 symmetry of the container, with census by k = |Simp|:

  k:            0  1  2  3  4  5  6  7  8  9
  raw tuples:   1  4 14 40 85 156 222 260 208 120   (total 1110)
  D4 classes:   1  1  3  6 14  22  33  35  30  18   (total 163)

Proof: L1 well-definedness + L2 (each diagram fits in 3×3, cross-diagram disjointness is
necessary since P is a packing) + completeness of the enumeration (all 20⁴ partition 4-tuples
filtered by the exact disjointness predicate). Trump's skeleton is the k = 5 class
(λ_BL, λ_BR, λ_TR, λ_TL) = ((2,1), (1), (1), ∅) up to D4 — one 3-cell staircase + two 1×1
corner diagrams, NOT "three 1×1 + one 2-cell" (shape note for the PI; k = 5 is as announced).
Realizability of a stratum is NOT claimed — empty strata are killed for free.

## L4 [T] — Trump's exact locked count (canary; code/trump_k.py, results/trump_k.json)

At Trump's own side s_T = 3.87708359002281417730789706… his packing has k = 5: squares at
(½,½), (3/2,½), (½,3/2), (s_T−½,½), (s_T−½,s_T−½) are simple; the sixth upright at
(½, 2.532558314349614787…) is **ε-off-grid**: it is x-flush to the left wall but its centre
height differs from the nearest slots by
  ε = cy − 5/2 = 0.03255831434961478706…  (from-below slot; equals its bottom-edge gap to
      square (½,3/2)'s top edge), and 0.155474… above the from-above slot s_T − 3/2;
cy has minimal polynomial of degree 7 (A03's certified data), hence is irrational and equals NO
slot value exactly. The five tilted squares (θ = 40.1819…°) are non-simple by orientation. All
separations decided with margin > 10⁻² against 60-digit certified decimals. So **k_Trump = 5**;
the PI's tier boundary stands: kill k ≥ 6, enumerate at k = 5.

**The blocked slide (measured, the bridge mechanism in the flesh).** The ε-off square cannot be
slid down onto its completing slot (½, 5/2): the landing corridor is [0,1] × [2, 2.032558…], and
the tilted square 7 (centre (1.68855870…, 1.95961282…)) has its leftmost corner at
(0.98404…, 2.01903…) — INSIDE the corridor (x < 1, y > 2), 0.01353 below the off-grid square's
bottom edge. The grid-completing slide is blocked by a mid-tilt corner at intrusion depth 0.0136;
this is exactly the A46/A48 bridge geometry and is why the k-maximality lemma below cannot force
k = 6 at Trump. (It also confirms the PI premise "Trump realizes no 6-skeleton" the honest way:
not because the wedge is above, but because the slide corridor is occupied.)

## L5 [S] — Pin-hypothesis kills and the downward-closure cap (tier-1 logic)

**Lemma (kill semantics).** Let S be any set of k slot squares (any pin-set, skeleton or not).
If a rational measure certificate passes the exact verifier for: "every admissible closed unit
square in [0,s0]² that is not provably meeting one of the k pinned unit squares has μ-mass ≥ 1,
and μ(total) < 11 − k", then no packing of 11 unit squares in [0,s0]² contains axis-aligned
squares at all k pins simultaneously. (A13/A14 case-LP semantics with degenerate cores; the
11 − k unpinned squares are admissible placements disjoint from the pins, each eats ≥ 1.)

**Corollary (cap).** A kill of pin-set S empties EVERY stratum whose skeleton contains S (the LP
never uses the "no further simple square" clause — it prices containment only). Every Young
4-tuple with k ≥ 7 contains a Young 4-tuple with exactly 6 cells (delete corner-maximal cells one
at a time; removing a maximal cell preserves the Young property). Hence killing the 33 D4 classes
at k = 6 empties every stratum with k ≥ 6 — the stratification is finite at the top with a
33-node cap, and no k = 7,8,9 LP is ever needed. D4 transfer of a kill is the usual symmetry
action on certificates. Killing further DOWN (k = 5, tier 2) is per-class; corners4-type pins
(k = 4) are measured ALIVE (τ = budget, §results), consistent with the ghost.

**Measured closure (2026-08-31).** 32 of the 33 k = 6 classes carry PASS exact certificates
(certs_wip/); the one open class is k6_23 = Trump's tuple + TL corner (τ = 4.9337, LP-dead,
below cert margin). The cap is nevertheless CLOSED for k ≥ 7 unconditionally: a combinatorial
check (every k = 7 class contains at least one CERTIFIED k = 6 sub-tuple, transitively for
k = 8, 9) passed with 0 exceptions. Open at the k = 6 layer itself: the single stratum k6_23.

## L6 [S] — k-maximality drain selection (the low-k patch), honest version

Setting: drain_lemma v3 (D1 attainment). Let M = argmin σ over D₀, m = min σ; normalize each
minimizer so its (tight) bounding box is [0,m]²; slots at side m (census unchanged on the window,
L2(iv)). Define the move set: a **grid-completing slide** of P ∈ M is an axis-parallel
translation of a single axis-aligned square Q along one coordinate onto a slot whose Young
predecessors are already in Simp(P), such that the swept corridor (Minkowski sweep of Q over the
translation segment) meets no other square of P and stays in [0,m]².

**Selection Lemma [S].** (a) A grid-completing slide maps M to M (σ cannot increase: the slide
stays inside the current bounding box; σ cannot decrease below m by minimality). (b) It strictly
increases k: the slid square becomes simple (its slot completes a diagram), and no other square's
simplicity is affected (Simp-membership of the others depends on their own positions and the
occupied-slot pattern, which only grows). (c) k ≤ 11, so every maximal chain of grid-completing
slides terminates. Hence: **some minimizer P\* ∈ M admits NO grid-completing slide** — WLOG the
minimizer is slide-stuck. ∎

**What this gives.** Low-k strata need not be killed outright; it suffices to kill their
slide-stuck minimizers: stratum Σ_S with small k contributes to s(11) only through packings where
every ε-off near-slot square is BLOCKED (its every landing corridor is intruded by another
square — generically a tilted corner, the bridge geometry of L4) or not axis-aligned/anchored.

**What this does NOT give [C].** (i) Slide-stuck ⇏ k large: k = 0 tilted minimizer candidates and
blocked configurations (Trump!) are slide-stuck at low k. (ii) The blockedness constraint is
semi-algebraic but INVISIBLE to the guard LP (the LP prices containment, not criticality — the F4
lesson of A45–A47 again): pin-LPs alone cannot close k ≤ 4. (iii) The move set is translations of
a single square only; σ-neutral compound moves (rotate-then-slide, cascades) are not selected
over — extending the move set enlarges the stuck-set analysis but could strengthen the lemma
(A49's measured "everything presses into flush" suggests rotations toward flush are also
σ-non-increasing in the drain sense; NOT formalized here). (iv) At a minimizer the bounding box is
touched on all four sides by definition, but not necessarily by axis-aligned squares — R-anchored
slots exist as positions, not as guaranteed occupation.

**Named gap G-A53-1 [C] (s-parametric kills).** LP kills are certified at s = s0 only. The
program "s(11) > s0' for s0' < s0" runs the stratification at the minimizer's own side m ∈
[3.82, s_T]; R-family slot positions move with m. Conjecture: residual τ\*(m) for a fixed
combinatorial pin-class is monotone non-decreasing in m on the window (more room, easier
covering — same monotonicity the A07 τ\*(s) curve shows globally); under it, a kill at s0
transfers down. Unproved; the honest alternative is interval-in-s certificates (A41 seam S6
machinery).

**Named gap G-A53-2 [C] (blocked-slide pricing).** Convert L4's corridor-intrusion geometry into
rows: a blocked ε-off square at gap ε forces a tilted corner inside an ε-corridor, which forces
the blocker's own support (A48 C1–C6' cascade). If the cascade's wall-termination instability
(A50, in flight) closes, slide-stuck low-k minimizers with ε-off squares are excluded, leaving
k = 0-pure-tilt (A51's hunt regime) + genuinely-on-grid strata. This is the composition point
with I-L19; nothing here assumes it.
