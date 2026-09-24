# part 1 -- reading notes: what NO-JAM(11) link 5d needs, and what the sources give

Sources read: BRIEF; k0_knowledge s.1, s.2, s.5-s.8; no_jam.md; float262.json (+ float262.py, geom262.py);
normal_room.md; strip_enclosure.md; ring_domain.md s.0; box_meeters.md s.0-1.2; three_lemmas.md s.4;
strip_jam.md s.0, s.7-9; flat_x.md s.0, s.5.  Notation: BL corner frame, wall x = 0, floor y = 0, O = (s/2, s/2).

## 1.1 The chain's shape at a non-PAIR corner  [T, no_jam.md s.2.3]
ROOM(S): every unit square in [0,s]^2 interior-disjoint from a structure S contains O.  ROOM(S) => every square of
P \ S contains O => |P \ S| <= 1 => n <= |S| + 1.  So the count closes at n = 11 iff |S| <= 9 (S may hold NINE squares,
not eight: one spare).  MISS => a sector at one corner (A259 s.2.2, s-eliminated by corner_frame_mono): a free Q
missing O has (q - O).n >= 1/2 for a wall normal n and lies in one half; dropping every square not at that corner is
sound (monotone).  So ROOM(S) is decided corner by corner: for each corner, a certificate over the squares of S at
that corner, with the free square Q in the corner's two sectors.

## 1.2 The JAM reduction that FLOAT2 must copy  [T given STRIP; three_lemmas.md s.4.3]
BL sectors of a JAM corner {A, A2, X, C}: STRIP (no sector square has an interior point in T_u \ C, T_u = C's WALL
drop) => the sector pocket of {A, A2, X, C} is inside the pocket of {A, A2, T_u} = pair3 at BL (floor row (a, phi) +
one wall square (h_v, theta): 4 parameters).  [M] s.4.2: replacing C by its FLOOR drop T_v FAILS (+0.11, +0.94): the
comparison obstacle is the wall drop, because A already occupies the floor.  STRIP for the JAM corner = STRIP2-IN-JAM:
[T-prose] on the ring domain (A267), reduced under H1-H3 to the DROP lemma (A272/A273: tree 40/81 cells + two capped
cells), [T] on the near-flat corner (A276 FLAT-X, CORNER).  The only hypotheses those proofs use: H1 (X meets TL,
X in the container, X_low >= 1), H2 (X meets int T_u, misses C), H3 (C meets the open box, floats).  A267's
WEDGE-FLOAT uses ONLY C, the wall and the floor (A267 s.1 remark (i)): "applies to a FLOAT2 corner's floaters
verbatim" (A267 s.5).  Lemma LOW / SLOPE (A271, (D1) L_h > 1.12) DOES use A (a floor toucher sharing the box).

## 1.3 The FLOAT2 witness  [M, float262.json; poses (cx, cy, theta) = centre + tilt, local261.verts]
C (0.7307, 1.5955, 14.47 deg), D (0.9503, 0.6035, 12.87 deg), A (1.9911, 0.6090, 14.45 deg), X (0.6549, 2.6825,
22.85 deg); terms: gaps C-D 0.0023, A-D 0.0022, X-C 0.0039 (A-C 0.27, X-D 1.01, X-A 1.36); box depths C 0.0135,
D 0.6368; float distances h_u(C) 0.1216, h_v(C) 0.9865, h_u(D) 0.3515, h_v(D) 0.0047; -J_C = -J_D = 0.0022.
"Jammed" here is A261's J (no wall-touching unit cell of ANY tilt meeting C is free of A, X, D), a local 4-square
model: A is a floor toucher whose box role is unspecified (its leftmost x = 1.38: it meets NO box -- a MIDDLE
toucher), X a wall toucher (top 3.34 > s - 1: it serves TL).  The optimiser maximised the least margin, so every
contact is at gap ~0.0022: the exact witness check (part 2) must say which drops each blocker blocks.
Reading of the picture: D lies 0.0047 above the floor and 0.35 off the wall, meeting the box deeply; C sits on D's
left vertex, 0.12 off the wall, meeting the box by a 0.013 sliver; X's bottom vertex rests on C's upper-left edge;
A's left flank rests on D's right vertex.

## 1.4 Definitions fixed for this note
FLOAT2 corner (BL): two floaters C, D meet the open box; no toucher of wall 3 or wall 0 meets the box (SAME-WALL +
WEDGED-SEAL give <= 1 toucher per wall at a doubly-met box; here there are 0).  Drops: T_u(Q) = Q - h_u(Q) e_x,
T_v(Q) = Q - h_v(Q) e_y; strips S_u(Q) = T_u(Q) \ Q, S_v(Q) = T_v(Q) \ Q.  A BLOCKER of a drop = a square of P
whose interior meets the drop's interior.  DIRECT blocker = a wall toucher; INDIRECT = anything else.
Facts used: (i) [T] Phi_1-maximality: every drop of every non-toucher is blocked (else translate it: a packing at
the same side with one more toucher; normal_ring.md s.1.2 Phi_1 = # wall touchers).  (ii) [T] BLOCKER-SIDE
(box_meeters.md s.1.2, s-free): a blocker of T_v(C) is separated from C by a line of positive slope, below-right;
a blocker of T_u(C) above-left.  (iii) [T] acyclicity of "blocks the horizontal drop of": two disjoint convex sets
have a separating line; if it is not horizontal, one set is left of the other at every common height (cf. A261 s.1.1
"acyclicity of below").  (iv) [T] a floater meets one box only; a toucher's wall extent w(theta) <= sqrt2 < s - 2.

## 1.5 What 5d needs, exactly
(a) ROOM(S) for a structure S with a FLOAT2 corner, |S| <= 9, decided per sector by certificates already run
(A259 PAIR: 2 rows of 2 = 4 squares, 4 params; A262 pair3: row of 2 + 1 square, 4 params, NOT LANDED) or new ones.
(b) The indirect-jam case: a JAM corner whose X does not meet T_u (a non-toucher K does): S_min = {A, C} at BL, K in
the pocket; needs ROOM(S_min u {K}) or a reason K is impossible.  (c) The list of what remains.
