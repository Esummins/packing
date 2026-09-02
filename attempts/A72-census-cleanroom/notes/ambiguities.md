# A72 — definitional ambiguities found while writing the clean-room enumerator

**Written BEFORE running the enumerator and BEFORE opening any A53 artefact.**
Sources read (the only ones): `attempts/A53-simple-strata/notes/lemmas.md` L1–L3 (statements),
`docs/proofs/instratum_bridge.md` §E.2–E.4, `docs/proofs/d4_reduction_s0.md` (D4 action, R2/R3/R8),
`LOG.md` 2026-08-31 entries (A53 dispatch + close). **Not opened:** `A53/code/skeletons2.py`,
`A53/results/skeletons_young.json`, `A53/code/skeletons.py`, `A67/code/verify_d4_s0.py`.

Classification: **BINDING** = a different reading would change the census counts or the tuple set.
**LABEL** = affects only names/encoding, provably not the enumerated set.

---

## BINDING ambiguities

### B1 — Is "inside 3×3" a definitional restriction or a derived container fit?
L3 says "4-tuples of Young diagrams **inside 3×3**"; L2(ii) instead *derives* that the slot
coordinates take exactly 6 values per axis ("offset 3 leaves the admissible band [1/2, s0−1/2]
since 1/2 + 3 > s0 − 1/2 ⟺ s0 < 4"). The two are only consistent because s0 < 4.
**Resolution:** treat 3×3 as *derived, not assumed*. The enumerator ranges over all offsets
i, j ∈ Z≥0 and keeps those whose closed unit square lies in [0,s0]² (i.e. the centre coordinate
lies in [1/2, s0−1/2]), then *asserts* that the maximal offset comes out as 2 and that the number
of Young diagrams is 20. If the assertion failed, L3's "3×3" would be an independent hypothesis.

### B2 — "pairwise interior-disjoint": which predicate exactly?
L1 fixes the packing as "11 pairwise **interior-disjoint closed** unit squares". L3 filters the
4-tuples by "pairwise interior-disjoint slot squares" without restating the predicate.
**Resolution:** two axis-aligned closed unit squares at centres p, q have disjoint interiors iff
max(|p_x−q_x|, |p_y−q_y|) ≥ 1 (flush contact allowed, exact rational `>=`). This is BINDING and
strongly so: reading it as *closed*-disjointness (strict `> 1`) would delete every flush pair and
collapse the census. The choice is forced by L1's wording, but L3 alone does not force it.

### B3 — Can one square be simple at two different corners?
L1 defines Simp(P) = ∪_c S_c(P) as a **union**; L2(i) says the 4-tuple is a **partition** of
Simp(P), justified by L1(iii) (s0 ∉ Z rules out integer distance to two opposite sides).
So at s0 the two readings agree — but the enumeration must decide what to do with a hypothetical
tuple placing the same slot point in two corner diagrams.
**Resolution:** enumerate 4-tuples of diagrams (not sets of squares) and apply the B2 predicate to
*all* cross-corner pairs including coincident points (Δ = (0,0) fails max ≥ 1, so such tuples are
rejected). The enumerator additionally *verifies* that the L-family {1/2,3/2,5/2} and R-family
{s0−1/2, s0−3/2, s0−5/2} are disjoint at s0, making the case vacuous. **s0-specific**: at an
integer side this resolution would matter and L1/L3 would be genuinely ambiguous.

### B4 — Is a maximality or realizability filter applied?
L1 defines S_c(P) as the **largest** Young set at c. A literal transcription would enumerate only
tuples that can *be* a largest set, i.e. reject a tuple with an addable slot.
**Resolution:** NO such filter. L3 says the census is "all 20⁴ partition 4-tuples filtered by the
exact disjointness predicate", and "Realizability of a stratum is NOT claimed — empty strata are
killed for free." So the census is an over-approximation by design, and exhaustiveness (the only
property H2 needs) is preserved. Recorded because the definition (L1) and the census (L3) point in
opposite directions here, and only L3's parenthetical resolves it.

### B5 — Is the Young/down-set condition per corner or on the union?
L1 states the diagram condition "at c", inside S_c(P).
**Resolution:** per corner, independently. The union over corners is *not* required to be a
down-set of anything. (An "on the union" reading is not even well-typed — the four corner grids
are different lattices.)

### B6 — Cardinality cap k ≤ 11?
P has exactly 11 squares, so Simp(P) has at most 11 elements; L3's enumeration imposes no such cap.
**Resolution:** no cap imposed; the enumerator reports max k and asserts max k ≤ 11 so the question
is moot. (Predicted moot: L3's table stops at k = 9.)

### B7 — Is the empty diagram a Young diagram?
The down-set condition is vacuous on ∅.
**Resolution:** yes; the all-empty tuple is a legitimate skeleton (k = 0). Consistent with L3's
table having a k = 0 column.

### B8 — Is the D4 action defined on tuples or on the plane?
`d4_reduction_s0.md` R2/R3 define D4 as the 8 signed-permutation matrices acting about the
container centre (s0/2, s0/2); R8 separately asserts the *slot-level* rule
"g·slots(c, λ) = slots(g·c, λ) or slots(g·c, λᵀ)".
**Resolution:** implement the action on **plane points only** (exact Fractions, about the centre),
then re-decode each image point into (corner, offset, offset). The slot-level rule is then a
*checked consequence*, never an input — so A72's D4 reduction does not inherit A53/A67's
combinatorial slot bookkeeping. The enumerator asserts (i) each image of a census tuple is again a
census tuple (D4-closure), (ii) each image diagram is again a down-set, (iii) R8's λ/λᵀ rule.

---

## LABEL-only conventions (recorded; provably do not move the census)

### L1c — Which inward axis is e_c (the i index) and which is f_c (the j index)?
L1 writes "(e_c, f_c) the inward unit axes at c" without saying which is which.
**Resolution:** e_c = inward **horizontal**, f_c = inward **vertical**, at all four corners.
Non-binding: the set of Young diagrams in a k×k box is closed under transposition, so swapping the
convention at all four corners simultaneously permutes the diagram family onto itself and leaves
the set of 4-tuples-of-slot-points setwise identical. Only the partition *labels* λ change.

### L2c — Partition notation λ: row lengths or column lengths?
**Resolution:** λ_i = |{ j : (i,j) ∈ D }| indexed by the *e_c* (horizontal) offset i, reported as a
non-increasing tuple. The Trump canary from L3 — ((2,1), (1), (1), ∅) — is therefore checked
**up to transposition per corner**, since L1c/L2c together leave λ vs λᵀ undetermined.

### L3c — Corner order inside the 4-tuple.
L1 writes (S_BL, S_BR, S_TR, S_TL) — cyclic. Adopted verbatim. Affects the encoding and hence the
canonical representative, not the census.

### L4c — Choice of D4 canonical representative.
Not specified anywhere in the written sources. **Resolution:** canon = lexicographic minimum, over
the 8 images, of the encoding "corner-major, cells sorted by (i,j)" under L3c's corner order.
Consequence for the diff: **class representatives are not a meaningful cross-check** unless A53
happens to use the same encoding. The invariant object is the *partition of the 1110 tuples into
orbits*; A72 diffs that partition, and reports representative agreement separately as a
convention-match datum rather than as a correctness criterion.

---

## Scope note — the 7204 / 944 "recursively locked" corpus is NOT clean-room re-enumerable

The BRIEF mentions the locked corpus (A67 R8) alongside the Young census. Reading 2 in L1 (the
recursive doubly-flush definition: "doubly-flush against {walls} ∪ {already-locked}, wall-anchored,
with positive-length flush contacts") is stated in one clause and never given a precise recursion,
a seeding rule, or a definition of which flush contacts count. Re-implementing it from the written
sources would produce a number determined by my guesses, not by the definition — the opposite of a
clean-room check. **A72 therefore re-enumerates the Young census (1110 / 163) only**, which is
exactly the object H2 names and exactly the object `hface` / B.CENSUS consumes. That Reading 2 is
under-specified in the written record is itself a finding (see report).
