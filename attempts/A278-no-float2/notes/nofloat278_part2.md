# A278 part 2 -- FLOAT-SLOPE (A277's case (N) is empty) and the forced structure of a FLOAT2 corner  [T]

**Lemma FLOAT-SLOPE [T] (any n, any s; no floating needed).**  C, D interior-disjoint unit squares of the quadrant
Q, both meeting the open box B.  Then EVERY separating normal n (C in {n.x >= beta}, D in {n.x <= beta}) has
n_u n_v < 0, and all of them lie in ONE open quadrant of directions: either every n is (-,+) -- C upper-left of every
separator, D lower-right -- or every n is (+,-).
Proof.  (i) n_u, n_v >= 0, n != 0.  D is in {n.x <= beta} and in Q, so D lies in the triangle {u, v >= 0,
n_u u + n_v v <= beta}.  C has a box point c (0 < c_u, c_v < 1) with n.c >= beta, so beta <= n_u c_u + n_v c_v <
n_u + n_v.  If n_u, n_v > 0 the triangle has legs a = beta/n_u, b = beta/n_v and SQUARE-IN-TRIANGLE needs
1/a + 1/b = (n_u + n_v)/beta <= 1, i.e. beta >= n_u + n_v: contradiction.  If n_v = 0 < n_u: D lies in the strip
0 <= u <= beta/n_u of width < 1: NOTCH-NARROW; n_u = 0 < n_v likewise.  (ii) n_u, n_v <= 0: apply (i) to -n with
the roles of C and D swapped (C has a box point too).  So n_u n_v < 0.  (iii) The separating normals of two convex
bodies form the cone {n : h_{C-D}(n) <= 0} of the sublinear support function of the Minkowski difference: a convex
cone, hence a connected arc of directions (shorter than a half-circle since C - D has interior).  By (i)-(ii) the
arc misses the closed quadrants {n_u n_v >= 0}, and a connected arc avoiding both axes lies in one open quadrant.  QED
Convention from now on: C is the upper-left floater (every D -> C normal is (-,+)), D the lower-right one.

Corollary 2.1 [T] (sharpens float2_room.md s.1.2 MUTUAL: case (N) never occurs).  In a FLOAT2 corner: D can block
only T_v(C) and C can block only T_u(D) (MUTUAL, with FLOAT-SLOPE supplying "every normal is (-,+)").  Hence, by
DROP-P1, T_u(C) has a blocker X and T_v(D) has a blocker Y, both OUTSIDE {C, D}; by BLOCKER-SIDE X is above-left of
C (every X -> C normal (+,-)) and Y below-right of D (every Y -> D normal (-,+)).  X and Y need not be distinct a
priori (ONE-DROP speaks of one floater); they may be touchers or non-touchers.  If X is a wall toucher it misses B
(FLOAT2 has no toucher meeting B), so X is in {y >= 1} (X-MISS); a floor toucher Y is in {x >= 1}.
Also [T]: T_v(C) is blocked (by D or another square) and T_u(D) is blocked (by C or another square).

Corollary 2.2 [T] (the box as a cell: P1+ with |Pi| = 2).  If M(B) = {C, D} exactly, then every wall-touching unit
cell T of any pose with int T disjoint from B is met by a square outside {C, D} (Pi = {B, T}: |M(Pi)| <= 2 = |Pi|
would make C a toucher).  In particular no wall-touching cell disjoint from B is EMPTY.  With k >= 3 floating
meeters, the same for every k-1 disjoint such cells jointly.

Lemma 2.3 [T] SWEEP (the any-direction landing test; box_meeters.md s.1.3 with the "every other square" hypothesis
made explicit).  Let l be a D -> C separator of slope angle alpha in (0, 90 deg) and l_Y a Y -> D separator of slope
angle alpha_Y.  For psi in [alpha, alpha_Y] (non-empty iff alpha <= alpha_Y) the translates D_t = D - t (cos psi,
sin psi), t >= 0, stay on D's side of both lines (d.n_l = sin(psi - alpha) >= 0 toward D's side, d.n_Y =
sin(alpha_Y - psi) >= 0), so they never meet C or Y; the first t* at which D_t touches a wall gives a wall-touching
cell T* of D's pose with M(T*) subset {D} u (P \ {C, D, Y}).  By P1, some square Z outside {C, D, Y} meets int T*
-- or no such psi exists, i.e. alpha > alpha_Y for EVERY choice of the two separators (the JAM inequality).
Mirror for C with X: for psi in [xi_X, alpha] (xi_X the X -> C separator's angle) C lands free of X and D unless
a square outside {C, D, X} meets the landing cell; else xi_X > alpha for every choice.  Note the nested JAM:
xi_X > alpha > alpha_Y (steeper going up-left) is the ONLY way both floaters are jammed by {C, D, X, Y} alone.

What part 2 does NOT give: a contradiction.  A JAM corner (A261's 3-square witness) satisfies xi_X > alpha' with
the floor toucher A in D's role; the FLOAT2 corner nests two of them.  Part 3 turns to the any-pose cells.
