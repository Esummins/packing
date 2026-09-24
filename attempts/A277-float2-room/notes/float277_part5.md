# part 5 -- the INDIRECT JAM, and the middle toucher above X  (BRIEF (b))

Setting: BL is a JAM corner: A (floor toucher) and C (floater) meet the open box, no wall-3 toucher meets it.  C's wall
drop T_u(C) is blocked (part 2.3) by some K; DIRECT means K = X, the wall-3 toucher serving TL (H1-H2 of the chain);
INDIRECT means K is anything else: a middle wall toucher X' (X'_low >= 1, X'_top <= s - 1), a free square, or a
floater of no box (a floater meets one box only, and BL's meeters are A, C).

## 5.1 The count does not see the holder  [T]
n <= 8 + cap(S_8) (part 3.1) with S_8 = {A, C, X (serves TL), ...}.  K, if not in S_8, is a pocket square: it is
counted in cap(S_8) whoever holds whom.  So the indirect jam needs NO reduction to the direct one for the COUNT; it
needs the same statement as everything else in 5d: **BL-CAP-2(A, C)** -- no two disjoint squares free of A and C
(and of X, A2 in S_8) both miss O in the BL sectors -- and the other corners' certificates.  Where the indirect case
differs is the DOMAIN of what has been certified or proved for JAM: A262's `jam` kernel PRUNEs every box in which X
misses T_u(C) (the direct-jam conditions), and STRIP_2-IN-JAM (A267-A276) assumes H1 for the holder (X_low > 1.406);
a middle-toucher holder has X'_low in [1, 1.406) and a free holder touches nothing.  So the certified JAM room
statements cover the direct case only.

## 5.2 "The holder must itself be held; the P4 chain ends at a toucher" -- true, but not a reduction  [T]/[F]
[T] K blocks T_u(C) => K has a point left of a point of C at the same height; two disjoint convex bodies either have a
non-horizontal separating line (then one is left of the other at EVERY shared height) or share no height; so the
relation "blocks the wall drop of" is antisymmetric, and K's own wall drop (K a non-toucher) is blocked by some K'
(part 2.3), and so on; the chain visits distinct squares and ends at a wall-3 toucher X''.  [F] as a reduction:
X'' holds the LAST square of the chain, not C; C's strip S_u(C) is occupied by K, whose pose is free (5 parameters of
its own), and nothing forces K to serve TL.  The only way K enters the room argument is as a pocket square (5.1).

## 5.3 The escape configuration (drawn on the page, panel (c))
A JAM ring (A262's) with X serving TL but NOT meeting T_u(C); a free square K above-left of C with a point in S_u(C),
K's centre in the BL-left sector (q_y < s/2) missing O; a square G containing O.  Count: 8 + K + G = 10; nothing in the
chain excludes it; an 11th square would be a second BL-sector miss, disjoint from K: exactly BL-CAP-2(A, C).  If instead
K contains O ("the holder is the centre square", BRIEF): n <= 8 + 1 + (misses) and every miss is again a BL-sector
square free of A, C: BL-CAP-2 once more, or nothing if there is one miss (n <= 10).  [M] A261 `local261` scenario G
("floater C blocked by a second floater K, itself blocked, and toucher Y"): NO-WITNESS in the drop sense (10
restarts) -- weak evidence that a free holder cannot even be posed locally; not used.

## 5.4 The middle toucher above X  [T]
If a START square S on wall 3 serves TL above X (X_top <= s - 1), then S in S_8 in X's place and X is a pocket square
(a toucher misses O: its far extent <= sqrt2 < s/2).  cap(S_8) >= 1 already; the count needs cap <= 2, i.e. BL-CAP-2
again (X is a BL-left-sector miss if its centre is below s/2, else a TL-left miss killed by pair3(TL) with S).  For the
STRIP route X's H1 fails (X_low may be < 1.406): the direct-jam strip proofs do not cover this X.  [M] `span262`: sup
-0.0327 at shat, none found.

## 5.5 The unified obligation for link 5d
> **CAP-2 of the two box meeters at every non-PAIR corner**: JAM -- BL-CAP-2(A, C) (5 parameters: a, alpha; h_u, h_v,
> theta), covering direct AND indirect holders and the middle toucher above X; FLOAT2 -- BL-CAP-2(C, D) (6 parameters).
> Both by the diameter test of part 3.3; both s-eliminated at s_max; neither needs a strip lemma or a holder hypothesis.
For the direct JAM the chain's ROOM route (pair3 + STRIP_2-IN-JAM) is stronger and stays; CAP-2 is what the rest of
5d needs.  Priced in part 6.
