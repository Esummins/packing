# A278 part 3 -- the cell that lands D: SHADOW-CELL (a 4-square local statement that implies NO-FLOAT2), and the
# witness certified  [T] + [T-computed]

**Definition (reach and shadow).**  For a finite set O of obstacles (closed unit squares of the packing) let
ADM(O) = { Z : Z a closed unit square in [0,s]^2, int Z disjoint from int K for every K in O }, and the SHADOW
Sh(O) = [0,s]^2 \ union { int Z : Z in ADM(O) }: the points no admissible square can cover.  Every square of P
outside O is in ADM(O), so no square of P outside O has an interior point in Sh(O).  (Sh grows with O.)

**Lemma SHADOW-CELL [T] (any n, s).**  P normal (P1) with a non-toucher.  Let F in P be a floater, O subset P a set of
squares containing F, and T a wall-touching unit cell of any pose in [0,s]^2 with
      (i)  int T \ int F  subset  Sh(O)          (the part of T outside F is in the shadow of O), and
      (ii) int T disjoint from int K for every K in O \ {F}   (the other obstacles miss T).
Then P is not normal.  Proof.  Let Z in P meet T at p in int Z meet int T.  If Z is in O then Z = F by (ii).  If Z is
not in O then Z is in ADM(O), so p is not in Sh(O), so by (i) p is in int F -- impossible, Z and F being interior-
disjoint.  Hence M(T) subset {F}: P1 says F is a toucher or |M(T)| >= 2 -- contradiction (M(T) = {} contradicts P1+
with |Pi| = 1 as well, part 1).  QED

**Theorem 3.1 (reduction) [T].**  NO-FLOAT2 at BL follows from the LOCAL statement
  L:  for every quadruple (C, D, X, Y) of unit squares in [0,s]^2 with C, D floaters meeting B, C upper-left
      (FLOAT-SLOPE), X blocking T_u(C) and Y blocking T_v(D) (X, Y outside {C, D}, all interiors pairwise disjoint),
      there is a wall-touching unit cell T with  int T subset int D u Sh({C,D,X,Y})  [or int C u Sh({C,D,X,Y})]
      and int T disjoint from the other three.
Proof: part 2 Cor. 2.1 supplies X, Y in every FLOAT2 corner of a normal P; SHADOW-CELL with O = {C, D, X, Y}.  QED
L is a statement about FOUR squares: the other n - 4 squares can only lie outside the shadow, and they are never
needed as obstacles.  L is sufficient, not necessary (a fifth square may be needed as an obstacle in principle).

**Sufficient test for the shadow (disc test) [T].**  A unit square Z contains the closed disc of radius 1/2 about its
centre c and is contained in the closed disc of radius 1/sqrt2 about c.  So c in K(O) := { c in [1/2, s-1/2]^2 :
dist(c, K) >= 1/2 for all K in O } and every point of Z is within 1/sqrt2 of c.  Hence
      { p : dist(p, K(O)) > 1/sqrt2 }  subset  Sh(O).
K(O) is polygon-with-arcs; replacing the disc by its INSCRIBED 64-gon inflates the obstacles LESS, so K_outer contains
K(O) and dist(p, K_outer) <= dist(p, K(O)): the test with K_outer is conservative.  (code/cell278.py)

**The witness certified [T-computed] (code/cell278.py, results/cell278.json; A277's Y-poke witness, s = s-hat, C
(0.7307, 1.5955, 14.47 deg), D (0.9503, 0.6035, 12.87 deg), X (0.6549, 2.6825, 22.85 deg), Y by its vertices, gaps
C-D 0.00227, D-Y 0.00055, all four drops blocked -- A277 s.2).**  Low footprints (x-projection of int Z meet the band
0 < y < 1): I(C) = (0.368, 0.424), I(D) = (0.352, 1.549), I(X) = {}, I(Y) = (1.548, 2.745).  The flat cells F_x =
[x, x+1] x [0,1] met by D alone among the four: x in (0.4239, 0.5483), a range of length 0.124.  Take T = F_x at
x = 0.48608: T meets D (area 0.855) and none of C, X, Y (0 exactly).  Disc test: dist(T \ int D, K_outer) = 0.7390 >
1/sqrt2 = 0.7071, margin 0.0319: T \ int D (area 0.145: the sliver under D's lower-right edge left of Y's left vertex,
the D-Y wedge above it, and the pocket between the wall, D and C) lies in the shadow of {C, D, X, Y}.  So in EVERY
packing containing these four squares, T is met by D alone: by SHADOW-CELL no such packing is normal.  ([M] adversary
over a fifth square Z meeting T \ int D: sup -0.043.)  This is A277's "J_D = +0.024" made exact and made independent
of the remaining seven squares -- the flat floor cell is the cell that lands D on the witness.

**Why the flat cell exists there (mechanism, [T] on the witness, [C] in general).**  I(Y) starts at Y's left vertex
1.548 = R_D - 0.0008 (Y pokes under D's RIGHT vertex because D is 0.0047 off the floor: only a vertex fits the sliver);
I(C) ends at 0.424 because C's part below height 1 is a 0.06-wide corner (C meets B by area 0.0004); D's low
footprint is 1.2 wide.  So gap = 1.548 - 0.424 = 1.124 >= 1.  The three quantities are not controlled in general:
C can reach deeper into B (I(C) longer), D can be higher (Y no longer a vertex poke: I(Y) starts earlier), and D can
be steep.  Part 4 draws the residual = the set of (C, D, X, Y) where no flat cell is free and asks which other pose.
