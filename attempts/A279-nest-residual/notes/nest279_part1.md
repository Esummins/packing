# A279 part 1 -- the NEST residual restated, with every hypothesis and its source

Frame: BL, wall x = 0, floor y = 0, B = (0,1)^2, s in [3.82, s-hat].  Unit squares C, D (floaters), X, Y.
Floor toucher Y: bottom vertex (b_Y, 0), edges (cos a, sin a), (-sin a, cos a), a = alpha_Y in (0, 90 deg):
left vertex (b_Y - sin a, cos a), top (b_Y + cos a - sin a, cos a + sin a).  Wall toucher X: leftmost vertex
(0, y_X), edges (cos phi, sin phi), (sin phi, -cos phi): lowest point y_X - cos phi.

R (the residual of L, no_float2.md s.0, part 4) is the set of quadruples with
 (H-C, H-D) C, D unit squares of the quadrant, both meeting B, h_u, h_v > 0 for both (floaters), interiors
           disjoint.  [T] FLOAT-SLOPE (A278 part 2): every D -> C separating normal is (-,+): C upper-left.
 (H-X)     int X meets int T_u(C) = int(C - h_u(C) e_x), X interior-disjoint from C, D, Y.  [T] BLOCKER-SIDE mirror
           (box_meeters.md s.1.2): every X -> C normal is (+,-): X above-left.  If X is a wall toucher it misses
           B (FLOAT2 has no toucher meeting B): X subset {y >= 1}, i.e. y_X - cos phi_X >= 1.
 (H-Y)     int Y meets int T_v(D); Y interior-disjoint from the rest; every Y -> D normal is (-,+): Y below-right
           [T] BLOCKER-SIDE.  Floor toucher Y misses B: Y subset {x >= 1}, i.e. b_Y - sin alpha_Y >= 1.
 (NEST)    eta_+ < alpha_- <= alpha_+ < xi_-  [T] forced on R by SWEEP (A278 part 6) when the swept region
           holds no fifth square; arcs: eta = Y -> D separator angles, alpha = D -> C, xi = X -> C.
 (NO-CELL) no wall-touching unit cell T of any pose with int T subset int D u Sh({C,D,X,Y}) missing C, X, Y
           (or the same with C and D exchanged).  Sh = shadow (A278 part 3).
NO-FLOAT2 <= (R empty) [T, Theorem 3.1].  Dimension 10 with X, Y touchers (C, D: 3 each; X: y_X, phi_X;
Y: b_Y, alpha_Y), 12 with free blockers; s enters only via the container (monotone, s-hat worst) [T, part 4].

What P1 / CELLS actually give (sources): CELLS (ring_swap.md s.1.3, Lean cells_swap) for ANY poses of the
cells; P1 (normal_ring.md s.1.2, (E2) TOUCH-CELL) needs the cell to TOUCH A WALL (Phi_1 rises); P4 RETREAT
(E5) allows a non-touching cell only if it lowers the (border cell, non-toucher) incidence count; P1+ family
form (box_meeters.md s.1.1).  Cor. 2.2 (A278 part 2): with M(B) = {C, D}, no wall cell disjoint from B is met
by <= {C, D}; a cell meeting B is allowed to be met by C and D both only if it is B itself... (P1+ with
Pi = {B, T} needs T interior-disjoint from B).

Reading of (NEST) [T] (part 6): Y is UNDER D (a point of Y straight below a point of D, and all Y -> D
separators shallower than all D -> C separators); D floats high; C, above-left of D by a steeper line, still
meets B, so C is near the wall.  Both floaters are wedged: D between C (steeper) and Y (shallower) exactly as
the JAM floater between X and A (ring_domain.md H1-H3, xi > alpha'), C between X and D likewise.  R is a
NESTED DOUBLE JAM.  [M] float277 F4/F5 (A277 s.4): sup of min(hypotheses, -J_anypose) <= 0 on the 4/5-square
model, i.e. every strictly feasible quadruple has a wall cell of some pose met by <= {D} or <= {C} among the
four -- but the shadow condition of L was not tested, and "met by <= {D}" at margin 0 is degenerate.

Plan for parts 2-4: (i) locate the free cell numerically on near-feasible NEST quadruples (import
A277/A278 code; ONE light python), read off its pose class; (ii) the count chase: which of "Y meets B",
"X meets B", "free wall cell", "not family-stuck" is forced in NEST; (iii) if a quadruple survives with the
shadow test, draw it.  Every numerical claim [M]/[T-computed]; lemmas [T] only with exchange steps cited.
