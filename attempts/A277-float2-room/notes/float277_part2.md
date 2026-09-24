# part 2 -- what one blocker can do (ONE-DROP), what two floaters do to each other (MUTUAL), and the witness

Setting (s-free, n-free): BL quadrant, F a unit square meeting the open box (0,1)^2 and touching no wall
(h_u(F), h_v(F) > 0, both < 1); drops T_u(F) = F - h_u e_x, T_v(F) = F - h_v e_y; a BLOCKER of a drop is a unit
square K of the quadrant, int K ∩ int F = ∅, int K ∩ int(drop) ≠ ∅.

## 2.1 Lemma ONE-DROP  [T]
*A square K blocks at most one of T_u(F), T_v(F).*  Proof.  BLOCKER-SIDE (box_meeters.md s.1.2, hypotheses: F meets
the open box, K interior-disjoint from F, K meets int T_v(F)) says EVERY line separating K from F, normal n from K to
F, has n_v > 0 and n_u < 0.  Its mirror (same section) for a blocker of T_u(F): every separating normal m from K to F
has m_u > 0 > m_v.  Disjoint convex bodies have a separating line; its normal cannot satisfy both.  ∎
Lean core: two sign conditions on one vector (`one_drop_core`, part 7).  Corollary: a floater with both drops blocked
has two DISTINCT blockers.

## 2.2 Lemma MUTUAL  [T]
*Let C, D both meet the open box and float, int C ∩ int D = ∅.  Exactly one of:*
*(P) some separating line has positive slope; naming C the square on its upper-left side, D may block T_v(C) and C
may block T_u(D); D never blocks T_u(C), C never blocks T_v(D);*
*(N) no separating line has positive slope; then neither blocks any drop of the other.*
Proof.  D blocks T_v(C) forces every separating normal (D to C) to be (-,+): positive slope, C upper-left.  C blocks
T_u(D) forces every normal (C to D) to be (+,-), i.e. (D to C) = (-,+): the same condition.  D blocks T_u(C) would
force (D to C) = (+,-): contradicts the previous two, and C blocks T_v(D) forces (C to D) = (-,+), i.e. (D to C) =
(+,-): the same contradiction.  If no separating line has positive slope, none of the four relations holds.  ∎
So in (P) C's wall drop and D's floor drop need blockers OUTSIDE {C, D}; in (N) all four drops do.  By ONE-DROP
the outside blockers of T_u(C) and T_v(C) differ, and those of T_u(D), T_v(D) differ; a single outside square may
block one drop of C and one of D (X above both; A below-right of both).

## 2.3 Normal form forces every drop of a non-toucher to be blocked  [T]
Phi_1 = # wall touchers is the first potential (normal_ring.md s.1.2).  If T_u(F) (or T_v(F)) had no blocker, replacing
F by the drop is a packing at the same side (the drop is inside the container, interior-disjoint from every other
square) with one more toucher.  So in the maximiser every drop of every non-toucher is blocked.  (This is the drop
form of A261's P1; it needs no cell family.)  Consequence for a FLOAT2 corner: case (P) needs two outside blockers
K_C (of T_u(C); above-left of C by a positive-slope line) and K_D (of T_v(D); below-right of D); case (N) needs at
least two, at most four, outside blockers.

## 2.4 The witness float262.json, exactly  [T-computed, code/witness277.py, results/witness277.json]
Drops and their blockers (interior overlap areas): T_u(C) <- X (0.00243), T_v(C) <- D (0.743), T_u(D) <- C (0.0428),
**T_v(D) <- NOBODY** (h_v(D) = 0.0047; T_v(D) meets A, X, C in area 0).  C-D are in case (P) with C upper-left, as
MUTUAL predicts.  Consequences:
(i) [F] BRIEF: "A on the floor and X on the wall block their drops" -- A blocks nothing; A's leftmost x is 1.382, it
    meets no box (a MIDDLE toucher: its right end 2.600 < s - 1).  X blocks T_u(C) only.
(ii) [F] as a normal-form object: D drops 0.0047 to the floor and becomes a toucher meeting the box (Phi_1 + 1); the
    corner is then a JAM corner (D on the floor meets the box; C floats; X above holds C) inside H1-H3: X_top = 3.337
    > s - 1, X_low = 2.028 >= 1, X meets int T_u(C), C meets the open box (area 3.8e-4), D' = T_v(D) meets it (area
    0.518) and int D' ∩ int C = ∅ (area 0 checked).  A262's verdict "JAMMED FLOAT2 EXISTS" is A261's coarse-grid J
    (JAM_COARSE cells miss the drop cell at D's tilt), not the drop notion.  Tag: the witness is [M] for "a FLOAT2
    configuration with C jammed exists"; for "a FLOAT2 corner in normal form exists" it is NOTHING.
(iii) The dropped pair: T_u(C) (wall offset b = h_v(C) = 0.9865, tilt 14.47 deg) and T_v(D) (floor offset a = h_u(D) =
    0.3515, tilt 12.87 deg) are interior-disjoint (area 0), as part 3 proves in general for case (P).
