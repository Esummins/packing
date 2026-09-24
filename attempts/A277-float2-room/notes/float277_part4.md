# part 4 -- route (S2): when STRIP-C and STRIP-D are the JAM strip lemma, and when they are not

Notation: case (P) of MUTUAL, C upper-left of the positive-slope separator, D lower-right; both meet the open box.
K_C blocks T_u(C) (above-left of C), K_D blocks T_v(D) (below-right of D), K_C, K_D not in {C, D} (part 2).

## 4.1 Lemma LOW with a FLOATING lower-right square  [T]
ring_domain.md (F4) proves L_h(C) = h_v(C) + cos theta_C > 1 (>= 1.121 in its cases (a), (b); > 1 in (c)) from: a
positive-slope separator with A below it and C's vertices B, R above it (Lemma SLOPE), and ONE point P of A under the
separator -- its left vertex at height cos alpha (case a), its top vertex (b), or its upper-left edge (c) -- with
x_P < 1 (A meets the box) and A a unit square.  The floor contact of A enters only as "the left vertex is at height
cos alpha".  For D floating, D's left vertex is at height h_v(D) + cos theta_D >= cos theta_D and h_u(D) < 1: every
inequality of (F4) holds with >= in place of =.  So **(D1) L_h(C) > 1 holds in case (P) with D in A's role** (Lean
cores `low_core`, `lh_gt_one`, `lh_gt_one_steep` unchanged: their hypotheses are the same numbers).  Mirror (swap
x and y: positive slopes stay positive, upper-left becomes lower-right): **L_h^mirror(D) = h_u(D) + cos theta'_D > 1**
with C in A's role.  WEDGE-FLOAT (A267 s.1, only C + the two walls) then applies to C, and mirrored to D.

## 4.2 What the JAM strip proofs use, and the transfer table
The proofs of STRIP_2-IN-JAM use (ring_domain.md s.0 header, strip_jam.md s.0, flat_x.md s.0 "nothing here uses A"):
H1 for the holder (meets the far box: X_top > s - 1, hence X_low > 1.406; inside the container; misses the open box,
X_low >= 1), H2 (holds T_u(C), misses C), C meets the open box and floats, and (D1) L_h > 1 -- the ONLY use of A.
A273's drop tree prunes on H1 / the box condition only (disc273.md s.2.4).  Hence, with 4.1:

| strip | holder | H1 | (D1) | status of the strip statement |
|---|---|---|---|---|
| STRIP-C | K_C = X serving TL (X in S_8) | holds | 4.1 | = 5b: [T] on theta, phi <= 5 deg (A276) + [T-computed] A273 tree (c5_4 / c5_5 capped) |
| STRIP-C | K_C a middle wall toucher (X_low in [1, 1.406)) or a non-toucher | FAILS | 4.1 | [C]: none of A267 / A272 / A273 / A276 applies (they use X_low > 1.406) |
| STRIP-D | K_D = A2 serving BR (in S_8), mirrored | holds | 4.1 mirror | = 5b mirrored (same tree, same theorems) |
| STRIP-D | K_D a middle floor toucher (Y of part 2: x_min = 1.548 < 1 + 0.406) or a non-toucher | FAILS | 4.1 mirror | [C] |

So route (S2) is complete exactly in the sub-case **both blockers serve their far boxes** (X in S_8 above C, A2 in S_8
right of D); there BL-CAP-2(T_u(C), T_v(D)) [4 parameters] closes the corner -- and by 3.4's [M] even ROOM with A2
added may hold there.  In every other sub-case (S2) has an open strip; (S1) has none.

## 4.3 Case (N)  [T]
Neither floater blocks a drop of the other; T_u(C), T_v(C), T_u(D), T_v(D) need outside blockers (>= 2 squares by
ONE-DROP).  The drops T_u(C) and T_v(D) may now overlap (no separator protects them), so a certificate on the dropped
pair would have to keep overlapping obstacles (never PRUNE on their overlap).  (S1) is unaffected: it never drops.
[M] no case-(N) configuration is in hand (the search of part 5 runs both cases; float262's witness is case (P)).

## 4.4 What is true without any strip  [T]
For every FLOAT2 corner, every BL-sector miss Q is interior-disjoint from C and D, and (from part 2.1-2.3) a normal-form
FLOAT2 corner carries two outside blockers, each a pocket square unless it serves its far box.  Nothing else about the
blockers is used by (S1).  In particular the "P4 RETREAT chain" (BRIEF (b)) is not needed and not used: the count of
3.1 charges every blocker as a pocket square whatever holds it.
