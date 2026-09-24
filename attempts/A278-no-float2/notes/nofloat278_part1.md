# A278 part 1 -- setting, hypotheses, and the exchange lemmas used (all cited)

Frame: BL corner, wall x = 0, floor y = 0, open box B = (0,1)^2, quadrant Q = {x, y >= 0}; side s in [3.82, s-hat].
A square Z MEETS B iff int Z meets B (k0_knowledge s.1).  For a floater F (meets B, touches no wall; wall distances
h_u(F) = min x of F > 0, h_v(F) = min y of F > 0, both < 1 since F has a box point): DROPS T_u(F) = F - h_u e_x,
T_v(F) = F - h_v e_y (wall-touching unit cells of F's pose), STRIPS S_u = T_u \ F, S_v = T_v \ F.  A BLOCKER of a
drop is a square of P \ {F} meeting the drop's interior.

Hypotheses on P (the packing): family-stuck, and NORMAL = a lexicographic maximiser of (Phi1, Phi2, Phi4, Phi3)
(normal_ring.md s.1.2, Lean exists_normalForm); the only property used below is

  P1  [T]  (normal_ring.md s.1.2 P1; proof = Lemma CELLS with |Pi| = 1, ring_swap.md s.1.3, Lean cells_swap):
      if P has a non-toucher, every wall-touching unit cell T of ANY pose inside [0,s]^2 is met by a toucher
      or by >= 2 squares.  Equivalently (box_meeters.md s.1.1 P1+ with |Pi| = 1): |M(T)| <= 1 forces M(T) = {toucher}
      -- an EMPTY wall cell (M(T) = {}) is excluded too (CELLS exchanges any non-toucher onto it, Phi1 + 1).
  P1+ [T]  (box_meeters.md s.1.1): a family Pi of pairwise interior-disjoint wall-touching cells of any pose with
      |M(Pi)| <= |Pi| is met by touchers only, and |M(Pi)| = |Pi| or every non-toucher is in M(Pi).

Consequences already proved, reused verbatim:
  BLOCKER-SIDE  [T] box_meeters.md s.1.2 (Lean blocker_side_core): Y interior-disjoint from the floater F, Y meets
      int T_v(F)  =>  every separating normal n from Y to F has n_u < 0 < n_v (Y is BELOW-RIGHT of F, positive-slope
      separator).  Mirror: a blocker X of T_u(F) has m_u > 0 > m_v (X ABOVE-LEFT of F).
  ONE-DROP      [T] float2_room.md s.1.1 (Lean one_drop_core): one square blocks at most one of T_u(F), T_v(F).
  MUTUAL        [T] float2_room.md s.1.2: floaters C, D meeting B, C upper-left of a positive-slope separator:
      D may block T_v(C), C may block T_u(D), never T_u(C) or T_v(D).
  DROP-P1       [T] float2_room.md s.1.3: in a normal P every drop of every non-toucher is blocked.
  SQUARE-IN-TRIANGLE [T] construct_towards.md C: a unit square inside {u, v >= 0, u/a + v/b <= 1} needs 1/a + 1/b <= 1.
  NOTCH-NARROW  [T] mintilt253.md: no unit square inside a strip of width < 1.
  SLOPE         [T] ring_domain.md (F3): A floor toucher, C a square, both meeting B => positive-slope separator, A below.
  X-MISS        [T] no_jam.md s.1: a wall toucher X misses B iff its lowest point is at height >= 1 (X subset {y >= 1});
      mirror for a floor toucher Y: Y misses B iff Y subset {x >= 1}.  (k0_knowledge s.1's gloss "y_X >= 1 - cos phi_X"
      is a slip: with the leftmost vertex at height y_L, the lowest point is y_L - cos phi_X and it must be >= 1.)

THEOREM NO-FLOAT2 (target).  In a normal family-stuck P at s in [3.82, s-hat], no corner box is met by two floaters.
Set-up for the proof attempt: C, D floaters meeting B (a FLOAT2 corner is type (0,0,>=2): no toucher meets B).

Tags: [T] proved here or cited; [T-computed] exact finite check with code in code/; [M] measured; [C] open; [F] false.
