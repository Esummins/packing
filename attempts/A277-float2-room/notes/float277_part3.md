# part 3 -- the FLOAT2 room statement: CAP-2 at the corner, not ROOM

## 3.1 The count, with the spare made explicit  [T]  (no_jam.md s.2.3 restated)
S_8 := two meeters per box (8 squares); the POCKET squares are the squares of P interior-disjoint from S_8 -- every
other square, including MIDDLE touchers and every blocker not in S_8.  cap(S_8) := the largest number of pairwise
interior-disjoint unit squares of [0,s]^2 interior-disjoint from S_8.  Then **n <= 8 + cap(S_8)**.  ROOM(S_8) gives
cap <= 1 (two squares containing O overlap) and n <= 9; but n = 11 is excluded already by **cap(S_8) <= 2**, i.e.
> **CAP-2(S_8): no two interior-disjoint unit squares of [0,s]^2, both interior-disjoint from S_8, both miss O.**
(Three pocket squares hold >= 2 misses.)  ROOM(S_8) is FALSE for every structure with a middle toucher or with a
blocker outside S_8 that misses O -- these ARE pocket squares missing O -- so for FLOAT2 the honest target is CAP-2.

## 3.2 Sectors for two misses  [T]  (A259 s.2.2 applied twice)
Each miss Q has (q - O).n >= 1/2 for a wall normal n and lies in one half: a corner SECTOR.  A miss in a sector of a
PAIR corner whose structure is in S_8 is killed by that corner's certificate (A259 PAIR / A260 hybrid / A262 pair3:
"no square free of that corner's squares misses O in its sectors" -- Q is free of all of S_8).  In a FLOAT2 ring
(BL FLOAT2; walls 1, 2 normal; X on wall 3 serves TL; A2 on wall 0 serves BR) the corners BR, TR, TL are PAIR
corners with structures {A2 + right row} (pair3), {right row + ceiling row} (PAIR / hybrid), {ceiling row + X}
(pair3).  So both misses lie in the BL sectors, and the FLOAT2 obligation is corner-local:
> **BL-CAP-2(C, D):** no two interior-disjoint unit squares of [0,s]^2, each interior-disjoint from C and D, both
> have their centres in the BL sectors {(q-O).(-v) >= 1/2, q_x <= s/2} u {(q-O).(-u) >= 1/2, q_y <= s/2} (psi in
> [-45, 45) so that -v points at the floor and -u at the left wall).
X and A2 may be added as obstacles (monotone: a miss is free of all of S_8); the BLOCKERS K_C, K_D may NOT (they may
be the misses).  s is eliminated as in A259 s.2.3: the sector half-planes and the container relax as s grows
(Lean `corner_frame_mono`), so BL-CAP-2 at s_max = 3.8771 implies it on the window.

## 3.3 CAP-2 by DIAMETER  [T]
Let R := the set of centres q of unit squares Q (any tilt) free of the obstacles with q in a BL sector.  If diam R <
1 then BL-CAP-2 holds: two such squares have centres at distance < 1, their inscribed discs of radius 1/2 overlap,
so the squares overlap.  (A252's "admissible centres of diameter < 1 => capacity <= 2", `capacity_le_two_of_anchor`.)
Over a parameter box the exact R is replaced by A259's over-approximation (obstacle CORES, tilt KERNEL of the free
square), so diam R_over < 1 is a box-valid test with A259's soundness direction.

## 3.4 What the dropped witness says  [M, code/diam277.py, results/diam277.json; 1 deg tilt grid, exact centre sets]
The FLOAT2 witness of part 2 with Y (all four drops blocked; not P1-normal -- part 2.4 / witness277b J_D > 0):
| obstacles | BL-sector centre region: area | diam | worst miss |
|---|---|---|---|
| {C, D, X, Y} | 0 | -- | none (ROOM holds) |
| {T_u(C), T_v(D), Y} and {T_u(C), T_v(D), X, Y} | 0 | -- | none |
| {T_u(C), T_v(D)} and {T_u(C), T_v(D), X} | 0.121 | **0.936** | +0.640 (a floor square right of T_v(D), centre (2.43, 0.71)) |
| {C, D} | 0.111 | **0.934** | +0.636 |
So on this point: ROOM with two obstacles is FALSE (the miss is where Y stands), CAP-2 with two obstacles is TRUE
by diameter with margin 0.064, and adding the floor blocker restores ROOM.  One point, one side (shat): [M] only.

## 3.5 The two routes, stated
(S1) **BL-CAP-2(C, D)** directly: obstacles C, D (6 parameters: h_u, h_v, theta each; both meet the open box, interior-
disjoint, floating); no strip lemma, no blocker hypothesis: covers direct, indirect, middle-toucher and case-(N)
FLOAT2 alike.  [C]; certificate = a 6-parameter box tree with the diameter test (priced in part 6).
(S2) **BL-CAP-2(T_u(C), T_v(D))** (4 parameters: b = h_v(C), theta_C, a = h_u(D), theta_D; both drops meet the open
box; interior-disjoint in case (P) [T]: the positive-slope separator is kept by both drops) **+ STRIP-C + STRIP-D**
(no BL-sector miss has an interior point in S_u(C), resp. S_v(D)).  Given the strips every miss avoids both drops, so
(S2) implies BL-CAP-2(C, D) in case (P).  Part 4 says exactly when STRIP-C / STRIP-D are the JAM strip lemma.
Both are weaker than what A262 asked for JAM (ROOM); both close n = 11 through 3.1-3.2 with no spare left.
