# A278 part 4 -- NO-FLOAT2: what is proved, the exact residual, and its price

**Status: NO-FLOAT2 is [C], reduced [T] to the 4-square local statement L (part 3, Theorem 3.1).**  What is [T]:
  (a) FLOAT-SLOPE (part 2): the two floaters are separated by positive-slope lines only, one is upper-left (C) of
      every separator; A277's case (N) is empty.  (b) Cor. 2.1: T_u(C) and T_v(D) have blockers X, Y outside {C, D},
      X above-left of C, Y below-right of D; wall/floor-toucher blockers lie in {y >= 1} / {x >= 1}.  (c) Cor. 2.2:
      with M(B) = {C, D} no wall cell disjoint from B is met by <= {C, D} (no empty wall cell anywhere).  (d) SWEEP
      (Lemma 2.3): a free landing direction for D or C is stopped by a square outside {C, D, X, Y}, else the nested
      JAM inequality xi_X > alpha > alpha_Y.  (e) SHADOW-CELL + the disc test (part 3): a wall cell whose part
      outside D lies in the shadow of {C, D, X, Y} is met by D alone in EVERY packing containing the four.
What is [T-computed]: A277's Y-poke witness (the only FLOAT2 corner with all drops blocked on disk) is landed by the
flat floor cell [0.486, 1.486] x [0, 1] with disc-test margin 0.032 -- independent of the other seven squares.

**The residual, exactly.**  R := { (C, D, X, Y) : C, D unit squares of Q meeting B, h_u, h_v > 0 for both, C
upper-left of D; X, Y unit squares of [0, s]^2, int X meets int T_u(C), int Y meets int T_v(D); the four pairwise
interior-disjoint }  minus  { quadruples where some wall-touching cell T of some pose has int T \ int D (or \ int C)
in Sh({C, D, X, Y}) and misses the other three }.  NO-FLOAT2 <= (R is empty).  Dimension: 6 (C, D) + 3 + 3 = 12 with
free blockers; 10 when X is a wall toucher (y_X, phi_X) and Y a floor toucher (x_Y, alpha_Y) -- the case the JAM
hypotheses H1 mirror; a non-toucher blocker is the INDIRECT case and its own drops are blocked by further squares
(box_meeters.md s.1.1: the chain ends at a toucher), which L never needs.  The side s enters only through the
container [0, s]^2 in ADM: monotone (a larger container has more admissible squares, a smaller shadow), so s = s-hat
is the worst case and the statement at s-hat implies it on [3.82, s-hat]  [T].
Where the flat-cell mechanism can fail (the sub-residual to draw): the gap inf I(Y) - sup I(C) between the low
footprints is < 1, or D's low footprint misses the gap, or the pocket T \ int D is reachable (a fifth square can
poke in).  [M] flat278 (code/flat278.py, results/flat278.jsonl, one python, running at this writing): the sup of
min(A277's local terms, -J_flat(C), -J_flat(D)) on the 4-square model with X, Y touchers -- > 0 exhibits a residual
point where no FLAT cell is free (then the any-pose test of A277 decides whether a tilted cell lands it).

**Certificate design (not launched; the lab is at its ceiling).**  A box tree over the 10 (12) parameters at s = s-hat.
Per box: (1) PRUNE by interval versions of the hypotheses (pair gaps >= 0 with cores/hulls, box depth of C and D > 0,
X and Y miss B, drops blocked: hull(X) meets core(T_u(C)) etc.); (2) CELL: for the flat cells F_x take the x-interval
[sup hull-footprint(C), inf hull-footprint(Y) - 1] and require it to meet core-footprint(D) -- a 1-D test -- or fall
back to D's own pose translated to the floor/wall; (3) SHADOW by the disc test with the obstacles replaced by their
CORES over the box (fewer admissible centres excluded => K_outer larger => conservative) and the target by
T \ core(D) (larger => conservative), verified as in cell278.  Every step is monotone in the box, so a CERT leaf is
sound; OPEN leaves are refined.  Bench: cell278's test costs 0.02 s per configuration (shapely), comparable to cert277's
kernel (0.02 s per box); cert277's 6-parameter tree was priced 30-1000 CPU-h (float2_room.md s.6).  Ten parameters
with the same kernel: NOT priced here; naive extrapolation puts it above 10^3 CPU-h.  A 2-D slice bench (h_v(D) x
alpha_Y at the witness) is the cheap first step (< 1 CPU-h) and is what an agent with compute should run first.

**What would remove the tree.**  A hand proof of L on the 10-parameter domain = three inequalities: (F1) sup I(C) <=
x_D^max - 1 - m for some m > 0, (F2) inf I(Y) >= x_D^max - m' (Y pokes under D's right vertex), (F3) the pocket
between D, Y and the floor / the wall, C, D is in the shadow.  (F2) is where D's height enters: for a floor toucher
Y below-right of D that meets int T_v(D) but not D, Y's left vertex lies in the STRIP S_v(D) = T_v(D) \ D, a
parallelogram of height h_v(D) under D's lower edges -- so for small h_v(D) only a vertex poke is possible and
inf I(Y) is within O(h_v) of D's right vertex; for h_v(D) near 1 (D barely in B) Y can stand under D and I(Y) starts
under D's middle, and (F1) must carry the load: C is then above D's left part and its low footprint... is not
bounded by anything proved here.  These are the two ends of the residual; both are [C].
